from flask import Blueprint, jsonify
from app.database.models import get_alerts

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts', methods=['GET'])
def get_alerts_endpoint():
    alerts = get_alerts()
    return jsonify({'alerts': alerts})