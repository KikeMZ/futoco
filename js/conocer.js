// Cerrar sesión
document.getElementById("logoutBtn").addEventListener("click", function () {
  localStorage.removeItem("token");
  window.location.href = "index.html";
});


document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const carrera = params.get("carrera");
  const session_id = localStorage.getItem("session_id");

  if (!carrera || !session_id) {
    document.getElementById("preguntas-tab").textContent = "Datos insuficientes para iniciar.";
    return;
  }

  await cargarEscenario(session_id, carrera);
});

async function cargarEscenario(session_id, carrera) {
  try {
    const preguntasTab = document.getElementById("preguntas-tab");
    preguntasTab.textContent = "Cargando situación...";

    const response = await fetch(`${API_BASE_URL}/game/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, carrera }),
    });

    if (!response.ok) throw new Error("Error al iniciar preguntas");

    const data = await response.json();
    mostrarEscenario(data);
  } catch (err) {
    console.error(err);
    document.getElementById("preguntas-tab").textContent = "Error al cargar la situación.";
  }
}


function mostrarEscenario(data) {
  const preguntasTab = document.getElementById("preguntas-tab");
  preguntasTab.textContent = data.escenario.situacion;

  const button1 = document.getElementById("opcion_1");
  const button2 = document.getElementById("opcion_2");

  button1.textContent = data.escenario.opciones[0];
  button2.textContent = data.escenario.opciones[1];

  // Limpiar eventos anteriores
  button1.replaceWith(button1.cloneNode(true));
  button2.replaceWith(button2.cloneNode(true));

  const btn1 = document.getElementById("opcion_1");
  const btn2 = document.getElementById("opcion_2");

  btn1.onclick = () => continuarQuiz(data.session_id, 0);
  btn2.onclick = () => continuarQuiz(data.session_id, 1);
}

async function continuarQuiz(session_id, opcionSeleccionada) {
  try {
    const preguntasTab = document.getElementById("preguntas-tab");

    const response = await fetch(`${API_BASE_URL}/game/next`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, opcion: opcionSeleccionada }),
    });

    if (!response.ok) throw new Error("Error al enviar respuesta");

    const data = await response.json();

    console.log(data);

    if (data.done) {
      preguntasTab.textContent = "¡Juego completado!";
      document.getElementById("opcion_1").style.display = "none";
      document.getElementById("opcion_2").style.display = "none";
    } else {
      mostrarEscenario(data);
    }
  } catch (err) {
    console.error(err);
    document.getElementById("preguntas-tab").textContent = "Error al procesar respuesta.";
  }
}