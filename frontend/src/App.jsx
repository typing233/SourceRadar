import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, NavLink, useNavigate } from 'react-router-dom'
import { getMe } from './api.js'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Feed from './pages/Feed.jsx'
import Settings from './pages/Settings.jsx'
import Digest from './pages/Digest.jsx'

function NavBar({ onLogout }) {
  return (
    <nav>
      <span className="nav-brand">🚀 SourceRadar</span>
      <NavLink className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')} to="/feed">Feed</NavLink>
      <NavLink className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')} to="/digest">Digest</NavLink>
      <NavLink className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')} to="/settings">Settings</NavLink>
      <button className="btn-logout" onClick={onLogout}>Logout</button>
    </nav>
  )
}

function ProtectedApp() {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <NavBar onLogout={handleLogout} />
      <Routes>
        <Route path="/feed" element={<Feed />} />
        <Route path="/digest" element={<Digest />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/feed" replace />} />
      </Routes>
    </div>
  )
}

function AuthLayout() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  const [authed, setAuthed] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) { setAuthed(false); return }
    getMe()
      .then(() => setAuthed(true))
      .catch(() => { localStorage.removeItem('token'); setAuthed(false) })
  }, [])

  if (authed === null) return <div className="spinner" style={{ marginTop: 120 }} />

  return (
    <BrowserRouter>
      {authed
        ? <ProtectedApp />
        : <AuthLayout />}
    </BrowserRouter>
  )
}
