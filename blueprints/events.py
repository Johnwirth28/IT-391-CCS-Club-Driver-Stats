from flask import Blueprint, jsonify, request
from datetime import datetime

api_events = Blueprint('api_events', __name__)

def init_event_routes(event_repo, event_chair_repo, event_session_repo):
    @api_events.route('/api/events', methods=['GET', 'POST'])
    def events():
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
            if 'event_name' not in data or 'event_link' not in data:
                return jsonify({'error': 'Missing required fields: event_name and event_link'}), 400

            try:
                event_id = event_repo.create_event(
                    data['event_name'],
                    data['event_link'],
                    data.get('event_notes'),
                    data.get('location_id')
                )
                return jsonify({'id': event_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            events = event_repo.get_events()
            return jsonify(events)

    @api_events.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
    def event(event_id):
        if request.method == 'GET':
            event = event_repo.get_event(event_id)
            if event:
                return jsonify(event)
            return {'error': 'Event not found'}, 404
        elif request.method == 'PUT':
            event_repo.update_event(event_id, request.json)
            return '', 204
        else:  # DELETE
            event_repo.delete_event(event_id)
            return '', 204

    @api_events.route('/api/event-chairs', methods=['GET', 'POST'])
    def event_chairs():
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
            if 'event_id' not in data or 'chair_name' not in data:
                return jsonify({'error': 'Missing required fields: event_id and chair_name'}), 400
            
            try:
                chair_id = event_chair_repo.create_event_chair(
                    data['event_id'],
                    data['chair_name']
                )
                return jsonify({'id': chair_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            chairs = event_chair_repo.get_all_event_chairs()
            return jsonify(chairs)

    @api_events.route('/api/event-sessions', methods=['GET', 'POST'])
    def event_sessions():
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
            if 'evt_session_date' not in data or 'event_id' not in data:
                return jsonify({'error': 'Missing required fields: evt_session_date and event_id'}), 400
            
            try:
                session_date = datetime.strptime(data['evt_session_date'], '%Y-%m-%d').date()
                session_id = event_session_repo.create_event_session(
                    session_date,
                    data['event_id']
                )
                return jsonify({'id': session_id}), 201
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            event_id = request.args.get('event_id', type=int)
            sessions = event_session_repo.get_event_sessions(event_id)
            return jsonify(sessions)