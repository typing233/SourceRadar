import { useState, useEffect } from 'react'
import { getTags, updateTags, getMe, updateSettings } from '../api.js'

export default function Settings() {
  const [tags, setTags] = useState([])
  const [newTag, setNewTag] = useState('')
  const [receiveDigest, setReceiveDigest] = useState(true)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [tagsRes, meRes] = await Promise.all([getTags(), getMe()])
        setTags(tagsRes.data.map(t => t.name))
        setReceiveDigest(meRes.data.receive_digest)
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

  if (loading) return <div className="spinner" />

  return (
    <main className="page">
      <div className="section-title">Settings</div>
      <div className="section-sub">Manage your interest tags and notification preferences</div>

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
    </main>
  )
}
