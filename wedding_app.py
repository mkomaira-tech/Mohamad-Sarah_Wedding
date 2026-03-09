import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
import qrcode
import requests
from io import BytesIO
from PIL import Image
from supabase import create_client, Client

# =========================================================
# إعداد Supabase
# =========================================================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# =========================================================
# دوال قاعدة البيانات
# =========================================================
def load_db():
    response = supabase.table("guests").select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df = df.rename(columns={
            "name": "الاسم", "side": "الجهة",
            "companions": "عدد المرافقين",
            "total_persons": "إجمالي الأشخاص",
            "table_number": "رقم الطاولة"
        })
        cols = ["الاسم","الجهة","عدد المرافقين","إجمالي الأشخاص","رقم الطاولة"]
        return df[[c for c in cols if c in df.columns]]
    return pd.DataFrame(columns=["الاسم","الجهة","عدد المرافقين","إجمالي الأشخاص","رقم الطاولة"])

def guest_exists(name):
    r = supabase.table("guests").select("name").eq("name", name.strip()).execute()
    return len(r.data) > 0

def add_guest(name, side, companions, total):
    supabase.table("guests").insert({
        "name": name.strip(), "side": side,
        "companions": companions, "total_persons": total,
        "table_number": "قيد الانتظار ⏳"
    }).execute()

def update_table_number(name, table_num):
    supabase.table("guests").update({"table_number": table_num}).eq("name", name).execute()

def delete_guest(name):
    supabase.table("guests").delete().eq("name", name).execute()

def get_guest_row(name):
    r = supabase.table("guests").select("*").eq("name", name.strip()).execute()
    return r.data[0] if r.data else None

# =========================================================
# دوال الصور
# =========================================================
BUCKET = "wedding-photos"

def upload_photo(file_bytes, filename):
    try:
        supabase.storage.from_(BUCKET).upload(
            filename, file_bytes,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )
        return True
    except Exception as e:
        st.error(f"خطأ في رفع الصورة: {e}")
        return False

def get_all_photos():
    try:
        files = supabase.storage.from_(BUCKET).list()
        return [
            supabase.storage.from_(BUCKET).get_public_url(f["name"])
            for f in files if f.get("name")
        ]
    except Exception:
        return []

# =========================================================
# إشعار Telegram
# =========================================================
def send_telegram_notification(guest_name, side, total):
    try:
        token   = st.secrets["telegram"]["bot_token"]
        chat_id = st.secrets["telegram"]["chat_id"]
        msg = (
            f"🎊 *ضيف جديد سجّل حضوره!*\n\n"
            f"👤 الاسم: {guest_name}\n"
            f"📍 الجهة: {side}\n"
            f"👥 الإجمالي: {total} أشخاص"
        )
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
            timeout=5
        )
    except Exception:
        pass

# =========================================================
# CSS مشترك - متجاوب مع الموبايل
# =========================================================
MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@300;400;700;900&display=swap');

:root {
    --gold: #D4AF37;
    --gold-light: #F3E5AB;
    --gold-dim: rgba(212,175,55,0.15);
    --bg-card: rgba(255,255,255,0.04);
    --bg-dark: rgba(10,15,30,0.88);
    --text: #F1F5F9;
    --text-muted: #94A3B8;
    --radius: 18px;
}

.stApp {
    background-image: url("https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=2070");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: var(--bg-dark);
    z-index: 0;
}
header, #MainMenu, footer { visibility: hidden; }
.main .block-container {
    z-index: 1;
    position: relative;
    padding: 0.5rem 1rem 3rem;
    max-width: 860px !important;
    margin: 0 auto !important;
}

h1 { font-family: 'Amiri', serif !important; color: var(--gold) !important; text-align: center; margin: 0 !important; }
h2 { font-family: 'Amiri', serif !important; color: var(--gold) !important; font-size: clamp(1.5rem,5vw,2.2rem) !important; text-align: center; margin: 1.5rem 0 1rem !important; }
h3 { font-family: 'Cairo', sans-serif !important; color: var(--text) !important; font-size: clamp(0.85rem,2.5vw,1.1rem) !important; font-weight: 300 !important; text-align: center; letter-spacing: 1px; }
p  { font-family: 'Cairo', sans-serif !important; color: var(--text-muted) !important; font-size: clamp(0.85rem,2vw,1rem) !important; text-align: center; }

.card {
    background: var(--bg-card);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius);
    padding: clamp(12px,3.5vw,26px);
    margin: 12px 0;
    box-shadow: 0 6px 28px rgba(0,0,0,0.4);
}

div.stButton > button {
    background: linear-gradient(135deg, var(--gold), var(--gold-light)) !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 9px 18px !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(212,175,55,0.3) !important;
    transition: all 0.25s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 20px rgba(212,175,55,0.55) !important;
}
div.stButton > button p {
    color: #000 !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 900 !important;
    font-size: clamp(0.85rem,2vw,1rem) !important;
    margin: 0 !important;
}

