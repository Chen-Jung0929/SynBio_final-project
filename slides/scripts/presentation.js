/* ========================================================================== 
   KAMI Slide System — route controller + explanatory scientific animations
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const slides = Array.from(document.querySelectorAll(".slide"));
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const indicator = document.getElementById("slide-indicator");
  const progressBar = document.getElementById("progress-bar");
  const toggleMotionBtn = document.getElementById("toggle-motion");
  let currentSlideIndex = 0;
  let isReducedMotion = false;
  let activeTimeouts = [];

  const C = {
    ink: "#1B365D",
    paper: "#f5f4ed",
    grid: "#dedccf",
    mute: "#c5c3b2",
    red: "#8f342d",
    text: "#2c2a29"
  };

  function clearActiveAnimations() {
    activeTimeouts.forEach(clearTimeout);
    activeTimeouts = [];
    if (window.anime) anime.remove("*");
  }

  function updateSlide(index) {
    clearActiveAnimations();
    slides.forEach(slide => slide.classList.remove("active"));
    currentSlideIndex = index;
    slides[currentSlideIndex].classList.add("active");
    indicator.textContent = `Slide ${currentSlideIndex + 1} / ${slides.length}`;
    progressBar.style.width = `${(currentSlideIndex / (slides.length - 1)) * 100}%`;
    prevBtn.disabled = currentSlideIndex === 0;
    nextBtn.disabled = currentSlideIndex === slides.length - 1;
    triggerSlideAnimations(currentSlideIndex + 1);
  }

  function nextSlide() { if (currentSlideIndex < slides.length - 1) updateSlide(currentSlideIndex + 1); }
  function prevSlide() { if (currentSlideIndex > 0) updateSlide(currentSlideIndex - 1); }

  document.addEventListener("keydown", e => {
    if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); nextSlide(); }
    if (e.key === "ArrowLeft") { e.preventDefault(); prevSlide(); }
    if (e.key === "r" || e.key === "R") toggleReducedMotion();
  });
  nextBtn.addEventListener("click", nextSlide);
  prevBtn.addEventListener("click", prevSlide);
  toggleMotionBtn.addEventListener("click", toggleReducedMotion);
  document.querySelectorAll(".replay-btn").forEach(btn => btn.addEventListener("click", e => {
    e.stopPropagation();
    clearActiveAnimations();
    triggerSlideAnimations(currentSlideIndex + 1, true);
  }));

  function toggleReducedMotion() {
    isReducedMotion = !isReducedMotion;
    document.body.classList.toggle("reduced-motion", isReducedMotion);
    toggleMotionBtn.textContent = isReducedMotion ? "Reduced Motion: ON" : "Reduced Motion: OFF";
    updateSlide(currentSlideIndex);
  }

  function triggerSlideAnimations(slideNum) {
    const scenes = {
      4: runScene1,
      6: runScene2,
      7: runVolcanoDerivation,
      8: runMLPrioritization,
      9: runSHAPAttribution,
      10: runSHAPThreshold,
      11: runPairSelection,
      12: runHillModel,
      13: runRandomPairControl,
      14: runThresholdSensitivity,
      15: runExternalValidation
    };
    if (scenes[slideNum]) scenes[slideNum]();
  }

  function resetContainer(id, width = 520, height = 420) {
    const container = document.getElementById(id);
    if (!container) return null;
    container.innerHTML = "";
    return d3.select(container).append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");
  }

  function reveal(selector, delay = 0, duration = 650) {
    const nodes = typeof selector === "string" ? document.querySelectorAll(selector) : selector;
    if (isReducedMotion) {
      d3.selectAll(nodes).style("opacity", 1);
      return;
    }
    activeTimeouts.push(setTimeout(() => {
      anime({ targets: nodes, opacity: [0, 1], translateY: [8, 0], duration, easing: "easeOutQuad", delay: anime.stagger(35) });
    }, delay));
  }

  function label(svg, text, x, y, cls = "step-caption", anchor = "middle") {
    return svg.append("text").attr("x", x).attr("y", y).attr("text-anchor", anchor).attr("class", cls).text(text);
  }

  function arrow(svg, x1, y1, x2, y2, cls = "derive") {
    const id = `arrow-${Math.random().toString(36).slice(2)}`;
    svg.append("defs").append("marker").attr("id", id).attr("viewBox", "0 0 10 10").attr("refX", 8).attr("refY", 5).attr("markerWidth", 5).attr("markerHeight", 5).attr("orient", "auto-start-reverse")
      .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z").attr("fill", C.ink);
    return svg.append("line").attr("class", cls).attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2).attr("stroke", C.ink).attr("stroke-width", 1.3).attr("marker-end", `url(#${id})`).style("opacity", 0);
  }

  function drawAxes(svg, x, y, xLabel, yLabel) {
    svg.append("g").attr("class", "axis").attr("transform", `translate(0,${y.range()[0]})`).call(d3.axisBottom(x).ticks(5));
    svg.append("g").attr("class", "axis").attr("transform", `translate(${x.range()[0]},0)`).call(d3.axisLeft(y).ticks(5));
    label(svg, xLabel, (x.range()[0] + x.range()[1]) / 2, y.range()[0] + 36, "step-caption");
    label(svg, yLabel, -((y.range()[0] + y.range()[1]) / 2), x.range()[0] - 38, "step-caption").attr("transform", "rotate(-90)");
  }

  function drawMiniMatrix(svg, x, y, rows, cols, values, cls = "matrix-demo") {
    const g = svg.append("g").attr("class", cls).attr("transform", `translate(${x},${y})`).style("opacity", 0);
    cols.forEach((c, j) => label(g, c, 58 + j * 36, 0, "matrix-header"));
    rows.forEach((r, i) => label(g, r, 0, 28 + i * 28, "matrix-header", "start"));
    rows.forEach((r, i) => cols.forEach((c, j) => {
      g.append("rect").attr("x", 50 + j * 36).attr("y", 10 + i * 28).attr("width", 30).attr("height", 22).attr("class", "matrix-cell");
      label(g, values[i][j], 65 + j * 36, 25 + i * 28, "svg-note");
    }));
    return g;
  }

  // Existing opening AND-gate teaching slide.
  function runScene1() {
    const svg = resetContainer("scene1-container"); if (!svg) return;
    label(svg, "Single marker overlap becomes separable only after using two inputs", 260, 28, "svg-title");
    const x = d3.scaleLinear().domain([0, 1]).range([70, 460]);
    const y = d3.scaleLinear().domain([0, 1]).range([350, 70]);
    drawAxes(svg, x, y, "Input A expression", "Input B expression");
    const normal = d3.range(18).map((_, i) => ({x: 0.12 + (i % 6) * 0.09, y: 0.08 + Math.floor(i / 6) * 0.12 + (i % 2) * 0.04}));
    const tumor = d3.range(18).map((_, i) => ({x: 0.58 + (i % 6) * 0.06, y: 0.52 + Math.floor(i / 6) * 0.12 + (i % 2) * 0.05}));
    svg.selectAll(".scene1-normal").data(normal).enter().append("circle").attr("class", "scene1-normal").attr("cx", d => x(d.x)).attr("cy", d => y(d.y)).attr("r", 4).attr("fill", C.mute).style("opacity", 0);
    svg.selectAll(".scene1-tumor").data(tumor).enter().append("circle").attr("class", "scene1-tumor").attr("cx", d => x(d.x)).attr("cy", d => y(d.y)).attr("r", 4).attr("fill", C.ink).style("opacity", 0);
    const v = svg.append("line").attr("x1", x(0.58)).attr("x2", x(0.58)).attr("y1", y(0)).attr("y2", y(1)).attr("stroke", C.red).attr("stroke-dasharray", "4 4").style("opacity", 0);
    const h = svg.append("line").attr("x1", x(0)).attr("x2", x(1)).attr("y1", y(0.50)).attr("y2", y(0.50)).attr("stroke", C.red).attr("stroke-dasharray", "4 4").style("opacity", 0);
    svg.append("rect").attr("class", "scene1-on").attr("x", x(0.58)).attr("y", y(1)).attr("width", x(1)-x(0.58)).attr("height", y(0.50)-y(1)).attr("fill", "rgba(27,54,93,.12)").attr("stroke", C.ink).style("opacity", 0);
    label(svg, "ON only when A high AND B high", 365, 105, "step-caption").attr("class", "scene1-on-label step-caption").style("opacity", 0);
    reveal(".scene1-normal,.scene1-tumor", 0); reveal([v.node(), h.node()], 900); reveal(".scene1-on,.scene1-on-label", 1500);
  }

  // Existing high-level pipeline slide.
  const pipelineSteps = ["Data", "DE", "ML", "SHAP", "Threshold", "Pair", "Hill", "Controls", "External"];
  function runScene2() {
    const container = document.getElementById("scene2-container"); if (!container) return;
    container.innerHTML = "";
    pipelineSteps.forEach((step, i) => {
      const n = document.createElement("div"); n.className = "pipeline-node"; n.id = `pipe-step-${i}`; n.innerHTML = `<span class="step-num">${String(i+1).padStart(2,"0")}</span><h4>${step}</h4>`; container.appendChild(n);
      if (i < pipelineSteps.length - 1) { const a = document.createElement("div"); a.className = "pipeline-arrow"; a.textContent = "→"; container.appendChild(a); }
      activeTimeouts.push(setTimeout(() => n.classList.add("active-step", "completed-step"), isReducedMotion ? 0 : i * 350));
    });
    const textCenter = document.querySelector("#slide-6 .text-center");
    if (textCenter) textCenter.innerHTML = "<strong>Logic of revised deck:</strong> every result figure is introduced as raw data → computation → visual mapping → conclusion → limitation.";
  }

  function runVolcanoDerivation() {
    const svg = resetContainer("scene3a-container"); if (!svg) return;
    label(svg, "Volcano derivation", 260, 24, "svg-title");
    const matrix = drawMiniMatrix(svg, 15, 50, ["UBE2S", "CCR6", "GENE3"], ["PDAC1", "PDAC2", "N1", "N2"], [[12, 14, 3, 4], [18, 20, 2, 1], [5, 4, 6, 5]]);
    const calc = svg.append("g").attr("class", "volcano-calc").style("opacity", 0);
    calc.append("rect").attr("x", 210).attr("y", 60).attr("width", 120).attr("height", 92).attr("fill", "rgba(222,220,207,.18)").attr("stroke", C.grid);
    label(calc, "Example gene: UBE2S", 270, 82, "matrix-header");
    label(calc, "mean PDAC = 13", 270, 105, "svg-note");
    label(calc, "mean normal = 3.5", 270, 124, "svg-note");
    label(calc, "log2FC = log2(13/3.5) = 1.9", 270, 143, "svg-note");
    const fdr = svg.append("g").attr("class", "volcano-fdr").style("opacity", 0);
    fdr.append("rect").attr("x", 350).attr("y", 60).attr("width", 135).attr("height", 92).attr("fill", "rgba(222,220,207,.18)").attr("stroke", C.grid);
    label(fdr, "Welch t-test", 418, 85, "matrix-header");
    label(fdr, "p-value → FDR", 418, 110, "svg-note");
    label(fdr, "y = -log10(FDR)", 418, 135, "svg-note");
    arrow(svg, 175, 102, 205, 102); arrow(svg, 330, 102, 348, 102);

    const x = d3.scaleLinear().domain([-3, 9]).range([65, 470]);
    const y = d3.scaleLinear().domain([0, 60]).range([370, 190]);
    drawAxes(svg, x, y, "x-axis = log2FC tumor / normal", "y-axis = -log10 FDR");
    const points = [{x:-1.2,y:6,t:"ns"},{x:.2,y:2,t:"ns"},{x:1.3,y:12,t:"up"},{x:2.0,y:18,t:"up"},{x:3.2,y:30,t:"up"},{x:5.2,y:35,t:"up"},{x:7.3,y:48,t:"up"},{x:8.2,y:42,t:"up"},{x:-.8,y:15,t:"ns"},{x:.5,y:8,t:"ns"}];
    for (let i=0;i<90;i++) points.push({x:-2+Math.random()*10,y:Math.random()*35,t:Math.random()>.55?"up":"ns"});
    const dots = svg.selectAll(".volcano-dot").data(points).enter().append("circle").attr("class","volcano-dot").attr("cx",d=>x(d.x)).attr("cy",d=>y(d.y)).attr("r",2.5).attr("fill",d=>d.t==="up"?"rgba(27,54,93,.45)":C.mute).style("opacity",0);
    const selected = [{x:3.78,y:52,n:"UBE2S"},{x:8.92,y:55,n:"CCR6"}];
    const top = svg.selectAll(".volcano-top").data(selected).enter().append("g").attr("class","volcano-top").style("opacity",0);
    top.append("circle").attr("cx",d=>x(d.x)).attr("cy",d=>y(d.y)).attr("r",6).attr("fill",C.red);
    top.append("text").attr("x",d=>x(d.x)+9).attr("y",d=>y(d.y)+4).text(d=>d.n).attr("fill",C.red).style("font-size","10px").style("font-weight",700);
    reveal([matrix.node()],0); reveal(".derive",700); reveal([calc.node()],950); reveal([fdr.node()],1650); reveal(dots.nodes(),2300); reveal(top.nodes(),3300);
  }

  function runMLPrioritization() {
    const svg = resetContainer("scene3-container"); if (!svg) return;
    label(svg, "Classifier workflow: samples × genes → probability → AUC", 260, 24, "svg-title");
    const g1 = drawMiniMatrix(svg, 25, 55, ["UBE2S", "CCR6", "MMP12"], ["S1", "S2", "S3"], [[12, 18, 9], [3, 2, 1], [14, 20, 8]], "gene-by-sample");
    label(g1, "genes × samples", 105, 115, "step-caption");
    const g2 = drawMiniMatrix(svg, 250, 55, ["S1", "S2", "S3"], ["UBE2S", "CCR6", "label"], [[12,18,1],[3,2,0],[14,20,1]], "sample-by-gene");
    label(g2, "rows=samples, columns=genes; label: PDAC=1 normal=0", 130, 115, "step-caption");
    arrow(svg, 205, 115, 242, 115);
    const split = svg.append("g").attr("class","ml-split").style("opacity",0);
    split.append("rect").attr("x",55).attr("y",230).attr("width",150).attr("height",70).attr("fill","rgba(27,54,93,.06)").attr("stroke",C.ink);
    split.append("rect").attr("x",235).attr("y",230).attr("width",95).attr("height",70).attr("fill","rgba(222,220,207,.35)").attr("stroke",C.grid);
    label(split,"train split: learn helpful genes",130,270,"step-caption"); label(split,"test split",282,270,"step-caption");
    const out = svg.append("g").attr("class","ml-out").style("opacity",0);
    out.append("rect").attr("x",360).attr("y",218).attr("width",115).attr("height",95).attr("fill",C.paper).attr("stroke",C.red);
    label(out,"output",418,244,"matrix-header"); label(out,"P(PDAC)=0.97",418,268,"step-caption"); label(out,"AUC = 1.000",418,292,"step-caption");
    arrow(svg, 205, 265, 235, 265); arrow(svg, 330, 265, 358, 265);
    reveal([g1.node()],0); reveal(".derive",650); reveal([g2.node()],900); reveal([split.node()],1700); reveal([out.node()],2500);
  }

  function runSHAPAttribution() {
    const svg = resetContainer("scene-shap-container"); if (!svg) return;
    label(svg, "SHAP decomposes one prediction", 260, 24, "svg-title");
    const profile = drawMiniMatrix(svg, 25, 65, ["sample T-01"], ["UBE2S", "CCR6", "MMP12", "AC009"], [[0.92,0.81,0.70,0.15]], "shap-profile");
    const pred = svg.append("g").attr("class","shap-pred").style("opacity",0);
    pred.append("rect").attr("x",195).attr("y",67).attr("width",130).attr("height",64).attr("fill","rgba(27,54,93,.06)").attr("stroke",C.ink);
    label(pred,"trained classifier",260,92,"matrix-header"); label(pred,"P(PDAC)=0.94",260,116,"step-caption");
    arrow(svg, 165, 95, 192, 95);
    const feats = [{n:"UBE2S",v:0.42},{n:"CCR6",v:0.35},{n:"MMP12",v:0.18},{n:"AC009",v:-0.22}];
    const x = d3.scaleLinear().domain([-0.5,0.5]).range([95,455]);
    const y = d3.scaleBand().domain(feats.map(d=>d.n)).range([200,345]).padding(.35);
    svg.append("line").attr("class","shap-axis").attr("x1",x(0)).attr("x2",x(0)).attr("y1",185).attr("y2",360).attr("stroke",C.grid).style("opacity",0);
    svg.selectAll(".shap-bar").data(feats).enter().append("rect").attr("class","shap-bar").attr("x",d=>d.v>0?x(0):x(d.v)).attr("y",d=>y(d.n)).attr("height",y.bandwidth()).attr("width",d=>Math.abs(x(d.v)-x(0))).attr("fill",d=>d.v>0?C.ink:C.mute).style("opacity",0);
    svg.selectAll(".shap-label").data(feats).enter().append("text").attr("class","shap-label step-caption").attr("x",d=>d.v>0?x(0)-6:x(0)+6).attr("y",d=>y(d.n)+14).attr("text-anchor",d=>d.v>0?"end":"start").text(d=>`${d.n} ${d.v>0?"pushes PDAC":"pulls normal"}`).style("opacity",0);
    label(svg,"negative SHAP ← normal",160,382,"step-caption"); label(svg,"PDAC → positive SHAP",365,382,"step-caption");
    reveal([profile.node()],0); reveal(".derive",650); reveal([pred.node()],950); reveal(".shap-axis,.shap-bar,.shap-label",1700);
  }

  function runSHAPThreshold() {
    const svg = resetContainer("scene-threshold-container"); if (!svg) return;
    label(svg, "Dependence plot: expression → SHAP value → zero crossing", 260, 24, "svg-title");
    const x = d3.scaleLinear().domain([0,1]).range([70,460]);
    const y = d3.scaleLinear().domain([-0.7,0.7]).range([350,70]);
    drawAxes(svg,x,y,"x-axis = expression","y-axis = SHAP value");
    const data = d3.range(55).map(i => { const xv=i/54; return {x:xv, yv:(xv-.46)*1.55 + Math.sin(i)*.08}; });
    const dots = svg.selectAll(".dep-dot").data(data).enter().append("circle").attr("class","dep-dot").attr("cx",d=>x(d.x)).attr("cy",d=>y(d.yv)).attr("r",3).attr("fill",d=>d.yv>0?C.ink:C.mute).style("opacity",0);
    const zero = svg.append("line").attr("class","dep-zero").attr("x1",x(0)).attr("x2",x(1)).attr("y1",y(0)).attr("y2",y(0)).attr("stroke",C.red).attr("stroke-dasharray","4 4").style("opacity",0);
    const th = svg.append("line").attr("class","dep-th").attr("x1",x(.46)).attr("x2",x(.46)).attr("y1",y(-.7)).attr("y2",y(.7)).attr("stroke",C.ink).style("opacity",0);
    label(svg,"SHAP = 0",415,y(0)-8,"step-caption").attr("class","dep-zero-label step-caption").style("opacity",0);
    label(svg,"threshold K_B ≈ 0.464",x(.46)+52,88,"step-caption").attr("class","dep-th-label step-caption").style("opacity",0);
    reveal(dots.nodes(),0); reveal(".dep-zero,.dep-zero-label",900); reveal(".dep-th,.dep-th-label",1700);
  }

  function pairData() {
    return {
      normal: [{x:.12,y:.05},{x:.20,y:.08},{x:.35,y:.12},{x:.45,y:.18},{x:.55,y:.25},{x:.65,y:.30},{x:.72,y:.45},{x:.82,y:.28},{x:.90,y:.22},{x:.60,y:.38}],
      tumor: [{x:.78,y:.48},{x:.80,y:.52},{x:.82,y:.65},{x:.85,y:.72},{x:.90,y:.80},{x:.95,y:.88},{x:.77,y:.90},{x:.88,y:.95},{x:.92,y:.78},{x:.84,y:.60},{x:.86,y:.85},{x:.96,y:.92}]
    };
  }

  function runPairSelection() {
    const svg = resetContainer("scene4-container"); if (!svg) return;
    label(svg,"Pair scoring → selected scatter",260,24,"svg-title");
    const genes = ["UBE2S","CCR6","MMP12","PKM","S100A6","GRN","CD63","GBA"];
    const cloud = svg.append("g").attr("class","pair-cloud").style("opacity",0);
    genes.forEach((g,i)=>{ cloud.append("circle").attr("cx",55+(i%4)*45).attr("cy",60+Math.floor(i/4)*34).attr("r",12).attr("fill",i<2?C.red:C.mute).attr("opacity",.85); label(cloud,g,55+(i%4)*45,63+Math.floor(i/4)*34,"svg-note"); });
    const score = svg.append("g").attr("class","pair-score").style("opacity",0);
    score.append("rect").attr("x",250).attr("y",48).attr("width",210).attr("height",92).attr("fill","rgba(222,220,207,.18)").attr("stroke",C.grid);
    label(score,"For each pair",355,70,"matrix-header"); label(score,"tumor AND activation = 97.8%",355,94,"svg-note"); label(score,"normal AND activation = 0.6%",355,113,"svg-note"); label(score,"correlation penalty: r = 0.714",355,132,"svg-note");
    arrow(svg, 200, 92, 247, 92);
    const x = d3.scaleLinear().domain([0,1]).range([65,465]), y = d3.scaleLinear().domain([0,1]).range([365,180]);
    drawAxes(svg,x,y,"UBE2S expression","CCR6 expression");
    const {normal,tumor}=pairData();
    svg.selectAll(".pair-n").data(normal).enter().append("circle").attr("class","pair-n").attr("cx",d=>x(d.x)).attr("cy",d=>y(d.y)).attr("r",4).attr("fill",C.mute).style("opacity",0);
    svg.selectAll(".pair-t").data(tumor).enter().append("circle").attr("class","pair-t").attr("cx",d=>x(d.x)).attr("cy",d=>y(d.y)).attr("r",4).attr("fill",C.ink).style("opacity",0);
    const v=svg.append("line").attr("class","pair-line").attr("x1",x(.76)).attr("x2",x(.76)).attr("y1",y(0)).attr("y2",y(1)).attr("stroke",C.red).attr("stroke-dasharray","4 4").style("opacity",0);
    const h=svg.append("line").attr("class","pair-line").attr("x1",x(0)).attr("x2",x(1)).attr("y1",y(.464)).attr("y2",y(.464)).attr("stroke",C.red).attr("stroke-dasharray","4 4").style("opacity",0);
    svg.append("rect").attr("class","pair-on").attr("x",x(.76)).attr("y",y(1)).attr("width",x(1)-x(.76)).attr("height",y(.464)-y(1)).attr("fill","rgba(27,54,93,.14)").attr("stroke",C.ink).style("opacity",0);
    label(svg,"AND ON = UBE2S high AND CCR6 high",335,205,"step-caption").attr("class","pair-on-label step-caption").style("opacity",0);
    reveal([cloud.node()],0); reveal(".derive",700); reveal([score.node()],950); reveal(".pair-n,.pair-t",1700); reveal([v.node(),h.node()],2400); reveal(".pair-on,.pair-on-label",3100);
  }

  function runHillModel() {
    const svg = resetContainer("scene5-container"); if (!svg) return;
    label(svg,"Expression → normalization → Hill responses → multiplication",260,24,"svg-title");
    const raw = svg.append("g").attr("class","hill-raw").style("opacity",0);
    raw.append("rect").attr("x",25).attr("y",55).attr("width",120).attr("height",78).attr("fill","rgba(222,220,207,.18)").attr("stroke",C.grid);
    label(raw,"raw expression",85,78,"matrix-header"); label(raw,"UBE2S = 14.2",85,102,"svg-note"); label(raw,"CCR6 = 20.1",85,122,"svg-note");
    const norm = svg.append("g").attr("class","hill-norm").style("opacity",0);
    norm.append("rect").attr("x",180).attr("y",55).attr("width",120).attr("height",78).attr("fill","rgba(222,220,207,.18)").attr("stroke",C.grid);
    label(norm,"min-max scale",240,78,"matrix-header"); label(norm,"A = 0.90",240,102,"svg-note"); label(norm,"B = 0.82",240,122,"svg-note");
    const mult = svg.append("g").attr("class","hill-mult").style("opacity",0);
    mult.append("rect").attr("x",335).attr("y",55).attr("width",145).attr("height",78).attr("fill","rgba(27,54,93,.06)").attr("stroke",C.ink);
    label(mult,"H(A) × H(B)",408,86,"matrix-header"); label(mult,"only double-high gives high output",408,113,"svg-note");
    arrow(svg,145,94,178,94); arrow(svg,300,94,333,94);
    const x=d3.scaleLinear().domain([0,1]).range([70,460]), y=d3.scaleLinear().domain([0,1]).range([365,175]);
    drawAxes(svg,x,y,"rescaled UBE2S (A)","rescaled CCR6 (B)");
    const Ka=.76,Kb=.464,n=1, grid=[]; for(let i=0;i<24;i++)for(let j=0;j<24;j++){const a=j/23,b=i/23,ha=a**n/(Ka**n+a**n),hb=b**n/(Kb**n+b**n);grid.push({a,b,o:ha*hb});}
    const col=d3.scaleLinear().domain([0,.1,.25,.5]).range([C.paper,"#dce2e8","#a6b9cd",C.ink]);
    svg.selectAll(".heatmap-cell").data(grid).enter().append("rect").attr("class","heatmap-cell").attr("x",d=>x(d.a)).attr("y",d=>y(d.b)-8).attr("width",17).attr("height",8.5).attr("fill",d=>col(d.o)).style("opacity",0);
    reveal([raw.node()],0); reveal(".derive",650); reveal([norm.node()],900); reveal([mult.node()],1600); reveal(".heatmap-cell",2300);
  }

  function runRandomPairControl() {
    const svg = resetContainer("scene-random-container"); if (!svg) return;
    label(svg,"Random pairs build a background distribution",260,24,"svg-title");
    const pool = svg.append("g").attr("class","random-pool").style("opacity",0);
    d3.range(32).forEach(i=>pool.append("circle").attr("cx",35+(i%8)*22).attr("cy",58+Math.floor(i/8)*22).attr("r",6).attr("fill",i===5||i===18?C.red:C.mute).attr("opacity",.8));
    label(pool,"58,581 filtered genes",115,160,"step-caption");
    const pipe=svg.append("g").attr("class","random-pipe").style("opacity",0);
    pipe.append("rect").attr("x",220).attr("y",62).attr("width",95).attr("height",42).attr("fill",C.paper).attr("stroke",C.grid); label(pipe,"random pair",267,88,"svg-note");
    pipe.append("rect").attr("x",220).attr("y",122).attr("width",95).attr("height",42).attr("fill",C.paper).attr("stroke",C.grid); label(pipe,"same AND gate",267,148,"svg-note");
    pipe.append("rect").attr("x",220).attr("y",182).attr("width",95).attr("height",42).attr("fill",C.paper).attr("stroke",C.grid); label(pipe,"compute AUC",267,208,"svg-note");
    label(pipe,"repeat 1,000×",267,248,"matrix-header");
    arrow(svg,180,100,218,82); arrow(svg,268,104,268,120); arrow(svg,268,164,268,180);
    const x=d3.scaleLinear().domain([0.45,1.0]).range([350,490]), y=d3.scaleLinear().domain([0,70]).range([350,80]);
    drawAxes(svg,x,y,"AUC of random gene pairs","frequency");
    const bins=[{x:.50,h:62},{x:.58,h:31},{x:.66,h:18},{x:.74,h:10},{x:.82,h:4},{x:.90,h:1}];
    svg.selectAll(".rand-bin").data(bins).enter().append("rect").attr("class","rand-bin").attr("x",d=>x(d.x)).attr("y",d=>y(d.h)).attr("width",20).attr("height",d=>350-y(d.h)).attr("fill",C.mute).style("opacity",0);
    const line=svg.append("line").attr("class","rand-line").attr("x1",x(.9986)).attr("x2",x(.9986)).attr("y1",y(0)).attr("y2",y(68)).attr("stroke",C.red).attr("stroke-width",2).style("opacity",0);
    label(svg,"UBE2S + CCR6 AUC = 0.9986",416,68,"step-caption").attr("class","rand-line-label step-caption").style("opacity",0);
    label(svg,"Empirical p < 0.0001",416,52,"matrix-header").attr("class","rand-line-label matrix-header").style("opacity",0);
    reveal([pool.node()],0); reveal(".derive",650); reveal([pipe.node()],950); reveal(".rand-bin",1800); reveal(".rand-line,.rand-line-label",2600);
  }

  function runThresholdSensitivity() {
    const svg = resetContainer("scene-sensitivity-container"); if (!svg) return;
    label(svg,"Perturb K_A and K_B, recompute output and metrics",260,24,"svg-title");
    const eq=svg.append("g").attr("class","sens-eq").style("opacity",0);
    eq.append("rect").attr("x",30).attr("y",55).attr("width",180).attr("height",78).attr("fill","rgba(222,220,207,.18)").attr("stroke",C.grid);
    label(eq,"H(X)=Xⁿ/(K_Xⁿ+Xⁿ)",120,85,"matrix-header"); label(eq,"highlight K_A and K_B",120,112,"svg-note");
    const slider=svg.append("g").attr("class","sens-slider").style("opacity",0);
    [-50,-25,-10,0,10,25,50].forEach((v,i)=>{ const x=55+i*24; slider.append("line").attr("x1",x).attr("x2",x).attr("y1",170).attr("y2",182).attr("stroke",v===0?C.red:C.grid); label(slider,String(v)+"%",x,198,"svg-note"); });
    label(slider,"K_A and K_B perturbation",130,160,"step-caption");
    const vals=[-50,-25,-10,0,10,25,50]; const data=[]; vals.forEach((a,i)=>vals.forEach((b,j)=>data.push({a,b,auc:.9978+(.001-Math.abs(i-3)*.00008-Math.abs(j-3)*.00005),acc:.86+(6-Math.abs(i-3)-Math.abs(j-3))*.02})));
    const gx=d3.scaleBand().domain(vals).range([270,490]).padding(.05), gy=d3.scaleBand().domain(vals).range([350,130]).padding(.05);
    const color=d3.scaleLinear().domain([.994, .999]).range(["#dce2e8", C.ink]);
    svg.selectAll(".sens-cell").data(data).enter().append("rect").attr("class","sens-cell").attr("x",d=>gx(d.b)).attr("y",d=>gy(d.a)).attr("width",gx.bandwidth()).attr("height",gy.bandwidth()).attr("fill",d=>color(d.auc)).style("opacity",0);
    label(svg,"columns = K_B perturbation",380,375,"step-caption"); label(svg,"rows = K_A perturbation",238,230,"step-caption").attr("transform","rotate(-90 238 230)");
    label(svg,"AUC remains > 0.994 across perturbations",380,108,"matrix-header").attr("class","sens-note matrix-header").style("opacity",0);
    label(svg,"Accuracy is more threshold-dependent than AUC.",130,245,"step-caption").attr("class","sens-note step-caption").style("opacity",0);
    reveal([eq.node()],0); reveal([slider.node()],850); reveal(".sens-cell",1600); reveal(".sens-note",2500);
  }

  function runExternalValidation() {
    const svg = resetContainer("scene6-container"); if (!svg) return;
    label(svg,"Threshold transfer from RNA-seq to microarray",260,24,"svg-title");
    const left=svg.append("g").attr("class","val-left").style("opacity",0), right=svg.append("g").attr("class","val-right").style("opacity",0);
    left.append("rect").attr("x",35).attr("y",55).attr("width",180).attr("height",118).attr("fill","rgba(27,54,93,.06)").attr("stroke",C.ink);
    label(left,"Discovery cohort",125,80,"matrix-header"); label(left,"RNA-seq TCGA/GTEx",125,105,"step-caption"); label(left,"AUC 0.9986",125,128,"svg-note"); label(left,"Sensitivity 97.8%",125,148,"svg-note"); label(left,"Specificity 99.4%",125,168,"svg-note");
    right.append("rect").attr("x",305).attr("y",55).attr("width",180).attr("height",118).attr("fill","rgba(222,220,207,.22)").attr("stroke",C.grid);
    label(right,"External cohort",395,80,"matrix-header"); label(right,"Microarray GSE62452",395,105,"step-caption"); label(right,"AUC 0.648",395,128,"svg-note"); label(right,"Sensitivity 4.3%",395,148,"svg-note").attr("fill",C.red); label(right,"Specificity 98.4%",395,168,"svg-note");
    arrow(svg,215,115,303,115);
    label(svg,"RNA-seq thresholds transferred",260,100,"step-caption").attr("class","transfer-label step-caption").style("opacity",0);
    const metrics=[{n:"Specificity",d:99.4,v:98.4},{n:"Sensitivity",d:97.8,v:4.3}];
    const x=d3.scaleBand().domain(metrics.map(d=>d.n)).range([90,440]).padding(.45), y=d3.scaleLinear().domain([0,100]).range([355,215]);
    drawAxes(svg,x,y,"metric","percent");
    svg.selectAll(".disc-bar").data(metrics).enter().append("rect").attr("class","disc-bar").attr("x",d=>x(d.n)).attr("y",d=>y(d.d)).attr("width",36).attr("height",d=>355-y(d.d)).attr("fill",C.ink).style("opacity",0);
    svg.selectAll(".val-bar").data(metrics).enter().append("rect").attr("class","val-bar").attr("x",d=>x(d.n)+42).attr("y",d=>y(d.v)).attr("width",36).attr("height",d=>355-y(d.v)).attr("fill",d=>d.n==="Sensitivity"?C.red:C.mute).style("opacity",0);
    label(svg,"high specificity remains",180,210,"matrix-header").attr("class","val-note matrix-header").style("opacity",0);
    label(svg,"threshold transferability is weak",350,210,"matrix-header").attr("class","val-note matrix-header").style("opacity",0);
    reveal([left.node()],0); reveal(".derive,.transfer-label",700); reveal([right.node()],1000); reveal(".disc-bar,.val-bar",1800); reveal(".val-note",2600);
  }

  updateSlide(0);
});
