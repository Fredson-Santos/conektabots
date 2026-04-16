'use client'

import { useState, useEffect } from 'react'
import { getApi } from '@/lib/api'

interface PlanUsage {
  plano: string
  bots_usados: number
  bots_limite: number
  regras_usadas: number
  regras_limite: number
  msgs_hora_usadas: number
  msgs_hora_limite: number
  renovacao?: string
}

const PLANS = [
  {
    nome: 'Free', preco: 'R$ 0', cor: 'border-gray-200',
    recursos: ['1 bot', '5 regras', '100 msgs/hora', 'Suporte por email'],
  },
  {
    nome: 'Starter', preco: 'R$ 49/mês', cor: 'border-blue-300',
    recursos: ['5 bots', '50 regras', '1.000 msgs/hora', 'Suporte prioritário'],
    destaque: true,
  },
  {
    nome: 'Pro', preco: 'R$ 149/mês', cor: 'border-purple-300',
    recursos: ['20 bots', '200 regras', '5.000 msgs/hora', 'Suporte dedicado', 'SLA 99.9%'],
  },
  {
    nome: 'Enterprise', preco: 'Consulte', cor: 'border-gray-300',
    recursos: ['Ilimitado', 'Regras ilimitadas', 'Msgs ilimitadas', 'Account Manager', 'SLA customizado'],
  },
]

interface BillingTabProps {
  onToast: (type: 'success' | 'error', message: string) => void
}

function UsageBar({ label, used, limit }: { label: string; used: number; limit: number }) {
  const pct = limit ? Math.min(100, Math.round((used / limit) * 100)) : 0
  const color = pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-orange-500' : 'bg-blue-500'

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-600 font-medium">{label}</span>
        <span className={pct > 90 ? 'text-red-600 font-semibold' : 'text-gray-500'}>
          {used.toLocaleString()} / {limit === -1 ? '∞' : limit.toLocaleString()} ({pct}%)
        </span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export function BillingTab({ onToast }: BillingTabProps) {
  const [usage, setUsage] = useState<PlanUsage | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const api = getApi()
        const res = await api.get('/dashboard/quota')
        setUsage(res.data)
      } catch {
        // Mock data for display if API not ready
        setUsage({
          plano: 'Free',
          bots_usados: 1, bots_limite: 1,
          regras_usadas: 3, regras_limite: 5,
          msgs_hora_usadas: 45, msgs_hora_limite: 100,
        })
      } finally { setLoading(false) }
    }
    fetchUsage()
  }, [])

  const handleUpgrade = () => {
    onToast('success', 'Redirecionando para o portal de pagamento...')
  }

  return (
    <div className="space-y-6">
      {/* Current plan usage */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-900">Plano Atual</h3>
          {usage && (
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
              {usage.plano}
            </span>
          )}
        </div>
        {loading ? (
          <div className="animate-pulse space-y-3">
            {[...Array(3)].map((_, i) => <div key={i} className="h-8 bg-gray-100 rounded" />)}
          </div>
        ) : usage ? (
          <div className="space-y-4">
            <UsageBar label="Bots" used={usage.bots_usados} limit={usage.bots_limite} />
            <UsageBar label="Regras" used={usage.regras_usadas} limit={usage.regras_limite} />
            <UsageBar label="Mensagens/hora" used={usage.msgs_hora_usadas} limit={usage.msgs_hora_limite} />
            {usage.renovacao && (
              <p className="text-xs text-gray-500 pt-2">
                Renovação em: {new Date(usage.renovacao).toLocaleDateString('pt-BR')}
              </p>
            )}
          </div>
        ) : null}
      </div>

      {/* Plans */}
      <div>
        <h3 className="text-base font-semibold text-gray-900 mb-3">Planos Disponíveis</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {PLANS.map(plan => (
            <div key={plan.nome} className={`relative bg-white rounded-xl border-2 p-4 shadow-sm ${plan.cor} ${plan.destaque ? 'ring-2 ring-blue-400' : ''}`}>
              {plan.destaque && (
                <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-blue-600 text-white text-xs font-bold rounded-full">
                  Popular
                </span>
              )}
              <h4 className="font-bold text-gray-900">{plan.nome}</h4>
              <p className="text-xl font-extrabold text-blue-600 mt-1">{plan.preco}</p>
              <ul className="mt-3 space-y-1.5">
                {plan.recursos.map(r => (
                  <li key={r} className="flex items-center gap-1.5 text-xs text-gray-600">
                    <span className="text-green-500 font-bold">✓</span> {r}
                  </li>
                ))}
              </ul>
              {usage?.plano === plan.nome ? (
                <p className="mt-4 text-center text-xs font-semibold text-blue-600">✓ Plano atual</p>
              ) : (
                <button onClick={handleUpgrade}
                  className={`mt-4 w-full py-2 rounded-lg text-sm font-semibold transition-colors ${
                    plan.destaque
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}>
                  {plan.nome === 'Enterprise' ? 'Falar com vendas' : `Escolher ${plan.nome}`}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
