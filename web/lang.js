/* 中英切换：优先 ?lang=，其次上次的选择，否则默认中文 */
(function(){
 const KEY='cpi-lang',root=document.documentElement;
 let saved=null;try{saved=localStorage.getItem(KEY)}catch(e){}
 const qp=new URLSearchParams(location.search).get('lang');
 let lang=qp==='en'||qp==='zh'?qp:saved==='en'||saved==='zh'?saved:'zh';
 const apply=()=>{root.lang=lang==='en'?'en':'zh-CN';
  document.querySelectorAll('[data-zh-title]').forEach(el=>{document.title=lang==='en'?el.dataset.enTitle:el.dataset.zhTitle});
  document.querySelectorAll('.lang button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.lang===lang))};
 window.LANG={get:()=>lang,set(l){if(l===lang)return;lang=l;try{localStorage.setItem(KEY,l)}catch(e){}
  apply();document.dispatchEvent(new CustomEvent('langchange',{detail:l}))}};
 apply();
 document.addEventListener('DOMContentLoaded',()=>{apply();
  document.querySelectorAll('.lang button').forEach(b=>b.onclick=()=>LANG.set(b.dataset.lang))});
})();
