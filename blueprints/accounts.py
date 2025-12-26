from flask import Blueprint, jsonify, request
from typing import Dict, Any

api_accounts = Blueprint('api_accounts', __name__)

def init_account_routes(account_repo):
    @api_accounts.route('/api/accounts', methods=['GET', 'POST'])
    def accounts():
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            
            required_fields = ['username', 'drivername', 'email', 'password']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
            try:
                account_id = account_repo.create_account(
                    data['username'],
                    data['drivername'],
                    data['email'],
                    data['password']
                )
                return jsonify({'id': account_id}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            try:
                accounts = account_repo.get_accounts()
                return jsonify(accounts)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @api_accounts.route('/api/accounts/<email>', methods=['GET', 'PUT', 'DELETE'])
    def account(email):
        if request.method == 'GET':
            try:
                account = account_repo.get_account_by_email(email)
                if account:
                    return jsonify(account)
                return {'error': 'Account not found'}, 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided or invalid JSON'}), 400
            try:
                account_repo.update_account(email, data)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:  # DELETE
            try:
                account_repo.delete_account(email)
                return '', 204
            except Exception as e:
                return jsonify({'error': str(e)}), 500