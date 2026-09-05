/**
 * SysCalculus - Client-Side Systems Simulators & Micro-Tools
 * 100% In-Browser Execution • Zero Server Latency • Zero Data Exfiltration
 */

window.SysCalculus = window.SysCalculus || {};

// ============================================================================
// 1. DATABASE CONNECTION POOL & DEADLOCK SIMULATOR
// ============================================================================
SysCalculus.initDbPoolSimulator = function() {
  const canvas = document.getElementById('simCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Controls
  const poolSizeInput = document.getElementById('poolSize');
  const poolSizeVal = document.getElementById('poolSizeVal');
  const rpsInput = document.getElementById('reqRate');
  const rpsVal = document.getElementById('reqRateVal');
  const queryDurationInput = document.getElementById('queryDuration');
  const queryDurationVal = document.getElementById('queryDurationVal');
  const leakToggle = document.getElementById('leakToggle');

  // Metrics Display
  const activeConnDisplay = document.getElementById('metricActiveConn');
  const queueDepthDisplay = document.getElementById('metricQueue');
  const p99Display = document.getElementById('metricP99');
  const errorRateDisplay = document.getElementById('metricErrorRate');
  const terminalLog = document.getElementById('simTerminalLog');

  let maxPool = parseInt(poolSizeInput ? poolSizeInput.value : 20, 10);
  let rps = parseInt(rpsInput ? rpsInput.value : 30, 10);
  let queryTime = parseInt(queryDurationInput ? queryDurationInput.value : 250, 10);
  let hasLeak = leakToggle ? leakToggle.checked : false;

  let activeConnections = 0;
  let leakedConnections = 0;
  let queue = [];
  let p99Latency = 12;
  let errorCount = 0;
  let totalRequests = 0;
  let animationFrameId = null;

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // Listeners
  if (poolSizeInput) {
    poolSizeInput.addEventListener('input', (e) => {
      maxPool = parseInt(e.target.value, 10);
      if (poolSizeVal) poolSizeVal.textContent = maxPool;
    });
  }
  if (rpsInput) {
    rpsInput.addEventListener('input', (e) => {
      rps = parseInt(e.target.value, 10);
      if (rpsVal) rpsVal.textContent = rps + ' req/s';
    });
  }
  if (queryDurationInput) {
    queryDurationInput.addEventListener('input', (e) => {
      queryTime = parseInt(e.target.value, 10);
      if (queryDurationVal) queryDurationVal.textContent = queryTime + ' ms';
    });
  }
  if (leakToggle) {
    leakToggle.addEventListener('change', (e) => {
      hasLeak = e.target.checked;
      if (hasLeak) {
        logTerminal('[WARN] Connection leak enabled: worker threads failing to call db.close() in finally block!');
      } else {
        leakedConnections = 0;
        logTerminal('[INFO] Connection pool flushed. Leaks resolved.');
      }
    });
  }

  function logTerminal(msg) {
    if (!terminalLog) return;
    const time = new Date().toISOString().substring(11, 19);
    const line = document.createElement('div');
    line.className = 'term-line';
    if (msg.includes('[WARN]') || msg.includes('DEADLOCK') || msg.includes('504')) {
      line.style.color = '#f85149';
    } else if (msg.includes('[INFO]')) {
      line.style.color = '#38bdf8';
    } else {
      line.style.color = '#8b949e';
    }
    line.textContent = `[${time}] ${msg}`;
    terminalLog.appendChild(line);
    terminalLog.scrollTop = terminalLog.scrollHeight;
    while (terminalLog.children.length > 40) {
      terminalLog.removeChild(terminalLog.firstChild);
    }
  }

  // Request Generator Loop
  setInterval(() => {
    const arrivals = Math.round(rps / 5);
    for (let i = 0; i < arrivals; i++) {
      totalRequests++;
      const reqId = Math.floor(Math.random() * 90000) + 10000;
      const effectivePool = Math.max(0, maxPool - leakedConnections);

      if (activeConnections < effectivePool) {
        // Acquired connection immediately
        activeConnections++;
        setTimeout(() => {
          if (hasLeak && Math.random() < 0.08 && leakedConnections < maxPool) {
            leakedConnections++;
            logTerminal(`[ERR] Worker #tx-${reqId} unhandled rejection. Leaked conn #L${leakedConnections}/${maxPool}`);
          }
          activeConnections = Math.max(0, activeConnections - 1);
        }, queryTime + (Math.random() * 40 - 20));
      } else {
        // Enqueue or drop
        if (queue.length < 50) {
          queue.push({ id: reqId, start: Date.now() });
        } else {
          errorCount++;
          if (Math.random() < 0.2) {
            logTerminal(`[CRIT] HTTP 504 Gateway Timeout: DB pool exhausted (${maxPool}/${maxPool}). Req #${reqId} rejected.`);
          }
        }
      }
    }

    // Process queued requests
    while (queue.length > 0 && activeConnections < Math.max(0, maxPool - leakedConnections)) {
      const item = queue.shift();
      activeConnections++;
      const waitTime = Date.now() - item.start;
      p99Latency = Math.min(6000, Math.round(queryTime + waitTime * 1.5));
      setTimeout(() => {
        activeConnections = Math.max(0, activeConnections - 1);
      }, queryTime);
    }

    if (queue.length === 0) {
      p99Latency = Math.max(12, Math.round(queryTime * 1.08 + (Math.random() * 6)));
    } else {
      p99Latency = Math.min(8000, 350 + (queue.length * 85));
    }

    // Update UI Metrics
    if (activeConnDisplay) activeConnDisplay.textContent = `${activeConnections + leakedConnections} / ${maxPool}`;
    if (queueDepthDisplay) {
      queueDepthDisplay.textContent = queue.length;
      queueDepthDisplay.style.color = queue.length > 15 ? '#f85149' : (queue.length > 0 ? '#d29922' : '#3fb950');
    }
    if (p99Display) {
      p99Display.textContent = `${p99Latency} ms`;
      p99Display.style.color = p99Latency > 800 ? '#f85149' : (p99Latency > 200 ? '#d29922' : '#38bdf8');
    }
    if (errorRateDisplay) {
      const rate = totalRequests > 0 ? ((errorCount / totalRequests) * 100).toFixed(1) : '0.0';
      errorRateDisplay.textContent = `${rate}%`;
      errorRateDisplay.style.color = parseFloat(rate) > 0.5 ? '#f85149' : '#3fb950';
    }
  }, 200);

  // Render Canvas
  function draw() {
    const rect = canvas.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;

    ctx.clearRect(0, 0, w, h);

    // Background Grid
    ctx.strokeStyle = '#161b22';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Draw Connection Slots (Grid of Pods)
    const totalSlots = maxPool;
    const cols = Math.min(10, Math.ceil(Math.sqrt(totalSlots * 2)));
    const rows = Math.ceil(totalSlots / cols);
    const slotSize = Math.min(26, Math.floor((w * 0.45) / cols));
    const startX = 30;
    const startY = 50;

    // Header label
    ctx.fillStyle = '#8b949e';
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.fillText(`POSTGRES POOL SLOTS (Cap: ${maxPool})`, startX, startY - 18);

    for (let i = 0; i < totalSlots; i++) {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const px = startX + col * (slotSize + 6);
      const py = startY + row * (slotSize + 6);

      let slotColor = '#21262d'; // idle
      let borderColor = '#30363d';

      if (i < leakedConnections) {
        slotColor = '#7f1d1d'; // leaked (dark red)
        borderColor = '#ef4444';
      } else if (i < leakedConnections + activeConnections) {
        slotColor = '#0369a1'; // busy (cyan)
        borderColor = '#38bdf8';
      }

      ctx.fillStyle = slotColor;
      ctx.fillRect(px, py, slotSize, slotSize);
      ctx.strokeStyle = borderColor;
      ctx.lineWidth = 1.5;
      ctx.strokeRect(px, py, slotSize, slotSize);

      // Pulse highlight on active
      if (slotColor === '#0369a1') {
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(px + slotSize / 2, py + slotSize / 2, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Draw Waiting Request Queue
    const queueX = w * 0.58;
    const queueY = startY;
    ctx.fillStyle = '#8b949e';
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.fillText(`WAITING THREAD QUEUE (${queue.length})`, queueX, queueY - 18);

    const maxQueueVis = 32;
    const qCols = 4;
    for (let i = 0; i < Math.min(queue.length, maxQueueVis); i++) {
      const qCol = i % qCols;
      const qRow = Math.floor(i / qCols);
      const qx = queueX + qCol * 28;
      const qy = queueY + qRow * 24;

      ctx.fillStyle = queue.length > 20 ? 'rgba(248, 81, 73, 0.2)' : 'rgba(210, 153, 34, 0.2)';
      ctx.strokeStyle = queue.length > 20 ? '#f85149' : '#d29922';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(qx, qy, 22, 16, 3);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = queue.length > 20 ? '#ff7b72' : '#e3b341';
      ctx.font = '9px "JetBrains Mono", monospace';
      ctx.fillText(`T${i + 1}`, qx + 4, qy + 11);
    }

    if (queue.length > maxQueueVis) {
      ctx.fillStyle = '#f85149';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillText(`+${queue.length - maxQueueVis} more threads waiting...`, queueX, queueY + 8 * 24 + 10);
    }

    // Health Status Stamp
    const isExhausted = (activeConnections + leakedConnections) >= maxPool;
    const statusText = isExhausted ? 'POOL EXHAUSTED (P99 SPIKE)' : 'HEALTHY (OPTIMAL RUNTIME)';
    const statusColor = isExhausted ? '#f85149' : '#3fb950';

    ctx.font = 'bold 11px "JetBrains Mono", monospace';
    ctx.fillStyle = statusColor;
    ctx.fillText(`STATUS: ${statusText}`, startX, h - 18);

    animationFrameId = requestAnimationFrame(draw);
  }

  draw();
};

// ============================================================================
// 2. AWS EGRESS COST CALCULATOR
// ============================================================================
SysCalculus.initEgressCalculator = function() {
  const egressSlider = document.getElementById('egressTbSlider');
  const egressValDisplay = document.getElementById('egressTbDisplay');
  const regionSelect = document.getElementById('awsRegionSelect');

  // Outputs
  const awsCostDisplay = document.getElementById('awsTotalCost');
  const r2CostDisplay = document.getElementById('r2TotalCost');
  const hetznerCostDisplay = document.getElementById('hetznerTotalCost');
  const savingsDisplay = document.getElementById('r2SavingsAmount');
  const savingsPercent = document.getElementById('r2SavingsPercent');
  const terraformSnippet = document.getElementById('terraformSnippet');

  if (!egressSlider) return;

  function calculate() {
    const tb = parseFloat(egressSlider.value);
    const gb = tb * 1024;
    const region = regionSelect ? regionSelect.value : 'us-east-1';

    if (egressValDisplay) {
      egressValDisplay.textContent = tb >= 1000 ? `${(tb / 1000).toFixed(1)} PB` : `${tb} TB`;
    }

    // AWS Tiered Pricing for Data Transfer Out (Internet)
    // First 100 GB/month: Free
    // Next 9.9 TB (up to 10 TB): $0.09 / GB
    // Next 40 TB (up to 50 TB): $0.085 / GB
    // Next 100 TB (up to 150 TB): $0.07 / GB
    // Greater than 150 TB: $0.05 / GB
    let awsCost = 0;
    let remainingGb = Math.max(0, gb - 100); // 100GB free tier

    // Tier 1: 9,900 GB @ $0.09
    const tier1 = Math.min(remainingGb, 9.9 * 1024);
    awsCost += tier1 * 0.09;
    remainingGb -= tier1;

    // Tier 2: 40 TB @ $0.085
    if (remainingGb > 0) {
      const tier2 = Math.min(remainingGb, 40 * 1024);
      awsCost += tier2 * 0.085;
      remainingGb -= tier2;
    }

    // Tier 3: 100 TB @ $0.07
    if (remainingGb > 0) {
      const tier3 = Math.min(remainingGb, 100 * 1024);
      awsCost += tier3 * 0.07;
      remainingGb -= tier3;
    }

    // Tier 4: Over 150 TB @ $0.05
    if (remainingGb > 0) {
      awsCost += remainingGb * 0.05;
    }

    // Regional multiplier adjustment (e.g. AP, SA are higher)
    if (region === 'ap-southeast-1' || region === 'ap-northeast-1') {
      awsCost *= 1.25;
    } else if (region === 'sa-east-1') {
      awsCost *= 1.55;
    }

    // Cloudflare R2: $0.00 Egress!
    // Storage cost only, but for egress pure calculation: $0
    const r2Cost = 0;

    // Hetzner Cloud: 20 TB included free per server, €1.00 (~$1.08) per TB thereafter
    const freeHetznerTb = 20;
    const billableHetznerTb = Math.max(0, tb - freeHetznerTb);
    const hetznerCost = billableHetznerTb * 1.08;

    const savings = Math.max(0, awsCost - r2Cost);
    const percent = awsCost > 0 ? ((savings / awsCost) * 100).toFixed(0) : 0;

    if (awsCostDisplay) awsCostDisplay.textContent = `$${Math.round(awsCost).toLocaleString()} /mo`;
    if (r2CostDisplay) r2CostDisplay.textContent = `$${r2Cost.toFixed(2)} /mo`;
    if (hetznerCostDisplay) hetznerCostDisplay.textContent = `$${Math.round(hetznerCost).toLocaleString()} /mo`;
    if (savingsDisplay) savingsDisplay.textContent = `$${Math.round(savings).toLocaleString()}`;
    if (savingsPercent) savingsPercent.textContent = `-${percent}%`;

    if (terraformSnippet) {
      terraformSnippet.value = `# Cloudflare R2 Zero-Egress Storage Bucket
resource "cloudflare_r2_bucket" "production_media" {
  account_id = var.cloudflare_account_id
  name       = "syscalculus-assets-${region}"
  location   = "auto" # Routed to closest edge POP
}

# AWS S3 Sync to Zero-Egress Mirror (Bypasses AWS Data Out)
resource "aws_s3_bucket" "source" {
  bucket = "primary-assets-origin"
}

# Calculated Monthly Egress Savings: $${Math.round(savings).toLocaleString()} USD/mo
# Egress Volume: ${tb} TB/month across ${region}`;
    }
  }

  egressSlider.addEventListener('input', calculate);
  if (regionSelect) regionSelect.addEventListener('change', calculate);
  calculate();
};

// ============================================================================
// 3. AIR-GAPPED ZERO-TRUST LOG SANITIZER
// ============================================================================
SysCalculus.initLogSanitizer = function() {
  const input = document.getElementById('logRawInput');
  const output = document.getElementById('logSanitizedOutput');
  const redactAws = document.getElementById('redactAwsKeys');
  const redactJwt = document.getElementById('redactJwt');
  const redactIps = document.getElementById('redactIps');
  const redactEmails = document.getElementById('redactEmails');
  const redactUris = document.getElementById('redactDbUris');

  const countDisplay = document.getElementById('redactedSecretsCount');
  const speedDisplay = document.getElementById('redactionTimeMs');
  const btnSample = document.getElementById('btnLoadSampleLog');
  const btnClear = document.getElementById('btnClearLog');

  if (!input || !output) return;

  const sampleLog = `2026-09-05 18:42:01.812 [ERROR] [auth.service] Failed login for user admin@cloudcorp.internal from 198.51.100.42: invalid credentials.
2026-09-05 18:42:02.104 [INFO] [s3.worker] Initializing AWS client with access key AKIAIOSFODNN7EXAMPLE and secret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY.
2026-09-05 18:42:03.490 [DEBUG] [db.connector] Connecting to postgres://prod_admin:sUp3rS3cr3tP@ss!@db.internal.cluster.local:5432/finance_db?sslmode=require
2026-09-05 18:42:04.221 [WARN] [gateway.api] Bearer token validation failed for token:
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
2026-09-05 18:42:05.610 [INFO] [payment.processor] Transaction processed for card 4532-1234-5678-9010 on billing server 10.244.3.189. Contact billing-ops@enterprise.com.`;

  function sanitize() {
    const t0 = performance.now();
    let text = input.value;
    let redactedCount = 0;

    if (!text.trim()) {
      output.value = '';
      if (countDisplay) countDisplay.textContent = '0';
      if (speedDisplay) speedDisplay.textContent = '0.0 ms';
      return;
    }

    // 1. AWS Access Key IDs
    if (!redactAws || redactAws.checked) {
      text = text.replace(/AKIA[0-9A-Z]{16}/g, () => {
        redactedCount++;
        return '[REDACTED_AWS_ACCESS_KEY]';
      });
      // AWS Secret Keys
      text = text.replace(/[0-9a-zA-Z/+]{40}(?=[^0-9a-zA-Z/+]|$)/g, (match) => {
        if (match.length === 40 && /[A-Z]/.test(match) && /[a-z]/.test(match) && /[0-9]/.test(match)) {
          redactedCount++;
          return '[REDACTED_AWS_SECRET_KEY]';
        }
        return match;
      });
    }

    // 2. JWTs (Header.Payload.Signature)
    if (!redactJwt || redactJwt.checked) {
      text = text.replace(/eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}/g, () => {
        redactedCount++;
        return '[REDACTED_JWT_TOKEN]';
      });
    }

    // 3. Database connection URI passwords
    if (!redactUris || redactUris.checked) {
      text = text.replace(/(postgres|mysql|mongodb|redis|amqp):\/\/[^:\s]+:([^@\s]+)@/g, (match, proto) => {
        redactedCount++;
        return `${proto}://user:[REDACTED_PASSWORD]@`;
      });
    }

    // 4. IP Addresses (IPv4)
    if (!redactIps || redactIps.checked) {
      text = text.replace(/\b(?!(127\.0\.0\.1|0\.0\.0\.0))\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, () => {
        redactedCount++;
        return '[REDACTED_IP]';
      });
    }

    // 5. Emails
    if (!redactEmails || redactEmails.checked) {
      text = text.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, () => {
        redactedCount++;
        return '[REDACTED_EMAIL]';
      });
    }

    // Credit cards
    text = text.replace(/\b(?:\d{4}[-\s]?){3}\d{4}\b/g, () => {
      redactedCount++;
      return '[REDACTED_CREDIT_CARD]';
    });

    const elapsed = (performance.now() - t0).toFixed(1);
    output.value = text;
    if (countDisplay) countDisplay.textContent = redactedCount;
    if (speedDisplay) speedDisplay.textContent = `${elapsed} ms`;
  }

  input.addEventListener('input', sanitize);
  [redactAws, redactJwt, redactIps, redactEmails, redactUris].forEach(checkbox => {
    if (checkbox) checkbox.addEventListener('change', sanitize);
  });

  if (btnSample) {
    btnSample.addEventListener('click', () => {
      input.value = sampleLog;
      sanitize();
    });
  }
  if (btnClear) {
    btnClear.addEventListener('click', () => {
      input.value = '';
      output.value = '';
      if (countDisplay) countDisplay.textContent = '0';
      if (speedDisplay) speedDisplay.textContent = '0.0 ms';
    });
  }

  // Initial run if prefilled
  if (input.value) sanitize();
};

// ============================================================================
// 4. CRONTAB VISUALIZER & 24-HOUR HEATMAP
// ============================================================================
SysCalculus.initCronVisualizer = function() {
  const cronInput = document.getElementById('cronExpressionInput');
  const humanDisplay = document.getElementById('cronHumanReadable');
  const heatmapContainer = document.getElementById('cronHeatmapGrid');
  const nextRunsList = document.getElementById('cronNextRunsList');
  const presetBtns = document.querySelectorAll('.cron-preset-btn');

  if (!cronInput) return;

  function parseField(field, min, max) {
    if (field === '*') {
      const arr = [];
      for (let i = min; i <= max; i++) arr.push(i);
      return arr;
    }
    if (field.startsWith('*/')) {
      const step = parseInt(field.replace('*/', ''), 10);
      const arr = [];
      for (let i = min; i <= max; i += step) arr.push(i);
      return arr;
    }
    if (field.includes(',')) {
      return field.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
    }
    if (field.includes('-')) {
      const [start, end] = field.split('-').map(s => parseInt(s.trim(), 10));
      const arr = [];
      for (let i = start; i <= end; i++) arr.push(i);
      return arr;
    }
    const val = parseInt(field, 10);
    return isNaN(val) ? [] : [val];
  }

  function update() {
    const expr = cronInput.value.trim();
    const parts = expr.split(/\s+/);

    if (parts.length !== 5) {
      if (humanDisplay) humanDisplay.textContent = 'Invalid format: Exactly 5 parts required (minute hour dom month dow)';
      return;
    }

    const [minStr, hrStr, domStr, monStr, dowStr] = parts;
    const minutes = parseField(minStr, 0, 59);
    const hours = parseField(hrStr, 0, 23);

    // Human translation
    let desc = `Runs at `;
    if (minStr === '*') desc += `every minute`;
    else if (minStr.startsWith('*/')) desc += `every ${minStr.replace('*/', '')} minutes`;
    else desc += `minute ${minStr}`;

    if (hrStr === '*') desc += `, every hour`;
    else if (hrStr.startsWith('*/')) desc += `, every ${hrStr.replace('*/', '')} hours`;
    else desc += `, past hour ${hrStr}:00`;

    if (humanDisplay) humanDisplay.textContent = desc;

    // Render 24-hour Heatmap
    if (heatmapContainer) {
      heatmapContainer.innerHTML = '';
      for (let h = 0; h < 24; h++) {
        const hourCell = document.createElement('div');
        hourCell.className = 'cron-hour-box';
        const isHourActive = hours.includes(h);

        let runsInHour = 0;
        if (isHourActive) {
          runsInHour = minutes.length;
        }

        hourCell.title = `${String(h).padStart(2, '0')}:00 - ${runsInHour} execution(s)`;
        hourCell.innerHTML = `<span class="hour-label">${String(h).padStart(2, '0')}h</span><span class="count-label">${runsInHour}x</span>`;

        if (runsInHour > 30) {
          hourCell.style.background = '#238636';
          hourCell.style.borderColor = '#3fb950';
          hourCell.style.color = '#fff';
        } else if (runsInHour > 0) {
          hourCell.style.background = '#0e4429';
          hourCell.style.borderColor = '#238636';
          hourCell.style.color = '#7ee787';
        } else {
          hourCell.style.background = '#161b22';
          hourCell.style.borderColor = '#21262d';
          hourCell.style.color = '#6e7681';
        }

        heatmapContainer.appendChild(hourCell);
      }
    }

    // Compute Next 5 Runs
    if (nextRunsList) {
      nextRunsList.innerHTML = '';
      let now = new Date();
      let found = 0;
      let check = new Date(now.getTime() + 60000);

      while (found < 5 && (check - now) < 30 * 86400000) {
        if (hours.includes(check.getHours()) && minutes.includes(check.getMinutes())) {
          found++;
          const li = document.createElement('li');
          li.className = 'next-run-item';
          li.innerHTML = `<strong>#${found}</strong> <code>${check.toUTCString().replace('GMT', 'UTC')}</code>`;
          nextRunsList.appendChild(li);
        }
        check = new Date(check.getTime() + 60000);
      }
    }
  }

  cronInput.addEventListener('input', update);
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      cronInput.value = btn.dataset.cron;
      update();
    });
  });

  update();
};

