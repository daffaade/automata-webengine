function showPage(pageId) {
  const pages = document.querySelectorAll(".page");
  const menus = document.querySelectorAll(".sidebar a");

  pages.forEach((page) => page.classList.remove("active-page"));
  menus.forEach((menu) => menu.classList.remove("active"));

  const selectedPage = document.getElementById(pageId);
  const selectedMenu = document.querySelector(
    `.sidebar a[data-page="${pageId}"]`,
  );

  if (selectedPage) selectedPage.classList.add("active-page");
  if (selectedMenu) selectedMenu.classList.add("active");

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

/* DFA VISUAL  */

let visualStates = [];
let visualTransitions = [];
let stateCounter = 0;

let draggedStateId = null;
let dragOffsetX = 0;
let dragOffsetY = 0;

let selectedVisualItem = {
  type: null,
  value: null,
};

function getAlphabet() {
  return document
    .getElementById("visualAlphabet")
    .value.split(",")
    .map((item) => item.trim())
    .filter((item) => item !== "");
}

function addVisualState() {
  const id = `q${stateCounter}`;
  stateCounter++;

  const state = {
    id: id,
    x: 80 + visualStates.length * 120,
    y: 200,
    isFinal: false,
  };

  visualStates.push(state);

  renderVisualGraph();
  updateVisualControls();

  if (visualStates.length === 1) {
    document.getElementById("visualStartState").value = id;
  }
}

function updateVisualControls() {
  const startSelect = document.getElementById("visualStartState");
  const fromSelect = document.getElementById("transitionFrom");
  const toSelect = document.getElementById("transitionTo");
  const finalList = document.getElementById("finalStateList");

  if (!startSelect || !fromSelect || !toSelect || !finalList) return;

  const currentStart = startSelect.value;

  startSelect.innerHTML = "";
  fromSelect.innerHTML = "";
  toSelect.innerHTML = "";

  visualStates.forEach((state) => {
    startSelect.innerHTML += `<option value="${state.id}">${state.id}</option>`;
    fromSelect.innerHTML += `<option value="${state.id}">${state.id}</option>`;
    toSelect.innerHTML += `<option value="${state.id}">${state.id}</option>`;
  });

  if (visualStates.some((state) => state.id === currentStart)) {
    startSelect.value = currentStart;
  }

  if (visualStates.length === 0) {
    finalList.innerHTML = "Belum ada state.";
    return;
  }

  finalList.innerHTML = visualStates
    .map((state) => {
      return `
        <label class="checkbox-item">
          <input
            type="checkbox"
            onchange="toggleVisualFinal('${state.id}', this.checked)"
            ${state.isFinal ? "checked" : ""}
          />
          ${state.id}
        </label>
      `;
    })
    .join("");
}

function toggleVisualFinal(id, checked) {
  const state = visualStates.find((item) => item.id === id);

  if (state) {
    state.isFinal = checked;
    renderVisualGraph();
  }
}

function addVisualTransition() {
  const from = document.getElementById("transitionFrom").value;
  const to = document.getElementById("transitionTo").value;
  const symbol = document.getElementById("transitionSymbol").value.trim();
  const alphabet = getAlphabet();

  if (!from || !to || symbol === "") {
    alert("Isi From, Symbol, dan To terlebih dahulu.");
    return;
  }

  if (alphabet.length === 0) {
    alert("Isi Alphabet terlebih dahulu, contoh: a,b atau 0,1.");
    return;
  }

  if (!alphabet.includes(symbol)) {
    alert(`Simbol "${symbol}" tidak ada dalam alphabet.`);
    return;
  }

  const existing = visualTransitions.find((item) => {
    return item.from === from && item.symbol === symbol;
  });

  if (existing) {
    alert(`Transisi dari ${from} dengan simbol ${symbol} sudah ada.`);
    return;
  }

  visualTransitions.push({
    from: from,
    to: to,
    symbol: symbol,
  });

  document.getElementById("transitionSymbol").value = "";

  renderVisualGraph();
}

function resetSvg(svg) {
  svg.innerHTML = `
    <defs>
      <marker
        id="arrowhead"
        markerWidth="10"
        markerHeight="7"
        refX="9"
        refY="3.5"
        orient="auto"
      >
        <polygon points="0 0, 10 3.5, 0 7" fill="#58a6ff"></polygon>
      </marker>
    </defs>
  `;
}

function renderVisualGraph() {
  try {
    const stateLayer = document.getElementById("stateLayer");
    const svg = document.getElementById("transitionSvg");

    if (!stateLayer || !svg) return;

    stateLayer.innerHTML = "";
    resetSvg(svg);

    visualTransitions.forEach((transition, index) => {
      const fromState = visualStates.find(
        (state) => state.id === transition.from,
      );
      const toState = visualStates.find((state) => state.id === transition.to);

      if (fromState && toState) {
        drawTransition(svg, fromState, toState, transition.symbol, index);
      }
    });

    visualStates.forEach((state) => {
      const node = document.createElement("div");
      node.id = `visual-${state.id}`;
      node.className = "visual-state";

      if (state.isFinal) {
        node.classList.add("final");
      }

      if (
        selectedVisualItem.type === "state" &&
        selectedVisualItem.value === state.id
      ) {
        node.classList.add("selected");
      }

      node.style.left = state.x + "px";
      node.style.top = state.y + "px";
      node.innerHTML = `<span>${state.id}</span>`;

    node.addEventListener("pointerdown", function (event) {
      event.stopPropagation();
      event.preventDefault();

      selectedVisualItem = {
        type: "state",
        value: state.id,
      };

      draggedStateId = state.id;

      const nodeRect = node.getBoundingClientRect();
      dragOffsetX = event.clientX - nodeRect.left;
      dragOffsetY = event.clientY - nodeRect.top;

      document.querySelectorAll(".visual-state").forEach((item) => {
        item.classList.remove("selected");
      });

      document
        .querySelectorAll(".transition-line, .transition-label")
        .forEach((item) => {
          item.classList.remove("selected");
        });

      node.classList.add("selected");
    });

    stateLayer.appendChild(node);
  });
  } catch (error) {
    console.error("Error drawing visual graph:", error);
  }
}

function redrawTransitionsOnly() {
  const svg = document.getElementById("transitionSvg");

  if (!svg) return;

  resetSvg(svg);

  visualTransitions.forEach((transition, index) => {
    const fromState = visualStates.find(
      (state) => state.id === transition.from,
    );
    const toState = visualStates.find((state) => state.id === transition.to);

    if (fromState && toState) {
      drawTransition(svg, fromState, toState, transition.symbol, index);
    }
  });
}

function getIntermediateNodes(fromState, toState) {
  const NODE_RADIUS = 39;
  const MARGIN = 10;
  const hitRadius = NODE_RADIUS + MARGIN;

  const fromCX = fromState.x + NODE_RADIUS;
  const fromCY = fromState.y + NODE_RADIUS;
  const toCX = toState.x + NODE_RADIUS;
  const toCY = toState.y + NODE_RADIUS;

  const blocked = [];

  visualStates.forEach((state) => {
    if (state.id === fromState.id || state.id === toState.id) return;

    const cx = state.x + NODE_RADIUS;
    const cy = state.y + NODE_RADIUS;

    // Project the node center onto the line segment from→to
    const dx = toCX - fromCX;
    const dy = toCY - fromCY;
    const lenSq = dx * dx + dy * dy;

    if (lenSq === 0) return;

    let t = ((cx - fromCX) * dx + (cy - fromCY) * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));

    const closestX = fromCX + t * dx;
    const closestY = fromCY + t * dy;

    const distSq =
      (cx - closestX) * (cx - closestX) + (cy - closestY) * (cy - closestY);

    if (distSq < hitRadius * hitRadius) {
      blocked.push(state);
    }
  });

  return blocked;
}

