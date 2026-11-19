
const menuButton=document.getElementById('menu-toggle');
const menu=document.getElementById('nav-menu');
menuButton?.addEventListener('click',()=>{const open=menu.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));});
// Navegación por secciones, incluso dentro del marco de Streamlit.
function closeSiteMenu(){
  menu?.classList.remove('open');
  menuButton?.setAttribute('aria-expanded','false');
}
menu?.querySelectorAll('a[href^="#"]').forEach(link=>{
  link.addEventListener('click',event=>{
    const id=link.getAttribute('href').slice(1);
    const target=document.getElementById(id);
    if(!target)return;
    event.preventDefault();
    closeSiteMenu();
    target.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    if(history.replaceState)history.replaceState(null,'','#'+id);
  });
});
menuButton?.addEventListener('keydown', e=>{if(e.key==='Escape')closeSiteMenu();});
document.addEventListener('keydown', e=>{if(e.key==='Escape')closeSiteMenu();});

const year=document.getElementById('year');if(year)year.textContent=new Date().getFullYear();
const IMAGES=window.SCHOOL_IMAGES||{};
function imageUrl(name){return IMAGES[name]||`assets/${name}`;}
function loadImage(target,filename,hero=false){
 if(!target)return;
 const src=imageUrl(filename);
 const img=new Image();
 img.onload=()=>{target.style.backgroundImage=hero?`linear-gradient(rgba(6,24,43,.65),rgba(6,24,43,.65)),url("${src}")`:`url("${src}")`;target.classList.add(hero?'has-photo':'with-photo');};
 img.onerror=()=>{if(target.matches('.gallery-card')){target.classList.add('unavailable');target.hidden=true;const current=document.querySelector('.filter.active')?.dataset.filter||'todos';applyFilter(current);}};
 img.src=src;
}
loadImage(document.querySelector('.hero-photo'),'fachada.jpg',false);
loadImage(document.querySelector('.institution-photo'),'patio-2.jpeg');
document.querySelectorAll('.gallery-card').forEach(el=>loadImage(el,el.dataset.file));
function applyFilter(value){
 let shown=0;
 document.querySelectorAll('.gallery-card').forEach(card=>{
  const visible=!card.classList.contains('unavailable')&&(value==='todos'||(card.dataset.group||'').split(/\s+/).includes(value));
  card.hidden=!visible;
  if(visible)shown++;
 });
 const empty=document.getElementById('gallery-empty');
 if(empty)empty.hidden=shown>0;
}
document.querySelectorAll('.filter').forEach(btn=>btn.addEventListener('click',()=>{
 document.querySelectorAll('.filter').forEach(b=>{b.classList.toggle('active',b===btn);b.setAttribute('aria-pressed',String(b===btn));});applyFilter(btn.dataset.filter);
}));
const lightbox=document.getElementById('lightbox');
document.querySelectorAll('.gallery-card').forEach(card=>card.addEventListener('click',()=>{
 if(!lightbox||!card.classList.contains('with-photo'))return;
 document.getElementById('dialog-title').textContent=card.dataset.title;
 const content=document.getElementById('dialog-content');content.replaceChildren();
 const img=document.createElement('img');img.src=imageUrl(card.dataset.file);img.alt=card.dataset.title;content.appendChild(img);
 if(lightbox.showModal)lightbox.showModal();
}));
document.getElementById('close-dialog')?.addEventListener('click',()=>lightbox.close());
lightbox?.addEventListener('click',e=>{if(e.target===lightbox)lightbox.close();});

// El código mantiene una galería segura: fotos ausentes no muestran bloques rotos.


// Animacion de entrada discreta, con soporte para filtros y accesibilidad.
(function setupScrollReveal(){
 const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
 const targets=[...document.querySelectorAll('.section .heading, .institution-info, .institution-photo, .level, .gallery-card, .info-banner, .news-clean, .contact-about, .social-card')];
 if(reduce.matches || !('IntersectionObserver' in window)) return;
 const observer=new IntersectionObserver(entries=>{
  for(const entry of entries){
   if(!entry.isIntersecting)continue;
   entry.target.classList.add('is-visible');
   observer.unobserve(entry.target);
  }
 },{threshold:0.08,rootMargin:'0px 0px -18px 0px'});
 for(const el of targets){
  // No ocultar elementos que ya aparecen en pantalla al comenzar.
  if(el.getBoundingClientRect().top < window.innerHeight * .96)continue;
  el.classList.add('reveal-ready');
  observer.observe(el);
 }
 // Respeta cambio de preferencia de movimiento durante la navegacion.
 reduce.addEventListener?.('change',e=>{if(e.matches)targets.forEach(el=>el.classList.add('is-visible'));});
})();

// Evita cargar/reproducir video si se solicitan movimientos reducidos.
(function setupHeroVideo(){
 const video=document.querySelector('.hero-background-video');
 if(!video)return;
 const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
 function sync(){if(reduce.matches){video.pause();return;}video.play().catch(()=>{});}
 sync();
 reduce.addEventListener?.('change',sync);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();else sync();});
})();
