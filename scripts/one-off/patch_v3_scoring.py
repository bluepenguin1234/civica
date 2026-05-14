"""
Civica v3 scoring system - patch civica-v5.html with:
  - Updated pillar weights (25/20/20/15/10/7/3)
  - Rank trajectory wired to grade() instead of 'na'
  - PERSONAS + computeBMS + computeTMS + generateBuyerTake
  - BBT tier labels (Hidden Gem / Strong Value / Market Rate / Premium Town / Luxury Market)
  - Persona selector chips in map filter area
  - TMS badge in profile header
  - Honest Buyer Take upgraded to generated 3-sentence summary
  - Methodology page formula pills updated
"""
from pathlib import Path
import re

HTML_FILE = Path(r"C:\Users\Brian\Desktop\Civica\civica-v5.html")
html = HTML_FILE.read_text(encoding="utf-8")
orig_len = len(html)
ok = []
warn = []

def rep(old, new, label):
    global html
    if old in html:
        html = html.replace(old, new, 1)
        ok.append(label)
    else:
        warn.append(f"NOT FOUND: {label}")

def rep_re(pattern, new, label):
    global html
    m = re.search(pattern, html)
    if m:
        html = re.sub(pattern, new, html, count=1)
        ok.append(label)
    else:
        warn.append(f"NOT FOUND (regex): {label}")

# ─────────────────────────────────────────────────────────────
# 1. State object — add persona
# ─────────────────────────────────────────────────────────────
rep(
    "let state={view:'landing',filter:'all',sort:'score',mapFilters:new Set(),compare:new Set(),favs:new Set(JSON.parse(localStorage.getItem('civica_favs')||'[]')),prof:null};",
    "let state={view:'landing',filter:'all',sort:'score',persona:'default',mapFilters:new Set(),compare:new Set(),favs:new Set(JSON.parse(localStorage.getItem('civica_favs')||'[]')),prof:null};",
    "state: add persona"
)

# ─────────────────────────────────────────────────────────────
# 2. Formula comment update
# ─────────────────────────────────────────────────────────────
rep(
    "Weights: Schools 22% · Safety 18% · Taxes 18% · Fiscal Health 18%\n            Economic Vitality 12% · Quality of Life 7% · Climate 5%",
    "Weights v3: Schools 25% · Safety 20% · Fiscal 20% · Taxes 15%\n            Economic 10% · Quality of Life 7% · Climate 3%",
    "formula comment weights"
)

# ─────────────────────────────────────────────────────────────
# 3. grade() — add rank_traj and housing_afford graders
# ─────────────────────────────────────────────────────────────
rep(
    "debt_pc:v=>v<3000?'green':v<6000?'yellow':'red',unemp:v=>v<3.5?'green':v<5.5?'yellow':'red'};",
    "debt_pc:v=>v<3000?'green':v<6000?'yellow':'red',unemp:v=>v<3.5?'green':v<5.5?'yellow':'red',rank_traj:v=>v<=-20?'green':v<=5?'yellow':'red',housing_afford:v=>v<=5?'green':v<=9?'yellow':'red'};",
    "grade(): rank_traj + housing_afford"
)

