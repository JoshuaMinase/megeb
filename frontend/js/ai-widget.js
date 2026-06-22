// Megeb AI — "What Ethiopian food can I make with these ingredients?"
(function () {
  const API = 'http://localhost:8000';

  const css = `
    #ai-btn {
      position: fixed; bottom: 28px; right: 28px; z-index: 9000;
      width: 60px; height: 60px; border-radius: 50%;
      background: #FF9124; border: none; cursor: pointer;
      box-shadow: 0 4px 20px rgba(255,145,36,.5);
      font-size: 26px; display: flex; align-items: center; justify-content: center;
      transition: transform .2s;
    }
    #ai-btn:hover { transform: scale(1.1); }
    #ai-panel {
      position: fixed; bottom: 100px; right: 28px; z-index: 9000;
      width: 340px; background: #fff; border-radius: 20px;
      box-shadow: 0 8px 40px rgba(0,0,0,.18);
      display: flex; flex-direction: column; overflow: hidden;
      transform: scale(.9) translateY(20px); opacity: 0; pointer-events: none;
      transition: transform .25s, opacity .25s;
    }
    #ai-panel.open { transform: scale(1) translateY(0); opacity: 1; pointer-events: all; }
    .ai-header {
      background: #FF9124; color: #fff; padding: 16px 18px;
      display: flex; justify-content: space-between; align-items: center;
    }
    .ai-header h3 { font-family: 'Times New Roman',serif; font-size: 17px; margin: 0; }
    .ai-header small { font-family: Georgia,serif; font-size: 11px; opacity: .85; }
    .ai-close { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
    .ai-body { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
    .ai-body label { font-family: Georgia,serif; font-size: 13px; color: #555; }
    .ai-body textarea {
      width: 100%; padding: 10px 12px; border: 2px solid #e8e8e8; border-radius: 10px;
      font-family: Georgia,serif; font-size: 14px; resize: none; outline: none;
      color: #263020; box-sizing: border-box; transition: border-color .2s;
    }
    .ai-body textarea:focus { border-color: #FF9124; }
    .ai-ask-btn {
      padding: 12px; background: #FF9124; color: #fff; border: none;
      border-radius: 10px; font-family: 'Times New Roman',serif; font-size: 16px;
      cursor: pointer; transition: background .2s;
    }
    .ai-ask-btn:hover { background: #263020; }
    .ai-ask-btn:disabled { background: #ddd; cursor: not-allowed; }
    .ai-result {
      font-family: Georgia,serif; font-size: 14px; color: #263020;
      line-height: 1.6; max-height: 300px; overflow-y: auto;
      border-top: 1px solid #f0f0f0; padding-top: 12px; display: none;
      white-space: pre-wrap;
    }
  `;

  document.head.insertAdjacentHTML('beforeend', `<style>${css}</style>`);
  document.body.insertAdjacentHTML('beforeend', `
    <button id="ai-btn" onclick="toggleAI()" title="What can I cook?">🍲</button>
    <div id="ai-panel">
      <div class="ai-header">
        <div>
          <h3>🇪🇹 What can I cook?</h3>
          <small>Enter your ingredients — get Ethiopian recipes</small>
        </div>
        <button class="ai-close" onclick="toggleAI()">×</button>
      </div>
      <div class="ai-body">
        <label>List the ingredients you have:</label>
        <textarea id="ai-ingredients" rows="3" placeholder="e.g. onion, berbere, lentils, garlic"></textarea>
        <button class="ai-ask-btn" id="ai-ask-btn" onclick="askAI()">Find Ethiopian Recipes →</button>
        <div class="ai-result" id="ai-result"></div>
      </div>
    </div>
  `);

  window.toggleAI = function () {
    document.getElementById('ai-panel').classList.toggle('open');
  };

  window.askAI = async function () {
    const ingredients = document.getElementById('ai-ingredients').value.trim();
    if (!ingredients) return;

    const btn    = document.getElementById('ai-ask-btn');
    const result = document.getElementById('ai-result');
    btn.disabled    = true;
    btn.textContent = 'Thinking...';
    result.style.display = 'none';
    result.textContent   = '';

    try {
      const token = localStorage.getItem('megeb_token');
      const res = await fetch(`${API}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ message: ingredients }),
      });
      const data = await res.json();

      result.textContent   = res.ok ? (data.reply || 'No suggestions found.') : '⚠️ AI unavailable. Make sure GROQ_API_KEY is set in backend/.env';
      result.style.display = 'block';
    } catch {
      result.textContent   = 'Connection error — is the server running?';
      result.style.display = 'block';
    }

    btn.disabled    = false;
    btn.textContent = 'Find Ethiopian Recipes →';
  };
})();
