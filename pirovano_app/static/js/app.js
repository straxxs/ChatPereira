async function logout(){try{await fetch('/auth/logout',{method:'POST'});}finally{window.location.href='/';}}
function escapeHtml(value){return String(value ?? '').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function showMessage(el,message,type='error'){if(!el)return;el.textContent=message;el.style.color=type==='ok'?'#198754':'#c92a2a';}
