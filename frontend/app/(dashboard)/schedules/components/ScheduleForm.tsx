'use client'

import { useState, useEffect } from 'react'
import { Schedule, ScheduleCreateInput } from '../hooks/useSchedules'
import { getApi } from '@/lib/api'

interface Bot {
  id: string
  nome: string
}

const STEPS = ['Bot', 'Chats Origem', 'Chats Destino', 'Horários', 'Tipo & Mídia', 'Revisão']

const MEDIA_OPTIONS = [
  { value: 'todos', label: 'Todos os tipos', icon: '📋' },
  { value: 'foto', label: 'Fotos', icon: '📷' },
  { value: 'video', label: 'Vídeos', icon: '🎬' },
  { value: 'texto', label: 'Texto', icon: '💬' },
  { value: 'documento', label: 'Documentos', icon: '📄' },
  { value: 'audio', label: 'Áudio', icon: '🎵' },
]

interface ScheduleFormProps {
  onSubmit: (data: ScheduleCreateInput) => Promise<void>
  onCancel: () => void
  initialData?: Schedule | null
  isLoading: boolean
}

export default function ScheduleForm({ onSubmit, onCancel, initialData, isLoading }: ScheduleFormProps) {
  const [step, setStep] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [bots, setBots] = useState<Bot[]>([])

  const [formData, setFormData] = useState<ScheduleCreateInput>({
    nome: '',
    bot_id: '',
    chats_origem: [],
    chats_destino: [],
    horarios: [],
    tipo_envio: 'pontual',
    tipo_midia: ['todos'],
    filtros: [],
  })
  const [newOrigem, setNewOrigem] = useState('')
  const [newDestino, setNewDestino] = useState('')
  const [newHorario, setNewHorario] = useState('')

  useEffect(() => {
    if (initialData) {
      setFormData({
        nome: initialData.nome,
        bot_id: initialData.bot_id,
        chats_origem: initialData.chats_origem || [],
        chats_destino: initialData.chats_destino || [],
        horarios: initialData.horarios || [],
        tipo_envio: initialData.tipo_envio || 'pontual',
        tipo_midia: initialData.tipo_midia || ['todos'],
        filtros: initialData.filtros || [],
      })
    }
  }, [initialData])

  useEffect(() => {
    const fetchBots = async () => {
      try {
        const api = getApi()
        const res = await api.get('/bots', { params: { page: 1, page_size: 100 } })
        const data = res.data
        setBots(Array.isArray(data) ? data : data.items || data.data || [])
      } catch { setBots([]) }
    }
    fetchBots()
  }, [])

  const addToList = (field: 'chats_origem' | 'chats_destino', value: string, setter: (v: string) => void) => {
    const trimmed = value.trim()
    if (!trimmed) return
    setFormData(prev => ({ ...prev, [field]: [...prev[field], trimmed] }))
    setter('')
  }

  const removeFromList = (field: 'chats_origem' | 'chats_destino', idx: number) => {
    setFormData(prev => ({ ...prev, [field]: prev[field].filter((_, i) => i !== idx) }))
  }

  const addHorario = () => {
    const trimmed = newHorario.trim()
    if (!trimmed || formData.horarios.includes(trimmed)) return
    setFormData(prev => ({ ...prev, horarios: [...prev.horarios, trimmed].sort() }))
    setNewHorario('')
  }

  const toggleMedia = (value: string) => {
    if (value === 'todos') {
      setFormData(prev => ({ ...prev, tipo_midia: ['todos'] }))
      return
    }
    setFormData(prev => {
      const current = prev.tipo_midia.filter(m => m !== 'todos')
      const has = current.includes(value)
      return { ...prev, tipo_midia: has ? current.filter(m => m !== value) : [...current, value] }
    })
  }

  const handleSubmit = async () => {
    setError(null)
    if (!formData.nome.trim()) { setError('Nome é obrigatório'); return }
    if (!formData.bot_id) { setError('Selecione um bot'); return }
    if (formData.horarios.length === 0) { setError('Adicione ao menos um horário'); return }
    try {
      await onSubmit(formData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar.')
    }
  }

  const canNext = () => {
    if (step === 0) return !!formData.nome && !!formData.bot_id
    if (step === 3) return formData.horarios.length > 0
    return true
  }

  return (
    <div className="flex flex-col h-full">
      {/* Steps indicator */}
      <div className="flex items-center gap-1 mb-6 overflow-x-auto pb-1">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={() => i < step && setStep(i)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                i === step
                  ? 'bg-blue-600 text-white shadow-sm'
                  : i < step
                  ? 'bg-blue-100 text-blue-700 hover:bg-blue-200 cursor-pointer'
                  : 'bg-gray-100 text-gray-400 cursor-default'
              }`}
            >
              {i < step ? '✓' : i + 1} {s}
            </button>
            {i < STEPS.length - 1 && <div className={`w-4 h-px ${i < step ? 'bg-blue-300' : 'bg-gray-200'}`} />}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="flex-1 overflow-y-auto space-y-4">

        {/* Step 0: Bot + Nome */}
        {step === 0 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Agendamento *</label>
              <input
                type="text"
                value={formData.nome}
                onChange={e => setFormData(p => ({ ...p, nome: e.target.value }))}
                placeholder="Ex: Envio diário de promoções"
                className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Bot *</label>
              {bots.length === 0 ? (
                <p className="text-sm text-gray-500 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  ⚠️ Nenhum bot disponível. Crie um bot primeiro em <strong>Bots</strong>.
                </p>
              ) : (
                <select
                  value={formData.bot_id}
                  onChange={e => setFormData(p => ({ ...p, bot_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                >
                  <option value="">Selecione um bot...</option>
                  {bots.map(b => <option key={b.id} value={b.id}>{b.nome}</option>)}
                </select>
              )}
            </div>
          </div>
        )}

        {/* Step 1: Chats Origem */}
        {step === 1 && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">Adicione os chats/grupos de onde as mensagens serão enviadas (username ou ID numérico).</p>
            <div className="flex gap-2">
              <input
                value={newOrigem}
                onChange={e => setNewOrigem(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addToList('chats_origem', newOrigem, setNewOrigem)}
                placeholder="@grupo ou -100123456"
                className="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button onClick={() => addToList('chats_origem', newOrigem, setNewOrigem)}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                Adicionar
              </button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {formData.chats_origem.map((c, i) => (
                <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border border-gray-200">
                  <span className="text-sm font-mono text-gray-700">{c}</span>
                  <button onClick={() => removeFromList('chats_origem', i)} className="text-red-400 hover:text-red-600 text-sm">✕</button>
                </div>
              ))}
              {formData.chats_origem.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-4">Nenhum chat adicionado ainda</p>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Chats Destino */}
        {step === 2 && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">Adicione os destinos onde as mensagens serão encaminhadas.</p>
            <div className="flex gap-2">
              <input
                value={newDestino}
                onChange={e => setNewDestino(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addToList('chats_destino', newDestino, setNewDestino)}
                placeholder="@canal ou -100789012"
                className="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button onClick={() => addToList('chats_destino', newDestino, setNewDestino)}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                Adicionar
              </button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {formData.chats_destino.map((c, i) => (
                <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border border-gray-200">
                  <span className="text-sm font-mono text-gray-700">{c}</span>
                  <button onClick={() => removeFromList('chats_destino', i)} className="text-red-400 hover:text-red-600 text-sm">✕</button>
                </div>
              ))}
              {formData.chats_destino.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-4">Nenhum destino adicionado ainda</p>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Horários */}
        {step === 3 && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">Adicione os horários de envio no formato HH:MM (ex: 09:00, 14:30).</p>
            <div className="flex gap-2">
              <input
                type="time"
                value={newHorario}
                onChange={e => setNewHorario(e.target.value)}
                className="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button onClick={addHorario}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                Adicionar
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.horarios.map((h, i) => (
                <span key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-mono border border-blue-200">
                  🕐 {h}
                  <button onClick={() => setFormData(p => ({ ...p, horarios: p.horarios.filter((_, j) => j !== i) }))}
                    className="text-blue-400 hover:text-blue-700 text-xs">✕</button>
                </span>
              ))}
              {formData.horarios.length === 0 && (
                <p className="text-xs text-gray-400 py-4 w-full text-center">Nenhum horário configurado</p>
              )}
            </div>
          </div>
        )}

        {/* Step 4: Tipo & Mídia */}
        {step === 4 && (
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Envio</label>
              <div className="grid grid-cols-2 gap-3">
                {(['pontual', 'sequencial'] as const).map(tipo => (
                  <button
                    key={tipo}
                    onClick={() => setFormData(p => ({ ...p, tipo_envio: tipo }))}
                    className={`p-3 rounded-xl border-2 text-left transition-all ${
                      formData.tipo_envio === tipo ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <p className="text-lg mb-1">{tipo === 'pontual' ? '📍' : '🔁'}</p>
                    <p className="text-sm font-semibold capitalize text-gray-900">{tipo}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {tipo === 'pontual' ? 'Envia mensagem única' : 'Envia em sequência'}
                    </p>
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipos de Mídia</label>
              <div className="grid grid-cols-3 gap-2">
                {MEDIA_OPTIONS.map(m => (
                  <button
                    key={m.value}
                    onClick={() => toggleMedia(m.value)}
                    className={`p-2.5 rounded-xl border-2 text-center transition-all ${
                      formData.tipo_midia.includes(m.value) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <p className="text-xl">{m.icon}</p>
                    <p className="text-xs font-medium text-gray-700 mt-0.5">{m.label}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Review */}
        {step === 5 && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 font-medium">Nome</span>
                <span className="text-gray-900">{formData.nome}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 font-medium">Tipo Envio</span>
                <span className="capitalize">{formData.tipo_envio}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 font-medium">Origens</span>
                <span>{formData.chats_origem.length} chat(s)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 font-medium">Destinos</span>
                <span>{formData.chats_destino.length} chat(s)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 font-medium">Horários</span>
                <span>{formData.horarios.join(', ')}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500 font-medium">Mídia</span>
                <span>{formData.tipo_midia.join(', ')}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Footer */}
      <div className="flex gap-3 mt-6 pt-4 border-t border-gray-100">
        {step > 0 ? (
          <button onClick={() => setStep(s => s - 1)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            ← Voltar
          </button>
        ) : (
          <button onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
        )}
        <div className="flex-1" />
        {step < STEPS.length - 1 ? (
          <button
            onClick={() => setStep(s => s + 1)}
            disabled={!canNext()}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Próximo →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {isLoading && (
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {initialData ? 'Salvar Alterações' : 'Criar Agendamento'}
          </button>
        )}
      </div>
    </div>
  )
}
