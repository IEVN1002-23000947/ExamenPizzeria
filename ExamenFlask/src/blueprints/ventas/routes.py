from . import ventas_bp
from flask import jsonify
from src.database import mysql

@ventas_bp.route('/dia/<dia>', methods=['GET'])
def ventas_dia(dia):
    dias = {
        'lunes': 0,
        'martes': 1,
        'miercoles': 2,
        'miércoles': 2,
        'jueves': 3,
        'viernes': 4,
        'sabado': 5,
        'sábado': 5,
        'domingo': 6
    }
    dia = dia.lower().strip()
    if dia not in dias:
        return jsonify({
            'exito': False,
            'mensaje': 'Dia de la semana no valido'
        }), 400
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT *
        FROM pedidos
        WHERE WEEKDAY(fecha_pedido) = %s
        ORDER BY fecha_pedido
    """, (dias[dia],))
    ventas = cursor.fetchall()
    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) AS total_acumulado
        FROM pedidos
        WHERE WEEKDAY(fecha_pedido) = %s
    """, (dias[dia],))
    resultado = cursor.fetchone()
    cursor.close()
    return jsonify({
        'exito': True,
        'ventas': ventas,
        'total_acumulado': float(resultado['total_acumulado'])
    })
    
@ventas_bp.route('/mes/<mes>', methods=['GET'])
def ventas_mes(mes):
    meses = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }
    mes = mes.lower().strip()
    if mes not in meses:
        return jsonify({
            'exito': False,
            'mensaje': 'Mes no valido'
        }), 400
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT *
        FROM pedidos
        WHERE MONTH(fecha_pedido) = %s
        ORDER BY fecha_pedido
    """, (meses[mes],))
    ventas = cursor.fetchall()
    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) AS total_acumulado
        FROM pedidos
        WHERE MONTH(fecha_pedido) = %s
    """, (meses[mes],))
    resultado = cursor.fetchone()

    cursor.close()
    return jsonify({
        'exito': True,
        'ventas': ventas,
        'total_acumulado': float(resultado['total_acumulado'])
    })
@ventas_bp.route('/<int:idpedido>/detalle', methods=['GET'])
def detalle_venta(idpedido):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT *
        FROM pedidos
        WHERE idpedido = %s
    """, (idpedido,))
    pedido = cursor.fetchone()
    if pedido is None:
        cursor.close()
        return jsonify({
            'exito': False,
            'mensaje': 'Pedido no encontrado'
        }), 404
    cursor.execute("""
        SELECT *
        FROM detalle_pedido
        WHERE idpedido = %s
    """, (idpedido,))
    detalles = cursor.fetchall()
    cursor.close()
    return jsonify({
        'exito': True,
        'pedido': pedido,
        'detalles': detalles
    })
