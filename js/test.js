let preguntaActual = null;
let respuestaActual = 3; // Valor inicial
const questionLabel = document.getElementById("questionLabel");
const answerInput = document.getElementById("answerInput");
const answerValue = document.getElementById("answerValue");
const nextBtn = document.getElementById("nextBtn");
const saveBtn = document.getElementById("saveBtn");

async function iniciarPreguntas() {
  try {
    const response = await fetch(`${API_BASE_URL}/questions/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) throw new Error("Error al iniciar preguntas");
    const data = await response.json();
    // Guardar session_id en sessionStorage
    sessionStorage.setItem("session_id", data.session_id);
    return data.first_question;
  } catch (err) {
    console.error("API error:", err);
    return null;
  }
}

async function siguientePregunta() {
  const sessionId = sessionStorage.getItem("session_id");

  try {
    const response = await fetch(`${API_BASE_URL}/questions/next_question`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        answer: respuestaActual,
      }),
    });
    if (!response.ok) throw new Error("Error al obtener siguiente pregunta");
    return await response.json();
  } catch (error) {
    console.error("API error:", error);
    return null;
  }
}

async function resultadosPreguntas() {
  const sessionId = sessionStorage.getItem("session_id");
  try {
    const response = await fetch(
      `${API_BASE_URL}/questions/result?session_id=${sessionId}`
    );
    if (!response.ok) throw new Error("Error al obtener resultados");
    return await response.json();
  } catch (error) {
    console.error("API error:", error);
    return null;
  }
}

// ----------------- Funciones UI -----------------
function mostrarPregunta(texto) {
  questionLabel.textContent = texto;
  answerInput.value = respuestaActual;
  answerValue.textContent = respuestaActual;
}

async function cargarPrimeraPregunta() {
  try {
    questionLabel.textContent = "Cargando pregunta...";

    const primera = await iniciarPreguntas();

    if (primera && primera.texto) {
      preguntaActual = primera;
      mostrarPregunta(preguntaActual.texto);
    } else {
      questionLabel.textContent = "No se pudo obtener la primera pregunta.";
    }
  } catch (err) {
    console.error("Error al cargar primera pregunta:", err);
    questionLabel.textContent = "Error al cargar la primera pregunta.";
  }
}

// ----------------- Eventos -----------------
document.addEventListener("DOMContentLoaded", cargarPrimeraPregunta);

answerInput.addEventListener("input", function () {
  respuestaActual = parseInt(this.value);
  answerValue.textContent = this.value;
});

nextBtn.addEventListener("click", async () => {
  nextBtn.disabled = true;
  questionLabel.textContent = "Cargando siguiente pregunta...";

  try {
    const data = await siguientePregunta();

    if (!data) throw new Error("No se recibieron datos del servidor");

    if (data.done) {
      // Test completado
      questionLabel.textContent = "¡Test completado!";
      nextBtn.classList.add("d-none");
      saveBtn.classList.remove("d-none");
    } else if (data.question) {
      // Mostrar siguiente pregunta
      preguntaActual = data.question;
      mostrarPregunta(preguntaActual.texto);
    }
  } catch (err) {
    console.error(err);
    questionLabel.textContent = "Error al cargar la siguiente pregunta.";
  } finally {
    nextBtn.disabled = false;
  }
});

saveBtn.addEventListener("click", async () => {
  try {
    const resultados = await resultadosPreguntas();
    if (resultados && resultados.carreras) {
      localStorage.setItem("carrerasTest", JSON.stringify(resultados.carreras));
      localStorage.setItem("testDone", "true");
      window.location.href = "inicio.html";
    } else {
      alert("No se pudieron obtener los resultados.");
    }
  } catch (err) {
    console.error(err);
    alert("Ocurrió un error al obtener resultados.");
  }
});
