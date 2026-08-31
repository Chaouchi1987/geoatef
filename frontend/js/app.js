const API=window.GEOANOMALY_API||"http://127.0.0.1:8000";
let TOKEN=localStorage.getItem("geo_token")||"";
let selectedScale=10,currentAnalysisId=null,eeConnected=false,eeMode=null,marker=null,circle=null,map=null,resizeObserver=null,targetLayers=[],reportCache=null,gaScanStartedAt=null;
let baseLayers={satellite:null,street:null};
const layerState={satellite:true,aoi:true,targets:true};
let geometryType="circle";

function formatDuration(seconds){const n=Math.max(0,Number(seconds)||0);if(n<60)return `${n.toFixed(1)} ث`;const m=Math.floor(n/60),sec=Math.round(n%60);return `${m}د ${String(sec).padStart(2,"0")}ث`;}
function setScanStatus(state,meta={}){const box=$("#gaScanStatus");if(!box)return;box.classList.remove("running","done","failed");if(state==="running")box.classList.add("running");if(state==="completed")box.classList.add("done");if(state==="failed")box.classList.add("failed");$("#gaScanState").textContent=state==="running"?"جارٍ الفحص":state==="completed"?"اكتمل الفحص":state==="failed"?"فشل الفحص":"جاهز";if(meta.duration_seconds!=null)$("#gaScanDuration").textContent=formatDuration(meta.duration_seconds);if(meta.sample_count!=null)$("#gaScanSamples").textContent=meta.sample_count;if(meta.observation_count!=null)$("#gaScanScenes").textContent=meta.observation_count;}
setInterval(()=>{if(gaScanStartedAt)$("#gaScanDuration").textContent=formatDuration((Date.now()-gaScanStartedAt)/1000)},250);
const $=s=>document.querySelector(s);
function esc(v){const d=document.createElement("div");d.textContent=v==null?"":String(v);return d.innerHTML;}
$("#langBtn")?.addEventListener("click",()=>window.toggleLanguage?.());

async function jsonFetch(url,opts={}){
  const controller=new AbortController(); const timeout=setTimeout(()=>controller.abort(),30000);
  opts.signal=opts.signal||controller.signal;
  opts.headers={...(opts.headers||{}),...(TOKEN?{"Authorization":`Bearer ${TOKEN}`}:{})};
  try{
    const r=await fetch(url,opts); const text=await r.text(); let d={}; try{d=JSON.parse(text)}catch{}
    if(!r.ok) throw new Error(d.detail||text||`HTTP ${r.status}`); return d;
  }catch(e){ if(e.name==="AbortError") throw new Error("انتهت مهلة الاتصال بالخادم."); throw e; } finally{ clearTimeout(timeout); }
}

function showApp(user){
  $("#authScreen").classList.add("hidden"); $("#app").classList.remove("hidden"); $("#userName").textContent=user.username;
  initMap(); setTimeout(()=>map&&map.invalidateSize(true),50); setTimeout(()=>map&&map.invalidateSize(true),300); setTimeout(()=>map&&map.invalidateSize(true),900);
  health(); checkEE();
}
function showAuth(){TOKEN="";localStorage.removeItem("geo_token");$("#app").classList.add("hidden");$("#authScreen").classList.remove("hidden");}

function resetAnalysisUI(){targetLayers.forEach(l=>map?.removeLayer(l));targetLayers=[];if(marker){map?.removeLayer(marker);marker=null}if(circle){map?.removeLayer(circle);circle=null}currentAnalysisId=null;reportCache=null;gaScanStartedAt=null;}

async function boot(){
  if(!TOKEN){showAuth();return}
  try{const u=await jsonFetch(`${API}/auth/me`);showApp(u)}catch{showAuth()}
}

