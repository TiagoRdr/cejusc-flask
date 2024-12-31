function showAlert() {
    Swal.fire({
        title: "Confirme a estatística",
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Confirmar"
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: "Estatística Salva!",
                icon: "success"
            }).then(() => {
                document.getElementById("saveForm").submit();
            });
        }
    });
}

function updateTotals() {
    // Função placeholder caso haja cálculos automáticos a serem adicionados
}
