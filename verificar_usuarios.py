import json

def verificar_usuarios():
    # Carregar usuários atuais
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    # Verificar usuários específicos
    matriculas_interesse = ['60641', '60690', '60680', '60667']

    for matricula in matriculas_interesse:
        print(f'=== Buscando matrícula: {matricula} ===')
        encontrado = False
        for uid, user in users.items():
            if user.get('matricula') == matricula:
                print(f'ID: {uid}')
                print(f'Nome: {user.get("nome_completo", "N/A")}')
                print(f'Login: {user.get("login", "N/A")}')
                print(f'Senha (hash): {user.get("senha", "N/A")[:50]}...')
                print(f'Tipo: {user.get("tipo", "N/A")}')
                encontrado = True
                break
        
        if not encontrado:
            print('Matrícula não encontrada no sistema')
        print()

if __name__ == "__main__":
    verificar_usuarios()