function drawTransition(svg, fromState, toState, symbol, transitionIndex) {
  const NODE_RADIUS = 39;
  const fromX = fromState.x + NODE_RADIUS;
  const fromY = fromState.y + NODE_RADIUS;
  const toX = toState.x + NODE_RADIUS;
  const toY = toState.y + NODE_RADIUS;

  if (fromState.id === toState.id) {
    drawLoopTransition(svg, fromX, fromY, symbol, transitionIndex);
    return;
  }

  const angle = Math.atan2(toY - fromY, toX - fromX);

  const startX = fromX + Math.cos(angle) * 42;
  const startY = fromY + Math.sin(angle) * 42;
  const endX = toX - Math.cos(angle) * 46;
  const endY = toY - Math.sin(angle) * 46;

  const hasReverse = visualTransitions.some((item) => {
    return item.from === toState.id && item.to === fromState.id;
  });

  const sameDirection = visualTransitions.filter((item) => {
    return item.from === fromState.id && item.to === toState.id;
  });

  const sameDirectionIndex = sameDirection.findIndex((item) => {
    return item.symbol === symbol;
  });

  // Check for intermediate nodes that the straight line would cross
  const blockedNodes = getIntermediateNodes(fromState, toState);

  let curveOffset = 0;

  if (blockedNodes.length > 0) {
    // Scale curve based on distance and number of blocked nodes
    const dx = toX - fromX;
    const dy = toY - fromY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const baseCurve = Math.max(80, dist * 0.45);
    curveOffset = -(baseCurve + blockedNodes.length * 30);

    if (hasReverse) {
      curveOffset = -(Math.abs(curveOffset) + 30);
    }
  } else if (hasReverse) {
    curveOffset = -65;
  } else if (sameDirection.length > 1) {
    curveOffset = (sameDirectionIndex - (sameDirection.length - 1) / 2) * 40;
  }

  if (curveOffset !== 0) {
    drawCurvedTransition(
      svg,
      startX,
      startY,
      endX,
      endY,
      symbol,
      transitionIndex,
      curveOffset,
    );
    return;
  }

  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

  line.setAttribute("x1", startX);
  line.setAttribute("y1", startY);
  line.setAttribute("x2", endX);
  line.setAttribute("y2", endY);
  line.setAttribute("class", "transition-line");
  line.setAttribute("marker-end", "url(#arrowhead)");

  if (
    selectedVisualItem.type === "transition" &&
    selectedVisualItem.value === transitionIndex
  ) {
    line.classList.add("selected");
  }

  line.addEventListener("click", function (event) {
    event.stopPropagation();

    selectedVisualItem = {
      type: "transition",
      value: transitionIndex,
    };

    renderVisualGraph();
  });

  svg.appendChild(line);

  addTransitionText(
    svg,
    (startX + endX) / 2,
    (startY + endY) / 2 - 8,
    symbol,
    transitionIndex,
  );
}

