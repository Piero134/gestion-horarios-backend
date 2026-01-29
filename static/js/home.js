document.addEventListener('DOMContentLoaded', function() {
    // 1. Obtener datos del template (JSON Script)
    const dataScript = document.getElementById('chart-data');
    if (!dataScript) return;

    const rawData = JSON.parse(dataScript.textContent);

    // Preparar arrays para Chart.js
    const labels = rawData.map(item => item.nombre);
    const dataValues = rawData.map(item => item.cantidad);

    // 2. Configuración del Gráfico
    const ctx = document.getElementById('vacantesChart').getContext('2d');

    // Detectar colores según variables CSS (aproximación)
    const style = getComputedStyle(document.body);
    const colorRed = style.getPropertyValue('--unmsm-red').trim();
    const colorGold = style.getPropertyValue('--unmsm-gold').trim();
    const colorText = style.getPropertyValue('--text-secondary').trim();

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Vacantes Ofertadas',
                data: dataValues,
                backgroundColor: [
                    colorRed,   // Ingeniería de Software
                    colorGold,  // Ingeniería de Sistemas
                    '#2c3e50'   // Otros (Ciencias de la computación?)
                ],
                borderRadius: 6,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    padding: 12,
                    titleFont: { family: "'Sora', sans-serif", size: 13 },
                    bodyFont: { family: "'IBM Plex Sans', sans-serif", size: 13 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        color: colorText,
                        font: { family: "'IBM Plex Sans', sans-serif" }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: colorText,
                        font: { family: "'Sora', sans-serif", weight: '600' }
                    }
                }
            }
        }
    });
});
