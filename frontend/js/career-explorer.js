// Career Explorer Controller: Handles search, filtering, modal presentation and target career selection
(function () {
  const STORAGE_KEY_STUDENT = "ai-student-mentor.studentId";
  const STORAGE_KEY_TARGET = "ai-student-mentor.targetCareerId";

  let allCareers = [];
  let currentCategory = "all";
  let searchQuery = "";
  let currentSelectedCareer = null;

  const esc = (window.appUtils && window.appUtils.escapeHTML) || ((s) => String(s || ""));
  const formatTitle = (window.appUtils && window.appUtils.formatTitle) || ((s) => String(s || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()));

  // DOM Elements
  const gridEl = document.getElementById("careers-grid");
  const loadingEl = document.getElementById("careers-loading");
  const errorEl = document.getElementById("careers-error");
  const emptyFilterEl = document.getElementById("careers-empty-filter");
  const countTextEl = document.getElementById("careers-count-text");
  const searchInput = document.getElementById("career-search-input");
  const categoriesContainer = document.getElementById("category-filters");
  const resetBtn = document.getElementById("reset-filters-btn");

  // Target Career Banner Elements
  const targetBanner = document.getElementById("target-career-banner");
  const targetNameEl = document.getElementById("target-career-name");
  const targetCatEl = document.getElementById("target-career-cat");
  const viewTargetBtn = document.getElementById("view-target-btn");

  // Modal Elements
  const modalBackdrop = document.getElementById("career-modal-backdrop");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalDismissBtn = document.getElementById("modal-dismiss-btn");
  const modalTitle = document.getElementById("modal-career-title");
  const modalCat = document.getElementById("modal-career-category");
  const modalDesc = document.getElementById("modal-career-desc");
  const modalReqSkills = document.getElementById("modal-required-skills");
  const modalRecSkills = document.getElementById("modal-recommended-skills");
  const modalPrereqs = document.getElementById("modal-prerequisites-list");
  const modalRelated = document.getElementById("modal-related-careers");
  const modalTargetBtn = document.getElementById("modal-set-target-btn");
  const modalTargetIndicator = document.getElementById("modal-target-indicator");
  const toastEl = document.getElementById("career-toast");

  function showToast(message) {
    if (!toastEl) return;
    toastEl.querySelector("span").textContent = message;
    toastEl.classList.add("show");
    setTimeout(() => {
      toastEl.classList.remove("show");
    }, 3200);
  }

  // Load active student pill in top nav
  async function loadStudentNav() {
    const studentId = localStorage.getItem(STORAGE_KEY_STUDENT);
    const navPill = document.getElementById("nav-user-pill");
    if (!navPill) return;

    if (!studentId) {
      navPill.innerHTML = `<div class="avatar-initial">?</div><span>Select Student</span>`;
      return;
    }

    try {
      const response = await window.api.get(`/api/students/${encodeURIComponent(studentId)}`);
      const student = response.student || response.data;
      if (student) {
        const initials = (student.name || "")
          .split(" ")
          .map((n) => n[0])
          .slice(0, 2)
          .join("")
          .toUpperCase();
        navPill.innerHTML = `
          <div class="avatar-initial">${esc(initials)}</div>
          <span>${esc(student.name)}</span>
        `;
        // If no explicit target set in localStorage, default to student's first goal
        if (!localStorage.getItem(STORAGE_KEY_TARGET) && student.career_goals && student.career_goals.length > 0) {
          localStorage.setItem(STORAGE_KEY_TARGET, student.career_goals[0]);
        }
      }
    } catch (err) {
      console.warn("Could not load student for nav:", err);
    }
  }

  // Fetch initial data: careers and categories
  async function init() {
    await loadStudentNav();

    if (loadingEl) loadingEl.style.display = "block";
    if (errorEl) errorEl.style.display = "none";

    try {
      const [careersRes, catRes] = await Promise.all([
        window.api.get("/api/careers"),
        window.api.get("/api/careers/categories").catch(() => ({ categories: [] })),
      ]);

      allCareers = careersRes.careers || careersRes.data || [];
      const categories = catRes.categories || [];

      renderCategoryButtons(categories);
      updateTargetBanner();
      renderCareers();

      if (loadingEl) loadingEl.style.display = "none";

      // Check if URL specified a career to highlight
      const urlParams = new URLSearchParams(window.location.search);
      const highlightId = urlParams.get("highlight") || urlParams.get("id");
      if (highlightId) {
        openCareerModal(highlightId);
      }
    } catch (err) {
      console.error("Failed to load careers:", err);
      if (loadingEl) loadingEl.style.display = "none";
      if (errorEl) {
        errorEl.style.display = "block";
        errorEl.innerHTML = `
          <strong>Failed to load career data:</strong> ${esc(err.message || 'Backend unreachable')}
          <br><button class="btn btn-sm btn-secondary" style="margin-top: 0.5rem;" onclick="window.location.reload()">Retry</button>
        `;
      }
    }
  }

  function renderCategoryButtons(categories) {
    if (!categoriesContainer) return;

    // Use categories from API or derive unique ones from loaded careers
    const uniqueCats = categories.length
      ? categories
      : Array.from(new Set(allCareers.map((c) => c.category))).filter(Boolean).sort();

    categoriesContainer.innerHTML = `
      <button class="filter-btn active" data-category="all" type="button">All Categories</button>
    `;

    uniqueCats.forEach((cat) => {
      const btn = document.createElement("button");
      btn.className = "filter-btn";
      btn.setAttribute("data-category", cat);
      btn.type = "button";
      btn.textContent = cat;
      btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        currentCategory = cat;
        renderCareers();
      });
      categoriesContainer.appendChild(btn);
    });

    const allBtn = categoriesContainer.querySelector('[data-category="all"]');
    if (allBtn) {
      allBtn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
        allBtn.classList.add("active");
        currentCategory = "all";
        renderCareers();
      });
    }
  }

  function updateTargetBanner() {
    const targetId = localStorage.getItem(STORAGE_KEY_TARGET);
    if (!targetId || !targetBanner) {
      if (targetBanner) targetBanner.style.display = "none";
      return;
    }

    const career = allCareers.find((c) => c.id === targetId);
    if (career) {
      targetBanner.style.display = "flex";
      if (targetNameEl) targetNameEl.textContent = career.title;
      if (targetCatEl) targetCatEl.textContent = career.category;
      if (viewTargetBtn) {
        viewTargetBtn.onclick = () => openCareerModal(career.id);
      }
    } else {
      targetBanner.style.display = "none";
    }
  }

  function filterCareers() {
    return allCareers.filter((career) => {
      // Category filter
      if (currentCategory !== "all" && career.category.toLowerCase() !== currentCategory.toLowerCase()) {
        return false;
      }
      // Search filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const inTitle = (career.title || "").toLowerCase().includes(q);
        const inDesc = (career.description || "").toLowerCase().includes(q);
        const inCat = (career.category || "").toLowerCase().includes(q);
        const inReqSkills = (career.required_skills || []).some((s) => s.toLowerCase().includes(q));
        const inRecSkills = (career.recommended_skills || []).some((s) => s.toLowerCase().includes(q));
        return inTitle || inDesc || inCat || inReqSkills || inRecSkills;
      }
      return true;
    });
  }

  function renderCareers() {
    if (!gridEl) return;
    const filtered = filterCareers();
    const targetCareerId = localStorage.getItem(STORAGE_KEY_TARGET);

    if (countTextEl) {
      countTextEl.textContent = `Showing ${filtered.length} of ${allCareers.length} career paths`;
    }

    if (filtered.length === 0) {
      gridEl.innerHTML = "";
      if (emptyFilterEl) emptyFilterEl.style.display = "block";
      return;
    }

    if (emptyFilterEl) emptyFilterEl.style.display = "none";
    gridEl.innerHTML = "";

    filtered.forEach((career) => {
      const isTarget = career.id === targetCareerId;
      const card = document.createElement("div");
      card.className = "card career-card" + (isTarget ? " selected" : "");

      const reqSkills = (career.required_skills || [])
        .slice(0, 4)
        .map((s) => `<span class="chip">${formatTitle(s)}</span>`)
        .join("");

      const prereqSummary = (career.prerequisites || []).slice(0, 2).map(p => esc(p)).join(" • ");

      card.innerHTML = `
        ${isTarget ? '<div class="target-badge">🎯 Current Target</div>' : ""}
        <div class="card-header" style="margin-bottom: 0.5rem;">
          <div>
            <div class="category-tag">${esc(career.category)}</div>
            <h3 style="margin: 0; font-size: 1.25rem;">${esc(career.title)}</h3>
          </div>
        </div>
        <div class="card-body">
          <p class="career-desc">${esc(career.description)}</p>
          <div style="margin-bottom: 0.75rem;">
            <small style="text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700;">Required Skills</small>
            <div class="chips" style="margin-top: 0.35rem;">
              ${reqSkills || '<span style="font-size: 0.85rem; color: var(--text-muted);">None listed</span>'}
              ${(career.required_skills || []).length > 4 ? `<span class="badge">+${career.required_skills.length - 4} more</span>` : ''}
            </div>
          </div>
          ${prereqSummary ? `
            <div style="margin-top: 0.5rem; font-size: 0.825rem; color: var(--text-secondary);">
              <strong>Prerequisites:</strong> ${prereqSummary}
            </div>
          ` : ''}
        </div>
        <div class="card-footer" style="gap: 0.5rem;">
          <button class="btn btn-sm btn-outline view-details-btn" type="button">
            View Details
          </button>
          <button class="btn btn-sm ${isTarget ? 'btn-secondary' : 'btn-primary'} set-target-btn" type="button">
            ${isTarget ? '✓ Selected' : 'Set as Target'}
          </button>
        </div>
      `;

      // Event Listeners
      card.querySelector(".view-details-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        openCareerModal(career.id);
      });

      card.querySelector(".set-target-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        selectTargetCareer(career);
      });

      card.addEventListener("click", () => {
        openCareerModal(career.id);
      });

      gridEl.appendChild(card);
    });
  }

  function selectTargetCareer(career) {
    localStorage.setItem(STORAGE_KEY_TARGET, career.id);
    updateTargetBanner();
    renderCareers();
    showToast(`🎯 "${career.title}" set as your target career!`);

    // If modal is currently open for this career, update modal button too
    if (currentSelectedCareer && currentSelectedCareer.id === career.id) {
      if (modalTargetIndicator) modalTargetIndicator.style.display = "inline-flex";
      if (modalTargetBtn) {
        modalTargetBtn.textContent = "✓ Current Target Career";
        modalTargetBtn.className = "btn btn-secondary";
      }
    }
  }

  async function openCareerModal(careerId) {
    if (!modalBackdrop) return;

    // First check in-memory cache
    let career = allCareers.find((c) => c.id === careerId);

    // Fetch enriched details from backend
    try {
      const res = await window.api.get(`/api/careers/${encodeURIComponent(careerId)}`);
      if (res.career || res.data) {
        career = res.career || res.data;
      }
    } catch (err) {
      console.warn("Could not fetch enriched career details, using cached record:", err);
    }

    if (!career) return;
    currentSelectedCareer = career;

    const targetCareerId = localStorage.getItem(STORAGE_KEY_TARGET);
    const isTarget = career.id === targetCareerId;

    if (modalTitle) modalTitle.textContent = career.title;
    if (modalCat) modalCat.textContent = career.category;
    if (modalDesc) modalDesc.textContent = career.description;

    if (modalTargetIndicator) {
      modalTargetIndicator.style.display = isTarget ? "inline-flex" : "none";
    }

    if (modalTargetBtn) {
      if (isTarget) {
        modalTargetBtn.textContent = "✓ Current Target Career";
        modalTargetBtn.className = "btn btn-secondary";
      } else {
        modalTargetBtn.textContent = "🎯 Set as My Target Career";
        modalTargetBtn.className = "btn btn-primary";
      }
      modalTargetBtn.onclick = () => selectTargetCareer(career);
    }

    const modalAnalyzeBtn = document.getElementById("modal-analyze-gap-btn");
    if (modalAnalyzeBtn) {
      modalAnalyzeBtn.style.display = "inline-flex";
      modalAnalyzeBtn.href = `skill-gap.html?career=${encodeURIComponent(career.id)}`;
    }

    // Required Skills
    if (modalReqSkills) {
      const skillsDetail = career.required_skills_detail || [];
      if (skillsDetail.length > 0) {
        modalReqSkills.innerHTML = skillsDetail
          .map(
            (s) => `
            <div class="chip" style="display: flex; flex-direction: column; align-items: flex-start; padding: 0.5rem 0.85rem; border-radius: var(--radius-md);">
              <div style="font-weight: 600; color: var(--text-primary);">${esc(s.name)}</div>
              ${s.description ? `<small style="color: var(--text-muted); font-size: 0.775rem;">${esc(s.description)}</small>` : ''}
            </div>
          `
          )
          .join("");
      } else {
        const skills = career.required_skills || [];
        modalReqSkills.innerHTML = skills.length
          ? skills.map((s) => `<span class="chip">${formatTitle(s)}</span>`).join("")
          : '<span style="color: var(--text-muted); font-size: 0.9rem;">None specified.</span>';
      }
    }

    // Recommended Skills
    if (modalRecSkills) {
      const recDetail = career.recommended_skills_detail || [];
      if (recDetail.length > 0) {
        modalRecSkills.innerHTML = recDetail
          .map(
            (s) => `
            <div class="chip" style="display: flex; flex-direction: column; align-items: flex-start; padding: 0.5rem 0.85rem; border-radius: var(--radius-md);">
              <div style="font-weight: 600; color: var(--text-primary);">${esc(s.name)}</div>
              ${s.description ? `<small style="color: var(--text-muted); font-size: 0.775rem;">${esc(s.description)}</small>` : ''}
            </div>
          `
          )
          .join("");
      } else {
        const rec = career.recommended_skills || [];
        modalRecSkills.innerHTML = rec.length
          ? rec.map((s) => `<span class="chip">${formatTitle(s)}</span>`).join("")
          : '<span style="color: var(--text-muted); font-size: 0.9rem;">No additional recommendations.</span>';
      }
    }

    // Prerequisites
    if (modalPrereqs) {
      const prereqs = career.prerequisites || [];
      modalPrereqs.innerHTML = prereqs.length
        ? prereqs.map((p) => `<li style="margin-bottom: 0.35rem;">${esc(p)}</li>`).join("")
        : '<li style="list-style: none; margin-left: -1.25rem; color: var(--text-muted);">None specified.</li>';
    }

    // Related Careers
    if (modalRelated) {
      const relatedDetail = career.related_careers_detail || [];
      if (relatedDetail.length > 0) {
        modalRelated.innerHTML = "";
        relatedDetail.forEach((r) => {
          const btn = document.createElement("button");
          btn.className = "chip";
          btn.style.cssText = "cursor: pointer; background: var(--surface); border: 1px solid var(--border);";
          btn.type = "button";
          btn.textContent = `🔗 ${r.title}`;
          btn.addEventListener("click", () => openCareerModal(r.id));
          modalRelated.appendChild(btn);
        });
      } else {
        const related = career.related_careers || [];
        modalRelated.innerHTML = "";
        if (related.length > 0) {
          related.forEach((rid) => {
            const btn = document.createElement("button");
            btn.className = "chip";
            btn.style.cssText = "cursor: pointer; background: var(--surface); border: 1px solid var(--border);";
            btn.type = "button";
            btn.textContent = `🔗 ${formatTitle(rid)}`;
            btn.addEventListener("click", () => openCareerModal(rid));
            modalRelated.appendChild(btn);
          });
        } else {
          modalRelated.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">No related paths listed.</span>';
        }
      }
    }

    modalBackdrop.classList.add("open");
  }

  function closeModal() {
    if (modalBackdrop) {
      modalBackdrop.classList.remove("open");
      currentSelectedCareer = null;
    }
  }

  window.careerExplorerOpenModal = (careerId) => {
    openCareerModal(careerId);
  };

  // Search input handler
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value;
      renderCareers();
    });
  }

  // Reset button in empty state
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      searchQuery = "";
      currentCategory = "all";
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      const allBtn = document.querySelector('[data-category="all"]');
      if (allBtn) allBtn.classList.add("active");
      renderCareers();
    });
  }

  // Modal event listeners
  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (modalDismissBtn) modalDismissBtn.addEventListener("click", closeModal);
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) closeModal();
    });
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modalBackdrop && modalBackdrop.classList.contains("open")) {
      closeModal();
    }
  });

  document.addEventListener("DOMContentLoaded", init);
})();