function drawCurvedTransition(
  svg,
  startX,
  startY,
  endX,
  endY,
  symbol,
  transitionIndex,
  curveOffset,
) {
  const midX = (startX + endX) / 2;
  const midY = (startY + endY) / 2;

  const dx = endX - startX;
  const dy = endY - startY;
  const length = Math.sqrt(dx * dx + dy * dy);

  const normalX = -dy / length;
  const normalY = dx / length;

  const controlX = midX + normalX * curveOffset;
  const controlY = midY + normalY * curveOffset;

  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");

  path.setAttribute(
    "d",
    `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`,
  );
  path.setAttribute("class", "transition-line");
  path.setAttribute("marker-end", "url(#arrowhead)");

  if (
    selectedVisualItem.type === "transition" &&
    selectedVisualItem.value === transitionIndex
  ) {
    path.classList.add("selected");
  }

  path.addEventListener("click", function (event) {
    event.stopPropagation();

    selectedVisualItem = {
      type: "transition",
      value: transitionIndex,
    };

    renderVisualGraph();
  });

  svg.appendChild(path);

  const peakX = midX + normalX * (curveOffset / 2);
  const peakY = midY + normalY * (curveOffset / 2);
  addTransitionText(svg, peakX, peakY - 8, symbol, transitionIndex);
}

function drawLoopTransition(svg, x, y, symbol, transitionIndex) {
  const transition = visualTransitions[transitionIndex];

  const loopSymbols = visualTransitions
    .filter((item) => {
      return item.from === transition.from && item.to === transition.to;
    })
    .map((item) => item.symbol);

  const firstLoopIndex = visualTransitions.findIndex((item) => {
    return item.from === transition.from && item.to === transition.to;
  });

  if (transitionIndex !== firstLoopIndex) {
    return;
  }

  const labelText = loopSymbols.join(",");

  const loopPath = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path",
  );

  const d = `
    M ${x - 12} ${y - 36}
    C ${x - 45} ${y - 100}, ${x + 45} ${y - 100}, ${x + 12} ${y - 36}
  `;

  loopPath.setAttribute("d", d);
  loopPath.setAttribute("class", "transition-line");
  loopPath.setAttribute("marker-end", "url(#arrowhead)");

  if (
    selectedVisualItem.type === "transition" &&
    loopSymbols.includes(visualTransitions[selectedVisualItem.value]?.symbol) &&
    visualTransitions[selectedVisualItem.value]?.from === transition.from &&
    visualTransitions[selectedVisualItem.value]?.to === transition.to
  ) {
    loopPath.classList.add("selected");
  }

  loopPath.addEventListener("click", function (event) {
    event.stopPropagation();

    selectedVisualItem = {
      type: "transition",
      value: firstLoopIndex,
    };

    renderVisualGraph();
  });

  svg.appendChild(loopPath);

  addTransitionText(svg, x, y - 90, labelText, firstLoopIndex);
}
function addTransitionText(svg, x, y, text, transitionIndex) {
  const label = document.createElementNS("http://www.w3.org/2000/svg", "text");

  label.setAttribute("x", x);
  label.setAttribute("y", y);
  label.setAttribute("text-anchor", "middle");
  label.setAttribute("class", "transition-label");
  label.textContent = text;

  if (
    selectedVisualItem.type === "transition" &&
    selectedVisualItem.value === transitionIndex
  ) {
    label.classList.add("selected");
  }

  label.addEventListener("click", function (event) {
    event.stopPropagation();

    selectedVisualItem = {
      type: "transition",
      value: transitionIndex,
    };

    renderVisualGraph();
  });

  svg.appendChild(label);
}

function runVisualDFA() {
  clearRunHighlight();

  const startState = document.getElementById("visualStartState").value;
  const alphabet = getAlphabet();
  const inputString = document.getElementById("visualInputString").value.trim();

  if (alphabet.length === 0) {
    document.getElementById("visualDfaOutput").innerHTML = `
      <div class="result reject">Alphabet belum diisi</div>
      <p>Isi alphabet terlebih dahulu, contoh: a,b atau 0,1.</p>
    `;
    return;
  }

  if (!startState) {
    document.getElementById("visualDfaOutput").innerHTML = `
      <div class="result reject">Belum ada state</div>
      <p>Tambahkan state terlebih dahulu.</p>
    `;
    return;
  }

  let currentState = startState;
  let path = [currentState];

  for (let char of inputString) {
    if (!alphabet.includes(char)) {
      document.getElementById("visualDfaOutput").innerHTML = `
        <div class="result reject">Rejected</div>
        <p>Karakter <b>${char}</b> tidak ada dalam alphabet.</p>
        <p><b>Path:</b> ${path.join(" → ")}</p>
      `;

      highlightState(currentState, false);
      return;
    }

    const transition = visualTransitions.find((item) => {
      return item.from === currentState && item.symbol === char;
    });

    if (!transition) {
      document.getElementById("visualDfaOutput").innerHTML = `
        <div class="result reject">Rejected</div>
        <p>Tidak ada transisi dari <b>${currentState}</b> dengan input <b>${char}</b>.</p>
        <p><b>Path:</b> ${path.join(" → ")}</p>
      `;

      highlightState(currentState, false);
      return;
    }

    currentState = transition.to;
    path.push(currentState);
  }

  const finalState = visualStates.find((item) => item.id === currentState);
  const accepted = finalState && finalState.isFinal;

  highlightState(currentState, accepted);

  document.getElementById("visualDfaOutput").innerHTML = `
    <div class="result ${accepted ? "accept" : "reject"}">
      ${accepted ? "Accepted" : "Rejected"}
    </div>

    <p><b>Start State:</b> ${startState}</p>
    <p><b>Final Position:</b> ${currentState}</p>
    <p><b>Path:</b> ${path.join(" → ")}</p>
  `;
}

