#!/usr/bin/env python3
"""
Script de inicialização do ML Direta
Sistema de Gestão Local
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Verifica se a versao do Python e compativel"""
    if sys.version_info < (3, 7):
        print("[X] Este sistema requer Python 3.7 ou superior")
        print(f"   Versao atual: {sys.version}")
        return False
    print(f"[OK] Python {sys.version.split()[0]} detectado")
    return True

def install_dependencies():
    """Instala as dependencias necessarias"""
    print("[INFO] Verificando dependencias...")
    
    try:
        import flask
        import pandas
        import werkzeug
        print("[OK] Dependencias ja instaladas")
        return True
    except ImportError:
        print("[INFO] Instalando dependencias...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("[OK] Dependencias instaladas com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("[ERRO] Erro ao instalar dependencias")
            print("   Tente instalar manualmente: pip install -r requirements.txt")
            return False

def create_data_directory():
    """Cria o diretorio de dados se nao existir"""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print("[OK] Diretorio de dados criado")
    else:
        print("[INFO] Diretorio de dados ja existe")

def start_server():
    """Inicia o servidor Flask"""
    print("\n[INFO] Iniciando servidor ML Direta...")
    print("[INFO] Servidor sera executado em: http://localhost:3000")
    print("[INFO] Admin padrao: RafaelPinho / @21314100")
    print("\n[INFO] Aguarde...")
    
    # Aguardar um pouco antes de abrir o navegador
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:3000")
    
    # Abrir navegador em thread separada
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Importar e executar o app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=3000)
    except KeyboardInterrupt:
        print("\n[INFO] Servidor encerrado pelo usuario")
    except Exception as e:
        print(f"[ERRO] Erro ao iniciar servidor: {e}")
        print("   Verifique se a porta 3000 esta disponivel")

def show_help():
    """Mostra informacoes de ajuda"""
    print("ML Direta - Sistema de Gestao Local")
    print("")
    print("COMANDOS:")
    print("    python start.py          - Inicia o sistema")
    print("    python start.py --help   - Mostra esta ajuda")
    print("")
    print("ACESSO PADRAO:")
    print("    Login: RafaelPinho")
    print("    Senha: @21314100")
    print("")
    print("ENDERECO:")
    print("    http://localhost:3000")
    print("")
    print("REQUISITOS:")
    print("    - Python 3.7 ou superior")
    print("    - Porta 3000 disponivel")
    print("    - Windows/Linux/MacOS")

def main():
    """Função principal"""
    print("ML Direta - Sistema de Gestao Local")
    print("=" * 50)
    
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
        return
    
    # Verificar Python
    if not check_python_version():
        input("\nPressione Enter para sair...")
        return
    
    # Instalar dependências
    if not install_dependencies():
        input("\nPressione Enter para sair...")
        return
    
    # Criar diretório de dados
    create_data_directory()
    
    # Iniciar servidor
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[INFO] Encerrando...")
    except Exception as e:
        print(f"\n[ERRO] Erro: {e}")
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
