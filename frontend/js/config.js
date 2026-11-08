// Frontend configuration. Contains no secrets: API keys live only on the backend.
window.APP_CONFIG = Object.freeze({
  APP_NAME: "AI Student Mentor",
  // Edit the production URL after deploying the Flask backend to Render.
  API_BASE_URL: ["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://127.0.0.1:5000"
    : "https://ai-student-mentor-api.onrender.com",
  REQUEST_TIMEOUT_MS: 20000, // generous: free Render instances cold-start slowly
});
