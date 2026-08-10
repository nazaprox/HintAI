```javascript
/* ============================================================
   HintAI — analyser.js
   ============================================================

   Analyse locale des images avec OpenCV.js.

   Responsabilités :
   - attendre le chargement d'OpenCV
   - vérifier la qualité d'une image
   - détecter une image trop sombre/floue
   - améliorer localement l'image
   - recadrer automatiquement autour du contenu
   - convertir le résultat en Blob
   - préparer l'image pour l'API

   IMPORTANT :
   Aucune analyse IA n'est effectuée ici.
   OpenCV.js fonctionne localement dans le navigateur.
   ============================================================ */


/* ============================================================
   ÉTAT OPENCV
   ============================================================ */

let opencvReady = false;


/* ============================================================
   INITIALISATION
   ============================================================ */

function waitForOpenCV(timeout = 15000) {
    return new Promise((resolve, reject) => {

        const start = Date.now();

        const check = () => {

            if (
                typeof cv !== "undefined" &&
                cv &&
                typeof cv.Mat === "function"
            ) {
                opencvReady = true;
                resolve(cv);
                return;
            }

            if (Date.now() - start >= timeout) {
                reject(
                    new Error(
                        "OpenCV.js n'a pas pu être chargé."
                    )
                );
                return;
            }

            setTimeout(check, 100);
        };

        check();
    });
}


/* ============================================================
   ÉTAT OPENCV
   ============================================================ */

async function ensureOpenCV() {

    if (opencvReady) {
        return true;
    }

    try {
        await waitForOpenCV();
        return true;
    } catch (error) {
        console.error(
            "OpenCV:",
            error
        );

        return false;
    }
}


/* ============================================================
   CHARGER UNE IMAGE
   ============================================================ */

function loadImage(source) {

    return new Promise(
        (resolve, reject) => {

            const image = new Image();

            image.onload = () => {
                resolve(image);
            };

            image.onerror = () => {
                reject(
                    new Error(
                        "Impossible de charger l'image."
                    )
                );
            };

            if (
                typeof source === "string"
            ) {
                image.src = source;
                return;
            }

            if (
                source instanceof Blob
            ) {
                image.src =
                    URL.createObjectURL(
                        source
                    );
                return;
            }

            reject(
                new Error(
                    "Source d'image invalide."
                )
            );
        }
    );
}


/* ============================================================
   DIMENSIONS
   ============================================================ */

function getImageDimensions(image) {

    return {
        width:
            image.naturalWidth ||
            image.width,

        height:
            image.naturalHeight ||
            image.height
    };
}


/* ============================================================
   LIMITER LA TAILLE
   ============================================================ */

function calculateResize(
    width,
    height,
    maxDimension = 1800
) {

    const largest =
        Math.max(
            width,
            height
        );

    if (
        largest <= maxDimension
    ) {
        return {
            width,
            height,
            scale: 1
        };
    }

    const scale =
        maxDimension /
        largest;

    return {
        width:
            Math.round(
                width * scale
            ),

        height:
            Math.round(
                height * scale
            ),

        scale
    };
}


/* ============================================================
   IMAGE → CANVAS
   ============================================================ */

function imageToCanvas(
    image,
    maxDimension = 1800
) {

    const dimensions =
        getImageDimensions(
            image
        );

    const resized =
        calculateResize(
            dimensions.width,
            dimensions.height,
            maxDimension
        );

    const canvas =
        document.createElement(
            "canvas"
        );

    canvas.width =
        resized.width;

    canvas.height =
        resized.height;

    const context =
        canvas.getContext(
            "2d",
            {
                willReadFrequently: true
            }
        );

    if (!context) {
        throw new Error(
            "Canvas 2D indisponible."
        );
    }

    context.drawImage(
        image,
        0,
        0,
        resized.width,
        resized.height
    );

    return canvas;
}


/* ============================================================
   CANVAS → MAT
   ============================================================ */

function canvasToMat(canvas) {

    if (!opencvReady) {
        throw new Error(
            "OpenCV.js n'est pas prêt."
        );
    }

    return cv.imread(
        canvas
    );
}


/* ============================================================
   QUALITÉ : LUMINOSITÉ
   ============================================================ */

function calculateBrightness(mat) {

    const gray =
        new cv.Mat();

    try {

        cv.cvtColor(
            mat,
            gray,
            cv.COLOR_RGBA2GRAY
        );

        const mean =
            cv.mean(
                gray
            )[0];

        return mean;

    } finally {

        gray.delete();
    }
}


/* ============================================================
   QUALITÉ : CONTRASTE
   ============================================================ */

function calculateContrast(mat) {

    const gray =
        new cv.Mat();

    const mean =
        new cv.Mat();

    const stddev =
        new cv.Mat();

    try {

        cv.cvtColor(
            mat,
            gray,
            cv.COLOR_RGBA2GRAY
        );

        cv.meanStdDev(
            gray,
            mean,
            stddev
        );

        return stddev.data64F[0];

    } finally {

        gray.delete();
        mean.delete();
        stddev.delete();
    }
}


/* ============================================================
   QUALITÉ : NETTETÉ
   ============================================================ */

function calculateSharpness(mat) {

    const gray =
        new cv.Mat();

    const laplacian =
        new cv.Mat();

    const mean =
        new cv.Mat();

    const stddev =
        new cv.Mat();

    try {

        cv.cvtColor(
            mat,
            gray,
            cv.COLOR_RGBA2GRAY
        );

        cv.Laplacian(
            gray,
            laplacian,
            cv.CV_64F
        );

        cv.meanStdDev(
            laplacian,
            mean,
            stddev
        );

        const value =
            stddev.data64F[0];

        return value * value;

    } finally {

        gray.delete();
        laplacian.delete();
        mean.delete();
        stddev.delete();
    }
}


/* ============================================================
   DÉTECTION QUALITÉ
   ============================================================ */

async function checkImageQuality(
    source
) {

    const ready =
        await ensureOpenCV();

    if (!ready) {

        return {
            success: false,
            usable: true,
            warning:
                "OpenCV.js indisponible. L'image sera envoyée telle quelle."
        };
    }

    let mat = null;

    try {

        const image =
            await loadImage(
                source
            );

        const canvas =
            imageToCanvas(
                image,
                1200
            );

        mat =
            canvasToMat(
                canvas
            );

        const brightness =
            calculateBrightness(
                mat
            );

        const contrast =
            calculateContrast(
                mat
            );

        const sharpness =
            calculateSharpness(
                mat
            );

        const warnings = [];

        if (
            brightness < 45
        ) {
            warnings.push(
                "L'image semble trop sombre."
            );
        }

        if (
            brightness > 235
        ) {
            warnings.push(
                "L'image semble surexposée."
            );
        }

        if (
            contrast < 15
        ) {
            warnings.push(
                "Le contraste semble faible."
            );
        }

        if (
            sharpness < 35
        ) {
            warnings.push(
                "L'image semble floue."
            );
        }

        return {

            success: true,

            usable:
                warnings.length < 3,

            brightness,
            contrast,
            sharpness,

            warnings
        };

    } catch (error) {

        console.error(
            "Erreur qualité image:",
            error
        );

        return {
            success: false,
            usable: true,
            warnings: [
                "La qualité n'a pas pu être évaluée."
            ]
        };

    } finally {

        if (mat) {
            mat.delete();
        }
    }
}


/* ============================================================
   AMÉLIORATION IMAGE
   ============================================================ */

async function enhanceImage(
    source
) {

    const ready =
        await ensureOpenCV();

    if (!ready) {
        return source;
    }

    let src = null;
    let gray = null;
    let enhanced = null;
    let resultCanvas = null;

    try {

        const image =
            await loadImage(
                source
            );

        const canvas =
            imageToCanvas(
                image,
                1800
            );

        src =
            canvasToMat(
                canvas
            );

        gray =
            new cv.Mat();

        enhanced =
            new cv.Mat();

        cv.cvtColor(
            src,
            gray,
            cv.COLOR_RGBA2GRAY
        );

        /*
         * CLAHE améliore le contraste local,
         * particulièrement utile pour les photos
         * de feuilles ou d'exercices.
         */

        const clahe =
            new cv.CLAHE(
                2.0,
                new cv.Size(
                    8,
                    8
                )
            );

        clahe.apply(
            gray,
            enhanced
        );

        clahe.delete();

        resultCanvas =
            document.createElement(
                "canvas"
            );

        resultCanvas.width =
            enhanced.cols;

        resultCanvas.height =
            enhanced.rows;

        cv.imshow(
            resultCanvas,
            enhanced
        );

        return await canvasToBlob(
            resultCanvas,
            "image/jpeg",
            0.88
        );

    } catch (error) {

        console.error(
            "Erreur amélioration image:",
            error
        );

        return source;

    } finally {

        if (src) {
            src.delete();
        }

        if (gray) {
            gray.delete();
        }

        if (enhanced) {
            enhanced.delete();
        }
    }
}


/* ============================================================
   DÉTECTION DU CONTENU
   ============================================================ */

async function detectContentBounds(
    source
) {

    const ready =
        await ensureOpenCV();

    if (!ready) {
        return null;
    }

    let src = null;
    let gray = null;
    let blurred = null;
    let edges = null;

    try {

        const image =
            await loadImage(
                source
            );

        const canvas =
            imageToCanvas(
                image,
                1600
            );

        src =
            canvasToMat(
                canvas
            );

        gray =
            new cv.Mat();

        blurred =
            new cv.Mat();

        edges =
            new cv.Mat();

        cv.cvtColor(
            src,
            gray,
            cv.COLOR_RGBA2GRAY
        );

        cv.GaussianBlur(
            gray,
            blurred,
            new cv.Size(
                5,
                5
            ),
            0
        );

        cv.Canny(
            blurred,
            edges,
            50,
            150
        );

        const contours =
            new cv.MatVector();

        const hierarchy =
            new cv.Mat();

        cv.findContours(
            edges,
            contours,
            hierarchy,
            cv.RETR_EXTERNAL,
            cv.CHAIN_APPROX_SIMPLE
        );

        let bestRect = null;
        let bestArea = 0;

        for (
            let i = 0;
            i < contours.size();
            i++
        ) {

            const contour =
                contours.get(i);

            const rect =
                cv.boundingRect(
                    contour
                );

            const area =
                rect.width *
                rect.height;

            if (
                area > bestArea
            ) {

                bestArea = area;
                bestRect = rect;
            }

            contour.delete();
        }

        contours.delete();
        hierarchy.delete();

        if (!bestRect) {
            return null;
        }

        /*
         * Évite les faux recadrages sur des zones
         * trop petites.
         */

        const imageArea =
            src.cols *
            src.rows;

        if (
            bestArea <
            imageArea * 0.08
        ) {
            return null;
        }

        return {
            x: bestRect.x,
            y: bestRect.y,
            width: bestRect.width,
            height: bestRect.height
        };

    } catch (error) {

        console.error(
            "Détection contenu:",
            error
        );

        return null;

    } finally {

        if (src) {
            src.delete();
        }

        if (gray) {
            gray.delete();
        }

        if (blurred) {
            blurred.delete();
        }

        if (edges) {
            edges.delete();
        }
    }
}


/* ============================================================
   RECADRAGE
   ============================================================ */

async function cropImage(
    source,
    bounds,
    padding = 25
) {

    if (!bounds) {
        return source;
    }

    const image =
        await loadImage(
            source
        );

    const canvas =
        imageToCanvas(
            image,
            1800
        );

    const x =
        Math.max(
            0,
            bounds.x - padding
        );

    const y =
        Math.max(
            0,
            bounds.y - padding
        );

    const right =
        Math.min(
            canvas.width,
            bounds.x +
                bounds.width +
                padding
        );

    const bottom =
        Math.min(
            canvas.height,
            bounds.y +
                bounds.height +
                padding
        );

    const width =
        right - x;

    const height =
        bottom - y;

    if (
        width <= 0 ||
        height <= 0
    ) {
        return source;
    }

    const output =
        document.createElement(
            "canvas"
        );

    output.width = width;
    output.height = height;

    const context =
        output.getContext(
            "2d"
        );

    if (!context) {
        return source;
    }

    context.drawImage(
        canvas,
        x,
        y,
        width,
        height,
        0,
        0,
        width,
        height
    );

    return canvasToBlob(
        output,
        "image/jpeg",
        0.9
    );
}


/* ============================================================
   CANVAS → BLOB
   ============================================================ */

function canvasToBlob(
    canvas,
    type = "image/jpeg",
    quality = 0.9
) {

    return new Promise(
        (resolve, reject) => {

            canvas.toBlob(
                blob => {

                    if (!blob) {
                        reject(
                            new Error(
                                "Impossible de créer le Blob."
                            )
                        );

                        return;
                    }

                    resolve(blob);
                },
                type,
                quality
            );
        }
    );
}


/* ============================================================
   PIPELINE COMPLET
   ============================================================ */

async function prepareImage(
    source,
    options = {}
) {

    const {
        enhance = true,
        autoCrop = false
    } = options;

    /*
     * 1. Vérification qualité
     */

    const quality =
        await checkImageQuality(
            source
        );

    /*
     * 2. Amélioration locale
     */

    let result =
        source;

    if (enhance) {

        result =
            await enhanceImage(
                result
            );
    }

    /*
     * 3. Recadrage optionnel
     */

    if (autoCrop) {

        const bounds =
            await detectContentBounds(
                result
            );

        if (bounds) {

            result =
                await cropImage(
                    result,
                    bounds
                );
        }
    }

    return {
        blob: result,
        quality
    };
}


/* ============================================================
   VALIDATION FICHIER
   ============================================================ */

function validateImageFile(
    file
) {

    if (!(file instanceof File)) {

        return {
            valid: false,
            message:
                "Fichier image invalide."
        };
    }

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (
        !allowedTypes.includes(
            file.type
        )
    ) {

        return {
            valid: false,
            message:
                "Format image non supporté."
        };
    }

    const maxSize =
        10 * 1024 * 1024;

    if (
        file.size > maxSize
    ) {

        return {
            valid: false,
            message:
                "L'image dépasse 10 Mo."
        };
    }

    return {
        valid: true
    };
}


/* ============================================================
   EXPORT GLOBAL
   ============================================================ */

window.HintAIAnalyzer = {

    waitForOpenCV,

    ensureOpenCV,

    checkImageQuality,

    enhanceImage,

    detectContentBounds,

    cropImage,

    prepareImage,

    validateImageFile,

    imageToCanvas,

    canvasToBlob

};


/* ============================================================
   LOG
   ============================================================ */

console.log(
    "HintAI Analyzer chargé."
);
```
