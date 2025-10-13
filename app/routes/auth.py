from flask import request, jsonify
from ..models import User
from ..utils import validate_phone
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    current_user
)
from flask_restx import Namespace, Resource, fields

user_routes = Namespace('users', description='User-related operations')

user_model = user_routes.model('User', {
    'phone_number': fields.String(required=True, description='Phone number of the user', example='+79161234567'),
    'password': fields.String(required=True, description='Password for the user', example='password123'),
    "is_trainer": fields.Boolean(required=True, description="Checked if user is trainer", example="true")
})

user_response_model = user_routes.model('UserResponse', {
    'message': fields.String(description='Message of the operation', example='Пользователь успешно зарегистрирован'),
    'access_token': fields.String(description='JWT access token', example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'),
    'refresh_token': fields.String(description='JWT refresh token', example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'),
    'user': fields.Nested(user_model)
})

@user_routes.route("/register")
class UserReg(Resource):
    @user_routes.doc(description="Регистрация нового пользователя", responses={201: 'Пользователь успешно зарегистрирован', 400: 'Ошибка при регистрации'})
    @user_routes.expect(user_model, validate=True) 
    @user_routes.marshal_with(user_response_model, code=201)
    def post(self):
        """Регистрация пользователей"""
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Данные не предоставлены"}), 400
        
        phone_number = data.get('phone_number')
        password = data.get('password')
        is_trainer = data.get("is_trainer")
        
        if not phone_number or not password:
            return jsonify({"error": "Номер телефона и пароль обязательны"}), 400
        
        is_valid, normalized_phone = validate_phone(phone_number)
        if not is_valid:
            return jsonify({"error": "Неверный формат номера телефона"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Пароль должен содержать минимум 6 символов"}), 400

        if User.query.filter_by(phone_number=normalized_phone).first():
            return jsonify({"error": "Пользователь с таким номером уже существует"}), 409

        user = User(phone_number=normalized_phone, is_trainer=is_trainer)
        user.set_password(password)
        
        user.add_user()

        
        access_token = create_access_token(identity=user.id) 
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            "message": "Пользователь успешно зарегистрирован",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }, 201


@user_routes.route('/login')
class UserLogin(Resource):
    @user_routes.doc(description="Авторизация пользователя", responses={200: 'Авторизация успешна', 400: 'Неверный формат данных', 401: 'Неверный номер телефона или пароль', 403: 'Аккаунт деактивирован'})
    @user_routes.expect(user_model) 
    @user_routes.marshal_with(user_response_model, code=200)  # Указываем формат ответа
    def post(self):
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


            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id) 
            
            return {
                "message": "Авторизация успешна",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }, 200
            
        except Exception as e:
            return jsonify({"error": "Ошибка при авторизации"}), 500
