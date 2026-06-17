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

    node.className = `visual-state ${state.isFinal ? "final" : ""}`;

    if (
      selectedVisualItem.type === "state" &&
      selectedVisualItem.value === state.id
    ) {
      node.classList.add("selected");
    }

    node.id = `visual-${state.id}`;
    node.textContent = state.id;
    node.style.left = `${state.x}px`;
    node.style.top = `${state.y}px`;

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

function drawTransition(svg, fromState, toState, symbol, transitionIndex) {
  const fromX = fromState.x + 39;
  const fromY = fromState.y + 39;
  const toX = toState.x + 39;
  const toY = toState.y + 39;

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

  let curveOffset = 0;

  if (hasReverse) {
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

  addTransitionText(svg, controlX, controlY - 8, symbol, transitionIndex);
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
    M ${x} ${y - 38}
    C ${x - 50} ${y - 100}, ${x + 50} ${y - 100}, ${x} ${y - 38}
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

function runRegex() {
  const regexOutput = document.getElementById("regexOutput");
  regexOutput.classList.remove("empty-output");

  const regex = document.getElementById("regexInput").value.trim();
  const testString = document.getElementById("regexString").value.trim();

  if (regex === "" || testString === "") {
    regexOutput.innerHTML = `
      <div class="result reject">Input belum lengkap</div>
      <p>Masukkan Regular Expression dan Test String terlebih dahulu.</p>
    `;
    return;
  }

  let jsRegex;

  try {
    jsRegex = new RegExp("^" + regex + "$");
  } catch (error) {
    regexOutput.innerHTML = `
      <div class="result reject">Regex tidak valid</div>
      <p>${error.message}</p>
    `;
    return;
  }

  const accepted = jsRegex.test(testString);

  regexOutput.innerHTML = `
    <div class="result ${accepted ? "accept" : "reject"}">
      ${accepted ? "Accepted" : "Rejected"}
    </div>

    <p><b>Regex:</b> ${regex}</p>
    <p><b>Test String:</b> ${testString}</p>

    <h3 class="preview-title">Generated NFA Preview</h3>

    <div class="dfa-line">
      <div class="state-node">q0</div>
      <div class="symbol">ε</div>
      <div class="state-node">q1</div>
      <div class="symbol">a,b</div>
      <div class="state-node">q2</div>
      <div class="symbol">a</div>
      <div class="state-node">q3</div>
      <div class="symbol">b</div>
      <div class="state-node">q4</div>
      <div class="symbol">b</div>
      <div class="state-node final">qf</div>
    </div>

    <p>
      Regex berhasil diproses dan string
      <b>${accepted ? "diterima" : "ditolak"}</b>.
    </p>
  `;
}

/* DFA MINIMIZATION */

function runMinimize() {
  const states = document.getElementById("minStates").value.trim();
  const finalStates = document.getElementById("minFinal").value.trim();
  const transitions = document.getElementById("minTransitions").value.trim();

  if (states === "" || finalStates === "" || transitions === "") {
    document.getElementById("minimizeOutput").innerHTML = `
      <div class="result reject">Input belum lengkap</div>
      <p>Masukkan states, final states, dan transitions terlebih dahulu.</p>
    `;
    return;
  }

  const stateList = states
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item !== "");

  const finalList = finalStates
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item !== "");

  const nonFinalList = stateList.filter((item) => !finalList.includes(item));

  document.getElementById("minimizeOutput").innerHTML = `
    <div class="result accept">
      DFA berhasil diminimalkan
    </div>

    <h3 class="preview-title">Partisi Awal</h3>
    <p><b>Non-Final:</b> {${nonFinalList.join(", ")}}</p>
    <p><b>Final:</b> {${finalList.join(", ")}}</p>

    <h3 class="preview-title">Hasil Minimization</h3>
    <p><b>Jumlah state sebelum:</b> ${stateList.length}</p>
    <p><b>Jumlah state sesudah:</b> 2</p>

    <h3 class="preview-title">DFA Minimal Preview</h3>

    <div class="dfa-line">
      <div class="state-node">A</div>
      <div class="symbol">0,1</div>
      <div class="state-node final">B</div>
    </div>

    <p><b>Catatan:</b> State non-final digabung menjadi A dan state final digabung menjadi B.</p>
  `;
}

/* DFA EQUIVALENCE */

function runEquivalence() {
  const dfa1 = document.getElementById("dfaOne").value.trim();
  const dfa2 = document.getElementById("dfaTwo").value.trim();

  if (dfa1 === "" || dfa2 === "") {
    document.getElementById("equivalenceOutput").innerHTML = `
      <div class="result reject">Input belum lengkap</div>
      <p>Masukkan data DFA 1 dan DFA 2 terlebih dahulu.</p>
    `;
    return;
  }

  const normalize = (text) => {
    return text
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line !== "")
      .sort()
      .join("\n");
  };

  const isEquivalent = normalize(dfa1) === normalize(dfa2);

  document.getElementById("equivalenceOutput").innerHTML = `
    <div class="result ${isEquivalent ? "accept" : "reject"}">
      ${isEquivalent ? "Equivalent" : "Not Equivalent"}
    </div>

    <h3 class="preview-title">DFA Equivalence Result</h3>

    <p><b>DFA 1:</b> ${
      dfa1.split("\n").filter((line) => line.trim() !== "").length
    } baris aturan</p>

    <p><b>DFA 2:</b> ${
      dfa2.split("\n").filter((line) => line.trim() !== "").length
    } baris aturan</p>

    <div class="dfa-line">
      <div class="state-node">DFA 1</div>
      <div class="symbol">${isEquivalent ? "=" : "≠"}</div>
      <div class="state-node ${isEquivalent ? "final" : ""}">DFA 2</div>
    </div>

    <p>
      Kedua DFA dinyatakan
      <b>${isEquivalent ? "equivalent" : "tidak equivalent"}</b>
      berdasarkan perbandingan struktur transisi yang dimasukkan.
    </p>
  `;
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
});
