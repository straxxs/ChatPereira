let consultasCache = [];
let currentChatId = null;

async function loadPaciente() {
  const [medRes, perfRes, conRes] = await Promise.all([
    fetch('/medicos'),
    fetch('/pacientes/perfil'),
    fetch('/consultas/mis-consultas')
  ]);

  if (medRes.ok) {
    const meds = await medRes.json();
    document.getElementById('medicoSelect').innerHTML =
      '<option value="">Seleccionar médico</option>' +
      meds.map(m => `<option value="${m.id_medico}">${escapeHtml(m.apellido_usuario)}, ${escapeHtml(m.nombre_usuario)} — ${escapeHtml(m.especialidad)}</option>`).join('');
  }

  if (perfRes.ok) {
    const p = await perfRes.json();
    document.getElementById('perfilBox').innerHTML = `
      <div class="profile-row"><span>Nombre</span><span>${escapeHtml(p.nombre_usuario)} ${escapeHtml(p.apellido_usuario)}</span></div>
      <div class="profile-row"><span>Mail</span><span>${escapeHtml(p.mail)}</span></div>
      <div class="profile-row"><span>DNI</span><span>${escapeHtml(p.DNI)}</span></div>
      <div class="profile-row"><span>Edad</span><span>${escapeHtml(p.edad)}</span></div>
      <div class="profile-row"><span>Teléfono</span><span>${escapeHtml(p.telefono || '—')}</span></div>`;
  }

  if (conRes.ok) {
    consultasCache = await conRes.json();
    renderConsultas();
  }
}

function renderConsultas() {
  const box = document.getElementById('consultasList');
  if (!consultasCache.length) {
    box.innerHTML = '<div class="empty">Todavía no tenés conversaciones. Iniciá tu primera consulta arriba.</div>';
    return;
  }

  box.innerHTML = consultasCache.map(c => `
    <button class="conversation-card" type="button" onclick="openPatientChat(${c.id_consulta})">
      <div class="conversation-avatar">${escapeHtml((c.medico_nombre || 'M').charAt(0).toUpperCase())}</div>
      <div class="conversation-main">
        <div class="conversation-top"><strong>${escapeHtml(c.medico_nombre)}</strong><span>${formatDate(c.fecha_hora)}</span></div>
        <div class="conversation-specialty">${escapeHtml(c.especialidad)}</div>
        <p>${escapeHtml(c.descripcion_sintomas)}</p>
      </div>
      <div class="conversation-side">
        <span class="badge badge-${String(c.estado).toLowerCase().replaceAll(' ', '_')}">${escapeHtml(c.estado)}</span>
        <span class="message-count">${Number(c.cantidad_mensajes || 0)} ${Number(c.cantidad_mensajes || 0) === 1 ? 'mensaje' : 'mensajes'}</span>
      </div>
    </button>`).join('');
}

async function openPatientChat(id) {
  const consulta = consultasCache.find(c => c.id_consulta === id);
  if (!consulta) return;
  currentChatId = id;
  document.getElementById('chatPanel').classList.remove('hidden');
  document.getElementById('chatTitle').textContent = consulta.medico_nombre;
  document.getElementById('chatSubtitle').textContent = consulta.especialidad;
  setStatusBadge(document.getElementById('chatStatus'), consulta.estado);
  await loadMessages('/consultas/' + id + '/mensajes', 'chatMessages');
  document.getElementById('chatPanel').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.getElementById('closeChat')?.addEventListener('click', () => {
  currentChatId = null;
  document.getElementById('chatPanel').classList.add('hidden');
});

document.getElementById('consultaImagen')?.addEventListener('change', event => {
  const file = event.target.files[0];
  const preview = document.getElementById('consultaPreview');
  if (!file) { preview.classList.add('hidden'); preview.innerHTML = ''; return; }
  preview.classList.remove('hidden');
  preview.innerHTML = `<img src="${URL.createObjectURL(file)}" alt="Vista previa de la imagen adjunta"><span>${escapeHtml(file.name)}</span>`;
});

document.getElementById('messageForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  if (!currentChatId) return;
  const formData = new FormData(e.currentTarget);
  const r = await fetch(`/consultas/${currentChatId}/mensajes`, { method: 'POST', body: formData });
  const j = await r.json();
  const error = document.getElementById('messageError');
  if (!r.ok) { showMessage(error, j.mensaje || 'No se pudo enviar el mensaje'); return; }
  e.currentTarget.reset();
  document.getElementById('messageFileName').textContent = '';
  showMessage(error, 'Enviado', 'ok');
  await loadMessages(`/consultas/${currentChatId}/mensajes`, 'chatMessages');
  await loadPaciente();
  const fresh = consultasCache.find(c => c.id_consulta === currentChatId);
  if (fresh) setStatusBadge(document.getElementById('chatStatus'), fresh.estado);
  setTimeout(() => showMessage(error, ''), 1200);
});

document.querySelector('#messageForm input[type="file"]')?.addEventListener('change', e => {
  document.getElementById('messageFileName').textContent = e.target.files[0]?.name || '';
});

document.getElementById('consultaForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const r = await fetch('/consultas', { method: 'POST', body: formData });
  const j = await r.json();
  const msg = document.getElementById('consultaMessage');
  if (!r.ok) { showMessage(msg, j.mensaje || 'No se pudo crear la consulta'); return; }
  showMessage(msg, 'Consulta iniciada correctamente.', 'ok');
  e.currentTarget.reset();
  document.getElementById('consultaPreview').classList.add('hidden');
  setTimeout(loadPaciente, 250);
});

async function loadMessages(url, targetId) {
  const box = document.getElementById(targetId);
  box.innerHTML = '<div class="chat-loading">Cargando conversación...</div>';
  const r = await fetch(url);
  if (!r.ok) { box.innerHTML = '<div class="empty">No se pudo cargar la conversación.</div>'; return; }
  const messages = await r.json();
  box.innerHTML = messages.length ? messages.map(renderMessage).join('') : '<div class="empty">No hay mensajes todavía.</div>';
  box.scrollTop = box.scrollHeight;
}

function renderMessage(m) {
  const mine = m.tipo === 'paciente';
  const image = m.imagen ? `<a class="chat-image-link" href="/consultas/imagen/${encodeURIComponent(m.imagen)}" target="_blank"><img src="/consultas/imagen/${encodeURIComponent(m.imagen)}" alt="Imagen adjunta"></a>` : '';
  return `<div class="message-row ${mine ? 'mine' : 'theirs'}">
    <div class="message-bubble">
      <span class="message-author">${escapeHtml(m.nombre_usuario)}</span>
      ${m.contenido ? `<p>${escapeHtml(m.contenido)}</p>` : ''}
      ${image}
      <time>${formatDate(m.fecha_hora)}</time>
    </div>
  </div>`;
}

function formatDate(value) {
  const date = new Date(String(value).replace(' ', 'T'));
  if (Number.isNaN(date.getTime())) return escapeHtml(value);
  return date.toLocaleString('es-AR', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' });
}

function setStatusBadge(el, value) {
  el.textContent = value;
  el.className = 'badge badge-' + String(value).toLowerCase().replaceAll(' ', '_');
}

loadPaciente();
