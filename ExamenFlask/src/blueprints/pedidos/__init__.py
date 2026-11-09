from flask import Blueprint

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/api/pedidos')

from . import routes
