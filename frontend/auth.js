const API_BASE = window.HINTAI_API_URL || "https://hintai-ai.onrender.com";

const Auth = {
    token: localStorage.getItem("hintai_token"),

    async register(email, password) {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email, password})
        });
        return response.json();
    },

    async login(email, password) {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email, password})
        });

        const data = await response.json();

        if (data.token) {
            localStorage.setItem("hintai_token", data.token);
            this.token = data.token;
        }

        return data;
    },

    async profile() {
        return fetch(`${API_BASE}/auth/me`, {
            headers: {
                Authorization: `Bearer ${this.token}`
            }
        }).then(r => r.json());
    },

    logout() {
        localStorage.removeItem("hintai_token");
        this.token = null;
    }
};

window.HintAIAuth = Auth;
