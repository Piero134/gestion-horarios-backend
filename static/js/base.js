document.addEventListener('DOMContentLoaded', function() {
    // 1. Sidebar Toggle Mobile
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('show');
        });
    }

    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 992 && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    const btnExportar = document.getElementById('btnExportarExcel');
    if (btnExportar) {
        btnExportar.addEventListener('click', function(e) {
            e.preventDefault();
            exportarExcel();
        });
    }

    function exportarExcel() {
        // Obtener parámetros de búsqueda actuales para filtrar el Excel igual que la tabla
        const params = new URLSearchParams(window.location.search);
        const exportUrl = `/grupos/api/grupos/exportar_excel/?${params.toString()}`;

        fetch(exportUrl)
            .then(async response => {
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || "Error al generar el reporte");
                }

                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = "reporte_grupos.xlsx";

                if (contentDisposition && contentDisposition.includes('filename=')) {
                    filename = contentDisposition.split('filename=')[1].replace(/['"]/g, '');
                }

                return response.blob().then(blob => ({ blob, filename }));
            })
            .then(({ blob, filename }) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();

                window.URL.revokeObjectURL(url);
                a.remove();

                if (typeof mostrarToast === "function") {
                    mostrarToast('Reporte descargado exitosamente', 'success');
                }
            })
            .catch(error => {
                console.error("Error en la exportación:", error);
                if (typeof mostrarToast === "function") {
                    mostrarToast(error.message, 'danger');
                }
            });
    }
});