# ─────────────────────────────────────────────────────────────
# 4. Inject PERSONAS + helper functions before grade()
# ─────────────────────────────────────────────────────────────
INJECT = r'''
/* ═══════════════════════════════
   v3 BUYER PERSONA PROFILES & DERIVED SCORES
═══════════════════════════════ */
const MA_ZHVI = 613049;

const PERSONAS = {
  default:           {label:"Balanced Buyer",    icon:"⚖️",  weights:{schools:.25,safety:.20,fiscal:.20,taxes:.15,econ:.10,qol:.07,climate:.03}},
  schools_first:     {label:"Schools First",     icon:"🎓",  weights:{schools:.40,safety:.20,fiscal:.15,taxes:.12,econ:.08,qol:.03,climate:.02}},
  tax_sensitive:     {label:"Tax Sensitive",     icon:"💰",  weights:{schools:.10,safety:.18,fiscal:.28,taxes:.30,econ:.08,qol:.04,climate:.02}},
  long_term_investor:{label:"Long-Term Investor",icon:"📈",  weights:{schools:.20,safety:.15,fiscal:.20,taxes:.10,econ:.25,qol:.05,climate:.05}},
  first_time_buyer:  {label:"First-Time Buyer",  icon:"🏠",  weights:{schools:.15,safety:.25,fiscal:.18,taxes:.22,econ:.12,qol:.05,climate:.03}},
};

function computeBMS(t, personaKey){
  const pw = (PERSONAS[personaKey]||PERSONAS.default).weights;
  return Math.round(
    (t.p_schools??50)*pw.schools + (t.p_safety??50)*pw.safety +
    (t.p_fiscal??50)*pw.fiscal   + (t.p_taxes??50)*pw.taxes   +
    (t.p_econ??50)*pw.econ       + (t.p_qol??50)*pw.qol       +
    (t.p_climate??50)*pw.climate
  );
}

function computeTMS(t){
  const inputs=[];
  if(t.d_10yr!=null){const v=t.d_10yr;inputs.push({s:v<=-20?95:v<=-5?80:v<=5?60:v<=20?40:v<=50?20:8,w:.30});}
  if(t.inc10yr!=null){const v=t.inc10yr;inputs.push({s:v>=75?100:v>=50?90:v>=30?78:v>=15?60:v>=0?40:20,w:.25});}
  if(t.med_home_val){const pct=(t.med_home_val/MA_ZHVI-1)*100;inputs.push({s:pct>=60?100:pct>=35?85:pct>=10?70:pct>=-10?55:30,w:.20});}
  if(t.pop10yr!=null){const v=t.pop10yr;inputs.push({s:v>=15?100:v>=7?95:v>=3?85:v>=0?70:v>=-5?50:25,w:.15});}
  if(t.crime5yr!=null){const v=t.crime5yr;inputs.push({s:v<=-25?100:v<=-10?88:v<=-2?75:v<=2?60:v<=10?45:v<=25?30:15,w:.10});}
  if(inputs.length<3)return null;
  const tw=inputs.reduce((a,i)=>a+i.w,0);
  return Math.round(inputs.reduce((a,i)=>a+i.s*i.w,0)/tw);
}

function tmsLabel(v){return v>=75?'Rising Town':v>=60?'Steady Growth':v>=45?'Hold Steady':v>=30?'Stagnating':'Declining';}
function tmsColor(v){return v>=75?'#1a8a3c':v>=60?'#0d2d52':v>=45?'#b25a00':v>=30?'#c06a00':'#c0392b';}
function tmsBg(v){return v>=75?'#e4faea':v>=60?'#e8eef6':v>=45?'#fff4e0':v>=30?'#fff0d8':'#fff0ee';}

function generateBuyerTake(t, personaKey){
  const pk = personaKey||'default';
  const pillars=[
    {name:'Schools',score:t.p_schools??50},{name:'Safety',score:t.p_safety??50},
    {name:'Fiscal Health',score:t.p_fiscal??50},{name:'Taxes',score:t.p_taxes??50},
    {name:'Economic Vitality',score:t.p_econ??50},{name:'Quality of Life',score:t.p_qol??50},
    {name:'Climate Risk',score:t.p_climate??50},
  ].sort((a,b)=>b.score-a.score);
  const top=pillars[0].name, top2=pillars[1].name, bot=pillars[pillars.length-1].name;
  const sc=t.score||0;

  // Sentence 1 — Bottom Line
  let s1;
  if(sc>=70) s1=`${t.name} is one of the strongest-scoring towns in Massachusetts — led by <strong>${top}</strong> and <strong>${top2}</strong>.`;
  else if(sc>=60) s1=`${t.name} scores well above average, with particular strength in <strong>${top}</strong>.`;
  else if(sc>=50) s1=`${t.name} is a solid mid-tier option with its best showing in <strong>${top}</strong>.`;
  else if(sc>=40) s1=`${t.name} shows meaningful trade-offs — strongest in <strong>${top}</strong>, weakest in <strong>${bot}</strong>.`;
  else s1=`${t.name} scores in the lower tier statewide, primarily due to challenges in <strong>${bot}</strong>.`;

  // Sentence 2 — Key Trade-Off
  const gScore={green:100,yellow:55,red:15};
  const graded=[
    {label:'Bond Rating',g:grade('bond',t.bond,t)},
    {label:'Free Cash',g:grade('free_cash',t.free_cash,t)},
    {label:'Tax Rate',g:grade('eff_rate',t.eff_rate,t)},
    {label:'School Rank',g:grade('d_rank',t.d_rank,t)},
    {label:'MCAS Math',g:grade('math',t.math,t)},
    {label:'Graduation Rate',g:grade('grad',t.grad,t)},
    {label:'Violent Crime',g:grade('violent',t.violent,t)},
    {label:'Flood Risk',g:grade('flood',t.flood,t)},
    {label:'Elec. Savings',g:grade('elec_save',t.elec_save,t)},
    {label:'Debt Per Capita',g:grade('debt_pc',t.debt_pc,t)},
  ].filter(m=>m.g!=='na').sort((a,b)=>gScore[b.g]-gScore[a.g]);
  let s2='';
  if(graded.length>=2){
    const best=graded[0], worst=graded[graded.length-1];
    const ba=best.g==='green'?'exceptional':'solid';
    const wa=worst.g==='red'?'a concern':'average';
    if(best.g!==worst.g) s2=`<strong>${best.label}</strong> is ${ba}, while <strong>${worst.label}</strong> is ${wa} — the key trade-off to weigh.`;
    else if(best.g==='green') s2=`Multiple metrics are strong here, with <strong>${best.label}</strong> standing out as particularly ${ba}.`;
    else s2=`<strong>${worst.label}</strong> is a concern worth researching before committing.`;
  }

  // Sentence 3 — Persona-specific
  let s3='';
  if(pk==='schools_first'){
    if(t.d_rank&&t.d_rank<=100) s3=`For school-focused families: district #${t.d_rank} of ${t.d_total||351} is among the state's strongest and deserves serious consideration.`;
    else if(t.d_rank&&t.d_rank<=180) s3=`For school-focused families: the district ranks #${t.d_rank} — above average, but schools alone won't be the primary draw here.`;
    else if(t.d_rank) s3=`For school-focused families: district rank #${t.d_rank} is a meaningful concern — research DESE profiles and recent trajectories before deciding.`;
    else s3=`For school-focused families: school ranking data is pending — check DESE district profiles directly.`;
  } else if(pk==='tax_sensitive'){
    if(t.eff_rate!=null&&t.eff_rate<1.0) s3=`For tax-sensitive buyers: at ${t.eff_rate}% effective rate, this is among the lowest tax burdens in the state.`;
    else if(t.med_tax!=null&&t.med_tax<6000) s3=`For tax-sensitive buyers: the $${t.med_tax.toLocaleString()} median tax bill is below the statewide average — favorable for budget-conscious buyers.`;
    else if(t.med_tax!=null&&t.med_tax>9500) s3=`For tax-sensitive buyers: the $${t.med_tax.toLocaleString()} median bill is well above average — confirm the TER justifies that premium before buying.`;
    else s3=`For tax-sensitive buyers: taxes are mid-range — review the TER to ensure you're getting proportional civic quality for what you're paying.`;
  } else if(pk==='long_term_investor'){
    const tms=computeTMS(t);
    if(tms!=null&&tms>=65) s3=`For long-term investors: momentum indicators point <strong>${tmsLabel(tms)}</strong> — income growth, school trajectory, and population trends are all moving in the right direction.`;
    else if(tms!=null&&tms>=45) s3=`For long-term investors: momentum is mixed (${tmsLabel(tms)}) — some indicators are positive but review school trajectory and income trends before a 10-year commitment.`;
    else if(tms!=null) s3=`For long-term investors: momentum is weak (${tmsLabel(tms)}) — multiple trend indicators are declining, warranting extra scrutiny on a long hold.`;
    else s3=`For long-term investors: trajectory data is incomplete; verify school rank trends and income growth directly from DESE and Census before committing.`;
  } else if(pk==='first_time_buyer'){
    if(t.med_home_val!=null&&t.med_inc!=null){
      const ratio=(t.med_home_val/t.med_inc).toFixed(1);
      if(parseFloat(ratio)<=5) s3=`For first-time buyers: at a ${ratio}× price-to-income ratio, ${t.name} is relatively attainable — entry here is reasonable relative to local wages.`;
      else if(parseFloat(ratio)<=8) s3=`For first-time buyers: the ${ratio}× price-to-income ratio is above average — budget carefully and compare to neighboring towns at similar Civica Scores.`;
      else s3=`For first-time buyers: at ${ratio}× income, entry is challenging — consider towns with comparable scores at more accessible price points.`;
    } else s3=`For first-time buyers: research current listing prices against your income — affordability varies significantly within this market.`;
  } else {
    if(sc>=65) s3=`Overall: ${t.name} checks enough boxes that most buyer types will find it near the top of their shortlist.`;
    else if(sc>=50) s3=`Overall: ${t.name} rewards buyers whose priorities align with its strengths — use the buyer profile filters to see how it scores for your situation.`;
    else s3=`Overall: review the pillar breakdown carefully and compare with higher-scoring alternatives nearby before committing.`;
  }

  return {s1,s2,s3};
}

'''

