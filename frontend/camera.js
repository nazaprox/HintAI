const HintAICamera = {

 stream: null,

 async start(video) {
  this.stream = await navigator.mediaDevices.getUserMedia({
   video: { facingMode: "environment" }
  });
  video.srcObject = this.stream;
 },

 capture(video, canvas) {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video,0,0);
  return new Promise(resolve => {
   canvas.toBlob(resolve,"image/jpeg",0.9);
  });
 },

 stop(){
  if(this.stream){
   this.stream.getTracks().forEach(t=>t.stop());
  }
 }
};
