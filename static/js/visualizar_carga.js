document.addEventListener('DOMContentLoaded', function() {
    // Formatar valores monetários dos romaneios
    document.querySelectorAll('.valor-monetario-romaneio').forEach(function(element) {
        const valor = parseFloat(element.textContent);
        if (!isNaN(valor)) {
            element.textContent = valor.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });
        }
    });

    // Formatar valores monetários das devoluções
    document.querySelectorAll('.valor-monetario-devolucao').forEach(function(element) {
        const valor = parseFloat(element.textContent);
        if (!isNaN(valor)) {
            element.textContent = valor.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });
        }
    });
});
