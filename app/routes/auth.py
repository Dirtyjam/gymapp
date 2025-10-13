from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from ..models import User
from ..utils import validate_phone

user_routes = Namespace('users')

@user_routes.route("/register")
class UserReg(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "Данные не предоставлены"}, 400

        phone_number = data.get('phone_number')
        password = data.get('password')
        is_trainer = data.get("is_trainer")

        if not phone_number or not password:
            return {"error": "Номер телефона и пароль обязательны"}, 400

        is_valid, normalized_phone = validate_phone(phone_number)
        if not is_valid:
            return {"error": "Неверный формат номера телефона"}, 400

        if len(password) < 6:
            return {"error": "Пароль должен содержать минимум 6 символов"}, 400

        if User.query.filter_by(phone_number=normalized_phone).first():
            return {"error": "Пользователь с таким номером уже существует"}, 409

        user = User(phone_number=normalized_phone, is_trainer=is_trainer)
        user.set_password(password)
        user.add_user()

        access_token = create_access_token(identity=phone_number)
        refresh_token = create_refresh_token(identity=phone_number)

        return {
            "message": "Пользователь успешно зарегистрирован",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }, 201



@user_routes.route('/login')
class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data:
                return {"error": "Данные не предоставлены"}, 400

            phone_number = data.get('phone_number')
            password = data.get('password')

            if not phone_number or not password:
                return {"error": "Номер телефона и пароль обязательны"}, 400

            is_valid, normalized_phone = validate_phone(phone_number)
            if not is_valid:
                return {"error": "Неверный формат номера телефона"}, 400

            user = User.query.filter_by(phone_number=normalized_phone).first()

            if not user or not user.check_password(password):
                return {"error": "Неверный номер телефона или пароль"}, 401

            if not user.is_active:
                return {"error": "Аккаунт деактивирован"}, 403

            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                "message": "Авторизация успешна",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }, 200

        except Exception as e:
            return {"error": "Ошибка при авторизации"}, 500
