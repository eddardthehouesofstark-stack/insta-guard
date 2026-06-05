// ============================================================
// InstaGuard — shared utilities
// All pages import this via <script src="../js/utils.js">
// ============================================================

const API = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : 'https://your-backend-url.onrender.com'; // UPDATE THIS after deploying backend

// ---- Auth helpers ------------------------------------------

function getUser() {
  try { return JSON.parse(localStorage.getItem('ig_user')); }
  catch { return null; }
}

function setUser(u) { localStorage.setItem('ig_user', JSON.stringify(u)); }

function clearUser() { localStorage.removeItem('ig_user'); localStorage.removeItem('ig_token'); }

function getToken() { return localStorage.getItem('ig_token'); }

function requireAuth() {
  const u = getUser();
  if (!u) { window.location.href = '/index.html'; return null; }
  return u;
}

function requireAdmin() {
  const u = requireAuth();
  if (u && u.role !== 'admin') { window.location.href = '/pages/dashboard.html'; return null; }
  return u;
}

// ---- API wrapper -------------------------------------------

async function apiFetch(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API + path, { ...opts, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

// ---- Toast -------------------------------------------------

let toastTimer;
function toast(msg, type = 'info') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = 'toast show ' + type;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = 'toast'; }, 3200);
}

// ---- Score helpers -----------------------------------------

function scoreClass(score) {
  if (score >= 80) return 'danger';
  if (score >= 50) return 'warn';
  return 'safe';
}

function scoreStatus(score) {
  if (score >= 80) return { label: 'Rejected', badge: 'badge-rejected' };
  if (score >= 50) return { label: 'Manual review', badge: 'badge-review' };
  return { label: 'Approved', badge: 'badge-approved' };
}

function renderScoreBar(score) {
  const cls = scoreClass(score);
  return `
    <div class="score-bar-wrap">
      <div class="score-bar-track">
        <div class="score-bar-fill ${cls}" style="width:${score}%"></div>
      </div>
      <div class="score-label">
        <span>Safety score</span><span>${score}/100</span>
      </div>
    </div>`;
}

// ---- Nav ---------------------------------------------------

function renderNav(activePage) {
  const user = getUser();
  if (!user) return;

  const links = [
    { href: 'dashboard.html',      label: 'Dashboard' },
    { href: 'image-checker.html',  label: 'Image checker' },
    { href: 'feed-analyzer.html',  label: 'Feed analyzer' },
  ];

  if (user.role === 'admin') {
    links.push({ href: 'admin.html', label: 'Admin panel' });
  }

  const nav = document.getElementById('nav');
  if (!nav) return;

  nav.innerHTML = `
    <a class="nav-logo" href="dashboard.html">Insta<span>Guard</span></a>
    <ul class="nav-links">
      ${links.map(l => `
        <li><a href="${l.href}" class="${l.href.includes(activePage) ? 'active' : ''}">${l.label}</a></li>
      `).join('')}
    </ul>
    <div class="nav-right">
      <span class="nav-user">${user.email}</span>
      <button class="btn-logout" onclick="logout()">Log out</button>
    </div>
  `;
}

function logout() {
  clearUser();
  window.location.href = '/index.html';
}

// ---- Date format -------------------------------------------

function fmtDate(iso) {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}
