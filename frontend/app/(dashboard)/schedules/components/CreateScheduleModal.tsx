'use client'

import { Schedule, ScheduleCreateInput } from '../hooks/useSchedules'
import ScheduleForm from './ScheduleForm'

interface CreateScheduleModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: ScheduleCreateInput) => Promise<void>
  schedule?: Schedule | null
  isLoading: boolean
}

export default function CreateScheduleModal({ isOpen, onClose, onSubmit, schedule, isLoading }: CreateScheduleModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h2 className="text-lg font-bold text-gray-900">
              {schedule ? `✏️ Editar: ${schedule.nome}` : '📅 Novo Agendamento'}
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">Configure o envio automático de mensagens</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-xl text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-hidden p-6">
          <ScheduleForm
            onSubmit={onSubmit}
            onCancel={onClose}
            initialData={schedule}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  )
}
