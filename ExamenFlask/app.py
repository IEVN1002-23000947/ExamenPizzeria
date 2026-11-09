
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from src.database import mysql
from src.blueprints.pedidos import pedidos_bp
from src.blueprints.ventas import ventas_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

mysql.init_app(app)
app.register_blueprint(pedidos_bp)
app.register_blueprint(ventas_bp)

@app.route('/')
def index():
    return jsonify({
        'mensaje': 'API Pizzeria funcionando'
    })
@app.route('/api/prueba-db')
def prueba_db():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT DATABASE() AS base')
    resultado = cursor.fetchone()
    cursor.close()
    return jsonify(resultado)
if __name__ == '__main__':
    app.run(debug=True)
