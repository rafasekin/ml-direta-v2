#!/usr/bin/env python3
"""
Script de teste para verificar login
"""

from app import app, init_data, load_data, check_password_hash
import sys

def test_login():
    """Testa o login do admin"""
    print("=== TESTE DE LOGIN ===")
    
    # Inicializar dados
    init_data()
    
    # Carregar usuários
    users = load_data('data/users.json')
    
    # Testar credenciais
    login = 'RafaelPinho'
    senha = '@21314100'
    
    print(f"Testando login: {login} / {senha}")
    
    # Simular lógica de login
    user = None
    user_id = None
    
    for uid, udata in users.items():
        if udata['login'] == login and check_password_hash(udata['senha'], senha):
            user = udata
            user_id = uid
            break
    
    if user:
        print("[OK] LOGIN SUCESSO!")
        print(f"   Nome: {user['nome_completo']}")
        print(f"   Tipo: {user['tipo']}")
        print(f"   Matricula: {user['matricula']}")
        return True
    else:
        print("[ERRO] LOGIN FALHOU!")
        return False

def test_server():
    """Testa se o servidor Flask inicia"""
    print("\n=== TESTE DO SERVIDOR ===")
    
    try:
        with app.test_client() as client:
            # Testar página de login
            response = client.get('/login')
            if response.status_code == 200:
                print("[OK] Pagina de login carregou!")
                
                # Testar POST de login
                response = client.post('/login', data={
                    'login': 'RafaelPinho',
                    'senha': '@21314100'
                }, follow_redirects=True)
                
                if response.status_code == 200:
                    print("[OK] POST de login funcionou!")
                    return True
                else:
                    print(f"[ERRO] POST de login falhou: {response.status_code}")
                    return False
            else:
                print(f"[ERRO] Pagina de login falhou: {response.status_code}")
                return False
    except Exception as e:
        print(f"[ERRO] Erro no servidor: {e}")
        return False

if __name__ == "__main__":
    print("ML Direta - Teste de Login")
    print("=" * 40)
    
    # Testar login
    login_ok = test_login()
    
    # Testar servidor
    server_ok = test_server()
    
    print("\n" + "=" * 40)
    if login_ok and server_ok:
        print("[OK] TODOS OS TESTES PASSARAM!")
        print("   Sistema pronto para uso.")
    else:
        print("[ERRO] ALGUNS TESTES FALHARAM!")
        print("   Verifique os erros acima.")
    
    print("\nPara iniciar o sistema:")
    print("   python start.py")
    print("   Acesse: http://localhost:3000")
    print("   Login: RafaelPinho")
    print("   Senha: @21314100")
