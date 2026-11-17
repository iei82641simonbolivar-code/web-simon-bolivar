
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
loadImage(document.querySelector('.hero-photo'),'fachada.jpg',true);
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
