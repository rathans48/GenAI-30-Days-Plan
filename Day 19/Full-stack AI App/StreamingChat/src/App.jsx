import React, { useState, useEffect } from 'react';

export default function StreamingChat() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('devmind_token') || '');
  const [authStatus, setAuthStatus] = useState('Checking session...');

  // Verify token state on load
  useEffect(() => {
    if (token) {
      setAuthStatus('🔒 Authenticated (Session Active)');
    } else {
      setAuthStatus('🔓 Unauthenticated (No Token Generated)');
    }
  }, [token]);

  // 1. Explicit Authentication Handler
  const handleGenerateToken = async () => {
    try {
      setAuthStatus('⏳ Fetching JWT Handshake...');
      const response = await fetch('http://127.0.0.1:8000/mock-token');
      if (!response.ok) throw new Error('Token endpoint unreachable');
      
      const data = await response.json();
      localStorage.setItem('devmind_token', data.access_token);
      setToken(data.access_token);
      console.log("💾 JWT Token Saved Successfully:", data.access_token);
    } catch (err) {
      console.error("❌ Auth Error:", err);
      setAuthStatus('⚠️ Authentication Failed (Is your FastAPI running?)');
    }
  };

  // 2. Clear Session Context
  const handleLogout = () => {
    localStorage.removeItem('devmind_token');
    setToken('');
    setResponse('');
  };

  // 3. Authenticated Stream Handler
  const handleQuery = () => {
    if (!prompt) return;
    if (!token) {
      alert("Access Denied: Please generate an authentication token first.");
      return;
    }

    setResponse('');
    setIsLoading(true);
    console.log("📡 Opening Server-Sent Events (SSE) connection stream...");

    // Build the authenticated streaming target URL
    const streamUrl = `http://127.0.0.1:8000/api/stream-query?prompt=${encodeURIComponent(prompt)}&token=${token}`;
    const eventSource = new EventSource(streamUrl);

    // Capture incoming tokens
    eventSource.onmessage = (event) => {
      const cleanToken = event.data;
      setResponse((prev) => prev + cleanToken);
    };

    // Trace stream completion or error blocks
    eventSource.onerror = (error) => {
      console.log("🔒 Stream closed by server or token window expired.");
      eventSource.close();
      setIsLoading(false);
    };
  };

  return (
    <div style={{
      padding: '2.5rem', 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
      backgroundColor: '#111827', 
      minHeight: '100vh',
      color: '#f9fafb'
    }}>
      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: '#60a5fa' }}>
          🧠 DevMind Full-Stack AI Core
        </h2>

        {/* --- AUTHENTICATION STATE CARD --- */}
        <div style={{
          background: '#1f2937',
          padding: '1.25rem',
          borderRadius: '8px',
          border: '1px solid #374151',
          marginBottom: '2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '0.875rem', color: '#9ca3af', display: 'block' }}>SECURITY PROFILE</span>
            <strong style={{ color: token ? '#34d399' : '#f87171' }}>{authStatus}</strong>
          </div>
          <div>
            {!token ? (
              <button onClick={handleGenerateToken} style={{
                background: '#2563eb', color: '#fff', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', cursor: 'pointer', fontWeight: '5px'
              }}>Generate JWT Token</button>
            ) : (
              <button onClick={handleLogout} style={{
                background: '#dc2626', color: '#fff', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', cursor: 'pointer'
              }}>Clear Session</button>
            )}
          </div>
        </div>

        {/* --- QUERY ROW --- */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask your model a technical question..."
            disabled={!token || isLoading}
            style={{
              flex: 1, padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#374151', color: '#fff', fontSize: '1rem'
            }}
          />
          <button 
            onClick={handleQuery} 
            disabled={isLoading || !token} 
            style={{
              background: isLoading || !token ? '#4b5563' : '#10b981', color: '#fff', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
            }}
          >
            {isLoading ? 'Streaming...' : 'Query Engine'}
          </button>
        </div>

        {/* --- STREAMING TERMINAL CANVAS --- */}
        <div style={{
          background: '#0f172a',
          padding: '1.5rem',
          borderRadius: '8px',
          border: '1px solid #1e293b',
          minHeight: '150px',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.6)'
        }}>
          <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>
            TERMINAL COMPILER STREAM_OUTPUT:
          </span>
          <p style={{ margin: 0, color: '#e2e8f0', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
            {response || (token ? 'Awaiting prompt execution...' : 'Please authenticate above to unlock query gateway.')}
          </p>
        </div>
      </div>
    </div>
  );
}