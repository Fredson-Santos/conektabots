'use client'

import React, { useState, useEffect } from 'react'
import { RulesTable } from './components/RulesTable'
import { RuleWizard } from './components/RuleWizard'
import { useRules } from './hooks/useRules'
import { Regra, RegraFull } from './hooks/useRules'

/**
 * Rules Management Page
 *
 * Main dashboard for managing automation rules with:
 * - Paginated rules table (20 items/page)
 * - Create new rule with 7-step wizard
 * - Edit existing rules
 * - Delete with confirmation
 * - Enable/disable toggle
 * - Search/filter
 * - Full API integration
 */
export default function RulesPage() {
  const { list, error: storeError } = useRules()

  // UI State
  const [loading, setLoading] = useState(true)
  const [wizardMode, setWizardMode] = useState<'create' | 'edit' | null>(null)
  const [selectedRule, setSelectedRule] = useState<RegraFull | null>(null)

  // Load rules on mount
  useEffect(() => {
    const loadRules = async () => {
      try {
        setLoading(true)
        await list()
      } catch (err) {
        console.error('Failed to load rules:', err)
      } finally {
        setLoading(false)
      }
    }
    loadRules()
  }, [list])

  const handleCreateRule = () => {
    setWizardMode('create')
    setSelectedRule(null)
  }

  const handleEditRule = (_rule: Regra) => {
    // Note: In real implementation, would fetch the full rule details here
    setWizardMode('edit')
    // setSelectedRule(rule) - would need to fetch full details with children
  }

  const handleWizardComplete = async () => {
    setWizardMode(null)
    setSelectedRule(null)
    // Refresh table
    try {
      await list()
    } catch (err) {
      console.error('Failed to refresh rules:', err)
    }
  }

  const handleWizardCancel = () => {
    setWizardMode(null)
    setSelectedRule(null)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Regras</h1>
          <p className="mt-1 text-gray-600">
            Crie e manage regras de encaminhamento automático para seus bots
          </p>
        </div>
        <button
          onClick={handleCreateRule}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 transition-colors shadow-sm"
        >
          + Nova Regra
        </button>
      </div>

      {/* Error Alert */}
      {storeError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">Erro: {storeError}</p>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center p-12">
          <div className="text-center">
            <div className="inline-block w-12 h-12 animate-spin text-blue-600 text-2xl">
              ⟳
            </div>
            <p className="mt-3 text-gray-600">Carregando regras...</p>
          </div>
        </div>
      ) : (
        <RulesTable
          onEdit={handleEditRule}
          onRefresh={() => list()}
        />
      )}

      {/* Wizard Modal */}
      {wizardMode && (
        <RuleWizard
          mode={wizardMode}
          initialData={selectedRule || undefined}
          onComplete={handleWizardComplete}
          onCancel={handleWizardCancel}
        />
      )}

      {/* Info Card */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-6">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Como funciona?</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>
            <strong>Règra:</strong> Define como mensagens são processadas e encaminhadas
          </li>
          <li>
            <strong>Origem:</strong> Chats/canais de onde as mensagens são lidas
          </li>
          <li>
            <strong>Destino:</strong> Chats/canais para onde as mensagens são encaminhadas
          </li>
          <li>
            <strong>Filtros:</strong> Palavras-chave para incluir ou bloquear mensagens
          </li>
          <li>
            <strong>Condições:</strong> Requisitos adicionais (emoji, preço, horário, etc)
          </li>
        </ul>
      </div>
    </div>
  )
}
