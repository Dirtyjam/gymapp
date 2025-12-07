from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

report_routes = Namespace('summary', description='Summary related operations')

@report_routes.route('/report')
class SummaryReport(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        difficaulty = data.get('difficaulty')
        self_health = data.get('self_health')
        comment = data.get('comment')
        is_skip = data.get('is_skip')
        skip_reason = data.get('skip_reason')
        date = data.get('date')

        if is_skip and not skip_reason:
            return {"error": "Причина пропуска обязательна, если тренировка пропущена"}, 400
        
        new_report = SummaryReport(
            difficaulty=difficaulty,
            self_health=self_health,
            comment=comment,
            is_skip=is_skip,
            skip_reason=skip_reason,
            user_id=user_id, 
            date=date
        )
        new_report.add_report()

        return new_report.to_dict(), 201
    

    @jwt_required()
    def get(self):
        reports = SummaryReport.query.all()
        return [report.to_dict() for report in reports], 200