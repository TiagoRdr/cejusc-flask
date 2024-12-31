// Ajusta a tabela dinamicamente
window.addEventListener('resize', function () {
    const table = document.querySelector('table');
    table.style.fontSize = window.innerWidth < 600 ? '12px' : '14px';
});

// Exportar tabela para Excel
document.getElementById('export_excel').addEventListener('click', function () {
    const table = document.getElementById('tabela_salario');
    const wb = XLSX.utils.table_to_book(table, { sheet: "Sheet1" });
    XLSX.writeFile(wb, 'tabela_salario.xlsx');
});

// Exportar tabela para PDF
async function exportTableToPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const imgPath = "../static/Logo-CEJUSC-1024x908.png";
    const imgX = 90, imgY = 2, imgWidth = 28, imgHeight = 25;
    const titleY = imgY + imgHeight + 10;

    const tableContainer = document.getElementById("tabela_salario");

    const img = new Image();
    img.src = imgPath;

    img.onload = async function () {
        doc.addImage(img, "PNG", imgX, imgY, imgWidth, imgHeight);

        await html2canvas(tableContainer).then((canvas) => {
            const imgData = canvas.toDataURL("image/png");
            const tableImgWidth = 190;
            const tableImgHeight = (canvas.height * tableImgWidth) / canvas.width;

            let heightLeft = tableImgHeight;
            let position = titleY + 1;

            doc.addImage(imgData, "PNG", 10, position, tableImgWidth, tableImgHeight);
            heightLeft -= 295;

            while (heightLeft >= 0) {
                doc.addPage();
                doc.addImage(imgData, "PNG", 10, position, tableImgWidth, tableImgHeight);
                heightLeft -= 295;
            }
        });

        doc.save("tabela_salario.pdf");
    };
}
