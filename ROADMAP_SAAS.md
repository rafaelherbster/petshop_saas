# 🚀 Roadmap para SaaS de Pet Shop

## Estado Atual do Projeto

### ✅ O que já existe:
- **Multi-tenancy** funcionando (isolamento por PetShop)
- **Módulos básicos**: Cadastro (tutores/pets), Agenda, Financeiro, Prontuário
- **Autenticação** com Django auth (email como username)
- **UI com TailwindCSS** e HTMX
- **Modelos de Planos** (Free, Starter, Pro, Enterprise) - apenas定义, sem implementação
- **Testes** de isolamento multi-tenant passando

### ⚠️ O que falta (por prioridade)

---

## 🔴 CRÍTICO (Sem isso não funciona como SaaS)

### 1. Sistema de Pagamento e Assinaturas
- [ ] Integrar **Stripe** ou **Mercado Pago** para cobranças recorrentes
- [ ] Implementar webhooks para processar pagamentos
- [ ] Controlar acesso baseado no plano (Free vs Paid)
- [ ] Sistema de trial/grátis limitado
- [ ] Cobrança por uso (se aplicável)

### 2. Configurações de Produção
- [ ] Configurar **PostgreSQL** (SQLite não serve para produção)
- [ ] Configurar **Redis** para cache e sessões
- [ ] Configurar **WhiteNoise** para static files
- [ ] Configurações de segurança (HTTPS, headers, etc)
- [ ] Environment variables (.env)

### 3. Sistema de Onboarding
- [ ] Fluxo de cadastro completo (Wizard)
- [ ] Configuração inicial do petshop (nome, CNPJ, horário)
- [ ] Tutorial/boas-vindas para novos usuários

### 4. Limites por Plano
- [ ] Implementar verificação de limites (max pets, serviços, funcionários)
- [ ] Bloqueio de funcionalidades do plano gratuito
- [ ] Upgrade/downgrade de planos

---

## 🟡 IMPORTANTE (Experiência profissional)

### 5. Dashboard e Métricas
- [ ] Dashboard com métricas do negócio
- [ ] Relatórios de receita, agendamentos, clientes
- [ ] Indicadores de crescimento

### 6. Sistema de Notificações
- [ ] Lembretes de agendamento (WhatsApp/SMS/Email)
- [ ] Notificações internas
- [ ] Notificações de pagamento

### 7. Área do Cliente (App/Portal)
- [ ] Portal para tutores visualizarem seus pets e histórico
- [ ] Agendamento online pelos clientes
- [ ] App mobile (PWA ou nativo)

### 8. Segurança e Compliance
- [ ] LGPD - consentimento, política de privacidade
- [ ] Backup automático
- [ ] Logs de auditoria
- [ ] 2FA opcional

---

## 🟢 BOM TER (Diferencial competitivo)

### 9. Marketing e Growth
- [ ] Sistema de indicação (indique e ganhe)
- [ ] Código promocional / cupons de desconto
- [ ] Email marketing integrado (Mailchimp, etc)

### 10. Integrações
- [ ] API pública para integrações
- [ ] Integração com sistemas de NF-e
- [ ] Integração com WhatsApp Business API
- [ ] Integração com sistemas de delivery

### 11. Automação
- [ ] Automação de marketing (segmentação de clientes)
- [ ] Fluxos automatizados (aniversário do pet, etc)

### 12. Suporte
- [ ] Central de ajuda / FAQ
- [ ] Chat de suporte integrado
- [ ] Sistema de feedback

---

## 📋 Detalhamento Técnico

### Sistema de Pagamento (Stripe)

```python
# Exemplo de verificação de plano
def verificar_plano(user):
    subscription = user.profile.pet_shop.subscription
    if not subscription or not subscription.is_active:
        raise PermissionDenied("Assinatura inativa")

    plan = subscription.plan
    if plan.tier == Plan.Tier.FREE:
        # Verificar limites
        if Pet.objects.count() >= plan.max_pets:
            raise PermissionDenied("Limite de pets atingido")
```

### Variáveis de Ambiente (.env)

```
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com
DATABASE_URL=postgres://...
REDIS_URL=redis://...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
EMAIL_HOST=smtp....
```

### Limites por Plano (modelo)

| Recurso | Free | Starter | Pro | Enterprise |
|---------|------|---------|-----|------------|
| Pets | 10 | 50 | 200 | Ilimitado |
| Serviços | 5 | 20 | 50 | Ilimitado |
| Funcionários | 1 | 3 | 10 | Ilimitado |
| Agendamentos/mês | 50 | 200 | 1000 | Ilimitado |
| Agenda online | ❌ | ✅ | ✅ | ✅ |
| Relatórios | ❌ | Básico | Avançado | Completo |
| API | ❌ | ❌ | ✅ | ✅ |
| Suporte | Email | Email | Prioritário | Dedicação |

---

## 🎯 Sugestão de Priorização

### Fase 1 (MVP - 2-4 semanas)
1. PostgreSQL + Configuração de produção
2. Sistema de signup/onboarding
3. Stripe integrado (cobração básica)
4. Limites do plano Free implementados

### Fase 2 (Produto vendável - 2-3 meses)
1. Dashboard com métricas
2. Lembretes de agendamento
3. Portal do cliente
4. Segurança/LGPD

### Fase 3 (Escala - 3-6 meses)
1. API pública
2. Integrações
3. Automação de marketing
4. App mobile

---

## 💰 Estimativa de Custo Mensal (AWS/Render/Hetzner)

- **Servidor**: R$ 100-200/mês (1-2GB RAM, 1 CPU)
- **PostgreSQL**: R$ 50-100/mês (managed)
- **Redis**: R$ 30-50/mês (managed)
- **Domínio**: R$ 40/ano
- **SSL**: Grátis (Let's Encrypt)
- **Email**: R$ 0-50/mês (SendGrid/Resend)
- **SMS/WhatsApp**: R$ 100-300/mês (Twilio/Z-api)

**Total estimado**: R$ 300-700/mês para começar

---

## ⚡ Próximos Passos Imediatos

1. **Criar conta no Stripe** e configurar keys de teste
2. **Migrar para PostgreSQL** localmente
3. **Criar arquivo .env.example**
4. **Implementar fluxo de signup** completo
5. **Criar comando de verificação de limites**

Quer que eu comece a implementar algum desses itens?