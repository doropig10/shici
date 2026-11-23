// Use Android's decoder only when a packaged image fails in WebView.
// Requests retain only the currently attached image, never an entire-book cache.
(function(){
 'use strict';
 const pending=new Map();let sequence=0;
 function status(img,text){
  let label=img.nextElementSibling;
  if(!label||!label.classList.contains('image-status')){label=document.createElement('span');label.className='image-status';label.setAttribute('role','status');img.insertAdjacentElement('afterend',label);}
  label.textContent=text;img.style.display='none';
 }
 function failed(img,code){status(img,'图片未能打开（'+code+'），请关闭后重新打开此词条。');}
 document.addEventListener('error',event=>{
  const img=event.target;
  if(!(img instanceof HTMLImageElement))return;
  if(img.dataset.nativeImage){failed(img,'DISPLAY');return;}
  const path=img.getAttribute('src')||'';
  if(!/^(cards|book)\/[A-Za-z0-9_().-]+\.webp$/.test(path)||path.includes('..'))return;
  if(!window.Android||typeof Android.requestImage!=='function')return;
  const token='image-'+(++sequence);img.dataset.nativeImage=token;
  for(const [key,value] of pending){if(!value.img.isConnected){clearTimeout(value.timer);pending.delete(key);}}
  const timer=setTimeout(()=>{const entry=pending.get(token);pending.delete(token);if(entry?.img.isConnected)failed(entry.img,'TIMEOUT');},20000);
  pending.set(token,{img,timer});status(img,'正在从安装包读取图片…');
  try{Android.requestImage(path,token);}catch(e){window.receiveNativeImage(token,'','BRIDGE');}
 },true);
 window.receiveNativeImage=function(token,data,error){
  const entry=pending.get(token);if(!entry)return;
  clearTimeout(entry.timer);pending.delete(token);
  const img=entry.img;if(!img.isConnected)return;
  if(error||!/^data:image\/(png|jpeg);base64,/.test(data)){failed(img,error||'FORMAT');return;}
  img.addEventListener('load',()=>{img.style.removeProperty('display');const label=img.nextElementSibling;if(label?.classList.contains('image-status'))label.remove();},{once:true});
  img.src=data;
 };
})();
