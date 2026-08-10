/* ============================================================
   HintAI — main.js
   ============================================================

   Contrôleur principal du frontend.

   Responsabilités :
   - communication avec FastAPI
   - gestion de l'API
   - gestion des crédits
   - Help Me
   - Learn a Concept
   - uploads
   - streaming SSE
   - historique local
   - authentification locale
   - séries quotidiennes
   - publicités
   - connexion avec analyser.js / OpenCV.js

   ============================================================ */


/* ============================================================
   CONFIGURATION
   ============================================================ */

const API_BASE =
    window.HINTAI_API_URL ||
    "";

const STORAGE_PREFIX =
    "hintai_";

const STORAGE_KEYS = {
    anonymousId:
        `${STORAGE_PREFIX}anonymous_id`,

    token:
        `${STORAGE_PREFIX}token`,

    credits:
        `${STORAGE_PREFIX}credits`,

    history:
        `${STORAGE_PREFIX}history`,

    streak:
        `${STORAGE_PREFIX}streak`,

    lastAction:
        `${STORAGE_PREFIX}last_action`
};


/* ============================================================
   ÉTAT GLOBAL
   ============================================================ */

const state = {

    credits: 20,

    streak: 0,

    authenticated: false,

    token: null,

    anonymousId: null,

    currentResponseId: null,

    currentMode: null,

    currentQuestion: null,

    loading: false,

    history: [],

    lastActionDate: null
};


/* ============================================================
   UTILITAIRES DOM
   ============================================================ */

function $(selector) {
    return document.querySelector(
        selector
    );
}


function $$(selector) {
    return Array.from(
        document.querySelectorAll(
            selector
        )
    );
}


function setText(
    selector,
    value
) {

    const element =
        $(selector);

    if (element) {
        element.textContent =
            value;
    }
}


function show(
    selector
) {

    const element =
        $(selector);

    if (element) {
        element.hidden = false;
        element.style.display = "";
    }
}


function hide(
    selector
) {

    const element =
        $(selector);

    if (element) {
        element.hidden = true;
        element.style.display = "none";
    }
}


function toggle(
    selector,
    visible
) {

    if (visible) {
        show(selector);
    } else {
        hide(selector);
    }
}


/* ============================================================
   STOCKAGE LOCAL
   ============================================================ */

function storageGet(
    key,
    fallback = null
) {

    try {

        const value =
            localStorage.getItem(
                key
            );

        if (
            value === null
        ) {
            return fallback;
        }

        return JSON.parse(
            value
        );

    } catch {

        return fallback;
    }
}


function storageSet(
    key,
    value
) {

    try {

        localStorage.setItem(
            key,
            JSON.stringify(
                value
            )
        );

    } catch (error) {

        console.error(
            "Storage:",
            error
        );
    }
}


function storageRemove(
    key
) {

    try {

        localStorage.removeItem(
            key
        );

    } catch {
        // Rien à faire.
    }
}


/* ============================================================
   IDENTIFIANT ANONYME
   ============================================================ */

function generateAnonymousId() {

    if (
        window.crypto &&
        crypto.randomUUID
    ) {

        return crypto.randomUUID();
    }

    return (
        "anon-" +
        Date.now() +
        "-" +
        Math.random()
            .toString(36)
            .slice(2)
    );
}


function getAnonymousId() {

    let id =
        storageGet(
            STORAGE_KEYS.anonymousId
        );

    if (!id) {

        id =
            generateAnonymousId();

        storageSet(
            STORAGE_KEYS.anonymousId,
            id
        );
    }

    state.anonymousId =
        id;

    return id;
}


/* ============================================================
   INITIALISATION ÉTAT
   ============================================================ */

