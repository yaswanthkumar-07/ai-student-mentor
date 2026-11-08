```javascript
// Frontend configuration. Contains no secrets: API keys live only on the backend.
window.APP_CONFIG = Object.freeze({
  APP_NAME: "AI Student Mentor",
  API_BASE_URL: ["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://127.0.0.1:5000"
    : "https://ai-student-mentor-api-jn1z.onrender.com",
  REQUEST_TIMEOUT_MS: 20000,
});

// Minimal fetch wrapper used by every page. Exposes window.api.get / window.api.post.
(function () {
  async function request(path, options = {}) {
    const { API_BASE_URL, REQUEST_TIMEOUT_MS } = window.APP_CONFIG;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const response = await fetch(API_BASE_URL + path, {
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        ...options,
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.message || `Request failed (${response.status})`);
      return body;
    } finally {
      clearTimeout(timer);
    }
  }
  window.api = {
    get: (path) => request(path),
    post: (path, data) => request(path, { method: "POST", body: JSON.stringify(data) }),
  };
})();
```