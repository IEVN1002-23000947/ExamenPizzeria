from . import pedidos_bp
from flask import jsonify, request, flash
from src.database import mysql

precios = {
    'Chica': 40,
    'Mediana': 80,
    'Grande': 120
}
precios_ingredientes = {
    'Jamon': 10,
    'Piña': 10,
    'Champiñones': 10
}
@pedidos_bp.route('/', methods=['POST'])
def registrar_pedido():

    datos = request.get_json()

    nombre = datos.get('nombre')
    direccion = datos.get('direccion')
    telefono = datos.get('telefono')
    fecha = datos.get('fecha_pedido')
    pizzas = datos.get('pizzas')

    if not nombre or not direccion or not telefono or not fecha:
        return jsonify({
            'exito': False,
            'mensaje': 'Completa todos los datos del cliente'
        }), 400

    if not isinstance(pizzas, list) or len(pizzas) == 0:
        return jsonify({
            'exito': False,
            'mensaje': 'Agrega al menos una pizza'
        }), 400

    total = 0
    detalles = []

    for pizza in pizzas:
        tamano = pizza.get('tamano')
        ingredientes = pizza.get('ingredientes')
        cantidad = pizza.get('cantidad')

        if tamano not in precios or not ingredientes or not cantidad:
            return jsonify({
                'exito': False,
                'mensaje': 'Revisa los datos de las pizzas'
            }), 400

        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            return jsonify({
                'exito': False,
                'mensaje': 'La cantidad debe ser un número entero mayor a cero'
            }), 400

        if isinstance(ingredientes, list):
            ingredientes = ', '.join(ingredientes)

        if not isinstance(ingredientes, str) or not ingredientes.strip():
            return jsonify({
                'exito': False,
                'mensaje': 'Selecciona los ingredientes de cada pizza'
            }), 400

        precio = precios[tamano]
        for ingrediente in ingredientes.split(', '):
            if ingrediente not in precios_ingredientes:
                return jsonify({
                    'exito': False,
                    'mensaje': 'Ingrediente no válido'
                }), 400
            precio += precios_ingredientes[ingrediente]
        subtotal = precio * cantidad
        total += subtotal
        detalles.append({
            'tamano': tamano,
            'ingredientes': ingredientes,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal
        })

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO pedidos
            (nombre, direccion, telefono, fecha_pedido, total)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, direccion, telefono, fecha, total))

        idpedido = cursor.lastrowid
        for pizza in detalles:
            cursor.execute("""
                INSERT INTO detalle_pedido
                (idpedido, tamano, ingredientes, cantidad,
                precio, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                idpedido,
                pizza['tamano'],
                pizza['ingredientes'],
                pizza['cantidad'],
                pizza['precio'],
                pizza['subtotal']
            ))
        mysql.connection.commit()
        mensaje = f'Pedido registrado correctamente. Total a pagar: ${total:.2f}'
        flash(mensaje, 'success')
        return jsonify({
            'exito': True,
            'mensaje': mensaje,
            'idpedido': idpedido,
            'total': total
        }), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            'exito': False,
            'mensaje': 'Error al registrar el pedido',
            'error': str(e)
        }), 500
    finally:
        cursor.close()
