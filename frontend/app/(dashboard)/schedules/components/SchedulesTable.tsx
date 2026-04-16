'use client'

import { Schedule } from '../hooks/useSchedules'

interface SchedulesTableProps {
  schedules: Schedule[]
  loading: boolean
  onEdit: (schedule: Schedule) => void
  onDelete: (schedule: Schedule) => void
  onToggleStatus: (schedule: Schedule) => void
  onManualSend: (schedule: Schedule) => void
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {[...Array(6)].map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </td>
      ))}
    </tr>
  )
}

const MEDIA_LABELS: Record<string, string> = {
  todos: 'Todos',
  foto: 'Foto',
  video: 'Vídeo',
  texto: 'Texto',
  documento: 'Doc',
  audio: 'Áudio',
}

export default function SchedulesTable({
  schedules,
  loading,
  onEdit,
  onDelete,
  onToggleStatus,
  onManualSend,
  currentPage,
  totalPages,
  onPageChange,
}: SchedulesTableProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Nome', 'Bot', 'Horários', 'Tipo', 'Mídia', 'Ações'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {[...Array(5)].map((_, i) => <SkeletonRow key={i} />)}
          </tbody>
        </table>
      </div>
    )
  }

  if (schedules.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
        <div className="text-5xl mb-4">📅</div>
        <h3 className="text-lg font-semibold text-gray-900">Sem agendamentos ainda</h3>
        <p className="mt-2 text-sm text-gray-500">
          Crie seu primeiro agendamento para automação de envios periódicos.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Desktop Table */}
      <div className="hidden md:block bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Nome / Status', 'Bot', 'Horários', 'Tipo Envio', 'Mídia', 'Ações'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {schedules.map(schedule => (
              <tr key={schedule.id} className="hover:bg-gray-50 transition-colors">
                {/* Nome + Status */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onToggleStatus(schedule)}
                      className={`w-2.5 h-2.5 rounded-full flex-shrink-0 transition-colors ${
                        schedule.ativo ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                      title={schedule.ativo ? 'Ativo — clique para desativar' : 'Inativo — clique para ativar'}
                    />
                    <span className="font-medium text-gray-900 text-sm">{schedule.nome}</span>
                  </div>
                  <p className="text-xs text-gray-400 ml-4 mt-0.5">
                    {schedule.chats_origem?.length || 0} origem → {schedule.chats_destino?.length || 0} destino
                  </p>
                </td>

                {/* Bot */}
                <td className="px-4 py-3 text-sm text-gray-700">
                  {schedule.bot_nome || schedule.bot_id?.slice(0, 8) + '...'}
                </td>

                {/* Horários */}
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {(schedule.horarios || []).slice(0, 3).map((h, i) => (
                      <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-mono">
                        {h}
                      </span>
                    ))}
                    {(schedule.horarios || []).length > 3 && (
                      <span className="text-xs text-gray-400">+{schedule.horarios.length - 3}</span>
                    )}
                  </div>
                </td>

                {/* Tipo Envio */}
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    schedule.tipo_envio === 'sequencial'
                      ? 'bg-purple-50 text-purple-700'
                      : 'bg-orange-50 text-orange-700'
                  }`}>
                    {schedule.tipo_envio === 'sequencial' ? '🔁 Sequencial' : '📍 Pontual'}
                  </span>
                </td>

                {/* Mídia */}
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {(schedule.tipo_midia || ['todos']).slice(0, 2).map((m, i) => (
                      <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                        {MEDIA_LABELS[m] || m}
                      </span>
                    ))}
                  </div>
                </td>

                {/* Ações */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => onManualSend(schedule)}
                      className="p-1.5 rounded-lg text-green-600 hover:bg-green-50 transition-colors"
                      title="Envio manual agora"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </button>
                    <button
                      onClick={() => onEdit(schedule)}
                      className="p-1.5 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
                      title="Editar agendamento"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => onDelete(schedule)}
                      className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                      title="Excluir agendamento"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-3">
        {schedules.map(schedule => (
          <div key={schedule.id} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onToggleStatus(schedule)}
                  className={`w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0 ${schedule.ativo ? 'bg-green-500' : 'bg-gray-300'}`}
                />
                <div>
                  <p className="font-semibold text-gray-900">{schedule.nome}</p>
                  <p className="text-xs text-gray-500">{schedule.bot_nome || 'Bot não identificado'}</p>
                </div>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                schedule.tipo_envio === 'sequencial' ? 'bg-purple-50 text-purple-700' : 'bg-orange-50 text-orange-700'
              }`}>
                {schedule.tipo_envio}
              </span>
            </div>
            <div className="mt-3 flex flex-wrap gap-1">
              {(schedule.horarios || []).map((h, i) => (
                <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-mono">{h}</span>
              ))}
            </div>
            <div className="mt-3 flex items-center gap-2">
              <button onClick={() => onManualSend(schedule)} className="flex-1 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                ▶ Enviar Agora
              </button>
              <button onClick={() => onEdit(schedule)} className="flex-1 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                ✏️ Editar
              </button>
              <button onClick={() => onDelete(schedule)} className="flex-1 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                🗑 Excluir
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-1">
          <p className="text-sm text-gray-500">Página {currentPage} de {totalPages}</p>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              ← Anterior
            </button>
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Próximo →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
