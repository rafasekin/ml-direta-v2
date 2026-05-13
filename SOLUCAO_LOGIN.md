# Solução de Problemas de Login

## 🔍 Verificação de Credenciais

### Credenciais Corretas:
```
Login: RafaelPinho
Senha: @21314100
```

## ⚠️ Pontos Comuns de Erro:

### 1. **Letras Maiúsculas/Minúsculas**
- ❌ Errado: rafaelpinho
- ❌ Errado: RAFAELPINHO  
- ✅ Correto: RafaelPinho

### 2. **Caracteres Especiais na Senha**
- ❌ Errado: 21314100 (sem @)
- ❌ Errado: @ 21314100 (com espaço)
- ✅ Correto: @21314100

### 3. **Espaços em Branco**
- ❌ Errado: " RafaelPinho " (com espaços)
- ❌ Errado: "@21314100 " (com espaço no final)
- ✅ Correto: RafaelPinho (sem espaços)

### 4. **Copiar e Colar**
- Ao copiar, verifique se não veio com espaços extras
- Digite manualmente se necessário

## 🧪 Como Testar:

### Método 1: Teste via Terminal
```bash
cd "pasta do sistema"
python test_login.py
```

### Método 2: Verificação Manual
```bash
python -c "
from app import load_data, check_password_hash
users = load_data('data/users.json')
for uid, user in users.items():
    if user['login'] == 'RafaelPinho':
        print('Usuario encontrado:', user['login'])
        print('Tipo:', user['tipo'])
        senha_teste = '@21314100'
        if check_password_hash(user['senha'], senha_teste):
            print('Senha: CORRETA')
        else:
            print('Senha: INCORRETA')
"
```

## 🔄 Se Ainda Não Funcionar:

### 1. **Recriar Usuário Admin**
```bash
python -c "
from app import init_data
import os
# Remover arquivo de usuários
if os.path.exists('data/users.json'):
    os.remove('data/users.json')
# Recriar
init_data()
print('Usuario admin recriado!')
"
```

### 2. **Verificar Arquivo de Usuários**
O arquivo `data/users.json` deve conter:
```json
{
  "1": {
    "id": 1,
    "nome_completo": "Rafael Pinho",
    "login": "RafaelPinho",
    "senha": "hash_gerado_aqui",
    "tipo": "admin",
    "matricula": "ADMIN001",
    "tempo_exibicao": "2027-03-03",
    "data_cadastro": "2026-03-03 22:04:37",
    "ativo": true,
    "campos_adicionais": {}
  }
}
```

### 3. **Iniciar Servidor Limpo**
```bash
# Fechar qualquer servidor anterior
# Iniciar novo
python start.py
```

## 📞 Checklist Final:

- [ ] Login: RafaelPinho (exatamente assim)
- [ ] Senha: @21314100 (exatamente assim)  
- [ ] Sem espaços antes/depois
- [ ] Letras maiúsculas/minúsculas corretas
- [ ] Servidor rodando na porta 3000
- [ ] Acessando: http://localhost:3000

## 🎯 Se Tudo Certo:

Após login correto, você verá:
- Saudação personalizada
- Dashboard administrativo
- Menu superior com opções

---

**Se ainda tiver problemas, execute o teste:**
```bash
python test_login.py
```

O teste mostrará exatamente onde está o erro.
