// Shows backend connectivity in any element with id="backend-status"
// and populates top nav student identity pill across pages.
document.addEventListener("DOMContentLoaded", async () => {
  const esc = (window.appUtils && window.appUtils.escapeHTML) || ((s) => String(s || ""));

  const el = document.getElementById("backend-status");
  if (el) {
    el.textContent = "Checking backend...";
    try {
      const data = await window.api.get("/api/health");
      el.textContent = data.message || "Backend is running";
      el.classList.add("ok");
    } catch (err) {
      el.textContent = "Backend unreachable";
      el.classList.add("bad");
    }
  }

  const navUser = document.getElementById("nav-user-pill");
  const studentId = localStorage.getItem("ai-student-mentor.studentId");
  if (navUser && studentId) {
    try {
      const sData = await window.api.get("/api/students/" + encodeURIComponent(studentId));
      const student = sData.student || sData.data;
      if (student) {
        const initials = (student.name || "")
          .split(" ")
          .map((n) => n[0])
          .slice(0, 2)
          .join("")
          .toUpperCase();
        navUser.innerHTML = `<div class="avatar-initial">${esc(initials)}</div><span>${esc(student.name)}</span>`;
      }
    } catch (e) {
      // ignore silently if backend unavailable
    }
  }
});
