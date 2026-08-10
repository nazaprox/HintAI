const API_BASE =
window.HINTAI_API_URL ||
"https://hintai-ai.onrender.com";



const state = {

    credits:20,

    streak:0,

    currentResponseId:null,

    currentPage:"home",

    history:[]

};





/* =========================
STORAGE
========================= */


function saveState(){

    localStorage.setItem(
        "hintai_state",
        JSON.stringify(state)
    );

}



function loadState(){

    const saved =
    localStorage.getItem(
        "hintai_state"
    );


    if(saved){

        Object.assign(
            state,
            JSON.parse(saved)
        );

    }

}




/* =========================
DOM
========================= */


function $(id){

    return document.getElementById(id);

}



function showScreen(name){


    document
    .querySelectorAll(".screen")
    .forEach(
        screen=>{

            screen.classList.remove(
                "active"
            );

        }
    );


    const target =
    $("screen-"+name);


    if(target){

        target.classList.add(
            "active"
        );

    }



    document
    .querySelectorAll(".nav-item")
    .forEach(
        btn=>{

            btn.classList.remove(
                "active"
            );

        }
    );



    const nav =
    document.querySelector(
        `[data-page="${name}"]`
    );


    if(nav){

        nav.classList.add(
            "active"
        );

    }



    state.currentPage=name;

}







/* =========================
NAVIGATION
========================= */


function initNavigation(){


document
.querySelectorAll("[data-page]")
.forEach(
button=>{


button.addEventListener(
"click",
()=>{


showScreen(
button.dataset.page
);


});



});



document
.querySelectorAll("[data-go]")
.forEach(
button=>{


button.addEventListener(
"click",
()=>{


showScreen(
button.dataset.go
);


});


});


}







/* =========================
CREDITS
========================= */


function updateCredits(){


$("credits").textContent =
state.credits;


$("profileCredits").textContent =
state.credits;


}




function spendCredits(amount){


if(state.credits < amount){


alert(
"Pas assez de crédits"
);


return false;


}


state.credits -= amount;


saveState();

updateCredits();


return true;


}







/* =========================
UPLOAD
========================= */


function initUpload(){



const input =
$("fileInput");



$("cameraBtn")
.onclick=()=>{

input.click();

};



$("pdfBtn")
.onclick=()=>{

input.click();

};



input.onchange=()=>{


if(input.files.length){


const file =
input.files[0];


document.querySelector(
"#response"
).textContent =

"Fichier sélectionné : "
+
file.name;



}


};


}








/* =========================
API SSE
========================= */


async function readStream(response){


const reader =
response.body.getReader();


const decoder =
new TextDecoder();


let result="";



while(true){


const {
done,
value
}
=
await reader.read();



if(done)
break;



const chunk =
decoder.decode(
value
);



result += chunk;



const events =
chunk.split(
"\n\n"
);



events.forEach(
event=>{


if(
event.includes(
"token"
)
){


try{


const data =
JSON.parse(
event.split(
"data:"
)[1]
);


appendResponse(
data.text
);


}catch(e){}



}



if(
event.includes(
"complete"
)
){

console.log(
"Terminé"
);

}


});



}



}







function appendResponse(text){


const box =
$("response");


if(
box.textContent.includes(
"Je suis prêt"
)
){

box.textContent="";

}



box.textContent += text;



}








/* =========================
HELP ME
========================= */



async function analyse(){



const text =
$("exerciseInput")
.value.trim();



if(!text){


alert(
"Ajoute un exercice"
);


return;


}



if(
!spendCredits(2)
)
return;



$("response").textContent =
"Analyse en cours...";




try{


const response =
await fetch(
API_BASE+
"/api/help-me/start",
{


method:"POST",


headers:{


"Content-Type":
"application/json"


},


body:
JSON.stringify({

inputType:"text",

text:text

})


}

);



await readStream(
response
);



}
catch(error){


$("response").textContent =
"Erreur connexion serveur";


console.error(
error
);


}



}








/* =========================
HINT
========================= */


async function getHint(){



if(
!spendCredits(1)
)
return;



const response =
await fetch(

API_BASE+
"/api/help-me/hint/1",

{

method:"POST",

headers:{

"Content-Type":
"application/json"

},

body:
JSON.stringify({

responseId:
state.currentResponseId

})

}


);



await readStream(
response
);


}







/* =========================
SOLUTION
========================= */


async function getSolution(){



if(
!spendCredits(2)
)
return;



const response =
await fetch(

API_BASE+
"/api/help-me/solution",

{

method:"POST",

headers:{

"Content-Type":
"application/json"

},

body:
JSON.stringify({

responseId:
state.currentResponseId

})

}


);



await readStream(
response
);


}







/* =========================
LEARN
========================= */


async function startLearn(){


const concept =
$("conceptInput")
.value.trim();



if(!concept)
return;



if(
!spendCredits(2)
)
return;



const response =
await fetch(

API_BASE+
"/api/learn-concept/start",

{


method:"POST",


headers:{


"Content-Type":
"application/json"


},


body:

JSON.stringify({

concept:concept

})


}

);



$("response").textContent =
"";



await readStream(
response
);



}








/* =========================
INIT
========================= */


function init(){



loadState();


updateCredits();


initNavigation();


initUpload();



$("analyseBtn")
.onclick =
analyse;



$("hintBtn")
.onclick =
getHint;



$("solutionBtn")
.onclick =
getSolution;



$("learnStartBtn")
.onclick =
startLearn;



}



document.addEventListener(
"DOMContentLoaded",
init
);