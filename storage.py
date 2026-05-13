"""
Persistência ML Direta: arquivos JSON locais (padrão) ou Supabase (quando
SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY estão definidos).
"""
from __future__ import annotations

import copy
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

# Diretório e arquivos (mesmos nomes que o app original)
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
FIELDS_FILE = os.path.join(DATA_DIR, "fields.json")
GREETINGS_FILE = os.path.join(DATA_DIR, "greetings.json")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
ANSWERS_FILE = os.path.join(DATA_DIR, "answers.json")

_data_cache: dict = {}
_cache_timestamps: dict = {}
_supa_revision: float = time.time()

_supabase_client = None


def use_supabase() -> bool:
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))


def _client():
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client

        _supabase_client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
    return _supabase_client


def _bump_revision():
    global _supa_revision
    _supa_revision = time.time()


def data_cache_revision() -> float:
    """Substitui max(getmtime) para invalidar cache de categorias no dashboard."""
    if use_supabase():
        return _supa_revision
    paths = (USERS_FILE, CATEGORIES_FILE, FIELDS_FILE)
    mt = 0.0
    for p in paths:
        try:
            mt = max(mt, os.path.getmtime(p))
        except OSError:
            pass
    return mt


def clear_cache(filename=None):
    global _data_cache, _cache_timestamps
    if filename:
        _data_cache.pop(filename, None)
        _cache_timestamps.pop(filename, None)
    else:
        _data_cache.clear()
        _cache_timestamps.clear()


def load_data(filename, use_cache=True):
    if use_supabase():
        return _load_supabase(filename, use_cache=use_cache)
    if not os.path.exists(filename):
        return {}
    if use_cache and filename in _data_cache:
        current_mtime = os.path.getmtime(filename)
        cached_mtime = _cache_timestamps.get(filename, 0)
        if current_mtime <= cached_mtime:
            return _data_cache[filename]
    start_time = time.time()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if use_cache:
            _data_cache[filename] = data
            _cache_timestamps[filename] = os.path.getmtime(filename)
        print(f"Carregado {filename} em {time.time() - start_time:.3f}s")
        return data
    except json.JSONDecodeError as e:
        print(f"Erro ao carregar JSON {filename}: {e}")
        return {}
    except Exception as e:
        print(f"Erro geral ao carregar {filename}: {e}")
        return {}


def save_data(filename, data):
    if use_supabase():
        _save_supabase(filename, data)
        _bump_revision()
        clear_cache(filename)
        print(f"Salvo Supabase {filename}")
        return
    start_time = time.time()
    try:
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except (OSError, PermissionError):
        # Sistema de arquivos somente leitura (Vercel); ignorar
        print(f"Aviso: não foi possível salvar {filename} (sistema somente leitura)")
        return
    clear_cache(filename)
    print(f"Salvo {filename} em {time.time() - start_time:.3f}s")


# --- Supabase: mapeamento arquivo -> recurso ---

_DOC_FILES = {CATEGORIES_FILE, FIELDS_FILE, GREETINGS_FILE, QUESTIONS_FILE}


def _doc_key_for_file(filename: str) -> str:
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]


def _load_supabase(filename: str, use_cache: bool):
    if use_cache and filename in _data_cache:
        return copy.deepcopy(_data_cache[filename])
    c = _client()
    if filename in _DOC_FILES:
        key = _doc_key_for_file(filename)
        r = c.table("ml_json_docs").select("body").eq("doc_key", key).limit(1).execute()
        rows = r.data or []
        if not rows:
            data = {}
        else:
            raw = rows[0].get("body") or "{}"
            data = json.loads(raw) if isinstance(raw, str) else raw
    elif filename == USERS_FILE:
        r = c.table("ml_users").select("*").execute()
        data = {}
        for row in r.data or []:
            uid = str(row["id"])
            data[uid] = _row_to_user(row)
    elif filename == ANSWERS_FILE:
        r = c.table("ml_answers").select("answer_id, body").execute()
        data = {}
        for row in r.data or []:
            aid = str(row["answer_id"])
            body = row.get("body") or {}
            if isinstance(body, str):
                body = json.loads(body)
            data[aid] = body
    else:
        data = {}
    if use_cache:
        _data_cache[filename] = copy.deepcopy(data)
        _cache_timestamps[filename] = time.time()
    return data


def _save_supabase(filename: str, data):
    c = _client()
    if filename in _DOC_FILES:
        key = _doc_key_for_file(filename)
        payload = json.dumps(data, ensure_ascii=False, default=str)
        c.table("ml_json_docs").upsert(
            {"doc_key": key, "body": payload},
            on_conflict="doc_key",
        ).execute()
    elif filename == USERS_FILE:
        _sync_users_table(c, data)
    elif filename == ANSWERS_FILE:
        _sync_answers_table(c, data)
    else:
        raise ValueError(f"Arquivo não suportado no Supabase: {filename}")


def _row_to_user(row: dict) -> dict:
    uid = str(row["id"])
    try:
        numeric_id = int(uid)
    except ValueError:
        numeric_id = uid
    u = {
        "id": numeric_id,
        "login": row["login"],
        "senha": row["senha"],
        "nome_completo": row.get("nome_completo") or "",
        "tipo": row["tipo"],
        "matricula": row.get("matricula") or "",
        "tempo_exibicao": row.get("tempo_exibicao") or "",
        "campos_adicionais": row.get("campos_adicionais") or {},
    }
    if row.get("created_at") is not None:
        u["created_at"] = row["created_at"]
    if row.get("data_cadastro") is not None:
        u["data_cadastro"] = row["data_cadastro"]
    if row.get("ativo") is not None:
        u["ativo"] = row["ativo"]
    return u


