// Obtener la ruta actual
var currentPage = window.location.pathname.split("/").pop();

if (localStorage.getItem('token')) {
  if (currentPage !== 'inicio.html') {
    window.location.href = 'inicio.html';
  }
} else {
  if (currentPage !== 'index.html') {
    window.location.href = 'index.html';
  }
}