$("#loginTab").onclick=()=>{$("#loginTab").classList.add("active");$("#signupTab").classList.remove("active");$("#emailWrap").classList.add("hidden");$("#authTitle").textContent="تسجيل الدخول";$(".auth-submit").textContent="دخول";AUTH_MODE="login";};
$("#signupTab").onclick=()=>{$("#signupTab").classList.add("active");$("#loginTab").classList.remove("active");$("#emailWrap").classList.remove("hidden");$("#authTitle").textContent="إنشاء حساب";$(".auth-submit").textContent="إنشاء الحساب";AUTH_MODE="signup";};
let AUTH_MODE="login";
$("#authForm").onsubmit=async e=>{
 e.preventDefault();const msg=$("#authMessage");
 try{
  const body={username:$("#authUsername").value.trim(),password:$("#authPassword").value};
  if(AUTH_MODE==="signup")body.email=$("#authEmail").value.trim();
  const d=await jsonFetch(`${API}/auth/${AUTH_MODE==="signup"?"signup":"login"}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  TOKEN=d.access_token;localStorage.setItem("geo_token",TOKEN);msg.style.color="#63df95";msg.textContent="تم تسجيل الدخول بنجاح.";
  const u=await jsonFetch(`${API}/auth/me`);showApp(u);
 }catch(e){msg.style.color="#ff7185";msg.textContent=e.message}
};
$("#logoutBtn").onclick=()=>{resetAnalysisUI();showAuth();};

async function health(){
 try{const h=await jsonFetch(`${API}/health`);$("#apiDot").className="ok";$("#apiStatus").textContent=`Backend ${h.version||"Connected"}`}
 catch{$("#apiDot").className="bad";$("#apiStatus").textContent="Backend Offline"}
}

async function checkEE(){
 try{
  const d=await jsonFetch(`${API}/auth/earth-engine/status`); eeConnected=!!d.connected; eeMode=d.mode||null;
  $("#eeDot").className=eeConnected?"ok":"bad"; $("#eeStatus").textContent=eeConnected?`Earth Engine ${eeMode==="local"?"Local":"Connected"}`:"Earth Engine Required";
  $("#startBtn").disabled=!eeConnected;
  if(eeConnected){$("#eeTitle").textContent="Google Earth Engine ✓";$("#eeHint").textContent=eeMode==="local"?"متصل بحساب Earth Engine المحلي لهذا الجهاز (وضع اختبار).":"متصل بحساب Google الخاص بالمستخدم.";$("#eeConnect").textContent="إعادة التحقق";$("#message").textContent="تم الاتصال بـ Earth Engine. يمكنك بدء الفحص."}
  else if(!d.oauth_configured && d.local_dev_available){$("#eeTitle").textContent="Earth Engine — وضع الاختبار المحلي";$("#eeHint").textContent="استخدم اعتماد Earth Engine الموجود على هذا الكمبيوتر للتجربة.";$("#eeConnect").textContent="ربط هذا الجهاز";$("#message").textContent="للاختبار المحلي: اربط Earth Engine الموجود على هذا الكمبيوتر."}
  else{$("#eeTitle").textContent="Google Earth Engine";$("#eeHint").textContent="اربط حساب Google Earth Engine قبل بدء الفحص.";$("#eeConnect").textContent="ربط الحساب";$("#message").textContent="يجب أولًا ربط حساب Google Earth Engine الخاص بك."}
 }catch(e){eeConnected=false;$("#startBtn").disabled=true;$("#eeDot").className="bad";$("#eeStatus").textContent="Earth Engine Error";$("#message").textContent=e.message}
}

$("#eeConnect").addEventListener("click",async()=>{
  const btn=$("#eeConnect");
  if(!btn) return;
  btn.disabled=true;
  const oldText=btn.textContent;
  btn.textContent="جاري الاتصال…";
  $("#message").textContent="جاري الاتصال بـ Google Earth Engine…";

  try{
    // First ask the backend what modes are available.
    const s=await jsonFetch(`${API}/auth/earth-engine/status`);

    if(s.connected){
      await checkEE();
      return;
    }

    // Local development mode: use the Earth Engine credentials already
    // authenticated on this computer. No Google password is entered here.
    if(s.local_dev_available===true){
      $("#message").textContent="جاري اختبار اعتماد Earth Engine المحلي…";
      const d=await jsonFetch(`${API}/auth/earth-engine/local-connect`,{
        method:"POST"
      });
      if(d.connected){
        await checkEE();
        $("#message").textContent="تم الاتصال الحقيقي بـ Earth Engine. يمكنك بدء الفحص.";
        return;
      }
    }

    // Production mode: redirect to the real Google OAuth authorization page.
    if(s.oauth_configured===true){
      const d=await jsonFetch(`${API}/auth/earth-engine/start`);
      if(!d.authorization_url) throw new Error("لم يُرجع الخادم رابط Google OAuth.");
      window.location.assign(d.authorization_url);
      return;
    }

    throw new Error(
      "لم يتم إعداد Google OAuth للتطبيق، ولا يوجد اعتماد Earth Engine محلي صالح على هذا الكمبيوتر. "
      +"للاختبار المحلي نفّذ earthengine authenticate ثم اضغط الزر مرة أخرى."
    );

  }catch(e){
    console.error("Earth Engine connection error:",e);
    $("#eeDot").className="bad";
    $("#eeStatus").textContent="Earth Engine Error";
    $("#message").textContent=e.message||"فشل الاتصال بـ Earth Engine.";
  }finally{
    btn.disabled=false;
    if(!eeConnected) btn.textContent=oldText;
  }
});

function readCoords(){return {lat:Number($("#lat").value),lon:Number($("#lon").value)}}
function updateMap(){
 const {lat,lon}=readCoords(); const radius=Number($("#radius").value); geometryType=$("#geometryType")?.value||geometryType||"circle";
 if(!Number.isFinite(lat)||!Number.isFinite(lon)||lat<-90||lat>90||lon<-180||lon>180)return;
 $("#radiusOut").textContent=`${radius} m`; $("#centre").textContent=`${lat.toFixed(6)}° / ${lon.toFixed(6)}°`;
 if(!map)return;
 if(marker)marker.setLatLng([lat,lon]);else marker=L.marker([lat,lon]).addTo(map);
 if(circle){map.removeLayer(circle);circle=null;}
 if(geometryType==="square"){
   const dlat=radius/111320, dlon=radius/(111320*Math.max(Math.cos(lat*Math.PI/180),.01));
   circle=L.rectangle([[lat-dlat,lon-dlon],[lat+dlat,lon+dlon]],{color:"#006233",fillColor:"#d21034",fillOpacity:.08}).addTo(map);
 }else{
   circle=L.circle([lat,lon],{radius,color:"#006233",fillColor:"#d21034",fillOpacity:.08}).addTo(map);
 }
 syncLayerManager();
}

["#lat","#lon","#radius"].forEach(sel=>$(sel).addEventListener("input",updateMap));
$("#geometryType")?.addEventListener("change",updateMap);
$("#centerMapBtn").onclick=()=>{updateMap();const {lat,lon}=readCoords();if(map)map.setView([lat,lon],18,{animate:true});};
document.querySelectorAll(".scale").forEach(b=>b.onclick=()=>{document.querySelectorAll(".scale").forEach(x=>x.classList.remove("active"));b.classList.add("active");selectedScale=Number(b.dataset.scale)});

function syncLayerManager(){
 document.querySelectorAll('.layer-row').forEach(row=>{
   const key=row.dataset.layer; const on=!!layerState[key];
   row.classList.toggle('active',on);
   const b=row.querySelector('b'); if(b)b.textContent=on?'ON':'OFF';
   row.setAttribute('aria-pressed',String(on));
 });
 if(baseLayers.satellite&&map){
   if(layerState.satellite){
     if(map.hasLayer(baseLayers.street))map.removeLayer(baseLayers.street);
     if(!map.hasLayer(baseLayers.satellite))baseLayers.satellite.addTo(map);
   }else{
     if(map.hasLayer(baseLayers.satellite))map.removeLayer(baseLayers.satellite);
     if(!map.hasLayer(baseLayers.street))baseLayers.street.addTo(map);
   }
 }
 if(map){
   if(layerState.aoi){ marker?.addTo(map); circle?.addTo(map); }
   else { marker&&map.removeLayer(marker); circle&&map.removeLayer(circle); }
 }
 targetLayers.forEach(l=>{if(layerState.targets)l.addTo(map);else map?.removeLayer(l)});
}

function initMap(){
 if(map)return;
 map=L.map("map",{zoomControl:true,preferCanvas:true,worldCopyJump:true,attributionControl:true}).setView([35.367481,7.755425],17);
 const satellite=L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Tiles © Esri"});
 const street=L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,subdomains:["a","b","c"],attribution:"© OpenStreetMap contributors"});
 baseLayers.satellite=satellite;baseLayers.street=street;satellite.addTo(map);
 L.control.layers({"Satellite / Esri":satellite,"Street / OpenStreetMap":street},null,{position:"topright",collapsed:true}).addTo(map);
 map.on("click",e=>{$("#lat").value=e.latlng.lat.toFixed(6);$("#lon").value=e.latlng.lng.toFixed(6);updateMap();});
 const panel=document.querySelector(".map-panel");
 if(window.ResizeObserver&&panel){resizeObserver=new ResizeObserver(()=>map&&map.invalidateSize(true));resizeObserver.observe(panel)}
 window.addEventListener("resize",()=>map&&map.invalidateSize(true));
window.addEventListener("error",function(e){console.error(e.error||e.message);const m=$("#message");if(m)m.textContent="خطأ في الواجهة: "+(e.message||"Unknown error");});
 map.on("baselayerchange",e=>{layerState.satellite=e.layer===baseLayers.satellite;syncLayerManager()});
 // AOI marker/shape are controlled by the Contents manager rather than Leaflet's
 // overlay control, so their visibility has one source of truth: layerState.aoi.

 map.whenReady(()=>{map.invalidateSize(true);updateMap();syncLayerManager()});
}

$("#startBtn").onclick=async()=>{
 if(!TOKEN){showAuth();return} if(!eeConnected){$("#message").textContent="اربط Google Earth Engine أولًا.";return}
 const {lat,lon}=readCoords();const radius=Number($("#radius").value);geometryType=$("#geometryType")?.value||"circle";
 if(!Number.isFinite(lat)||!Number.isFinite(lon)||lat<-90||lat>90||lon<-180||lon>180){$("#message").textContent="الإحداثيات غير صالحة.";return}
 const btn=$("#startBtn");btn.disabled=true;$("#message").textContent="جاري إرسال منطقة الفحص إلى المحرك العلمي…";
 try{
  const aoi=await jsonFetch(`${API}/aoi`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({latitude:lat,longitude:lon,radius_m:radius,scale_m:selectedScale,geometry_type:geometryType})});
  const run=await jsonFetch(`${API}/analysis/start`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({aoi_id:aoi.aoi_id,scale_m:selectedScale,start_date:"2024-01-01",end_date:"2026-01-01",cloud_pct:20})});
  currentAnalysisId=run.analysis_id;gaScanStartedAt=Date.now();setScanStatus("running");poll(run.analysis_id);
 }catch(e){$("#message").textContent=`لم يبدأ الفحص: ${e.message}`;btn.disabled=false}
};

async function poll(id){
 try{
  const s=await jsonFetch(`${API}/analysis/${id}/status`);$("#analysisStatus").textContent=(s.status||"").toUpperCase();$("#stage").textContent=s.stage||"";$("#stageMsg").textContent=s.error||s.message||"Processing…";$("#message").textContent=s.error?`فشل الفحص: ${s.error}`:`الفحص: ${s.stage||s.status}`;
  if(s.status==="completed"){gaScanStartedAt=null;await loadResults(id);try{const rep=await jsonFetch(`${API}/reports/${id}`);const md=rep.metadata||{};setScanStatus("completed",{duration_seconds:md.duration_seconds,sample_count:md.sample_count,observation_count:md.observation_count});}catch(e){setScanStatus("completed")}$("#startBtn").disabled=false;$("#reportBtn").disabled=false;return}
  if(s.status==="failed"){gaScanStartedAt=null;setScanStatus("failed");$("#startBtn").disabled=false;return}
  setTimeout(()=>poll(id),1200);
 }catch(e){$("#message").textContent=`خطأ في حالة الفحص: ${e.message}`;$("#startBtn").disabled=false}
}

async function loadResults(id){
 const d=await jsonFetch(`${API}/analysis/${id}/datasets`); $("#datasets").innerHTML=d.datasets.length?d.datasets.map(x=>`<div class="target"><b>${esc(x.name)}</b><small>${esc(x.status)} · ${x.scenes!=null?x.scenes+" scenes":(x.resolution_m?x.resolution_m+" m":"—")} · ${esc(x.note||"")}</small></div>`).join(""):"لا توجد بيانات حقيقية.";
 const t=await jsonFetch(`${API}/analysis/${id}/targets`); $("#targets").innerHTML=t.targets.length?t.targets.map(x=>`<button type="button" class="target target-card" data-target-id="${esc(x.target_id)}"><b>${esc(x.target_id)} · ${Number(x.strength_percent??x.anomaly_score*100).toFixed(1)}%</b><small>${esc(x.type_interpretation?.label||"Surface signature")} · ${Number(x.type_interpretation?.fit_percent||0).toFixed(1)}% fit</small><small>${Number(x.estimated_surface_length_m||10).toFixed(1)} × ${Number(x.estimated_surface_width_m||10).toFixed(1)} m · ${esc(x.utm?.label||"—")}</small></button>`).join(""):"لم يتم تحديد أهداف مدعومة علميًا.";
 targetLayers.forEach(l=>map?.removeLayer(l)); targetLayers=[]; const color=s=>{const v=Math.max(0,Math.min(1,Number(s)||0));return v>=.8?"#d21034":v>=.65?"#ff7a00":v>=.5?"#f0c808":"#35b779"}; const bounds=[];
 (t.targets||[]).forEach(x=>{const c=color(x.anomaly_score),lat=x.latitude,lon=x.longitude,length=Number(x.estimated_surface_length_m||x.box_size_m||10),width=Number(x.estimated_surface_width_m||x.box_size_m||10),dlat=(width/2)/111320,dlon=(length/2)/(111320*Math.max(Math.cos(lat*Math.PI/180),.01)); const r=L.rectangle([[lat-dlat,lon-dlon],[lat+dlat,lon+dlon]],{color:c,weight:3,fillColor:c,fillOpacity:.22}); const m=L.circleMarker([lat,lon],{radius:8,color:"#fff",weight:2,fillColor:c,fillOpacity:.95}); const it=x.type_interpretation||{}; const temporal=Number(x.temporal_disturbance_score||0)*100; const risk=Number(x.surface_artifact_risk||0)*100; const human=Number(x.human_surface_change_signal||0)*100; const pop=`<div class="target-popup"><div class="tp-head"><div><small class="tp-kicker">CANDIDATE ZONE</small><strong>${esc(x.target_id)}</strong></div><span class="tp-score" style="color:${c}">${Number(x.strength_percent||0).toFixed(1)}%</span></div><div class="tp-meter"><i style="width:${Math.min(100,Math.max(0,Number(x.strength_percent||0)))}%;background:${c}"></i></div><div class="tp-grid"><div><small>التفسير</small><b>${esc(it.label||"—")}</b></div><div><small>ملاءمة الفرضية</small><b>${Number(it.fit_percent||0).toFixed(1)}%</b></div><div><small>التغير التاريخي</small><b>${temporal.toFixed(1)}%</b></div><div><small>تغير الغطاء/النشاط السطحي</small><b>${human.toFixed(1)}%</b></div><div><small>مخاطر السطح</small><b>${risk.toFixed(1)}%</b></div><div><small>البصمة</small><b>${Number(x.estimated_surface_length_m||10).toFixed(1)} × ${Number(x.estimated_surface_width_m||10).toFixed(1)} m</b></div></div><div style="margin-top:9px"><b>UTM:</b> ${esc(x.utm?.label||"—")}</div><div><b>العمق:</b> غير مقدّر من بيانات الأقمار الصناعية وحدها</div><div><b>Trace ID:</b> ${esc(x.trace_id||"—")}</div><div class="tp-note">${esc(it.scientific_note||"")}</div></div>`; r.bindPopup(pop);m.bindPopup(pop);if(layerState.targets){r.addTo(map);m.addTo(map)}targetLayers.push(r,m);bounds.push([lat,lon]);}); if(bounds.length)map.fitBounds(bounds,{padding:[60,60],maxZoom:19});
}
async function openReport(){if(!currentAnalysisId)return;try{reportCache=await jsonFetch(`${API}/reports/${currentAnalysisId}`);$("#reportContent").innerHTML=`<div class="report-hero"><span>GEOANOMALY PRO</span><h2>التقرير العلمي الكامل</h2><small>Created by Chaouchi Atef</small></div><div class="report-grid"><div><b>وقت الفحص</b><span>${reportCache.metadata?.duration_seconds??"—"} ثانية</span></div><div><b>العينات الحقيقية</b><span>${reportCache.metadata?.sample_count??"—"}</span></div><div><b>مشاهدات Earth Engine</b><span>${reportCache.metadata?.observation_count??"—"}</span></div><div><b>UTM</b><span>${reportCache.metadata?.centre_utm?.label||"—"}</span></div></div><h3>الأهداف</h3>${(reportCache.targets||[]).map(x=>`<article class="report-target"><div class="rt-title"><b>${esc(x.target_id)}</b><strong>${Number(x.strength_percent||0).toFixed(1)}%</strong></div><p>${esc(x.type_interpretation?.label||"—")} · fit ${Number(x.type_interpretation?.fit_percent||0).toFixed(1)}%</p><p>Surface footprint: ${Number(x.estimated_surface_length_m||10).toFixed(1)} × ${Number(x.estimated_surface_width_m||10).toFixed(1)} m</p><p>UTM: ${esc(x.utm?.label||"—")}</p><p>Evidence: ${esc((x.evidence||[]).join(" · "))}</p><p>Historical change: ${((Number(x.temporal_disturbance_score)||0)*100).toFixed(1)}% · Surface context risk: ${((Number(x.surface_artifact_risk)||0)*100).toFixed(1)}%</p></article>`).join("")||"<p>لا توجد أهداف مدعومة علميًا.</p>"}<div class="report-warning">${(reportCache.limitations||[]).map(x=>`<div>• ${esc(x)}</div>`).join("")}</div><button type="button" id="downloadPdfBtn" class="primary">تحميل PDF</button>`;$("#reportModal").classList.remove("hidden")}catch(e){$("#message").textContent="التقرير غير متاح: "+e.message}}
$("#reportBtn").onclick=openReport;
document.addEventListener("click",async e=>{if(e.target.id==="downloadPdfBtn"&&currentAnalysisId){const r=await fetch(`${API}/reports/${currentAnalysisId}/pdf`,{headers:{Authorization:`Bearer ${TOKEN}`}});if(!r.ok){$("#message").textContent="التقرير PDF غير متاح.";return}const b=await r.blob(),u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download=`GeoAnomalyPro_${currentAnalysisId}.pdf`;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}});
$("#closeReport").onclick=()=>$("#reportModal").classList.add("hidden");
$("#clearBtn").onclick=()=>{targetLayers.forEach(l=>map?.removeLayer(l));targetLayers=[];if(marker){map?.removeLayer(marker);marker=null}if(circle){map?.removeLayer(circle);circle=null}currentAnalysisId=null;reportCache=null;gaScanStartedAt=null;setScanStatus("ready",{duration_seconds:null,sample_count:null,observation_count:null});$("#analysisStatus").textContent="IDLE";$("#stage").textContent="في انتظار الفحص";$("#stageMsg").textContent="تم تنظيف نتيجة الفحص ويمكن بدء فحص جديد.";$("#datasets").textContent="لم يبدأ الفحص.";$("#targets").textContent="لا توجد أهداف.";$("#reportBtn").disabled=true;$("#startBtn").disabled=!eeConnected;updateMap()};
document.querySelectorAll(".nav-item").forEach(btn=>btn.addEventListener("click",()=>{document.querySelectorAll(".nav-item").forEach(x=>x.classList.remove("active"));btn.classList.add("active");const n=btn.dataset.nav;const cp=$(".control-panel"),rp=$(".results-panel");if(n==="aoi"){setPanel(cp,false);setMapFocus(false);cp?.scrollTo({top:0,behavior:"smooth"});return}if(n==="datasets"){setPanel(rp,false);$("#datasets")?.scrollIntoView({behavior:"smooth",block:"center"});return}if(n==="targets"||n==="anomalies"){setPanel(rp,false);$("#targets")?.scrollIntoView({behavior:"smooth",block:"center"});return}if(n==="reports"){if(currentAnalysisId)openReport();else $("#message").textContent="أكمل فحصًا أولًا لعرض التقرير.";return}if(n==="temporal"){setPanel(rp,false);$("#stageMsg").textContent=currentAnalysisId?"تمت مقارنة البصمات السطحية تاريخيًا لكل خلية عند نجاح وحدة Temporal.":"سيظهر التحليل الزمني بعد اكتمال الفحص.";return}if(n==="geology"){setPanel(rp,false);$("#stageMsg").textContent=currentAnalysisId?"الذكاء الجيولوجي يعرض مؤشرات طيفية نسبية، وليس تحديدًا مباشرًا لمعدن.":"سيظهر التحليل الجيولوجي بعد الفحص.";return}if(n==="analysis"){setPanel(rp,false);$("#stageMsg")?.scrollIntoView({behavior:"smooth",block:"center"});return}setMapFocus(false)}));
setInterval(()=>$("#clock").textContent=new Date().toLocaleString(),1000);
boot();




function setMapFocus(enabled){
 const shell=document.querySelector('.app-shell');
 if(!shell)return;
 shell.classList.toggle('map-focus',!!enabled);
 const btn=$('#focusMapTop');
 if(btn)btn.textContent=enabled?'عودة للوحات':'خريطة كاملة';
 setTimeout(()=>map?.invalidateSize?.(true),220);
}

function setPanel(panel,hidden){
 if(!panel)return;
 panel.classList.toggle('panel-hidden',!!hidden);
 setTimeout(()=>map?.invalidateSize?.(true),220);
}

document.addEventListener('DOMContentLoaded',()=>{
 const cp=document.querySelector('.control-panel');
 const rp=document.querySelector('.results-panel');
 $('#closeControl')?.addEventListener('click',()=>setPanel(cp,true));
 $('#closeResults')?.addEventListener('click',()=>setPanel(rp,true));
 $('#openControl')?.addEventListener('click',()=>setPanel(cp,false));
 $('#openResults')?.addEventListener('click',()=>setPanel(rp,false));
 $('#panelToggle')?.addEventListener('click',()=>{
   const hidden=cp?.classList.contains('panel-hidden')&&rp?.classList.contains('panel-hidden');
   setPanel(cp,!hidden); setPanel(rp,!hidden); setMapFocus(!hidden);
 });
 $('#focusMapTop')?.addEventListener('click',()=>{
   const enabled=document.querySelector('.app-shell')?.classList.contains('map-focus');
   setMapFocus(!enabled);
 });
 document.querySelectorAll('.layer-row').forEach(row=>row.addEventListener('click',()=>{const key=row.dataset.layer;layerState[key]=!layerState[key];syncLayerManager()}));
 $('#layerManagerToggle')?.addEventListener('click',()=>{$('#layerManager')?.classList.add('hidden')});
 $('#openLayers')?.addEventListener('click',()=>{$('#layerManager')?.classList.remove('hidden');syncLayerManager()});
 syncLayerManager();
 $('#fitAoiBtn')?.addEventListener('click',()=>{
   if(circle&&map)map.fitBounds(circle.getBounds(),{padding:[50,50],maxZoom:19});
   else if(map)map.setView([Number($('#lat')?.value),Number($('#lon')?.value)],18);
 });
});


document.addEventListener('click',e=>{
 const card=e.target.closest?.('.target-card');
 if(!card)return;
 const id=card.dataset.targetId;
 const layers=targetLayers.filter(x=>x?.getPopup?.());
 const idx=[...document.querySelectorAll('.target-card')].findIndex(x=>x.dataset.targetId===id);
 const pair=layers[idx*2]||layers[idx];
 pair?.openPopup?.();
});
