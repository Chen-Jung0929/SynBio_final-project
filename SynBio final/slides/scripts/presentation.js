/* ==========================================================================
   KAMI Slide System — Custom Script & Animation Engine
   Handles slide routing, keyboard events, and scientific animations
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {

  // ==========================================
  // 1. Presentation State & Controller
  // ==========================================
  const slides = document.querySelectorAll(".slide");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const indicator = document.getElementById("slide-indicator");
  const progressBar = document.getElementById("progress-bar");
  const toggleMotionBtn = document.getElementById("toggle-motion");
  
  let currentSlideIndex = 0;
  let isReducedMotion = false;
  let activeTimelines = []; // Track active Anime.js timelines for cleaning
  let activeTimeouts = [];  // Track active setTimeout calls for cleaning

  // Clear running animation states
  function clearActiveAnimations() {
    activeTimelines.forEach(tl => {
      if (tl) tl.pause();
    });
    activeTimelines = [];
    activeTimeouts.forEach(t => clearTimeout(t));
    activeTimeouts = [];
  }

  function updateSlide(index) {
    clearActiveAnimations();
    
    // Remove active class from all slides
    slides.forEach(slide => slide.classList.remove("active"));
    
    // Update active slide
    currentSlideIndex = index;
    slides[currentSlideIndex].classList.add("active");
    
    // Update controls UI
    indicator.textContent = `Slide ${currentSlideIndex + 1} / ${slides.length}`;
    const progressPercent = ((currentSlideIndex) / (slides.length - 1)) * 100;
    progressBar.style.width = `${progressPercent}%`;
    
    // Enable/disable buttons
    prevBtn.disabled = currentSlideIndex === 0;
    nextBtn.disabled = currentSlideIndex === slides.length - 1;
    
    // Trigger animations for the active slide
    triggerSlideAnimations(currentSlideIndex + 1);
  }

  function nextSlide() {
    if (currentSlideIndex < slides.length - 1) {
      updateSlide(currentSlideIndex + 1);
    }
  }

  function prevSlide() {
    if (currentSlideIndex > 0) {
      updateSlide(currentSlideIndex - 1);
    }
  }

  // Key Bindings
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === "Space") {
      e.preventDefault();
      nextSlide();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      prevSlide();
    } else if (e.key === "r" || e.key === "R") {
      toggleReducedMotion();
    }
  });

  // Click Bindings
  nextBtn.addEventListener("click", nextSlide);
  prevBtn.addEventListener("click", prevSlide);

  // Reduced Motion Controller
  function toggleReducedMotion() {
    isReducedMotion = !isReducedMotion;
    if (isReducedMotion) {
      document.body.classList.add("reduced-motion");
      toggleMotionBtn.textContent = "Reduced Motion: ON";
    } else {
      document.body.classList.remove("reduced-motion");
      toggleMotionBtn.textContent = "Reduced Motion: OFF";
    }
    // Re-render active slide to reflect state change
    updateSlide(currentSlideIndex);
  }

  toggleMotionBtn.addEventListener("click", toggleMotionBtnClick);
  function toggleMotionBtnClick() {
    toggleReducedMotion();
  }

  // Replay Animation Triggers
  document.querySelectorAll(".replay-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      triggerSlideAnimations(currentSlideIndex + 1, true);
    });
  });


  // ==========================================
  // 2. Explanatory Animation Implementations
  // ==========================================

  function triggerSlideAnimations(slideNum, forceReplay = false) {
    switch (slideNum) {
      case 4: // Scene 1 — Why AND Gate?
        runScene1();
        break;
      case 6: // Scene 2 — Computational Pipeline Flow
        runScene2();
        break;
      case 7: // Slide 7 — Volcano Plot (Static/Interactive)
        runScene3a();
        break;
      case 8: // Scene 3 — Machine Learning & SHAP
        runScene3();
        break;
      case 9: // Scene 4 — Selection & Orthogonality
        runScene4();
        break;
      case 10: // Scene 5 — Hill-Equation contour heatmap
        runScene5();
        break;
      case 11: // Scene 6 — Validation Metrics Comparison
        runScene6();
        break;
      default:
        // No animations on other slides
        break;
    }
  }

  // Helper: Clear container and create SVG
  function resetContainer(id, width = 500, height = 400) {
    const container = document.getElementById(id);
    if (!container) return null;
    container.innerHTML = "";
    const svg = d3.select(`#${id}`)
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");
    return svg;
  }


  // ----------------------------------------------------
  // Scene 1 — Why AND Gate? (Ambiguity to 2D logic)
  // ----------------------------------------------------
  function runScene1() {
    const width = 500;
    const height = 400;
    const svg = resetContainer("scene1-container", width, height);
    if (!svg) return;

    // Normal samples (brown/gray) and Tumor samples (ink-blue)
    const normalPoints = [
      {x: 100, y: 320}, {x: 120, y: 310}, {x: 140, y: 290}, {x: 150, y: 330},
      {x: 160, y: 280}, {x: 180, y: 300}, {x: 190, y: 260}, {x: 210, y: 290},
      {x: 230, y: 270}, {x: 250, y: 310}, {x: 130, y: 200}, {x: 160, y: 210},
      {x: 110, y: 150}, {x: 150, y: 180}, {x: 170, y: 160}, {x: 180, y: 190}
    ];

    const tumorPoints = [
      {x: 300, y: 100}, {x: 320, y: 90}, {x: 340, y: 120}, {x: 350, y: 80},
      {x: 360, y: 110}, {x: 380, y: 70}, {x: 390, y: 130}, {x: 410, y: 90},
      {x: 430, y: 100}, {x: 450, y: 120}, {x: 280, y: 220}, {x: 260, y: 240},
      {x: 330, y: 230}, {x: 310, y: 250}, {x: 290, y: 270}, {x: 340, y: 210}
    ];

    // Axis scales
    const xScale = d3.scaleLinear().domain([0, 500]).range([50, 450]);
    const yScale = d3.scaleLinear().domain([0, 400]).range([350, 50]);

    // Grid layout
    svg.append("g")
      .attr("transform", "translate(0, 350)")
      .call(d3.axisBottom(xScale).ticks(5).tickFormat(""))
      .attr("class", "axis");
    svg.append("g")
      .attr("transform", "translate(50, 0)")
      .call(d3.axisLeft(yScale).ticks(5).tickFormat(""))
      .attr("class", "axis");

    // Labels
    svg.append("text")
      .attr("x", 250)
      .attr("y", 385)
      .attr("text-anchor", "middle")
      .text("Gene A Expression (Min-Max Scaled)")
      .style("font-size", "11px");

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -200)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .text("Gene B Expression (Min-Max Scaled)")
      .style("font-size", "11px");

    // Legend
    const legend = svg.append("g").attr("transform", "translate(300, 30)");
    legend.append("circle").attr("cx", 0).attr("cy", 0).attr("r", 5).attr("fill", "#c5c3b2");
    legend.append("text").attr("x", 12).attr("y", 4).text("Normal (GTEx)").style("font-size", "11px");
    legend.append("circle").attr("cx", 0).attr("cy", 20).attr("r", 5).attr("fill", "#1B365D");
    legend.append("text").attr("x", 12).attr("y", 24).text("Tumor (TCGA)").style("font-size", "11px");

    if (isReducedMotion) {
      // Direct render 2D scatter with threshold
      renderPoints();
      drawThresholdBox();
      return;
    }

    // Animation stages
    // 1. Show all points projected on X-axis (1D Gene A representation)
    const normalGroup = svg.selectAll(".normal-pt")
      .data(normalPoints)
      .enter()
      .append("circle")
      .attr("class", "normal-pt")
      .attr("cx", d => xScale(d.x))
      .attr("cy", yScale(0)) // Projected onto bottom axis
      .attr("r", 5)
      .attr("fill", "#c5c3b2")
      .style("opacity", 0);

    const tumorGroup = svg.selectAll(".tumor-pt")
      .data(tumorPoints)
      .enter()
      .append("circle")
      .attr("class", "tumor-pt")
      .attr("cx", d => xScale(d.x))
      .attr("cy", yScale(0))
      .attr("r", 5)
      .attr("fill", "#1B365D")
      .style("opacity", 0);

    // Timeline sequence
    // A. Fade in points on 1D axis
    anime({
      targets: '#scene1-container circle',
      opacity: [0, 0.7],
      delay: anime.stagger(30),
      duration: 800,
      easing: 'easeOutQuad'
    });

    // B. Draw X-axis threshold (1D split marker)
    let thresholdLine1;
    activeTimeouts.push(setTimeout(() => {
      thresholdLine1 = svg.append("line")
        .attr("x1", xScale(240))
        .attr("y1", yScale(0))
        .attr("x2", xScale(240))
        .attr("y2", yScale(400))
        .attr("stroke", "#8f342d")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "4 4")
        .style("opacity", 0);

      anime({
        targets: thresholdLine1.node(),
        opacity: 0.8,
        duration: 500,
        easing: 'easeOutQuad'
      });
    }, 1200));

    // C. Transition points to their 2D layout (Y-axis reveal)
    activeTimeouts.push(setTimeout(() => {
      // Remove X-threshold line during transition to 2D
      if (thresholdLine1) {
        anime({
          targets: thresholdLine1.node(),
          opacity: 0,
          duration: 300,
          complete: () => thresholdLine1.remove()
        });
      }

      normalGroup.transition()
        .duration(1500)
        .attr("cy", d => yScale(d.y));

      tumorGroup.transition()
        .duration(1500)
        .attr("cy", d => yScale(d.y));
    }, 2500));

    // D. Draw 2D AND-gate quadrant threshold box
    activeTimeouts.push(setTimeout(() => {
      drawThresholdBox();
    }, 4200));

    function renderPoints() {
      svg.selectAll(".normal-pt")
        .data(normalPoints)
        .enter()
        .append("circle")
        .attr("cx", d => xScale(d.x))
        .attr("cy", d => yScale(d.y))
        .attr("r", 5)
        .attr("fill", "#c5c3b2")
        .style("opacity", 0.7);

      svg.selectAll(".tumor-pt")
        .data(tumorPoints)
        .enter()
        .append("circle")
        .attr("cx", d => xScale(d.x))
        .attr("cy", d => yScale(d.y))
        .attr("r", 5)
        .attr("fill", "#1B365D")
        .style("opacity", 0.7);
    }

    function drawThresholdBox() {
      // Draw lines at boundaries (x=240, y=200)
      svg.append("line")
        .attr("x1", xScale(240))
        .attr("y1", yScale(0))
        .attr("x2", xScale(240))
        .attr("y2", yScale(400))
        .attr("stroke", "#c5c3b2")
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", "2 2");

      svg.append("line")
        .attr("x1", xScale(0))
        .attr("y1", yScale(200))
        .attr("x2", xScale(500))
        .attr("y2", yScale(200))
        .attr("stroke", "#c5c3b2")
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", "2 2");

      // Color the Double-High quadrant (top right, x > 240, y > 200)
      const rect = svg.append("rect")
        .attr("x", xScale(240))
        .attr("y", yScale(400))
        .attr("width", xScale(500) - xScale(240))
        .attr("height", yScale(200) - yScale(400))
        .attr("fill", "rgba(27, 54, 93, 0.15)")
        .attr("stroke", "#1B365D")
        .attr("stroke-width", 2)
        .style("opacity", 0);

      const label = svg.append("text")
        .attr("x", xScale(370))
        .attr("y", yScale(300))
        .attr("text-anchor", "middle")
        .text("ON Region (Tumor Active)")
        .attr("fill", "#1B365D")
        .style("font-size", "12px")
        .style("font-weight", "600")
        .style("opacity", 0);

      if (isReducedMotion) {
        rect.style("opacity", 1);
        label.style("opacity", 1);
      } else {
        anime({
          targets: [rect.node(), label.node()],
          opacity: 1,
          duration: 800,
          easing: 'easeOutQuad'
        });
      }
    }
  }


  // ----------------------------------------------------
  // Scene 2 — Computational Pipeline Flow
  // ----------------------------------------------------
  const pipelineSteps = [
    { num: "01", name: "Data Fetch", desc: "Combined TCGA (n=178) & GTEx (n=167)" },
    { num: "02", name: "QC Filters", desc: "Low-variance filtering (58,581 features)" },
    { num: "03", name: "Welch's DE", desc: "Welch t-test screen (19,399 candidate genes)" },
    { num: "04", name: "ML Lasso", desc: "L1 Logistic Regression (perfect 1.0 AUC)" },
    { num: "05", name: "SHAP Values", desc: "Explainable AI threshold & logic prioritization" },
    { num: "06", name: "Pair Scoring", desc: "Orthogonality scoring (Pearson score search)" },
    { num: "07", name: "Hill Model", desc: "Simulation: optimal params (UBE2S & CCR6)" },
    { num: "08", name: "Sensitivity", desc: "K parameter sweeps & negative permutation" },
    { num: "09", name: "External Val", desc: "GSE62452 Microarray validation" }
  ];

  let currentPipelineStep = 0;

  function runScene2() {
    const container = document.getElementById("scene2-container");
    if (!container) return;
    container.innerHTML = "";

    currentPipelineStep = 0;

    // Render all elements
    pipelineSteps.forEach((step, idx) => {
      const node = document.createElement("div");
      node.className = "pipeline-node";
      node.id = `pipe-step-${idx}`;
      node.innerHTML = `
        <span class="step-num">${step.num}</span>
        <h4>${step.name}</h4>
      `;
      node.addEventListener("click", () => showPipelineDetails(idx));
      container.appendChild(node);

      if (idx < pipelineSteps.length - 1) {
        const arrow = document.createElement("div");
        arrow.className = "pipeline-arrow";
        arrow.textContent = "→";
        container.appendChild(arrow);
      }
    });

    if (isReducedMotion) {
      // Show everything instantly
      pipelineSteps.forEach((_, idx) => {
        const el = document.getElementById(`pipe-step-${idx}`);
        if (el) el.classList.add("completed-step");
      });
      showPipelineDetails(8);
      return;
    }

    // Slide-in sequence
    runPipelineStepAnimation();
  }

  function runPipelineStepAnimation() {
    if (currentPipelineStep >= pipelineSteps.length) return;

    const el = document.getElementById(`pipe-step-${currentPipelineStep}`);
    if (!el) return;

    el.classList.add("active-step");
    showPipelineDetails(currentPipelineStep);

    anime({
      targets: el,
      scale: [0.9, 1],
      opacity: [0, 1],
      duration: 600,
      easing: 'easeOutQuad',
      complete: () => {
        activeTimeouts.push(setTimeout(() => {
          el.classList.remove("active-step");
          el.classList.add("completed-step");
          currentPipelineStep++;
          runPipelineStepAnimation();
        }, 1500));
      }
    });
  }

  function showPipelineDetails(index) {
    // Highlight selected, un-highlight others
    pipelineSteps.forEach((_, idx) => {
      const el = document.getElementById(`pipe-step-${idx}`);
      if (el) {
        el.classList.remove("active-step");
        if (idx < index) {
          el.classList.add("completed-step");
        } else if (idx === index) {
          el.classList.add("active-step");
        } else {
          el.classList.remove("completed-step");
        }
      }
    });

    // We can show details in the pipeline text label or update a sub-description card
    const step = pipelineSteps[index];
    const textCenter = document.querySelector("#slide-6 .text-center");
    if (textCenter) {
      textCenter.innerHTML = `<strong>Step ${step.num} — ${step.name}:</strong> ${step.desc}`;
    }
  }

  // Bind pipeline flow buttons
  const prevFlowBtn = document.getElementById("prev-flow-btn");
  const nextFlowBtn = document.getElementById("next-flow-btn");

  if (prevFlowBtn) {
    prevFlowBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      clearActiveAnimations();
      let prevIdx = currentPipelineStep - 1;
      if (prevIdx < 0) prevIdx = 0;
      currentPipelineStep = prevIdx;
      showPipelineDetails(prevIdx);
    });
  }

  if (nextFlowBtn) {
    nextFlowBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      clearActiveAnimations();
      let nextIdx = currentPipelineStep + 1;
      if (nextIdx >= pipelineSteps.length) nextIdx = pipelineSteps.length - 1;
      currentPipelineStep = nextIdx;
      showPipelineDetails(nextIdx);
    });
  }


  // ----------------------------------------------------
  // Slide 7 — Volcano Plot (Differential Expression)
  // ----------------------------------------------------
  function runScene3a() {
    const width = 500;
    const height = 400;
    const svg = resetContainer("scene3a-container", width, height);
    if (!svg) return;

    // Standard scales
    const xScale = d3.scaleLinear().domain([-10, 15]).range([50, 450]);
    const yScale = d3.scaleLinear().domain([0, 60]).range([350, 50]);

    // Draw Axes
    svg.append("g")
      .attr("transform", "translate(0, 350)")
      .call(d3.axisBottom(xScale).ticks(5))
      .attr("class", "axis");
    svg.append("g")
      .attr("transform", "translate(50, 0)")
      .call(d3.axisLeft(yScale).ticks(5))
      .attr("class", "axis");

    // Labels
    svg.append("text")
      .attr("x", 250)
      .attr("y", 385)
      .attr("text-anchor", "middle")
      .text("log2 Fold Change (log2FC)")
      .style("font-size", "11px");

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -200)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .text("-log10 FDR Significance")
      .style("font-size", "11px");

    // Generate points representing genes
    const volcanoPoints = [];
    // Downregulated/low significance (Normal)
    for (let i = 0; i < 120; i++) {
      volcanoPoints.push({
        x: (Math.random() - 0.6) * 4,
        y: Math.random() * 15,
        type: "ns"
      });
    }
    // Significant upregulated (Tumor)
    for (let i = 0; i < 80; i++) {
      volcanoPoints.push({
        x: 1 + Math.random() * 8,
        y: 10 + Math.random() * 40,
        type: "up"
      });
    }

    const circles = svg.selectAll(".volcano-dot")
      .data(volcanoPoints)
      .enter()
      .append("circle")
      .attr("class", "volcano-dot")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", 3)
      .attr("fill", d => d.type === "up" ? "rgba(27, 54, 93, 0.4)" : "#c5c3b2")
      .style("opacity", isReducedMotion ? 0.7 : 0);

    // Top Candidates Annotated
    const UBE2S = { x: 3.78, y: 52, label: "UBE2S" };
    const CCR6 = { x: 8.92, y: 55, label: "CCR6" };

    const topPoints = svg.selectAll(".top-dot")
      .data([UBE2S, CCR6])
      .enter()
      .append("g");

    topPoints.append("circle")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", 6)
      .attr("fill", "#8f342d");

    topPoints.append("text")
      .attr("x", d => xScale(d.x) + 10)
      .attr("y", d => yScale(d.y) + 4)
      .text(d => d.label)
      .style("font-size", "11px")
      .style("font-weight", "600")
      .attr("fill", "#8f342d");

    if (isReducedMotion) {
      return;
    }

    // Animate points appearing
    anime({
      targets: '.volcano-dot',
      opacity: 0.7,
      delay: anime.stagger(4),
      duration: 1000,
      easing: 'easeOutQuad'
    });
  }


  // ----------------------------------------------------
  // Scene 3 — Machine Learning & SHAP (Push/Pull bar chart)
  // ----------------------------------------------------
  function runScene3() {
    const width = 500;
    const height = 400;
    const svg = resetContainer("scene3-container", width, height);
    if (!svg) return;

    // Feature attribution data
    const features = [
      { name: "RP11-40C6.2", val: 3.03, rank: 1, type: "push" },
      { name: "AC009065.4", val: -2.12, rank: 2, type: "pull" },
      { name: "MMP12", val: 0.79, rank: 3, type: "push" },
      { name: "MISP", val: 0.54, rank: 4, type: "push" },
      { name: "UBE2SP2", val: -0.48, rank: 5, type: "pull" }
    ];

    const xScale = d3.scaleLinear().domain([-3.5, 3.5]).range([50, 450]);
    const yScale = d3.scaleBand().domain(features.map(f => f.name)).range([80, 320]).padding(0.4);

    // Draw central axis at 0
    svg.append("line")
      .attr("x1", xScale(0))
      .attr("y1", 60)
      .attr("x2", xScale(0))
      .attr("y2", 340)
      .attr("stroke", varColor("warm-gray-border"))
      .attr("stroke-width", 1.5);

    // Draw bottom X Axis ticks
    svg.append("g")
      .attr("transform", "translate(0, 340)")
      .call(d3.axisBottom(xScale).ticks(5))
      .attr("class", "axis");

    svg.append("text")
      .attr("x", 250)
      .attr("y", 375)
      .attr("text-anchor", "middle")
      .text("SHAP Feature Importance Value")
      .style("font-size", "11px");

    // Labels explaining prediction forces
    svg.append("text")
      .attr("x", xScale(-2.5))
      .attr("y", 50)
      .attr("text-anchor", "middle")
      .text("← Pulls Toward Normal")
      .attr("fill", "#666")
      .style("font-size", "11px");

    svg.append("text")
      .attr("x", xScale(2.5))
      .attr("y", 50)
      .attr("text-anchor", "middle")
      .text("Pushes Toward PDAC →")
      .attr("fill", "#1B365D")
      .style("font-size", "11px")
      .style("font-weight", "600");

    // Render bars
    const bars = svg.selectAll(".shap-bar")
      .data(features)
      .enter()
      .append("rect")
      .attr("class", "shap-bar")
      .attr("x", d => d.val > 0 ? xScale(0) : xScale(d.val))
      .attr("y", d => yScale(d.name))
      .attr("height", yScale.bandwidth())
      .attr("fill", d => d.type === "push" ? "#1B365D" : "#c5c3b2")
      .attr("width", 0); // Start at width 0 for animation

    // Render names on left/right depending on value sign
    const textLabels = svg.selectAll(".bar-label")
      .data(features)
      .enter()
      .append("text")
      .attr("x", d => d.val > 0 ? xScale(-0.1) : xScale(0.1))
      .attr("y", d => yScale(d.name) + yScale.bandwidth()/2 + 4)
      .attr("text-anchor", d => d.val > 0 ? "end" : "start")
      .text(d => d.name)
      .style("font-size", "11px")
      .style("font-weight", "600")
      .style("opacity", 0);

    if (isReducedMotion) {
      bars.attr("x", d => d.val > 0 ? xScale(0) : xScale(d.val))
        .attr("width", d => Math.abs(xScale(d.val) - xScale(0)));
      textLabels.style("opacity", 1);
      drawRoughNotationDisclaimer();
      return;
    }

    // Animation bar growth
    anime({
      targets: '.shap-bar',
      width: (el, i) => {
        const d = features[i];
        return Math.abs(xScale(d.val) - xScale(0));
      },
      x: (el, i) => {
        const d = features[i];
        return d.val > 0 ? xScale(0) : xScale(d.val);
      },
      duration: 1200,
      easing: 'easeOutQuint',
      delay: anime.stagger(150),
      complete: () => {
        anime({
          targets: textLabels.nodes(),
          opacity: 1,
          duration: 500,
          easing: 'easeOutQuad'
        });
        drawRoughNotationDisclaimer();
      }
    });

    function drawRoughNotationDisclaimer() {
      const disclaimer = document.getElementById("shap-disclaimer");
      if (disclaimer && window.RoughNotation) {
        const annotation = window.RoughNotation.annotate(disclaimer, {
          type: 'box',
          color: '#1B365D',
          padding: 8,
          strokeWidth: 1.5
        });
        annotation.show();
      }
    }
  }


  // ----------------------------------------------------
  // Scene 4 — Selection & Orthogonality
  // ----------------------------------------------------
  function runScene4() {
    const width = 500;
    const height = 400;
    const svg = resetContainer("scene4-container", width, height);
    if (!svg) return;

    // Normal samples and Tumor samples mapped on 2D expressions
    const normalPoints = [
      {x: 0.12, y: 0.05}, {x: 0.20, y: 0.08}, {x: 0.35, y: 0.12}, {x: 0.40, y: 0.15},
      {x: 0.50, y: 0.20}, {x: 0.55, y: 0.25}, {x: 0.60, y: 0.38}, {x: 0.65, y: 0.30},
      {x: 0.70, y: 0.28}, {x: 0.72, y: 0.45}, {x: 0.85, y: 0.30}, {x: 0.90, y: 0.22}
    ];

    const tumorPoints = [
      {x: 0.78, y: 0.48}, {x: 0.80, y: 0.52}, {x: 0.82, y: 0.65}, {x: 0.85, y: 0.72},
      {x: 0.90, y: 0.80}, {x: 0.95, y: 0.88}, {x: 0.77, y: 0.90}, {x: 0.88, y: 0.95},
      {x: 0.92, y: 0.78}, {x: 0.84, y: 0.60}, {x: 0.86, y: 0.85}, {x: 0.96, y: 0.92}
    ];

    const xScale = d3.scaleLinear().domain([0, 1]).range([60, 440]);
    const yScale = d3.scaleLinear().domain([0, 1]).range([340, 60]);

    // Axis line render
    svg.append("g")
      .attr("transform", "translate(0, 340)")
      .call(d3.axisBottom(xScale).ticks(5))
      .attr("class", "axis");
    svg.append("g")
      .attr("transform", "translate(60, 0)")
      .call(d3.axisLeft(yScale).ticks(5))
      .attr("class", "axis");

    svg.append("text")
      .attr("x", 250)
      .attr("y", 380)
      .attr("text-anchor", "middle")
      .text("Rescaled UBE2S Expression (Input A)")
      .style("font-size", "11px")
      .style("font-weight", "600");

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -200)
      .attr("y", 22)
      .attr("text-anchor", "middle")
      .text("Rescaled CCR6 Expression (Input B)")
      .style("font-size", "11px")
      .style("font-weight", "600");

    // Draw Decision Boundaries
    const lineA = svg.append("line")
      .attr("x1", xScale(0.76))
      .attr("y1", yScale(0))
      .attr("x2", xScale(0.76))
      .attr("y2", yScale(1))
      .attr("stroke", "#8f342d")
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "4 4")
      .style("opacity", 0);

    const lineB = svg.append("line")
      .attr("x1", xScale(0))
      .attr("y1", yScale(0.464))
      .attr("x2", xScale(1))
      .attr("y2", yScale(0.464))
      .attr("stroke", "#8f342d")
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "4 4")
      .style("opacity", 0);

    // Quad labels
    const boundsLabelA = svg.append("text")
      .attr("x", xScale(0.76) + 6)
      .attr("y", yScale(0.98))
      .text("K_A = 0.760")
      .style("font-size", "10px")
      .attr("fill", "#8f342d")
      .style("opacity", 0);

    const boundsLabelB = svg.append("text")
      .attr("x", xScale(0.02))
      .attr("y", yScale(0.464) - 6)
      .text("K_B = 0.464")
      .style("font-size", "10px")
      .attr("fill", "#8f342d")
      .style("opacity", 0);

    // Draw ON region background
    const ONbox = svg.append("rect")
      .attr("x", xScale(0.76))
      .attr("y", yScale(1))
      .attr("width", xScale(1) - xScale(0.76))
      .attr("height", yScale(0.464) - yScale(1))
      .attr("fill", "rgba(27, 54, 93, 0.12)")
      .attr("stroke", "#1B365D")
      .attr("stroke-width", 1.5)
      .style("opacity", 0);

    // Draw normal & tumor points
    const normalGroup = svg.selectAll(".norm-dot")
      .data(normalPoints)
      .enter()
      .append("circle")
      .attr("class", "norm-dot")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", 4.5)
      .attr("fill", "#c5c3b2")
      .style("opacity", isReducedMotion ? 0.75 : 0);

    const tumorGroup = svg.selectAll(".tum-dot")
      .data(tumorPoints)
      .enter()
      .append("circle")
      .attr("class", "tum-dot")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", 4.5)
      .attr("fill", "#1B365D")
      .style("opacity", isReducedMotion ? 0.75 : 0);

    if (isReducedMotion) {
      lineA.style("opacity", 0.8);
      lineB.style("opacity", 0.8);
      boundsLabelA.style("opacity", 1);
      boundsLabelB.style("opacity", 1);
      ONbox.style("opacity", 1);
      annotateRoughLines();
      return;
    }

    // Sequence animations
    // 1. Reveal points
    anime({
      targets: '.norm-dot, .tum-dot',
      opacity: 0.75,
      delay: anime.stagger(40),
      duration: 800,
      easing: 'easeOutQuad',
      complete: () => {
        // 2. Draw threshold lines
        anime({
          targets: [lineA.node(), lineB.node(), boundsLabelA.node(), boundsLabelB.node()],
          opacity: [0, 0.8],
          duration: 600,
          easing: 'easeOutQuad',
          complete: () => {
            // 3. Reveal the ON quadrant
            anime({
              targets: ONbox.node(),
              opacity: 1,
              duration: 800,
              easing: 'easeOutQuad',
              complete: () => {
                annotateRoughLines();
              }
            });
          }
        });
      }
    });

    function annotateRoughLines() {
      const corrWarn = document.getElementById("corr-warn");
      if (corrWarn && window.RoughNotation) {
        const annotation = window.RoughNotation.annotate(corrWarn, {
          type: 'highlight',
          color: 'rgba(222, 220, 207, 0.5)',
          padding: 3
        });
        annotation.show();
      }
    }
  }


  // ----------------------------------------------------
  // Scene 5 — Hill-Equation AND Gate Simulation contour
  // ----------------------------------------------------
  function runScene5() {
    const width = 500;
    const height = 400;
    const svg = resetContainer("scene5-container", width, height);
    if (!svg) return;

    // Mathematical parameters
    const n = 1;
    const Ka = 0.76;
    const Kb = 0.46;

    // Generate grid matrix for rendering contour
    const gridSize = 25;
    const contourData = [];

    for (let r = 0; r < gridSize; r++) {
      for (let c = 0; c < gridSize; c++) {
        const aVal = c / (gridSize - 1);
        const bVal = r / (gridSize - 1);
        const ha = Math.pow(aVal, n) / (Math.pow(Ka, n) + Math.pow(aVal, n));
        const hb = Math.pow(bVal, n) / (Math.pow(Kb, n) + Math.pow(bVal, n));
        const out = ha * hb;
        contourData.push({
          row: r,
          col: c,
          aVal: aVal,
          bVal: bVal,
          output: out
        });
      }
    }

    const xScale = d3.scaleLinear().domain([0, 1]).range([60, 440]);
    const yScale = d3.scaleLinear().domain([0, 1]).range([340, 60]);

    // Grid sizes in svg pixels
    const cellW = (440 - 60) / gridSize;
    const cellH = (340 - 60) / gridSize;

    // Color gradient scale representing activation level
    // Interpolate from warm parchment to ink-blue
    const colorScale = d3.scaleLinear()
      .domain([0, 0.1, 0.25, 0.5])
      .range(["#f5f4ed", "#dce2e8", "#a6b9cd", "#1B365D"]);

    // Draw Axes
    svg.append("g")
      .attr("transform", "translate(0, 340)")
      .call(d3.axisBottom(xScale).ticks(5))
      .attr("class", "axis");
    svg.append("g")
      .attr("transform", "translate(60, 0)")
      .call(d3.axisLeft(yScale).ticks(5))
      .attr("class", "axis");

    svg.append("text")
      .attr("x", 250)
      .attr("y", 380)
      .attr("text-anchor", "middle")
      .text("Rescaled Input A [UBE2S]")
      .style("font-size", "11px");

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -200)
      .attr("y", 22)
      .attr("text-anchor", "middle")
      .text("Rescaled Input B [CCR6]")
      .style("font-size", "11px");

    // Render cells of the contour heatmap
    const cells = svg.selectAll(".heatmap-cell")
      .data(contourData)
      .enter()
      .append("rect")
      .attr("class", "heatmap-cell")
      .attr("x", d => xScale(d.aVal))
      .attr("y", d => yScale(d.bVal) - cellH)
      .attr("width", cellW + 0.5)
      .attr("height", cellH + 0.5)
      .attr("fill", d => colorScale(d.output))
      .style("opacity", isReducedMotion ? 1 : 0);

    // Annotate the decision threshold border (output = 0.25)
    // Draw contour line where output = 0.25
    // 0.25 threshold boundary is approx when ha * hb = 0.25. 
    // This is mathematically drawn as B = Kb / ((4*A/(Ka+A)) - 1)
    const lineGenerator = d3.line()
      .x(d => xScale(d.a))
      .y(d => yScale(d.b))
      .curve(d3.curveBasis);

    const boundaryPoints = [];
    for (let a = Ka + 0.05; a <= 1.0; a += 0.02) {
      const termA = a / (Ka + a);
      if (termA > 0.25) {
        const termB = 0.25 / termA;
        const b = (Kb * termB) / (1 - termB);
        if (b >= 0 && b <= 1.0) {
          boundaryPoints.push({ a: a, b: b });
        }
      }
    }

    const contourLine = svg.append("path")
      .datum(boundaryPoints)
      .attr("fill", "none")
      .attr("stroke", "#8f342d")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "4 4")
      .attr("d", lineGenerator)
      .style("opacity", 0);

    const contourLabel = svg.append("text")
      .attr("x", xScale(0.9))
      .attr("y", yScale(0.55))
      .text("ON Threshold (0.25)")
      .attr("fill", "#8f342d")
      .style("font-size", "10px")
      .style("font-weight", "600")
      .style("opacity", 0);

    if (isReducedMotion) {
      cells.style("opacity", 1);
      contourLine.style("opacity", 0.9);
      contourLabel.style("opacity", 1);
      annotateThresholdDisclaimer();
      return;
    }

    // Animate equation lines fade-in on the left
    anime({
      targets: '#hill-equation-container .equation-line',
      opacity: [0, 1],
      translateY: [15, 0],
      delay: anime.stagger(200),
      duration: 800,
      easing: 'easeOutQuad'
    });

    // Heatmap cells reveal sweep
    anime({
      targets: '.heatmap-cell',
      opacity: 1,
      delay: (el, i) => {
        const d = contourData[i];
        // Diagonal sweep animation from bottom-left to top-right
        return (d.row + d.col) * 20;
      },
      duration: 500,
      easing: 'easeOutQuad',
      complete: () => {
        // Draw threshold contour line
        anime({
          targets: [contourLine.node(), contourLabel.node()],
          opacity: 0.9,
          duration: 600,
          easing: 'easeOutQuad',
          complete: () => {
            annotateThresholdDisclaimer();
          }
        });
      }
    });

    function annotateThresholdDisclaimer() {
      const disclaimer = document.getElementById("threshold-disclaimer");
      if (disclaimer && window.RoughNotation) {
        const annotation = window.RoughNotation.annotate(disclaimer, {
          type: 'underline',
          color: '#1B365D',
          strokeWidth: 1.5
        });
        annotation.show();
      }
    }
  }


  // ----------------------------------------------------
  // Scene 6 — Validation & Metrics Comparison
  // ----------------------------------------------------
  function runScene6() {
    const width = 500;
    const height = 400;
    const svg = resetContainer("scene6-container", width, height);
    if (!svg) return;

    // Discovery vs GSE62452 Validation comparative metrics
    const metrics = [
      { name: "ROC-AUC", discovery: 99.9, validation: 64.8 },
      { name: "Specificity", discovery: 99.4, validation: 98.4 },
      { name: "Sensitivity", discovery: 97.8, validation: 4.3 }
    ];

    const xScale = d3.scaleBand().domain(metrics.map(m => m.name)).range([60, 440]).padding(0.4);
    const yScale = d3.scaleLinear().domain([0, 100]).range([340, 60]);

    // Draw Axes
    svg.append("g")
      .attr("transform", "translate(0, 340)")
      .call(d3.axisBottom(xScale))
      .attr("class", "axis");
    svg.append("g")
      .attr("transform", "translate(60, 0)")
      .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => d + "%"))
      .attr("class", "axis");

    // Grid lines
    svg.selectAll(".y-grid")
      .data([20, 40, 60, 80, 100])
      .enter()
      .append("line")
      .attr("class", "grid-line")
      .attr("x1", 60)
      .attr("y1", d => yScale(d))
      .attr("x2", 440)
      .attr("y2", d => yScale(d));

    // Legend
    const legend = svg.append("g").attr("transform", "translate(300, 30)");
    legend.append("rect").attr("x", 0).attr("y", 0).attr("width", 15).attr("height", 10).attr("fill", "#1B365D");
    legend.append("text").attr("x", 20).attr("y", 9).text("Discovery Cohort").style("font-size", "11px");
    legend.append("rect").attr("x", 0).attr("y", 20).attr("width", 15).attr("height", 10).attr("fill", "#c5c3b2");
    legend.append("text").attr("x", 20).attr("y", 29).text("Validation (GSE62452)").style("font-size", "11px");

    // Double Bar rendering setup
    const groupWidth = xScale.bandwidth();
    const barWidth = groupWidth / 2 - 2;

    const discBars = svg.selectAll(".disc-bar")
      .data(metrics)
      .enter()
      .append("rect")
      .attr("class", "disc-bar")
      .attr("x", d => xScale(d.name))
      .attr("y", yScale(0))
      .attr("width", barWidth)
      .attr("fill", "#1B365D")
      .attr("height", 0);

    const valBars = svg.selectAll(".val-bar")
      .data(metrics)
      .enter()
      .append("rect")
      .attr("class", "val-bar")
      .attr("x", d => xScale(d.name) + barWidth + 4)
      .attr("y", yScale(0))
      .attr("width", barWidth)
      .attr("fill", d => d.name === "Sensitivity" ? "#8f342d" : "#c5c3b2") // Highlight sensitivity collapse
      .attr("height", 0);

    // Value Labels on top of bars
    const discLabels = svg.selectAll(".disc-val-label")
      .data(metrics)
      .enter()
      .append("text")
      .attr("class", "disc-val-label")
      .attr("x", d => xScale(d.name) + barWidth / 2)
      .attr("y", d => yScale(d.discovery) - 5)
      .attr("text-anchor", "middle")
      .text(d => d.discovery + "%")
      .style("font-size", "10px")
      .style("font-weight", "600")
      .style("opacity", 0);

    const valLabels = svg.selectAll(".val-val-label")
      .data(metrics)
      .enter()
      .append("text")
      .attr("class", "val-val-label")
      .attr("x", d => xScale(d.name) + barWidth * 1.5 + 4)
      .attr("y", d => yScale(d.validation) - 5)
      .attr("text-anchor", "middle")
      .text(d => d.validation + "%")
      .style("font-size", "10px")
      .style("font-weight", "600")
      .style("opacity", 0)
      .attr("fill", d => d.name === "Sensitivity" ? "#8f342d" : "inherit");

    if (isReducedMotion) {
      discBars.attr("y", d => yScale(d.discovery))
        .attr("height", d => yScale(0) - yScale(d.discovery));
      valBars.attr("y", d => yScale(d.validation))
        .attr("height", d => yScale(0) - yScale(d.validation));
      discLabels.style("opacity", 1);
      valLabels.style("opacity", 1);
      annotateTakeawayAlert();
      return;
    }

    // Animate bars rising
    anime({
      targets: '.disc-bar',
      y: (el, i) => yScale(metrics[i].discovery),
      height: (el, i) => yScale(0) - yScale(metrics[i].discovery),
      duration: 1000,
      easing: 'easeOutQuint',
      delay: anime.stagger(100),
      complete: () => {
        anime({
          targets: '.val-bar',
          y: (el, i) => yScale(metrics[i].validation),
          height: (el, i) => yScale(0) - yScale(metrics[i].validation),
          duration: 1000,
          easing: 'easeOutQuint',
          delay: anime.stagger(100),
          complete: () => {
            // Fade in labels
            anime({
              targets: ['.disc-val-label', '.val-val-label'],
              opacity: 1,
              duration: 500,
              easing: 'easeOutQuad',
              complete: () => {
                annotateTakeawayAlert();
              }
            });
          }
        });
      }
    });

    function annotateTakeawayAlert() {
      const takeaway = document.getElementById("validation-takeaway");
      if (takeaway && window.RoughNotation) {
        const annotation = window.RoughNotation.annotate(takeaway, {
          type: 'box',
          color: '#8f342d',
          padding: 12,
          strokeWidth: 2,
          iterations: 3
        });
        annotation.show();
      }
    }
  }


  // ==========================================
  // Helper functions
  // ==========================================
  function varColor(cssVarName) {
    return getComputedStyle(document.documentElement).getPropertyValue(`--${cssVarName}`).trim();
  }

  // Initialize
  updateSlide(0);

});
