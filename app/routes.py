from flask import Blueprint, request, jsonify
from .models import User
from .utils import validate_phone
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    current_user
)


register_bp = Blueprint("register_bp", __name__)
auth_bp = Blueprint("auth_bp", __name__)


@register_bp.route("/register", methods=["POST"])
def do_reg():

    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400
    
    phone_number = data.get('phone_number')
    password = data.get('password')
    
    if not phone_number or not password:
        return jsonify({"error": "Номер телефона и пароль обязательны"}), 400
    
    is_valid, normalized_phone = validate_phone(phone_number)
    if not is_valid:
        return jsonify({"error": "Неверный формат номера телефона"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Пароль должен содержать минимум 6 символов"}), 400

    if User.query.filter_by(phone_number=normalized_phone).first():
        return jsonify({"error": "Пользователь с таким номером уже существует"}), 409

    user = User(phone_number=normalized_phone)
    user.set_password(password)
    
    user.add_user()

    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    
    return jsonify({
        "message": "Пользователь успешно зарегистрирован",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 201



@auth_bp.route('/login', methods=['POST'])
def login():
    """Авторизация пользователя"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Данные не предоставлены"}), 400
        
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if not phone_number or not password:
            return jsonify({"error": "Номер телефона и пароль обязательны"}), 400
        
        is_valid, normalized_phone = validate_phone(phone_number)
        if not is_valid:
            return jsonify({"error": "Неверный формат номера телефона"}), 400
        
        user = User.query.filter_by(phone_number=normalized_phone).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Неверный номер телефона или пароль"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Аккаунт деактивирован"}), 403

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        
        return jsonify({
            "message": "Авторизация успешна",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Ошибка при авторизации"}), 500