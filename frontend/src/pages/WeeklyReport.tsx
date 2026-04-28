import { useState, useEffect } from 'react'
import { reportApi, ContentItem } from '../services/api'
import ContentCard from '../components/ContentCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function WeeklyReport() {
  const [items, setItems] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [sendStatus, setSendStatus] = useState<string | null>(null)

  useEffect(() => {
    reportApi.getWeekly()
      .then(res => setItems(res.data))
      .catch(err => console.error('Failed to load report:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleSendEmail = async () => {
    setSending(true)
    setSendStatus(null)
    try {
      const res = await reportApi.send()
      setSendStatus(res.data.message)
    } catch {
      setSendStatus('Failed to send report.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Weekly Report</h1>
          <p className="text-sm text-gray-500 mt-1">Your top picks from the past 7 days</p>
        </div>
        <button
          onClick={handleSendEmail}
          disabled={sending}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {sending ? 'Sending...' : 'Send to email'}
        </button>
      </div>

      {sendStatus && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          {sendStatus}
        </div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : items.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-4xl mb-4">📭</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No report yet</h3>
          <p className="text-gray-600">Content from the past 7 days will appear here once scraped.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map(item => (
            <ContentCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
