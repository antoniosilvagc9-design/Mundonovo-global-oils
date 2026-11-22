/* Trading Global — atualização automática de versões publicadas (Modo TV).
   Compara o HTML efetivamente servido pelo GitHub Pages, sem alterar cotações. */
(function(){
 "use strict";
 if(!window.fetch || !window.crypto || !window.crypto.subtle || !window.TextEncoder)return;
 const tv=window.matchMedia("(min-width:1200px) and (min-aspect-ratio:3/2)");
 if(!tv.matches)return;
 const INTERVAL=30000;
 const url=new URL("index.html",document.baseURI);
 let baseline=null,busy=false;
 async function fingerprint(){
   const request=new URL(url.href);
   request.searchParams.set("_tv_version_check",String(Date.now()));
   const response=await fetch(request.href,{cache:"no-store",credentials:"same-origin"});
   if(!response.ok)throw new Error("Versão indisponível");
   const html=await response.text();
   const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(html));
   return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,"0")).join("");
 }
 async function check(){
   if(busy||document.hidden||!tv.matches||!navigator.onLine)return;
   busy=true;
   try{
     const current=await fingerprint();
     if(baseline===null){baseline=current;return;}
     if(current!==baseline){
       // Só recarrega quando a versão publicada mudou; nunca em intervalo fixo.
       window.location.reload();
     }
   }catch(e){ /* Rede instável: manter painel atual, tentar depois. */ }
   finally{busy=false;}
 }
 check();
 setInterval(check,INTERVAL);
 document.addEventListener("visibilitychange",()=>{if(!document.hidden)check()});
})();
