import json
import math
from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st

import db_helper as db

st.set_page_config(page_title="FuelUp", page_icon="⚡", layout="wide")
db.init_db()
db.seed_default_foods()

LIME, BLUE, MUTED = "#b6f500", "#2f7bff", "#8b95a8"
DASH, PROFILES, FOOD_DB = "Dashboard", "Profiles", "Food Database"

# ---------------------------------------------------------------- icons
ICONS = {
    "grid": "<rect x='3' y='3' width='7' height='7' rx='1.5'/><rect x='14' y='3' width='7' height='7' rx='1.5'/><rect x='3' y='14' width='7' height='7' rx='1.5'/><rect x='14' y='14' width='7' height='7' rx='1.5'/>",
    "users": "<circle cx='9' cy='8' r='3.5'/><path d='M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6'/><path d='M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.3c2 .7 3.5 2.5 3.5 5.7'/>",
    "flame": "<path d='M12 22c4 0 7-2.8 7-6.8 0-3-1.8-5-3.4-6.7-.4 1.6-1.4 2.6-2.4 3C13.6 8.4 12.4 4.6 9.5 2c.2 3.6-1.6 5.3-3 7.3C5.2 11.2 5 13 5 15.2 5 19.2 8 22 12 22z'/>",
    "dumb": "<path d='M6.5 6.5v11M17.5 6.5v11M3 9v6M21 9v6M6.5 12h11'/>",
    "bolt": "<path d='M13 2 4 14h7l-1 8 9-12h-7z'/>",
    "bowl": "<path d='M3 11h18a9 9 0 0 1-18 0zM8 3c0 2 1.5 2 1.5 4M12 3c0 2 1.5 2 1.5 4M16 3c0 2 1.5 2 1.5 4'/>",
    "user": "<circle cx='12' cy='8' r='4'/><path d='M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7'/>",
    "target": "<circle cx='12' cy='12' r='9'/><circle cx='12' cy='12' r='5'/><circle cx='12' cy='12' r='1'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    "chart": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
}


def icon(name, size=20, color="currentColor"):
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' "
            f"stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>{ICONS[name]}</svg>")


def html(s):
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def section(title, ic):
    html(f"<div class='h2'><span class='ib'>{icon(ic, 18)}</span>{title}</div>")


