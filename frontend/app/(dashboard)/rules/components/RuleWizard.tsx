'use client'

import React, { useState, useEffect } from 'react'
import { RegraCreateData, RegraFull, RegraUpdateData, useRules } from '../hooks/useRules'
import { getApi } from '@/lib/api'
import { UUID } from '@/lib/types'

interface Bot {
  id: UUID
  nome: string
  ativo: boolean
}

interface RuleWizardProps {
  mode: 'create' | 'edit'
  initialData?: RegraFull
  onComplete: () => void
  onCancel: () => void
}

const INITIAL_FORM_STATE = {
  nome: '',
  bot_id: '' as UUID | '',
  marketplace_integracao_id: null as UUID | null,
  substituto: '',
  filtro_midia: 'todos',
  converter_link: false,
  origens: [] as string[],
  destinos: [] as string[],
  filtros: [] as Array<{ tipo: string; valor: string }>,
  condicoes: [] as string[],
}

/**
 * 7-Step Rule Creation/Edit Wizard
 *
 * Steps:
 * 1. Select bot
 * 2. Select source chats
 * 3. Select destination chats
 * 4. Configure filters (whitelist/blacklist)
 * 5. Configure conditions
 * 6. Select media types
 * 7. Review and submit
 *
 * Features:
 * - Step validation
 * - Progress tracking
 * - Back/Next navigation
 * - Form state persistence
 * - Real-time validation
 * - Pre-fill for editing
 */
