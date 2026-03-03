document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  let workflow = params.get("wf") || params.get("usage");

  if (workflow) {
    // Dynamically construct the target URL
    const targetUrl = `docs/workflows/${workflow}.html`;

    // Redirect to the dynamically constructed URL
    window.location.href = targetUrl;
  }
});
