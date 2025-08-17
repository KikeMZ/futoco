// Obtener la ruta actual
var currentPage = window.location.pathname.split("/").pop();

// Si hay token y no estamos ya en home, redirigimos
if (localStorage.getItem('token') && currentPage !== 'inicio.html') {
  window.location.href = 'inicio.html';
}

// Si NO hay token y no estamos en index, podemos redirigir a index (opcional)
if (!localStorage.getItem('token') && currentPage !== 'index.html') {
  window.location.href = 'index.html';
}