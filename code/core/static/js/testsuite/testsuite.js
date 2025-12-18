document.addEventListener("DOMContentLoaded", () => {
  initializeTabs()
  hideMessagesAfterDelay()
})

function initializeTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn")
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const tab = this.getAttribute("data-tab")
      switchTab(tab)
    })
  })
}

function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("active")
  })
  document.querySelector(`[data-tab="${tab}"]`).classList.add("active")

  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.remove("active")
  })
  document.getElementById(`${tab}-tab`).classList.add("active")
}

function openModal(modalId, mode) {
  const modal = document.getElementById(modalId)
  modal.classList.add("active")

  if (mode === "create") {
    const form = modal.querySelector("form")
    if (form) {
      form.reset()

      if (modalId === "testSuiteModal") {
        form.action = "/testsuite/testsuite/crear/"
        modal.querySelector("h3").textContent = "Nuevo Test Suite"
      } else if (modalId === "casoModal") {
        form.action = "/testsuite/caso/crear/"
        modal.querySelector("h3").textContent = "Nuevo Caso de Prueba"
      } else if (modalId === "ejecucionModal") {
        form.action = "/testsuite/ejecucion/crear/"
        modal.querySelector("h3").textContent = "Nueva Ejecución"
      }
    }
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId)
  modal.classList.remove("active")

  const form = modal.querySelector("form")
  if (form) {
    form.reset()
  }
}

window.onclick = (event) => {
  if (event.target.classList.contains("modal")) {
    event.target.classList.remove("active")
  }
}

function editTestSuite(id, nombre, descripcion, proyectoId) {
  const modal = document.getElementById("testSuiteModal")
  const form = modal.querySelector("form")

  modal.querySelector("h3").textContent = "Editar Test Suite"
  form.action = `/testsuite/testsuite/${id}/editar/`

  form.querySelector('[name="nombre"]').value = nombre
  form.querySelector('[name="descripcion"]').value = descripcion
  form.querySelector('[name="proyecto"]').value = proyectoId

  modal.classList.add("active")
}

function editCaso(id, nombre, descripcion, testsuiteId, estadoId, version, entornoId) {
  const modal = document.getElementById("casoModal")
  const form = modal.querySelector("form")

  modal.querySelector("h3").textContent = "Editar Caso de Prueba"
  form.action = `/testsuite/caso/${id}/editar/`

  form.querySelector('[name="nombre"]').value = nombre
  form.querySelector('[name="descripcion"]').value = descripcion
  form.querySelector('[name="test_suite"]').value = testsuiteId
  if (estadoId !== null) {
    form.querySelector('[name="estado"]').value = estadoId
  }
  form.querySelector('[name="version"]').value = version
  if (entornoId !== null) {
    form.querySelector('[name="entorno"]').value = entornoId
  }

  modal.classList.add("active")
}

function editEjecucion(id, casoId, estadoId, resultado, observaciones) {
  const modal = document.getElementById("ejecucionModal")
  const form = modal.querySelector("form")

  modal.querySelector("h3").textContent = "Editar Ejecución"
  form.action = `/testsuite/ejecucion/${id}/editar/`

  form.querySelector('[name="caso_prueba"]').value = casoId
  if (estadoId !== null) {
    form.querySelector('[name="estado"]').value = estadoId
  }
  form.querySelector('[name="resultado"]').value = resultado
  form.querySelector('[name="observaciones"]').value = observaciones

  modal.classList.add("active")
}

function hideMessagesAfterDelay() {
  const messages = document.querySelectorAll(".messages-container .alert")
  messages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      setTimeout(() => {
        message.remove()
      }, 300)
    }, 4000)
  })
}
