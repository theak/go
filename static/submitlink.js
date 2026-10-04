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
      btn.textContent = "🗑️";
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
const recentEl = document.getElementById("recent");
const results = document.getElementById("results");

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
  recentEl.hidden = !!s;
  document.getElementById("create").hidden = !s || exact;
  document.getElementById("create-name").value = q.value.trim();
  document.getElementById("create-label").textContent = q.value.trim();
  document.getElementById("create-note").href = "/note/" + encodeURIComponent(q.value.trim());
}

q.addEventListener("input", filter);
q.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  const first = document.querySelector("#results a:not([hidden])");
  if (first) {
    track(first.dataset.go);
    location.href = first.href;
  } else {
    document.getElementById("url").focus();
  }
});
if (matchMedia("(pointer: fine)").matches) q.focus();
filter();

/* RECENT LINKS (stored per-device in localStorage) */

function loadRecent() {
  try { return JSON.parse(localStorage.getItem("recent")) || []; } catch { return []; }
}

function saveRecent(names) {
  try { localStorage.setItem("recent", JSON.stringify(names.slice(0, 5))); } catch {}
  renderRecent();
}

function track(name) {
  saveRecent([name, ...loadRecent().filter((n) => n !== name)]);
}

function renderRecent() {
  recentEl.replaceChildren(...loadRecent().map((name) => {
    const link = document.querySelector(`#results a[data-go="${CSS.escape(name)}"]`);
    if (!link) return "";
    const a = document.createElement("a");
    a.href = link.href;
    a.target = "_blank";
    a.dataset.go = name;
    a.innerHTML = `<span></span><small></small>`;
    // Use the leading emoji of the description as the icon.
    a.firstChild.textContent = link.dataset.desc.match(/^\P{L}*/u)[0].trim() || "🔗";
    a.lastChild.textContent = link.querySelector("b").textContent;
    return a;
  }));
}

// Long-press a recent link to remove it.
let pressTimer, longPressed;
recentEl.addEventListener("pointerdown", (e) => {
  const a = e.target.closest("a");
  if (!a) return;
  longPressed = false;
  pressTimer = setTimeout(() => {
    longPressed = true;
    saveRecent(loadRecent().filter((n) => n !== a.dataset.go));
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
