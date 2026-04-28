import { ContentItem } from '../services/api'

interface ContentCardProps {
  item: ContentItem
}

const SOURCE_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  github: { label: 'GitHub', color: 'text-white', bg: 'bg-gray-800' },
  hackernews: { label: 'Hacker News', color: 'text-white', bg: 'bg-orange-500' },
  producthunt: { label: 'Product Hunt', color: 'text-white', bg: 'bg-red-500' },
}

export default function ContentCard({ item }: ContentCardProps) {
  const source = SOURCE_CONFIG[item.source] || { label: item.source, color: 'text-white', bg: 'bg-gray-500' }

  const scoreLabel = item.source === 'github' ? '⭐' : '▲'

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`text-xs font-medium px-2 py-0.5 rounded ${source.bg} ${source.color}`}>
              {source.label}
            </span>
            {item.match_score !== null && item.match_score !== undefined && (
              <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                Match: {Math.round(item.match_score)}
              </span>
            )}
            <span className="text-xs text-gray-500">
              {scoreLabel} {item.score.toLocaleString()}
            </span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-1 leading-snug">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600 transition-colors"
            >
              {item.title}
            </a>
          </h3>
          {item.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {item.description}
            </p>
          )}
          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {item.tags.slice(0, 6).map((tag) => (
                <span
                  key={tag}
                  className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 text-blue-600 hover:text-blue-800 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  )
}
