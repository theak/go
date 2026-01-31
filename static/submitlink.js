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