function highlightState(id, accepted) {
  const node = document.getElementById(`visual-${id}`);

  if (!node) return;

  node.classList.add(accepted ? "active-run" : "reject-run");
}

function clearRunHighlight() {
  document.querySelectorAll(".visual-state").forEach((node) => {
    node.classList.remove("active-run", "reject-run");
  });
}

function resetVisualDFA() {
  visualStates = [];
  visualTransitions = [];
  stateCounter = 0;

  selectedVisualItem = {
    type: null,
    value: null,
  };

  const output = document.getElementById("visualDfaOutput");

  if (output) {
    output.innerHTML = "Hasil simulasi akan muncul di sini.";
  }

  renderVisualGraph();
  updateVisualControls();
}

function deleteSelectedVisualItem() {
  if (!selectedVisualItem.type) return;

  if (selectedVisualItem.type === "state") {
    const stateId = selectedVisualItem.value;

    visualStates = visualStates.filter((state) => state.id !== stateId);

    visualTransitions = visualTransitions.filter((transition) => {
      return transition.from !== stateId && transition.to !== stateId;
    });

    document.getElementById("visualDfaOutput").innerHTML = `
      <div class="result reject">State dihapus</div>
      <p>State <b>${stateId}</b> dan transisi yang terhubung sudah dihapus.</p>
    `;
  }

  if (selectedVisualItem.type === "transition") {
    const index = selectedVisualItem.value;
    const deletedTransition = visualTransitions[index];

    if (deletedTransition) {
      visualTransitions.splice(index, 1);

      document.getElementById("visualDfaOutput").innerHTML = `
        <div class="result reject">Transisi dihapus</div>
        <p>Transisi <b>${deletedTransition.from} --${deletedTransition.symbol}--> ${deletedTransition.to}</b> sudah dihapus.</p>
      `;
    }
  }

  selectedVisualItem = {
    type: null,
    value: null,
  };

  renderVisualGraph();
  updateVisualControls();
}

/* REGEX TO NFA */

async function runRegex() {
  const regexOutput = document.getElementById("regexOutput");
  regexOutput.classList.remove("empty-output");

  const regex = document.getElementById("regexInput").value.trim();
  const testString = document.getElementById("regexString").value.trim();

  if (regex === "") {
    regexOutput.innerHTML = `
      <div class="result reject">Input belum lengkap</div>
      <p>Masukkan Regular Expression terlebih dahulu.</p>
    `;
    return;
  }

  regexOutput.innerHTML = `
    <div class="result accept">Memproses...</div>
    <p>Sedang mengkonversi Regex ke NFA...</p>
  `;

  try {
    // 1. Convert Regex to NFA
    const convertRes = await fetch("/api/regex/to-nfa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ regex: regex }),
    });

    const convertData = await convertRes.json();

    if (!convertRes.ok) {
      regexOutput.innerHTML = `
        <div class="result reject">Regex tidak valid</div>
        <p>${convertData.error || "Gagal mengkonversi Regex"}</p>
      `;
      return;
    }

    const nfa = convertData.nfa;

    let testResultHtml = "";
    if (testString !== "") {
      const testRes = await fetch("/api/nfa/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          states: nfa.states,
          alphabet: nfa.alphabet,
          transitions: nfa.transitions,
          start_state: nfa.start_state,
          accept_states: nfa.accept_states,
          string: testString
        }),
      });

      const testData = await testRes.json();

      if (!testRes.ok) {
        regexOutput.innerHTML = `
          <div class="result reject">Gagal simulasi</div>
          <p>${testData.error}</p>
        `;
        return;
      }

      const accepted = testData.accepted;
      testResultHtml = `
        <div class="result ${accepted ? "accept" : "reject"}">
          ${accepted ? "String Diterima" : "String Ditolak"}
        </div>
        <p><b>Test String:</b> ${testString}</p>
      `;
    }

    // Format transitions for display
    let transitionsHtml = "<ul>";
    for (const [state_symbol, to_states] of Object.entries(nfa.transitions)) {
      transitionsHtml += `<li><b>${state_symbol}</b> &rarr; {${to_states.join(', ')}}</li>`;
    }
    transitionsHtml += "</ul>";

    regexOutput.innerHTML = `
      <div class="result accept">NFA Berhasil Dibuat</div>
      <p><b>Regex:</b> ${regex}</p>
      ${testResultHtml}

      <div class="equivalence-summary">
        <div class="summary-card"><span>Jumlah States</span><b>${nfa.states.length}</b></div>
        <div class="summary-card"><span>Start State</span><b>${nfa.start_state}</b></div>
        <div class="summary-card"><span>Accept States</span><b>${nfa.accept_states.join(', ')}</b></div>
      </div>

      <h3 class="preview-title">NFA Details</h3>
      <p><b>States:</b> {${nfa.states.join(', ')}}</p>
      <p><b>Alphabet:</b> {${nfa.alphabet.join(', ')}}</p>
      <p><b>Transitions:</b></p>
      ${transitionsHtml}
    `;

    // Render static NFA graph
    const graphData = formatGraphData(nfa);
    renderStaticGraph("regexStateLayer", "regexTransitionSvg", graphData);

  } catch (error) {
    regexOutput.innerHTML = `
      <div class="result reject">Network Error</div>
      <p>${error.message}</p>
    `;
  }
}

