import { useState, useEffect } from 'react'
import { getTags, updateTags, getMe, updateSettings, getLLMConfig, updateLLMConfig, testLLMConnection, analyzeAllItems } from '../api.js'

export default function Settings() {
  const [tags, setTags] = useState([])
  const [newTag, setNewTag] = useState('')
  const [receiveDigest, setReceiveDigest] = useState(true)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  
  const [llmBaseUrl, setLlmBaseUrl] = useState('')
  const [llmApiKey, setLlmApiKey] = useState('')
  const [llmModelName, setLlmModelName] = useState('')
  const [llmEmbeddingModel, setLlmEmbeddingModel] = useState('')
  const [llmConfigured, setLlmConfigured] = useState(false)
  const [testingConnection, setTestingConnection] = useState(false)
  const [connectionResult, setConnectionResult] = useState(null)
  const [savingLLM, setSavingLLM] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const [tagsRes, meRes, llmRes] = await Promise.all([
          getTags(), 
          getMe(),
          getLLMConfig().catch(() => ({ data: { configured: false } }))
        ])
        setTags(tagsRes.data.map(t => t.name))
        setReceiveDigest(meRes.data.receive_digest)
        
        if (llmRes.data) {
          setLlmBaseUrl(llmRes.data.base_url || '')
          setLlmModelName(llmRes.data.model_name || '')
          setLlmEmbeddingModel(llmRes.data.embedding_model || '')
          setLlmConfigured(llmRes.data.configured || false)
        }
      } catch {
        setError('Failed to load settings.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  function addTag() {
    const t = newTag.trim().toLowerCase()
    if (!t || tags.includes(t)) { setNewTag(''); return }
    setTags(prev => [...prev, t])
    setNewTag('')
  }

  function removeTag(tag) {
    setTags(prev => prev.filter(t => t !== tag))
  }

  async function handleSave(e) {
    e.preventDefault()
    setMsg('')
    setError('')
    setSaving(true)
    try {
      await updateTags(tags)
      await updateSettings({ receive_digest: receiveDigest })
      setMsg('Settings saved!')
    } catch {
      setError('Failed to save settings.')
    } finally {
      setSaving(false)
    }
  }

  function handleTagKeyDown(e) {
    if (e.key === 'Enter') { e.preventDefault(); addTag() }
  }

  async function handleSaveLLM() {
    setError('')
    setMsg('')
    setSavingLLM(true)
    setConnectionResult(null)
    try {
      const payload = {
        base_url: llmBaseUrl || null,
        api_key: llmApiKey || null,
        model_name: llmModelName || null,
        embedding_model: llmEmbeddingModel || null,
      }
      await updateLLMConfig(payload)
      setLlmConfigured(!!llmApiKey)
      setMsg('LLM configuration saved!')
    } catch {
      setError('Failed to save LLM configuration.')
    } finally {
      setSavingLLM(false)
    }
  }

  async function handleTestConnection() {
    setTestingConnection(true)
    setConnectionResult(null)
    try {
      const res = await testLLMConnection()
      setConnectionResult({
        success: res.data.success,
        message: res.data.message,
      })
    } catch (err) {
      setConnectionResult({
        success: false,
        message: err.response?.data?.detail || 'Connection test failed',
      })
    } finally {
      setTestingConnection(false)
    }
  }

  async function handleAnalyzeAll() {
    setAnalyzing(true)
    setError('')
    setMsg('')
    try {
      const res = await analyzeAllItems()
      setMsg(`Analyzed ${res.data.analyzed} items out of ${res.data.total}.`)
    } catch {
      setError('Failed to analyze items.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <div className="spinner" />

  return (
    <main className="page">
      <div className="section-title">Settings</div>
      <div className="section-sub">Manage your interest tags, notification preferences, and LLM configuration</div>

      <form className="card" onSubmit={handleSave}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 8 }}>Interest Tags</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 12 }}>
          Add topics you care about (e.g. <em>rust</em>, <em>ai</em>, <em>frontend</em>). Feed items are ranked by how well they match.
        </p>

        <div className="tag-list">
          {tags.length === 0 && (
            <span style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>No tags yet — add some below</span>
          )}
          {tags.map(t => (
            <span key={t} className="tag-removable">
              {t}
              <button type="button" className="tag-remove-btn" onClick={() => removeTag(t)} title="Remove tag">×</button>
            </span>
          ))}
        </div>

        <div className="tag-input-row">
          <input
            type="text"
            placeholder="Add tag and press Enter or +"
            value={newTag}
            onChange={e => setNewTag(e.target.value)}
            onKeyDown={handleTagKeyDown}
          />
          <button type="button" className="btn btn-outline" onClick={addTag}>+ Add</button>
        </div>

        <div className="toggle-row">
          <div>
            <div className="toggle-label">Weekly Digest Email</div>
            <div className="toggle-sublabel">Receive a personalized weekly roundup every Monday</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={receiveDigest}
              onChange={e => setReceiveDigest(e.target.checked)}
            />
            <span className="slider" />
          </label>
        </div>

        {error && <p className="error-msg">{error}</p>}
        {msg && <p className="success-msg">{msg}</p>}

        <div style={{ marginTop: 20 }}>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Save Settings'}
          </button>
        </div>
      </form>

      <div className="card llm-config-section">
        <h3>
          <span>🧠</span>
          LLM Configuration (Semantic Analysis)
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 16 }}>
          Configure an OpenAI-compatible API for automatic project tagging and categorization.
          This powers the 3D topology view and smart project recommendations.
        </p>

        <div className="llm-config-form">
          <div className="llm-config-row">
            <div className="form-group">
              <label htmlFor="llm-base-url">API Base URL</label>
              <input
                id="llm-base-url"
                type="text"
                placeholder="https://api.openai.com/v1"
                value={llmBaseUrl}
                onChange={e => setLlmBaseUrl(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="llm-api-key">API Key</label>
              <input
                id="llm-api-key"
                type="password"
                placeholder="sk-..."
                value={llmApiKey}
                onChange={e => setLlmApiKey(e.target.value)}
              />
            </div>
          </div>
          <div className="llm-config-row">
            <div className="form-group">
              <label htmlFor="llm-model">Chat Model</label>
              <input
                id="llm-model"
                type="text"
                placeholder="gpt-3.5-turbo"
                value={llmModelName}
                onChange={e => setLlmModelName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="llm-embedding">Embedding Model</label>
              <input
                id="llm-embedding"
                type="text"
                placeholder="text-embedding-ada-002"
                value={llmEmbeddingModel}
                onChange={e => setLlmEmbeddingModel(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className={`llm-status-indicator ${llmConfigured ? 'configured' : 'not-configured'}`}>
          <span className={`status-dot ${llmConfigured ? 'configured' : 'not-configured'}`} />
          <span>
            {llmConfigured 
              ? 'LLM is configured and ready for semantic analysis.'
              : 'LLM is not configured. Basic keyword matching will be used.'}
          </span>
        </div>

        {connectionResult && (
          <div className={`llm-status-indicator ${connectionResult.success ? 'success' : 'error'}`}>
            <span className={`status-dot ${connectionResult.success ? 'success' : 'error'}`} />
            <span>{connectionResult.message}</span>
          </div>
        )}

        <div className="llm-info-box">
          <h4>💡 Compatible Services</h4>
          <p>
            Any OpenAI-compatible API is supported. Popular options include:
            <br/>
            <code>OpenAI</code>, <code>Azure OpenAI</code>, <code>Ollama</code> (local), 
            <code>Together AI</code>, <code>Anyscale</code>, and more.
          </p>
        </div>

        <div className="llm-actions">
          <button 
            type="button" 
            className="btn btn-primary" 
            onClick={handleSaveLLM}
            disabled={savingLLM}
          >
            {savingLLM ? 'Saving…' : 'Save LLM Config'}
          </button>
          <button 
            type="button" 
            className="btn btn-outline" 
            onClick={handleTestConnection}
            disabled={testingConnection || !llmApiKey}
          >
            {testingConnection ? 'Testing…' : 'Test Connection'}
          </button>
          <button 
            type="button" 
            className="btn btn-outline" 
            onClick={handleAnalyzeAll}
            disabled={analyzing || !llmConfigured}
          >
            {analyzing ? 'Analyzing…' : 'Analyze All Items'}
          </button>
        </div>
      </div>
    </main>
  )
}
