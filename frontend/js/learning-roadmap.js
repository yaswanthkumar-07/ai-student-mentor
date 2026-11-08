/**
 * AI Student Mentor - Module 4: Personalized Learning Roadmap
 * Renders stage-by-stage learning curriculum with interactive localStorage progress tracking.
 */

(function () {
  "use strict";

  const STORAGE_KEY_STUDENT = "ai-student-mentor.studentId";
  const STORAGE_KEY_TARGET = "ai-student-mentor.targetCareerId";
  const STORAGE_KEY_PROGRESS = "ai-student-mentor.roadmapProgress";

  const esc = (window.appUtils && window.appUtils.escapeHTML) || ((s) => String(s || ""));
  const formatTitle = (window.appUtils && window.appUtils.formatTitle) || ((s) => String(s || ""));

  let currentRoadmap = null;
  let activeStudentId = null;
  let activeCareerId = null;
  let progressState = {}; // { [studentId]: { [careerId]: { [taskId]: status } } }

  // Elements
  const loadingEl = document.getElementById("roadmap-loading");
  const errorEl = document.getElementById("roadmap-error");
  const contentEl = document.getElementById("roadmap-content");
  const studentEmptyEl = document.getElementById("student-empty-state");
  const careerEmptyEl = document.getElementById("career-empty-state");

  const targetTitleEl = document.getElementById("target-career-title");
  const targetCategoryEl = document.getElementById("target-career-category");
  const targetDescEl = document.getElementById("target-career-description");

  const overallPercentEl = document.getElementById("overall-percent");
  const overallTaskCounterEl = document.getElementById("overall-task-counter");
  const overallBarEl = document.getElementById("overall-bar");

  const stagesContainer = document.getElementById("stages-container");
  const resetBtn = document.getElementById("reset-progress-btn");
  const toastEl = document.getElementById("roadmap-toast");

  async function init() {
    activeStudentId = localStorage.getItem(STORAGE_KEY_STUDENT);

    const params = new URLSearchParams(window.location.search);
    const queryCareer = params.get("career");
    if (queryCareer) {
      localStorage.setItem(STORAGE_KEY_TARGET, queryCareer);
    }
    activeCareerId = localStorage.getItem(STORAGE_KEY_TARGET);

    if (!activeStudentId) {
      if (loadingEl) loadingEl.style.display = "none";
      if (studentEmptyEl) studentEmptyEl.style.display = "block";
      return;
    }

    if (!activeCareerId) {
      if (loadingEl) loadingEl.style.display = "none";
      if (careerEmptyEl) careerEmptyEl.style.display = "block";
      return;
    }

    loadProgressFromStorage();

    try {
      if (loadingEl) loadingEl.style.display = "flex";
      const res = await window.api.get(`/api/roadmap/${encodeURIComponent(activeStudentId)}/${encodeURIComponent(activeCareerId)}`);

      if (loadingEl) loadingEl.style.display = "none";

      if (res.error) {
        throw new Error(res.error);
      }

      // Backend returns { status: "success", data: { student, career, title, total_stages, total_tasks, stages: [...] } }
      const roadmapData = res.data || res;
      currentRoadmap = roadmapData;
      renderRoadmap(roadmapData);
      updateOverallProgress();
    } catch (err) {
      console.error("Roadmap loading failed:", err);
      if (loadingEl) loadingEl.style.display = "none";
      if (errorEl) {
        errorEl.style.display = "block";
        errorEl.innerHTML = `
          <strong>Roadmap Error:</strong> ${esc(err.message || 'Unable to build learning roadmap.')}
          <div style="margin-top: 0.5rem;">
            <a href="career-explorer.html" class="btn btn-sm btn-secondary">Select Another Career</a>
          </div>
        `;
      }
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", handleResetProgress);
    }
  }

  function loadProgressFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_PROGRESS);
      progressState = raw ? JSON.parse(raw) : {};
    } catch (e) {
      console.warn("Could not parse roadmapProgress from localStorage:", e);
      progressState = {};
    }
  }

  function saveProgressToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY_PROGRESS, JSON.stringify(progressState));
    } catch (e) {
      console.warn("Could not save roadmapProgress to localStorage:", e);
    }
  }

  function getTaskStatus(taskId) {
    if (!progressState[activeStudentId]) return "not_started";
    if (!progressState[activeStudentId][activeCareerId]) return "not_started";
    return progressState[activeStudentId][activeCareerId][taskId] || "not_started";
  }

  function setTaskStatus(taskId, status) {
    if (!progressState[activeStudentId]) progressState[activeStudentId] = {};
    if (!progressState[activeStudentId][activeCareerId]) progressState[activeStudentId][activeCareerId] = {};
    progressState[activeStudentId][activeCareerId][taskId] = status;
    saveProgressToStorage();
    updateOverallProgress();
    showToast(`Task status updated: ${status.replace('_', ' ')}`);
  }

  function showToast(message) {
    if (!toastEl) return;
    toastEl.querySelector("span").textContent = message;
    toastEl.classList.add("show");
    setTimeout(() => {
      toastEl.classList.remove("show");
    }, 2500);
  }

  function handleResetProgress() {
    const confirmed = window.confirm("Are you sure you want to reset all task progress for this career? This cannot be undone.");
    if (!confirmed) return;

    if (progressState[activeStudentId] && progressState[activeStudentId][activeCareerId]) {
      delete progressState[activeStudentId][activeCareerId];
      saveProgressToStorage();
    }

    // Refresh UI
    renderRoadmap(currentRoadmap);
    updateOverallProgress();
    showToast("Progress reset successfully.");
  }

  function renderRoadmap(data) {
    if (contentEl) contentEl.style.display = "block";

    const career = data.career || {};
    // Extract stages from data.stages (backend contract) or fallback to data.roadmap.stages
    const stages = data.stages || (data.roadmap && data.roadmap.stages) || [];
    const roadmapTitle = data.title || (data.roadmap && data.roadmap.title) || career.title || "Personalized Roadmap";

    if (targetTitleEl) targetTitleEl.textContent = roadmapTitle;
    if (targetCategoryEl) targetCategoryEl.textContent = career.category || "Curriculum";
    if (targetDescEl) targetDescEl.textContent = career.description || "Step-by-step competency path for your target career.";

    if (!stagesContainer) return;
    stagesContainer.innerHTML = "";

    if (stages.length === 0) {
      stagesContainer.innerHTML = `
        <div class="empty-state">
          <p>No learning stages available for this career path.</p>
        </div>
      `;
      return;
    }

    stages.forEach((stage, stageIndex) => {
      const stageCard = document.createElement("div");
      stageCard.className = "card";
      stageCard.style.padding = "1.5rem";

      // Each stage contains skills (backend contract) or tasks
      const tasks = stage.skills || stage.tasks || [];

      stageCard.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1.25rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
              <span class="badge badge-primary" style="font-weight: 700;">Stage ${stage.order || stage.stage_number || (stageIndex + 1)}</span>
              <h3 style="margin: 0; font-size: 1.25rem;">${esc(stage.title)}</h3>
            </div>
            ${stage.description ? `<p style="margin: 0; font-size: 0.9rem; color: var(--text-secondary);">${esc(stage.description)}</p>` : ''}
            ${stage.estimated_weeks ? `<small style="color: var(--text-muted); font-size: 0.8rem;">Est. Duration: ~${stage.estimated_weeks} weeks</small>` : ''}
          </div>
          <span class="badge" id="stage-badge-${stageIndex}">${tasks.length} Modules</span>
        </div>

        <div class="stage-tasks-list" style="display: flex; flex-direction: column; gap: 1rem;"></div>
      `;

      const tasksListEl = stageCard.querySelector(".stage-tasks-list");

      tasks.forEach((task, taskIndex) => {
        // Use stable skill_id as the taskId, fallback to task_id
        const taskId = task.skill_id || task.task_id || `stage_${stage.order || stageIndex + 1}_task_${taskIndex + 1}`;
        const currentStatus = getTaskStatus(taskId);

        const taskRow = document.createElement("div");
        taskRow.className = "card";
        taskRow.style.margin = "0";
        taskRow.style.background = "var(--surface)";
        taskRow.style.borderColor = "var(--border)";
        taskRow.id = `task-card-${taskId}`;

        // Border highlighting based on status
        applyTaskCardStyle(taskRow, currentStatus);

        const resources = task.resources || [];
        const hasResources = resources.length > 0;

        const isAcquired = task.status === "acquired" || task.is_already_acquired;
        const isNeedsImprovement = task.status === "needs_improvement";
        const isMissing = task.status === "missing" || task.is_missing;

        taskRow.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 260px;">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; flex-wrap: wrap;">
                <h4 style="margin: 0; font-size: 1.05rem; color: var(--text-primary);">${esc(task.name || task.title || formatTitle(taskId))}</h4>
                ${isAcquired ? `<span class="chip chip-level-advanced" style="font-size: 0.7rem;">✓ In Student Profile</span>` : ''}
                ${isNeedsImprovement ? `<span class="chip chip-level-intermediate" style="font-size: 0.7rem;">Level Up</span>` : ''}
                ${isMissing ? `<span class="chip chip-level-beginner" style="font-size: 0.7rem;">Focus Area</span>` : ''}
                ${task.badge_label && !isAcquired && !isNeedsImprovement && !isMissing ? `<span class="badge" style="font-size: 0.7rem;">${esc(task.badge_label)}</span>` : ''}
              </div>
              <p style="margin: 0 0 0.5rem; font-size: 0.875rem; color: var(--text-secondary); line-height: 1.45;">
                ${esc(task.description || 'Master key competencies and demonstrate practical skill.')}
              </p>
            </div>

            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <label for="status-select-${taskId}" style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Status:</label>
              <select id="status-select-${taskId}" class="form-control" style="font-size: 0.825rem; padding: 0.35rem 0.65rem; border-radius: var(--radius-sm); width: auto;">
                <option value="not_started" ${currentStatus === 'not_started' ? 'selected' : ''}>Not Started</option>
                <option value="in_progress" ${currentStatus === 'in_progress' ? 'selected' : ''}>⏳ In Progress</option>
                <option value="completed" ${currentStatus === 'completed' ? 'selected' : ''}>✓ Completed</option>
              </select>
            </div>
          </div>

          ${hasResources ? `
            <div style="margin-top: 0.85rem; padding-top: 0.75rem; border-top: 1px dashed var(--border);">
              <small style="font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Curated Learning Resources:</small>
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
        `;

        const selectEl = taskRow.querySelector(`#status-select-${taskId}`);
        if (selectEl) {
          selectEl.addEventListener("change", (e) => {
            const newStatus = e.target.value;
            setTaskStatus(taskId, newStatus);
            applyTaskCardStyle(taskRow, newStatus);
          });
        }

        tasksListEl.appendChild(taskRow);
      });

      stagesContainer.appendChild(stageCard);
    });
  }

  function applyTaskCardStyle(cardEl, status) {
    if (!cardEl) return;
    if (status === "completed") {
      cardEl.style.borderLeft = "4px solid var(--success)";
      cardEl.style.opacity = "0.9";
    } else if (status === "in_progress") {
      cardEl.style.borderLeft = "4px solid var(--warning)";
      cardEl.style.opacity = "1";
    } else {
      cardEl.style.borderLeft = "4px solid var(--border)";
      cardEl.style.opacity = "1";
    }
  }

  function updateOverallProgress() {
    if (!currentRoadmap) return;
    const stages = currentRoadmap.stages || (currentRoadmap.roadmap && currentRoadmap.roadmap.stages) || [];

    let totalTasks = 0;
    let completedTasks = 0;

    stages.forEach((stage, stageIndex) => {
      const tasks = stage.skills || stage.tasks || [];
      tasks.forEach((task, taskIndex) => {
        totalTasks += 1;
        const taskId = task.skill_id || task.task_id || `stage_${stage.order || stageIndex + 1}_task_${taskIndex + 1}`;
        if (getTaskStatus(taskId) === "completed") {
          completedTasks += 1;
        }
      });
    });

    const pct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    if (overallPercentEl) overallPercentEl.textContent = `${pct}%`;
    if (overallTaskCounterEl) overallTaskCounterEl.textContent = `${completedTasks} of ${totalTasks} tasks completed`;
    if (overallBarEl) {
      overallBarEl.style.width = `${pct}%`;
      if (pct === 100) overallBarEl.style.background = "var(--success)";
      else if (pct >= 50) overallBarEl.style.background = "var(--primary)";
      else overallBarEl.style.background = "var(--primary-dark, #2563eb)";
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
