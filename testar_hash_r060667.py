import json
from werkzeug.security import check_password_hash, generate_password_hash

def testar_hash_r060667():
    # Carregar usuários atuais
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    # Buscar usuário r060667
    usuario_encontrado = None
    for uid, user in users.items():
        if user.get('login') == 'r060667':
            usuario_encontrado = user
            break
    
    if not usuario_encontrado:
        print('USUARIO r060667 NAO ENCONTRADO!')
        return
    
    # Obter hash armazenado
    hash_armazenado = usuario_encontrado.get('senha', '')
    senha_correta = 'r@67839'
    
    print('=== TESTE DE HASH r060667 ===')
    print(f'Hash armazenado: {hash_armazenado}')
    print(f'Senha esperada: {senha_correta}')
    
    # Testar verificação
    try:
        resultado = check_password_hash(hash_armazenado, senha_correta)
        print(f'Verificacao: {resultado}')
        
        if resultado:
            print('HASH ESTA CORRETO!')
        else:
            print('HASH ESTA INCORRETO!')
            
            # Gerar novo hash para comparação
            novo_hash = generate_password_hash(senha_correta)
            print(f'Novo hash gerado: {novo_hash}')
            print(f'Hashes sao iguais: {hash_armazenado == novo_hash}')
            
    except Exception as e:
        print(f'ERRO NA VERIFICACAO: {e}')

if __name__ == "__main__":
    testar_hash_r060667()
