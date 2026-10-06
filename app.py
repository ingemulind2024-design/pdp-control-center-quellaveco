import io
import base64
import time
import hashlib
import hmac
from pathlib import Path
import uuid
import unicodedata
import html
import tempfile
import gc

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import extra_streamlit_components as stx

from PIL import Image, ImageOps
from datetime import datetime, timezone, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image as RLImage,
    KeepTogether
)
from reportlab.graphics.shapes import (
    Drawing,
    Line,
    String,
    PolyLine
)

from supabase import create_client

st.set_page_config(
    page_title="PDP Control Center Quellaveco - MAININ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)


# =====================================================
# SESIÓN PERSISTENTE EN NAVEGADOR
# =====================================================
COOKIE_SESION = "mainin_quellaveco_session"
DIAS_SESION_PERSISTENTE = 7
COOKIE_MAX_AGE = DIAS_SESION_PERSISTENTE * 24 * 60 * 60

# Se usa para ESCRIBIR/BORRAR la cookie en el navegador.
cookie_manager = stx.CookieManager(
    key="mainin_quellaveco_cookie_manager"
)



# =====================================================
# IDENTIDAD VISUAL PROFESIONAL - PDP QUELLAVECO
# =====================================================

def aplicar_estilo_profesional():
    st.markdown(
        """
        <style>
        :root {
            --ink: #0B1F33;
            --ink-2: #143A5E;
            --blue: #155EEF;
            --cyan: #0EA5E9;
            --red: #D92D20;
            --green: #079455;
            --amber: #DC6803;
            --bg: #F3F6F9;
            --card: #FFFFFF;
            --line: #DDE5EE;
            --muted: #667085;
            --soft: #EEF3F8;
            --shadow: 0 10px 28px rgba(11,31,51,.07);
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background:
                radial-gradient(circle at 82% 8%, rgba(21,94,239,.055), transparent 24rem),
                linear-gradient(180deg, #F8FAFC 0%, var(--bg) 44%, #F5F7FA 100%);
        }

        .block-container {
            padding-top: 1.05rem;
            padding-bottom: 3rem;
            max-width: 1540px;
        }

        /* Sidebar: limpio, corporativo y compacto */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071A2C 0%, #0B2747 100%);
            border-right: 1px solid rgba(255,255,255,.08);
        }

        [data-testid="stSidebar"] * {
            color: #E8EEF5;
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: .75rem;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,.10) !important;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            padding: .52rem .62rem;
            margin: .16rem 0;
            border-radius: 10px;
            border: 1px solid transparent;
            transition: .16s ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255,255,255,.07);
            border-color: rgba(255,255,255,.08);
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(21,94,239,.34), rgba(14,165,233,.12));
            border-color: rgba(106,170,255,.28);
            box-shadow: inset 3px 0 0 #66B6FF;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,.06) !important;
            color: #F4F7FB !important;
            border-color: rgba(255,255,255,.16) !important;
        }

        /* Tipografía */
        h1, h2, h3 {
            color: var(--ink) !important;
            letter-spacing: -.025em;
        }
        h1 { font-weight: 850 !important; }
        h2, h3 { font-weight: 800 !important; }
        p, label { color: #344054; }

        /* Inputs */
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        [data-baseweb="select"] > div {
            background: #FFFFFF !important;
            border-radius: 11px !important;
            border-color: #D6DEE8 !important;
            box-shadow: 0 1px 2px rgba(16,24,40,.025);
        }

        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="textarea"] > div:focus-within,
        [data-baseweb="select"] > div:focus-within {
            border-color: #84ADFF !important;
            box-shadow: 0 0 0 3px rgba(21,94,239,.10) !important;
        }

        /* Botones */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button,
        .stDownloadButton > button {
            border-radius: 11px !important;
            min-height: 42px;
            font-weight: 750 !important;
            border: 1px solid #CCD6E2 !important;
            background: #FFFFFF;
            color: var(--ink) !important;
            box-shadow: 0 2px 6px rgba(11,31,51,.035);
            transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            border-color: #A8B7C8 !important;
            box-shadow: 0 7px 18px rgba(11,31,51,.09);
        }

        button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #155EEF 0%, #0B4ACB 100%) !important;
            border-color: #155EEF !important;
            color: #FFFFFF !important;
            box-shadow: 0 7px 18px rgba(21,94,239,.20);
        }

        /* Formularios y contenedores */
        [data-testid="stForm"],
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            background: rgba(255,255,255,.94);
            border: 1px solid var(--line) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 24px rgba(11,31,51,.045);
        }

        [data-testid="stForm"] {
            padding: 1.1rem 1.15rem 1.2rem;
        }

        /* Métricas nativas */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 15px;
            padding: .9rem 1rem;
            box-shadow: 0 6px 18px rgba(11,31,51,.045);
        }
        [data-testid="stMetricLabel"] { color: var(--muted) !important; font-weight: 700 !important; }
        [data-testid="stMetricValue"] { color: var(--ink) !important; font-weight: 850 !important; }

        [data-testid="stAlert"] {
            border-radius: 12px;
            border-width: 1px;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 7px 20px rgba(11,31,51,.045);
        }

        [data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 8px 8px 1px;
            box-shadow: 0 8px 24px rgba(11,31,51,.05);
        }

        [data-testid="stFileUploader"] {
            background: #FFFFFF;
            border: 1px dashed #B9C7D6;
            border-radius: 15px;
            padding: 8px;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--line) !important;
            border-radius: 13px !important;
            background: #FFFFFF;
            box-shadow: 0 4px 14px rgba(11,31,51,.035);
        }

        hr {
            border-color: #E4EAF1 !important;
            margin-top: 1.15rem !important;
            margin-bottom: 1.15rem !important;
        }

        /* Header command-center */
        .mainin-header {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(115deg, #061827 0%, #0B2747 54%, #103D67 100%);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 20px;
            padding: 20px 22px 18px;
            margin-bottom: 1.05rem;
            color: white;
            box-shadow: 0 16px 38px rgba(6,24,39,.17);
        }

        .mainin-header:before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(14,165,233,.14) 1px, transparent 1px),
                linear-gradient(rgba(14,165,233,.10) 1px, transparent 1px);
            background-size: 36px 36px;
            mask-image: linear-gradient(90deg, transparent 0%, rgba(0,0,0,.35) 60%, rgba(0,0,0,.75) 100%);
            pointer-events: none;
        }

        .mainin-header:after {
            content: "";
            position: absolute;
            width: 340px;
            height: 340px;
            border-radius: 50%;
            right: -115px;
            top: -165px;
            background: radial-gradient(circle, rgba(21,94,239,.38) 0%, rgba(21,94,239,0) 68%);
            pointer-events: none;
        }

        .mainin-head-top {
            position: relative;
            z-index: 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            margin-bottom: 11px;
        }

        .mainin-kicker {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: .14em;
            text-transform: uppercase;
            color: #B9D4EF;
        }

        .mainin-kicker:before {
            content: "";
            width: 18px;
            height: 2px;
            border-radius: 99px;
            background: #49B7F5;
        }

        .mainin-status {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 9px;
            border: 1px solid rgba(255,255,255,.14);
            border-radius: 999px;
            background: rgba(255,255,255,.065);
            backdrop-filter: blur(7px);
            font-size: 10px;
            font-weight: 750;
            color: #EAF2F9;
        }

        .mainin-status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #32D583;
            box-shadow: 0 0 0 4px rgba(50,213,131,.11);
        }

        .mainin-title {
            position: relative;
            z-index: 2;
            font-size: clamp(25px, 2.8vw, 39px);
            line-height: 1.03;
            font-weight: 880;
            letter-spacing: -.035em;
            color: #FFFFFF;
            margin: 0 0 7px 0;
        }

        .mainin-subtitle {
            position: relative;
            z-index: 2;
            font-size: 12.5px;
            color: #C9D7E5;
            margin: 0;
            max-width: 900px;
        }

        .mainin-area-row {
            position: relative;
            z-index: 2;
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 13px;
        }

        .mainin-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 8px;
            border-radius: 8px;
            background: rgba(255,255,255,.07);
            border: 1px solid rgba(255,255,255,.10);
            color: #DCE8F4;
            font-size: 10px;
            font-weight: 750;
            letter-spacing: .025em;
        }

        .mainin-chip:before {
            content: "";
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #66B6FF;
        }

        /* Sidebar identity */
        .sidebar-user-card {
            border: 1px solid rgba(255,255,255,.10);
            border-radius: 14px;
            background: rgba(255,255,255,.055);
            padding: 11px 12px;
            margin: 7px 0 10px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
        }

        .sidebar-user-top { display:flex; align-items:center; gap:9px; margin-bottom:8px; }
        .sidebar-avatar {
            width: 34px; height:34px; border-radius:10px;
            display:flex; align-items:center; justify-content:center;
            background: linear-gradient(135deg,#155EEF,#0EA5E9);
            color:#FFF; font-weight:850; font-size:13px;
            box-shadow: 0 5px 12px rgba(21,94,239,.24);
        }
        .sidebar-user-name { color:#FFFFFF; font-weight:800; font-size:12.5px; line-height:1.15; }
        .sidebar-user-caption { color:#91A8BE; font-size:9.5px; margin-top:2px; }
        .sidebar-pill {
            display:inline-block;
            padding:4px 7px;
            margin:2px 3px 0 0;
            border-radius:999px;
            border:1px solid rgba(255,255,255,.10);
            background:rgba(255,255,255,.055);
            color:#CFE0F1;
            font-size:9.5px;
            font-weight:750;
        }

        /* Títulos de sección */
        .executive-title-row {
            display:flex;
            align-items:flex-end;
            justify-content:space-between;
            gap:16px;
            margin: .2rem 0 .75rem;
        }
        .executive-eyebrow {
            display:flex;
            align-items:center;
            gap:7px;
            font-size:9.5px;
            font-weight:850;
            letter-spacing:.14em;
            text-transform:uppercase;
            color:#55728F;
            margin-bottom:4px;
        }
        .executive-eyebrow:before {
            content:"";
            width:7px; height:7px; border-radius:2px;
            background:#155EEF;
            box-shadow:0 0 0 3px rgba(21,94,239,.09);
        }
        .executive-title {
            font-size:24px;
            line-height:1.08;
            font-weight:860;
            letter-spacing:-.028em;
            color:var(--ink);
        }
        .executive-subtitle { color:#667085; font-size:12px; margin-top:4px; max-width:900px; }
        .executive-badge {
            white-space:nowrap;
            border:1px solid #D4DFEA;
            background:linear-gradient(180deg,#FFFFFF,#F5F8FB);
            color:#31506F;
            border-radius:999px;
            padding:6px 10px;
            font-size:10px;
            font-weight:750;
            box-shadow:0 3px 9px rgba(11,31,51,.04);
        }

        /* KPIs ejecutivos */
        .exec-meta-line { display:flex; flex-wrap:wrap; gap:7px; margin:.2rem 0 .75rem; }
        .exec-meta-pill {
            display:inline-flex; align-items:center; gap:6px;
            padding:5px 8px; border-radius:8px;
            background:#FFFFFF; border:1px solid #DCE5EE;
            color:#53657A; font-size:10px; font-weight:700;
        }
        .exec-kpi-grid {
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:11px;
            margin:.25rem 0 .75rem;
        }
        .exec-kpi-card {
            position:relative;
            background:linear-gradient(180deg,#FFFFFF 0%,#FBFCFE 100%);
            border:1px solid #DCE5EE;
            border-radius:16px;
            padding:14px 15px 13px 16px;
            box-shadow:0 9px 24px rgba(11,31,51,.05);
            overflow:hidden;
        }
        .exec-kpi-card:after {
            content:"";
            position:absolute;
            right:-18px; top:-24px;
            width:82px; height:82px; border-radius:50%;
            background:rgba(21,94,239,.035);
        }
        .exec-kpi-card:before { content:""; position:absolute; left:0; top:0; width:3px; height:100%; background:#155EEF; }
        .exec-kpi-card.good:before { background:var(--green); }
        .exec-kpi-card.warn:before { background:#F79009; }
        .exec-kpi-card.risk:before { background:var(--red); }
        .exec-kpi-card.neutral:before { background:#5B7895; }
        .exec-kpi-label { color:#667085; font-size:9.5px; font-weight:800; text-transform:uppercase; letter-spacing:.08em; margin-bottom:6px; }
        .exec-kpi-value { color:var(--ink); font-size:27px; line-height:1; font-weight:880; letter-spacing:-.035em; }
        .exec-kpi-foot { color:#7A8795; font-size:10px; margin-top:7px; min-height:15px; }
        .exec-mini-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:9px; margin:.15rem 0 .8rem; }
        .exec-mini { background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:9px 10px; }
        .exec-mini-label { color:#748295; font-size:8.8px; font-weight:800; text-transform:uppercase; letter-spacing:.07em; }
        .exec-mini-value { color:#173A5E; font-size:17px; font-weight:850; margin-top:2px; }

        /* Login compacto · pensado primero para celular */
        .login-brand {
            max-width: 460px;
            margin: 2.2vh auto 12px;
            text-align: center;
            padding: 0 12px;
        }
        .login-brand-kicker {
            display:inline-flex;
            align-items:center;
            gap:7px;
            padding:5px 9px;
            border-radius:999px;
            background:#EAF2FF;
            border:1px solid #CFDDF7;
            color:#174EA6;
            font-size:9px;
            font-weight:850;
            letter-spacing:.10em;
            text-transform:uppercase;
        }
        .login-brand-title {
            color:var(--ink);
            font-size:30px;
            line-height:1.04;
            font-weight:880;
            letter-spacing:-.035em;
            margin:10px 0 5px;
        }
        .login-brand-sub {
            color:#667085;
            font-size:11.5px;
            line-height:1.35;
            margin:0;
        }
        .login-form-title {
            font-size:19px;
            line-height:1.1;
            color:var(--ink);
            font-weight:850;
            margin-bottom:2px;
        }
        .login-form-copy {
            color:#7A8795;
            font-size:10.5px;
            margin-bottom:8px;
        }
        .login-secure {
            display:flex;
            justify-content:center;
            align-items:center;
            gap:6px;
            color:#667085;
            font-size:9.5px;
            margin-top:8px;
        }
        .login-secure-dot {
            width:6px;
            height:6px;
            border-radius:50%;
            background:#12B76A;
            box-shadow:0 0 0 3px rgba(18,183,106,.10);
        }

        #MainMenu { visibility:hidden; }
        footer { visibility:hidden; }
        /* Mantener el control lateral disponible sin convertir
           la barra nativa de Streamlit en protagonista. */
        header[data-testid="stHeader"] {
            display:block !important;
            visibility:visible !important;
            background:transparent !important;
            z-index:999990 !important;
        }

        [data-testid="stToolbar"] {
            display:flex !important;
            visibility:visible !important;
            opacity:1 !important;
        }

        /* Ocultar enlaces accesorios como Fork / GitHub,
           pero conservar los controles internos necesarios. */
        header[data-testid="stHeader"] a {
            display:none !important;
        }

        [data-testid="stDecoration"] { display:none !important; }
        .stAppDeployButton { display:none !important; }

        /* KPIs compactos para vistas operativas */
        .planner-kpi-grid {
            display:grid;
            grid-template-columns:repeat(3,minmax(0,1fr));
            gap:10px;
            margin:.2rem 0 .7rem;
        }
        .planner-kpi-card {
            position:relative;
            overflow:hidden;
            background:linear-gradient(180deg,#FFFFFF 0%,#FBFCFE 100%);
            border:1px solid #DCE5EE;
            border-radius:16px;
            padding:12px 13px 11px;
            box-shadow:0 8px 20px rgba(11,31,51,.05);
        }
        .planner-kpi-card:before {
            content:"";
            position:absolute;
            inset:0 auto 0 0;
            width:3px;
            background:#155EEF;
        }
        .planner-kpi-card.good:before { background:#079455; }
        .planner-kpi-card.warn:before { background:#F79009; }
        .planner-kpi-card.risk:before { background:#D92D20; }
        .planner-kpi-card.neutral:before { background:#5B7895; }
        .planner-kpi-label {
            color:#667085;
            font-size:9px;
            font-weight:800;
            text-transform:uppercase;
            letter-spacing:.08em;
            margin-bottom:4px;
        }
        .planner-kpi-value {
            color:var(--ink);
            font-size:26px;
            line-height:1;
            font-weight:880;
            letter-spacing:-.035em;
        }
        .planner-kpi-foot {
            color:#7A8795;
            font-size:9.5px;
            margin-top:5px;
            min-height:12px;
            line-height:1.2;
        }


        /* Curva S · estado en vivo */
        .curve-live-strip {
            display:flex;
            align-items:center;
            flex-wrap:wrap;
            gap:7px;
            margin:.18rem 0 .55rem;
            padding:7px 9px;
            border:1px solid #DCE5EE;
            border-radius:11px;
            background:linear-gradient(180deg,#FFFFFF 0%,#F8FAFC 100%);
            box-shadow:0 4px 12px rgba(11,31,51,.035);
            color:#53657A;
            font-size:10px;
            font-weight:700;
        }
        .curve-live-now {
            display:inline-flex;
            align-items:center;
            gap:6px;
            color:#173A5E;
            font-weight:850;
            padding-right:3px;
        }
        .curve-live-now:before {
            content:"";
            width:7px;
            height:7px;
            border-radius:50%;
            background:#0EA5E9;
            box-shadow:0 0 0 4px rgba(14,165,233,.10);
        }
        .curve-chip {
            display:inline-flex;
            align-items:center;
            gap:4px;
            padding:4px 7px;
            border-radius:999px;
            background:#F5F8FC;
            border:1px solid #E1E8F0;
            color:#53657A;
        }
        .curve-chip strong { color:#0B1F33; font-weight:850; }
        .curve-chip.plan strong { color:#155EEF; }
        .curve-chip.real strong { color:#D92D20; }
        .curve-chip.good strong { color:#079455; }
        .curve-chip.risk strong { color:#D92D20; }

        @media (max-width: 1100px) {
            .exec-kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .exec-mini-grid { grid-template-columns:repeat(3,minmax(0,1fr)); }
        }

        /* ==================================================
           NAVEGACIÓN RESPONSIVE · sidebar siempre recuperable
           ================================================== */

        /* Compatibilidad con distintas versiones de Streamlit. */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display:flex !important;
            visibility:visible !important;
            opacity:1 !important;
            position:fixed !important;
            top:9px !important;
            left:10px !important;
            width:42px !important;
            height:42px !important;
            z-index:1000005 !important;
            pointer-events:auto !important;
        }

        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="collapsedControl"] button {
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            width:42px !important;
            min-width:42px !important;
            height:42px !important;
            min-height:42px !important;
            padding:0 !important;
            border:1px solid #D7E2EC !important;
            background:rgba(255,255,255,.97) !important;
            color:#0B1F33 !important;
            border-radius:12px !important;
            box-shadow:0 7px 20px rgba(11,31,51,.14) !important;
            backdrop-filter:blur(10px);
        }

        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="collapsedControl"] svg {
            color:#0B1F33 !important;
            fill:currentColor !important;
            width:20px !important;
            height:20px !important;
        }

        /* El control de cierre dentro del sidebar también debe ser táctil. */
        [data-testid="stSidebarCollapseButton"] button {
            min-width:38px !important;
            min-height:38px !important;
            border-radius:10px !important;
        }

        /* En escritorio dejamos una zona segura para que el botón
           de reapertura no se pierda detrás del contenido. */
        @media (min-width: 769px) {
            header[data-testid="stHeader"] {
                height:54px !important;
            }

            .block-container {
                padding-top:1.15rem;
            }

            [data-testid="stSidebarCollapsedControl"],
            [data-testid="collapsedControl"] {
                top:8px !important;
                left:12px !important;
            }
        }

        /* MOBILE UX: menos scroll, mejor lectura y controles táctiles */
        @media (max-width: 768px) {

            /* La cabecera nativa queda como una franja técnica mínima.
               El contenido empieza DESPUÉS de ella para que nunca tape
               el título de PDP Control Center. */
            header[data-testid="stHeader"] {
                display:block !important;
                height:52px !important;
                background:rgba(248,250,252,.96) !important;
                backdrop-filter:blur(12px);
                border-bottom:1px solid rgba(221,229,238,.78);
                z-index:999990 !important;
            }

            [data-testid="stToolbar"] {
                display:flex !important;
                visibility:visible !important;
                opacity:1 !important;
            }

            /* Botón de navegación: siempre visible y con zona táctil real. */
            [data-testid="stSidebarCollapsedControl"],
            [data-testid="collapsedControl"] {
                top:5px !important;
                left:8px !important;
                width:42px !important;
                height:42px !important;
            }

            [data-testid="stSidebarCollapsedControl"] button,
            [data-testid="collapsedControl"] button {
                width:42px !important;
                height:42px !important;
                min-height:42px !important;
                padding:0 !important;
            }

            .stAppDeployButton { display:none !important; }

            /* 52 px de cabecera + respiración visual.
               Esto elimina el solapamiento observado en celular. */
            .block-container {
                padding-top:3.65rem !important;
                padding-left:.62rem;
                padding-right:.62rem;
                padding-bottom:1.6rem;
            }

            /* Cuando el sidebar está abierto, no necesita el espacio
               superior extra del contenido principal. */
            [data-testid="stSidebar"] .block-container {
                padding-top:.65rem !important;
            }

            /* El primer encabezado del aplicativo respira debajo
               del botón de navegación y se mantiene completamente visible. */
            .app-topbar {
                margin-top:0 !important;
                position:relative;
                z-index:1;
            }

            .page-intro {
                position:relative;
                z-index:1;
            }


            [data-testid="stSidebar"] {
                width:min(86vw, 292px) !important;
            }

            [data-testid="stSidebar"] .block-container {
                padding:.55rem .65rem 1rem;
            }

            [data-testid="stSidebar"] [role="radiogroup"] label {
                min-height:42px;
                display:flex;
                align-items:center;
                padding:.48rem .58rem;
                margin:.10rem 0;
                border-radius:9px;
            }

            .stButton > button,
            [data-testid="stFormSubmitButton"] > button,
            .stDownloadButton > button {
                min-height:46px !important;
                border-radius:12px !important;
                font-size:13px !important;
            }

            [data-baseweb="input"] > div,
            [data-baseweb="textarea"] > div,
            [data-baseweb="select"] > div {
                min-height:44px;
                border-radius:10px !important;
            }

            [data-testid="stForm"] {
                padding:.82rem .82rem .92rem;
                border-radius:14px !important;
            }

            [data-testid="stMetric"] {
                padding:.70rem .72rem;
                border-radius:12px;
            }

            [data-testid="stMetricLabel"] {
                font-size:10px !important;
            }

            [data-testid="stMetricValue"] {
                font-size:22px !important;
            }

            hr {
                margin-top:.72rem !important;
                margin-bottom:.72rem !important;
            }

            .mainin-header {
                border-radius:14px;
                padding:11px 12px 10px;
                margin-bottom:.65rem;
                box-shadow:0 8px 22px rgba(6,24,39,.13);
            }

            .mainin-head-top {
                margin-bottom:6px;
                gap:7px;
            }

            .mainin-kicker {
                font-size:8px;
                letter-spacing:.09em;
                gap:5px;
            }

            .mainin-kicker:before {
                width:12px;
            }

            .mainin-status {
                padding:4px 7px;
                font-size:8.5px;
            }

            .mainin-status-dot {
                width:6px;
                height:6px;
                box-shadow:0 0 0 3px rgba(50,213,131,.10);
            }

            .mainin-title {
                font-size:20px;
                line-height:1.08;
                margin-bottom:3px;
                letter-spacing:-.025em;
            }

            .mainin-subtitle {
                display:none;
            }

            .mainin-area-row {
                gap:4px;
                margin-top:7px;
            }

            .mainin-chip {
                padding:4px 6px;
                border-radius:7px;
                font-size:8px;
            }

            .mainin-chip:nth-child(3) {
                display:none;
            }

            .executive-title-row {
                align-items:flex-start;
                flex-direction:column;
                gap:5px;
                margin:.1rem 0 .52rem;
            }

            .executive-title {
                font-size:19px;
                line-height:1.12;
            }

            .executive-subtitle {
                font-size:10.5px;
                line-height:1.35;
                margin-top:2px;
            }

            .executive-badge {
                padding:4px 7px;
                font-size:8.5px;
            }

            .exec-meta-line {
                gap:4px;
                margin:.10rem 0 .50rem;
            }

            .exec-meta-pill {
                padding:4px 6px;
                border-radius:7px;
                font-size:8.5px;
            }

            .exec-kpi-grid {
                grid-template-columns:repeat(2,minmax(0,1fr));
                gap:7px;
                margin:.12rem 0 .55rem;
            }

            .exec-kpi-card {
                border-radius:12px;
                padding:10px 10px 9px 12px;
                box-shadow:0 5px 14px rgba(11,31,51,.045);
            }

            .exec-kpi-label {
                font-size:8px;
                margin-bottom:4px;
                letter-spacing:.055em;
            }

            .exec-kpi-value {
                font-size:21px;
            }

            .exec-kpi-foot {
                font-size:8.5px;
                margin-top:4px;
                min-height:12px;
                line-height:1.2;
            }

            .exec-mini-grid {
                grid-template-columns:repeat(2,minmax(0,1fr));
                gap:6px;
                margin:.10rem 0 .55rem;
            }

            .exec-mini {
                border-radius:10px;
                padding:7px 8px;
            }

            .exec-mini-label { font-size:7.8px; }
            .exec-mini-value { font-size:15px; }

            [data-testid="stPlotlyChart"] {
                border-radius:12px;
                padding:2px 2px 0;
                box-shadow:0 4px 14px rgba(11,31,51,.04);
            }

            [data-testid="stDataFrame"] {
                border-radius:11px;
                box-shadow:none;
            }

            [data-testid="stFileUploader"] {
                padding:5px;
                border-radius:11px;
            }

            [data-testid="stExpander"] {
                border-radius:11px !important;
                box-shadow:none;
            }

            .login-brand {
                margin:.9rem auto 8px;
            }

            .login-brand-kicker {
                font-size:8px;
                padding:4px 7px;
            }

            .login-brand-title {
                font-size:24px;
                margin:8px 0 3px;
            }

            .login-brand-sub {
                font-size:10.5px;
            }

            .login-form-title {
                font-size:18px;
            }

            .login-form-copy {
                font-size:10px;
                margin-bottom:6px;
            }
        }

        @media (max-width: 420px) {
            .block-container {
                padding-left:.48rem;
                padding-right:.48rem;
            }

            .mainin-title { font-size:18px; }
            .mainin-chip { font-size:7.7px; }
            .exec-kpi-value { font-size:20px; }
            .exec-kpi-foot { display:none; }
            .planner-kpi-grid { grid-template-columns:1fr 1fr; }
            .planner-kpi-foot { display:none; }
            .curve-live-strip {
                gap:5px;
                padding:6px 7px;
                font-size:9px;
            }
            .curve-chip { padding:3px 6px; }
            .login-brand-title { font-size:22px; }
        }


        /* ==================================================
           V7 · MAININ OPERATIONAL EXPERIENCE
           Premium, role-aware, responsive, touch-friendly
           ================================================== */

        :root {
            --navy-950:#061625;
            --navy-900:#0A2036;
            --navy-800:#103556;
            --brand-600:#2563EB;
            --brand-500:#3B82F6;
            --sky-400:#38BDF8;
            --surface:#FFFFFF;
            --surface-2:#F8FAFC;
            --surface-3:#F1F5F9;
            --border:#DCE4ED;
            --text:#0F2438;
            --text-2:#52677B;
            --success:#0E9F6E;
            --warning:#D97706;
            --danger:#DC2626;
            --radius-lg:18px;
            --radius-md:13px;
            --elev-1:0 1px 2px rgba(15,36,56,.035), 0 8px 24px rgba(15,36,56,.045);
            --elev-2:0 14px 34px rgba(7,30,51,.10);
        }

        /* Más aire útil, menos decoración vacía */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background:
                radial-gradient(circle at 88% -2%, rgba(59,130,246,.075), transparent 25rem),
                linear-gradient(180deg,#FBFCFE 0%,#F4F7FA 100%) !important;
        }

        .block-container {
            max-width: 1500px;
            padding-top: .72rem;
            padding-bottom: 2.2rem;
        }

        /* --------------------------------------------------
           Sidebar / navegación
           -------------------------------------------------- */
        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 0% 0%, rgba(56,189,248,.11), transparent 15rem),
                linear-gradient(180deg,var(--navy-950) 0%,#0A2540 58%,#0B2A49 100%) !important;
            box-shadow: 12px 0 36px rgba(6,22,37,.10);
        }

        [data-testid="stSidebar"] .block-container {
            padding: .68rem .72rem 1rem;
        }

        .brand-lockup {
            display:flex;
            align-items:center;
            gap:10px;
            margin:2px 2px 10px;
            padding:7px 5px 9px;
        }
        .brand-mark {
            width:37px;
            height:37px;
            border-radius:12px;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#FFF;
            font-size:17px;
            font-weight:900;
            letter-spacing:-.05em;
            background:linear-gradient(145deg,#2F6FED,#38BDF8);
            box-shadow:0 8px 18px rgba(37,99,235,.30), inset 0 1px 0 rgba(255,255,255,.22);
        }
        .brand-copy { min-width:0; }
        .brand-name {
            color:#FFFFFF;
            font-size:13px;
            font-weight:850;
            letter-spacing:.06em;
            line-height:1.1;
        }
        .brand-product {
            color:#8EA9C1;
            font-size:9px;
            font-weight:700;
            letter-spacing:.08em;
            margin-top:3px;
            text-transform:uppercase;
        }

        .nav-label {
            color:#738EA7;
            font-size:8px;
            font-weight:850;
            letter-spacing:.14em;
            text-transform:uppercase;
            margin:12px 6px 5px;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap:2px;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            min-height:42px;
            padding:.54rem .66rem !important;
            margin:.08rem 0 !important;
            border-radius:11px !important;
            border:1px solid transparent !important;
            background:transparent;
            transition:background .14s ease, border-color .14s ease, transform .14s ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background:rgba(255,255,255,.065) !important;
            border-color:rgba(255,255,255,.065) !important;
            transform:translateX(1px);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background:linear-gradient(90deg,rgba(47,111,237,.30),rgba(56,189,248,.08)) !important;
            border-color:rgba(112,181,255,.20) !important;
            box-shadow:inset 3px 0 0 #67C3FF, 0 5px 14px rgba(1,12,23,.10) !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label p {
            color:#DCE8F4 !important;
            font-size:11.5px !important;
            font-weight:700 !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
            color:#FFFFFF !important;
        }

        .sidebar-user-card {
            padding:10px 10px 9px;
            margin:4px 0 7px;
            border-radius:13px;
            background:linear-gradient(180deg,rgba(255,255,255,.065),rgba(255,255,255,.035));
            border:1px solid rgba(255,255,255,.09);
            box-shadow:inset 0 1px 0 rgba(255,255,255,.04);
        }
        .sidebar-avatar {
            width:32px;
            height:32px;
            border-radius:10px;
            font-size:12px;
        }
        .sidebar-user-name { font-size:11.5px; }
        .sidebar-user-caption { font-size:8.8px; color:#8099B1; }
        .sidebar-pill {
            padding:3px 6px;
            font-size:8.5px;
            background:rgba(255,255,255,.045);
        }

        [data-testid="stSidebar"] .stButton > button {
            min-height:36px !important;
            border-radius:10px !important;
            font-size:10.5px !important;
            background:rgba(255,255,255,.045) !important;
            border-color:rgba(255,255,255,.10) !important;
            box-shadow:none !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background:rgba(255,255,255,.08) !important;
        }

        /* --------------------------------------------------
           Header de aplicación: compacto y de alta jerarquía
           -------------------------------------------------- */
        .app-topbar {
            position:relative;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:18px;
            overflow:hidden;
            min-height:82px;
            padding:15px 17px 14px;
            margin-bottom:.72rem;
            color:#FFF;
            background:
                radial-gradient(circle at 92% 20%, rgba(56,189,248,.19), transparent 16rem),
                linear-gradient(118deg,#071A2C 0%,#0B2A49 58%,#123C64 100%);
            border:1px solid rgba(255,255,255,.08);
            border-radius:17px;
            box-shadow:var(--elev-2);
        }
        .app-topbar:after {
            content:"";
            position:absolute;
            width:260px;
            height:260px;
            right:-120px;
            top:-160px;
            border-radius:50%;
            border:1px solid rgba(125,211,252,.15);
            box-shadow:0 0 0 34px rgba(125,211,252,.025),0 0 0 68px rgba(125,211,252,.018);
            pointer-events:none;
        }
        .topbar-left { position:relative; z-index:2; min-width:0; }
        .topbar-kicker {
            color:#8DB9DC;
            font-size:8px;
            font-weight:850;
            letter-spacing:.14em;
            text-transform:uppercase;
            margin-bottom:4px;
        }
        .topbar-title {
            color:#FFF;
            font-size:clamp(21px,2vw,30px);
            font-weight:880;
            letter-spacing:-.035em;
            line-height:1.03;
            white-space:nowrap;
        }
        .topbar-subtitle {
            color:#AFC4D7;
            font-size:10.5px;
            margin-top:4px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
            max-width:780px;
        }
        .topbar-context {
            position:relative;
            z-index:2;
            display:flex;
            align-items:center;
            justify-content:flex-end;
            flex-wrap:wrap;
            gap:6px;
        }
        .context-pill {
            display:inline-flex;
            align-items:center;
            gap:5px;
            padding:5px 8px;
            border-radius:999px;
            border:1px solid rgba(255,255,255,.11);
            background:rgba(255,255,255,.055);
            color:#D7E6F3;
            font-size:8.8px;
            font-weight:750;
            white-space:nowrap;
        }
        .context-dot {
            width:6px;
            height:6px;
            border-radius:50%;
            background:#34D399;
            box-shadow:0 0 0 3px rgba(52,211,153,.09);
        }

        /* --------------------------------------------------
           Encabezados de páginas / accesos
           -------------------------------------------------- */
        .page-intro {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:14px;
            margin:.08rem 0 .78rem;
            padding:10px 12px;
            background:linear-gradient(180deg,#FFFFFF 0%, #F9FBFD 100%);
            border:1px solid #E3EAF2;
            border-radius:16px;
            box-shadow:0 8px 22px rgba(15,36,56,.045);
        }
        .page-intro-main {
            display:flex;
            align-items:center;
            gap:11px;
            min-width:0;
        }
        .page-icon {
            width:36px;
            height:36px;
            flex:0 0 36px;
            display:flex;
            align-items:center;
            justify-content:center;
            border-radius:11px;
            color:#174EA6;
            font-size:17px;
            background:linear-gradient(145deg,#EEF5FF,#E7F1FF);
            border:1px solid #D5E4FA;
            box-shadow:0 4px 10px rgba(37,99,235,.08);
        }
        .page-overline {
            color:#6B7E90;
            font-size:8px;
            font-weight:850;
            letter-spacing:.13em;
            text-transform:uppercase;
            line-height:1.1;
            margin-bottom:3px;
        }
        .page-title {
            color:var(--text);
            font-size:21px;
            font-weight:860;
            letter-spacing:-.028em;
            line-height:1.08;
        }
        .page-subtitle {
            color:#718096;
            font-size:10.5px;
            line-height:1.35;
            margin-top:3px;
        }
        .page-badge {
            flex:0 0 auto;
            padding:5px 8px;
            border-radius:999px;
            border:1px solid #D8E2EC;
            background:#FFFFFF;
            color:#4D647A;
            font-size:8.5px;
            font-weight:800;
            box-shadow:0 3px 9px rgba(15,36,56,.035);
        }

        /* Secciones nativas más editoriales */
        h3 {
            font-size:15px !important;
            line-height:1.2 !important;
            margin-top:1.05rem !important;
            margin-bottom:.42rem !important;
            letter-spacing:-.015em !important;
        }
        h3:after {
            content:"";
            display:block;
            width:28px;
            height:2px;
            margin-top:5px;
            border-radius:999px;
            background:linear-gradient(90deg,#2563EB,#38BDF8);
            opacity:.75;
        }

        /* --------------------------------------------------
           Controles, formularios y datos
           -------------------------------------------------- */
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        [data-baseweb="select"] > div {
            border-radius:10px !important;
            border-color:#D6E0E9 !important;
            box-shadow:0 1px 2px rgba(15,36,56,.02) !important;
        }
        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="textarea"] > div:focus-within,
        [data-baseweb="select"] > div:focus-within {
            border-color:#7BA7F7 !important;
            box-shadow:0 0 0 3px rgba(37,99,235,.09) !important;
        }

        .stButton > button,
        [data-testid="stFormSubmitButton"] > button,
        .stDownloadButton > button {
            border-radius:10px !important;
            min-height:40px;
            font-size:11px !important;
            font-weight:760 !important;
            letter-spacing:.005em;
            box-shadow:0 2px 6px rgba(15,36,56,.035);
        }
        button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            background:linear-gradient(135deg,#2563EB 0%,#1557D6 100%) !important;
            box-shadow:0 7px 16px rgba(37,99,235,.18) !important;
        }

        [data-testid="stForm"] {
            padding:1rem 1rem 1.08rem !important;
            border-radius:14px !important;
            box-shadow:var(--elev-1) !important;
        }

        [data-testid="stMetric"] {
            border-radius:13px !important;
            padding:.78rem .86rem !important;
            box-shadow:var(--elev-1) !important;
        }

        [data-testid="stDataFrame"] {
            border-radius:12px !important;
            border-color:#DDE5EC !important;
            box-shadow:0 5px 16px rgba(15,36,56,.035) !important;
        }

        [data-testid="stPlotlyChart"] {
            border-radius:14px !important;
            padding:5px 5px 0 !important;
            box-shadow:var(--elev-1) !important;
        }

        [data-testid="stFileUploader"] {
            border-radius:13px !important;
            background:linear-gradient(180deg,#FFF,#FBFCFE) !important;
            border:1px dashed #B7C8D8 !important;
        }

        [data-testid="stExpander"] {
            border-radius:12px !important;
            box-shadow:none !important;
        }

        /* Tabs como selector segmentado */
        [data-baseweb="tab-list"] {
            gap:4px;
            background:#EDF2F7;
            border-radius:11px;
            padding:4px;
            width:max-content;
            max-width:100%;
        }
        [data-baseweb="tab"] {
            min-height:34px;
            border-radius:8px;
            padding:6px 10px;
            color:#5C7084 !important;
            font-size:10px !important;
            font-weight:750 !important;
        }
        [data-baseweb="tab"][aria-selected="true"] {
            background:#FFFFFF !important;
            color:#174EA6 !important;
            box-shadow:0 3px 8px rgba(15,36,56,.07);
        }
        [data-baseweb="tab-highlight"] { display:none !important; }

        /* Alertas más discretas */
        [data-testid="stAlert"] {
            border-radius:11px !important;
            box-shadow:none !important;
            font-size:10.5px !important;
        }

        /* --------------------------------------------------
           Login premium: memorable, pero sin exceso de texto
           -------------------------------------------------- */
        .login-shell {
            max-width:780px;
            margin:3vh auto 10px;
        }
        .login-brandline {
            display:flex;
            align-items:center;
            justify-content:center;
            gap:9px;
            margin-bottom:10px;
        }
        .login-symbol {
            width:35px;
            height:35px;
            border-radius:11px;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#FFF;
            font-weight:900;
            font-size:16px;
            background:linear-gradient(145deg,#2563EB,#38BDF8);
            box-shadow:0 8px 18px rgba(37,99,235,.22);
        }
        .login-brandtext {
            color:#15314D;
            font-size:11px;
            font-weight:850;
            letter-spacing:.10em;
            text-transform:uppercase;
        }
        .login-panel {
            position:relative;
            overflow:hidden;
            border-radius:18px;
            padding:18px 18px 15px;
            color:#FFF;
            background:
                radial-gradient(circle at 90% 15%,rgba(56,189,248,.20),transparent 12rem),
                linear-gradient(120deg,#071A2C,#0D3155 65%,#123E69);
            box-shadow:0 18px 42px rgba(7,30,51,.16);
            margin-bottom:11px;
        }
        .login-panel:before {
            content:"";
            position:absolute;
            inset:0;
            background:linear-gradient(90deg,rgba(125,211,252,.08) 1px,transparent 1px),linear-gradient(rgba(125,211,252,.055) 1px,transparent 1px);
            background-size:30px 30px;
            mask-image:linear-gradient(90deg,transparent,rgba(0,0,0,.70));
            pointer-events:none;
        }
        .login-panel-row {
            position:relative;
            z-index:2;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:12px;
        }
        .login-product {
            color:#FFFFFF;
            font-size:25px;
            line-height:1.02;
            font-weight:880;
            letter-spacing:-.035em;
        }
        .login-location {
            color:#9BB9D2;
            font-size:9.5px;
            margin-top:4px;
            font-weight:700;
        }
        .login-mini-status {
            display:flex;
            flex-wrap:wrap;
            justify-content:flex-end;
            gap:5px;
        }
        .login-mini-status span {
            border:1px solid rgba(255,255,255,.11);
            background:rgba(255,255,255,.055);
            color:#D7E7F4;
            border-radius:999px;
            padding:5px 7px;
            font-size:8px;
            font-weight:800;
            letter-spacing:.035em;
        }
        .login-card-title {
            color:var(--text);
            font-size:18px;
            line-height:1.05;
            font-weight:850;
            margin:1px 0 3px;
        }
        .login-card-sub {
            color:#7B8B9B;
            font-size:9.5px;
            margin-bottom:7px;
        }
        .login-foot {
            display:flex;
            align-items:center;
            justify-content:center;
            gap:6px;
            margin-top:7px;
            color:#748496;
            font-size:8.8px;
        }
        .login-foot-dot {
            width:6px;
            height:6px;
            border-radius:50%;
            background:#10B981;
            box-shadow:0 0 0 3px rgba(16,185,129,.09);
        }

        /* --------------------------------------------------
           Responsive: jerarquía, no miniaturización
           -------------------------------------------------- */
        @media (max-width: 768px) {
            .block-container {
                padding:.48rem .54rem 1.4rem;
            }

            [data-testid="stSidebar"] {
                width:min(87vw,286px) !important;
            }

            .app-topbar {
                min-height:auto;
                padding:11px 11px 10px;
                border-radius:14px;
                margin-bottom:.52rem;
                align-items:flex-start;
            }
            .topbar-kicker { font-size:7px; }
            .topbar-title {
                font-size:18px;
                white-space:normal;
            }
            .topbar-subtitle { display:none; }
            .topbar-context {
                gap:4px;
                max-width:48%;
            }
            .context-pill {
                font-size:7.4px;
                padding:4px 6px;
            }
            .context-pill.context-secondary { display:none; }

            .page-intro {
                gap:8px;
                padding-bottom:7px;
                margin-bottom:.55rem;
            }
            .page-intro-main { gap:8px; }
            .page-icon {
                width:32px;
                height:32px;
                flex-basis:32px;
                border-radius:10px;
                font-size:15px;
            }
            .page-overline { font-size:7px; }
            .page-title { font-size:18px; }
            .page-subtitle {
                font-size:9.5px;
                max-width:78vw;
            }
            .page-badge { display:none; }

            .exec-kpi-grid {
                grid-template-columns:repeat(2,minmax(0,1fr)) !important;
                gap:6px !important;
            }
            .exec-kpi-card {
                padding:9px 9px 8px 11px !important;
                border-radius:11px !important;
            }
            .exec-kpi-label { font-size:7.4px !important; }
            .exec-kpi-value { font-size:20px !important; }
            .exec-kpi-foot { display:none !important; }

            .exec-mini-grid {
                grid-template-columns:repeat(2,minmax(0,1fr)) !important;
                gap:5px !important;
            }
            .exec-mini {
                padding:6px 7px !important;
                border-radius:9px !important;
            }

            [data-testid="stForm"] { padding:.76rem !important; }
            [data-testid="stMetric"] { padding:.64rem .68rem !important; }

            .stButton > button,
            [data-testid="stFormSubmitButton"] > button,
            .stDownloadButton > button {
                min-height:44px !important;
                border-radius:11px !important;
                font-size:12px !important;
            }

            [data-baseweb="input"] > div,
            [data-baseweb="textarea"] > div,
            [data-baseweb="select"] > div {
                min-height:43px;
            }

            [data-baseweb="tab-list"] {
                width:100%;
                overflow-x:auto;
            }

            .login-shell {
                margin:.65rem auto 6px;
                max-width:440px;
            }
            .login-panel {
                padding:14px 13px 12px;
                border-radius:15px;
                margin-bottom:8px;
            }
            .login-panel-row {
                align-items:flex-start;
            }
            .login-product { font-size:21px; }
            .login-mini-status { max-width:42%; }
            .login-mini-status span { font-size:7px; padding:4px 5px; }
            .login-brandline { margin-bottom:7px; }
        }

        @media (max-width: 420px) {
            .block-container { padding-left:.42rem; padding-right:.42rem; }
            .app-topbar { padding:10px; }
            .topbar-title { font-size:16.5px; }
            .context-pill { padding:4px 5px; }
            .page-title { font-size:17px; }
            .page-subtitle { display:none; }
            .login-mini-status span:nth-child(3) { display:none; }
            .login-product { font-size:20px; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def mostrar_header_profesional(
    subtitulo="Sistema integrado de seguimiento y control de la Parada de Planta",
    estado="Sistema operativo",
    rol="",
    area=""
):
    rol_txt = str(rol or "").strip()
    area_txt = str(area or estado or "").strip()

    rol_html = (
        f'<span class="context-pill context-secondary">{rol_txt}</span>'
        if rol_txt
        else ''
    )

    st.markdown(
        f"""
        <div class="app-topbar">
            <div class="topbar-left">
                <div class="topbar-kicker">MAININ · PROJECT DELIVERY PLATFORM</div>
                <div class="topbar-title">PDP Control Center · Quellaveco</div>
                <div class="topbar-subtitle">{subtitulo}</div>
            </div>
            <div class="topbar-context">
                <span class="context-pill"><span class="context-dot"></span> Operativo</span>
                {rol_html}
                <span class="context-pill">{area_txt}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def mostrar_titulo_ejecutivo(
    titulo,
    subtitulo="",
    badge=""
):
    badge_html = (
        f'<span class="executive-badge">{badge}</span>'
        if badge
        else ''
    )

    st.markdown(
        f"""
        <div class="executive-title-row">
            <div>
                <div class="executive-eyebrow">PDP · QUELLAVECO</div>
                <div class="executive-title">{titulo}</div>
                <div class="executive-subtitle">{subtitulo}</div>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )



ICONOS_MENU = {
    "Dashboard general": "◫",
    "Importar planificación": "⇧",
    "Administrar OTs": "▤",
    "Reportes": "↗",
    "Dashboard": "◫",
    "Registrar avance": "+",
    "Detalle por OT": "⌁",
    "Evidencias": "▧",
}


def etiqueta_menu(nombre):
    """Etiqueta visual sin cambiar el valor lógico usado por el aplicativo."""
    return f"{ICONOS_MENU.get(nombre, '•')}   {nombre}"


def mostrar_etiqueta_navegacion(texto="Navegación"):
    st.markdown(
        f'<div class="nav-label">{texto}</div>',
        unsafe_allow_html=True
    )


def mostrar_acceso_pagina(
    titulo,
    subtitulo="",
    icono="◫",
    contexto="PDP · QUELLAVECO",
    badge=""
):
    badge_html = (
        f'<div class="page-badge">{badge}</div>'
        if badge
        else ''
    )

    st.markdown(
        f"""
        <div class="page-intro">
            <div class="page-intro-main">
                <div class="page-icon">{icono}</div>
                <div>
                    <div class="page-overline">{contexto}</div>
                    <div class="page-title">{titulo}</div>
                    <div class="page-subtitle">{subtitulo}</div>
                </div>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def mostrar_resumen_ejecutivo_dashboard(
    kpis,
    total_ots,
    vista
):
    plan = float(kpis.get("avance_plan", 0) or 0)
    real = float(kpis.get("avance_general", 0) or 0)
    spi = float(kpis.get("spi", 0) or 0)
    desviacion = real - plan

    if desviacion >= -5:
        clase = "good"
        estado = "En línea"
    elif desviacion >= -10:
        clase = "warn"
        estado = "Seguimiento"
    else:
        clase = "risk"
        estado = "Recuperación"

    fecha_actualizacion = (
        pd.Timestamp.now(tz="America/Lima")
        .strftime("%d/%m/%Y %H:%M")
    )

    st.markdown(
        f"""
        <div class="exec-meta-line">
            <span class="exec-meta-pill">Vista: {vista}</span>
            <span class="exec-meta-pill">Actualizado: {fecha_actualizacion}</span>
            <span class="exec-meta-pill">Estado: {estado}</span>
        </div>

        <div class="exec-kpi-grid">
            <div class="exec-kpi-card neutral">
                <div class="exec-kpi-label">Plan actual</div>
                <div class="exec-kpi-value">{plan:.1f}%</div>
                <div class="exec-kpi-foot">Avance esperado a la hora de corte</div>
            </div>
            <div class="exec-kpi-card {clase}">
                <div class="exec-kpi-label">Avance real</div>
                <div class="exec-kpi-value">{real:.1f}%</div>
                <div class="exec-kpi-foot">Último avance acumulado registrado</div>
            </div>
            <div class="exec-kpi-card {clase}">
                <div class="exec-kpi-label">Desviación</div>
                <div class="exec-kpi-value">{desviacion:+.1f} pp</div>
                <div class="exec-kpi-foot">REAL menos PLAN</div>
            </div>
            <div class="exec-kpi-card {clase}">
                <div class="exec-kpi-label">SPI</div>
                <div class="exec-kpi-value">{spi:.2f}</div>
                <div class="exec-kpi-foot">Índice de desempeño del cronograma</div>
            </div>
        </div>

        <div class="exec-mini-grid">
            <div class="exec-mini">
                <div class="exec-mini-label">OTs</div>
                <div class="exec-mini-value">{int(total_ots)}</div>
            </div>
            <div class="exec-mini">
                <div class="exec-mini-label">Actividades</div>
                <div class="exec-mini-value">{int(kpis.get('actividades', 0) or 0)}</div>
            </div>
            <div class="exec-mini">
                <div class="exec-mini-label">Culminadas</div>
                <div class="exec-mini-value">{int(kpis.get('culminadas', 0) or 0)}</div>
            </div>
            <div class="exec-mini">
                <div class="exec-mini-label">En ejecución</div>
                <div class="exec-mini-value">{int(kpis.get('parciales', 0) or 0)}</div>
            </div>
            <div class="exec-mini">
                <div class="exec-mini-label">No iniciadas</div>
                <div class="exec-mini-value">{int(kpis.get('no_iniciadas', 0) or 0)}</div>
            </div>
            <div class="exec-mini">
                <div class="exec-mini-label">HH plan / ganadas</div>
                <div class="exec-mini-value">{float(kpis.get('hh_plan', 0) or 0):.0f} / {float(kpis.get('hh_ganadas', 0) or 0):.0f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


aplicar_estilo_profesional()

# =====================================================
# CONEXIÓN SUPABASE
# =====================================================

@st.cache_resource
def conectar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


@st.cache_resource
def conectar_supabase_admin():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ADMIN_KEY"]

    return create_client(url, key)


supabase = conectar_supabase_admin()
supabase_admin = conectar_supabase_admin()


# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

AREAS = [
    "ELECTRICIDAD",
    "INSTRUMENTACION"
]


USUARIOS_LOGIN = [
    "super_elec",
    "super_inst",
    "planner_elec",
    "planner_inst",
    "adm_quellaveco"
]

ETIQUETAS_USUARIOS_LOGIN = {
    "super_elec": "super_elec · Supervisor Electricidad",
    "super_inst": "super_inst · Supervisor Instrumentación",
    "planner_elec": "planner_elec · Planner Electricidad",
    "planner_inst": "planner_inst · Planner Instrumentación",
    "adm_quellaveco": "adm_quellaveco · Administrador"
}

# =====================================================
# FUNCIONES DE IMPORTACIÓN
# =====================================================

def limpiar_texto(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto == "":
        return None

    return texto


def limpiar_numero(valor, default=None):
    if pd.isna(valor):
        return default

    try:
        return float(valor)
    except Exception:
        return default


def limpiar_entero(valor, default=None):
    if pd.isna(valor):
        return default

    try:
        return int(float(valor))
    except Exception:
        return default


def limpiar_fecha(valor):
    if pd.isna(valor):
        return None

    try:
        fecha = pd.to_datetime(valor)
        return fecha.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None



# =====================================================
# TRATAMIENTO AUTOMÁTICO MANPOWER -> PDP QUELLAVECO
# =====================================================

def _normalizar_columna_manpower(nombre):
    texto = str(nombre or "").replace("\n", " ").strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return " ".join(texto.split())


def _mapa_columnas_manpower(df):
    mapa = {}
    for columna in df.columns:
        clave = _normalizar_columna_manpower(columna)
        if clave and clave not in mapa:
            mapa[clave] = columna
    return mapa


def _texto_manpower(valor):
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if not texto or texto.lower() == "nan":
        return None
    return texto


def _ot_manpower(valor):
    if pd.isna(valor):
        return None

    if isinstance(valor, (int, np.integer)):
        return str(int(valor))

    if isinstance(valor, (float, np.floating)):
        if np.isnan(valor):
            return None
        if float(valor).is_integer():
            return str(int(valor))

    texto = str(valor).strip()
    if not texto or texto.lower() == "nan":
        return None

    if texto.endswith(".0"):
        parte = texto[:-2]
        if parte.replace("-", "").isdigit():
            return parte

    return texto


def _numero_manpower(valor, entero=False):
    if pd.isna(valor):
        return None
    try:
        numero = float(valor)
        if np.isnan(numero):
            return None
        return int(round(numero)) if entero else numero
    except Exception:
        return None


def _fecha_manpower(valor):
    if pd.isna(valor):
        return pd.NaT

    if isinstance(valor, (int, float, np.integer, np.floating)):
        try:
            return (
                pd.Timestamp("1899-12-30")
                + pd.to_timedelta(float(valor), unit="D")
            )
        except Exception:
            return pd.NaT

    return pd.to_datetime(valor, errors="coerce")


def _valor_columna_manpower(row, mapa, nombre_normalizado):
    columna = mapa.get(nombre_normalizado)
    if columna is None:
        return None
    return row.get(columna)


def convertir_hoja_manpower(
    archivo_bytes,
    hoja_fuente,
    empresa_objetivo,
    prefijo_actividad,
    nombre_area
):
    """
    Convierte directamente una hoja ELEC/INST del manpower de Quellaveco
    al formato interno que utiliza el importador PDP.

    Conserva explícitamente:
    - DESCRIPCION TRABAJO -> descripcion_trabajo
    - DESCRIPCION OPERACIÓN -> operacion
    - SSOMA -> ssoma

    La columna descripcion se mantiene por compatibilidad con el resto del
    aplicativo y toma OPERACION; si está vacía usa DESCRIPCION TRABAJO.
    """

    df = pd.read_excel(
        io.BytesIO(archivo_bytes),
        sheet_name=hoja_fuente,
        header=5
    )

    if df.empty:
        raise ValueError(
            f"La hoja {hoja_fuente} no contiene información utilizable."
        )

    mapa = _mapa_columnas_manpower(df)

    columnas_requeridas = [
        "OT",
        "EQUIPO",
        "DESCRIPCION TRABAJO",
        "DESCRIPCION OPERACION",
        "EMPRESA",
        "INICIO",
        "FIN",
        "CANT PERS",
        "DUR (HR)",
        "HH"
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in mapa
    ]

    if faltantes:
        raise ValueError(
            "La hoja no tiene todas las columnas requeridas: "
            + ", ".join(faltantes)
        )

    empresa_objetivo_norm = str(empresa_objetivo).strip().upper()

    actividades = []
    pendientes = []
    hh_completadas = 0
    filas_mainin = 0

    for indice, row in df.iterrows():
        fila_origen = int(indice) + 7

        empresa = _texto_manpower(
            _valor_columna_manpower(row, mapa, "EMPRESA")
        )

        if not empresa:
            continue

        if empresa.strip().upper() != empresa_objetivo_norm:
            continue

        filas_mainin += 1

        ot = _ot_manpower(
            _valor_columna_manpower(row, mapa, "OT")
        )

        equipo = _texto_manpower(
            _valor_columna_manpower(row, mapa, "EQUIPO")
        )

        descripcion_trabajo = _texto_manpower(
            _valor_columna_manpower(
                row,
                mapa,
                "DESCRIPCION TRABAJO"
            )
        )

        operacion = _texto_manpower(
            _valor_columna_manpower(
                row,
                mapa,
                "DESCRIPCION OPERACION"
            )
        )

        ssoma = _texto_manpower(
            _valor_columna_manpower(
                row,
                mapa,
                "SSOMA"
            )
        )

        descripcion_actividad = (
            operacion
            or descripcion_trabajo
        )

        inicio = _fecha_manpower(
            _valor_columna_manpower(row, mapa, "INICIO")
        )

        fin = _fecha_manpower(
            _valor_columna_manpower(row, mapa, "FIN")
        )

        motivo = []

        if not ot:
            motivo.append("Falta OT")

        if not descripcion_actividad:
            motivo.append("Falta DESCRIPCION TRABAJO / OPERACION")

        if pd.isna(inicio) or pd.isna(fin):
            motivo.append("Falta INICIO y/o FIN")

        if motivo:
            pendientes.append({
                "fila_origen": fila_origen,
                "ot": ot or "",
                "equipo": equipo or "",
                "descripcion_trabajo": descripcion_trabajo or "",
                "operacion": operacion or "",
                "ssoma": ssoma or "",
                "motivo": "; ".join(motivo)
            })
            continue

        supervisor = _texto_manpower(
            _valor_columna_manpower(row, mapa, "SUPERVISOR")
        )

        especialidad = _texto_manpower(
            _valor_columna_manpower(row, mapa, "ESPECIALIDAD")
        )

        grupo = _texto_manpower(
            _valor_columna_manpower(row, mapa, "GRUPO")
        )

        area_origen = _texto_manpower(
            _valor_columna_manpower(row, mapa, "AREA")
        )

        puesto_operaciones = _texto_manpower(
            _valor_columna_manpower(
                row,
                mapa,
                "PUESTO DE OPERACIONES"
            )
        )

        partes_seccion = [
            parte
            for parte in [area_origen, puesto_operaciones]
            if parte
        ]
        seccion = " | ".join(partes_seccion) or None

        personal = _numero_manpower(
            _valor_columna_manpower(row, mapa, "CANT PERS"),
            entero=True
        )

        duracion_h = _numero_manpower(
            _valor_columna_manpower(row, mapa, "DUR (HR)")
        )

        hh_plan = _numero_manpower(
            _valor_columna_manpower(row, mapa, "HH")
        )

        tratamiento = None

        if (
            hh_plan is None
            and personal is not None
            and duracion_h is not None
        ):
            hh_plan = float(personal) * float(duracion_h)
            hh_completadas += 1
            tratamiento = "HH completada = Personal × Duración"

        criticidad = _texto_manpower(
            _valor_columna_manpower(row, mapa, "CRITICIDAD")
        )

        actividades.append({
            "ot": ot,
            "codigo_actividad": (
                f"{prefijo_actividad}-{fila_origen:04d}"
            ),
            "descripcion": descripcion_actividad,
            "descripcion_trabajo": descripcion_trabajo,
            "operacion": operacion,
            "ssoma": ssoma,
            "supervisor": supervisor,
            "especialidad": especialidad,
            "grupo": grupo,
            "peso": 1,
            "inicio_plan": inicio.to_pydatetime(),
            "fin_plan": fin.to_pydatetime(),
            "seccion": seccion,
            "personal": personal,
            "duracion_h": duracion_h,
            "hh_plan": hh_plan,
            "fila_origen": fila_origen,
            "criticidad_origen": criticidad,
            "empresa_origen": empresa,
            "tratamiento": tratamiento,
            "_equipo": equipo,
            "_ubicacion_tecnica": _texto_manpower(
                _valor_columna_manpower(
                    row,
                    mapa,
                    "DENOM.UBIC.TECNICA"
                )
            )
        })

    if not actividades:
        raise ValueError(
            f"No se encontraron actividades válidas para {empresa_objetivo}."
        )

    df_actividades_base = pd.DataFrame(actividades)

    df_ots = (
        df_actividades_base[
            [
                "ot",
                "_equipo",
                "descripcion_trabajo",
                "_ubicacion_tecnica",
                "empresa_origen"
            ]
        ]
        .drop_duplicates(subset=["ot"], keep="first")
        .rename(columns={
            "_equipo": "equipo",
            "descripcion_trabajo": "descripcion",
            "_ubicacion_tecnica": "ubicacion_tecnica_origen"
        })
        .reset_index(drop=True)
    )

    columnas_actividades = [
        "ot",
        "codigo_actividad",
        "descripcion",
        "descripcion_trabajo",
        "operacion",
        "ssoma",
        "supervisor",
        "especialidad",
        "grupo",
        "peso",
        "inicio_plan",
        "fin_plan",
        "seccion",
        "personal",
        "duracion_h",
        "hh_plan",
        "fila_origen",
        "criticidad_origen",
        "empresa_origen",
        "tratamiento"
    ]

    df_actividades = (
        df_actividades_base[columnas_actividades]
        .reset_index(drop=True)
    )

    inicio_min = df_actividades["inicio_plan"].min()
    fin_max = df_actividades["fin_plan"].max()

    resumen = {
        "area": nombre_area,
        "empresa": empresa_objetivo,
        "filas_mainin": filas_mainin,
        "ots": len(df_ots),
        "actividades": len(df_actividades),
        "excluidas": len(pendientes),
        "hh_completadas": hh_completadas,
        "inicio": inicio_min,
        "fin": fin_max
    }

    return {
        "ots": df_ots,
        "actividades": df_actividades,
        "pendientes": pd.DataFrame(pendientes),
        "resumen": resumen
    }

def convertir_manpower_quellaveco(archivo_bytes):
    """Convierte ELEC e INST en una sola carga del manpower fuente."""

    libro = pd.ExcelFile(io.BytesIO(archivo_bytes))
    hojas = set(libro.sheet_names)

    configuraciones = [
        {
            "clave": "ELECTRICIDAD",
            "hoja": "ELEC",
            "empresa": "MAININ ELE",
            "prefijo": "ELEC",
            "nombre": "Electricidad"
        },
        {
            "clave": "INSTRUMENTACION",
            "hoja": "INST",
            "empresa": "MAININ INS",
            "prefijo": "INST",
            "nombre": "Instrumentación"
        }
    ]

    resultados = {}

    for config in configuraciones:
        if config["hoja"] not in hojas:
            resultados[config["clave"]] = {
                "error": (
                    f"No se encontró la hoja {config['hoja']} en el archivo."
                )
            }
            continue

        try:
            resultados[config["clave"]] = convertir_hoja_manpower(
                archivo_bytes=archivo_bytes,
                hoja_fuente=config["hoja"],
                empresa_objetivo=config["empresa"],
                prefijo_actividad=config["prefijo"],
                nombre_area=config["nombre"]
            )
        except Exception as exc:
            resultados[config["clave"]] = {
                "error": str(exc)
            }

    return resultados


# =====================================================
# EVIDENCIAS FOTOGRÁFICAS
# =====================================================

BUCKET_EVIDENCIAS = "evidencias-ots"


def comprimir_imagen(
    archivo,
    max_dimension=1600,
    calidad=80
):
    """
    Comprime automáticamente fotografías provenientes
    de celular o PC y devuelve bytes JPEG optimizados.
    """

    archivo.seek(0)

    imagen = Image.open(archivo)

    # Corrige la orientación EXIF de fotografías de celular
    imagen = ImageOps.exif_transpose(imagen)

    # Convierte PNG / WEBP / transparencias a RGB
    if imagen.mode in ("RGBA", "LA", "P"):

        if imagen.mode == "P":
            imagen = imagen.convert("RGBA")

        fondo = Image.new(
            "RGB",
            imagen.size,
            "white"
        )

        if imagen.mode in ("RGBA", "LA"):
            fondo.paste(
                imagen,
                mask=imagen.getchannel("A")
            )
        else:
            fondo.paste(imagen)

        imagen = fondo

    elif imagen.mode != "RGB":
        imagen = imagen.convert("RGB")

    # Reduce resolución manteniendo proporción
    imagen.thumbnail(
        (max_dimension, max_dimension),
        Image.Resampling.LANCZOS
    )

    salida = io.BytesIO()

    imagen.save(
        salida,
        format="JPEG",
        quality=calidad,
        optimize=True,
        progressive=True
    )

    salida.seek(0)

    return salida.getvalue()


def subir_evidencia(
    archivo,
    ot,
    codigo_actividad,
    tipo_evidencia
):
    """
    Comprime y sube una fotografía al bucket evidencias-ots.
    Retorna la metadata que se almacenará en el JSONB
    avances_actividad.evidencias.
    """

    bytes_originales = archivo.getvalue()
    tamano_original = len(bytes_originales)

    bytes_comprimidos = comprimir_imagen(
        archivo,
        max_dimension=1600,
        calidad=80
    )

    tamano_comprimido = len(bytes_comprimidos)

    ahorro = (
        (1 - tamano_comprimido / tamano_original) * 100
        if tamano_original > 0
        else 0
    )

    ot_segura = "".join(
        caracter
        for caracter in str(ot)
        if caracter.isalnum() or caracter in "-_"
    )

    actividad_segura = "".join(
        caracter
        for caracter in str(codigo_actividad)
        if caracter.isalnum() or caracter in "-_"
    )

    tipo_seguro = "".join(
        caracter
        for caracter in str(tipo_evidencia).lower()
        if caracter.isalnum() or caracter in "-_"
    )

    nombre_archivo = (
        f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_"
        f"{uuid.uuid4().hex[:10]}.jpg"
    )

    ruta = (
        f"{ot_segura}/"
        f"{actividad_segura}/"
        f"{tipo_seguro}/"
        f"{nombre_archivo}"
    )

    (
        supabase_admin
        .storage
        .from_(BUCKET_EVIDENCIAS)
        .upload(
            path=ruta,
            file=bytes_comprimidos,
            file_options={
                "content-type": "image/jpeg",
                "upsert": "false"
            }
        )
    )

    # IMPORTANTE:
    # Guardamos únicamente el PATH permanente del archivo.
    # La URL para visualizarlo se generará temporalmente
    # mediante una Signed URL cuando el usuario abra Evidencias.
    return {
        "path": ruta,
        "nombre_original": archivo.name,
        "tipo": tipo_evidencia,
        "tamano_original": tamano_original,
        "tamano_comprimido": tamano_comprimido,
        "ahorro_pct": round(ahorro, 1)
    }


def extraer_path_evidencia(evidencia):
    """
    Obtiene el path permanente de una evidencia.

    Compatible con:
    1) registros nuevos que guardan {"path": "..."}
    2) registros antiguos que guardan {"url": "...", "path": "..."}
    3) registros muy antiguos que solo guardaron una URL pública.
    """

    if not evidencia:
        return ""

    if isinstance(evidencia, dict):

        path = str(
            evidencia.get("path")
            or ""
        ).strip()

        if path:
            return path

        url = str(
            evidencia.get("url")
            or ""
        ).strip()

    elif isinstance(evidencia, str):

        url = evidencia.strip()

        # Si por alguna razón se almacenó directamente un path.
        if (
            url
            and "://" not in url
            and not url.startswith("/")
        ):
            return url

    else:
        return ""

    if not url:
        return ""

    marcadores = [
        f"/storage/v1/object/public/{BUCKET_EVIDENCIAS}/",
        f"/storage/v1/object/sign/{BUCKET_EVIDENCIAS}/",
        f"/storage/v1/object/{BUCKET_EVIDENCIAS}/"
    ]

    for marcador in marcadores:

        if marcador in url:

            path = url.split(
                marcador,
                1
            )[1]

            # Retirar parámetros de una URL firmada previa.
            path = path.split("?", 1)[0]

            return path.strip("/")

    return ""


def crear_url_firmada_evidencia(
    evidencia,
    duracion_segundos=3600
):
    """
    Genera una URL temporal para visualizar una evidencia privada.
    El archivo NO expira ni se elimina.
    Solo expira este permiso temporal de lectura.
    """

    path = extraer_path_evidencia(
        evidencia
    )

    if not path:
        return ""

    try:

        respuesta = (
            supabase_admin
            .storage
            .from_(BUCKET_EVIDENCIAS)
            .create_signed_url(
                path,
                duracion_segundos
            )
        )

        if isinstance(respuesta, dict):

            return (
                respuesta.get("signedURL")
                or respuesta.get("signedUrl")
                or respuesta.get("signed_url")
                or ""
            )

        return str(respuesta or "")

    except Exception:
        return ""


def subir_evidencias(
    archivos,
    ot,
    codigo_actividad,
    tipo_evidencia
):
    """
    Procesa varias fotografías y devuelve una lista JSON.
    """

    evidencias = []

    for archivo in archivos or []:

        evidencia = subir_evidencia(
            archivo,
            ot,
            codigo_actividad,
            tipo_evidencia
        )

        evidencias.append(evidencia)

    return evidencias



# =====================================================
# CORTE VALIDADO PARA PRESENTACIÓN AL CLIENTE
# =====================================================
# Regularización solicitada por contingencia de conectividad.
# Este bloque NO cambia las fechas de los cortes oficiales.
# Únicamente fija el valor REAL validado para el corte
# 05/10/2026 19:00 y deja visible la trazabilidad en la curva.
CORTE_CLIENTE_FECHA = pd.Timestamp(
    "2026-10-05 19:00:00"
)

CORTE_CLIENTE_DATOS = {
    "ELECTRICIDAD": {
        "plan": 100.0,
        "real": 86.3,
        "ots": 101,
        "actividades": 164,
        "culminadas": 139
    },
    "INSTRUMENTACION": {
        "plan": 100.0,
        "real": 88.8,
        "ots": 160,
        "actividades": 210,
        "culminadas": 180
    },
    "CONSOLIDADO": {
        "plan": 100.0,
        "real": 87.7,
        "ots": 261,
        "actividades": 374,
        "culminadas": 319
    }
}

# =====================================================
# CORRECCIONES HISTÓRICAS DE CURVA S
# =====================================================
# Ajustes solicitados para Instrumentación:
# 05/10/2026 07:00 -> 51.3%
# 05/10/2026 14:00 -> 65.2%
#
# El consolidado se recalcula con el mismo criterio que
# ya usa el aplicativo: promedio ponderado por cantidad
# de actividades de cada área.
#
# Electricidad:    164 actividades
# Instrumentación: 210 actividades
# Total:           374 actividades
#
# Valores resultantes consolidados:
# 07:00 -> 54.6%
# 14:00 -> 65.0%

CORRECCIONES_CURVA_REAL = {
    "INSTRUMENTACION": {
        pd.Timestamp("2026-10-05 07:00:00"): 51.3,
        pd.Timestamp("2026-10-05 14:00:00"): 65.2
    },
    "CONSOLIDADO": {
        pd.Timestamp("2026-10-05 07:00:00"): 54.6,
        pd.Timestamp("2026-10-05 14:00:00"): 65.0
    }
}


def identificar_vista_corte_cliente(
    activities: pd.DataFrame
):
    """
    Identifica Electricidad, Instrumentación o Consolidado
    usando el código de actividad del plan cargado.
    """
    if (
        activities is None
        or activities.empty
        or "codigo_actividad" not in activities.columns
    ):
        return None

    codigos = (
        activities["codigo_actividad"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    tiene_elec = codigos.str.startswith(
        "ELEC"
    ).any()

    tiene_inst = codigos.str.startswith(
        "INST"
    ).any()

    if tiene_elec and tiene_inst:
        return "CONSOLIDADO"

    if tiene_elec:
        return "ELECTRICIDAD"

    if tiene_inst:
        return "INSTRUMENTACION"

    return None


def obtener_corte_cliente(
    activities: pd.DataFrame
):
    vista = identificar_vista_corte_cliente(
        activities
    )

    if not vista:
        return None

    datos = CORTE_CLIENTE_DATOS.get(
        vista
    )

    if not datos:
        return None

    salida = dict(datos)
    salida["vista"] = vista
    salida["fecha"] = CORTE_CLIENTE_FECHA

    return salida


def mostrar_corte_validado_cliente(
    activities: pd.DataFrame
):
    """
    Franja compacta que deja claro al cliente que los valores
    corresponden al corte validado del 05/10/2026 19:00.
    """
    corte = obtener_corte_cliente(
        activities
    )

    if not corte:
        return

    nombre_vista = {
        "ELECTRICIDAD": "Electricidad",
        "INSTRUMENTACION": "Instrumentación",
        "CONSOLIDADO": "Todas las áreas"
    }.get(
        corte["vista"],
        corte["vista"]
    )

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-wrap:wrap;
            align-items:center;
            gap:7px;
            padding:8px 10px;
            margin:.15rem 0 .65rem;
            border:1px solid #B7E4C7;
            border-left:4px solid #079455;
            border-radius:11px;
            background:#F4FBF7;
            color:#344054;
            font-size:11px;
            font-weight:700;
        ">
            <span style="color:#067647;font-weight:850;">
                ✓ CORTE VALIDADO · 05/10/2026 19:00
            </span>
            <span>Vista: <strong>{nombre_vista}</strong></span>
            <span>PLAN <strong style="color:#155EEF;">{corte["plan"]:.1f}%</strong></span>
            <span>REAL <strong style="color:#D92D20;">{corte["real"]:.1f}%</strong></span>
            <span>OTs <strong>{corte["ots"]}</strong></span>
            <span>Actividades <strong>{corte["actividades"]}</strong></span>
            <span>Culminadas <strong>{corte["culminadas"]}</strong></span>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# FUNCIONES DEL DASHBOARD
# =====================================================

def latest_progress(progress: pd.DataFrame) -> pd.DataFrame:
    if progress.empty:
        return pd.DataFrame(
            columns=["actividad_id", "avance"]
        )

    data = progress.copy()

    data["fecha_registro"] = pd.to_datetime(
        data["fecha_registro"],
        errors="coerce",
        utc=True
    )

    return (
        data
        .sort_values("fecha_registro")
        .groupby("actividad_id", as_index=False)
        .tail(1)
    )


def build_activity_status(
    activities: pd.DataFrame,
    progress: pd.DataFrame
) -> pd.DataFrame:

    if activities.empty:
        return activities.copy()

    latest = latest_progress(progress)

    if latest.empty:
        result = activities.copy()
        result["avance_real"] = 0.0

    else:
        columnas_avance = [
            "actividad_id",
            "avance",
            "descripcion_avance",
            "observaciones",
            "fecha_registro"
        ]

        columnas_disponibles = [
            c for c in columnas_avance
            if c in latest.columns
        ]

        result = activities.merge(
            latest[columnas_disponibles],
            left_on="id",
            right_on="actividad_id",
            how="left"
        )

        result["avance_real"] = pd.to_numeric(
            result.get("avance", 0),
            errors="coerce"
        ).fillna(0)

    if "peso" not in result.columns:
        result["peso"] = 1.0

    result["peso"] = pd.to_numeric(
        result["peso"],
        errors="coerce"
    ).fillna(1)

    return result


def weighted_progress(
    activity_status: pd.DataFrame
) -> float:

    if activity_status.empty:
        return 0.0

    denominator = activity_status["peso"].sum()

    if denominator <= 0:
        return float(
            activity_status["avance_real"].mean()
        )

    return float(
        (
            activity_status["avance_real"]
            * activity_status["peso"]
        ).sum()
        / denominator
    )


def compute_kpis(
    activities: pd.DataFrame,
    progress: pd.DataFrame
) -> dict:

    status = build_activity_status(
        activities,
        progress
    )

    if status.empty:
        return {
            "avance_general": 0.0,
            "actividades": 0,
            "culminadas": 0,
            "parciales": 0,
            "no_iniciadas": 0,
            "pendientes": 0,
            "spi": 0.0,
            "hh_plan": 0.0,
            "hh_ganadas": 0.0
        }

    # REAL general con la misma metodología de la Curva S original:
    # promedio simple del último avance de TODAS las actividades.
    avance_general = float(
        status["avance_real"].mean()
    ) if not status.empty else 0.0

    culminadas = int(
        (status["avance_real"] >= 100).sum()
    )

    parciales = int(
        (
            (status["avance_real"] > 0)
            & (status["avance_real"] < 100)
        ).sum()
    )

    no_iniciadas = int(
        (status["avance_real"] <= 0).sum()
    )

    pendientes = int(
        (status["avance_real"] < 100).sum()
    )

    if "hh_plan" in status.columns:
        hh_plan_series = pd.to_numeric(
            status["hh_plan"],
            errors="coerce"
        ).fillna(0)
    else:
        hh_plan_series = pd.Series(
            0.0,
            index=status.index
        )

    hh_plan = float(
        hh_plan_series.sum()
    )

    hh_ganadas = float(
        (
            hh_plan_series
            * status["avance_real"]
            / 100
        ).sum()
    )

    # =====================================================
    # PLAN ACTUAL
    # Misma metodología de la Curva S:
    # promedio simple del avance esperado de todas
    # las actividades según la fecha/hora actual.
    # =====================================================

    inicio = pd.to_datetime(
        status["inicio_plan"],
        errors="coerce"
    )

    fin = pd.to_datetime(
        status["fin_plan"],
        errors="coerce"
    )

    ahora = pd.Timestamp.now(tz="America/Lima").tz_localize(None)

    avances_plan_actual = []

    for fecha_inicio, fecha_fin in zip(inicio, fin):

        if pd.isna(fecha_inicio) or pd.isna(fecha_fin):
            avances_plan_actual.append(0.0)
            continue

        if fecha_fin <= fecha_inicio:
            fecha_fin = (
                fecha_inicio
                + pd.Timedelta(minutes=1)
            )

        if ahora <= fecha_inicio:
            avance_plan_actividad = 0.0

        elif ahora >= fecha_fin:
            avance_plan_actividad = 100.0

        else:
            duracion = (
                fecha_fin - fecha_inicio
            ).total_seconds()

            transcurrido = (
                ahora - fecha_inicio
            ).total_seconds()

            avance_plan_actividad = (
                transcurrido
                / duracion
                * 100.0
                if duracion > 0
                else 100.0
            )

        avances_plan_actual.append(
            max(
                0.0,
                min(
                    100.0,
                    avance_plan_actividad
                )
            )
        )

    plan_actual = (
        float(
            sum(avances_plan_actual)
            / len(avances_plan_actual)
        )
        if avances_plan_actual
        else 0.0
    )

    spi = (
        avance_general / plan_actual
        if plan_actual > 0
        else 0.0
    )
    return {
        "avance_general": avance_general,
        "avance_plan": plan_actual,
        "actividades": len(status),
        "culminadas": culminadas,
        "parciales": parciales,
        "no_iniciadas": no_iniciadas,
        "pendientes": pendientes,
        "spi": spi,
        "hh_plan": hh_plan,
        "hh_ganadas": hh_ganadas
    }


def build_s_curve(
    activities: pd.DataFrame,
    progress: pd.DataFrame
) -> pd.DataFrame:

    if activities.empty:
        return pd.DataFrame(
            columns=["fecha", "PLAN", "REAL"]
        )

    acts = activities.copy()

    acts["inicio_plan"] = pd.to_datetime(
        acts["inicio_plan"],
        errors="coerce"
    )

    acts["fin_plan"] = pd.to_datetime(
        acts["fin_plan"],
        errors="coerce"
    )

    valid = acts.dropna(
        subset=[
            "id",
            "inicio_plan",
            "fin_plan"
        ]
    ).copy()

    if valid.empty:
        return pd.DataFrame(
            columns=["fecha", "PLAN", "REAL"]
        )

    invalidas = (
        valid["fin_plan"]
        <= valid["inicio_plan"]
    )

    valid.loc[
        invalidas,
        "fin_plan"
    ] = (
        valid.loc[
            invalidas,
            "inicio_plan"
        ]
        + pd.Timedelta(minutes=1)
    )

    inicio_programa = (
        valid["inicio_plan"].min()
    )

    fin_programa = (
        valid["fin_plan"].max()
    )

    cortes = [inicio_programa]

    dia = inicio_programa.normalize()
    dia_final = fin_programa.normalize()

    horas_corte = [0, 7, 14, 19]

    while dia <= dia_final:

        for hora in horas_corte:

            corte = (
                dia
                + pd.Timedelta(hours=hora)
            )

            if (
                inicio_programa
                < corte
                < fin_programa
            ):
                cortes.append(corte)

        dia += pd.Timedelta(days=1)

    cortes.append(fin_programa)

    # =====================================================
    # PUNTO EN VIVO
    # =====================================================
    # Los cortes oficiales se mantienen en:
    # 00:00 / 07:00 / 14:00 / 19:00.
    #
    # Además agregamos la hora actual mientras la parada
    # está en ejecución. Esto permite que la curva REAL
    # muestre el avance acumulado registrado hasta este
    # momento, aunque el último reporte haya ocurrido
    # después del último corte oficial.
    ahora_lima = (
        pd.Timestamp.now(
            tz="America/Lima"
        )
        .tz_localize(None)
    )

    if (
        inicio_programa
        < ahora_lima
        < fin_programa
    ):
        cortes.append(ahora_lima)

    cortes = sorted(
        pd.Series(cortes)
        .drop_duplicates()
        .tolist()
    )

    total_actividades = len(valid)

    plan_values = []

    for corte in cortes:

        suma_plan = 0.0

        for _, actividad in valid.iterrows():

            inicio_act = (
                actividad["inicio_plan"]
            )

            fin_act = (
                actividad["fin_plan"]
            )

            if corte <= inicio_act:
                avance = 0.0

            elif corte >= fin_act:
                avance = 100.0

            else:
                duracion = (
                    fin_act - inicio_act
                ).total_seconds()

                transcurrido = (
                    corte - inicio_act
                ).total_seconds()

                avance = (
                    transcurrido
                    / duracion
                    * 100
                    if duracion > 0
                    else 100
                )

            suma_plan += max(
                0,
                min(100, avance)
            )

        plan_values.append(
            suma_plan
            / total_actividades
        )

    prog = progress.copy()

    if not prog.empty:

        prog["fecha_registro"] = (
            pd.to_datetime(
                prog["fecha_registro"],
                errors="coerce",
                utc=True
            )
            .dt.tz_convert("America/Lima")
            .dt.tz_localize(None)
        )

        prog["avance"] = pd.to_numeric(
            prog["avance"],
            errors="coerce"
        ).fillna(0).clip(0, 100)

        prog = prog.dropna(
            subset=[
                "actividad_id",
                "fecha_registro"
            ]
        )

    real_values = []

    ids_actividades = (
        valid["id"].tolist()
    )

    for corte in cortes:

        if prog.empty:

            real_values.append(
                0.0
                if corte <= ahora_lima
                else None
            )

            continue

        # IMPORTANTE:
        # La curva REAL debe mantener el último avance conocido
        # hasta la hora actual. No debe desaparecer solo porque
        # el último reporte ocurrió antes que el punto EN VIVO.
        #
        # Únicamente ocultamos puntos que realmente están en el futuro.
        if corte > ahora_lima:
            real_values.append(None)
            continue

        disponibles = prog[
            prog["fecha_registro"] <= corte
        ]

        if disponibles.empty:

            real_values.append(0.0)
            continue

        ultimos = (
            disponibles
            .sort_values("fecha_registro")
            .groupby(
                "actividad_id",
                as_index=False
            )
            .tail(1)
            .set_index("actividad_id")[
                "avance"
            ]
            .to_dict()
        )

        suma_real = sum(
            float(
                ultimos.get(
                    actividad_id,
                    0
                )
            )
            for actividad_id
            in ids_actividades
        )

        real_values.append(
            suma_real
            / total_actividades
        )

    curva = pd.DataFrame({
        "fecha": pd.to_datetime(cortes),
        "PLAN": plan_values,
        "REAL": real_values
    })

    curva["PLAN"] = (
        pd.to_numeric(
            curva["PLAN"],
            errors="coerce"
        )
        .fillna(0)
        .clip(0, 100)
        .cummax()
    )

    indices_real = (
        curva.index[
            curva["REAL"].notna()
        ]
        .tolist()
    )

    if indices_real:

        curva.loc[
            indices_real,
            "REAL"
        ] = (
            pd.to_numeric(
                curva.loc[
                    indices_real,
                    "REAL"
                ],
                errors="coerce"
            )
            .fillna(0)
            .clip(0, 100)
            .cummax()
        )

    curva.loc[
        curva.index[0],
        "PLAN"
    ] = 0.0

    curva.loc[
        curva.index[-1],
        "PLAN"
    ] = 100.0

    if pd.isna(
        curva.loc[
            curva.index[0],
            "REAL"
        ]
    ):
        curva.loc[
            curva.index[0],
            "REAL"
        ] = 0.0

    # =====================================================
    # AJUSTE VALIDADO DEL CORTE 05/10/2026 19:00
    # =====================================================
    # Se mantiene la hora oficial del corte.
    # Solo se regulariza el valor PLAN/REAL validado para
    # presentación al cliente después de la contingencia.
    corte_cliente = obtener_corte_cliente(
        activities
    )

    curva["CORTE_VALIDADO"] = False

    if corte_cliente:

        fecha_cliente = pd.Timestamp(
            corte_cliente["fecha"]
        )

        coincidencia = (
            curva["fecha"]
            == fecha_cliente
        )

        if coincidencia.any():

            indice_cliente = (
                curva.index[
                    coincidencia
                ][0]
            )

        else:

            fila_cliente = pd.DataFrame({
                "fecha": [fecha_cliente],
                "PLAN": [
                    corte_cliente["plan"]
                ],
                "REAL": [
                    corte_cliente["real"]
                ],
                "CORTE_VALIDADO": [True]
            })

            curva = pd.concat(
                [
                    curva,
                    fila_cliente
                ],
                ignore_index=True
            ).sort_values(
                "fecha"
            ).reset_index(
                drop=True
            )

            indice_cliente = (
                curva.index[
                    curva["fecha"]
                    == fecha_cliente
                ][0]
            )

        curva.loc[
            indice_cliente,
            "PLAN"
        ] = float(
            corte_cliente["plan"]
        )

        curva.loc[
            indice_cliente,
            "REAL"
        ] = float(
            corte_cliente["real"]
        )

        curva.loc[
            indice_cliente,
            "CORTE_VALIDADO"
        ] = True

        # La Curva S acumulada no debe retroceder después
        # de un corte histórico corregido.
        curva["PLAN"] = (
            pd.to_numeric(
                curva["PLAN"],
                errors="coerce"
            )
            .fillna(0)
            .clip(0, 100)
            .cummax()
        )

        indices_real = (
            curva.index[
                curva["REAL"].notna()
            ]
            .tolist()
        )

        if indices_real:

            curva.loc[
                indices_real,
                "REAL"
            ] = (
                pd.to_numeric(
                    curva.loc[
                        indices_real,
                        "REAL"
                    ],
                    errors="coerce"
                )
                .fillna(0)
                .clip(0, 100)
                .cummax()
            )

    # =====================================================
    # CORRECCIONES HISTÓRICAS ADICIONALES
    # =====================================================
    # Se aplican después del cálculo normal de la curva y
    # antes de devolverla. No se alteran las fechas ni horas
    # de los cortes oficiales.
    vista_curva = identificar_vista_corte_cliente(
        activities
    )

    correcciones_vista = (
        CORRECCIONES_CURVA_REAL.get(
            vista_curva,
            {}
        )
    )

    if correcciones_vista:

        for fecha_correccion, real_correccion in (
            correcciones_vista.items()
        ):

            coincidencia = (
                curva["fecha"]
                == fecha_correccion
            )

            if coincidencia.any():

                indice_correccion = (
                    curva.index[
                        coincidencia
                    ][0]
                )

                curva.loc[
                    indice_correccion,
                    "REAL"
                ] = float(
                    real_correccion
                )

            else:

                # Respaldo por si el corte no existiera por
                # alguna diferencia de rango de planificación.
                fila_correccion = pd.DataFrame({
                    "fecha": [fecha_correccion],
                    "PLAN": [None],
                    "REAL": [float(real_correccion)],
                    "CORTE_VALIDADO": [False]
                })

                curva = pd.concat(
                    [
                        curva,
                        fila_correccion
                    ],
                    ignore_index=True
                ).sort_values(
                    "fecha"
                ).reset_index(
                    drop=True
                )

        # Mantener propiedad acumulativa de la Curva S.
        indices_real = (
            curva.index[
                curva["REAL"].notna()
            ]
            .tolist()
        )

        if indices_real:

            curva.loc[
                indices_real,
                "REAL"
            ] = (
                pd.to_numeric(
                    curva.loc[
                        indices_real,
                        "REAL"
                    ],
                    errors="coerce"
                )
                .fillna(0)
                .clip(0, 100)
                .cummax()
            )

    return curva


def crear_curva_s_tiempo_real(
    curva: pd.DataFrame,
    altura: int = 480
):
    """
    Curva S visual unificada para ADMIN y PLANNER.
    - PLAN azul / REAL rojo.
    - Valores visibles, separados con offsets para evitar solapamientos.
    - Línea vertical de hora actual durante la ejecución.
    - Punto EN VIVO pequeño y circular.
    """

    if curva is None or curva.empty:
        return go.Figure(), None

    data = curva.copy()
    data["fecha"] = pd.to_datetime(
        data["fecha"],
        errors="coerce"
    )
    data = data.dropna(subset=["fecha"]).sort_values("fecha")

    if data.empty:
        return go.Figure(), None

    ahora_lima = (
        pd.Timestamp.now(tz="America/Lima")
        .tz_localize(None)
    )

    inicio = data["fecha"].min()
    fin = data["fecha"].max()
    en_ejecucion = bool(inicio <= ahora_lima <= fin)

    figura = go.Figure()

    # Corte histórico validado para cliente.
    if "CORTE_VALIDADO" in data.columns:

        cortes_validados = data[
            data["CORTE_VALIDADO"].fillna(False)
        ]

        if not cortes_validados.empty:

            fila_validada = (
                cortes_validados.iloc[0]
            )

            figura.add_shape(
                type="line",
                x0=fila_validada["fecha"],
                x1=fila_validada["fecha"],
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(
                    color="#079455",
                    width=1.4,
                    dash="dot"
                ),
                layer="below"
            )

            figura.add_annotation(
                x=fila_validada["fecha"],
                y=1.01,
                xref="x",
                yref="paper",
                text="CORTE VALIDADO · 05/10 19:00",
                showarrow=False,
                xanchor="center",
                yanchor="bottom",
                bgcolor="#ECFDF3",
                bordercolor="#ABEFC6",
                borderpad=4,
                font=dict(
                    color="#067647",
                    size=9
                )
            )

            # Resaltar únicamente el punto REAL validado.
            if pd.notna(
                fila_validada.get("REAL")
            ):

                figura.add_trace(
                    go.Scatter(
                        x=[
                            fila_validada["fecha"]
                        ],
                        y=[
                            float(
                                fila_validada["REAL"]
                            )
                        ],
                        mode="markers",
                        marker=dict(
                            size=10,
                            symbol="circle",
                            color="#D92D20",
                            line=dict(
                                width=2.5,
                                color="#079455"
                            )
                        ),
                        name="REAL · corte validado",
                        showlegend=False,
                        hovertemplate=(
                            "<b>CORTE VALIDADO</b><br>"
                            "05/10/2026 19:00<br>"
                            "REAL: <b>%{y:.1f}%</b>"
                            "<extra></extra>"
                        )
                    )
                )

    # Zona transcurrida, muy sutil.
    if en_ejecucion:
        figura.add_vrect(
            x0=inicio,
            x1=ahora_lima,
            fillcolor="rgba(21,94,239,0.020)",
            line_width=0,
            layer="below"
        )

    # PLAN
    figura.add_trace(
        go.Scatter(
            x=data["fecha"],
            y=data["PLAN"],
            mode="lines+markers",
            name="PLAN",
            line=dict(
                width=3.4,
                shape="spline",
                smoothing=1.0,
                color="#155EEF"
            ),
            marker=dict(
                size=7,
                color="#155EEF",
                line=dict(width=1.2, color="#FFFFFF")
            ),
            hovertemplate=(
                "<b>PLAN</b><br>"
                "%{x|%d/%m/%Y %H:%M}<br>"
                "Avance: <b>%{y:.1f}%</b>"
                "<extra></extra>"
            )
        )
    )

    # REAL
    figura.add_trace(
        go.Scatter(
            x=data["fecha"],
            y=data["REAL"],
            mode="lines+markers",
            name="REAL",
            line=dict(
                width=3.6,
                shape="spline",
                smoothing=1.0,
                color="#D92D20"
            ),
            marker=dict(
                size=7,
                color="#D92D20",
                line=dict(width=1.2, color="#FFFFFF")
            ),
            connectgaps=False,
            hovertemplate=(
                "<b>REAL</b><br>"
                "%{x|%d/%m/%Y %H:%M}<br>"
                "Avance: <b>%{y:.1f}%</b>"
                "<extra></extra>"
            )
        )
    )

    # -----------------------------------------------------
    # ETIQUETAS DE CADA PUNTO
    # Se dibujan como annotations para controlar x/y en píxeles.
    # PLAN siempre arriba, REAL siempre abajo.
    # Si ambos valores están cerca, aumenta la separación.
    # -----------------------------------------------------
    for i, fila in data.reset_index(drop=True).iterrows():

        fecha = fila["fecha"]
        plan = fila.get("PLAN")
        real = fila.get("REAL")

        plan_val = float(plan) if pd.notna(plan) else None
        real_val = float(real) if pd.notna(real) else None

        cercania = (
            abs(plan_val - real_val)
            if plan_val is not None and real_val is not None
            else 999
        )

        if cercania <= 3:
            shift_plan_y = 23
            shift_real_y = -23
        elif cercania <= 8:
            shift_plan_y = 18
            shift_real_y = -18
        else:
            shift_plan_y = 13
            shift_real_y = -13

        # Pequeño movimiento horizontal alternado.
        # En el punto cercano a AHORA se separan a izquierda/derecha.
        xshift_plan = [-7, 0, 7][i % 3]
        xshift_real = [7, 0, -7][i % 3]

        if en_ejecucion and abs(fecha - ahora_lima) <= pd.Timedelta(minutes=5):
            xshift_plan = -16
            xshift_real = 16

        if plan_val is not None:
            figura.add_annotation(
                x=fecha,
                y=plan_val,
                text=f"{plan_val:.1f}%",
                showarrow=False,
                xshift=xshift_plan,
                yshift=shift_plan_y,
                xanchor="center",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(255,255,255,0)",
                borderpad=1.5,
                font=dict(
                    size=9,
                    color="#155EEF"
                )
            )

        if real_val is not None:
            figura.add_annotation(
                x=fecha,
                y=real_val,
                text=f"{real_val:.1f}%",
                showarrow=False,
                xshift=xshift_real,
                yshift=shift_real_y,
                xanchor="center",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(255,255,255,0)",
                borderpad=1.5,
                font=dict(
                    size=9,
                    color="#D92D20"
                )
            )

    info_vivo = None

    if en_ejecucion:

        # Línea de tiempo real más fina para no competir con los datos.
        figura.add_shape(
            type="line",
            x0=ahora_lima,
            x1=ahora_lima,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(
                color="#0B1F33",
                width=1.5,
                dash="dash"
            ),
            layer="above"
        )

        figura.add_annotation(
            x=ahora_lima,
            y=1.045,
            xref="x",
            yref="paper",
            text=f"AHORA · {ahora_lima:%d/%m %H:%M}",
            showarrow=False,
            xanchor="center",
            yanchor="bottom",
            bgcolor="#0B1F33",
            bordercolor="#0B1F33",
            borderpad=4,
            font=dict(
                color="#FFFFFF",
                size=9
            )
        )

        diferencias = (
            data["fecha"] - ahora_lima
        ).abs()
        idx_vivo = diferencias.idxmin()
        fila_vivo = data.loc[idx_vivo]

        if diferencias.loc[idx_vivo] <= pd.Timedelta(minutes=5):

            plan_vivo = (
                float(fila_vivo["PLAN"])
                if pd.notna(fila_vivo["PLAN"])
                else None
            )

            real_vivo = (
                float(fila_vivo["REAL"])
                if pd.notna(fila_vivo["REAL"])
                else None
            )

            # Punto circular pequeño. Reemplaza el rombo grande.
            for serie, valor, color in [
                ("PLAN", plan_vivo, "#155EEF"),
                ("REAL", real_vivo, "#D92D20")
            ]:
                if valor is None:
                    continue

                figura.add_trace(
                    go.Scatter(
                        x=[fila_vivo["fecha"]],
                        y=[valor],
                        mode="markers",
                        marker=dict(
                            size=9,
                            symbol="circle",
                            color=color,
                            line=dict(
                                width=2,
                                color="#FFFFFF"
                            )
                        ),
                        name=f"{serie} EN VIVO",
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{serie} EN VIVO</b><br>"
                            "%{x|%d/%m/%Y %H:%M}<br>"
                            "Avance: <b>%{y:.1f}%</b>"
                            "<extra></extra>"
                        )
                    )
                )

            if plan_vivo is not None:
                brecha_vivo = (
                    real_vivo - plan_vivo
                    if real_vivo is not None
                    else None
                )

                info_vivo = {
                    "ahora": ahora_lima,
                    "plan": plan_vivo,
                    "real": real_vivo,
                    "brecha": brecha_vivo
                }

    figura.update_layout(
        height=altura,
        hovermode="x unified",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#344054",
            size=12
        ),
        xaxis=dict(
            title="Fecha / hora",
            tickformat="%d/%m\n%H:%M",
            nticks=8,
            showgrid=True,
            gridwidth=1,
            gridcolor="#EDF2F7",
            linecolor="#98A2B3",
            tickfont=dict(
                size=10,
                color="#475467"
            ),
            title_font=dict(
                size=11,
                color="#667085"
            ),
            automargin=True
        ),
        yaxis=dict(
            title="Avance acumulado (%)",
            range=[-8, 112],
            dtick=20,
            ticksuffix="%",
            showgrid=True,
            gridwidth=1,
            gridcolor="#E7EDF4",
            linecolor="#98A2B3",
            zeroline=False,
            tickfont=dict(
                size=10,
                color="#475467"
            ),
            title_font=dict(
                size=11,
                color="#667085"
            ),
            automargin=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.075,
            xanchor="center",
            x=0.5,
            font=dict(
                size=11,
                color="#344054"
            )
        ),
        margin=dict(
            l=52,
            r=34,
            t=76,
            b=52
        )
    )

    return figura, info_vivo


def mostrar_estado_curva_en_vivo(info_vivo):
    if not info_vivo:
        return

    plan = info_vivo.get("plan")
    real = info_vivo.get("real")
    brecha = info_vivo.get("brecha")
    ahora = info_vivo.get("ahora")

    real_html = (
        f"{real:.1f}%"
        if real is not None
        else "Sin reporte"
    )

    if brecha is None:
        clase_brecha = ""
        brecha_html = "Sin dato"
    else:
        clase_brecha = "good" if brecha >= -5 else "risk"
        brecha_html = f"{brecha:+.1f} pp"

    st.markdown(
        f"""
        <div class="curve-live-strip">
            <span class="curve-live-now">EN VIVO · {ahora:%H:%M}</span>
            <span class="curve-chip plan">PLAN <strong>{plan:.1f}%</strong></span>
            <span class="curve-chip real">REAL <strong>{real_html}</strong></span>
            <span class="curve-chip {clase_brecha}">BRECHA <strong>{brecha_html}</strong></span>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# INFORME DIARIO AUTOMÁTICO
# =====================================================

def construir_resumen_diario(
    ots: pd.DataFrame,
    actividades: pd.DataFrame,
    avances: pd.DataFrame,
    nombre_area: str,
    fecha_objetivo
) -> str:

    if actividades.empty:
        return (
            f"Informe diario - {nombre_area}\n\n"
            "No existen actividades cargadas para esta área."
        )

    estado = build_activity_status(
        actividades,
        avances
    )

    kpis = compute_kpis(
        actividades,
        avances
    )

    if avances.empty:

        diarios = pd.DataFrame()

    else:

        fechas_lima = pd.to_datetime(
            avances["fecha_registro"],
            errors="coerce",
            utc=True
        ).dt.tz_convert("America/Lima")

        diarios = avances[
            fechas_lima.dt.date == fecha_objetivo
        ].copy()

        if not diarios.empty:
            diarios["fecha_lima"] = fechas_lima.loc[
                diarios.index
            ]

    lineas = [
        (
            f"INFORME DIARIO DE CONTROL DE OTs - "
            f"{nombre_area.upper()}"
        ),
        f"Fecha: {fecha_objetivo.strftime('%d/%m/%Y')}",
        "",
        "RESUMEN EJECUTIVO",
        (
            f"- OTs registradas: "
            f"{ots['id'].nunique() if not ots.empty else 0}."
        ),
        (
            f"- Actividades programadas: "
            f"{kpis['actividades']}."
        ),
        (
            f"- Avance general acumulado: "
            f"{kpis['avance_general']:.1f}%."
        ),
        (
            f"- Actividades culminadas: "
            f"{kpis['culminadas']}."
        ),
        (
            f"- Actividades en ejecución: "
            f"{kpis['parciales']}."
        ),
        (
            f"- Actividades no iniciadas: "
            f"{kpis['no_iniciadas']}."
        ),
        (
            f"- HH planificadas: "
            f"{kpis['hh_plan']:.0f}."
        ),
        (
            f"- HH ganadas: "
            f"{kpis['hh_ganadas']:.0f}."
        ),
        (
            f"- SPI: "
            f"{kpis['spi']:.2f}."
        ),
        "",
        (
            f"REGISTROS REALIZADOS EL DÍA: "
            f"{len(diarios)}"
        )
    ]

    if diarios.empty:

        lineas += [
            "",
            "No se registraron avances durante la fecha seleccionada."
        ]

    else:

        actividad_lookup = (
            actividades
            .set_index("id")
        )

        ot_lookup = (
            ots
            .set_index("id")
            if not ots.empty
            else pd.DataFrame()
        )

        principales = diarios.sort_values(
            "fecha_lima",
            ascending=False
        ).head(10)

        lineas += [
            "",
            "PRINCIPALES ACTUALIZACIONES"
        ]

        for _, registro in principales.iterrows():

            actividad_id = registro.get(
                "actividad_id"
            )

            codigo = ""
            descripcion_actividad = ""
            ot_numero = ""
            equipo = ""

            if (
                actividad_id in actividad_lookup.index
            ):

                actividad = actividad_lookup.loc[
                    actividad_id
                ]

                codigo = str(
                    actividad.get(
                        "codigo_actividad",
                        ""
                    )
                )

                descripcion_actividad = str(
                    actividad.get(
                        "descripcion",
                        ""
                    )
                )

                ot_id = actividad.get(
                    "ot_id"
                )

                if (
                    not ot_lookup.empty
                    and ot_id in ot_lookup.index
                ):

                    ot_info = ot_lookup.loc[
                        ot_id
                    ]

                    ot_numero = str(
                        ot_info.get(
                            "ot",
                            ""
                        )
                    )

                    equipo = str(
                        ot_info.get(
                            "equipo",
                            ""
                        )
                    )

            hora = ""

            fecha_registro = registro.get(
                "fecha_lima"
            )

            if pd.notna(fecha_registro):
                hora = fecha_registro.strftime(
                    "%H:%M"
                )

            descripcion_reporte = (
                registro.get(
                    "descripcion_avance"
                )
                or descripcion_actividad
                or ""
            )

            lineas.append(
                f"- {hora} | OT {ot_numero} | "
                f"{equipo} | {codigo} | "
                f"{registro.get('avance', 0)}% | "
                f"{descripcion_reporte}"
            )

        observaciones = (
            diarios.get(
                "observaciones",
                pd.Series(
                    dtype="object"
                )
            )
            .fillna("")
            .astype(str)
        )

        observaciones = [
            texto.strip()
            for texto in observaciones
            if texto.strip()
        ]

        if observaciones:

            lineas += [
                "",
                "OBSERVACIONES / RESTRICCIONES"
            ]

            for observacion in observaciones[:10]:
                lineas.append(
                    f"- {observacion}"
                )

        criticos = diarios[
            diarios.get(
                "critica",
                False
            ).fillna(False)
            if "critica" in diarios.columns
            else pd.Series(
                False,
                index=diarios.index
            )
        ]

        if not criticos.empty:

            lineas += [
                "",
                "ACTIVIDADES MARCADAS COMO CRÍTICAS"
            ]

            for _, registro in criticos.head(
                10
            ).iterrows():

                actividad_id = registro.get(
                    "actividad_id"
                )

                if (
                    actividad_id
                    in actividad_lookup.index
                ):

                    actividad = actividad_lookup.loc[
                        actividad_id
                    ]

                    lineas.append(
                        f"- "
                        f"{actividad.get('codigo_actividad', '')}: "
                        f"{registro.get('avance', 0)}% - "
                        f"{registro.get('descripcion_avance', '')}"
                    )

    pendientes = estado[
        estado["avance_real"] < 100
    ].copy()

    if not pendientes.empty:

        pendientes = pendientes.sort_values(
            [
                "critica",
                "avance_real"
            ],
            ascending=[
                False,
                True
            ]
        )

        lineas += [
            "",
            "PENDIENTES PRINCIPALES"
        ]

        for _, actividad in pendientes.head(
            10
        ).iterrows():

            lineas.append(
                f"- "
                f"{actividad.get('codigo_actividad', '')}: "
                f"{actividad.get('descripcion', '')} | "
                f"Avance {actividad.get('avance_real', 0):.1f}%"
            )

    return "\n".join(lineas)



# =====================================================
# SECCIONES EDITABLES DEL INFORME DIARIO
# =====================================================

def construir_secciones_informe_diario(
    ots: pd.DataFrame,
    actividades: pd.DataFrame,
    avances: pd.DataFrame,
    nombre_area: str,
    fecha_objetivo
) -> dict:

    estado = build_activity_status(
        actividades,
        avances
    )

    kpis = compute_kpis(
        actividades,
        avances
    )

    # Avances de la fecha seleccionada
    if avances.empty:
        diarios = pd.DataFrame()
    else:
        fechas_lima = pd.to_datetime(
            avances["fecha_registro"],
            errors="coerce",
            utc=True
        ).dt.tz_convert("America/Lima")

        diarios = avances[
            fechas_lima.dt.date == fecha_objetivo
        ].copy()

        if not diarios.empty:
            diarios["fecha_lima"] = fechas_lima.loc[
                diarios.index
            ]

    # -------------------------------------------------
    # RESUMEN EJECUTIVO
    # -------------------------------------------------
    resumen = (
        f"OTs registradas: "
        f"{ots['id'].nunique() if not ots.empty else 0}\n"
        f"Actividades programadas: {kpis['actividades']}\n"
        f"Avance general acumulado: {kpis['avance_general']:.1f}%\n"
        f"Actividades culminadas: {kpis['culminadas']}\n"
        f"Actividades en ejecución: {kpis['parciales']}\n"
        f"Actividades no iniciadas: {kpis['no_iniciadas']}\n"
        f"HH planificadas: {kpis['hh_plan']:.0f}\n"
        f"HH ganadas: {kpis['hh_ganadas']:.0f}\n"
        f"SPI: {kpis['spi']:.2f}"
    )

    # -------------------------------------------------
    # PRINCIPALES ACTUALIZACIONES
    # -------------------------------------------------
    actualizaciones = []

    if not diarios.empty:
        actividad_lookup = actividades.set_index("id")
        ot_lookup = (
            ots.set_index("id")
            if not ots.empty
            else pd.DataFrame()
        )

        principales = diarios.sort_values(
            "fecha_lima",
            ascending=False
        ).head(10)

        for _, registro in principales.iterrows():

            actividad_id = registro.get("actividad_id")
            codigo = ""
            ot_numero = ""
            equipo = ""

            if actividad_id in actividad_lookup.index:
                actividad = actividad_lookup.loc[actividad_id]

                codigo = str(
                    actividad.get("codigo_actividad", "")
                )

                ot_id = actividad.get("ot_id")

                if (
                    not ot_lookup.empty
                    and ot_id in ot_lookup.index
                ):
                    ot_info = ot_lookup.loc[ot_id]
                    ot_numero = str(ot_info.get("ot", ""))
                    equipo = str(ot_info.get("equipo", ""))

            hora = ""
            fecha_registro = registro.get("fecha_lima")

            if pd.notna(fecha_registro):
                hora = fecha_registro.strftime("%H:%M")

            detalle = (
                registro.get("descripcion_avance")
                or ""
            )

            actualizaciones.append(
                f"{hora} | OT {ot_numero} | {equipo} | "
                f"{codigo} | {registro.get('avance', 0)}% | "
                f"{detalle}"
            )

    if not actualizaciones:
        actualizaciones = [
            "No se registraron avances durante la fecha seleccionada."
        ]

    # -------------------------------------------------
    # OBSERVACIONES / RESTRICCIONES
    # -------------------------------------------------
    observaciones = []

    if not diarios.empty and "observaciones" in diarios.columns:

        actividad_lookup_obs = (
            actividades.set_index("id")
            if not actividades.empty
            else pd.DataFrame()
        )

        ot_lookup_obs = (
            ots.set_index("id")
            if not ots.empty
            else pd.DataFrame()
        )

        for _, registro_obs in diarios.iterrows():

            observacion = str(
                registro_obs.get(
                    "observaciones",
                    ""
                )
                or ""
            ).strip()

            if not observacion:
                continue

            actividad_id_obs = registro_obs.get(
                "actividad_id"
            )

            codigo_obs = ""
            descripcion_obs = ""
            ot_numero_obs = ""
            equipo_obs = ""

            if (
                not actividad_lookup_obs.empty
                and actividad_id_obs
                in actividad_lookup_obs.index
            ):

                actividad_obs = (
                    actividad_lookup_obs.loc[
                        actividad_id_obs
                    ]
                )

                codigo_obs = str(
                    actividad_obs.get(
                        "codigo_actividad",
                        ""
                    )
                )

                descripcion_obs = str(
                    actividad_obs.get(
                        "descripcion",
                        ""
                    )
                )

                ot_id_obs = actividad_obs.get(
                    "ot_id"
                )

                if (
                    not ot_lookup_obs.empty
                    and ot_id_obs
                    in ot_lookup_obs.index
                ):

                    ot_obs = ot_lookup_obs.loc[
                        ot_id_obs
                    ]

                    ot_numero_obs = str(
                        ot_obs.get(
                            "ot",
                            ""
                        )
                    )

                    equipo_obs = str(
                        ot_obs.get(
                            "equipo",
                            ""
                        )
                    )

            observaciones.append(
                f"OT {ot_numero_obs} | "
                f"{descripcion_obs} | "
                f"{observacion}"
            )

    if not observaciones:
        observaciones = [
            "Sin observaciones o restricciones registradas."
        ]

    # -------------------------------------------------
    # ACTIVIDADES CRÍTICAS
    # -------------------------------------------------
    criticas = []

    if not diarios.empty and "critica" in diarios.columns:
        actividad_lookup = actividades.set_index("id")

        for _, registro in diarios[
            diarios["critica"].fillna(False)
        ].head(10).iterrows():

            actividad_id = registro.get("actividad_id")

            if actividad_id in actividad_lookup.index:
                actividad = actividad_lookup.loc[actividad_id]

                criticas.append(
                    f"{actividad.get('codigo_actividad', '')} | "
                    f"{registro.get('avance', 0)}% | "
                    f"{registro.get('descripcion_avance', '')}"
                )

    if not criticas:
        criticas = [
            "No se registraron actividades críticas en la fecha seleccionada."
        ]

    # -------------------------------------------------
    # PENDIENTES PRINCIPALES
    # -------------------------------------------------
    pendientes = estado[
        estado["avance_real"] < 100
    ].copy()

    pendientes_texto = []

    if not pendientes.empty:

        if "critica" in pendientes.columns:
            pendientes["critica"] = (
                pendientes["critica"]
                .fillna(False)
            )
            pendientes = pendientes.sort_values(
                ["critica", "avance_real"],
                ascending=[False, True]
            )
        else:
            pendientes = pendientes.sort_values(
                "avance_real",
                ascending=True
            )

        for _, actividad in pendientes.head(10).iterrows():
            pendientes_texto.append(
                f"{actividad.get('codigo_actividad', '')} | "
                f"{actividad.get('descripcion', '')} | "
                f"Avance {float(actividad.get('avance_real', 0)):.1f}%"
            )

    if not pendientes_texto:
        pendientes_texto = [
            "No existen actividades pendientes."
        ]

    return {
        "resumen": resumen,
        "actualizaciones": "\n".join(
            f"• {item}" for item in actualizaciones
        ),
        "observaciones": "\n".join(
            f"• {item}" for item in observaciones
        ),
        "criticas": "\n".join(
            f"• {item}" for item in criticas
        ),
        "pendientes": "\n".join(
            f"• {item}" for item in pendientes_texto
        )
    }




# =====================================================
# COMPONENTES GERENCIALES PARA PDF
# =====================================================

def calcular_semaforo_pdf(
    actividades: pd.DataFrame,
    avances: pd.DataFrame
) -> pd.DataFrame:

    estado = build_activity_status(
        actividades,
        avances
    )

    if estado.empty:
        return estado

    ahora = pd.Timestamp.now(tz="America/Lima").tz_localize(None)

    inicio = pd.to_datetime(
        estado.get("inicio_plan"),
        errors="coerce"
    )

    fin = pd.to_datetime(
        estado.get("fin_plan"),
        errors="coerce"
    )

    real = pd.to_numeric(
        estado.get("avance_real", 0),
        errors="coerce"
    ).fillna(0)

    planes = []

    for ini, fn in zip(inicio, fin):

        if pd.isna(ini) or pd.isna(fn):
            planes.append(0.0)
            continue

        if fn <= ini:
            fn = ini + pd.Timedelta(minutes=1)

        if ahora <= ini:
            plan = 0.0
        elif ahora >= fn:
            plan = 100.0
        else:
            total = (fn - ini).total_seconds()
            transcurrido = (ahora - ini).total_seconds()
            plan = (
                transcurrido / total * 100
                if total > 0
                else 100.0
            )

        planes.append(
            max(0.0, min(100.0, float(plan)))
        )

    estado["PLAN ACTUAL (%)"] = planes
    estado["DESVIACIÓN (pp)"] = (
        real - estado["PLAN ACTUAL (%)"]
    ).round(1)

    if "critica" not in estado.columns:
        estado["critica"] = False

    estado["critica"] = (
        estado["critica"].fillna(False)
    )

    def clasificar(fila):

        real_f = float(
            fila.get("avance_real", 0) or 0
        )
        plan_f = float(
            fila.get("PLAN ACTUAL (%)", 0) or 0
        )
        critica = bool(
            fila.get("critica", False)
        )
        fin_f = fila.get("fin_plan")
        desviacion = real_f - plan_f

        if real_f >= 100:
            return (
                "VERDE",
                "Culminada",
                "Sin acción requerida",
                90
            )

        if (
            pd.notna(fin_f)
            and ahora > pd.Timestamp(fin_f)
            and real_f < 100
        ):
            return (
                "ROJO",
                "Crítica vencida"
                if critica else "Vencida",
                "Escalar y definir recuperación inmediata",
                1 if critica else 2
            )

        if critica:
            if desviacion < -10:
                return (
                    "ROJO",
                    "Crítica atrasada",
                    "Escalar y definir recuperación inmediata",
                    3
                )
            if desviacion < -5:
                return (
                    "NARANJA",
                    "Crítica en riesgo",
                    "Aplicar plan de recuperación",
                    5
                )
            return (
                "VERDE",
                "Crítica en línea",
                "Mantener seguimiento cercano",
                30
            )

        if desviacion < -20:
            return (
                "ROJO",
                "Atraso crítico",
                "Intervención inmediata / reprogramar recursos",
                4
            )
        if desviacion < -10:
            return (
                "NARANJA",
                "Atrasada",
                "Definir plan de recuperación",
                6
            )
        if desviacion < -5:
            return (
                "AMARILLO",
                "En riesgo",
                "Seguimiento del supervisor",
                10
            )

        return (
            "VERDE",
            "En línea",
            "Sin acción requerida",
            40
        )

    resultado = estado.apply(
        clasificar,
        axis=1
    )

    estado["NIVEL"] = resultado.map(
        lambda x: x[0]
    )
    estado["ALERTA"] = resultado.map(
        lambda x: x[1]
    )
    estado["ACCIÓN REQUERIDA"] = resultado.map(
        lambda x: x[2]
    )
    estado["_PRIORIDAD"] = resultado.map(
        lambda x: x[3]
    )

    return estado


def construir_curva_s_pdf(
    actividades: pd.DataFrame,
    avances: pd.DataFrame
):

    curva = build_s_curve(
        actividades,
        avances
    )

    if curva.empty:
        return None

    curva = curva.copy()

    if "fecha" not in curva.columns:
        return None

    curva["fecha"] = pd.to_datetime(
        curva["fecha"],
        errors="coerce"
    )

    curva = curva.dropna(
        subset=["fecha"]
    )

    if curva.empty:
        return None

    # Reducir puntos si la curva es muy extensa.
    if len(curva) > 24:
        indices = np.linspace(
            0,
            len(curva) - 1,
            24
        ).astype(int)
        curva = curva.iloc[
            sorted(set(indices))
        ].copy()

    width = 500
    height = 220

    left = 48
    right = 18
    bottom = 38
    top = 22

    plot_w = width - left - right
    plot_h = height - bottom - top

    drawing = Drawing(
        width,
        height
    )

    # Ejes y grilla discreta.
    for valor in [0, 25, 50, 75, 100]:

        y = bottom + (
            valor / 100.0
        ) * plot_h

        drawing.add(
            Line(
                left,
                y,
                width - right,
                y,
                strokeColor=colors.HexColor("#E4E7EC"),
                strokeWidth=0.6
            )
        )

        drawing.add(
            String(
                12,
                y - 3,
                f"{valor}%",
                fontName="Helvetica",
                fontSize=7,
                fillColor=colors.HexColor("#667085")
            )
        )

    drawing.add(
        Line(
            left,
            bottom,
            left,
            height - top,
            strokeColor=colors.HexColor("#98A2B3"),
            strokeWidth=0.8
        )
    )

    drawing.add(
        Line(
            left,
            bottom,
            width - right,
            bottom,
            strokeColor=colors.HexColor("#98A2B3"),
            strokeWidth=0.8
        )
    )

    n = len(curva)

    def puntos(columna):

        valores = pd.to_numeric(
            curva[columna],
            errors="coerce"
        ).fillna(0).clip(
            lower=0,
            upper=100
        )

        resultado = []

        for i, valor in enumerate(valores):

            x = (
                left
                if n <= 1
                else left + (
                    i / (n - 1)
                ) * plot_w
            )

            y = bottom + (
                float(valor) / 100.0
            ) * plot_h

            resultado.extend(
                [x, y]
            )

        return resultado

    if "PLAN" in curva.columns:
        drawing.add(
            PolyLine(
                puntos("PLAN"),
                strokeColor=colors.HexColor("#082D55"),
                strokeWidth=2
            )
        )

    if "REAL" in curva.columns:
        drawing.add(
            PolyLine(
                puntos("REAL"),
                strokeColor=colors.HexColor("#D92D20"),
                strokeWidth=2
            )
        )

    # Etiquetas de fechas: inicio, medio y fin.
    posiciones = sorted(
        set(
            [
                0,
                max(0, n // 2),
                max(0, n - 1)
            ]
        )
    )

    for idx in posiciones:

        fecha = curva.iloc[idx]["fecha"]

        x = (
            left
            if n <= 1
            else left + (
                idx / (n - 1)
            ) * plot_w
        )

        drawing.add(
            String(
                x - 20,
                16,
                fecha.strftime("%d/%m %H:%M"),
                fontName="Helvetica",
                fontSize=6.5,
                fillColor=colors.HexColor("#667085")
            )
        )

    drawing.add(
        Line(
            340,
            205,
            360,
            205,
            strokeColor=colors.HexColor("#082D55"),
            strokeWidth=2
        )
    )
    drawing.add(
        String(
            365,
            201,
            "PLAN",
            fontName="Helvetica-Bold",
            fontSize=7,
            fillColor=colors.HexColor("#344054")
        )
    )

    drawing.add(
        Line(
            415,
            205,
            435,
            205,
            strokeColor=colors.HexColor("#D92D20"),
            strokeWidth=2
        )
    )
    drawing.add(
        String(
            440,
            201,
            "REAL",
            fontName="Helvetica-Bold",
            fontSize=7,
            fillColor=colors.HexColor("#344054")
        )
    )

    return drawing


# =====================================================
# REPORTE PDF EJECUTIVO POR ÁREA
# =====================================================

def construir_pdf_ejecutivo_area(
    ots: pd.DataFrame,
    actividades: pd.DataFrame,
    avances: pd.DataFrame,
    nombre_area: str
) -> bytes:

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=30,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloMainin",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#082D55"),
        spaceAfter=8
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloMainin",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#667085"),
        spaceAfter=14
    )

    estilo_h2 = ParagraphStyle(
        "H2Mainin",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#082D55"),
        spaceBefore=8,
        spaceAfter=8
    )

    story = []

    story.append(
        Paragraph(
            "PDP CONTROL CENTER QUELLAVECO - MAININ",
            estilo_titulo
        )
    )

    story.append(
        Paragraph(
            f"Informe Ejecutivo - {nombre_area}",
            estilo_subtitulo
        )
    )

    story.append(
        Paragraph(
            f"Fecha de emisión: "
            f"{datetime.now():%d/%m/%Y %H:%M}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 12))

    kpis = compute_kpis(
        actividades,
        avances
    )

    total_ots = (
        int(ots["id"].nunique())
        if not ots.empty and "id" in ots.columns
        else 0
    )

    resumen_data = [
        ["Indicador", "Valor"],
        ["OTs", str(total_ots)],
        ["Actividades", str(kpis["actividades"])],
        [
            "Avance general",
            f"{kpis['avance_general']:.1f}%"
        ],
        [
            "SPI",
            f"{kpis['spi']:.2f}"
        ],
        [
            "HH planificadas",
            f"{kpis['hh_plan']:.0f}"
        ],
        [
            "HH ganadas",
            f"{kpis['hh_ganadas']:.0f}"
        ],
        [
            "Culminadas",
            str(kpis["culminadas"])
        ],
        [
            "En ejecución",
            str(kpis["parciales"])
        ],
        [
            "No iniciadas",
            str(kpis["no_iniciadas"])
        ]
    ]

    tabla_resumen = Table(
        resumen_data,
        colWidths=[240, 160]
    )

    tabla_resumen.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#082D55")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D0D5DD")
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F3F6F9")
                ]
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(
        Paragraph(
            "Indicadores principales",
            estilo_h2
        )
    )

    story.append(tabla_resumen)
    story.append(Spacer(1, 14))

    # =================================================
    # CURVA S
    # =================================================

    story.append(
        Paragraph(
            "Curva S - Plan vs Real",
            estilo_h2
        )
    )

    curva_pdf = construir_curva_s_pdf(
        actividades,
        avances
    )

    if curva_pdf is not None:
        story.append(curva_pdf)
    else:
        story.append(
            Paragraph(
                "No existe información suficiente para construir la Curva S.",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 12))

    # =================================================
    # SEMÁFORO EJECUTIVO
    # =================================================

    estado_gerencial = calcular_semaforo_pdf(
        actividades,
        avances
    )

    story.append(
        Paragraph(
            "Semáforo ejecutivo",
            estilo_h2
        )
    )

    if estado_gerencial.empty:

        story.append(
            Paragraph(
                "No existe información suficiente para calcular alertas.",
                styles["BodyText"]
            )
        )

    else:

        conteos = {
            nivel: int(
                (
                    estado_gerencial["NIVEL"]
                    == nivel
                ).sum()
            )
            for nivel in [
                "VERDE",
                "AMARILLO",
                "NARANJA",
                "ROJO"
            ]
        }

        resumen_semaforo = [
            [
                "En línea",
                "En riesgo",
                "Recuperación",
                "Intervención"
            ],
            [
                str(conteos["VERDE"]),
                str(conteos["AMARILLO"]),
                str(conteos["NARANJA"]),
                str(conteos["ROJO"])
            ]
        ]

        tabla_semaforo = Table(
            resumen_semaforo,
            colWidths=[100, 100, 100, 100]
        )

        tabla_semaforo.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#F2F4F7")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#344054")
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, 1),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, 1),
                    14
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D0D5DD")
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

        story.append(tabla_semaforo)
        story.append(Spacer(1, 10))

        foco = (
            estado_gerencial[
                estado_gerencial[
                    "NIVEL"
                ].isin(
                    [
                        "ROJO",
                        "NARANJA",
                        "AMARILLO"
                    ]
                )
            ]
            .sort_values(
                [
                    "_PRIORIDAD",
                    "avance_real"
                ],
                ascending=[
                    True,
                    True
                ]
            )
            .head(10)
            .copy()
        )

        if foco.empty:

            story.append(
                Paragraph(
                    "No existen desviaciones que requieran atención gerencial.",
                    styles["BodyText"]
                )
            )

        else:

            story.append(
                Paragraph(
                    "Foco de atención gerencial",
                    styles["Heading3"]
                )
            )

            foco_data = [
                [
                    "Nivel",
                    "Actividad",
                    "Plan",
                    "Real",
                    "Desv.",
                    "Acción requerida"
                ]
            ]

            for _, fila in foco.iterrows():

                foco_data.append([
                    str(
                        fila.get(
                            "NIVEL",
                            ""
                        )
                    ),
                    Paragraph(
                        (
                            str(
                                fila.get(
                                    "codigo_actividad",
                                    ""
                                )
                            )
                            + " - "
                            + str(
                                fila.get(
                                    "descripcion",
                                    ""
                                )
                            )
                        )[:120],
                        styles["BodyText"]
                    ),
                    f"{float(fila.get('PLAN ACTUAL (%)', 0)):.0f}%",
                    f"{float(fila.get('avance_real', 0)):.0f}%",
                    f"{float(fila.get('DESVIACIÓN (pp)', 0)):.0f}",
                    Paragraph(
                        str(
                            fila.get(
                                "ACCIÓN REQUERIDA",
                                ""
                            )
                        ),
                        styles["BodyText"]
                    )
                ])

            tabla_foco = Table(
                foco_data,
                colWidths=[
                    48,
                    150,
                    38,
                    38,
                    38,
                    120
                ],
                repeatRows=1
            )

            tabla_foco.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#082D55")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        6.8
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor("#D0D5DD")
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F8FAFC")
                        ]
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    )
                ])
            )

            story.append(tabla_foco)

    story.append(Spacer(1, 14))

    if not avances.empty:

        story.append(
            Paragraph(
                "Resumen de avances",
                estilo_h2
            )
        )

        fecha_hoy = pd.Timestamp.now(
            tz="America/Lima"
        ).date()

        secciones = construir_secciones_informe_diario(
            ots,
            actividades,
            avances,
            nombre_area,
            fecha_hoy
        )

        for titulo, clave in [
            (
                "Resumen ejecutivo",
                "resumen"
            ),
            (
                "Principales actualizaciones",
                "actualizaciones"
            ),
            (
                "Observaciones / Restricciones",
                "observaciones"
            ),
            (
                "Actividades críticas",
                "criticas"
            ),
            (
                "Pendientes principales",
                "pendientes"
            )
        ]:

            story.append(
                Paragraph(
                    titulo,
                    styles["Heading3"]
                )
            )

            contenido = (
                secciones.get(clave, "")
                or ""
            )

            for linea in contenido.splitlines():

                if linea.strip():

                    linea_segura = (
                        linea
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )

                    story.append(
                        Paragraph(
                            linea_segura,
                            styles["BodyText"]
                        )
                    )

                else:
                    story.append(
                        Spacer(1, 4)
                    )

            story.append(
                Spacer(1, 6)
            )

    story.append(
        Paragraph(
            "Detalle por OT",
            estilo_h2
        )
    )

    estado = build_activity_status(
        actividades,
        avances
    )

    if (
        not estado.empty
        and not ots.empty
        and "ot_id" in estado.columns
    ):

        detalle_ot = (
            estado
            .groupby(
                "ot_id",
                dropna=False
            )
            .agg(
                actividades=("id", "count"),
                culminadas=(
                    "avance_real",
                    lambda serie: int(
                        (serie >= 100).sum()
                    )
                ),
                en_ejecucion=(
                    "avance_real",
                    lambda serie: int(
                        (
                            (serie > 0)
                            & (serie < 100)
                        ).sum()
                    )
                ),
                no_iniciadas=(
                    "avance_real",
                    lambda serie: int(
                        (serie <= 0).sum()
                    )
                ),
                avance_ot=(
                    "avance_real",
                    "mean"
                )
            )
            .reset_index()
            .merge(
                ots[
                    [
                        "id",
                        "ot",
                        "equipo"
                    ]
                ],
                left_on="ot_id",
                right_on="id",
                how="left"
            )
        )

        tabla_ot_data = [
            [
                "OT",
                "Equipo",
                "Act.",
                "Avance",
                "Culm.",
                "Ejec.",
                "No inic."
            ]
        ]

        for _, fila in detalle_ot.sort_values(
            "ot"
        ).iterrows():

            tabla_ot_data.append([
                str(
                    fila.get(
                        "ot",
                        ""
                    )
                ),
                str(
                    fila.get(
                        "equipo",
                        ""
                    )
                ),
                str(
                    int(
                        fila.get(
                            "actividades",
                            0
                        )
                    )
                ),
                f"{float(fila.get('avance_ot', 0)):.1f}%",
                str(
                    int(
                        fila.get(
                            "culminadas",
                            0
                        )
                    )
                ),
                str(
                    int(
                        fila.get(
                            "en_ejecucion",
                            0
                        )
                    )
                ),
                str(
                    int(
                        fila.get(
                            "no_iniciadas",
                            0
                        )
                    )
                )
            ])

        tabla_ot = Table(
            tabla_ot_data,
            colWidths=[
                68,
                120,
                42,
                55,
                42,
                42,
                48
            ],
            repeatRows=1
        )

        tabla_ot.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#082D55")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7.5
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D0D5DD")
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F8FAFC")
                    ]
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ])
        )

        story.append(tabla_ot)

    else:

        story.append(
            Paragraph(
                "No existe información disponible por OT.",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "MAININ - Mantenimiento e Ingeniería Industrial",
            estilo_subtitulo
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()




# =====================================================
# REPORTE PDF DE DESEMPEÑO POR SUPERVISOR
# =====================================================

def lista_supervisores_reporte(
    actividades: pd.DataFrame
):
    """
    Devuelve los supervisores con nombre válido,
    ordenados alfabéticamente.
    """
    if (
        actividades is None
        or actividades.empty
        or "supervisor" not in actividades.columns
    ):
        return []

    return sorted(
        {
            str(valor or "").strip()
            for valor in actividades["supervisor"].tolist()
            if str(valor or "").strip()
        }
    )


def filtrar_reporte_supervisor(
    ots: pd.DataFrame,
    actividades: pd.DataFrame,
    avances: pd.DataFrame,
    supervisor: str
):
    """
    Filtra OTs, actividades y avances para un supervisor.
    Los KPIs se recalculan exclusivamente con sus actividades.
    """
    if actividades is None or actividades.empty:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame()
        )

    nombre = str(supervisor or "").strip()

    serie_supervisor = (
        actividades["supervisor"]
        .fillna("")
        .astype(str)
        .str.strip()
        if "supervisor" in actividades.columns
        else pd.Series(
            "",
            index=actividades.index
        )
    )

    actividades_sup = actividades[
        serie_supervisor.eq(nombre)
    ].copy()

    if actividades_sup.empty:
        return (
            pd.DataFrame(),
            actividades_sup,
            pd.DataFrame()
        )

    ids_actividades = (
        actividades_sup["id"]
        .dropna()
        .tolist()
        if "id" in actividades_sup.columns
        else []
    )

    if (
        avances is not None
        and not avances.empty
        and "actividad_id" in avances.columns
        and ids_actividades
    ):
        avances_sup = avances[
            avances["actividad_id"].isin(
                ids_actividades
            )
        ].copy()
    else:
        avances_sup = pd.DataFrame(
            columns=(
                avances.columns
                if avances is not None
                else []
            )
        )

    ids_ot = (
        actividades_sup["ot_id"]
        .dropna()
        .unique()
        .tolist()
        if "ot_id" in actividades_sup.columns
        else []
    )

    if (
        ots is not None
        and not ots.empty
        and "id" in ots.columns
        and ids_ot
    ):
        ots_sup = ots[
            ots["id"].isin(ids_ot)
        ].copy()
    else:
        ots_sup = pd.DataFrame(
            columns=(
                ots.columns
                if ots is not None
                else []
            )
        )

    return (
        ots_sup,
        actividades_sup,
        avances_sup
    )


def construir_pdf_supervisor(
    ots: pd.DataFrame,
    actividades: pd.DataFrame,
    avances: pd.DataFrame,
    nombre_area: str,
    supervisor: str
) -> bytes:
    """
    Genera un PDF horizontal con:
    - identificación del supervisor
    - KPIs recalculados solo con sus actividades
    - resumen de estado
    - detalle completo de sus actividades
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24
    )

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloSupervisor",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#082D55"),
        spaceAfter=5
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloSupervisor",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#667085"),
        spaceAfter=10
    )

    estilo_h2 = ParagraphStyle(
        "H2Supervisor",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#082D55"),
        spaceBefore=7,
        spaceAfter=6
    )

    estilo_tabla = ParagraphStyle(
        "TablaSupervisor",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=6.2,
        leading=7.4,
        textColor=colors.HexColor("#344054")
    )

    estilo_tabla_bold = ParagraphStyle(
        "TablaSupervisorBold",
        parent=estilo_tabla,
        fontName="Helvetica-Bold"
    )

    story = []

    story.append(
        Paragraph(
            "PDP CONTROL CENTER QUELLAVECO - MAININ",
            estilo_titulo
        )
    )

    story.append(
        Paragraph(
            "Reporte de desempeño por supervisor",
            estilo_subtitulo
        )
    )

    datos_identificacion = [
        [
            "Área",
            str(nombre_area or ""),
            "Supervisor",
            str(supervisor or "")
        ],
        [
            "Fecha de emisión",
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),
            "Tipo de reporte",
            "KPIs y actividades"
        ]
    ]

    tabla_identificacion = Table(
        datos_identificacion,
        colWidths=[
            82, 270, 92, 270
        ]
    )

    tabla_identificacion.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EEF4FB")
            ),
            (
                "BACKGROUND",
                (2, 0),
                (2, -1),
                colors.HexColor("#EEF4FB")
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (2, 0),
                (2, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#D0D5DD")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(tabla_identificacion)
    story.append(Spacer(1, 10))

    kpis = compute_kpis(
        actividades,
        avances
    )

    total_ots = (
        int(ots["id"].nunique())
        if (
            ots is not None
            and not ots.empty
            and "id" in ots.columns
        )
        else 0
    )

    plan = float(
        kpis.get(
            "avance_plan",
            0
        ) or 0
    )

    real = float(
        kpis.get(
            "avance_general",
            0
        ) or 0
    )

    brecha = real - plan

    story.append(
        Paragraph(
            "Indicadores del supervisor",
            estilo_h2
        )
    )

    kpi_data = [
        [
            "OTs",
            "Actividades",
            "Plan actual",
            "Avance real",
            "Brecha",
            "SPI"
        ],
        [
            str(total_ots),
            str(
                int(
                    kpis.get(
                        "actividades",
                        0
                    ) or 0
                )
            ),
            f"{plan:.1f}%",
            f"{real:.1f}%",
            f"{brecha:+.1f} pp",
            f"{float(kpis.get('spi', 0) or 0):.2f}"
        ],
        [
            "Culminadas",
            "En ejecución",
            "No iniciadas",
            "HH plan",
            "HH ganadas",
            "Pendientes"
        ],
        [
            str(
                int(
                    kpis.get(
                        "culminadas",
                        0
                    ) or 0
                )
            ),
            str(
                int(
                    kpis.get(
                        "parciales",
                        0
                    ) or 0
                )
            ),
            str(
                int(
                    kpis.get(
                        "no_iniciadas",
                        0
                    ) or 0
                )
            ),
            f"{float(kpis.get('hh_plan', 0) or 0):.0f}",
            f"{float(kpis.get('hh_ganadas', 0) or 0):.0f}",
            str(
                int(
                    kpis.get(
                        "pendientes",
                        0
                    ) or 0
                )
            )
        ]
    ]

    tabla_kpis = Table(
        kpi_data,
        colWidths=[122] * 6
    )

    tabla_kpis.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#082D55")
            ),
            (
                "BACKGROUND",
                (0, 2),
                (-1, 2),
                colors.HexColor("#EEF4FB")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "TEXTCOLOR",
                (0, 2),
                (-1, 2),
                colors.HexColor("#344054")
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 2),
                (-1, 2),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 3),
                (-1, 3),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#D0D5DD")
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(tabla_kpis)
    story.append(Spacer(1, 10))

    estado = calcular_semaforo_pdf(
        actividades,
        avances
    )

    if (
        not estado.empty
        and ots is not None
        and not ots.empty
        and "ot_id" in estado.columns
    ):
        datos_ot = (
            ots[
                [
                    "id",
                    "ot",
                    "equipo"
                ]
            ]
            .rename(
                columns={
                    "id": "ot_id"
                }
            )
        )

        estado = estado.merge(
            datos_ot,
            on="ot_id",
            how="left"
        )

    story.append(
        Paragraph(
            "Detalle de actividades",
            estilo_h2
        )
    )

    if estado.empty:

        story.append(
            Paragraph(
                "No existen actividades para el supervisor seleccionado.",
                styles["BodyText"]
            )
        )

    else:

        estado = estado.copy()

        estado["_REAL"] = pd.to_numeric(
            estado.get(
                "avance_real",
                0
            ),
            errors="coerce"
        ).fillna(0)

        estado["_PLAN"] = pd.to_numeric(
            estado.get(
                "PLAN ACTUAL (%)",
                0
            ),
            errors="coerce"
        ).fillna(0)

        estado = estado.sort_values(
            [
                "_PRIORIDAD",
                "_REAL",
                "codigo_actividad"
            ],
            ascending=[
                True,
                True,
                True
            ]
        )

        detalle_data = [
            [
                "OT",
                "Equipo",
                "Grupo",
                "Descripción",
                "Plan",
                "Real",
                "Brecha",
                "Estado",
                "Inicio",
                "Fin"
            ]
        ]

        for _, fila in estado.iterrows():

            inicio = pd.to_datetime(
                fila.get(
                    "inicio_plan"
                ),
                errors="coerce"
            )

            fin = pd.to_datetime(
                fila.get(
                    "fin_plan"
                ),
                errors="coerce"
            )

            descripcion = (
                fila.get(
                    "descripcion_trabajo"
                )
                or fila.get(
                    "descripcion"
                )
                or ""
            )

            detalle_data.append([
                Paragraph(
                    str(
                        fila.get(
                            "ot",
                            ""
                        )
                        or ""
                    ),
                    estilo_tabla_bold
                ),
                Paragraph(
                    str(
                        fila.get(
                            "equipo",
                            ""
                        )
                        or ""
                    ),
                    estilo_tabla
                ),
                Paragraph(
                    str(
                        fila.get(
                            "grupo",
                            ""
                        )
                        or "Sin grupo"
                    ),
                    estilo_tabla
                ),
                Paragraph(
                    str(
                        descripcion
                    )[:260],
                    estilo_tabla
                ),
                f"{float(fila.get('PLAN ACTUAL (%)', 0) or 0):.1f}%",
                f"{float(fila.get('avance_real', 0) or 0):.1f}%",
                f"{float(fila.get('DESVIACIÓN (pp)', 0) or 0):+.1f}",
                Paragraph(
                    str(
                        fila.get(
                            "ALERTA",
                            ""
                        )
                        or ""
                    ),
                    estilo_tabla
                ),
                (
                    inicio.strftime(
                        "%d/%m %H:%M"
                    )
                    if pd.notna(inicio)
                    else ""
                ),
                (
                    fin.strftime(
                        "%d/%m %H:%M"
                    )
                    if pd.notna(fin)
                    else ""
                )
            ])

        tabla_detalle = Table(
            detalle_data,
            colWidths=[
                58,
                68,
                70,
                190,
                42,
                42,
                42,
                78,
                65,
                65
            ],
            repeatRows=1
        )

        estilo_detalle = [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#082D55")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6.2
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                colors.HexColor("#D0D5DD")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "ALIGN",
                (4, 1),
                (6, -1),
                "CENTER"
            ),
            (
                "ALIGN",
                (8, 1),
                (9, -1),
                "CENTER"
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F8FAFC")
                ]
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3.5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3.5
            )
        ]

        # Semáforo visual en la columna Estado.
        for indice_fila, (_, fila) in enumerate(
            estado.iterrows(),
            start=1
        ):

            nivel = str(
                fila.get(
                    "NIVEL",
                    ""
                )
                or ""
            ).upper()

            mapa_color = {
                "VERDE": "#E7F8EF",
                "AMARILLO": "#FFF7D6",
                "NARANJA": "#FFF0E0",
                "ROJO": "#FDE8E7"
            }

            if nivel in mapa_color:
                estilo_detalle.append(
                    (
                        "BACKGROUND",
                        (7, indice_fila),
                        (7, indice_fila),
                        colors.HexColor(
                            mapa_color[nivel]
                        )
                    )
                )

        tabla_detalle.setStyle(
            TableStyle(
                estilo_detalle
            )
        )

        story.append(tabla_detalle)

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "MAININ - PDP Control Center Quellaveco",
            estilo_subtitulo
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()



# =====================================================
# INFORME FOTOGRÁFICO POR OT
# =====================================================

def descargar_evidencia_pdf(evidencia):
    """
    Descarga desde Supabase Storage los bytes de una evidencia
    para incorporarla al PDF. El bucket permanece privado.
    """
    path = extraer_path_evidencia(
        evidencia
    )

    if not path:
        return None

    try:
        respuesta = (
            supabase_admin
            .storage
            .from_(BUCKET_EVIDENCIAS)
            .download(path)
        )

        if isinstance(
            respuesta,
            (bytes, bytearray)
        ):
            return bytes(respuesta)

        contenido = getattr(
            respuesta,
            "content",
            None
        )

        if isinstance(
            contenido,
            (bytes, bytearray)
        ):
            return bytes(contenido)

        return None

    except Exception:
        return None


def preparar_imagen_pdf(
    evidencia,
    ancho_max=205,
    alto_max=138
):
    """
    Convierte la evidencia a JPEG y devuelve un RLImage
    manteniendo la proporción y orientación de celular.
    """
    contenido = descargar_evidencia_pdf(
        evidencia
    )

    if not contenido:
        return None

    try:
        imagen = Image.open(
            io.BytesIO(contenido)
        )

        imagen = ImageOps.exif_transpose(
            imagen
        )

        if imagen.mode != "RGB":
            imagen = imagen.convert(
                "RGB"
            )

        ancho_original, alto_original = (
            imagen.size
        )

        if (
            ancho_original <= 0
            or alto_original <= 0
        ):
            return None

        escala = min(
            ancho_max / ancho_original,
            alto_max / alto_original,
            1.0
        )

        ancho_pdf = max(
            1,
            ancho_original * escala
        )

        alto_pdf = max(
            1,
            alto_original * escala
        )

        buffer_imagen = io.BytesIO()

        imagen.save(
            buffer_imagen,
            format="JPEG",
            quality=82,
            optimize=True
        )

        buffer_imagen.seek(0)

        return RLImage(
            buffer_imagen,
            width=ancho_pdf,
            height=alto_pdf
        )

    except Exception:
        return None


def contar_fotos_por_etapa(
    avances_ot: pd.DataFrame
):
    conteo = {
        "INICIO": 0,
        "DURANTE": 0,
        "FINAL": 0
    }

    if (
        avances_ot is None
        or avances_ot.empty
    ):
        return conteo

    for _, registro in (
        avances_ot.iterrows()
    ):

        etapa = str(
            registro.get(
                "tipo_evidencia",
                ""
            )
            or ""
        ).strip().upper()

        if etapa not in conteo:
            continue

        evidencias = (
            registro.get(
                "evidencias"
            )
            or []
        )

        if isinstance(
            evidencias,
            (list, tuple)
        ):
            conteo[etapa] += len(
                evidencias
            )

    return conteo


def construir_fotos_etapa_pdf(
    avances_ot: pd.DataFrame,
    actividades_ot: pd.DataFrame,
    etapa: str,
    estilo_caption,
    estilo_vacio
):
    """
    Devuelve una lista de elementos ReportLab con fotografías
    de una etapa: INICIO, DURANTE o FINAL.
    """

    if (
        avances_ot is None
        or avances_ot.empty
    ):
        return [
            Paragraph(
                "Sin evidencia fotográfica registrada.",
                estilo_vacio
            )
        ]

    mapa_actividades = {}

    if (
        actividades_ot is not None
        and not actividades_ot.empty
        and "id" in actividades_ot.columns
    ):
        mapa_actividades = (
            actividades_ot
            .set_index("id")
            .to_dict("index")
        )

    tarjetas = []

    registros_etapa = (
        avances_ot[
            avances_ot[
                "tipo_evidencia"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
            .eq(etapa)
        ]
        if "tipo_evidencia"
        in avances_ot.columns
        else pd.DataFrame()
    )

    if registros_etapa.empty:
        return [
            Paragraph(
                "Sin evidencia fotográfica registrada.",
                estilo_vacio
            )
        ]

    registros_etapa = (
        registros_etapa
        .copy()
    )

    if "fecha_registro" in (
        registros_etapa.columns
    ):
        registros_etapa[
            "_fecha_orden"
        ] = pd.to_datetime(
            registros_etapa[
                "fecha_registro"
            ],
            errors="coerce",
            utc=True
        )

        registros_etapa = (
            registros_etapa
            .sort_values(
                "_fecha_orden"
            )
        )

    for _, registro in (
        registros_etapa.iterrows()
    ):

        actividad = mapa_actividades.get(
            registro.get(
                "actividad_id"
            ),
            {}
        )

        evidencias = (
            registro.get(
                "evidencias"
            )
            or []
        )

        if not isinstance(
            evidencias,
            (list, tuple)
        ):
            continue

        fecha_texto = ""

        fecha_registro = pd.to_datetime(
            registro.get(
                "fecha_registro"
            ),
            errors="coerce",
            utc=True
        )

        if pd.notna(
            fecha_registro
        ):
            fecha_registro = (
                fecha_registro
                .tz_convert(
                    "America/Lima"
                )
            )

            fecha_texto = (
                fecha_registro.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

        codigo = str(
            actividad.get(
                "codigo_actividad",
                ""
            )
            or ""
        )

        grupo = str(
            actividad.get(
                "grupo",
                ""
            )
            or ""
        )

        avance = float(
            registro.get(
                "avance",
                0
            )
            or 0
        )

        descripcion_avance = str(
            registro.get(
                "descripcion_avance",
                ""
            )
            or ""
        ).strip()

        for evidencia in evidencias:

            imagen_pdf = (
                preparar_imagen_pdf(
                    evidencia
                )
            )

            if imagen_pdf is None:
                continue

            titulo_caption = (
                f"<b>{codigo or 'Actividad'}</b>"
            )

            if grupo:
                titulo_caption += (
                    f" · Grupo {grupo}"
                )

            titulo_caption += (
                f" · {avance:.0f}%"
            )

            if fecha_texto:
                titulo_caption += (
                    f"<br/>{fecha_texto}"
                )

            if descripcion_avance:
                titulo_caption += (
                    "<br/>"
                    + descripcion_avance[:150]
                )

            caption = Paragraph(
                titulo_caption,
                estilo_caption
            )

            tarjeta = Table(
                [
                    [imagen_pdf],
                    [caption]
                ],
                colWidths=[218]
            )

            tarjeta.setStyle(
                TableStyle([
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#D0D5DD"
                        )
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.white
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, 0),
                        "CENTER"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, 0),
                        5
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        5
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "TOPPADDING",
                        (0, 1),
                        (-1, 1),
                        4
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 1),
                        (-1, 1),
                        5
                    )
                ])
            )

            tarjetas.append(
                tarjeta
            )

    if not tarjetas:
        return [
            Paragraph(
                "Sin evidencia fotográfica disponible para insertar en el PDF.",
                estilo_vacio
            )
        ]

    elementos = []

    # Tres fotografías por fila para aprovechar A4 horizontal.
    for inicio in range(
        0,
        len(tarjetas),
        3
    ):

        fila = tarjetas[
            inicio:inicio + 3
        ]

        while len(fila) < 3:
            fila.append("")

        tabla_fotos = Table(
            [fila],
            colWidths=[
                232,
                232,
                232
            ]
        )

        tabla_fotos.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

        elementos.append(
            tabla_fotos
        )

    return elementos


def construir_pdf_fotografico_ot(
    ot_info: dict,
    actividades_ot: pd.DataFrame,
    avances_ot: pd.DataFrame,
    nombre_area: str
) -> bytes:
    """
    Informe fotográfico por OT:
    - cabecera de OT / equipo / descripción
    - KPIs de la OT
    - cuadro de actividades
    - evidencias ANTES (INICIO), DURANTE y DESPUÉS (FINAL)
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=22,
        bottomMargin=22
    )

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "FotoOTTitulo",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#082D55"
        ),
        spaceAfter=3
    )

    estilo_sub = ParagraphStyle(
        "FotoOTSub",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#667085"
        ),
        spaceAfter=9
    )

    estilo_h2 = ParagraphStyle(
        "FotoOTH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor(
            "#082D55"
        ),
        spaceBefore=6,
        spaceAfter=5
    )

    estilo_body = ParagraphStyle(
        "FotoOTBody",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor(
            "#344054"
        )
    )

    estilo_tabla = ParagraphStyle(
        "FotoOTTabla",
        parent=estilo_body,
        fontSize=6.2,
        leading=7.5
    )

    estilo_caption = ParagraphStyle(
        "FotoOTCaption",
        parent=estilo_body,
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER
    )

    estilo_vacio = ParagraphStyle(
        "FotoOTVacio",
        parent=estilo_body,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor(
            "#98A2B3"
        )
    )

    story = []

    ot_numero = str(
        ot_info.get(
            "ot",
            ""
        )
        or ""
    )

    equipo = str(
        ot_info.get(
            "equipo",
            ""
        )
        or "Sin equipo"
    )

    descripcion_ot = str(
        ot_info.get(
            "descripcion",
            ""
        )
        or ""
    )

    story.append(
        Paragraph(
            "MAININ · PDP CONTROL CENTER QUELLAVECO",
            estilo_titulo
        )
    )

    story.append(
        Paragraph(
            (
                f"INFORME FOTOGRÁFICO POR OT · "
                f"{nombre_area}"
            ),
            estilo_sub
        )
    )

    cabecera = Table(
        [
            [
                "OT",
                ot_numero,
                "EQUIPO",
                equipo
            ],
            [
                "ÁREA",
                str(
                    nombre_area
                    or ""
                ),
                "FECHA DE EMISIÓN",
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            ]
        ],
        colWidths=[
            65,
            270,
            85,
            300
        ]
    )

    cabecera.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor(
                    "#EEF4FB"
                )
            ),
            (
                "BACKGROUND",
                (2, 0),
                (2, -1),
                colors.HexColor(
                    "#EEF4FB"
                )
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (2, 0),
                (2, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor(
                    "#D0D5DD"
                )
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(
        cabecera
    )

    if descripcion_ot:
        story.append(
            Spacer(1, 7)
        )

        story.append(
            Paragraph(
                (
                    "<b>Descripción de la OT:</b> "
                    + descripcion_ot
                ),
                estilo_body
            )
        )

    story.append(
        Spacer(1, 8)
    )

    kpis_ot = compute_kpis(
        actividades_ot,
        avances_ot
    )

    plan_ot = float(
        kpis_ot.get(
            "avance_plan",
            0
        )
        or 0
    )

    real_ot = float(
        kpis_ot.get(
            "avance_general",
            0
        )
        or 0
    )

    brecha_ot = (
        real_ot
        - plan_ot
    )

    conteo_fotos = (
        contar_fotos_por_etapa(
            avances_ot
        )
    )

    kpi_data = [
        [
            "Actividades",
            "Plan actual",
            "Avance real",
            "Brecha",
            "Culminadas",
            "HH plan",
            "HH ganadas"
        ],
        [
            str(
                int(
                    kpis_ot.get(
                        "actividades",
                        0
                    )
                    or 0
                )
            ),
            f"{plan_ot:.1f}%",
            f"{real_ot:.1f}%",
            f"{brecha_ot:+.1f} pp",
            str(
                int(
                    kpis_ot.get(
                        "culminadas",
                        0
                    )
                    or 0
                )
            ),
            f"{float(kpis_ot.get('hh_plan', 0) or 0):.0f}",
            f"{float(kpis_ot.get('hh_ganadas', 0) or 0):.0f}"
        ]
    ]

    tabla_kpis = Table(
        kpi_data,
        colWidths=[
            102,
            102,
            102,
            102,
            102,
            102,
            102
        ]
    )

    tabla_kpis.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#082D55"
                )
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor(
                    "#D0D5DD"
                )
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(
        tabla_kpis
    )

    story.append(
        Spacer(1, 7)
    )

    fotos_resumen = Table(
        [
            [
                "ANTES / INICIO",
                "DURANTE",
                "DESPUÉS / FINAL"
            ],
            [
                str(
                    conteo_fotos["INICIO"]
                ),
                str(
                    conteo_fotos["DURANTE"]
                ),
                str(
                    conteo_fotos["FINAL"]
                )
            ]
        ],
        colWidths=[
            238,
            238,
            238
        ]
    )

    fotos_resumen.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#F2F4F7"
                )
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor(
                    "#D0D5DD"
                )
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            )
        ])
    )

    story.append(
        fotos_resumen
    )

    story.append(
        Paragraph(
            "Cuadro de actividades",
            estilo_h2
        )
    )

    estado_ot = calcular_semaforo_pdf(
        actividades_ot,
        avances_ot
    )

    if estado_ot.empty:

        story.append(
            Paragraph(
                "No existen actividades registradas para esta OT.",
                estilo_vacio
            )
        )

    else:

        detalle_data = [
            [
                "GRUPO",
                "SUPERVISOR",
                "DESCRIPCIÓN",
                "PLAN",
                "REAL",
                "ESTADO"
            ]
        ]

        for _, fila in (
            estado_ot.iterrows()
        ):

            descripcion_actividad = (
                fila.get(
                    "descripcion_trabajo"
                )
                or fila.get(
                    "descripcion"
                )
                or ""
            )

            detalle_data.append([
                Paragraph(
                    str(
                        fila.get(
                            "grupo",
                            ""
                        )
                        or "Sin grupo"
                    ),
                    estilo_tabla
                ),
                Paragraph(
                    str(
                        fila.get(
                            "supervisor",
                            ""
                        )
                        or ""
                    ),
                    estilo_tabla
                ),
                Paragraph(
                    str(
                        descripcion_actividad
                    )[:350],
                    estilo_tabla
                ),
                f"{float(fila.get('PLAN ACTUAL (%)', 0) or 0):.1f}%",
                f"{float(fila.get('avance_real', 0) or 0):.1f}%",
                Paragraph(
                    str(
                        fila.get(
                            "ALERTA",
                            ""
                        )
                        or ""
                    ),
                    estilo_tabla
                )
            ])

        tabla_detalle = Table(
            detalle_data,
            colWidths=[
                80,
                105,
                335,
                55,
                55,
                85
            ],
            repeatRows=1
        )

        tabla_detalle.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#082D55"
                    )
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    6.3
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.HexColor(
                        "#D0D5DD"
                    )
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "ALIGN",
                    (3, 1),
                    (4, -1),
                    "CENTER"
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor(
                            "#F8FAFC"
                        )
                    ]
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                )
            ])
        )

        story.append(
            tabla_detalle
        )

    # Una página nueva antes del registro fotográfico.
    story.append(
        PageBreak()
    )

    etapas_pdf = [
        (
            "INICIO",
            "ANTES · INICIO"
        ),
        (
            "DURANTE",
            "DURANTE · EJECUCIÓN"
        ),
        (
            "FINAL",
            "DESPUÉS · FINAL"
        )
    ]

    for indice_etapa, (
        etapa,
        titulo_etapa
    ) in enumerate(etapas_pdf):

        story.append(
            Paragraph(
                titulo_etapa,
                estilo_h2
            )
        )

        story.append(
            Paragraph(
                (
                    f"OT {ot_numero} · "
                    f"Equipo {equipo}"
                ),
                estilo_body
            )
        )

        story.append(
            Spacer(1, 5)
        )

        elementos_fotos = (
            construir_fotos_etapa_pdf(
                avances_ot,
                actividades_ot,
                etapa,
                estilo_caption,
                estilo_vacio
            )
        )

        story.extend(
            elementos_fotos
        )

        if indice_etapa < (
            len(etapas_pdf) - 1
        ):
            story.append(
                PageBreak()
            )

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            "MAININ · Informe generado desde PDP Control Center Quellaveco",
            estilo_sub
        )
    )

    doc.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


# =====================================================
# INFORME FOTOGRÁFICO GENERAL / POR SUPERVISOR
# =====================================================

def filtrar_datos_fotograficos_supervisor(
    df_ots: pd.DataFrame,
    df_actividades: pd.DataFrame,
    df_avances: pd.DataFrame,
    supervisor: str
):
    """
    Devuelve únicamente las OTs, actividades y avances
    correspondientes al supervisor seleccionado.
    """
    if (
        df_actividades is None
        or df_actividades.empty
        or "supervisor" not in df_actividades.columns
    ):
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame()
        )

    nombre = str(
        supervisor
        or ""
    ).strip()

    actividades_filtradas = (
        df_actividades[
            df_actividades[
                "supervisor"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq(nombre)
        ]
        .copy()
    )

    if actividades_filtradas.empty:
        return (
            pd.DataFrame(),
            actividades_filtradas,
            pd.DataFrame()
        )

    ids_ot = (
        actividades_filtradas[
            "ot_id"
        ]
        .dropna()
        .unique()
        .tolist()
        if "ot_id"
        in actividades_filtradas.columns
        else []
    )

    ots_filtradas = (
        df_ots[
            df_ots["id"].isin(
                ids_ot
            )
        ].copy()
        if (
            df_ots is not None
            and not df_ots.empty
            and "id" in df_ots.columns
        )
        else pd.DataFrame()
    )

    ids_actividades = (
        actividades_filtradas[
            "id"
        ]
        .dropna()
        .tolist()
        if "id"
        in actividades_filtradas.columns
        else []
    )

    avances_filtrados = (
        df_avances[
            df_avances[
                "actividad_id"
            ].isin(
                ids_actividades
            )
        ].copy()
        if (
            df_avances is not None
            and not df_avances.empty
            and "actividad_id"
            in df_avances.columns
            and ids_actividades
        )
        else pd.DataFrame(
            columns=(
                df_avances.columns
                if df_avances is not None
                else []
            )
        )
    )

    return (
        ots_filtradas,
        actividades_filtradas,
        avances_filtrados
    )


def contar_total_fotos(
    df_avances: pd.DataFrame
):
    conteo = contar_fotos_por_etapa(
        df_avances
    )

    return (
        int(
            conteo.get(
                "INICIO",
                0
            )
        )
        + int(
            conteo.get(
                "DURANTE",
                0
            )
        )
        + int(
            conteo.get(
                "FINAL",
                0
            )
        )
    )


def construir_pdf_fotografico_multiple(
    df_ots: pd.DataFrame,
    df_actividades: pd.DataFrame,
    df_avances: pd.DataFrame,
    nombre_area: str,
    titulo_reporte: str,
    supervisor: str = ""
) -> bytes:
    """
    Genera un único PDF fotográfico con múltiples OTs.

    Estructura:
    1. Resumen general.
    2. Cuadro consolidado de OTs.
    3. Una sección independiente por cada OT.
    4. Cuadro de actividades.
    5. Fotografías Antes / Durante / Después.
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=22,
        leftMargin=22,
        topMargin=22,
        bottomMargin=22
    )

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "MultiFotoTitulo",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#082D55"
        ),
        spaceAfter=3
    )

    estilo_sub = ParagraphStyle(
        "MultiFotoSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#667085"
        ),
        spaceAfter=9
    )

    estilo_h2 = ParagraphStyle(
        "MultiFotoH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor(
            "#082D55"
        ),
        spaceBefore=6,
        spaceAfter=5
    )

    estilo_ot_titulo = ParagraphStyle(
        "MultiFotoOTTitulo",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=colors.HexColor(
            "#082D55"
        ),
        spaceAfter=4
    )

    estilo_body = ParagraphStyle(
        "MultiFotoBody",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor(
            "#344054"
        )
    )

    estilo_tabla = ParagraphStyle(
        "MultiFotoTabla",
        parent=estilo_body,
        fontSize=6.1,
        leading=7.3
    )

    estilo_caption = ParagraphStyle(
        "MultiFotoCaption",
        parent=estilo_body,
        fontSize=6.4,
        leading=7.8,
        alignment=TA_CENTER
    )

    estilo_vacio = ParagraphStyle(
        "MultiFotoVacio",
        parent=estilo_body,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor(
            "#98A2B3"
        )
    )

    story = []

    if (
        df_ots is None
        or df_ots.empty
    ):
        story.append(
            Paragraph(
                "No existen OTs disponibles para generar el informe.",
                estilo_body
            )
        )
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # --------------------------------------------------------
    # PORTADA / RESUMEN
    # --------------------------------------------------------
    story.append(
        Paragraph(
            "MAININ · PDP CONTROL CENTER QUELLAVECO",
            estilo_titulo
        )
    )

    story.append(
        Paragraph(
            titulo_reporte,
            estilo_sub
        )
    )

    datos_cabecera = [
        [
            "ÁREA",
            str(
                nombre_area
                or ""
            ),
            "FECHA DE EMISIÓN",
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        ]
    ]

    if supervisor:
        datos_cabecera.append([
            "SUPERVISOR",
            str(
                supervisor
            ),
            "TIPO",
            "Informe fotográfico por supervisor"
        ])
    else:
        datos_cabecera.append([
            "ALCANCE",
            "Todas las OTs de la vista seleccionada",
            "TIPO",
            "Informe fotográfico general"
        ])

    tabla_cabecera = Table(
        datos_cabecera,
        colWidths=[
            85,
            270,
            105,
            260
        ]
    )

    tabla_cabecera.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor(
                    "#EEF4FB"
                )
            ),
            (
                "BACKGROUND",
                (2, 0),
                (2, -1),
                colors.HexColor(
                    "#EEF4FB"
                )
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (2, 0),
                (2, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor(
                    "#D0D5DD"
                )
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(
        tabla_cabecera
    )
    story.append(
        Spacer(1, 9)
    )

    kpis_general = compute_kpis(
        df_actividades,
        df_avances
    )

    total_fotos_general = (
        contar_total_fotos(
            df_avances
        )
    )

    conteo_fotos_general = (
        contar_fotos_por_etapa(
            df_avances
        )
    )

    resumen_kpis = [
        [
            "OTs",
            "Actividades",
            "Avance real",
            "Culminadas",
            "Fotos antes",
            "Fotos durante",
            "Fotos después",
            "Total fotos"
        ],
        [
            str(
                len(
                    df_ots
                )
            ),
            str(
                int(
                    kpis_general.get(
                        "actividades",
                        0
                    )
                    or 0
                )
            ),
            f"{float(kpis_general.get('avance_general', 0) or 0):.1f}%",
            str(
                int(
                    kpis_general.get(
                        "culminadas",
                        0
                    )
                    or 0
                )
            ),
            str(
                conteo_fotos_general[
                    "INICIO"
                ]
            ),
            str(
                conteo_fotos_general[
                    "DURANTE"
                ]
            ),
            str(
                conteo_fotos_general[
                    "FINAL"
                ]
            ),
            str(
                total_fotos_general
            )
        ]
    ]

    tabla_resumen = Table(
        resumen_kpis,
        colWidths=[
            90,
            90,
            90,
            90,
            90,
            90,
            90,
            90
        ]
    )

    tabla_resumen.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#082D55"
                )
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.5
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor(
                    "#D0D5DD"
                )
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(
        tabla_resumen
    )

    story.append(
        Paragraph(
            "Resumen por OT",
            estilo_h2
        )
    )

    # --------------------------------------------------------
    # CUADRO RESUMEN DE TODAS LAS OTs
    # --------------------------------------------------------
    resumen_ots = [
        [
            "OT",
            "EQUIPO",
            "ACT.",
            "REAL",
            "ANTES",
            "DURANTE",
            "DESPUÉS"
        ]
    ]

    df_ots_ordenadas = (
        df_ots.copy()
    )

    if "ot" in df_ots_ordenadas.columns:
        df_ots_ordenadas = (
            df_ots_ordenadas
            .sort_values(
                "ot"
            )
        )

    for _, fila_ot in (
        df_ots_ordenadas.iterrows()
    ):

        ot_id = fila_ot.get(
            "id"
        )

        actividades_ot = (
            df_actividades[
                df_actividades[
                    "ot_id"
                ]
                == ot_id
            ].copy()
            if (
                df_actividades is not None
                and not df_actividades.empty
                and "ot_id"
                in df_actividades.columns
            )
            else pd.DataFrame()
        )

        ids_actividades_ot = (
            actividades_ot[
                "id"
            ]
            .dropna()
            .tolist()
            if (
                not actividades_ot.empty
                and "id"
                in actividades_ot.columns
            )
            else []
        )

        avances_ot = (
            df_avances[
                df_avances[
                    "actividad_id"
                ].isin(
                    ids_actividades_ot
                )
            ].copy()
            if (
                df_avances is not None
                and not df_avances.empty
                and "actividad_id"
                in df_avances.columns
                and ids_actividades_ot
            )
            else pd.DataFrame(
                columns=(
                    df_avances.columns
                    if df_avances is not None
                    else []
                )
            )
        )

        kpis_ot = compute_kpis(
            actividades_ot,
            avances_ot
        )

        fotos_ot = (
            contar_fotos_por_etapa(
                avances_ot
            )
        )

        resumen_ots.append([
            str(
                fila_ot.get(
                    "ot",
                    ""
                )
                or ""
            ),
            str(
                fila_ot.get(
                    "equipo",
                    ""
                )
                or "Sin equipo"
            ),
            str(
                int(
                    kpis_ot.get(
                        "actividades",
                        0
                    )
                    or 0
                )
            ),
            f"{float(kpis_ot.get('avance_general', 0) or 0):.1f}%",
            str(
                fotos_ot["INICIO"]
            ),
            str(
                fotos_ot["DURANTE"]
            ),
            str(
                fotos_ot["FINAL"]
            )
        ])

    tabla_ots = Table(
        resumen_ots,
        colWidths=[
            95,
            135,
            55,
            60,
            60,
            60,
            60
        ],
        repeatRows=1
    )

    tabla_ots.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#082D55"
                )
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6.3
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                colors.HexColor(
                    "#D0D5DD"
                )
            ),
            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "CENTER"
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor(
                        "#F8FAFC"
                    )
                ]
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3
            )
        ])
    )

    story.append(
        tabla_ots
    )

    # --------------------------------------------------------
    # DETALLE DE CADA OT
    # --------------------------------------------------------
    total_ots = len(
        df_ots_ordenadas
    )

    for indice_ot, (
        _,
        fila_ot
    ) in enumerate(
        df_ots_ordenadas.iterrows(),
        start=1
    ):

        ot_id = fila_ot.get(
            "id"
        )

        actividades_ot = (
            df_actividades[
                df_actividades[
                    "ot_id"
                ]
                == ot_id
            ].copy()
            if (
                df_actividades is not None
                and not df_actividades.empty
                and "ot_id"
                in df_actividades.columns
            )
            else pd.DataFrame()
        )

        if actividades_ot.empty:
            continue

        ids_actividades_ot = (
            actividades_ot[
                "id"
            ]
            .dropna()
            .tolist()
        )

        avances_ot = (
            df_avances[
                df_avances[
                    "actividad_id"
                ].isin(
                    ids_actividades_ot
                )
            ].copy()
            if (
                df_avances is not None
                and not df_avances.empty
                and "actividad_id"
                in df_avances.columns
            )
            else pd.DataFrame(
                columns=(
                    df_avances.columns
                    if df_avances is not None
                    else []
                )
            )
        )

        story.append(
            PageBreak()
        )

        ot_numero = str(
            fila_ot.get(
                "ot",
                ""
            )
            or ""
        )

        equipo = str(
            fila_ot.get(
                "equipo",
                ""
            )
            or "Sin equipo"
        )

        descripcion_ot = str(
            fila_ot.get(
                "descripcion",
                ""
            )
            or ""
        )

        story.append(
            Paragraph(
                (
                    f"OT {ot_numero} · "
                    f"{equipo}"
                ),
                estilo_ot_titulo
            )
        )

        story.append(
            Paragraph(
                (
                    f"OT {indice_ot} de {total_ots}"
                    + (
                        f" · Supervisor: {supervisor}"
                        if supervisor
                        else ""
                    )
                ),
                estilo_sub
            )
        )

        if descripcion_ot:
            story.append(
                Paragraph(
                    (
                        "<b>Descripción de la OT:</b> "
                        + descripcion_ot
                    ),
                    estilo_body
                )
            )

            story.append(
                Spacer(
                    1,
                    6
                )
            )

        kpis_ot = compute_kpis(
            actividades_ot,
            avances_ot
        )

        fotos_ot = (
            contar_fotos_por_etapa(
                avances_ot
            )
        )

        resumen_ot = Table(
            [
                [
                    "Actividades",
                    "Plan",
                    "Real",
                    "Culminadas",
                    "Antes",
                    "Durante",
                    "Después"
                ],
                [
                    str(
                        int(
                            kpis_ot.get(
                                "actividades",
                                0
                            )
                            or 0
                        )
                    ),
                    f"{float(kpis_ot.get('avance_plan', 0) or 0):.1f}%",
                    f"{float(kpis_ot.get('avance_general', 0) or 0):.1f}%",
                    str(
                        int(
                            kpis_ot.get(
                                "culminadas",
                                0
                            )
                            or 0
                        )
                    ),
                    str(
                        fotos_ot["INICIO"]
                    ),
                    str(
                        fotos_ot["DURANTE"]
                    ),
                    str(
                        fotos_ot["FINAL"]
                    )
                ]
            ],
            colWidths=[
                102,
                102,
                102,
                102,
                102,
                102,
                102
            ]
        )

        resumen_ot.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#082D55"
                    )
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7.3
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.HexColor(
                        "#D0D5DD"
                    )
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        story.append(
            resumen_ot
        )

        story.append(
            Paragraph(
                "Cuadro de actividades",
                estilo_h2
            )
        )

        estado_ot = calcular_semaforo_pdf(
            actividades_ot,
            avances_ot
        )

        if estado_ot.empty:

            story.append(
                Paragraph(
                    "No existen actividades registradas para esta OT.",
                    estilo_vacio
                )
            )

        else:

            detalle = [
                [
                    "GRUPO",
                    "SUPERVISOR",
                    "DESCRIPCIÓN",
                    "PLAN",
                    "REAL",
                    "ESTADO"
                ]
            ]

            for _, fila_act in (
                estado_ot.iterrows()
            ):

                descripcion_actividad = (
                    fila_act.get(
                        "descripcion_trabajo"
                    )
                    or fila_act.get(
                        "descripcion"
                    )
                    or ""
                )

                detalle.append([
                    Paragraph(
                        str(
                            fila_act.get(
                                "grupo",
                                ""
                            )
                            or "Sin grupo"
                        ),
                        estilo_tabla
                    ),
                    Paragraph(
                        str(
                            fila_act.get(
                                "supervisor",
                                ""
                            )
                            or ""
                        ),
                        estilo_tabla
                    ),
                    Paragraph(
                        str(
                            descripcion_actividad
                        )[:350],
                        estilo_tabla
                    ),
                    f"{float(fila_act.get('PLAN ACTUAL (%)', 0) or 0):.1f}%",
                    f"{float(fila_act.get('avance_real', 0) or 0):.1f}%",
                    Paragraph(
                        str(
                            fila_act.get(
                                "ALERTA",
                                ""
                            )
                            or ""
                        ),
                        estilo_tabla
                    )
                ])

            tabla_detalle = Table(
                detalle,
                colWidths=[
                    80,
                    105,
                    335,
                    55,
                    55,
                    85
                ],
                repeatRows=1
            )

            tabla_detalle.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#082D55"
                        )
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        6.2
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor(
                            "#D0D5DD"
                        )
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "ALIGN",
                        (3, 1),
                        (4, -1),
                        "CENTER"
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor(
                                "#F8FAFC"
                            )
                        ]
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    )
                ])
            )

            story.append(
                tabla_detalle
            )

        # ----------------------------------------------------
        # FOTOGRAFÍAS DE LA OT
        # ----------------------------------------------------
        etapas = [
            (
                "INICIO",
                "ANTES · INICIO"
            ),
            (
                "DURANTE",
                "DURANTE · EJECUCIÓN"
            ),
            (
                "FINAL",
                "DESPUÉS · FINAL"
            )
        ]

        for etapa, titulo_etapa in etapas:

            story.append(
                Paragraph(
                    titulo_etapa,
                    estilo_h2
                )
            )

            elementos = (
                construir_fotos_etapa_pdf(
                    avances_ot,
                    actividades_ot,
                    etapa,
                    estilo_caption,
                    estilo_vacio
                )
            )

            story.extend(
                elementos
            )

    story.append(
        Spacer(
            1,
            10
        )
    )

    story.append(
        Paragraph(
            "MAININ · Informe generado desde PDP Control Center Quellaveco",
            estilo_sub
        )
    )

    doc.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


def mostrar_reportes_fotograficos_adicionales(
    df_ots: pd.DataFrame,
    df_actividades: pd.DataFrame,
    df_avances: pd.DataFrame,
    nombre_area: str,
    key_prefix: str
):
    """
    Panel para:
    - PDF fotográfico GENERAL con todas las OTs.
    - PDF fotográfico POR SUPERVISOR.
    """

    st.subheader(
        "Informe fotográfico general"
    )

    st.caption(
        "Genera un único PDF donde cada OT aparece con la "
        "misma ficha completa: datos generales, descripción de "
        "actividades y evidencias Antes, Durante y Después."
    )

    if (
        df_ots is None
        or df_ots.empty
        or df_actividades is None
        or df_actividades.empty
    ):
        st.info(
            "No existen datos suficientes para generar el informe general."
        )
        return

    total_fotos = contar_total_fotos(
        df_avances
    )

    g1, g2, g3 = st.columns(3)

    with g1:
        st.metric(
            "OTs incluidas",
            len(
                df_ots
            )
        )

    with g2:
        st.metric(
            "Actividades",
            len(
                df_actividades
            )
        )

    with g3:
        st.metric(
            "Fotografías",
            total_fotos
        )

    st.info(
        "El informe general procesa las fotografías en modo "
        "optimizado para evitar sobrecargar la memoria de Streamlit. "
        "Si contiene muchas evidencias puede tomar algunos segundos."
    )

    key_general_pdf = (
        f"{key_prefix}_"
        "pdf_fotografico_general"
    )

    generar_general = st.button(
        "Preparar informe general de todas las OTs",
        type="primary",
        use_container_width=True,
        key=(
            f"{key_prefix}_"
            "generar_pdf_fotografico_general"
        )
    )

    if generar_general:

        with st.spinner(
            "Preparando informe general de todas las OTs..."
        ):

            try:

                pdf_general = (
                    construir_pdf_formato_antapaccay(
                        df_ots,
                        df_actividades,
                        df_avances,
                        nombre_area,
                        (
                            "INFORME FOTOGRÁFICO GENERAL · "
                            "TODAS LAS OTs"
                        ),
                        incluir_portada=True
                    )
                )

                st.session_state[
                    key_general_pdf
                ] = pdf_general

                st.success(
                    "Informe fotográfico general preparado correctamente."
                )

            except Exception as exc:

                st.error(
                    "No fue posible generar el informe "
                    f"fotográfico general: {exc}"
                )

    pdf_general_guardado = (
        st.session_state.get(
            key_general_pdf
        )
    )

    if pdf_general_guardado:

        nombre_area_archivo = (
            str(
                nombre_area
            )
            .strip()
            .lower()
            .replace(
                " ",
                "_"
            )
        )

        st.download_button(
            "Descargar informe general de todas las OTs",
            data=pdf_general_guardado,
            file_name=(
                "Informe_Fotografico_General_"
                f"{nombre_area_archivo}_"
                f"{datetime.now():%Y%m%d_%H%M}.pdf"
            ),
            mime="application/pdf",
            use_container_width=True,
            key=(
                f"{key_prefix}_"
                "descargar_pdf_fotografico_general"
            )
        )

    st.divider()

    # =====================================================
    # INFORME FOTOGRÁFICO POR SUPERVISOR
    # =====================================================
    st.subheader(
        "Informe fotográfico por supervisor"
    )

    st.caption(
        "Seleccione un supervisor para generar un único PDF. "
        "Cada OT bajo su responsabilidad tendrá su ficha completa, "
        "descripción de actividades y evidencias Antes, Durante y Después."
    )

    supervisores = (
        lista_supervisores_reporte(
            df_actividades
        )
    )

    if not supervisores:

        st.info(
            "No existen supervisores asignados en esta vista."
        )
        return

    supervisor_fotografico = st.selectbox(
        "Seleccionar supervisor para informe fotográfico",
        supervisores,
        key=(
            f"{key_prefix}_"
            "selector_supervisor_fotografico"
        )
    )

    (
        ots_supervisor,
        actividades_supervisor,
        avances_supervisor
    ) = filtrar_datos_fotograficos_supervisor(
        df_ots,
        df_actividades,
        df_avances,
        supervisor_fotografico
    )

    fotos_supervisor = (
        contar_total_fotos(
            avances_supervisor
        )
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "OTs",
            len(
                ots_supervisor
            )
        )

    with s2:
        st.metric(
            "Actividades",
            len(
                actividades_supervisor
            )
        )

    with s3:
        st.metric(
            "Fotografías",
            fotos_supervisor
        )

    key_supervisor_pdf = (
        f"{key_prefix}_"
        "pdf_fotografico_supervisor"
    )

    generar_supervisor = st.button(
        "Preparar informe fotográfico del supervisor",
        type="primary",
        use_container_width=True,
        key=(
            f"{key_prefix}_"
            "generar_pdf_fotografico_supervisor"
        )
    )

    if generar_supervisor:

        with st.spinner(
            "Preparando informe fotográfico del supervisor..."
        ):

            try:

                pdf_supervisor = (
                    construir_pdf_formato_antapaccay(
                        ots_supervisor,
                        actividades_supervisor,
                        avances_supervisor,
                        nombre_area,
                        (
                            "INFORME FOTOGRÁFICO POR SUPERVISOR · "
                            f"{supervisor_fotografico}"
                        ),
                        supervisor=(
                            supervisor_fotografico
                        ),
                        incluir_portada=True
                    )
                )

                st.session_state[
                    key_supervisor_pdf
                ] = {
                    "supervisor": (
                        supervisor_fotografico
                    ),
                    "data": pdf_supervisor
                }

                st.success(
                    "Informe fotográfico del supervisor preparado correctamente."
                )

            except Exception as exc:

                st.error(
                    "No fue posible generar el informe "
                    f"fotográfico del supervisor: {exc}"
                )

    pdf_supervisor_guardado = (
        st.session_state.get(
            key_supervisor_pdf
        )
    )

    if (
        isinstance(
            pdf_supervisor_guardado,
            dict
        )
        and pdf_supervisor_guardado.get(
            "supervisor"
        )
        == supervisor_fotografico
        and pdf_supervisor_guardado.get(
            "data"
        )
    ):

        supervisor_archivo = (
            str(
                supervisor_fotografico
            )
            .strip()
            .lower()
            .replace(
                " ",
                "_"
            )
        )

        st.download_button(
            "Descargar informe fotográfico del supervisor",
            data=pdf_supervisor_guardado[
                "data"
            ],
            file_name=(
                "Informe_Fotografico_"
                f"{supervisor_archivo}_"
                f"{datetime.now():%Y%m%d_%H%M}.pdf"
            ),
            mime="application/pdf",
            use_container_width=True,
            key=(
                f"{key_prefix}_"
                "descargar_pdf_fotografico_supervisor"
            )
        )



# =====================================================
# INFORME POR OT - FORMATO TIPO ANTAPACCAY
# =====================================================

def _texto_pdf(valor):
    texto = str(
        valor
        if valor is not None
        else ""
    ).strip()

    return html.escape(
        texto
    ).replace(
        "\n",
        "<br/>"
    )


def _unicos_columna(
    df: pd.DataFrame,
    columna: str,
    separador=" / "
):
    if (
        df is None
        or df.empty
        or columna not in df.columns
    ):
        return ""

    valores = []

    for valor in df[columna].tolist():

        texto = str(
            valor
            if valor is not None
            else ""
        ).strip()

        if (
            texto
            and texto.lower() != "nan"
            and texto not in valores
        ):
            valores.append(
                texto
            )

    return separador.join(
        valores
    )


def _area_operativa_ot(
    actividades_ot: pd.DataFrame,
    nombre_area: str
):
    """
    Prioriza la primera parte de SECCION.
    Ejemplo:
    CMOP | PUESTO X -> CMOP
    """

    secciones = _unicos_columna(
        actividades_ot,
        "seccion"
    )

    if secciones:

        areas = []

        for bloque in secciones.split(
            " / "
        ):

            area = bloque.split(
                "|",
                1
            )[0].strip()

            if (
                area
                and area not in areas
            ):
                areas.append(
                    area
                )

        if areas:
            return " / ".join(
                areas
            )

    return str(
        nombre_area
        or ""
    )


def _turno_ot(
    actividades_ot: pd.DataFrame
):
    """
    Turno derivado únicamente del horario planificado.
    DIA: 06:00 - 17:59
    NOCHE: 18:00 - 05:59
    """

    if (
        actividades_ot is None
        or actividades_ot.empty
        or "inicio_plan"
        not in actividades_ot.columns
    ):
        return ""

    fechas = pd.to_datetime(
        actividades_ot[
            "inicio_plan"
        ],
        errors="coerce"
    ).dropna()

    if fechas.empty:
        return ""

    turnos = []

    for hora in (
        fechas.dt.hour.tolist()
    ):

        turno = (
            "DIA"
            if 6 <= int(hora) < 18
            else "NOCHE"
        )

        if turno not in turnos:
            turnos.append(
                turno
            )

    return " / ".join(
        turnos
    )


def _numero_resumen(
    df: pd.DataFrame,
    columna: str,
    modo="max"
):
    if (
        df is None
        or df.empty
        or columna not in df.columns
    ):
        return 0.0

    valores = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).dropna()

    if valores.empty:
        return 0.0

    if modo == "sum":
        return float(
            valores.sum()
        )

    return float(
        valores.max()
    )


def _descripcion_principal_ot(
    fila_ot: dict,
    actividades_ot: pd.DataFrame
):
    descripcion_ot = str(
        fila_ot.get(
            "descripcion",
            ""
        )
        or ""
    ).strip()

    if descripcion_ot:
        return descripcion_ot

    descripcion_trabajo = (
        _unicos_columna(
            actividades_ot,
            "descripcion_trabajo"
        )
    )

    if descripcion_trabajo:
        return descripcion_trabajo

    return _unicos_columna(
        actividades_ot,
        "descripcion"
    )


def _detalles_ejecutados_ot(
    actividades_ot: pd.DataFrame,
    avances_ot: pd.DataFrame
):
    """
    Para el DETALLE se prioriza lo realmente reportado
    por campo. Si no existen descripciones de avance,
    utiliza Operación / Descripción de la planificación.
    """

    detalles = []

    if (
        avances_ot is not None
        and not avances_ot.empty
    ):

        avances_ordenados = (
            avances_ot.copy()
        )

        if "fecha_registro" in (
            avances_ordenados.columns
        ):

            avances_ordenados[
                "_fecha_detalle"
            ] = pd.to_datetime(
                avances_ordenados[
                    "fecha_registro"
                ],
                errors="coerce",
                utc=True
            )

            avances_ordenados = (
                avances_ordenados
                .sort_values(
                    "_fecha_detalle"
                )
            )

        for _, registro in (
            avances_ordenados.iterrows()
        ):

            detalle = str(
                registro.get(
                    "descripcion_avance",
                    ""
                )
                or ""
            ).strip()

            if (
                detalle
                and detalle not in detalles
            ):
                detalles.append(
                    detalle
                )

    if not detalles:

        for columna in [
            "operacion",
            "descripcion",
            "descripcion_trabajo"
        ]:

            if (
                actividades_ot is not None
                and not actividades_ot.empty
                and columna
                in actividades_ot.columns
            ):

                for valor in (
                    actividades_ot[
                        columna
                    ].tolist()
                ):

                    detalle = str(
                        valor
                        if valor is not None
                        else ""
                    ).strip()

                    if (
                        detalle
                        and detalle.lower() != "nan"
                        and detalle not in detalles
                    ):
                        detalles.append(
                            detalle
                        )

    return detalles


def _evidencias_por_etapa(
    avances_ot: pd.DataFrame
):
    resultado = {
        "INICIO": [],
        "DURANTE": [],
        "FINAL": []
    }

    if (
        avances_ot is None
        or avances_ot.empty
    ):
        return resultado

    registros = (
        avances_ot.copy()
    )

    if "fecha_registro" in (
        registros.columns
    ):

        registros[
            "_orden_foto"
        ] = pd.to_datetime(
            registros[
                "fecha_registro"
            ],
            errors="coerce",
            utc=True
        )

        registros = (
            registros
            .sort_values(
                "_orden_foto"
            )
        )

    for _, registro in (
        registros.iterrows()
    ):

        etapa = str(
            registro.get(
                "tipo_evidencia",
                ""
            )
            or ""
        ).strip().upper()

        if etapa not in resultado:
            continue

        evidencias = (
            registro.get(
                "evidencias"
            )
            or []
        )

        if not isinstance(
            evidencias,
            (list, tuple)
        ):
            continue

        for evidencia in evidencias:

            resultado[
                etapa
            ].append(
                evidencia
            )

    return resultado



def _preparar_imagen_pdf_temporal(
    evidencia,
    directorio_temporal,
    indice_foto,
    ancho_max=158,
    alto_max=145
):
    """
    Versión estable para compilados grandes.

    La foto se descarga, corrige orientación, reduce resolución
    y se guarda temporalmente en disco. ReportLab recibe la ruta
    del archivo y no mantiene todos los BytesIO simultáneamente
    en memoria.
    """
    contenido = descargar_evidencia_pdf(
        evidencia
    )

    if not contenido:
        return None

    try:

        with Image.open(
            io.BytesIO(contenido)
        ) as imagen_original:

            imagen = ImageOps.exif_transpose(
                imagen_original
            )

            if imagen.mode != "RGB":
                imagen = imagen.convert(
                    "RGB"
                )
            else:
                imagen = imagen.copy()

        # La evidencia se mostrará pequeña dentro de A4.
        # No tiene sentido conservar resolución fotográfica completa.
        imagen.thumbnail(
            (900, 900),
            Image.Resampling.LANCZOS
        )

        ancho_original, alto_original = (
            imagen.size
        )

        if (
            ancho_original <= 0
            or alto_original <= 0
        ):
            return None

        escala = min(
            ancho_max / ancho_original,
            alto_max / alto_original,
            1.0
        )

        ancho_pdf = max(
            1,
            ancho_original * escala
        )

        alto_pdf = max(
            1,
            alto_original * escala
        )

        ruta_imagen = Path(
            directorio_temporal
        ) / (
            f"evidencia_{indice_foto}.jpg"
        )

        imagen.save(
            ruta_imagen,
            format="JPEG",
            quality=68,
            optimize=True
        )

        imagen.close()

        return RLImage(
            str(ruta_imagen),
            width=ancho_pdf,
            height=alto_pdf
        )

    except Exception:
        return None


def _tabla_evidencias_antapaccay(
    avances_ot: pd.DataFrame,
    estilo_vacio,
    directorio_temporal=None,
    prefijo_foto="ot"
):
    """
    Construye una matriz:
       Antes | Durante | Después
    Si hay varias fotos, crea tantas filas como sea necesario.
    """

    etapas = (
        _evidencias_por_etapa(
            avances_ot
        )
    )

    listas = [
        etapas["INICIO"],
        etapas["DURANTE"],
        etapas["FINAL"]
    ]

    max_fotos = max(
        [
            len(lista)
            for lista in listas
        ]
        + [1]
    )

    filas = []

    for indice in range(
        max_fotos
    ):

        fila_imagenes = []

        for lista in listas:

            if indice < len(lista):

                identificador_foto = (
                    f"{prefijo_foto}_"
                    f"{indice}_"
                    f"{len(filas)}_"
                    f"{len(fila_imagenes)}"
                )

                if directorio_temporal:

                    imagen = (
                        _preparar_imagen_pdf_temporal(
                            lista[indice],
                            directorio_temporal,
                            identificador_foto,
                            ancho_max=158,
                            alto_max=145
                        )
                    )

                else:

                    imagen = (
                        preparar_imagen_pdf(
                            lista[indice],
                            ancho_max=158,
                            alto_max=145
                        )
                    )

                if imagen is not None:

                    celda = Table(
                        [[imagen]],
                        colWidths=[166],
                        rowHeights=[153]
                    )

                    celda.setStyle(
                        TableStyle([
                            (
                                "ALIGN",
                                (0, 0),
                                (-1, -1),
                                "CENTER"
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "MIDDLE"
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            )
                        ])
                    )

                    fila_imagenes.append(
                        celda
                    )

                else:

                    fila_imagenes.append(
                        Paragraph(
                            "Evidencia no disponible",
                            estilo_vacio
                        )
                    )

            else:

                fila_imagenes.append(
                    Paragraph(
                        "Sin evidencia",
                        estilo_vacio
                    )
                )

        filas.append(
            fila_imagenes
        )

        filas.append([
            Paragraph(
                "<b>Antes</b>",
                estilo_vacio
            ),
            Paragraph(
                "<b>Durante</b>",
                estilo_vacio
            ),
            Paragraph(
                "<b>Después</b>",
                estilo_vacio
            )
        ])

    tabla = Table(
        filas,
        colWidths=[
            174,
            174,
            174
        ]
    )

    estilos = [
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.55,
            colors.black
        ),
        (
            "ALIGN",
            (0, 0),
            (-1, -1),
            "CENTER"
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            3
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            3
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            3
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            3
        )
    ]

    # Cada segunda fila es la franja gris Antes/Durante/Después.
    for fila in range(
        1,
        len(filas),
        2
    ):

        estilos.append(
            (
                "BACKGROUND",
                (0, fila),
                (-1, fila),
                colors.HexColor(
                    "#D9D9D9"
                )
            )
        )

    tabla.setStyle(
        TableStyle(
            estilos
        )
    )

    return tabla


def _agregar_ot_formato_antapaccay(
    story,
    fila_ot: dict,
    actividades_ot: pd.DataFrame,
    avances_ot: pd.DataFrame,
    nombre_area: str,
    numero_ot: int,
    total_ots: int,
    supervisor_filtro: str = "",
    directorio_temporal=None
):
    """
    Agrega una OT completa al story:
    - ficha
    - descripción de actividades
    - evidencias fotográficas Antes/Durante/Después
    """

    styles = getSampleStyleSheet()

    azul_tabla = colors.HexColor(
        "#294B6D"
    )

    gris_caption = colors.HexColor(
        "#D9D9D9"
    )

    estilo_titulo_ot = ParagraphStyle(
        f"T_OT_{numero_ot}",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.black,
        spaceAfter=10
    )

    estilo_label = ParagraphStyle(
        f"L_OT_{numero_ot}",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.6,
        leading=9.2,
        textColor=colors.white
    )

    estilo_valor = ParagraphStyle(
        f"V_OT_{numero_ot}",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.7,
        leading=9.5,
        textColor=colors.black
    )

    estilo_h3 = ParagraphStyle(
        f"H3_OT_{numero_ot}",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=12.5,
        textColor=colors.black,
        spaceBefore=7,
        spaceAfter=8
    )

    estilo_detalle = ParagraphStyle(
        f"D_OT_{numero_ot}",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10,
        leftIndent=15,
        firstLineIndent=-7,
        textColor=colors.black,
        spaceAfter=2
    )

    estilo_vacio = ParagraphStyle(
        f"E_OT_{numero_ot}",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.black
    )

    ot_numero = str(
        fila_ot.get(
            "ot",
            ""
        )
        or ""
    )

    equipo = str(
        fila_ot.get(
            "equipo",
            ""
        )
        or "Sin equipo"
    )

    descripcion_principal = (
        _descripcion_principal_ot(
            fila_ot,
            actividades_ot
        )
    )

    area_operativa = (
        _area_operativa_ot(
            actividades_ot,
            nombre_area
        )
    )

    supervisores = (
        supervisor_filtro
        or _unicos_columna(
            actividades_ot,
            "supervisor"
        )
        or "Sin asignar"
    )

    ssoma = (
        _unicos_columna(
            actividades_ot,
            "ssoma"
        )
        or "Sin asignar"
    )

    especialidad = (
        _unicos_columna(
            actividades_ot,
            "especialidad"
        )
        or "-"
    )

    grupos = (
        _unicos_columna(
            actividades_ot,
            "grupo"
        )
        or "-"
    )

    turno = (
        _turno_ot(
            actividades_ot
        )
        or "-"
    )

    personal = int(
        round(
            _numero_resumen(
                actividades_ot,
                "personal",
                "max"
            )
        )
    )

    horas = (
        _numero_resumen(
            actividades_ot,
            "duracion_h",
            "max"
        )
    )

    hh = (
        _numero_resumen(
            actividades_ot,
            "hh_plan",
            "sum"
        )
    )

    story.append(
        Paragraph(
            (
                f"2.1.{numero_ot}. "
                f"{_texto_pdf(equipo)} "
                f"(OT: {_texto_pdf(ot_numero)})"
            ),
            estilo_titulo_ot
        )
    )

    # --------------------------------------------------------
    # FICHA TIPO ANTAPACCAY
    # --------------------------------------------------------
    tabla_datos = [
        [
            Paragraph(
                "AREA",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    area_operativa
                ),
                estilo_valor
            ),
            "",
            ""
        ],
        [
            Paragraph(
                "OT",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    ot_numero
                ),
                estilo_valor
            ),
            "",
            ""
        ],
        [
            Paragraph(
                "DESCRIPCION DE ACTIVIDAD",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    descripcion_principal
                ),
                estilo_valor
            ),
            "",
            ""
        ],
        [
            Paragraph(
                "EQUIPO",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    equipo
                ),
                estilo_valor
            ),
            "",
            ""
        ],
        [
            Paragraph(
                "SUPERVISOR OPERATIVO MAININ",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    supervisores
                ),
                estilo_valor
            ),
            Paragraph(
                "TURNO",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    turno
                ),
                estilo_valor
            )
        ],
        [
            Paragraph(
                "SUPERVISOR SEGURIDAD MAININ",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    ssoma
                ),
                estilo_valor
            ),
            Paragraph(
                "PERSONAL",
                estilo_label
            ),
            Paragraph(
                str(
                    personal
                ),
                estilo_valor
            )
        ],
        [
            Paragraph(
                "ESPECIALIDAD",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    especialidad
                ),
                estilo_valor
            ),
            Paragraph(
                "HORAS",
                estilo_label
            ),
            Paragraph(
                (
                    f"{horas:.1f}"
                    if horas
                    else "-"
                ),
                estilo_valor
            )
        ],
        [
            Paragraph(
                "GRUPO",
                estilo_label
            ),
            Paragraph(
                _texto_pdf(
                    grupos
                ),
                estilo_valor
            ),
            Paragraph(
                "HH",
                estilo_label
            ),
            Paragraph(
                (
                    f"{hh:.0f}"
                    if hh
                    else "-"
                ),
                estilo_valor
            )
        ]
    ]

    ficha = Table(
        tabla_datos,
        colWidths=[
            194,
            202,
            70,
            58
        ]
    )

    estilo_ficha = [
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.black
        ),
        (
            "BACKGROUND",
            (0, 0),
            (0, -1),
            azul_tabla
        ),
        (
            "BACKGROUND",
            (2, 4),
            (2, -1),
            azul_tabla
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            3
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            3
        ),
        (
            "SPAN",
            (1, 0),
            (3, 0)
        ),
        (
            "SPAN",
            (1, 1),
            (3, 1)
        ),
        (
            "SPAN",
            (1, 2),
            (3, 2)
        ),
        (
            "SPAN",
            (1, 3),
            (3, 3)
        )
    ]

    ficha.setStyle(
        TableStyle(
            estilo_ficha
        )
    )

    story.append(
        ficha
    )

    story.append(
        Spacer(
            1,
            14
        )
    )

    # --------------------------------------------------------
    # DESCRIPCIÓN DE LAS ACTIVIDADES
    # --------------------------------------------------------
    story.append(
        Paragraph(
            "DESCRIPCIÓN DE LAS ACTIVIDADES",
            estilo_h3
        )
    )

    actividad_header = Table(
        [[
            Paragraph(
                (
                    "<b>ACTIVIDAD:</b> "
                    + _texto_pdf(
                        descripcion_principal
                    )
                ),
                estilo_label
            )
        ]],
        colWidths=[
            524
        ]
    )

    actividad_header.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                azul_tabla
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            )
        ])
    )

    story.append(
        actividad_header
    )

    detalles = (
        _detalles_ejecutados_ot(
            actividades_ot,
            avances_ot
        )
    )

    # ========================================================
    # DETALLE EJECUTADO
    # ========================================================
    # IMPORTANTE:
    # No colocar todos los Paragraph dentro de UNA sola celda
    # de Table. Cuando una OT tiene muchos registros, ReportLab
    # convierte esa celda en una fila indivisible y puede superar
    # la altura de una página ("Flowable too large").
    #
    # En su lugar, cada línea se agrega como Flowable independiente,
    # permitiendo que ReportLab haga salto de página automáticamente.

    estilo_detalle_titulo = ParagraphStyle(
        f"DET_TIT_OT_{numero_ot}",
        parent=estilo_valor,
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        leftIndent=7,
        rightIndent=7,
        spaceBefore=5,
        spaceAfter=4,
        borderWidth=0.5,
        borderColor=colors.black,
        borderPadding=(5, 6, 4, 6)
    )

    estilo_detalle_linea = ParagraphStyle(
        f"DET_LIN_OT_{numero_ot}",
        parent=estilo_detalle,
        fontName="Helvetica",
        fontSize=7.8,
        leading=10,
        leftIndent=14,
        rightIndent=7,
        firstLineIndent=-7,
        spaceBefore=0,
        spaceAfter=3
    )

    story.append(
        Paragraph(
            "<b>DETALLE:</b>",
            estilo_detalle_titulo
        )
    )

    if detalles:

        for detalle in detalles:

            # Limitar únicamente caracteres de control; el texto
            # completo sigue disponible y puede dividirse entre páginas.
            detalle_limpio = str(
                detalle
                or ""
            ).strip()

            if not detalle_limpio:
                continue

            story.append(
                Paragraph(
                    (
                        "• "
                        + _texto_pdf(
                            detalle_limpio
                        )
                    ),
                    estilo_detalle_linea
                )
            )

    else:

        story.append(
            Paragraph(
                "• Sin descripción de ejecución registrada.",
                estilo_detalle_linea
            )
        )

    story.append(
        Spacer(
            1,
            10
        )
    )

    # --------------------------------------------------------
    # EVIDENCIAS FOTOGRÁFICAS
    # --------------------------------------------------------
    story.append(
        Paragraph(
            "EVIDENCIAS FOTOGRÁFICAS",
            estilo_h3
        )
    )

    story.append(
        _tabla_evidencias_antapaccay(
            avances_ot,
            estilo_vacio,
            directorio_temporal=directorio_temporal,
            prefijo_foto=(
                f"ot_{numero_ot}"
            )
        )
    )

    story.append(
        Spacer(
            1,
            5
        )
    )

    story.append(
        Paragraph(
            (
                f"OT {numero_ot} de {total_ots}"
                + (
                    " · "
                    + _texto_pdf(
                        supervisor_filtro
                    )
                    if supervisor_filtro
                    else ""
                )
            ),
            ParagraphStyle(
                f"FOOT_OT_{numero_ot}",
                parent=styles["BodyText"],
                fontSize=6.5,
                leading=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#667085"
                )
            )
        )
    )


def construir_pdf_formato_antapaccay(
    df_ots: pd.DataFrame,
    df_actividades: pd.DataFrame,
    df_avances: pd.DataFrame,
    nombre_area: str,
    titulo_reporte: str,
    supervisor: str = "",
    incluir_portada: bool = True
) -> bytes:
    """
    Genera el formato solicitado:
    cada OT conserva exactamente la misma estructura,
    y el PDF puede contener una OT, todas las OTs
    o todas las OTs de un supervisor.
    """

    # El compilado puede contener cientos de fotografías.
    # Se construye en disco temporal para reducir consumo de RAM.
    directorio_trabajo = tempfile.TemporaryDirectory()

    ruta_pdf_temporal = (
        Path(directorio_trabajo.name)
        / "informe_antapaccay.pdf"
    )

    doc = SimpleDocTemplate(
        str(ruta_pdf_temporal),
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()

    estilo_portada = ParagraphStyle(
        "PortadaAntapaccay",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#294B6D"
        ),
        spaceAfter=10
    )

    estilo_sub = ParagraphStyle(
        "SubAntapaccay",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#475467"
        )
    )

    story = []

    if (
        df_ots is None
        or df_ots.empty
    ):
        story.append(
            Paragraph(
                "No existen OTs para generar el informe.",
                estilo_sub
            )
        )

        doc.build(
            story
        )

        pdf_bytes = (
            ruta_pdf_temporal
            .read_bytes()
        )

        directorio_trabajo.cleanup()

        return pdf_bytes

    df_ots_ordenadas = (
        df_ots.copy()
    )

    if "ot" in (
        df_ots_ordenadas.columns
    ):

        df_ots_ordenadas[
            "_ot_orden"
        ] = (
            df_ots_ordenadas[
                "ot"
            ]
            .fillna("")
            .astype(str)
        )

        df_ots_ordenadas = (
            df_ots_ordenadas
            .sort_values(
                "_ot_orden"
            )
            .drop(
                columns=[
                    "_ot_orden"
                ]
            )
        )

    # ========================================================
    # PORTADA DEL COMPILADO
    # ========================================================
    if incluir_portada:

        story.append(
            Spacer(
                1,
                95
            )
        )

        story.append(
            Paragraph(
                "MAININ",
                estilo_portada
            )
        )

        story.append(
            Paragraph(
                _texto_pdf(
                    titulo_reporte
                ),
                estilo_portada
            )
        )

        story.append(
            Spacer(
                1,
                10
            )
        )

        alcance = (
            f"Supervisor: {supervisor}"
            if supervisor
            else "Alcance: todas las OTs seleccionadas"
        )

        total_fotos = (
            contar_total_fotos(
                df_avances
            )
        )

        kpis = compute_kpis(
            df_actividades,
            df_avances
        )

        portada_info = Table(
            [
                [
                    "ÁREA",
                    str(
                        nombre_area
                        or ""
                    )
                ],
                [
                    "ALCANCE",
                    alcance
                ],
                [
                    "OTs",
                    str(
                        len(
                            df_ots_ordenadas
                        )
                    )
                ],
                [
                    "ACTIVIDADES",
                    str(
                        int(
                            kpis.get(
                                "actividades",
                                0
                            )
                            or 0
                        )
                    )
                ],
                [
                    "AVANCE REAL",
                    (
                        f"{float(kpis.get('avance_general', 0) or 0):.1f}%"
                    )
                ],
                [
                    "EVIDENCIAS",
                    str(
                        total_fotos
                    )
                ],
                [
                    "FECHA DE EMISIÓN",
                    datetime.now().strftime(
                        "%d/%m/%Y %H:%M"
                    )
                ]
            ],
            colWidths=[
                140,
                300
            ]
        )

        portada_info.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#294B6D"
                    )
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.black
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            portada_info
        )

        story.append(
            PageBreak()
        )

    total_ots = len(
        df_ots_ordenadas
    )

    # ========================================================
    # UNA FICHA COMPLETA POR CADA OT
    # ========================================================
    for numero_ot, (
        _,
        fila_ot
    ) in enumerate(
        df_ots_ordenadas.iterrows(),
        start=1
    ):

        ot_id = fila_ot.get(
            "id"
        )

        actividades_ot = (
            df_actividades[
                df_actividades[
                    "ot_id"
                ].eq(
                    ot_id
                )
            ].copy()
            if (
                df_actividades is not None
                and not df_actividades.empty
                and "ot_id"
                in df_actividades.columns
            )
            else pd.DataFrame()
        )

        ids_actividades = (
            actividades_ot[
                "id"
            ]
            .dropna()
            .tolist()
            if (
                not actividades_ot.empty
                and "id"
                in actividades_ot.columns
            )
            else []
        )

        avances_ot = (
            df_avances[
                df_avances[
                    "actividad_id"
                ].isin(
                    ids_actividades
                )
            ].copy()
            if (
                df_avances is not None
                and not df_avances.empty
                and "actividad_id"
                in df_avances.columns
                and ids_actividades
            )
            else pd.DataFrame(
                columns=(
                    df_avances.columns
                    if df_avances is not None
                    else []
                )
            )
        )

        _agregar_ot_formato_antapaccay(
            story,
            fila_ot.to_dict(),
            actividades_ot,
            avances_ot,
            nombre_area,
            numero_ot,
            total_ots,
            supervisor,
            directorio_temporal=(
                directorio_trabajo.name
            )
        )

        # Liberación preventiva de objetos intermedios
        # durante compilados con muchas OTs.
        gc.collect()

        if numero_ot < total_ots:
            story.append(
                PageBreak()
            )

    doc.build(
        story
    )

    pdf_bytes = (
        ruta_pdf_temporal
        .read_bytes()
    )

    directorio_trabajo.cleanup()

    gc.collect()

    return pdf_bytes


# =====================================================
# PREPARAR DATAFRAME PARA EXCEL
# =====================================================

def preparar_dataframe_excel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte columnas no compatibles con Excel:
    - timestamps con zona horaria -> timestamps sin zona horaria
    - listas/diccionarios -> texto
    """

    salida = df.copy()

    for columna in salida.columns:

        serie = salida[columna]

        # Datetime con timezone
        if pd.api.types.is_datetime64tz_dtype(serie):
            salida[columna] = serie.dt.tz_localize(None)
            continue

        # Datetime normal
        if pd.api.types.is_datetime64_any_dtype(serie):
            continue

        # Objetos que pueden contener Timestamp con timezone,
        # listas o diccionarios.
        if serie.dtype == "object":

            def limpiar_valor(valor):

                if isinstance(valor, pd.Timestamp):

                    if valor.tzinfo is not None:
                        return valor.tz_localize(None)

                    return valor

                if isinstance(valor, (list, dict, tuple)):
                    return str(valor)

                return valor

            salida[columna] = serie.map(
                limpiar_valor
            )

    return salida



# =====================================================
# IDENTIDAD VISUAL MAININ - SIDEBAR
# =====================================================

LOGO_MAININ = Path(__file__).parent / "logo_mainin.png"


def mostrar_logo_mainin_sidebar():
    """Identidad compacta y consistente para escritorio y móvil."""

    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <div class="brand-mark">M</div>
                <div class="brand-copy">
                    <div class="brand-name">MAININ</div>
                    <div class="brand-product">PDP · Quellaveco</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =====================================================
def mostrar_kpis_operativos(kpis, total_ots):
    total_actividades = int(kpis.get("actividades", 0) or 0)
    avance_general = float(kpis.get("avance_general", 0) or 0)
    culminadas = int(kpis.get("culminadas", 0) or 0)
    en_ejecucion = int(kpis.get("parciales", 0) or 0)
    no_iniciadas = int(kpis.get("no_iniciadas", 0) or 0)
    spi = float(kpis.get("spi", 0) or 0)
    hh_plan = float(kpis.get("hh_plan", 0) or 0)
    hh_ganadas = float(kpis.get("hh_ganadas", 0) or 0)

    def clase_por_valor(nombre, valor=None):
        if nombre == "avance_general":
            if valor >= 90:
                return "good"
            if valor >= 70:
                return "warn"
            return "risk"
        if nombre == "spi":
            if valor >= 1:
                return "good"
            if valor >= 0.9:
                return "warn"
            return "risk"
        if nombre in {"culminadas", "hh_ganadas"}:
            return "good"
        if nombre in {"no_iniciadas"}:
            return "risk"
        return "neutral"

    tarjetas = [
        ("OTs", f"{total_ots}", "Órdenes activas del área", "neutral"),
        ("Actividades", f"{total_actividades}", "Frente total de trabajo", "neutral"),
        ("Avance", f"{avance_general:.1f}%", "Progreso acumulado real", clase_por_valor("avance_general", avance_general)),
        ("Culminadas", f"{culminadas}", "Actividades al 100%", "good"),
        ("En ejecución", f"{en_ejecucion}", "Con avance parcial", "warn"),
        ("No iniciadas", f"{no_iniciadas}", "Pendientes de arranque", "risk"),
        ("SPI", f"{spi:.2f}", "Desempeño plan vs real", clase_por_valor("spi", spi)),
        ("HH plan", f"{hh_plan:.0f}", "Horas hombre planificadas", "neutral"),
        ("HH ganadas", f"{hh_ganadas:.0f}", "Horas hombre ejecutadas", "good"),
    ]

    html = ['<div class="planner-kpi-grid">']
    for titulo, valor, pie, clase in tarjetas:
        html.append(
            f'<div class="planner-kpi-card {clase}"><div class="planner-kpi-label">{titulo}</div><div class="planner-kpi-value">{valor}</div><div class="planner-kpi-foot">{pie}</div></div>'
        )
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


# CONTROL DE ROLES Y CONTRASEÑAS
# =====================================================

ROLES_PERMITIDOS = {
    "admin",
    "planner",
    "supervisor",
    "lider"
}


def normalizar_rol(rol):
    """
    Mantiene compatibilidad con usuarios REPORTER existentes.
    REPORTER se interpreta temporalmente como PLANNER.
    """
    rol_normalizado = str(rol or "").strip().lower()

    if rol_normalizado == "reporter":
        return "planner"

    return rol_normalizado


def verificar_contrasena(password_plano, password_hash):
    """
    Formato esperado:
    pbkdf2_sha256$260000$SALT$HASH_HEX
    """

    if not password_hash:
        return False

    try:
        algoritmo, iteraciones, salt, hash_guardado = (
            password_hash.split("$", 3)
        )

        if algoritmo != "pbkdf2_sha256":
            return False

        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            password_plano.encode("utf-8"),
            salt.encode("utf-8"),
            int(iteraciones)
        ).hex()

        return hmac.compare_digest(
            hash_calculado,
            hash_guardado
        )

    except Exception:
        return False


def menu_por_rol(rol):
    """
    ADMIN: menú administrativo completo.
    PLANNER: menú completo de su área.
    SUPERVISOR / LIDER: solo registro de avances.
    """

    rol = normalizar_rol(rol)

    if rol == "planner":
        return [
            "Dashboard",
            "Registrar avance",
            "Detalle por OT",
            "Evidencias",
            "Reportes"
        ]

    if rol in {"supervisor", "lider"}:
        return [
            "Registrar avance"
        ]

    return []


# =====================================================
# LOGIN Y CONTROL DE ACCESO
# =====================================================

def _secreto_sesion():
    """
    Usa una clave privada del servidor para firmar el token.
    Nunca se envía la contraseña al navegador.
    """
    secreto = st.secrets.get("SUPABASE_ADMIN_KEY")

    if not secreto:
        raise RuntimeError(
            "No existe SUPABASE_ADMIN_KEY para firmar la sesión."
        )

    return str(secreto)


def crear_token_sesion(username):
    expira = int(
        (
            datetime.now(timezone.utc)
            + timedelta(days=DIAS_SESION_PERSISTENTE)
        ).timestamp()
    )

    payload = f"{str(username).strip()}|{expira}"

    payload_b64 = (
        base64.urlsafe_b64encode(
            payload.encode("utf-8")
        )
        .decode("ascii")
        .rstrip("=")
    )

    firma = hmac.new(
        _secreto_sesion().encode("utf-8"),
        payload_b64.encode("ascii"),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{firma}"


def validar_token_sesion(token):
    try:
        payload_b64, firma_recibida = str(token).split(".", 1)

        firma_esperada = hmac.new(
            _secreto_sesion().encode("utf-8"),
            payload_b64.encode("ascii"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            firma_esperada,
            firma_recibida
        ):
            return None

        padding = "=" * (-len(payload_b64) % 4)

        payload = base64.urlsafe_b64decode(
            payload_b64 + padding
        ).decode("utf-8")

        username, expira_txt = payload.rsplit("|", 1)

        if int(datetime.now(timezone.utc).timestamp()) >= int(expira_txt):
            return None

        return username.strip() or None

    except Exception:
        return None


def leer_token_sesion_persistente():
    """
    En un refresh completo, st.context.cookies es la fuente principal
    porque contiene las cookies enviadas en la petición inicial.

    CookieManager queda como respaldo para versiones antiguas de Streamlit.
    """

    # 1) Lectura síncrona desde la petición inicial del navegador
    try:
        cookies_contexto = st.context.cookies
        token = cookies_contexto.get(COOKIE_SESION)

        if token:
            return str(token)

    except Exception:
        pass

    # 2) Respaldo mediante el componente
    try:
        cookies_componente = cookie_manager.get_all(
            key="mainin_leer_cookies_sesion"
        ) or {}

        token = cookies_componente.get(
            COOKIE_SESION
        )

        if token:
            return str(token)

    except Exception:
        pass

    return None


def guardar_sesion_persistente(username):
    """
    Guarda un token firmado por 7 días.
    No almacena la contraseña.
    """
    token = crear_token_sesion(username)

    cookie_manager.set(
        COOKIE_SESION,
        token,
        key="mainin_guardar_sesion",
        path="/",
        expires_at=(
            datetime.now()
            + timedelta(days=DIAS_SESION_PERSISTENTE)
        ),
        max_age=COOKIE_MAX_AGE,
        secure=True,
        same_site="lax"
    )

    return token


def eliminar_sesion_persistente():
    """
    Elimina la cookie de sesión de forma robusta.

    Se expira explícitamente usando el mismo path="/"
    con el que fue creada. Después se ejecuta delete()
    como limpieza adicional.
    """
    try:
        cookie_manager.set(
            COOKIE_SESION,
            "",
            key="mainin_expirar_sesion",
            path="/",
            expires_at=(
                datetime.now()
                - timedelta(days=1)
            ),
            max_age=0,
            secure=True,
            same_site="lax"
        )
    except Exception:
        pass

    try:
        cookie_manager.delete(
            COOKIE_SESION,
            key="mainin_eliminar_sesion"
        )
    except Exception:
        pass


def obtener_usuario(username):
    resultado = (
        supabase
        .table("usuarios_app")
        .select(
            "id,username,nombre,rol,area_id,activo,password_hash,"
            "areas(id,codigo,nombre)"
        )
        .eq("username", username)
        .eq("activo", True)
        .limit(1)
        .execute()
    )

    datos = resultado.data or []

    if not datos:
        return None

    return datos[0]


if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None

if "logout_en_proceso" not in st.session_state:
    st.session_state["logout_en_proceso"] = False


# =====================================================
# RESTAURAR SESIÓN PERSISTENTE
# =====================================================
if (
    st.session_state["usuario_logueado"] is None
    and not st.session_state["logout_en_proceso"]
):

    token_guardado = leer_token_sesion_persistente()

    if token_guardado:

        username_guardado = validar_token_sesion(
            token_guardado
        )

        if username_guardado:

            usuario_guardado = obtener_usuario(
                username_guardado
            )

            if usuario_guardado is not None:

                rol_guardado = normalizar_rol(
                    usuario_guardado.get("rol")
                )

                rol_valido = (
                    rol_guardado in ROLES_PERMITIDOS
                )

                area_valida = (
                    rol_guardado == "admin"
                    or bool(
                        usuario_guardado.get("area_id")
                    )
                )

                if rol_valido and area_valida:

                    usuario_guardado["rol"] = rol_guardado

                    st.session_state[
                        "usuario_logueado"
                    ] = usuario_guardado

                else:
                    eliminar_sesion_persistente()

            else:
                eliminar_sesion_persistente()

        else:
            eliminar_sesion_persistente()


# =====================================================
# PANTALLA DE LOGIN
# =====================================================

if st.session_state["usuario_logueado"] is None:

    st.markdown(
        """
        <style>
        [data-testid="stVerticalBlockBorderWrapper"] {
            max-width: 470px;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="login-shell">
            <div class="login-brandline">
                <div class="login-symbol">M</div>
                <div class="login-brandtext">MAININ · QUELLAVECO</div>
            </div>
            <div class="login-panel">
                <div class="login-panel-row">
                    <div>
                        <div class="login-product">PDP Control Center</div>
                        <div class="login-location">Electricidad · Instrumentación</div>
                    </div>
                    <div class="login-mini-status">
                        <span>PLAN</span>
                        <span>REAL</span>
                        <span>EVIDENCIAS</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.markdown(
            """
            <div class="login-card-title">Acceso</div>
            <div class="login-card-sub">Ingrese sus credenciales corporativas</div>
            """,
            unsafe_allow_html=True
        )

        username = st.selectbox(
            "Usuario",
            options=USUARIOS_LOGIN,
            index=None,
            placeholder="Buscar o seleccionar usuario",
            format_func=lambda usuario_login: (
                ETIQUETAS_USUARIOS_LOGIN.get(
                    usuario_login,
                    usuario_login
                )
            ),
            help=(
                "Seleccione su usuario. También puede escribir "
                "para buscarlo dentro de la lista."
            )
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Contraseña"
        )

        mantener_sesion = st.checkbox(
            "Mantener sesión iniciada",
            value=True,
            help=(
                "Mantiene el acceso durante 7 días en este navegador."
            )
        )

        if st.button(
            "Ingresar al Control Center",
            type="primary",
            use_container_width=True
        ):

            if not username:
                st.warning(
                    "Seleccione un usuario antes de ingresar."
                )
                usuario = None
            else:
                usuario = obtener_usuario(
                    str(username).strip()
                )

            if not username:
                pass

            elif usuario is None:
                st.error("Usuario no encontrado o inactivo.")

            else:

                rol_login = normalizar_rol(
                    usuario.get("rol")
                )

                if rol_login not in ROLES_PERMITIDOS:
                    st.error(
                        "El usuario tiene un rol no permitido. "
                        "Contacte al administrador."
                    )

                elif (
                    rol_login != "admin"
                    and not usuario.get("area_id")
                ):
                    st.error(
                        "El usuario no tiene un área asignada."
                    )

                elif verificar_contrasena(
                    password.strip(),
                    usuario.get("password_hash")
                ):

                    usuario["rol"] = rol_login

                    st.session_state[
                        "usuario_logueado"
                    ] = usuario

                    st.session_state[
                        "logout_en_proceso"
                    ] = False

                    if mantener_sesion:

                        guardar_sesion_persistente(
                            usuario.get(
                                "username",
                                str(username or "").strip()
                            )
                        )

                        # CookieManager es un componente del navegador.
                        # Damos tiempo a que la escritura termine antes
                        # del rerun; esto evita perder la cookie.
                        time.sleep(1.0)

                    else:
                        eliminar_sesion_persistente()
                        time.sleep(0.25)

                    st.rerun()

                else:
                    st.error("Contraseña incorrecta.")

        st.markdown(
            """
            <div class="login-foot">
                <span class="login-foot-dot"></span>
                Sesión segura · MAININ
            </div>
            """,
            unsafe_allow_html=True
        )

    st.stop()


# =====================================================
# USUARIO LOGUEADO
# =====================================================

usuario = st.session_state["usuario_logueado"]

rol = normalizar_rol(
    usuario.get("rol")
)

usuario["rol"] = rol

area_info = usuario.get("areas")

if rol == "admin":
    codigo_area = "TODAS"
    nombre_area = "Todas las áreas"
else:
    codigo_area = area_info["codigo"]
    nombre_area = area_info["nombre"]


# =====================================================
# SIDEBAR
# =====================================================

mostrar_logo_mainin_sidebar()

with st.sidebar:

    nombre_rol_sidebar = {
        "admin": "ADMIN",
        "planner": "PLANNER",
        "supervisor": "SUPERVISOR",
        "lider": "LÍDER"
    }.get(
        rol,
        rol.upper()
    )

    area_sidebar = (
        "TODAS LAS ÁREAS"
        if rol == "admin"
        else nombre_area
    )

    inicial_usuario = str(usuario.get("nombre") or "U").strip()[:1].upper()

    st.markdown(
        f"""
        <div class="sidebar-user-card">
            <div class="sidebar-user-top">
                <div class="sidebar-avatar">{inicial_usuario}</div>
                <div>
                    <div class="sidebar-user-name">{usuario['nombre']}</div>
                    <div class="sidebar-user-caption">Workspace activo</div>
                </div>
            </div>
            <span class="sidebar-pill">{nombre_rol_sidebar}</span>
            <span class="sidebar-pill">{area_sidebar}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "↪  Cerrar sesión",
        use_container_width=True
    ):
        # Primero bloqueamos cualquier restauración automática
        # dentro de esta misma sesión de Streamlit.
        st.session_state[
            "logout_en_proceso"
        ] = True

        # Luego vencemos la cookie persistente del navegador.
        eliminar_sesion_persistente()

        # CookieManager trabaja en el frontend; damos tiempo
        # a que el navegador procese la expiración antes del rerun.
        time.sleep(1.0)

        st.session_state["usuario_logueado"] = None
        st.rerun()


# =====================================================
# PANTALLA PRINCIPAL
# =====================================================

mostrar_header_profesional(
    subtitulo="Seguimiento ejecutivo y operativo de la parada de planta",
    estado=nombre_area,
    rol=nombre_rol_sidebar,
    area=area_sidebar
)


# =====================================================
# ADMINISTRADOR
# =====================================================

if rol == "admin":

    # =====================================================
    # MENÚ ADMINISTRADOR
    # =====================================================

    with st.sidebar:

        mostrar_etiqueta_navegacion("Workspace")

        pagina_admin = st.radio(
            "Menú administrador",
            [
                "Dashboard general",
                "Importar planificación",
                "Administrar OTs",
                "Reportes"
            ],
            format_func=etiqueta_menu,
            label_visibility="collapsed"
        )


    # =====================================================
    # DASHBOARD GENERAL
    # =====================================================

    if pagina_admin == "Dashboard general":

        mostrar_acceso_pagina(
            "Dashboard Ejecutivo de Parada",
            "PLAN vs REAL, cumplimiento, alertas y desempeño operativo.",
            icono="◫",
            contexto="ADMIN · CONTROL EJECUTIVO",
            badge="Electricidad · Instrumentación"
        )

        # =================================================
        # 1. CARGAR ÁREAS ACTIVAS
        # =================================================

        resultado_areas_admin = (
            supabase
            .table("areas")
            .select("id,codigo,nombre")
            .eq("activo", True)
            .order("id")
            .execute()
        )

        areas_admin = (
            resultado_areas_admin.data
            or []
        )

        if not areas_admin:

            st.warning(
                "No existen áreas activas configuradas."
            )

        else:

            # =============================================
            # SELECTOR DE VISTA ADMINISTRATIVA
            # =============================================

            mapa_vistas_admin = {
                "Todas las áreas": None
            }

            for area in areas_admin:
                mapa_vistas_admin[
                    area["nombre"]
                ] = area["id"]

            vista_admin = st.selectbox(
                "Seleccionar vista",
                list(mapa_vistas_admin.keys()),
                key="selector_vista_admin"
            )

            area_id_seleccionada_admin = (
                mapa_vistas_admin[
                    vista_admin
                ]
            )

            if area_id_seleccionada_admin is None:

                areas_vista_admin = areas_admin

                st.info(
                    "Vista actual: TODAS LAS ÁREAS"
                )

            else:

                areas_vista_admin = [
                    area
                    for area in areas_admin
                    if area["id"]
                    == area_id_seleccionada_admin
                ]

                st.info(
                    f"Vista actual: {vista_admin}"
                )

            ids_areas_admin = [
                area["id"]
                for area in areas_vista_admin
            ]

            # =============================================
            # 2. OTs DE LA VISTA SELECCIONADA
            # =============================================


            ots_admin = (
                supabase
                .table("ots")
                .select(
                    "id,ot,area_id,equipo,descripcion,activo"
                )
                .in_(
                    "area_id",
                    ids_areas_admin
                )
                .eq(
                    "activo",
                    True
                )
                .execute()
            ).data or []

            df_ots_admin = pd.DataFrame(
                ots_admin
            )

            if not ots_admin:

                st.warning(
                    "Todavía no existen OTs activas "
                    "en las áreas configuradas."
                )

            else:

                ids_ots_admin = [
                    ot["id"]
                    for ot in ots_admin
                ]

                # =========================================
                # 3. ACTIVIDADES CONSOLIDADAS
                # =========================================

                actividades_admin = (
                    supabase
                    .table("actividades")
                    .select(
                        "id,ot_id,codigo_actividad,descripcion,"
                        "descripcion_trabajo,operacion,ssoma,"
                        "supervisor,especialidad,grupo,peso,"
                        "inicio_plan,fin_plan,seccion,personal,"
                        "duracion_h,hh_plan,critica,activo"
                    )
                    .in_(
                        "ot_id",
                        ids_ots_admin
                    )
                    .eq(
                        "activo",
                        True
                    )
                    .execute()
                ).data or []

                df_actividades_admin = pd.DataFrame(
                    actividades_admin
                )

                if actividades_admin:

                    ids_actividades_admin = [
                        actividad["id"]
                        for actividad in actividades_admin
                    ]

                    avances_admin = (
                        supabase
                        .table("avances_actividad")
                        .select(
                            "id,actividad_id,avance,"
                            "descripcion_avance,observaciones,"
                            "tipo_evidencia,critica,evidencias,"
                            "usuario,fecha_registro"
                        )
                        .in_(
                            "actividad_id",
                            ids_actividades_admin
                        )
                        .execute()
                    ).data or []

                else:

                    avances_admin = []

                df_avances_admin = pd.DataFrame(
                    avances_admin
                )

                # =========================================
                # 4. RESUMEN EJECUTIVO DE LA PDP
                # =========================================

                kpis_admin = compute_kpis(
                    df_actividades_admin,
                    df_avances_admin
                )

                total_ots_admin = len(
                    df_ots_admin
                )

                mostrar_titulo_ejecutivo(
                    "Resumen ejecutivo",
                    (
                        "Indicadores clave de cumplimiento y productividad "
                        "de la vista seleccionada."
                    ),
                    vista_admin
                )

                mostrar_resumen_ejecutivo_dashboard(
                    kpis_admin,
                    total_ots_admin,
                    vista_admin
                )

                st.divider()

                # =========================================
                # 5. CURVA S - PLAN VS REAL
                # =========================================

                titulo_curva_admin = (
                    "Curva S consolidada · Plan vs Real"
                    if area_id_seleccionada_admin is None
                    else f"Curva S · {vista_admin}"
                )

                mostrar_titulo_ejecutivo(
                    titulo_curva_admin,
                    (
                        "Cortes oficiales 00:00 · 07:00 · 14:00 · 19:00, "
                        "más punto de avance en vivo durante la ejecución."
                    ),
                    "Control de avance"
                )

                curva_admin = build_s_curve(
                    df_actividades_admin,
                    df_avances_admin
                )

                mostrar_corte_validado_cliente(
                    df_actividades_admin
                )

                if curva_admin.empty:

                    st.info(
                        "No existe información suficiente "
                        "para construir la Curva S consolidada."
                    )

                else:

                    figura_curva_admin, info_curva_admin = (
                        crear_curva_s_tiempo_real(
                            curva_admin,
                            altura=490
                        )
                    )

                    mostrar_estado_curva_en_vivo(
                        info_curva_admin
                    )

                    st.plotly_chart(
                        figura_curva_admin,
                        use_container_width=True,
                        config={
                            "displaylogo": False,
                            "displayModeBar": False,
                            "responsive": True
                        }
                    )

                st.divider()

                # =========================================
                # 6. SEMÁFORO EJECUTIVO
                # =========================================

                mostrar_titulo_ejecutivo(
                    "Semáforo ejecutivo",
                    (
                        "Priorización automática por desviación PLAN vs REAL, "
                        "criticidad y vencimiento."
                    ),
                    "Foco gerencial"
                )

                estado_semaforo_admin = build_activity_status(
                    df_actividades_admin,
                    df_avances_admin
                )

                if estado_semaforo_admin.empty:

                    st.info(
                        "No existe información suficiente para "
                        "calcular el semáforo ejecutivo."
                    )

                else:

                    estado_semaforo_admin = (
                        estado_semaforo_admin
                        .merge(
                            df_ots_admin[
                                [
                                    "id",
                                    "ot",
                                    "area_id",
                                    "equipo"
                                ]
                            ],
                            left_on="ot_id",
                            right_on="id",
                            how="left",
                            suffixes=(
                                "",
                                "_ot"
                            )
                        )
                    )

                    mapa_area_sem_admin = {
                        area["id"]: area["nombre"]
                        for area in areas_vista_admin
                    }

                    estado_semaforo_admin["Área"] = (
                        estado_semaforo_admin[
                            "area_id"
                        ].map(
                            mapa_area_sem_admin
                        )
                    )

                    ahora_sem_admin = pd.Timestamp.now(tz="America/Lima").tz_localize(None)

                    inicio_sem_admin = pd.to_datetime(
                        estado_semaforo_admin.get(
                            "inicio_plan"
                        ),
                        errors="coerce"
                    )

                    fin_sem_admin = pd.to_datetime(
                        estado_semaforo_admin.get(
                            "fin_plan"
                        ),
                        errors="coerce"
                    )

                    real_sem_admin = pd.to_numeric(
                        estado_semaforo_admin.get(
                            "avance_real",
                            0
                        ),
                        errors="coerce"
                    ).fillna(0)

                    plan_sem_admin = []

                    for ini_sem, fin_sem in zip(
                        inicio_sem_admin,
                        fin_sem_admin
                    ):

                        if (
                            pd.isna(ini_sem)
                            or pd.isna(fin_sem)
                        ):
                            plan_sem_admin.append(0.0)
                            continue

                        if fin_sem <= ini_sem:
                            fin_sem = (
                                ini_sem
                                + pd.Timedelta(minutes=1)
                            )

                        if ahora_sem_admin <= ini_sem:
                            valor_plan_sem = 0.0

                        elif ahora_sem_admin >= fin_sem:
                            valor_plan_sem = 100.0

                        else:
                            duracion_sem = (
                                fin_sem - ini_sem
                            ).total_seconds()

                            transcurrido_sem = (
                                ahora_sem_admin - ini_sem
                            ).total_seconds()

                            valor_plan_sem = (
                                transcurrido_sem
                                / duracion_sem
                                * 100
                                if duracion_sem > 0
                                else 100.0
                            )

                        plan_sem_admin.append(
                            max(
                                0.0,
                                min(
                                    100.0,
                                    float(valor_plan_sem)
                                )
                            )
                        )

                    estado_semaforo_admin[
                        "PLAN ACTUAL (%)"
                    ] = plan_sem_admin

                    estado_semaforo_admin[
                        "DESVIACIÓN (pp)"
                    ] = (
                        real_sem_admin
                        - estado_semaforo_admin[
                            "PLAN ACTUAL (%)"
                        ]
                    ).round(1)

                    if (
                        "critica"
                        not in estado_semaforo_admin.columns
                    ):
                        estado_semaforo_admin[
                            "critica"
                        ] = False

                    estado_semaforo_admin[
                        "critica"
                    ] = (
                        estado_semaforo_admin[
                            "critica"
                        ]
                        .fillna(False)
                    )

                    def semaforo_gerencial_admin(fila):

                        real = float(
                            fila.get(
                                "avance_real",
                                0
                            )
                            or 0
                        )

                        plan = float(
                            fila.get(
                                "PLAN ACTUAL (%)",
                                0
                            )
                            or 0
                        )

                        critica = bool(
                            fila.get(
                                "critica",
                                False
                            )
                        )

                        fin = fila.get(
                            "fin_plan"
                        )

                        desviacion = real - plan

                        if real >= 100:
                            return (
                                "🟢",
                                "VERDE",
                                "Culminada",
                                "Sin acción requerida",
                                90
                            )

                        if (
                            pd.notna(fin)
                            and ahora_sem_admin
                            > pd.Timestamp(fin)
                            and real < 100
                        ):
                            return (
                                "🔴",
                                "ROJO",
                                (
                                    "Crítica vencida"
                                    if critica
                                    else "Vencida"
                                ),
                                (
                                    "Escalar y definir "
                                    "recuperación inmediata"
                                ),
                                1 if critica else 2
                            )

                        if critica:

                            if desviacion < -10:
                                return (
                                    "🔴",
                                    "ROJO",
                                    "Crítica atrasada",
                                    (
                                        "Escalar y definir "
                                        "recuperación inmediata"
                                    ),
                                    3
                                )

                            if desviacion < -5:
                                return (
                                    "🟠",
                                    "NARANJA",
                                    "Crítica en riesgo",
                                    (
                                        "Aplicar plan de "
                                        "recuperación"
                                    ),
                                    5
                                )

                            return (
                                "🟢",
                                "VERDE",
                                "Crítica en línea",
                                "Mantener seguimiento cercano",
                                30
                            )

                        if desviacion < -20:
                            return (
                                "🔴",
                                "ROJO",
                                "Atraso crítico",
                                (
                                    "Intervención inmediata / "
                                    "reprogramar recursos"
                                ),
                                4
                            )

                        if desviacion < -10:
                            return (
                                "🟠",
                                "NARANJA",
                                "Atrasada",
                                "Definir plan de recuperación",
                                6
                            )

                        if desviacion < -5:
                            return (
                                "🟡",
                                "AMARILLO",
                                "En riesgo",
                                "Seguimiento del supervisor",
                                10
                            )

                        return (
                            "🟢",
                            "VERDE",
                            "En línea",
                            "Sin acción requerida",
                            40
                        )

                    resultado_sem_admin = (
                        estado_semaforo_admin
                        .apply(
                            semaforo_gerencial_admin,
                            axis=1
                        )
                    )

                    estado_semaforo_admin[
                        "SEMÁFORO"
                    ] = resultado_sem_admin.map(
                        lambda item: item[0]
                    )

                    estado_semaforo_admin[
                        "NIVEL"
                    ] = resultado_sem_admin.map(
                        lambda item: item[1]
                    )

                    estado_semaforo_admin[
                        "ALERTA"
                    ] = resultado_sem_admin.map(
                        lambda item: item[2]
                    )

                    estado_semaforo_admin[
                        "ACCIÓN REQUERIDA"
                    ] = resultado_sem_admin.map(
                        lambda item: item[3]
                    )

                    estado_semaforo_admin[
                        "_PRIORIDAD"
                    ] = resultado_sem_admin.map(
                        lambda item: item[4]
                    )

                    verdes_sem_admin = int(
                        (
                            estado_semaforo_admin[
                                "NIVEL"
                            ] == "VERDE"
                        ).sum()
                    )

                    amarillos_sem_admin = int(
                        (
                            estado_semaforo_admin[
                                "NIVEL"
                            ] == "AMARILLO"
                        ).sum()
                    )

                    naranjas_sem_admin = int(
                        (
                            estado_semaforo_admin[
                                "NIVEL"
                            ] == "NARANJA"
                        ).sum()
                    )

                    rojos_sem_admin = int(
                        (
                            estado_semaforo_admin[
                                "NIVEL"
                            ] == "ROJO"
                        ).sum()
                    )

                    gs1, gs2, gs3, gs4 = st.columns(4)

                    with gs1:
                        st.metric(
                            "🟢 En línea",
                            verdes_sem_admin
                        )

                    with gs2:
                        st.metric(
                            "🟡 En riesgo",
                            amarillos_sem_admin
                        )

                    with gs3:
                        st.metric(
                            "🟠 Recuperación",
                            naranjas_sem_admin
                        )

                    with gs4:
                        st.metric(
                            "🔴 Intervención",
                            rojos_sem_admin
                        )

                    foco_gerencial_admin = (
                        estado_semaforo_admin[
                            estado_semaforo_admin[
                                "NIVEL"
                            ].isin(
                                [
                                    "ROJO",
                                    "NARANJA",
                                    "AMARILLO"
                                ]
                            )
                        ]
                        .sort_values(
                            [
                                "_PRIORIDAD",
                                "avance_real"
                            ],
                            ascending=[
                                True,
                                True
                            ]
                        )
                        .head(12)
                        .copy()
                    )

                    if foco_gerencial_admin.empty:

                        st.success(
                            "No existen desviaciones que "
                            "requieran atención en este momento."
                        )

                    else:

                        st.markdown(
                            "#### Foco de atención gerencial"
                        )

                        columnas_foco_admin = [
                            "SEMÁFORO",
                            "ALERTA",
                            "Área",
                            "ot",
                            "equipo",
                            "codigo_actividad",
                            "PLAN ACTUAL (%)",
                            "avance_real",
                            "DESVIACIÓN (pp)",
                            "supervisor",
                            "ACCIÓN REQUERIDA"
                        ]

                        columnas_foco_admin = [
                            columna
                            for columna
                            in columnas_foco_admin
                            if columna
                            in foco_gerencial_admin.columns
                        ]

                        tabla_foco_admin = (
                            foco_gerencial_admin[
                                columnas_foco_admin
                            ]
                            .rename(
                                columns={
                                    "ot": "OT",
                                    "equipo": "EQUIPO",
                                    "codigo_actividad":
                                        "ACTIVIDAD",
                                    "avance_real":
                                        "REAL (%)",
                                    "supervisor":
                                        "SUPERVISOR"
                                }
                            )
                        )

                        st.dataframe(
                            tabla_foco_admin,
                            use_container_width=True,
                            hide_index=True,
                            height=320
                        )

                st.divider()

                # =========================================
                # 7. COMPARATIVO POR ÁREA
                # =========================================

                titulo_comparativo_admin = (
                    "Comparativo por área"
                    if area_id_seleccionada_admin is None
                    else f"Indicadores · {vista_admin}"
                )

                mostrar_titulo_ejecutivo(
                    titulo_comparativo_admin,
                    "Comparación de PLAN, REAL, SPI, HH y estado de actividades.",
                    "Benchmark interno"
                )

                resumen_areas = []

                for area in areas_vista_admin:

                    area_id_admin = area["id"]

                    ots_area_admin = (
                        df_ots_admin[
                            df_ots_admin["area_id"]
                            == area_id_admin
                        ].copy()
                        if not df_ots_admin.empty
                        else pd.DataFrame()
                    )

                    ids_ots_area_admin = (
                        ots_area_admin["id"]
                        .dropna()
                        .tolist()
                        if not ots_area_admin.empty
                        else []
                    )

                    if (
                        ids_ots_area_admin
                        and not df_actividades_admin.empty
                    ):

                        actividades_area_admin = (
                            df_actividades_admin[
                                df_actividades_admin["ot_id"]
                                .isin(
                                    ids_ots_area_admin
                                )
                            ].copy()
                        )

                    else:

                        actividades_area_admin = (
                            pd.DataFrame()
                        )

                    ids_actividades_area_admin = (
                        actividades_area_admin["id"]
                        .dropna()
                        .tolist()
                        if not actividades_area_admin.empty
                        else []
                    )

                    if (
                        ids_actividades_area_admin
                        and not df_avances_admin.empty
                    ):

                        avances_area_admin = (
                            df_avances_admin[
                                df_avances_admin[
                                    "actividad_id"
                                ].isin(
                                    ids_actividades_area_admin
                                )
                            ].copy()
                        )

                    else:

                        avances_area_admin = (
                            pd.DataFrame()
                        )

                    kpis_area_admin = compute_kpis(
                        actividades_area_admin,
                        avances_area_admin
                    )

                    resumen_areas.append({
                        "Área": area["nombre"],
                        "Código": area["codigo"],
                        "OTs": len(ots_area_admin),
                        "Actividades": kpis_area_admin[
                            "actividades"
                        ],
                        "Plan (%)": round(
                            kpis_area_admin.get(
                                "avance_plan",
                                0
                            ),
                            1
                        ),
                        "Real (%)": round(
                            kpis_area_admin[
                                "avance_general"
                            ],
                            1
                        ),
                        "SPI": round(
                            kpis_area_admin[
                                "spi"
                            ],
                            2
                        ),
                        "Culminadas": kpis_area_admin[
                            "culminadas"
                        ],
                        "En ejecución": kpis_area_admin[
                            "parciales"
                        ],
                        "No iniciadas": kpis_area_admin[
                            "no_iniciadas"
                        ],
                        "Pendientes": kpis_area_admin[
                            "pendientes"
                        ],
                        "HH plan": round(
                            kpis_area_admin[
                                "hh_plan"
                            ],
                            0
                        ),
                        "HH ganadas": round(
                            kpis_area_admin[
                                "hh_ganadas"
                            ],
                            0
                        )
                    })

                df_resumen_areas = pd.DataFrame(
                    resumen_areas
                )

                if not df_resumen_areas.empty:

                    figura_areas = go.Figure()

                    figura_areas.add_bar(
                        x=df_resumen_areas["Área"],
                        y=df_resumen_areas["Plan (%)"],
                        name="PLAN",
                        marker_color="#155EEF",
                        marker_line_width=0
                    )

                    figura_areas.add_bar(
                        x=df_resumen_areas["Área"],
                        y=df_resumen_areas["Real (%)"],
                        name="REAL",
                        marker_color="#D92D20",
                        marker_line_width=0
                    )

                    figura_areas.update_layout(
                        barmode="group",
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#FFFFFF",
                        font=dict(color="#344054", size=12),
                        bargap=0.28,
                        yaxis=dict(
                            title="Avance (%)",
                            range=[0, 100],
                            gridcolor="#EEF2F6",
                            ticksuffix="%",
                            zeroline=False
                        ),
                        xaxis=dict(
                            title="Área",
                            linecolor="#D0D5DD"
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.03,
                            xanchor="right",
                            x=1
                        ),
                        height=430,
                        margin=dict(
                            l=30,
                            r=20,
                            t=45,
                            b=30
                        )
                    )

                    st.plotly_chart(
                        figura_areas,
                        use_container_width=True
                    )

                    st.dataframe(
                        df_resumen_areas,
                        use_container_width=True,
                        hide_index=True,
                        height=280
                    )

                st.divider()

                # =========================================
                # 8. DESEMPEÑO POR SUPERVISOR
                # =========================================

                titulo_supervisor_admin = (
                    "Desempeño por Supervisor · Todas las áreas"
                    if area_id_seleccionada_admin is None
                    else f"Desempeño por Supervisor · {vista_admin}"
                )

                mostrar_titulo_ejecutivo(
                    titulo_supervisor_admin,
                    (
                        "Cumplimiento, desviación y disciplina de reporte por responsable. "
                        "Las actividades futuras no penalizan el indicador."
                    ),
                    "Disciplina operativa"
                )

                estado_supervisor_admin = build_activity_status(
                    df_actividades_admin,
                    df_avances_admin
                )

                if estado_supervisor_admin.empty:

                    st.info(
                        "No existen actividades para evaluar "
                        "el desempeño de supervisores."
                    )

                elif (
                    "supervisor"
                    not in estado_supervisor_admin.columns
                ):

                    st.warning(
                        "Las actividades cargadas no contienen "
                        "información de supervisor."
                    )

                else:

                    # -----------------------------------------
                    # Incorporar OT y área
                    # -----------------------------------------

                    estado_supervisor_admin = (
                        estado_supervisor_admin
                        .merge(
                            df_ots_admin[
                                [
                                    "id",
                                    "ot",
                                    "area_id",
                                    "equipo"
                                ]
                            ],
                            left_on="ot_id",
                            right_on="id",
                            how="left",
                            suffixes=(
                                "",
                                "_ot"
                            )
                        )
                    )

                    mapa_area_supervisor_admin = {
                        area["id"]: area["nombre"]
                        for area in areas_vista_admin
                    }

                    estado_supervisor_admin[
                        "Área"
                    ] = (
                        estado_supervisor_admin[
                            "area_id"
                        ].map(
                            mapa_area_supervisor_admin
                        )
                    )

                    # -----------------------------------------
                    # Normalizar campos
                    # -----------------------------------------

                    estado_supervisor_admin[
                        "supervisor"
                    ] = (
                        estado_supervisor_admin[
                            "supervisor"
                        ]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    estado_supervisor_admin = (
                        estado_supervisor_admin[
                            estado_supervisor_admin[
                                "supervisor"
                            ] != ""
                        ]
                        .copy()
                    )

                    if estado_supervisor_admin.empty:

                        st.info(
                            "No existen supervisores asignados "
                            "en la planificación seleccionada."
                        )

                    else:

                        ahora_supervisor_admin = (
                            pd.Timestamp.now(tz="America/Lima").tz_localize(None)
                        )

                        inicio_supervisor_admin = (
                            pd.to_datetime(
                                estado_supervisor_admin[
                                    "inicio_plan"
                                ],
                                errors="coerce"
                            )
                        )

                        fin_supervisor_admin = (
                            pd.to_datetime(
                                estado_supervisor_admin[
                                    "fin_plan"
                                ],
                                errors="coerce"
                            )
                        )

                        real_supervisor_admin = (
                            pd.to_numeric(
                                estado_supervisor_admin[
                                    "avance_real"
                                ],
                                errors="coerce"
                            )
                            .fillna(0)
                            .clip(0, 100)
                        )

                        # -----------------------------------------
                        # Plan esperado actual por actividad
                        # -----------------------------------------

                        planes_supervisor_admin = []

                        for (
                            fecha_inicio_sup,
                            fecha_fin_sup
                        ) in zip(
                            inicio_supervisor_admin,
                            fin_supervisor_admin
                        ):

                            if (
                                pd.isna(fecha_inicio_sup)
                                or pd.isna(fecha_fin_sup)
                            ):
                                planes_supervisor_admin.append(
                                    0.0
                                )
                                continue

                            if (
                                fecha_fin_sup
                                <= fecha_inicio_sup
                            ):
                                fecha_fin_sup = (
                                    fecha_inicio_sup
                                    + pd.Timedelta(minutes=1)
                                )

                            if (
                                ahora_supervisor_admin
                                <= fecha_inicio_sup
                            ):
                                plan_sup = 0.0

                            elif (
                                ahora_supervisor_admin
                                >= fecha_fin_sup
                            ):
                                plan_sup = 100.0

                            else:

                                duracion_sup = (
                                    fecha_fin_sup
                                    - fecha_inicio_sup
                                ).total_seconds()

                                transcurrido_sup = (
                                    ahora_supervisor_admin
                                    - fecha_inicio_sup
                                ).total_seconds()

                                plan_sup = (
                                    transcurrido_sup
                                    / duracion_sup
                                    * 100.0
                                    if duracion_sup > 0
                                    else 100.0
                                )

                            planes_supervisor_admin.append(
                                max(
                                    0.0,
                                    min(
                                        100.0,
                                        float(plan_sup)
                                    )
                                )
                            )

                        estado_supervisor_admin[
                            "PLAN ACTUAL (%)"
                        ] = planes_supervisor_admin

                        estado_supervisor_admin[
                            "REAL ACTUAL (%)"
                        ] = real_supervisor_admin

                        estado_supervisor_admin[
                            "DESVIACIÓN (pp)"
                        ] = (
                            estado_supervisor_admin[
                                "REAL ACTUAL (%)"
                            ]
                            - estado_supervisor_admin[
                                "PLAN ACTUAL (%)"
                            ]
                        ).round(1)

                        # -----------------------------------------
                        # Disciplina de reporte
                        # -----------------------------------------

                        if (
                            "fecha_registro"
                            in estado_supervisor_admin.columns
                        ):

                            fechas_registro_sup = (
                                pd.to_datetime(
                                    estado_supervisor_admin[
                                        "fecha_registro"
                                    ],
                                    errors="coerce",
                                    utc=True
                                )
                            )

                            estado_supervisor_admin[
                                "_fecha_registro_lima"
                            ] = (
                                fechas_registro_sup
                                .dt.tz_convert(
                                    "America/Lima"
                                )
                            )

                        else:

                            estado_supervisor_admin[
                                "_fecha_registro_lima"
                            ] = pd.NaT

                        # Actividad exigible:
                        # ya llegó su inicio plan y aún no culmina.
                        estado_supervisor_admin[
                            "_exigible"
                        ] = (
                            inicio_supervisor_admin.notna()
                            & (
                                inicio_supervisor_admin
                                <= ahora_supervisor_admin
                            )
                            & (
                                estado_supervisor_admin[
                                    "REAL ACTUAL (%)"
                                ] < 100
                            )
                        )

                        # Sin reporte:
                        # actividad exigible sin ningún avance registrado.
                        estado_supervisor_admin[
                            "_sin_reporte"
                        ] = (
                            estado_supervisor_admin[
                                "_exigible"
                            ]
                            & estado_supervisor_admin[
                                "_fecha_registro_lima"
                            ].isna()
                        )

                        # Vencida:
                        # fin plan superado y avance < 100%.
                        estado_supervisor_admin[
                            "_vencida"
                        ] = (
                            fin_supervisor_admin.notna()
                            & (
                                fin_supervisor_admin
                                < ahora_supervisor_admin
                            )
                            & (
                                estado_supervisor_admin[
                                    "REAL ACTUAL (%)"
                                ] < 100
                            )
                        )

                        # Atrasada:
                        # desviación mayor a 10 pp o actividad vencida.
                        estado_supervisor_admin[
                            "_atrasada"
                        ] = (
                            (
                                estado_supervisor_admin[
                                    "DESVIACIÓN (pp)"
                                ] < -10
                            )
                            | estado_supervisor_admin[
                                "_vencida"
                            ]
                        )

                        # -----------------------------------------
                        # Consolidado por Supervisor + Área
                        # -----------------------------------------

                        resumen_supervisores_admin = []

                        grupos_supervisor_admin = (
                            estado_supervisor_admin
                            .groupby(
                                [
                                    "Área",
                                    "supervisor"
                                ],
                                dropna=False
                            )
                        )

                        for (
                            area_sup,
                            supervisor_sup
                        ), grupo_sup in grupos_supervisor_admin:

                            total_actividades_sup = len(
                                grupo_sup
                            )

                            plan_promedio_sup = float(
                                grupo_sup[
                                    "PLAN ACTUAL (%)"
                                ].mean()
                            )

                            real_promedio_sup = float(
                                grupo_sup[
                                    "REAL ACTUAL (%)"
                                ].mean()
                            )

                            desviacion_sup = (
                                real_promedio_sup
                                - plan_promedio_sup
                            )

                            atrasadas_sup = int(
                                grupo_sup[
                                    "_atrasada"
                                ].sum()
                            )

                            vencidas_sup = int(
                                grupo_sup[
                                    "_vencida"
                                ].sum()
                            )

                            sin_reporte_sup = int(
                                grupo_sup[
                                    "_sin_reporte"
                                ].sum()
                            )

                            exigibles_sup = int(
                                grupo_sup[
                                    "_exigible"
                                ].sum()
                            )

                            reportadas_sup = max(
                                0,
                                exigibles_sup
                                - sin_reporte_sup
                            )

                            cumplimiento_reporte_sup = (
                                (
                                    reportadas_sup
                                    / exigibles_sup
                                    * 100
                                )
                                if exigibles_sup > 0
                                else None
                            )

                            fechas_validas_sup = (
                                grupo_sup[
                                    "_fecha_registro_lima"
                                ]
                                .dropna()
                            )

                            if fechas_validas_sup.empty:
                                ultimo_reporte_sup = (
                                    "Sin reporte"
                                )
                            else:
                                ultimo_reporte_sup = (
                                    fechas_validas_sup
                                    .max()
                                    .strftime(
                                        "%d/%m %H:%M"
                                    )
                                )

                            # ---------------------------------
                            # Estado gerencial del supervisor
                            # ---------------------------------

                            if exigibles_sup == 0:
                                estado_gestion_sup = (
                                    "⚪ PROGRAMADO"
                                )

                            elif (
                                vencidas_sup > 0
                                or desviacion_sup < -20
                            ):
                                estado_gestion_sup = (
                                    "🔴 INTERVENCIÓN"
                                )

                            elif (
                                atrasadas_sup > 0
                                or desviacion_sup < -10
                            ):
                                estado_gestion_sup = (
                                    "🟠 RECUPERACIÓN"
                                )

                            elif (
                                sin_reporte_sup > 0
                                or desviacion_sup < -5
                            ):
                                estado_gestion_sup = (
                                    "🟡 SEGUIMIENTO"
                                )

                            else:
                                estado_gestion_sup = (
                                    "🟢 EN LÍNEA"
                                )

                            resumen_supervisores_admin.append({
                                "Estado":
                                    estado_gestion_sup,
                                "Área":
                                    area_sup,
                                "Supervisor":
                                    supervisor_sup,
                                "Actividades":
                                    total_actividades_sup,
                                "Plan (%)":
                                    round(
                                        plan_promedio_sup,
                                        1
                                    ),
                                "Real (%)":
                                    round(
                                        real_promedio_sup,
                                        1
                                    ),
                                "Desv. (pp)":
                                    round(
                                        desviacion_sup,
                                        1
                                    ),
                                "Atrasadas":
                                    atrasadas_sup,
                                "Vencidas":
                                    vencidas_sup,
                                "Sin reporte":
                                    sin_reporte_sup,
                                "Reporte (%)":
                                    (
                                        round(
                                            cumplimiento_reporte_sup,
                                            0
                                        )
                                        if cumplimiento_reporte_sup
                                        is not None
                                        else None
                                    ),
                                "Último reporte":
                                    ultimo_reporte_sup
                            })

                        df_supervisores_admin = (
                            pd.DataFrame(
                                resumen_supervisores_admin
                            )
                        )

                        if df_supervisores_admin.empty:

                            st.info(
                                "No existe información suficiente "
                                "para evaluar supervisores."
                            )

                        else:

                            # ---------------------------------
                            # KPIs gerenciales compactos
                            # ---------------------------------

                            total_supervisores_admin = (
                                len(
                                    df_supervisores_admin
                                )
                            )

                            supervisores_alerta_admin = int(
                                (
                                    ~df_supervisores_admin[
                                        "Estado"
                                    ].isin(
                                        [
                                            "🟢 EN LÍNEA",
                                            "⚪ PROGRAMADO"
                                        ]
                                    )
                                ).sum()
                            )

                            total_atrasadas_admin = int(
                                df_supervisores_admin[
                                    "Atrasadas"
                                ].sum()
                            )

                            total_sin_reporte_admin = int(
                                df_supervisores_admin[
                                    "Sin reporte"
                                ].sum()
                            )

                            sup1, sup2, sup3, sup4 = (
                                st.columns(4)
                            )

                            with sup1:
                                st.metric(
                                    "Supervisores",
                                    total_supervisores_admin
                                )

                            with sup2:
                                st.metric(
                                    "Con alerta",
                                    supervisores_alerta_admin
                                )

                            with sup3:
                                st.metric(
                                    "Actividades atrasadas",
                                    total_atrasadas_admin
                                )

                            with sup4:
                                st.metric(
                                    "Actividades sin reporte",
                                    total_sin_reporte_admin
                                )

                            # ---------------------------------
                            # Orden gerencial:
                            # rojos -> naranjas -> amarillos -> verdes
                            # ---------------------------------

                            prioridad_estado_supervisor = {
                                "🔴 INTERVENCIÓN": 1,
                                "🟠 RECUPERACIÓN": 2,
                                "🟡 SEGUIMIENTO": 3,
                                "🟢 EN LÍNEA": 4,
                                "⚪ PROGRAMADO": 5
                            }

                            df_supervisores_admin[
                                "_orden"
                            ] = (
                                df_supervisores_admin[
                                    "Estado"
                                ]
                                .map(
                                    prioridad_estado_supervisor
                                )
                                .fillna(9)
                            )

                            df_supervisores_admin = (
                                df_supervisores_admin
                                .sort_values(
                                    [
                                        "_orden",
                                        "Desv. (pp)",
                                        "Supervisor"
                                    ],
                                    ascending=[
                                        True,
                                        True,
                                        True
                                    ]
                                )
                                .drop(
                                    columns=["_orden"]
                                )
                            )

                            st.dataframe(
                                df_supervisores_admin,
                                use_container_width=True,
                                hide_index=True,
                                height=min(
                                    460,
                                    42
                                    + (
                                        len(
                                            df_supervisores_admin
                                        )
                                        * 35
                                    )
                                ),
                                column_config={
                                    "Plan (%)":
                                        st.column_config.NumberColumn(
                                            "Plan (%)",
                                            format="%.1f%%"
                                        ),
                                    "Real (%)":
                                        st.column_config.NumberColumn(
                                            "Real (%)",
                                            format="%.1f%%"
                                        ),
                                    "Desv. (pp)":
                                        st.column_config.NumberColumn(
                                            "Desv. (pp)",
                                            format="%.1f"
                                        ),
                                    "Reporte (%)":
                                        st.column_config.NumberColumn(
                                            "Reporte (%)",
                                            format="%.0f%%"
                                        )
                                }
                            )

                            st.caption(
                                "Criterio: el % de reporte comienza a medirse "
                                "recién cuando llega la hora de inicio planificada "
                                "de al menos una actividad del supervisor. "
                                "Antes de ese momento el estado es PROGRAMADO y "
                                "el % de reporte queda sin valor. "
                                "'Sin reporte' solo considera actividades cuyo "
                                "inicio plan ya ocurrió y que aún no tienen ningún "
                                "avance registrado. 'Atrasadas' considera "
                                "desviación menor a -10 pp o actividades vencidas "
                                "sin culminar."
                            )



                st.divider()

                # =========================================
                # 9. CENTRO DE CONTROL OPERATIVO
                # =========================================

                if area_id_seleccionada_admin is None:

                    st.subheader(
                        "Centro de Control Operativo - Todas las áreas"
                    )

                    st.caption(
                        "Detalle consolidado de todas las actividades. "
                        "Puede filtrar por área, OT, estado, supervisor "
                        "y especialidad sin salir de la sesión ADMIN."
                    )

                else:

                    st.subheader(
                        f"Centro de Control Operativo - {vista_admin}"
                    )

                    st.caption(
                        "Detalle completo del área seleccionada: "
                        "OTs, actividades, avance, responsables, "
                        "fechas, HH, criticidad y última actualización."
                    )

                # Reconstruimos el estado completo para mostrar
                # también actividades culminadas y no iniciadas.
                detalle_operativo_admin = build_activity_status(
                    df_actividades_admin,
                    df_avances_admin
                )

                if detalle_operativo_admin.empty:

                    st.info(
                        "No existen actividades para mostrar "
                        "en la vista seleccionada."
                    )

                else:

                    # -----------------------------------------
                    # Incorporar OT, equipo y área
                    # -----------------------------------------

                    detalle_operativo_admin = (
                        detalle_operativo_admin
                        .merge(
                            df_ots_admin[
                                [
                                    "id",
                                    "ot",
                                    "area_id",
                                    "equipo"
                                ]
                            ],
                            left_on="ot_id",
                            right_on="id",
                            how="left",
                            suffixes=(
                                "",
                                "_ot"
                            )
                        )
                    )

                    mapa_area_detalle_admin = {
                        area["id"]: area["nombre"]
                        for area in areas_vista_admin
                    }

                    detalle_operativo_admin[
                        "Área"
                    ] = (
                        detalle_operativo_admin[
                            "area_id"
                        ].map(
                            mapa_area_detalle_admin
                        )
                    )

                    # -----------------------------------------
                    # Estado operativo
                    # -----------------------------------------

                    detalle_operativo_admin[
                        "ESTADO"
                    ] = np.where(
                        detalle_operativo_admin[
                            "avance_real"
                        ] >= 100,
                        "CULMINADA",
                        np.where(
                            detalle_operativo_admin[
                                "avance_real"
                            ] > 0,
                            "EN EJECUCIÓN",
                            "NO INICIADA"
                        )
                    )

                    if (
                        "critica"
                        not in detalle_operativo_admin.columns
                    ):
                        detalle_operativo_admin[
                            "critica"
                        ] = False

                    detalle_operativo_admin[
                        "critica"
                    ] = (
                        detalle_operativo_admin[
                            "critica"
                        ]
                        .fillna(False)
                    )

                    detalle_operativo_admin[
                        "CRITICIDAD"
                    ] = np.where(
                        detalle_operativo_admin[
                            "critica"
                        ],
                        "CRÍTICA",
                        "NORMAL"
                    )

                    # -----------------------------------------
                    # Última actualización en hora Perú
                    # -----------------------------------------

                    if (
                        "fecha_registro"
                        in detalle_operativo_admin.columns
                    ):

                        fecha_ultima_admin = pd.to_datetime(
                            detalle_operativo_admin[
                                "fecha_registro"
                            ],
                            errors="coerce",
                            utc=True
                        )

                        detalle_operativo_admin[
                            "ÚLTIMA ACTUALIZACIÓN"
                        ] = (
                            fecha_ultima_admin
                            .dt.tz_convert(
                                "America/Lima"
                            )
                            .dt.strftime(
                                "%d/%m/%Y %H:%M"
                            )
                        )

                    else:

                        detalle_operativo_admin[
                            "ÚLTIMA ACTUALIZACIÓN"
                        ] = ""

                    # -----------------------------------------
                    # Normalizar números
                    # -----------------------------------------

                    for columna_num_admin in [
                        "avance_real",
                        "personal",
                        "hh_plan"
                    ]:

                        if (
                            columna_num_admin
                            in detalle_operativo_admin.columns
                        ):

                            detalle_operativo_admin[
                                columna_num_admin
                            ] = pd.to_numeric(
                                detalle_operativo_admin[
                                    columna_num_admin
                                ],
                                errors="coerce"
                            ).fillna(0)


                    # -----------------------------------------
                    # SEMÁFOROS Y ALERTAS DE ATRASO
                    # -----------------------------------------

                    ahora_admin = pd.Timestamp.now(tz="America/Lima").tz_localize(None)

                    inicio_admin = pd.to_datetime(
                        detalle_operativo_admin.get(
                            "inicio_plan"
                        ),
                        errors="coerce"
                    )

                    fin_admin = pd.to_datetime(
                        detalle_operativo_admin.get(
                            "fin_plan"
                        ),
                        errors="coerce"
                    )

                    avance_real_admin = pd.to_numeric(
                        detalle_operativo_admin.get(
                            "avance_real",
                            0
                        ),
                        errors="coerce"
                    ).fillna(0)

                    avance_plan_admin = []

                    for fecha_inicio_admin, fecha_fin_admin in zip(
                        inicio_admin,
                        fin_admin
                    ):

                        if (
                            pd.isna(fecha_inicio_admin)
                            or pd.isna(fecha_fin_admin)
                        ):
                            avance_plan_admin.append(0.0)
                            continue

                        if (
                            fecha_fin_admin
                            <= fecha_inicio_admin
                        ):
                            fecha_fin_admin = (
                                fecha_inicio_admin
                                + pd.Timedelta(minutes=1)
                            )

                        if ahora_admin <= fecha_inicio_admin:

                            plan_actividad_admin = 0.0

                        elif ahora_admin >= fecha_fin_admin:

                            plan_actividad_admin = 100.0

                        else:

                            duracion_admin = (
                                fecha_fin_admin
                                - fecha_inicio_admin
                            ).total_seconds()

                            transcurrido_admin = (
                                ahora_admin
                                - fecha_inicio_admin
                            ).total_seconds()

                            plan_actividad_admin = (
                                (
                                    transcurrido_admin
                                    / duracion_admin
                                )
                                * 100
                                if duracion_admin > 0
                                else 100.0
                            )

                        avance_plan_admin.append(
                            max(
                                0.0,
                                min(
                                    100.0,
                                    float(plan_actividad_admin)
                                )
                            )
                        )

                    detalle_operativo_admin[
                        "PLAN ACTUAL (%)"
                    ] = avance_plan_admin

                    detalle_operativo_admin[
                        "DESVIACIÓN (pp)"
                    ] = (
                        avance_real_admin
                        - detalle_operativo_admin[
                            "PLAN ACTUAL (%)"
                        ]
                    ).round(1)

                    def clasificar_alerta_admin(fila):
                        """
                        Semaforización PDP:
                        - Verde: desviación >= -5 pp
                        - Amarillo: entre -5 y -10 pp
                        - Naranja: entre -10 y -20 pp
                        - Rojo: desviación < -20 pp
                        - Vencida: fin_plan < ahora y avance < 100%

                        Actividades críticas:
                        - Verde: desviación >= -5 pp
                        - Naranja: entre -5 y -10 pp
                        - Rojo: desviación < -10 pp
                        """

                        real = float(
                            fila.get("avance_real", 0) or 0
                        )

                        plan = float(
                            fila.get("PLAN ACTUAL (%)", 0) or 0
                        )

                        critica = bool(
                            fila.get("critica", False)
                        )

                        inicio = fila.get("inicio_plan")
                        fin = fila.get("fin_plan")

                        desviacion = real - plan

                        # -------------------------------------
                        # 1. CULMINADA
                        # -------------------------------------

                        if real >= 100:
                            return {
                                "semaforo": "🟢",
                                "nivel": "VERDE",
                                "alerta": "Culminada",
                                "accion": "Sin acción requerida",
                                "prioridad": 90
                            }

                        # -------------------------------------
                        # 2. ACTIVIDAD VENCIDA
                        # -------------------------------------

                        if (
                            pd.notna(fin)
                            and ahora_admin > pd.Timestamp(fin)
                            and real < 100
                        ):
                            return {
                                "semaforo": "🔴",
                                "nivel": "ROJO",
                                "alerta": (
                                    "Crítica vencida"
                                    if critica
                                    else "Vencida"
                                ),
                                "accion": (
                                    "Escalar y definir recuperación inmediata"
                                ),
                                "prioridad": 1 if critica else 2
                            }

                        # -------------------------------------
                        # 3. AÚN NO DEBE INICIAR
                        # -------------------------------------

                        if (
                            pd.notna(inicio)
                            and ahora_admin < pd.Timestamp(inicio)
                        ):
                            return {
                                "semaforo": "⚪",
                                "nivel": "PROGRAMADA",
                                "alerta": (
                                    "Crítica por iniciar"
                                    if critica
                                    else "Por iniciar"
                                ),
                                "accion": (
                                    "Verificar recursos y liberación"
                                    if critica
                                    else "Seguimiento según programa"
                                ),
                                "prioridad": 80
                            }

                        # -------------------------------------
                        # 4. REGLA ESPECIAL: CRÍTICAS
                        # -------------------------------------

                        if critica:

                            if desviacion < -10:
                                return {
                                    "semaforo": "🔴",
                                    "nivel": "ROJO",
                                    "alerta": "Crítica atrasada",
                                    "accion": (
                                        "Escalar y definir recuperación inmediata"
                                    ),
                                    "prioridad": 3
                                }

                            if desviacion < -5:
                                return {
                                    "semaforo": "🟠",
                                    "nivel": "NARANJA",
                                    "alerta": "Crítica en riesgo",
                                    "accion": (
                                        "Aplicar plan de recuperación"
                                    ),
                                    "prioridad": 5
                                }

                            return {
                                "semaforo": "🟢",
                                "nivel": "VERDE",
                                "alerta": "Crítica en línea",
                                "accion": (
                                    "Mantener seguimiento cercano"
                                ),
                                "prioridad": 30
                            }

                        # -------------------------------------
                        # 5. ACTIVIDAD NORMAL
                        # -------------------------------------

                        if desviacion < -20:
                            return {
                                "semaforo": "🔴",
                                "nivel": "ROJO",
                                "alerta": "Atraso crítico",
                                "accion": (
                                    "Intervención inmediata / reprogramar recursos"
                                ),
                                "prioridad": 4
                            }

                        if desviacion < -10:
                            return {
                                "semaforo": "🟠",
                                "nivel": "NARANJA",
                                "alerta": "Atrasada",
                                "accion": (
                                    "Definir plan de recuperación"
                                ),
                                "prioridad": 6
                            }

                        if desviacion < -5:
                            return {
                                "semaforo": "🟡",
                                "nivel": "AMARILLO",
                                "alerta": "En riesgo",
                                "accion": (
                                    "Seguimiento del supervisor"
                                ),
                                "prioridad": 10
                            }

                        return {
                            "semaforo": "🟢",
                            "nivel": "VERDE",
                            "alerta": "En línea",
                            "accion": "Sin acción requerida",
                            "prioridad": 40
                        }


                    clasificacion_admin = (
                        detalle_operativo_admin
                        .apply(
                            clasificar_alerta_admin,
                            axis=1
                        )
                    )

                    detalle_operativo_admin[
                        "SEMÁFORO"
                    ] = clasificacion_admin.map(
                        lambda item: item["semaforo"]
                    )

                    detalle_operativo_admin[
                        "NIVEL"
                    ] = clasificacion_admin.map(
                        lambda item: item["nivel"]
                    )

                    detalle_operativo_admin[
                        "ALERTA"
                    ] = clasificacion_admin.map(
                        lambda item: item["alerta"]
                    )

                    detalle_operativo_admin[
                        "ACCIÓN REQUERIDA"
                    ] = clasificacion_admin.map(
                        lambda item: item["accion"]
                    )

                    detalle_operativo_admin[
                        "_prioridad_alerta"
                    ] = clasificacion_admin.map(
                        lambda item: item["prioridad"]
                    )

                    # -----------------------------------------
                    # RESUMEN EJECUTIVO DE SEMÁFOROS
                    # -----------------------------------------

                    verdes_admin = int(
                        (
                            detalle_operativo_admin[
                                "NIVEL"
                            ]
                            == "VERDE"
                        ).sum()
                    )

                    amarillos_admin = int(
                        (
                            detalle_operativo_admin[
                                "NIVEL"
                            ]
                            == "AMARILLO"
                        ).sum()
                    )

                    naranjas_admin = int(
                        (
                            detalle_operativo_admin[
                                "NIVEL"
                            ]
                            == "NARANJA"
                        ).sum()
                    )

                    rojos_admin = int(
                        (
                            detalle_operativo_admin[
                                "NIVEL"
                            ]
                            == "ROJO"
                        ).sum()
                    )

                    sem1, sem2, sem3, sem4 = st.columns(4)

                    with sem1:
                        st.metric(
                            "🟢 En línea",
                            verdes_admin
                        )

                    with sem2:
                        st.metric(
                            "🟡 En riesgo",
                            amarillos_admin
                        )

                    with sem3:
                        st.metric(
                            "🟠 Recuperación",
                            naranjas_admin
                        )

                    with sem4:
                        st.metric(
                            "🔴 Intervención",
                            rojos_admin
                        )

                    alertas_prioritarias_admin = (
                        detalle_operativo_admin[
                            detalle_operativo_admin[
                                "NIVEL"
                            ].isin(
                                [
                                    "ROJO",
                                    "NARANJA",
                                    "AMARILLO"
                                ]
                            )
                        ]
                        .sort_values(
                            [
                                "_prioridad_alerta",
                                "avance_real"
                            ],
                            ascending=[
                                True,
                                True
                            ]
                        )
                        .copy()
                    )

                    if not alertas_prioritarias_admin.empty:

                        st.markdown(
                            "#### Situaciones que requieren atención"
                        )

                        st.caption(
                            "Prioridad automática según desviación "
                            "PLAN vs REAL, criticidad y vencimiento."
                        )

                        columnas_alertas_admin = [
                            "SEMÁFORO",
                            "ALERTA",
                            "Área",
                            "ot",
                            "equipo",
                            "codigo_actividad",
                            "descripcion",
                            "PLAN ACTUAL (%)",
                            "avance_real",
                            "DESVIACIÓN (pp)",
                            "supervisor",
                            "fin_plan",
                            "ACCIÓN REQUERIDA"
                        ]

                        columnas_alertas_admin = [
                            columna
                            for columna
                            in columnas_alertas_admin
                            if columna
                            in alertas_prioritarias_admin.columns
                        ]

                        tabla_alertas_admin = (
                            alertas_prioritarias_admin[
                                columnas_alertas_admin
                            ]
                            .head(20)
                            .copy()
                        )

                        tabla_alertas_admin = (
                            tabla_alertas_admin
                            .rename(
                                columns={
                                    "ot": "OT",
                                    "equipo": "EQUIPO",
                                    "codigo_actividad":
                                        "ACTIVIDAD",
                                    "descripcion":
                                        "DESCRIPCIÓN",
                                    "avance_real":
                                        "REAL (%)",
                                    "supervisor":
                                        "SUPERVISOR",
                                    "fin_plan":
                                        "FIN PLAN"
                                }
                            )
                        )

                        st.dataframe(
                            tabla_alertas_admin,
                            use_container_width=True,
                            hide_index=True,
                            height=360
                        )

                    # -----------------------------------------
                    # KPIs rápidos de la vista operativa
                    # -----------------------------------------

                    total_operativo_admin = len(
                        detalle_operativo_admin
                    )

                    ejecucion_operativo_admin = int(
                        (
                            detalle_operativo_admin[
                                "ESTADO"
                            ]
                            == "EN EJECUCIÓN"
                        ).sum()
                    )

                    culminadas_operativo_admin = int(
                        (
                            detalle_operativo_admin[
                                "ESTADO"
                            ]
                            == "CULMINADA"
                        ).sum()
                    )

                    no_iniciadas_operativo_admin = int(
                        (
                            detalle_operativo_admin[
                                "ESTADO"
                            ]
                            == "NO INICIADA"
                        ).sum()
                    )

                    criticas_operativo_admin = int(
                        detalle_operativo_admin[
                            "critica"
                        ].sum()
                    )

                    op1, op2, op3, op4, op5 = st.columns(
                        5
                    )

                    with op1:

                        st.metric(
                            "Total actividades",
                            total_operativo_admin
                        )

                    with op2:

                        st.metric(
                            "En ejecución",
                            ejecucion_operativo_admin
                        )

                    with op3:

                        st.metric(
                            "Culminadas",
                            culminadas_operativo_admin
                        )

                    with op4:

                        st.metric(
                            "No iniciadas",
                            no_iniciadas_operativo_admin
                        )

                    with op5:

                        st.metric(
                            "Críticas",
                            criticas_operativo_admin
                        )

                    st.markdown(
                        "#### Filtros operativos"
                    )

                    # -----------------------------------------
                    # FILTROS FILA 1
                    # -----------------------------------------

                    filtro1, filtro2, filtro3 = st.columns(
                        3
                    )

                    with filtro1:

                        if (
                            area_id_seleccionada_admin
                            is None
                        ):

                            opciones_area_operativa = (
                                ["TODAS"]
                                + sorted(
                                    detalle_operativo_admin[
                                        "Área"
                                    ]
                                    .dropna()
                                    .astype(str)
                                    .unique()
                                    .tolist()
                                )
                            )

                            filtro_area_operativa = (
                                st.selectbox(
                                    "Área",
                                    opciones_area_operativa,
                                    key=(
                                        "admin_operativo_area"
                                    )
                                )
                            )

                        else:

                            filtro_area_operativa = (
                                vista_admin
                            )

                    with filtro2:

                        opciones_ot_operativa = (
                            ["TODAS"]
                            + sorted(
                                detalle_operativo_admin[
                                    "ot"
                                ]
                                .dropna()
                                .astype(str)
                                .unique()
                                .tolist()
                            )
                        )

                        filtro_ot_operativa = st.selectbox(
                            "OT",
                            opciones_ot_operativa,
                            key="admin_operativo_ot"
                        )

                    with filtro3:

                        opciones_estado_operativo = [
                            "TODOS",
                            "NO INICIADA",
                            "EN EJECUCIÓN",
                            "CULMINADA"
                        ]

                        filtro_estado_operativo = (
                            st.selectbox(
                                "Estado",
                                opciones_estado_operativo,
                                key=(
                                    "admin_operativo_estado"
                                )
                            )
                        )

                    # -----------------------------------------
                    # FILTROS FILA 2
                    # -----------------------------------------

                    filtro4, filtro5, filtro6 = st.columns(
                        3
                    )

                    with filtro4:

                        supervisores_operativos = (
                            ["TODOS"]
                            + sorted(
                                detalle_operativo_admin[
                                    "supervisor"
                                ]
                                .dropna()
                                .astype(str)
                                .loc[
                                    lambda serie:
                                    serie.str.strip()
                                    != ""
                                ]
                                .unique()
                                .tolist()
                            )
                            if (
                                "supervisor"
                                in detalle_operativo_admin.columns
                            )
                            else ["TODOS"]
                        )

                        filtro_supervisor_operativo = (
                            st.selectbox(
                                "Supervisor",
                                supervisores_operativos,
                                key=(
                                    "admin_operativo_supervisor"
                                )
                            )
                        )

                    with filtro5:

                        especialidades_operativas = (
                            ["TODAS"]
                            + sorted(
                                detalle_operativo_admin[
                                    "especialidad"
                                ]
                                .dropna()
                                .astype(str)
                                .loc[
                                    lambda serie:
                                    serie.str.strip()
                                    != ""
                                ]
                                .unique()
                                .tolist()
                            )
                            if (
                                "especialidad"
                                in detalle_operativo_admin.columns
                            )
                            else ["TODAS"]
                        )

                        filtro_especialidad_operativa = (
                            st.selectbox(
                                "Especialidad",
                                especialidades_operativas,
                                key=(
                                    "admin_operativo_especialidad"
                                )
                            )
                        )

                    with filtro6:

                        filtro_alerta_operativa = (
                            st.selectbox(
                                "Semáforo",
                                [
                                    "TODOS",
                                    "ROJO",
                                    "NARANJA",
                                    "AMARILLO",
                                    "VERDE",
                                    "PROGRAMADA"
                                ],
                                key=(
                                    "admin_operativo_alerta"
                                )
                            )
                        )

                    busqueda_operativa_admin = st.text_input(
                        "Buscar por OT, equipo, actividad, trabajo, operación o SSOMA",
                        placeholder=(
                            "Ejemplo: 7169908, SAG, ACT-009..."
                        ),
                        key="admin_operativo_busqueda"
                    )

                    # -----------------------------------------
                    # APLICAR FILTROS
                    # -----------------------------------------

                    detalle_filtrado_admin = (
                        detalle_operativo_admin.copy()
                    )

                    if (
                        area_id_seleccionada_admin
                        is None
                        and filtro_area_operativa
                        != "TODAS"
                    ):

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                detalle_filtrado_admin[
                                    "Área"
                                ].astype(str)
                                == filtro_area_operativa
                            ]
                        )

                    if filtro_ot_operativa != "TODAS":

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                detalle_filtrado_admin[
                                    "ot"
                                ].astype(str)
                                == filtro_ot_operativa
                            ]
                        )

                    if (
                        filtro_estado_operativo
                        != "TODOS"
                    ):

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                detalle_filtrado_admin[
                                    "ESTADO"
                                ]
                                == filtro_estado_operativo
                            ]
                        )

                    if (
                        filtro_supervisor_operativo
                        != "TODOS"
                        and "supervisor"
                        in detalle_filtrado_admin.columns
                    ):

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                detalle_filtrado_admin[
                                    "supervisor"
                                ].astype(str)
                                == filtro_supervisor_operativo
                            ]
                        )

                    if (
                        filtro_especialidad_operativa
                        != "TODAS"
                        and "especialidad"
                        in detalle_filtrado_admin.columns
                    ):

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                detalle_filtrado_admin[
                                    "especialidad"
                                ].astype(str)
                                == filtro_especialidad_operativa
                            ]
                        )

                    if (
                        filtro_alerta_operativa
                        != "TODOS"
                    ):

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                detalle_filtrado_admin[
                                    "NIVEL"
                                ]
                                == filtro_alerta_operativa
                            ]
                        )

                    if busqueda_operativa_admin.strip():

                        termino_operativo_admin = (
                            busqueda_operativa_admin
                            .strip()
                            .lower()
                        )

                        mascara_busqueda_admin = (
                            pd.Series(
                                False,
                                index=(
                                    detalle_filtrado_admin.index
                                )
                            )
                        )

                        for columna_busqueda_admin in [
                            "ot",
                            "equipo",
                            "codigo_actividad",
                            "descripcion",
                            "descripcion_trabajo",
                            "operacion",
                            "ssoma"
                        ]:

                            if (
                                columna_busqueda_admin
                                in detalle_filtrado_admin.columns
                            ):

                                mascara_busqueda_admin = (
                                    mascara_busqueda_admin
                                    |
                                    detalle_filtrado_admin[
                                        columna_busqueda_admin
                                    ]
                                    .fillna("")
                                    .astype(str)
                                    .str.lower()
                                    .str.contains(
                                        termino_operativo_admin,
                                        regex=False
                                    )
                                )

                        detalle_filtrado_admin = (
                            detalle_filtrado_admin[
                                mascara_busqueda_admin
                            ]
                        )

                    # -----------------------------------------
                    # RESULTADO FILTRADO
                    # -----------------------------------------

                    st.caption(
                        f"{len(detalle_filtrado_admin)} "
                        "actividad(es) encontradas con los "
                        "filtros seleccionados."
                    )

                    columnas_operativas_admin = [
                        "SEMÁFORO",
                        "ALERTA",
                        "Área",
                        "ot",
                        "equipo",
                        "codigo_actividad",
                        "descripcion_trabajo",
                        "operacion",
                        "ssoma",
                        "descripcion",
                        "ESTADO",
                        "PLAN ACTUAL (%)",
                        "avance_real",
                        "DESVIACIÓN (pp)",
                        "CRITICIDAD",
                        "supervisor",
                        "especialidad",
                        "grupo",
                        "inicio_plan",
                        "fin_plan",
                        "personal",
                        "hh_plan",
                        "ÚLTIMA ACTUALIZACIÓN",
                        "ACCIÓN REQUERIDA",
                        "descripcion_avance",
                        "observaciones"
                    ]

                    columnas_operativas_admin = [
                        columna
                        for columna
                        in columnas_operativas_admin
                        if columna
                        in detalle_filtrado_admin.columns
                    ]

                    detalle_filtrado_admin = (
                        detalle_filtrado_admin
                        .sort_values(
                            [
                                "_prioridad_alerta",
                                "avance_real"
                            ],
                            ascending=[
                                True,
                                True
                            ]
                        )
                    )

                    tabla_operativa_admin = (
                        detalle_filtrado_admin[
                            columnas_operativas_admin
                        ]
                        .copy()
                    )

                    tabla_operativa_admin = (
                        tabla_operativa_admin
                        .rename(
                            columns={
                                "ot": "OT",
                                "equipo": "EQUIPO",
                                "codigo_actividad":
                                    "ACTIVIDAD",
                                "descripcion_trabajo":
                                    "DESCRIPCIÓN TRABAJO",
                                "operacion":
                                    "OPERACIÓN",
                                "ssoma":
                                    "SSOMA",
                                "descripcion":
                                    "DESCRIPCIÓN",
                                "avance_real":
                                    "AVANCE (%)",
                                "supervisor":
                                    "SUPERVISOR",
                                "especialidad":
                                    "ESPECIALIDAD",
                                "grupo":
                                    "GRUPO",
                                "inicio_plan":
                                    "INICIO PLAN",
                                "fin_plan":
                                    "FIN PLAN",
                                "personal":
                                    "PERSONAL",
                                "hh_plan":
                                    "HH PLAN",
                                "descripcion_avance":
                                    "ÚLTIMO AVANCE",
                                "observaciones":
                                    "OBSERVACIONES"
                            }
                        )
                    )

                    if "AVANCE (%)" in (
                        tabla_operativa_admin.columns
                    ):

                        tabla_operativa_admin[
                            "AVANCE (%)"
                        ] = (
                            tabla_operativa_admin[
                                "AVANCE (%)"
                            ]
                            .round(1)
                        )

                    if "HH PLAN" in (
                        tabla_operativa_admin.columns
                    ):

                        tabla_operativa_admin[
                            "HH PLAN"
                        ] = (
                            tabla_operativa_admin[
                                "HH PLAN"
                            ]
                            .round(0)
                        )

                    st.dataframe(
                        tabla_operativa_admin,
                        use_container_width=True,
                        hide_index=True,
                        height=600
                    )

                    # -----------------------------------------
                    # DETALLE RÁPIDO DE UNA ACTIVIDAD
                    # -----------------------------------------

                    if not detalle_filtrado_admin.empty:

                        st.markdown(
                            "#### Detalle rápido de actividad"
                        )

                        opciones_actividad_admin = {}

                        for _, fila_admin in (
                            detalle_filtrado_admin.iterrows()
                        ):

                            etiqueta_admin = (
                                f"OT {fila_admin.get('ot', '')} | "
                                f"{fila_admin.get('codigo_actividad', '')} | "
                                f"{fila_admin.get('descripcion', '')}"
                            )

                            opciones_actividad_admin[
                                etiqueta_admin
                            ] = fila_admin

                        actividad_admin_texto = st.selectbox(
                            "Seleccionar actividad",
                            list(
                                opciones_actividad_admin.keys()
                            ),
                            key=(
                                "admin_operativo_actividad"
                            )
                        )

                        actividad_admin_detalle = (
                            opciones_actividad_admin[
                                actividad_admin_texto
                            ]
                        )

                        det1, det2, det3, det4 = st.columns(
                            4
                        )

                        with det1:

                            st.metric(
                                "Avance",
                                f"{float(actividad_admin_detalle.get('avance_real', 0)):.1f}%"
                            )

                        with det2:

                            st.metric(
                                "Estado",
                                actividad_admin_detalle.get(
                                    "ESTADO",
                                    ""
                                )
                            )

                        with det3:

                            st.metric(
                                "Personal",
                                int(
                                    float(
                                        actividad_admin_detalle.get(
                                            "personal",
                                            0
                                        )
                                        or 0
                                    )
                                )
                            )

                        with det4:

                            st.metric(
                                "HH plan",
                                f"{float(actividad_admin_detalle.get('hh_plan', 0) or 0):.0f}"
                            )

                        dta1, dta2 = st.columns(
                            2
                        )

                        with dta1:

                            st.write(
                                "**Supervisor:** "
                                f"{actividad_admin_detalle.get('supervisor') or '-'}"
                            )

                            st.write(
                                "**Especialidad:** "
                                f"{actividad_admin_detalle.get('especialidad') or '-'}"
                            )

                            st.write(
                                "**Grupo:** "
                                f"{actividad_admin_detalle.get('grupo') or '-'}"
                            )

                            st.write(
                                "**Criticidad:** "
                                f"{actividad_admin_detalle.get('CRITICIDAD') or '-'}"
                            )

                        with dta2:

                            st.write(
                                "**Inicio plan:** "
                                f"{actividad_admin_detalle.get('inicio_plan') or '-'}"
                            )

                            st.write(
                                "**Fin plan:** "
                                f"{actividad_admin_detalle.get('fin_plan') or '-'}"
                            )

                            st.write(
                                "**Última actualización:** "
                                f"{actividad_admin_detalle.get('ÚLTIMA ACTUALIZACIÓN') or 'Sin reporte'}"
                            )

                        ultimo_avance_admin = (
                            actividad_admin_detalle.get(
                                "descripcion_avance"
                            )
                            or ""
                        )

                        observaciones_admin = (
                            actividad_admin_detalle.get(
                                "observaciones"
                            )
                            or ""
                        )

                        if ultimo_avance_admin:

                            st.info(
                                "**Último avance reportado:** "
                                f"{ultimo_avance_admin}"
                            )

                        if observaciones_admin:

                            st.warning(
                                "**Observaciones / Restricciones:** "
                                f"{observaciones_admin}"
                            )


    # =====================================================
    # IMPORTAR PLANIFICACIÓN
    # =====================================================

    elif pagina_admin == "Importar planificación":

        mostrar_acceso_pagina(
            "Importar planificación",
            "Convierta y cargue el manpower de la parada en un solo flujo.",
            icono="⇧",
            contexto="ADMIN · PLANIFICACIÓN",
            badge="Excel → PDP"
        )

        st.info(
            "Puede subir directamente el MANPOWER ORIGINAL de Quellaveco "
            "o un archivo que ya tenga las hojas OTs y Actividades. "
            "El aplicativo detectará el formato y realizará el tratamiento automáticamente."
        )

        resultado_areas = (
            supabase
            .table("areas")
            .select("id,codigo,nombre")
            .eq("activo", True)
            .order("id")
            .execute()
        )

        areas_disponibles = resultado_areas.data or []

        mapa_areas = {
            f"{area['codigo']} - {area['nombre']}": area
            for area in areas_disponibles
        }

        if not mapa_areas:

            st.error(
                "No existen áreas disponibles en la base de datos."
            )

        else:

            area_texto = st.selectbox(
                "Seleccione el área que desea reemplazar",
                list(mapa_areas.keys())
            )

            area_seleccionada = mapa_areas[area_texto]
            codigo_area_import = str(
                area_seleccionada.get("codigo") or ""
            ).strip().upper()

            st.warning(
                f"La carga reemplazará únicamente la planificación de "
                f"{area_seleccionada['nombre']}."
            )

            archivo = st.file_uploader(
                "Suba el Excel original de manpower o el formato PDP",
                type=["xlsx"],
                key=f"importacion_plan_{codigo_area_import}"
            )

            if archivo is not None:

                try:
                    archivo_bytes = archivo.getvalue()
                    libro = pd.ExcelFile(
                        io.BytesIO(archivo_bytes)
                    )
                    hojas_archivo = set(libro.sheet_names)

                    pendientes_import = pd.DataFrame()
                    resumen_tratamiento = None

                    # ==========================================
                    # DETECCIÓN AUTOMÁTICA DE FORMATO
                    # ==========================================
                    if {"OTs", "Actividades"}.issubset(hojas_archivo):
                        formato_detectado = "FORMATO PDP"

                        df_ots = pd.read_excel(
                            io.BytesIO(archivo_bytes),
                            sheet_name="OTs"
                        )

                        df_actividades = pd.read_excel(
                            io.BytesIO(archivo_bytes),
                            sheet_name="Actividades"
                        )

                    else:
                        configuracion_manpower = {
                            "ELECTRICIDAD": {
                                "hoja": "ELEC",
                                "empresa": "MAININ ELE",
                                "prefijo": "ELEC",
                                "nombre": "Electricidad"
                            },
                            "INSTRUMENTACION": {
                                "hoja": "INST",
                                "empresa": "MAININ INS",
                                "prefijo": "INST",
                                "nombre": "Instrumentación"
                            }
                        }

                        config = configuracion_manpower.get(
                            codigo_area_import
                        )

                        if not config:
                            raise ValueError(
                                "El área seleccionada no tiene una regla de conversión configurada."
                            )

                        if config["hoja"] not in hojas_archivo:
                            raise ValueError(
                                f"No se encontró la hoja {config['hoja']} para "
                                f"{area_seleccionada['nombre']}."
                            )

                        formato_detectado = "MANPOWER ORIGINAL"

                        conversion = convertir_hoja_manpower(
                            archivo_bytes=archivo_bytes,
                            hoja_fuente=config["hoja"],
                            empresa_objetivo=config["empresa"],
                            prefijo_actividad=config["prefijo"],
                            nombre_area=config["nombre"]
                        )

                        df_ots = conversion["ots"]
                        df_actividades = conversion["actividades"]
                        pendientes_import = conversion["pendientes"]
                        resumen_tratamiento = conversion["resumen"]

                    st.success(
                        f"Formato detectado: {formato_detectado}. "
                        f"Se prepararon {len(df_ots)} OTs y "
                        f"{len(df_actividades)} actividades."
                    )

                    if resumen_tratamiento:
                        r1, r2, r3, r4 = st.columns(4)

                        with r1:
                            st.metric(
                                "Filas MAININ",
                                resumen_tratamiento["filas_mainin"]
                            )

                        with r2:
                            st.metric(
                                "OTs",
                                resumen_tratamiento["ots"]
                            )

                        with r3:
                            st.metric(
                                "Actividades",
                                resumen_tratamiento["actividades"]
                            )

                        with r4:
                            st.metric(
                                "Excluidas",
                                resumen_tratamiento["excluidas"]
                            )

                        st.caption(
                            f"HH completadas automáticamente: "
                            f"{resumen_tratamiento['hh_completadas']} · "
                            f"Inicio: {resumen_tratamiento['inicio']} · "
                            f"Fin: {resumen_tratamiento['fin']}"
                        )

                    st.markdown("#### Vista previa de OTs")
                    st.dataframe(
                        df_ots.head(10),
                        use_container_width=True,
                        hide_index=True
                    )

                    st.markdown("#### Vista previa de actividades")

                    columnas_preview = [
                        "ot",
                        "codigo_actividad",
                        "descripcion_trabajo",
                        "operacion",
                        "ssoma",
                        "supervisor",
                        "especialidad",
                        "grupo",
                        "inicio_plan",
                        "fin_plan",
                        "personal",
                        "duracion_h",
                        "hh_plan"
                    ]

                    columnas_preview = [
                        columna
                        for columna in columnas_preview
                        if columna in df_actividades.columns
                    ]

                    if columnas_preview:
                        st.dataframe(
                            df_actividades[columnas_preview].head(20),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.dataframe(
                            df_actividades.head(20),
                            use_container_width=True,
                            hide_index=True
                        )

                    if not pendientes_import.empty:
                        st.warning(
                            f"Se excluyeron {len(pendientes_import)} fila(s) "
                            "por información obligatoria incompleta."
                        )
                        with st.expander("Ver filas excluidas"):
                            st.dataframe(
                                pendientes_import,
                                use_container_width=True,
                                hide_index=True
                            )

                    st.divider()

                    confirmar = st.checkbox(
                        f"Confirmo que deseo reemplazar la planificación de "
                        f"{area_seleccionada['nombre']}."
                    )

                    texto_confirmacion = st.text_input(
                        "Para confirmar escriba exactamente: REEMPLAZAR"
                    )

                    puede_importar = (
                        confirmar
                        and texto_confirmacion.strip().upper() == "REEMPLAZAR"
                    )

                    if st.button(
                        "REEMPLAZAR PLANIFICACIÓN DEL ÁREA",
                        type="primary",
                        use_container_width=True,
                        disabled=not puede_importar
                    ):

                        try:
                            area_id = area_seleccionada["id"]

                            progreso = st.progress(
                                5,
                                text="Preparando información..."
                            )

                            # ==========================================
                            # VALIDAR COLUMNAS BASE
                            # ==========================================
                            columnas_ots = {
                                "ot",
                                "equipo",
                                "descripcion"
                            }

                            columnas_actividades = {
                                "ot",
                                "codigo_actividad",
                                "descripcion",
                                "supervisor",
                                "especialidad",
                                "grupo",
                                "peso",
                                "inicio_plan",
                                "fin_plan",
                                "seccion",
                                "personal",
                                "duracion_h",
                                "hh_plan"
                            }

                            faltantes_ots = (
                                columnas_ots - set(df_ots.columns)
                            )

                            faltantes_act = (
                                columnas_actividades
                                - set(df_actividades.columns)
                            )

                            if faltantes_ots:
                                raise ValueError(
                                    "Faltan columnas en OTs: "
                                    + ", ".join(sorted(faltantes_ots))
                                )

                            if faltantes_act:
                                raise ValueError(
                                    "Faltan columnas en Actividades: "
                                    + ", ".join(sorted(faltantes_act))
                                )

                            progreso.progress(
                                15,
                                text="Limpiando OTs..."
                            )

                            # ==========================================
                            # PREPARAR OTs
                            # ==========================================
                            ots_limpias = []

                            for _, row in df_ots.iterrows():
                                ot = limpiar_texto(row.get("ot"))

                                if not ot:
                                    continue

                                ots_limpias.append({
                                    "ot": ot,
                                    "area_id": area_id,
                                    "equipo": limpiar_texto(
                                        row.get("equipo")
                                    ),
                                    "descripcion": limpiar_texto(
                                        row.get("descripcion")
                                    ),
                                    "activo": True
                                })

                            if not ots_limpias:
                                raise ValueError(
                                    "No existen OTs válidas para importar."
                                )

                            progreso.progress(
                                25,
                                text="Revisando planificación anterior..."
                            )

                            ots_actuales = (
                                supabase_admin
                                .table("ots")
                                .select("id")
                                .eq("area_id", area_id)
                                .execute()
                            ).data or []

                            ot_ids = [
                                x["id"]
                                for x in ots_actuales
                            ]

                            # ==========================================
                            # ELIMINAR PLANIFICACIÓN ANTERIOR DEL ÁREA
                            # ==========================================
                            if ot_ids:
                                actividades_actuales = (
                                    supabase_admin
                                    .table("actividades")
                                    .select("id,ot_id")
                                    .in_("ot_id", ot_ids)
                                    .execute()
                                ).data or []

                                actividad_ids = [
                                    x["id"]
                                    for x in actividades_actuales
                                ]

                                if actividad_ids:
                                    supabase_admin.table(
                                        "avances_actividad"
                                    ).delete().in_(
                                        "actividad_id",
                                        actividad_ids
                                    ).execute()

                                    supabase_admin.table(
                                        "actividades"
                                    ).delete().in_(
                                        "id",
                                        actividad_ids
                                    ).execute()

                                progreso.progress(
                                    40,
                                    text="Eliminando OTs anteriores..."
                                )

                                supabase_admin.table(
                                    "ots"
                                ).delete().eq(
                                    "area_id",
                                    area_id
                                ).execute()

                            # ==========================================
                            # INSERTAR OTs
                            # ==========================================
                            progreso.progress(
                                55,
                                text="Cargando OTs..."
                            )

                            (
                                supabase_admin
                                .table("ots")
                                .insert(ots_limpias)
                                .execute()
                            )

                            ots_nuevas = (
                                supabase_admin
                                .table("ots")
                                .select("id,ot")
                                .eq("area_id", area_id)
                                .execute()
                            ).data or []

                            mapa_ots = {
                                str(x["ot"]): x["id"]
                                for x in ots_nuevas
                            }

                            progreso.progress(
                                65,
                                text="Preparando actividades..."
                            )

                            # ==========================================
                            # PREPARAR ACTIVIDADES + NUEVOS CAMPOS
                            # ==========================================
                            actividades_limpias = []
                            ots_no_encontradas = []

                            for _, row in df_actividades.iterrows():
                                ot = limpiar_texto(
                                    row.get("ot")
                                )

                                codigo = limpiar_texto(
                                    row.get("codigo_actividad")
                                )

                                descripcion = limpiar_texto(
                                    row.get("descripcion")
                                )

                                if not ot or not codigo or not descripcion:
                                    continue

                                if ot not in mapa_ots:
                                    ots_no_encontradas.append(ot)
                                    continue

                                actividades_limpias.append({
                                    "ot_id": mapa_ots[ot],
                                    "codigo_actividad": codigo,
                                    "descripcion": descripcion,
                                    "descripcion_trabajo": limpiar_texto(
                                        row.get("descripcion_trabajo")
                                    ),
                                    "operacion": limpiar_texto(
                                        row.get("operacion")
                                    ),
                                    "ssoma": limpiar_texto(
                                        row.get("ssoma")
                                    ),
                                    "supervisor": limpiar_texto(
                                        row.get("supervisor")
                                    ),
                                    "especialidad": limpiar_texto(
                                        row.get("especialidad")
                                    ),
                                    "grupo": limpiar_texto(
                                        row.get("grupo")
                                    ),
                                    "peso": limpiar_numero(
                                        row.get("peso"),
                                        1
                                    ),
                                    "inicio_plan": limpiar_fecha(
                                        row.get("inicio_plan")
                                    ),
                                    "fin_plan": limpiar_fecha(
                                        row.get("fin_plan")
                                    ),
                                    "seccion": limpiar_texto(
                                        row.get("seccion")
                                    ),
                                    "personal": limpiar_entero(
                                        row.get("personal")
                                    ),
                                    "duracion_h": limpiar_numero(
                                        row.get("duracion_h")
                                    ),
                                    "hh_plan": limpiar_numero(
                                        row.get("hh_plan")
                                    ),
                                    "critica": False,
                                    "activo": True
                                })

                            if ots_no_encontradas:
                                raise ValueError(
                                    "Estas OTs aparecen en Actividades "
                                    "pero no en la hoja OTs: "
                                    + ", ".join(
                                        sorted(set(ots_no_encontradas))
                                    )
                                )

                            if not actividades_limpias:
                                raise ValueError(
                                    "No existen actividades válidas."
                                )

                            progreso.progress(
                                80,
                                text="Cargando actividades..."
                            )

                            batch_size = 200

                            for inicio_lote in range(
                                0,
                                len(actividades_limpias),
                                batch_size
                            ):
                                lote = actividades_limpias[
                                    inicio_lote:inicio_lote + batch_size
                                ]

                                (
                                    supabase_admin
                                    .table("actividades")
                                    .insert(lote)
                                    .execute()
                                )

                            progreso.progress(
                                100,
                                text="Importación completada."
                            )

                            st.success(
                                f"Planificación de "
                                f"{area_seleccionada['nombre']} "
                                f"actualizada correctamente: "
                                f"{len(ots_limpias)} OTs y "
                                f"{len(actividades_limpias)} actividades. "
                                "Se conservaron Descripción de trabajo, "
                                "Operación y SSOMA."
                            )

                            st.balloons()

                        except Exception as import_error:
                            st.error(
                                "No fue posible importar la planificación: "
                                f"{import_error}"
                            )

                except Exception as exc:
                    st.error(
                        f"No fue posible procesar el Excel: {exc}"
                    )


    # =====================================================
    # ADMINISTRAR OTs
    # =====================================================

    elif pagina_admin == "Administrar OTs":

        mostrar_acceso_pagina(
            "Administrar OTs",
            "Cree, revise y mantenga las órdenes de trabajo por área.",
            icono="▤",
            contexto="ADMIN · MAESTRO DE OTs",
            badge="Electricidad · Instrumentación"
        )

        st.info(
            "Desde aquí puede crear y revisar las OTs de Electricidad e Instrumentación."
        )


        # =========================================================
        # CARGAR ÁREAS ACTIVAS
        # =========================================================

        try:
            resultado_areas_ot = (
                supabase
                .table("areas")
                .select("id,codigo,nombre")
                .eq("activo", True)
                .order("id")
                .execute()
            )

            areas_ot = resultado_areas_ot.data or []

        except Exception as e:
            st.error(f"Error al cargar las áreas: {e}")
            areas_ot = []

        if not areas_ot:

            st.warning("No existen áreas activas configuradas.")

        else:

            # =====================================================
            # CREAR NUEVA OT
            # =====================================================

            st.markdown("### ➕ Crear nueva OT")

            opciones_area_ot = {
                f"{a['nombre']}": a["id"]
                for a in areas_ot
            }

            with st.form("form_crear_ot", clear_on_submit=True):

                area_seleccionada_ot = st.selectbox(
                    "Área",
                    list(opciones_area_ot.keys())
                )

                codigo_ot = st.text_input(
                    "Número / Código de OT",
                    placeholder="Ejemplo: OT-001"
                )

                equipo_ot = st.text_input(
                    "Equipo",
                    placeholder="Ejemplo: Tablero eléctrico"
                )

                descripcion_ot = st.text_area(
                    "Descripción",
                    placeholder="Descripción del trabajo"
                )

                activo_ot = st.checkbox(
                    "OT activa",
                    value=True
                )

                guardar_ot = st.form_submit_button(
                    "Guardar OT",
                    use_container_width=True
                )

            if guardar_ot:

                codigo_ot_limpio = codigo_ot.strip()

                if not codigo_ot_limpio:

                    st.warning("Debe ingresar el número o código de la OT.")

                else:

                    area_id_ot = opciones_area_ot[
                        area_seleccionada_ot
                    ]

                    try:

                        # Verificar duplicado
                        existente_ot = (
                            supabase
                            .table("ots")
                            .select("id")
                            .eq("area_id", area_id_ot)
                            .eq("ot", codigo_ot_limpio)
                            .execute()
                        )

                        if existente_ot.data:

                            st.warning(
                                "Esta OT ya existe en el área seleccionada."
                            )

                        else:

                            nueva_ot = {
                                "ot": codigo_ot_limpio,
                                "area_id": area_id_ot,
                                "equipo": equipo_ot.strip() or None,
                                "descripcion": descripcion_ot.strip() or None,
                                "activo": activo_ot
                            }

                            (
                                supabase
                                .table("ots")
                                .insert(nueva_ot)
                                .execute()
                            )

                            st.success(
                                f"OT {codigo_ot_limpio} creada correctamente."
                            )

                            st.rerun()

                    except Exception as e:

                        st.error(
                            f"No se pudo crear la OT: {e}"
                        )

            # =====================================================
            # LISTADO DE OTs
            # =====================================================

            st.divider()
            st.markdown("### 📋 OTs registradas")

            try:

                resultado_ots_admin = (
                    supabase
                    .table("ots")
                    .select(
                        "id,ot,equipo,descripcion,activo,area_id,"
                        "areas(codigo,nombre)"
                    )
                    .order("id", desc=True)
                    .execute()
                )

                ots_admin = resultado_ots_admin.data or []

                if not ots_admin:

                    st.info("Todavía no existen OTs registradas.")

                else:

                    filas_ots = []

                    for registro in ots_admin:

                        area_info = registro.get("areas") or {}

                        filas_ots.append({
                            "ID": registro.get("id"),
                            "Área": area_info.get("nombre", ""),
                            "OT": registro.get("ot", ""),
                            "Equipo": registro.get("equipo", ""),
                            "Descripción": registro.get("descripcion", ""),
                            "Activo": "Sí" if registro.get("activo") else "No"
                        })

                    df_ots_admin = pd.DataFrame(filas_ots)

                    st.dataframe(
                        df_ots_admin,
                        use_container_width=True,
                        hide_index=True
                    )

            except Exception as e:

                st.error(
                    f"No se pudieron cargar las OTs: {e}"
                )

    

    # =====================================================
    # REPORTES
    # =====================================================

    elif pagina_admin == "Reportes":

        mostrar_acceso_pagina(
            "Reportes gerenciales",
            "Consolide indicadores y genere entregables ejecutivos.",
            icono="↗",
            contexto="ADMIN · REPORTING",
            badge="PDF · Excel"
        )

        resultado_areas_reporte_admin = (
            supabase
            .table("areas")
            .select("id,codigo,nombre")
            .eq("activo", True)
            .order("id")
            .execute()
        )

        areas_reporte_admin = (
            resultado_areas_reporte_admin.data
            or []
        )

        if not areas_reporte_admin:

            st.warning(
                "No existen áreas activas configuradas."
            )

        else:

            opciones_reporte_admin = {
                "Todas las áreas": None
            }

            for area in areas_reporte_admin:
                opciones_reporte_admin[
                    area["nombre"]
                ] = area["id"]

            vista_reporte_admin = st.selectbox(
                "Seleccionar reporte",
                list(
                    opciones_reporte_admin.keys()
                ),
                key="selector_reporte_admin"
            )

            area_reporte_admin_id = (
                opciones_reporte_admin[
                    vista_reporte_admin
                ]
            )

            if area_reporte_admin_id is None:

                ids_area_reporte_admin = [
                    area["id"]
                    for area in areas_reporte_admin
                ]

                nombre_reporte_admin = (
                    "Todas las áreas"
                )

                codigo_reporte_admin = (
                    "consolidado"
                )

            else:

                ids_area_reporte_admin = [
                    area_reporte_admin_id
                ]

                area_obj_reporte_admin = next(
                    area
                    for area in areas_reporte_admin
                    if area["id"]
                    == area_reporte_admin_id
                )

                nombre_reporte_admin = (
                    area_obj_reporte_admin[
                        "nombre"
                    ]
                )

                codigo_reporte_admin = (
                    area_obj_reporte_admin[
                        "codigo"
                    ]
                )

            ots_reporte_admin = (
                supabase
                .table("ots")
                .select(
                    "id,ot,equipo,descripcion,activo,area_id"
                )
                .in_(
                    "area_id",
                    ids_area_reporte_admin
                )
                .eq(
                    "activo",
                    True
                )
                .execute()
            ).data or []

            if not ots_reporte_admin:

                st.warning(
                    "No existen OTs activas para "
                    "la vista seleccionada."
                )

            else:

                df_ots_reporte_admin = pd.DataFrame(
                    ots_reporte_admin
                )

                ids_ots_reporte_admin = [
                    ot["id"]
                    for ot in ots_reporte_admin
                ]

                actividades_reporte_admin = (
                    supabase
                    .table("actividades")
                    .select(
                        "id,ot_id,codigo_actividad,descripcion,"
                        "descripcion_trabajo,operacion,ssoma,"
                        "supervisor,especialidad,grupo,peso,"
                        "inicio_plan,fin_plan,seccion,personal,"
                        "duracion_h,hh_plan,critica,activo"
                    )
                    .in_(
                        "ot_id",
                        ids_ots_reporte_admin
                    )
                    .eq(
                        "activo",
                        True
                    )
                    .execute()
                ).data or []

                if not actividades_reporte_admin:

                    st.warning(
                        "No existen actividades para "
                        "la vista seleccionada."
                    )

                else:

                    df_actividades_reporte_admin = (
                        pd.DataFrame(
                            actividades_reporte_admin
                        )
                    )

                    ids_act_reporte_admin = (
                        df_actividades_reporte_admin[
                            "id"
                        ]
                        .dropna()
                        .tolist()
                    )

                    avances_reporte_admin = (
                        supabase
                        .table("avances_actividad")
                        .select(
                            "id,actividad_id,avance,"
                            "descripcion_avance,observaciones,"
                            "tipo_evidencia,critica,evidencias,"
                            "usuario,fecha_registro"
                        )
                        .in_(
                            "actividad_id",
                            ids_act_reporte_admin
                        )
                        .execute()
                    ).data or []

                    df_avances_reporte_admin = (
                        pd.DataFrame(
                            avances_reporte_admin
                        )
                    )

                    kpis_reporte_admin = compute_kpis(
                        df_actividades_reporte_admin,
                        df_avances_reporte_admin
                    )

                    ar1, ar2, ar3, ar4 = st.columns(
                        4
                    )

                    with ar1:
                        st.metric(
                            "OTs",
                            len(
                                df_ots_reporte_admin
                            )
                        )

                    with ar2:
                        st.metric(
                            "Actividades",
                            kpis_reporte_admin[
                                "actividades"
                            ]
                        )

                    with ar3:
                        st.metric(
                            "Avance general",
                            f"{kpis_reporte_admin['avance_general']:.1f}%"
                        )

                    with ar4:
                        st.metric(
                            "SPI",
                            f"{kpis_reporte_admin['spi']:.2f}"
                        )

                    st.divider()

                    mostrar_reportes_fotograficos_adicionales(
                        df_ots_reporte_admin,
                        df_actividades_reporte_admin,
                        df_avances_reporte_admin,
                        nombre_reporte_admin,
                        "admin"
                    )

                    st.divider()

                    # =====================================
                    # REPORTE POR SUPERVISOR - ADMIN
                    # =====================================
                    st.markdown(
                        "### Reporte por supervisor"
                    )

                    st.caption(
                        "Seleccione un supervisor de la vista "
                        "actual para revisar sus KPIs, actividades "
                        "y generar un PDF individual."
                    )

                    supervisores_admin_reporte = (
                        lista_supervisores_reporte(
                            df_actividades_reporte_admin
                        )
                    )

                    if not supervisores_admin_reporte:

                        st.info(
                            "No existen supervisores asignados "
                            "para la vista seleccionada."
                        )

                    else:

                        supervisor_admin_reporte = (
                            st.selectbox(
                                "Seleccionar supervisor",
                                supervisores_admin_reporte,
                                key=(
                                    "selector_supervisor_"
                                    "reporte_admin"
                                )
                            )
                        )

                        (
                            df_ots_sup_admin,
                            df_act_sup_admin,
                            df_av_sup_admin
                        ) = filtrar_reporte_supervisor(
                            df_ots_reporte_admin,
                            df_actividades_reporte_admin,
                            df_avances_reporte_admin,
                            supervisor_admin_reporte
                        )

                        kpis_sup_admin = compute_kpis(
                            df_act_sup_admin,
                            df_av_sup_admin
                        )

                        plan_sup_admin = float(
                            kpis_sup_admin.get(
                                "avance_plan",
                                0
                            ) or 0
                        )

                        real_sup_admin = float(
                            kpis_sup_admin.get(
                                "avance_general",
                                0
                            ) or 0
                        )

                        brecha_sup_admin = (
                            real_sup_admin
                            - plan_sup_admin
                        )

                        as1, as2, as3, as4 = (
                            st.columns(4)
                        )

                        with as1:
                            st.metric(
                                "OTs",
                                len(
                                    df_ots_sup_admin
                                )
                            )

                        with as2:
                            st.metric(
                                "Actividades",
                                int(
                                    kpis_sup_admin.get(
                                        "actividades",
                                        0
                                    ) or 0
                                )
                            )

                        with as3:
                            st.metric(
                                "Avance real",
                                f"{real_sup_admin:.1f}%",
                                delta=(
                                    f"{brecha_sup_admin:+.1f} pp"
                                )
                            )

                        with as4:
                            st.metric(
                                "SPI",
                                f"{float(kpis_sup_admin.get('spi', 0) or 0):.2f}"
                            )

                        estado_sup_admin = (
                            calcular_semaforo_pdf(
                                df_act_sup_admin,
                                df_av_sup_admin
                            )
                        )

                        if (
                            not estado_sup_admin.empty
                            and not df_ots_sup_admin.empty
                        ):

                            estado_sup_admin = (
                                estado_sup_admin
                                .merge(
                                    df_ots_sup_admin[
                                        [
                                            "id",
                                            "ot",
                                            "equipo"
                                        ]
                                    ].rename(
                                        columns={
                                            "id": "ot_id"
                                        }
                                    ),
                                    on="ot_id",
                                    how="left"
                                )
                            )

                            vista_sup_admin = (
                                estado_sup_admin[
                                    [
                                        "ot",
                                        "equipo",
                                        "grupo",
                                        "descripcion",
                                        "PLAN ACTUAL (%)",
                                        "avance_real",
                                        "DESVIACIÓN (pp)",
                                        "ALERTA"
                                    ]
                                ]
                                .rename(
                                    columns={
                                        "ot": "OT",
                                        "equipo": "EQUIPO",
                                        "grupo": "GRUPO",
                                        "descripcion": "DESCRIPCIÓN",
                                        "PLAN ACTUAL (%)": "PLAN (%)",
                                        "avance_real": "REAL (%)",
                                        "DESVIACIÓN (pp)": "BRECHA (pp)",
                                        "ALERTA": "ESTADO"
                                    }
                                )
                            )

                            st.dataframe(
                                vista_sup_admin,
                                use_container_width=True,
                                hide_index=True,
                                height=340
                            )

                        try:

                            pdf_sup_admin = (
                                construir_pdf_supervisor(
                                    df_ots_sup_admin,
                                    df_act_sup_admin,
                                    df_av_sup_admin,
                                    nombre_reporte_admin,
                                    supervisor_admin_reporte
                                )
                            )

                            archivo_sup_admin = (
                                str(
                                    supervisor_admin_reporte
                                )
                                .strip()
                                .lower()
                                .replace(
                                    " ",
                                    "_"
                                )
                            )

                            st.download_button(
                                "Descargar PDF del supervisor",
                                data=pdf_sup_admin,
                                file_name=(
                                    "PDP_Quellaveco_"
                                    f"{str(codigo_reporte_admin).lower()}_"
                                    f"{archivo_sup_admin}_"
                                    f"{datetime.now():%Y%m%d_%H%M}.pdf"
                                ),
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="descarga_pdf_supervisor_admin"
                            )

                        except Exception as exc:

                            st.error(
                                "No fue posible generar el "
                                "PDF del supervisor: "
                                f"{exc}"
                            )

                    st.divider()

                    st.markdown(
                        "### Informe ejecutivo para gerencia"
                    )

                    st.write(
                        "Incluye KPIs, Curva S PLAN vs REAL, "
                        "semáforo ejecutivo, foco de atención, "
                        "acciones requeridas, resumen operativo "
                        "y detalle por OT."
                    )

                    try:

                        pdf_admin_bytes = (
                            construir_pdf_ejecutivo_area(
                                df_ots_reporte_admin,
                                df_actividades_reporte_admin,
                                df_avances_reporte_admin,
                                nombre_reporte_admin
                            )
                        )

                        st.download_button(
                            "Descargar informe gerencial PDF",
                            data=pdf_admin_bytes,
                            file_name=(
                                "PDP_Quellaveco_"
                                f"{str(codigo_reporte_admin).lower()}_"
                                f"{datetime.now():%Y%m%d_%H%M}.pdf"
                            ),
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )

                    except Exception as exc:

                        st.error(
                            "No fue posible generar el "
                            f"reporte gerencial: {exc}"
                        )


else:

    # =====================================================
    # MENÚ DEL USUARIO POR ÁREA
    # =====================================================

    with st.sidebar:

        mostrar_etiqueta_navegacion("Workspace")

        opciones_menu = menu_por_rol(
            rol
        )

        if not opciones_menu:
            st.error(
                "Este usuario no tiene permisos "
                "de menú configurados."
            )
            st.stop()

        pagina = st.radio(
            "Menú",
            opciones_menu,
            format_func=etiqueta_menu,
            label_visibility="collapsed"
        )


    # =====================================================
    # OBTENER OTs DEL ÁREA DEL USUARIO
    # =====================================================

    resultado_ots = (
        supabase
        .table("ots")
        .select("id,ot,equipo,descripcion,activo,area_id")
        .eq("area_id", usuario["area_id"])
        .eq("activo", True)
        .execute()
    )

    ots_area = resultado_ots.data or []


    # =====================================================
    # DASHBOARD
    # =====================================================

    if pagina == "Dashboard":

        mostrar_acceso_pagina(
            f"Dashboard · {nombre_area}",
            "Estado operativo del área, curva S y desempeño de actividades.",
            icono="◫",
            contexto=f"{nombre_rol_sidebar} · CONTROL OPERATIVO",
            badge=nombre_area
        )

        # =================================================
        # 1. CARGAR ACTIVIDADES DEL ÁREA
        # =================================================

        ot_ids = [ot["id"] for ot in ots_area]

        if ot_ids:

            actividades_data = (
                supabase
                .table("actividades")
                .select(
                    "id,ot_id,codigo_actividad,descripcion,"
                    "descripcion_trabajo,operacion,ssoma,"
                    "supervisor,especialidad,grupo,peso,"
                    "inicio_plan,fin_plan,seccion,personal,"
                    "duracion_h,hh_plan,critica,activo"
                )
                .in_("ot_id", ot_ids)
                .eq("activo", True)
                .execute()
            ).data or []

        else:
            actividades_data = []

        df_ots = pd.DataFrame(ots_area)
        df_actividades = pd.DataFrame(actividades_data)

        # =================================================
        # 2. CARGAR AVANCES
        # =================================================

        if not df_actividades.empty:

            actividad_ids = (
                df_actividades["id"]
                .dropna()
                .tolist()
            )

            avances_data = (
                supabase
                .table("avances_actividad")
                .select(
                    "id,actividad_id,avance,"
                    "descripcion_avance,observaciones,"
                    "tipo_evidencia,critica,evidencias,"
                    "usuario,fecha_registro"
                )
                .in_("actividad_id", actividad_ids)
                .execute()
            ).data or []

        else:
            avances_data = []

        df_avances = pd.DataFrame(avances_data)

        # =================================================
        # 3. SI TODAVÍA NO HAY PLANIFICACIÓN
        # =================================================

        if df_actividades.empty:

            st.warning(
                "No existen actividades cargadas para esta área."
            )

        else:

            # =============================================
            # 4. PREPARAR DATOS
            # =============================================

            df_estado = build_activity_status(
                df_actividades,
                df_avances
            )

            kpis = compute_kpis(
                df_actividades,
                df_avances
            )

            curva_s = build_s_curve(
                df_actividades,
                df_avances
            )

            mostrar_corte_validado_cliente(
                df_actividades
            )

            # Incorporar información de OT y equipo
            if not df_ots.empty:

                datos_ot = (
                    df_ots[
                        [
                            "id",
                            "ot",
                            "equipo",
                            "descripcion"
                        ]
                    ]
                    .rename(
                        columns={
                            "id": "ot_id",
                            "descripcion": "descripcion_ot"
                        }
                    )
                )

                df_estado = df_estado.merge(
                    datos_ot,
                    on="ot_id",
                    how="left"
                )

            # =============================================
            # 5. ENCABEZADO
            # =============================================

            st.caption(
                f"Control operativo exclusivo de {nombre_area} · "
                f"{len(df_ots)} OTs · "
                f"{len(df_actividades)} actividades"
            )

            # =============================================
            # 6. KPIs PRINCIPALES
            # =============================================

            avance_real = float(
                kpis.get("avance_general", 0)
            )

            avance_plan = float(
                kpis.get("avance_plan", 0)
            )

            desviacion = (
                avance_real - avance_plan
            )

            spi = float(
                kpis.get("spi", 0)
            )

            hh_plan = float(
                kpis.get("hh_plan", 0)
            )

            hh_ganadas = float(
                kpis.get("hh_ganadas", 0)
            )

            # =========================================================
            # INDICADORES PRINCIPALES DEL DASHBOARD
            # =========================================================
            total_ots = len(ots_area)
            mostrar_kpis_operativos(kpis, total_ots)

            st.divider()

            # =============================================
            # 7. SEMÁFORO DEL PROYECTO
            # =============================================

            if avance_plan <= 0:

                st.info(
                    "La planificación aún no ha iniciado "
                    "o no existe un avance plan calculable."
                )

            elif spi >= 1:

                st.success(
                    f"🟢 EN LÍNEA / ADELANTADO · "
                    f"SPI {spi:.2f}"
                )

            elif spi >= 0.90:

                st.warning(
                    f"🟡 DESVIACIÓN CONTROLABLE · "
                    f"SPI {spi:.2f}"
                )

            else:

                st.error(
                    f"🔴 DESVIACIÓN CRÍTICA · "
                    f"SPI {spi:.2f}"
                )        

            st.divider()

            # =============================================
            # 8. CURVA S
            # =============================================

            mostrar_titulo_ejecutivo(
                "Curva S · Plan vs Real",
                (
                    "Valores por corte y línea vertical de tiempo real "
                    "para identificar el punto exacto de ejecución."
                ),
                "Seguimiento en vivo"
            )

            if curva_s.empty:

                st.info(
                    "No existen fechas suficientes para "
                    "construir la Curva S."
                )

            else:

                fig_s, info_curva_s = crear_curva_s_tiempo_real(
                    curva_s,
                    altura=490
                )

                mostrar_estado_curva_en_vivo(
                    info_curva_s
                )

                st.plotly_chart(
                    fig_s,
                    use_container_width=True,
                    config={
                        "displaylogo": False,
                        "displayModeBar": False,
                        "responsive": True
                    }
                )

            st.divider()

            # =============================================
            # 9. AVANCE POR OT
            # =============================================

            st.subheader("Avance por OT")

            if "ot" in df_estado.columns:

                # =========================================
                # FILTRO DE SUPERVISOR PARA AVANCE POR OT
                # =========================================
                if "supervisor" in df_estado.columns:

                    supervisores_ot = sorted(
                        {
                            str(valor or "").strip()
                            for valor in df_estado["supervisor"].tolist()
                            if str(valor or "").strip()
                        }
                    )

                    hay_sin_supervisor_ot = any(
                        not str(valor or "").strip()
                        for valor in df_estado["supervisor"].tolist()
                    )

                    opciones_supervisor_ot = ["TODOS"]

                    opciones_supervisor_ot.extend(
                        supervisores_ot
                    )

                    if hay_sin_supervisor_ot:
                        opciones_supervisor_ot.append(
                            "SIN SUPERVISOR"
                        )

                    filtro_supervisor_ot = st.selectbox(
                        "Filtrar avance por supervisor",
                        opciones_supervisor_ot,
                        key="filtro_supervisor_avance_ot",
                        help=(
                            "Permite revisar únicamente las OTs y actividades "
                            "asignadas al supervisor seleccionado."
                        )
                    )

                else:
                    filtro_supervisor_ot = "TODOS"

                df_estado_ot = df_estado.copy()

                if (
                    "supervisor" in df_estado_ot.columns
                    and filtro_supervisor_ot != "TODOS"
                ):

                    supervisor_normalizado = (
                        df_estado_ot["supervisor"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    if filtro_supervisor_ot == "SIN SUPERVISOR":

                        df_estado_ot = df_estado_ot[
                            supervisor_normalizado.eq("")
                        ].copy()

                    else:

                        df_estado_ot = df_estado_ot[
                            supervisor_normalizado.eq(
                                filtro_supervisor_ot
                            )
                        ].copy()

                if df_estado_ot.empty:

                    st.info(
                        "No existen OTs con actividades para "
                        "el supervisor seleccionado."
                    )

                else:

                    df_ot = (
                        df_estado_ot
                        .groupby(
                            ["ot", "equipo"],
                            dropna=False
                        )
                        .apply(
                            lambda grupo: pd.Series({
                                "Avance": weighted_progress(
                                    grupo
                                ),
                                "Actividades": len(grupo),
                                "Pendientes": int(
                                    (
                                        grupo["avance_real"] < 100
                                    ).sum()
                                )
                            })
                        )
                        .reset_index()
                    )

                    df_ot["OT / Equipo"] = (
                        df_ot["ot"].fillna("").astype(str)
                        + " - "
                        + df_ot["equipo"].fillna(
                            "Sin equipo"
                        ).astype(str)
                    )

                    df_ot = df_ot.sort_values(
                        "Avance",
                        ascending=True
                    )

                    if filtro_supervisor_ot != "TODOS":
                        st.caption(
                            f"Supervisor: {filtro_supervisor_ot} · "
                            f"{len(df_ot)} OT(s) · "
                            f"{len(df_estado_ot)} actividad(es)"
                        )

                    fig_ot = px.bar(
                        df_ot,
                        x="Avance",
                        y="OT / Equipo",
                        orientation="h",
                        text="Avance",
                        hover_data=["Actividades", "Pendientes"],
                        color_discrete_sequence=["#155EEF"]
                    )

                    fig_ot.update_traces(
                        texttemplate="%{text:.1f}%",
                        textposition="outside",
                        textfont=dict(size=12, color="#0B1F33"),
                        cliponaxis=False,
                        marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<br>Actividades: %{customdata[0]}<br>Pendientes: %{customdata[1]}<extra></extra>"
                    )

                    fig_ot.update_layout(
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#FFFFFF",
                        font=dict(color="#1F2937", size=13),
                        xaxis_title="Avance (%)",
                        yaxis_title="",
                        xaxis=dict(
                            range=[0, 105],
                            ticksuffix="%",
                            gridcolor="#E5EAF0",
                            linecolor="#98A2B3",
                            tickfont=dict(size=11, color="#344054")
                        ),
                        yaxis=dict(
                            gridcolor="rgba(0,0,0,0)",
                            linecolor="#D0D5DD",
                            tickfont=dict(size=11, color="#344054"),
                            automargin=True
                        ),
                        margin=dict(l=20, r=46, t=18, b=30),
                        height=max(
                            360,
                            min(1200, len(df_ot) * 42)
                        )
                    )

                    st.plotly_chart(
                        fig_ot,
                        use_container_width=True,
                        config={
                            "displaylogo": False,
                            "displayModeBar": False,
                            "responsive": True
                        }
                    )

            # =============================================
            # 10. ESTADO DE ACTIVIDADES
            # =============================================

            st.subheader("Estado de actividades")

            estado_resumen = pd.DataFrame({
                "Estado": [
                    "Culminadas",
                    "En ejecución",
                    "No iniciadas"
                ],
                "Cantidad": [
                    int(kpis.get("culminadas", 0)),
                    int(kpis.get("parciales", 0)),
                    int(kpis.get("no_iniciadas", 0))
                ]
            })

            fig_estado = px.bar(
                estado_resumen,
                x="Estado",
                y="Cantidad",
                text="Cantidad",
                color="Estado",
                color_discrete_map={
                    "Culminadas": "#079455",
                    "En ejecución": "#F79009",
                    "No iniciadas": "#D92D20"
                }
            )

            fig_estado.update_traces(
                textposition="outside",
                textfont=dict(size=12, color="#0B1F33"),
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<extra></extra>"
            )

            fig_estado.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#1F2937", size=13),
                yaxis_title="N.º de actividades",
                xaxis_title="",
                showlegend=False,
                yaxis=dict(
                    gridcolor="#E5EAF0",
                    linecolor="#98A2B3",
                    tickfont=dict(size=11, color="#344054")
                ),
                xaxis=dict(
                    linecolor="#98A2B3",
                    tickfont=dict(size=11, color="#344054")
                ),
                margin=dict(l=20, r=26, t=12, b=20),
                height=340
            )

            st.plotly_chart(
                fig_estado,
                use_container_width=True,
                config={"displaylogo": False, "displayModeBar": False, "responsive": True}
            )

            st.divider()

            # =============================================
            # 11. AVANCE POR ESPECIALIDAD
            # =============================================

            c_esp, c_sup = st.columns(2)

            with c_esp:

                st.subheader(
                    "Avance por especialidad"
                )

                if "especialidad" in df_estado.columns:

                    especialidad = (
                        df_estado
                        .groupby(
                            "especialidad",
                            dropna=False
                        )
                        .apply(
                            lambda grupo: pd.Series({
                                "Avance": weighted_progress(
                                    grupo
                                ),
                                "Actividades": len(grupo),
                                "Pendientes": int(
                                    (
                                        grupo["avance_real"]
                                        < 100
                                    ).sum()
                                )
                            })
                        )
                        .reset_index()
                    )

                    especialidad[
                        "especialidad"
                    ] = (
                        especialidad[
                            "especialidad"
                        ]
                        .fillna("SIN ESPECIALIDAD")
                    )

                    especialidad = (
                        especialidad
                        .sort_values(
                            "Avance",
                            ascending=True
                        )
                    )

                    fig_esp = px.bar(
                        especialidad,
                        x="Avance",
                        y="especialidad",
                        orientation="h",
                        text="Avance",
                        color_discrete_sequence=["#0EA5E9"]
                    )

                    fig_esp.update_traces(
                        texttemplate="%{text:.1f}%",
                        textposition="outside",
                        textfont=dict(size=12, color="#0B1F33"),
                        cliponaxis=False,
                        marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<extra></extra>"
                    )

                    fig_esp.update_layout(
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#FFFFFF",
                        font=dict(color="#1F2937", size=13),
                        xaxis_title="Avance (%)",
                        yaxis_title="",
                        xaxis=dict(
                            range=[0, 105],
                            ticksuffix="%",
                            gridcolor="#E5EAF0",
                            linecolor="#98A2B3",
                            tickfont=dict(size=11, color="#344054")
                        ),
                        yaxis=dict(
                            gridcolor="rgba(0,0,0,0)",
                            linecolor="#D0D5DD",
                            tickfont=dict(size=11, color="#344054"),
                            automargin=True
                        ),
                        margin=dict(l=18, r=44, t=12, b=24),
                        height=380
                    )

                    st.plotly_chart(
                        fig_esp,
                        use_container_width=True,
                        config={"displaylogo": False, "displayModeBar": False, "responsive": True}
                    )

            # =============================================
            # 12. AVANCE POR SUPERVISOR
            # =============================================

            with c_sup:

                st.subheader(
                    "Avance por supervisor"
                )

                if "supervisor" in df_estado.columns:

                    # =========================================
                    # AVANCE POR SUPERVISOR
                    # =========================================
                    # Las actividades sin supervisor asignado
                    # NO se muestran en esta gráfica.
                    # Importante: siguen formando parte de los
                    # KPIs generales y de la base de datos.
                    df_supervisor_grafico = (
                        df_estado.copy()
                    )

                    supervisor_normalizado_grafico = (
                        df_supervisor_grafico[
                            "supervisor"
                        ]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    df_supervisor_grafico = (
                        df_supervisor_grafico[
                            supervisor_normalizado_grafico.ne("")
                        ]
                        .copy()
                    )

                    if df_supervisor_grafico.empty:

                        st.info(
                            "No existen actividades con "
                            "supervisor asignado."
                        )

                    else:

                        supervisor = (
                            df_supervisor_grafico
                            .groupby(
                                "supervisor",
                                dropna=False
                            )
                            .apply(
                                lambda grupo: pd.Series({
                                    "Avance": weighted_progress(
                                        grupo
                                    ),
                                    "Actividades": len(grupo),
                                    "Pendientes": int(
                                        (
                                            grupo["avance_real"]
                                            < 100
                                        ).sum()
                                    )
                                })
                            )
                            .reset_index()
                        )

                        supervisor = (
                            supervisor
                            .sort_values(
                                "Avance",
                                ascending=True
                            )
                        )

                        fig_sup = px.bar(
                            supervisor,
                            x="Avance",
                            y="supervisor",
                            orientation="h",
                            text="Avance",
                            color_discrete_sequence=["#155EEF"]
                        )

                        fig_sup.update_traces(
                            texttemplate="%{text:.1f}%",
                            textposition="outside",
                            textfont=dict(size=12, color="#0B1F33"),
                            cliponaxis=False,
                            marker_line_width=0,
                            hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<extra></extra>"
                        )

                        fig_sup.update_layout(
                            paper_bgcolor="#FFFFFF",
                            plot_bgcolor="#FFFFFF",
                            font=dict(color="#1F2937", size=13),
                            xaxis_title="Avance (%)",
                            yaxis_title="",
                            xaxis=dict(
                                range=[0, 105],
                                ticksuffix="%",
                                gridcolor="#E5EAF0",
                                linecolor="#98A2B3",
                                tickfont=dict(size=11, color="#344054")
                            ),
                            yaxis=dict(
                                gridcolor="rgba(0,0,0,0)",
                                linecolor="#D0D5DD",
                                tickfont=dict(size=11, color="#344054"),
                                automargin=True
                            ),
                            margin=dict(l=18, r=44, t=12, b=24),
                            height=380
                        )

                        st.plotly_chart(
                            fig_sup,
                            use_container_width=True,
                            config={"displaylogo": False, "displayModeBar": False, "responsive": True}
                        )
            st.divider()

            # =============================================
            # 13. FILTROS DE DETALLE
            # =============================================

            st.subheader(
                "Detalle de planificación y avance"
            )

            f1, f2, f3 = st.columns(3)

            lista_ots = ["TODAS"]

            if "ot" in df_estado.columns:
                lista_ots += sorted(
                    df_estado["ot"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

            with f1:

                filtro_ot = st.selectbox(
                    "Filtrar por OT",
                    lista_ots,
                    key="dash_filtro_ot"
                )

            lista_especialidades = ["TODAS"]

            if "especialidad" in df_estado.columns:
                lista_especialidades += sorted(
                    df_estado["especialidad"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

            with f2:

                filtro_especialidad = st.selectbox(
                    "Filtrar por especialidad",
                    lista_especialidades,
                    key="dash_filtro_especialidad"
                )

            with f3:

                filtro_estado = st.selectbox(
                    "Estado",
                    [
                        "TODOS",
                        "CULMINADAS",
                        "EN EJECUCIÓN",
                        "NO INICIADAS",
                        "PENDIENTES"
                    ],
                    key="dash_filtro_estado"
                )

            detalle = df_estado.copy()

            if filtro_ot != "TODAS":

                detalle = detalle[
                    detalle["ot"].astype(str)
                    == filtro_ot
                ]

            if filtro_especialidad != "TODAS":

                detalle = detalle[
                    detalle[
                        "especialidad"
                    ].astype(str)
                    == filtro_especialidad
                ]

            if filtro_estado == "CULMINADAS":

                detalle = detalle[
                    detalle["avance_real"] >= 100
                ]

            elif filtro_estado == "EN EJECUCIÓN":

                detalle = detalle[
                    (
                        detalle["avance_real"] > 0
                    )
                    & (
                        detalle["avance_real"] < 100
                    )
                ]

            elif filtro_estado == "NO INICIADAS":

                detalle = detalle[
                    detalle["avance_real"] <= 0
                ]

            elif filtro_estado == "PENDIENTES":

                detalle = detalle[
                    detalle["avance_real"] < 100
                ]

            # =============================================
            # 14. ESTADO TEXTUAL
            # =============================================

            detalle["estado"] = np.where(
                detalle["avance_real"] >= 100,
                "CULMINADA",
                np.where(
                    detalle["avance_real"] > 0,
                    "EN EJECUCIÓN",
                    "NO INICIADA"
                )
            )

            columnas_tabla = [
                "ot",
                "equipo",
                "codigo_actividad",
                "descripcion",
                "especialidad",
                "supervisor",
                "grupo",
                "inicio_plan",
                "fin_plan",
                "hh_plan",
                "avance_real",
                "estado"
            ]

            columnas_tabla = [
                columna
                for columna in columnas_tabla
                if columna in detalle.columns
            ]

            tabla = detalle[
                columnas_tabla
            ].copy()

            tabla = tabla.rename(
                columns={
                    "ot": "OT",
                    "equipo": "EQUIPO",
                    "codigo_actividad": "ACTIVIDAD",
                    "descripcion": "DESCRIPCIÓN",
                    "especialidad": "ESPECIALIDAD",
                    "supervisor": "SUPERVISOR",
                    "grupo": "GRUPO",
                    "inicio_plan": "INICIO PLAN",
                    "fin_plan": "FIN PLAN",
                    "hh_plan": "HH PLAN",
                    "avance_real": "AVANCE REAL (%)",
                    "estado": "ESTADO"
                }
            )

            st.dataframe(
                tabla,
                use_container_width=True,
                hide_index=True,
                height=500
            )

            # =============================================
            # 15. RESUMEN FINAL
            # =============================================

            st.caption(
                f"Mostrando {len(tabla)} actividades · "
                f"{int(kpis.get('culminadas', 0))} culminadas · "
                f"{int(kpis.get('parciales', 0))} en ejecución · "
                f"{int(kpis.get('no_iniciadas', 0))} no iniciadas."
            )    
    
    # =====================================================
    # REGISTRAR AVANCE
    # =====================================================

    elif pagina == "Registrar avance":

        mostrar_acceso_pagina(
            f"Registrar avance · {nombre_area}",
            "Actualice el progreso y deje trazabilidad del trabajo ejecutado.",
            icono="+",
            contexto=f"{nombre_rol_sidebar} · CAMPO",
            badge=nombre_area
        )

        if not ots_area:
            st.warning(
                "Todavía no existen OTs cargadas para esta área."
            )

        else:

            # ============================================
            # FILTRO SUPERVISOR + SELECCIÓN DE OT
            # MISMA LÓGICA DEL APP ANTAPACCAY
            # ============================================

            ids_ots_area_registro = [
                ot["id"]
                for ot in ots_area
            ]

            actividades_area_registro = []

            if ids_ots_area_registro:
                actividades_area_registro = (
                    supabase
                    .table("actividades")
                    .select(
                        "id,ot_id,supervisor,activo"
                    )
                    .in_(
                        "ot_id",
                        ids_ots_area_registro
                    )
                    .eq("activo", True)
                    .execute()
                ).data or []

            supervisores_area = sorted(
                {
                    str(
                        actividad_sup.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                    for actividad_sup
                    in actividades_area_registro
                    if str(
                        actividad_sup.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                }
            )

            col_supervisor, col_ot = st.columns(2)

            with col_supervisor:

                supervisor_seleccionado = st.selectbox(
                    "Seleccione supervisor",
                    ["TODOS"] + supervisores_area,
                    key=(
                        f"supervisor_registro_"
                        f"{usuario.get('area_id')}"
                    )
                )

            # ==================================================
            # REGULARIZACIÓN DE CORTE HISTÓRICO
            # ==================================================
            # Solo PLANNER puede retroregistrar un avance.
            # No cambia la estructura de cortes de la Curva S:
            # únicamente registra el avance con la fecha/hora
            # histórica seleccionada para que el REAL del corte
            # se recalcule correctamente.
            modo_regularizacion = False
            fecha_corte_regularizacion = None
            hora_corte_regularizacion = None
            fecha_registro_efectiva_utc = None
            fecha_registro_efectiva_lima = None
            motivo_regularizacion = ""

            if rol == "planner":

                modo_regularizacion = st.checkbox(
                    "Regularizar un corte anterior",
                    value=False,
                    key=(
                        f"regularizar_corte_"
                        f"{usuario.get('area_id')}"
                    ),
                    help=(
                        "Use esta opción únicamente para completar "
                        "avances que no pudieron registrarse en su "
                        "momento por una contingencia. El avance se "
                        "asignará al corte histórico seleccionado."
                    )
                )

                if modo_regularizacion:

                    st.warning(
                        "MODO REGULARIZACIÓN: el avance se registrará "
                        "con la fecha y hora del corte seleccionado. "
                        "La fecha/hora del corte NO se modifica; "
                        "solo se completa el avance REAL faltante."
                    )

                    reg1, reg2 = st.columns(2)

                    fecha_hoy_lima = (
                        pd.Timestamp.now(
                            tz="America/Lima"
                        ).date()
                    )

                    fecha_default_regularizacion = (
                        fecha_hoy_lima
                        - pd.Timedelta(days=1)
                    )

                    with reg1:
                        fecha_corte_regularizacion = st.date_input(
                            "Fecha del corte",
                            value=fecha_default_regularizacion,
                            max_value=fecha_hoy_lima,
                            key=(
                                f"fecha_corte_regularizacion_"
                                f"{usuario.get('area_id')}"
                            )
                        )

                    with reg2:
                        hora_corte_regularizacion = st.selectbox(
                            "Hora del corte",
                            [
                                "00:00",
                                "07:00",
                                "14:00",
                                "19:00"
                            ],
                            index=3,
                            key=(
                                f"hora_corte_regularizacion_"
                                f"{usuario.get('area_id')}"
                            )
                        )

                    motivo_regularizacion = st.text_input(
                        "Motivo de regularización",
                        value="Contingencia de conectividad",
                        key=(
                            f"motivo_regularizacion_"
                            f"{usuario.get('area_id')}"
                        )
                    )

                    hora_reg, minuto_reg = [
                        int(parte)
                        for parte
                        in hora_corte_regularizacion.split(":")
                    ]

                    fecha_registro_efectiva_lima = pd.Timestamp(
                        year=fecha_corte_regularizacion.year,
                        month=fecha_corte_regularizacion.month,
                        day=fecha_corte_regularizacion.day,
                        hour=hora_reg,
                        minute=minuto_reg,
                        tz="America/Lima"
                    )

                    fecha_registro_efectiva_utc = (
                        fecha_registro_efectiva_lima
                        .tz_convert("UTC")
                    )

                    ahora_lima_regularizacion = pd.Timestamp.now(
                        tz="America/Lima"
                    )

                    if (
                        fecha_registro_efectiva_lima
                        > ahora_lima_regularizacion
                    ):
                        st.error(
                            "El corte seleccionado está en el futuro. "
                            "Seleccione un corte anterior."
                        )
                        st.stop()

                    st.info(
                        "Corte a regularizar: "
                        f"{fecha_registro_efectiva_lima:%d/%m/%Y %H:%M} · "
                        "La carga quedará trazada como regularización."
                    )

            # ==================================================
            # OTs PENDIENTES SEGÚN SUPERVISOR
            # En Registrar avance se ocultan automáticamente
            # las OTs que ya llegaron al 100%.
            #
            # - Si se selecciona TODOS:
            #   una OT se retira cuando TODAS sus actividades
            #   activas están al 100%.
            #
            # - Si se selecciona un supervisor:
            #   una OT se retira cuando TODAS las actividades
            #   de ESE supervisor dentro de la OT están al 100%.
            # ==================================================

            ids_actividades_area_registro = [
                actividad_sup["id"]
                for actividad_sup in actividades_area_registro
                if actividad_sup.get("id") is not None
            ]

            avances_area_registro = []

            if ids_actividades_area_registro:

                avances_area_registro = (
                    supabase
                    .table("avances_actividad")
                    .select(
                        "actividad_id,avance,fecha_registro"
                    )
                    .in_(
                        "actividad_id",
                        ids_actividades_area_registro
                    )
                    .execute()
                ).data or []

            df_avances_area_registro = pd.DataFrame(
                avances_area_registro
            )

            mapa_ultimo_avance_registro = {}

            if not df_avances_area_registro.empty:

                ultimos_registro = latest_progress(
                    df_avances_area_registro
                )

                if not ultimos_registro.empty:

                    mapa_ultimo_avance_registro = {
                        fila["actividad_id"]: float(
                            fila.get("avance", 0) or 0
                        )
                        for _, fila
                        in ultimos_registro.iterrows()
                    }

            actividades_relevantes_registro = []

            for actividad_sup in actividades_area_registro:

                supervisor_actividad = str(
                    actividad_sup.get(
                        "supervisor",
                        ""
                    )
                    or ""
                ).strip()

                if (
                    supervisor_seleccionado != "TODOS"
                    and supervisor_actividad
                    != supervisor_seleccionado
                ):
                    continue

                actividad_copia = dict(
                    actividad_sup
                )

                actividad_copia[
                    "_avance_real"
                ] = float(
                    mapa_ultimo_avance_registro.get(
                        actividad_sup.get("id"),
                        0
                    )
                    or 0
                )

                actividades_relevantes_registro.append(
                    actividad_copia
                )

            ids_ot_con_actividades = {
                actividad_sup.get("ot_id")
                for actividad_sup
                in actividades_relevantes_registro
                if actividad_sup.get("ot_id") is not None
            }

            ids_ot_pendientes = set()

            for ot_id_registro in ids_ot_con_actividades:

                actividades_ot_registro = [
                    actividad_sup
                    for actividad_sup
                    in actividades_relevantes_registro
                    if actividad_sup.get("ot_id")
                    == ot_id_registro
                ]

                # La OT queda disponible si al menos una actividad
                # del alcance seleccionado todavía está por debajo de 100%.
                if any(
                    float(
                        actividad_sup.get(
                            "_avance_real",
                            0
                        )
                        or 0
                    ) < 100
                    for actividad_sup
                    in actividades_ot_registro
                ):

                    ids_ot_pendientes.add(
                        ot_id_registro
                    )

            if modo_regularizacion:

                # Para corregir un corte histórico se deben poder
                # seleccionar también OTs que HOY ya están al 100%,
                # porque pudieron haber estado pendientes en el corte.
                ots_filtradas_registro = [
                    ot
                    for ot in ots_area
                    if ot.get("id")
                    in ids_ot_con_actividades
                ]

            else:

                ots_filtradas_registro = [
                    ot
                    for ot in ots_area
                    if ot.get("id")
                    in ids_ot_pendientes
                ]

            total_ots_alcance_registro = len(
                {
                    ot.get("id")
                    for ot in ots_area
                    if ot.get("id") in ids_ot_con_actividades
                }
            )

            total_ots_completadas_ocultas = max(
                0,
                total_ots_alcance_registro
                - len(ots_filtradas_registro)
            )

            mapa_ots = {
                (
                    f"{ot['ot']} - "
                    f"{ot.get('equipo') or 'Sin equipo'}"
                ): ot
                for ot in ots_filtradas_registro
            }

            with col_ot:

                ot_texto = st.selectbox(
                    "Escriba o seleccione la OT *",
                    list(mapa_ots.keys()),
                    index=None,
                    placeholder="Buscar OT...",
                    key=(
                        f"ot_registro_"
                        f"{usuario.get('area_id')}_"
                        f"{supervisor_seleccionado}"
                    )
                )

            if modo_regularizacion:

                st.caption(
                    "Regularización histórica · "
                    f"{len(ots_filtradas_registro)} OT(s) "
                    "del alcance disponibles, incluyendo OTs "
                    "que actualmente ya estén al 100%."
                )

            elif supervisor_seleccionado == "TODOS":

                st.caption(
                    f"OTs pendientes disponibles: "
                    f"{len(ots_filtradas_registro)} · "
                    f"OTs al 100% ocultas: "
                    f"{total_ots_completadas_ocultas}."
                )

            else:

                st.caption(
                    f"OTs pendientes de "
                    f"{supervisor_seleccionado}: "
                    f"{len(ots_filtradas_registro)} · "
                    f"OTs al 100% ocultas: "
                    f"{total_ots_completadas_ocultas}."
                )

            if not mapa_ots:

                if modo_regularizacion:
                    st.warning(
                        "No existen OTs disponibles para "
                        "regularizar en el alcance seleccionado."
                    )
                else:
                    st.success(
                        "No quedan OTs pendientes para "
                        "el supervisor seleccionado. "
                        "Todas las OTs de su alcance están al 100%."
                    )

                st.stop()

            if not ot_texto:

                st.info(
                    "Seleccione una OT para continuar."
                )
                st.stop()

            ot_seleccionada = mapa_ots[ot_texto]

            st.info(
                f"Equipo: "
                f"{ot_seleccionada.get('equipo') or 'Sin equipo'}"
            )

            # ============================================
            # OBTENER ACTIVIDADES DE LA OT
            # ============================================

            actividades_resultado = (
                supabase
                .table("actividades")
                .select(
                    "id,codigo_actividad,descripcion,descripcion_trabajo,"
                    "operacion,ssoma,supervisor,especialidad,grupo,peso,"
                    "inicio_plan,fin_plan,"
                    "seccion,personal,duracion_h,hh_plan,critica,activo"
                )
                .eq(
                    "ot_id",
                    ot_seleccionada["id"]
                )
                .eq("activo", True)
                .order("codigo_actividad")
                .execute()
            )

            actividades_ot = (
                actividades_resultado.data
                or []
            )

            # Si se seleccionó un supervisor específico,
            # mostrar únicamente sus actividades dentro de la OT.
            if supervisor_seleccionado != "TODOS":

                actividades_ot = [
                    actividad_ot
                    for actividad_ot in actividades_ot
                    if str(
                        actividad_ot.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                    == supervisor_seleccionado
                ]

            if not actividades_ot:

                st.warning(
                    "Esta OT no tiene actividades registradas."
                )

            else:

                mapa_actividades = {
                    f"{act['codigo_actividad']} - {act['descripcion']}": act
                    for act in actividades_ot
                }

                actividad_texto = st.selectbox(
                    "Seleccione una actividad",
                    list(mapa_actividades.keys()),
                    key=f"selector_actividad_ot_{ot_seleccionada['id']}"
                )

                actividad = mapa_actividades[actividad_texto]

                st.divider()

                # ============================================
                # DATOS PLANIFICADOS
                # ============================================

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.text_input(
                        "Supervisor",
                        value=str(actividad.get("supervisor") or ""),
                        disabled=True
                    )

                with c2:
                    st.text_input(
                        "Especialidad",
                        value=str(actividad.get("especialidad") or ""),
                        disabled=True
                    )

                with c3:
                    st.text_input(
                        "Grupo",
                        value=str(actividad.get("grupo") or ""),
                        disabled=True
                    )

                with c4:
                    st.text_input(
                        "Sección",
                        value=str(actividad.get("seccion") or ""),
                        disabled=True
                    )

                c5, c6, c7, c8 = st.columns(4)

                with c5:
                    st.text_input(
                        "Inicio planificado",
                        value=str(actividad.get("inicio_plan") or ""),
                        disabled=True
                    )

                with c6:
                    st.text_input(
                        "Fin planificado",
                        value=str(actividad.get("fin_plan") or ""),
                        disabled=True
                    )

                with c7:
                    st.text_input(
                        "Personal",
                        value=str(actividad.get("personal") or ""),
                        disabled=True
                    )

                with c8:
                    st.text_input(
                        "HH planificadas",
                        value=str(actividad.get("hh_plan") or ""),
                        disabled=True
                    )

                st.text_area(
                    "Descripción de actividad",
                    value=str(actividad.get("descripcion") or ""),
                    disabled=True
                )

                dt1, dt2 = st.columns(2)

                with dt1:
                    st.text_area(
                        "Descripción de trabajo",
                        value=str(actividad.get("descripcion_trabajo") or ""),
                        disabled=True
                    )

                with dt2:
                    st.text_area(
                        "Operación",
                        value=str(actividad.get("operacion") or ""),
                        disabled=True
                    )

                st.text_area(
                    "SSOMA",
                    value=str(actividad.get("ssoma") or ""),
                    disabled=True
                )

                st.divider()

                # ============================================
                # FORMULARIO DE AVANCE
                # ============================================

                # Obtener el último avance GUARDADO de la actividad
                # seleccionada. Así, al cambiar de actividad, el campo
                # no hereda el porcentaje de la actividad anterior.
                consulta_ultimo_avance = (
                    supabase
                    .table("avances_actividad")
                    .select("avance,fecha_registro")
                    .eq(
                        "actividad_id",
                        actividad["id"]
                    )
                )

                if (
                    modo_regularizacion
                    and fecha_registro_efectiva_utc
                    is not None
                ):

                    consulta_ultimo_avance = (
                        consulta_ultimo_avance
                        .lte(
                            "fecha_registro",
                            fecha_registro_efectiva_utc.isoformat()
                        )
                    )

                ultimo_avance_resultado = (
                    consulta_ultimo_avance
                    .order(
                        "fecha_registro",
                        desc=True
                    )
                    .limit(1)
                    .execute()
                )

                ultimo_avance_data = (
                    ultimo_avance_resultado.data
                    or []
                )

                ultimo_avance_guardado = (
                    int(
                        float(
                            ultimo_avance_data[0].get(
                                "avance",
                                0
                            )
                            or 0
                        )
                    )
                    if ultimo_avance_data
                    else 0
                )

                if modo_regularizacion:

                    st.caption(
                        "Avance conocido hasta el corte "
                        f"{fecha_registro_efectiva_lima:%d/%m/%Y %H:%M}: "
                        f"{ultimo_avance_guardado}%"
                    )

                else:

                    st.caption(
                        f"Último avance registrado de esta actividad: "
                        f"{ultimo_avance_guardado}%"
                    )

                avance = st.number_input(
                    "Porcentaje de avance de la actividad (%)",
                    min_value=0,
                    max_value=100,
                    value=ultimo_avance_guardado,
                    step=5,
                    key=f"avance_actividad_{actividad['id']}"
                )

                tipo_evidencia = st.selectbox(
                    "Tipo de evidencia",
                    [
                        "INICIO",
                        "DURANTE",
                        "FINAL"
                    ],
                    key=f"tipo_evidencia_{actividad['id']}"
                )

                critica = st.checkbox(
                    "Marcar actividad como crítica",
                    key=f"critica_actividad_{actividad['id']}"
                )

                descripcion_avance = st.text_area(
                    "Descripción breve del avance realizado *",
                    key=f"descripcion_avance_{actividad['id']}"
                )

                observaciones = st.text_area(
                    "Observaciones",
                    key=f"observaciones_avance_{actividad['id']}"
                )

                archivos_evidencia = st.file_uploader(
                    "Evidencias fotográficas",
                    type=["jpg", "jpeg", "png", "webp"],
                    accept_multiple_files=True,
                    key=f"evidencias_actividad_{actividad['id']}",
                    help=(
                        "Puede tomar fotografías desde el celular "
                        "o seleccionarlas desde la PC. "
                        "Las imágenes se comprimirán automáticamente."
                    )
                )

                if archivos_evidencia:

                    st.caption(
                        f"{len(archivos_evidencia)} "
                        "fotografía(s) seleccionada(s)."
                    )

                # ============================================
                # PROTECCIÓN CONTRA DOBLE REGISTRO
                # ============================================
                # Creamos una huella del contenido actual.
                # Si el usuario vuelve a presionar Guardar sin
                # modificar nada, NO se inserta un segundo registro.
                nombres_evidencias_actuales = sorted(
                    [
                        str(
                            getattr(
                                archivo,
                                "name",
                                ""
                            )
                            or ""
                        )
                        for archivo in (
                            archivos_evidencia
                            or []
                        )
                    ]
                )

                tamanos_evidencias_actuales = sorted(
                    [
                        int(
                            getattr(
                                archivo,
                                "size",
                                0
                            )
                            or 0
                        )
                        for archivo in (
                            archivos_evidencia
                            or []
                        )
                    ]
                )

                identificador_corte_huella = (
                    fecha_registro_efectiva_utc.isoformat()
                    if (
                        modo_regularizacion
                        and fecha_registro_efectiva_utc
                        is not None
                    )
                    else "REGISTRO_ACTUAL"
                )

                contenido_huella_avance = "|".join([
                    str(actividad["id"]),
                    identificador_corte_huella,
                    str(int(avance)),
                    str(tipo_evidencia),
                    str(bool(critica)),
                    descripcion_avance.strip(),
                    observaciones.strip(),
                    str(motivo_regularizacion or "").strip(),
                    ",".join(
                        nombres_evidencias_actuales
                    ),
                    ",".join(
                        str(valor)
                        for valor
                        in tamanos_evidencias_actuales
                    )
                ])

                huella_avance_actual = (
                    hashlib.sha256(
                        contenido_huella_avance.encode(
                            "utf-8"
                        )
                    ).hexdigest()
                )

                clave_huella_guardada = (
                    f"avance_guardado_huella_"
                    f"{actividad['id']}"
                )

                registro_ya_guardado = (
                    st.session_state.get(
                        clave_huella_guardada
                    )
                    == huella_avance_actual
                )

                clave_boton_guardar = (
                    f"guardar_avance_"
                    f"{actividad['id']}"
                )

                # Cuando el mismo registro ya fue cargado,
                # el botón se muestra en VERDE.
                if registro_ya_guardado:

                    st.markdown(
                        f"""
                        <style>
                        .st-key-{clave_boton_guardar} button {{
                            background: linear-gradient(
                                135deg,
                                #12B76A 0%,
                                #079455 100%
                            ) !important;
                            border-color: #079455 !important;
                            color: #FFFFFF !important;
                            box-shadow:
                                0 7px 18px
                                rgba(18,183,106,.22) !important;
                        }}

                        .st-key-{clave_boton_guardar} button:hover {{
                            background: linear-gradient(
                                135deg,
                                #0E9F5B 0%,
                                #067647 100%
                            ) !important;
                            border-color: #067647 !important;
                            color: #FFFFFF !important;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                guardar = st.button(
                    (
                        "✓ Avance guardado"
                        if registro_ya_guardado
                        else "Guardar avance"
                    ),
                    type="primary",
                    use_container_width=True,
                    key=clave_boton_guardar
                )

                if guardar:

                    # ----------------------------------------
                    # 1. Bloqueo inmediato de segundo clic
                    # ----------------------------------------
                    if registro_ya_guardado:

                        st.warning(
                            "Este registro ya ha sido cargado. "
                            "Para registrar un nuevo avance, "
                            "modifique el porcentaje, la descripción, "
                            "las observaciones, el tipo de evidencia "
                            "o los archivos adjuntos."
                        )

                    elif not descripcion_avance.strip():

                        st.error(
                            "Debe ingresar una descripción del avance."
                        )

                    else:

                        try:

                            # --------------------------------
                            # 2. Protección adicional en BD
                            # --------------------------------
                            # Si por latencia o doble clic llega una
                            # segunda petición casi al mismo tiempo,
                            # verificamos el último registro de esta
                            # actividad y usuario antes de subir fotos
                            # o insertar nuevamente.
                            consulta_duplicado = (
                                supabase
                                .table("avances_actividad")
                                .select(
                                    "avance,descripcion_avance,"
                                    "observaciones,tipo_evidencia,"
                                    "critica,evidencias,usuario,"
                                    "fecha_registro"
                                )
                                .eq(
                                    "actividad_id",
                                    actividad["id"]
                                )
                                .eq(
                                    "usuario",
                                    usuario["username"]
                                )
                            )

                            if (
                                modo_regularizacion
                                and fecha_registro_efectiva_utc
                                is not None
                            ):

                                inicio_ventana_corte = (
                                    fecha_registro_efectiva_utc
                                    - pd.Timedelta(seconds=1)
                                ).isoformat()

                                fin_ventana_corte = (
                                    fecha_registro_efectiva_utc
                                    + pd.Timedelta(seconds=1)
                                ).isoformat()

                                consulta_duplicado = (
                                    consulta_duplicado
                                    .gte(
                                        "fecha_registro",
                                        inicio_ventana_corte
                                    )
                                    .lte(
                                        "fecha_registro",
                                        fin_ventana_corte
                                    )
                                )

                            ultimo_registro_duplicado = (
                                consulta_duplicado
                                .order(
                                    "fecha_registro",
                                    desc=True
                                )
                                .limit(1)
                                .execute()
                            )

                            datos_ultimo_duplicado = (
                                ultimo_registro_duplicado.data
                                or []
                            )

                            duplicado_reciente = False

                            if datos_ultimo_duplicado:

                                ultimo = (
                                    datos_ultimo_duplicado[0]
                                )

                                fecha_ultimo = pd.to_datetime(
                                    ultimo.get(
                                        "fecha_registro"
                                    ),
                                    errors="coerce",
                                    utc=True
                                )

                                ahora_utc = pd.Timestamp.now(
                                    tz="UTC"
                                )

                                if modo_regularizacion:

                                    dentro_ventana = bool(
                                        pd.notna(fecha_ultimo)
                                        and fecha_registro_efectiva_utc
                                        is not None
                                        and abs(
                                            fecha_ultimo
                                            - fecha_registro_efectiva_utc
                                        )
                                        <= pd.Timedelta(
                                            seconds=1
                                        )
                                    )

                                else:

                                    dentro_ventana = (
                                        pd.notna(fecha_ultimo)
                                        and (
                                            ahora_utc
                                            - fecha_ultimo
                                        )
                                        <= pd.Timedelta(
                                            minutes=5
                                        )
                                    )

                                evidencias_ultimo = (
                                    ultimo.get(
                                        "evidencias"
                                    )
                                    or []
                                )

                                nombres_evidencias_ultimo = (
                                    sorted(
                                        [
                                            str(
                                                evidencia.get(
                                                    "nombre_original",
                                                    ""
                                                )
                                                or ""
                                            )
                                            for evidencia
                                            in evidencias_ultimo
                                            if isinstance(
                                                evidencia,
                                                dict
                                            )
                                        ]
                                    )
                                )

                                duplicado_reciente = bool(
                                    dentro_ventana
                                    and float(
                                        ultimo.get(
                                            "avance",
                                            0
                                        )
                                        or 0
                                    )
                                    == float(avance)
                                    and str(
                                        ultimo.get(
                                            "descripcion_avance",
                                            ""
                                        )
                                        or ""
                                    ).strip()
                                    == descripcion_avance.strip()
                                    and str(
                                        ultimo.get(
                                            "observaciones",
                                            ""
                                        )
                                        or ""
                                    ).strip()
                                    == observaciones.strip()
                                    and str(
                                        ultimo.get(
                                            "tipo_evidencia",
                                            ""
                                        )
                                        or ""
                                    )
                                    == str(
                                        tipo_evidencia
                                    )
                                    and bool(
                                        ultimo.get(
                                            "critica",
                                            False
                                        )
                                    )
                                    == bool(critica)
                                    and (
                                        nombres_evidencias_ultimo
                                        == nombres_evidencias_actuales
                                    )
                                )

                            if duplicado_reciente:

                                st.session_state[
                                    clave_huella_guardada
                                ] = huella_avance_actual

                                st.markdown(
                                    f"""
                                    <style>
                                    .st-key-{clave_boton_guardar} button {{
                                        background:
                                            #079455 !important;
                                        border-color:
                                            #079455 !important;
                                        color:
                                            #FFFFFF !important;
                                    }}
                                    </style>
                                    """,
                                    unsafe_allow_html=True
                                )

                                st.warning(
                                    "Este registro ya ha sido cargado "
                                    "recientemente. No se generó un "
                                    "registro duplicado."
                                )

                            else:

                                evidencias_urls = []

                                if archivos_evidencia:

                                    with st.spinner(
                                        "Comprimiendo y cargando evidencias..."
                                    ):

                                        evidencias_urls = subir_evidencias(
                                            archivos_evidencia,
                                            ot_seleccionada["ot"],
                                            actividad["codigo_actividad"],
                                            tipo_evidencia
                                        )

                                observaciones_guardar = (
                                    observaciones.strip()
                                )

                                if (
                                    modo_regularizacion
                                    and fecha_registro_efectiva_utc
                                    is not None
                                ):

                                    fecha_carga_real = (
                                        pd.Timestamp.now(
                                            tz="America/Lima"
                                        )
                                    )

                                    nota_regularizacion = (
                                        "[REGULARIZACIÓN DE CORTE] "
                                        f"Corte: "
                                        f"{fecha_registro_efectiva_lima:%d/%m/%Y %H:%M} | "
                                        f"Cargado realmente: "
                                        f"{fecha_carga_real:%d/%m/%Y %H:%M} | "
                                        f"Motivo: "
                                        f"{motivo_regularizacion.strip() or 'Contingencia operativa'}"
                                    )

                                    observaciones_guardar = (
                                        (
                                            observaciones_guardar
                                            + "\n"
                                            + nota_regularizacion
                                        ).strip()
                                    )

                                payload = {
                                    "actividad_id": actividad["id"],
                                    "avance": avance,
                                    "descripcion_avance": descripcion_avance.strip(),
                                    "observaciones": observaciones_guardar,
                                    "tipo_evidencia": tipo_evidencia,
                                    "critica": critica,
                                    "evidencias": evidencias_urls,
                                    "usuario": usuario["username"]
                                }

                                if (
                                    modo_regularizacion
                                    and fecha_registro_efectiva_utc
                                    is not None
                                ):

                                    payload["fecha_registro"] = (
                                        fecha_registro_efectiva_utc.isoformat()
                                    )

                                (
                                    supabase
                                    .table("avances_actividad")
                                    .insert(payload)
                                    .execute()
                                )

                                # Marcar este contenido como guardado.
                                # El segundo clic quedará bloqueado.
                                st.session_state[
                                    clave_huella_guardada
                                ] = huella_avance_actual

                                # Cambiar inmediatamente el botón a verde.
                                st.markdown(
                                    f"""
                                    <style>
                                    .st-key-{clave_boton_guardar} button {{
                                        background:
                                            linear-gradient(
                                                135deg,
                                                #12B76A 0%,
                                                #079455 100%
                                            ) !important;
                                        border-color:
                                            #079455 !important;
                                        color:
                                            #FFFFFF !important;
                                        box-shadow:
                                            0 7px 18px
                                            rgba(
                                                18,
                                                183,
                                                106,
                                                .22
                                            ) !important;
                                    }}
                                    </style>
                                    """,
                                    unsafe_allow_html=True
                                )

                                if evidencias_urls:

                                    total_original = sum(
                                        evidencia.get(
                                            "tamano_original",
                                            0
                                        )
                                        for evidencia
                                        in evidencias_urls
                                    )

                                    total_comprimido = sum(
                                        evidencia.get(
                                            "tamano_comprimido",
                                            0
                                        )
                                        for evidencia
                                        in evidencias_urls
                                    )

                                    ahorro_total = (
                                        (
                                            1
                                            - total_comprimido
                                            / total_original
                                        )
                                        * 100
                                        if total_original > 0
                                        else 0
                                    )

                                    if modo_regularizacion:

                                        st.success(
                                            "✓ Regularización registrada "
                                            f"en el corte "
                                            f"{fecha_registro_efectiva_lima:%d/%m/%Y %H:%M} "
                                            f"con {len(evidencias_urls)} evidencia(s). "
                                            "La fecha/hora del corte se mantiene "
                                            "y solo se actualiza el avance REAL."
                                        )

                                    else:

                                        st.success(
                                            f"✓ Avance registrado correctamente "
                                            f"con {len(evidencias_urls)} "
                                            f"evidencia(s). "
                                            f"Compresión aproximada: "
                                            f"{ahorro_total:.0f}%. "
                                            "El registro quedó protegido "
                                            "contra doble envío."
                                        )

                                else:

                                    if modo_regularizacion:

                                        st.success(
                                            "✓ Regularización registrada "
                                            f"en el corte "
                                            f"{fecha_registro_efectiva_lima:%d/%m/%Y %H:%M}. "
                                            "La Curva S recalculará el REAL "
                                            "de ese corte sin modificar "
                                            "su fecha ni hora."
                                        )

                                    else:

                                        st.success(
                                            "✓ Avance registrado correctamente. "
                                            "El registro quedó protegido "
                                            "contra doble envío."
                                        )

                        except Exception as exc:

                            st.error(
                                f"No fue posible guardar el avance: {exc}"
                            )
    
    # =====================================================
    # DETALLE POR OT
    # =====================================================

    elif pagina == "Detalle por OT":

        mostrar_acceso_pagina(
            f"Detalle por OT · {nombre_area}",
            "Revise actividades, estado y último avance por orden de trabajo.",
            icono="⌁",
            contexto=f"{nombre_rol_sidebar} · TRAZABILIDAD",
            badge=nombre_area
        )

        if not ots_area:

            st.warning(
                "Todavía no existen OTs cargadas para esta área."
            )

        else:

            # ================================================
            # FILTRO SUPERVISOR + SELECCIÓN DE OT
            # MISMA LÓGICA DEL APP ANTAPACCAY
            # ================================================

            ids_ots_detalle_area = [
                ot["id"]
                for ot in ots_area
            ]

            actividades_area_detalle = []

            if ids_ots_detalle_area:
                actividades_area_detalle = (
                    supabase
                    .table("actividades")
                    .select(
                        "id,ot_id,supervisor,activo"
                    )
                    .in_(
                        "ot_id",
                        ids_ots_detalle_area
                    )
                    .eq("activo", True)
                    .execute()
                ).data or []

            supervisores_detalle = sorted(
                {
                    str(
                        actividad_det.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                    for actividad_det
                    in actividades_area_detalle
                    if str(
                        actividad_det.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                }
            )

            col_sup_det, col_ot_det = st.columns(2)

            with col_sup_det:

                supervisor_detalle = st.selectbox(
                    "Seleccione supervisor",
                    ["TODOS"] + supervisores_detalle,
                    key=(
                        f"detalle_supervisor_"
                        f"{usuario.get('area_id')}"
                    )
                )

            if supervisor_detalle == "TODOS":

                ots_detalle_filtradas = ots_area

            else:

                ids_ots_supervisor_detalle = {
                    actividad_det["ot_id"]
                    for actividad_det
                    in actividades_area_detalle
                    if str(
                        actividad_det.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                    == supervisor_detalle
                }

                ots_detalle_filtradas = [
                    ot
                    for ot in ots_area
                    if ot["id"]
                    in ids_ots_supervisor_detalle
                ]

            mapa_detalle_ots = {
                (
                    f"{ot['ot']} - "
                    f"{ot.get('equipo') or 'Sin equipo'}"
                ): ot
                for ot in ots_detalle_filtradas
            }

            with col_ot_det:

                ot_detalle_texto = st.selectbox(
                    "Escriba o seleccione la OT *",
                    list(mapa_detalle_ots.keys()),
                    index=None,
                    placeholder="Buscar OT...",
                    key=(
                        f"detalle_ot_selector_"
                        f"{usuario.get('area_id')}_"
                        f"{supervisor_detalle}"
                    )
                )

            if supervisor_detalle == "TODOS":
                st.caption(
                    f"Mostrando todas las OTs disponibles: "
                    f"{len(ots_detalle_filtradas)} OT(s)."
                )
            else:
                st.caption(
                    f"Mostrando OTs de "
                    f"{supervisor_detalle}: "
                    f"{len(ots_detalle_filtradas)} OT(s)."
                )

            if not mapa_detalle_ots:

                st.warning(
                    "No existen OTs activas para "
                    "el supervisor seleccionado."
                )
                st.stop()

            if not ot_detalle_texto:

                st.info(
                    "Seleccione una OT para visualizar su detalle."
                )
                st.stop()

            ot_detalle = mapa_detalle_ots[
                ot_detalle_texto
            ]

            # ================================================
            # INFORMACIÓN GENERAL DE LA OT
            # ================================================

            c1, c2 = st.columns(2)

            with c1:
                st.info(
                    f"**OT:** {ot_detalle['ot']}"
                )

            with c2:
                st.info(
                    f"**Equipo:** "
                    f"{ot_detalle.get('equipo') or 'Sin equipo'}"
                )

            if ot_detalle.get("descripcion"):

                st.caption(
                    f"Descripción: "
                    f"{ot_detalle['descripcion']}"
                )

            # ================================================
            # OBTENER ACTIVIDADES DE LA OT
            # ================================================

            resultado_actividades_detalle = (
                supabase
                .table("actividades")
                .select(
                    "id,ot_id,codigo_actividad,descripcion,"
                    "descripcion_trabajo,operacion,ssoma,"
                    "supervisor,especialidad,grupo,peso,"
                    "inicio_plan,fin_plan,seccion,personal,"
                    "duracion_h,hh_plan,critica,activo"
                )
                .eq(
                    "ot_id",
                    ot_detalle["id"]
                )
                .eq(
                    "activo",
                    True
                )
                .order(
                    "codigo_actividad"
                )
                .execute()
            )

            actividades_detalle = (
                resultado_actividades_detalle.data
                or []
            )

            if supervisor_detalle != "TODOS":
                actividades_detalle = [
                    actividad_det
                    for actividad_det
                    in actividades_detalle
                    if str(
                        actividad_det.get(
                            "supervisor",
                            ""
                        )
                    ).strip()
                    == supervisor_detalle
                ]

            if not actividades_detalle:

                st.warning(
                    "Esta OT no tiene actividades registradas."
                )

            else:

                df_actividades_detalle = pd.DataFrame(
                    actividades_detalle
                )

                # ============================================
                # OBTENER AVANCES DE LAS ACTIVIDADES
                # ============================================

                ids_actividades_detalle = (
                    df_actividades_detalle["id"]
                    .dropna()
                    .tolist()
                )

                resultado_avances_detalle = (
                    supabase
                    .table("avances_actividad")
                    .select(
                        "id,actividad_id,avance,"
                        "descripcion_avance,observaciones,"
                        "tipo_evidencia,critica,evidencias,"
                        "usuario,fecha_registro"
                    )
                    .in_(
                        "actividad_id",
                        ids_actividades_detalle
                    )
                    .execute()
                )

                avances_detalle = (
                    resultado_avances_detalle.data
                    or []
                )

                df_avances_detalle = pd.DataFrame(
                    avances_detalle
                )

                # ============================================
                # ESTADO ACTUAL DE LAS ACTIVIDADES
                # ============================================

                estado_ot = build_activity_status(
                    df_actividades_detalle,
                    df_avances_detalle
                )

                kpis_ot = compute_kpis(
                    df_actividades_detalle,
                    df_avances_detalle
                )

                # ============================================
                # INDICADORES DE LA OT
                # ============================================

                o1, o2, o3, o4, o5, o6 = st.columns(6)

                with o1:

                    st.metric(
                        "Actividades",
                        kpis_ot["actividades"]
                    )

                with o2:

                    st.metric(
                        "Avance OT",
                        f"{kpis_ot['avance_general']:.1f}%"
                    )

                with o3:

                    st.metric(
                        "Culminadas",
                        kpis_ot["culminadas"]
                    )

                with o4:

                    st.metric(
                        "En ejecución",
                        kpis_ot["parciales"]
                    )

                with o5:

                    st.metric(
                        "No iniciadas",
                        kpis_ot["no_iniciadas"]
                    )

                with o6:

                    st.metric(
                        "Pendientes",
                        kpis_ot["pendientes"]
                    )

                hh1, hh2 = st.columns(2)

                with hh1:

                    st.metric(
                        "HH planificadas",
                        f"{kpis_ot['hh_plan']:.0f}"
                    )

                with hh2:

                    st.metric(
                        "HH ganadas",
                        f"{kpis_ot['hh_ganadas']:.0f}"
                    )

                st.divider()

                # ============================================
                # BARRA DE AVANCE
                # ============================================

                avance_ot = float(
                    kpis_ot["avance_general"]
                )

                st.write(
                    f"**Avance general de la OT: "
                    f"{avance_ot:.1f}%**"
                )

                st.progress(
                    min(
                        max(
                            avance_ot / 100,
                            0
                        ),
                        1
                    )
                )

                st.divider()

                # ============================================
                # ESTADO TEXTUAL
                # ============================================

                estado_ot["estado"] = np.where(
                    estado_ot["avance_real"] >= 100,
                    "CULMINADA",
                    np.where(
                        estado_ot["avance_real"] > 0,
                        "EN EJECUCIÓN",
                        "NO INICIADA"
                    )
                )

                # ============================================
                # ÚLTIMO REPORTE
                # ============================================

                if not df_avances_detalle.empty:

                    ultimos_reportes = latest_progress(
                        df_avances_detalle
                    )

                    columnas_reporte = [
                        columna
                        for columna in [
                            "actividad_id",
                            "descripcion_avance",
                            "observaciones",
                            "tipo_evidencia",
                            "usuario",
                            "fecha_registro"
                        ]
                        if columna in ultimos_reportes.columns
                    ]

                    columnas_reporte = [
                        columna
                        for columna in columnas_reporte
                        if columna not in estado_ot.columns
                        or columna == "actividad_id"
                    ]

                    if columnas_reporte:

                        estado_ot = estado_ot.merge(
                            ultimos_reportes[
                                columnas_reporte
                            ],
                            left_on="id",
                            right_on="actividad_id",
                            how="left",
                            suffixes=(
                                "",
                                "_ultimo"
                            )
                        )

                # ============================================
                # TABLA DE ACTIVIDADES
                # ============================================

                columnas_detalle_ot = [
                    "codigo_actividad",
                    "descripcion_trabajo",
                    "operacion",
                    "ssoma",
                    "descripcion",
                    "supervisor",
                    "especialidad",
                    "grupo",
                    "inicio_plan",
                    "fin_plan",
                    "personal",
                    "hh_plan",
                    "avance_real",
                    "estado"
                ]

                columnas_detalle_ot = [
                    columna
                    for columna in columnas_detalle_ot
                    if columna in estado_ot.columns
                ]

                tabla_ot = estado_ot[
                    columnas_detalle_ot
                ].copy()

                tabla_ot = tabla_ot.rename(
                    columns={
                        "codigo_actividad":
                            "ACTIVIDAD",
                        "descripcion_trabajo":
                            "DESCRIPCIÓN TRABAJO",
                        "operacion":
                            "OPERACIÓN",
                        "ssoma":
                            "SSOMA",
                        "descripcion":
                            "DESCRIPCIÓN",
                        "supervisor":
                            "SUPERVISOR",
                        "especialidad":
                            "ESPECIALIDAD",
                        "grupo":
                            "GRUPO",
                        "inicio_plan":
                            "INICIO PLAN",
                        "fin_plan":
                            "FIN PLAN",
                        "personal":
                            "PERSONAL",
                        "hh_plan":
                            "HH PLAN",
                        "avance_real":
                            "AVANCE (%)",
                        "estado":
                            "ESTADO"
                    }
                )

                st.subheader(
                    "Actividades de la OT"
                )

                st.dataframe(
                    tabla_ot,
                    use_container_width=True,
                    hide_index=True,
                    height=450
                )

                # ============================================
                # ACTIVIDADES EN EJECUCIÓN
                # ============================================

                actividades_ejecucion = estado_ot[
                    (
                        estado_ot["avance_real"] > 0
                    )
                    &
                    (
                        estado_ot["avance_real"] < 100
                    )
                ]

                if not actividades_ejecucion.empty:

                    st.subheader(
                        "Actividades actualmente en ejecución"
                    )

                    for _, actividad_actual in (
                        actividades_ejecucion.iterrows()
                    ):

                        with st.expander(
                            f"{actividad_actual.get('codigo_actividad', '')} "
                            f"- {actividad_actual.get('descripcion', '')}"
                        ):

                            x1, x2, x3 = st.columns(3)

                            with x1:

                                st.metric(
                                    "Avance",
                                    f"{float(actividad_actual.get('avance_real', 0)):.1f}%"
                                )

                            with x2:

                                st.write(
                                    "**Supervisor:**"
                                )

                                st.write(
                                    actividad_actual.get(
                                        "supervisor"
                                    )
                                    or "-"
                                )

                            with x3:

                                st.write(
                                    "**Grupo:**"
                                )

                                st.write(
                                    actividad_actual.get(
                                        "grupo"
                                    )
                                    or "-"
                                )

                            descripcion_ultimo = (
                                actividad_actual.get(
                                    "descripcion_avance"
                                )
                                or actividad_actual.get(
                                    "descripcion_avance_ultimo"
                                )
                            )

                            if descripcion_ultimo:

                                st.write(
                                    "**Último avance reportado:**"
                                )

                                st.write(
                                    descripcion_ultimo
                                )

                            observacion_ultima = (
                                actividad_actual.get(
                                    "observaciones"
                                )
                                or actividad_actual.get(
                                    "observaciones_ultimo"
                                )
                            )

                            if observacion_ultima:

                                st.write(
                                    "**Observaciones:**"
                                )

                                st.write(
                                    observacion_ultima
                                )

    # =====================================================
    # EVIDENCIAS
    # =====================================================

    elif pagina == "Evidencias":

        mostrar_acceso_pagina(
            f"Evidencias · {nombre_area}",
            "Consulte el registro fotográfico asociado a los avances.",
            icono="▧",
            contexto=f"{nombre_rol_sidebar} · EVIDENCIAS",
            badge=nombre_area
        )

        if not ots_area:

            st.warning(
                "Todavía no existen OTs cargadas para esta área."
            )

        else:

            ids_ots_evidencias = [
                ot["id"]
                for ot in ots_area
            ]

            actividades_evidencias = (
                supabase
                .table("actividades")
                .select(
                    "id,ot_id,codigo_actividad,descripcion,supervisor"
                )
                .in_("ot_id", ids_ots_evidencias)
                .eq("activo", True)
                .execute()
            ).data or []

            if not actividades_evidencias:

                st.info(
                    "No existen actividades disponibles."
                )

            else:

                ids_actividades_evidencias = [
                    actividad["id"]
                    for actividad in actividades_evidencias
                ]

                registros_evidencias = (
                    supabase
                    .table("avances_actividad")
                    .select(
                        "id,actividad_id,avance,"
                        "descripcion_avance,observaciones,"
                        "tipo_evidencia,evidencias,"
                        "usuario,fecha_registro"
                    )
                    .in_(
                        "actividad_id",
                        ids_actividades_evidencias
                    )
                    .order(
                        "fecha_registro",
                        desc=True
                    )
                    .execute()
                ).data or []

                registros_con_fotos = [
                    registro
                    for registro in registros_evidencias
                    if registro.get("evidencias")
                ]

                if not registros_con_fotos:

                    st.info(
                        "Todavía no existen evidencias fotográficas "
                        "registradas para esta área."
                    )

                else:

                    mapa_ots_evidencias = {
                        ot["id"]: ot
                        for ot in ots_area
                    }

                    mapa_actividades_evidencias = {
                        actividad["id"]: actividad
                        for actividad in actividades_evidencias
                    }

                    opciones_ot = ["TODAS"] + sorted(
                        {
                            str(ot.get("ot", ""))
                            for ot in ots_area
                            if str(ot.get("ot", "")).strip()
                        }
                    )

                    supervisores_disponibles = sorted(
                        {
                            str(
                                actividad.get(
                                    "supervisor",
                                    ""
                                )
                                or ""
                            ).strip()
                            for actividad in actividades_evidencias
                            if str(
                                actividad.get(
                                    "supervisor",
                                    ""
                                )
                                or ""
                            ).strip()
                        }
                    )

                    hay_sin_supervisor = any(
                        not str(
                            actividad.get(
                                "supervisor",
                                ""
                            )
                            or ""
                        ).strip()
                        for actividad in actividades_evidencias
                    )

                    opciones_supervisor = ["TODOS"]

                    if supervisores_disponibles:
                        opciones_supervisor.extend(
                            supervisores_disponibles
                        )

                    if hay_sin_supervisor:
                        opciones_supervisor.append(
                            "SIN SUPERVISOR"
                        )

                    f1, f2, f3 = st.columns(3)

                    with f1:

                        filtro_ot_evidencias = st.selectbox(
                            "Filtrar por OT",
                            opciones_ot,
                            key="filtro_evidencias_ot"
                        )

                    with f2:

                        filtro_supervisor_evidencias = st.selectbox(
                            "Supervisor",
                            opciones_supervisor,
                            key="filtro_evidencias_supervisor"
                        )

                    with f3:

                        filtro_tipo_evidencias = st.selectbox(
                            "Tipo de evidencia",
                            [
                                "TODAS",
                                "INICIO",
                                "DURANTE",
                                "FINAL"
                            ],
                            key="filtro_evidencias_tipo"
                        )

                    registros_filtrados = []

                    for registro in registros_con_fotos:

                        actividad = (
                            mapa_actividades_evidencias.get(
                                registro["actividad_id"],
                                {}
                            )
                        )

                        ot = mapa_ots_evidencias.get(
                            actividad.get("ot_id"),
                            {}
                        )

                        if (
                            filtro_ot_evidencias != "TODAS"
                            and str(ot.get("ot", ""))
                            != filtro_ot_evidencias
                        ):
                            continue

                        supervisor_actividad = str(
                            actividad.get(
                                "supervisor",
                                ""
                            )
                            or ""
                        ).strip()

                        if (
                            filtro_supervisor_evidencias
                            == "SIN SUPERVISOR"
                            and supervisor_actividad
                        ):
                            continue

                        if (
                            filtro_supervisor_evidencias
                            not in {
                                "TODOS",
                                "SIN SUPERVISOR"
                            }
                            and supervisor_actividad
                            != filtro_supervisor_evidencias
                        ):
                            continue

                        if (
                            filtro_tipo_evidencias != "TODAS"
                            and str(
                                registro.get(
                                    "tipo_evidencia",
                                    ""
                                )
                            ).upper()
                            != filtro_tipo_evidencias
                        ):
                            continue

                        registros_filtrados.append(
                            (
                                registro,
                                actividad,
                                ot
                            )
                        )

                    st.caption(
                        f"{len(registros_filtrados)} "
                        "registro(s) con evidencia."
                    )

                    for (
                        registro,
                        actividad,
                        ot
                    ) in registros_filtrados:

                        titulo = (
                            f"OT {ot.get('ot', '')} · "
                            f"{actividad.get('codigo_actividad', '')} · "
                            f"{registro.get('avance', 0)}%"
                        )

                        with st.expander(
                            titulo,
                            expanded=False
                        ):

                            d1, d2, d3, d4 = st.columns(4)

                            with d1:
                                st.write(
                                    "**Tipo:** "
                                    f"{registro.get('tipo_evidencia', '')}"
                                )

                            with d2:
                                st.write(
                                    "**Supervisor:** "
                                    f"{actividad.get('supervisor') or 'Sin asignar'}"
                                )

                            with d3:
                                st.write(
                                    "**Usuario:** "
                                    f"{registro.get('usuario', '')}"
                                )

                            with d4:
                                fecha_evidencia = pd.to_datetime(
                                    registro.get("fecha_registro"),
                                    errors="coerce",
                                    utc=True
                                )

                                if not pd.isna(fecha_evidencia):

                                    fecha_evidencia = (
                                        fecha_evidencia
                                        .tz_convert("America/Lima")
                                    )

                                    fecha_texto = (
                                        fecha_evidencia.strftime(
                                            "%d/%m/%Y %H:%M"
                                        )
                                    )

                                else:
                                    fecha_texto = ""

                                st.write(
                                    "**Fecha:** "
                                    f"{fecha_texto}"
                                )

                            st.write(
                                "**Actividad:** "
                                f"{actividad.get('descripcion', '')}"
                            )

                            st.write(
                                "**Avance reportado:** "
                                f"{registro.get('descripcion_avance', '')}"
                            )

                            observacion = (
                                registro.get("observaciones")
                                or ""
                            )

                            if observacion:
                                st.write(
                                    "**Observaciones:** "
                                    f"{observacion}"
                                )

                            evidencias_lista = (
                                registro.get("evidencias")
                                or []
                            )

                            columnas_fotos = st.columns(
                                min(
                                    len(evidencias_lista),
                                    3
                                )
                            )

                            for indice, evidencia in enumerate(
                                evidencias_lista
                            ):

                                if isinstance(
                                    evidencia,
                                    str
                                ):
                                    nombre_evidencia = (
                                        f"Evidencia {indice + 1}"
                                    )

                                else:
                                    nombre_evidencia = (
                                        evidencia.get(
                                            "nombre_original"
                                        )
                                        or f"Evidencia {indice + 1}"
                                    )

                                # La fotografía se mantiene almacenada
                                # permanentemente. Solo la URL de lectura
                                # es temporal (1 hora).
                                url_evidencia = (
                                    crear_url_firmada_evidencia(
                                        evidencia,
                                        duracion_segundos=3600
                                    )
                                )

                                if not url_evidencia:
                                    st.warning(
                                        "No fue posible generar acceso "
                                        f"temporal a {nombre_evidencia}."
                                    )
                                    continue

                                with columnas_fotos[
                                    indice % len(columnas_fotos)
                                ]:

                                    st.image(
                                        url_evidencia,
                                        caption=nombre_evidencia,
                                        use_container_width=True
                                    )



    # =====================================================
    # REPORTES
    # =====================================================

    elif pagina == "Reportes":

        mostrar_acceso_pagina(
            f"Reportes · {nombre_area}",
            "Genere el reporte ejecutivo y exporte la información del área.",
            icono="↗",
            contexto=f"{nombre_rol_sidebar} · REPORTING",
            badge="PDF · Excel"
        )

        if not ots_area:

            st.warning(
                "Todavía no existen OTs cargadas para esta área."
            )

        else:

            ids_ots_reporte = [
                ot["id"]
                for ot in ots_area
            ]

            actividades_reporte = (
                supabase
                .table("actividades")
                .select(
                    "id,ot_id,codigo_actividad,descripcion,"
                    "descripcion_trabajo,operacion,ssoma,"
                    "supervisor,especialidad,grupo,peso,"
                    "inicio_plan,fin_plan,seccion,personal,"
                    "duracion_h,hh_plan,critica,activo"
                )
                .in_(
                    "ot_id",
                    ids_ots_reporte
                )
                .eq(
                    "activo",
                    True
                )
                .execute()
            ).data or []

            if not actividades_reporte:

                st.warning(
                    "No existen actividades cargadas "
                    "para esta área."
                )

            else:

                df_ots_reporte = pd.DataFrame(
                    ots_area
                )

                df_actividades_reporte = pd.DataFrame(
                    actividades_reporte
                )

                ids_actividades_reporte = (
                    df_actividades_reporte[
                        "id"
                    ]
                    .dropna()
                    .tolist()
                )

                avances_reporte = (
                    supabase
                    .table("avances_actividad")
                    .select(
                        "id,actividad_id,avance,"
                        "descripcion_avance,observaciones,"
                        "tipo_evidencia,critica,evidencias,"
                        "usuario,fecha_registro"
                    )
                    .in_(
                        "actividad_id",
                        ids_actividades_reporte
                    )
                    .execute()
                ).data or []

                df_avances_reporte = pd.DataFrame(
                    avances_reporte
                )

                kpis_reporte = compute_kpis(
                    df_actividades_reporte,
                    df_avances_reporte
                )

                r1, r2, r3, r4 = st.columns(4)

                with r1:
                    st.metric(
                        "OTs",
                        len(df_ots_reporte)
                    )

                with r2:
                    st.metric(
                        "Actividades",
                        kpis_reporte[
                            "actividades"
                        ]
                    )

                with r3:
                    st.metric(
                        "Avance general",
                        f"{kpis_reporte['avance_general']:.1f}%"
                    )

                with r4:
                    st.metric(
                        "SPI",
                        f"{kpis_reporte['spi']:.2f}"
                    )

                st.divider()

                mostrar_reportes_fotograficos_adicionales(
                    df_ots_reporte,
                    df_actividades_reporte,
                    df_avances_reporte,
                    nombre_area,
                    "planner"
                )

                st.divider()

                # =========================================
                # REPORTE POR SUPERVISOR
                # =========================================
                st.subheader(
                    "Reporte por supervisor"
                )

                st.caption(
                    "Seleccione un supervisor para revisar sus "
                    "KPIs, sus actividades y exportar un PDF "
                    "individual de desempeño."
                )

                supervisores_reporte = (
                    lista_supervisores_reporte(
                        df_actividades_reporte
                    )
                )

                if not supervisores_reporte:

                    st.info(
                        "No existen supervisores asignados "
                        "en las actividades de esta área."
                    )

                else:

                    supervisor_reporte = st.selectbox(
                        "Seleccionar supervisor",
                        supervisores_reporte,
                        key="selector_supervisor_reporte_planner"
                    )

                    (
                        df_ots_supervisor,
                        df_actividades_supervisor,
                        df_avances_supervisor
                    ) = filtrar_reporte_supervisor(
                        df_ots_reporte,
                        df_actividades_reporte,
                        df_avances_reporte,
                        supervisor_reporte
                    )

                    kpis_supervisor = compute_kpis(
                        df_actividades_supervisor,
                        df_avances_supervisor
                    )

                    plan_supervisor = float(
                        kpis_supervisor.get(
                            "avance_plan",
                            0
                        ) or 0
                    )

                    real_supervisor = float(
                        kpis_supervisor.get(
                            "avance_general",
                            0
                        ) or 0
                    )

                    brecha_supervisor = (
                        real_supervisor
                        - plan_supervisor
                    )

                    sr1, sr2, sr3, sr4 = st.columns(4)

                    with sr1:
                        st.metric(
                            "OTs",
                            len(
                                df_ots_supervisor
                            )
                        )

                    with sr2:
                        st.metric(
                            "Actividades",
                            int(
                                kpis_supervisor.get(
                                    "actividades",
                                    0
                                ) or 0
                            )
                        )

                    with sr3:
                        st.metric(
                            "Avance real",
                            f"{real_supervisor:.1f}%",
                            delta=(
                                f"{brecha_supervisor:+.1f} pp"
                            )
                        )

                    with sr4:
                        st.metric(
                            "SPI",
                            f"{float(kpis_supervisor.get('spi', 0) or 0):.2f}"
                        )

                    sr5, sr6, sr7, sr8 = st.columns(4)

                    with sr5:
                        st.metric(
                            "Culminadas",
                            int(
                                kpis_supervisor.get(
                                    "culminadas",
                                    0
                                ) or 0
                            )
                        )

                    with sr6:
                        st.metric(
                            "En ejecución",
                            int(
                                kpis_supervisor.get(
                                    "parciales",
                                    0
                                ) or 0
                            )
                        )

                    with sr7:
                        st.metric(
                            "No iniciadas",
                            int(
                                kpis_supervisor.get(
                                    "no_iniciadas",
                                    0
                                ) or 0
                            )
                        )

                    with sr8:
                        st.metric(
                            "HH plan / ganadas",
                            (
                                f"{float(kpis_supervisor.get('hh_plan', 0) or 0):.0f}"
                                " / "
                                f"{float(kpis_supervisor.get('hh_ganadas', 0) or 0):.0f}"
                            )
                        )

                    estado_supervisor = (
                        calcular_semaforo_pdf(
                            df_actividades_supervisor,
                            df_avances_supervisor
                        )
                    )

                    if (
                        not estado_supervisor.empty
                        and not df_ots_supervisor.empty
                    ):

                        estado_supervisor = (
                            estado_supervisor
                            .merge(
                                df_ots_supervisor[
                                    [
                                        "id",
                                        "ot",
                                        "equipo"
                                    ]
                                ].rename(
                                    columns={
                                        "id": "ot_id"
                                    }
                                ),
                                on="ot_id",
                                how="left"
                            )
                        )

                        tabla_supervisor = (
                            estado_supervisor[
                                [
                                    "ot",
                                    "equipo",
                                    "grupo",
                                    "descripcion",
                                    "PLAN ACTUAL (%)",
                                    "avance_real",
                                    "DESVIACIÓN (pp)",
                                    "ALERTA"
                                ]
                            ]
                            .rename(
                                columns={
                                    "ot": "OT",
                                    "equipo": "EQUIPO",
                                    "grupo": "GRUPO",
                                    "descripcion": "DESCRIPCIÓN",
                                    "PLAN ACTUAL (%)": "PLAN (%)",
                                    "avance_real": "REAL (%)",
                                    "DESVIACIÓN (pp)": "BRECHA (pp)",
                                    "ALERTA": "ESTADO"
                                }
                            )
                        )

                        st.dataframe(
                            tabla_supervisor,
                            use_container_width=True,
                            hide_index=True,
                            height=360
                        )

                    try:

                        pdf_supervisor = (
                            construir_pdf_supervisor(
                                df_ots_supervisor,
                                df_actividades_supervisor,
                                df_avances_supervisor,
                                nombre_area,
                                supervisor_reporte
                            )
                        )

                        nombre_archivo_supervisor = (
                            str(
                                supervisor_reporte
                            )
                            .strip()
                            .lower()
                            .replace(
                                " ",
                                "_"
                            )
                        )

                        st.download_button(
                            "Descargar PDF del supervisor",
                            data=pdf_supervisor,
                            file_name=(
                                "PDP_Quellaveco_"
                                f"{codigo_area.lower()}_"
                                f"{nombre_archivo_supervisor}_"
                                f"{datetime.now():%Y%m%d_%H%M}.pdf"
                            ),
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                            key="descarga_pdf_supervisor_planner"
                        )

                    except Exception as exc:

                        st.error(
                            "No fue posible generar el "
                            "PDF del supervisor: "
                            f"{exc}"
                        )

                st.divider()

                st.subheader(
                    "Reporte ejecutivo PDF"
                )

                st.write(
                    "El PDF incluye indicadores principales, "
                    "resumen del día, actividades críticas, "
                    "pendientes y detalle consolidado por OT."
                )

                try:

                    pdf_bytes = construir_pdf_ejecutivo_area(
                        df_ots_reporte,
                        df_actividades_reporte,
                        df_avances_reporte,
                        nombre_area
                    )

                    st.download_button(
                        "Descargar reporte ejecutivo PDF",
                        data=pdf_bytes,
                        file_name=(
                            f"PDP_Quellaveco_"
                            f"{codigo_area.lower()}_"
                            f"{datetime.now():%Y%m%d_%H%M}.pdf"
                        ),
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

                except Exception as exc:

                    st.error(
                        "No fue posible generar el PDF: "
                        f"{exc}"
                    )

                st.divider()

                st.subheader(
                    "Exportación completa a Excel"
                )

                estado_reporte = build_activity_status(
                    df_actividades_reporte,
                    df_avances_reporte
                )

                if not estado_reporte.empty:

                    estado_reporte = (
                        estado_reporte
                        .merge(
                            df_ots_reporte[
                                [
                                    "id",
                                    "ot",
                                    "equipo"
                                ]
                            ],
                            left_on="ot_id",
                            right_on="id",
                            how="left",
                            suffixes=(
                                "",
                                "_ot"
                            )
                        )
                    )

                buffer_reporte_excel = io.BytesIO()

                # Excel no admite fechas con timezone.
                # También limpiamos listas/diccionarios antes de exportar.
                excel_ots = preparar_dataframe_excel(
                    df_ots_reporte
                )

                excel_actividades = preparar_dataframe_excel(
                    df_actividades_reporte
                )

                excel_avances = preparar_dataframe_excel(
                    df_avances_reporte
                )

                excel_estado = preparar_dataframe_excel(
                    estado_reporte
                )

                with pd.ExcelWriter(
                    buffer_reporte_excel,
                    engine="openpyxl"
                ) as writer:

                    excel_ots.to_excel(
                        writer,
                        index=False,
                        sheet_name="OTs"
                    )

                    excel_actividades.to_excel(
                        writer,
                        index=False,
                        sheet_name="Actividades"
                    )

                    excel_avances.to_excel(
                        writer,
                        index=False,
                        sheet_name="Avances"
                    )

                    excel_estado.to_excel(
                        writer,
                        index=False,
                        sheet_name="Estado_Actual"
                    )

                st.download_button(
                    "Descargar reporte completo en Excel",
                    data=buffer_reporte_excel.getvalue(),
                    file_name=(
                        f"PDP_Quellaveco_"
                        f"{codigo_area.lower()}_"
                        f"{datetime.now():%Y%m%d_%H%M}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.spreadsheetml.sheet"
                    ),
                    use_container_width=True
                )
