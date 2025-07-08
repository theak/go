function expand(td) {
  td.innerHTML = td.title;
}
function rename(link_id, link_name) {
  const newName =  prompt("Name for " + link_name);
  if (newName !== null) {
    const formData = new FormData();
    formData.append("id", link_id);
    formData.append("newName", newName);
    formData.append("action", "rename");
    try {
      const response = fetch("/update_link", {
        method: "POST",
        body: formData,
      }).then(() => window.location.href = "/");
    } catch (e) {
      console.error(e);
    }
  }
}
