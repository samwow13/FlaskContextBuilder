class HierarchicalDropdown {
    constructor(container, options = {}) {
        this.container = container;
        this.selectedValue = null;
        this.selectedText = '';
        this.onSelect = options.onSelect || (() => {});
        this.placeholder = options.placeholder || 'Select a file...';
        this.data = [];
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        this.container.innerHTML = '';
        this.container.className = 'hierarchical-dropdown-container';
        
        // Create the main dropdown button
        this.button = document.createElement('button');
        this.button.className = 'hierarchical-dropdown-button';
        this.button.innerHTML = `
            <span class="dropdown-text">${this.placeholder}</span>
            <i class="fas fa-chevron-down dropdown-arrow"></i>
        `;
        this.button.onclick = (e) => {
            e.stopPropagation();
            this.toggle();
        };
        
        // Create the dropdown menu
        this.menu = document.createElement('div');
        this.menu.className = 'hierarchical-dropdown-menu';
        this.menu.style.display = 'none';
        
        this.container.appendChild(this.button);
        this.container.appendChild(this.menu);
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.close();
            }
        });
    }
    
    setData(treeData) {
        this.data = treeData;
        this.renderMenu();
    }
    
    renderMenu() {
        this.menu.innerHTML = '';
        this.renderItems(this.data, this.menu, 0);
    }
    
    renderItems(items, parentElement, level) {
        items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'dropdown-item';
            itemElement.style.paddingLeft = `${level * 20 + 10}px`;
            
            if (item.type === 'folder') {
                itemElement.innerHTML = `
                    <i class="fas fa-folder folder-icon"></i>
                    <span>${item.name}</span>
                    <i class="fas fa-chevron-right submenu-arrow"></i>
                `;
                
                const submenu = document.createElement('div');
                submenu.className = 'dropdown-submenu';
                submenu.style.display = 'none';
                
                let isExpanded = false;
                
                itemElement.onclick = (e) => {
                    e.stopPropagation();
                    isExpanded = !isExpanded;
                    submenu.style.display = isExpanded ? 'block' : 'none';
                    itemElement.querySelector('.submenu-arrow').className = 
                        isExpanded ? 'fas fa-chevron-down submenu-arrow' : 'fas fa-chevron-right submenu-arrow';
                    itemElement.querySelector('.folder-icon').className = 
                        isExpanded ? 'fas fa-folder-open folder-icon' : 'fas fa-folder folder-icon';
                };
                
                parentElement.appendChild(itemElement);
                parentElement.appendChild(submenu);
                
                if (item.children && item.children.length > 0) {
                    this.renderItems(item.children, submenu, level + 1);
                }
                
            } else if (item.type === 'file') {
                const sizeText = this.formatFileSize(item.size);
                itemElement.innerHTML = `
                    <i class="fas fa-file file-icon"></i>
                    <span>${item.name}</span>
                    <span class="file-size">${sizeText}</span>
                `;
                
                itemElement.onclick = (e) => {
                    e.stopPropagation();
                    this.selectItem(item);
                };
                
                parentElement.appendChild(itemElement);
            }
        });
    }
    
    selectItem(item) {
        this.selectedValue = item.path;
        this.selectedText = `${item.relative_path} (${this.formatFileSize(item.size)})`;
        this.button.querySelector('.dropdown-text').textContent = this.selectedText;
        this.button.classList.add('has-selection');
        this.close();
        this.onSelect(this.selectedValue, this.selectedText);
    }
    
    toggle() {
        this.isOpen ? this.close() : this.open();
    }
    
    open() {
        this.menu.style.display = 'block';
        this.isOpen = true;
        this.button.querySelector('.dropdown-arrow').className = 'fas fa-chevron-up dropdown-arrow';
    }
    
    close() {
        this.menu.style.display = 'none';
        this.isOpen = false;
        this.button.querySelector('.dropdown-arrow').className = 'fas fa-chevron-down dropdown-arrow';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    getValue() {
        return this.selectedValue;
    }
    
    setValue(value) {
        // Find the item in the tree and select it
        const findItem = (items) => {
            for (let item of items) {
                if (item.type === 'file' && item.path === value) {
                    this.selectItem(item);
                    return true;
                } else if (item.children) {
                    if (findItem(item.children)) return true;
                }
            }
            return false;
        };
        
        findItem(this.data);
    }
    
    clear() {
        this.selectedValue = null;
        this.selectedText = '';
        this.button.querySelector('.dropdown-text').textContent = this.placeholder;
        this.button.classList.remove('has-selection');
    }
}