'use client'

import { useEffect, useState } from 'react'
import { useLogs, LogFilters } from './hooks/useLogs'
import LogsTable from './components/LogsTable'

const STATUS_OPTIONS = ['', 'sucesso', 'erro', 'bloqueado', 'pendente']

export default function LogsPage() {
  const {
    logs, loading, error,
    totalPages, currentPage, totalLogs, autoRefresh,
    fetchLogs, setAutoRefresh, exportCsv,
  } = useLogs()

  const [filters, setFilters] = useState<LogFilters>({})
  const [search, setSearch] = useState('')

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchLogs(1, {}) }, [])

  const handleFilterChange = (key: keyof LogFilters, value: string) => {
    const newFilters = { ...filters, [key]: value || undefined }
    setFilters(newFilters)
    fetchLogs(1, newFilters)
  }

  const handleSearch = () => {
    const newFilters = { ...filters, search: search || undefined }
    setFilters(newFilters)
    fetchLogs(1, newFilters)
  }

  const handleClearFilters = () => {
    setFilters({})
    setSearch('')
    fetchLogs(1, {})
  }

  const hasFilters = Object.values(filters).some(Boolean) || search

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Logs de Atividade</h1>
          <p className="mt-1 text-gray-600">Histórico completo de execuções e mensagens processadas.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium border transition-colors ${
              autoRefresh
                ? 'bg-green-50 border-green-300 text-green-700'
                : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} />
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh'}
          </button>
          <button
            onClick={exportCsv}
            disabled={logs.length === 0}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-40 transition-colors"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export CSV
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total', value: totalLogs, icon: '📋', color: 'text-gray-900' },
          { label: 'Sucesso', value: logs.filter(l => l.status === 'sucesso').length, icon: '✅', color: 'text-green-700' },
          { label: 'Erros', value: logs.filter(l => l.status === 'erro').length, icon: '❌', color: 'text-red-700' },
          { label: 'Bloqueados', value: logs.filter(l => l.status === 'bloqueado').length, icon: '🚫', color: 'text-orange-700' },
        ].map(stat => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-3 shadow-sm">
            <p className="text-2xl">{stat.icon}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value.toLocaleString()}</p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
        <div className="flex flex-wrap gap-3 items-end">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-gray-500 mb-1">Busca global</label>
            <div className="flex gap-2">
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder="@chat, bot, mensagem..."
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button onClick={handleSearch}
                className="px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                🔍
              </button>
            </div>
          </div>

          {/* Status */}
          <div className="w-40">
            <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
            <select
              value={filters.status || ''}
              onChange={e => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s || 'Todos'}</option>)}
            </select>
          </div>

          {/* Data Início */}
          <div className="w-40">
            <label className="block text-xs font-medium text-gray-500 mb-1">De</label>
            <input
              type="date"
              value={filters.data_inicio || ''}
              onChange={e => handleFilterChange('data_inicio', e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Data Fim */}
          <div className="w-40">
            <label className="block text-xs font-medium text-gray-500 mb-1">Até</label>
            <input
              type="date"
              value={filters.data_fim || ''}
              onChange={e => handleFilterChange('data_fim', e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Clear */}
          {hasFilters && (
            <button onClick={handleClearFilters}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              ✕ Limpar filtros
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && !loading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <h3 className="font-semibold">Erro ao carregar logs</h3>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      )}

      {/* Table */}
      <LogsTable
        logs={logs}
        loading={loading && logs.length === 0}
        currentPage={currentPage}
        totalPages={totalPages}
        totalLogs={totalLogs}
        onPageChange={p => fetchLogs(p, filters)}
      />
    </div>
  )
}
