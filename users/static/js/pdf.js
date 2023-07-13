const fileInput = document.getElementById('pdfUpload');
const previewContainer = document.getElementById('pdf-preview');
const documentListContainer = document.getElementById('document-list');

let pdf = null;
let currentPage = 1;
let totalPages = 0;

fileInput.addEventListener('change', function () {
  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onload = function () {
    const typedarray = new Uint8Array(reader.result);
    const loadingTask = pdfjsLib.getDocument(typedarray);

    loadingTask.promise.then(function (pdfDocument) {
      pdf = pdfDocument;
      totalPages = pdf.numPages;

      renderPage(currentPage);
      renderDocumentList();
    });
  };

  reader.readAsArrayBuffer(file);
});

function renderPage(pageNumber) {
  pdf.getPage(pageNumber).then(function (page) {
    const viewport = page.getViewport({ scale: 0.8 });
    const canvas = document.createElement('canvas');
    const canvasContext = canvas.getContext('2d');
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    const renderContext = {
      canvasContext: canvasContext,
      viewport: viewport
    };

    page.render(renderContext).promise.then(function () {

      previewContainer.innerHTML = '';
      previewContainer.appendChild(canvas);
    });
  });
}

function renderDocumentList() {
  documentListContainer.innerHTML = '';

  for (let i = 1; i <= totalPages; i++) {
    const documentItem = document.createElement('div');
    documentItem.classList.add('document-item');
    documentItem.textContent = `Page ${i}`;

    if (i === currentPage) {
      documentItem.classList.add('active');
    }

    documentItem.addEventListener('click', function () {
      currentPage = i;
      renderPage(currentPage);
      updateDocumentList();
    });

    documentListContainer.appendChild(documentItem);
  }
}

function updateDocumentList() {
  const documentItems = documentListContainer.getElementsByClassName('document-item');
  for (let i = 0; i < documentItems.length; i++) {
    const documentItem = documentItems[i];
    const pageNumber = i + 1;

    if (pageNumber === currentPage) {
      documentItem.classList.add('active');
    } else {
      documentItem.classList.remove('active');
    }
  }
}