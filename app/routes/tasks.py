from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Task


task_routes = Namespace('tasks')

@task_routes.route('/task')
class CreateTask(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        trainer_id = int(get_jwt_identity())
        student_id = data.get('student_id')
        title = data.get('title')
        type = data.get('type')
        duration = data.get('duration')
        intensity = data.get('intensity')
        description = data.get('description')
        date_time = data.get('date_time')

        if not all([student_id, title, description, date_time, type, duration, intensity]):
            return {"error": "Не все поля заполнены"}, 400

        new_task = Task(
            trainer_id=trainer_id,
            student_id=student_id,
            title=title,
            description=description,
            date_time=date_time,
            type=type,
            duration=duration,
            intensity=intensity
        )
        new_task.add_task()

        user = User.query.filter_by(id=student_id).first()
        if user:
            user.trainer_id = trainer_id

        db.session.commit()

        return new_task.to_dict(), 201

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        tasks = Task.query.filter(
            (Task.student_id == user_id) | (Task.trainer_id == user_id)
        ).all()

        return [
            task.to_dict() for task in tasks
        ], 200
    

@task_routes.route('/profile/students/<string:nickname>')
class StudentTasks(Resource):
    @jwt_required()
    def get(self, nickname):
        trainer_id = int(get_jwt_identity())

        trainer = User.query.filter_by(id=trainer_id, is_trainer=True).first()
        if not trainer:
            return {"error": "Доступ запрещен: вы не тренер"}, 403
        student = User.query.filter_by(nickname=nickname, trainer_id=trainer.id, is_trainer=False).first()
        if not student:
            return {"error": "Ученик не найден или не прикреплён к вам"}, 404

        tasks = Task.query.filter_by(student_id=student.id, trainer_id=trainer.id).all()

        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ]
        }, 200
