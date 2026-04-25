"""
Context processor para fornecer informações do tenant aos templates.

VERSÃO SIMPLIFICADA - Não faz queries ao banco para evitar erros 500
quando o banco está vazio ou inacessível (ex: PostgreSQL do Render hibernando).
"""
from django.urls import reverse


def tenant_context(request):
    """
    Fornece contexto básico para os templates.

    IMPORTANTE: Este context processor roda em TODAS as páginas,
    então não pode fazer queries ao banco de dados.
    """

    # Retornar contexto mínimo que não requer banco
    return {
        'pet_shop': None,
        'dashboard_url': '/',
        'tutor_list_url': '/',
        'appointment_list_url': '/',
        'pet_list_url': '/',
        'service_list_url': '/',
        'config_url': '/config/',
    }