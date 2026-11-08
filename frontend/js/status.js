// Shows backend connectivity in any element with id="backend-status".
document.addEventListener("DOMContentLoaded", async () => {
  const el = document.getElementById("backend-status");
  if (!el) return;
  el.textContent = "Checking backend...";
  try {
    const data = await window.api.get("/api/health");
    el.textContent = data.message;
    el.classList.add("ok");
  } catch (err) {
    el.textContent = "Backend unreachable";
    el.classList.add("bad");
  }
});
