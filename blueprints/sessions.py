from flask import Blueprint, jsonify, request

api_sessions = Blueprint('api_sessions', __name__)

def init_session_routes(session_raw_repo, session_pax_repo, session_final_repo):
    # Session Raw Data routes
    @api_sessions.route('/api/session-raw', methods=['POST'])
    def create_session_raw():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
        required_fields = ['session_class_abrv', 'session_car_num', 'sr_raw_time', 'car_id', 'event_session_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        try:
            session_id = session_raw_repo.create_session_raw(
                data['session_class_abrv'],
                data['session_car_num'],
                data['sr_raw_time'],
                data['car_id'],
                data['event_session_id']
            )
            return jsonify({'id': session_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api_sessions.route('/api/session-raw/<int:session_id>', methods=['GET', 'PUT', 'DELETE'])
    def session_raw(session_id):
        if request.method == 'GET':
            try:
                include_car = request.args.get('include_car') == 'true'
                if include_car:
                    session = session_raw_repo.get_session_raw_with_car_details(session_id)
                else:
                    session = session_raw_repo.get_session_raw(session_id)
                if session:
                    return jsonify(session)
                return {'error': 'Raw session data not found'}, 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            try:
                session_raw_repo.update_session_raw(session_id, data)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:  # DELETE
            try:
                session_raw_repo.delete_session_raw(session_id)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    # Session PAX Data routes
    @api_sessions.route('/api/session-pax', methods=['POST'])
    def create_session_pax():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
        required_fields = ['session_class_abrv', 'session_car_num', 'sp_raw_time', 
                          'sp_pax_factor', 'sp_pax_time', 'car_id', 'event_session_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        try:
            session_id = session_pax_repo.create_session_pax(
                data['session_class_abrv'],
                data['session_car_num'],
                data['sp_raw_time'],
                data['sp_pax_factor'],
                data['sp_pax_time'],
                data['car_id'],
                data['event_session_id']
            )
            return jsonify({'id': session_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api_sessions.route('/api/session-raw/search', methods=['GET'])
    def search_raw_sessions():
        try:
            car_id = request.args.get('car_id')
            driver = request.args.get('driver')
            
            if car_id:
                sessions = session_raw_repo.get_session_raw_by_car(int(car_id))
            elif driver:
                sessions = session_raw_repo.get_session_raw_by_driver(driver)
            else:
                return jsonify({'error': 'Either car_id or driver parameter is required'}), 400
                
            return jsonify(sessions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api_sessions.route('/api/session-pax/<int:session_id>', methods=['GET', 'PUT', 'DELETE'])
    def session_pax(session_id):
        if request.method == 'GET':
            try:
                include_car = request.args.get('include_car') == 'true'
                if include_car:
                    session = session_pax_repo.get_session_pax_with_car_details(session_id)
                else:
                    session = session_pax_repo.get_session_pax(session_id)
                if session:
                    return jsonify(session)
                return {'error': 'PAX session data not found'}, 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            try:
                session_pax_repo.update_session_pax(session_id, data)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:  # DELETE
            try:
                session_pax_repo.delete_session_pax(session_id)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @api_sessions.route('/api/session-pax/search', methods=['GET'])
    def search_pax_sessions():
        try:
            car_id = request.args.get('car_id')
            driver = request.args.get('driver')
            
            if car_id:
                sessions = session_pax_repo.get_session_pax_by_car(int(car_id))
            elif driver:
                sessions = session_pax_repo.get_session_pax_by_driver(driver)
            else:
                return jsonify({'error': 'Either car_id or driver parameter is required'}), 400
                
            return jsonify(sessions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Session Final Data routes
    @api_sessions.route('/api/session-final', methods=['POST'])
    def create_session_final():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
        required_fields = ['session_class_abrv', 'session_car_num', 'sf_has_trophy', 
                          'sf_car_color', 'car_id', 'event_session_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        try:
            session_id = session_final_repo.create_session_final(
                data['session_class_abrv'],
                data['session_car_num'],
                data['sf_has_trophy'],
                data['sf_car_color'],
                data['car_id'],
                data['event_session_id']
            )
            return jsonify({'id': session_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api_sessions.route('/api/session-final/<int:session_id>', methods=['GET', 'PUT', 'DELETE'])
    def session_final(session_id):
        if request.method == 'GET':
            try:
                include_car = request.args.get('include_car') == 'true'
                include_runs = request.args.get('include_runs') == 'true'
                
                if include_car and include_runs:
                    session = session_final_repo.get_session_final_with_car_details(session_id)
                    if session:
                        runs = session_final_repo.get_session_final_with_runs(session_id)
                        session['runs'] = runs.get('runs', [])
                elif include_car:
                    session = session_final_repo.get_session_final_with_car_details(session_id)
                elif include_runs:
                    session = session_final_repo.get_session_final_with_runs(session_id)
                else:
                    session = session_final_repo.get_session_final(session_id)
                    
                if session:
                    return jsonify(session)
                return {'error': 'Final session data not found'}, 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            try:
                session_final_repo.update_session_final(session_id, data)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:  # DELETE
            try:
                session_final_repo.delete_session_final(session_id)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
    @api_sessions.route('/api/session-final/search', methods=['GET'])
    def search_final_sessions():
        try:
            car_id = request.args.get('car_id')
            driver = request.args.get('driver')
            include_runs = request.args.get('include_runs') == 'true'
            
            if car_id:
                sessions = session_final_repo.get_session_final_by_car(int(car_id))
            elif driver:
                sessions = session_final_repo.get_session_final_by_driver(driver)
            else:
                return jsonify({'error': 'Either car_id or driver parameter is required'}), 400
            
            if include_runs and sessions:
                for session in sessions:
                    runs = session_final_repo.get_session_final_with_runs(session['session_data_id'])
                    session['runs'] = runs.get('runs', [])
                    
            return jsonify(sessions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500