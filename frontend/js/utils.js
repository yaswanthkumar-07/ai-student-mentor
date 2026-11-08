// Global utilities for safe escaping and DOM manipulation
(function () {
  function escapeHTML(str) {
    if (str == null) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatTitle(str) {
    if (!str) return "";
    return escapeHTML(str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()));
  }

  window.appUtils = {
    escapeHTML,
    formatTitle,
  };
})();