function loadState() {

    state.anonymousId =
        getAnonymousId();

    state.token =
        storageGet(
            STORAGE_KEYS.token
        );

    state.authenticated =
        Boolean(
            state.token
        );

    state.credits =
        Number(
            storageGet(
                STORAGE_KEYS.credits,
                20
            )
        );

    state.history =
        storageGet(
            STORAGE_KEYS.history,
            []
        );

    const streak =
        storageGet(
            STORAGE_KEYS.streak,
            {
                count: 0,
                lastDate: null
            }
        );

    state.streak =
        Number(
            streak.count || 0
        );

    state.lastActionDate =
        streak.lastDate;

    updateUI();
}


/* ============================================================
   CRÉDITS
   ============================================================ */

function getCredits() {
    return state.credits;
}


function setCredits(
    amount
) {

    state.credits =
        Math.max(
            0,
            Number(amount) || 0
        );

    storageSet(
        STORAGE_KEYS.credits,
        state.credits
    );

    updateCreditUI();
}


function addCredits(
    amount
) {

    if (
        !Number.isFinite(
            Number(amount)
        )
    ) {
        return;
    }

    setCredits(
        state.credits +
        Number(amount)
    );
}


function canSpend(
    amount
) {

    return (
        state.credits >=
        Number(amount)
    );
}


function spendCredits(
    amount
) {

    amount =
        Number(amount);

    if (
        !Number.isFinite(
            amount
        ) ||
        amount < 0
    ) {
        return false;
    }

    if (
        !canSpend(
            amount
        )
    ) {

        showInsufficientCredits();

        return false;
    }

    setCredits(
        state.credits -
        amount
    );

    return true;
}


/* ============================================================
   COÛTS
   ============================================================ */

const CREDIT_COSTS = {

    helpMeAnalysis: 2,

    hint: 1,

    question: 1,

    solution: 2,

    evaluationExercise: 1,

    correction: 1,

    exerciseQuestion: 1,

    exerciseHint: 1,

    learnExplanation: 2,

    learnQuestion: 1,

    learnHint: 1,

    simpleExercise: 1,

    difficultExercise: 2,

    newExplanation: 1,

    documentAnalysis: 1,

    upload: 0.5
};


/* ============================================================
   AFFICHAGE CRÉDITS
   ============================================================ */

function updateCreditUI() {

    const selectors = [
        "#credits",
        "#credit-count",
        "[data-credits]",
        ".credit-count"
    ];

    selectors.forEach(
        selector => {

            $$(selector).forEach(
                element => {

                    element.textContent =
                        String(
                            state.credits
                        );
                }
            );
        }
    );
}


/* ============================================================
   ERREUR CRÉDITS
   ============================================================ */

function showInsufficientCredits() {

    const message =
        "Crédits insuffisants.";

    if (
        typeof window.showToast ===
        "function"
    ) {

        window.showToast(
            message
        );

        return;
    }

    alert(
        message
    );
}


/* ============================================================
   DATES
   ============================================================ */

function dateKey(
    date = new Date()
) {

    return date
        .toISOString()
        .slice(
            0,
            10
        );
}


function yesterdayKey() {

    const date =
        new Date();

    date.setDate(
        date.getDate() - 1
    );

    return dateKey(
        date
    );
}


/* ============================================================
   SÉRIE QUOTIDIENNE
   ============================================================ */

function registerRealAction() {

    const today =
        dateKey();

    const previous =
        state.lastActionDate;

    if (
        previous === today
    ) {
        return;
    }

    if (
        previous === yesterdayKey()
    ) {

        state.streak += 1;

    } else {

        state.streak = 1;
    }

    state.lastActionDate =
        today;

    storageSet(
        STORAGE_KEYS.streak,
        {
            count:
                state.streak,

            lastDate:
                today
        }
    );

    /*
     * Récompenses :
     * 3 jours = +6 crédits
     * 6 jours = +12 crédits
     *
     * La récompense n'est accordée
     * qu'après une véritable action.
     */

    if (
        state.streak === 3
    ) {

        addCredits(6);

        notify(
            "Série de 3 jours : +6 crédits !"
        );
    }

    if (
        state.streak === 6
    ) {

        addCredits(12);

        notify(
            "Série de 6 jours : +12 crédits !"
        );
    }

    updateStreakUI();
}


