import { useState, useEffect } from 'react'
import { getDigest, generateDigest } from '../api.js'

const SOURCE_LABELS = { github: 'GitHub', hn: 'Hacker News', ph: 'Product Hunt' }
const BADGE_CLASS = { github: 'badge-github', hn: 'badge-hn', ph: 'badge-ph' }

function scoreStars(score) {
  const filled = Math.round(score * 5)
  return '★'.repeat(filled) + '☆'.repeat(5 - filled)
}

function DigestItemCard({ entry }) {
  return (
    <div className="item-card">
      <div className="item-header">
        <div className="item-title">
          <a href={entry.url} target="_blank" rel="noopener noreferrer">{entry.title}</a>
        </div>
        <span className={`badge ${BADGE_CLASS[entry.source] || ''}`}>
          {SOURCE_LABELS[entry.source] || entry.source}
        </span>
      </div>
      <div className="stars" style={{ marginBottom: 6 }}>{scoreStars(entry.match_score)}</div>
      {entry.description && (
        <p className="item-desc">
          {entry.description.length > 200 ? entry.description.slice(0, 200) + '…' : entry.description}
        </p>
      )}
      {entry.raw_tags?.length > 0 && (
        <div className="item-tags">
          {entry.raw_tags.slice(0, 5).map(t => <span key={t} className="tag-chip">{t}</span>)}
        </div>
      )}
    </div>
  )
}

export default function Digest() {
  const [digest, setDigest] = useState(undefined)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [genMsg, setGenMsg] = useState('')

  useEffect(() => {
    getDigest()
      .then(({ data }) => setDigest(data))
      .catch(() => setError('Failed to load digest.'))
      .finally(() => setLoading(false))
  }, [])

  async function handleGenerate() {
    setGenerating(true)
    setGenMsg('')
    setError('')
    try {
      const { data } = await generateDigest()
      setDigest(data)
      setGenMsg('Digest generated! Email sent if SMTP is configured.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate digest.')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <div className="spinner" />

  const weekLabel = digest?.week_start
    ? new Date(digest.week_start).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
    : null

  return (
    <main className="page">
      <div className="digest-header">
        <div>
          <div className="section-title">Weekly Digest</div>
          {weekLabel && <div className="digest-meta">Week of {weekLabel}</div>}
        </div>
        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? '⏳ Generating…' : '⚡ Generate & Email Digest Now'}
        </button>
      </div>

      {error && <p className="error-msg" style={{ marginBottom: 16 }}>{error}</p>}
      {genMsg && <p className="success-msg" style={{ marginBottom: 16 }}>{genMsg}</p>}

      {!digest || digest.items?.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">📬</div>
          <p>No digest yet. Click "Generate & Email Digest Now" to create your first one!</p>
        </div>
      ) : (
        <>
          <p style={{ fontSize: '0.88rem', color: 'var(--muted)', marginBottom: 16 }}>
            {digest.items.length} top items · {digest.sent_at ? `Emailed ${new Date(digest.sent_at).toLocaleDateString()}` : 'Not yet emailed'}
          </p>
          {digest.items.map(entry => <DigestItemCard key={entry.id} entry={entry} />)}
        </>
      )}
    </main>
  )
}
