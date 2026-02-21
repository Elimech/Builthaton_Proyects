import streamlit as st
import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import json
import re
import time

# ==============================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==============================
st.set_page_config(page_title="Inbox Triage", page_icon="📩", layout="centered")

def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Fondo de la aplicación con un gradiente moderno y suave */
        .stApp {
            background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
        }
        
        /* Contenedor principal estilo tarjeta (Glassmorphism) */
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin-top: 2rem;
            margin-bottom: 2rem;
        }

        /* Estilo general de los textos */
        h1, h2, h3 {
            color: #2c3e50 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Botones primarios mejorados */
        div.stButton > button {
            background: linear-gradient(to right, #667eea, #764ba2);
            color: white !important;
            border-radius: 10px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            background: linear-gradient(to right, #764ba2, #667eea);
        }

        /* Separadores más sutiles */
        hr {
            border-top: 1px solid rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_css()

# ==============================
# CONFIGURACIÓN SEGURA
# ==============================
EMAIL = st.secrets["EMAIL_USER"]
PASSWORD = st.secrets["EMAIL_PASS"]
IMAP_SERVER = "imap.gmail.com"

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==============================
# ESTADO INICIAL
# ==============================
if "analizado" not in st.session_state:
    st.session_state["analizado"] = False
if "resultado" not in st.session_state:
    st.session_state["resultado"] = None
if "asuntos" not in st.session_state:
    st.session_state["asuntos"] = []
if "email_ids" not in st.session_state:
    st.session_state["email_ids"] = []
if "labels" not in st.session_state:
    st.session_state["labels"] = []
if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = "ES"
if "last_cluster_lang" not in st.session_state:
    st.session_state["last_cluster_lang"] = None

# ==============================
# CHECKBOX DE IDIOMA
# ==============================
st.write("") 
if st.session_state["ui_lang"] == "EN":
    checkbox_label = "🌎 Show in Spanish? (uncheck = Spanish)"
else:
    checkbox_label = "🌎 ¿Mostrar en Inglés? (marcar = Inglés)"

idioma_checked = st.checkbox(checkbox_label, value=(st.session_state["ui_lang"] == "EN"), key="idioma_toggle")

LANG = "EN" if st.session_state.get("idioma_toggle", False) else "ES"
st.session_state["ui_lang"] = LANG

# ==============================
# TEXTOS Y OPCIONES SEGÚN IDIOMA
# ==============================
if LANG == "EN":
    TITLE = "📩 Inbox Triage Assistant"
    BUTTON_ANALYZE = "Analyze Emails"
    ERROR_CLUSTER = "Less than 3 clusters generated. Please try again."
    ARCHIVE_TEXT = "Archive"
    EMAIL_COUNT = "Emails in cluster:"
    FILTER_LABEL = "Search Filter (choose one):"
    FILTER_OPTIONS = ("Inbox excluding Trash, Spam, and Sent", "Primary Inbox only")
    FILTER_QUERIES = {
        "Inbox excluding Trash, Spam, and Sent": "in:inbox -in:trash -in:spam -in:sent",
        "Primary Inbox only": "category:primary in:inbox"
    }
    NUM_TO_READ_LABEL = "Number of emails to analyze (max 200)"
    NO_SUBJECT = "(No Subject)"
    ERR_INBOX = "Could not access the INBOX folder."
    ERR_GEN_CLUSTERS = "Error generating clusters:"
    ERR_CRIT = "Critical error:"
    TXT_FAILED = "Failed:"
    
    # Textos de la barra de progreso
    PROG_1 = "Connecting to mailbox..."
    PROG_2 = "Fetching emails..."
    PROG_3 = "Parsing email content..."
    PROG_4 = "AI is grouping emails (this may take a few seconds)..."
    PROG_5 = "Analysis complete!"
else:
    TITLE = "📩 Asistente Inteligente de Bandeja"
    BUTTON_ANALYZE = "Analizar correos"
    ERROR_CLUSTER = "Se generaron menos de 3 clusters. Intenta nuevamente."
    ARCHIVE_TEXT = "Archivar"
    EMAIL_COUNT = "Correos en el cluster:"
    FILTER_LABEL = "Filtro de búsqueda (elige uno):"
    FILTER_OPTIONS = ("INBOX excluyendo Papelera, Spam y Enviados", "Solo Principal")
    FILTER_QUERIES = {
        "INBOX excluyendo Papelera, Spam y Enviados": "in:inbox -in:trash -in:spam -in:sent",
        "Solo Principal": "category:primary in:inbox"
    }
    NUM_TO_READ_LABEL = "Número de correos a analizar (máx 200)"
    NO_SUBJECT = "(Sin Asunto)"
    ERR_INBOX = "No se pudo acceder a la carpeta INBOX."
    ERR_GEN_CLUSTERS = "Error al generar clusters:"
    ERR_CRIT = "Error crítico:"
    TXT_FAILED = "Fallidos:"
    
    # Textos de la barra de progreso
    PROG_1 = "Conectando al buzón..."
    PROG_2 = "Buscando correos..."
    PROG_3 = "Procesando asuntos..."
    PROG_4 = "La IA está agrupando los correos (esto puede tardar unos segundos)..."
    PROG_5 = "¡Análisis completado!"

# ==============================
# UI PRINCIPAL
# ==============================
st.markdown(f"<h1 style='text-align: center;'>{TITLE}</h1>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"**{FILTER_LABEL}**")
    filter_option = st.radio("", FILTER_OPTIONS, index=0, label_visibility="collapsed")
with col2:
    num_to_read = st.number_input(NUM_TO_READ_LABEL, min_value=1, max_value=250, value=20, step=1)

st.write("") 

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def decodificar_asunto(header_subject):
    if not header_subject:
        return NO_SUBJECT
    try:
        decoded_parts = decode_header(header_subject)
    except Exception:
        return str(header_subject)
    subject = ""
    for content, encoding in decoded_parts:
        if isinstance(content, bytes):
            try:
                codificacion = encoding if encoding and encoding != 'unknown-8bit' else 'utf-8'
                subject += content.decode(codificacion, errors="replace")
            except Exception:
                subject += content.decode('utf-8', errors="replace")
        else:
            subject += content
    return subject

def _extract_json_from_text(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No se encontró JSON válido en la respuesta." if LANG == "ES" else "No valid JSON found in response.")
    return json.loads(text[start:end+1])

def clusterizar_correos(lista_asuntos):

    MAX_ANALISIS = 200  # 🔥 aumentamos a 200 para usar todos los correos posibles

    if len(lista_asuntos) > MAX_ANALISIS:
        st.warning(f"Se analizarán solo los últimos {MAX_ANALISIS} correos para clustering (por rendimiento).")
    
    asuntos_limitados = lista_asuntos[:MAX_ANALISIS]

    asuntos_texto = "\n".join(
        [f"{i}. {a[:120]}" for i, a in enumerate(asuntos_limitados)]
    )

    if LANG == "EN":
        prompt = f"""
Cluster the following emails into at least 3 meaningful and actionable groups.

Return ONLY valid JSON with this structure:
{{
  "clusters": [
    {{
      "nombre": "Cluster name",
      "descripcion": "Short explanation",
      "indices": [list of email numbers]
    }}
  ]
}}

Emails:
{asuntos_texto}
"""
    else:
        prompt = f"""
Agrupa los siguientes correos en al menos 3 clusters significativos y accionables.

Devuelve SOLO un JSON válido con esta estructura:
{{
  "clusters": [
    {{
      "nombre": "Nombre del cluster",
      "descripcion": "Breve explicación",
      "indices": [lista de números]
    }}
  ]
}}

Correos:
{asuntos_texto}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        contenido = response.text.strip()
        parsed = _extract_json_from_text(contenido)
        return parsed

    except Exception as e:
        st.error(f"Error al generar clusters: {e}")
        return {"clusters": []}

def traducir_clusters(resultado, target_lang="EN"):
    if not resultado or "clusters" not in resultado:
        return resultado
    clusters_traducidos = []
    for c in resultado["clusters"]:
        nombre = c.get("nombre", "")
        descripcion = c.get("descripcion", "")
        try:
            if target_lang == "EN":
                prompt = f"""Translate the following cluster title and description to English.
Title: {nombre}
Description: {descripcion}
Return only a JSON object with keys "nombre" and "descripcion" (in English)."""
            else:
                prompt = f"""Traduce al Español el siguiente título y descripción de cluster.
Título: {nombre}
Descripción: {descripcion}
Devuelve solo un JSON con claves "nombre" y "descripcion" (en español)."""
            resp = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            parsed = json.loads(resp.text.strip())
            clusters_traducidos.append({
                "nombre": parsed.get("nombre", nombre),
                "descripcion": parsed.get("descripcion", descripcion),
                "indices": c.get("indices", [])
            })
        except Exception:
            clusters_traducidos.append(c)
    return {"clusters": clusters_traducidos}

def archivar_cluster(indices):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("INBOX")
        email_uids = st.session_state["email_ids"]
        archived, failed = [], []
        for i in indices:
            if 0 <= i < len(email_uids):
                uid_str = email_uids[i]
                typ, response = mail.uid('STORE', uid_str, '+FLAGS', '(\\Deleted)')
                if typ == "OK":
                    archived.append(uid_str)
                else:
                    failed.append((uid_str, response))
        mail.expunge()
        mail.logout()
        return archived, failed
    except Exception as e:
        return [], [(None, str(e))]

# ==============================
# ACCIÓN: ANALIZAR CORREOS
# ==============================
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    analizar_btn = st.button(BUTTON_ANALYZE, use_container_width=True)

if analizar_btn:
    # --- UI DE LA BARRA DE PROGRESO ---
    progress_text = st.empty()
    progress_bar = st.progress(0)

    try:
        # Paso 1: Conectando
        progress_text.markdown(f"⏳ **{PROG_1}**")
        progress_bar.progress(10)
        
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        status, _ = mail.select("INBOX", readonly=True)
        
        if status != "OK":
            st.error(ERR_INBOX)
            mail.logout()
            progress_text.empty()
            progress_bar.empty()
            st.stop()

        # Paso 2: Buscando correos
        progress_text.markdown(f"🔍 **{PROG_2}**")
        progress_bar.progress(30)
        
        gm_query = FILTER_QUERIES[filter_option]
        typ, data = mail.uid('search', None, 'X-GM-RAW', f'"{gm_query}"')
        asuntos, email_uids, labels_list = [], [], []

        if typ == "OK" and data and data[0]:
            all_uids = data[0].split()
            recent_uids = all_uids[-int(num_to_read):]

            # Paso 3: Descargando y procesando contenido
            progress_text.markdown(f"📥 **{PROG_3}**")
            progress_bar.progress(50)
            
            uid_range = ",".join([uid.decode() if isinstance(uid, bytes) else str(uid) for uid in recent_uids])
            res, msg_data = mail.uid('fetch', uid_range, '(X-GM-LABELS BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
            
            if res == "OK" and msg_data:
                for i in range(0, len(msg_data), 2):
                    if not isinstance(msg_data[i], tuple):
                        continue
                    meta_bytes = msg_data[i][0]
                    header_bytes = msg_data[i][1]
                    meta_str = meta_bytes.decode(errors="replace")
                    labels_raw = ""
                    subj_raw = NO_SUBJECT
                    labels_match = re.search(r'X-GM-LABELS\s+\((.*?)\)', meta_str)
                    if labels_match:
                        labels_raw = labels_match.group(1).strip()
                    try:
                        msg = email.message_from_bytes(header_bytes)
                        subj_raw = msg.get('Subject', NO_SUBJECT)
                    except:
                        subj_raw = NO_SUBJECT
                    asuntos.append(decodificar_asunto(subj_raw))
                    labels_list.append(labels_raw)

                email_uids = [uid.decode() if isinstance(uid, bytes) else str(uid) for uid in recent_uids]

            st.session_state["email_ids"] = email_uids
            st.session_state["asuntos"] = asuntos
            st.session_state["labels"] = labels_list

            # Paso 4: Llamada a la IA para agrupar
            progress_text.markdown(f"🤖 **{PROG_4}**")
            progress_bar.progress(70)
            
            clusters = clusterizar_correos(asuntos)
            st.session_state["resultado"] = clusters
            st.session_state["analizado"] = True
            st.session_state["last_cluster_lang"] = LANG

            # Paso 5: Completado
            progress_text.markdown(f"✅ **{PROG_5}**")
            progress_bar.progress(100)
            time.sleep(0.8) # Pausa breve para que el usuario vea que llegó al 100%
            
            # Limpiamos la barra de progreso para dejar limpia la UI
            progress_text.empty()
            progress_bar.empty()

            if LANG == "EN":
                st.success(f"Analyzed {len(asuntos)} emails (filter: {gm_query}).")
            else:
                st.success(f"Se analizaron {len(asuntos)} correos (filtro: {gm_query}).")
        else:
            progress_text.empty()
            progress_bar.empty()
            if LANG == "EN":
                st.warning(f"No messages found for query: {gm_query}")
            else:
                st.warning(f"No se encontraron mensajes con la consulta: {gm_query}")

        mail.logout()
    except imaplib.IMAP4.error as imap_err:
        progress_text.empty()
        progress_bar.empty()
        st.error(f"IMAP Error: {imap_err}")
    except Exception as e:
        progress_text.empty()
        progress_bar.empty()
        st.error(f"{ERR_CRIT} {e}")

# ==============================
# CAMBIO DE IDIOMA DINÁMICO PARA CLUSTERS
# ==============================
if st.session_state["analizado"] and st.session_state["resultado"]:
    if st.session_state.get("last_cluster_lang") != LANG:
        target = "EN" if LANG == "EN" else "ES"
        st.session_state["resultado"] = traducir_clusters(st.session_state["resultado"], target_lang=target)
        st.session_state["last_cluster_lang"] = LANG

# ==============================
# INTERFAZ (RESULTADOS + ACCIONES)
# ==============================
if st.session_state["analizado"] and st.session_state["resultado"]:
    st.divider()
    resultado = st.session_state["resultado"]
    asuntos = st.session_state["asuntos"]

    if "clusters" not in resultado or not resultado["clusters"]:
        st.warning(ERROR_CLUSTER)
    else:
        for idx, cluster in enumerate(resultado["clusters"]):
            nombre = cluster.get("nombre", f"Cluster {idx}")
            descripcion = cluster.get("descripcion", "")
            indices = cluster.get("indices", [])

            with st.expander(f"📁 **{nombre}** ({len(indices)} correos)", expanded=True):
                st.write(f"*{descripcion}*")
                st.write(f"📊 **{EMAIL_COUNT}** {len(indices)}")

                for i in indices:
                    try:
                        ii = int(i)
                    except:
                        continue
                    if 0 <= ii < len(asuntos):
                        st.markdown(f"&nbsp;&nbsp;🔹 {asuntos[ii]}")

                if st.button(f"📥 {ARCHIVE_TEXT} '{nombre}'", key=f"btn_archivar_{idx}"):
                    safe_indices = []
                    for it in indices:
                        try:
                            ii = int(it)
                            if 0 <= ii < len(st.session_state["email_ids"]):
                                safe_indices.append(ii)
                        except:
                            continue

                    archived, failed = archivar_cluster(safe_indices)
                    if archived:
                        st.success(f"{ARCHIVE_TEXT} (UID): {archived}")
                        for ii in sorted(safe_indices, reverse=True):
                            del st.session_state["asuntos"][ii]
                            del st.session_state["email_ids"][ii]
                            del st.session_state["labels"][ii]

                        if st.session_state["resultado"] and "clusters" in st.session_state["resultado"]:
                            nuevos_clusters = []
                            for cl in st.session_state["resultado"]["clusters"]:
                                nuevos_indices = [i for i in cl["indices"] if i not in safe_indices]
                                if nuevos_indices:
                                    cl["indices"] = nuevos_indices
                                    nuevos_clusters.append(cl)
                            st.session_state["resultado"]["clusters"] = nuevos_clusters
                        st.rerun()

                    if failed:
                        st.error(f"{TXT_FAILED} {failed}")