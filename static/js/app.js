class ContextGenerator {
    constructor() {
        this.fileRowCounter = 0;
        this.availableFiles = [];
        this.selectedDirectory = '';
        this.fileLineCounts = {}; // Cache: filePath -> line count
        this.totalLinesOfCode = 0;
        this.init();
    }

    init() {
        this.bindEvents();
        this.addInitialFileRow();
    }

    bindEvents() {
        // LOC listeners
        document.addEventListener('change', (e) => {
            if (e.target.matches('.file-row input[type="checkbox"], .file-select')) {
                this.recalculateTotalLines();
            }
        });
    
        document.getElementById('pickDirectoryBtn').addEventListener('click', () => this.promptForDirectory());
        document.getElementById('addFileBtn').addEventListener('click', () => this.addFileRow());
        document.getElementById('clearAllBtn').addEventListener('click', () => this.clearAllFiles());
        document.getElementById('copyContextBtn').addEventListener('click', () => this.copyContext());
        document.getElementById('previewContextBtn').addEventListener('click', () => this.previewContext());
        document.querySelector('.toast-close').addEventListener('click', () => this.hideToast());
        document.getElementById('clearPreviewBtn').addEventListener('click', () => this.clearPreview());
    }

    promptForDirectory() {
        const path = window.prompt('Please enter the full directory path:', this.selectedDirectory || '');
        if (path && path.trim() !== '') {
            this.selectedDirectory = path.trim();
            this.browseDirectory();
        } else if (path !== null) { // User clicked OK but entered nothing or only whitespace
            this.showError('Directory path cannot be empty.');
        }
    }
    
    clearPreview() {
        const previewSection = document.getElementById('contextPreview');
        const contextContent = document.getElementById('contextContent');
        contextContent.innerHTML = ''; // Use innerHTML to clear all child elements
        previewSection.style.display = 'none';
    }

    async browseDirectory() {
        const directory = this.selectedDirectory;
        const errorDiv = document.getElementById('directoryError');
        errorDiv.style.display = 'none'; // Hide previous errors

        if (!directory) {
            this.showError('Please enter a directory path');
            return;
        }
        // Reset LOC cache and display on directory change
        this.fileLineCounts = {};
        this.totalLinesOfCode = 0;
        this.updateLinesOfCodeDisplay();

        try {
            const response = await fetch('/api/browse-directory', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ directory })
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to browse directory');
            }
            this.availableFiles = data.files;
            const fullPath = this.selectedDirectory;
            // Replace backslashes with forward slashes for consistent splitting, then split by forward slash
            const parts = fullPath.replace(/\\/g, '/').split('/');
            // Get the last part, or a default if the path is somehow empty or malformed
            const folderName = parts.pop() || parts.pop() || 'Project'; // Handles trailing slash and gets last element
            document.getElementById('currentProjectNameDisplay').textContent = folderName || 'No Project Selected'; // Ensure a fallback
            this.updateFileSelectors(); // Update all selectors with new files
            this.showToast('Directory loaded successfully!');
        } catch (error) {
            this.showError(error.message);
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
            this.availableFiles = []; // Clear available files on error
            this.updateFileSelectors(); // Reflect that no files are available
        }
    }

    addFileRow() {
        // After adding a row, update LOC display
        setTimeout(() => this.recalculateTotalLines(), 0);
        const fileRows = document.getElementById('fileRows');
        const rowId = ++this.fileRowCounter;
        const fileRow = document.createElement('div');
        fileRow.className = 'file-row';
        fileRow.id = `fileRow-${rowId}`;
        fileRow.innerHTML = `
            <input type="checkbox" id="checkbox-${rowId}" onchange="contextGenerator.updateActionButtons()">
            <select class="file-select" id="select-${rowId}" onchange="contextGenerator.handleFileSelectChange(event)">
                <option value="">Select a file...</option>
            </select>
            <button class="remove-btn" onclick="contextGenerator.removeFileRow(${rowId})" title="Remove">
                <i class="fas fa-times"></i>
            </button>
        `;
        fileRows.appendChild(fileRow);
        this.updateFileSelectorsForRow(fileRow.querySelector('.file-select'));
        this.updateActionButtons();
    }
    
    handleFileSelectChange(event) {
        setTimeout(() => this.recalculateTotalLines(), 0);
        const selectElement = event.target;
        if (selectElement.value) {
            selectElement.classList.add('file-select-bold');
        } else {
            selectElement.classList.remove('file-select-bold');
        }
        this.updateActionButtons();
    }

    addInitialFileRow() {
        this.addFileRow();
    }

    removeFileRow(rowId) {
        setTimeout(() => this.recalculateTotalLines(), 0);
        const fileRow = document.getElementById(`fileRow-${rowId}`);
        if (fileRow) {
            fileRow.remove();
            this.updateActionButtons();
        }
    }

    clearAllFiles() {
        setTimeout(() => this.recalculateTotalLines(), 0);
        const fileRows = document.getElementById('fileRows');
        fileRows.innerHTML = '';
        this.fileRowCounter = 0;
        this.addInitialFileRow(); // Add one empty row back
        this.updateActionButtons();
        this.clearPreview(); // Also clear the preview section
    }
    
    updateFileSelectors() {
        const selects = document.querySelectorAll('.file-select');
        selects.forEach(select => this.updateFileSelectorsForRow(select));
    }

    updateFileSelectorsForRow(selectElement) {
        const currentValue = selectElement.value;
        selectElement.innerHTML = '<option value="">Select a file...</option>'; // Clear existing options
        this.availableFiles.forEach(file => {
            const option = document.createElement('option');
            option.value = file.path; // Full path for backend
            option.textContent = `${file.relative_path} (${this.formatFileSize(file.size)})`;
            selectElement.appendChild(option);
        });
        // Restore previous selection if still valid
        if (currentValue && this.availableFiles.some(f => f.path === currentValue)) {
            selectElement.value = currentValue;
            selectElement.classList.add('file-select-bold');
        } else {
            selectElement.classList.remove('file-select-bold');
        }
    }

    updateActionButtons() {
        this.recalculateTotalLines();
        const hasValidSelection = this.getSelectedFiles().length > 0;
        // Enable buttons if custom instructions might be available OR files are selected
        // This logic will be refined by the copy/preview methods themselves
        document.getElementById('copyContextBtn').disabled = false; 
        document.getElementById('previewContextBtn').disabled = false;
    }

    getSelectedFiles() {
        const selectedFiles = [];
        const checkboxes = document.querySelectorAll('.file-row input[type="checkbox"]');
        const selects = document.querySelectorAll('.file-select');
        checkboxes.forEach((checkbox, index) => {
            if (checkbox.checked && selects[index] && selects[index].value) {
                selectedFiles.push(selects[index].value);
            }
        });
        return selectedFiles;
    }

    async getFormattedCustomInstructions() {
        try {
            const response = await fetch('/api/custom-instructions');
            if (!response.ok) {
                console.error('Failed to fetch custom instructions:', response.status);
                return { fullText: '', header: '', userInstructions: '', rawInstructions: '', error: true };
            }
            const data = await response.json();
            if (data.instructions && data.instructions.trim() !== '') {
                const rawInstructions = data.instructions.trim();
                const header = "Custom Instructions for LLM";
                const userInstructionsContent = `User Instructions: ${rawInstructions}`;
                const fullText = `${header}\n${userInstructionsContent}\n\n---\n\n`;
                return { fullText, header, userInstructions: userInstructionsContent, rawInstructions, error: false };
            }
            return { fullText: '', header: '', userInstructions: '', rawInstructions: '', error: false };
        } catch (error) {
            console.error('Error fetching or formatting custom instructions:', error);
            return { fullText: '', header: '', userInstructions: '', rawInstructions: '', error: true };
        }
    }

    async copyContext() {
        try {
            const customInstructionsData = await this.getFormattedCustomInstructions();
            const selectedFiles = this.getSelectedFiles();
            let contextToCopy = '';
            let messageParts = [];
    
            if (customInstructionsData.rawInstructions) {
                if (selectedFiles.length === 0) {
                    contextToCopy = `${customInstructionsData.header}\n${customInstructionsData.userInstructions}`;
                } else {
                    contextToCopy = customInstructionsData.fullText;
                }
                messageParts.push('custom instructions');
            } else if (customInstructionsData.error && selectedFiles.length === 0) {
                this.showError('Failed to load custom instructions. No files selected to copy.');
                return;
            }
    
    
            if (selectedFiles.length > 0) {
                const response = await fetch('/api/get-context', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_paths: selectedFiles, selected_directory: this.selectedDirectory })
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to generate context for copy');
                }
    
                if (data.files && data.files.length > 0) {
                    const filesContext = data.files.map(file =>
                        `File: ${file.path}\n\`\`\`\n${file.content}\n\`\`\`\n`
                    ).join('\n');
                    contextToCopy += filesContext; 
                    messageParts.push(`${selectedFiles.length} file(s)`);
                } else if (data.error && !customInstructionsData.rawInstructions) { 
                    throw new Error(data.error);
                }
            }
    
            if (contextToCopy.trim() === '') {
                this.showError('No content selected or available to copy.');
                return;
            }
    
            await navigator.clipboard.writeText(contextToCopy.trim());
            let toastMessage = 'Context copied to clipboard!';
            if (messageParts.length > 0) {
                toastMessage = `Copied ${messageParts.join(' and ')} to clipboard!`;
            }
            this.showToast(toastMessage);
    
        } catch (error) {
            this.showError(`Failed to copy context: ${error.message}`);
        }
    }
    
    async previewContext() {
        try {
            const customInstructionsData = await this.getFormattedCustomInstructions();
            const selectedFiles = this.getSelectedFiles();
    
            const previewSection = document.getElementById('contextPreview');
            const contextContent = document.getElementById('contextContent');
            contextContent.innerHTML = ''; 
            let contentExists = false;
    
            if (customInstructionsData.rawInstructions) {
                const instructionsHeaderDiv = document.createElement('div');
                instructionsHeaderDiv.classList.add('file-preview-path'); 
                instructionsHeaderDiv.style.fontWeight = 'bold';
                instructionsHeaderDiv.textContent = customInstructionsData.header;
                contextContent.appendChild(instructionsHeaderDiv);
    
                const instructionsContentPre = document.createElement('pre');
                instructionsContentPre.classList.add('file-preview-content'); 
                instructionsContentPre.textContent = customInstructionsData.userInstructions; 
                contextContent.appendChild(instructionsContentPre);
    
                const separator = document.createElement('hr');
                separator.style.margin = "10px 0";
                contextContent.appendChild(separator);
                contentExists = true;
            } else if (customInstructionsData.error && selectedFiles.length === 0) {
                const errorP = document.createElement('p');
                errorP.classList.add('error-message');
                errorP.textContent = 'Failed to load custom instructions. No files selected for preview.';
                contextContent.appendChild(errorP);
                previewSection.style.display = 'block';
                return; 
            }
    
    
            if (selectedFiles.length > 0) {
                const response = await fetch('/api/get-context', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_paths: selectedFiles, selected_directory: this.selectedDirectory })
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to generate context for preview');
                }
    
                if (data.files && data.files.length > 0) {
                    data.files.forEach((file, index) => {
                        const fileContainer = document.createElement('div');
                        fileContainer.classList.add('file-preview-item');
                        fileContainer.classList.add(index % 2 === 0 ? 'even-bg' : 'odd-bg');
    
                        const filePathElement = document.createElement('div');
                        filePathElement.classList.add('file-preview-path');
                        filePathElement.textContent = `File: ${file.path}`;
    
                        const fileContentElement = document.createElement('pre');
                        fileContentElement.classList.add('file-preview-content');
                        fileContentElement.textContent = file.content;
    
                        fileContainer.appendChild(filePathElement);
                        fileContainer.appendChild(fileContentElement);
                        contextContent.appendChild(fileContainer);
                    });
                    contentExists = true;
                } else if (data.error && !contentExists) { 
                    throw new Error(data.error);
                }
            }
    
            if (contentExists) {
                previewSection.style.display = 'block';
                previewSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                contextContent.textContent = 'No content to preview (no custom instructions or files selected).';
                previewSection.style.display = 'block';
            }
    
        } catch (error) {
            this.showError(`Failed to preview context: ${error.message}`);
            const previewSection = document.getElementById('contextPreview');
            const contextContent = document.getElementById('contextContent');
            contextContent.innerHTML = `<p class="error-message">Error previewing context: ${error.message}</p>`;
            previewSection.style.display = 'block';
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
        if (toast && toastMessage) { // Check if elements exist
            toastMessage.textContent = message;
            toast.className = `toast ${isError ? 'error' : ''}`; // Ensure "toast" class is always present
            toast.style.display = 'block';
            setTimeout(() => this.hideToast(), 3000);
        }
    }

    showError(message) {
        this.showToast(message, true);
    }

    hideToast() {
        const toast = document.getElementById('toast');
        if (toast) { // Check if toast element exists
            toast.style.display = 'none';
        }
    }
    // --- LOC Feature Methods ---
    async fetchLineCount(filePath) {
        if (this.fileLineCounts[filePath] !== undefined) {
            return this.fileLineCounts[filePath];
        }
        try {
            const response = await fetch('/api/get-line-count', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_path: filePath, selected_directory: this.selectedDirectory })
            });
            const data = await response.json();
            if (response.ok && typeof data.line_count === 'number') {
                this.fileLineCounts[filePath] = data.line_count;
                return data.line_count;
            } else {
                this.fileLineCounts[filePath] = 0;
                return 0;
            }
        } catch (e) {
            this.fileLineCounts[filePath] = 0;
            return 0;
        }
    }

    async recalculateTotalLines() {
        const selectedFiles = this.getSelectedFiles();
        let total = 0;
        const counts = await Promise.all(selectedFiles.map(f => this.fetchLineCount(f)));
        for (const count of counts) total += count;
        this.totalLinesOfCode = total;
        this.updateLinesOfCodeDisplay();
    }

    updateLinesOfCodeDisplay() {
        const display = document.getElementById('linesOfCodeDisplay');
        if (display) {
            display.textContent = `Total Lines of Code: ${this.totalLinesOfCode}`;
            display.classList.remove('loc-green', 'loc-yellow', 'loc-red');
            if (this.totalLinesOfCode > 8000) {
                display.classList.add('loc-red');
            } else if (this.totalLinesOfCode > 4000) {
                display.classList.add('loc-yellow');
            } else {
                display.classList.add('loc-green');
            }
        }
    }
}

const contextGenerator = new ContextGenerator();