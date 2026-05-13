# ML Direta - Sistema de Gestão Local

Sistema web completo para gestão de usuários com cadastro inteligente, cronograma de fases e sistema de dúvidas, executado localmente via terminal.

## 🎯 Características Principais

### 👥 Tipos de Usuários
- **Administrador**: Acesso total ao sistema
- **Usuário (Colaborador)**: Acesso apenas às próprias informações

### 📋 Cadastro Inteligente
- **Campos obrigatórios fixos**: Nome, Login, Senha, Matrícula, Tempo de exibição
- **Campos configuráveis**: Crie categorias e campos personalizados
- **Validação automática**: Detecta campos vazios durante o cadastro

### 📊 Upload em Massa
- **Excel (.xlsx)**: Importe múltiplos usuários de uma vez
- **Modelo dinâmico**: Baixe template com campos atuais do sistema
- **Inteligência por matrícula**: Atualiza dados existentes automaticamente

### 🗓️ Cronograma por Fases
- **Fases configuráveis**: Integração, IST, Treinamentos, etc.
- **Modalidades**: Presencial ou Online
- **Exibição inteligente**: Apenas fases com dados preenchidos

### 💬 Sistema de Dúvidas
- **Perguntas pré-definidas**: Configure categorias e perguntas
- **Histórico completo**: Mantém conversas entre usuários e admin
- **Contador de pendentes**: Acompanhe dúvidas não respondidas

### 👋 Saudações Personalizadas
- **Pop-up de boas-vindas**: Exibido a cada login
- **Conteúdo multimídia**: Texto, imagem e vídeo
- **Personalização**: Use {nome} para incluir nome do usuário

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.7 ou superior
- Porta 3000 disponível
- Windows/Linux/MacOS

### Inicialização

#### Opção 1: Menu Interativo (Recomendado)
Execute o arquivo `iniciar.bat` e escolha:
- **1** - Iniciar apenas sistema local (localhost:3000)
- **2** - Iniciar sistema + acesso externo (URL pública)
- **3** - Apenas acesso externo (sistema já rodando)
- **4** - Sair

#### Opção 2: Acesso Externo Direto
Execute `iniciar_externo.bat` para iniciar sistema + acesso externo automaticamente

#### Opção 3: Terminal Manual
```bash
python start.py
```

### Acesso Padrão
```
Login: RafaelPinho
Senha: @21314100
```

