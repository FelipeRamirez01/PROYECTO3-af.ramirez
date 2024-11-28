from flask import Blueprint, jsonify, request
from models.models import Producto, Ingrediente
from app import db

api_bp = Blueprint('api_bp', __name__)

# Consultar todos los productos
@api_bp.route('/productos', methods=['GET'])
def get_productos():
    productos = Producto.query.all()
    return jsonify([{
        'id': p.id, 'nombre': p.nombre, 'precio_publico': p.precio_publico,
        'calorias': p.calcular_calorias(), 'costo': p.calcular_costo()
    } for p in productos])

# Consultar un producto según su ID
@api_bp.route('/productos/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return jsonify({'id': producto.id, 'nombre': producto.nombre, 'precio_publico': producto.precio_publico})

# Consultar un producto según su nombre
@api_bp.route('/productos/nombre/<string:nombre>', methods=['GET'])
def get_producto_por_nombre(nombre):
    producto = Producto.query.filter_by(nombre=nombre).first_or_404()
    return jsonify({'id': producto.id, 'nombre': producto.nombre, 'precio_publico': producto.precio_publico})

# Consultar las calorías de un producto según su ID
@api_bp.route('/productos/<int:producto_id>/calorias', methods=['GET'])
def get_calorias_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return jsonify({'calorias': producto.calcular_calorias()})

# Consultar la rentabilidad de un producto según su ID
@api_bp.route('/productos/<int:producto_id>/rentabilidad', methods=['GET'])
def get_rentabilidad_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return jsonify({'rentabilidad': producto.calcular_rentabilidad()})

# Consultar el costo de producción de un producto según su ID
@api_bp.route('/productos/<int:producto_id>/costo', methods=['GET'])
def get_costo_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return jsonify({'costo': producto.calcular_costo()})

# Vender un producto según su ID
@api_bp.route('/productos/<int:producto_id>/vender', methods=['POST'])
def vender_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    for ingrediente in producto.ingredientes:
        ingrediente.inventario -= 1  # Ajusta la lógica según tu necesidad
    db.session.commit()
    return jsonify({'mensaje': f'Producto {producto.nombre} vendido con éxito.'})

# Consultar todos los ingredientes
@api_bp.route('/ingredientes', methods=['GET'])
def get_ingredientes():
    ingredientes = Ingrediente.query.all()
    return jsonify([{
        'id': i.id, 'nombre': i.nombre, 'precio': i.precio, 'calorias': i.calorias,
        'inventario': i.inventario, 'es_vegetariano': i.es_vegetariano
    } for i in ingredientes])

# Consultar un ingrediente según su ID
@api_bp.route('/ingredientes/<int:ingrediente_id>', methods=['GET'])
def get_ingrediente(ingrediente_id):
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    return jsonify({'id': ingrediente.id, 'nombre': ingrediente.nombre, 'inventario': ingrediente.inventario})

# Consultar un ingrediente según su nombre
@api_bp.route('/ingredientes/nombre/<string:nombre>', methods=['GET'])
def get_ingrediente_por_nombre(nombre):
    ingrediente = Ingrediente.query.filter_by(nombre=nombre).first_or_404()
    return jsonify({'id': ingrediente.id, 'nombre': ingrediente.nombre, 'inventario': ingrediente.inventario})

# Consultar si un ingrediente es sano según su ID
@api_bp.route('/ingredientes/<int:ingrediente_id>/sano', methods=['GET'])
def es_ingrediente_sano(ingrediente_id):
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    return jsonify({'es_sano': ingrediente.calorias < 100 or ingrediente.es_vegetariano})

# Reabastecer un ingrediente según su ID
@api_bp.route('/ingredientes/<int:ingrediente_id>/reabastecer', methods=['GET','POST'])
def reabastecer_ingrediente(ingrediente_id):
    if request.method == 'POST':
        try:
            # Obtener el ingrediente por ID
            ingrediente = Ingrediente.query.get_or_404(ingrediente_id)

            # Validar la solicitud JSON
            data = request.get_json()
            if not data or 'cantidad' not in data:
                return jsonify({'error': 'Se requiere la cantidad en la solicitud JSON.'}), 400

            # Obtener la cantidad de la solicitud
            cantidad = data.get('cantidad', 10)  # Valor por defecto: 10
            if not isinstance(cantidad, int) or cantidad <= 0:
                return jsonify({'error': 'La cantidad debe ser un número entero positivo.'}), 400

            # Reabastecer el ingrediente
            ingrediente.abastecer(cantidad)
            
            # Devolver una respuesta JSON válida
            return jsonify({
                'mensaje': f'Ingrediente {ingrediente.nombre} reabastecido con éxito.',
                'nuevo_inventario': ingrediente.inventario
            }), 200
        
        except Exception as e:
            # Manejo general de errores
            return jsonify({'error': str(e)}), 500