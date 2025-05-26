#!/usr/bin/env python3
"""
Flask LLM Context Generator Setup Script
Creates all necessary files and folders for the application.
Run this script in your target project directory.
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create the necessary directory structure."""
    directories = [
        'templates',
        'static',
        'static/css',
        'static/js'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_requirements_txt():
    """Create requirements.txt with necessary dependencies."""
    requirements = """Flask==2.3.3
Werkzeug==2.3.7
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✓ Created requirements.txt")

def create_flask_app():
    """Create the main Flask application file."""
    app_content = """from flask import Flask, render_template, request, jsonify
import os
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

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
        
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
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

@app.route('/api/get-context', methods=['POST'])
def get_context():
    try:
        data = request.get_json()
        file_paths = data.get('file_paths', [])
        
        context_parts = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                context_parts.append(f"File: {filename}\\n```\\n{content}\\n```\\n")
            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        full_context = "\\n".join(context_parts)
        
        return jsonify({'context': full_context})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
    
    with open('app.py', 'w') as f:
        f.write(app_content)
    print("✓ Created app.py")

def create_html_template():
    """Create the main HTML template."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Context Generator</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-robot"></i> LLM Context Generator</h1>
            <p>Select files to generate context for your LLM prompts</p>
        </header>

        <div class="main-content">
            <!-- Directory Selection -->
            <div class="section">
                <h2><i class="fas fa-folder-open"></i> Select Directory</h2>
                <div class="directory-selector">
                    <input type="text" id="directoryInput" placeholder="Enter directory path..." class="directory-input">
                    <button id="browseBtn" class="btn btn-primary">
                        <i class="fas fa-search"></i> Browse
                    </button>
                    <input type="file" id="directoryPicker" webkitdirectory directory multiple style="display: none;">
                    <button id="pickDirectoryBtn" class="btn btn-secondary">
                        <i class="fas fa-folder"></i> Pick Folder
                    </button>
                </div>
                <div id="directoryError" class="error-message" style="display: none;"></div>
            </div>

            <!-- File Selection -->
            <div class="section">
                <h2><i class="fas fa-files"></i> File Selection</h2>
                <div class="file-controls">
                    <button id="addFileBtn" class="btn btn-success">
                        <i class="fas fa-plus"></i> Add File
                    </button>
                    <button id="clearAllBtn" class="btn btn-warning">
                        <i class="fas fa-trash"></i> Clear All
                    </button>
                </div>
                
                <div id="fileRows" class="file-rows">
                    <!-- File rows will be dynamically added here -->
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="section">
                <div class="action-buttons">
                    <button id="copyContextBtn" class="btn btn-primary btn-large" disabled>
                        <i class="fas fa-copy"></i> Copy Context to Clipboard
                    </button>
                    <button id="previewContextBtn" class="btn btn-secondary btn-large" disabled>
                        <i class="fas fa-eye"></i> Preview Context
                    </button>
                </div>
            </div>

            <!-- Context Preview -->
            <div id="contextPreview" class="section" style="display: none;">
                <div class="context-header">
                    <h2><i class="fas fa-eye"></i> Context Preview</h2>
                    <button id="clearPreviewBtn" class="btn btn-warning">
                        <i class="fas fa-times"></i> Clear
                    </button>
                </div>
                <div class="context-container">
                    <pre id="contextContent"></pre>
                </div>
            </div>
        </div>

        <!-- Toast Notifications -->
        <div id="toast" class="toast" style="display: none;">
            <div class="toast-content">
                <span id="toastMessage"></span>
                <button class="toast-close">&times;</button>
            </div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
"""
    
    with open('templates/index.html', 'w') as f:
        f.write(html_content)
    print("✓ Created templates/index.html")

def create_css_styles():
    """Create the CSS styles."""
    css_content = """/* Modern CSS Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    text-align: center;
    margin-bottom: 40px;
    color: white;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

.main-content {
    background: white;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.section {
    margin-bottom: 30px;
}

.section h2 {
    color: #4a5568;
    margin-bottom: 20px;
    font-size: 1.4rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Directory Selector */
.directory-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.directory-input {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.directory-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Buttons */
.btn {
    padding: 12px 20px;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.btn:active {
    transform: translateY(0);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.btn-success {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
}

.btn-warning {
    background: linear-gradient(135deg, #ed8936, #dd6b20);
    color: white;
}

.btn-secondary {
    background: linear-gradient(135deg, #a0aec0, #718096);
    color: white;
}

.btn-large {
    padding: 16px 24px;
    font-size: 1.1rem;
}

/* File Controls */
.file-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

/* File Rows */
.file-rows {
    border: 2px dashed #e2e8f0;
    border-radius: 10px;
    min-height: 100px;
    padding: 20px;
}

.file-row {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    background: #f7fafc;
    border-radius: 10px;
    margin-bottom: 10px;
    transition: all 0.3s ease;
}

.file-row:hover {
    background: #edf2f7;
    transform: translateX(5px);
}

.file-row input[type="checkbox"] {
    transform: scale(1.2);
    cursor: pointer;
}

.file-select {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.95rem;
    background: white;
}

.file-select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.remove-btn {
    background: #e53e3e;
    color: white;
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.remove-btn:hover {
    background: #c53030;
    transform: scale(1.1);
}

/* Action Buttons */
.action-buttons {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

/* Context Preview */
.context-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.context-header h2 {
    margin-bottom: 0;
}

.context-container {
    background: #1a202c;
    color: #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
}

#contextContent {
    padding: 20px;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
}

/* Toast Notifications */
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #48bb78;
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    z-index: 1000;
    animation: slideInRight 0.3s ease;
}

.toast.error {
    background: #e53e3e;
}

.toast-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.toast-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    opacity: 0.8;
}

.toast-close:hover {
    opacity: 1;
}

/* Error Messages */
.error-message {
    color: #e53e3e;
    font-size: 0.9rem;
    margin-top: 5px;
    padding: 8px 12px;
    background: #fed7d7;
    border-radius: 6px;
}

/* Animations */
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 15px;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .main-content {
        padding: 20px;
    }
    
    .directory-selector {
        flex-direction: column;
    }
    
    .file-row {
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
    }
    
    .action-buttons {
        flex-direction: column;
    }
    
    .btn-large {
        width: 100%;
        justify-content: center;
    }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #5a67d8;
}
"""
    
    with open('static/css/style.css', 'w') as f:
        f.write(css_content)
    print("✓ Created static/css/style.css")

def create_javascript():
    """Create the JavaScript application logic."""
    js_content = """
class ContextGenerator {
    constructor() {
        this.fileRowCounter = 0;
        this.availableFiles = [];
        this.selectedDirectory = '';
        this.init();
    }

    init() {
        this.bindEvents();
        this.addInitialFileRow();
    }

    bindEvents() {
        // Directory browsing
        document.getElementById('browseBtn').addEventListener('click', () => this.browseDirectory());
        document.getElementById('directoryInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.browseDirectory();
        });

        // File management
        document.getElementById('addFileBtn').addEventListener('click', () => this.addFileRow());
        document.getElementById('clearAllBtn').addEventListener('click', () => this.clearAllFiles());

        // Context actions
        document.getElementById('copyContextBtn').addEventListener('click', () => this.copyContext());
        document.getElementById('previewContextBtn').addEventListener('click', () => this.previewContext());

        // Toast close
        document.querySelector('.toast-close').addEventListener('click', () => this.hideToast());
    }

    handleDirectoryPicker(event) {
        const files = event.target.files;
        if (files.length > 0) {
            const firstFile = files[0];
            const directoryPath = firstFile.webkitRelativePath.split('/')[0];
            
            document.getElementById('directoryInput').value = directoryPath;
            this.browseDirectory();
        }
    }

    clearPreview() {
        const previewSection = document.getElementById('contextPreview');
        const contextContent = document.getElementById('contextContent');
        
        contextContent.textContent = '';
        previewSection.style.display = 'none';
    }

    async browseDirectory() {
        const directoryInput = document.getElementById('directoryInput');
        const directory = directoryInput.value.trim();
        const errorDiv = document.getElementById('directoryError');

        if (!directory) {
            this.showError('Please enter a directory path');
            return;
        }

        try {
            const response = await fetch('/api/browse-directory', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ directory })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to browse directory');
            }

            this.availableFiles = data.files;
            this.selectedDirectory = directory;
            this.updateFileSelectors();
            this.showToast('Directory loaded successfully!');
            errorDiv.style.display = 'none';

        } catch (error) {
            this.showError(error.message);
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        }
    }

    addFileRow() {
        const fileRows = document.getElementById('fileRows');
        const rowId = ++this.fileRowCounter;

        const fileRow = document.createElement('div');
        fileRow.className = 'file-row';
        fileRow.id = `fileRow-${rowId}`;

        fileRow.innerHTML = `
            <input type="checkbox" id="checkbox-${rowId}" onchange="contextGenerator.updateActionButtons()">
            <select class="file-select" id="select-${rowId}" onchange="contextGenerator.updateActionButtons()">
                <option value="">Select a file...</option>
            </select>
            <button class="remove-btn" onclick="contextGenerator.removeFileRow(${rowId})" title="Remove">
                <i class="fas fa-times"></i>
            </button>
        `;

        fileRows.appendChild(fileRow);
        this.updateFileSelectors();
        this.updateActionButtons();
    }

    addInitialFileRow() {
        this.addFileRow();
    }

    removeFileRow(rowId) {
        const fileRow = document.getElementById(`fileRow-${rowId}`);
        if (fileRow) {
            fileRow.remove();
            this.updateActionButtons();
        }
    }

    clearAllFiles() {
        const fileRows = document.getElementById('fileRows');
        fileRows.innerHTML = '';
        this.fileRowCounter = 0;
        this.addInitialFileRow();
        this.updateActionButtons();
    }

    updateFileSelectors() {
        const selects = document.querySelectorAll('.file-select');
        selects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Select a file...</option>';
            
            this.availableFiles.forEach(file => {
                const option = document.createElement('option');
                option.value = file.path;
                option.textContent = `${file.relative_path} (${this.formatFileSize(file.size)})`;
                select.appendChild(option);
            });
            
            if (currentValue && this.availableFiles.some(f => f.path === currentValue)) {
                select.value = currentValue;
            }
        });
    }

    updateActionButtons() {
        const checkboxes = document.querySelectorAll('.file-row input[type="checkbox"]');
        const selects = document.querySelectorAll('.file-select');
        
        let hasValidSelection = false;
        
        checkboxes.forEach((checkbox, index) => {
            if (checkbox.checked && selects[index].value) {
                hasValidSelection = true;
            }
        });

        document.getElementById('copyContextBtn').disabled = !hasValidSelection;
        document.getElementById('previewContextBtn').disabled = !hasValidSelection;
    }

    getSelectedFiles() {
        const selectedFiles = [];
        const checkboxes = document.querySelectorAll('.file-row input[type="checkbox"]');
        const selects = document.querySelectorAll('.file-select');
        
        checkboxes.forEach((checkbox, index) => {
            if (checkbox.checked && selects[index].value) {
                selectedFiles.push(selects[index].value);
            }
        });
        
        return selectedFiles;
    }

    async copyContext() {
        try {
            const selectedFiles = this.getSelectedFiles();
            
            if (selectedFiles.length === 0) {
                this.showError('No files selected');
                return;
            }

            const response = await fetch('/api/get-context', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file_paths: selectedFiles })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate context');
            }

            await navigator.clipboard.writeText(data.context);
            this.showToast(`Context from ${selectedFiles.length} file(s) copied to clipboard!`);

        } catch (error) {
            this.showError(`Failed to copy context: ${error.message}`);
        }
    }

    async previewContext() {
        try {
            const selectedFiles = this.getSelectedFiles();
            
            if (selectedFiles.length === 0) {
                this.showError('No files selected');
                return;
            }

            const response = await fetch('/api/get-context', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file_paths: selectedFiles })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate context');
            }

            const previewSection = document.getElementById('contextPreview');
            const contextContent = document.getElementById('contextContent');
            
            contextContent.textContent = data.context;
            previewSection.style.display = 'block';
            previewSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            this.showError(`Failed to preview context: ${error.message}`);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showToast(message, isError = false) {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        toastMessage.textContent = message;
        toast.className = `toast ${isError ? 'error' : ''}`;
        toast.style.display = 'block';
        
        setTimeout(() => this.hideToast(), 3000);
    }

    showError(message) {
        this.showToast(message, true);
    }

    hideToast() {
        const toast = document.getElementById('toast');
        toast.style.display = 'none';
    }
}

const contextGenerator = new ContextGenerator();
"""
    
    with open('static/js/app.js', 'w') as f:
        f.write(js_content)
    print("✓ Created static/js/app.js")

def create_run_script():
    """Create a run script for easy startup."""
    run_content = """#!/usr/bin/env python3

import subprocess
import sys
import os

def install_requirements():
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found. Please run setup.py first.")
        sys.exit(1)
    
    try:
        import flask
    except ImportError:
        print("Flask not found. Installing requirements...")
        install_requirements()
    
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
"""
    
    with open('run.py', 'w') as f:
        f.write(run_content)
    
    # Make it executable on Unix systems
    if os.name != 'nt':  # Not Windows
        os.chmod('run.py', 0o755)
    
    print("✓ Created run.py")

def main():
    """Main setup function."""
    print("🚀 Setting up Flask LLM Context Generator...")
    print("=" * 50)
    
    try:
        create_directory_structure()
        create_requirements_txt()
        create_flask_app()
        create_html_template()
        create_css_styles()
        create_javascript()
        create_run_script()
        
        print("=" * 50)
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python run.py")
        print("3. Open your browser to: http://localhost:5000")
        print("\n🎉 Happy coding!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()