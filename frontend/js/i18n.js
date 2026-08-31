const I18N={
  en:{
    app:"GeoAnomaly Pro",tag:"GEOSPATIAL INTELLIGENCE",project:"Project",aoi:"Inspection Area",data:"Data Sources",analysis:"Analysis",geo:"Geological Intelligence",anom:"Anomaly Detection",targets:"Targets",temporal:"Temporal Analysis",reports:"Reports",
    area:"AREA OF INTEREST",lat:"Latitude",lon:"Longitude",radius:"Inspection radius",scale:"Investigation scale",updateMap:"Update map",mapHint:"or click directly on the map",location:"Location",crs:"Coordinate system",policy:"Scientific policy",real:"REAL DATA ONLY",connectEE:"Connect Earth Engine",start:"Start Scientific Analysis",clear:"Clear",report:"Scientific Report",waiting:"Define an AOI and connect Earth Engine to begin.",
    datasets:"DATASETS",ranking:"TARGET RANKING",status:"Analysis status",idle:"Waiting for analysis",noRun:"No analysis is running.",noData:"No data yet.",noTargets:"Targets appear only when supported by real backend evidence.",fullMap:"Full map",panels:"Panels",fitAoi:"Fit inspection area",output:"OUTPUTS / REPORTS",layers:"LAYERS",satellite:"Satellite imagery",aoiLayer:"AOI",targetLayer:"Evidence targets",on:"ON",off:"OFF",
    login:"Sign in",signup:"Create account",username:"Username",email:"Email",password:"Password",logout:"Sign out",language:"ع",eeReady:"Earth Engine Ready",eeRequired:"Earth Engine Required",connected:"Connected",realData:"REAL DATA ONLY",pdf:"Download PDF",close:"Close",candidate:"CANDIDATE ZONE",interpretation:"Interpretation",fit:"Hypothesis fit",historical:"Historical change",surfaceChange:"Surface change",surfaceRisk:"Surface-context risk",footprint:"Footprint",depth:"Depth",notEstimated:"Not estimated from satellite data alone"
  },
  ar:{
    app:"GeoAnomaly Pro",tag:"الذكاء الجغرافي المكاني",project:"المشروع",aoi:"منطقة الفحص",data:"مصادر البيانات",analysis:"التحليل",geo:"الذكاء الجيولوجي",anom:"كشف الشذوذ",targets:"الأهداف",temporal:"التحليل الزمني",reports:"التقارير",
    area:"منطقة الاهتمام",lat:"خط العرض",lon:"خط الطول",radius:"نطاق الفحص",scale:"مقياس التحقيق",updateMap:"تحديث الخريطة",mapHint:"أو انقر مباشرة على الخريطة",location:"الموقع",crs:"نظام الإحداثيات",policy:"السياسة العلمية",real:"بيانات حقيقية فقط",connectEE:"ربط Earth Engine",start:"بدء الفحص العلمي",clear:"مسح",report:"التقرير العلمي",waiting:"حدد منطقة الفحص واربط Earth Engine لبدء التحليل.",
    datasets:"مصادر البيانات",ranking:"ترتيب الأهداف",status:"حالة التحليل",idle:"في انتظار الفحص",noRun:"لا توجد عملية تحليل جارية.",noData:"لم يبدأ الفحص.",noTargets:"لا تظهر أهداف إلا بناءً على أدلة حقيقية.",fullMap:"خريطة كاملة",panels:"اللوحات",fitAoi:"إظهار منطقة الفحص",output:"المخرجات / التقارير",layers:"الطبقات",satellite:"المرئيات الفضائية",aoiLayer:"منطقة الفحص",targetLayer:"الأهداف المدعومة بالأدلة",on:"تشغيل",off:"إيقاف",
    login:"تسجيل الدخول",signup:"إنشاء حساب",username:"اسم المستخدم",email:"البريد الإلكتروني",password:"كلمة المرور",logout:"خروج",language:"EN",eeReady:"Earth Engine متصل",eeRequired:"Earth Engine مطلوب",connected:"متصل",realData:"بيانات حقيقية فقط",pdf:"تحميل PDF",close:"إغلاق",candidate:"منطقة مرشحة",interpretation:"التفسير",fit:"ملاءمة الفرضية",historical:"التغير التاريخي",surfaceChange:"التغير السطحي",surfaceRisk:"مخاطر سياق السطح",footprint:"البصمة",depth:"العمق",notEstimated:"لا يُقدّر من بيانات الأقمار الصناعية وحدها"
  }
};
let LANG=localStorage.getItem("geo_lang")||"ar";
function t(k){return (I18N[LANG]&&I18N[LANG][k])||I18N.en[k]||k}
const STATIC_I18N={
  "#authTitle":"login","#authSubtitle":"waiting","#loginTab":"login","#signupTab":"signup","#langBtn":"language","#focusMapTop":"fullMap","#closeControl":"close","#closeResults":"close","#centerMapBtn":"updateMap","#eeConnect":"connectEE","#startBtn":"start","#clearBtn":"clear","#reportBtn":"report","#openControl":"aoi","#openResults":"targets","#closeReport":"close","#downloadPdfBtn":"pdf",
  ".sidebar .nav-item:nth-child(1) span":"project", ".sidebar .nav-item:nth-child(2) span":"aoi", ".sidebar .nav-item:nth-child(3) span":"data", ".sidebar .nav-item:nth-child(4) span":"analysis", ".sidebar .nav-item:nth-child(5) span":"geo", ".sidebar .nav-item:nth-child(6) span":"anom", ".sidebar .nav-item:nth-child(7) span":"targets", ".sidebar .nav-item:nth-child(8) span":"temporal", ".sidebar .nav-item:nth-child(9) span":"reports",
  ".control-panel .panel-head>span":"aoi", ".section-kicker":"area", ".control-panel .coord-actions span":"mapHint", ".aoi-card span:nth-of-type(1)":"location", ".aoi-card span:nth-of-type(2)":"crs", ".aoi-card span:nth-of-type(3)":"policy", ".results-panel .panel-head>span":"status", ".section-title:nth-of-type(1)":"datasets", ".section-title:nth-of-type(2)":"ranking", ".layer-manager .lm-head strong":"layers"
};
function applyLanguage(){
  document.documentElement.lang=LANG; document.documentElement.dir=LANG==="ar"?"rtl":"ltr";
  document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=t(el.dataset.i18n));
  Object.entries(STATIC_I18N).forEach(([sel,key])=>{document.querySelectorAll(sel).forEach(el=>{if(el)el.textContent=t(key)})});
  document.querySelector("#langBtn")?.replaceChildren(document.createTextNode(t("language")));
  document.querySelector("#focusMapTop")?.setAttribute("aria-label",t("fullMap"));
}
function toggleLanguage(){LANG=LANG==="ar"?"en":"ar";localStorage.setItem("geo_lang",LANG);applyLanguage()}
window.toggleLanguage=toggleLanguage;
window.addEventListener("DOMContentLoaded",applyLanguage);
