// Obtener la ruta actual
var currentPage = window.location.pathname.split("/").pop();

// Revisar si el test ya se completó
const testDone = localStorage.getItem("testDone"); // valor: 'true' cuando ya lo hizo

if (!testDone && currentPage !== "test.html") {
  // Si NO ha hecho el test y no estamos ya en test.html, redirigir
  window.location.href = "test.html";
}