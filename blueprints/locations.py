from flask import Blueprint, jsonify, request

api_locations = Blueprint('api_locations', __name__)

def init_location_routes(location_repo):
    @api_locations.route('/api/locations', methods=['GET', 'POST'])
    def locations():
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
            if 'lat' not in data or 'lon' not in data:
                return jsonify({'error': 'Missing required fields: lat and lon'}), 400
            
            try:
                location_id = location_repo.create_location(
                    data['lat'],
                    data['lon'],
                    data.get('surface_type'),
                    data.get('course_map_url')
                )
                return jsonify({'id': location_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            try:
                locations = location_repo.get_locations()
                return jsonify(locations)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @api_locations.route('/api/locations/<int:location_id>', methods=['GET', 'PUT', 'DELETE'])
    def location(location_id):
        if request.method == 'GET':
            try:
                location = location_repo.get_location(location_id)
                if location:
                    return jsonify(location)
                return {'error': 'Location not found'}, 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            try:
                location_repo.update_location(location_id, data)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:  # DELETE
            try:
                location_repo.delete_location(location_id)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500