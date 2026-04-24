---
name: Implementacao Multi-tenant
description: Arquitetura de isolamento multi-tenant implementada
type: reference
---

## Middleware
- **Arquivo**: `core/middleware.py`
- **Responsabilidade**: Extrair e validar o PetShop do usuário, armazenar em thread-local
- **Valida**: `profile.pet_shop` existe e `is_active=True`
- **Fallback**: Qualquer erro → `request.pet_shop = None`
- **Thread-local**: Usa `_thread_locals` com cleanup no `finally`

## Manager + QuerySet
- **Arquivo**: `core/models.py`
- **TenantQuerySet**: Intercepta `get()`, `filter()`, `all()`, etc. → adiciona `pet_shop=current`
- **PermissionDenied**: Se `pet_shop=None` → operação bloqueada
- **TenantManager**: Usa `TenantQuerySet`, auto-atribui `pet_shop` no `.create()`
- **TenantModel**: Abstract model com `pet_shop` + `objects = TenantManager()`

## Models que usam TenantModel
- Appointment, Service, Pet (cadastro), HealthRecord

## Models que NAO usam TenantModel (precisam filtro manual)
- Tutor (tem `pet_shop` mas não herda de TenantModel)
- LoyaltyCard (usa `pet__pet_shop`)
- Payment (usa `appointment__pet_shop`)
- UserProfile (tem `pet_shop`, mas não é multi-tenant crítico)

## Views
- Models TenantModel: removidos filtros `pet_shop=request.pet_shop`
- Models não-TenantModel: mantidos filtros manuais

## Admin
- `TenantModelAdmin`: filtro automático por `request.pet_shop`
- Superusers/staff: bypass do filtro (veem todos)
- Configurações por modelo: `tenant_field` para relacionamentos (ex: `pet__pet_shop`)
