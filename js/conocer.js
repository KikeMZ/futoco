const API_BASE_URL = "https://aimodelflask.onrender.com";

document.addEventListener("DOMContentLoaded", async () => {
  const session_id = localStorage.getItem("session_id");
  if (!session_id) {
    alert("No hay sesión activa. Redirigiendo a inicio.");
    window.location.href = "index.html";
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const carrera = params.get("carrera");
  if (!carrera) {
    document.getElementById("preguntas-tab").textContent =
      "Datos insuficientes para iniciar.";
    return;
  }

  // Ocultar botones mientras cargamos
  toggleButtons(false);

  await cargarEscenario(carrera);
});

// ---------------- Funciones de UI ----------------

function toggleButtons(show) {
  const btn1 = document.getElementById("opcion_1");
  const btn2 = document.getElementById("opcion_2");
  const preguntaTexto = document.getElementById("preguntaTexto");

  btn1.style.display = show ? "" : "none";
  btn2.style.display = show ? "" : "none";
  preguntaTexto.style.display = show ? "" : "none";

  if (show) {
    btn1.disabled = false;
    btn2.disabled = false;
    preguntaTexto.textContent = "Selecciona una opción:";
  }
}

async function cargarEscenario(carrera) {
  try {
    const preguntasTab = document.getElementById("preguntas-tab");
    preguntasTab.textContent = "Cargando situación...";

    const response = await fetch(`${API_BASE_URL}/game/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: localStorage.getItem("session_id"),
        carrera: carrera,
      }),
    });

    if (!response.ok) throw new Error("Error al iniciar preguntas");

    const data = await response.json();
    mostrarEscenario(data.escenario);
  } catch (err) {
    console.error(err);
    document.getElementById("preguntas-tab").textContent =
      "Error al cargar la situación.";
  }
}

function mostrarEscenario(data) {
  const preguntasTab = document.getElementById("preguntas-tab");
  const btn1 = document.getElementById("opcion_1");
  const btn2 = document.getElementById("opcion_2");

  preguntasTab.textContent = data.situacion;

  btn1.textContent = data.opciones[0];
  btn2.textContent = data.opciones[1];

  // Mostrar y habilitar botones
  toggleButtons(true);

  // Asignar eventos
  btn1.onclick = () => continuarQuiz(1);
  btn2.onclick = () => continuarQuiz(2);
}


// ---------------- Función de proceso ----------------

async function continuarQuiz(opcion) {
  const preguntasTab = document.getElementById("preguntas-tab");
  const btn1 = document.getElementById("opcion_1");
  const btn2 = document.getElementById("opcion_2");
  const preguntaTexto = document.getElementById("preguntaTexto");

  try {
    const session_id = localStorage.getItem("session_id");
    if (!session_id) throw new Error("Session ID no encontrado");

    const opcionInt = parseInt(opcion, 10);
    if (![1, 2].includes(opcionInt)) throw new Error("Opción inválida");

    // Deshabilitar botones mientras procesamos
    btn1.disabled = true;
    btn2.disabled = true;
    preguntaTexto.textContent = "";
    preguntasTab.textContent = "Procesando respuesta...";

    const response = await fetch(`${API_BASE_URL}/game/next`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        opcion: opcionInt,
        session_id: session_id,
      }),
    });

    if (!response.ok) throw new Error("Error al enviar respuesta");

    const data = await response.json();

    // Mostrar resultado de la acción
    preguntasTab.textContent = data.resultado;

    if (data.done) {
      // Juego terminado
      toggleButtons(false);
      mostrarScore(data.score);
    } else {
      // Esperar un pequeño tiempo para mostrar el resultado antes de cargar la siguiente pregunta
      setTimeout(() => {
        mostrarEscenario(data.next_escenario);
      }, 1000);
    }
  } catch (err) {
    console.error(err);
    preguntasTab.textContent = "Error al procesar respuesta.";
    toggleButtons(true); // reactivar botones en caso de error
  }
}

function mostrarScore(score) {
  const preguntasTab = document.getElementById("preguntas-tab");
  preguntasTab.innerHTML = `
  <div class="d-flex flex-column align-items-center justify-content-center text-center" style="min-height: 200px;">
    <p>¡Juego completado!</p>
    <p>Score:</p>
    <ul>
      <li>Crecimiento: ${score.crecimiento}</li>
      <li>Estrés: ${score.estres}</li>
      <li>Satisfacción: ${score.satisfaccion}</li>
    </ul>
    <button id="btnRegresar" class="btn btn-primary mt-3">Regresar al inicio</button>
    </div>
  `;

  const btnRegresar = document.getElementById("btnRegresar");
  btnRegresar.addEventListener("click", () => {
    window.location.href = "inicio.html";
  });
}
