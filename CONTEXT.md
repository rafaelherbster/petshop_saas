# Contexto da Implementação Multi-tenant

## Problemas Identificados (Original)
1. TenantMiddleware: race condition, falta verificação is_active, risco de acesso entre tenants
2. Modelo Tutor: falta constraint unique por (pet_shop, phone)
3. (Não havia FIN_ENTREGUE — descartado)

## Soluções Implementadas

### Camada 1 — TenantMiddleware (core/middleware.py)
- Valida `profile.pet_shop` e `pet_shop.is_active`
- Armazena tenant em thread-local (`_thread_locals`)
- Catch global `Exception` → `request.pet_shop = None`
- Cleanup no `finally` evita vazamento entre threads

### Camada 2 — TenantManager + TenantQuerySet (core/models.py)
- Filtro automático por `pet_shop` em todos os modelos que herdam de `TenantModel`
- Levanta `PermissionDenied` se tenant for `None`
- `_clone()` override para manter filtro em query-chaining
- Auto-assigna `pet_shop` no `.create()` e `save()`

### Camada 3 — Views atualizadas
- Models `TenantModel` (Appointment, Pet, Service, HealthRecord): queries **sem** filtro manual
- Models não-`TenantModel` (Tutor, Payment, LoyaltyCard): **mantêm** filtros manuais `pet_shop=request.pet_shop` ou relacionamentos

### Admin multi-tenant (core/admin_base.py + admin.py em cada app)
- `TenantModelAdmin` herda de `admin.ModelAdmin`
- Filtra automaticamente por `request.pet_shop`
- Superusers/staff veem todos (bypass)
- Auto-assigna `pet_shop` na criação

## Migrations Aplicadas
- `cadastro/0004_tutor_unique_tutor_phone_per_petshop` ✅

## Arquivos Modificados/Criados
```
core/
  middleware.py      (refatorado)
  models.py          (adicionado TenantManager, TenantQuerySet)
  admin_base.py      (criado)
  admin.py           (existente, já estava)
agenda/
  views.py           (atualizado)
  admin.py           (criado)
cadastro/
  models.py          (adicionado constraint)
  views.py           (atualizado)
  admin.py           (criado)
financeiro/
  views.py           (atualizado)
  admin.py           (criado)
prontuario/
  views.py           (atualizado)
  admin.py           (criado)
```

## ❌ Problema Detectado nos Testes

### TESTE 1: Sem tenant => Expected PermissionDenied, mas retornou dados
Isso significa que `Appointment.objects.all()` **não** levantou `PermissionDenied` quando `pet_shop=None`.

**Causa provável:** O `TenantQuerySet._apply_tenant_filter()` não está sendo chamado ou `get_current_pet_shop()` está retornando um valor inesperado.

**Suspeita:** O método `_clone()` pode estar interferindo, ou o manager está usando um queryset padrão em vez do TenantQuerySet.

### TESTE 2: Com tenant ativo => retornou 6 appointments (de todos os tenants, não apenas 1)
Confirmando que o filtro de tenant não está aplicando.

### TESTE 3: Tenant inativo => retornou dados (esperado 0)
- Mostra que `is_active` check não está funcionando no queryset (só no middleware seta request.pet_shop = None se inativo, mas o queryset ainda pode ter tenant setado manualmente no thread-local)

### TESTE 4: Criacao automática de Appointment => IntegrityError (pet_shop NULL)
O `TenantManager.create` não auto-atribuiu `pet_shop`. Isso indica que `get_current_pet_shop()` retornou `None` no momento da criação, ou o manager não está sendo usado.

### TESTE 5: order_by quebrou filtro
O `_clone()` pode não estar funcionando como esperado.

---

## 🎯 Tarefas Pendentes (Próxima Sessão)

### 1. Depurar TenantQuerySet
- Por que `get_current_pet_shop()` parece retornar valor incorreto nos testes?
- Verificar se `TenantManager` está corretamente vinculado aos modelos
- Teste manual no shell do Django para isolar o problema

### 2. Corrigir auto-geração de pet_shop no create()
- O `TenantManager.create` deve auto-atribuir `pet_shop` se não fornecido
- Verificar se `get_current_pet_shop()` está acessível no contexto de criação

### 3. Garantir que isativo bloqueia acesso
- Se `request.pet_shop` é None (por inativo), as queries devem levantar `PermissionDenied`
- Talvez precisamos de um middleware extra que valida `request.pet_shop` e limpa thread-local se inativo

### 4. Ajustar `_clone()` para não quebrar encadeamento
- O `_clone()` atual pode estar causando comportamentos inesperados
- Talvez remover `_clone()` e confiar nos métodos overrides (`filter`, `all`, etc.)

### 5. Testes manuais finais
- Criar dois pet_shops com usuários diferentes
- Tentar acessar appointments do outro tenant (deve falhar)
- Testar admin: superuser vs usuário normal
- Testar criação via views

### 6. (Opcional) Separar thread-local em módulo dedicado
- Evita import circular between middleware e models
- Criar `core/tenant_context.py` com `get_current_pet_shop`/`set_current_pet_shop`

### 7. Revisar Todas as Views
- Garantir que todas as queries de modelos TenantModel não tenham `pet_shop=` manual
- Garantir que modelos não-tenant tenham filtro correto

---

## Como Retomar

Quando você voltar, inicie com:
> "Continuando a implementação multi-tenant"

E eu devo:
1. Ler este arquivo `CONTEXT.md`
2. Executar os testes novamente (ou analisar o problema do TenantQuerySet)
3. Corrigir as falhas detectadas
4. Validar isolation completa