/* DFA MINIMIZATION */

let currentMinDFAOriginal = null;
let currentMinDFAMinimized = null;

async function runMinimize() {
  const states = document.getElementById("minStates").value.trim();
  const finalStates = document.getElementById("minFinal").value.trim();
  const transitionsRaw = document.getElementById("minTransitions").value.trim();
  const outputBox = document.getElementById("minimizeOutput");

  if (states === "" || finalStates === "" || transitionsRaw === "") {
    outputBox.innerHTML = `
      <div class="result reject">Input belum lengkap</div>
      <p>Masukkan states, final states, dan transitions terlebih dahulu.</p>
    `;
    return;
  }
  
  outputBox.innerHTML = `
    <div class="result accept">Memproses...</div>
    <p>Sedang meminimalkan DFA...</p>
  `;

  const stateList = parseListInput(states);
  const finalList = parseListInput(finalStates);
  const startState = stateList[0] || "";
  
  const parsedTransitions = parseTransitionsInput(transitionsRaw);
  
  const alphabetSet = new Set();
  for (const from in parsedTransitions) {
    for (const symbol in parsedTransitions[from]) {
      alphabetSet.add(symbol);
    }
  }

  const dfaData = {
    states: stateList,
    alphabet: Array.from(alphabetSet),
    transitions: parsedTransitions,
    start_state: startState,
    accept_states: finalList
  };

  try {
    const res = await fetch("/api/dfa/minimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dfaData),
    });

    const data = await res.json();

    if (!res.ok) {
      outputBox.innerHTML = `
        <div class="result reject">Gagal</div>
        <p>${data.error}</p>
      `;
      return;
    }

    currentMinDFAOriginal = formatGraphData(dfaData);
    currentMinDFAMinimized = formatGraphData(data.minimized);

    toggleMinGraph('original');

    outputBox.innerHTML = `
      <div class="result accept">${data.message}</div>
      <p><b>Jumlah state sebelum:</b> ${data.original_states}</p>
      <p><b>Jumlah state sesudah:</b> ${data.minimized_states}</p>
      
      <h3 class="preview-title">Langkah Minimisasi</h3>
      <ul style="padding-left: 20px; line-height: 1.6;">
        ${data.steps.map(step => {
          let stepNum = step.step;
          if (typeof stepNum === 'string' && stepNum.startsWith('3.')) {
            stepNum = "3 (Iterasi " + stepNum.split('.')[1] + ")";
          }
          return `<li><b>Step ${stepNum}:</b> ${step.description}</li>`;
        }).join('')}
      </ul>
    `;

  } catch (error) {
    outputBox.innerHTML = `
      <div class="result reject">Network Error</div>
      <p>${error.message}</p>
    `;
  }
}

function toggleMinGraph(viewType) {
  const btnOrig = document.getElementById("btnViewOriginal");
  const btnMin = document.getElementById("btnViewMinimized");
  
  if (btnOrig) btnOrig.classList.remove("active");
  if (btnMin) btnMin.classList.remove("active");

  const canvas = document.getElementById("minGraphCanvas");
  canvas.style.transition = "opacity 0.2s ease-out";
  canvas.style.opacity = 0;

  setTimeout(() => {
    if (viewType === "original") {
      if (btnOrig) btnOrig.classList.add("active");
      renderStaticGraph(
        "minStateLayer",
        "minTransitionSvg",
        currentMinDFAOriginal,
      );
    } else {
      if (btnMin) btnMin.classList.add("active");
      renderStaticGraph(
        "minStateLayer",
        "minTransitionSvg",
        currentMinDFAMinimized,
      );
    }
    canvas.style.opacity = 1;
  }, 200);
}

/* DFA EQUIVALENCE */

function parseListInput(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item !== "");
}

function parseTransitionsInput(value) {
  const transitions = {};

  const lines = value
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line !== "");

  lines.forEach((line) => {
    const parts = line.split(",").map((item) => item.trim());

    if (parts.length === 3) {
      const from = parts[0];
      const symbol = parts[1];
      const to = parts[2];

      transitions[`${from},${symbol}`] = to;
    }
  });

  return transitions;
}

function getEquivalenceDFA(prefix) {
  return {
    states: parseListInput(document.getElementById(`${prefix}States`).value),
    alphabet: parseListInput(
      document.getElementById(`${prefix}Alphabet`).value,
    ),
    start_state: document.getElementById(`${prefix}Start`).value.trim(),
    accept_states: parseListInput(
      document.getElementById(`${prefix}Accept`).value,
    ),
    transitions: parseTransitionsInput(
      document.getElementById(`${prefix}Transitions`).value,
    ),
  };
}