function updateStreakUI() {

    $$(

        "[data-streak]"

    ).forEach(
        element => {

            element.textContent =
                String(
                    state.streak
                );
        }
    );
}


/* ============================================================
   NOTIFICATION
   ============================================================ */

function notify(
    message
) {

    if (
        typeof window.showToast ===
        "function"
    ) {

        window.showToast(
            message
        );

        return;
    }

    console.log(
        "[HintAI]",
        message
    );
}


/* ============================================================
   HEADERS API
   ============================================================ */

function apiHeaders(
    json = true
) {

    const headers = {};

    if (json) {

        headers[
            "Content-Type"
        ] =
            "application/json";
    }

    if (
        state.token
    ) {

        headers[
            "Authorization"
        ] =
            `Bearer ${state.token}`;
    }

    headers[
        "X-Anonymous-ID"
    ] =
        getAnonymousId();

    return headers;
}


/* ============================================================
   API REQUEST
   ============================================================ */

async function apiRequest(
    endpoint,
    options = {}
) {

    const {
        method = "GET",
        body = undefined,
        json = true,
        signal = undefined
    } = options;

    const response =
        await fetch(
            API_BASE +
            endpoint,
            {
                method,

                headers:
                    apiHeaders(
                        json
                    ),

                body:
                    body === undefined
                        ? undefined
                        : json
                            ? JSON.stringify(
                                body
                            )
                            : body,

                signal
            }
        );

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";

    let data;

    if (
        contentType.includes(
            "application/json"
        )
    ) {

        data =
            await response.json();

    } else {

        data =
            await response.text();
    }

    if (
        !response.ok
    ) {

        const message =
            data &&
            typeof data ===
                "object"
                ? data.message ||
                  "Erreur API."
                : "Erreur API.";

        throw new Error(
            message
        );
    }

    return data;
}


/* ============================================================
   SSE
   ============================================================ */

async function readSSE(
    response,
    callbacks = {}
) {

    if (
        !response.body
    ) {
        throw new Error(
            "Streaming non disponible."
        );
    }

    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder(
            "utf-8"
        );

    let buffer = "";

    while (true) {

        const {
            done,
            value
        } =
            await reader.read();

        if (done) {
            break;
        }

        buffer +=
            decoder.decode(
                value,
                {
                    stream: true
                }
            );

        const events =
            buffer.split(
                "\n\n"
            );

        buffer =
            events.pop() || "";

        for (
            const rawEvent
            of events
        ) {

            processSSEEvent(
                rawEvent,
                callbacks
            );
        }
    }

    if (
        buffer.trim()
    ) {

        processSSEEvent(
            buffer,
            callbacks
        );
    }
}


function processSSEEvent(
    rawEvent,
    callbacks
) {

    let eventName =
        "message";

    let dataText =
        "";

    const lines =
        rawEvent.split(
            "\n"
        );

    for (
        const line
        of lines
    ) {

        if (
            line.startsWith(
                "event:"
            )
        ) {

            eventName =
                line
                    .slice(6)
                    .trim();
        }

        if (
            line.startsWith(
                "data:"
            )
        ) {

            dataText +=
                line
                    .slice(5)
                    .trim();
        }
    }

    let data =
        dataText;

    try {

        data =
            JSON.parse(
                dataText
            );

    } catch {
        // Data texte.
    }

    const callback =
        callbacks[
            eventName
        ];

    if (
        typeof callback ===
        "function"
    ) {

        callback(
            data
        );
    }

    if (
        typeof callbacks.onEvent ===
        "function"
    ) {

        callbacks.onEvent(
            eventName,
            data
        );
    }
}


/* ============================================================
   STREAM API
   ============================================================ */

