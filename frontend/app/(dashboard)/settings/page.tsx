'use client'

import { useState } from 'react'
import { AccountTab } from './components/AccountTab'
import { TeamTab } from './components/TeamTab'
import { BillingTab } from './components/BillingTab'

type TabId = 'account' | 'team' | 'billing'

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'account', label: 'Conta', icon: '👤' },
  { id: 'team', label: 'Equipe', icon: '👥' },
  { id: 'billing', label: 'Plano & Faturamento', icon: '💳' },
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabId>('account')
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message })
    setTimeout(() => setToast(null), 3500)
  }

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium ${
          toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
        }`}>
          {toast.type === 'success' ? '✅ ' : '❌ '}{toast.message}
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configurações</h1>
        <p className="mt-1 text-gray-600">Gerencie sua conta, equipe e plano de assinatura.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'account' && <AccountTab onToast={showToast} />}
        {activeTab === 'team' && <TeamTab onToast={showToast} />}
        {activeTab === 'billing' && <BillingTab onToast={showToast} />}
      </div>
    </div>
  )
}