function validateEquivalenceInput(dfa, name) {
  if (dfa.states.length === 0) {
    return `${name}: States belum diisi.`;
  }

  if (dfa.alphabet.length === 0) {
    return `${name}: Alphabet belum diisi.`;
  }

  if (dfa.start_state === "") {
    return `${name}: Start state belum diisi.`;
  }

  if (!dfa.states.includes(dfa.start_state)) {
    return `${name}: Start state "${dfa.start_state}" tidak ada di daftar states.`;
  }

  const invalidAccept = dfa.accept_states.find((state) => {
    return !dfa.states.includes(state);
  });

  if (invalidAccept) {
    return `${name}: Accept state "${invalidAccept}" tidak ada di daftar states.`;
  }

  if (Object.keys(dfa.transitions).length === 0) {
    return `${name}: Transitions belum diisi.`;
  }

  return null;
}

async function runEquivalence() {
  const output = document.getElementById("equivalenceOutput");

  const dfa1 = getEquivalenceDFA("eq1");
  const dfa2 = getEquivalenceDFA("eq2");

  const error1 = validateEquivalenceInput(dfa1, "DFA 1");
  const error2 = validateEquivalenceInput(dfa2, "DFA 2");

  if (error1 || error2) {
    output.innerHTML = `
      <div class="result reject">Input belum lengkap</div>
      <p>${error1 || error2}</p>
    `;
    return;
  }

  output.innerHTML = `
    <div class="result accept">Memproses...</div>
    <p>Sedang memeriksa ekuivalensi DFA.</p>
  `;

  try {
    const response = await fetch("/api/dfa/equivalence", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        dfa1: dfa1,
        dfa2: dfa2,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      output.innerHTML = `
        <div class="result reject">Error</div>
        <p>${data.error}</p>
      `;
      return;
    }

    // Tampilkan grafis untuk kedua DFA
    document.getElementById("eqGraphContainer").style.display = "grid";
    renderStaticGraph("eq1StateLayer", "eq1TransitionSvg", formatGraphData(dfa1));
    renderStaticGraph("eq2StateLayer", "eq2TransitionSvg", formatGraphData(dfa2));

    let pairsHtml = "";

    data.visited_pairs.forEach(function (pair) {
      const sameStatus = pair.accept_dfa1 === pair.accept_dfa2;

      pairsHtml +=
        '<div class="state-pair-card ' +
        (sameStatus ? "accept" : "reject") +
        '">' +
        '<div class="pair">(' +
        pair.state_dfa1 +
        ", " +
        pair.state_dfa2 +
        ")</div>" +
        '<div class="status">' +
        (sameStatus ? "Status sama" : "Status berbeda") +
        "</div>" +
        "</div>";
    });

    let stepsHtml = "";

    data.steps.forEach(function (step) {
      stepsHtml += '<div class="step-card">';
      stepsHtml += "<p>";
      stepsHtml +=
        "<b>Step " + step.step + ":</b> " + step.description + "<br />";
      stepsHtml += step.detail + "<br />";

      if (step.transitions) {
        stepsHtml += "<b>Transitions:</b><ul>";

        step.transitions.forEach(function (item) {
          stepsHtml += "<li>" + item + "</li>";
        });

        stepsHtml += "</ul>";
      }

      stepsHtml += "<b>Result:</b> " + step.result;
      stepsHtml += "</p>";
      stepsHtml += "</div>";
    });

    output.innerHTML =
      '<div class="result ' +
      (data.equivalent ? "accept" : "reject") +
      '">' +
      (data.equivalent ? "Equivalent" : "Not Equivalent") +
      "</div>" +
      "<p><b>Reason:</b> " +
      data.reason +
      "</p>" +
      (data.witness ? "<p><b>Witness:</b> " + data.witness + "</p>" : "") +
      '<div class="equivalence-summary">' +
      '<div class="summary-card"><span>DFA 1 States</span><b>' +
      data.dfa1_info.num_states +
      "</b></div>" +
      '<div class="summary-card"><span>DFA 2 States</span><b>' +
      data.dfa2_info.num_states +
      "</b></div>" +
      '<div class="summary-card"><span>Visited Pairs</span><b>' +
      data.visited_pairs.length +
      "</b></div>" +
      "</div>" +
      '<h3 class="preview-title">Visited State Pairs</h3>' +
      '<div class="state-pair-list">' +
      pairsHtml +
      "</div>" +
      '<h3 class="preview-title">Product Construction Steps</h3>' +
      stepsHtml;
  } catch (error) {
    output.innerHTML = `
      <div class="result reject">Request gagal</div>
      <p>${error.message}</p>
    `;
  }
}

/* EVENT LISTENER */

