// Cerrar sesión
document.getElementById("logoutBtn").addEventListener("click", function () {
  localStorage.removeItem("token");
  window.location.href = "index.html";
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
    card.addEventListener("click", function (e) {
      if (window.innerWidth < 768) {
        if (e.target.closest(".btn-tab")) {
          window.location.href =
            "conocer.html?carrera=" + encodeURIComponent(card.dataset.carrera);
        }
      } else {
        window.location.href =
          "conocer.html?carrera=" + encodeURIComponent(card.dataset.carrera);
      }
    });
    card.querySelector(".btn-tab").addEventListener("click", function (e) {
      if (window.innerWidth < 768) {
        window.location.href =
          "conocer.html?carrera=" + encodeURIComponent(card.dataset.carrera);
        e.stopPropagation();
      }
    });
  });
