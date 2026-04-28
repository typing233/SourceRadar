import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { contentApi, ContentItem, FeedResponse } from '../services/api'
import { useAuth } from '../context/AuthContext'
import ContentCard from '../components/ContentCard'
import LoadingSpinner from '../components/LoadingSpinner'

const SOURCES = [
  { key: '', label: 'All' },
  { key: 'github', label: 'GitHub' },
  { key: 'hackernews', label: 'Hacker News' },
  { key: 'producthunt', label: 'Product Hunt' },
]

export default function Feed() {
  const { user } = useAuth()
  const [items, setItems] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [source, setSource] = useState('')
  const [search, setSearch] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [refreshing, setRefreshing] = useState(false)

  const fetchFeed = useCallback(async (pageNum: number, src: string, q: string, append = false) => {
    try {
      let response
      if (q) {
        response = await contentApi.search(q, pageNum)
      } else {
        response = await contentApi.getFeed(pageNum, 20, src || undefined)
      }
      const data: FeedResponse = response.data
      if (append) {
        setItems(prev => [...prev, ...data.items])
      } else {
        setItems(data.items)
      }
      setTotalPages(data.pages)
    } catch (err) {
      console.error('Failed to fetch feed:', err)
    }
  }, [])

  useEffect(() => {
    setLoading(true)
    setPage(1)
    fetchFeed(1, source, searchQuery).finally(() => setLoading(false))
  }, [source, searchQuery, fetchFeed])

  const handleLoadMore = async () => {
    if (page >= totalPages || loadingMore) return
    setLoadingMore(true)
    const nextPage = page + 1
    await fetchFeed(nextPage, source, searchQuery, true)
    setPage(nextPage)
    setLoadingMore(false)
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await contentApi.refresh()
      await fetchFeed(1, source, searchQuery)
      setPage(1)
    } catch (err) {
      console.error('Refresh failed:', err)
    } finally {
      setRefreshing(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearchQuery(search)
  }

  if (!user?.tags || user.tags.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-5xl mb-4">🎯</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Set up your interests</h2>
        <p className="text-gray-600 mb-6">Add tags to get a personalized feed of projects and articles.</p>
        <Link
          to="/profile"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Configure Tags →
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Feed</h1>
          <p className="text-sm text-gray-500 mt-1">
            Based on: {user.tags.slice(0, 5).join(', ')}{user.tags.length > 5 ? ` +${user.tags.length - 5} more` : ''}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <svg className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search articles..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors">
            Search
          </button>
          {searchQuery && (
            <button
              type="button"
              onClick={() => { setSearch(''); setSearchQuery('') }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </form>

      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {SOURCES.map(s => (
          <button
            key={s.key}
            onClick={() => { setSource(s.key); setPage(1) }}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              source === s.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : items.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No content found</h3>
          <p className="text-gray-600">Try refreshing or changing your filters.</p>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {items.map(item => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
          {page < totalPages && (
            <div className="text-center mt-8">
              <button
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {loadingMore ? 'Loading...' : 'Load more'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
