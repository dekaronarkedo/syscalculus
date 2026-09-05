/**
 * SysCalculus - Client-Side App Helpers
 * Search palette, clipboard helpers, and fast tag filter.
 */

(function() {
  'use strict';

  // 1. Tag Filtering
  const filterBtns = document.querySelectorAll('.tag-btn');
  const cards = document.querySelectorAll('.card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');

      cards.forEach(card => {
        const cat = card.getAttribute('data-cat');
        if (filter === 'all' || cat === filter) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // 2. Clipboard Copy Helpers
  document.addEventListener('click', function(e) {
    const copyBtn = e.target.closest('.copy-code-btn, .btn-copy');
    if (!copyBtn) return;

    let targetSelector = copyBtn.getAttribute('data-copy-target');
    let textToCopy = '';

    if (targetSelector) {
      const targetEl = document.querySelector(targetSelector);
      if (targetEl) {
        textToCopy = targetEl.value !== undefined ? targetEl.value : targetEl.innerText;
      }
    } else {
      const container = copyBtn.closest('.workbench-card, pre, code');
      if (container) {
        const pre = container.querySelector('pre, code, textarea');
        if (pre) textToCopy = pre.value !== undefined ? pre.value : pre.innerText;
      }
    }

    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy.trim()).then(() => {
        const origText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span style="color:#3fb950">✓ Copied</span>';
        setTimeout(() => {
          copyBtn.innerHTML = origText;
        }, 1800);
      }).catch(err => {
        console.error('Clipboard copy error: ', err);
      });
    }
  });

  // 3. Quick Search Palette (Ctrl+K or Cmd+K)
  const searchModal = document.getElementById('searchModal');
  const searchInput = document.getElementById('modalSearchInput');
  const searchResults = document.getElementById('modalSearchResults');
  const navSearchBtn = document.querySelector('.search-trigger');

  const toolsIndex = [
    { title: 'Database Deadlock & Connection Pool Simulator', path: '/tools/db-deadlock-simulator.html', tag: 'PostgreSQL / SRE', desc: 'Simulate PostgreSQL connection starvation, queue buildup and P99 latency spikes in real-time.' },
    { title: 'AWS Egress Cost Calculator & Zero-Egress Architecture', path: '/tools/aws-egress-calculator.html', tag: 'Cloud / FinOps', desc: 'Calculate AWS NAT Gateway and Internet egress gouging vs Cloudflare R2 and Hetzner.' },
    { title: 'Zero-Trust Air-Gapped Log Sanitizer', path: '/tools/airgapped-log-sanitizer.html', tag: 'Security / DevOps', desc: 'Scrub AWS keys, JWT tokens, IP addresses and database passwords client-side with 0 network latency.' },
    { title: 'Linux Crontab Visualizer & 24h Execution Heatmap', path: '/tools/crontab-visualizer.html', tag: 'Linux / DevOps', desc: 'Interactive 5-part cron syntax parser with 24-hour heatmap schedule and next 10 runs.' },
    { title: 'Docker Run to Production Docker Compose Converter', path: '/tools/docker-compose-converter.html', tag: 'Containers / Docker', desc: 'Convert messy docker run terminal commands into clean, security-hardened docker-compose.yml.' },
    { title: 'LLM VRAM & Quantization Sizer (FP16/INT8/INT4)', path: '/tools/llm-vram-sizer.html', tag: 'AI / MLOps', desc: 'Compute weights, KV cache, and CUDA overhead for LLaMA 3, DeepSeek, and Mistral models.' }
  ];

  function openSearch() {
    if (!searchModal) return;
    searchModal.classList.add('active');
    if (searchInput) {
      searchInput.value = '';
      searchInput.focus();
      renderSearchResults('');
    }
  }

  function closeSearch() {
    if (!searchModal) return;
    searchModal.classList.remove('active');
  }

  function renderSearchResults(query) {
    if (!searchResults) return;
    const q = query.toLowerCase().trim();
    const filtered = toolsIndex.filter(t => 
      t.title.toLowerCase().includes(q) || 
      t.tag.toLowerCase().includes(q) || 
      t.desc.toLowerCase().includes(q)
    );

    if (filtered.length === 0) {
      searchResults.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No tools found matching query. Press ESC to close.</div>';
      return;
    }

    searchResults.innerHTML = filtered.map((item, idx) => `
      <a href="${item.path}" class="search-result-item ${idx === 0 ? 'focused' : ''}">
        <div style="margin-bottom: 0.25rem;"><span class="result-badge">${item.tag}</span></div>
        <div class="result-title">${item.title}</div>
        <div class="result-desc">${item.desc}</div>
      </a>
    `).join('');
  }

  if (navSearchBtn) navSearchBtn.addEventListener('click', openSearch);

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (searchModal && searchModal.classList.contains('active')) {
        closeSearch();
      } else {
        openSearch();
      }
    }
    if (e.key === 'Escape' && searchModal && searchModal.classList.contains('active')) {
      closeSearch();
    }
  });

  if (searchModal) {
    searchModal.addEventListener('click', (e) => {
      if (e.target === searchModal) closeSearch();
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      renderSearchResults(e.target.value);
    });
  }

})();
