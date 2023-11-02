const editFileInput = document.getElementById("editPdfUpload");
const editPreviewContainer = document.getElementById("editPdfPreview");
const editDocumentListContainer = document.getElementById("editDocumentList");

let editPdf = null;
let editCurrentPage = 1;
let editTotalPages = 0;

editFileInput.addEventListener("change", function () {
  const editFile = editFileInput.files[0];
  const reader = new FileReader();

  reader.onload = function () {
    const typedarray = new Uint8Array(reader.result);
    const loadingTask = pdfjsLib.getDocument(typedarray);

    loadingTask.promise.then(function (pdfDocument) {
      editPdf = pdfDocument;
      editTotalPages = editPdf.numPages;

      editRenderPage(editCurrentPage);
      editRenderDocumentList();
    });
  };

  reader.readAsArrayBuffer(editFile);
});

function editRenderPage(pageNumber) {
  editPdf.getPage(pageNumber).then(function (page) {
    const viewport = page.getViewport({ scale: 0.8 });
    const canvas = document.createElement("canvas");
    const canvasContext = canvas.getContext("2d");
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    const renderContext = {
      canvasContext: canvasContext,
      viewport: viewport,
    };

    page.render(renderContext).promise.then(function () {
      editPreviewContainer.innerHTML = "";
      editPreviewContainer.appendChild(canvas);
    });
  });
}

function editRenderDocumentList() {
  editDocumentListContainer.innerHTML = "";

  for (let i = 1; i <= editTotalPages; i++) {
    const documentItem = document.createElement("div");
    documentItem.classList.add("document-item");
    documentItem.textContent = `Page ${i}`;

    if (i === editCurrentPage) {
      documentItem.classList.add("active");
    }

    documentItem.addEventListener("click", function () {
      editCurrentPage = i;
      editRenderPage(editCurrentPage);
      editUpdateDocumentList();
    });

    editDocumentListContainer.appendChild(documentItem);
  }
}

function editUpdateDocumentList() {
  const documentItems =
    editDocumentListContainer.getElementsByClassName("document-item");
  for (let i = 0; i < documentItems.length; i++) {
    const documentItem = documentItems[i];
    const pageNumber = i + 1;

    if (pageNumber === editCurrentPage) {
      documentItem.classList.add("active");
    } else {
      documentItem.classList.remove("active");
    }
  }
}
