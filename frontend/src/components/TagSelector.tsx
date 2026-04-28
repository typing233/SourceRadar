import { useState } from 'react'

const PREDEFINED_TAGS = [
  "AI", "Rust", "Go", "Python", "JavaScript", "TypeScript", "React", "Vue",
  "Frontend", "Backend", "DevOps", "Open Source", "Productivity", "Indie Dev",
  "Mobile", "Web3", "Security", "Database", "Machine Learning", "CLI Tools"
]

interface TagSelectorProps {
  selectedTags: string[]
  onChange: (tags: string[]) => void
}

export default function TagSelector({ selectedTags, onChange }: TagSelectorProps) {
  const [customInput, setCustomInput] = useState('')

  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      onChange(selectedTags.filter(t => t !== tag))
    } else {
      onChange([...selectedTags, tag])
    }
  }

  const addCustomTag = () => {
    const tag = customInput.trim()
    if (tag && !selectedTags.includes(tag)) {
      onChange([...selectedTags, tag])
      setCustomInput('')
    }
  }

  const removeTag = (tag: string) => {
    onChange(selectedTags.filter(t => t !== tag))
  }

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">Suggested tags</p>
        <div className="flex flex-wrap gap-2">
          {PREDEFINED_TAGS.map(tag => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`text-sm px-3 py-1 rounded-full border transition-colors ${
                selectedTags.includes(tag)
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:text-blue-600'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">Add custom tag</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={customInput}
            onChange={e => setCustomInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addCustomTag()}
            placeholder="e.g. WebAssembly, Svelte..."
            className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={addCustomTag}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 transition-colors"
          >
            Add
          </button>
        </div>
      </div>

      {selectedTags.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Your tags ({selectedTags.length})</p>
          <div className="flex flex-wrap gap-2">
            {selectedTags.map(tag => (
              <span
                key={tag}
                className="flex items-center gap-1 text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-200"
              >
                {tag}
                <button
                  onClick={() => removeTag(tag)}
                  className="hover:text-red-500 transition-colors ml-1"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
