if (new URLSearchParams(location.search).has("deleted")) history.replaceState({}, "", "/");

function expand(td) {
  td.innerHTML = td.title;
}

function rename(link_id, link_name) {
  const newName = prompt("Name for " + link_name);
  if (newName !== null) {
    const formData = new FormData();
    formData.append("id", link_id);
    formData.append("newName", newName);
    formData.append("action", "rename");
    fetch("/update_link", { method: "POST", body: formData })
      .then(() => window.location.href = "/");
  }
}

function editUrl(link_id, current_url) {
  const newUrl = prompt("New URL:", current_url);
  if (newUrl !== null && newUrl !== current_url) {
    const formData = new FormData();
    formData.append("id", link_id);
    formData.append("newUrl", newUrl);
    formData.append("action", "edit_url");
    fetch("/update_link", { method: "POST", body: formData })
      .then(() => window.location.href = "/");
  }
}

function banner(type, msg) {
  document.getElementById("banner").innerHTML =
    `<div class="alert alert-${type}">${msg}</div>`;
}

let lastDeleted = null;

function deleteLink(btn, link_id, link_name) {
  const icon = btn.innerHTML;
  btn.textContent = "…";
  btn.disabled = true;
  const formData = new FormData();
  formData.append("id", link_id);
  formData.append("action", "delete");
  fetch("/update_link", { method: "POST", body: formData })
    .then((r) => {
      if (!r.ok) throw new Error();
      return r.json();
    })
    .then((link) => {
      lastDeleted = link;
      document.getElementById("banner").innerHTML =
        `<div class="alert alert-success">${link_name} deleted ` +
        `<a href="#" class="link-secondary float-end" onclick="undoDelete(event)">Undo</a></div>`;
      btn.closest("tr").remove();
      document.querySelector(`#results a[data-go="${CSS.escape(link.name)}"]`)?.remove();
      renderRecent();
      filter();
    })
    .catch(() => {
      banner("danger", "Failed to delete " + link_name);
      btn.innerHTML = icon;
      btn.disabled = false;
    });
}

function undoDelete(e) {
  if (e) e.preventDefault();
  if (!lastDeleted) return;
  const fd = new FormData();
  fd.append("action", "restore");
  fd.append("name", lastDeleted.name);
  fd.append("url", lastDeleted.url);
  if (lastDeleted.description != null) fd.append("description", lastDeleted.description);
  fd.append("metadata", lastDeleted.metadata ?? "{}");
  fetch("/update_link", { method: "POST", body: fd })
    .then((r) => {
      if (!r.ok) throw new Error();
      window.location.href = "/";
    })
    .catch(() => banner("danger", "Failed to restore " + lastDeleted.name));
}

/* SEARCH */

const q = document.getElementById("q");
const results = document.getElementById("results");
const url = document.getElementById("url");

function filter() {
  const s = q.value.trim().toLowerCase();
  // Name matches first (exact, then prefix), then description, then URL.
  const rank = (a) => {
    const name = a.dataset.go.toLowerCase();
    return name === s ? 0 : name.startsWith(s) ? 1 : name.includes(s) ? 2
      : a.dataset.desc.toLowerCase().includes(s) ? 3 : 4;
  };
  const items = [...results.children];
  const hits = !s ? [] : items.filter((a) => a.dataset.search.includes(s))
    .sort((a, b) => rank(a) - rank(b)).slice(0, 8);
  for (const a of items) a.hidden = !hits.includes(a);
  results.prepend(...hits);
  const exact = hits.length > 0 && rank(hits[0]) === 0;
  document.getElementById("clear").hidden = !s;
  document.getElementById("create").hidden = !s || exact;
  document.getElementById("create-name").value = q.value.trim();
  document.getElementById("create-label").textContent = q.value.trim();
}

q.addEventListener("input", filter);
q.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  const first = document.querySelector("#results a:not([hidden])");
  if (first) {
    track(first.dataset.go);
    location.href = first.href;
  } else {
    url.focus();
  }
});
document.getElementById("clear").addEventListener("click", () => {
  q.value = "";
  filter();
  q.focus();
});
// A blank URL creates a note, so the button says which one you'll get.
url.addEventListener("input", () => {
  document.getElementById("create-btn").textContent = url.value ? "Create link" : "Create note";
});
if (matchMedia("(pointer: fine)").matches) q.focus();
filter();

/* RECENT LINKS (stored per-device in localStorage as [{name, t}]) */

const recentEl = document.getElementById("recent");

function loadRecent() {
  try { return JSON.parse(localStorage.getItem("recent")).filter((r) => r.name); } catch { return []; }
}

function saveRecent(list) {
  try { localStorage.setItem("recent", JSON.stringify(list.slice(0, 5))); } catch {}
  renderRecent();
}

function track(name) {
  saveRecent([{ name, t: Date.now() }, ...loadRecent().filter((r) => r.name !== name)]);
}

function ago(t) {
  const m = Math.round((Date.now() - t) / 60000);
  return m < 1 ? "just now" : m < 60 ? `${m}m ago` : m < 1440 ? `${Math.round(m / 60)}h ago` : `${Math.round(m / 1440)}d ago`;
}

function renderRecent() {
  const tiles = loadRecent().map(({ name, t }) => {
    const link = document.querySelector(`#results a[data-go="${CSS.escape(name)}"]`);
    if (!link) return null;
    const a = document.createElement("a");
    a.href = link.href;
    a.target = "_blank";
    a.dataset.go = name;
    a.innerHTML = `<span class="ago"></span><span class="arrow">↗</span><span class="go"><span class="muted"></span><b></b></span>`;
    a.querySelector(".ago").textContent = ago(t);
    a.querySelector(".muted").textContent = link.querySelector(".name").textContent.slice(0, -name.length);
    a.querySelector("b").textContent = name;
    return a;
  }).filter(Boolean);
  recentEl.replaceChildren(...tiles);
  document.getElementById("recent-section").hidden = !tiles.length;
}

// Long-press a recent link to remove it.
let pressTimer, longPressed;
recentEl.addEventListener("pointerdown", (e) => {
  const a = e.target.closest("a");
  if (!a) return;
  longPressed = false;
  pressTimer = setTimeout(() => {
    longPressed = true;
    saveRecent(loadRecent().filter((r) => r.name !== a.dataset.go));
  }, 500);
});
for (const ev of ["pointerup", "pointerleave", "pointercancel"]) {
  recentEl.addEventListener(ev, () => clearTimeout(pressTimer));
}
recentEl.addEventListener("contextmenu", (e) => e.preventDefault());
recentEl.addEventListener("click", (e) => {
  if (longPressed) { e.preventDefault(); e.stopPropagation(); }
});

document.addEventListener("click", (e) => {
  const a = e.target.closest("a[data-go]");
  if (a) track(a.dataset.go);
});
renderRecent();