async function streamAPI(
    endpoint,
    body,
    callbacks = {}
) {

    const response =
        await fetch(
            API_BASE +
            endpoint,
            {
                method: "POST",

                headers:
                    apiHeaders(
                        true
                    ),

                body:
                    JSON.stringify(
                        body
                    )
            }
        );

    if (
        !response.ok
    ) {

        let message =
            "Erreur serveur.";

        try {

            const data =
                await response.json();

            message =
                data.message ||
                message;

        } catch {
            // Rien.
        }

        throw new Error(
            message
        );
    }

    await readSSE(
        response,
        callbacks
    );
}


/* ============================================================
   HELP ME — DÉMARRER
   ============================================================ */

async function startHelpMe(
    payload
) {

    if (
        !payload ||
        typeof payload !==
            "object"
    ) {

        throw new Error(
            "Données Help Me invalides."
        );
    }

    if (
        !spendCredits(
            CREDIT_COSTS.helpMeAnalysis
        )
    ) {
        return null;
    }

    state.loading = true;
    state.currentMode =
        "help-me";

    registerRealAction();

    let responseId =
        null;

    let output = "";

    try {

        await streamAPI(
            "/api/help-me/start",
            payload,
            {

                start(data) {

                    responseId =
                        data.id ||
                        data.responseId ||
                        null;

                    state.currentResponseId =
                        responseId;
                },

                status(data) {

                    updateStatus(
                        data.message ||
                        ""
                    );
                },

                token(data) {

                    const text =
                        data.text ||
                        "";

                    output +=
                        text;

                    appendResponseText(
                        text
                    );
                },

                complete(data) {

                    state.currentResponseId =
                        data.responseId ||
                        responseId;
                },

                onEvent(
                    event,
                    data
                ) {

                    if (
                        event ===
                        "complete"
                    ) {

                        saveHistory(
                            {
                                mode:
                                    "help-me",

                                responseId:
                                    state.currentResponseId,

                                text:
                                    output,

                                date:
                                    new Date()
                                        .toISOString()
                            }
                        );
                    }
                }
            }
        );

        return {
            responseId:
                state.currentResponseId,

            text:
                output
        };

    } catch (error) {

        /*
         * Si le serveur échoue avant de produire
         * une réponse, restituer les crédits.
         */

        addCredits(
            CREDIT_COSTS.helpMeAnalysis
        );

        throw error;

    } finally {

        state.loading =
            false;

        updateLoadingUI();
    }
}


/* ============================================================
   HELP ME — INDICE
   ============================================================ */

async function requestHint(
    level
) {

    if (
        ![1, 2, 3].includes(
            Number(level)
        )
    ) {

        throw new Error(
            "Niveau d'indice invalide."
        );
    }

    if (
        !state.currentResponseId
    ) {

        throw new Error(
            "Aucune session Help Me active."
        );
    }

    if (
        !spendCredits(
            CREDIT_COSTS.hint
        )
    ) {
        return null;
    }

    let output = "";

    try {

        await streamAPI(
            `/api/help-me/hint/${level}`,
            {
                responseId:
                    state.currentResponseId
            },
            {

                token(data) {

                    const text =
                        data.text ||
                        "";

                    output +=
                        text;

                    appendResponseText(
                        text
                    );
                }
            }
        );

        return output;

    } catch (error) {

        addCredits(
            CREDIT_COSTS.hint
        );

        throw error;
    }
}


/* ============================================================
   HELP ME — QUESTION
   ============================================================ */

