window.addEventListener("DOMContentLoaded", () => {
  const loadComponent = (url, elementId) => {
    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error(`${url} fetch failed: ${res.status}`);
        return res.text();
      })
      .then(html => {
        document.getElementById(elementId).innerHTML = html;
      })
      .catch(err => console.error(err));
  };

  loadComponent("components/header.html", "header");
  loadComponent("components/footer.html", "footer");
});


