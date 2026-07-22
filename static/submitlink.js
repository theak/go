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
