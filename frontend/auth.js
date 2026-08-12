"use strict";

const Auth = {
    token: localStorage.getItem("hintai_token"),

    async register(email, password) {
        const response = await fetch(`${window.HINTAI_API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        return response.json();
    },

    async login(email, password) {
        const response = await fetch(`${window.HINTAI_API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (data.token) {
            localStorage.setItem("hintai_token", data.token);
            this.token = data.token;
        }
        return data;
    },

    async profile() {
        return fetch(`${window.HINTAI_API_URL}/auth/me`, {
            headers: this.token ? { Authorization: `Bearer ${this.token}` } : {}
        }).then(r => r.json());
    },

    logout() {
        localStorage.removeItem("hintai_token");
        this.token = null;
    },

    isAuthenticated() {
        return Boolean(this.token);
    }
};

window.HintAIAuth = Auth;
window.HintAI = window.HintAI || {};
window.HintAI.auth = Auth;
