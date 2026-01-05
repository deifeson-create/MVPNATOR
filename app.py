import streamlit as st
import pandas as pd
import requests
import concurrent.futures
from datetime import datetime, timedelta

# ==============================================================================
# 1. CONFIGURAÇÕES INICIAIS
# ==============================================================================
st.set_page_config(page_title="Painel MVP - Oficial", layout="wide", page_icon="🏆")

# --- 🔒 BLOQUEIO DE SEGURANÇA (SENHA MESTRA) ---
def check_master_password():
    """Bloqueia o app até que a senha mestra seja inserida."""
    if "app_unlocked" not in st.session_state:
        st.session_state.app_unlocked = False

    if not st.session_state.app_unlocked:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.title("🔒 Acesso Restrito")
            st.markdown("Este sistema é protegido. Insira a senha de acesso.")
            
            with st.form("master_login"):
                senha_input = st.text_input("Senha do Sistema", type="password")
                submit = st.form_submit_button("Desbloquear Painel", use_container_width=True)
                
                if submit:
                    # Verifica a senha no secrets
                    if senha_input == st.secrets["security"]["MASTER_PASSWORD"]:
                        st.session_state.app_unlocked = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
        
        st.stop() # Para a execução aqui se não estiver desbloqueado

# Executa a verificação antes de qualquer coisa
check_master_password()

# ==============================================================================
# 2. CONSTANTES E CONFIGURAÇÕES DE NEGÓCIO
# ==============================================================================

CONFIG_PESQUISA = {
    "PESQUISAS_IDS": ["35", "43"],
    "IDS_PERGUNTAS_VALIDAS": ["65", "75"]
}

SETORES_AGENTES = {
    "NRC": ['RILDYVAN', 'MILENA', 'ALVES', 'MONICKE', 'AYLA', 'MARIANY', 'EDUARDA', 
            'MENEZES', 'JUCIENNY', 'MARIA', 'ANDREZA', 'LUZILENE', 'IGO', 'AIDA', 
            'Caribé', 'Michelly', 'ADRIA', 'ERICA', 'HENRIQUE', 'SHYRLEI', 'ANNA', 
            'JULIA', 'FERNANDES'],
    "CANCELAMENTO": ['BARBOSA', 'ELOISA', 'LARISSA', 'EDUARDO', 'CAMILA', 'SAMARA'],
    "NEGOCIACAO": ['Carla', 'Lenk', 'Ana Luiza', 'JULIETTI', 'RODRIGO', 'Monalisa', 
                   'Ramom', 'Ednael', 'Leticia', 'Rita', 'Mariana', 'Flavia s', 'Uri', 
                   'Clara', 'Wanderson', 'Aparecida', 'Cristina', 'Caio', 'LUKAS'],
    "SUPORTE": ['VALERIO', 'TARCISIO', 'GRANJA', 'ALICE', 'FERNANDO', 'SANTOS', 'RENAN', 
                'FERREIRA', 'HUEMILLY', 'LOPES', 'LAUDEMILSON', 'RAYANE', 'LAYS', 'JORGE', 
                'LIGIA', 'ALESSANDRO', 'GEIBSON', 'ROBERTO', 'OLIVEIRA', 'MAURÍCIO', 'AVOLO', 
                'CLEBER', 'ROMERIO', 'JUNIOR', 'ISABELA', 'RENAN', 'WAGNER', 'CLAUDIA', 
                'ANTONIO', 'JOSE', 'LEONARDO', 'KLEBSON', 'OZENAIDE']
}

CANAIS_ALVO = ['appchat', 'chat', 'botmessenger', 'instagram', 'whatsapp']

# ==============================================================================
# 3. CARREGAMENTO DE SEGREDOS (API)
# ==============================================================================
try:
    API_URL = st.secrets["api"]["BASE_URL"]
    API_USER = st.secrets["api"]["ADMIN_USER"]
    API_PASS = st.secrets["api"]["ADMIN_PASS"]
    API_CONTA_PADRAO = st.secrets["api"]["ID_CONTA"]
except Exception as e:
    st.error("❌ Erro Crítico: Credenciais da API não encontradas no secrets.")
    st.stop()

