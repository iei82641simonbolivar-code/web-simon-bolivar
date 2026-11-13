const cfg = window.COLE_CONFIG || {};
const menuButton = document.getElementById('menu-toggle');
const menu = document.getElementById('nav-menu');
menuButton.addEventListener('click', () => {
  const open = menu.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});
menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  menu.classList.remove('open'); menuButton.setAttribute('aria-expanded', 'false');
}));
document.getElementById('year').textContent = new Date().getFullYear();

function loadImage(target, filename, hero=false) {
  const url = `assets/${filename}`;
  const img = new Image();
  img.onload = () => {
    target.style.backgroundImage = hero ? `linear-gradient(#102a4d44,#102a4d44),url("${url}")` : `url("${url}")`;
    target.classList.add(hero ? 'has-photo' : 'with-photo');
  };
  img.src = url;
}
loadImage(document.querySelector('.hero-photo'), 'fachada.jpg', true);
document.querySelectorAll('.gallery-card').forEach(el => loadImage(el, el.dataset.file));

document.querySelectorAll('.filter').forEach(btn => btn.addEventListener('click', () => {
  document.querySelectorAll('.filter').forEach(b => { b.classList.toggle('active', b === btn); b.setAttribute('aria-pressed', String(b===btn)); });
  document.querySelectorAll('.gallery-card').forEach(card => {
    card.hidden = btn.dataset.filter !== 'todos' && card.dataset.group !== btn.dataset.filter;
  });
}));
const lightbox = document.getElementById('lightbox');
document.querySelectorAll('.gallery-card').forEach(card => card.addEventListener('click', () => {
  document.getElementById('dialog-title').textContent = card.dataset.title;
  const content = document.getElementById('dialog-content');
  content.replaceChildren();
  if(card.classList.contains('with-photo')){
    const image = document.createElement('img');
    image.src = `assets/${card.dataset.file}`; image.alt = card.dataset.title;
    content.appendChild(image);
  } else {
    const p = document.createElement('p'); p.textContent = 'Fotografía pendiente de aprobación institucional.'; content.appendChild(p);
  }
  lightbox.showModal();
}));
document.getElementById('close-dialog').addEventListener('click', () => lightbox.close());
lightbox.addEventListener('click', e => { if(e.target===lightbox) lightbox.close(); });

const number = String(cfg.whatsappNumber || '').replace(/\D/g,'');
if(number) {
  const url = `https://wa.me/${number}?text=${encodeURIComponent(cfg.whatsappMessage || 'Hola')}`;
  for(const id of ['wa-button', 'wa-float']){
    const a = document.getElementById(id); a.href=url; a.target='_blank'; a.rel='noopener noreferrer';
    a.classList.remove('disabled'); a.removeAttribute('aria-disabled'); a.removeAttribute('tabindex');
  }
  document.getElementById('wa-button').textContent = 'Consultar por WhatsApp ↗';
  document.getElementById('wa-float').title = 'Abrir WhatsApp';
  document.getElementById('wa-float').setAttribute('aria-label','Abrir WhatsApp');
  document.getElementById('wa-description').textContent = 'Escríbenos al WhatsApp institucional. Si WAHA y n8n están conectados al número, recibirás atención automatizada.';
}