rep(
    "function grade(key,val,t){",
    INJECT + "function grade(key,val,t){",
    "inject PERSONAS + computeBMS + computeTMS + generateBuyerTake"
)

# ─────────────────────────────────────────────────────────────
# 5. Wire rank_trajectory in PILLARS array
# ─────────────────────────────────────────────────────────────
rep(
    "['d_10yr','10-Year Rank Trend',t.d_10yr!=null?(t.d_10yr<0?t.d_10yr+' spots (improving)':'+'+t.d_10yr+' spots'):null,'na']",
    "['d_10yr','10-Year Rank Trend',t.d_10yr!=null?(t.d_10yr<0?Math.abs(t.d_10yr)+' spots (improving)':'+'+t.d_10yr+' spots (slipping)'):null,grade('rank_traj',t.d_10yr,t)]",
    "PILLARS: wire rank_trajectory to grade()"
)

# ─────────────────────────────────────────────────────────────
# 6. Update PILLARS weight display strings in renderProf
# ─────────────────────────────────────────────────────────────
rep('{num:1,icon:"🎓",bg:"#fff4e0",name:"Schools",wt:"22%"',    '{num:1,icon:"🎓",bg:"#fff4e0",name:"Schools",wt:"25%"',    "PILLARS Schools 22%→25%")
rep('{num:2,icon:"🛡️",bg:"#fff0ee",name:"Safety",wt:"18%"',   '{num:2,icon:"🛡️",bg:"#fff0ee",name:"Safety",wt:"20%"',   "PILLARS Safety 18%→20%")
rep('{num:3,icon:"💰",bg:"#e4faea",name:"Taxes",wt:"18%"',      '{num:3,icon:"💰",bg:"#e4faea",name:"Taxes",wt:"15%"',      "PILLARS Taxes 18%→15%")
rep('{num:4,icon:"🏦",bg:"#e8eef6",name:"Fiscal Health",wt:"18%"', '{num:4,icon:"🏦",bg:"#e8eef6",name:"Fiscal Health",wt:"20%"', "PILLARS Fiscal 18%→20%")
rep('{num:5,icon:"📈",bg:"#e4faea",name:"Economic Vitality",wt:"12%"', '{num:5,icon:"📈",bg:"#e4faea",name:"Economic Vitality",wt:"10%"', "PILLARS Econ 12%→10%")
rep('{num:7,icon:"🌿",bg:"#e4faea",name:"Climate Risk",wt:"5%"','{num:7,icon:"🌿",bg:"#e4faea",name:"Climate Risk",wt:"3%"', "PILLARS Climate 5%→3%")

