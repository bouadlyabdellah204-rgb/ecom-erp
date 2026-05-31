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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="نظام إدارة التجارة الإلكترونية",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS — Sahibona-inspired dark sidebar + colorful cards
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Poppins:wght@300;400;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Cairo', 'Poppins', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main background */
.main .block-container {
    padding: 1.5rem 2rem;
    background: #f0f2f6;
    max-width: 100%;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1f3a 0%, #0d1128 100%) !important;
    border-right: 1px solid #2d3561;
}
[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.5rem;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #c8cfe8 !important;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* Radio buttons in sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.95rem !important;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    margin: 2px 0;
    display: block;
    transition: all 0.2s;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
}

/* Metric Cards */
.metric-card-blue {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #42a5f5 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: white;
    box-shadow: 0 8px 32px rgba(21,101,192,0.4);
    border: 1px solid rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}
.metric-card-purple {
    background: linear-gradient(135deg, #6a1b9a 0%, #8e24aa 50%, #ba68c8 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: white;
    box-shadow: 0 8px 32px rgba(106,27,154,0.4);
    border: 1px solid rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}
.metric-card-green {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #66bb6a 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: white;
    box-shadow: 0 8px 32px rgba(27,94,32,0.4);
    border: 1px solid rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}
.metric-card-red {
    background: linear-gradient(135deg, #b71c1c 0%, #c62828 50%, #ef5350 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: white;
    box-shadow: 0 8px 32px rgba(183,28,28,0.4);
    border: 1px solid rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}
.metric-card-orange {
    background: linear-gradient(135deg, #e65100 0%, #f57c00 50%, #ffb74d 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: white;
    box-shadow: 0 8px 32px rgba(230,81,0,0.4);
    border: 1px solid rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}
.metric-card-teal {
    background: linear-gradient(135deg, #004d40 0%, #00695c 50%, #4db6ac 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: white;
    box-shadow: 0 8px 32px rgba(0,77,64,0.4);
    border: 1px solid rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}

.metric-card-blue::before, .metric-card-purple::before,
.metric-card-green::before, .metric-card-red::before,
.metric-card-orange::before, .metric-card-teal::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
}

.metric-icon {
    font-size: 2rem;
    float: right;
    opacity: 0.85;
}
.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    opacity: 0.85;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.2rem;
    font-family: 'Poppins', sans-serif;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 900;
    line-height: 1.1;
    font-family: 'Poppins', sans-serif;
}
.metric-sub {
    font-size: 0.72rem;
    opacity: 0.75;
    margin-top: 0.3rem;
}

/* Section headers */
.section-header {
    background: linear-gradient(90deg, #1a1f3a, #2d3561);
    color: white;
    padding: 0.8rem 1.4rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Cairo', sans-serif;
}

/* Form styling */
[data-testid="stForm"] {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border: 1px solid #e8eaf0;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #1976d2);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    font-family: 'Cairo', 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(21,101,192,0.3);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(21,101,192,0.4);
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Cairo', 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(27,94,32,0.3) !important;
}

/* Logo area */
.logo-area {
    text-align: center;
    padding: 1.5rem 0.5rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1.5rem;
}
.logo-title {
    font-size: 1.5rem;
    font-weight: 900;
    color: #ffffff !important;
    font-family: 'Poppins', sans-serif;
    letter-spacing: 2px;
}
.logo-sub {
    font-size: 0.7rem;
    color: #8892c0 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Page title */
.page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1a1f3a;
    margin-bottom: 0.2rem;
    font-family: 'Cairo', sans-serif;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #7b89a8;
    margin-bottom: 1.5rem;
}

/* Table card */
.table-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-top: 1rem;
}

/* Alert styling */
div[data-testid="stAlert"] {
    border-radius: 10px;
    font-family: 'Cairo', sans-serif;
}

/* Selectbox / Input */
[data-testid="stSelectbox"] > div, 
[data-testid="stTextInput"] > div > div,
[data-testid="stNumberInput"] > div > div {
    border-radius: 8px;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #d0d5e8, transparent);
    margin: 1.5rem 0;
}

/* Nav item active */
.nav-active {
    background: rgba(21,101,192,0.25) !important;
    color: #64b5f6 !important;
    border-left: 3px solid #1976d2;
}
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
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sku TEXT,
        purchase_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
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
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )""")
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
    conn.execute("INSERT INTO products (name,sku,purchase_price,selling_price,stock) VALUES (?,?,?,?,?)",
                 (name, sku, purchase_price, selling_price, stock))
    conn.commit(); conn.close()

def update_product(pid, name, sku, purchase_price, selling_price, stock):
    conn = get_conn()
    conn.execute("UPDATE products SET name=?,sku=?,purchase_price=?,selling_price=?,stock=? WHERE id=?",
                 (name, sku, purchase_price, selling_price, stock, pid))
    conn.commit(); conn.close()

def delete_product(pid):
    conn = get_conn()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit(); conn.close()

def add_expense(dt, category, amount, description):
    conn = get_conn()
    conn.execute("INSERT INTO expenses (date,category,amount,description) VALUES (?,?,?,?)",
                 (dt, category, amount, description))
    conn.commit(); conn.close()

def update_expense(eid, dt, category, amount, description):
    conn = get_conn()
    conn.execute("UPDATE expenses SET date=?,category=?,amount=?,description=? WHERE id=?",
                 (dt, category, amount, description, eid))
    conn.commit(); conn.close()

def delete_expense(eid):
    conn = get_conn()
    conn.execute("DELETE FROM expenses WHERE id=?", (eid,))
    conn.commit(); conn.close()

def add_sale(dt, product_id, product_name, quantity, selling_price, purchase_price, delivery_cost, ads_share):
    conn = get_conn()
    conn.execute("INSERT INTO sales (date,product_id,product_name,quantity,selling_price,purchase_price,delivery_cost,ads_share) VALUES (?,?,?,?,?,?,?,?)",
                 (dt, product_id, product_name, quantity, selling_price, purchase_price, delivery_cost, ads_share))
    conn.execute("UPDATE products SET stock = stock - ? WHERE id=?", (quantity, product_id))
    conn.commit(); conn.close()

def delete_sale(sid, product_id, quantity):
    conn = get_conn()
    conn.execute("DELETE FROM sales WHERE id=?", (sid,))
    conn.execute("UPDATE products SET stock = stock + ? WHERE id=?", (quantity, product_id))
    conn.commit(); conn.close()

# ─────────────────────────────────────────
# PDF GENERATORS
# ─────────────────────────────────────────
BRAND_COLOR = colors.HexColor("#1565c0")
DARK_COLOR  = colors.HexColor("#1a1f3a")
LIGHT_BG    = colors.HexColor("#f0f4ff")
GREEN_COLOR = colors.HexColor("#2e7d32")
RED_COLOR   = colors.HexColor("#c62828")

def build_pdf_header(elements, title, subtitle=""):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=20,
                                  textColor=DARK_COLOR, alignment=TA_CENTER, spaceAfter=4)
    sub_style = ParagraphStyle('sub', fontName='Helvetica', fontSize=10,
                                textColor=colors.HexColor("#7b89a8"), alignment=TA_CENTER, spaceAfter=2)
    date_style = ParagraphStyle('date', fontName='Helvetica', fontSize=9,
                                 textColor=colors.HexColor("#aaaaaa"), alignment=TA_CENTER, spaceAfter=16)
    elements.append(Paragraph("🛒  E-COMMERCE ERP SYSTEM", title_style))
    elements.append(Paragraph(title, ParagraphStyle('t2', fontName='Helvetica-Bold', fontSize=14,
                                                     textColor=BRAND_COLOR, alignment=TA_CENTER, spaceAfter=2)))
    if subtitle:
        elements.append(Paragraph(subtitle, sub_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d  %H:%M')}", date_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=BRAND_COLOR, spaceAfter=14))

def generate_inventory_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    build_pdf_header(elements, "Inventory Status Report", "Rapport d'état des stocks")
    if df.empty:
        elements.append(Paragraph("No products found.", getSampleStyleSheet()['Normal']))
    else:
        df2 = df.copy()
        df2['Capital (DH)'] = (df2['stock'] * df2['purchase_price']).round(2)
        table_data = [['ID', 'Product Name', 'SKU', 'Purchase\nPrice (DH)', 'Selling\nPrice (DH)', 'Stock', 'Capital\nInvested (DH)']]
        for _, row in df2.iterrows():
            table_data.append([
                str(row['id']), row['name'], row.get('sku','—'),
                f"{row['purchase_price']:.2f}", f"{row['selling_price']:.2f}",
                str(row['stock']), f"{row['Capital (DH)']:.2f}"
            ])
        total_capital = df2['Capital (DH)'].sum()
        table_data.append(['', '', '', '', 'TOTAL', '', f"{total_capital:.2f} DH"])
        t = Table(table_data, colWidths=[1*cm, 4.5*cm, 2.5*cm, 2.2*cm, 2.2*cm, 1.5*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), DARK_COLOR),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_BG]),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('GRID', (0,0), (-1,-2), 0.4, colors.HexColor("#d0d5e8")),
            ('BACKGROUND', (0,-1), (-1,-1), BRAND_COLOR),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,-1), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.5*cm))
        stat_data = [['Total Products', 'Total Units in Stock', 'Total Capital Invested'],
                     [str(len(df2)), str(df2['stock'].sum()), f"{total_capital:.2f} DH"]]
        st2 = Table(stat_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        st2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#d0d5e8")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(st2)
    doc.build(elements)
    buf.seek(0)
    return buf

def generate_expenses_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    build_pdf_header(elements, "Operational Expenses Statement", "Relevé des dépenses opérationnelles")
    if df.empty:
        elements.append(Paragraph("No expenses found.", getSampleStyleSheet()['Normal']))
    else:
        table_data = [['ID', 'Date', 'Category', 'Description', 'Amount (DH)']]
        for _, row in df.iterrows():
            table_data.append([str(row['id']), row['date'], row['category'],
                                str(row.get('description',''))[:40], f"{row['amount']:.2f}"])
        total = df['amount'].sum()
        table_data.append(['', '', '', 'TOTAL', f"{total:.2f} DH"])
        t = Table(table_data, colWidths=[1*cm, 2.5*cm, 4*cm, 6*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), DARK_COLOR),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (3,1), (3,-2), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_BG]),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('GRID', (0,0), (-1,-2), 0.4, colors.HexColor("#d0d5e8")),
            ('BACKGROUND', (0,-1), (-1,-1), RED_COLOR),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,-1), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.5*cm))
        by_cat = df.groupby('category')['amount'].sum().reset_index()
        cat_data = [['Category', 'Total (DH)']] + [[r['category'], f"{r['amount']:.2f} DH"] for _, r in by_cat.iterrows()]
        ct = Table(cat_data, colWidths=[9*cm, 7.5*cm])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#d0d5e8")),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ]))
        elements.append(Paragraph("Breakdown by Category:", ParagraphStyle('bk', fontName='Helvetica-Bold',
                                                                              fontSize=10, spaceAfter=6, spaceBefore=10)))
        elements.append(ct)
    doc.build(elements)
    buf.seek(0)
    return buf

def generate_sales_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(A4[1], A4[0]), leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    build_pdf_header(elements, "Sales & Orders Report", "Rapport des ventes et commandes")
    if df.empty:
        elements.append(Paragraph("No sales found.", getSampleStyleSheet()['Normal']))
    else:
        df2 = df.copy()
        df2['Revenue'] = df2['quantity'] * df2['selling_price']
        df2['COGS'] = df2['quantity'] * df2['purchase_price']
        df2['Gross Profit'] = df2['Revenue'] - df2['COGS']
        table_data = [['ID', 'Date', 'Product', 'Qty', 'Unit Price\n(DH)', 'Revenue\n(DH)', 'Delivery\n(DH)', 'Ads Share\n(DH)', 'Gross\nProfit (DH)']]
        for _, row in df2.iterrows():
            table_data.append([
                str(row['id']), row['date'], row['product_name'][:18],
                str(row['quantity']), f"{row['selling_price']:.2f}",
                f"{row['Revenue']:.2f}", f"{row['delivery_cost']:.2f}",
                f"{row['ads_share']:.2f}", f"{row['Gross Profit']:.2f}"
            ])
        totals = ['', '', 'TOTAL', str(int(df2['quantity'].sum())), '',
                  f"{df2['Revenue'].sum():.2f}", f"{df2['delivery_cost'].sum():.2f}",
                  f"{df2['ads_share'].sum():.2f}", f"{df2['Gross Profit'].sum():.2f}"]
        table_data.append(totals)
        t = Table(table_data, colWidths=[1*cm, 2.2*cm, 3.8*cm, 1*cm, 2.2*cm, 2.5*cm, 2.2*cm, 2.2*cm, 2.6*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), DARK_COLOR),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_BG]),
            ('FONTSIZE', (0,1), (-1,-1), 7.5),
            ('GRID', (0,0), (-1,-2), 0.4, colors.HexColor("#d0d5e8")),
            ('BACKGROUND', (0,-1), (-1,-1), GREEN_COLOR),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,-1), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t)
    doc.build(elements)
    buf.seek(0)
    return buf

def generate_dashboard_pdf(metrics, df_products, df_expenses, df_sales):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    build_pdf_header(elements, "Executive Financial Report", "Rapport Financier Exécutif — Tableau de bord complet")
    styles = getSampleStyleSheet()
    # KPI Cards
    kpi_data = [
        ['📊 KPI', 'VALUE', 'NOTE'],
        ['Total Sales Revenue', f"{metrics['total_sales']:.2f} DH", 'Σ (Qty × Selling Price)'],
        ['Cost of Goods Sold (COGS)', f"{metrics['cogs']:.2f} DH", 'Σ (Qty × Purchase Price)'],
        ['Total Static Expenses', f"{metrics['static_expenses']:.2f} DH", 'All logged expense records'],
        ['Total Delivery Costs', f"{metrics['delivery_costs']:.2f} DH", 'From sales records'],
        ['Total Ads Share', f"{metrics['ads_share']:.2f} DH", 'From sales records'],
        ['Total Expenses Combined', f"{metrics['total_expenses']:.2f} DH", 'Static + Delivery + Ads'],
        ['Net Clean Profit', f"{metrics['net_profit']:.2f} DH",
         f"Margin: {metrics['margin']:.1f}%"],
        ['Capital Invested in Stock', f"{metrics['capital']:.2f} DH", 'Current stock × Purchase price'],
        ['Total Products (SKUs)', str(metrics['n_products']), 'Active inventory'],
        ['Total Sales Transactions', str(metrics['n_sales']), 'All orders logged'],
    ]
    t = Table(kpi_data, colWidths=[6*cm, 4.5*cm, 6*cm])
    profit_row = 7
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#d0d5e8")),
        ('BACKGROUND', (0, profit_row), (-1, profit_row),
         GREEN_COLOR if metrics['net_profit'] >= 0 else RED_COLOR),
        ('TEXTCOLOR', (0, profit_row), (-1, profit_row), colors.white),
        ('FONTNAME', (0, profit_row), (-1, profit_row), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    elements.append(t)
    doc.build(elements)
    buf.seek(0)
    return buf

# ─────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-area">
        <div style="font-size:2.5rem;">🛒</div>
        <div class="logo-title">ECOM ERP</div>
        <div class="logo-sub">Point de Vente Pro</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["📈  Tableau de bord", "📦  Gestion du stock", "💸  Dépenses", "🛍️  Ventes & Commandes"],
        label_visibility="collapsed"
    )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 0.5rem 1rem; font-size:0.75rem; color:#5a6490;">
        <div style="margin-bottom:0.3rem;">💾 Auto-save activé</div>
        <div style="margin-bottom:0.3rem;">🗄️ SQLite Database</div>
        <div>📄 Export PDF Ready</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# COMPUTE METRICS HELPER
# ─────────────────────────────────────────
def compute_metrics():
    df_sales = load_sales()
    df_expenses = load_expenses()
    df_products = load_products()
    total_sales = (df_sales['quantity'] * df_sales['selling_price']).sum() if not df_sales.empty else 0
    cogs = (df_sales['quantity'] * df_sales['purchase_price']).sum() if not df_sales.empty else 0
    static_expenses = df_expenses['amount'].sum() if not df_expenses.empty else 0
    delivery_costs = df_sales['delivery_cost'].sum() if not df_sales.empty else 0
    ads_share = (df_sales['quantity'] * df_sales['ads_share']).sum() if not df_sales.empty else 0
    total_expenses = static_expenses + delivery_costs + ads_share
    net_profit = total_sales - cogs - total_expenses
    margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
    capital = (df_products['stock'] * df_products['purchase_price']).sum() if not df_products.empty else 0
    return {
        "total_sales": total_sales, "cogs": cogs, "static_expenses": static_expenses,
        "delivery_costs": delivery_costs, "ads_share": ads_share,
        "total_expenses": total_expenses, "net_profit": net_profit,
        "margin": margin, "capital": capital,
        "n_products": len(df_products), "n_sales": len(df_sales)
    }

# ═══════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════
if page == "📈  Tableau de bord":
    st.markdown('<div class="page-title">📈 Tableau de bord</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Vue d\'ensemble de vos performances commerciales en temps réel</div>', unsafe_allow_html=True)

    m = compute_metrics()
    df_sales = load_sales()
    df_expenses = load_expenses()
    df_products = load_products()

    # ── Metric Cards Row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card-blue">
            <div class="metric-icon">🛒</div>
            <div class="metric-label">Ventes Totales</div>
            <div class="metric-value">{m['total_sales']:,.2f} DH</div>
            <div class="metric-sub">{m['n_sales']} commandes</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        profit_class = "metric-card-green" if m['net_profit'] >= 0 else "metric-card-red"
        profit_icon = "📈" if m['net_profit'] >= 0 else "📉"
        st.markdown(f"""
        <div class="{profit_class}">
            <div class="metric-icon">{profit_icon}</div>
            <div class="metric-label">Bénéfice Net</div>
            <div class="metric-value">{m['net_profit']:,.2f} DH</div>
            <div class="metric-sub">Marge: {m['margin']:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card-teal">
            <div class="metric-icon">🏭</div>
            <div class="metric-label">Capital Investi (Stock)</div>
            <div class="metric-value">{m['capital']:,.2f} DH</div>
            <div class="metric-sub">{m['n_products']} produits</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Metric Cards Row 2
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"""
        <div class="metric-card-red">
            <div class="metric-icon">💸</div>
            <div class="metric-label">Dépenses Totales</div>
            <div class="metric-value">{m['total_expenses']:,.2f} DH</div>
            <div class="metric-sub">Statiques + Livraison + Pub</div>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card-orange">
            <div class="metric-icon">📦</div>
            <div class="metric-label">Coût des Marchandises (COGS)</div>
            <div class="metric-value">{m['cogs']:,.2f} DH</div>
            <div class="metric-sub">Prix d'achat × Quantités</div>
        </div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="metric-card-purple">
            <div class="metric-icon">📊</div>
            <div class="metric-label">Marge Brute</div>
            <div class="metric-value">{(m['total_sales']-m['cogs']):,.2f} DH</div>
            <div class="metric-sub">Ventes − COGS</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">📅 Activité Journalière des Ventes</div>', unsafe_allow_html=True)
        if not df_sales.empty:
            daily = df_sales.copy()
            daily['revenue'] = daily['quantity'] * daily['selling_price']
            daily_agg = daily.groupby('date').agg(revenue=('revenue','sum'), orders=('id','count')).reset_index()
            daily_agg = daily_agg.sort_values('date')
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily_agg['date'], y=daily_agg['revenue'],
                                  name='Revenue (DH)', marker_color='#1976d2', opacity=0.85))
            fig.add_trace(go.Scatter(x=daily_agg['date'], y=daily_agg['orders'],
                                      name='Orders', mode='lines+markers',
                                      line=dict(color='#ff9800', width=2.5),
                                      marker=dict(size=7), yaxis='y2'))
            fig.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                margin=dict(l=10, r=10, t=20, b=10),
                height=280, font=dict(family='Poppins, Cairo'),
                legend=dict(orientation='h', y=1.1, x=0),
                yaxis=dict(title='DH', gridcolor='#f0f2f6'),
                yaxis2=dict(title='Orders', overlaying='y', side='right', gridcolor='#f0f2f6'),
                xaxis=dict(gridcolor='#f0f2f6'),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune vente enregistrée pour le moment.")

    with c2:
        st.markdown('<div class="section-header">💸 Répartition des Dépenses</div>', unsafe_allow_html=True)
        if not df_expenses.empty:
            cat_exp = df_expenses.groupby('category')['amount'].sum().reset_index()
            fig2 = px.pie(cat_exp, names='category', values='amount',
                          color_discrete_sequence=['#1565c0','#6a1b9a','#b71c1c','#e65100','#1b5e20','#004d40'],
                          hole=0.4)
            fig2.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                margin=dict(l=10, r=10, t=20, b=10), height=280,
                font=dict(family='Poppins, Cairo'),
                legend=dict(orientation='h', y=-0.15, x=0.1, font=dict(size=10)),
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label',
                               textfont_size=9)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucune dépense enregistrée pour le moment.")

    # Profit waterfall
    if not df_sales.empty or not df_expenses.empty:
        st.markdown('<div class="section-header">📊 Analyse Financière — Waterfall</div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Waterfall(
            name="Analyse", orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Ventes", "- COGS", "- Dépenses\nStatiques", "- Livraison", "- Pub / Ads", "Bénéfice Net"],
            textposition="outside",
            text=[f"{m['total_sales']:.0f}", f"-{m['cogs']:.0f}",
                  f"-{m['static_expenses']:.0f}", f"-{m['delivery_costs']:.0f}",
                  f"-{m['ads_share']:.0f}", f"{m['net_profit']:.0f}"],
            y=[m['total_sales'], -m['cogs'], -m['static_expenses'], -m['delivery_costs'], -m['ads_share'], 0],
            connector={"line": {"color": "#c8cfe8"}},
            increasing={"marker": {"color": "#2e7d32"}},
            decreasing={"marker": {"color": "#c62828"}},
            totals={"marker": {"color": "#1565c0"}},
        ))
        fig3.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=20, b=10), height=300,
            font=dict(family='Poppins, Cairo', size=11),
            yaxis=dict(title='DH', gridcolor='#f0f2f6'),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Download PDF
    st.markdown("---")
    pdf_buf = generate_dashboard_pdf(m, df_products, df_expenses, df_sales)
    st.download_button(
        label="⬇️  Télécharger le Rapport Financier Exécutif (PDF)",
        data=pdf_buf,
        file_name=f"executive_report_{date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════
# PAGE: INVENTORY
# ═══════════════════════════════════════════════════════════
elif page == "📦  Gestion du stock":
    st.markdown('<div class="page-title">📦 Gestion du Stock & Inventaire</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Ajoutez, modifiez ou supprimez vos produits — synchronisé avec les ventes</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Ajouter un Produit", "✏️ Modifier / Supprimer"])

    with tab1:
        with st.form("add_product_form", clear_on_submit=True):
            st.markdown("**Nouveau Produit**")
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("Nom du Produit *", placeholder="Ex: Sac à main cuir noir")
                p_purchase = st.number_input("Prix d'achat (DH) *", min_value=0.0, step=0.5)
                p_stock = st.number_input("Stock Initial *", min_value=0, step=1)
            with c2:
                p_sku = st.text_input("SKU / Référence", placeholder="Ex: SAC-001")
                p_selling = st.number_input("Prix de vente (DH) *", min_value=0.0, step=0.5)
            submitted = st.form_submit_button("✅ Enregistrer le Produit", use_container_width=True)
            if submitted:
                if not p_name:
                    st.error("❌ Le nom du produit est obligatoire.")
                elif p_selling < p_purchase:
                    st.warning("⚠️ Prix de vente inférieur au prix d'achat — vérifiez vos chiffres.")
                else:
                    add_product(p_name, p_sku, p_purchase, p_selling, p_stock)
                    st.success(f"✅ Produit **{p_name}** ajouté avec succès!")
                    st.rerun()

    with tab2:
        df_products = load_products()
        if df_products.empty:
            st.info("Aucun produit trouvé. Commencez par en ajouter un.")
        else:
            df_display = df_products.copy()
            df_display['Capital (DH)'] = (df_display['stock'] * df_display['purchase_price']).round(2)
            df_display.columns = ['ID','Nom','SKU','Prix Achat','Prix Vente','Stock','Créé le','Capital (DH)']

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.dataframe(df_display[['ID','Nom','SKU','Prix Achat','Prix Vente','Stock','Capital (DH)']],
                         use_container_width=True, hide_index=True,
                         column_config={
                             "ID": st.column_config.NumberColumn(width="small"),
                             "Prix Achat": st.column_config.NumberColumn(format="%.2f DH"),
                             "Prix Vente": st.column_config.NumberColumn(format="%.2f DH"),
                             "Capital (DH)": st.column_config.NumberColumn(format="%.2f DH"),
                             "Stock": st.column_config.NumberColumn(width="small"),
                         })
            st.markdown('</div>', unsafe_allow_html=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Produits", len(df_products))
            col2.metric("Total Unités en Stock", int(df_products['stock'].sum()))
            col3.metric("Capital Total Investi", f"{df_display['Capital (DH)'].sum():,.2f} DH")

            st.markdown("---")
            st.markdown("**✏️ Modifier un produit**")
            product_options = {f"[{r['id']}] {r['name']}": r['id'] for _, r in df_products.iterrows()}
            selected_label = st.selectbox("Sélectionnez un produit à modifier", list(product_options.keys()), key="edit_prod_sel")
            selected_id = product_options[selected_label]
            row = df_products[df_products['id'] == selected_id].iloc[0]

            with st.form("edit_product_form"):
                c1, c2 = st.columns(2)
                with c1:
                    e_name = st.text_input("Nom", value=row['name'])
                    e_purchase = st.number_input("Prix d'achat (DH)", value=float(row['purchase_price']), step=0.5)
                    e_stock = st.number_input("Stock", value=int(row['stock']), step=1)
                with c2:
                    e_sku = st.text_input("SKU", value=row.get('sku','') or '')
                    e_selling = st.number_input("Prix de vente (DH)", value=float(row['selling_price']), step=0.5)
                cc1, cc2 = st.columns(2)
                with cc1:
                    save_edit = st.form_submit_button("💾 Sauvegarder les modifications", use_container_width=True)
                with cc2:
                    del_btn = st.form_submit_button("🗑️ Supprimer ce produit", use_container_width=True)
                if save_edit:
                    update_product(selected_id, e_name, e_sku, e_purchase, e_selling, e_stock)
                    st.success(f"✅ Produit **{e_name}** mis à jour!")
                    st.rerun()
                if del_btn:
                    delete_product(selected_id)
                    st.success("🗑️ Produit supprimé.")
                    st.rerun()

    # PDF Download
    st.markdown("---")
    df_prod_pdf = load_products()
    pdf_buf = generate_inventory_pdf(df_prod_pdf)
    st.download_button(
        label="⬇️  Télécharger le Rapport d'Inventaire (PDF)",
        data=pdf_buf,
        file_name=f"inventory_report_{date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════
# PAGE: EXPENSES
# ═══════════════════════════════════════════════════════════
elif page == "💸  Dépenses":
    st.markdown('<div class="page-title">💸 Suivi des Dépenses</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enregistrez toutes vos charges opérationnelles, pub, et frais divers</div>', unsafe_allow_html=True)

    CATEGORIES = ["Ads Meta/Facebook", "Ads TikTok", "Sourcing / Achat Stock",
                  "Emballage & Packaging", "Perte Livraison", "Frais Fixes", "Autre"]

    tab1, tab2 = st.tabs(["➕ Ajouter une Dépense", "✏️ Modifier / Supprimer"])

    with tab1:
        with st.form("add_expense_form", clear_on_submit=True):
            st.markdown("**Nouvelle Dépense**")
            c1, c2, c3 = st.columns([1,2,1])
            with c1:
                e_date = st.date_input("Date", value=date.today())
            with c2:
                e_cat = st.selectbox("Catégorie *", CATEGORIES)
            with c3:
                e_amount = st.number_input("Montant (DH) *", min_value=0.0, step=1.0)
            e_desc = st.text_input("Description", placeholder="Ex: Campagne Meta - Sacs de Luxe - Mai 2025")
            submitted = st.form_submit_button("✅ Enregistrer la Dépense", use_container_width=True)
            if submitted:
                if e_amount <= 0:
                    st.error("❌ Le montant doit être supérieur à 0.")
                else:
                    add_expense(str(e_date), e_cat, e_amount, e_desc)
                    st.success(f"✅ Dépense de **{e_amount:.2f} DH** enregistrée!")
                    st.rerun()

    with tab2:
        df_expenses = load_expenses()
        if df_expenses.empty:
            st.info("Aucune dépense trouvée.")
        else:
            df_disp = df_expenses.copy()
            df_disp.columns = ['ID','Date','Catégorie','Montant (DH)','Description','Créé le']
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.dataframe(df_disp[['ID','Date','Catégorie','Montant (DH)','Description']],
                         use_container_width=True, hide_index=True,
                         column_config={
                             "Montant (DH)": st.column_config.NumberColumn(format="%.2f DH"),
                         })
            st.markdown('</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            c1.metric("Total Dépenses", f"{df_expenses['amount'].sum():,.2f} DH")
            c2.metric("Nombre d'Enregistrements", len(df_expenses))

            st.markdown("---")
            st.markdown("**✏️ Modifier une dépense**")
            exp_options = {f"[{r['id']}] {r['date']} — {r['category']} — {r['amount']:.2f} DH": r['id']
                           for _, r in df_expenses.iterrows()}
            sel_label = st.selectbox("Sélectionnez une dépense", list(exp_options.keys()), key="edit_exp_sel")
            sel_id = exp_options[sel_label]
            erow = df_expenses[df_expenses['id'] == sel_id].iloc[0]

            with st.form("edit_expense_form"):
                c1, c2, c3 = st.columns([1,2,1])
                with c1:
                    ne_date = st.date_input("Date", value=pd.to_datetime(erow['date']).date())
                with c2:
                    ne_cat = st.selectbox("Catégorie", CATEGORIES,
                                          index=CATEGORIES.index(erow['category']) if erow['category'] in CATEGORIES else 0)
                with c3:
                    ne_amount = st.number_input("Montant (DH)", value=float(erow['amount']), step=1.0)
                ne_desc = st.text_input("Description", value=str(erow.get('description','') or ''))
                cc1, cc2 = st.columns(2)
                with cc1:
                    save_e = st.form_submit_button("💾 Sauvegarder", use_container_width=True)
                with cc2:
                    del_e = st.form_submit_button("🗑️ Supprimer", use_container_width=True)
                if save_e:
                    update_expense(sel_id, str(ne_date), ne_cat, ne_amount, ne_desc)
                    st.success("✅ Dépense mise à jour!")
                    st.rerun()
                if del_e:
                    delete_expense(sel_id)
                    st.success("🗑️ Dépense supprimée.")
                    st.rerun()

    st.markdown("---")
    df_exp_pdf = load_expenses()
    pdf_buf = generate_expenses_pdf(df_exp_pdf)
    st.download_button(
        label="⬇️  Télécharger le Relevé des Dépenses (PDF)",
        data=pdf_buf,
        file_name=f"expenses_report_{date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════
# PAGE: SALES
# ═══════════════════════════════════════════════════════════
elif page == "🛍️  Ventes & Commandes":
    st.markdown('<div class="page-title">🛍️ Ventes & Commandes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enregistrez vos ventes — le stock est mis à jour automatiquement</div>', unsafe_allow_html=True)

    df_products = load_products()
    tab1, tab2 = st.tabs(["➕ Enregistrer une Vente", "📋 Historique & Suppression"])

    with tab1:
        if df_products.empty:
            st.warning("⚠️ Ajoutez d'abord des produits dans **Gestion du stock** avant d'enregistrer des ventes.")
        else:
            with st.form("add_sale_form", clear_on_submit=True):
                st.markdown("**Nouvelle Commande / Vente**")
                c1, c2 = st.columns(2)
                with c1:
                    s_date = st.date_input("Date de la Vente", value=date.today())
                    available_products = {f"[{r['id']}] {r['name']} (Stock: {r['stock']})": r['id']
                                          for _, r in df_products.iterrows() if r['stock'] > 0}
                    if not available_products:
                        st.warning("⚠️ Aucun produit avec du stock disponible.")
                        s_product_id = None
                        s_qty = 1
                        s_delivery = 0.0
                        s_ads = 0.0
                    else:
                        s_product_label = st.selectbox("Produit *", list(available_products.keys()))
                        s_product_id = available_products[s_product_label]
                        prod_row = df_products[df_products['id'] == s_product_id].iloc[0]
                        s_qty = st.number_input("Quantité Vendue *", min_value=1, step=1, max_value=int(prod_row['stock']))
                with c2:
                    s_delivery = st.number_input("Coût de Livraison Réel (DH)", min_value=0.0, step=1.0)
                    s_ads = st.number_input("Part Pub par Unité (DH/unité)", min_value=0.0, step=0.5,
                                            help="Montant de publicité attribué à cette vente par unité vendue")
                    if available_products and s_product_id:
                        st.info(f"💰 Prix de vente: **{prod_row['selling_price']:.2f} DH** | Prix achat: **{prod_row['purchase_price']:.2f} DH**")
                        est_revenue = s_qty * prod_row['selling_price']
                        est_cogs = s_qty * prod_row['purchase_price']
                        est_profit = est_revenue - est_cogs - s_delivery - (s_qty * s_ads)
                        st.info(f"📊 Profit estimé: **{est_profit:.2f} DH**")

                submitted = st.form_submit_button("✅ Confirmer la Vente", use_container_width=True)
                if submitted:
                    if not available_products or not s_product_id:
                        st.error("❌ Aucun produit disponible.")
                    elif s_qty > int(prod_row['stock']):
                        st.error(f"❌ Stock insuffisant! Stock disponible: {prod_row['stock']}")
                    else:
                        add_sale(str(s_date), s_product_id, prod_row['name'], s_qty,
                                 prod_row['selling_price'], prod_row['purchase_price'],
                                 s_delivery, s_ads)
                        st.success(f"✅ Vente de **{s_qty}× {prod_row['name']}** enregistrée! Stock mis à jour.")
                        st.rerun()

    with tab2:
        df_sales = load_sales()
        if df_sales.empty:
            st.info("Aucune vente enregistrée pour le moment.")
        else:
            df_disp = df_sales.copy()
            df_disp['Revenue (DH)'] = (df_disp['quantity'] * df_disp['selling_price']).round(2)
            df_disp['COGS (DH)'] = (df_disp['quantity'] * df_disp['purchase_price']).round(2)
            df_disp['Profit Brut (DH)'] = (df_disp['Revenue (DH)'] - df_disp['COGS (DH)']).round(2)

            display_cols = ['id','date','product_name','quantity','selling_price','Revenue (DH)','delivery_cost','ads_share','Profit Brut (DH)']
            rename_map = {'id':'ID','date':'Date','product_name':'Produit','quantity':'Qté',
                         'selling_price':'Prix Unit.','Revenue (DH)':'CA (DH)',
                         'delivery_cost':'Livraison (DH)','ads_share':'Pub/Unité (DH)','Profit Brut (DH)':'Profit Brut (DH)'}
            df_show = df_disp[display_cols].rename(columns=rename_map)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.dataframe(df_show, use_container_width=True, hide_index=True,
                         column_config={
                             "CA (DH)": st.column_config.NumberColumn(format="%.2f DH"),
                             "Prix Unit.": st.column_config.NumberColumn(format="%.2f DH"),
                             "Livraison (DH)": st.column_config.NumberColumn(format="%.2f DH"),
                             "Pub/Unité (DH)": st.column_config.NumberColumn(format="%.2f DH"),
                             "Profit Brut (DH)": st.column_config.NumberColumn(format="%.2f DH"),
                         })
            st.markdown('</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("CA Total", f"{df_disp['Revenue (DH)'].sum():,.2f} DH")
            c2.metric("Profit Brut Total", f"{df_disp['Profit Brut (DH)'].sum():,.2f} DH")
            c3.metric("Total Commandes", len(df_sales))

            st.markdown("---")
            st.markdown("**🗑️ Supprimer une vente** (restaure le stock)")
            sale_options = {f"[{r['id']}] {r['date']} — {r['product_name']} ×{r['quantity']}": r['id']
                            for _, r in df_sales.iterrows()}
            del_label = st.selectbox("Sélectionnez une vente à annuler", list(sale_options.keys()), key="del_sale_sel")
            del_sale_id = sale_options[del_label]
            del_row = df_sales[df_sales['id'] == del_sale_id].iloc[0]
            if st.button(f"🗑️ Annuler cette vente (stock +{del_row['quantity']} restauré)", type="secondary"):
                delete_sale(del_sale_id, del_row['product_id'], del_row['quantity'])
                st.success(f"✅ Vente annulée. Stock restauré: +{del_row['quantity']} unités.")
                st.rerun()

    st.markdown("---")
    df_s_pdf = load_sales()
    pdf_buf = generate_sales_pdf(df_s_pdf)
    st.download_button(
        label="⬇️  Télécharger le Rapport des Ventes (PDF)",
        data=pdf_buf,
        file_name=f"sales_report_{date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
