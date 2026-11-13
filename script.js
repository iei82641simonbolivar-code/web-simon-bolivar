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

// PUBLICACIONES OFICIALES: desde noticias.json, incrustadas por app.py.
// No se insertan textos HTML de terceros: todo contenido se escribe con textContent.
(function () {
  const root = document.getElementById('news-results');
  const empty = document.getElementById('news-empty');
  const search = document.getElementById('news-search');
  const filters = document.querySelectorAll('.news-filter');
  if (!root || !empty || !search) return;
  const records = Array.isArray(window.__NOTICIAS__) ? window.__NOTICIAS__ : [];
  let active = 'todos';
  const labels = {comunicado:'Comunicado', actividad:'Actividad', documento:'Documento'};
  function make(tag, className, text){const node = document.createElement(tag);if(className)node.className=className;if(text !== undefined)node.textContent=text;return node;}
  function validUrl(value){if(typeof value !== 'string' || !value.trim())return null;try {const url=new URL(value,window.location.href);return ['https:','http:'].includes(url.protocol)?url.href:null;}catch(e){return null;}}
  function draw(){
    const q=search.value.trim().toLocaleLowerCase('es');
    const found=records.filter(item=>item && typeof item==='object' && item.publicado===true && labels[item.tipo] && typeof item.titulo==='string' && item.titulo.trim()).filter(item=>(active==='todos'||item.tipo===active)&&[item.titulo,item.resumen,item.fecha].join(' ').toLocaleLowerCase('es').includes(q)).sort((a,b)=>String(b.fecha||'').localeCompare(String(a.fecha||'')));
    root.replaceChildren();empty.hidden=found.length>0;
    empty.textContent=records.some(i=>i && i.publicado===true) ? 'No se encontraron publicaciones con esos filtros.' : 'Conoce las últimas novedades del colegio en su página de Facebook.';
    found.forEach(item=>{
      const card=make('article','card news-item');
      card.appendChild(make('span','news-category',labels[item.tipo]));
      if(typeof item.fecha==='string' && /^\d{4}-\d{2}-\d{2}$/.test(item.fecha)){
        const time=make('time','',item.fecha.split('-').reverse().join('/'));time.dateTime=item.fecha;card.appendChild(time);
      }
      card.appendChild(make('h3','',item.titulo));
      if(item.resumen)card.appendChild(make('p','',String(item.resumen)));
      const safe=validUrl(item.enlace);
      if(safe){const link=make('a','','Abrir publicación ↗');link.href=safe;link.target='_blank';link.rel='noopener noreferrer';card.appendChild(link);}
      root.appendChild(card);
    });
  }
  filters.forEach(b=>b.addEventListener('click',()=>{active=b.dataset.kind;filters.forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});draw();}));
  if(!records.some(i=>i && i.publicado===true)){ const toolbar=document.querySelector('.news-toolbar'); if(toolbar) toolbar.hidden=true; }
  search.addEventListener('input',draw);draw();
})();
