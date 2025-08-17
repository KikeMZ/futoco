// Manejo de login
const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  // Simulación de login
  if (email === "admin@example.com" && password === "1234") {
    localStorage.setItem("token", "123456");
    window.location.href = "inicio.html";
  } else {
    alert("Usuario o contraseña incorrectos");
  }
});

// Manejo de registro (simulación)
const registerForm = document.getElementById("registerForm");
registerForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const pass = document.getElementById("registerPassword").value;
  const passConfirm = document.getElementById("registerPasswordConfirm").value;
  if (pass !== passConfirm) {
    alert("Las contraseñas no coinciden");
    return;
  }
  alert("Registro exitoso (simulado)");
  // Opcional: cambiar a login tab
  const loginTab = new bootstrap.Tab(document.getElementById("login-tab"));
  loginTab.show();
});

const authCard = document.getElementById("authCard");
const recoverCard = document.getElementById("recoverCard");
const recoverLink = document.getElementById("recoverLink");
const cancelRecover = document.getElementById("cancelRecover");

// Mostrar recuperación y ocultar auth
recoverLink.addEventListener("click", (e) => {
  e.preventDefault();
  authCard.style.display = "none";
  recoverCard.style.display = "block";
});

// Cancelar recuperación y volver al auth
cancelRecover.addEventListener("click", () => {
  recoverCard.style.display = "none";
  authCard.style.display = "block";
});

// Manejo de envío de recuperación (simulado)
const recoverForm = document.getElementById("recoverForm");
recoverForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("recoverEmail").value;
  alert(`Se ha enviado un enlace de recuperación a ${email} (simulado)`);
});
