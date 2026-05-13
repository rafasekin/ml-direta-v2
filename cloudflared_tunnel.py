#!/usr/bin/env python3
"""
Script para expor a aplicação ML Direta usando Cloudflare Tunnel
Gera URL pública aleatória para acesso externo
"""

import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime

def check_cloudflared():
    """Verifica se o cloudflared está instalado"""
    try:
        result = subprocess.run(['cloudflared', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Cloudflared encontrado: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Cloudflared não encontrado")
    return False

def install_cloudflared():
    """Instala o cloudflared"""
    print("📥 Instalando Cloudflared...")
    
    try:
        # Download do cloudflared para Windows
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        response = requests.get(url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open('cloudflared.exe', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ Cloudflared instalado com sucesso!")
            return True
        else:
            print(f"❌ Erro no download: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao instalar cloudflared: {e}")
        return False

def start_tunnel():
    """Inicia o tunnel do Cloudflare"""
    print("\n🚀 Iniciando Cloudflare Tunnel...")
    print("📍 Aguarde, gerando URL pública...")
    
    # Comando para iniciar tunnel temporário
    cmd = [
        'cloudflared', 'tunnel', '--url', 
        'http://localhost:3000',
        '--logfile', 'cloudflared.log'
    ]
    
    try:
        # Inicia o processo
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("⏳ Aguardando URL pública...")
        
        # Monitora a saída para encontrar a URL
        url_found = False
        start_time = time.time()
        timeout = 60  # 60 segundos timeout
        
        while not url_found and (time.time() - start_time) < timeout:
            if process.poll() is not None:
                print("❌ Processo do cloudflared finalizou inesperadamente")
                return None, None
            
            # Lê a saída linha por linha
            line = process.stdout.readline()
            if line:
                print(f"📋 {line.strip()}")
                
                # Procura pela URL pública
                if "https://" in line and "trycloudflare.com" in line:
                    # Extrai a URL
                    parts = line.split()
                    for part in parts:
                        if part.startswith("https://") and "trycloudflare.com" in part:
                            url = part.rstrip('.')
                            print(f"\n🎉 URL PÚBLICA GERADA!")
                            print(f"🔗 {url}")
                            print(f"⏰ Gerado em: {datetime.now().strftime('%H:%M:%S')}")
                            print(f"📱 Compartilhe esta URL para acesso externo!")
                            print(f"\n⚠️  Mantenha esta janela aberta para manter o tunnel ativo")
                            print(f"⚠️  Pressione Ctrl+C para parar o tunnel")
                            print(f"\n" + "="*60)
                            return url, process
        
        print("❌ Timeout: não foi possível gerar a URL em 60 segundos")
        process.terminate()
        return None, None
        
    except KeyboardInterrupt:
        print("\n⏹️  Tunnel interrompido pelo usuário")
        if 'process' in locals():
            process.terminate()
        return None, None
    except Exception as e:
        print(f"❌ Erro ao iniciar tunnel: {e}")
        return None, None

def show_instructions():
    """Mostra instruções de uso"""
    print("\n" + "="*60)
    print("🌐 CLOUDFLARE TUNNEL - ML DIRETA")
    print("="*60)
    print("\n📝 INSTRUÇÕES:")
    print("1. Certifique-se que o sistema ML Direta está rodando na porta 3000")
    print("2. Execute este script para gerar URL pública")
    print("3. Compartilhe a URL gerada para acesso externo")
    print("4. Mantenha esta janela aberta para manter o tunnel ativo")
    print("\n🔧 REQUISITOS:")
    print("- Conexão com internet")
    print("- Sistema ML Direta rodando em http://localhost:3000")
    print("\n⚠️  IMPORTANTE:")
    print("- A URL é temporária e muda a cada execução")
    print("- Acesso público enquanto o tunnel estiver ativo")
    print("- Feche esta janela para desativar o tunnel")
    print("="*60)

def main():
    """Função principal"""
    print("🌐 CLOUDFLARE TUNNEL - ML DIRETA")
    print("="*50)
    
    # Mostra instruções
    show_instructions()
    
    # Verifica se o usuário quer continuar
    try:
        response = input("\n🚀 Deseja iniciar o tunnel agora? (S/N): ").strip().upper()
        if response != 'S':
            print("❌ Operação cancelada")
            return
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada")
        return
    
    # Verifica/instala cloudflared
    if not check_cloudflared():
        print("\n📥 Cloudflared não encontrado. Deseja instalar? (S/N): ", end="")
        try:
            response = input().strip().upper()
            if response != 'S':
                print("❌ Operação cancelada")
                return
        except KeyboardInterrupt:
            print("\n❌ Operação cancelada")
            return
        
        if not install_cloudflared():
            print("❌ Falha na instalação do cloudflared")
            return
    
    # Inicia o tunnel
    url, process = start_tunnel()
    
    if url and process:
        print(f"\n🎯 TUNNEL ATIVO!")
        print(f"🔗 URL Pública: {url}")
        print(f"🔗 URL Local: http://localhost:3000")
        print(f"\n📱 Use a URL pública para acesso externo")
        print(f"💻 Use a URL local para acesso na mesma rede")
        
        try:
            # Mantém o script rodando
            process.wait()
        except KeyboardInterrupt:
            print(f"\n⏹️  Encerrando tunnel...")
            process.terminate()
            print(f"✅ Tunnel encerrado")
            print(f"🔗 URL {url} não está mais ativa")

if __name__ == "__main__":
    main()