### URLs de Acesso
- **Local:** http://localhost:3000
- **Externo:** URL gerada automaticamente (ex: https://random-words-123.trycloudflare.com)

### 🌐 Acesso Externo com Cloudflare Tunnel

O sistema pode ser exposto para acesso externo através de URL pública temporária:

**Como usar:**
1. Execute `iniciar.bat` → opção 2
2. Ou execute `iniciar_externo.bat` diretamente
3. Aguarde a geração da URL pública
4. Compartilhe a URL para acesso externo

**Benefícios:**
- ✅ URL aleatória e segura
- ✅ Acesso de qualquer lugar
- ✅ Funciona em celular/tablet
- ✅ Perfeito para demonstrações
- ✅ Controle total (feche para desativar)

**Importante:**
- 🔓 URL é pública - compartilhe com cuidado
- ⏰ URL é temporária - muda a cada execução
- 🌐 Requer conexão com internet

## 📁 Estrutura do Projeto

```
ml-direta/
├── app.py                 # Aplicação Flask principal
├── start.py              # Script de inicialização
├── requirements.txt      # Dependências Python
├── README.md            # Este arquivo
├── data/                # Armazenamento local (JSON)
│   ├── users.json       # Usuários cadastrados
│   ├── categories.json  # Categorias de campos
│   ├── fields.json      # Campos configuráveis
│   ├── greetings.json   # Saudações
│   ├── schedule.json    # Cronograma
│   ├── questions.json   # Perguntas
│   └── answers.json     # Respostas
├── templates/           # Templates HTML
│   ├── base.html       # Template base
│   ├── login.html      # Página de login
│   ├── greeting.html   # Saudações
│   ├── admin/          # Templates admin
│   └── user/           # Templates usuário
└── static/             # Arquivos estáticos
    ├── css/style.css   # Estilos personalizados
    └── js/script.js    # Scripts JavaScript
```

## 🔧 Funcionalidades Detalhadas

### Sistema de Autenticação
- Login seguro com hash de senhas
- Sessões persistentes
- Controle de acesso por tipo de usuário
- Tempo de exibição configurável por usuário

### Campos Configuráveis
- **Tipos de campo**: Texto livre, Data, Link, Seleção
- **Categorias**: Organize campos em grupos lógicos
- **Obrigatoriedade**: Defina quais campos são obrigatórios
- **Integração automática**: Campos aparecem em cadastro e Excel

### Upload de Usuários
- **Validação de colunas**: Verifica campos obrigatórios
- **Detecção de vazios**: Alerta sobre campos em branco
- **Atualização inteligente**: Mantém matrícula, atualiza demais dados
- **Opção ignorar vazios**: Continue mesmo com campos incompletos

### Cronograma Inteligente
- **Ordenação automática**: Fases exibidas por data de início
- **Filtro de conteúdo**: Não exibe fases vazias
- **Informações completas**: Data, local, link, instrutor
- **Modalidades específicas**: Presencial (local) ou Online (link)

### Sistema de Dúvidas
- **Categorias organizadas**: Agrupe perguntas por assunto
- **Texto complementar**: Opcional por pergunta
- **Histórico completo**: Mantém todas as interações
- **Notificações**: Contador de dúvidas pendentes

## 🎨 Interface Responsiva

- **Design moderno**: Bootstrap 5 com customizações
- **Totalmente responsivo**: Funciona em desktop, tablet e mobile
- **Feedback visual**: Alerts, tooltips e animações
- **Acessibilidade**: Navegação por teclado e leitores de tela

## 💾 Armazenamento Local

- **Sem dependência de nuvem**: Tudo fica armazenado localmente
- **Formato JSON**: Fácil backup e migração
- **Dados persistentes**: Informações mantidas entre reinicializações
- **Segurança**: Senhas armazenadas com hash

## 🔒 Segurança

- **Hash de senhas**: Werkzeug security
- **Sessões seguras**: Flask session management
- **Validação de entrada**: Sanitização de dados
- **Controle de acesso**: Decoradores de permissão

## 🛠️ Manutenção

### Backup dos Dados
Para fazer backup, simplesmente copie a pasta `data/`:
```bash
# Copiar pasta de dados
cp -r data/ backup-data-$(date +%Y%m%d)/
```

### Limpeza de Logs
O sistema não gera logs automaticamente, mas pode limpar dados antigos manualmente:
- Remova usuários inativos via interface admin
- Limpe respostas antigas no sistema de dúvidas
- Atualize saudações periodicamente

### Atualização do Sistema
Para atualizar, mantenha a pasta `data/` e substitua os demais arquivos.

## 🚨 Solução de Problemas

### Porta Ocupada
Se a porta 3000 estiver em uso:
```bash
# Verificar processo na porta
netstat -ano | findstr :3000

# Matar processo (Windows)
taskkill /PID <PID> /F
```

### Dependências Faltando
Se ocorrer erro de importação:
```bash
# Instalar dependências manualmente
pip install -r requirements.txt
```

### Python Não Reconhecido
Se `python` não funcionar:
```bash
# Tente com python3
python3 start.py

# Ou adicione Python ao PATH do sistema
```

## 📞 Suporte

Este sistema foi desenvolvido para uso local e autônomo. 
Caso encontre problemas:

1. **Verifique os pré-requisitos** (Python 3.7+)
2. **Confirme a porta 3000 está livre**
3. **Reinstale as dependências**
4. **Reinicie o sistema**

## 📄 Licença

Este projeto é fornecido para uso interno e local. 
Mantenha esta estrutura de arquivos intacta para garantir o funcionamento adequado.

---

**ML Direta** - Sistema de Gestão Local  
Versão 1.0.0 | Desenvolvido para execução local
