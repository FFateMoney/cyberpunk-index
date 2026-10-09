/* 榜单页、明细页共用：数据访问、配色、国名、转义。
   数据来自 data/cpi.js（由 code/04_web.py 生成，勿手改），结构见该脚本说明。
   需在 lang.js、names.js、data/cpi.js 之后加载。 */
(function(){
 const D=window.CPI_DATA;
 if(!D){ // 数据文件缺失时给出提示，而不是一片空白
  document.addEventListener('DOMContentLoaded',()=>document.body.insertAdjacentHTML('afterbegin',
   '<div style="position:relative;z-index:99;margin:16px;padding:16px;border:1px solid #ff3864;background:#1a0510;color:#ffd6e0;font:15px/1.6 monospace">'+
   '数据文件 web/data/cpi.js 缺失：请在项目根目录运行 <b>python code/run_all.py</b>（或 python code/04_web.py）。<br>'+
   'Data file web/data/cpi.js is missing: run <b>python code/run_all.py</b> from the project root.</div>'));
  return;
 }
 const YEARS=Object.keys(D.data).sort();
 const MAXALL=Math.max(...YEARS.flatMap(y=>Object.values(D.data[y]).map(r=>r[2])));
 const ZH=window.ZH_NAMES||{};
 // 颜色：青 → 紫 → 品红 → 黄，按全部年份最高 CPI 归一，跨年份可比
 const STOPS=[[0,[0,240,255]],[.42,[139,92,255]],[.72,[255,43,214]],[1,[252,238,10]]];
 const toRow=(iso,r)=>({iso,country:D.names[iso]||iso,T:r[0],L:r[1],CPI:r[2],rank:r[3],sub:r[4],ind:r[5]});

 window.CPI={
  D,YEARS,MAXALL,
  /** 某快照年的全部入榜国家，按名次排序 */
  rows:y=>Object.entries(D.data[y]||{}).map(([iso,r])=>toRow(iso,r)).sort((a,b)=>a.rank-b.rank),
  /** 某国某年的数据，不在榜返回 null */
  row:(y,iso)=>D.data[y]&&D.data[y][iso]?toRow(iso,D.data[y][iso]):null,
  /** 当前语言下的国名；中文缺失时退回英文 */
  name:iso=>LANG.get()==='zh'?(ZH[iso]||D.names[iso]||iso):(D.names[iso]||iso),
  zhName:iso=>ZH[iso]||'',
  col(v){const t=Math.max(0,Math.min(1,v/MAXALL));let i=1;while(i<STOPS.length-1&&t>STOPS[i][0])i++;
   const[a,ca]=STOPS[i-1],[b,cb]=STOPS[i],k=(t-a)/(b-a);return`rgb(${ca.map((c,j)=>Math.round(c+(cb[j]-c)*k))})`},
  esc:s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])),
  link:(iso,y)=>`country.html?iso=${iso}&year=${y}`,
 };
})();
