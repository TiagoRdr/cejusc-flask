document.getElementById('btn_salario_minimo').addEventListener('click', function() {
    Swal.fire({
        title: 'Insira o Salário Mínimo',
        input: 'text',
        inputLabel: 'Salário Mínimo Atual',
        inputPlaceholder: 'Digite o valor...',
        showCancelButton: true,
        confirmButtonText: 'Confirmar',
        cancelButtonText: 'Cancelar',
        inputValidator: (value) => {
            if (!value) {
                return 'Por favor, insira um valor';
            }
        }
    }).then((result) => {
        if (result.isConfirmed) {
            // Envia o valor para o backend
            const salarioMinimo = result.value;

            fetch('/minimal-wage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',  // Certifique-se que está configurado como application/json
                },
                body: JSON.stringify({ salario_minimo: salarioMinimo }) // Certifique-se de que os dados estão em formato JSON
            })
            .then(response => {
                if (response.ok) {
                    // Se a requisição for bem-sucedida, redireciona para /minimal-wage
                    window.location.href = '/minimal-wage';
                } else {
                    Swal.fire('Erro!', 'Houve um problema ao enviar os dados.', 'error');
                }
            })
            .catch(error => {
                Swal.fire('Erro!', 'Houve um problema ao enviar os dados.', 'error');
            });
        }
    });
});
