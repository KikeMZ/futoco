const API_BASE_URL = "https://aimodelflask.onrender.com";

// Cerrar sesión
document.getElementById("logoutBtn").addEventListener("click", function () {
  localStorage.removeItem("token");
  window.location.href = "index.html";
});

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("cardsGrid");
  grid.innerHTML = ""; // limpiar lo que viene hardcodeado en el HTML

  const carrerasGuardadas = localStorage.getItem("carrerasTest");
  if (!carrerasGuardadas) {
    grid.innerHTML = `<p class="text-center text-muted">No hay resultados guardados.</p>`;
    localStorage.setItem("testDone", "false");
    return;
  }

  const carreras = JSON.parse(carrerasGuardadas);

  carreras.forEach((carrera) => {
    // Calcular compatibilidad (ejemplo simple usando distancia)
    const compatibilidad = Math.round((1 - carrera.distancia_vectorial) * 100);

    const col = document.createElement("div");
    col.className = "col-12 col-md-4 d-flex justify-content-center";

    col.innerHTML = `
      <div class="card carrera-card position-relative w-100" data-carrera="${carrera.nombre}">
        <div class="card-body text-center py-4">
          <h5 class="card-title mb-2">${carrera.nombre}</h5>
          <div class="card-hover-text d-none">Conocer más</div>
          <div class="card-mobile-text d-md-none text-primary small mb-2">
            Haz click para conocer más acerca de ${carrera.nombre}
          </div>
        </div>
        <div class="card-tab position-absolute top-0 end-0 d-flex align-items-center justify-content-center">
          <button class="btn btn-tab" aria-label="Ver detalles"><span>&gt;</span></button>
        </div>
        <span class="card-compat">${compatibilidad}%</span>
      </div>
    `;

    grid.appendChild(col);
  });

  document.querySelectorAll(".carrera-card").forEach(function (card) {
    // Web: hover muestra texto alterno
    card.addEventListener("mouseenter", function () {
      if (window.innerWidth >= 768) {
        const hoverText = card.querySelector(".card-hover-text");
        if (hoverText) hoverText.classList.remove("d-none");
      }
    });
    card.addEventListener("mouseleave", function () {
      if (window.innerWidth >= 768) {
        const hoverText = card.querySelector(".card-hover-text");
        if (hoverText) hoverText.classList.add("d-none");
      }
    });

    // Click en card o pestaña lleva a conocer.html
    card.addEventListener("click", async function (e) {
      e.stopPropagation();

      const carrera = card.dataset.carrera;

      try {
        const response = await fetch(`${API_BASE_URL}/questions/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) throw new Error("Error al iniciar sesión");

        const data = await response.json();
        localStorage.setItem("session_id", data.session_id);

        window.location.href = "conocer.html?carrera=" + encodeURIComponent(carrera);
      } catch (err) {
        console.error(err);
        alert("No se pudo iniciar la sesión.");
      }
    });
  });
});
