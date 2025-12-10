// Variables globales
let allEmployees = [];
let showInactive = false;
let editingEmployeeId = null;

// Cargar empleados al iniciar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Loaded - Iniciando carga de empleados');
    loadEmployees();
    
    // Búsqueda en tiempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            filterEmployees(e.target.value);
        });
    }
});

// Cargar todos los empleados
async function loadEmployees() {
    console.log('🔄 Cargando empleados...');
    try {
        const response = await fetch('/employees/api');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('✅ Respuesta recibida:', data);
        allEmployees = data.employees;
        console.log(`📊 Total empleados cargados: ${allEmployees.length}`);
        updateStats();
        displayEmployees();
    } catch (error) {
        console.error('❌ Error al cargar empleados:', error);
        showError('Error al cargar la lista de empleados');
        
        const container = document.getElementById('employees-container');
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                Error al cargar empleados: ${error.message}
            </div>
        `;
    }
}

// Actualizar estadísticas
function updateStats() {
    const total = allEmployees.length;
    const active = allEmployees.filter(e => e.is_active).length;
    const inactive = total - active;
    
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-active').textContent = active;
    document.getElementById('stat-inactive').textContent = inactive;
    
    loadWorkingEmployees();
}

// Obtener empleados trabajando actualmente
async function loadWorkingEmployees() {
    try {
        const response = await fetch('/assignments/api/current');
        const data = await response.json();
        const workingCount = new Set(data.assignments.map(a => a.employee_id)).size;
        document.getElementById('stat-working').textContent = workingCount;
    } catch (error) {
        document.getElementById('stat-working').textContent = '0';
    }
}

// Mostrar empleados
function displayEmployees() {
    console.log('📋 Mostrando empleados...');
    const container = document.getElementById('employees-container');
    
    let employees = showInactive ? allEmployees : allEmployees.filter(e => e.is_active);
    console.log(`👥 Empleados a mostrar:`, employees.length);
    
    if (employees.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> 
                No hay empleados ${showInactive ? '' : 'activos'} registrados.
                <button class="btn btn-sm btn-primary ms-2" data-bs-toggle="modal" 
                        data-bs-target="#employeeModal" onclick="openAddModal()">
                    <i class="fas fa-plus"></i> Añadir Primero
                </button>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover align-middle">';
    html += '<thead class="table-light"><tr>';
    html += '<th width="5%"><i class="fas fa-hashtag"></i></th>';
    html += '<th width="25%"><i class="fas fa-user"></i> Nombre</th>';
    html += '<th width="25%"><i class="fas fa-envelope"></i> Email</th>';
    html += '<th width="20%"><i class="fas fa-briefcase"></i> Puesto</th>';
    html += '<th width="10%"><i class="fas fa-circle-check"></i> Estado</th>';
    html += '<th width="15%" class="text-center"><i class="fas fa-cog"></i> Acciones</th>';
    html += '</tr></thead><tbody>';
    
    employees.forEach((emp, index) => {
        const statusBadge = emp.is_active 
            ? '<span class="badge bg-success"><i class="fas fa-check"></i> Activo</span>'
            : '<span class="badge bg-secondary"><i class="fas fa-ban"></i> Inactivo</span>';
        
        const roleBadge = emp.role === 'admin'
            ? '<span class="badge bg-warning text-dark ms-1"><i class="fas fa-crown"></i> Admin</span>'
            : '';
        
        html += `<tr class="${emp.is_active ? '' : 'table-secondary'}">`;
        html += `<td class="text-muted">${index + 1}</td>`;
        html += `<td><strong>${emp.name}</strong> ${roleBadge}</td>`;
        html += `<td><small>${emp.email}</small></td>`;
        html += `<td>${emp.position || '<span class="text-muted">-</span>'}</td>`;
        html += `<td>${statusBadge}</td>`;
        html += `<td class="text-center">`;
        html += `<div class="btn-group btn-group-sm">`;
        html += `<button class="btn btn-outline-primary" onclick="editEmployee(${emp.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                 </button>`;
        html += `<button class="btn btn-outline-${emp.is_active ? 'warning' : 'success'}" 
                    onclick="confirmToggleStatus(${emp.id}, ${!emp.is_active})" 
                    title="${emp.is_active ? 'Desactivar' : 'Activar'}">
                    <i class="fas fa-${emp.is_active ? 'ban' : 'check'}"></i>
                 </button>`;
        html += `</div></td></tr>`;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
    console.log('✅ Tabla generada correctamente');
}

// Filtrar empleados
function filterEmployees(searchTerm) {
    if (!searchTerm) {
        displayEmployees();
        return;
    }
    
    const filtered = allEmployees.filter(emp => {
        const term = searchTerm.toLowerCase();
        return emp.name.toLowerCase().includes(term) ||
               emp.email.toLowerCase().includes(term) ||
               (emp.position && emp.position.toLowerCase().includes(term));
    });
    
    const container = document.getElementById('employees-container');
    
    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-search"></i> No se encontraron empleados que coincidan con "${searchTerm}"
            </div>
        `;
        return;
    }
    
    // Mostrar filtrados (reutilizar lógica de displayEmployees pero con filtered)
    const tempAll = allEmployees;
    allEmployees = filtered;
    displayEmployees();
    allEmployees = tempAll;
}

// Toggle mostrar inactivos
function toggleShowInactive() {
    showInactive = !showInactive;
    document.getElementById('toggleText').textContent = showInactive ? 'Ocultar Inactivos' : 'Mostrar Inactivos';
    document.getElementById('toggleIcon').className = showInactive ? 'fas fa-eye-slash' : 'fas fa-eye';
    displayEmployees();
}

// Abrir modal para añadir
function openAddModal() {
    console.log('📝 Abriendo modal para nuevo empleado');
    editingEmployeeId = null;
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-user-plus"></i> Nuevo Empleado';
    document.getElementById('employeeForm').reset();
    document.getElementById('employee_id').value = '';
    document.getElementById('is_active').value = 'true';
    document.getElementById('role').value = 'employee';
}

// Editar empleado
function editEmployee(employeeId) {
    console.log('✏️ Editando empleado:', employeeId);
    const employee = allEmployees.find(e => e.id === employeeId);
    if (!employee) return;
    
    editingEmployeeId = employeeId;
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-user-edit"></i> Editar Empleado';
    document.getElementById('employee_id').value = employee.id;
    document.getElementById('name').value = employee.name;
    document.getElementById('email').value = employee.email;
    document.getElementById('email_confirm').value = employee.email;
    document.getElementById('position').value = employee.position || '';
    document.getElementById('role').value = employee.role || 'employee';
    document.getElementById('is_active').value = employee.is_active.toString();
    
    // Limpiar contraseñas
    document.getElementById('password').value = '';
    document.getElementById('password_confirm').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
    modal.show();
}

// Guardar empleado
async function saveEmployee() {
    console.log('💾 Guardando empleado...');
    const form = document.getElementById('employeeForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const email = document.getElementById('email').value.trim();
    const emailConfirm = document.getElementById('email_confirm').value.trim();
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('password_confirm').value;
    
    // Validar emails
    if (email !== emailConfirm) {
        showError('Los emails no coinciden');
        return;
    }
    
    // Validar contraseñas solo si se proporcionaron
    if (password || passwordConfirm) {
        if (password.length < 8) {
            showError('La contraseña debe tener al menos 8 caracteres');
            return;
        }
        if (password !== passwordConfirm) {
            showError('Las contraseñas no coinciden');
            return;
        }
    }
    
    const data = {
        name: document.getElementById('name').value.trim(),
        email: email,
        email_confirm: emailConfirm,
        position: document.getElementById('position').value.trim(),
        birth_date: document.getElementById('birth_date').value || null,
        role: document.getElementById('role').value,
        is_active: document.getElementById('is_active').value === 'true'
    };
    
    if (password) {
        data.password = password;
        data.password_confirm = passwordConfirm;
    }
    
    console.log('📤 Enviando datos:', data);
    
    try {
        let response;
        if (editingEmployeeId) {
            const updateData = {
                name: data.name,
                email: data.email,
                position: data.position,
                is_active: data.is_active
            };
            response = await fetch(`/employees/api/${editingEmployeeId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al actualizar');
            }
            
            showSuccess('Empleado actualizado correctamente');
        } else {
            response = await fetch('/employees/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al crear');
            }
            
            showSuccess(password ? 'Usuario creado con credenciales' : 'Empleado creado sin credenciales');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('employeeModal')).hide();
        await loadEmployees();
        
    } catch (error) {
        console.error('❌ Error al guardar:', error);
        showError('Error al guardar: ' + error.message);
    }
}

