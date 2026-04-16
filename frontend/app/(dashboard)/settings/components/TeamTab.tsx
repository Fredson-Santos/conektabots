'use client'

import { useState, useEffect } from 'react'
import { getApi } from '@/lib/api'

interface Member {
  id: string
  nome: string
  email: string
  role: 'owner' | 'admin' | 'editor' | 'viewer'
  criado_em: string
}

const ROLE_CONFIG = {
  owner: { label: 'Proprietário', color: 'bg-purple-100 text-purple-700' },
  admin: { label: 'Admin', color: 'bg-blue-100 text-blue-700' },
  editor: { label: 'Editor', color: 'bg-green-100 text-green-700' },
  viewer: { label: 'Visualizador', color: 'bg-gray-100 text-gray-600' },
}

interface TeamTabProps {
  onToast: (type: 'success' | 'error', message: string) => void
}

export function TeamTab({ onToast }: TeamTabProps) {
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<'admin' | 'editor' | 'viewer'>('editor')
  const [inviting, setInviting] = useState(false)
  const [removingId, setRemovingId] = useState<string | null>(null)

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const api = getApi()
        const res = await api.get('/tenants/members')
        const data = res.data
        setMembers(Array.isArray(data) ? data : data.items || data.data || [])
      } catch { setMembers([]) }
      finally { setLoading(false) }
    }
    fetchMembers()
  }, [])

  const handleInvite = async () => {
    if (!inviteEmail.trim()) { onToast('error', 'Informe o email'); return }
    setInviting(true)
    try {
      const api = getApi()
      const res = await api.post('/tenants/members/invite', { email: inviteEmail, role: inviteRole })
      setMembers(prev => [...prev, res.data])
      setInviteEmail('')
      onToast('success', `Convite enviado para ${inviteEmail}!`)
    } catch (err) {
      onToast('error', err instanceof Error ? err.message : 'Erro ao convidar.')
    } finally { setInviting(false) }
  }

  const handleUpdateRole = async (memberId: string, newRole: string) => {
    try {
      const api = getApi()
      await api.patch(`/tenants/members/${memberId}`, { role: newRole })
      setMembers(prev => prev.map(m => m.id === memberId ? { ...m, role: newRole as Member['role'] } : m))
      onToast('success', 'Papel atualizado.')
    } catch (err) {
      onToast('error', err instanceof Error ? err.message : 'Erro ao atualizar.')
    }
  }

  const handleRemove = async (memberId: string) => {
    setRemovingId(memberId)
    try {
      const api = getApi()
      await api.delete(`/tenants/members/${memberId}`)
      setMembers(prev => prev.filter(m => m.id !== memberId))
      onToast('success', 'Membro removido.')
    } catch (err) {
      onToast('error', err instanceof Error ? err.message : 'Erro ao remover.')
    } finally { setRemovingId(null) }
  }

  return (
    <div className="space-y-6">
      {/* Invite */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Convidar Membro</h3>
        <div className="flex flex-wrap gap-3">
          <input
            type="email"
            value={inviteEmail}
            onChange={e => setInviteEmail(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleInvite()}
            placeholder="email@exemplo.com"
            className="flex-1 min-w-[200px] px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={inviteRole}
            onChange={e => setInviteRole(e.target.value as typeof inviteRole)}
            className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="editor">Editor</option>
            <option value="admin">Admin</option>
            <option value="viewer">Visualizador</option>
          </select>
          <button onClick={handleInvite} disabled={inviting}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {inviting ? 'Enviando...' : 'Convidar'}
          </button>
        </div>
      </div>

      {/* Members list */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-base font-semibold text-gray-900">Membros da Equipe ({members.length})</h3>
        </div>
        {loading ? (
          <div className="p-6 space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-200" />
                <div className="flex-1 space-y-1.5">
                  <div className="h-3.5 bg-gray-200 rounded w-1/3" />
                  <div className="h-3 bg-gray-100 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : members.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500 text-sm">Nenhum membro além de você. Convide alguém!</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {members.map(member => {
              const role = ROLE_CONFIG[member.role] || ROLE_CONFIG.viewer
              return (
                <li key={member.id} className="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold flex-shrink-0">
                    {member.nome[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">{member.nome}</p>
                    <p className="text-xs text-gray-500 truncate">{member.email}</p>
                  </div>
                  {member.role === 'owner' ? (
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${role.color}`}>{role.label}</span>
                  ) : (
                    <select
                      value={member.role}
                      onChange={e => handleUpdateRole(member.id, e.target.value)}
                      className={`px-2 py-1 rounded-lg text-xs font-semibold border-0 focus:outline-none focus:ring-1 focus:ring-blue-400 ${role.color}`}
                    >
                      <option value="admin">Admin</option>
                      <option value="editor">Editor</option>
                      <option value="viewer">Visualizador</option>
                    </select>
                  )}
                  {member.role !== 'owner' && (
                    <button
                      onClick={() => handleRemove(member.id)}
                      disabled={removingId === member.id}
                      className="p-1.5 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition-colors disabled:opacity-40"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7a4 4 0 11-8 0 4 4 0 018 0zM9 14a6 6 0 00-6 6v1h12v-1a6 6 0 00-6-6zM21 12h-6" />
                      </svg>
                    </button>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}
