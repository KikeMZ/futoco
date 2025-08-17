// Preguntas de ejemplo
const preguntas = [
  "¿Te sentiste motivado hoy?",
  "¿Tuviste energía suficiente?",
  "¿Te sentiste apoyado?",
  "¿Lograste tus objetivos?",
  "¿Te sentiste satisfecho?",
];

let respuestas =
  JSON.parse(localStorage.getItem("respuestasTest")) ||
  Array(preguntas.length).fill(3);
let current = 0;

function setThumbSize(valor) {
  // Tamaño entre 18px (min) y 36px (max)
  const min = 18,
    max = 36;
  const size = min + ((valor - 1) * (max - min)) / 4;
  document
    .getElementById("answerInput")
    .style.setProperty("--thumb-size", size + "px");
}

function mostrarPregunta() {
  document.getElementById("questionLabel").textContent = preguntas[current];
  document.getElementById("answerInput").value = respuestas[current] || 3;
  document.getElementById("answerValue").textContent = respuestas[current] || 3;
  document.getElementById("prevBtn").disabled = current === 0;
  document.getElementById("nextBtn").disabled =
    current === preguntas.length - 1;
  setThumbSize(respuestas[current] || 3);
}

document.getElementById("answerInput").addEventListener("input", function () {
  respuestas[current] = parseInt(this.value);
  document.getElementById("answerValue").textContent = this.value;
  localStorage.setItem("respuestasTest", JSON.stringify(respuestas));
  setThumbSize(this.value);
});

document.getElementById("prevBtn").addEventListener("click", function () {
  if (current > 0) {
    current--;
    mostrarPregunta();
  }
});

document.getElementById("nextBtn").addEventListener("click", function () {
  if (current < preguntas.length - 1) {
    current++;
    mostrarPregunta();
  }
});

document.getElementById("saveBtn").addEventListener("click", function () {
  localStorage.setItem("respuestasTest", JSON.stringify(respuestas));
  localStorage.setItem("testDone", "true")
  console.log(localStorage.getItem("respuestasTest"));
  
  alert("Respuestas guardadas correctamente");

  window.location.href = "inicio.html";
});

mostrarPregunta();