# ─────────────────────────────────────────────────────────────
# 7. Methodology page formula pills
# ─────────────────────────────────────────────────────────────
rep(
    '<div class="formula-pill">🎓 Schools <strong>×22%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">🛡️ Safety <strong>×18%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">💰 Taxes <strong>×18%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">🏦 Fiscal Health <strong>×18%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">📈 Economic Vitality <strong>×12%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">⚡ Quality of Life <strong>×7%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">🌿 Climate Risk <strong>×5%</strong></div>',
    '<div class="formula-pill">🎓 Schools <strong>×25%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">🛡️ Safety <strong>×20%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">🏦 Fiscal Health <strong>×20%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">💰 Taxes <strong>×15%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">📈 Economic Vitality <strong>×10%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">⚡ Quality of Life <strong>×7%</strong></div><span class="formula-plus">+</span>\n        <div class="formula-pill">🌿 Climate Risk <strong>×3%</strong></div>',
    "Methodology formula pills"
)

# ─────────────────────────────────────────────────────────────
# 8. Methodology pillar weight badges — Schools (22%→25%)
# ─────────────────────────────────────────────────────────────
rep(
    '<h3>1. Schools</h3><p>Quality and trajectory of public education</p></div><span class="pillar-wt-badge">22% of score</span>',
    '<h3>1. Schools</h3><p>Quality and trajectory of public education</p></div><span class="pillar-wt-badge">25% of score</span>',
    "Methodology Schools badge 22%→25%"
)
rep(
    '<span>State District Rank (of 351) — 40%</span>',
    '<span>State District Rank (of 351) — 35%</span>',
    "Methodology Schools rank weight 40%→35%"
)
rep(
    '<span>10-Year Rank Trend — 15%</span>',
    '<span>10-Year Rank Trend — 20% (now scored)</span>',
    "Methodology Schools trajectory 15%→20%"
)

