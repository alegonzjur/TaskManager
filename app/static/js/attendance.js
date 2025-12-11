// Variables globales
let currentAttendance = null;
let selectedLocation = 'office';
let workTimer = null;

// Cargar al iniciar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Sistema de fichaje cargado');
    loadCurrentStatus();
    loadTodayStats();
    loadTodayAttendances();
    
    // Recargar cada 30 segundos
    setInterval(() => {
        loadCurrentStatus();
        loadTodayStats();
        loadTodayAttendances();
    }, 30000);
    
    // Cargar empleados para admin
    if (document.getElementById('admin-employee-select')) {
        loadEmployeesForAdmin();
    }
    
    // Toggle ubicación en modal admin
    const radioButtons = document.querySelectorAll('input[name="admin-action"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            const locationDiv = document.getElementById('admin-location-select');
            locationDiv.style.display = this.value === 'in' ? 'block' : 'none';
        });
    });
});

// Cargar estado actual del usuario
async function loadCurrentStatus() {
    try {
        const response = await fetch('/attendance/api/current');
        const data = await response.json();
        
        currentAttendance = data.attendance;
        
        if (currentAttendance) {
            showCheckedIn();
        } else {
            showNotCheckedIn();
        }
    } catch (error) {
        console.error('Error al cargar estado:', error);
        document.getElementById('check-loading').style.display = 'block';
        document.getElementById('not-checked-in').style.display = 'none';
        document.getElementById('checked-in').style.display = 'none';
    }
}

// Mostrar panel "No fichado"
function showNotCheckedIn() {
    document.getElementById('check-loading').style.display = 'none';
    document.getElementById('not-checked-in').style.display = 'block';
    document.getElementById('checked-in').style.display = 'none';
    
    // Detener timer si existe
    if (workTimer) {
        clearInterval(workTimer);
        workTimer = null;
    }
}

// Mostrar panel "Fichado"
function showCheckedIn() {
    document.getElementById('check-loading').style.display = 'none';
    document.getElementById('not-checked-in').style.display = 'none';
    document.getElementById('checked-in').style.display = 'block';
    
    // Mostrar información
    const locationText = currentAttendance.location === 'office' ? 
        '🏢 Oficina' : '🏠 Casa (Teletrabajo)';
    document.getElementById('location-display').textContent = locationText;
    
    const checkInTime = new Date(currentAttendance.check_in);
    document.getElementById('check-in-time').textContent = formatTime(checkInTime);
    
    // Iniciar temporizador
    startWorkTimer();
}

