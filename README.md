# PetShop Pro - Sistema de Gestão para Pet Shops

Sistema SaaS multi-tenant para gestão de pet shops.

## 🚀 Deploy no Render

### Pré-requisitos
- Conta no [Render](https://render.com)
- Repositório GitHub com o projeto

### Passo a Passo

1. **Faça push do código para GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/seu-usuario/petshop-saas.git
   git push -u origin main
   ```

2. **Crie o banco de dados no Render**
   - Acesse https://dashboard.render.com
   - New → PostgreSQL
   - Nome: `petshop_saas`
   - Salve a DATABASE_URL (você precisará dela)

3. **Crie o Web Service**
   - New → Web Service
   - Conecte seu repositório GitHub
   - Configure:
     - Name: `petshop-saas`
     - Runtime: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn config.wsgi --log-file - --bind 0.0.0.0:$PORT`
   - Add Environment Variable:
     - `SECRET_KEY` = (gere uma com: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
     - `ALLOWED_HOSTS` = `seu-app.onrender.com`
     - `DATABASE_URL` = (a URL do PostgreSQL que você criou)

4. **Deploy**
   - Clique em "Create Web Service"
   - Aguarde o deploy terminar

5. **Migrações**
   - Após o deploy, vá em "Shell" no dashboard do Render
   - Execute: `python manage.py migrate`

6. **Crie superuser (opcional)**
   - No shell: `python manage.py createsuperuser`

### URLs
- Seu app: `https://seu-app.onrender.com`
- Admin: `https://seu-app.onrender.com/admin/`

---

## 🛠️ Desenvolvimento Local

```bash
# Clone
git clone https://github.com/seu-usuario/petshop-saas.git
cd petshop-saas

# Crie ambiente virtual
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Copie o arquivo de ambiente
copy .env.example .env

# Execute migrações
python manage.py migrate

# Rode o servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

---

## 📱 Funcionalidades

- ✅ Cadastro de tutores e pets
- ✅ Agenda de serviços
- ✅ Controle financeiro
- ✅ Prontuário médico
- ✅ Multi-tenancy (vários pet shops no mesmo sistema)
- ✅ Recuperação de senha
- ✅ Design responsivo (funciona no celular)

---

## 📝 Notas

- O plano gratuito do Render hiberna após 15 min de inatividade
- Na primeira acesso após hibernar, pode demorar ~30s para acordar
- Para evitar isso, upgrade para plano pago (~$7/mês)