async function askHelpMeQuestion(
    question
) {

    question =
        String(
            question || ""
        ).trim();

    if (
        !question
    ) {

        throw new Error(
            "La question est vide."
        );
    }

    if (
        !state.currentResponseId
    ) {

        throw new Error(
            "Aucune session active."
        );
    }

    if (
        !spendCredits(
            CREDIT_COSTS.question
        )
    ) {
        return null;
    }

    let output = "";

    try {

        await streamAPI(
            "/api/help-me/question",
            {
                responseId:
                    state.currentResponseId,

                question
            },
            {

                token(data) {

                    const text =
                        data.text ||
                        "";

                    output +=
                        text;

                    appendResponseText(
                        text
                    );
                }
            }
        );

        return output;

    } catch (error) {

        addCredits(
            CREDIT_COSTS.question
        );

        throw error;
    }
}


/* ============================================================
   HELP ME — SOLUTION
   ============================================================ */

async function requestSolution() {

    if (
        !state.currentResponseId
    ) {

        throw new Error(
            "Aucune session active."
        );
    }

    if (
        !spendCredits(
            CREDIT_COSTS.solution
        )
    ) {
        return null;
    }

    let output = "";

    try {

        await streamAPI(
            "/api/help-me/solution",
            {
                responseId:
                    state.currentResponseId
            },
            {

                token(data) {

                    const text =
                        data.text ||
                        "";

                    output +=
                        text;

                    appendResponseText(
                        text
                    );
                }
            }
        );

        return output;

    } catch (error) {

        addCredits(
            CREDIT_COSTS.solution
        );

        throw error;
    }
}


/* ============================================================
   LEARN A CONCEPT
   ============================================================ */

async function startLearnConcept(
    concept,
    exercises = [],
    explanation = ""
) {

    concept =
        String(
            concept || ""
        ).trim();

    if (
        !concept
    ) {

        throw new Error(
            "Le concept est requis."
        );
    }

    if (
        !spendCredits(
            CREDIT_COSTS.learnExplanation
        )
    ) {
        return null;
    }

    state.loading = true;
    state.currentMode =
        "learn";

    registerRealAction();

    let output = "";
    let responseId = null;

    try {

        await streamAPI(
            "/api/learn-concept/start",
            {
                concept,
                exercises,
                explanation
            },
            {

                start(data) {

                    responseId =
                        data.id ||
                        data.responseId ||
                        null;

                    state.currentResponseId =
                        responseId;
                },

                token(data) {

                    const text =
                        data.text ||
                        "";

                    output +=
                        text;

                    appendResponseText(
                        text
                    );
                },

                complete(data) {

                    state.currentResponseId =
                        data.responseId ||
                        responseId;
                }
            }
        );

        saveHistory(
            {
                mode:
                    "learn",

                responseId:
                    state.currentResponseId,

                concept,

                text:
                    output,

                date:
                    new Date()
                        .toISOString()
            }
        );

        return {
            responseId:
                state.currentResponseId,

            text:
                output
        };

    } catch (error) {

        addCredits(
            CREDIT_COSTS.learnExplanation
        );

        throw error;

    } finally {

        state.loading = false;
        updateLoadingUI();
    }
}


/* ============================================================
   UPLOAD IMAGE
   ============================================================ */

