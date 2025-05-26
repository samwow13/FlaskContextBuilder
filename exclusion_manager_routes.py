from flask import Blueprint, jsonify, request
import os
import json

exclusion_manager_bp = Blueprint('exclusion_manager_bp', __name__)
EXCLUSION_FILE = os.path.join(os.path.dirname(__file__), 'file_exclude_patterns.json')

def load_exclusions():
    if not os.path.exists(EXCLUSION_FILE):
        return {'exclude_dirs': [], 'exclude_files': [], 'exclude_patterns': []}
    with open(EXCLUSION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_exclusions(data):
    with open(EXCLUSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

@exclusion_manager_bp.route('/api/exclusions', methods=['GET'])
def get_exclusions():
    return jsonify(load_exclusions())

@exclusion_manager_bp.route('/api/exclusions', methods=['POST'])
def set_exclusions():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid data'}), 400
    # Ensure all keys exist and are lists
    for k in ['exclude_dirs', 'exclude_files', 'exclude_patterns']:
        if k not in data or not isinstance(data[k], list):
            data[k] = []
    save_exclusions(data)
    return jsonify({'message': 'Exclusions updated successfully.'})