# Safety badge (18%→20%) — first occurrence of "18% of score" in methodology pillar cards
rep(
    '<h3>2. Safety</h3><p>Crime rates and 5-year trend</p></div><span class="pillar-wt-badge">18% of score</span>',
    '<h3>2. Safety</h3><p>Crime rates and 5-year trend</p></div><span class="pillar-wt-badge">20% of score</span>',
    "Methodology Safety badge 18%→20%"
)

# Taxes badge (18%→15%)
rep(
    '<h3>3. Taxes</h3><p>What you\'ll actually pay</p></div><span class="pillar-wt-badge">18% of score</span>',
    '<h3>3. Taxes</h3><p>What you\'ll actually pay</p></div><span class="pillar-wt-badge">15% of score</span>',
    "Methodology Taxes badge 18%→15%"
)
rep(
    '<span>Effective Tax Rate — 55%</span>',
    '<span>Effective Tax Rate — 45%</span>',
    "Methodology Taxes rate weight 55%→45%"
)
rep(
    '<span>Tax Burden as % of Household Income — 45%</span>',
    '<span>Tax Burden as % of Household Income — 35%</span>',
    "Methodology Taxes burden weight 45%→35%"
)

# Fiscal Health badge (18%→20%)
rep(
    '<h3>4. Fiscal Health</h3><p>Is the town financially stable?</p></div><span class="pillar-wt-badge">18% of score</span>',
    '<h3>4. Fiscal Health</h3><p>Is the town financially stable?</p></div><span class="pillar-wt-badge">20% of score</span>',
    "Methodology Fiscal badge 18%→20%"
)

# Economic Vitality badge (12%→10%)
rep(
    '<h3>5. Economic Vitality</h3><p>Is the town growing and prosperous?</p></div><span class="pillar-wt-badge">12% of score</span>',
    '<h3>5. Economic Vitality</h3><p>Is the town growing and prosperous?</p></div><span class="pillar-wt-badge">10% of score</span>',
    "Methodology Econ badge 12%→10%"
)