def obter_contas_do_setor(nome_setor):
    """Regra de Negócio: Negociação usa conta 1 e 14."""
    contas = [API_CONTA_PADRAO]
    if nome_setor == "NEGOCIACAO":
        if "14" not in contas: contas.append("14")
    return contas

# ==============================================================================
# 4. FUNÇÕES VISUAIS
# ==============================================================================
def render_top3_cards(df_rank):
    """Renderiza os cards de Ouro, Prata e Bronze."""
    if df_rank.empty: return

    top_3 = df_rank.head(3).to_dict('records')
    
    st.markdown("""
    <style>
        .podium-box {
            padding: 15px; border-radius: 10px; text-align: center; color: #1f2937;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid rgba(0,0,0,0.1);
        }
        .podium-medal { font-size: 40px; margin-bottom: 5px; }
        .podium-title { font-weight: 800; text-transform: uppercase; font-size: 14px; letter-spacing: 1px; }
        .podium-name { font-size: 18px; font-weight: 700; margin: 10px 0; }
        .podium-stats { font-size: 12px; opacity: 0.9; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    metais = [
        {"nome": "OURO", "emoji": "🥇", "bg": "linear-gradient(135deg, #FFD700 0%, #FDB931 100%)"},
        {"nome": "PRATA", "emoji": "🥈", "bg": "linear-gradient(135deg, #E0E0E0 0%, #BDBDBD 100%)"},
        {"nome": "BRONZE", "emoji": "🥉", "bg": "linear-gradient(135deg, #E6A570 0%, #CD7F32 100%)"}
    ]

    for i, dados in enumerate(top_3):
        if i < 3:
            with cols[i]:
                metal = metais[i]
                st.markdown(f"""
                <div class="podium-box" style="background: {metal['bg']};">
                    <div class="podium-medal">{metal['emoji']}</div>
                    <div class="podium-title">{metal['nome']}</div>
                    <div class="podium-name">{dados['Agente']}</div>
                    <div class="podium-stats">
                        Score: {int(dados['Score_Final'])}<br>
                        CSAT: {dados['CSAT_Score']:.4f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# 5. FUNÇÕES DE CÁLCULO
# ==============================================================================
def time_str_to_seconds(tempo_str):
    if not tempo_str or not isinstance(tempo_str, str): return 0
    try:
        parts = list(map(int, tempo_str.split(':')))
        if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
    except: pass
    return 0

def seconds_to_hms(seconds):
    if not seconds: return "00:00:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def calcular_rankings_setor(df_dados):
    if df_dados.empty: return None, df_dados
    df = df_dados.copy()
    
    df['TMA_Seg'] = df['TMA'].apply(time_str_to_seconds)
    df['TMIA_Seg'] = df['TMIA'].apply(time_str_to_seconds)

    df_elegivel = df[(df['Volume'] > 0) & (df['CSAT_Qtd'] > 0)].copy()
    if df_elegivel.empty: return None, df

    df_elegivel['Rank_TMA'] = df_elegivel['TMA_Seg'].rank(ascending=True)
    df_elegivel['Rank_TMIA'] = df_elegivel['TMIA_Seg'].rank(ascending=True)
    df_elegivel['Rank_CSAT'] = df_elegivel['CSAT_Score'].rank(ascending=False)

    df_elegivel['Score_Final'] = (df_elegivel['Rank_TMA'] + df_elegivel['Rank_TMIA'] + df_elegivel['Rank_CSAT'])

    df_final = df_elegivel.sort_values(by='Score_Final', ascending=True)
    vencedor = df_final.iloc[0]['Agente']
    return vencedor, df_final

# ==============================================================================
# 6. INTEGRAÇÃO API
# ==============================================================================
@st.cache_data(ttl=3600)
def get_token():
    try:
        url = f"{API_URL.rstrip('/')}/rest/v2/authuser"
        payload = {"login": API_USER, "chave": API_PASS}
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200 and r.json().get("success"):
            return r.json()["result"]["token"]
    except: pass
    return None

@st.cache_data(ttl=86400)
def buscar_ids_canais(token):
    url = f"{API_URL.rstrip('/')}/rest/v2/canais"
    headers = {"Authorization": f"Bearer {token}"}
    ids = []
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            for c in r.json():
                if any(alvo in str(c.get("canal", "")).lower() for alvo in CANAIS_ALVO):
                    ids.append(str(c.get("id_canal")))
    except: pass
    return ids

@st.cache_data(ttl=3600)
def mapear_agentes_api(token):
    url = f"{API_URL.rstrip('/')}/rest/v2/agentes"
    headers = {"Authorization": f"Bearer {token}"}
    agentes_categorizados = {setor: {} for setor in SETORES_AGENTES.keys()}
    todos_ids = []
    page = 1
    while True:
        try:
            params = {"limit": 100, "page": page, "bol_cancelado": 0}
            r = requests.get(url, headers=headers, params=params)
            if r.status_code != 200: break
            data = r.json()
            rows = data.get("result", [])
            if not rows: break
            for ag in rows:
                cod = str(ag.get("cod_agente"))
                nome_api = str(ag.get("nome_exibicao") or ag.get("agente")).strip().upper()
                partes_nome = nome_api.split()
                for setor, lista_nomes in SETORES_AGENTES.items():
                    for alvo in lista_nomes:
                        if alvo.upper() in partes_nome:
                            agentes_categorizados[setor][cod] = nome_api
                            todos_ids.append(cod)
                            break
            if page * 100 >= data.get("total", 0): break
            page += 1
        except: break
    return agentes_categorizados, list(set(todos_ids))

@st.cache_data(ttl=600)
def buscar_dados_operacionais_multi(token, lista_contas, d_ini, d_fim, canais, agentes_ids):
    url = f"{API_URL.rstrip('/')}/rest/v2/relAtEstatistico"
    headers = {"Authorization": f"Bearer {token}"}
    temp_stats = {} 
    
    for id_conta in lista_contas:
        params = {
            "data_inicial": f"{d_ini} 00:00:00", "data_final": f"{d_fim} 23:59:59",
            "agrupador": "agente", "agente[]": agentes_ids, "canal[]": canais, "id_conta": id_conta
        }
        try:
            r = requests.get(url, headers=headers, params=params, timeout=40)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    for item in data:
                        nome = str(item.get("agrupador", "")).upper()
                        qtd = int(item.get("num_qtd", 0)) - int(item.get("num_qtd_abandonado", 0))
                        tma_sec = time_str_to_seconds(item.get("tma", "00:00:00"))
                        tmia_sec = time_str_to_seconds(item.get("tmia", "00:00:00"))
                        
                        if nome not in temp_stats: temp_stats[nome] = {"Vol": 0, "W_TMA": 0, "W_TMIA": 0}
                        temp_stats[nome]["Vol"] += qtd
                        temp_stats[nome]["W_TMA"] += (tma_sec * qtd)
                        temp_stats[nome]["W_TMIA"] += (tmia_sec * qtd)
        except: pass

    stats_final = {}
    for nome, dados in temp_stats.items():
        vol = dados["Vol"]
        if vol > 0: avg_tma = dados["W_TMA"] / vol; avg_tmia = dados["W_TMIA"] / vol
        else: avg_tma = 0; avg_tmia = 0
        stats_final[nome] = {"Volume": vol, "TMA": seconds_to_hms(avg_tma), "TMIA": seconds_to_hms(avg_tmia)}
    return stats_final

def buscar_csat_multi(token, lista_contas, id_agente, d_ini, d_fim):
    url = f"{API_URL.rstrip('/')}/rest/v2/RelPesqAnalitico"
    headers = {"Authorization": f"Bearer {token}"}
    pos_total, tot_total = 0, 0
    
    for id_conta in lista_contas:
        for p_id in CONFIG_PESQUISA['PESQUISAS_IDS']:
            page = 1
            while True:
                params = {"data_inicial": d_ini, "data_final": d_fim, "pesquisa": p_id, "id_conta": id_conta, "limit": 1000, "page": page, "agente[]": [id_agente]}
                try:
                    r = requests.get(url, headers=headers, params=params)
                    if r.status_code != 200: break
                    data = r.json()
                    if not data or not isinstance(data, list): break
                    encontrou = False
                    for bloco in data:
                        if str(bloco.get("id_pergunta", "")) in CONFIG_PESQUISA['IDS_PERGUNTAS_VALIDAS']:
                            encontrou = True
                            for resp in bloco.get("respostas", []):
                                try:
                                    val = float(resp.get("nom_valor", -1))
                                    if val >= 0:
                                        tot_total += 1
                                        if val >= 8: pos_total += 1
                                except: pass
                    if len(data) < 2 and not encontrou: break
                    if len(data) < 100: break
                    page += 1
                except: break
    return pos_total, tot_total

# ==============================================================================
# 7. APP STREAMLIT (Layout)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Configuração")
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1)
    data_ini = st.date_input("Início", inicio_mes)
    data_fim = st.date_input("Fim", hoje)
    
    st.markdown("---")
    st.markdown("**Status:** 🟢 Sistema Seguro")
    btn_calcular = st.button("🚀 Calcular MVP", use_container_width=True, type="primary")

st.title("🏆 Ranking MVP - Resultados Oficiais")
st.markdown("Sistema de eleição automática baseado em **Soma de Rankings**.")

if btn_calcular:
    token = get_token()
    if not token: st.error("Erro de Autenticação."); st.stop()
        
    with st.status("🔍 Analisando indicadores...", expanded=True) as status:
        st.write("📡 Mapeando equipe e setores...")
        ids_canais = buscar_ids_canais(token)
        mapa_setores, lista_todos_ids = mapear_agentes_api(token)
        
        if not lista_todos_ids: st.error("Nenhum agente encontrado."); st.stop()
            
        d_ini_str = data_ini.strftime("%Y-%m-%d")
        d_fim_str = data_fim.strftime("%Y-%m-%d")
        
        abas = st.tabs(list(mapa_setores.keys()))
        
        for i, (setor, agentes_dict) in enumerate(mapa_setores.items()):
            if not agentes_dict:
                with abas[i]: st.warning("Setor sem agentes mapeados."); continue
            
            contas_alvo = obter_contas_do_setor(setor)
            st.toast(f"Analisando {setor} (Contas: {contas_alvo})...")
            
            ids_setor = list(agentes_dict.keys())
            stats_ops = buscar_dados_operacionais_multi(token, contas_alvo, d_ini_str, d_fim_str, ids_canais, ids_setor)
            
            dados_setor = []
            progress_text = f"Processando {setor}..."
            my_bar = st.progress(0, text=progress_text)
            total_ag = len(ids_setor); done = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = {executor.submit(buscar_csat_multi, token, contas_alvo, cod, d_ini_str, d_fim_str): cod for cod in ids_setor}
                
                for future in concurrent.futures.as_completed(futures):
                    cod = futures[future]
                    nome = agentes_dict[cod]
                    try:
                        pos, tot = future.result()
                        csat = (pos / tot * 100) if tot > 0 else 0.0
                        ops = stats_ops.get(nome, {"Volume": 0, "TMA": "00:00:00", "TMIA": "00:00:00"})
                        if ops["Volume"] == 0:
                            for k, v in stats_ops.items():
                                if k in nome or nome in k: ops = v; break
                        dados_setor.append({
                            "Agente": nome, "Volume": ops["Volume"], "TMA": ops["TMA"],
                            "TMIA": ops["TMIA"], "CSAT_Score": csat, "CSAT_Qtd": tot
                        })
                    except: pass
                    done += 1
                    my_bar.progress(int(done/total_ag*100), text=f"{setor}: {done}/{total_ag}")
            my_bar.empty()
            
            df_setor = pd.DataFrame(dados_setor)
            vencedor, df_rank = calcular_rankings_setor(df_setor)
            
            with abas[i]:
                if vencedor:
                    st.success(f"### 👑 Vencedor: {vencedor}")
                    render_top3_cards(df_rank)
                    
                    st.markdown("#### 📊 Tabela Detalhada")
                    st.dataframe(
                        df_rank[['Agente', 'Score_Final', 'Volume', 'TMA', 'TMIA', 'CSAT_Score', 'CSAT_Qtd', 'Rank_TMA', 'Rank_TMIA', 'Rank_CSAT']],
                        column_config={
                            "CSAT_Score": st.column_config.NumberColumn("CSAT %", format="%.6f%%"),
                            "Score_Final": st.column_config.NumberColumn("Score", help="Menor = Melhor")
                        },
                        use_container_width=True, hide_index=True
                    )
                else:
                    st.warning("Dados insuficientes para cálculo do MVP.")
                    if not df_setor.empty: st.dataframe(df_setor)

        status.update(label="Processamento Concluído!", state="complete", expanded=False)
