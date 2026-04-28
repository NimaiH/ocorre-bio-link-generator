import streamlit as st
import os
import base64
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# --- 1. FUNÇÕES DE APOIO ---

def extrair_cores(imagem_file, n_cores=5):
    """ Extrai as cores da foto para criar a paleta. """
    img = Image.open(imagem_file).convert('RGB')
    img.thumbnail((100, 100))
    ar_img = np.array(img).reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_cores, random_state=42, n_init=10)
    kmeans.fit(ar_img)
    cores = sorted(kmeans.cluster_centers_.astype(int), key=lambda x: sum(x))
    return [f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}' for c in cores]

def detectar_icone(titulo):
    """ Coloca ícones automaticamente nos botões. """
    t = titulo.lower()
    if 'whatsapp' in t: return '<i class="fab fa-whatsapp"></i>'
    if 'instagram' in t: return '<i class="fab fa-instagram"></i>'
    if 'ifood' in t or 'cardápio' in t: return '<i class="fas fa-utensils"></i>'
    if 'email' in t or 'e-mail' in t: return '<i class="far fa-envelope"></i>'
    if 'maps' in t or 'chegar' in t: return '<i class="fas fa-map-marker-alt"></i>'
    return '<i class="fas fa-link"></i>'

def calcular_contraste(hex_color):
    """ Define se a borda do botão no site será clara ou escura. """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminosidade = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "rgba(0,0,0,0.2)" if luminosidade > 0.5 else "rgba(255,255,255,0.2)"

# --- 2. CONFIGURAÇÃO DA INTERFACE ---

st.set_page_config(page_title="O Corre - Bio Link Generator", layout="wide")

if 'fundo' not in st.session_state: st.session_state.fundo = "#1a1a1a"
if 'texto' not in st.session_state: st.session_state.texto = "#ffffff"
if 'hover' not in st.session_state: st.session_state.hover = "#ffd700"

with st.sidebar:
    st.header("⚙️ Configurações")
    nome = st.text_input("Nome do Negócio", "O Corre Inicial")
    bio = st.text_area("Bio/Descrição", "Digitalizando microempreendedores")
    foto = st.file_uploader("📸 Foto de Perfil", type=['png', 'jpg', 'jpeg'])

    cores_vivas = []
    if foto:
        try:
            cores_vivas = extrair_cores(foto)
        except: pass

    st.subheader("🎨 Estilo e Cores")

    def criar_bloco_cor(label, key_session):
        st.write(f"**{label}**")
        if cores_vivas:
            cols = st.columns(len(cores_vivas))
            for idx, cor in enumerate(cores_vivas):
                if cols[idx].button("🎨", key=f"btn_{key_session}_{idx}", help=f"Aplicar {cor}"):
                    st.session_state[key_session] = cor
                    st.rerun()
        return st.color_picker(f"Seletor {label}", st.session_state[key_session], key=f"picker_{key_session}")

    cor_fundo = criar_bloco_cor("Fundo", "fundo")
    st.divider()
    cor_texto = criar_bloco_cor("Texto", "texto")
    st.divider()
    cor_hover = criar_bloco_cor("Hover", "hover")
    cor_borda = calcular_contraste(cor_fundo)

    st.subheader("🔗 Links")
    links_final = []
    for i in range(1, 5):
        t = st.text_input(f"Título {i}", key=f"t{i}")
        u = st.text_input(f"URL {i}", key=f"u{i}")
        if t and u: links_final.append({"titulo": t, "url": u})

# --- 3. GERAÇÃO DO SITE ---

def gerar_html(links):
    botoes_html = "".join([f'<a href="{l["url"]}" class="btn" target="_blank">{detectar_icone(l["titulo"])} {l["titulo"]}</a>' for l in links])
    perfil_html = ""
    if foto:
        base64_foto = base64.b64encode(foto.getvalue()).decode()
        perfil_html = f'<img src="data:image/png;base64,{base64_foto}" class="profile-img">'

    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <style>
            body {{ background: {cor_fundo}; color: {cor_texto}; margin: 0; padding: 40px 20px; font-family: sans-serif; text-align: center; }}
            .container {{ max-width: 450px; margin: auto; }}
            .profile-img {{ width:120px; height:120px; border-radius:50%; border: 3px solid {cor_texto}; object-fit:cover; margin-bottom: 20px; }}
            .btn {{ display: block; background: rgba(255,255,255,0.05); border: 2px solid {cor_borda}; color: {cor_texto}; padding: 16px; margin: 12px 0; text-decoration: none; border-radius: 12px; font-weight: bold; transition: 0.3s; }}
            .btn:hover {{ background: {cor_hover}; color: #000; transform: translateY(-3px); }}
        </style>
    </head>
    <body><div class="container">{perfil_html}<h1>{nome}</h1><p>{bio}</p>{botoes_html}</div></body>
    </html>
    """

# --- 4. EXECUÇÃO E EXPORTAÇÃO ---

st.title("🚀 Dashboard O Corre")

nome_cliente = st.text_input("Nome do arquivo para exportar", "index")

if st.button("💾 Exportar para a pasta Exports"):
    caminho_arquivo = os.path.join("exports", f"{nome_cliente}.html")
    if not os.path.exists("exports"): os.makedirs("exports")
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(gerar_html(links_final))
    st.success(f"✅ Arquivo salvo em: **{caminho_arquivo}**")

st.divider()
# A LINHA QUE FALTAVA PARA O PREVIEW APARECER:
st.components.v1.html(gerar_html(links_final), height=600, scrolling=True)
