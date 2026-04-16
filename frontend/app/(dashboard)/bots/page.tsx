'use client'

import { useEffect, useState } from 'react'
import { DashboardLayout, navigationItems } from '@/app/components/layout'
import { Button, Alert } from '@/app/components/ui'
import { PlusIcon } from '@heroicons/react/24/outline'
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
    <DashboardLayout
      sidebarItems={navigationItems}
      title="Bots Management"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Bots' },
      ]}
      actions={
        <Button
          variant="primary"
          size="md"
          icon={<PlusIcon className="w-5 h-5" />}
          onClick={() => {
            setEditingBot(null)
            setIsCreateModalOpen(true)
          }}
        >
          Create Bot
        </Button>
      }
    >
      <div className="space-y-lg">
        {/* Page Description */}
        <div>
          <p className="text-sm text-gray-600">
            Create, configure, and manage your Telegram bots.
          </p>
        </div>

        {/* Error Alert */}
        {error && !loading && (
          <Alert
            type="error"
            title="Error Loading Bots"
            description={error}
            action={{ label: 'Retry', onClick: () => fetchBots(currentPage, pageSize) }}
          />
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
    </DashboardLayout>
  )
}
