'use client'

import { useState } from 'react'
import { getApi } from '@/lib/api'
import { auth } from '@/lib/auth'

interface AccountTabProps {
  onToast: (type: 'success' | 'error', message: string) => void
}

export function AccountTab({ onToast }: AccountTabProps) {
  const userData = auth.getUserData()
  const [name, setName] = useState(userData?.name || '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)

  const handleSaveProfile = async () => {
    if (!name.trim()) { onToast('error', 'Nome é obrigatório'); return }
    setSaving(true)
    try {
      const api = getApi()
      await api.patch('/auth/me', { nome: name })
      onToast('success', 'Perfil atualizado com sucesso!')
    } catch (err) {
      onToast('error', err instanceof Error ? err.message : 'Erro ao salvar.')
    } finally { setSaving(false) }
  }

  const handleChangePassword = async () => {
    if (newPassword.length < 8) { onToast('error', 'Senha deve ter pelo menos 8 caracteres'); return }
    if (newPassword !== confirmPassword) { onToast('error', 'Senhas não coincidem'); return }
    setSavingPassword(true)
    try {
      const api = getApi()
      await api.post('/auth/change-password', { senha_atual: currentPassword, nova_senha: newPassword })
      setCurrentPassword(''); setNewPassword(''); setConfirmPassword('')
      onToast('success', 'Senha alterada com sucesso!')
    } catch (err) {
      onToast('error', err instanceof Error ? err.message : 'Erro ao alterar senha.')
    } finally { setSavingPassword(false) }
  }

  return (
    <div className="space-y-6">
      {/* Profile */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Informações do Perfil</h3>
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-2xl font-bold">
            {(name || 'U')[0].toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{name || 'Usuário'}</p>
            <p className="text-sm text-gray-500">{userData?.email || 'email@exemplo.com'}</p>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome completo</label>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              value={userData?.email || ''}
              disabled
              className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm bg-gray-50 text-gray-400 cursor-not-allowed"
            />
          </div>
          <button onClick={handleSaveProfile} disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2">
            {saving && <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>}
            Salvar Perfil
          </button>
        </div>
      </div>

      {/* Password */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Alterar Senha</h3>
        <div className="space-y-4">
          {[
            { label: 'Senha atual', value: currentPassword, setter: setCurrentPassword },
            { label: 'Nova senha', value: newPassword, setter: setNewPassword },
            { label: 'Confirmar nova senha', value: confirmPassword, setter: setConfirmPassword },
          ].map(({ label, value, setter }) => (
            <div key={label}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                type="password"
                value={value}
                onChange={e => setter(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          ))}
          <button onClick={handleChangePassword} disabled={savingPassword}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2">
            {savingPassword && <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>}
            Alterar Senha
          </button>
        </div>
      </div>

      {/* Danger zone */}
      <div className="bg-white rounded-xl border border-red-200 p-6 shadow-sm">
        <h3 className="text-base font-semibold text-red-700 mb-2">Zona de Perigo</h3>
        <p className="text-sm text-gray-600 mb-4">Ao excluir sua conta, todos os dados serão removidos permanentemente e não poderão ser recuperados.</p>
        <button className="px-4 py-2 bg-white border border-red-300 text-red-600 text-sm font-semibold rounded-lg hover:bg-red-50 transition-colors">
          Excluir Conta
        </button>
      </div>
    </div>
  )
}
