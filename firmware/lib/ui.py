PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Knowledge Assistant</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;500&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdib3g9IjAgMCAzMiAzMiI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNCIgZmlsbD0iIzBhMGEwYSIvPjxwb2x5Z29uIHBvaW50cz0iMTIsOCAyNCwxNiAxMiwyNCIgZmlsbD0iIzVjNjE0ZCIvPjwvc3ZnPg==">
<script>
tailwind.config = { darkMode: "class", theme: { extend: {
  colors: {
    tertiary: "#0b0a09", background: "#f9f9f8",
    "secondary-container": "#e0e5cc", "surface-container": "#eeeeed",
    secondary: "#5c614d", "surface-container-lowest": "#ffffff",
    outline: "#747878", "on-primary-container": "#898888",
    "surface-dim": "#dadad9", error: "#ba1a1a",
    "on-surface": "#1a1c1c", primary: "#0a0a0a",
    "surface-bright": "#f9f9f8", "tertiary-fixed-dim": "#c9c6c4",
    "surface-container-highest": "#e2e2e2",
    "secondary-fixed-dim": "#c4c9b1",
    "on-tertiary-fixed-variant": "#484645",
    "on-secondary-fixed": "#191d0e", "on-surface-variant": "#444748",
    surface: "#f9f9f8", "primary-container": "#212121",
    "tertiary-fixed": "#e6e2e0", "secondary-fixed": "#e0e5cc",
    "on-primary": "#ffffff", "on-primary-fixed-variant": "#474746",
    "on-background": "#1a1c1c", "on-primary-fixed": "#1b1c1c",
    "surface-container-high": "#e8e8e7",
    "on-tertiary-fixed": "#1c1b1a", "error-container": "#ffdad6",
    "primary-fixed-dim": "#c8c6c5",
    "surface-container-low": "#f3f4f3",
    "on-secondary-container": "#626753", "surface-variant": "#e2e2e2",
    "tertiary-container": "#222120", "inverse-primary": "#c8c6c5",
    "on-tertiary-container": "#8b8886", "primary-fixed": "#e5e2e1",
    "on-secondary": "#ffffff", "inverse-on-surface": "#f1f1f0",
    "on-secondary-fixed-variant": "#444937", "outline-variant": "#c4c7c7",
    "inverse-surface": "#2f3130"
  },
  fontFamily: {
    sans: ["Inter", "system-ui", "sans-serif"],
    serif: ["Source Serif 4", "Georgia", "serif"],
  }
}}};
</script>
<style>
  .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; vertical-align: middle; }
  .atmospheric-shadow { box-shadow: 0px 4px 20px rgba(0,0,0,0.04); }
  .sidebar-active { position: relative; }
  .sidebar-active::before { content: ''; position: absolute; left: 0; top: 25%; bottom: 25%; width: 4px; background-color: #5c614d; border-radius: 0 4px 4px 0; }
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e2e2; border-radius: 10px; }
  .fade-in { animation: fadeIn .25s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  .typing-dot { width: 6px; height: 6px; border-radius: 50%; background: #747878; display: inline-block; animation: dotPulse 1.4s infinite; }
  .typing-dot:nth-child(2) { animation-delay: .2s; }
  .typing-dot:nth-child(3) { animation-delay: .4s; }
  @keyframes dotPulse { 0%,80%,100% { opacity: .3; } 40% { opacity: 1; } }
</style>
</head>
<body class="bg-background text-on-surface font-sans">

<!-- Sidebar -->
<aside class="fixed left-0 top-0 h-full w-[280px] bg-surface-container-low flex flex-col border-r border-outline-variant/30 z-30 transition-transform duration-300 md:translate-x-0 -translate-x-full" id="sideNav">
  <div class="p-6 flex flex-col h-full">
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 rounded-lg bg-secondary-fixed flex items-center justify-center text-on-secondary-fixed font-bold text-sm">KC</div>
        <div class="overflow-hidden">
          <h1 class="font-semibold text-lg text-primary truncate">esp32 · chat</h1>
          <p class="text-xs text-on-surface-variant opacity-70" id="modelDisplaySide">—</p>
        </div>
      </div>
      <button class="w-full mt-6 py-2.5 px-4 bg-primary text-on-primary rounded-lg font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2" onclick="newChat()">
        <span class="material-symbols-outlined text-[20px]">add</span> New Chat
      </button>
    </div>
    <nav class="flex-1 space-y-1 custom-scrollbar overflow-y-auto">
      <div class="text-xs font-semibold text-on-surface-variant/50 px-4 py-2 uppercase tracking-wider">Skills</div>
      <div id="skillsListSide"></div>
    </nav>
    <div class="mt-auto pt-4 border-t border-outline-variant/20 flex items-center gap-3">
      <div class="w-2 h-2 rounded-full bg-secondary" id="statusDotSide"></div>
      <div class="flex-1 overflow-hidden">
        <p class="text-sm font-medium truncate" id="ipDisplaySide">—</p>
      </div>
    </div>
  </div>
</aside>

<!-- Main -->
<main class="ml-0 md:ml-[280px] flex flex-col min-h-screen">
  <!-- Top Bar -->
  <header class="flex justify-between items-center h-16 px-6 w-full sticky top-0 bg-surface/80 backdrop-blur-md z-20 border-b border-outline-variant/10">
    <div class="flex items-center gap-4">
      <button class="md:hidden text-on-surface" onclick="document.getElementById('sideNav').classList.toggle('-translate-x-full')">
        <span class="material-symbols-outlined">menu</span>
      </button>
      <span class="font-semibold text-lg text-primary">Knowledge Assistant</span>
      <div class="hidden lg:flex items-center gap-2 px-3 py-1 bg-surface-container-low rounded-full">
        <span class="w-2 h-2 rounded-full bg-secondary" id="statusDot"></span>
        <span class="text-xs text-on-secondary-container" id="statusText">Ready</span>
      </div>
    </div>
    <div class="flex items-center gap-3 text-xs text-on-surface-variant">
      <span id="skillDisplay" class="px-2 py-1 bg-secondary-fixed rounded-full font-medium">General</span>
      <span id="ipDisplay" class="opacity-50">—</span>
    </div>
  </header>

  <!-- Messages -->
  <section class="flex-1 overflow-y-auto px-6 py-8 custom-scrollbar">
    <div class="max-w-[800px] mx-auto space-y-8 pb-40" id="messages"></div>
  </section>

  <!-- Floating Input -->
  <footer class="fixed bottom-0 left-0 md:left-[280px] right-0 p-6 flex justify-center z-10 pointer-events-none">
    <div class="w-full max-w-[800px] bg-surface-container-lowest border border-outline-variant/40 rounded-2xl atmospheric-shadow p-2 flex flex-col pointer-events-auto transition-all duration-300 focus-within:ring-2 focus-within:ring-secondary/20">
      <div class="flex items-end gap-2 px-2 py-1">
        <textarea id="input" class="flex-1 py-3 px-2 bg-transparent border-none focus:ring-0 text-on-surface placeholder:text-on-surface-variant/40 font-sans resize-none min-h-[48px] max-h-[200px] outline-none" rows="1" placeholder="Ask anything or share a thought..." oninput="this.style.height='';this.style.height=this.scrollHeight+'px'" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
        <div class="flex items-center gap-2">
          <button class="w-10 h-10 bg-primary text-on-primary rounded-xl flex items-center justify-center hover:opacity-90 transition-all active:scale-95 disabled:opacity-40" id="btnSend" onclick="send()">
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL'1">send</span>
          </button>
        </div>
      </div>
      <div class="flex items-center gap-3 px-3 py-2 mt-1 border-t border-outline-variant/10">
        <div class="flex items-center gap-1.5 px-2 py-0.5 bg-secondary-fixed rounded-full">
          <span class="material-symbols-outlined text-[14px] text-on-secondary-fixed">model_training</span>
          <span class="text-xs text-on-secondary-fixed font-semibold uppercase tracking-tighter" id="skillBadge">General</span>
        </div>
        <span class="text-xs text-on-surface-variant/40 italic">&crarr; Enter to send</span>
      </div>
    </div>
  </footer>
</main>

<script>
const PROXY = '__PROXY_URL__';
let skills = {};
let activeSkill = 'general';
let loading = false;

function fetchJSON(url, body) {
  const opts = { headers: { 'Content-Type': 'application/json' } };
  if (body) { opts.method = 'POST'; opts.body = JSON.stringify(body); }
  return fetch(url, opts).then(r => r.json());
}

async function loadConfig() {
  const d = await fetchJSON('/api/info');
  document.getElementById('modelDisplaySide').textContent = d.model || '—';
  document.getElementById('ipDisplay').textContent = d.ip || '';
  document.getElementById('ipDisplaySide').textContent = d.ip || '';
}

async function loadSkills() {
  const d = await fetchJSON('/api/skills');
  d.skills.forEach(s => { skills[s.id] = s; });
  const el = document.getElementById('skillsListSide');
  el.innerHTML = d.skills.map(s => `
    <div class="flex items-center gap-3 px-4 py-2.5 rounded-lg cursor-pointer transition-colors hover:bg-surface-container-high mb-0.5 ${s.id === activeSkill ? 'bg-secondary-fixed/40 font-semibold' : 'text-on-surface-variant'}" data-id="${s.id}" onclick="activateSkill('${s.id}')">
      <div class="w-7 h-7 rounded-md bg-surface-container flex items-center justify-center text-xs flex-shrink-0 ${s.id === activeSkill ? 'bg-secondary-fixed' : ''}">${s.icon || '?'}</div>
      <div class="flex-1 min-w-0">
        <div class="text-sm truncate">${s.name}</div>
      </div>
      ${s.id === activeSkill ? '<span class="material-symbols-outlined text-[16px] text-secondary">check</span>' : ''}
    </div>
  `).join('');
}

async function activateSkill(id) {
  activeSkill = id;
  await fetchJSON('/api/skills/activate', { skill: id });
  document.getElementById('skillDisplay').textContent = skills[id] ? skills[id].name : id;
  document.getElementById('skillBadge').textContent = skills[id] ? skills[id].name : id;
  loadSkills();
  addSystemMsg('Switched to ' + (skills[id] ? skills[id].name : id));
  if (window.innerWidth < 768) document.getElementById('sideNav').classList.add('-translate-x-full');
}

function newChat() {
  document.getElementById('messages').innerHTML = '';
  addSystemMsg('New session started.');
}

function addMsg(role, content) {
  const el = document.getElementById('messages');
  const d = document.createElement('div');
  d.className = 'fade-in';
  if (role === 'user') {
    d.className += ' flex flex-col items-end gap-2';
    d.innerHTML = `<div class="bg-surface-container-low border border-outline-variant/30 rounded-xl px-5 py-3.5 atmospheric-shadow max-w-[85%]"><p class="text-sm text-on-surface">${escapeHtml(content)}</p></div>`;
  } else if (role === 'ai') {
    d.className += ' flex flex-col gap-2';
    d.innerHTML = `<div class="flex items-center gap-2 text-xs text-on-surface-variant/60 font-semibold uppercase tracking-widest mb-1">Assistant</div><div class="font-serif text-[18px] leading-[1.6] text-on-surface max-w-[90%]"><p>${escapeHtml(content)}</p></div>`;
  } else if (role === 'error') {
    d.className += ' flex flex-col items-end gap-2';
    d.innerHTML = `<div class="bg-error-container border border-error/30 rounded-xl px-5 py-3.5 max-w-[85%]"><p class="text-sm text-on-error-container">${escapeHtml(content)}</p></div>`;
  } else {
    d.className += ' flex justify-center';
    d.innerHTML = `<div class="text-xs text-on-surface-variant/40 italic py-2">${escapeHtml(content)}</div>`;
  }
  el.appendChild(d);
  el.scrollTop = el.scrollHeight;
  return d;
}

function addSystemMsg(text) {
  const m = document.getElementById('messages');
  const d = document.createElement('div');
  d.className = 'fade-in flex justify-center';
  d.innerHTML = `<div class="text-xs text-on-surface-variant/40 italic py-2">${escapeHtml(text)}</div>`;
  m.appendChild(d);
  m.scrollTop = m.scrollHeight;
}

function showTyping() {
  const el = document.getElementById('messages');
  const d = document.createElement('div');
  d.className = 'fade-in flex flex-col gap-2';
  d.id = 'typingIndicator';
  d.innerHTML = `<div class="flex items-center gap-2 text-xs text-on-surface-variant/60 font-semibold uppercase tracking-widest mb-1">Assistant</div><div class="font-serif text-[18px] leading-[1.6] text-on-surface max-w-[90%]"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>`;
  el.appendChild(d);
  el.scrollTop = el.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById('typingIndicator');
  if (t) t.remove();
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function setBusy(b) {
  loading = b;
  document.getElementById('btnSend').disabled = b;
  document.getElementById('input').disabled = b;
  document.getElementById('statusDot').className = 'w-2 h-2 rounded-full ' + (b ? 'bg-yellow-500 animate-pulse' : 'bg-secondary');
  document.getElementById('statusText').textContent = b ? 'Thinking...' : 'Ready';
}

async function send() {
  if (loading) return;
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';

  addMsg('user', text);
  showTyping();
  setBusy(true);

  try {
    const sp = (skills[activeSkill] && skills[activeSkill].prompt) || 'You are a helpful assistant.';
    const res = await fetchJSON(PROXY, { message: text, system_prompt: sp });
    removeTyping();
    if (res.error) {
      addMsg('error', res.error);
    } else {
      addMsg('ai', res.response);
      fetch('/api/display', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user: text, ai: res.response})
      }).catch(() => {});
    }
  } catch (e) {
    removeTyping();
    addMsg('error', 'Connection failed: ' + e.message);
  }
  setBusy(false);
}

loadConfig();
loadSkills();
addSystemMsg('System ready. Select a skill and start chatting.');
</script>
</body>
</html>"""
