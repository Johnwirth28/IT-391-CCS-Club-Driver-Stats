from flask import Flask, Blueprint, jsonify, request

api_cars = Blueprint('api_cars', __name__)

def init_car_routes(car_repo):
    @api_cars.route('/api/cars', methods=['GET', 'POST'])
    def cars():
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
            required_fields = ['car_driver_name', 'car_year', 'car_make', 'car_model']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
            try:
                car_id = car_repo.create_car(
                    data['car_driver_name'],
                    data['car_year'],
                    data['car_make'],
                    data['car_model'],
                    data.get('wheelbase'),
                    data.get('mods'),
                    data.get('tire_description'),
                    data.get('weight')
                )
                return jsonify({'id': car_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            try:
                # Check for query parameters
                driver_name = request.args.get('driver')
                make = request.args.get('make')
                model = request.args.get('model')
                
                if driver_name:
                    cars = car_repo.get_cars_by_driver(driver_name)
                elif make:
                    cars = car_repo.get_cars_by_make_model(make, model)
                else:
                    cars = car_repo.get_cars()
                    
                return jsonify(cars)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @api_cars.route('/api/cars/<int:car_id>', methods=['GET', 'PUT', 'DELETE'])
    def car(car_id):
        if request.method == 'GET':
            try:
                car = car_repo.get_car(car_id)
                if car:
                    return jsonify(car)
                return {'error': 'Car not found'}, 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            try:
                car_repo.update_car(car_id, data)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:  # DELETE
            try:
                car_repo.delete_car(car_id)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500