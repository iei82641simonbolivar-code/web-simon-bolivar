const menuButton=document.getElementById('menu-toggle');
const menu=document.getElementById('nav-menu');
menuButton?.addEventListener('click',()=>{const open=menu.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));});
menu?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{menu.classList.remove('open');menuButton?.setAttribute('aria-expanded','false');}));
const year=document.getElementById('year'); if(year) year.textContent=new Date().getFullYear();
// app.py incorpora las imágenes en este diccionario para Streamlit.
// Si se abre el HTML fuera de Streamlit, se usan rutas relativas.
function imageUrl(name){return (window.SCHOOL_IMAGES||{})[name]||`assets/${name}`;}
function loadImage(target,filename,hero=false){
 if(!target)return;
 const img=new Image();
 img.onload=()=>{
  const url=imageUrl(filename);
  target.style.backgroundImage=hero?`linear-gradient(#102a4d44,#102a4d44),url("${url}")`:`url("${url}")`;
  target.classList.add(hero?'has-photo':'with-photo');
 };
 img.onerror=()=>{if(target.classList.contains('gallery-card'))target.classList.add('unavailable');};
 img.src=imageUrl(filename);
}
loadImage(document.querySelector('.hero-photo'),'fachada.jpg',true);
loadImage(document.querySelector('.institution-photo'),'patio-2.jpeg');
document.querySelectorAll('.gallery-card').forEach(el=>loadImage(el,el.dataset.file));
document.querySelectorAll('.filter').forEach(btn=>btn.addEventListener('click',()=>{
 document.querySelectorAll('.filter').forEach(b=>{b.classList.toggle('active',b===btn);b.setAttribute('aria-pressed',String(b===btn));});
 document.querySelectorAll('.gallery-card').forEach(card=>{card.hidden=btn.dataset.filter!=='todos'&&card.dataset.group!==btn.dataset.filter;});
}));
const lightbox=document.getElementById('lightbox');
document.querySelectorAll('.gallery-card').forEach(card=>card.addEventListener('click',()=>{
 if(!lightbox||!card.classList.contains('with-photo'))return;
 document.getElementById('dialog-title').textContent=card.dataset.title;
 const content=document.getElementById('dialog-content');content.replaceChildren();
 const image=document.createElement('img');image.src=imageUrl(card.dataset.file);image.alt=card.dataset.title;content.appendChild(image);
 if(typeof lightbox.showModal==='function')lightbox.showModal();
}));
document.getElementById('close-dialog')?.addEventListener('click',()=>lightbox.close());
lightbox?.addEventListener('click',e=>{if(e.target===lightbox)lightbox.close();});