async function uploadImage(
    file
) {

    if (
        !file
    ) {

        throw new Error(
            "Aucune image sélectionnée."
        );
    }

    if (
        window.HintAIAnalyzer &&
        typeof
            window.HintAIAnalyzer
                .validateImageFile ===
            "function"
    ) {

        const validation =
            window.HintAIAnalyzer
                .validateImageFile(
                    file
                );

        if (
            !validation.valid
        ) {

            throw new Error(
                validation.message
            );
        }
    }

    /*
     * 0,5 crédit pour l'upload.
     */

    if (
        !spendCredits(
            CREDIT_COSTS.upload
        )
    ) {
        return null;
    }

    let uploadFile =
        file;

    /*
     * Analyse et amélioration locale.
     * Cette opération ne coûte aucun crédit
     * supplémentaire.
     */

    if (
        window.HintAIAnalyzer &&
        typeof
            window.HintAIAnalyzer
                .prepareImage ===
            "function"
    ) {

        try {

            const prepared =
                await window.HintAIAnalyzer
                    .prepareImage(
                        file,
                        {
                            enhance: true,
                            autoCrop: false
                        }
                    );

            if (
                prepared &&
                prepared.blob
            ) {

                uploadFile =
                    prepared.blob;
            }

        } catch (error) {

            console.warn(
                "Analyse locale:",
                error
            );
        }
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        uploadFile,
        file.name ||
            "image.jpg"
    );

    try {

        /*
         * Endpoint volontairement centralisé.
         * Le backend peut l'adapter sans modifier
         * toute l'application.
         */

        const response =
            await fetch(
                API_BASE +
                "/api/upload",
                {
                    method: "POST",

                    headers:
                        apiHeaders(
                            false
                        ),

                    body:
                        formData
                }
            );

        if (
            !response.ok
        ) {

            throw new Error(
                "Échec de l'upload."
            );
        }

        const data =
            await response.json();

        return data;

    } catch (error) {

        /*
         * Échec d'upload :
         * restitution du demi-crédit.
         */

        addCredits(
            CREDIT_COSTS.upload
        );

        throw error;
    }
}


/* ============================================================
   UPLOAD PDF
   ============================================================ */