div[data-baseweb="tab-list"] {
    gap: 5px;
    justify-content: center;
    background: rgba(0,0,0,0.22);
    padding: 7px;
    border-radius: 50px;
    flex-wrap: wrap;
    margin-bottom: 1.2rem;
}
button[data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 50px !important;
    border: 1px solid rgba(212,175,55,0.2) !important;
    color: var(--text-muted) !important;
    padding: 6px 12px !important;
    font-family: 'Cairo', sans-serif !important;
    font-size: clamp(0.7rem,1.8vw,0.88rem) !important;
    transition: 0.2s !important;
    white-space: nowrap;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg,var(--gold),var(--gold-light)) !important;
    color: #000 !important;
    font-weight: 900 !important;
    border: none !important;
}

.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(212,175,55,0.28) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Cairo', sans-serif !important;
}
.stTextInput label, .stTextArea label, div[data-testid="stSelectboxLabel"] {
    color: var(--text-muted) !important;
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.88rem !important;
}

@keyframes glow {
    0%,100% { text-shadow: 0 0 10px rgba(212,175,55,0.35); }
    50%      { text-shadow: 0 0 26px rgba(212,175,55,0.8), 0 0 45px rgba(212,175,55,0.25); }
}
.hero-title {
    font-size: clamp(2.2rem,9vw,4.2rem) !important;
    animation: glow 3s ease-in-out infinite;
    line-height: 1.1 !important;
}