# ---------------------------------------------------------------- styling & animations
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,.stApp{font-family:'Inter',sans-serif;font-variant-numeric:tabular-nums}
.stApp{background:#0b0f19;background-image:radial-gradient(600px 300px at 80% -5%,#b6f50014,transparent),radial-gradient(500px 300px at 0 100%,#2f7bff12,transparent);color:#e5e7eb}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden}
.block-container{max-width:1050px;padding-top:1.5rem}

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:linear-gradient(180deg,#141b2b,#0f1522);
    border:1px solid #1f293d!important;
    border-radius:18px;
    box-shadow:0 12px 32px #00000050;
    animation:rise .6s cubic-bezier(0.16, 1, 0.3, 1) both;
    transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{
    border-color:#2d3b57!important;
    transform:translateY(-3px);
    box-shadow:0 16px 40px #00000070;
}

@keyframes rise{from{opacity:0;transform:translateY(16px)}}

h1,h2,h3,p,label,span,div{color:#e5e7eb}
.mut{color:#8b95a8!important;font-size:13px}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.top h1{margin:0;font-size:26px;font-weight:700;letter-spacing:-.3px;padding:0}
.who{display:flex;align-items:center;gap:10px;font-weight:600}
.dot{width:9px;height:9px;border-radius:50%;background:#b6f500;animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 #b6f500aa}70%,100%{box-shadow:0 0 0 9px #b6f50000}}
.av{width:38px;height:38px;border:2px solid #8b95a8;border-radius:50%;display:grid;place-items:center;transition:0.3s}
.av:hover{border-color:#b6f500;color:#b6f500}
.h2{display:flex;align-items:center;gap:10px;font-size:16px;font-weight:600;margin-bottom:12px}
.ib{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:#b6f50014;color:#b6f500;border:1px solid #b6f50030;transition:0.3s}
.ib:hover{background:#b6f50030;transform:scale(1.05)}
.prog{display:flex;gap:18px;align-items:center}
.ring{position:relative;width:96px;height:96px;flex:none}
.ring svg{transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:9;stroke-linecap:round}
.ring .t{stroke:#1e2638}
.ring .v{stroke:#b6f500;stroke-dasharray:263.9;stroke-dashoffset:var(--off);animation:fill 1.4s cubic-bezier(.2,.8,.2,1);filter:drop-shadow(0 0 6px #b6f50088)}
@keyframes fill{from{stroke-dashoffset:263.9}}
.ring span{position:absolute;inset:0;display:grid;place-items:center}
.pinfo{flex:1}.big{font-size:22px;font-weight:700}
.bar{height:8px;background:#1e2638;border-radius:9px;overflow:hidden;margin:8px 0}
.bar i{display:block;height:100%;background:#b6f500;border-radius:9px;animation:grow 1.4s cubic-bezier(.2,.8,.2,1)}
@keyframes grow{from{width:0}}
.item{display:flex;align-items:center;gap:12px;padding:8px 0;animation:rise .4s both;transition:0.2s}
.item:hover{transform:translateX(4px)}
.tag{width:10px;height:10px;border-radius:50%;flex:none}
.item b{text-transform:capitalize}

.stButton>button{border-radius:12px;background:#0f1522;color:#e5e7eb;border:1px solid #1f293d;font-weight:600;transition:all 0.3s cubic-bezier(0.16, 1, 0.3, 1)}
.stButton>button:hover{border-color:#2f7bff;color:#2f7bff;transform:translateY(-2px);box-shadow:0 6px 16px #2f7bff22}

.stButton>button[kind="primary"], div.stFormSubmitButton>button, button[kind="primary"] {
    background-color: #b6f500 !important;
    color: #0b0f19 !important;
    border: none !important;
    font-weight: 800 !important;
}
.stButton>button[kind="primary"] p, div.stFormSubmitButton>button p, button[kind="primary"] p,
.stButton>button[kind="primary"] span, div.stFormSubmitButton>button span, button[kind="primary"] span {
    color: #0b0f19 !important;
    font-weight: 800 !important;
}

.stButton>button[kind="primary"]:hover, div.stFormSubmitButton>button:hover, button[kind="primary"]:hover {
    background-color: #c8ff2e !important;
    color: #0b0f19 !important;
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 8px 24px #b6f50055 !important;
}

.stTextInput input,.stNumberInput input,div[data-baseweb="select"]>div{background:#0d1320!important;border-color:#1f293d!important;border-radius:11px!important;transition:0.3s}
.stTextInput input:focus,.stNumberInput input:focus{border-color:#b6f500!important;box-shadow:0 0 10px #b6f50033}
</style>""", unsafe_allow_html=True)


def add_log():
    ss = st.session_state
    name, grams = ss.fn.strip().lower(), ss.fg
    if not name:
        ss.flash = "Please select a food name."
        return
    food = db.get_food_item(name)
    if not food:
        ss.flash = f"Food '{name}' not found in database."
        return
    db.add_daily_log(ss.active, name, grams, food[0] / 100 * grams, food[1] / 100 * grams, "Meal")
    if "fn" in ss:
        del ss["fn"]
    ss.flash = f"Logged {grams:g} g of {name}."


def ring(label, ic, val, target, unit):
    pct = min(val / target, 1) if target else 0
    return (f"<div class='prog'><div class='ring'><svg viewBox='0 0 96 96' width='96' height='96'>"
            f"<circle class='t' cx='48' cy='48' r='42'/><circle class='v' cx='48' cy='48' r='42' style='--off:{263.9 * (1 - pct):.1f}'/></svg>"
            f"<span>{icon(ic, 34, LIME)}</span></div><div class='pinfo'><div class='mut'>{label}</div>"
            f"<div class='big'>{val:,.1f} {unit}</div><div class='bar'><i style='width:{pct * 100:.0f}%'></i></div>"
            f"<div class='mut'>of {target:g} {unit} · {pct * 100:.0f}%</div></div></div>")


def header(title, name):
    cols = st.columns([2, 2.2, 1.2])
    with cols[0]:
        html(f"<div class='top'><div><h1>{title}</h1><div class='mut'>{date.today():%A, %d %B}</div></div></div>")
    with cols[1]:
        b1, b2, b3 = st.columns(3)
        if b1.button("Dashboard", use_container_width=True, type="primary" if st.session_state.get("page") == DASH else "secondary"):
            st.session_state.page = DASH
            st.rerun()
        if b2.button("Profiles", use_container_width=True, type="primary" if st.session_state.get("page") == PROFILES else "secondary"):
            st.session_state.page = PROFILES
            st.rerun()
        if b3.button("Food DB", use_container_width=True, type="primary" if st.session_state.get("page") == FOOD_DB else "secondary"):
            st.session_state.page = FOOD_DB
            st.rerun()
    with cols[2]:
        html(f"<div class='who' style='justify-content: flex-end;'>{name}<span class='dot'></span><span class='av'>{icon('user', 20)}</span></div>")


# ---------------------------------------------------------------- database & session setup
profiles = db.get_all_profiles()
names = [p[0] for p in profiles]

st.session_state.setdefault("fg", 100.0)
st.session_state.setdefault("fn", "")
st.session_state.setdefault("page", DASH)

if names:
    if "active" not in st.session_state or st.session_state.active not in names:
        st.session_state.active = names[0]
else:
    st.session_state.page = PROFILES

page = st.session_state.get("page", DASH)
active_name = st.session_state.get("active")
prof = next((p for p in profiles if p[0] == active_name), profiles[0] if profiles else None)

# ================================================================ PAGE 1: DASHBOARD
if page == DASH and prof:
    name, weight, height, goal, tp, tc = prof
    header(DASH, f"{name} · {goal}")
    if "flash" in st.session_state:
        st.toast(st.session_state.pop("flash"))

    total_p, total_c = db.get_today_summary(name)
    with st.container(border=True):
        section("Daily progress", "target")
        c1, c2 = st.columns(2)
        c1.markdown(ring("Protein", "dumb", total_p, tp, "g").replace("\n", ""), unsafe_allow_html=True)
        c2.markdown(ring("Calories", "flame", total_c, tc, "kcal").replace("\n", ""), unsafe_allow_html=True)

    with st.container(border=True):
        section("Food logging", "bowl")
        all_food_items = [f[0] for f in db.get_all_foods()]
        
        col_f, col_g, col_btn = st.columns([3, 1.5, 1.2])
        selected_food = col_f.selectbox("Select food item", [""] + all_food_items, key="fn")
        grams = col_g.number_input("Grams", min_value=1.0, step=10.0, key="fg")
        
        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Add to log", type="primary", use_container_width=True):
                add_log()
                st.rerun()

    with st.container(border=True):
        section("Today’s food history", "clock")
        logs = db.get_today_logs(name)
        if not logs:
            st.caption("No food logged for today yet.")
        for lid, meal, food, g, p, c in logs:
            left, right = st.columns([14, 1])
            left.markdown(
                f"<div class='item'><span class='tag' style='background:{LIME}'></span>"
                f"<div style='flex:1'><b>{food}</b><div class='mut'>{g:g} g</div></div>"
                f"<div><span style='color:{LIME}'>{p:.1f} g</span> · <span style='color:{BLUE}'>{c:.0f} kcal</span></div></div>",
                unsafe_allow_html=True)
            if right.button("✕", key=f"del{lid}"):
                db.delete_log(lid)
                st.rerun()

    with st.container(border=True):
        section("Weekly nutrition", "chart")
        v1, v2 = st.columns([3, 1])
        view = v1.radio("Series", ["Both", "Protein", "Calories"], horizontal=True, label_visibility="collapsed")
        days = v2.selectbox("Range", [7, 14], format_func=lambda d: f"Last {d} days", label_visibility="collapsed")

        totals = db.get_range_totals(name, days)
        rows = []
        for i in range(days - 1, -1, -1):
            d = date.today() - timedelta(days=i)
            p, c = totals.get(d.isoformat(), (0, 0))
            if view in ("Both", "Protein"):
                rows.append(dict(Date=pd.Timestamp(d), Series="Protein", Percent=p / tp * 100 if tp else 0, Actual=round(p, 1), Unit="g"))
            if view in ("Both", "Calories"):
                rows.append(dict(Date=pd.Timestamp(d), Series="Calories", Percent=c / tc * 100 if tc else 0, Actual=round(c), Unit="kcal"))
        df = pd.DataFrame(rows)

        if not df.empty:
            base = alt.Chart(df).encode(
                x=alt.X("Date:T", title=None, scale=alt.Scale(nice=False, padding=18),
                        axis=alt.Axis(format="%a" if days == 7 else "%d", tickCount=days, labelAngle=0,
                                      labelColor=MUTED, labelFontSize=12, grid=True, gridDash=[4, 5],
                                      gridColor="#1f293d", domain=False, ticks=False)),
                y=alt.Y("Percent:Q", title=None, axis=None,
                        scale=alt.Scale(domain=[0, max(110, df.Percent.max() * 1.15) if not df.empty else 110])),
                color=alt.Color("Series:N", legend=None,
                                scale=alt.Scale(domain=["Protein", "Calories"], range=[LIME, BLUE])))
            goal_line = alt.Chart(pd.DataFrame({"y": [100]})).mark_rule(
                strokeDash=[6, 6], color=MUTED, opacity=.5).encode(y="y:Q")
            chart = (base.mark_area(interpolate="monotone", opacity=.16)
                     + base.mark_line(interpolate="monotone", strokeWidth=3)
                     + base.mark_point(filled=True, size=90, opacity=1, stroke="#121826", strokeWidth=2).encode(
                         tooltip=[alt.Tooltip("Date:T", format="%a %d %b"), "Series:N",
                                  alt.Tooltip("Actual:Q"), "Unit:N", alt.Tooltip("Percent:Q", format=".0f", title="% of goal")])
                     + goal_line).properties(height=280).configure_view(strokeWidth=0).configure(background="transparent")
            st.altair_chart(chart, use_container_width=True, theme=None)
        else:
            st.info("No data available for the selected range.")
        st.caption("Both lines show % of your daily goal. The dashed line is 100%.")

# ================================================================ PAGE 2: PROFILES ONLY
elif page == PROFILES:
    header(PROFILES, prof[0] if prof else "New user")
    
    # Quick Profile Switcher Box for multi-user support
    if profiles:
        with st.container(border=True):
            section("Switch active profile", "users")
            selected_active = st.selectbox("Select profile to view/edit", names, index=names.index(active_name) if active_name in names else 0)
            if selected_active != active_name:
                st.session_state.active = selected_active
                st.rerun()

    with st.container(border=True):
        section("Setup / update profile (Weight Gainer)", "user")
        cur = prof or ("Thanuka", 63.0, 175.0, "Weight Gain", 126.0, 2400.0)
        
        with st.form("profile_form"):
            f1, f2 = st.columns(2)
            pname = f1.text_input("Unique profile name", value=cur[0])
            weight = f2.number_input("Body weight (kg)", value=float(cur[1]), min_value=20.0, max_value=250.0, step=0.5)
            
            height = st.number_input("Height (cm)", value=float(cur[2]), min_value=100.0, max_value=250.0, step=1.0)
            
            st.info("💡 **Weight Gainer Formula:** Protein target = Weight × 2 (g). Maintenance calories estimated automatically with +200 kcal added for surplus.")
            
            submitted = st.form_submit_button("Save & Calculate Targets")

        if submitted:
            clean_pname = pname.strip()
            if clean_pname:
                calc_protein = weight * 2.0
                est_maintenance = (10 * weight) + (6.25 * height) - (5 * 22) + 5
                calc_calories = est_maintenance + 200
                
                db.save_user_profile(clean_pname, weight, height, "Weight Gain", calc_protein, calc_calories)
                st.session_state.active = clean_pname
                st.success(f"Profile saved! Target Protein set to {calc_protein:.0f}g, Target Calories set to {calc_calories:.0f} kcal.")
                st.rerun()
            else:
                st.warning("Please enter a unique profile name.")

    with st.container(border=True):
        section("All saved profiles", "users")
        if not profiles:
            st.caption("No profiles created yet.")
        for n, w, h, g, p, c in profiles:
            l, r = st.columns([10, 1])
            l.markdown(f"<div class='item'><span class='ib'>{icon('user', 18)}</span><div><b>{n}</b>"
                       f"<div class='mut'>{w:g} kg · {h:g} cm · Goal: {g} · Protein: {p:g}g · Calories: {c:g} kcal</div></div></div>",
                       unsafe_allow_html=True)
            if r.button("🗑️", key=f"dp{n}"):
                db.delete_profile(n)
                st.rerun()

# ================================================================ PAGE 3: FOOD DATABASE ONLY
else:
    header(FOOD_DB, prof[0] if prof else "New user")
    with st.container(border=True):
        section("Manual food database (per 100 g)", "bowl")
        with st.form("food_db_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([3, 1.5, 1.5])
            fname = f1.text_input("Food name")
            fprot = f2.number_input("Protein (g) per 100g", min_value=0.0, step=0.1)
            fcal = f3.number_input("Calories (kcal) per 100g", min_value=0.0, step=1.0)
            
            submitted_food = st.form_submit_button("Add food to database")

        if submitted_food and fname.strip():
            clean_name = fname.strip().lower()
            db.add_new_food(clean_name, fprot, fcal)
            st.success(f"Added '{clean_name}' successfully!")
            st.rerun()
            
        all_foods = db.get_all_foods()
        for f_name, f_prot, f_cal in all_foods:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.markdown(f"**{f_name}**")
            col2.markdown(f"<span style='color:#b6f500'>{f_prot} g</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#2f7bff'>{f_cal} kcal</span>", unsafe_allow_html=True)
            if col4.button("🗑️", key=f"del_food_{f_name}"):
                db.delete_food_item(f_name)
                st.success(f"Deleted '{f_name}'")
                st.rerun()
