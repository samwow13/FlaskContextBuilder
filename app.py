from flask import Flask, render_template, request, jsonify
import os
import json
from pathlib import Path
import fnmatch


app = Flask(__name__)

# Import and register blueprints
from custom_instructions_routes import custom_instructions_bp
from prompt_builder_routes import prompt_builder_bp
from exclusion_manager_routes import exclusion_manager_bp

app.register_blueprint(custom_instructions_bp)
app.register_blueprint(prompt_builder_bp)
app.register_blueprint(exclusion_manager_bp)
app.secret_key = 'your-secret-key-change-this'

# Utility function to load exclude patterns
def load_exclude_patterns():
    exclude_file = os.path.join(os.path.dirname(__file__), 'file_exclude_patterns.json')
    if not os.path.exists(exclude_file):
        return {'exclude_dirs': [], 'exclude_files': [], 'exclude_patterns': []}
    with open(exclude_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_excluded(path, filename, rel_root, patterns):
    # Check directory exclusion
    for ex_dir in patterns.get('exclude_dirs', []):
        if ex_dir and ex_dir in rel_root.split(os.sep):
            return True
    # Check file exclusion
    if filename in patterns.get('exclude_files', []):
        return True
    # Check pattern exclusion
    for pat in patterns.get('exclude_patterns', []):
        if fnmatch.fnmatch(filename, pat):
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/browse-directory', methods=['POST'])
def browse_directory():
    try:
        data = request.get_json()
        directory = data.get('directory', '')

        if not directory or not os.path.exists(directory):
            return jsonify({'error': 'Directory does not exist'}), 400

        exclude_patterns = load_exclude_patterns()
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                # Filter directories in-place to skip excluded ones
                rel_root = os.path.relpath(root, directory)
                dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d), d, os.path.join(rel_root, d), exclude_patterns)]
                for filename in filenames:
                    if is_excluded(os.path.join(root, filename), filename, rel_root, exclude_patterns):
                        continue
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, directory)
                    try:
                        file_size = os.path.getsize(file_path)
                        files.append({
                            'name': filename,
                            'path': file_path,
                            'relative_path': relative_path,
                            'size': file_size
                        })
                    except (OSError, PermissionError):
                        continue
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403

        return jsonify({'files': files})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/read-file', methods=['POST'])
def read_file():
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File does not exist'}), 400
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({
                'content': content,
                'filename': os.path.basename(file_path),
                'path': file_path
            })
        
        except UnicodeDecodeError:
            return jsonify({'error': 'File is not a text file or uses unsupported encoding'}), 400
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-line-count', methods=['POST'])
def get_line_count():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        selected_directory = data.get('selected_directory')
        if not file_path or not selected_directory:
            return jsonify({'error': 'Missing file_path or selected_directory'}), 400
        # Normalize paths
        norm_file = os.path.abspath(file_path)
        norm_dir = os.path.abspath(selected_directory)
        # Security: file must be inside selected_directory
        if not os.path.commonpath([norm_file, norm_dir]) == norm_dir:
            return jsonify({'error': 'Unauthorized file access'}), 403
        if not os.path.isfile(norm_file):
            return jsonify({'error': 'File does not exist'}), 404
        try:
            with open(norm_file, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for _ in f)
            return jsonify({'line_count': line_count})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-context', methods=['POST'])
def get_context():
    try:
        data = request.get_json()
        file_paths = data.get('file_paths', [])
        selected_directory = data.get('selected_directory')
        
        files_data = [] # Changed from context_parts
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f: # Added errors='ignore'
                    content = f.read()
                
                display_path = os.path.basename(file_path) # Default to basename
                if selected_directory:
                    norm_selected_dir = os.path.normpath(selected_directory)
                    norm_file_path = os.path.normpath(file_path)
                    if os.path.commonpath([norm_file_path, norm_selected_dir]) == norm_selected_dir:
                        display_path = os.path.relpath(norm_file_path, norm_selected_dir)

                display_path = display_path.replace('\\', '/')
                
                # Append a dictionary for each file
                files_data.append({
                    'path': display_path,
                    'content': content
                })
            
            except PermissionError:
                # Optionally, log this error or notify the user about skipped files due to permissions
                print(f"Permission denied for file: {file_path}")
                files_data.append({
                    'path': display_path, 
                    'content': f"Error: Could not read file {display_path} due to permissions."
                })
                continue
            except Exception as e:
                # Handle other potential errors during file reading for a specific file
                print(f"Error reading file {file_path}: {e}")
                files_data.append({
                    'path': display_path, 
                    'content': f"Error: Could not read file {display_path}. {str(e)}"
                })
                continue
        
        return jsonify({'files': files_data}) # Return list of file objects
    
    except Exception as e:
        # General error for the endpoint
        print(f"Error in get_context endpoint: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
