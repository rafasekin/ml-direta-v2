#!/usr/bin/env python3
"""
Envia o conteúdo atual de data/*.json para o Supabase (tabelas ml_*).
Configure no ambiente:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY

Uso (na pasta Ml direta v9):
  python scripts/migrate_json_to_supabase.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def load_json(name: str) -> dict | list:
    p = DATA / name
    if not p.exists():
        print(f"[AVISO] {p} não encontrado — usando objeto vazio.")
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ambiente ou no arquivo .env na pasta Ml direta v9.")
        sys.exit(1)

    from supabase import create_client

    c = create_client(url, key)

    docs = [
        ("categories", "categories.json"),
        ("fields", "fields.json"),
        ("questions", "questions.json"),
        ("greetings", "greetings.json"),
    ]
    for doc_key, fname in docs:
        data = load_json(fname)
        body = json.dumps(data, ensure_ascii=False, default=str)
        c.table("ml_json_docs").upsert({"doc_key": doc_key, "body": body}, on_conflict="doc_key").execute()
        print(f"[OK] ml_json_docs / {doc_key}")

    users = load_json("users.json")
    if not isinstance(users, dict):
        print("[ERRO] users.json deve ser um objeto {id: usuario, ...}")
        sys.exit(1)
    rows = []
    for uid, u in users.items():
        rows.append(
            {
                "id": str(uid),
                "login": u["login"],
                "senha": u["senha"],
                "nome_completo": u.get("nome_completo"),
                "tipo": u["tipo"],
                "matricula": u.get("matricula"),
                "tempo_exibicao": u.get("tempo_exibicao"),
                "created_at": u.get("created_at"),
                "data_cadastro": u.get("data_cadastro"),
                "ativo": u.get("ativo", True),
                "campos_adicionais": u.get("campos_adicionais") or {},
            }
        )
    chunk = 150
    for i in range(0, len(rows), chunk):
        c.table("ml_users").upsert(rows[i : i + chunk], on_conflict="id").execute()
    print(f"[OK] ml_users — {len(rows)} linhas")

    answers = load_json("answers.json")
    if not isinstance(answers, dict):
        print("[ERRO] answers.json deve ser um objeto {id: resposta, ...}")
        sys.exit(1)
    arows = [{"answer_id": str(aid), "body": body} for aid, body in answers.items()]
    for i in range(0, len(arows), 200):
        c.table("ml_answers").upsert(arows[i : i + 200], on_conflict="answer_id").execute()
    print(f"[OK] ml_answers — {len(arows)} linhas")
    print("Migração concluída.")


if __name__ == "__main__":
    main()
