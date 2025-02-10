// Conectar ao servidor Socket.IO
var socket = io();

// Quando receber uma notificação de financeiro
socket.on('notificacao_financeiro', function(data) {
    // Criar notificação usando SweetAlert2
    Swal.fire({
        title: 'Novo Financeiro',
        html: `O usuário ${data.usuario} inseriu dados financeiros na carga ${data.carga_numero}<br>Data: ${data.data}`,
        icon: 'info',
        confirmButtonText: 'OK',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 5000,
        timerProgressBar: true
    });
});
