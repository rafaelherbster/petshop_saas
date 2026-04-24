---
name: Problemas Isolamento Tenant
description: Bugs detectados nos testes de isolamento multi-tenant
type: feedback
---

## Problema 1: get_current_pet_shop retorna valor incorreto nos testes
**Sintoma**: `Appointment.objects.all()` retorna dados de múltiplos tenants mesmo com tenant definido.
**Possível causa**: `get_current_pet_shop()` não está lendo o valor correto do thread-local durante a execução do QuerySet.
**Ação**: Testar no shell: `from core.middleware import get_current_pet_shop; print(get_current_pet_shop())`

## Problema 2: Criacao automática de Appointment falha com IntegrityError
**Sintoma**: `Appointment.objects.create(pet=..., date=..., ...)` levanta `NOT NULL constraint failed: agenda_appointment.pet_shop_id`
**Causa**: `TenantManager.create()` não está auto-atribuindo `pet_shop` (chama `get_current_pet_shop()` que retorna `None`)
**Ação**: Verificar se `TenantManager` é usado (modelo herda de `TenantModel`? Sim) e se `pet_shop` está em `kwargs`

## Problema 3: order_by quebra filtro
**Sintoma**: `Appointment.objects.order_by('-date')` retorna TODOS os appointments, não só do tenant
**Causa**: `_clone()` pode estar retornando um QuerySet que não tem o filtro aplicado, ou `order_by` está usando o manager base em vez do tenant-filtered
**Ação**: Remover `_clone()` e garantir que todos os métodos retornem `self._apply_tenant_filter()` ou um clone filtrado

## Problema 4: Tenant inativo ainda retorna dados
**Sintoma**: `set_current_pet_shop(shop_inactive)` ainda permite queries
**Causa raiz**: O middleware seta `request.pet_shop = None` se inativo, mas nos testes usamos `set_current_pet_shop()` diretamente (bypass do middleware). O `TenantQuerySet` deve **também** validar `is_active`?
**Decisão**: O TenantQuerySet deve bloquear se o pet_shop não estiver ativo? Ou confiar no middleware?

## Como debugar (próxima sessão)
```python
# No shell
from core.middleware import _thread_locals, get_current_pet_shop
from agenda.models import Appointment
shop = PetShop.objects.first()
set_current_pet_shop(shop)
print('pet_shop:', get_current_pet_shop())
print('qs type:', type(Appointment.objects.all()))
print('qs query:', Appointment.objects.all().query)
```

## Plano de correção sugerido
1. Remover `_clone()` de `TenantQuerySet` (pode não ser necessário — os métodos individuais já aplicam filtro)
2. Garantir que `TenantManager.get_queryset()` sempre retorna `TenantQuerySet` filtrado
3. Adicionar verificação de `is_active` dentro de `_apply_tenant_filter()`?  
   → Decisão: **NÃO** — o middleware já valida, mas nos testes diretos o `set_current_pet_shop` pode setar um shop inativo. Adicionar validação no `_apply_tenant_filter` extrai o shop e checa `.is_active` (custo: extra DB query por request).  
   → Alternativa: nos testes, sempre usar shop ativo.
