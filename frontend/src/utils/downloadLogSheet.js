import { captureElement } from './captureElement';

export async function downloadLogSheetImage(element, filename = 'daily-log.png') {
  if (!element) return;

  const canvas = await captureElement(element, {
    hideSelectors: ['.log-download-btn'],
    backgroundColor: '#1e293b',
    scale: 2,
  });

  const link = document.createElement('a');
  link.download = filename;
  link.href = canvas.toDataURL('image/png');
  link.click();
}
