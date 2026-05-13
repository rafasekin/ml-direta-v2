import json
from werkzeug.security import generate_password_hash

def corrigir_senha_r060667():
    # Carregar usuários atuais
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    # Buscar e atualizar usuário r060667
    for uid, user in users.items():
        if user.get('login') == 'r060667':
            print(f'=== CORRIGINDO SENHA DO USUÁRIO r060667 ===')
            print(f'ID: {uid}')
            print(f'Nome: {user.get("nome_completo", "N/A")}')
            print(f'Hash anterior: {user.get("senha", "N/A")[:50]}...')
            
            # Gerar novo hash
            nova_senha = 'r@67839'
            novo_hash = generate_password_hash(nova_senha)
            
            # Atualizar senha
            user['senha'] = novo_hash
            
            print(f'Nova senha: {nova_senha}')
            print(f'Novo hash: {novo_hash[:50]}...')
            print('Senha atualizada com sucesso!')
            break
    else:
        print('Usuário r060667 não encontrado!')
        return

    # Salvar dados atualizados
    with open('data/users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2, default=str)
    
    print('Dados salvos com sucesso!')

if __name__ == "__main__":
    corrigir_senha_r060667()
