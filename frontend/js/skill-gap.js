/**
 * AI Student Mentor - Module 3: Skill Gap Analysis
 * Compares student skills against target career prerequisites.
 */

(function () {
  "use strict";

  const STORAGE_KEY_STUDENT = "ai-student-mentor.studentId";
  const STORAGE_KEY_TARGET = "ai-student-mentor.targetCareerId";

  const esc = (window.appUtils && window.appUtils.escapeHTML) || ((s) => String(s || ""));
  const formatTitle = (window.appUtils && window.appUtils.formatTitle) || ((s) => String(s || ""));

  let currentAnalysis = null;
  let currentFilter = "all";

  // Elements
  const loadingEl = document.getElementById("gap-loading");
  const errorEl = document.getElementById("gap-error");
  const contentEl = document.getElementById("gap-content");
  const studentEmptyEl = document.getElementById("student-empty-state");
  const careerEmptyEl = document.getElementById("career-empty-state");

  const targetTitleEl = document.getElementById("target-career-title");
  const targetCategoryEl = document.getElementById("target-career-category");
  const targetDescEl = document.getElementById("target-career-description");

  const readinessPercentEl = document.getElementById("readiness-percent");
  const readinessRatioEl = document.getElementById("readiness-ratio");
  const readinessBarEl = document.getElementById("readiness-bar");

  const countAcquiredEl = document.getElementById("count-acquired");
  const countNeedsImpEl = document.getElementById("count-needs-imp");
  const countMissingEl = document.getElementById("count-missing");
  const countRecommendedEl = document.getElementById("count-recommended");

  const pillAllCount = document.getElementById("pill-all-count");
  const pillAcqCount = document.getElementById("pill-acq-count");
  const pillImpCount = document.getElementById("pill-imp-count");
  const pillMisCount = document.getElementById("pill-mis-count");
  const pillRecCount = document.getElementById("pill-rec-count");

  const skillsGrid = document.getElementById("skills-grid");
  const filterPillsContainer = document.getElementById("skill-filter-pills");

  async function init() {
    const studentId = localStorage.getItem(STORAGE_KEY_STUDENT);

    // Read target career from query param or localStorage
    const params = new URLSearchParams(window.location.search);
    const queryCareer = params.get("career");
    if (queryCareer) {
      localStorage.setItem(STORAGE_KEY_TARGET, queryCareer);
    }
    const targetCareerId = localStorage.getItem(STORAGE_KEY_TARGET);

    if (!studentId) {
      if (loadingEl) loadingEl.style.display = "none";
      if (studentEmptyEl) studentEmptyEl.style.display = "block";
      return;
    }

    if (!targetCareerId) {
      if (loadingEl) loadingEl.style.display = "none";
      if (careerEmptyEl) careerEmptyEl.style.display = "block";
      return;
    }

    try {
      if (loadingEl) loadingEl.style.display = "flex";
      const res = await window.api.get(`/api/skill-gap/${encodeURIComponent(studentId)}/${encodeURIComponent(targetCareerId)}`);

      if (loadingEl) loadingEl.style.display = "none";

      if (res.error) {
        throw new Error(res.error);
      }

      // Backend returns { status: "success", data: { student, career, summary, skills: { acquired, needs_improvement, missing, recommended } } }
      const analysisData = res.data || res;
      currentAnalysis = analysisData;
      renderAnalysis(analysisData);
      setupFilters();
    } catch (err) {
      console.error("Skill gap analysis failed:", err);
      if (loadingEl) loadingEl.style.display = "none";
      if (errorEl) {
        errorEl.style.display = "block";
        errorEl.innerHTML = `
          <strong>Analysis Error:</strong> ${esc(err.message || 'Unable to compute skill gaps.')}
          <div style="margin-top: 0.5rem;">
            <a href="career-explorer.html" class="btn btn-sm btn-secondary">Select Another Career</a>
          </div>
        `;
      }
    }
  }

  function renderAnalysis(data) {
    if (contentEl) contentEl.style.display = "block";

    const career = data.career || data.target_career || {};
    const summary = data.summary || {};

    if (targetTitleEl) targetTitleEl.textContent = career.title || "Career Gap Analysis";
    if (targetCategoryEl) targetCategoryEl.textContent = career.category || "General";
    if (targetDescEl) targetDescEl.textContent = career.description || "";

    // Readiness score
    const pct = summary.coverage_percentage !== undefined ? summary.coverage_percentage : 0;
    if (readinessPercentEl) readinessPercentEl.textContent = `${pct}%`;
    if (readinessRatioEl) {
      readinessRatioEl.textContent = `${summary.acquired_count || 0} of ${summary.total_required_skills || 0} required skills acquired`;
    }
    if (readinessBarEl) {
      readinessBarEl.style.width = `${pct}%`;
      if (pct >= 80) readinessBarEl.style.background = "var(--success)";
      else if (pct >= 50) readinessBarEl.style.background = "var(--primary)";
      else readinessBarEl.style.background = "var(--warning)";
    }

    // Counts
    if (countAcquiredEl) countAcquiredEl.textContent = summary.acquired_count || 0;
    if (countNeedsImpEl) countNeedsImpEl.textContent = summary.needs_improvement_count || 0;
    if (countMissingEl) countMissingEl.textContent = summary.missing_count || 0;
    if (countRecommendedEl) countRecommendedEl.textContent = summary.recommended_count || 0;

    // Filter pill numbers
    const totalSkills =
      (summary.acquired_count || 0) +
      (summary.needs_improvement_count || 0) +
      (summary.missing_count || 0) +
      (summary.recommended_count || 0);

    if (pillAllCount) pillAllCount.textContent = totalSkills;
    if (pillAcqCount) pillAcqCount.textContent = summary.acquired_count || 0;
    if (pillImpCount) pillImpCount.textContent = summary.needs_improvement_count || 0;
    if (pillMisCount) pillMisCount.textContent = summary.missing_count || 0;
    if (pillRecCount) pillRecCount.textContent = summary.recommended_count || 0;

    renderSkillCards();
  }

  function setupFilters() {
    if (!filterPillsContainer) return;
    const buttons = filterPillsContainer.querySelectorAll(".filter-btn");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        currentFilter = btn.getAttribute("data-filter") || "all";
        renderSkillCards();
      });
    });
  }

  function renderSkillCards() {
    if (!skillsGrid || !currentAnalysis) return;
    skillsGrid.innerHTML = "";

    // Support both data.skills.* (backend contract) and top-level fallbacks
    const skillsObj = currentAnalysis.skills || currentAnalysis;
    const categories = [
      { key: "acquired", list: skillsObj.acquired || [], label: "Acquired", badgeClass: "chip-level-advanced" },
      { key: "needs_improvement", list: skillsObj.needs_improvement || [], label: "Needs Improvement", badgeClass: "chip-level-intermediate" },
      { key: "missing", list: skillsObj.missing || [], label: "Missing", badgeClass: "chip-level-beginner" },
      { key: "recommended", list: skillsObj.recommended || [], label: "Recommended", badgeClass: "badge-indigo" }
    ];

    let itemsToDisplay = [];
    categories.forEach((cat) => {
      if (currentFilter === "all" || currentFilter === cat.key) {
        cat.list.forEach((item) => {
          itemsToDisplay.push({ ...item, groupKey: cat.key, groupLabel: cat.label, badgeClass: cat.badgeClass });
        });
      }
    });

    if (itemsToDisplay.length === 0) {
      skillsGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <p>No skills found under the "${esc(currentFilter.replace('_', ' '))}" classification.</p>
        </div>
      `;
      return;
    }

    itemsToDisplay.forEach((item) => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.display = "flex";
      card.style.flexDirection = "column";
      card.style.justifyContent = "space-between";

      // Status indicator border
      let borderColor = "var(--border)";
      if (item.groupKey === "acquired") borderColor = "var(--success)";
      else if (item.groupKey === "needs_improvement") borderColor = "var(--warning)";
      else if (item.groupKey === "missing") borderColor = "var(--danger)";
      else if (item.groupKey === "recommended") borderColor = "var(--indigo)";
      card.style.borderLeft = `4px solid ${borderColor}`;

      const resources = item.resources || [];
      const hasResources = resources.length > 0;

      const isRequired = item.type === "required" || item.is_required === true;
      const currentLevel = item.current_level || item.current_proficiency;
      const suggestedAction = item.action || item.suggested_action;

      card.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
            <h4 style="margin: 0; font-size: 1.1rem; color: var(--text-primary);">${esc(item.name || formatTitle(item.skill_id))}</h4>
            <span class="chip ${item.badgeClass}" style="font-size: 0.75rem; text-transform: capitalize;">
              ${esc(item.groupLabel)}
            </span>
          </div>

          <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.75rem; font-size: 0.825rem;">
            <span style="color: var(--text-muted);">Requirement:</span>
            <span class="badge ${isRequired ? 'badge-primary' : ''}">${isRequired ? 'Required Role Skill' : 'Recommended Elective'}</span>
            ${currentLevel ? `<span style="color: var(--text-muted); margin-left: 0.5rem;">Student Level:</span> <strong>${esc(currentLevel)}</strong>` : ''}
          </div>

          <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem; line-height: 1.45;">
            ${esc(item.description || 'Core technical competency relevant to target career.')}
          </p>

          <div style="background: var(--surface); padding: 0.65rem 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border); margin-bottom: 0.75rem;">
            <small style="text-transform: uppercase; font-weight: 700; font-size: 0.7rem; color: var(--text-muted); display: block; margin-bottom: 0.2rem;">Action Recommendation</small>
            <div style="font-size: 0.85rem; color: var(--text-primary); font-weight: 500;">
              ${esc(suggestedAction || 'Review learning resources to maintain or build proficiency.')}
            </div>
          </div>
        </div>

        <div>
          ${hasResources ? `
            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px dashed var(--border);">
              <small style="font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Curated Learning Material:</small>
              <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                ${resources.map(r => `
                  <a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer" style="font-size: 0.825rem; display: flex; align-items: center; justify-content: space-between; text-decoration: none; padding: 0.35rem 0.5rem; background: var(--bg); border-radius: 4px; border: 1px solid var(--border);">
                    <span style="font-weight: 500; color: var(--primary);">📖 ${esc(r.title)}</span>
                    <span class="badge" style="font-size: 0.7rem;">${esc(r.platform || 'Resource')} ↗</span>
                  </a>
                `).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      `;

      skillsGrid.appendChild(card);
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
