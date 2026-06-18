import html2canvas from 'html2canvas';

function hideElements(root, selectors) {
  const hidden = [];
  selectors.forEach((selector) => {
    root.querySelectorAll(selector).forEach((el) => {
      hidden.push({ el, display: el.style.display });
      el.style.display = 'none';
    });
  });
  return hidden;
}

function restoreHidden(hidden) {
  hidden.forEach(({ el, display }) => {
    el.style.display = display;
  });
}

function backupStyle(el, props) {
  const values = {};
  props.forEach((prop) => {
    values[prop] = el.style[prop];
  });
  return { el, values };
}

function restoreStyles(backups) {
  backups.forEach(({ el, values }) => {
    Object.entries(values).forEach(([prop, value]) => {
      el.style[prop] = value;
    });
  });
}

function expandForCapture(element) {
  const backups = [];
  const expand = (el, extra = []) => {
    if (!el) return;
    backups.push(backupStyle(el, ['overflow', 'overflowX', 'overflowY', 'width', 'maxWidth', ...extra]));
    el.style.overflow = 'visible';
    el.style.overflowX = 'visible';
    el.style.overflowY = 'visible';
    el.style.maxWidth = 'none';
  };

  expand(element);
  expand(element.querySelector('.grid-wrapper'));
  expand(element.querySelector('.map-container'));

  const table = element.querySelector('.hos-grid');
  if (table) {
    backups.push(backupStyle(table, ['width', 'minWidth']));
    const fullWidth = Math.max(table.scrollWidth, table.offsetWidth);
    table.style.width = `${fullWidth}px`;
    table.style.minWidth = `${fullWidth}px`;

    const gridWrapper = element.querySelector('.grid-wrapper');
    if (gridWrapper) gridWrapper.style.width = `${fullWidth}px`;

    const padding = 48;
    element.style.width = `${fullWidth + padding}px`;
  } else {
    element.style.width = `${element.scrollWidth}px`;
  }

  return backups;
}

/** Capture a DOM node as canvas, expanding scrollable children so nothing is clipped. */
export async function captureElement(element, options = {}) {
  const {
    hideSelectors = ['.log-download-btn'],
    backgroundColor = '#1e293b',
    scale = 2,
    waitMs = 0,
  } = options;

  if (!element) throw new Error('No element to capture');

  element.scrollIntoView({ block: 'nearest' });
  if (waitMs > 0) {
    await new Promise((resolve) => setTimeout(resolve, waitMs));
  }

  const hidden = hideElements(element, hideSelectors);
  const styleBackups = expandForCapture(element);

  await new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  });

  const width = element.scrollWidth;
  const height = element.scrollHeight;

  try {
    return await html2canvas(element, {
      scale,
      useCORS: true,
      allowTaint: true,
      logging: false,
      backgroundColor,
      width,
      height,
      windowWidth: width,
      windowHeight: height,
      scrollX: 0,
      scrollY: 0,
      x: 0,
      y: 0,
    });
  } finally {
    restoreStyles(styleBackups);
    restoreHidden(hidden);
  }
}