document.addEventListener("pointermove", function (event) {
  if (!draggedStateId) return;

  event.preventDefault();

  const graphCanvas = document.getElementById("graphCanvas");
  if (!graphCanvas) return;

  const rect = graphCanvas.getBoundingClientRect();
  const state = visualStates.find((item) => item.id === draggedStateId);

  if (!state) return;

  let newX = event.clientX - rect.left - dragOffsetX;
  let newY = event.clientY - rect.top - dragOffsetY;

  const nodeSize = 78;

  newX = Math.max(0, Math.min(newX, graphCanvas.offsetWidth - nodeSize));
  newY = Math.max(0, Math.min(newY, graphCanvas.offsetHeight - nodeSize));

  state.x = newX;
  state.y = newY;

  const node = document.getElementById(`visual-${state.id}`);

  if (node) {
    node.style.left = `${newX}px`;
    node.style.top = `${newY}px`;
  }

  redrawTransitionsOnly();
});

document.addEventListener("pointerup", function () {
  if (draggedStateId) {
    draggedStateId = null;
    renderVisualGraph();
  }
});

document.addEventListener("keydown", function (event) {
  const activeElement = document.activeElement;

  const isTyping =
    activeElement.tagName === "INPUT" ||
    activeElement.tagName === "TEXTAREA" ||
    activeElement.tagName === "SELECT";

  if (isTyping) return;

  if (event.key === "Delete" || event.key === "Backspace") {
    event.preventDefault();
    deleteSelectedVisualItem();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  renderVisualGraph();
  updateVisualControls();

  const graphCanvas = document.getElementById("graphCanvas");

  if (graphCanvas) {
    graphCanvas.addEventListener("pointerdown", function (event) {
      if (event.target === graphCanvas || event.target.id === "transitionSvg") {
        selectedVisualItem = {
          type: null,
          value: null,
        };

        renderVisualGraph();
      }
    });
  }

  const visualInput = document.getElementById("visualInputString");
  if (visualInput) {
    visualInput.addEventListener("keydown", function(event) {
      if (event.key === "Enter") {
        event.preventDefault();
        runVisualDFA();
      }
    });
  }
});

/* THEME TOGGLE */
function toggleTheme() {
  document.body.classList.toggle('light-mode');
  const isLight = document.body.classList.contains('light-mode');
  
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
  
  const btns = document.querySelectorAll('.theme-toggle-btn');
  btns.forEach(btn => {
    const icon = btn.querySelector('.icon');
    const text = btn.querySelector('.theme-text');
    if (icon) icon.textContent = isLight ? '🌙' : '☀️';
    if (text) text.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-mode');
    const btns = document.querySelectorAll('.theme-toggle-btn');
    btns.forEach(btn => {
      const icon = btn.querySelector('.icon');
      const text = btn.querySelector('.theme-text');
      if (icon) icon.textContent = '🌙';
      if (text) text.textContent = 'Dark Mode';
    });
  }
});

/* ZOOM GRAPH */
let currentZoom = 1;
function zoomGraph(factor) {
  currentZoom *= factor;
  
  if (currentZoom < 0.3) currentZoom = 0.3;
  if (currentZoom > 3) currentZoom = 3;
  
  const canvas = document.getElementById("graphCanvas");
  if (canvas) {
    canvas.style.zoom = currentZoom;
  }
}

let currentStaticZooms = {};
function zoomStaticGraph(canvasId, factor) {
  if (!currentStaticZooms[canvasId]) currentStaticZooms[canvasId] = 1;
  currentStaticZooms[canvasId] *= factor;
  
  if (currentStaticZooms[canvasId] < 0.3) currentStaticZooms[canvasId] = 0.3;
  if (currentStaticZooms[canvasId] > 3) currentStaticZooms[canvasId] = 3;
  
  const canvas = document.getElementById(canvasId);
  if (canvas) {
    canvas.style.zoom = currentStaticZooms[canvasId];
  }
}

/* --- STATIC GRAPH RENDERER FOR PROGRAM 2, 3, 4 --- */

function renderStaticGraph(stateLayerId, svgId, graphData) {
  const stateLayer = document.getElementById(stateLayerId);
  const svg = document.getElementById(svgId);

  if (!stateLayer || !svg) return;

  stateLayer.innerHTML = "";
  resetSvg(svg);

  const columns = 6;
  graphData.states.forEach((state, index) => {
    if (state.x === undefined || state.y === undefined) {
      state.x = 100 + (index % columns) * 240;
      state.y = 260 + Math.floor(index / columns) * 200;
    }
  });

  graphData.transitions.forEach((transition, index) => {
    const fromState = graphData.states.find((s) => s.id === String(transition.from));
    const toState = graphData.states.find((s) => s.id === String(transition.to));

    if (fromState && toState) {
      drawStaticTransition(svg, fromState, toState, transition.symbol, index, graphData.transitions);
    }
  });

  graphData.states.forEach((state) => {
    const node = document.createElement("div");
    
    let className = "visual-state";
    if (state.isFinal) className += " final";
    if (state.isStart) {
       className += " start-node";
       node.style.boxShadow = "0 0 0 4px rgba(0, 212, 255, 0.4)";
    }
    node.className = className;
    node.style.cursor = "default";

    node.id = `${stateLayerId}-visual-${state.id}`;
    node.textContent = state.id;
    node.style.left = `${state.x}px`;
    node.style.top = `${state.y}px`;

    stateLayer.appendChild(node);
  });
}

function drawStaticTransition(svg, fromState, toState, symbol, transitionIndex, allTransitions) {
  const fromX = fromState.x + 39;
  const fromY = fromState.y + 39;
  const toX = toState.x + 39;
  const toY = toState.y + 39;

  if (fromState.id === toState.id) {
    drawStaticLoopTransition(svg, fromX, fromY, symbol, transitionIndex, allTransitions);
    return;
  }

  const dx = toX - fromX;
  const dy = toY - fromY;
  const angle = Math.atan2(dy, dx);
  const distance = Math.sqrt(dx * dx + dy * dy);

  const startX = fromX + Math.cos(angle) * 42;
  const startY = fromY + Math.sin(angle) * 42;
  const endX = toX - Math.cos(angle) * 46;
  const endY = toY - Math.sin(angle) * 46;

  const hasReverse = allTransitions.some((item) => {
    return String(item.from) === String(toState.id) && String(item.to) === String(fromState.id);
  });

  const sameDirection = allTransitions.filter((item) => {
    return String(item.from) === String(fromState.id) && String(item.to) === String(toState.id);
  });

  const sameDirectionIndex = sameDirection.findIndex((item) => {
    return item.symbol === symbol;
  });

  let curveOffset = 0;

  if (hasReverse) {
    curveOffset = -65;
  } else if (sameDirection.length > 1) {
    curveOffset = (sameDirectionIndex - (sameDirection.length - 1) / 2) * 40;
  } else if (distance > 260) {
    // If it skips a node (distance ~480+), curve it high enough to clear loops
    curveOffset = -(60 + distance * 0.45); 
  }

  if (curveOffset !== 0) {
    drawStaticCurvedTransition(svg, startX, startY, endX, endY, symbol, curveOffset);
    return;
  }

  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", startX);
  line.setAttribute("y1", startY);
  line.setAttribute("x2", endX);
  line.setAttribute("y2", endY);
  line.setAttribute("class", "transition-line");
  line.setAttribute("marker-end", "url(#arrowhead)");

  svg.appendChild(line);

  addStaticTransitionText(svg, (startX + endX) / 2, (startY + endY) / 2 - 8, symbol);
}

function drawStaticCurvedTransition(svg, startX, startY, endX, endY, symbol, curveOffset) {
  const midX = (startX + endX) / 2;
  const midY = (startY + endY) / 2;

  const dx = endX - startX;
  const dy = endY - startY;
  const length = Math.sqrt(dx * dx + dy * dy);

  const normalX = -dy / length;
  const normalY = dx / length;

  const controlX = midX + normalX * curveOffset;
  const controlY = midY + normalY * curveOffset;

  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");

  path.setAttribute("d", `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`);
  path.setAttribute("class", "transition-line");
  path.setAttribute("marker-end", "url(#arrowhead)");

  svg.appendChild(path);

  // Text is placed at the peak of the quadratic bezier curve
  const peakX = midX + normalX * (curveOffset / 2);
  const peakY = midY + normalY * (curveOffset / 2);
  addStaticTransitionText(svg, peakX, peakY - 8, symbol);
}

function drawStaticLoopTransition(svg, x, y, symbol, transitionIndex, allTransitions) {
  const transition = allTransitions[transitionIndex];

  const loopSymbols = allTransitions
    .filter((item) => String(item.from) === String(transition.from) && String(item.to) === String(transition.to))
    .map((item) => item.symbol);

  const firstLoopIndex = allTransitions.findIndex((item) => {
    return String(item.from) === String(transition.from) && String(item.to) === String(transition.to);
  });

  if (transitionIndex !== firstLoopIndex) {
    return;
  }

  const labelText = loopSymbols.join(",");

  const loopPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  const d = `
    M ${x} ${y - 38}
    C ${x - 50} ${y - 100}, ${x + 50} ${y - 100}, ${x} ${y - 38}
  `;

  loopPath.setAttribute("d", d);
  loopPath.setAttribute("class", "transition-line");
  loopPath.setAttribute("marker-end", "url(#arrowhead)");

  svg.appendChild(loopPath);

  addStaticTransitionText(svg, x, y - 90, labelText);
}

function addStaticTransitionText(svg, x, y, text) {
  const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
  label.setAttribute("x", x);
  label.setAttribute("y", y);
  label.setAttribute("text-anchor", "middle");
  label.setAttribute("class", "transition-label");
  label.textContent = text;
  svg.appendChild(label);
}

function formatGraphData(data) {
  const states = data.states.map((id) => ({
    id: String(id),
    isFinal: data.accept_states.some(a => String(a) === String(id)),
    isStart: String(id) === String(data.start_state),
  }));

  const transitionsMap = {};
  for (const key in data.transitions) {
    const parts = key.split(",");
    if (parts.length >= 2) {
      const from = parts[0];
      const symbol = parts.slice(1).join(",");
      const toValue = data.transitions[key];
      const toArray = Array.isArray(toValue) ? toValue : [toValue];

      toArray.forEach(to => {
        const tKey = `${from}->${to}`;
        if (!transitionsMap[tKey]) {
          transitionsMap[tKey] = { from: String(from), to: String(to), symbols: [] };
        }
        if (!transitionsMap[tKey].symbols.includes(symbol)) {
          transitionsMap[tKey].symbols.push(symbol);
        }
      });
    }
  }

  const transitions = Object.values(transitionsMap).map(t => ({
    from: t.from,
    to: t.to,
    symbol: t.symbols.join(",")
  }));

  return { states, transitions };
}
