document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  let workflow = params.get("wf") ?? params.get("usage");
  if (workflow) {
    // Allow only expected slug characters.
    if (!/^[A-Za-z0-9\/_-]+$/.test(workflow)) {
      console.error(
        `Invalid workflow specification (allowed is ^[A-Za-z0-9\/_-]+$): ${workflow}`,
      );
      return;
    }
    // Dynamically construct the target URL
    const targetUrl = `docs/workflows/${workflow}.html`;

    // Redirect to the dynamically constructed URL
    window.location.href = targetUrl;
  }
});
