from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from functools import wraps, lru_cache
import secrets
import time

from storage import (
    ANSWERS_FILE,
    CATEGORIES_FILE,
    DATA_DIR,
    FIELDS_FILE,
    GREETINGS_FILE,
    QUESTIONS_FILE,
    USERS_FILE,
    clear_cache,
    data_cache_revision,
    init_data,
    load_data,
    save_data,
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
if os.environ.get("VERCEL"):
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Filtro personalizado para formatar datas
@app.template_filter('format_date')
def format_date(date_string):
    if not date_string:
        return date_string
    
    try:
        # Lista de formatos para tentar
        date_formats = [
            '%Y-%m-%d %H:%M:%S',  # 2026-02-06 00:00:00
            '%Y-%m-%d %H:%M:%S.%f',  # 2026-02-06 00:00:00.000000
            '%Y-%m-%d',  # 2026-02-06
            '%d/%m/%Y',  # 06/02/2026
            '%d/%m/%Y %H:%M:%S',  # 06/02/2026 00:00:00
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                continue
        
        # Se nenhum formato funcionar, retorna o original
        return date_string
    except Exception:
        return date_string

# Filtro personalizado para formatar data e hora
@app.template_filter('format_datetime')
def format_datetime(date_string):
    if not date_string:
        return date_string
    
    try:
        # Lista de formatos para tentar
        date_formats = [
            '%Y-%m-%d %H:%M:%S',  # 2026-02-06 00:00:00
            '%Y-%m-%d %H:%M:%S.%f',  # 2026-02-06 00:00:00.000000
            '%Y-%m-%d',  # 2026-02-06
            '%d/%m/%Y',  # 06/02/2026
            '%d/%m/%Y %H:%M:%S',  # 06/02/2026 00:00:00
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime('%d/%m/%Y %H:%M:%S')
            except ValueError:
                continue
        
        # Se nenhum formato funcionar, retorna o original
        return date_string
    except Exception:
        return date_string

if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
    except (OSError, PermissionError):
        # Em produção (Vercel), o sistema de arquivos pode ser somente leitura
        # Nesse caso, os dados virão do Supabase (via SUPABASE_URL)
        pass

# Cache para processamento de categorias
_categories_cache = {}
_categories_cache_timestamps = {}


@lru_cache(maxsize=128)
def parse_date_cached(date_str):
    """Função cacheada para parsing de datas"""
    if not date_str:
        return None

    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


# Decoradores de autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        users = load_data(USERS_FILE)
        user = users.get(session['user_id'])
        if not user or user['tipo'] != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Rotas principais
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        
        print(f"Tentativa de login - Login: {login}, Senha: {senha}")
        
        # Forçar recarregamento sem cache para debug
        users = load_data(USERS_FILE, use_cache=False)
        user = None
        
        for uid, udata in users.items():
            login_comparacao = udata.get('login', '')
            
            if udata['login'] == login:
                print(f"USUARIO ENCONTRADO: {udata['login']} (ID: {uid})")
                print(f"Hash: {udata['senha'][:50]}...")
                
                try:
                    password_check = check_password_hash(udata['senha'], senha)
                    print(f"VERIFICACAO SENHA: {password_check}")
                    
                    if password_check:
                        user = udata
                        user_id = uid
                        print(f"LOGIN SUCESSO: {login}")
                        break
                except Exception as e:
                    print(f"ERRO VERIFICACAO: {e}")
                    continue
        
        if not user:
            print(f"Login falhou para: {login}")
            flash('Login ou senha incorretos!')
            return render_template('login.html')
        
        if user:
            session['user_id'] = user_id
            session['user_tipo'] = user['tipo']
            
            # Verificar tempo de exibição
            if user['tipo'] == 'usuario':
                try:
                    # Tentar parser com formato de data apenas
                    tempo_exibicao = datetime.strptime(user['tempo_exibicao'], '%Y-%m-%d')
                except ValueError:
                    try:
                        # Tentar parser com formato de data e hora
                        tempo_exibicao = datetime.strptime(user['tempo_exibicao'], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # Se ambos falharem, usar data atual como fallback
                        tempo_exibicao = datetime.now()
                
                if datetime.now() > tempo_exibicao:
                    session['tempo_expirado'] = True
                else:
                    session['tempo_expirado'] = False
            
            return redirect(url_for('greeting'))
        else:
            flash('Login ou senha incorretos!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/greeting')
@login_required
def greeting():
    greetings = load_data(GREETINGS_FILE)
    users = load_data(USERS_FILE)
    user = users.get(session['user_id'])
    
    # Personalizar saudação
    greeting_text = greetings.get('texto', 'Bem-vindo(a)!')
    greeting_text = greeting_text.replace('{nome}', user['nome_completo'])
    
    return render_template('greeting.html', 
                         greeting=greetings, 
                         greeting_text=greeting_text,
                         user=user)

@app.route('/dashboard')
@login_required
def dashboard():
    users = load_data(USERS_FILE)
    user = users.get(session['user_id'])
    
    if user['tipo'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = load_data(USERS_FILE)
    admin_count = sum(1 for u in users.values() if u['tipo'] == 'admin')
    user_count = sum(1 for u in users.values() if u['tipo'] == 'usuario')
    
    # Carregar dados para o dashboard
    categories = load_data(CATEGORIES_FILE)
    answers = load_data(ANSWERS_FILE)
    unanswered_count = sum(1 for answer in answers.values() if not answer.get('resposta'))
    
    return render_template('admin/dashboard.html', 
                         admin_count=admin_count, 
                         user_count=user_count,
                         categories=categories,
                         unanswered_count=unanswered_count)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    users = load_data(USERS_FILE)
    user = users.get(session['user_id'])
    
    # Verificar se tempo expirou
    try:
        # Tentar parser com formato de data apenas
        tempo_exibicao = datetime.strptime(user['tempo_exibicao'], '%Y-%m-%d')
    except ValueError:
        try:
            # Tentar parser com formato de data e hora
            tempo_exibicao = datetime.strptime(user['tempo_exibicao'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # Se ambos falharem, usar data atual como fallback
            tempo_exibicao = datetime.now()
    tempo_expirado = datetime.now() > tempo_exibicao
    
    if tempo_expirado:
        return render_template('user/tempo_expirado.html', user=user)
    
    # Calcular dias restantes
    dias_restantes = (tempo_exibicao - datetime.now()).days
    
    # Carregar campos adicionais
    fields = load_data(FIELDS_FILE)
    categories = load_data(CATEGORIES_FILE)
    
    # Processar categorias para ordenação por data de início (otimizado)
    start_time = time.time()
    
    # Verificar cache para categorias processadas
    cache_key = f"categories_{session['user_id']}_{hash(str(user.get('campos_adicionais', {})))}"
    current_mtime = data_cache_revision()
    
    # Dados do usuário sempre disponíveis
    user_data = user.get('campos_adicionais', {})
    
    if cache_key in _categories_cache and _categories_cache_timestamps.get(cache_key, 0) >= current_mtime:
        categorias_ordenadas = _categories_cache[cache_key]
        print(f"Categorias carregadas do cache em {time.time() - start_time:.3f}s")
    else:
        categorias_ordenadas = []
        data_hoje = datetime.now().date()
        
        # Pré-compilar padrões de busca para melhor performance
        date_patterns = [
            ('DATA INÍCIO', 'DATA INICIO', 'DATA DE CARREGAMENTO'),
            ('DATA TÉRMINO', 'DATA TERMINO', 'DATA TÉRMINIO')
        ]
        
        for category_name, category_data in categories.items():
            categoria_info = {
                'name': category_name,
                'created_at': category_data.get('created_at', ''),
                'data_inicio': None,
                'data_termino': None,
                'status': 'pendente'
            }
            
            # Buscar dados do usuário para esta categoria
            user_category_data = user_data.get(category_name, {})
            
            # Procurar campos de data usando busca otimizada
            if category_name in fields:
                category_fields = fields[category_name]
                
                # Buscar data de início
                for pattern in date_patterns[0]:
                    if pattern in category_fields:
                        data_str = user_category_data.get(pattern)
                        if data_str:
                            categoria_info['data_inicio'] = parse_date_cached(data_str)
                            break
                
                # Buscar data de término
                for pattern in date_patterns[1]:
                    if pattern in category_fields:
                        data_str = user_category_data.get(pattern)
                        if data_str:
                            categoria_info['data_termino'] = parse_date_cached(data_str)
                            break
            
            # Se tem apenas data de início mas não data de término, usar a mesma data para ambos
            if categoria_info['data_inicio'] and not categoria_info['data_termino']:
                categoria_info['data_termino'] = categoria_info['data_inicio']
            
            # Determinar status da categoria (lógica otimizada)
            if categoria_info['data_inicio']:
                if categoria_info['data_inicio'] <= data_hoje:
                    if categoria_info['data_termino'] and categoria_info['data_termino'] < data_hoje:
                        categoria_info['status'] = 'concluida'
                    else:
                        categoria_info['status'] = 'atual'
                else:
                    categoria_info['status'] = 'proxima'
            
            categorias_ordenadas.append(categoria_info)
        
        # Armazenar no cache
        _categories_cache[cache_key] = categorias_ordenadas
        _categories_cache_timestamps[cache_key] = current_mtime
        
        print(f"Categorias processadas em {time.time() - start_time:.3f}s")
    
    # Ordenar categorias por data de início (as sem data ficam no final)
    categorias_com_data = [c for c in categorias_ordenadas if c['data_inicio']]
    categorias_sem_data = [c for c in categorias_ordenadas if not c['data_inicio']]
    
    categorias_com_data.sort(key=lambda x: x['data_inicio'])
    categorias_ordenadas = categorias_com_data + categorias_sem_data
    
    # Identificar fase atual e próxima fase
    fase_atual = None
    proxima_fase = None
    
    for categoria in categorias_ordenadas:
        # Adicionar campos adicionais (LOCAL, ACESSO, INSTRUTOR) da categoria
        category_name = categoria['name']
        user_category_data = user_data.get(category_name, {})
        
        # Adicionar LOCAL
        if 'LOCAL' in user_category_data and user_category_data['LOCAL']:
            categoria['local'] = user_category_data['LOCAL']
        
        # Adicionar INSTRUTOR
        if 'INSTRUTOR' in user_category_data and user_category_data['INSTRUTOR']:
            categoria['instrutor'] = user_category_data['INSTRUTOR']
        
        # Adicionar ACESSO (link)
        if 'ACESSO' in user_category_data and user_category_data['ACESSO']:
            categoria['acesso'] = user_category_data['ACESSO']
        
        if categoria['status'] == 'atual':
            fase_atual = categoria
        elif categoria['status'] == 'proxima' and not proxima_fase:
            proxima_fase = categoria
    
    # Calcular progresso geral (data admissão até data operação)
    progresso_percentual = 0
    data_admissao = None
    data_operacao = None
    
    # Obter data de admissão
    if 'campos_adicionais' in user and 'CADASTRO' in user['campos_adicionais']:
        admissao_str = user['campos_adicionais']['CADASTRO'].get('ADMISSÃO')
        if admissao_str:
            try:
                # Tentar diferentes formatos de data
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
                    try:
                        data_admissao = datetime.strptime(admissao_str, fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass
    
    # Obter data de operação
    if 'campos_adicionais' in user and 'OPERAÇÃO' in user['campos_adicionais']:
        operacao_str = user['campos_adicionais']['OPERAÇÃO'].get('DATA DE OPERAÇÃO')
        if operacao_str and operacao_str != '-':
            try:
                # Tentar diferentes formatos de data
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
                    try:
                        data_operacao = datetime.strptime(operacao_str, fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass
    
    # Calcular percentual de progresso
    if data_admissao and data_operacao:
        today = datetime.now().date()
        total_dias = (data_operacao - data_admissao).days
        dias_decorridos = (today - data_admissao).days
        
        if total_dias > 0:
            progresso_percentual = min(100, max(0, (dias_decorridos / total_dias) * 100))
            if today > data_operacao:
                progresso_percentual = 100
            elif today < data_admissao:
                progresso_percentual = 0
    
    return render_template('user/dashboard.html', 
                         user=user, 
                         dias_restantes=dias_restantes,
                         fields=fields,
                         categories=categories,
                         categorias_ordenadas=categorias_ordenadas,
                         fase_atual=fase_atual,
                         proxima_fase=proxima_fase,
                         today_date=datetime.now().date(),
                         progresso_percentual=progresso_percentual,
                         data_admissao=data_admissao,
                         data_operacao=data_operacao)

# Rotas de administração de usuários
@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = load_data(USERS_FILE)
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_form():
    if request.method == 'POST':
        users = load_data(USERS_FILE)
        
        # Gerar novo ID
        new_id = str(max(int(uid) for uid in users.keys()) + 1) if users else '1'
        
        # Verificar se login já existe
        login = request.form['login']
        for udata in users.values():
            if udata['login'] == login:
                flash('Login já existe!')
                return redirect(url_for('admin_user_form'))
        
        # Criar novo usuário
        new_user = {
            'id': int(new_id),
            'nome_completo': request.form['nome_completo'],
            'login': request.form['login'],
            'senha': generate_password_hash(request.form['senha']),
            'tipo': request.form['tipo'],
            'matricula': request.form['matricula'],
            'tempo_exibicao': request.form['tempo_exibicao'],
            'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ativo': True,
            'campos_adicionais': {}
        }
        
        users[new_id] = new_user
        save_data(USERS_FILE, users)
        
        flash('Usuário criado com sucesso!')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html')

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_edit(user_id):
    users = load_data(USERS_FILE)
    fields = load_data(FIELDS_FILE)
    user = users.get(str(user_id))
    
    if not user:
        flash('Usuário não encontrado!')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        # Atualizar dados básicos
        user['nome_completo'] = request.form['nome_completo']
        user['matricula'] = request.form['matricula']
        user['tempo_exibicao'] = request.form['tempo_exibicao']
        user['tipo'] = request.form['tipo']
        
        # Atualizar senha se fornecida
        if request.form.get('senha'):
            user['senha'] = generate_password_hash(request.form['senha'])
        
        # Atualizar campos adicionais
        user['campos_adicionais'] = {}
        for category, category_fields in fields.items():
            user['campos_adicionais'][category] = {}
            for field_name, field_config in category_fields.items():
                field_key = f"{category}_{field_name}"
                if field_key in request.form:
                    value = request.form[field_key]
                    if value and value.strip():
                        # Converter datas de DD/MM/AAAA para YYYY-MM-DD
                        if field_config.get('type') in ['date', 'data'] and '/' in value:
                            try:
                                parts = value.strip().split('/')
                                if len(parts) == 3:
                                    day, month, year = parts
                                    # Validar e converter
                                    if len(day) == 2 and len(month) == 2 and len(year) == 4:
                                        formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)} 00:00:00"
                                        value = formatted_date
                            except:
                                pass  # Mantém valor original se falhar
                        
                        user['campos_adicionais'][category][field_name] = value
        
        users[str(user_id)] = user
        save_data(USERS_FILE, users)
        
        flash('Usuário atualizado com sucesso!')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form_simple.html', user=user, fields=fields, edit=True)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_user_delete(user_id):
    users = load_data(USERS_FILE)
    user_id_str = str(user_id)
    
    if user_id_str in users:
        del users[user_id_str]
        save_data(USERS_FILE, users)
        flash('Usuário excluído com sucesso!')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete_multiple', methods=['POST'])
@login_required
@admin_required
def admin_users_delete_multiple():
    users = load_data(USERS_FILE)
    user_ids = request.form.getlist('user_ids')
    
    deleted_count = 0
    for user_id in user_ids:
        if user_id in users:
            del users[user_id]
            deleted_count += 1
    
    if deleted_count > 0:
        save_data(USERS_FILE, users)
        flash(f'{deleted_count} usuário(s) excluído(s) com sucesso!')
    else:
        flash('Nenhum usuário foi excluído.')
    
    return redirect(url_for('admin_users'))

# Rotas de categorias e campos
@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    categories = load_data(CATEGORIES_FILE)
    fields = load_data(FIELDS_FILE)
    return render_template('admin/categories.html', categories=categories, fields=fields)

@app.route('/admin/category/add', methods=['POST'])
@login_required
@admin_required
def admin_category_add():
    categories = load_data(CATEGORIES_FILE)
    category_name = request.form['category_name']
    
    if category_name not in categories:
        categories[category_name] = {
            'name': category_name,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_data(CATEGORIES_FILE, categories)
        flash('Categoria criada com sucesso!')
    else:
        flash('Categoria já existe!')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/field/add', methods=['POST'])
@login_required
@admin_required
def admin_field_add():
    fields = load_data(FIELDS_FILE)
    category = request.form['category']
    field_name = request.form['field_name']
    field_type = request.form['field_type']
    required = request.form.get('required', 'off') == 'on'
    
    if category not in fields:
        fields[category] = {}
    
    fields[category][field_name] = {
        'name': field_name,
        'type': field_type,
        'required': required,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_data(FIELDS_FILE, fields)
    flash('Campo criado com sucesso!')
    return redirect(url_for('admin_categories'))

@app.route('/admin/category/edit/<category_name>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_category_edit(category_name):
    categories = load_data(CATEGORIES_FILE)
    
    if request.method == 'POST':
        new_name = request.form['category_name']
        
        if category_name in categories:
            # Renomear categoria
            categories[new_name] = categories.pop(category_name)
            categories[new_name]['name'] = new_name
            
            # Renomear nos campos também
            fields = load_data(FIELDS_FILE)
            if category_name in fields:
                fields[new_name] = fields.pop(category_name)
                save_data(FIELDS_FILE, fields)
            
            save_data(CATEGORIES_FILE, categories)
            flash('Categoria atualizada com sucesso!')
        
        return redirect(url_for('admin_categories'))
    
    category = categories.get(category_name)
    if not category:
        flash('Categoria não encontrada!')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_edit.html', category_name=category_name, category=category)

@app.route('/admin/category/delete/<category_name>', methods=['POST'])
@login_required
@admin_required
def admin_category_delete(category_name):
    categories = load_data(CATEGORIES_FILE)
    
    if category_name in categories:
        del categories[category_name]
        save_data(CATEGORIES_FILE, categories)
        
        # Remover campos da categoria também
        fields = load_data(FIELDS_FILE)
        if category_name in fields:
            del fields[category_name]
            save_data(FIELDS_FILE, fields)
        
        flash('Categoria deletada com sucesso!')
    else:
        flash('Categoria não encontrada!')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/field/edit/<category_name>/<field_name>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_field_edit(category_name, field_name):
    fields = load_data(FIELDS_FILE)
    
    if request.method == 'POST':
        new_name = request.form['field_name']
        field_type = request.form['field_type']
        required = request.form.get('required', 'off') == 'on'
        
        if category_name in fields and field_name in fields[category_name]:
            # Editar campo
            field_data = fields[category_name].pop(field_name)
            field_data['name'] = new_name
            field_data['type'] = field_type
            field_data['required'] = required
            fields[category_name][new_name] = field_data
            
            save_data(FIELDS_FILE, fields)
            flash('Campo atualizado com sucesso!')
        
        return redirect(url_for('admin_categories'))
    
    if category_name not in fields or field_name not in fields[category_name]:
        flash('Campo não encontrado!')
        return redirect(url_for('admin_categories'))
    
    field = fields[category_name][field_name]
    return render_template('admin/field_edit.html', category_name=category_name, field_name=field_name, field=field)

@app.route('/admin/field/delete/<category_name>/<field_name>', methods=['POST'])
@login_required
@admin_required
def admin_field_delete(category_name, field_name):
    fields = load_data(FIELDS_FILE)
    
    if category_name in fields and field_name in fields[category_name]:
        del fields[category_name][field_name]
        
        # Remover categoria se não tiver mais campos
        if not fields[category_name]:
            del fields[category_name]
        
        save_data(FIELDS_FILE, fields)
        flash('Campo deletado com sucesso!')
    else:
        flash('Campo não encontrado!')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/reorder', methods=['POST'])
@login_required
@admin_required
def admin_categories_reorder():
    categories = load_data(CATEGORIES_FILE)
    fields = load_data(FIELDS_FILE)
    
    # Obter ordem das categorias
    category_order = request.form.getlist('category_order')
    
    # Recriar dicionários na nova ordem
    new_categories = {}
    new_fields = {}
    
    for category_name in category_order:
        if category_name in categories:
            new_categories[category_name] = categories[category_name]
        if category_name in fields:
            # Obter ordem dos campos para esta categoria
            field_order_key = f'field_order_{category_name}'
            field_order = request.form.getlist(field_order_key)
            
            # Recriar campos na nova ordem
            if field_order:
                new_fields[category_name] = {}
                for field_name in field_order:
                    if field_name in fields[category_name]:
                        new_fields[category_name][field_name] = fields[category_name][field_name]
            else:
                new_fields[category_name] = fields[category_name]
    
    # Adicionar categorias/campos que não estavam na lista
    for category_name, category_data in categories.items():
        if category_name not in new_categories:
            new_categories[category_name] = category_data
    
    for category_name, field_data in fields.items():
        if category_name not in new_fields:
            new_fields[category_name] = field_data
    
    save_data(CATEGORIES_FILE, new_categories)
    save_data(FIELDS_FILE, new_fields)
    flash('Categorias e campos reordenados com sucesso!')
    
    return redirect(url_for('admin_categories'))

# Rotas de saudações
@app.route('/admin/greetings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_greetings():
    greetings = load_data(GREETINGS_FILE)
    
    if request.method == 'POST':
        greetings['texto'] = request.form['texto']
        greetings['imagem'] = request.form['imagem']
        greetings['video'] = request.form['video']
        save_data(GREETINGS_FILE, greetings)
        flash('Saudação atualizada com sucesso!')
    
    return render_template('admin/greetings.html', greetings=greetings)

# Rotas de perguntas e dúvidas
def fix_missing_matriculas():
    """Atualiza respostas existentes que não têm matrícula"""
    answers = load_data(ANSWERS_FILE)
    users = load_data(USERS_FILE)
    updated = False
    
    for answer_id, answer in answers.items():
        if 'user_matricula' not in answer or not answer['user_matricula']:
            user_id = answer.get('user_id')
            if user_id and user_id in users:
                user = users[user_id]
                answer['user_matricula'] = user.get('matricula', 'N/A')
                updated = True
    
    if updated:
        save_data(ANSWERS_FILE, answers)
        print("Matrículas atualizadas nas respostas existentes")

@app.route('/admin/questions')
@login_required
@admin_required
def admin_questions():
    # Corrigir matrículas ausentes em respostas existentes
    fix_missing_matriculas()
    
    questions = load_data(QUESTIONS_FILE)
    answers = load_data(ANSWERS_FILE)
    
    # Contar não respondidas
    unanswered_count = sum(1 for answer in answers.values() if not answer.get('resposta'))
    
    # Agrupar respostas por usuário
    users_answers = {}
    for answer_id, answer in answers.items():
        # Tratar campos ausentes com valores padrão
        user_name = answer.get('user_name', 'Usuário Desconhecido')
        user_matricula = answer.get('user_matricula', 'N/A')
        user_key = f"{user_name}|{user_matricula}"
        
        if user_key not in users_answers:
            users_answers[user_key] = {
                'user_name': user_name,
                'user_matricula': user_matricula,
                'answers': []
            }
        users_answers[user_key]['answers'].append({
            'id': answer_id,
            'answer': answer
        })
    
    # Ordenar respostas de cada usuário por data (mais recente primeiro)
    for user_data in users_answers.values():
        user_data['answers'].sort(key=lambda x: x['answer'].get('data_pergunta', ''), reverse=True)
    
    return render_template('admin/questions.html', 
                         questions=questions, 
                         answers=answers, 
                         unanswered_count=unanswered_count,
                         users_answers=users_answers)

@app.route('/admin/questions/user/<user_key>')
@login_required
@admin_required
def admin_user_questions(user_key):
    answers = load_data(ANSWERS_FILE)
    
    # Extrair nome e matrícula do user_key
    try:
        if '|' in user_key:
            user_name, user_matricula = user_key.split('|', 1)  # Split apenas no primeiro |
        else:
            user_name = user_key
            user_matricula = 'N/A'
        
        # Agrupar respostas do usuário específico
        user_answers = []
        for answer_id, answer in answers.items():
            answer_name = answer.get('user_name', 'Usuário Desconhecido')
            answer_matricula = answer.get('user_matricula', 'N/A')
            
            if answer_name == user_name and answer_matricula == user_matricula:
                user_answers.append({
                    'id': answer_id,
                    'answer': answer
                })
        
        # Ordenar por data (mais recente primeiro)
        user_answers.sort(key=lambda x: x['answer'].get('data_pergunta', ''), reverse=True)
        
        return jsonify({
            'user_name': user_name,
            'user_matricula': user_matricula,
            'answers': user_answers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/answer/<answer_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_answer(answer_id):
    answers = load_data(ANSWERS_FILE)
    
    if answer_id in answers:
        answers[answer_id]['resposta'] = request.form['resposta']
        answers[answer_id]['data_resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(ANSWERS_FILE, answers)
        flash('Resposta atualizada com sucesso!')
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/answer/<answer_id>/comment', methods=['POST'])
@login_required
@admin_required
def admin_add_comment(answer_id):
    answers = load_data(ANSWERS_FILE)
    
    if answer_id in answers:
        answers[answer_id]['comentario_admin'] = request.form['comentario']
        answers[answer_id]['data_comentario'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(ANSWERS_FILE, answers)
        flash('Comentário adicionado com sucesso!')
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/question/add', methods=['POST'])
@login_required
@admin_required
def admin_question_add():
    questions = load_data(QUESTIONS_FILE)
    category = request.form['category']
    question_text = request.form['question_text']
    allows_text = request.form.get('allows_text', 'off') == 'on'
    
    if category not in questions:
        questions[category] = []
    
    questions[category].append({
        'text': question_text,
        'allows_text': allows_text,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    save_data(QUESTIONS_FILE, questions)
    flash('Pergunta adicionada com sucesso!')
    return redirect(url_for('admin_questions'))

@app.route('/admin/question/edit', methods=['POST'])
@login_required
@admin_required
def admin_question_edit():
    questions = load_data(QUESTIONS_FILE)
    category = request.form['category']
    index = int(request.form['index'])
    new_category = request.form['new_category']
    question_text = request.form['question_text']
    allows_text = request.form.get('allows_text', 'off') == 'on'
    
    # Verificar se a categoria e índice são válidos
    if category in questions and 0 <= index < len(questions[category]):
        question = questions[category].pop(index)
        
        # Se a categoria mudou, mover para a nova categoria
        if new_category != category:
            if new_category not in questions:
                questions[new_category] = []
            questions[new_category].append(question)
            category = new_category
        else:
            questions[category].insert(index, question)
        
        # Atualizar os dados da pergunta
        questions[category][index]['text'] = question_text
        questions[category][index]['allows_text'] = allows_text
        
        save_data(QUESTIONS_FILE, questions)
        flash('Pergunta atualizada com sucesso!')
    else:
        flash('Pergunta não encontrada!')
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/question/delete', methods=['POST'])
@login_required
@admin_required
def admin_question_delete():
    questions = load_data(QUESTIONS_FILE)
    category = request.form['category']
    index = int(request.form['index'])
    
    # Verificar se a categoria e índice são válidos
    if category in questions and 0 <= index < len(questions[category]):
        questions[category].pop(index)
        
        # Se a categoria ficar vazia, removê-la
        if not questions[category]:
            del questions[category]
        
        save_data(QUESTIONS_FILE, questions)
        flash('Pergunta excluída com sucesso!')
    else:
        flash('Pergunta não encontrada!')
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/answer/<int:answer_id>', methods=['POST'])
@login_required
@admin_required
def admin_answer(answer_id):
    answers = load_data(ANSWERS_FILE)
    answer_id_str = str(answer_id)
    
    if answer_id_str in answers:
        answers[answer_id_str]['resposta'] = request.form['resposta']
        answers[answer_id_str]['data_resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(ANSWERS_FILE, answers)
        flash('Resposta enviada com sucesso!')
    
    return redirect(url_for('admin_questions'))

# Rotas do usuário
@app.route('/user/questions', methods=['GET', 'POST'])
@login_required
def user_questions():
    questions = load_data(QUESTIONS_FILE)
    answers = load_data(ANSWERS_FILE)
    users = load_data(USERS_FILE)
    user = users.get(session['user_id'])
    
    if request.method == 'POST':
        question_id = request.form['question_id']
        complement = request.form.get('complement', '')
        
        # Criar nova resposta
        new_answer_id = str(max(int(aid) for aid in answers.keys()) + 1) if answers else '1'
        
        answers[new_answer_id] = {
            'user_id': session['user_id'],
            'user_name': user['nome_completo'],
            'user_matricula': user.get('matricula', 'N/A'),
            'question_id': question_id,
            'question_text': request.form['question_text'],
            'complement': complement,
            'resposta': None,
            'data_pergunta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        save_data(ANSWERS_FILE, answers)
        flash('Dúvida enviada com sucesso!')
        return redirect(url_for('user_questions'))
    
    # Filtrar perguntas do usuário
    user_answers = {aid: answer for aid, answer in answers.items() 
                   if answer.get('user_id') == session['user_id']}
    
    return render_template('user/questions.html', 
                         questions=questions, 
                         user_answers=user_answers)

# Rotas de upload Excel
@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('admin_upload'))
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('admin_upload'))
        
        if file and file.filename.endswith('.xlsx'):
            try:
                start_time = time.time()
                
                print(f"DEBUG: Iniciando processamento do arquivo: {file.filename}")
                print(f"DEBUG: Tamanho do arquivo: {file.content_length if hasattr(file, 'content_length') else 'desconhecido'}")
                
                # Limpar cache para garantir dados atualizados
                clear_cache(USERS_FILE)
                
                # Otimização: ler Excel com parâmetros de performance
                print(f"DEBUG: Tentando ler arquivo Excel...")
                df = pd.read_excel(file, dtype=str, na_filter=False)
                print(f"DEBUG: Arquivo Excel lido com sucesso")
                
                users = load_data(USERS_FILE)
                fields = load_data(FIELDS_FILE)
                
                print(f"Arquivo carregado em {time.time() - start_time:.3f}s - {len(df)} linhas")
                
                # Verificar colunas obrigatórias
                required_columns = ['nome_completo', 'login', 'senha', 'matricula', 'tempo_exibicao']
                for col in required_columns:
                    if col not in df.columns:
                        flash(f'Coluna obrigatória faltando: {col}')
                        return redirect(url_for('admin_upload'))
                
                # Criar índice de matrículas para busca O(1)
                matricula_index = {str(u.get('matricula')): uid for uid, u in users.items()}
                
                # Obter modo de upload
                upload_mode = request.form.get('upload_mode', 'update')
                
                # Processar em lotes
                batch_size = 100
                processed_count = 0
                updated_count = 0
                created_count = 0
                
                for batch_start in range(0, len(df), batch_size):
                    batch_end = min(batch_start + batch_size, len(df))
                    batch_df = df.iloc[batch_start:batch_end]
                    
                    for index, row in batch_df.iterrows():
                        actual_index = batch_start + index
                        processed_count += 1
                        
                        # Buscar usuário existente usando índice O(1)
                        matricula = str(row['matricula'])
                        existing_id = matricula_index.get(matricula)
                        existing_user = users.get(existing_id) if existing_id else None
                        
                        # Verificar campos obrigatórios vazios (só para novos usuários)
                        if not existing_user:
                            empty_required = []
                            for col in required_columns:
                                if pd.isna(row[col]) or str(row[col]).strip() == '':
                                    empty_required.append(col)
                            
                            if empty_required and request.form.get('ignore_empty') != 'on':
                                flash(f'Linha {actual_index + 1}: Campos obrigatórios em branco detectados: {", ".join(empty_required)}')
                                continue
                        else:
                            # Para usuários existentes, só verificar login como obrigatório
                            if pd.isna(row['login']) or str(row['login']).strip() == '':
                                flash(f'Linha {actual_index + 1}: Login é obrigatório para atualização de usuário existente')
                                continue
                        
                        # Criar ou atualizar usuário
                        if existing_user:
                            # Atualizar usuário existente
                            user_data = existing_user
                            updated_count += 1
                            
                            if upload_mode == 'update':
                                # Modo UPDATE: só atualiza campos com informação
                                print(f"Processando usuário existente: {user_data.get('login', 'N/A')} (Matrícula: {matricula})")
                                
                                if pd.notna(row['nome_completo']) and str(row['nome_completo']).strip():
                                    user_data['nome_completo'] = str(row['nome_completo']).strip()
                                
                                if pd.notna(row['login']) and str(row['login']).strip():
                                    user_data['login'] = str(row['login']).strip()
                                
                                if pd.notna(row['tempo_exibicao']) and str(row['tempo_exibicao']).strip():
                                    user_data['tempo_exibicao'] = str(row['tempo_exibicao']).strip()
                                
                                # Debug específico para senha
                                senha_excel = str(row['senha']).strip() if pd.notna(row['senha']) else ''
                                if senha_excel:
                                    user_data['senha'] = generate_password_hash(senha_excel)
                                    print(f"SENHA ATUALIZADA: {senha_excel}")
                                
                                # Processar campos adicionais (cronograma)
                                if not user_data.get('campos_adicionais'):
                                    user_data['campos_adicionais'] = {}
                                
                                for category, category_fields in fields.items():
                                    if category not in user_data['campos_adicionais']:
                                        user_data['campos_adicionais'][category] = {}
                                    
                                    for field_name, field_config in category_fields.items():
                                        # Procurar coluna com categoria no nome
                                        column_with_category = f"{field_name} [{category}]"
                                        if column_with_category in df.columns:
                                            value = row[column_with_category]
                                            if pd.notna(value) and str(value).strip():
                                                # Converter datas se necessário
                                                if field_config.get('type') in ['date', 'data'] and '/' in str(value):
                                                    try:
                                                        parts = str(value).strip().split('/')
                                                        if len(parts) == 3:
                                                            day, month, year = parts
                                                            if len(day) == 2 and len(month) == 2 and len(year) == 4:
                                                                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)} 00:00:00"
                                                                value = formatted_date
                                                    except:
                                                        pass
                                                user_data['campos_adicionais'][category][field_name] = str(value)
                                                print(f"CAMPO ADICIONAL ATUALIZADO: {category} - {field_name} = {value}")
                                
                                users[existing_id] = user_data
                            else:
                                # Modo REPLACE: substitui todos os campos
                                user_data['nome_completo'] = str(row['nome_completo']).strip() if pd.notna(row['nome_completo']) else ''
                                user_data['login'] = str(row['login']).strip() if pd.notna(row['login']) else ''
                                user_data['tempo_exibicao'] = str(row['tempo_exibicao']).strip() if pd.notna(row['tempo_exibicao']) else ''
                                
                                senha_excel = str(row['senha']).strip() if pd.notna(row['senha']) else ''
                                if senha_excel:
                                    user_data['senha'] = generate_password_hash(senha_excel)
                                    print(f"SENHA ATUALIZADA (REPLACE): {senha_excel}")
                                
                                # Processar campos adicionais (cronograma) no modo REPLACE
                                user_data['campos_adicionais'] = {}
                                
                                for category, category_fields in fields.items():
                                    user_data['campos_adicionais'][category] = {}
                                    for field_name, field_config in category_fields.items():
                                        # Procurar coluna com categoria no nome
                                        column_with_category = f"{field_name} [{category}]"
                                        if column_with_category in df.columns:
                                            value = row[column_with_category]
                                            if pd.notna(value) and str(value).strip():
                                                # Converter datas se necessário
                                                if field_config.get('type') in ['date', 'data'] and '/' in str(value):
                                                    try:
                                                        parts = str(value).strip().split('/')
                                                        if len(parts) == 3:
                                                            day, month, year = parts
                                                            if len(day) == 2 and len(month) == 2 and len(year) == 4:
                                                                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)} 00:00:00"
                                                                value = formatted_date
                                                    except:
                                                        pass
                                                user_data['campos_adicionais'][category][field_name] = str(value)
                                                print(f"CAMPO ADICIONAL ATUALIZADO (REPLACE): {category} - {field_name} = {value}")
                                
                                users[existing_id] = user_data
                        else:
                            # Criar novo usuário
                            new_id = str(max(int(uid) for uid in users.keys()) + 1) if users else '1'
                            created_count += 1
                            
                            new_user = {
                                'id': int(new_id),
                                'nome_completo': str(row['nome_completo']).strip() if pd.notna(row['nome_completo']) else '',
                                'login': str(row['login']).strip() if pd.notna(row['login']) else '',
                                'senha': generate_password_hash(str(row['senha']).strip()) if pd.notna(row['senha']) and str(row['senha']).strip() else generate_password_hash('temp123'),
                                'tipo': 'usuario',
                                'matricula': matricula,
                                'tempo_exibicao': str(row['tempo_exibicao']).strip() if pd.notna(row['tempo_exibicao']) else '',
                                'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'ativo': True,
                                'campos_adicionais': {}
                            }
                            
                            # Processar campos adicionais (cronograma) para novos usuários
                            for category, category_fields in fields.items():
                                new_user['campos_adicionais'][category] = {}
                                for field_name, field_config in category_fields.items():
                                    # Procurar coluna com categoria no nome
                                    column_with_category = f"{field_name} [{category}]"
                                    if column_with_category in df.columns:
                                        value = row[column_with_category]
                                        if pd.notna(value) and str(value).strip():
                                            # Converter datas se necessário
                                            if field_config.get('type') in ['date', 'data'] and '/' in str(value):
                                                try:
                                                    parts = str(value).strip().split('/')
                                                    if len(parts) == 3:
                                                        day, month, year = parts
                                                        if len(day) == 2 and len(month) == 2 and len(year) == 4:
                                                            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)} 00:00:00"
                                                            value = formatted_date
                                                except:
                                                    pass
                                            new_user['campos_adicionais'][category][field_name] = str(value)
                                            print(f"CAMPO ADICIONAL CRIADO: {category} - {field_name} = {value}")
                            
                            users[new_id] = new_user
                
                save_data(USERS_FILE, users)
                
                if upload_mode == 'update':
                    flash('Upload processado com sucesso! (Modo: Atualizar Banco de Dados)')
                else:
                    flash('Upload processado com sucesso! (Modo: Deletar e Substituir)')
                
                # Debug - mostrar estatísticas do processamento
                flash(f"Debug: Processadas {processed_count} linhas. Atualizados: {updated_count}, Criados: {created_count}")
                print(f"UPLOAD COMPLETO: {processed_count} linhas processadas")
                print(f"UPLOAD ESTATÍSTICAS: Atualizados={updated_count}, Criados={created_count}")
                
            except Exception as e:
                flash(f'Erro ao processar arquivo: {str(e)}')
        else:
            flash('Formato de arquivo inválido! Apenas arquivos .xlsx são aceitos.')
        
        return redirect(url_for('admin_upload'))
    
    return render_template('admin/upload.html')

@app.route('/admin/download-template')
@login_required
@admin_required
def admin_download_template():
    fields = load_data(FIELDS_FILE)
    
    # Criar DataFrame com campos obrigatórios
    columns = ['nome_completo', 'login', 'senha', 'matricula', 'tempo_exibicao']
    
    # Adicionar campos configuráveis com categoria como referência
    for category, category_fields in fields.items():
        for field_name, field_config in category_fields.items():
            # Criar nome de coluna com categoria como referência
            column_name = f"{field_name} [{category}]"
            columns.append(column_name)
    
    # Criar DataFrame vazio com as colunas
    df = pd.DataFrame(columns=columns)
    
    # Adicionar linha de exemplo com categorias
    example_row = {}
    for col in columns:
        if '[' in col and ']' in col:
            # Extrair nome do campo e categoria
            field_name = col.split(' [')[0]
            category = col.split(' [')[1].replace(']', '')
            example_row[col] = f"Exemplo {field_name} (Categoria: {category})"
        else:
            example_row[col] = f"Exemplo {col}"
    
    # Adicionar linha de exemplo
    df = pd.concat([df, pd.DataFrame([example_row])], ignore_index=True)
    
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="template_usuarios.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


init_data()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
