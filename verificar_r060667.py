import json
from werkzeug.security import check_password_hash

def verificar_usuario_r060667():
    # Carregar usuários atuais
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    # Buscar usuário r060667
    usuario_encontrado = None
    for uid, user in users.items():
        if user.get('login') == 'r060667':
            usuario_encontrado = user
            print(f'=== USUÁRIO r060667 ENCONTRADO ===')
            print(f'ID: {uid}')
            print(f'Nome: {user.get("nome_completo", "N/A")}')
            print(f'Login: {user.get("login", "N/A")}')
            print(f'Matrícula: {user.get("matricula", "N/A")}')
            print(f'Senha (hash): {user.get("senha", "N/A")}')
            print(f'Tipo: {user.get("tipo", "N/A")}')
            break
    
    if not usuario_encontrado:
        print('USUÁRIO r060667 NÃO ENCONTRADO!')
        return
    
    # Testar a senha
    senha_test = 'r@67839'
    hash_armazenado = usuario_encontrado.get('senha', '')
    
    print(f'\n=== TESTE DE SENHA ===')
    print(f'Senha testada: {senha_test}')
    print(f'Hash armazenado: {hash_armazenado[:50]}...')
    
    try:
        resultado = check_password_hash(hash_armazenado, senha_test)
        print(f'Verificação do hash: {resultado}')
        
        if resultado:
            print('✅ SENHA CORRETA - Login deveria funcionar!')
        else:
            print('❌ SENHA INCORRETA - Hash não corresponde à senha!')
            
            # Tentar outras senhas possíveis
            outras_senhas = ['r@67857', 'r@67879', 'temp123', 'r060667']
            print(f'\n=== TESTANDO OUTRAS SENHAS POSSÍVEIS ===')
            for senha in outras_senhas:
                try:
                    resultado = check_password_hash(hash_armazenado, senha)
                    print(f'Senha "{senha}": {resultado}')
                    if resultado:
                        print(f'🔍 SENHA CORRETA ENCONTRADA: {senha}')
                except:
                    print(f'Senha "{senha}": Erro na verificação')
                    
    except Exception as e:
        print(f'❌ ERRO NA VERIFICAÇÃO: {e}')

if __name__ == "__main__":
    verificar_usuario_r060667()
