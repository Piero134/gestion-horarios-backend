// static/js/facultades.js

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const table = document.getElementById('facultadesTable');

    if (searchInput && table) {
        searchInput.addEventListener('keyup', function() {
            const filter = searchInput.value.toLowerCase();
            const rows = table.getElementsByTagName('tr');

            // Comenzamos desde el índice 1 para saltar el encabezado (thead)
            for (let i = 1; i < rows.length; i++) {
                const nombreCell = rows[i].getElementsByTagName('td')[2]; // Columna Nombre
                const siglasCell = rows[i].getElementsByTagName('td')[1]; // Columna Siglas

                if (nombreCell && siglasCell) {
                    const nombreText = nombreCell.textContent || nombreCell.innerText;
                    const siglasText = siglasCell.textContent || siglasCell.innerText;

                    if (nombreText.toLowerCase().indexOf(filter) > -1 || siglasText.toLowerCase().indexOf(filter) > -1) {
                        rows[i].style.display = "";
                    } else {
                        rows[i].style.display = "none";
                    }
                }
            }
        });
    }
});
