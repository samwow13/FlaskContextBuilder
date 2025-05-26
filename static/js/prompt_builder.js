// Basic JavaScript for Prompt Builder Modal
document.addEventListener('DOMContentLoaded', () => {
    const promptBuilderModal = document.getElementById('promptBuilderModal');
    const promptBuilderBtn = document.getElementById('promptBuilderBtn');
    const closePromptBuilderModal = document.getElementById('closePromptBuilderModal');

    if (promptBuilderBtn) {
        promptBuilderBtn.addEventListener('click', () => {
            if (promptBuilderModal) promptBuilderModal.style.display = 'block';
        });
    }

    if (closePromptBuilderModal) {
        closePromptBuilderModal.addEventListener('click', () => {
            if (promptBuilderModal) promptBuilderModal.style.display = 'none';
        });
    }

    // Close modal if user clicks outside of the modal content
    window.addEventListener('click', (event) => {
        if (event.target === promptBuilderModal) {
            promptBuilderModal.style.display = 'none';
        }
    });

    // Add specific logic for prompt builder here
    console.log('Prompt Builder JS loaded');
});
