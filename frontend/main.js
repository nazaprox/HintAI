const API_BASE = window.HINTAI_API_URL || "https://hintai-ai-v2.onrender.com";
const STORAGE_KEY = "hintai_state";

const state = { credits: 20, streak: 0, xp: 0, level: 1, solved: 0, currentResponseId: null, currentPage: "home", history: [] };
const $ = id => document.getElementById(id);

function saveState(){ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
function loadState(){ try { const saved=JSON.parse(localStorage.getItem(STORAGE_KEY)||"null"); if(saved) Object.assign(state,saved); } catch(e){ console.warn("state reset",e); } }
function showScreen(name){
  document.querySelectorAll(".screen").forEach(s=>s.classList.toggle("active",s.id===`screen-${name}`));
  document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.page===name));
  state.currentPage=name; saveState(); window.scrollTo({top:0,behavior:"smooth"});
}
function updateUI(){
  [$("credits"),$("homeCredits"),$("profileCredits")].forEach(el=>{if(el) el.textContent=Math.max(0,state.credits);});
  [$("profileStreak"),$("profileStreak2")].forEach(el=>{if(el) el.textContent=state.streak+(el.id==="profileStreak"?" j":"");});
  [$("homeXp"),$("profileXp")].forEach(el=>{if(el) el.textContent=state.xp;});
  [$("homeLevel"),$("profileLevel")].forEach(el=>{if(el) el.textContent=state.level;});
  [$("homeSolved"),$("profileSolved2")].forEach(el=>{if(el) el.textContent=state.solved;});
  const progress=$("xpProgress"); if(progress) progress.style.width=`${Math.min(100,(state.xp%100))}%`;
}
function spendCredits(amount){ if(state.credits<amount){ alert("Pas assez de crédits. Gagne 1 crédit avec une rewarded ad ou consulte ton offre."); return false; } state.credits-=amount; saveState(); updateUI(); return true; }
function gainProgress(amount=10){ state.xp+=amount; state.level=Math.max(1,Math.floor(state.xp/100)+1); state.solved+=1; state.streak=Math.max(1,state.streak); saveState(); updateUI(); }
function addHistory(label){ state.history.unshift({label,at:new Date().toLocaleString("fr-FR",{dateStyle:"short",timeStyle:"short"})}); state.history=state.history.slice(0,20); renderHistory(); saveState(); }
function renderHistory(){const box=$("history");if(box)box.innerHTML=state.history.length?state.history.map(x=>`<div class="history-item"><span>✓</span><div><strong>${escapeHtml(x.label)}</strong><small>${x.at}</small></div></div>`).join(""):"Aucune activité.";}
function escapeHtml(value){return String(value).replace(/[&<>'"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c]));}

async function readStream(response){
  if(!response.ok){let detail="Erreur serveur";try{const d=await response.json();detail=d.detail||detail;}catch(e){}throw new Error(detail);}
  if(!response.body)return;
  const reader=response.body.getReader(),decoder=new TextDecoder();let buffer="";
  while(true){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const events=buffer.split("\n\n");buffer=events.pop()||"";for(const event of events){const line=event.split("\n").find(x=>x.startsWith("data:"));if(!line)continue;try{const data=JSON.parse(line.slice(5).trim());if(event.includes("start")){state.currentResponseId=data.id;saveState();}if(event.includes("token"))appendResponse(data.text||"");if(event.includes("complete")&&data.responseId)state.currentResponseId=data.responseId;}catch(e){}}}
}
function appendResponse(text){const box=$("response");if(box.textContent.includes("Je suis prêt")||box.textContent.includes("en cours"))box.textContent="";box.textContent+=text;box.scrollTop=box.scrollHeight;}

async function analyse(){
  const text=$("exerciseInput").value.trim(),file=$("fileInput").files[0];
  if(!text&&!file){alert("Ajoute un exercice ou sélectionne un document.");return;}
  if(!spendCredits(2))return;
  $("response").textContent="Analyse en cours…";
  try{
    let payload={inputType:"text",text};
    if(file){payload.inputType=file.type==="application/pdf"?"pdf":"image";const form=new FormData();form.append("file",file);const upload=await fetch(`${API_BASE}/api/upload`,{method:"POST",headers:{"X-User-Id":getUserId()},body:form});if(!upload.ok)throw new Error("Upload refusé");const info=await upload.json();payload.fileId=info.fileId;}
    const response=await fetch(`${API_BASE}/api/help-me/start`,{method:"POST",headers:{"Content-Type":"application/json","X-User-Id":getUserId()},body:JSON.stringify(payload)});
    await readStream(response);gainProgress(10);addHistory("Analyse d’un exercice");
  }catch(error){$("response").textContent=error.message||"Erreur de connexion au serveur.";console.error(error);}
}
async function getHint(){if(!state.currentResponseId){alert("Analyse d'abord un exercice.");return;}if(!spendCredits(1))return;try{await readStream(await fetch(`${API_BASE}/api/help-me/hint/1`,{method:"POST",headers:{"Content-Type":"application/json","X-User-Id":getUserId()},body:JSON.stringify({responseId:state.currentResponseId})}));addHistory("Indice demandé");}catch(e){appendResponse(`\n${e.message}`);}}
async function getSolution(){if(!state.currentResponseId){alert("Analyse d'abord un exercice.");return;}if(!spendCredits(2))return;try{await readStream(await fetch(`${API_BASE}/api/help-me/solution`,{method:"POST",headers:{"Content-Type":"application/json","X-User-Id":getUserId()},body:JSON.stringify({responseId:state.currentResponseId})}));gainProgress(15);addHistory("Solution complète");}catch(e){appendResponse(`\n${e.message}`);}}
async function startLearn(){const concept=$("conceptInput").value.trim();if(!concept){alert("Indique un concept.");return;}if(!spendCredits(2))return;$("response").textContent="";try{await readStream(await fetch(`${API_BASE}/api/learn-concept/start`,{method:"POST",headers:{"Content-Type":"application/json","X-User-Id":getUserId()},body:JSON.stringify({concept})}));gainProgress(10);addHistory(`Apprentissage : ${concept}`);}catch(e){alert(e.message);}}
function getUserId(){let id=localStorage.getItem("hintai_user_id");if(!id){id=`anon_${crypto.randomUUID?crypto.randomUUID():Date.now()}`;localStorage.setItem("hintai_user_id",id);}return id;}
function initUpload(){const input=$("fileInput");$("cameraBtn").onclick=()=>{input.setAttribute("capture","environment");input.accept="image/*";input.click();};$("pdfBtn").onclick=()=>{input.removeAttribute("capture");input.accept=".pdf,application/pdf";input.click();};input.onchange=()=>{const f=input.files[0];if($("fileStatus"))$("fileStatus").textContent=f?`${f.name} · ${(f.size/1024/1024).toFixed(1)} Mo`:"Aucun fichier sélectionné.";};}
function init(){loadState();updateUI();renderHistory();initUpload();document.querySelectorAll("[data-page]").forEach(b=>b.addEventListener("click",()=>showScreen(b.dataset.page)));document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>showScreen(b.dataset.go)));$("analyseBtn").onclick=analyse;$("hintBtn").onclick=getHint;$("solutionBtn").onclick=getSolution;$("learnStartBtn").onclick=startLearn;}
document.addEventListener("DOMContentLoaded",init);
