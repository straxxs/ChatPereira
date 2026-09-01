let medicoConsultasCache = [];
let currentDoctorChatId = null;

async function loadMedico() {
  const box = document.getElementById('medicoConsultas');
  const r = await fetch('/consultas/pendientes');
  if (!r.ok) { box.innerHTML = '<div class="empty">No se pudieron cargar las consultas.</div>'; return; }
  medicoConsultasCache = await r.json();
  renderDoctorList();
}

function renderDoctorList() {
  const box = document.getElementById('medicoConsultas');
  box.innerHTML = medicoConsultasCache.length ? medicoConsultasCache.map(c => `
    <button class="doctor-item doctor-item-button" type="button" onclick="openDoctorChat(${c.id_consulta})">
      <div class="conversation-avatar">${escapeHtml((c.paciente_nombre || 'P').charAt(0).toUpperCase())}</div>
      <div class="doctor-item-content">
        <div class="conversation-top"><h3>${escapeHtml(c.paciente_nombre)}</h3><span>${formatDoctorDate(c.ultimo_mensaje_fecha || c.fecha_hora)}</span></div>
        <p class="conversation-id">Consulta #${c.id_consulta}</p>
        <p class="conversation-preview">${escapeHtml(c.ultimo_mensaje || c.descripcion_sintomas || 'Sin mensajes')}</p>
      </div>
      <div class="conversation-side">
        <span class="badge badge-${String(c.estado).toLowerCase().replaceAll(' ', '_')}">${escapeHtml(c.estado)}</span>
        <span class="message-count">${Number(c.cantidad_mensajes || 0)} mensajes</span>
        ${c.ultimo_mensaje_tipo === 'paciente' ? '<span class="new-message">Nuevo mensaje</span>' : ''}
      </div>
    </button>`).join('') : '<div class="empty">No hay consultas pendientes.</div>';
}

async function openDoctorChat(id) {
  const consulta = medicoConsultasCache.find(c => c.id_consulta === id);
  if (!consulta) return;
  currentDoctorChatId = id;
  document.getElementById('doctorChatPanel').classList.remove('hidden');
  document.getElementById('doctorChatTitle').textContent = consulta.paciente_nombre;
  document.getElementById('doctorChatSubtitle').textContent = `Consulta #${consulta.id_consulta}`;
  setStatusBadge(document.getElementById('doctorChatStatus'), consulta.estado);
  await loadDoctorMessages(id);
  document.getElementById('doctorChatPanel').scrollIntoView({ behavior:'smooth', block:'start' });
}

document.getElementById('closeDoctorChat')?.addEventListener('click', () => {
  currentDoctorChatId = null;
  document.getElementById('doctorChatPanel').classList.add('hidden');
});

document.getElementById('doctorReplyForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  if (!currentDoctorChatId) return;
  const formData = new FormData(e.currentTarget);
  const r = await fetch(`/devoluciones/${currentDoctorChatId}`, { method:'POST', body: formData });
  const j = await r.json();
  const error = document.getElementById('doctorMessageError');
  if (!r.ok) { showMessage(error, j.mensaje || 'No se pudo enviar la respuesta'); return; }
  e.currentTarget.reset();
  showMessage(error, 'Respuesta enviada.', 'ok');
  await loadDoctorMessages(currentDoctorChatId);
  await loadMedico();
  setTimeout(() => showMessage(error, ''), 1200);
});

async function loadDoctorMessages(id) {
  const box = document.getElementById('doctorChatMessages');
  box.innerHTML = '<div class="chat-loading">Cargando conversación...</div>';
  const r = await fetch(`/consultas/${id}/mensajes`);
  if (!r.ok) { box.innerHTML = '<div class="empty">No se pudo cargar la conversación.</div>'; return; }
  const messages = await r.json();
  box.innerHTML = messages.length ? messages.map(m => renderDoctorMessage(m)).join('') : '<div class="empty">No hay mensajes todavía.</div>';
  box.scrollTop = box.scrollHeight;
}

function renderDoctorMessage(m) {
  const mine = m.tipo === 'medico';
  const image = m.imagen ? `<a class="chat-image-link" href="/consultas/imagen/${encodeURIComponent(m.imagen)}" target="_blank"><img src="/consultas/imagen/${encodeURIComponent(m.imagen)}" alt="Imagen adjunta"></a>` : '';
  return `<div class="message-row ${mine ? 'mine' : 'theirs'}"><div class="message-bubble">
    <span class="message-author">${escapeHtml(m.nombre_usuario)}</span>
    ${m.contenido ? `<p>${escapeHtml(m.contenido)}</p>` : ''}${image}<time>${formatDoctorDate(m.fecha_hora)}</time>
  </div></div>`;
}

function formatDoctorDate(value) {
  const date = new Date(String(value).replace(' ', 'T'));
  if (Number.isNaN(date.getTime())) return escapeHtml(value);
  return date.toLocaleString('es-AR', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' });
}

function setStatusBadge(el, value) {
  el.textContent = value;
  el.className = 'badge badge-' + String(value).toLowerCase().replaceAll(' ', '_');
}

let lastDoctorMessageSignature = '';

async function refreshDoctorView() {
  await loadMedico();
  if (currentDoctorChatId) {
    await loadDoctorMessages(currentDoctorChatId);
    const current = medicoConsultasCache.find(c => c.id_consulta === currentDoctorChatId);
    if (current) setStatusBadge(document.getElementById('doctorChatStatus'), current.estado);
  }
}

setInterval(refreshDoctorView, 5000);

document.getElementById('recetaForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.currentTarget));
  const r = await fetch('/recetas', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
  const j = await r.json();
  showMessage(document.getElementById('recetaMessage'), j.ok ? 'Receta guardada correctamente.' : j.mensaje, j.ok ? 'ok' : 'error');
  if (r.ok) e.currentTarget.reset();
});

loadMedico();