# Climate Risk badge (5%→3%)
rep(
    '<h3>7. Climate Risk</h3><p>Long-term exposure to flood and fire</p></div><span class="pillar-wt-badge">5% of score</span>',
    '<h3>7. Climate Risk</h3><p>Long-term exposure to flood and fire</p></div><span class="pillar-wt-badge">3% of score</span>',
    "Methodology Climate badge 5%→3%"
)

# ─────────────────────────────────────────────────────────────
# 9. Persona selector chips — add above map filter pills
# ─────────────────────────────────────────────────────────────
PERSONA_SELECTOR = '''<div style="padding:10px 0 6px;border-bottom:1px solid var(--border);margin-bottom:10px">
          <div style="font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#98989d;margin-bottom:7px">Who are you buying for?</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px" id="persona-chips">
            <button class="persona-chip active" data-persona="default" onclick="setPersona('default',this)">⚖️ Balanced</button>
            <button class="persona-chip" data-persona="schools_first" onclick="setPersona('schools_first',this)">🎓 Schools First</button>
            <button class="persona-chip" data-persona="tax_sensitive" onclick="setPersona('tax_sensitive',this)">💰 Tax Sensitive</button>
            <button class="persona-chip" data-persona="long_term_investor" onclick="setPersona('long_term_investor',this)">📈 Long-Term Investor</button>
            <button class="persona-chip" data-persona="first_time_buyer" onclick="setPersona('first_time_buyer',this)">🏠 First-Time Buyer</button>
          </div>
        </div>
        '''
rep(
    '<div class="map-filter-pills" id="map-filter-pills">',
    PERSONA_SELECTOR + '<div class="map-filter-pills" id="map-filter-pills">',
    "persona selector chips before filter pills"
)

# ─────────────────────────────────────────────────────────────
# 10. Add persona-chip CSS before </style>
# ─────────────────────────────────────────────────────────────
PERSONA_CSS = """.persona-chip{padding:5px 12px;border-radius:20px;border:1.5px solid var(--border-mid);background:#fff;font-size:.73rem;font-weight:600;color:var(--sec);cursor:pointer;transition:all .15s;font-family:inherit}
.persona-chip:hover{border-color:var(--blue);color:var(--blue);background:#f0f6ff}
.persona-chip.active{background:var(--blue);color:#fff;border-color:var(--blue)}
.bbt-badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.62rem;font-weight:700;background:#e4faea;color:#1a8a3c}
.bbt-badge.sv{background:#e8eef6;color:#0d2d52}
.bbt-badge.mr{background:#f5f5f7;color:#525252}
.bbt-badge.pt{background:#fff4e0;color:#b25a00}
.bbt-badge.lm{background:#fff0ee;color:#c0392b}
.tms-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 11px;border-radius:20px;font-size:.7rem;font-weight:700;margin-top:6px}
.match-score{font-size:.65rem;font-weight:700;color:var(--blue);background:#f0f6ff;padding:2px 8px;border-radius:10px;margin-top:2px;display:inline-block}
"""
rep("</style>", PERSONA_CSS + "</style>", "persona/TMS/BBT CSS")

# ─────────────────────────────────────────────────────────────
# 11. Add setPersona function near setFilter
# ─────────────────────────────────────────────────────────────
SET_PERSONA_FN = """
function setPersona(pk, btn){
  state.persona=pk;
  document.querySelectorAll('.persona-chip').forEach(c=>c.classList.remove('active'));
  btn.classList.add('active');
  // If not default, switch sort to BMS
  if(pk!=='default') state.sort='bms';
  else if(state.sort==='bms') state.sort='score';
  renderGrid();
  renderMapMarkers();
}
"""
rep(
    "function setFilter(f,btn){",
    SET_PERSONA_FN + "function setFilter(f,btn){",
    "setPersona function"
)