export function RuleWizard({
  mode,
  initialData,
  onComplete,
  onCancel,
}: RuleWizardProps) {
  const { create, update } = useRules()
  const api = getApi()

  // Wizard state
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState(INITIAL_FORM_STATE)
  const [bots, setBots] = useState<Bot[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadingBots, setLoadingBots] = useState(true)

  // Load bots
  useEffect(() => {
    const loadBots = async () => {
      try {
        const response = await api.get<Bot[]>('/bots')
        setBots(response.data)
      } catch (err) {
        console.error('Failed to load bots:', err)
        setError('Erro ao carregar bots')
      } finally {
        setLoadingBots(false)
      }
    }
    loadBots()
  }, [api])

  // Pre-fill for edit mode
  useEffect(() => {
    if (mode === 'edit' && initialData) {
      setFormData({
        nome: initialData.nome,
        bot_id: initialData.bot_id,
        marketplace_integracao_id: initialData.marketplace_integracao_id ?? null,
        substituto: initialData.substituto || '',
        filtro_midia: initialData.filtro_midia,
        converter_link: initialData.converter_link,
        origens: initialData.origens.map((o) => o.origem),
        destinos: initialData.destinos.map((d) => d.destino),
        filtros: initialData.filtros.map((f) => ({
          tipo: f.tipo,
          valor: f.valor,
        })),
        condicoes: initialData.condicoes.map((c) => c.condicao),
      })
    }
  }, [mode, initialData])

  // Step validation
  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.bot_id !== ''
      case 2:
        return formData.origens.length > 0
      case 3:
        return formData.destinos.length > 0
      case 4:
        return true // Filters are optional
      case 5:
        return true // Conditions are optional
      case 6:
        return true // Media type has default
      case 7:
        return (
          formData.nome.trim() !== '' &&
          formData.bot_id !== '' &&
          formData.origens.length > 0 &&
          formData.destinos.length > 0
        )
      default:
        return true
    }
  }

  const handleNext = () => {
    if (isStepValid() && currentStep < 7) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    if (!isStepValid()) {
      setError('Preencha todos os campos obrigatórios')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      if (mode === 'create') {
        await create(formData as RegraCreateData)
      } else if (mode === 'edit' && initialData) {
        const updateData: RegraUpdateData = {
          nome: formData.nome,
          substituto: formData.substituto || null,
          filtro_midia: formData.filtro_midia,
          converter_link: formData.converter_link,
        }
        await update(initialData.id, updateData)
        // Note: Child records (origens, destinos, filtros, condicoes) would need separate endpoints
      }
      onComplete()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao salvar regra')
      console.error('Failed to submit:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loadingBots) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin">⟳ Carregando...</div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-2xl rounded-lg bg-white shadow-lg overflow-auto max-h-screen">
        {/* Header */}
        <div className="border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Nova Regra' : 'Editar Regra'}
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            Passo {currentStep} de 7
          </p>
          {/* Progress Bar */}
          <div className="mt-4 h-2 rounded-full bg-gray-200 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300"
              style={{ width: `${(currentStep / 7) * 100}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 min-h-96">
          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Step 1: Select Bot */}
          {currentStep === 1 && (
            <StepSelectBot
              bots={bots}
              value={formData.bot_id}
              onChange={(bot_id) => setFormData({ ...formData, bot_id })}
            />
          )}

          {/* Step 2: Source Chats */}
          {currentStep === 2 && (
            <StepSourceChats
              value={formData.origens}
              onChange={(origens) => setFormData({ ...formData, origens })}
            />
          )}

          {/* Step 3: Destination Chats */}
          {currentStep === 3 && (
            <StepDestinationChats
              value={formData.destinos}
              onChange={(destinos) => setFormData({ ...formData, destinos })}
            />
          )}

          {/* Step 4: Filters */}
          {currentStep === 4 && (
            <StepFilters
              value={formData.filtros}
              onChange={(filtros) => setFormData({ ...formData, filtros })}
            />
          )}

          {/* Step 5: Conditions */}
          {currentStep === 5 && (
            <StepConditions
              value={formData.condicoes}
              onChange={(condicoes) => setFormData({ ...formData, condicoes })}
            />
          )}

          {/* Step 6: Media Types */}
          {currentStep === 6 && (
            <StepMediaTypes
              value={formData.filtro_midia}
              converterLink={formData.converter_link}
              onMediaTypeChange={(filtro_midia) =>
                setFormData({ ...formData, filtro_midia })
              }
              onConverterLinkChange={(converter_link) =>
                setFormData({ ...formData, converter_link })
              }
            />
          )}

          {/* Step 7: Review */}
          {currentStep === 7 && (
            <StepReview
              formData={formData}
              bots={bots}
              onChangeName={(nome) => setFormData({ ...formData, nome })}
              onChangeSubstituto={(substituto) =>
                setFormData({ ...formData, substituto })
              }
            />
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 bg-gray-50 p-6 flex justify-between gap-3">
          <button
            onClick={onCancel}
            className="rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Cancelar
          </button>
          <div className="flex gap-3">
            <button
              onClick={handlePrev}
              disabled={currentStep === 1}
              className="rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50 transition-colors"
            >
              ← Anterior
            </button>
            {currentStep < 7 && (
              <button
                onClick={handleNext}
                disabled={!isStepValid()}
                className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                Próximo →
              </button>
            )}
            {currentStep === 7 && (
              <button
                onClick={handleSubmit}
                disabled={!isStepValid() || isSubmitting}
                className="rounded-lg bg-green-600 px-4 py-2 font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {isSubmitting ? '✓ Salvando...' : 'Salvar Regra'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Step 1: Select Bot
 */
function StepSelectBot({
  bots,
  value,
  onChange,
}: {
  bots: Bot[]
  value: UUID | ''
  onChange: (bot_id: UUID) => void
}) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Qual bot executará esta regra?
        </h3>
        <p className="text-sm text-gray-600">
          Selecione a conta Telegram que processará as mensagens
        </p>
      </div>

      <div className="grid gap-3">
        {bots.length === 0 ? (
          <p className="text-sm text-gray-500">Nenhum bot disponível</p>
        ) : (
          bots.map((bot) => (
            <button
              key={bot.id}
              onClick={() => onChange(bot.id)}
              className={`rounded-lg border-2 p-4 text-left transition-all ${
                value === bot.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <p className="font-medium text-gray-900">{bot.nome}</p>
              <p className="mt-0.5 text-xs text-gray-500">
                ID: {String(bot.id).substring(0, 8)}
              </p>
              <div className="mt-2 flex items-center gap-2">
                <div
                  className={`h-2 w-2 rounded-full ${bot.ativo ? 'bg-green-500' : 'bg-gray-300'}`}
                />
                <span className="text-xs text-gray-600">
                  {bot.ativo ? 'Ativo' : 'Inativo'}
                </span>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  )
}

/**
 * Step 2: Source Chats
 */
function StepSourceChats({
  value,
  onChange,
}: {
  value: string[]
  onChange: (origens: string[]) => void
}) {
  const [input, setInput] = useState('')

  const handleAdd = () => {
    if (input.trim() && !value.includes(input.trim())) {
      onChange([...value, input.trim()])
      setInput('')
    }
  }

  const handleRemove = (chat: string) => {
    onChange(value.filter((c) => c !== chat))
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Selecione os chats de origem
        </h3>
        <p className="text-sm text-gray-600">
          De onde as mensagens serão lidas? (ex: @canal_vendas ou -1001234567890)
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="@canal_vendas ou -1001234567890"
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
          <button
            onClick={handleAdd}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            + Adicionar
          </button>
        </div>

        {value.length > 0 && (
          <div className="space-y-2 pt-2">
            {value.map((chat) => (
              <div
                key={chat}
                className="flex items-center justify-between rounded-lg bg-blue-50 p-3 border border-blue-200"
              >
                <p className="font-mono text-sm text-gray-900">{chat}</p>
                <button
                  onClick={() => handleRemove(chat)}
                  className="text-red-600 hover:text-red-700 font-bold"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {value.length === 0 && (
          <p className="text-sm text-gray-500 italic">
            Adicione pelo menos um chat de origem
          </p>
        )}
      </div>
    </div>
  )
}

/**
 * Step 3: Destination Chats
 */
function StepDestinationChats({
  value,
  onChange,
}: {
  value: string[]
  onChange: (destinos: string[]) => void
}) {
  const [input, setInput] = useState('')

  const handleAdd = () => {
    if (input.trim() && !value.includes(input.trim())) {
      onChange([...value, input.trim()])
      setInput('')
    }
  }

  const handleRemove = (chat: string) => {
    onChange(value.filter((c) => c !== chat))
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Selecione os chats de destino
        </h3>
        <p className="text-sm text-gray-600">
          Para onde as mensagens será encaminhadas?
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="@canal_destino ou -1009876543210"
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
          <button
            onClick={handleAdd}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            + Adicionar
          </button>
        </div>

        {value.length > 0 && (
          <div className="space-y-2 pt-2">
            {value.map((chat) => (
              <div
                key={chat}
                className="flex items-center justify-between rounded-lg bg-green-50 p-3 border border-green-200"
              >
                <p className="font-mono text-sm text-gray-900">{chat}</p>
                <button
                  onClick={() => handleRemove(chat)}
                  className="text-red-600 hover:text-red-700 font-bold"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {value.length === 0 && (
          <p className="text-sm text-gray-500 italic">
            Adicione pelo menos um chat de destino
          </p>
        )}
      </div>
    </div>
  )
}

/**
 * Step 4: Filters (Whitelist/Blacklist)
 */
function StepFilters({
  value,
  onChange,
}: {
  value: Array<{ tipo: string; valor: string }>
  onChange: (filtros: Array<{ tipo: string; valor: string }>) => void
}) {
  const [tipo, setTipo] = useState('incluir')
  const [palavra, setPalavra] = useState('')

  const handleAdd = () => {
    if (palavra.trim()) {
      onChange([...value, { tipo, valor: palavra.trim() }])
      setPalavra('')
    }
  }

  const handleRemove = (index: number) => {
    onChange(value.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Configure filtros de palavras-chave
        </h3>
        <p className="text-sm text-gray-600">
          <strong>Incluir:</strong> Só encaminha se contiver a palavra
          <br />
          <strong>Bloquear:</strong> Não encaminha se contiver a palavra
        </p>
      </div>

      <div className="space-y-3">
        <div className="grid gap-2 grid-cols-1 sm:grid-cols-4 items-end">
          <div className="sm:col-span-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="incluir">Incluir</option>
              <option value="bloquear">Bloquear</option>
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Palavra-chave
            </label>
            <input
              type="text"
              value={palavra}
              onChange={(e) => setPalavra(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
              placeholder="ex: promoção, urgente"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>
          <button
            onClick={handleAdd}
            className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            + Adicionar
          </button>
        </div>

        {value.length > 0 && (
          <div className="space-y-2 pt-2">
            {value.map((filter, index) => (
              <div
                key={index}
                className={`flex items-center justify-between rounded-lg p-3 border ${
                  filter.tipo === 'incluir'
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div>
                  <p className="text-xs font-medium text-gray-600 uppercase">
                    {filter.tipo}
                  </p>
                  <p className="font-mono text-sm text-gray-900">
                    {filter.valor}
                  </p>
                </div>
                <button
                  onClick={() => handleRemove(index)}
                  className="text-red-600 hover:text-red-700 font-bold"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <p className="text-xs text-gray-500 italic">
          Filtros são opcionais. Deixe em branco para não filtrar.
        </p>
      </div>
    </div>
  )
}

/**
 * Step 5: Conditions
 */
function StepConditions({
  value,
  onChange,
}: {
  value: string[]
  onChange: (condicoes: string[]) => void
}) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Condições obrigatórias
        </h3>
        <p className="text-sm text-gray-600">
          Marque as condições que a mensagem deve atender
        </p>
      </div>

      <div className="space-y-3">
        {[
          { id: 'tem_emoji', label: '✨ Deve ter emoji' },
          { id: 'tem_preco', label: '💰 Deve ter preço' },
          { id: 'horario_comercial', label: '🕐 Horário comercial (9h-18h)' },
          { id: 'autenticado', label: '✓ Remetente autenticado' },
        ].map((condition) => (
          <label
            key={condition.id}
            className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input
              type="checkbox"
              checked={value.includes(condition.id)}
              onChange={(e) => {
                if (e.target.checked) {
                  onChange([...value, condition.id])
                } else {
                  onChange(value.filter((c) => c !== condition.id))
                }
              }}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">{condition.label}</span>
          </label>
        ))}
      </div>

      <p className="text-xs text-gray-500 italic">
        Condições são opcionais.
      </p>
    </div>
  )
}

/**
 * Step 6: Media Types
 */
function StepMediaTypes({
  value,
  converterLink,
  onMediaTypeChange,
  onConverterLinkChange,
}: {
  value: string
  converterLink: boolean
  onMediaTypeChange: (tipo: string) => void
  onConverterLinkChange: (converter: boolean) => void
}) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Tipos de mídia
        </h3>
        <p className="text-sm text-gray-600">
          Filtrar o tipo de mensagem a encaminhar
        </p>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filtro de mídia
          </label>
          <select
            value={value}
            onChange={(e) => onMediaTypeChange(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="todos">Todos (sem filtro)</option>
            <option value="foto">Only Fotos</option>
            <option value="video">Only Vídeos</option>
            <option value="foto_video">Fotos ou Vídeos</option>
            <option value="documento">Only Documentos</option>
            <option value="audio">Only Áudios</option>
          </select>
        </div>

        <label className="flex items-center gap-3 rounded-lg border border-gray-200 p-4 hover:bg-gray-50 cursor-pointer transition-colors">
          <input
            type="checkbox"
            checked={converterLink}
            onChange={(e) => onConverterLinkChange(e.target.checked)}
            className="rounded border-gray-300 w-5 h-5"
          />
          <div>
            <p className="font-medium text-gray-900">
              🔗 Converter links de afiliado
            </p>
            <p className="text-xs text-gray-600">
              Converte links Shopee, AliExpress em seus links de afiliado
            </p>
          </div>
        </label>
      </div>
    </div>
  )
}

/**
 * Step 7: Review and Name
 */
function StepReview({
  formData,
  bots,
  onChangeName,
  onChangeSubstituto,
}: {
  formData: typeof INITIAL_FORM_STATE
  bots: Bot[]
  onChangeName: (name: string) => void
  onChangeSubstituto: (sub: string) => void
}) {
  const bot = bots.find((b) => b.id === formData.bot_id)

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Nome da regra *
        </label>
        <input
          type="text"
          value={formData.nome}
          onChange={(e) => onChangeName(e.target.value)}
          placeholder="ex: Reenviar para Suporte"
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Prefixo nas mensagens (opcional)
        </label>
        <input
          type="text"
          value={formData.substituto}
          onChange={(e) => onChangeSubstituto(e.target.value)}
          placeholder="ex: [SUPORTE] "
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />
        <p className="mt-1 text-xs text-gray-500">
          Este texto será adicionado no início de cada mensagem encaminhada
        </p>
      </div>

      {/* Summary */}
      <div className="rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 p-4 space-y-3">
        <h4 className="font-semibold text-gray-900">Resumo da Regra</h4>

        <div className="grid gap-3 text-sm">
          <div>
            <p className="text-gray-600">Bot</p>
            <p className="font-medium text-gray-900">{bot?.nome || 'N/A'}</p>
          </div>

          <div>
            <p className="text-gray-600">De (origem)</p>
            <div className="flex flex-wrap gap-2 mt-1">
              {formData.origens.map((o) => (
                <span
                  key={o}
                  className="inline-block bg-blue-100 text-blue-900 px-2 py-1 rounded text-xs"
                >
                  {o}
                </span>
              ))}
            </div>
          </div>

          <div>
            <p className="text-gray-600">Para (destino)</p>
            <div className="flex flex-wrap gap-2 mt-1">
              {formData.destinos.map((d) => (
                <span
                  key={d}
                  className="inline-block bg-green-100 text-green-900 px-2 py-1 rounded text-xs"
                >
                  {d}
                </span>
              ))}
            </div>
          </div>

          {formData.filtros.length > 0 && (
            <div>
              <p className="text-gray-600">Filtros</p>
              <p className="text-xs text-gray-700 mt-1">
                {formData.filtros.length} filtro(s) configurado(s)
              </p>
            </div>
          )}

          <div>
            <p className="text-gray-600">Tipo de mídia</p>
            <p className="font-medium text-gray-900 capitalize">
              {formData.filtro_midia}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