// Confirmar cambio de estado
function confirmToggleStatus(employeeId, newStatus) {
    const employee = allEmployees.find(e => e.id === employeeId);
    const message = newStatus 
        ? `¿Activar a ${employee.name}?`
        : `¿Desactivar a ${employee.name}? No podrá iniciar sesión.`;
    
    document.getElementById('confirmMessage').textContent = message;
    document.getElementById('confirmButton').onclick = () => toggleEmployeeStatus(employeeId, newStatus);
    
    const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    modal.show();
}

// Cambiar estado del empleado
async function toggleEmployeeStatus(employeeId, newStatus) {
    try {
        const response = await fetch(`/employees/api/${employeeId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: newStatus })
        });
        
        if (!response.ok) {
            throw new Error('Error al cambiar estado');
        }
        
        showSuccess(`Empleado ${newStatus ? 'activado' : 'desactivado'} correctamente`);
        bootstrap.Modal.getInstance(document.getElementById('confirmModal')).hide();
        await loadEmployees();
    } catch (error) {
        showError('Error al cambiar el estado del empleado');
    }
}

// Mostrar mensaje de éxito
function showSuccess(message) {
    console.log('✅', message);
    // Usar toasts de Bootstrap si están disponibles
    alert(message); // Por ahora, simple alert
}

// Mostrar mensaje de error
function showError(message) {
    console.error('❌', message);
    alert('Error: ' + message);
}

// Indicador de fortaleza de contraseña
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strengthBar = document.getElementById('password-strength-bar');
            const strengthContainer = document.getElementById('password-strength');
            
            if (password.length === 0) {
                strengthContainer.style.display = 'none';
                return;
            }
            
            strengthContainer.style.display = 'block';
            
            let strength = 0;
            if (password.length >= 8) strength += 25;
            if (password.length >= 12) strength += 25;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
            if (/\d/.test(password)) strength += 15;
            if (/[^a-zA-Z0-9]/.test(password)) strength += 10;
            
            strengthBar.style.width = strength + '%';
            
            if (strength < 40) {
                strengthBar.className = 'progress-bar bg-danger';
            } else if (strength < 70) {
                strengthBar.className = 'progress-bar bg-warning';
            } else {
                strengthBar.className = 'progress-bar bg-success';
            }
        });
    }
});

console.log('✅ JavaScript de empleados cargado completamente');