// Iniciar temporizador de trabajo
function startWorkTimer() {
    // Detener timer anterior si existe
    if (workTimer) {
        clearInterval(workTimer);
    }
    
    const updateTimer = () => {
        const checkIn = new Date(currentAttendance.check_in);
        const now = new Date();
        const elapsed = now - checkIn;
        
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        document.getElementById('work-timer').textContent = 
            `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    };
    
    updateTimer();
    workTimer = setInterval(updateTimer, 1000);
}

// Cargar estadísticas de hoy
async function loadTodayStats() {
    try {
        const response = await fetch('/attendance/api/stats/today');
        const data = await response.json();
        
        document.getElementById('stat-working').textContent = data.currently_working;
        document.getElementById('stat-checked-in').textContent = data.checked_in_today;
        document.getElementById('stat-office').textContent = data.in_office;
        document.getElementById('stat-home').textContent = data.in_home;
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// Cargar fichajes de hoy
async function loadTodayAttendances() {
    try {
        const response = await fetch('/attendance/api/today');
        const data = await response.json();
        
        displayTodayAttendances(data.attendances);
    } catch (error) {
        console.error('Error al cargar fichajes:', error);
    }
}

// Mostrar fichajes de hoy
function displayTodayAttendances(attendances) {
    const container = document.getElementById('today-attendances');
    
    if (attendances.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> Aún no hay fichajes registrados hoy
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover align-middle">';
    html += '<thead class="table-light"><tr>';
    html += '<th><i class="fas fa-user"></i> Empleado</th>';
    html += '<th><i class="fas fa-map-marker-alt"></i> Ubicación</th>';
    html += '<th><i class="fas fa-sign-in-alt"></i> Entrada</th>';
    html += '<th><i class="fas fa-sign-out-alt"></i> Salida</th>';
    html += '<th><i class="fas fa-clock"></i> Duración</th>';
    html += '<th>Estado</th>';
    html += '</tr></thead><tbody>';
    
    attendances.forEach(att => {
        const checkIn = new Date(att.check_in);
        const checkOut = att.check_out ? new Date(att.check_out) : null;
        
        const statusBadge = att.is_active ?
            '<span class="badge bg-success pulse"><i class="fas fa-circle"></i> Trabajando</span>' :
            '<span class="badge bg-secondary"><i class="fas fa-check"></i> Finalizado</span>';
        
        const locationIcon = att.location === 'office' ? 
            '<span class="badge bg-primary"><i class="fas fa-building"></i> Oficina</span>' :
            '<span class="badge bg-info"><i class="fas fa-home"></i> Casa</span>';
        
        html += `<tr>`;
        html += `<td><strong>${att.employee_name}</strong></td>`;
        html += `<td>${locationIcon}</td>`;
        html += `<td>${formatTime(checkIn)}</td>`;
        html += `<td>${checkOut ? formatTime(checkOut) : '<span class="text-muted">-</span>'}</td>`;
        html += `<td><strong>${att.duration_formatted}</strong></td>`;
        html += `<td>${statusBadge}</td>`;
        html += `</tr>`;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Mostrar modal de entrada
function showCheckInModal(location) {
    selectedLocation = location;
    const locationText = location === 'office' ? 'Oficina' : 'Casa (Teletrabajo)';
    document.getElementById('modal-location-text').textContent = locationText;
    document.getElementById('check-in-notes').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('checkInModal'));
    modal.show();
}

// Confirmar entrada
async function confirmCheckIn() {
    const notes = document.getElementById('check-in-notes').value.trim();
    
    const data = {
        location: selectedLocation,
        notes: notes
    };
    
    try {
        const response = await fetch('/attendance/api/check-in', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al registrar entrada');
        }
        
        const result = await response.json();
        
        // Cerrar modal
        bootstrap.Modal.getInstance(document.getElementById('checkInModal')).hide();
        
        // Mostrar mensaje
        showSuccess('¡Entrada registrada correctamente! 🎉');
        
        // Recargar estado
        await loadCurrentStatus();
        await loadTodayStats();
        await loadTodayAttendances();
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// Mostrar modal de salida
function showCheckOutModal() {
    if (!currentAttendance) return;
    
    const duration = currentAttendance.duration_formatted;
    document.getElementById('modal-duration').textContent = duration;
    document.getElementById('check-out-notes').value = currentAttendance.notes || '';
    
    const modal = new bootstrap.Modal(document.getElementById('checkOutModal'));
    modal.show();
}

// Confirmar salida
async function confirmCheckOut() {
    const notes = document.getElementById('check-out-notes').value.trim();
    
    const data = {
        notes: notes
    };
    
    try {
        const response = await fetch('/attendance/api/check-out', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al registrar salida');
        }
        
        const result = await response.json();
        
        // Cerrar modal
        bootstrap.Modal.getInstance(document.getElementById('checkOutModal')).hide();
        
        // Mostrar mensaje
        showSuccess('¡Salida registrada! Hasta mañana 👋');
        
        // Recargar estado
        await loadCurrentStatus();
        await loadTodayStats();
        await loadTodayAttendances();
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// ADMIN: Cargar empleados
async function loadEmployeesForAdmin() {
    try {
        const response = await fetch('/employees/api?active_only=true');
        const data = await response.json();
        
        const select = document.getElementById('admin-employee-select');
        select.innerHTML = '<option value="">Selecciona un empleado</option>';
        
        data.employees.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = emp.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar empleados:', error);
    }
}

// ADMIN: Fichar por otro empleado
async function adminCheckEmployee() {
    const employeeId = document.getElementById('admin-employee-select').value;
    const action = document.querySelector('input[name="admin-action"]:checked').value;
    
    if (!employeeId) {
        showError('Selecciona un empleado');
        return;
    }
    
    try {
        let response;
        
        if (action === 'in') {
            const location = document.querySelector('input[name="admin-location"]:checked').value;
            response = await fetch('/attendance/api/check-in', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: parseInt(employeeId),
                    location: location,
                    notes: 'Fichado por administrador'
                })
            });
        } else {
            response = await fetch('/attendance/api/check-out', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: parseInt(employeeId),
                    notes: 'Fichado por administrador'
                })
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al registrar');
        }
        
        // Cerrar modal
        bootstrap.Modal.getInstance(document.getElementById('adminCheckModal')).hide();
        
        showSuccess('Fichaje registrado correctamente');
        
        // Recargar datos
        await loadTodayStats();
        await loadTodayAttendances();
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// Utilidades
function formatTime(date) {
    return date.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

console.log('✅ JavaScript de fichaje cargado completamente');