import { useState, useEffect, useCallback } from 'react'
import { getFeed } from '../api.js'

const SOURCE_LABELS = { github: 'GitHub', hn: 'Hacker News', ph: 'Product Hunt' }
const BADGE_CLASS = { github: 'badge-github', hn: 'badge-hn', ph: 'badge-ph' }

function ItemCard({ item }) {
  const pct = Math.round(item.match_score * 100)
  const published = item.published_at
    ? new Date(item.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    : null

  return (
    <div className="item-card">
      <div className="item-header">
        <div className="item-title">
          <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
        </div>
        <span className={`badge ${BADGE_CLASS[item.source] || ''}`}>
          {SOURCE_LABELS[item.source] || item.source}
        </span>
      </div>
      {item.description && (
        <p className="item-desc">
          {item.description.length > 160 ? item.description.slice(0, 160) + '…' : item.description}
        </p>
      )}
      {item.raw_tags?.length > 0 && (
        <div className="item-tags">
          {item.raw_tags.slice(0, 5).map(t => (
            <span key={t} className="tag-chip">{t}</span>
          ))}
        </div>
      )}
      <div className="item-footer">
        <div className="match-bar-wrap" title={`${pct}% match`}>
          <div className="match-bar" style={{ width: `${pct}%` }} />
        </div>
        <span className="item-meta">{pct}% match</span>
        {published && <span className="item-meta">{published}</span>}
      </div>
    </div>
  )
}

export default function Feed() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [source, setSource] = useState('')
  const [q, setQ] = useState('')
  const [debouncedQ, setDebouncedQ] = useState('')
  const [loading, setLoading] = useState(false)
  const PAGE_SIZE = 20

  // Debounce search query
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q), 400)
    return () => clearTimeout(t)
  }, [q])

  const fetchFeed = useCallback(async (p, src, query) => {
    setLoading(true)
    try {
      const { data } = await getFeed({ page: p, page_size: PAGE_SIZE, source: src || undefined, q: query || undefined })
      setItems(data.items)
      setTotal(data.total)
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false)
    }
  }, [])

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1)
  }, [source, debouncedQ])

  useEffect(() => {
    fetchFeed(page, source, debouncedQ)
  }, [page, source, debouncedQ, fetchFeed])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <main className="page">
      <div className="section-title">Your Feed</div>
      <div className="section-sub">{total} items · sorted by relevance</div>

      <div className="filters">
        <select value={source} onChange={e => setSource(e.target.value)}>
          <option value="">All Sources</option>
          <option value="github">GitHub Trending</option>
          <option value="hn">Hacker News</option>
          <option value="ph">Product Hunt</option>
        </select>
        <input
          type="search"
          placeholder="Search titles & descriptions…"
          value={q}
          onChange={e => setQ(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="spinner" />
      ) : items.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">🔭</div>
          <p>No items found. Try adjusting your filters or check back after the next crawl.</p>
        </div>
      ) : (
        <>
          {items.map(item => <ItemCard key={item.id} item={item} />)}
          <div className="pagination">
            <button
              className="btn btn-outline"
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
            >← Prev</button>
            <span className="page-info">Page {page} of {totalPages}</span>
            <button
              className="btn btn-outline"
              disabled={page >= totalPages}
              onClick={() => setPage(p => p + 1)}
            >Next →</button>
          </div>
        </>
      )}
    </main>
  )
}
