// frontend/src/utils/pdf.js
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';

GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.js`;

export const loadPdf = async (url) => {
  const pdf = await getDocument(url).promise;
  return pdf;
};

export const renderPage = async (pdf, pageNumber, canvasContext) => {
  const page = await pdf.getPage(pageNumber);
  const viewport = page.getViewport({ scale: 1 });
  canvasContext.canvas.height = viewport.height;
  canvasContext.canvas.width = viewport.width;

  const renderContext = {
    canvasContext,
    viewport,
  };
  await page.render(renderContext).promise;
};