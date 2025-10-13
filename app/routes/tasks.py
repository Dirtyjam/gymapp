from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from app import db
from app.models import User, Task     


task_routes = Namespace('tasks', description='Task-related operations')

task_model = task_routes.model('Task', {
    'student_id': fields.Integer(required=True, description='ID ученика', example=2),
    'title': fields.String(required=True, description='Название задания', example='Подтягивания'),
    'description': fields.String(required=True, description='Описание задания', example='Сгибание рук на турнике'),
    'due_date': fields.String(required=True, description='Дата выполнения задания в формате YYYY-MM-DD', example='2023-12-31')
})

task_model_response = task_routes.model('TaskResponse', {
    'id': fields.Integer(description='ID задания', example=1),
    'trainer_id': fields.Integer(description='ID тренера', example=1),
    'student_id': fields.Integer(description='ID ученика', example=2),
    'title': fields.String(description='Название задания', example='Подтягивания'),
    'description': fields.String(description='Описание задания', example='Сгибание рук на турнике'),
    'due_date': fields.String(description='Дата выполнения задания в формате YYYY-MM-DD', example='2023-12-31')
})



@task_routes.route('/create_task')
class CreateTask(Resource):
    @jwt_required()
    @task_routes.doc(
        description="Создать новое задание для ученика от имени тренера.",
        responses={
            201: "Задание успешно создано",
            400: "Некорректные данные запроса",
            401: "Неавторизованный доступ"
        },
        params={
            "Authorization": {
                "description": "JWT access token. Формат: Bearer {token}",
                "in": "header",
                "type": "string",
                "required": True
            }
        }
    )
    @task_routes.expect(task_model)
    @task_routes.marshal_with(task_model_response, code=201)
    def post(self):
        data = request.json
        trainer_id = data.get('trainer_id')
        student_id = data.get('student_id')
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')

        new_task = Task(
            trainer_id=trainer_id,
            student_id=student_id,
            title=title,
            description=description,
            due_date=due_date
        )
        db.session.add(new_task)

        user = User.query.filter_by(id=student_id).first()
        if user:
            user.trainer_id = trainer_id

        db.session.commit()

        return new_task, 201