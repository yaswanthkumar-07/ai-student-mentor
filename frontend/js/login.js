// Login and Demo Student Selection Handler
(function () {
  const STORAGE_KEY = "ai-student-mentor.studentId";
  const container = document.getElementById("student-cards-container");
  const loadingEl = document.getElementById("login-loading");
  const errorEl = document.getElementById("login-error");

  const esc = (window.appUtils && window.appUtils.escapeHTML) || ((s) => String(s || ""));

  async function loadDemoStudents() {
    if (!container) return;
    if (loadingEl) loadingEl.style.display = "block";
    if (errorEl) errorEl.style.display = "none";
    container.innerHTML = "";

    try {
      const response = await window.api.get("/api/students");
      const students = response.students || response.data || [];

      if (loadingEl) loadingEl.style.display = "none";

      if (!students.length) {
        container.innerHTML = `
          <div class="empty-state" style="grid-column: 1 / -1;">
            <span class="empty-state-icon">👥</span>
            <h3>No Demo Profiles Found</h3>
            <p>We couldn't locate any demonstration student records in the system.</p>
          </div>
        `;
        return;
      }

      const activeStudentId = localStorage.getItem(STORAGE_KEY);

      students.forEach((student) => {
        const card = document.createElement("div");
        card.className = "card card-clickable" + (student.id === activeStudentId ? " selected" : "");
        card.setAttribute("role", "button");
        card.setAttribute("tabindex", "0");
        card.setAttribute("aria-label", `Select ${student.name || "Student"}`);

        const initials = (student.name || "")
          .split(" ")
          .map((n) => n[0])
          .slice(0, 2)
          .join("");

        const degree = student.education ? `${esc(student.education.field)} (Year ${esc(student.education.year_of_study)})` : "Student";
        const institution = student.education ? esc(student.education.institution) : "";
        const skills = (student.skills || [])
          .slice(0, 4)
          .map((s) => `<span class="chip chip-level-${esc(s.level || 'beginner')}">${esc((s.skill_id || '').replace(/_/g, ' '))}</span>`)
          .join("");

        const goals = (student.career_goals || [])
          .map((g) => `<span class="badge badge-indigo">${esc((g || '').replace(/_/g, ' ').toUpperCase())}</span>`)
          .join(" ");

        card.innerHTML = `
          <div class="card-header">
            <div style="display: flex; align-items: center; gap: 0.85rem;">
              <div class="profile-avatar-lg" style="width: 48px; height: 48px; font-size: 1.2rem;">${esc(initials)}</div>
              <div>
                <h3 style="margin: 0; font-size: 1.15rem;">${esc(student.name)}</h3>
                <small style="color: var(--text-muted);">${esc(student.email || "")}</small>
              </div>
            </div>
            ${student.id === activeStudentId ? '<span class="badge badge-success">Active</span>' : ''}
          </div>
          <div class="card-body">
            <p style="margin: 0.25rem 0 0.75rem; font-size: 0.9rem; color: var(--text-secondary);">
              <strong>🎓 ${degree}</strong><br>
              <span style="color: var(--text-muted); font-size: 0.85rem;">${institution}</span>
            </p>
            <div style="margin-bottom: 0.75rem;">
              <small style="text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600;">Key Skills</small>
              <div class="chips" style="margin-top: 0.35rem;">
                ${skills || '<span style="font-size: 0.85rem; color: var(--text-muted);">No skills recorded</span>'}
              </div>
            </div>
            <div>
              <small style="text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600;">Target Career</small>
              <div style="margin-top: 0.35rem;">
                ${goals || '<span class="badge">Undecided</span>'}
              </div>
            </div>
          </div>
          <div class="card-footer">
            <span style="font-size: 0.85rem; color: var(--text-muted);">📍 ${esc(student.preferred_location || 'Remote')}</span>
            <button class="btn btn-sm btn-primary" type="button">Select Profile &rarr;</button>
          </div>
        `;

        const selectStudent = () => {
          localStorage.setItem(STORAGE_KEY, student.id);
          // Also set target career if present
          if (student.career_goals && student.career_goals.length > 0) {
            localStorage.setItem("ai-student-mentor.targetCareerId", student.career_goals[0]);
          }
          window.location.href = "dashboard.html";
        };

        card.addEventListener("click", selectStudent);
        card.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            selectStudent();
          }
        });

        container.appendChild(card);
      });
    } catch (err) {
      console.error("Failed to load students:", err);
      if (loadingEl) loadingEl.style.display = "none";
      if (errorEl) {
        errorEl.style.display = "block";
        errorEl.innerHTML = `
          <strong>Failed to load demo students:</strong> ${esc(err.message || 'Backend unreachable')}
          <br><button class="btn btn-sm btn-secondary" style="margin-top: 0.5rem;" onclick="window.location.reload()">Retry</button>
        `;
      }
    }
  }

  document.addEventListener("DOMContentLoaded", loadDemoStudents);
})();
