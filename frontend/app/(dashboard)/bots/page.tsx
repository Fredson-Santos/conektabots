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

  // Calculate statistics
  const totalBots = bots.length
  const activeBots = bots.filter((bot) => bot.ativo).length
  const inactiveBots = totalBots - activeBots

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
      <div className="space-y-8">
        {/* Page Description */}
        <div>
          <p className="text-sm text-gray-600">
            Create, configure, and manage your Telegram bots.
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Total Bots Card */}
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Total Bots
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">
                  {totalBots}
                </p>
              </div>
              <div className="rounded-lg bg-blue-50 p-3">
                <svg
                  className="h-6 w-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Active Bots Card */}
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Active
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">
                  {activeBots}
                </p>
              </div>
              <div className="rounded-lg bg-green-50 p-3">
                <svg
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Inactive Bots Card */}
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Inactive
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">
                  {inactiveBots}
                </p>
              </div>
              <div className="rounded-lg bg-gray-100 p-3">
                <svg
                  className="h-6 w-6 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </div>
            </div>
          </div>
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
