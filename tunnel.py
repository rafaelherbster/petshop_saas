"""
Executar: python tunnel.py
Depois instalar ngrok e configurar token em: https://dashboard.ngrok.com/get-started/setup
"""
from pyngrok import ngrok

# Conecta na porta 8000
public_url = ngrok.connect(8000)
print(f"\n🎉 Acesse pelo celular:")
print(f"   {public_url}")
print(f"\n⚠️  Mantenha este terminal aberto!\n")