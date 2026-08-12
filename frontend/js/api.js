window.HINTAI_API_URL = window.HINTAI_API_URL || "https://hintai-ai-v2.onrender.com";

const API = {
  baseUrl: window.HINTAI_API_URL,

  async request(endpoint, method = "GET", body = null) {
    const userId = window.Storage ? window.Storage.getUserId() : "anon_user";
    const token = window.Storage ? window.Storage.getAuthToken() : null;
    const headers = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    let url = endpoint.startsWith("http") ? endpoint : `${this.baseUrl}${endpoint}`;
    const options = { method, headers };
    if (body && !(body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify({ ...body, user_id: userId });
    } else if (body instanceof FormData) {
      options.body = body;
    }
    if (method === "GET" && !url.includes("user_id=")) {
      url += `${url.includes("?") ? "&" : "?"}user_id=${encodeURIComponent(userId)}`;
    }
    const res = await fetch(url, options);
    const json = await res.json().catch(() => ({}));
    if (!res.ok || !json.success) throw new Error(json.error?.message || "Une erreur est survenue.");
    return json.data;
  },

  async streamRequest(endpoint, body, callbacks = {}) {
    try {
      const data = await this.request(endpoint, "POST", body);
      callbacks.onInit?.(data);
      const chunks = [
        ["ANALYSIS", data.analysis], ["CONCEPT", data.key_concept], ["HINT1", data.hints?.[1] || data.hint1],
        ["METHOD", data.method_explanation], ["SOLUTION", data.full_solution], ["EXPLANATION", data.explanation],
        ["EXAMPLE", data.example], ["EXERCISE", data.exercise], ["CORRECTION", data.correction], ["QUIZ", data.quiz && JSON.stringify(data.quiz)]
      ];
      chunks.forEach(([section, text]) => { if (text) callbacks.onChunk?.({ section, text }); });
      callbacks.onDone?.(data);
      return data;
    } catch (err) {
      callbacks.onError?.(err);
      if (!callbacks.onError) throw err;
    }
  },

  getHealth() { return this.request("/api/health"); },
  getUserMe() { return this.request("/api/user/me"); },
  getUserCredits() { return this.request("/api/user/credits"); },
  claimReward() { return this.request("/api/user/reward", "POST"); },
  uploadFile(formData) { return this.request("/api/upload", "POST", formData); },
  startHelpMe(exerciseText, fileId) { return this.request("/api/help-me/start", "POST", { exercise_text: exerciseText, file_id: fileId }); },
  startHelpMeStream(exerciseText, fileId, callbacks) { return this.streamRequest("/api/help-me/start", { exercise_text: exerciseText, file_id: fileId }, callbacks); },
  getHint(sessionId, level) { return this.request(`/api/help-me/hint/${level}`, "POST", { session_id: sessionId }); },
  getHintStream(sessionId, level, callbacks) { return this.streamRequest(`/api/help-me/hint/${level}`, { session_id: sessionId }, callbacks); },
  getSolution(sessionId) { return this.request("/api/help-me/solution", "POST", { session_id: sessionId }); },
  getSolutionStream(sessionId, callbacks) { return this.streamRequest("/api/help-me/solution", { session_id: sessionId }, callbacks); },
  learnConcept(concept, level = "Collège / Lycée") { return this.request("/api/learn-concept/start", "POST", { concept, user_level: level }); },
  learnConceptStream(concept, level = "Collège / Lycée", callbacks) { return this.streamRequest("/api/learn-concept/start", { concept, user_level: level }, callbacks); },
  register(email, password, name) { return this.request("/api/auth/register", "POST", { email, password, name, anon_user_id: window.Storage.getUserId() }); },
  login(email, password) { return this.request("/api/auth/login", "POST", { email, password }); },
  logout() { return this.request("/api/auth/logout", "POST"); }
};

window.API = API;
