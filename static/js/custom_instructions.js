document.addEventListener('DOMContentLoaded', () => {
    const customInstructionsModal = document.getElementById('customInstructionsModal');
    const customInstructionsBtn = document.getElementById('customInstructionsBtn');
    const closeCustomInstructionsModal = document.getElementById('closeCustomInstructionsModal');
    const customInstructionsTextarea = document.getElementById('customInstructionsTextarea');
    const saveCustomInstructionsBtn = document.getElementById('saveCustomInstructionsBtn');

    // Function to show toast messages (assuming showToast is globally available from app.js)
    // If not, you might need to pass it or ensure app.js loads first and defines it globally.
    const displayToast = (message, type = 'success') => {
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.warn('showToast function not found. Please ensure app.js is loaded and showToast is global.');
            alert(`${type.toUpperCase()}: ${message}`); // Fallback alert
        }
    };

    async function loadCustomInstructions() {
        try {
            const response = await fetch('/api/custom-instructions');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.instructions) {
                customInstructionsTextarea.value = data.instructions;
            }
        } catch (error) {
            console.error('Failed to load custom instructions:', error);
            displayToast('Failed to load custom instructions.', 'error');
        }
    }

    async function saveCustomInstructions() {
        const instructions = customInstructionsTextarea.value;
        try {
            const response = await fetch('/api/custom-instructions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ instructions }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            displayToast(result.message || 'Instructions saved successfully!');
            if (customInstructionsModal) customInstructionsModal.style.display = 'none'; // Optionally close modal on save
        } catch (error) {
            console.error('Failed to save custom instructions:', error);
            displayToast('Failed to save custom instructions.', 'error');
        }
    }

    if (customInstructionsBtn) {
        customInstructionsBtn.addEventListener('click', () => {
            if (customInstructionsModal) {
                customInstructionsModal.style.display = 'block';
                loadCustomInstructions(); // Load instructions when modal is opened
            }
        });
    }

    if (closeCustomInstructionsModal) {
        closeCustomInstructionsModal.addEventListener('click', () => {
            if (customInstructionsModal) customInstructionsModal.style.display = 'none';
        });
    }

    if (saveCustomInstructionsBtn) {
        saveCustomInstructionsBtn.addEventListener('click', saveCustomInstructions);
    }

    // Close modal if user clicks outside of the modal content
    window.addEventListener('click', (event) => {
        if (event.target === customInstructionsModal) {
            customInstructionsModal.style.display = 'none';
        }
    });

    console.log('Custom Instructions JS loaded and enhanced.');
});
