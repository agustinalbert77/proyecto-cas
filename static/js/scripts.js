function openModal(src, title, desc){
  const m = document.getElementById('photoModal');
  document.getElementById('modalImg').src = src;
  document.getElementById('modalTitle').innerText = title;
  document.getElementById('modalDesc').innerText = desc;
  m.classList.add('show');
}
function closeModal(ev){
  const m = document.getElementById('photoModal');
  if(!ev || ev.target.id === 'photoModal' || ev.target.classList.contains('close')){
    m.classList.remove('show');
  }
}
