// exclusion_manager.js
// Handles modal logic and API calls for managing file_exclude_patterns.json

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('exclusionManagerModal');
    const openBtn = document.getElementById('manageExclusionsBtn');
    const closeBtn = document.getElementById('closeExclusionManagerModal');
    const saveBtn = document.getElementById('saveExclusionsBtn');

    // Lists and inputs
    const excludeDirsList = document.getElementById('excludeDirsList');
    const excludeFilesList = document.getElementById('excludeFilesList');
    const excludePatternsList = document.getElementById('excludePatternsList');
    const newExcludeDir = document.getElementById('newExcludeDir');
    const newExcludeFile = document.getElementById('newExcludeFile');
    const newExcludePattern = document.getElementById('newExcludePattern');
    const addExcludeDirBtn = document.getElementById('addExcludeDirBtn');
    const addExcludeFileBtn = document.getElementById('addExcludeFileBtn');
    const addExcludePatternBtn = document.getElementById('addExcludePatternBtn');

    let exclusions = {
        exclude_dirs: [],
        exclude_files: [],
        exclude_patterns: []
    };

    function renderList(listElem, items, type) {
        listElem.innerHTML = '';
        items.forEach((item, idx) => {
            const li = document.createElement('li');
            li.textContent = item;
            const rmBtn = document.createElement('button');
            rmBtn.textContent = 'Remove';
            rmBtn.className = 'btn btn-warning';
            rmBtn.style.marginLeft = '10px';
            rmBtn.onclick = function() {
                exclusions[type].splice(idx, 1);
                renderAll();
            };
            li.appendChild(rmBtn);
            listElem.appendChild(li);
        });
    }
    function renderAll() {
        renderList(excludeDirsList, exclusions.exclude_dirs, 'exclude_dirs');
        renderList(excludeFilesList, exclusions.exclude_files, 'exclude_files');
        renderList(excludePatternsList, exclusions.exclude_patterns, 'exclude_patterns');
    }
    function fetchExclusions() {
        fetch('/api/exclusions')
            .then(res => res.json())
            .then(data => {
                exclusions = data;
                renderAll();
            });
    }
    openBtn.onclick = function() {
        modal.style.display = 'block';
        fetchExclusions();
    };
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    };
    window.onclick = function(event) {
        if (event.target === modal) modal.style.display = 'none';
    };
    addExcludeDirBtn.onclick = function() {
        const val = newExcludeDir.value.trim();
        if (val && !exclusions.exclude_dirs.includes(val)) {
            exclusions.exclude_dirs.push(val);
            newExcludeDir.value = '';
            renderAll();
        }
    };
    addExcludeFileBtn.onclick = function() {
        const val = newExcludeFile.value.trim();
        if (val && !exclusions.exclude_files.includes(val)) {
            exclusions.exclude_files.push(val);
            newExcludeFile.value = '';
            renderAll();
        }
    };
    addExcludePatternBtn.onclick = function() {
        const val = newExcludePattern.value.trim();
        if (val && !exclusions.exclude_patterns.includes(val)) {
            exclusions.exclude_patterns.push(val);
            newExcludePattern.value = '';
            renderAll();
        }
    };
    saveBtn.onclick = function() {
        fetch('/api/exclusions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(exclusions)
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message || 'Exclusions updated!');
            modal.style.display = 'none';
        })
        .catch(() => alert('Failed to save exclusions.'));
    };
});