.tl { direction:rtl; padding-right:30px; position:relative; margin:8px 0 18px; }
.tl::before { content:''; position:absolute; top:0; right:10px; height:100%; width:3px; background:linear-gradient(to bottom,var(--gold),var(--gold-light),var(--gold)); border-radius:4px; }
.tl-item { position:relative; margin-bottom:22px; }
.tl-dot  { position:absolute; right:-25px; top:12px; width:18px; height:18px; background:var(--gold); border:3px solid #0F172A; border-radius:50%; box-shadow:0 0 10px rgba(212,175,55,0.8); z-index:2; }
.tl-box  { background:rgba(15,23,42,0.8); backdrop-filter:blur(10px); border:1px solid rgba(212,175,55,0.25); border-right:4px solid var(--gold); padding:12px 16px; border-radius:12px; transition:0.3s; }
.tl-box:hover { transform:translateX(-5px); }
.tl-box h4 { color:var(--gold) !important; font-family:'Amiri',serif !important; font-size:1.3rem !important; margin:0 0 4px !important; }
.tl-box p  { color:#fff !important; font-family:'Cairo',sans-serif !important; font-size:0.95rem !important; margin:0 !important; text-align:right !important; font-weight:600 !important; }

.wish-box { background:linear-gradient(135deg,rgba(225,29,72,0.1),rgba(147,51,234,0.1)); border:1.5px dashed #E11D48; border-radius:var(--radius); padding:clamp(16px,4vw,26px); text-align:center; margin-bottom:18px; }
.wish-btn { display:inline-block; background:linear-gradient(135deg,#E11D48,#9333EA); color:#fff !important; font-family:'Cairo',sans-serif !important; font-weight:900 !important; font-size:clamp(0.95rem,2.5vw,1.1rem) !important; text-decoration:none !important; padding:11px 26px !important; border-radius:50px !important; margin-top:10px; transition:0.3s; box-shadow:0 6px 20px rgba(225,29,72,0.35); }
.wish-btn:hover { transform:translateY(-3px) !important; }

.cal-link { display:block; background:rgba(255,255,255,0.06); border:1px solid var(--gold); color:var(--gold) !important; padding:9px 16px; border-radius:50px; text-decoration:none; font-family:'Cairo',sans-serif; font-weight:700; text-align:center; max-width:260px; margin:12px auto; transition:0.25s; font-size:0.9rem; }
.cal-link:hover { background:var(--gold-dim); }

@media(max-width:640px) {
    .main .block-container { padding: 0.4rem 0.5rem 2rem; }
}
</style>
"""

# =========================================================
# إعداد الصفحة
# =========================================================
st.set_page_config(
    page_title="Mohammad & Sarah Wedding",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

query_params   = st.query_params
ADMIN_PASSWORD = st.secrets["admin"]["password"]
BASE_URL       = "https://mohamad-sarahwedding-pycf9neap43w7zh9pewmhu.streamlit.app/"  # ← غيّر لرابطك
WISH_MONEY_LINK= "https://YOUR-WISHMONEY-LINK"           # ← غيّر لرابطك

# =========================================================
# 1. لوحة الأدمن  ← yoursite.app/?admin=كلمة_السر
# =========================================================
if query_params.get("admin") == ADMIN_PASSWORD:

    if "admin_filter" not in st.session_state:
        st.session_state.admin_filter = "الكل"

    st.markdown("""
<style>
/* خلفية اللوحة (Dark Mode Dashboard) */
.stApp { background: #070B14 !important; background-image: radial-gradient(circle at 50% 0%, #1A233A 0%, #070B14 80%) !important; }
.stApp::before { display: none; }

/* تنسيق الخطوط */
h1, h2, h3, p { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }

/* تصميم كروت الإحصائيات العلوية (KPI Cards) */
div[data-testid="column"] { padding: 0 10px; }
div[data-testid="column"] div.stButton > button {
    border-radius: 16px !important;
    height: 120px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.4) !important;
    width: 100% !important;
}
div[data-testid="column"] div.stButton > button:hover { transform: translateY(-5px) !important; filter: brightness(1.15); }
div[data-testid="column"] div.stButton > button p { font-family: 'Cairo', sans-serif !important; font-weight: 900 !important; font-size: 1.4rem !important; line-height: 1.6 !important; margin: 0 !important; }

/* كرت العريس (أزرق داكن/مضيء) */
div[data-testid="column"]:nth-child(1) div.stButton > button {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 58, 138, 0.3)) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    border-right: 5px solid #3B82F6 !important;
}
div[data-testid="column"]:nth-child(1) div.stButton > button p { color: #93C5FD !important; }

/* كرت العروس (وردي داكن/مضيء) */
div[data-testid="column"]:nth-child(2) div.stButton > button {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(157, 23, 77, 0.3)) !important;
    border: 1px solid rgba(236, 72, 153, 0.2) !important;
    border-right: 5px solid #EC4899 !important;
}
div[data-testid="column"]:nth-child(2) div.stButton > button p { color: #F9A8D4 !important; }

/* كرت الإجمالي (ذهبي داكن/مضيء) */
div[data-testid="column"]:nth-child(3) div.stButton > button {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(184, 134, 11, 0.3)) !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-right: 5px solid #D4AF37 !important;
}
div[data-testid="column"]:nth-child(3) div.stButton > button p { color: #FDE047 !important; }

/* الحاوية الزجاجية للجدول (Glassmorphism) */
.admin-table-container {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 25px;
    margin-top: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

/* شريط الفلتر النشط */
.active-filter-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #E2E8F0;
    padding: 8px 20px;
    border-radius: 30px;
    font-size: 1rem;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 20px;
}

/* أزرار الإجراءات (Primary & Secondary) */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 0 !important;
    font-size: 1.1rem !important;
    font-weight: bold !important;
    box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3) !important;
}
div.stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important; }

/* زر تحميل CSV وخروج */
div.stDownloadButton > button, div.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #cbd5e1 !important;
    border-radius: 50px !important;
    transition: 0.3s !important;
}
div.stDownloadButton > button:hover, div.stButton > button[kind="secondary"]:hover { background: rgba(255, 255, 255, 0.1) !important; color: #FFF !important; }
</style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:Amiri; margin: 20px 0 30px; text-shadow: 0 0 20px rgba(212,175,55,0.4);'>⚙️ غرفة تحكم MK Technology ⚙️</h1>", unsafe_allow_html=True)

    df = load_db()
    if not df.empty:
        count_groom = int(df[df['الجهة']=='جهة العريس 🤵']['إجمالي الأشخاص'].sum())
        count_bride = int(df[df['الجهة']=='جهة العروس 👰']['إجمالي الأشخاص'].sum())
        count_all   = int(df['إجمالي الأشخاص'].sum())

        # الكروت الثلاثة العلوية
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(f"🤵 العريس\n\n{count_groom} ضيف", use_container_width=True): st.session_state.admin_filter = "جهة العريس 🤵"
        with c2:
            if st.button(f"👰 العروس\n\n{count_bride} ضيف", use_container_width=True): st.session_state.admin_filter = "جهة العروس 👰"
        with c3:
            if st.button(f"👥 الإجمالي\n\n{count_all} ضيف", use_container_width=True): st.session_state.admin_filter = "الكل"

        filt = st.session_state.admin_filter
        view_df = df if filt=="الكل" else df[df['الجهة']==filt].copy()
        view_df = view_df.copy()
        view_df["حذف؟"] = False

        # الحاوية الزجاجية للبطاقات الذكية
        st.markdown("<div class='admin-table-container'>", unsafe_allow_html=True)
        
        # مؤشر الفلتر النشط
        filter_color = "#3B82F6" if "العريس" in filt else "#EC4899" if "العروس" in filt else "#D4AF37"
        st.markdown(f"<div style='text-align: center;'><div class='active-filter-badge' style='border-color: {filter_color};'>القائمة تعرض حالياً: <span style='color: {filter_color};'>{filt}</span></div></div>", unsafe_allow_html=True)

        # رسالة التلميح (أصبحت صندوقاً مضيئاً وواضحاً جداً)
        st.markdown("""
        <div style='background: rgba(212, 175, 55, 0.1); border-right: 4px solid #D4AF37; padding: 12px 15px; color: #FFFFFF; font-family: Cairo; margin-bottom: 25px; border-radius: 8px; direction: rtl; line-height: 1.6;'>
            💡 <b>تلميح للإدارة:</b> اكتب رقم الطاولة في المربع مباشرة. ولحذف ضيف، ضع علامة الصح (✓) تحت عمود (إجراء)، ثم اضغط زر الحفظ الأخضر بالأسفل.
        </div>
        """, unsafe_allow_html=True)

        # إضافة ستايل لتوسيط النص داخل مربع الطاولة وتلوينه
        st.markdown("""
        <style>
        .admin-table-container input { text-align: center !important; font-weight: bold !important; color: #D4AF37 !important; }
        </style>
        """, unsafe_allow_html=True)

        # ترويسة القائمة (Header) بخلفية بارزة لتفصلها عن البيانات
        st.markdown("""
        <div style='display: flex; background: rgba(0,0,0,0.5); padding: 12px 10px; border-radius: 10px; color: #94A3B8; font-size: 0.95rem; font-weight: bold; margin-bottom: 15px; direction: rtl;'>
            <div style='flex: 4;'>👤 بيانات الضيف</div>
            <div style='flex: 2; text-align: center;'>👥 العدد</div>
            <div style='flex: 3; text-align: center;'>🪑 الطاولة</div>
            <div style='flex: 1; text-align: center;'>🗑️ إجراء</div>
        </div>
        """, unsafe_allow_html=True)

        # توليد البطاقات الذكية لكل ضيف بمسافات موزونة
        for index, row in view_df.iterrows():
            g_name = row["الاسم"]
            g_side = row["الجهة"]
            g_total = row["إجمالي الأشخاص"]
            g_table = row["رقم الطاولة"]

            icon = "🤵" if "العريس" in g_side else "👰" if "العروس" in g_side else "👤"

            with st.container():
                # نسب جديدة للأعمدة لمنع التداخل [4: الاسم، 2: العدد، 3: الطاولة، 1: الحذف]
                c1, c2, c3, c4 = st.columns([4, 2, 3, 1])
                
                with c1:
                    # زيادة البادينغ ليوازي ارتفاع حقل النص
                    st.markdown(f"<div style='padding-top: 10px; line-height: 1.2; direction: rtl;'><b style='color:#FFFFFF; font-size:1.05rem;'>{icon} {g_name}</b></div>", unsafe_allow_html=True)
                
                with c2:
                    st.markdown(f"<div style='text-align:center; padding-top: 10px; color:#E2E8F0; font-weight:bold; font-size:1.1rem;'>{g_total}</div>", unsafe_allow_html=True)
                
                with c3:
                    st.text_input("الطاولة", value=g_table, key=f"tbl_{g_name}", label_visibility="collapsed")
                
                with c4:
                    st.markdown("<div style='padding-top: 8px; text-align:center; display:flex; justify-content:center;'>", unsafe_allow_html=True)
                    st.checkbox("حذف", key=f"del_{g_name}", label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                # فاصل خفيف بين الضيوف
                st.markdown("<hr style='margin: 4px 0 16px 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # أزرار الإجراءات السفلية
        col_save, col_export = st.columns([2, 1])
        with col_save:
            if st.button("💾 حفظ التعديلات الشاملة", type="primary", use_container_width=True):
                for index, row in view_df.iterrows():
                    name = row["الاسم"]
                    new_table = st.session_state.get(f"tbl_{name}", row["رقم الطاولة"])
                    to_delete = st.session_state.get(f"del_{name}", False)

                    if to_delete:
                        delete_guest(name)
                    elif new_table != row["رقم الطاولة"]:
                        update_table_number(name, new_table)
                        
                st.success("✅ تم تحديث قاعدة البيانات بنجاح!")
                st.rerun()
                
        with col_export:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 تحميل الإكسيل", data=csv, file_name="wedding_guests.csv", mime="text/csv", use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True) # إغلاق الحاوية الزجاجية


    else:
        st.info("لا يوجد ضيوف مسجلون بعد في قاعدة البيانات.")

    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
    col_empty, col_exit, col_empty2 = st.columns([1, 1, 1])
    with col_exit:
        if st.button("🚪 إغلاق لوحة التحكم", use_container_width=True):
            st.query_params.clear()
            st.rerun()

# =========================================================
# 2. تذكرة VIP
# =========================================================
elif "vip" in query_params:
    guest_name = urllib.parse.unquote(query_params.get("name",""))
    row        = get_guest_row(guest_name)
    if row:
        guests_count = row.get("companions","—")
        guest_side   = row.get("side","—")
        table_num    = row.get("table_number","قيد الانتظار ⏳")
    else:
        guests_count, guest_side, table_num = "—","—","قيد الانتظار ⏳"

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700;900&display=swap');
.stApp { background:linear-gradient(135deg,#0a0a1a,#1a0a2e,#0a1a0a) !important; background-image:none !important; }
.stApp::before { display:none; }
header { visibility:hidden; }
.main .block-container { display:flex; flex-direction:column; align-items:center; padding-top:2rem; }
@keyframes fadeUp { from{transform:translateY(35px);opacity:0;} to{transform:translateY(0);opacity:1;} }
.ticket { background:rgba(255,255,255,0.04); backdrop-filter:blur(20px); border:1px solid rgba(212,175,55,0.4); border-radius:24px; padding:clamp(18px,5vw,36px); text-align:center; max-width:440px; width:92%; animation:fadeUp 0.85s ease forwards; box-shadow:0 18px 55px rgba(212,175,55,0.14); }
.vip-badge { background:linear-gradient(135deg,#D4AF37,#F3E5AB); color:#000; padding:4px 16px; border-radius:50px; font-family:'Cairo',sans-serif; font-weight:900; font-size:0.9rem; display:inline-block; margin-bottom:14px; }
h1 { font-family:'Amiri',serif !important; color:#D4AF37 !important; font-size:clamp(1.7rem,6vw,2.4rem) !important; margin:5px 0 !important; }
.info-row { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-bottom:1px solid rgba(212,175,55,0.12); direction:rtl; }
.info-row:last-child { border-bottom:none; }
.info-label { color:#64748B; font-family:'Cairo',sans-serif; font-size:0.88rem; }
.info-value { color:#F1F5F9; font-family:'Cairo',sans-serif; font-weight:700; font-size:0.95rem; }
.table-val  { color:#D4AF37; font-size:1.2rem !important; background:rgba(212,175,55,0.12); padding:2px 12px; border-radius:8px; }
div.stButton > button { background:linear-gradient(135deg,#D4AF37,#F3E5AB) !important; border:none !important; border-radius:50px !important; margin-top:8px; }
div.stButton > button p { color:#000 !important; font-family:'Cairo',sans-serif !important; font-weight:900 !important; }
</style>""", unsafe_allow_html=True)

    st.balloons()
    st.markdown(f"""
<div class="ticket">
    <div class="vip-badge">✨ VIP PASS ✨</div>
    <h1>أهلاً بك يا {guest_name}</h1>
    <p style="color:#64748B;font-family:'Cairo',sans-serif;font-size:0.88rem;margin:3px 0 14px;">تذكرتك مفعّلة وجاهزة</p>
    <div style="background:rgba(0,0,0,0.18);border-radius:14px;padding:4px 14px;">
        <div class="info-row"><span class="info-label">المدعو من</span><span class="info-value">{guest_side}</span></div>
        <div class="info-row"><span class="info-label">المرافقون</span><span class="info-value">{guests_count}</span></div>
        <div class="info-row"><span class="info-label">رقم الطاولة</span><span class="info-value table-val">{table_num}</span></div>
        <div class="info-row"><span class="info-label">الحالة</span><span class="info-value" style="color:#4ade80;">✔️ مؤكد</span></div>
    </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↩️ العودة للموقع"):
        st.query_params.clear()
        st.rerun()

# =========================================================
# 3. الموقع الرئيسي
# =========================================================
else:
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

    # مقدمة سينمائية
    components.html("""<script>
const pd=window.parent.document;
if(!pd.getElementById('cin')){
    const d=pd.createElement('div');
    d.id='cin';
    d.style.cssText='position:fixed;inset:0;background:#000;z-index:999999;transition:opacity 1.4s;display:flex;flex-direction:column;justify-content:center;align-items:center;';
    d.innerHTML=`
        <video autoplay muted playsinline style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.7;">
            <source src="https://videos.pexels.com/video-files/3195394/3195394-uhd_2560_1440_25fps.mp4" type="video/mp4">
        </video>
        <div style="position:relative;z-index:2;text-align:center;padding:0 20px;">
            <h1 style="color:#D4AF37;font-family:'Amiri',serif;font-size:clamp(2.2rem,8vw,3.8rem);text-shadow:2px 2px 12px #000;margin:0;">محمد & سارة</h1>
            <p style="color:#F3E5AB;font-family:'Cairo',sans-serif;font-size:clamp(0.9rem,2.5vw,1rem);margin-top:8px;letter-spacing:3px;">٣١ مايو ٢٠٢٦</p>
        </div>
        <button onclick="this.closest('#cin').style.opacity='0';setTimeout(()=>this.closest('#cin').remove(),1400)"
            style="position:absolute;bottom:8%;padding:10px 28px;background:linear-gradient(135deg,#D4AF37,#F3E5AB);color:#000;font-weight:900;font-size:clamp(0.95rem,2.5vw,1.1rem);border:none;border-radius:50px;cursor:pointer;font-family:'Cairo',sans-serif;box-shadow:0 5px 18px rgba(212,175,55,0.5);">
            دخول للموقع 🤍
        </button>`;
    pd.body.appendChild(d);
    d.querySelector('video').onended=()=>{d.style.opacity='0';setTimeout(()=>d.remove(),1400);};
}
</script>""", width=0, height=0)

    st.markdown("""
<div style="text-align:center;padding:1rem 0 0.4rem;">
    <h1 class="hero-title">محمد & سارة</h1>
    <h3 style="margin-top:6px;margin-bottom:18px;">ندعوكم لمشاركتنا أجمل لحظات العمر</h3>
</div>""", unsafe_allow_html=True)

    tab_home, tab_rsvp, tab_gallery, tab_album, tab_house = st.tabs([
        "🏠 الرئيسية", "💌 دعوة وتهنئة", "📸 صورنا", "🎞️ ألبوم الزفاف", "🛋️ عشنا"
    ])

    # ══════════════ الرئيسية ══════════════
    with tab_home:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # ← استبدل
        with c2:
            st.image("https://images.unsplash.com/photo-1583939000240-69279c118671", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        cal_url = "https://calendar.google.com/calendar/render?action=TEMPLATE&text=حفل+زفاف+محمد+وسارة&dates=20260531T160000Z/20260531T210000Z&location=Sofia+Palace,+Rmeileh,+Lebanon"
        st.markdown(f'<a href="{cal_url}" target="_blank" class="cal-link">📅 أضف الموعد إلى تقويمك</a>', unsafe_allow_html=True)

        components.html("""<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;display:flex;justify-content:center;align-items:center;min-height:150px;}
.wrap{background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:18px 24px;display:flex;gap:clamp(14px,4vw,36px);flex-wrap:wrap;justify-content:center;}
.box{display:flex;flex-direction:column;align-items:center;min-width:50px;}
.num{font-size:clamp(1.8rem,6vw,3rem);font-weight:700;color:#D4AF37;line-height:1;text-shadow:0 0 16px rgba(212,175,55,0.5);}
.lbl{font-size:clamp(0.7rem,1.8vw,0.9rem);color:#E2E8F0;margin-top:3px;font-family:'Cairo',sans-serif;}
</style></head><body>
<div class="wrap">
    <div class="box"><span class="num" id="d">00</span><span class="lbl">يوم</span></div>
    <div class="box"><span class="num" id="h">00</span><span class="lbl">ساعة</span></div>
    <div class="box"><span class="num" id="m">00</span><span class="lbl">دقيقة</span></div>
    <div class="box"><span class="num" id="s">00</span><span class="lbl">ثانية</span></div>
</div>
<script>
const t=new Date("May 31, 2026 19:00:00").getTime();
setInterval(()=>{
    const x=t-Date.now();
    document.getElementById('d').textContent=String(Math.floor(x/864e5)).padStart(2,'0');
    document.getElementById('h').textContent=String(Math.floor(x%864e5/36e5)).padStart(2,'0');
    document.getElementById('m').textContent=String(Math.floor(x%36e5/6e4)).padStart(2,'0');
    document.getElementById('s').textContent=String(Math.floor(x%6e4/1e3)).padStart(2,'0');
},1000);
</script></body></html>""", height=175)

        st.markdown("<h2>جدول الليلة ⏳</h2>", unsafe_allow_html=True)
        st.markdown("""<div class="tl">
<div class="tl-item"><div class="tl-dot"></div><div class="tl-box"><h4>🕖 07:00 م</h4><p>استقبال الأحباب وبداية التجمع</p></div></div>
<div class="tl-item"><div class="tl-dot"></div><div class="tl-box"><h4>🕗 08:00 م</h4><p>الزفة الملكية ودخول العرسان</p></div></div>
<div class="tl-item"><div class="tl-dot"></div><div class="tl-box"><h4>🍽️ 09:30 م</h4><p>عشاء العرسان (بوفيه مفتوح)</p></div></div>
<div class="tl-item"><div class="tl-dot"></div><div class="tl-box"><h4>🎂 11:00 م</h4><p>قطع الكيكة وصنع الذكريات</p></div></div>
</div>""", unsafe_allow_html=True)

        st.markdown("<h2>موقع الحفل 📍</h2>", unsafe_allow_html=True)
        components.html("""<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700;900&family=Amiri:wght@700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;padding:6px;}
.wrap{border-radius:18px;overflow:hidden;border:1.5px solid rgba(212,175,55,0.45);box-shadow:0 10px 35px rgba(0,0,0,0.5);}
iframe{width:100%;height:clamp(240px,40vw,320px);border:0;display:block;}
.info{background:rgba(15,23,42,0.92);backdrop-filter:blur(10px);padding:14px 18px;direction:rtl;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;}
.venue{color:#D4AF37;font-family:'Amiri',serif;font-size:1.2rem;}
.loc{color:#64748B;font-family:'Cairo',sans-serif;font-size:0.82rem;margin-top:2px;}
.btn{background:linear-gradient(135deg,#D4AF37,#F3E5AB);color:#000 !important;font-family:'Cairo',sans-serif;font-weight:900;font-size:0.88rem;padding:8px 18px;border-radius:50px;text-decoration:none;white-space:nowrap;}
</style></head><body>
<div class="wrap">
    <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3322.993864119795!2d35.3934256764207!3d33.60546367332862!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x151ee52e784728f9%3A0xaa57f0e88d65b592!2sSofia%20Palace!5e0!3m2!1sen!2slb!4v1772620814491!5m2!1sen!2slb" allowfullscreen loading="lazy"></iframe>
    <div class="info">
        <div><div class="venue">Sofia Palace 🏛️</div><div class="loc">الرميلة، لبنان</div></div>
        <a href="https://maps.app.goo.gl/YZCjR4FNNa5tCE8G6" target="_blank" class="btn">🚗 اتجاهات</a>
    </div>
</div></body></html>""", height=370)

    # ══════════════ دعوة وتهنئة ══════════════
    with tab_rsvp:
        st.markdown("<h2>تأكيد الحضور 🎟️</h2>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns([3,2])
        with c1: rsvp_name  = st.text_input("الاسم الكريم", placeholder="مثال: أحمد خليل...")
        with c2: guest_side = st.selectbox("الجهة", ["جهة العريس 🤵","جهة العروس 👰"])
        guests_count = st.selectbox("عدد المرافقين (غير احتسابك)", [
            "بدون مرافقين","مرافق واحد","مرافقان","3 مرافقين","4 مرافقين"
        ])

        if st.button("تأكيد الحضور واستخراج التذكرة 🎫"):
            if rsvp_name:
                comp_map = {"بدون مرافقين":0,"مرافق واحد":1,"مرافقان":2,"3 مرافقين":3,"4 مرافقين":4}
                total    = 1 + comp_map.get(guests_count,0)
                enc      = urllib.parse.quote(rsvp_name.strip())
                tkt_url  = f"{BASE_URL}/?vip=true&name={enc}"

                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(tkt_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="#D4AF37", back_color="#0F172A")
                buf = BytesIO(); img.save(buf, format="PNG")

                if guest_exists(rsvp_name):
                    st.info(f"أهلاً بعودتك يا {rsvp_name}! تذكرتك جاهزة 👇")
                else:
                    add_guest(rsvp_name, guest_side, guests_count, total)
                    send_telegram_notification(rsvp_name, guest_side, total)
                    st.success(f"✅ تم تأكيد حضورك يا {rsvp_name}!")
                    st.balloons()

                row = get_guest_row(rsvp_name)
                cur_table = row["table_number"] if row else "قيد الانتظار ⏳"

                st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(30,41,59,.9),rgba(15,23,42,.9));border:1.5px dashed #D4AF37;padding:16px;border-radius:14px;text-align:center;margin-top:14px;">
    <p style="color:#D4AF37;font-family:'Amiri',serif;font-size:1.4rem;margin:0 0 4px;">تذكرة VIP 🌟</p>
    <p style="color:#E2E8F0;font-family:'Cairo',sans-serif;margin:0 0 3px;">الضيف: <b>{rsvp_name}</b></p>
    <p style="color:#475569;font-family:'Cairo',sans-serif;font-size:0.82rem;margin:0;">امسح الرمز يوم الحفل لعرض رقم طاولتك</p>
</div>""", unsafe_allow_html=True)

                _, mid, _ = st.columns([1,1,1])
                with mid: st.image(buf, use_container_width=True)

                wa_msg = f"✨ تذكرة زفاف محمد وسارة ✨\n\n👤 {rsvp_name}\n🎫 الطاولة: {cur_table}\n🔗 {tkt_url}\n\n🎁 Wish Money:\n{WISH_MONEY_LINK}"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" target="_blank" style="display:block;background:#25D366;color:#fff;text-align:center;padding:10px;border-radius:50px;text-decoration:none;font-family:\'Cairo\',sans-serif;font-weight:700;margin-top:10px;">💬 احفظ التذكرة عبر واتساب</a>', unsafe_allow_html=True)
            else:
                st.error("يرجى إدخال اسمك أولاً!")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h2>النقوط والتهاني 💌</h2>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"""<div class="wish-box">
<h3 style="color:#E11D48;font-family:'Amiri',serif;font-size:clamp(1.4rem,4vw,1.9rem);margin:0 0 7px;">💖 فرحتنا تكتمل بوجودكم</h3>
<p style="color:#E2E8F0 !important;font-family:'Cairo',sans-serif;line-height:1.8;margin:0;">مشاركتكم هي أكبر هدية 🤍<br>ولمن يرغب بإرسال النقوط إلكترونياً:</p>
<a href="{WISH_MONEY_LINK}" target="_blank" class="wish-btn">✨ إرسال النقوط عبر Wish Money ✨</a>
</div>""", unsafe_allow_html=True)

        gn = st.text_input("اسمك", key="gn")
        gm = st.text_area("اترك تهنئة من قلبك...", key="gm", height=85)
        if st.button("إرسال التهنئة 🕊️"):
            if gm:
                import random
                n = gn or "ضيفنا الغالي"
                st.info(random.choice([
                    f"شكراً لك يا {n}، كلماتك تلامس القلب 🤍",
                    f"وجودك معنا سيزيد فرحتنا يا {n} ✨",
                    f"أمنياتك الجميلة لن ننساها يا {n} 💍"
                ]), icon="💌")
            else:
                st.warning("لا تحرمنا من كلماتك الطيبة!")
        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════ صورنا ══════════════
    with tab_gallery:
        st.markdown("<h2>قصتنا في صور 📷</h2>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        photos = [
            ("https://images.unsplash.com/photo-1511285560929-80b456fea0bc","اللقاء الأول 🤍"),
            ("https://images.unsplash.com/photo-1544928147-79a2dbc1f389","يوم الخطوبة 💍"),
            ("https://images.unsplash.com/photo-1522673607200-164d1b6ce486","لحظات لا تنسى ✨"),
            ("https://images.unsplash.com/photo-1606800052052-a08af7148866","رحلتنا معاً ✈️"),
            ("https://images.unsplash.com/photo-1583939000240-69279c118671","عائلتنا الصغيرة 👨‍👩‍👧"),
            ("https://images.unsplash.com/photo-1620063994354-9ce535560b0e","في انتظار اليوم الكبير 🎉"),
        ]
        for i in range(0,len(photos),3):
            cols = st.columns(3)
            for j,col in enumerate(cols):
                if i+j < len(photos):
                    col.image(photos[i+j][0], caption=photos[i+j][1], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════ ألبوم الزفاف ══════════════
    with tab_album:
        st.markdown("<h2>ألبوم يوم الزفاف 🎞️</h2>", unsafe_allow_html=True)
        st.markdown("<p>شاركوا أجمل لحظاتكم — كل صورة ترفعونها ذكرى خالدة 🤍</p>", unsafe_allow_html=True)

        # رفع الصورة
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#D4AF37;text-align:center;margin-bottom:10px;'>📤 ارفع صورتك</h3>", unsafe_allow_html=True)
        uploader_name = st.text_input("اسمك (اختياري)", placeholder="مثال: أحمد وعائلته...", key="uname")
        uploaded = st.file_uploader(
            "اختر صورة أو التقطها مباشرة 📸",
            type=["jpg","jpeg","png"],
            label_visibility="collapsed"
        )
        if st.button("رفع الصورة ⬆️"):
            if uploaded:
                import time, re
                safe  = re.sub(r'[^a-zA-Z0-9._-]','_', uploader_name or "guest")
                fname = f"{safe}_{int(time.time())}_{uploaded.name}"
                with st.spinner("جارٍ الرفع..."):
                    if upload_photo(uploaded.read(), fname):
                        st.success("🎉 تم رفع صورتك بنجاح!")
                        st.balloons()
            else:
                st.warning("اختر صورة أولاً!")
        st.markdown("</div>", unsafe_allow_html=True)

        # الألبوم
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#D4AF37;text-align:center;margin-bottom:14px;'>🖼️ الألبوم الحي</h3>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            if st.button("🔄 تحديث الألبوم"):
                st.rerun()

        photo_urls = get_all_photos()
        if photo_urls:
            st.markdown(f"<p style='color:#4ADE80 !important;font-family:Cairo,sans-serif;text-align:center;'>{len(photo_urls)} صورة في الألبوم ✨</p>", unsafe_allow_html=True)
            for i in range(0, len(photo_urls), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i+j < len(photo_urls):
                        col.image(photo_urls[i+j], use_container_width=True)
        else:
            st.markdown("""
<div style="text-align:center;padding:35px 20px;">
    <div style="font-size:2.8rem;">📭</div>
    <p style="color:#475569 !important;margin-top:8px;font-family:'Cairo',sans-serif;">الألبوم فارغ حتى الآن...<br>كونوا أول من يرفع صورة! 🌟</p>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════ عشنا الصغير ══════════════
    with tab_house:
        st.markdown("<h2>عشنا الصغير 🛋️</h2>", unsafe_allow_html=True)
        st.markdown("<p>نظرة خاطفة على مملكتنا القادمة...</p>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.image("https://images.unsplash.com/photo-1600210492486-724fe5c67fb0", caption="زوايا دافئة 💡", use_container_width=True)
        with c2:
            st.image("https://images.unsplash.com/photo-1616594039964-ae9021a400a0", caption="غرفة النوم الرئيسية 🤍", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
<div style="text-align:center;margin-top:35px;padding-bottom:18px;">
    <p style="font-size:0.78rem !important;color:rgba(148,163,184,0.35) !important;letter-spacing:1px;">
        Designed by <span style="color:#D4AF37;font-weight:700;">MK Technology</span> © 2026
    </p>
</div>""", unsafe_allow_html=True)
