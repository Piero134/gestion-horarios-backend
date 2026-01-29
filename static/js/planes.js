// ==================== PLANES DE ESTUDIO - JAVASCRIPT ====================

document.addEventListener('DOMContentLoaded', function() {

    // ========== ELEMENTOS DEL DOM ==========
    const filtroFacultad = document.getElementById('filtroFacultad');
    const filtroEscuela = document.getElementById('filtroEscuela');
    const filtroPlan = document.getElementById('filtroPlan');
    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    const planVisualizacion = document.getElementById('planVisualizacion');
    const emptyState = document.getElementById('emptyState');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const ciclosContainer = document.getElementById('ciclosContainer');

    // Estado actual
    let planActual = null;

    // ========== INICIALIZACIÓN ==========

    // Si hay preselección desde escuela, cargar automáticamente
    if (CONTEXT_DATA.escuelaPreseleccionada) {
        cargarEscuelasFacultad(CONTEXT_DATA.facultadPreseleccionada, () => {
            filtroEscuela.value = CONTEXT_DATA.escuelaPreseleccionada;
            cargarPlanesEscuela(CONTEXT_DATA.escuelaPreseleccionada);

            // Si hay plan preseleccionado, cargarlo
            if (CONTEXT_DATA.planSeleccionado) {
                setTimeout(() => {
                    filtroPlan.value = CONTEXT_DATA.planSeleccionado;
                    cargarPlanDetalle(CONTEXT_DATA.planSeleccionado);
                }, 500);
            }
        });
    }

    // ========== EVENT LISTENERS ==========

    // Cambio de Facultad
    filtroFacultad.addEventListener('change', function() {
        const facultadId = this.value;

        // Resetear escuela y plan
        filtroEscuela.innerHTML = '<option value="">Seleccione una facultad primero</option>';
        filtroEscuela.disabled = true;
        filtroPlan.innerHTML = '<option value="">Seleccione una escuela primero</option>';
        filtroPlan.disabled = true;

        // Ocultar visualización
        ocultarVisualizacion();

        if (facultadId) {
            cargarEscuelasFacultad(facultadId);
        }
    });

    // Cambio de Escuela
    filtroEscuela.addEventListener('change', function() {
        const escuelaId = this.value;

        // Resetear plan
        filtroPlan.innerHTML = '<option value="">Seleccione una escuela primero</option>';
        filtroPlan.disabled = true;

        // Ocultar visualización
        ocultarVisualizacion();

        if (escuelaId) {
            cargarPlanesEscuela(escuelaId);
        }
    });

    // Cambio de Plan
    filtroPlan.addEventListener('change', function() {
        const planId = this.value;

        if (planId) {
            cargarPlanDetalle(planId);
        } else {
            ocultarVisualizacion();
        }
    });

    // Limpiar Filtros
    btnLimpiarFiltros.addEventListener('click', function() {
        filtroFacultad.value = '';
        filtroEscuela.innerHTML = '<option value="">Seleccione una facultad primero</option>';
        filtroEscuela.disabled = true;
        filtroPlan.innerHTML = '<option value="">Seleccione una escuela primero</option>';
        filtroPlan.disabled = true;
        ocultarVisualizacion();

        // Actualizar URL sin parámetros
        window.history.pushState({}, '', window.location.pathname);
    });

    // Descargar PDF
    document.getElementById('btnDescargarPDF')?.addEventListener('click', function() {
        if (planActual) {
            generarPDF(planActual);
        }
    });

    // ========== FUNCIONES DE CARGA DE DATOS ==========

    function cargarEscuelasFacultad(facultadId, callback) {
        mostrarLoading();

        fetch(`/escuelas/api/escuelas/${facultadId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.escuelas.length > 0) {
                    filtroEscuela.innerHTML = '<option value="">Todas las escuelas</option>';

                    data.escuelas.forEach(escuela => {
                        const option = document.createElement('option');
                        option.value = escuela.id;
                        option.textContent = `${escuela.codigo} - ${escuela.nombre}`;
                        filtroEscuela.appendChild(option);
                    });

                    filtroEscuela.disabled = false;

                    if (callback) callback();
                } else {
                    filtroEscuela.innerHTML = '<option value="">No hay escuelas disponibles</option>';
                    mostrarAlerta('No se encontraron escuelas para esta facultad', 'warning');
                }
            })
            .catch(error => {
                console.error('Error al cargar escuelas:', error);
                mostrarAlerta('Error al cargar las escuelas', 'danger');
            })
            .finally(() => {
                ocultarLoading();
            });
    }

    function cargarPlanesEscuela(escuelaId) {
        mostrarLoading();

        fetch(`/planes/api/planes/escuela/${escuelaId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.planes.length > 0) {
                    filtroPlan.innerHTML = '<option value="">Seleccione un plan</option>';

                    data.planes.forEach(plan => {
                        const option = document.createElement('option');
                        option.value = plan.id;
                        option.textContent = `${plan.nombre} (${plan.total_asignaturas} asignaturas)`;
                        filtroPlan.appendChild(option);
                    });

                    filtroPlan.disabled = false;
                } else {
                    filtroPlan.innerHTML = '<option value="">No hay planes disponibles</option>';
                    mostrarAlerta('No se encontraron planes de estudio para esta escuela', 'warning');
                }
            })
            .catch(error => {
                console.error('Error al cargar planes:', error);
                mostrarAlerta('Error al cargar los planes de estudio', 'danger');
            })
            .finally(() => {
                ocultarLoading();
            });
    }

    function cargarPlanDetalle(planId) {
        mostrarLoading();

        fetch(`/planes/api/plan/${planId}/detalle/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    planActual = data.plan;
                    mostrarPlanDetalle(data.plan);

                    // Actualizar URL con parámetros
                    const url = new URL(window.location);
                    url.searchParams.set('plan', planId);
                    window.history.pushState({}, '', url);
                } else {
                    mostrarAlerta('Error al cargar el detalle del plan', 'danger');
                }
            })
            .catch(error => {
                console.error('Error al cargar detalle del plan:', error);
                mostrarAlerta('Error al cargar el detalle del plan', 'danger');
            })
            .finally(() => {
                ocultarLoading();
            });
    }

    // ========== FUNCIONES DE VISUALIZACIÓN ==========

    function mostrarPlanDetalle(plan) {
        // Actualizar información del header
        document.getElementById('planNombre').textContent = plan.nombre;
        document.getElementById('planEscuela').innerHTML = `
            <i class="bi bi-mortarboard me-1"></i>${plan.escuela.nombre}
        `;
        document.getElementById('planFacultad').innerHTML = `
            <i class="bi bi-building me-1"></i>${plan.facultad.siglas}
        `;

        // Actualizar estadísticas
        document.getElementById('statTotalAsignaturas').textContent = plan.total_asignaturas;
        document.getElementById('statTotalCreditos').textContent = plan.total_creditos;
        document.getElementById('statTotalCiclos').textContent = plan.total_ciclos;
        document.getElementById('statDuracion').textContent = calcularDuracion(plan.total_ciclos);

        // Renderizar ciclos
        renderizarCiclos(plan.ciclos);

        // Mostrar visualización
        emptyState.classList.add('d-none');
        planVisualizacion.classList.remove('d-none');

        // Scroll suave al inicio de la visualización
        planVisualizacion.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderizarCiclos(ciclos) {
        ciclosContainer.innerHTML = '';

        ciclos.forEach((ciclo, index) => {
            const cicloCard = crearCicloCard(ciclo, index);
            ciclosContainer.appendChild(cicloCard);
        });
    }

    function crearCicloCard(ciclo, index) {
        const card = document.createElement('div');
        card.className = 'ciclo-card';
        card.style.animationDelay = `${index * 0.05}s`;

        const collapseId = `ciclo${ciclo.ciclo}`;

        card.innerHTML = `
            <div class="ciclo-header" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="true">
                <div class="ciclo-title-section">
                    <div class="ciclo-numero">${ciclo.ciclo}</div>
                    <div class="ciclo-info">
                        <h4>Ciclo ${ciclo.ciclo}</h4>
                        <p>${ciclo.asignaturas.length} asignaturas · ${ciclo.creditos_ciclo} créditos</p>
                    </div>
                </div>
                <div class="ciclo-stats">
                    <div class="ciclo-stat">
                        <span class="ciclo-stat-value">${ciclo.asignaturas.length}</span>
                        <span class="ciclo-stat-label">Cursos</span>
                    </div>
                    <div class="ciclo-stat">
                        <span class="ciclo-stat-value">${ciclo.creditos_ciclo}</span>
                        <span class="ciclo-stat-label">Créditos</span>
                    </div>
                    <i class="bi bi-chevron-up ciclo-toggle"></i>
                </div>
            </div>
            <div id="${collapseId}" class="collapse show">
                <div class="ciclo-body">
                    <div class="asignaturas-grid">
                        ${ciclo.asignaturas.map((asig, idx) => crearAsignaturaCard(asig, idx)).join('')}
                    </div>
                </div>
            </div>
        `;

        // Agregar evento para rotar el ícono
        const header = card.querySelector('.ciclo-header');
        const toggle = card.querySelector('.ciclo-toggle');
        const collapse = card.querySelector('.collapse');

        collapse.addEventListener('show.bs.collapse', () => {
            toggle.classList.remove('collapsed');
        });

        collapse.addEventListener('hide.bs.collapse', () => {
            toggle.classList.add('collapsed');
        });

        return card;
    }

    function crearAsignaturaCard(asignatura, index) {
        const prerequisitosHTML = asignatura.prerequisitos.length > 0 ? `
            <div class="prerequisitos-section">
                <div class="prerequisitos-title">
                    <i class="bi bi-link-45deg"></i> Prerequisitos
                </div>
                <div class="prerequisitos-list">
                    ${asignatura.prerequisitos.map(prereq => `
                        <span class="prerequisito-badge" title="${prereq.nombre}">
                            <i class="bi bi-arrow-left-short"></i>
                            ${prereq.codigo} - ${prereq.nombre}
                        </span>
                    `).join('')}
                </div>
            </div>
        ` : '';

        return `
            <div class="asignatura-card" style="animation-delay: ${index * 0.03}s">
                <div class="asignatura-header">
                    <span class="asignatura-codigo">${asignatura.codigo}</span>
                    <span class="asignatura-tipo tipo-${asignatura.tipo}" title="${asignatura.tipo_display}">
                        ${asignatura.tipo}
                    </span>
                </div>
                <h5 class="asignatura-nombre" title="${asignatura.nombre}">
                    ${asignatura.nombre}
                </h5>
                <div class="asignatura-info">
                    <div class="info-item">
                        <i class="bi bi-star-fill"></i>
                        <strong>${asignatura.creditos}</strong> créditos
                    </div>
                    ${asignatura.horas_teoria > 0 ? `
                        <div class="info-item">
                            <i class="bi bi-book"></i>
                            <strong>${asignatura.horas_teoria}</strong>h teoría
                        </div>
                    ` : ''}
                    ${asignatura.horas_practica > 0 ? `
                        <div class="info-item">
                            <i class="bi bi-pen"></i>
                            <strong>${asignatura.horas_practica}</strong>h práctica
                        </div>
                    ` : ''}
                    ${asignatura.horas_laboratorio > 0 ? `
                        <div class="info-item">
                            <i class="bi bi-pc-display"></i>
                            <strong>${asignatura.horas_laboratorio}</strong>h lab
                        </div>
                    ` : ''}
                </div>
                ${prerequisitosHTML}
            </div>
        `;
    }

    function ocultarVisualizacion() {
        planVisualizacion.classList.add('d-none');
        emptyState.classList.remove('d-none');
        planActual = null;
    }

    // ========== FUNCIONES AUXILIARES ==========

    function calcularDuracion(ciclos) {
        const años = Math.floor(ciclos / 2);
        const semestres = ciclos % 2;

        if (semestres > 0) {
            return `${años}.5 años`;
        } else {
            return `${años} años`;
        }
    }

    function mostrarLoading() {
        loadingOverlay.classList.remove('d-none');
    }

    function ocultarLoading() {
        loadingOverlay.classList.add('d-none');
    }

    function mostrarAlerta(mensaje, tipo = 'info') {
        // Crear alerta Bootstrap
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${tipo} alert-dismissible fade show custom-alert shadow-sm`;
        alertDiv.setAttribute('role', 'alert');

        const iconos = {
            success: 'check-circle-fill',
            danger: 'exclamation-circle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill'
        };

        alertDiv.innerHTML = `
            <div class="d-flex align-items-start gap-3">
                <div class="flex-shrink-0">
                    <i class="bi bi-${iconos[tipo]} fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    ${mensaje}
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Insertar al inicio del main-content
        const mainContent = document.querySelector('.main-content');
        mainContent.insertBefore(alertDiv, mainContent.firstChild);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    function generarPDF(plan) {
        mostrarAlerta('Funcionalidad de exportación a PDF en desarrollo', 'info');
        // TODO: Implementar generación de PDF con reportlab o similar
        console.log('Generando PDF para plan:', plan);
    }

    // ========== BÚSQUEDA EN TIEMPO REAL (OPCIONAL) ==========

    // Agregar funcionalidad de búsqueda si hay un input de búsqueda
    const searchInput = document.querySelector('#searchInput');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);

            searchTimeout = setTimeout(() => {
                const query = e.target.value.trim();

                if (query.length >= 3) {
                    buscarPlanes(query);
                }
            }, 500);
        });
    }

    function buscarPlanes(query) {
        const facultadId = filtroFacultad.value;
        const escuelaId = filtroEscuela.value;

        fetch(`/planes/api/planes/buscar/?q=${encodeURIComponent(query)}&facultad=${facultadId}&escuela=${escuelaId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar resultados de búsqueda
                    console.log('Resultados de búsqueda:', data.planes);
                    // TODO: Implementar vista de resultados
                }
            })
            .catch(error => {
                console.error('Error en búsqueda:', error);
            });
    }

});
