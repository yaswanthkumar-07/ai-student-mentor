// Dashboard Controller: Loads and renders the selected student's profile
(function () {
  const STORAGE_KEY = "ai-student-mentor.studentId";
  const TARGET_CAREER_KEY = "ai-student-mentor.targetCareerId";

  const loadingEl = document.getElementById("dashboard-loading");
  const errorEl = document.getElementById("dashboard-error");
  const contentEl = document.getElementById("dashboard-content");
  const emptyEl = document.getElementById("dashboard-empty");

  const esc = (window.appUtils && window.appUtils.escapeHTML) || ((s) => String(s || ""));
  const formatTitle = (window.appUtils && window.appUtils.formatTitle) || ((s) => String(s || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()));

  function getInitials(name) {
    if (!name) return "??";
    return name
      .split(" ")
      .map((part) => part[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  }

  async function loadStudentProfile() {
    const studentId = localStorage.getItem(STORAGE_KEY);

    if (!studentId) {
      if (loadingEl) loadingEl.style.display = "none";
      if (emptyEl) emptyEl.style.display = "block";
      if (contentEl) contentEl.style.display = "none";
      return;
    }

    if (loadingEl) loadingEl.style.display = "block";
    if (errorEl) errorEl.style.display = "none";
    if (emptyEl) emptyEl.style.display = "none";
    if (contentEl) contentEl.style.display = "none";

    try {
      const response = await window.api.get(`/api/students/${encodeURIComponent(studentId)}`);
      const student = response.student || response.data;

      if (!student) {
        throw new Error("Student profile could not be found.");
      }

      renderProfile(student);

      if (loadingEl) loadingEl.style.display = "none";
      if (contentEl) contentEl.style.display = "block";
    } catch (err) {
      console.error("Failed to load student profile:", err);
      if (loadingEl) loadingEl.style.display = "none";
      if (errorEl) {
        errorEl.style.display = "block";
        errorEl.innerHTML = `
          <strong>Profile Error:</strong> ${esc(err.message || "Failed to load student profile.")}
          <div style="margin-top: 0.75rem;">
            <a href="login.html" class="btn btn-sm btn-primary">Choose Another Student</a>
          </div>
        `;
      }
    }
  }

  function renderProfile(student) {
    // Top nav indicator
    const navUserEl = document.getElementById("nav-user-pill");
    if (navUserEl) {
      navUserEl.innerHTML = `
        <div class="avatar-initial">${esc(getInitials(student.name))}</div>
        <span>${esc(student.name)}</span>
      `;
    }

    // Hero Section
    const avatarEl = document.getElementById("student-avatar");
    if (avatarEl) avatarEl.textContent = getInitials(student.name);

    const nameEl = document.getElementById("student-name");
    if (nameEl) nameEl.textContent = student.name;

    const emailEl = document.getElementById("student-email");
    if (emailEl) emailEl.textContent = student.email || "No email listed";

    const locEl = document.getElementById("student-location");
    if (locEl) locEl.textContent = student.preferred_location ? `📍 ${student.preferred_location}` : "📍 Remote";

    const eduSubEl = document.getElementById("student-edu-sub");
    if (eduSubEl && student.education) {
      eduSubEl.textContent = `${student.education.field} • Year ${student.education.year_of_study} at ${student.education.institution}`;
    }

    // Stat counters
    const skillsList = student.skills_detail || student.skills || [];
    const statSkillsCount = document.getElementById("stat-skills-count");
    if (statSkillsCount) statSkillsCount.textContent = skillsList.length;

    const statEduLevel = document.getElementById("stat-edu-level");
    if (statEduLevel && student.education) {
      statEduLevel.textContent = student.education.level || "Degree";
    }

    const statTargetCount = document.getElementById("stat-target-count");
    if (statTargetCount) {
      statTargetCount.textContent = (student.career_goals || []).length;
    }

    // Education details
    const eduContent = document.getElementById("education-details");
    if (eduContent && student.education) {
      eduContent.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
          <div>
            <small style="color: var(--text-muted); text-transform: uppercase; font-weight: 600; font-size: 0.75rem;">Program & Field</small>
            <div style="font-weight: 600; font-size: 1.05rem;">${esc(student.education.field)}</div>
          </div>
          <div>
            <small style="color: var(--text-muted); text-transform: uppercase; font-weight: 600; font-size: 0.75rem;">Institution</small>
            <div style="font-size: 0.95rem;">${esc(student.education.institution)}</div>
          </div>
          <div style="display: flex; gap: 1.5rem;">
            <div>
              <small style="color: var(--text-muted); text-transform: uppercase; font-weight: 600; font-size: 0.75rem;">Level</small>
              <div style="font-weight: 500;">${esc(student.education.level)}</div>
            </div>
            <div>
              <small style="color: var(--text-muted); text-transform: uppercase; font-weight: 600; font-size: 0.75rem;">Year of Study</small>
              <div><span class="badge badge-primary">Year ${esc(student.education.year_of_study)}</span></div>
            </div>
          </div>
        </div>
      `;
    }

    // Interests
    const interestsEl = document.getElementById("interests-chips");
    if (interestsEl) {
      const interests = student.interests || [];
      if (interests.length === 0) {
        interestsEl.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">No interests specified.</span>';
      } else {
        interestsEl.innerHTML = interests
          .map((item) => `<span class="chip" style="font-weight: 500;">💡 ${formatTitle(item)}</span>`)
          .join("");
      }
    }

    // Skills Matrix
    const skillsGrid = document.getElementById("skills-container");
    if (skillsGrid) {
      if (skillsList.length === 0) {
        skillsGrid.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">No skills recorded.</span>';
      } else {
        skillsGrid.innerHTML = skillsList
          .map((s) => {
            const skillName = s.name || formatTitle(s.skill_id);
            const level = s.level || "beginner";
            const category = s.category || "General";
            return `
              <div class="card" style="padding: 1rem; border-radius: var(--radius-md); background: var(--surface-subtle);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                  <strong style="font-size: 0.95rem;">${esc(skillName)}</strong>
                  <span class="chip chip-level-${esc(level)}" style="padding: 0.15rem 0.5rem; font-size: 0.75rem; font-weight: 600; text-transform: capitalize;">${esc(level)}</span>
                </div>
                <small style="color: var(--text-muted); font-size: 0.8rem;">${esc(category)}</small>
                ${s.description ? `<p style="margin: 0.5rem 0 0; font-size: 0.825rem; color: var(--text-secondary); line-height: 1.4;">${esc(s.description)}</p>` : ""}
              </div>
            `;
          })
          .join("");
      }
    }

    // Career Goals
    const goalsEl = document.getElementById("career-goals-container");
    if (goalsEl) {
      const goals = student.career_goals_detail || [];
      const storedTarget = localStorage.getItem(TARGET_CAREER_KEY);

      if (goals.length === 0) {
        goalsEl.innerHTML = `
          <div class="empty-state" style="padding: 1.5rem; margin: 0;">
            <p style="margin: 0 0 1rem;">No career goals configured yet.</p>
            <a href="pages/career-explorer.html" class="btn btn-sm btn-primary">Explore Careers Now</a>
          </div>
        `;
      } else {
        goalsEl.innerHTML = goals
          .map((goal) => {
            const isSelected = storedTarget === goal.id;
            return `
              <div class="card" style="border-left: 4px solid var(--primary); padding: 1.25rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                  <div>
                    <span class="badge badge-primary" style="margin-bottom: 0.25rem;">${esc(goal.category || 'Career Path')}</span>
                    <h3 style="margin: 0.25rem 0; font-size: 1.2rem;">${esc(goal.title)}</h3>
                  </div>
                  ${isSelected ? '<span class="badge badge-success">Target Selected</span>' : ''}
                </div>
                ${goal.description ? `<p style="margin: 0.5rem 0 1rem; font-size: 0.925rem; color: var(--text-secondary);">${esc(goal.description)}</p>` : ""}
                <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;">
                  <a href="pages/career-explorer.html?highlight=${encodeURIComponent(goal.id)}" class="btn btn-sm btn-outline">
                    View in Career Explorer &rarr;
                  </a>
                  <a href="pages/skill-gap.html" class="btn btn-sm btn-secondary">
                    Skill Gap &rarr;
                  </a>
                  <a href="pages/learning-roadmap.html" class="btn btn-sm btn-secondary">
                    Roadmap &rarr;
                  </a>
                </div>
              </div>
            `;
          })
          .join("");
      }
    }
  }

  document.addEventListener("DOMContentLoaded", loadStudentProfile);
})();
