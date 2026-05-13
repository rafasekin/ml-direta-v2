import json

def verificar_login_r060667():
    # Carregar usuários atuais
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    # Buscar usuário r060667
    for uid, user in users.items():
        login_armazenado = user.get('login', '')
        if 'r060667' in login_armazenado.lower():
            print(f'=== USUÁRIO ENCONTRADO ===')
            print(f'ID: {uid}')
            print(f'Login armazenado: "{login_armazenado}"')
            print(f'Login com repr: {repr(login_armazenado)}')
            print(f'Comprimento: {len(login_armazenado)}')
            print(f'Login tem espaços: {login_armazenado != login_armazenado.strip()}')
            print(f'Login em maiúsculas: {login_armazenado.upper()}')
            print(f'Login em minúsculas: {login_armazenado.lower()}')
            
            # Comparar com diferentes variações
            testes = ['r060667', 'r060667 ', ' r060667', 'R060667', 'r060667\n']
            for teste in testes:
                print(f"'{teste}' == '{login_armazenado}' ? {teste == login_armazenado}")
            break

if __name__ == "__main__":
    verificar_login_r060667()
