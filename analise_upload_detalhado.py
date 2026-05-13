import pandas as pd
import json
from werkzeug.security import generate_password_hash

def analisar_upload_detalhado():
    print("=== ANÁLISE DETALHADA DO UPLOAD ===")
    
    # Carregar arquivo Excel
    df = pd.read_excel('08 - MALA DIRETA.xlsx')
    print(f"Arquivo Excel: {len(df)} linhas")
    
    # Carregar usuários atuais
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # Analisar cada linha do Excel
    for idx, row in df.iterrows():
        print(f"\n--- LINHA {idx+1} ---")
        login_excel = str(row['login']).strip()
        senha_excel = str(row['senha']).strip()
        matricula_excel = str(row['matricula']).strip()
        
        print(f"Login Excel: {login_excel}")
        print(f"Senha Excel: {senha_excel}")
        print(f"Matrícula Excel: {matricula_excel}")
        
        # Verificar se usuário existe no sistema
        usuario_sistema = None
        for uid, user in users.items():
            if user.get('login') == login_excel:
                usuario_sistema = user
                break
        
        if usuario_sistema:
            print(f"Usuário encontrado no sistema: {usuario_sistema.get('nome_completo', 'N/A')}")
            
            # Gerar hash da senha do Excel
            hash_esperado = generate_password_hash(senha_excel)
            hash_atual = usuario_sistema.get('senha', '')
            
            print(f"Hash atual: {hash_atual[:50]}...")
            print(f"Hash esperado: {hash_esperado[:50]}...")
            
            # Verificar se os hashes são iguais
            if hash_atual == hash_esperado:
                print("✅ SENHA JÁ ESTÁ ATUALIZADA")
            else:
                print("❌ SENHA NÃO FOI ATUALIZADA NO UPLOAD")
                print("   -> Upload não funcionou para este usuário")
        else:
            print("❌ USUÁRIO NÃO ENCONTRADO NO SISTEMA")

if __name__ == "__main__":
    analisar_upload_detalhado()