// ============================================================================
// 5. DOCKER RUN TO DOCKER COMPOSE CONVERTER
// ============================================================================
SysCalculus.initDockerConverter = function() {
  const input = document.getElementById('dockerRunInput');
  const output = document.getElementById('dockerComposeOutput');
  const btnConvert = document.getElementById('btnDockerConvert');

  if (!input || !output) return;

  function convert() {
    const raw = input.value.trim();
    if (!raw) {
      output.value = '';
      return;
    }

    let serviceName = 'app';
    let image = 'nginx:alpine';
    let ports = [];
    let volumes = [];
    let environment = [];
    let restart = 'unless-stopped';

    // Regex parsing for docker run flags
    const nameMatch = raw.match(/--name\s+([^\s]+)/);
    if (nameMatch) serviceName = nameMatch[1];

    const portMatches = [...raw.matchAll(/-p\s+([^\s]+)|--publish\s+([^\s]+)/g)];
    portMatches.forEach(m => ports.push(m[1] || m[2]));

    const volMatches = [...raw.matchAll(/-v\s+([^\s]+)|--volume\s+([^\s]+)/g)];
    volMatches.forEach(m => volumes.push(m[1] || m[2]));

    const envMatches = [...raw.matchAll(/-e\s+([^\s]+)|--env\s+([^\s]+)/g)];
    envMatches.forEach(m => environment.push(m[1] || m[2]));

    const restartMatch = raw.match(/--restart\s+([^\s]+)/);
    if (restartMatch) restart = restartMatch[1];

    // Detect image (usually the last word or after options)
    const tokens = raw.replace(/\\/g, ' ').split(/\s+/);
    for (let i = tokens.length - 1; i >= 0; i--) {
      const t = tokens[i];
      if (t && !t.startsWith('-') && tokens[i - 1] !== '-p' && tokens[i - 1] !== '-v' && tokens[i - 1] !== '-e' && tokens[i - 1] !== '--name' && tokens[i - 1] !== '--restart' && t !== 'docker' && t !== 'run') {
        image = t;
        break;
      }
    }

    let yaml = `version: "3.8"\n\nservices:\n  ${serviceName}:\n    image: ${image}\n    container_name: ${serviceName}\n    restart: ${restart}\n`;

    if (ports.length > 0) {
      yaml += `    ports:\n`;
      ports.forEach(p => yaml += `      - "${p}"\n`);
    }

    if (environment.length > 0) {
      yaml += `    environment:\n`;
      environment.forEach(e => yaml += `      - ${e}\n`);
    }

    if (volumes.length > 0) {
      yaml += `    volumes:\n`;
      volumes.forEach(v => yaml += `      - ${v}\n`);
    }

    yaml += `    security_opt:\n      - no-new-privileges:true\n`;
    yaml += `    logging:\n      driver: "json-file"\n      options:\n        max-size: "10m"\n        max-file: "3"\n`;

    output.value = yaml;
  }

  input.addEventListener('input', convert);
  if (btnConvert) btnConvert.addEventListener('click', convert);
  if (input.value) convert();
};

