'use client'

import { useEffect, useState } from 'react'
import { useSchedules, Schedule, ScheduleCreateInput } from './hooks/useSchedules'
import SchedulesTable from './components/SchedulesTable'
import CreateScheduleModal from './components/CreateScheduleModal'
import DeleteScheduleModal from './components/DeleteScheduleModal'

export default function SchedulesPage() {
  const {
    schedules, loading, error,
    totalPages, currentPage, pageSize,
    fetchSchedules, createSchedule, updateSchedule,
    deleteSchedule, toggleScheduleStatus, triggerManualSend,
  } = useSchedules()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null)
  const [deletingSchedule, setDeletingSchedule] = useState<Schedule | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchSchedules(1, pageSize) }, [])

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message })
    setTimeout(() => setToast(null), 3500)
  }

  const handleCreate = async (data: ScheduleCreateInput) => {
    setIsSubmitting(true)
    try {
      await createSchedule(data)
      setIsModalOpen(false)
      showToast('success', 'Agendamento criado com sucesso!')
    } catch { showToast('error', 'Erro ao criar agendamento.') }
    finally { setIsSubmitting(false) }
  }

  const handleUpdate = async (data: ScheduleCreateInput) => {
    if (!editingSchedule) return
    setIsSubmitting(true)
    try {
      await updateSchedule(editingSchedule.id, data)
      setEditingSchedule(null)
      setIsModalOpen(false)
      showToast('success', 'Agendamento atualizado!')
    } catch { showToast('error', 'Erro ao atualizar agendamento.') }
    finally { setIsSubmitting(false) }
  }

  const handleDelete = async () => {
    if (!deletingSchedule) return
    setIsDeleting(true)
    try {
      await deleteSchedule(deletingSchedule.id)
      setDeletingSchedule(null)
      showToast('success', 'Agendamento removido.')
    } catch { showToast('error', 'Erro ao remover agendamento.') }
    finally { setIsDeleting(false) }
  }

  const handleToggleStatus = async (schedule: Schedule) => {
    try {
      await toggleScheduleStatus(schedule.id, schedule.ativo)
      showToast('success', `Agendamento ${schedule.ativo ? 'desativado' : 'ativado'}.`)
    } catch { showToast('error', 'Erro ao alterar status.') }
  }

  const handleManualSend = async (schedule: Schedule) => {
    try {
      await triggerManualSend(schedule.id)
      showToast('success', `Envio manual de "${schedule.nome}" iniciado!`)
    } catch { showToast('error', 'Erro ao disparar envio manual.') }
  }

  const handleOpenCreate = () => {
    setEditingSchedule(null)
    setIsModalOpen(true)
  }

  const handleEdit = (schedule: Schedule) => {
    setEditingSchedule(schedule)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingSchedule(null)
  }

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all ${
          toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
        }`}>
          {toast.type === 'success' ? '✅ ' : '❌ '}{toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agendamentos</h1>
          <p className="mt-1 text-gray-600">Automatize envios periódicos com horários configurados.</p>
        </div>
        <button
          onClick={handleOpenCreate}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 active:bg-blue-800 transition w-full sm:w-auto justify-center"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Novo Agendamento
        </button>
      </div>

      {/* Error */}
      {error && !loading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <h3 className="font-semibold">Erro</h3>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total', value: schedules.length, icon: '📅' },
          { label: 'Ativos', value: schedules.filter(s => s.ativo).length, icon: '🟢' },
          { label: 'Inativos', value: schedules.filter(s => !s.ativo).length, icon: '⚪' },
          { label: 'Com envio', value: schedules.filter(s => s.horarios?.length > 0).length, icon: '🕐' },
        ].map(stat => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-3 shadow-sm">
            <p className="text-2xl">{stat.icon}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <SchedulesTable
        schedules={schedules}
        loading={loading && schedules.length === 0}
        onEdit={handleEdit}
        onDelete={s => setDeletingSchedule(s)}
        onToggleStatus={handleToggleStatus}
        onManualSend={handleManualSend}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={p => fetchSchedules(p, pageSize)}
      />

      {/* Create/Edit Modal */}
      <CreateScheduleModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={editingSchedule ? handleUpdate : handleCreate}
        schedule={editingSchedule}
        isLoading={isSubmitting}
      />

      {/* Delete Modal */}
      <DeleteScheduleModal
        isOpen={deletingSchedule !== null}
        schedule={deletingSchedule}
        isLoading={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setDeletingSchedule(null)}
      />
    </div>
  )
}
