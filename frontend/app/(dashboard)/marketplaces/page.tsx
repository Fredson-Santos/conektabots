'use client'

import { useEffect, useState } from 'react'
import { DashboardLayout, navigationItems } from '@/app/components/layout'
import { Button, Alert, EmptyState, Card } from '@/app/components/ui'
import { PlusIcon, ShoppingCartIcon } from '@heroicons/react/24/outline'
import { useMarketplaces, Marketplace, MarketplaceCreateInput } from './hooks/useMarketplaces'
import MarketplacesTable from './components/MarketplacesTable'
import CreateMarketplaceModal from './components/CreateMarketplaceModal'

function DeleteMarketplaceModal({
  isOpen,
  marketplace,
  isLoading,
  onConfirm,
  onCancel,
}: {
  isOpen: boolean
  marketplace: Marketplace | null
  isLoading: boolean
  onConfirm: () => void
  onCancel: () => void
}) {
  if (!isOpen || !marketplace) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-white rounded-lg shadow-lg w-full max-w-md p-lg space-y-md">
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto">
          <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </div>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900">Remove Integration?</h3>
          <p className="mt-2 text-sm text-gray-600">
            Remove <strong>{marketplace.nome}</strong>? This action cannot be undone.
          </p>
        </div>
        <div className="flex gap-md pt-md">
          <Button variant="secondary" size="md" fullWidth onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="danger"
            size="md"
            fullWidth
            loading={isLoading}
            onClick={onConfirm}
          >
            Remove
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function MarketplacesPage() {
  const {
    marketplaces,
    loading,
    error,
    totalPages,
    currentPage,
    fetchMarketplaces,
    createMarketplace,
    updateMarketplace,
    deleteMarketplace,
    testConnection,
  } = useMarketplaces()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingMarketplace, setEditingMarketplace] = useState<Marketplace | null>(null)
  const [deletingMarketplace, setDeletingMarketplace] = useState<Marketplace | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchMarketplaces(1)
  }, [])

  const handleCreate = async (data: MarketplaceCreateInput) => {
    setIsSubmitting(true)
    try {
      await createMarketplace(data)
      setIsModalOpen(false)
    } catch (err) {
      console.error('Failed to create marketplace:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdate = async (data: MarketplaceCreateInput) => {
    if (!editingMarketplace) return
    setIsSubmitting(true)
    try {
      await updateMarketplace(editingMarketplace.id, data)
      setEditingMarketplace(null)
      setIsModalOpen(false)
    } catch (err) {
      console.error('Failed to update marketplace:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!deletingMarketplace) return
    setIsDeleting(true)
    try {
      await deleteMarketplace(deletingMarketplace.id)
      setDeletingMarketplace(null)
    } catch (err) {
      console.error('Failed to delete marketplace:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleTest = async (m: Marketplace) => {
    const result = await testConnection(m.id)
    console.log(result)
  }

  return (
    <DashboardLayout
      sidebarItems={navigationItems}
      title="Marketplaces"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Marketplaces' },
      ]}
      actions={
        <Button
          variant="primary"
          size="md"
          icon={<PlusIcon className="w-5 h-5" />}
          onClick={() => {
            setEditingMarketplace(null)
            setIsModalOpen(true)
          }}
        >
          Add Integration
        </Button>
      }
    >
      <div className="space-y-lg">
        {/* Page Description */}
        <div>
          <p className="text-sm text-gray-600">
            Connect and manage integrations with sales marketplaces like Shopee, Mercado Livre, and Amazon.
          </p>
        </div>

        {/* Error Alert */}
        {error && !loading && (
          <Alert
            type="error"
            title="Error Loading Marketplaces"
            description={error}
            action={{ label: 'Retry', onClick: () => fetchMarketplaces(currentPage) }}
          />
        )}

        {/* Empty State */}
        {!loading && marketplaces.length === 0 ? (
          <EmptyState
            icon={<ShoppingCartIcon className="w-12 h-12 text-gray-400" />}
            title="No integrations yet"
            description="Connect your first marketplace to automate messages across multiple channels"
            action={{
              label: 'Add Integration',
              onClick: () => {
                setEditingMarketplace(null)
                setIsModalOpen(true)
              },
              icon: <PlusIcon className="w-5 h-5" />,
            }}
          />
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-lg">
              <Card>
                <div className="p-md space-y-sm">
                  <p className="text-xs font-semibold uppercase text-gray-500">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{marketplaces.length}</p>
                </div>
              </Card>
              <Card>
                <div className="p-md space-y-sm">
                  <p className="text-xs font-semibold uppercase text-gray-500">Active</p>
                  <p className="text-2xl font-bold text-green-600">
                    {marketplaces.filter((m) => m.status === 'ativo').length}
                  </p>
                </div>
              </Card>
              <Card>
                <div className="p-md space-y-sm">
                  <p className="text-xs font-semibold uppercase text-gray-500">Errors</p>
                  <p className="text-2xl font-bold text-red-600">
                    {marketplaces.filter((m) => m.status === 'erro').length}
                  </p>
                </div>
              </Card>
              <Card>
                <div className="p-md space-y-sm">
                  <p className="text-xs font-semibold uppercase text-gray-500">Inactive</p>
                  <p className="text-2xl font-bold text-gray-500">
                    {marketplaces.filter((m) => m.status === 'inativo').length}
                  </p>
                </div>
              </Card>
            </div>

            {/* Marketplaces Table */}
            <MarketplacesTable
              marketplaces={marketplaces}
              loading={loading && marketplaces.length === 0}
              onEdit={(m) => {
                setEditingMarketplace(m)
                setIsModalOpen(true)
              }}
              onDelete={(m) => setDeletingMarketplace(m)}
              onTestConnection={handleTest}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={(p) => fetchMarketplaces(p)}
            />
          </>
        )}

        {/* Create/Edit Modal */}
        <CreateMarketplaceModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            setEditingMarketplace(null)
          }}
          onSubmit={editingMarketplace ? handleUpdate : handleCreate}
          marketplace={editingMarketplace}
          isLoading={isSubmitting}
        />

        {/* Delete Confirmation Modal */}
        <DeleteMarketplaceModal
          isOpen={deletingMarketplace !== null}
          marketplace={deletingMarketplace}
          isLoading={isDeleting}
          onConfirm={handleDelete}
          onCancel={() => setDeletingMarketplace(null)}
        />
      </div>
    </DashboardLayout>
  )
}
