'use client'

import { useEffect, useState } from 'react'
import { useBots, Bot, BotCreateInput } from './hooks/useBots'
import BotsTable from './components/BotsTable'
import CreateBotModal from './components/CreateBotModal'
import DeleteConfirmationModal from './components/DeleteConfirmationModal'

export default function BotsPage() {
  const {
    bots,
    loading,
    error,
    totalPages,
    currentPage,
    pageSize,
    fetchBots,
    createBot,
    updateBot,
    deleteBot,
    toggleBotStatus,
  } = useBots()

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [editingBot, setEditingBot] = useState<Bot | null>(null)
  const [deleteBot_modal, setDeleteBotModal] = useState<Bot | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeletingBot, setIsDeletingBot] = useState(false)

  // Fetch bots on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchBots(1, pageSize)
  }, [])

  const handleCreateBot = async (data: BotCreateInput) => {
    try {
      setIsSubmitting(true)
      await createBot(data)
      setIsCreateModalOpen(false)
    } catch (err) {
      console.error('Failed to create bot:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdateBot = async (data: BotCreateInput) => {
    if (!editingBot) return

    try {
      setIsSubmitting(true)
      await updateBot(editingBot.id, data)
      setEditingBot(null)
    } catch (err) {
      console.error('Failed to update bot:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteBot = async () => {
    if (!deleteBot_modal) return

    try {
      setIsDeletingBot(true)
      await deleteBot(deleteBot_modal.id)
      setDeleteBotModal(null)
    } catch (err) {
      console.error('Failed to delete bot:', err)
    } finally {
      setIsDeletingBot(false)
    }
  }

  const handleToggleBotStatus = async (bot: Bot) => {
    try {
      await toggleBotStatus(bot.id, bot.ativo)
    } catch (err) {
      console.error('Failed to toggle bot status:', err)
    }
  }

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchBots(newPage, pageSize)
    }
  }

  const handleEditBot = (bot: Bot) => {
    setEditingBot(bot)
    setIsCreateModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsCreateModalOpen(false)
    setEditingBot(null)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bots Management</h1>
          <p className="mt-1 text-gray-600">
            Create, configure, and manage your Telegram bots.
          </p>
        </div>
        <button
          onClick={() => {
            setEditingBot(null)
            setIsCreateModalOpen(true)
          }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 active:bg-blue-800 transition w-full sm:w-auto justify-center sm:justify-start"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Create Bot
        </button>
      </div>

      {/* Error Alert */}
      {error && !loading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <h3 className="font-semibold">Error Loading Bots</h3>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      )}

      {/* Bots Table */}
      <BotsTable
        bots={bots}
        loading={loading && bots.length === 0}
        onEdit={handleEditBot}
        onDelete={(bot) => setDeleteBotModal(bot)}
        onToggleStatus={handleToggleBotStatus}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />

      {/* Create/Edit Bot Modal */}
      <CreateBotModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        onSubmit={editingBot ? handleUpdateBot : handleCreateBot}
        bot={editingBot}
        isLoading={isSubmitting}
      />

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={deleteBot_modal !== null}
        bot={deleteBot_modal}
        isLoading={isDeletingBot}
        onConfirm={handleDeleteBot}
        onCancel={() => setDeleteBotModal(null)}
      />
    </div>
  )
}