async function uploadPDF(
    file
) {

    if (
        !file
    ) {

        throw new Error(
            "Aucun PDF sélectionné."
        );
    }

    if (
        file.type !==
        "application/pdf"
    ) {

        throw new Error(
            "Le fichier doit être un PDF."
        );
    }

    const maxSize =
        20 * 1024 * 1024;

    if (
        file.size > maxSize
    ) {

        throw new Error(
            "Le PDF dépasse 20 Mo."
        );
    }

    if (
        !spendCredits(
            CREDIT_COSTS.upload
        )
    ) {
        return null;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    try {

        const response =
            await fetch(
                API_BASE +
                "/api/upload",
                {
                    method: "POST",

                    headers:
                        apiHeaders(
                            false
                        ),

                    body:
                        formData
                }
            );

        if (
            !response.ok
        ) {

            throw new Error(
                "Échec de l'upload PDF."
            );
        }

        return await response.json();

    } catch (error) {

        addCredits(
            CREDIT_COSTS.upload
        );

        throw error;
    }
}


/* ============================================================
   HISTORIQUE LOCAL
   ============================================================ */

function saveHistory(
    item
) {

    state.history.unshift(
        item
    );

    /*
     * On conserve les derniers éléments
     * localement.
     */

    state.history =
        state.history.slice(
            0,
            100
        );

    storageSet(
        STORAGE_KEYS.history,
        state.history
    );

    renderHistory();
}


function getHistory() {
    return [
        ...state.history
    ];
}


function clearHistory() {

    state.history = [];

    storageSet(
        STORAGE_KEYS.history,
        []
    );

    renderHistory();
}


function renderHistory() {

    const containers =
        $$(
            "[data-history]"
        );

    containers.forEach(
        container => {

            container.innerHTML =
                "";

            if (
                state.history.length ===
                0
            ) {

                const empty =
                    document.createElement(
                        "div"
                    );

                empty.textContent =
                    "Aucun historique.";

                container.appendChild(
                    empty
                );

                return;
            }

            state.history.forEach(
                item => {

                    const element =
                        document.createElement(
                            "div"
                        );

                    element.className =
                        "history-item";

                    const title =
                        document.createElement(
                            "strong"
                        );

                    title.textContent =
                        item.concept ||
                        item.mode ||
                        "Session";

                    const date =
                        document.createElement(
                            "small"
                        );

                    date.textContent =
                        item.date
                            ? new Date(
                                item.date
                              ).toLocaleString()
                            : "";

                    element.appendChild(
                        title
                    );

                    element.appendChild(
                        date
                    );

                    container.appendChild(
                        element
                    );
                }
            );
        }
    );
}


/* ============================================================
   AUTHENTIFICATION
   ============================================================ */

function setAuthToken(
    token
) {

    state.token =
        token || null;

    state.authenticated =
        Boolean(
            state.token
        );

    if (
        state.token
    ) {

        storageSet(
            STORAGE_KEYS.token,
            state.token
        );

    } else {

        storageRemove(
            STORAGE_KEYS.token
        );
    }

    updateAuthUI();
}


function logout() {

    setAuthToken(
        null
    );

    notify(
        "Déconnexion effectuée."
    );
}


function updateAuthUI() {

    $$(
        "[data-authenticated]"
    ).forEach(
        element => {

            element.hidden =
                !state.authenticated;
        }
    );

    $$(
        "[data-unauthenticated]"
    ).forEach(
        element => {

            element.hidden =
                state.authenticated;
        }
    );
}


/* ============================================================
   PUBLICITÉ SIMPLE
   ============================================================ */

function showSimpleAd() {

    /*
     * Publicité simple :
     * 5 secondes.
     *
     * Aucun crédit gagné.
     */

    const ad =
        $(
            "#ad-container"
        );

    if (!ad) {
        return;
    }

    ad.hidden = false;

    let remaining = 5;

    const timer =
        setInterval(
            () => {

                setText(
                    "#ad-countdown",
                    `${remaining}s`
                );

                remaining -= 1;

                if (
                    remaining < 0
                ) {

                    clearInterval(
                        timer
                    );

                    ad.hidden = true;
                }

            },
            1000
        );
}


/* ============================================================
   PUBLICITÉ RÉCOMPENSÉE
   ============================================================ */

function showRewardedAd(
    reward = 0
) {

    /*
     * Publicité récompensée :
     * 15 secondes.
     *
     * La récompense est accordée uniquement
     * après la fin complète de la publicité.
     */

    const ad =
        $(
            "#rewarded-ad-container"
        );

    if (!ad) {

        if (
            reward > 0
        ) {
            addCredits(
                reward
            );
        }

        return;
    }

    ad.hidden = false;

    let remaining = 15;

    const timer =
        setInterval(
            () => {

                setText(
                    "#rewarded-ad-countdown",
                    `${remaining}s`
                );

                remaining -= 1;

                if (
                    remaining < 0
                ) {

                    clearInterval(
                        timer
                    );

                    ad.hidden = true;

                    if (
                        reward > 0
                    ) {

                        addCredits(
                            reward
                        );

                        notify(
                            `+${reward} crédits !`
                        );
                    }
                }

            },
            1000
        );
}


/* ============================================================
   UI RÉPONSE
   ============================================================ */

function appendResponseText(
    text
) {

    const targets =
        $$(
            "[data-response]"
        );

    if (
        targets.length === 0
    ) {

        console.log(
            text
        );

        return;
    }

    targets.forEach(
        target => {

            target.textContent +=
                text;

            target.scrollTop =
                target.scrollHeight;
        }
    );
}


function clearResponse() {

    $$(
        "[data-response]"
    ).forEach(
        target => {

            target.textContent =
                "";
        }
    );
}


function updateStatus(
    message
) {

    $$(
        "[data-status]"
    ).forEach(
        element => {

            element.textContent =
                message;
        }
    );
}


function updateLoadingUI() {

    $$(
        "[data-loading]"
    ).forEach(
        element => {

            element.hidden =
                !state.loading;
        }
    );
}


/* ============================================================
   UI GÉNÉRALE
   ============================================================ */

function updateUI() {

    updateCreditUI();

    updateStreakUI();

    updateAuthUI();

    renderHistory();

    updateLoadingUI();
}


/* ============================================================
   FORMULAIRE HELP ME
   ============================================================ */

function bindHelpMeForm() {

    const form =
        $(
            "#help-me-form"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            if (
                state.loading
            ) {
                return;
            }

            const textInput =
                form.querySelector(
                    "[name='text']"
                );

            const text =
                textInput
                    ? textInput.value.trim()
                    : "";

            if (!text) {

                notify(
                    "Entre ton exercice."
                );

                return;
            }

            clearResponse();

            try {

                await startHelpMe(
                    {
                        inputType:
                            "text",

                        text
                    }
                );

            } catch (error) {

                console.error(
                    error
                );

                notify(
                    error.message
                );
            }
        }
    );
}


