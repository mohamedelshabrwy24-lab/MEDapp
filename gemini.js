// MedRef - Client API Layer (Secure Gateway Integration)
// All research calls route directly through /api/research on the secure local gateway.
// Zero API keys are stored in browser localStorage or transmitted from the client.

class GeminiAPI {
  constructor() {
    this.serverReady = false;
  }

  async checkServerHealth() {
    try {
      const res = await fetch('/api/health', { method: 'GET' });
      if (res.ok) {
        const data = await res.json();
        this.serverReady = data.credentials?.gemini_configured || false;
        return data;
      }
    } catch (e) {
      console.warn('[MedRef Gateway] Server health check failed:', e.message);
    }
    return { status: 'offline', credentials: { gemini_configured: false } };
  }

  async saveKeyToServer(geminiKey, tavilyKey = '') {
    const cleanKey = (geminiKey || '').trim();
    if (!cleanKey) {
      throw new Error('Please enter a valid API key.');
    }

    const res = await fetch('/api/save_keys', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gemini_key: cleanKey,
        tavily_key: (tavilyKey || '').trim()
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    this.serverReady = true;
    return data;
  }

  async searchCondition(condition, setting = 'emergency') {
    const cleanCondition = (condition || '').trim();
    if (!cleanCondition) {
      throw new Error('Please enter a valid condition name.');
    }

    console.log(`[MedRef Engine] 🛡️ Sending research query for "${cleanCondition}" to /api/research...`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000);

    try {
      const res = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          condition: cleanCondition,
          setting: setting
        })
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        if (errData.error === 'MISSING_API_KEY') {
          throw new Error('MISSING_SERVER_API_KEY');
        }
        throw new Error(errData.message || `Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error('Network request timed out. Please try again or use the Wi-Fi link.');
      }
      throw err;
    }
  }

  // Compatibility stubs
  hasApiKey() { return this.serverReady; }
  isReady() { return this.serverReady; }
  setApiKey() { /* No-op: handled server-side in .env */ }
  getApiKey() { return ''; }
}

const geminiAPI = new GeminiAPI();
