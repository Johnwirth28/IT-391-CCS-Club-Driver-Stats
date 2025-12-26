from flask import Blueprint, jsonify, request

api_weather = Blueprint('api_weather', __name__)

def init_weather_routes(weather_repo):
    @api_weather.route('/api/weather', methods=['POST'])
    def create_weather():
        data = request.json
        if not data:
            return 'Bad weather request',400
        weather_id = weather_repo.create_weather(
            data['cloud_cover'],
            data['humidity'],
            data['precip'],
            data['high_temp'],
            data['low_temp'],
            data['pressure'],
            data['wind_speed'],
            data['wind_dir'],
            data['event_session_id']
        )
        return jsonify({'id': weather_id}), 201

    @api_weather.route('/api/weather/<int:weather_id>', methods=['GET', 'PUT', 'DELETE'])
    def weather_data(weather_id):
        if request.method == 'GET':
            weather = weather_repo.get_weather(weather_id)
            if weather:
                return jsonify(weather)
            return {'error': 'Weather data not found'}, 404
        elif request.method == 'PUT':
            weather_repo.update_weather(weather_id, request.json)
            return '', 204
        else:  # DELETE
            weather_repo.delete_weather(weather_id)
            return '', 204

    @api_weather.route('/api/weather/session/<int:session_id>', methods=['GET'])
    def session_weather(session_id):
        weather = weather_repo.get_weather_for_session(session_id)
        return jsonify(weather)