# ─────────────────────────────────────────────────────────────
# 12. Add 'bms' sort option to filteredTowns sort
# ─────────────────────────────────────────────────────────────
rep(
    "if(state.sort==='score') return b.score-a.score;\n    if(state.sort==='ter') return b.ter-a.ter;\n    if(state.sort==='schools') return(a.d_rank||999)-(b.d_rank||999);\n    if(state.sort==='tax') return(a.med_tax||999999)-(b.med_tax||999999);\n    if(state.sort==='name') return a.name.localeCompare(b.name);",
    "if(state.sort==='score') return b.score-a.score;\n    if(state.sort==='ter') return b.ter-a.ter;\n    if(state.sort==='bms') return computeBMS(b,state.persona)-computeBMS(a,state.persona);\n    if(state.sort==='schools') return(a.d_rank||999)-(b.d_rank||999);\n    if(state.sort==='tax') return(a.med_tax||999999)-(b.med_tax||999999);\n    if(state.sort==='name') return a.name.localeCompare(b.name);",
    "add bms sort to filteredTowns"
)

# ─────────────────────────────────────────────────────────────
# 13. Add BBT badge and Match Score to card grid
# ─────────────────────────────────────────────────────────────
OLD_CARD_SCORE = """      <div class="card-top">
          <div><div class="card-name">${t.name}</div><div class="card-sub">${t.county} County · Pop. ${t.pop.toLocaleString()}</div></div>
          <div style="text-align:right"><div class="score-badge" style="color:${col};text-shadow:0 0 18px ${col}">${t.score}</div><div class="score-sub">Civica<br>Score</div></div>
        </div>"""
NEW_CARD_SCORE = """      <div class="card-top">
          <div><div class="card-name">${t.name}</div><div class="card-sub">${t.county} County · Pop. ${t.pop.toLocaleString()}</div>${state.persona!=='default'?`<div class="match-score">Match: ${computeBMS(t,state.persona)}</div>`:''}</div>
          <div style="text-align:right"><div class="score-badge" style="color:${col};text-shadow:0 0 18px ${col}">${state.persona!=='default'?computeBMS(t,state.persona):t.score}</div><div class="score-sub">${state.persona!=='default'?PERSONAS[state.persona].label.split(' ')[0]+'<br>Match':'Civica<br>Score'}</div></div>
        </div>"""
rep(OLD_CARD_SCORE, NEW_CARD_SCORE, "card: add match score display")

# Add BBT badge to card stats
rep(
    "<div class=\"stat-item\"><div class=\"sv\">${t.ter} <span style=\"font-size:.67rem;font-weight:400;color:var(--sec)\">${t.ter_r}</span></div><div class=\"sk\">TER</div></div>",
    "<div class=\"stat-item\"><div class=\"sv\">${t.ter} <span style=\"font-size:.67rem;font-weight:400;color:var(--sec)\">${t.ter_r}</span></div><div class=\"sk\">TER</div></div>\n          <div class=\"stat-item\"><div class=\"sv\" style=\"font-size:.72rem\">${t.value_rating||'—'}</div><div class=\"sk\">Value Tier</div></div>",
    "card: add BBT Value Tier stat"
)

# ─────────────────────────────────────────────────────────────
# 14. Add TMS badge to profile header (next to Civica Score)
# ─────────────────────────────────────────────────────────────
OLD_HEADER_GAUGE = """        <div style="text-align:center;flex-shrink:0">
          ${scoreGauge(t.score,108,true)}
          <div style="font-size:.65rem;opacity:.75;margin-top:2px">Civica Score</div>
        </div>"""
NEW_HEADER_GAUGE = """        <div style="text-align:center;flex-shrink:0">
          ${scoreGauge(t.score,108,true)}
          <div style="font-size:.65rem;opacity:.75;margin-top:2px">Civica Score</div>
          ${(()=>{const tms=computeTMS(t);return tms!=null?`<div class="tms-badge" style="background:${tmsBg(tms)};color:${tmsColor(tms)}">${tmsLabel(tms)} ↑</div>`:''})()}
        </div>"""
