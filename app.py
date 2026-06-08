from flask import Flask, render_template, request, jsonify
from core.engine import GameEngine
import os

app = Flask(__name__)

# Instantiate and configure global game session loop mechanics
session_engine = GameEngine()
session_engine.initialize_game_session()

@app.route('/')
def dashboard_home():
    """Renders the master asynchronous dashboard interface."""
    current_state = session_engine.package_current_state()
    return render_template('index.html', state=current_state)

@app.route('/api/command', methods=['POST'])
def route_asynchronous_command():
    """Intercepts client actions, executes data updates, and syncs UI views."""
    payload = request.json or {}
    action_type = payload.get('action_type', '')
    argument = payload.get('argument', '')

    # Mutate data records inside core tracking scripts
    feedback_log = session_engine.execute_action_command(action_type, argument)
    
    # Recapture fresh updated session models
    updated_state = session_engine.package_current_state()
    
    return jsonify({
        "log": feedback_log,
        "state": updated_state
    })

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)