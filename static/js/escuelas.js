document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const table = document.getElementById('escuelasTable');

    // Función auxiliar para quitar tildes y convertir a minúsculas
    function normalizarTexto(texto) {
        return texto
            .normalize("NFD")           // Separa la letra del acento (ej. 'á' se vuelve 'a' + '´')
            .replace(/[\u0300-\u036f]/g, "") // Borra los símbolos de acento
            .toLowerCase();             // Convierte a minúsculas
    }

    if (searchInput && table) {
        searchInput.addEventListener('keyup', function() {
            // 1. Normalizamos lo que escribe el usuario
            const filter = normalizarTexto(searchInput.value);

            const rows = table.getElementsByTagName('tr');

            // Empezamos desde 1 para saltar el encabezado
            for (let i = 1; i < rows.length; i++) {
                const codigoCell = rows[i].getElementsByTagName('td')[0];
                const nombreCell = rows[i].getElementsByTagName('td')[1];
                const facultadCell = rows[i].getElementsByTagName('td')[2];

                let textoFila = "";

                if (codigoCell) textoFila += codigoCell.textContent || codigoCell.innerText;
                if (nombreCell) textoFila += nombreCell.textContent || nombreCell.innerText;
                if (facultadCell) textoFila += facultadCell.textContent || facultadCell.innerText;

                // 2. Normalizamos el texto de la fila antes de comparar
                if (normalizarTexto(textoFila).indexOf(filter) > -1) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        });
    }
});