// ============================================================================
// 6. LLM VRAM & QUANTIZATION SIZER
// ============================================================================
SysCalculus.initLlmVramSizer = function() {
  const paramSlider = document.getElementById('llmParamSlider');
  const paramDisplay = document.getElementById('llmParamDisplay');
  const quantSelect = document.getElementById('llmQuantSelect');
  const ctxSelect = document.getElementById('llmCtxSelect');

  const totalVramDisplay = document.getElementById('llmTotalVram');
  const weightsVramDisplay = document.getElementById('llmWeightsVram');
  const kvVramDisplay = document.getElementById('llmKvVram');
  const hardwareBadge = document.getElementById('llmHardwareRec');

  if (!paramSlider) return;

  function calculate() {
    const paramsBillion = parseFloat(paramSlider.value);
    const quantBits = parseFloat(quantSelect ? quantSelect.value : 4);
    const ctxLength = parseInt(ctxSelect ? ctxSelect.value : 8192, 10);

    if (paramDisplay) paramDisplay.textContent = `${paramsBillion}B Parameters`;

    // Weights VRAM (GB) = (Params * (bits / 8)) * 1.15 (overhead)
    const weightsGb = (paramsBillion * 1e9 * (quantBits / 8)) / (1024 * 1024 * 1024);

    // KV Cache VRAM (GB)
    // Formula: 2 * n_layers * n_heads * head_dim * context * precision
    // Standard approx for LLaMA architecture: ~0.5 MB per 1k context per Billion params at 16-bit
    const kvGb = (ctxLength / 1000) * (paramsBillion * 0.04) * 0.12;

    // CUDA Context & Activation Overhead
    const overheadGb = Math.max(1.2, paramsBillion * 0.05);

    const totalVram = weightsGb + kvGb + overheadGb;

    if (totalVramDisplay) totalVramDisplay.textContent = `${totalVram.toFixed(1)} GB`;
    if (weightsVramDisplay) weightsVramDisplay.textContent = `${weightsGb.toFixed(1)} GB`;
    if (kvVramDisplay) kvVramDisplay.textContent = `${kvGb.toFixed(2)} GB`;

    if (hardwareBadge) {
      let rec = '';
      let badgeClass = 'badge-green';
      if (totalVram <= 8) {
        rec = 'Consumer GPU (RTX 3070 / 4060 8GB)';
      } else if (totalVram <= 16) {
        rec = 'Prosumer GPU (RTX 4080 / Apple M2 Pro 16GB)';
      } else if (totalVram <= 24) {
        rec = 'Workstation GPU (1x RTX 3090 / 4090 24GB)';
      } else if (totalVram <= 48) {
        rec = 'Dual GPU (2x RTX 3090 / 1x A6000 48GB)';
      } else if (totalVram <= 80) {
        rec = 'Datacenter GPU (1x NVIDIA A100 / H100 80GB)';
      } else {
        const gpuCount = Math.ceil(totalVram / 80);
        rec = `Multi-GPU Cluster (${gpuCount}x NVIDIA H100 80GB SXM)`;
        badgeClass = 'badge-red';
      }
      hardwareBadge.textContent = rec;
    }
  }

  paramSlider.addEventListener('input', calculate);
  if (quantSelect) quantSelect.addEventListener('change', calculate);
  if (ctxSelect) ctxSelect.addEventListener('change', calculate);
  calculate();
};

// Global Bootstrapper on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  SysCalculus.initDbPoolSimulator();
  SysCalculus.initEgressCalculator();
  SysCalculus.initLogSanitizer();
  SysCalculus.initCronVisualizer();
  SysCalculus.initDockerConverter();
  SysCalculus.initLlmVramSizer();
});
