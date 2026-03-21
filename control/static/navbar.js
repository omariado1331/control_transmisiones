// Configuración
const API_BASE_URL = '/control';

// Inicializar navbar
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    setActiveNavLink();
});

// Función para obtener el token CSRF
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

// Cargar datos del usuario
async function loadUserData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user-info/`, {
            headers: { 'X-CSRFToken': getCSRFToken() }
        });
        const data = await response.json();
        
        document.getElementById('userName').textContent = data.username || 'Administrador';
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('userName').textContent = 'Administrador';
    }
}

// Logout
function logout() {
    if (confirm('¿Estás seguro de cerrar sesión?')) {
        fetch(`${API_BASE_URL}/api/logout/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .finally(() => {
            window.location.href = '/control/';
        });
    }
}

// Marcar el link activo según la URL actual
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Inicializar navbar (esta función se llama después de insertar el HTML)
function initNavbar() {
    console.log('Inicializando navbar...');
    loadUserData();
    setActiveNavLink();
}

// Exportar funciones para usar en otras páginas
window.initNavbar = initNavbar;
window.logout = logout;

