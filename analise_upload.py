import pandas as pd
import sys

def analisar_arquivo_upload():
    try:
        df = pd.read_excel('08 - MALA DIRETA.xlsx')
        print(f'Arquivo carregado: {len(df)} linhas')
        print(f'Colunas: {list(df.columns)}')
        print()
        
        # Verificar matrículas específicas
        matriculas_interesse = ['60641', '60690']
        
        for matricula in matriculas_interesse:
            print(f'=== Buscando matrícula: {matricula} ===')
            rows = df[df['matricula'].astype(str).str.contains(matricula, na=False)]
            if not rows.empty:
                for idx, row in rows.iterrows():
                    print(f'Linha {idx+1}:')
                    print(f'  Nome: {row.get("nome_completo", "N/A")}')
                    print(f'  Login: {row.get("login", "N/A")}')
                    print(f'  Senha: {row.get("senha", "N/A")}')
                    print(f'  Matrícula: {row.get("matricula", "N/A")}')
                    print(f'  Tempo exibição: {row.get("tempo_exibicao", "N/A")}')
                    print(f'  Senha é NaN: {pd.isna(row.get("senha", ""))}')
                    print(f'  Senha é vazia: {str(row.get("senha", "")).strip() == ""}')
            else:
                print('Matrícula não encontrada')
            print()
        
        # Verificar valores nulos na coluna senha
        print('=== Análise da coluna senha ===')
        senhas_vazias = df['senha'].isna().sum()
        senhas_vazias_str = (df['senha'].astype(str).str.strip() == '').sum()
        print(f'Senhas NaN: {senhas_vazias}')
        print(f'Senhas vazias (""): {senhas_vazias_str}')
        print(f'Senhas válidas: {len(df) - senhas_vazias - senhas_vazias_str}')
        
        # Mostrar primeiras linhas com problemas
        print('\n=== Primeiras 10 linhas ===')
        for idx, row in df.head(10).iterrows():
            print(f'Linha {idx+1}: Login={row.get("login", "N/A")}, Senha={row.get("senha", "N/A")}, Matrícula={row.get("matricula", "N/A")}')
        
    except Exception as e:
        print(f'Erro: {e}')
        sys.exit(1)

if __name__ == "__main__":
    analisar_arquivo_upload()
