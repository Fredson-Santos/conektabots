'use client'

import { useState } from 'react'
import { Log } from '../hooks/useLogs'

const STATUS_CONFIG = {
  sucesso: { label: 'Sucesso', color: 'bg-green-100 text-green-700', dot: 'bg-green-500' },
  erro: { label: 'Erro', color: 'bg-red-100 text-red-700', dot: 'bg-red-500' },
  bloqueado: { label: 'Bloqueado', color: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500' },
  pendente: { label: 'Pendente', color: 'bg-blue-100 text-blue-700', dot: 'bg-blue-400' },
}

interface LogDetailModalProps {
  log: Log | null
  onClose: () => void
}

function LogDetailModal({ log, onClose }: LogDetailModalProps) {
  if (!log) return null
  const status = STATUS_CONFIG[log.status] || STATUS_CONFIG.pendente

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">Detalhe do Log</h3>
          <button onClick={onClose} className="p-2 rounded-xl text-gray-400 hover:bg-gray-100 transition-colors">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${status.color}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
              {status.label}
            </span>
            <span className="text-xs text-gray-400">{new Date(log.criado_em).toLocaleString('pt-BR')}</span>
          </div>
          {[
            { label: 'Bot', value: log.bot_nome || log.bot_id },
            { label: 'Origem', value: log.chat_origem },
            { label: 'Destino', value: log.chat_destino },
            { label: 'Tipo Mídia', value: log.tipo_midia || '—' },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between text-sm border-b border-gray-50 pb-2">
              <span className="text-gray-500 font-medium">{label}</span>
              <span className="text-gray-900 font-mono text-right max-w-xs truncate">{value}</span>
            </div>
          ))}
          {log.mensagem && (
            <div>
              <p className="text-xs font-semibold text-gray-500 mb-1">MENSAGEM</p>
              <p className="text-sm bg-gray-50 rounded-lg p-3 text-gray-800 line-clamp-6">{log.mensagem}</p>
            </div>
          )}
          {log.erro && (
            <div>
              <p className="text-xs font-semibold text-red-500 mb-1">ERRO</p>
              <p className="text-sm bg-red-50 rounded-lg p-3 text-red-800 font-mono">{log.erro}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface LogsTableProps {
  logs: Log[]
  loading: boolean
  currentPage: number
  totalPages: number
  totalLogs: number
  onPageChange: (page: number) => void
}

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {[...Array(6)].map((_, i) => (
        <td key={i} className="px-4 py-2.5">
          <div className="h-3.5 bg-gray-200 rounded w-3/4" />
        </td>
      ))}
    </tr>
  )
}

export default function LogsTable({ logs, loading, currentPage, totalPages, totalLogs, onPageChange }: LogsTableProps) {
  const [selectedLog, setSelectedLog] = useState<Log | null>(null)

  if (loading && logs.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Data/Hora', 'Bot', 'Origem → Destino', 'Status', 'Mídia', 'Ação'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {[...Array(8)].map((_, i) => <SkeletonRow key={i} />)}
          </tbody>
        </table>
      </div>
    )
  }

  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
        <div className="text-5xl mb-4">📋</div>
        <h3 className="text-lg font-semibold text-gray-900">Nenhum log encontrado</h3>
        <p className="mt-2 text-sm text-gray-500">Os logs de execução aparecerão aqui quando seus bots processar mensagens.</p>
      </div>
    )
  }

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Data/Hora', 'Bot', 'Origem → Destino', 'Status', 'Mídia', 'Ação'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {logs.map(log => {
                const status = STATUS_CONFIG[log.status] || STATUS_CONFIG.pendente
                return (
                  <tr key={log.id} className="hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => setSelectedLog(log)}>
                    <td className="px-4 py-2.5 text-xs text-gray-500 whitespace-nowrap font-mono">
                      {new Date(log.criado_em).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-4 py-2.5 text-sm text-gray-700 max-w-[100px] truncate">
                      {log.bot_nome || log.bot_id?.slice(0, 8) + '...'}
                    </td>
                    <td className="px-4 py-2.5 text-xs">
                      <div className="flex items-center gap-1">
                        <span className="font-mono text-gray-600 max-w-[80px] truncate">{log.chat_origem}</span>
                        <span className="text-gray-400">→</span>
                        <span className="font-mono text-gray-600 max-w-[80px] truncate">{log.chat_destino}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold ${status.color}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                        {status.label}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-xs text-gray-500 capitalize">{log.tipo_midia || '—'}</td>
                    <td className="px-4 py-2.5">
                      <button
                        onClick={e => { e.stopPropagation(); setSelectedLog(log) }}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Ver →
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50">
          <p className="text-xs text-gray-500">{totalLogs.toLocaleString()} registros totais</p>
          {totalPages > 1 && (
            <div className="flex items-center gap-2">
              <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage <= 1}
                className="px-3 py-1 text-xs font-medium rounded-lg border border-gray-200 text-gray-700 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                ← Anterior
              </button>
              <span className="text-xs text-gray-500">Pág. {currentPage} / {totalPages}</span>
              <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage >= totalPages}
                className="px-3 py-1 text-xs font-medium rounded-lg border border-gray-200 text-gray-700 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                Próximo →
              </button>
            </div>
          )}
        </div>
      </div>

      <LogDetailModal log={selectedLog} onClose={() => setSelectedLog(null)} />
    </>
  )
}