def _user_to_row(uid: str, u: dict) -> dict:
    return {
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


def _sync_users_table(c, users: dict):
    r = c.table("ml_users").select("id").execute()
    existing = {str(x["id"]) for x in (r.data or [])}
    incoming = set(str(k) for k in users.keys())
    for rid in existing - incoming:
        c.table("ml_users").delete().eq("id", rid).execute()
    rows = [_user_to_row(str(uid), u) for uid, u in users.items()]
    chunk = 150
    for i in range(0, len(rows), chunk):
        c.table("ml_users").upsert(rows[i : i + chunk], on_conflict="id").execute()


def _sync_answers_table(c, answers: dict):
    r = c.table("ml_answers").select("answer_id").execute()
    existing = {str(x["answer_id"]) for x in (r.data or [])}
    incoming = set(str(k) for k in answers.keys())
    for rid in existing - incoming:
        c.table("ml_answers").delete().eq("answer_id", rid).execute()
    rows = [{"answer_id": str(aid), "body": body} for aid, body in answers.items()]
    chunk = 200
    for i in range(0, len(rows), chunk):
        c.table("ml_answers").upsert(rows[i : i + chunk], on_conflict="answer_id").execute()


def init_data():
    if use_supabase():
        _init_supabase()
        return

    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except (OSError, PermissionError):
            # Sistema de arquivos somente leitura (Vercel)
            pass

    users = load_data(USERS_FILE)
    admin_exists = any(
        u.get("login") == "RafaelPinho" and u.get("tipo") == "admin" for u in users.values()
    )
    if not admin_exists:
        admin_user = {
            "id": 1,
            "nome_completo": "Rafael Pinho",
            "login": "RafaelPinho",
            "senha": generate_password_hash("@21314100"),
            "tipo": "admin",
            "matricula": "ADMIN001",
            "tempo_exibicao": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "campos_adicionais": {},
        }
        users["1"] = admin_user
        save_data(USERS_FILE, users)
        print("Usuário admin padrão criado: RafaelPinho / @21314100")

    test_login = "testuser"
    test_senha = "test123"
    test_exists = False
    for uid, u in users.items():
        if u.get("login") == test_login:
            test_exists = True
            users[uid]["senha"] = generate_password_hash(test_senha)
            save_data(USERS_FILE, users)
            print(f"Senha do usuário de teste atualizada: {test_login} / {test_senha}")
            break
    if not test_exists:
        new_id = str(max([int(uid) for uid in users.keys()] + [0]) + 1)
        users[new_id] = {
            "id": int(new_id),
            "nome_completo": "Usuário Teste",
            "login": test_login,
            "senha": generate_password_hash(test_senha),
            "tipo": "usuario",
            "matricula": "TEST001",
            "tempo_exibicao": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "campos_adicionais": {},
        }
        save_data(USERS_FILE, users)
        print(f"Usuário de teste criado: {test_login} / {test_senha}")

    if not load_data(CATEGORIES_FILE):
        save_data(CATEGORIES_FILE, {})
    if not load_data(FIELDS_FILE):
        save_data(FIELDS_FILE, {})
    if not load_data(GREETINGS_FILE):
        save_data(
            GREETINGS_FILE,
            {"texto": "Bem-vindo(a), {nome}!", "imagem": "", "video": ""},
        )
    if not load_data(QUESTIONS_FILE):
        save_data(QUESTIONS_FILE, {})
    if not load_data(ANSWERS_FILE):
        save_data(ANSWERS_FILE, {})


def _init_supabase():
    c = _client()
    defaults = [
        ("categories", "{}"),
        ("fields", "{}"),
        ("questions", "{}"),
        (
            "greetings",
            json.dumps({"texto": "Bem-vindo(a), {nome}!", "imagem": "", "video": ""}, ensure_ascii=False),
        ),
    ]
    for key, body in defaults:
        r = c.table("ml_json_docs").select("doc_key").eq("doc_key", key).limit(1).execute()
        if not (r.data or []):
            c.table("ml_json_docs").insert({"doc_key": key, "body": body}).execute()

    r = c.table("ml_users").select("id").eq("login", "RafaelPinho").limit(1).execute()
    if not (r.data or []):
        admin_user = {
            "id": "1",
            "nome_completo": "Rafael Pinho",
            "login": "RafaelPinho",
            "senha": generate_password_hash("@21314100"),
            "tipo": "admin",
            "matricula": "ADMIN001",
            "tempo_exibicao": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ativo": True,
            "campos_adicionais": {},
        }
        c.table("ml_users").insert(_user_to_row("1", admin_user)).execute()
        print("Supabase: usuário admin padrão criado: RafaelPinho / @21314100")

    seed_test = os.environ.get("ML_SEED_TEST_USER", "").lower() in ("1", "true", "yes")
    if seed_test:
        users = load_data(USERS_FILE, use_cache=False)
        test_login = "testuser"
        test_senha = "test123"
        found = None
        for uid, u in users.items():
            if u.get("login") == test_login:
                found = uid
                break
        if found:
            users[found]["senha"] = generate_password_hash(test_senha)
            save_data(USERS_FILE, users)
        else:
            new_id = str(max([int(uid) for uid in users.keys()] + [0]) + 1)
            users[new_id] = {
                "id": int(new_id),
                "nome_completo": "Usuário Teste",
                "login": test_login,
                "senha": generate_password_hash(test_senha),
                "tipo": "usuario",
                "matricula": "TEST001",
                "tempo_exibicao": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "campos_adicionais": {},
            }
            save_data(USERS_FILE, users)
