// Script principal do ML Direta

// Funções utilitárias
const ML = {
    // Formatar data
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    },
    
    // Calcular dias restantes
    daysRemaining: function(endDate) {
        const today = new Date();
        const end = new Date(endDate);
        const diffTime = end - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays > 0 ? diffDays : 0;
    },
    
    // Mostrar toast de notificação
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remover após 5 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    },
    
    // Confirmar ação
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Loading
    showLoading: function(element) {
        element.disabled = true;
        element.innerHTML = '<span class="spinner"></span> Processando...';
    },
    
    hideLoading: function(element, originalText) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
};

// Inicialização quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Table sorting
    const tables = document.querySelectorAll('.table-sortable');
    tables.forEach(function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.addEventListener('click', function() {
                const tableBody = table.querySelector('tbody');
                const rows = Array.from(tableBody.querySelectorAll('tr'));
                const sortKey = this.dataset.sort;
                const isAsc = this.classList.contains('asc');
                
                // Remove class from all headers
                headers.forEach(h => h.classList.remove('asc', 'desc'));
                
                // Add class to current header
                this.classList.add(isAsc ? 'desc' : 'asc');
                
                // Sort rows
                rows.sort(function(a, b) {
                    const aVal = a.querySelector(`td[data-${sortKey}]`).dataset[sortKey];
                    const bVal = b.querySelector(`td[data-${sortKey}]`).dataset[sortKey];
                    
                    if (isAsc) {
                        return aVal.localeCompare(bVal);
                    } else {
                        return bVal.localeCompare(aVal);
                    }
                });
                
                // Reorder rows
                rows.forEach(function(row) {
                    tableBody.appendChild(row);
                });
            });
        });
    });
    
    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const target = this.dataset.search;
            const items = document.querySelectorAll(`[data-search-target="${target}"]`);
            
            items.forEach(function(item) {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // Checkbox select all
    const selectAllCheckboxes = document.querySelectorAll('[data-select-all]');
    selectAllCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const target = this.dataset.selectAll;
            const checkboxes = document.querySelectorAll(`[data-select="${target}"]`);
            
            checkboxes.forEach(function(cb) {
                cb.checked = checkbox.checked;
            });
            
            updateSelectedCount(target);
        });
    });
    
    // Individual checkboxes
    const individualCheckboxes = document.querySelectorAll('[data-select]');
    individualCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const target = this.dataset.select;
            updateSelectedCount(target);
        });
    });
    
    function updateSelectedCount(target) {
        const checkboxes = document.querySelectorAll(`[data-select="${target}"]:checked`);
        const countElement = document.querySelector(`[data-selected-count="${target}"]`);
        const deleteButton = document.querySelector(`[data-delete-selected="${target}"]`);
        
        if (countElement) {
            countElement.textContent = `${checkboxes.length} itens selecionados`;
        }
        
        if (deleteButton) {
            deleteButton.disabled = checkboxes.length === 0;
        }
    }
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const previewTarget = this.dataset.preview;
            const previewElement = document.querySelector(previewTarget);
            
            if (file && previewElement) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (file.type.startsWith('image/')) {
                        previewElement.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="Preview">`;
                    } else {
                        previewElement.innerHTML = `<div class="alert alert-info">Arquivo selecionado: ${file.name}</div>`;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Dynamic form fields
    const dynamicFields = document.querySelectorAll('[data-dynamic-field]');
    dynamicFields.forEach(function(field) {
        field.addEventListener('change', function() {
            const target = this.dataset.dynamicField;
            const value = this.value;
            const targetElements = document.querySelectorAll(`[data-dynamic-target="${target}"]`);
            
            targetElements.forEach(function(element) {
                if (element.dataset.dynamicValue === value) {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    });
    
    // Countdown timers
    const countdownElements = document.querySelectorAll('[data-countdown]');
    countdownElements.forEach(function(element) {
        const targetDate = element.dataset.countdown;
        
        function updateCountdown() {
            const now = new Date().getTime();
            const target = new Date(targetDate).getTime();
            const distance = target - now;
            
            if (distance < 0) {
                element.innerHTML = 'Expirado';
                return;
            }
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            
            element.innerHTML = `${days}d ${hours}h ${minutes}m`;
        }
        
        updateCountdown();
        setInterval(updateCountdown, 60000); // Update every minute
    });
});

// Export para uso global
window.ML = ML;
