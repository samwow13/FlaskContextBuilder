from flask import Blueprint, jsonify, request, current_app
import os
import json

custom_instructions_bp = Blueprint('custom_instructions_bp', __name__)

# Define the path for the custom instructions file relative to the application root
INSTRUCTIONS_FILE_NAME = 'custom_instructions.json'

def get_instructions_file_path():
    return os.path.join(current_app.root_path, INSTRUCTIONS_FILE_NAME)

@custom_instructions_bp.route('/api/custom-instructions', methods=['GET'])
def get_custom_instructions():
    instructions_file = get_instructions_file_path()
    try:
        if os.path.exists(instructions_file):
            with open(instructions_file, 'r') as f:
                data = json.load(f)
                return jsonify({"instructions": data.get("instructions", "")})
        else:
            # If file doesn't exist, return empty instructions
            return jsonify({"instructions": ""})
    except Exception as e:
        current_app.logger.error(f"Error reading custom instructions file: {e}")
        return jsonify({"error": "Failed to load custom instructions"}), 500

@custom_instructions_bp.route('/api/custom-instructions', methods=['POST'])
def save_custom_instructions():
    instructions_file = get_instructions_file_path()
    try:
        data = request.json
        instructions = data.get('instructions')
        if instructions is None:
            return jsonify({"error": "No instructions provided"}), 400

        with open(instructions_file, 'w') as f:
            json.dump({"instructions": instructions}, f, indent=4)
        
        current_app.logger.info(f"Custom instructions saved to {instructions_file}")
        return jsonify({"message": "Custom instructions saved successfully!"}), 200
    except Exception as e:
        current_app.logger.error(f"Error saving custom instructions file: {e}")
        return jsonify({"error": "Failed to save custom instructions"}), 500