/* ============================================================
   FORMULAIRE LEARN
   ============================================================ */

function bindLearnForm() {

    const form =
        $(
            "#learn-form"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const input =
                form.querySelector(
                    "[name='concept']"
                );

            const concept =
                input
                    ? input.value.trim()
                    : "";

            if (!concept) {

                notify(
                    "Entre un concept."
                );

                return;
            }

            clearResponse();

            try {

                await startLearnConcept(
                    concept
                );

            } catch (error) {

                console.error(
                    error
                );

                notify(
                    error.message
                );
            }
        }
    );
}


/* ============================================================
   BOUTONS D'ACTION
   ============================================================ */

function bindActions() {

    $$(
        "[data-action]"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                async () => {

                    const action =
                        button.dataset.action;

                    try {

                        switch (
                            action
                        ) {

                            case "hint-1":
                                await requestHint(
                                    1
                                );
                                break;

                            case "hint-2":
                                await requestHint(
                                    2
                                );
                                break;

                            case "hint-3":
                                await requestHint(
                                    3
                                );
                                break;

                            case "solution":
                                await requestSolution();
                                break;

                            case "clear-history":
                                clearHistory();
                                break;

                            case "logout":
                                logout();
                                break;

                            case "simple-ad":
                                showSimpleAd();
                                break;

                            case "rewarded-ad":
                                showRewardedAd(
                                    Number(
                                        button.dataset.reward ||
                                        0
                                    )
                                );
                                break;
                        }

                    } catch (error) {

                        console.error(
                            error
                        );

                        notify(
                            error.message
                        );
                    }
                }
            );
        }
    );
}


/* ============================================================
   INPUT FICHIER
   ============================================================ */

function bindFileInputs() {

    $$(
        "input[type='file']"
    ).forEach(
        input => {

            input.addEventListener(
                "change",
                async () => {

                    const file =
                        input.files &&
                        input.files[0];

                    if (!file) {
                        return;
                    }

                    try {

                        let result;

                        if (
                            file.type ===
                            "application/pdf"
                        ) {

                            result =
                                await uploadPDF(
                                    file
                                );

                        } else {

                            result =
                                await uploadImage(
                                    file
                                );
                        }

                        /*
                         * Permet au reste de l'interface
                         * de récupérer le résultat.
                         */

                        window.dispatchEvent(
                            new CustomEvent(
                                "hintai:upload",
                                {
                                    detail:
                                        result
                                }
                            )
                        );

                    } catch (error) {

                        console.error(
                            error
                        );

                        notify(
                            error.message
                        );

                    } finally {

                        input.value =
                            "";
                    }
                }
            );
        }
    );
}


/* ============================================================
   INITIALISATION
   ============================================================ */

function init() {

    loadState();

    bindHelpMeForm();

    bindLearnForm();

    bindActions();

    bindFileInputs();

    updateUI();

    console.log(
        "HintAI main.js chargé."
    );
}


/* ============================================================
   API PUBLIQUE
   ============================================================ */

window.HintAI = {

    state,

    getCredits,

    addCredits,

    spendCredits,

    canSpend,

    startHelpMe,

    requestHint,

    askHelpMeQuestion,

    requestSolution,

    startLearnConcept,

    uploadImage,

    uploadPDF,

    getHistory,

    clearHistory,

    showSimpleAd,

    showRewardedAd,

    setAuthToken,

    logout,

    notify
};


/* ============================================================
   DOM READY
   ============================================================ */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        init
    );

} else {

    init();
}

