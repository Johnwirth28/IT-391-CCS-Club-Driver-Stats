from flask import Blueprint, jsonify, request

api_runs = Blueprint('api_runs', __name__)

def init_run_routes(run_repo):
    @api_runs.route('/api/runs', methods=['POST'])
    def create_run():
        data = request.json
        if not data:
            return 'Bad run request', 400
        run_id = run_repo.create_run(
            data['run_time'],
            data['is_dnf'],
            data['num_penalties'],
            data['fsession_id']
        )
        return jsonify({'id': run_id}), 201

    @api_runs.route('/api/runs/<int:run_id>', methods=['GET', 'PUT', 'DELETE'])
    def run(run_id):
        if request.method == 'GET':
            run = run_repo.get_run(run_id)
            if run:
                return jsonify(run)
            return {'error': 'Run not found'}, 404
        elif request.method == 'PUT':
            run_repo.update_run(run_id, request.json)
            return '', 204
        else:  # DELETE
            run_repo.delete_run(run_id)
            return '', 204

    @api_runs.route('/api/runs/session/<int:fsession_id>', methods=['GET'])
    def runs_by_session(fsession_id):
        runs = run_repo.get_runs_by_final_session(fsession_id)
        return jsonify(runs)