rep(OLD_HEADER_GAUGE, NEW_HEADER_GAUGE, "profile header: TMS badge")

# ─────────────────────────────────────────────────────────────
# 15. Upgrade "Honest Buyer Take" to 3-sentence generated summary
# ─────────────────────────────────────────────────────────────
OLD_BUYER_TAKE = """      <!-- Buyer Take -->
      <div class="sec-label">Honest Buyer Take</div>
      <div class="psec open" id="ps${idx}-buy">
        <div class="psec-hdr" onclick="toggleSec('ps${idx}-buy')">
          <div class="psec-icon-wrap" style="background:#f5f5f7">🏡</div>
          <div class="psec-title-wrap"><span class="psec-title">Is ${t.name} right for you?</span></div>
          <span class="psec-wt">Summary</span><span class="psec-chev">▼</span>
        </div>
        <div class="psec-body">
          <div class="buyer-grid">
            <div class="buyer-col gc"><h4>Strong fit if…</h4><ul class="buyer-list">${good.map(s=>`<li>${s}</li>`).join('')}</ul></div>
            <div class="buyer-col bc"><h4>Reconsider if…</h4><ul class="buyer-list">${bad.map(s=>`<li>${s}</li>`).join('')}</ul></div>
          </div>
        </div>
      </div>"""
NEW_BUYER_TAKE = """      <!-- Buyer Take -->
      <div class="sec-label">Honest Buyer Take</div>
      <div class="psec open" id="ps${idx}-buy">
        <div class="psec-hdr" onclick="toggleSec('ps${idx}-buy')">
          <div class="psec-icon-wrap" style="background:#f5f5f7">🏡</div>
          <div class="psec-title-wrap"><span class="psec-title">Is ${t.name} right for you?</span></div>
          <span class="psec-wt">${state.persona!=='default'?PERSONAS[state.persona].label:'Balanced'}</span><span class="psec-chev">▼</span>
        </div>
        <div class="psec-body">
          ${(()=>{const bt=generateBuyerTake(t,state.persona);return`
          <div style="font-size:.87rem;line-height:1.7;color:#1d1d1f;padding:2px 0 10px">
            <p style="margin:0 0 8px">${bt.s1}</p>
            ${bt.s2?`<p style="margin:0 0 8px;color:#374151">${bt.s2}</p>`:''}
            <p style="margin:0;padding:10px;background:#f0f6ff;border-left:3px solid var(--blue);border-radius:0 6px 6px 0;font-size:.83rem;color:#1d4ed8">${bt.s3}</p>
          </div>
          <details style="margin-top:8px">
            <summary style="font-size:.72rem;font-weight:600;color:var(--sec);cursor:pointer;padding:6px 0">Full breakdown ▾</summary>
            <div class="buyer-grid" style="margin-top:8px">
              <div class="buyer-col gc"><h4>Strong fit if…</h4><ul class="buyer-list">${good.map(s=>`<li>${s}</li>`).join('')}</ul></div>
              <div class="buyer-col bc"><h4>Reconsider if…</h4><ul class="buyer-list">${bad.map(s=>`<li>${s}</li>`).join('')}</ul></div>
            </div>
          </details>
          `})()}
        </div>
      </div>"""
rep(OLD_BUYER_TAKE, NEW_BUYER_TAKE, "Honest Buyer Take: 3-sentence generated summary")

# ─────────────────────────────────────────────────────────────
# Print results
# ─────────────────────────────────────────────────────────────
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("\nApplied changes: " + str(len(ok)))
for o in ok:
    print(f"  OK: {o.encode('ascii', errors='replace').decode()}")
if warn:
    print("\nNOT FOUND:")
    for w in warn:
        print(f"  WARN: {w.encode('ascii', errors='replace').decode()}")

print(f"\nOriginal size: {orig_len} chars -> New size: {len(html)} chars (+{len(html)-orig_len})")

HTML_FILE.write_text(html, encoding="utf-8")
print("civica-v5.html written successfully")
