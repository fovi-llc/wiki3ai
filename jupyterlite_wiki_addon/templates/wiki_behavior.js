(function() {
  const body = document.body;
  const status = document.getElementById('wiki-share-status');
  const applyTheme = (isDark) => {
    body.classList.toggle('jp-mod-dark', isDark);
    body.classList.toggle('jp-mod-light', !isDark);
    body.setAttribute('data-jp-theme-light', String(!isDark));
    body.setAttribute('data-jp-theme-name', isDark ? 'JupyterLab Dark' : 'JupyterLab Light');
  };
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  applyTheme(media.matches);
  if (media.addEventListener) {
    media.addEventListener('change', (event) => applyTheme(event.matches));
  } else if (media.addListener) {
    media.addListener((event) => applyTheme(event.matches));
  }
  const announce = (message) => {
    if (!status) {
      return;
    }
    status.textContent = message;
    window.setTimeout(() => { status.textContent = ''; }, 1500);
  };
  body.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-share]');
    if (!trigger) {
      return;
    }
    event.preventDefault();
    const shareTarget = trigger.getAttribute('data-share') || window.location.pathname;
    const url = new URL(shareTarget, window.location.origin).toString();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(() => {
        trigger.classList.add('wiki-share-success');
        window.setTimeout(() => trigger.classList.remove('wiki-share-success'), 1500);
        announce('Link copied to clipboard.');
      }).catch(() => {
        window.prompt('Copy this link', url);
      });
    } else {
      window.prompt('Copy this link', url);
    }
  });
})();
