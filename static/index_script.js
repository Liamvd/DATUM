//Start questionnaires
document.getElementById('startUpload').addEventListener('click', function() {
  document.getElementById('back').classList.toggle('hidden');
  document.getElementById('form-portal').classList.toggle('hidden');
  document.getElementById('uploadDiv').classList.toggle('hidden');
});

document.getElementById('back').addEventListener('click', function() {
  document.getElementById('back').classList.toggle('hidden');
  document.getElementById('form-portal').classList.toggle('hidden');
  document.getElementById('uploadDiv').classList.toggle('hidden');
});

document.querySelectorAll('.collapse-btn').forEach(button => {
  button.addEventListener('click', function() {
    event.stopPropagation();
    event.preventDefault();

    const box = this.closest('.uploadBox');
    const content = box.querySelector('.uploadContent');

    if (box.classList.contains('active')) {
      content.style.height = content.scrollHeight + 'px';
      requestAnimationFrame(() => {
        content.style.height = '0';
      });
      box.classList.remove('active');
      this.setAttribute('aria-expanded', 'false');
    } else {
      content.style.height = content.scrollHeight + 'px';
      box.classList.add('active');
      this.setAttribute('aria-expanded', 'true');

      content.addEventListener('transitionend', function handler() {
        content.style.height = 'auto';
        content.removeEventListener('transitionend', handler);
      });
    }
  });
});

function uploadData() {
    const inputFile = document.getElementById('fileInput').value;
    const inputUrl = document.getElementById('urlInput').value;
    const inputText = document.getElementById('plaintextInput').value;
    fetch('/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file: inputFile, url: inputUrl, text: inputText })
    })
    .then(response => response.json())
    .then(data => {
        // create text input table
        const containerOriginal = document.getElementById('originalData');

        const tableOriginalData = document.createElement('table');

        tableOriginalData.style.borderCollapse = 'collapse';
        tableOriginalData.style.width = '100%';

        const tbody = tableOriginalData.createTBody();

        // An array to hold the data for the rows
        const rowsData = [
            ['File input', inputFile],
            ['Url input', inputUrl],
            ['Text input', inputText]
        ];

        // Loop through the data to create each row
        rowsData.forEach(rowData => {
            // Create a new row in the table body
            const row = tbody.insertRow();

            // Add the header cell (first cell)
            const headerCell = row.insertCell();
            headerCell.textContent = rowData[0];
            // Optional: make the header cell bold
            headerCell.style.fontWeight = 'bold';
            headerCell.style.border = '1px solid black'; // Adds the border
            headerCell.style.textAlign = 'left';         // Aligns text to the left
            headerCell.style.padding = '8px';

            // Add the value cell (second cell)
            const valueCell = row.insertCell();
            valueCell.textContent = rowData[1];
            valueCell.style.border = '1px solid black';  // Adds the border
            valueCell.style.textAlign = 'left';          // Aligns text to the left
            valueCell.style.padding = '8px';
        });

        containerOriginal.innerHTML = '';
        containerOriginal.appendChild(tableOriginalData);

        console.log(data)
        console.log(data.rdf_transformed)
        console.log(data.rdf_transformed.Text_input)
        const container = document.getElementById('rdfData');
        container.innerHTML = '';
        const table = document.createElement('table');
        table.style.borderCollapse = 'collapse';
        table.style.width = '100%';

        const tbodyNew = table.createTBody();

        // Create an array with the desired headers and corresponding data paths
        const rowsDataNew = [
            ['File input', data.rdf_transformed.File_input],
            ['Url input', data.rdf_transformed.Url_input],
            ['Text input', data.rdf_transformed.Text_input]
        ];

        // Loop through the data to create each row
        rowsDataNew.forEach(rowDataNew => {
            const rowNew = tbodyNew.insertRow();

            // Create and style the header cell
            const headerCellNew = rowNew.insertCell();
            headerCellNew.textContent = rowDataNew[0];
            headerCellNew.style.fontWeight = 'bold';
            headerCellNew.style.border = '1px solid black';
            headerCellNew.style.textAlign = 'left';
            headerCellNew.style.padding = '8px';
            // Align header to the top, which is useful for multi-line content
            headerCellNew.style.verticalAlign = 'top';

            // Create and style the value cell
            const valueCellNew = rowNew.insertCell();
            valueCellNew.textContent = rowDataNew[1];
            valueCellNew.style.border = '1px solid black';
            valueCellNew.style.textAlign = 'left';
            valueCellNew.style.padding = '8px';
            // This style preserves whitespace and line breaks from your source data
            valueCellNew.style.whiteSpace = 'pre-wrap';
        });

        // Add the finished table to the container
        container.appendChild(table);
    });
    document.getElementById('back').classList.toggle('hidden');
    document.getElementById('uploadDiv').classList.toggle('hidden');
    document.getElementById('transformedData').classList.toggle('hidden');
}

function addMetadata() {
    document.getElementById('transformedData').classList.toggle('hidden');
    document.getElementById('metadataDiv').classList.toggle('hidden');
}

function exportData() {
    document.getElementById('metadataDiv').classList.toggle('hidden');
    document.getElementById('exportDiv').classList.toggle('hidden');
}

function exportAllegrograph() {
    fetch('/export', {
        method: 'POST',
    })
}

function startOver() {
    document.getElementById('exportDiv').classList.toggle('hidden');
    document.getElementById('back').classList.toggle('hidden');
    document.getElementById('uploadDiv').classList.toggle('hidden');
}