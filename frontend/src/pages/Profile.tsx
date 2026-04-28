import { useState, useEffect } from 'react'
import { userApi } from '../services/api'
import { useAuth } from '../context/AuthContext'
import TagSelector from '../components/TagSelector'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [tags, setTags] = useState<string[]>(user?.tags || [])
  const [emailReports, setEmailReports] = useState(user?.email_reports ?? true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (user) {
      setTags(user.tags || [])
      setEmailReports(user.email_reports)
    }
  }, [user])

  const handleSave = async () => {
    setSaving(true)
    setSaved(false)
    try {
      await userApi.updateTags(tags)
      await userApi.updateProfile({ email_reports: emailReports })
      await refreshUser()
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      console.error('Failed to save profile:', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile</h1>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Account</h2>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-500">Username</label>
            <p className="text-gray-900 mt-0.5">{user?.username}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Email</label>
            <p className="text-gray-900 mt-0.5">{user?.email}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Member since</label>
            <p className="text-gray-900 mt-0.5">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Interest Tags</h2>
        <p className="text-sm text-gray-600 mb-4">
          Select topics you care about to personalize your feed and weekly reports.
        </p>
        <TagSelector selectedTags={tags} onChange={setTags} />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Notifications</h2>
        <label className="flex items-center gap-3 cursor-pointer">
          <div className="relative">
            <input
              type="checkbox"
              className="sr-only"
              checked={emailReports}
              onChange={e => setEmailReports(e.target.checked)}
            />
            <div className={`w-10 h-6 rounded-full transition-colors ${emailReports ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
            <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${emailReports ? 'translate-x-4' : ''}`}></div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">Weekly email reports</p>
            <p className="text-xs text-gray-500">Receive your top picks every Monday morning</p>
          </div>
        </label>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save changes'}
        </button>
        {saved && (
          <span className="text-sm text-green-600 flex items-center gap-1">
            ✓ Changes saved
          </span>
        )}
      </div>
    </div>
  )
}
