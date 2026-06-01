import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ECOM ERP — Système de Gestion",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS (Professional Dark/Light Theme)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main .block-container {
    padding: 1.5rem 2rem;
    background: #f8f9fa;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1f3a 0%, #0d1128 100%) !important;
    border-right: 1px solid #2d3561;
}

[data-testid="stSidebar"] * {
    color: #c8cfe8 !important;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* Metric Cards */
.metric-card-blue { background: linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #42a5f5 100%); border-radius: 16px; padding: 1.4rem 1.6rem; color: white; box-shadow: 0 8px 32px rgba(21,101,192,0.25); border: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; }
.metric-card-purple { background: linear-gradient(135deg, #6a1b9a 0%, #8e24aa 50%, #ba68c8 100%); border-radius: 16px; padding: 1.4rem 1.6rem; color: white; box-shadow: 0 8px 32px rgba(106,27,154,0.25); border: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; }
.metric-card-green { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #66bb6a 100%); border-radius: 16px; padding: 1.4rem 1.6rem; color: white; box-shadow: 0 8px 32px rgba(27,94,32,0.25); border: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; }
.metric-card-red { background: linear-gradient(135deg, #b71c1c 0%, #c62828 50%, #ef5350 100%); border-radius: 16px; padding: 1.4rem 1.6rem; color: white; box-shadow: 0 8px 32px rgba(183,28,28,0.25); border: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; }
.metric-card-orange { background: linear-gradient(135deg, #e65100 0%, #f57c00 50%, #ffb74d 100%); border-radius: 16px; padding: 1.4rem 1.6rem; color: white; box-shadow: 0 8px 32px rgba(230,81,0,0.25); border: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; }
.metric-card-teal { background: linear-gradient(135deg, #004d40 0%, #00695c 50%, #4db6ac 100%); border-radius: 16px; padding: 1.4rem 1.6rem; color: white; box-shadow: 0 8px 32px rgba(0,77,64,0.25); border: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; }

.metric-icon { font-size: 2rem; float: right; opacity: 0.85; }
.metric-label { font-size: 0.85rem; font-weight: 600; opacity: 0.9; margin-bottom: 0.2rem; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-value { font-size: 1.8rem; font-weight: 800; line-height: 1.1; }
.metric-sub { font-size: 0.75rem; opacity: 0.8; margin-top: 0.3rem; }

.section-header {
    background: linear-gradient(90deg, #1a1f3a, #2d3561); color: white;
    padding: 0.8rem 1.4rem; border-radius: 12px; font-size: 1.1rem; font-weight: 600;
    margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem;
}

[data-testid="stForm"] { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(0,0,0,0.05); border: 1px solid #e8eaf0; }
.page-title { font-size: 1.8rem; font-weight: 800; color: #1a1f3a; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 0.9rem; color: #7b89a8; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────
DB_PATH = "business_system.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        security_question TEXT,
        security_answer TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sku TEXT,
        purchase_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        initial_stock INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        selling_price REAL NOT NULL,
        purchase_price REAL NOT NULL,
        delivery_cost REAL DEFAULT 0,
        ads_share REAL DEFAULT 0,
        status TEXT DEFAULT 'Livré',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )""")
    
    c.execute("SELECT * FROM users WHERE role='Admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, email, password, role, security_question, security_answer) VALUES (?,?,?,?,?,?)",
                  ("Administrateur", "admin@ecom.com", "admin123", "Admin", "Ville preferee", "Meknes"))
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────
def load_products():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM products ORDER BY id DESC", conn)
    conn.close()
    return df

def load_expenses():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def load_sales():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM sales ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def add_product(name, sku, purchase_price, selling_price, stock):
    conn = get_conn()
    conn.execute("INSERT INTO products (name,sku,purchase_price,selling_price,stock,initial_stock) VALUES (?,?,?,?,?,?)",
                 (name, sku, purchase_price, selling_price, stock, stock))
    conn.commit(); conn.close()

def add_sale(dt, product_id, product_name, quantity, selling_price, purchase_price, delivery_cost, ads_share, status="Livré"):
    conn = get_conn()
    conn.execute("INSERT INTO sales (date,product_id,product_name,quantity,selling_price,purchase_price,delivery_cost,ads_share,status) VALUES (?,?,?,?,?,?,?,?,?)",
                 (dt, product_id, product_name, quantity, selling_price, purchase_price, delivery_cost, ads_share, status))
    if status == "Livré":
        conn.execute("UPDATE products SET stock = stock - ? WHERE id=?", (quantity, product_id))
    conn.commit(); conn.close()

# ─────────────────────────────────────────
# DATE FILTERING HELPER
# ─────────────────────────────────────────
def filter_dataframe_by_period(df, period, custom_start=None, custom_end=None):
    if df.empty or 'date' not in df.columns:
        return df
    df_copy = df.copy()
    df_copy['dt_parsed'] = pd.to_datetime(df_copy['date'])
    today = pd.Timestamp(date.today())
    
    if period == "Ce Mois":
        df_copy = df_copy[(df_copy['dt_parsed'].dt.month == today.month) & (df_copy['dt_parsed'].dt.year == today.year)]
    elif period == "Ce Trimestre":
        current_quarter = (today.month - 1) // 3 + 1
        df_copy = df_copy[((df_copy['dt_parsed'].dt.month - 1) // 3 + 1 == current_quarter) & (df_copy['dt_parsed'].dt.year == today.year)]
    elif period == "Ce Semestre":
        semester = 1 if today.month <= 6 else 2
        if semester == 1:
            df_copy = df_copy[(df_copy['dt_parsed'].dt.month <= 6) & (df_copy['dt_parsed'].dt.year == today.year)]
        else:
            df_copy = df_copy[(df_copy['dt_parsed'].dt.month > 6) & (df_copy['dt_parsed'].dt.year == today.year)]
    elif period == "Cette Année":
        df_copy = df_copy[df_copy['dt_parsed'].dt.year == today.year]
    elif period == "Période Personnalisée" and custom_start and custom_end:
        df_copy = df_copy[(df_copy['dt_parsed'].dt.date >= custom_start) & (df_copy['dt_parsed'].dt.date <= custom_end)]
        
    return df_copy.drop(columns=['dt_parsed'])

# ─────────────────────────────────────────
# UNIVERSAL PDF GENERATOR
# ─────────────────────────────────────────
def generate_master_pdf(period_title, metrics, df_p, df_e, df_s, inc_kpi, inc_stock, inc_exp, inc_sales):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.2*cm, rightMargin=1.2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T1', fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor("#1a1f3a"), alignment=TA_CENTER, spaceAfter=4)
    p_style = ParagraphStyle('P1', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=15)
    h_style = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor("#1565c0"), spaceBefore=12, spaceAfter=6)

    elements.append(Paragraph("RAPPORT DE PERFORMANCE FINANCIERE - ECOM ERP", title_style))
    elements.append(Paragraph(f"Période: {period_title} | Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M')}", p_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1f3a"), spaceAfter=15))

    if inc_kpi:
        elements.append(Paragraph("I. Indicateurs Clés de Performance (KPIs)", h_style))
        kpi_data = [
            ['Indicateur', 'Valeur (DH)', 'Description'],
            ['Chiffre d\'Affaires Gross', f"{metrics['total_sales']:.2f} DH", 'Total des ventes brutes'],
            ['Coût des Marchandises (COGS)', f"{metrics['cogs']:.2f} DH", 'Coût total d\'achat du stock vendu'],
            ['Dépenses Globales', f"{metrics['total_expenses']:.2f} DH", 'Charges fixes + Marketing + Logistique'],
            ['Bénéfice Net', f"{metrics['net_profit']:.2f} DH", f"Marge nette calculée: {metrics['margin']:.1f}%"]
        ]
        t_kpi = Table(kpi_data, colWidths=[6*cm, 4.5*cm, 7.5*cm])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1f3a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d0d5e8")),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#2e7d32")),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 0.5*cm))

    if inc_stock and not df_p.empty:
        elements.append(Paragraph("II. État Réel des Stocks & Inventaire", h_style))
        stock_data = [['ID', 'Nom du Produit', 'SKU', 'Prix d\'Achat', 'Stock Dispo', 'Valeur Stock']]
        for _, r in df_p.iterrows():
            stock_data.append([str(r['id']), r['name'], str(r['sku']), f"{r['purchase_price']:.2f}", str(r['stock']), f"{(r['stock']*r['purchase_price']):.2f}"])
        t_stock = Table(stock_data, colWidths=[1*cm, 5.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4*cm])
        t_stock.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2d3561")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e8eaf0")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_stock)
        elements.append(Spacer(1, 0.5*cm))

    if inc_exp and not df_e.empty:
        elements.append(Paragraph("III. Registre Chronologique des Dépenses", h_style))
        exp_data = [['Date', 'Catégorie', 'Montant', 'Description']]
        for _, r in df_e.iterrows():
            exp_data.append([r['date'], r['category'], f"{r['amount']:.2f} DH", str(r['description'])])
        t_exp = Table(exp_data, colWidths=[3*cm, 4.5*cm, 3*cm, 7.5*cm])
        t_exp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#b71c1c")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e8eaf0")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_exp)
        elements.append(Spacer(1, 0.5*cm))

    if inc_sales and not df_s.empty:
        elements.append(Paragraph("IV. Journal des Commandes et Ventes", h_style))
        sales_data = [['ID', 'Date', 'Produit', 'Qté', 'Prix Vente', 'Statut']]
        for _, r in df_s.iterrows():
            sales_data.append([str(r['id']), r['date'], r['product_name'], str(r['quantity']), f"{r['selling_price']:.2f}", r['status']])
        t_sales = Table(sales_data, colWidths=[1*cm, 2.5*cm, 6.5*cm, 1.5*cm, 3*cm, 3.5*cm])
        t_sales.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b5e20")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e8eaf0")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_sales)

    doc.build(elements)
    buf.seek(0)
    return buf

# ─────────────────────────────────────────
# AUTHENTICATION SYSTEM
# ─────────────────────────────────────────
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #1a1f3a;'>🔒 Connexion Sécurisée - ECOM ERP</h2>", unsafe_allow_html=True)
    
    auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔑 Se connecter", "📝 Créer un compte Collaborateur", "🔄 Mot de passe oublié"])
    
    with auth_tab1:
        with st.form("login_form"):
            lemail = st.text_input("Identifiant / Email")
            lpass = st.text_input("Mot de passe", type="password")
            btn_login = st.form_submit_button("Accéder au système", use_container_width=True)
            if btn_login:
                conn = get_conn()
                res = conn.execute("SELECT username, role FROM users WHERE email=? AND password=?", (lemail, lpass)).fetchone()
                conn.close()
                if res:
                    st.session_state.authenticated = True
                    st.session_state.username = res[0]
                    st.session_state.user_role = res[1]
                    st.success(f"Ravi de vous revoir, {res[0]} !")
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect.")
                    
    with auth_tab2:
        with st.form("register_form"):
            rname = st.text_input("Nom complet de l'employé")
            remail = st.text_input("Adresse Email")
            rpass = st.text_input("Mot de passe temporaire", type="password")
            rrole = st.selectbox("Niveau d'accès / Rôle", ["Admin", "Assistant"])
            r_q = st.selectbox("Question de sécurité (Récupération)", ["Ville préférée", "Première école", "Nom du premier animal"])
            r_a = st.text_input("Réponse à la question de sécurité")
            btn_reg = st.form_submit_button("Enregistrer le compte", use_container_width=True)
            if btn_reg:
                if rname and remail and rpass and r_a:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO users (username, email, password, role, security_question, security_answer) VALUES (?,?,?,?,?,?)",
                                     (rname, remail, rpass, rrole, r_q, r_a))
                        conn.commit()
                        conn.close()
                        st.success("Compte collaborateur créé avec succès !")
                    except sqlite3.IntegrityError:
                        st.error("Cet email est déjà attribué à un autre utilisateur.")
                else:
                    st.warning("Veuillez remplir tous les champs obligatoires.")
                    
    with auth_tab3:
        with st.form("recover_form"):
            femail = st.text_input("Saisissez votre adresse email")
            fq = st.selectbox("Votre question de sécurité configurée", ["Ville préférée", "Première école", "Nom du premier animal"])
            fa = st.text_input("Votre réponse secrète")
            btn_rec = st.form_submit_button("Vérifier et afficher le mot de passe", use_container_width=True)
            if btn_rec:
                conn = get_conn()
                user = conn.execute("SELECT password FROM users WHERE email=? AND security_question=? AND security_answer=?", (femail, fq, fa)).fetchone()
                conn.close()
                if user:
                    st.info(f"Votre mot de passe secret est : **{user[0]}**")
                else:
                    st.error("Données d'authentification ou réponse de sécurité introuvables.")
    st.stop()

# ─────────────────────────────────────────
# SIDEBAR NAVIGATION (ROLE-BASED)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0;">
        <div style="font-size:2.5rem;">🛒</div>
        <div style="font-weight:800; font-size:1.4rem; color:white;">ECOM ERP</div>
        <div style="font-size:0.8rem; color:#7b89a8;">Session : {st.session_state.username} ({st.session_state.user_role})</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.user_role == "Admin":
        nav_options = ["📈 Tableau de bord", "📦 Gestion du stock", "💸 Dépenses globales", "🛍️ Commandes & Ventes"]
    else:
        nav_options = ["🛍️ Commandes & Ventes"]

    page = st.radio("Navigation principale", nav_options, label_visibility="collapsed")
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("### 📅 Filtrage de la Période")
    global_period = st.selectbox("Choisir l'intervalle", ["Toutes les données", "Ce Mois", "Ce Trimestre", "Ce Semestre", "Cette Année", "Période Personnalisée"])
    
    c_start, c_end = None, None
    if global_period == "Période Personnalisée":
        c_start = st.date_input("Date de début", value=date.today())
        c_end = st.date_input("Date de fin", value=date.today())

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ─────────────────────────────────────────
# METRICS COMPUTE WITH FILTERS
# ─────────────────────────────────────────
def compute_metrics(df_s_filtered, df_e_filtered, df_p_all):
    total_sales = (df_s_filtered['quantity'] * df_s_filtered['selling_price']).sum() if not df_s_filtered.empty else 0
    cogs = (df_s_filtered['quantity'] * df_s_filtered['purchase_price']).sum() if not df_s_filtered.empty else 0
    static_expenses = df_e_filtered['amount'].sum() if not df_e_filtered.empty else 0
    delivery_costs = df_s_filtered['delivery_cost'].sum() if not df_s_filtered.empty else 0
    ads_share = (df_s_filtered['quantity'] * df_s_filtered['ads_share']).sum() if not df_s_filtered.empty else 0
    
    total_expenses = static_expenses + delivery_costs + ads_share
    net_profit = total_sales - cogs - total_expenses
    margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
    capital = (df_p_all['stock'] * df_p_all['purchase_price']).sum() if not df_p_all.empty else 0
    
    return {
        "total_sales": total_sales, "cogs": cogs, "static_expenses": static_expenses,
        "delivery_costs": delivery_costs, "ads_share": ads_share,
        "total_expenses": total_expenses, "net_profit": net_profit,
        "margin": margin, "capital": capital,
        "n_products": len(df_p_all), "n_sales": len(df_s_filtered)
    }

# Load Data
raw_sales = load_sales()
raw_expenses = load_expenses()
raw_products = load_products()

# Apply Filters
df_sales = filter_dataframe_by_period(raw_sales, global_period, c_start, c_end)
df_expenses = filter_dataframe_by_period(raw_expenses, global_period, c_start, c_end)
m = compute_metrics(df_sales, df_expenses, raw_products)

# ═══════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════
if page == "📈 Tableau de bord":
    st.markdown('<div class="page-title">📈 Dashboard Analytique & Financier</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Vue d\'ensemble de vos performances commerciales pour la période : <b>{global_period}</b></div>', unsafe_allow_html=True)

    # Metrics Row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card-blue"><div class="metric-icon">🛒</div><div class="metric-label">Ventes Brutes</div><div class="metric-value">{m['total_sales']:,.2f} DH</div><div class="metric-sub">{m['n_sales']} Commandes validées</div></div>""", unsafe_allow_html=True)
    with col2:
        profit_class = "metric-card-green" if m['net_profit'] >= 0 else "metric-card-red"
        st.markdown(f"""<div class="{profit_class}"><div class="metric-icon">📊</div><div class="metric-label">Bénéfice Net Réel</div><div class="metric-value">{m['net_profit']:,.2f} DH</div><div class="metric-sub">Marge nette globale : {m['margin']:.1f}%</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card-teal"><div class="metric-icon">🏭</div><div class="metric-label">Valeur du Stock Actuel</div><div class="metric-value">{m['capital']:,.2f} DH</div><div class="metric-sub">{m['n_products']} Références produits</div></div>""", unsafe_allow_html=True)

    # Metrics Row 2
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"""<div class="metric-card-red"><div class="metric-icon">💸</div><div class="metric-label">Dépenses Globales</div><div class="metric-value">{m['total_expenses']:,.2f} DH</div><div class="metric-sub">Fixes + Logistique + Marketing</div></div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class="metric-card-orange"><div class="metric-icon">📦</div><div class="metric-label">Coût des Marchandises (COGS)</div><div class="metric-value">{m['cogs']:,.2f} DH</div><div class="metric-sub">Prix d'achat net × Quantités vendues</div></div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""<div class="metric-card-purple"><div class="metric-icon">📊</div><div class="metric-label">Marge Brute</div><div class="metric-value">{(m['total_sales']-m['cogs']):,.2f} DH</div><div class="metric-sub">Ventes directes minorées du COGS</div></div>""", unsafe_allow_html=True)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">📈 Évolution Chronologique du Chiffre d\'Affaires</div>', unsafe_allow_html=True)
        if not df_sales.empty:
            daily = df_sales.copy()
            daily['revenue'] = daily['quantity'] * daily['selling_price']
            daily_agg = daily.groupby('date').agg(revenue=('revenue','sum')).reset_index().sort_values('date')
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily_agg['date'], y=daily_agg['revenue'], name='Revenue (DH)', marker_color='#1976d2'))
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=260, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune transaction enregistrée sur cette période pour générer le graphique.")
            
    with c2:
        st.markdown('<div class="section-header">📊 Répartition Analytique des Dépenses</div>', unsafe_allow_html=True)
        if not df_expenses.empty:
            cat_exp = df_expenses.groupby('category')['amount'].sum().reset_index()
            fig2 = px.pie(cat_exp, names='category', values='amount', hole=0.35)
            fig2.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucune dépense fixe enregistrée sur cette période.")

    # PDF Exporter
    st.markdown('<div class="section-header">⚙️ Centre de Génération de Rapports Comptables PDF</div>', unsafe_allow_html=True)
    with st.expander("Configurer les modules à exporter dans le document PDF"):
        c_kpi = st.checkbox("Inclure le résumé des Indicateurs Financiers (KPIs)", value=True)
        c_stock = st.checkbox("Inclure l'état d'inventaire du Stock Actuel", value=True)
        c_exp = st.checkbox("Inclure le registre des charges et dépenses", value=True)
        c_sales = st.checkbox("Inclure le journal complet des ventes", value=True)
        
        master_pdf_buf = generate_master_pdf(global_period, m, raw_products, df_expenses, df_sales, c_kpi, c_stock, c_exp, c_sales)
        st.download_button(
            label="⬇️ Télécharger le rapport PDF Personnalisé",
            data=master_pdf_buf,
            file_name=f"Rapport_Comptable_{global_period}_{date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ═══════════════════════════════════════════════════════════
# PAGE: INVENTORY
# ═══════════════════════════════════════════════════════════
elif page == "📦 Gestion du stock":
    st.markdown('<div class="page-title">📦 Gestion des Stocks & Inventaire Comptable</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Suivi permanent des flux d\'entrée, de sortie et valorisation du stock disponible</div>', unsafe_allow_html=True)
    
    if raw_products.empty:
        st.info("L'inventaire est actuellement vide.")
    else:
        df_acc = raw_products.copy()
        df_acc['Sorties (Ventes)'] = df_acc['initial_stock'] - df_acc['stock']
        df_acc['Valeur Stock (DH)'] = df_acc['stock'] * df_acc['purchase_price']
        
        df_acc.columns = ['ID', 'Nom Produit', 'SKU', 'Prix d\'Achat (DH)', 'Prix de Vente (DH)', 'Stock Restant', 'Stock Initial', 'Date Création', 'Sorties (Ventes)', 'Valeur Stock (DH)']
        st.dataframe(df_acc[['ID', 'Nom Produit', 'SKU', 'Stock Initial', 'Sorties (Ventes)', 'Stock Restant', 'Prix d\'Achat (DH)', 'Valeur Stock (DH)']], use_container_width=True, hide_index=True)

    with st.form("add_product_form"):
        st.markdown("**➕ Réceptionner un nouveau produit / Approvisionnement**")
        colp1, colp2 = st.columns(2)
        with colp1:
            name_p = st.text_input("Désignation / Nom du produit")
            pur_p = st.number_input("Prix d'achat unitaire (DH)", min_value=0.0)
        with colp2:
            sku_p = st.text_input("Code Unique / SKU")
            stk_p = st.number_input("Quantité reçue (Unités)", min_value=1, step=1)
        sel_p = st.number_input("Prix de vente ciblé (DH)", min_value=0.0)
        
        if st.form_submit_button("Injecter et Sauvegarder dans la base de données"):
            if name_p:
                add_product(name_p, sku_p, pur_p, sel_p, stk_p)
                st.success("Produit enregistré et comptabilisé avec succès dans la base SQL !")
                st.rerun()

# ═══════════════════════════════════════════════════════════
# PAGE: EXPENSES (BULK EXCEL)
# ═══════════════════════════════════════════════════════════
elif page == "💸 Dépenses globales":
    st.markdown('<div class="page-title">💸 Registre de Saisie des Dépenses (Mode Tableur)</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Cliquez sur le bouton (+) en bas du tableau pour ajouter plusieurs lignes à la fois, puis sauvegardez globalement.</div>', unsafe_allow_html=True)
    
    CATEGORIES = ["Ads Meta/Facebook", "Ads TikTok", "Sourcing / Achat Stock", "Emballage & Packaging", "Perte Logistique", "Frais Fixes / Locaux", "Autre Charge"]
    
    if 'expense_buffer' not in st.session_state:
        st.session_state.expense_buffer = pd.DataFrame([
            {"Date": str(date.today()), "Category": "Ads Meta/Facebook", "Amount": 0.0, "Description": ""}
        ])
        
    edited_df = st.data_editor(
        st.session_state.expense_buffer,
        num_rows="dynamic",
        column_config={
            "Date": st.column_config.DateColumn("Date d'effet", required=True),
            "Category": st.column_config.SelectboxColumn("Type de Charge", options=CATEGORIES, required=True),
            "Amount": st.column_config.NumberColumn("Montant Engagé (DH)", min_value=0.0, required=True, format="%.2f DH"),
            "Description": st.column_config.TextColumn("Note descriptive / Justificatif")
        },
        use_container_width=True,
        key="bulk_expense_editor"
    )
    
    if st.button("💾 Valider et Enregistrer définitivement ces lignes"):
        conn = get_conn()
        saved_count = 0
        for _, row in edited_df.iterrows():
            if row['Amount'] > 0:
                conn.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?,?,?,?)",
                             (str(row['Date']), row['Category'], float(row['Amount']), row['Description']))
                saved_count += 1
        conn.commit()
        conn.close()
        if saved_count > 0:
            st.success(f"Opération réussie : {saved_count} ligne(s) de dépenses enregistrée(s) avec succès !")
            st.session_state.expense_buffer = pd.DataFrame([{"Date": str(date.today()), "Category": "Ads Meta/Facebook", "Amount": 0.0, "Description": ""}])
            st.rerun()
        else:
            st.warning("Veuillez remplir des montants supérieurs à 0 DH avant de soumettre.")

    st.markdown("---")
    st.markdown("### 📋 Historique comptable des charges fixes sur la période sélectionnée")
    st.dataframe(df_expenses, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════
# PAGE: ORDERS & SALES
# ═══════════════════════════════════════════════════════════
elif page == "🛍️ Commandes & Ventes":
    st.markdown('<div class="page-title">🛍️ Traitement des Commandes & Logistique</div>', unsafe_allow_html=True)
    
    if st.session_state.user_role == "Assistant":
        st.info("ℹ️ Mode Collaborateur Actif : Les tableaux de rentabilité globale et de coûts publicitaires globaux sont masqués pour préserver la confidentialité de la stratégie d'entreprise.")

    tab1, tab2 = st.tabs(["➕ Enregistrer une nouvelle commande", "📋 Liste des commandes & Changement de statut"])
    
    with tab1:
        if raw_products.empty:
            st.warning("Aucun produit disponible en stock pour enregistrer une vente.")
        else:
            with st.form("sale_entry"):
                s_dt = st.date_input("Date de la transaction", value=date.today())
                prod_map = {f"[{r['id']}] {r['name']} (Dispo: {r['stock']})": r['id'] for _, r in raw_products.iterrows() if r['stock'] > 0}
                
                if prod_map:
                    sel_p_label = st.selectbox("Sélectionner l'article vendu", list(prod_map.keys()))
                    chosen_p_id = prod_map[sel_p_label]
                    p_row = raw_products[raw_products['id'] == chosen_p_id].iloc[0]
                    
                    s_qte = st.number_input("Quantité achetée", min_value=1, max_value=int(p_row['stock']), step=1)
                    s_deliv = st.number_input("Coût réel de livraison (Payé au livreur)", min_value=0.0)
                    s_ad = st.number_input("Coût Marketing unitaire estimé (Ads share)", min_value=0.0)
                    s_status = st.selectbox("Statut actuel de livraison", ["En attente", "Expédié", "Livré", "Retourné"])
                    
                    if st.form_submit_button("Valider et Sauvegarder la commande"):
                        add_sale(str(s_dt), chosen_p_id, p_row['name'], s_qte, p_row['selling_price'], p_row['purchase_price'], s_deliv, s_ad, s_status)
                        st.success("Commande comptabilisée et mise à jour automatique du stock réalisée !")
                        st.rerun()
                else:
                    st.error("Rupture de stock totale sur toutes vos références.")

    with tab2:
        st.markdown("### 📋 Suivi de livraison en temps réel")
        if df_sales.empty:
            st.info("Aucune commande enregistrée sur l'intervalle temporel sélectionné.")
        else:
            st.dataframe(df_sales, use_container_width=True, hide_index=True)