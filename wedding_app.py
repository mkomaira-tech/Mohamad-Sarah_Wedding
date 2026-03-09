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
    url = st.secrets["supabase"]["https://cdvotvobfynweyaouuyo.supabase.co"]   # ← ضع رابط مشروعك
    key = st.secrets["supabase"]["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkdm90dm9iZnlud2V5YW91dXlvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwMDI1OTcsImV4cCI6MjA4ODU3ODU5N30.-6PqZWUXbkdRhC8FWTIucwxMVusUa3uCl5x5qQlPphs"]   # ← ضع anon key
    return create_client(url, key)

supabase = init_supabase()

# =========================================================
# دوال قاعدة البيانات (Supabase)
# =========================================================
def load_db():
    response = supabase.table("guests").select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df = df.rename(columns={
            "name":         "الاسم",
            "side":         "الجهة",
            "companions":   "عدد المرافقين",
            "total_persons":"إجمالي الأشخاص",
            "table_number": "رقم الطاولة"
        })
        # احتفظ فقط بالأعمدة المطلوبة
        cols = ["الاسم","الجهة","عدد المرافقين","إجمالي الأشخاص","رقم الطاولة"]
        return df[[c for c in cols if c in df.columns]]
    return pd.DataFrame(columns=["الاسم","الجهة","عدد المرافقين","إجمالي الأشخاص","رقم الطاولة"])

def guest_exists(name):
    r = supabase.table("guests").select("name").eq("name", name.strip()).execute()
    return len(r.data) > 0

def add_guest(name, side, companions, total):
    supabase.table("guests").insert({
        "name":         name.strip(),
        "side":         side,
        "companions":   companions,
        "total_persons":total,
        "table_number": "قيد الانتظار ⏳"
    }).execute()

def update_table_number(name, table_num):
    supabase.table("guests").update(
        {"table_number": table_num}
    ).eq("name", name).execute()

def delete_guest(name):
    supabase.table("guests").delete().eq("name", name).execute()

def get_guest_row(name):
    r = supabase.table("guests").select("*").eq("name", name.strip()).execute()
    if r.data:
        return r.data[0]
    return None

# =========================================================
# دوال الصور (Supabase Storage)
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
        urls = []
        for f in files:
            if f.get("name"):
                url = supabase.storage.from_(BUCKET).get_public_url(f["name"])
                urls.append(url)
        return urls
    except Exception:
        return []

# =========================================================
# إشعار Telegram
# =========================================================
def send_telegram_notification(guest_name, side, total):
    try:
        token   = st.secrets["telegram"]["bot_token"]  # ← من BotFather
        chat_id = st.secrets["telegram"]["chat_id"]    # ← من @userinfobot
        msg = (
            f"🎊 *ضيف جديد سجّل حضوره!*\n\n"
            f"👤 الاسم: {guest_name}\n"
            f"📍 الجهة: {side}\n"
            f"👥 الإجمالي: {total} أشخاص"
        )
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={
            "chat_id":    chat_id,
            "text":       msg,
            "parse_mode": "Markdown"
        }, timeout=5)
    except Exception:
        pass  # الإشعار اختياري، لا يوقف التطبيق

# =========================================================
# إعداد الصفحة
# =========================================================
st.set_page_config(page_title="Mohammad & Sarah Wedding", page_icon="✨", layout="wide")

# =========================================================
# نظام التوجيه الذكي
# =========================================================
query_params = st.query_params
ADMIN_PASSWORD = st.secrets["admin"]["password"]  # ← اختر كلمة سر قوية

# ---------------------------------------------------------
# 1. لوحة تحكم العريس
# ---------------------------------------------------------
if query_params.get("admin") == ADMIN_PASSWORD:

    if "admin_filter" not in st.session_state:
        st.session_state.admin_filter = "الكل"

    st.markdown("""
<style>
.stApp { background-color: #0F172A; }
h1, h2, h3, p { font-family: 'Cairo', sans-serif; color: #E2E8F0; direction: rtl; text-align: right; }

div.stButton > button {
    background: linear-gradient(45deg, #D4AF37, #F3E5AB) !important;
    border: none !important; border-radius: 30px !important;
    padding: 10px 25px !important;
    box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4) !important;
    transition: all 0.3s ease !important; width: 100%;
}
div.stButton > button p {
    color: #000000 !important; font-family: 'Cairo', sans-serif !important;
    font-weight: 900 !important; font-size: 1.2rem !important; margin: 0 !important;
}
div[data-testid="column"]:nth-child(1) div.stButton > button {
    background: rgba(59, 130, 246, 0.15) !important;
    border: 2px solid #3B82F6 !important; box-shadow: none !important;
}
div[data-testid="column"]:nth-child(1) div.stButton > button p { color: #60A5FA !important; font-size: 1.5rem !important; }
div[data-testid="column"]:nth-child(2) div.stButton > button {
    background: rgba(236, 72, 153, 0.15) !important;
    border: 2px solid #EC4899 !important; box-shadow: none !important;
}
div[data-testid="column"]:nth-child(2) div.stButton > button p { color: #F472B6 !important; font-size: 1.5rem !important; }
div[data-testid="column"]:nth-child(3) div.stButton > button {
    background: rgba(34, 197, 94, 0.15) !important;
    border: 2px solid #22C55E !important; box-shadow: none !important;
}
div[data-testid="column"]:nth-child(3) div.stButton > button p { color: #4ADE80 !important; font-size: 1.5rem !important; }
div[data-testid="column"] div.stButton > button:hover { transform: translateY(-5px) !important; filter: brightness(1.2); }
</style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;color:#D4AF37;font-family:Amiri;margin-top:30px;'>👑 لوحة تحكم العريس الذكية 👑</h1>", unsafe_allow_html=True)

    df = load_db()
    if not df.empty:
        count_groom = df[df['الجهة'] == 'جهة العريس 🤵']['إجمالي الأشخاص'].sum()
        count_bride = df[df['الجهة'] == 'جهة العروس 👰']['إجمالي الأشخاص'].sum()
        count_all   = df['إجمالي الأشخاص'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"🤵 العريس\n{count_groom}", use_container_width=True):
                st.session_state.admin_filter = "جهة العريس 🤵"
        with col2:
            if st.button(f"👰 العروس\n{count_bride}", use_container_width=True):
                st.session_state.admin_filter = "جهة العروس 👰"
        with col3:
            if st.button(f"👥 الإجمالي\n{count_all}", use_container_width=True):
                st.session_state.admin_filter = "الكل"

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.admin_filter == "جهة العريس 🤵":
            view_df = df[df['الجهة'] == 'جهة العريس 🤵'].copy()
            st.markdown("<h4 style='text-align:center;color:#60A5FA;font-family:Cairo;'>الجدول يعرض: معازيم العريس فقط</h4>", unsafe_allow_html=True)
        elif st.session_state.admin_filter == "جهة العروس 👰":
            view_df = df[df['الجهة'] == 'جهة العروس 👰'].copy()
            st.markdown("<h4 style='text-align:center;color:#F472B6;font-family:Cairo;'>الجدول يعرض: معازيم العروس فقط</h4>", unsafe_allow_html=True)
        else:
            view_df = df.copy()
            st.markdown("<h4 style='text-align:center;color:#4ADE80;font-family:Cairo;'>الجدول يعرض: جميع الحضور</h4>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center;color:#cbd5e1;'>💡 انقر على رقم الطاولة لتعديله. ولحذف اسم، حدد مربع الحذف ثم اضغط حفظ.</p>", unsafe_allow_html=True)

        view_df["حذف؟"] = False
        edited_df = st.data_editor(
            view_df,
            column_config={
                "حذف؟":            st.column_config.CheckboxColumn("🗑️ حذف؟", default=False),
                "الاسم":           st.column_config.TextColumn("👤 الاسم", disabled=True),
                "الجهة":           st.column_config.TextColumn("📍 الجهة", disabled=True),
                "عدد المرافقين":   st.column_config.TextColumn("👨‍👩‍👧‍👦 المرافقين", disabled=True),
                "إجمالي الأشخاص": st.column_config.NumberColumn("🔢 الإجمالي", disabled=True),
                "رقم الطاولة":    st.column_config.TextColumn("🪑 رقم الطاولة")
            },
            use_container_width=True, hide_index=True
        )

        if st.button("💾 تنفيذ التعديلات وحفظ"):
            names_to_delete = edited_df[edited_df["حذف؟"] == True]["الاسم"].tolist()
            for _, row in edited_df.iterrows():
                update_table_number(row["الاسم"], row["رقم الطاولة"])
            for name in names_to_delete:
                delete_guest(name)
            st.success("✅ تم حفظ التعديلات بنجاح!")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("تحميل القائمة كملف CSV 📥", data=csv, file_name="wedding_guests.csv", mime="text/csv")
    else:
        st.warning("لم يقم أحد بتأكيد الحضور حتى الآن.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("تسجيل الخروج والعودة للموقع 🚪"):
        st.query_params.clear()
        st.rerun()

# ---------------------------------------------------------
# 2. صفحة تذكرة VIP
# ---------------------------------------------------------
elif "vip" in query_params:
    encoded_name = query_params.get("name", "")
    guest_name   = urllib.parse.unquote(encoded_name)
    row          = get_guest_row(guest_name)

    if row:
        guests_count = row.get("companions",    "غير معروف")
        guest_side   = row.get("side",          "غير محدد")
        table_num    = row.get("table_number",  "قيد الانتظار ⏳")
    else:
        guests_count, guest_side, table_num = "غير معروف", "غير محدد", "قيد الانتظار ⏳"

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;700;900&display=swap');
:root { --vip-gold: #D4AF37; --vip-text: #E2E8F0; --vip-muted: #cbd5e1; }
h1 { font-family: 'Amiri', serif !important; color: var(--vip-gold) !important; font-size: clamp(2rem, 8vw, 3rem); margin-bottom: 10px; }
p  { font-family: 'Cairo', sans-serif !important; color: var(--vip-text) !important; font-size: clamp(1rem, 3vw, 1.2rem); }
.stApp { background-image: url("https://images.unsplash.com/photo-1544078755-6b8d2b2c938a?q=80&w=2070"); background-size: cover; background-position: center; }
.stApp::before { content:""; position:absolute; top:0; left:0; right:0; bottom:0; background:rgba(10,10,10,0.85); z-index:0; }
header { visibility: hidden; }
.main .block-container { z-index:1; position:relative; padding-top:3rem; display:flex; flex-direction:column; align-items:center; }
.ticket-card {
    background: rgba(255,255,255,0.05); backdrop-filter: blur(15px);
    border: 1px solid rgba(212,175,55,0.4); border-radius: 20px;
    padding: clamp(20px,5vw,40px); text-align: center;
    box-shadow: 0 20px 50px rgba(212,175,55,0.2);
    max-width: 500px; width: 90%;
    animation: slide-up 1s ease-out forwards;
}
@keyframes slide-up { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.vip-badge { background: linear-gradient(45deg, #D4AF37, #F3E5AB); color: #000; padding: 5px 20px; border-radius: 30px; font-weight: bold; font-family: 'Cairo', sans-serif; font-size: clamp(1rem,3vw,1.2rem); display: inline-block; margin-bottom: 20px; }
div.stButton > button { background: linear-gradient(45deg, #D4AF37, #F3E5AB) !important; border: none !important; border-radius: 30px !important; padding: 10px 30px !important; box-shadow: 0 5px 15px rgba(212,175,55,0.4) !important; transition: all 0.3s ease !important; }
div.stButton > button:hover { transform: translateY(-3px) !important; }
div.stButton > button p { color: #000000 !important; font-family: 'Cairo', sans-serif !important; font-weight: 900 !important; font-size: 1.3rem !important; margin: 0 !important; }
</style>
    """, unsafe_allow_html=True)

    st.balloons()
    st.markdown(f"""
<div class="ticket-card">
    <div class="vip-badge">VIP PASS 🌟</div>
    <h1>أهلاً بك يا {guest_name}</h1>
    <p>تذكرتك الملكية مفعلة وجاهزة.</p>
    <hr style="border-color:rgba(212,175,55,0.3);margin:20px 0;">
    <div style="color:#E2E8F0;font-family:'Cairo',sans-serif;font-size:clamp(1rem,3vw,1.1rem);text-align:right;direction:rtl;line-height:2;">
        <b>المدعو من:</b> {guest_side}<br>
        <b>المرافقين المسجلين:</b> {guests_count}<br>
        <b style="color:#D4AF37;font-size:1.3rem;">رقم الطاولة:</b>
        <span style="background:rgba(212,175,55,0.2);padding:2px 10px;border-radius:5px;">{table_num}</span><br>
        <b>الحالة:</b> <span style="color:#4ade80;">تم تأكيد الحضور ✔️</span>
    </div>
</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("العودة إلى تفاصيل الحفل ↩️"):
        st.query_params.clear()
        st.rerun()

# ---------------------------------------------------------
# 3. الموقع الرئيسي
# ---------------------------------------------------------
else:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;700;900&display=swap');
:root { --primary-gold:#D4AF37; --light-gold:#F3E5AB; --text-main:#FFFFFF; --text-muted:#E2E8F0; --overlay-color:rgba(10,15,30,0.85); }
h1 { font-family:'Amiri',serif !important; color:var(--primary-gold) !important; text-align:center; }
h2 { font-family:'Amiri',serif !important; color:var(--primary-gold) !important; font-size:clamp(2rem,8vw,3rem) !important; text-align:center; margin-top:30px !important; margin-bottom:20px !important; }
h3 { font-family:'Cairo',sans-serif !important; color:var(--text-main) !important; font-size:clamp(1rem,4vw,1.5rem) !important; font-weight:300 !important; letter-spacing:2px; text-align:center; }
p  { font-family:'Cairo',sans-serif !important; color:var(--text-muted) !important; font-size:clamp(1rem,3vw,1.2rem) !important; text-align:center; }
.stApp { background-image:url("https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=2070"); background-size:cover; background-position:center; background-attachment:fixed; }
.stApp::before { content:""; position:absolute; top:0; left:0; right:0; bottom:0; background:var(--overlay-color); z-index:0; }
header, #MainMenu, footer { visibility:hidden; }
.main .block-container { z-index:1; position:relative; padding-top:1rem; }
@keyframes pulse-gold { 0%{text-shadow:0 0 10px rgba(212,175,55,0.4);} 50%{text-shadow:0 0 25px rgba(212,175,55,0.8);} 100%{text-shadow:0 0 10px rgba(212,175,55,0.4);} }
.glowing-title { font-size:clamp(3rem,12vw,5rem) !important; margin-bottom:0; animation:pulse-gold 3s infinite; }
.content-box { background:rgba(255,255,255,0.05); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:clamp(15px,4vw,30px); margin:20px 0; box-shadow:0 8px 32px 0 rgba(0,0,0,0.5); }
div.stButton > button { background:linear-gradient(45deg,var(--primary-gold),var(--light-gold)) !important; border:none !important; border-radius:30px !important; padding:10px 25px !important; box-shadow:0 5px 15px rgba(212,175,55,0.4) !important; transition:all 0.3s ease !important; width:100% !important; }
div.stButton > button:hover { transform:translateY(-3px) !important; box-shadow:0 8px 25px rgba(212,175,55,0.7) !important; }
div.stButton > button p { color:#000000 !important; font-family:'Cairo',sans-serif !important; font-weight:900 !important; font-size:1.3rem !important; margin:0 !important; }
div[data-baseweb="tab-list"] { gap:10px; justify-content:center; margin-bottom:30px; background:rgba(0,0,0,0.2); padding:10px; border-radius:20px; }
button[data-baseweb="tab"] { background-color:rgba(255,255,255,0.05) !important; border-radius:15px !important; border:1px solid rgba(212,175,55,0.3) !important; color:#E2E8F0 !important; padding:10px 20px !important; font-family:'Cairo',sans-serif; transition:0.3s; }
button[data-baseweb="tab"][aria-selected="true"] { background:linear-gradient(45deg,#D4AF37,#F3E5AB) !important; color:#0F172A !important; font-weight:bold !important; border:none !important; transform:scale(1.05); }
.wish-money-box { background:linear-gradient(135deg,rgba(225,29,72,0.15),rgba(147,51,234,0.15)); border:2px dashed #E11D48; border-radius:20px; padding:30px; text-align:center; margin-bottom:30px; }
.wish-btn { display:inline-block; background:linear-gradient(45deg,#E11D48,#9333EA) !important; color:#FFFFFF !important; font-family:'Cairo',sans-serif !important; font-weight:900 !important; font-size:clamp(1.1rem,3vw,1.4rem) !important; text-decoration:none !important; padding:15px 35px !important; border-radius:40px !important; box-shadow:0 10px 25px rgba(225,29,72,0.4) !important; transition:all 0.3s ease !important; margin-top:15px; }
.timeline-container { direction:rtl; margin:40px auto; max-width:700px; position:relative; padding-right:40px; }
.timeline-container::before { content:''; position:absolute; top:0; right:15px; height:100%; width:4px; background:linear-gradient(to bottom,#D4AF37,#F3E5AB,#D4AF37); border-radius:5px; }
.timeline-item { position:relative; margin-bottom:40px; }
.timeline-dot { position:absolute; right:-33px; top:15px; width:24px; height:24px; background:#D4AF37; border:4px solid #0F172A; border-radius:50%; box-shadow:0 0 15px rgba(212,175,55,0.9); z-index:2; }
.timeline-content { background:rgba(15,23,42,0.85); backdrop-filter:blur(12px); border:1px solid rgba(212,175,55,0.4); border-right:5px solid #D4AF37; padding:20px 25px; border-radius:15px; box-shadow:0 8px 25px rgba(0,0,0,0.6); transition:all 0.3s ease; }
.timeline-content:hover { transform:translateX(-10px); box-shadow:0 10px 30px rgba(212,175,55,0.3); }
.timeline-content h4 { color:#D4AF37 !important; font-family:'Amiri',serif !important; margin:0 0 10px 0 !important; font-size:1.8rem !important; font-weight:bold !important; }
.timeline-content p  { color:#FFFFFF !important; font-family:'Cairo',sans-serif !important; margin:0 !important; font-size:1.2rem !important; line-height:1.6 !important; text-align:right !important; font-weight:bold !important; }
</style>
    """, unsafe_allow_html=True)

    # ---- مقدمة سينمائية ----
    cinematic_intro_html = """
<script>
    const parentDoc = window.parent.document;
    if (!parentDoc.getElementById('cinematic-intro')) {
        const introDiv = parentDoc.createElement('div');
        introDiv.id = 'cinematic-intro';
        introDiv.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:black;z-index:999999;transition:opacity 1.5s ease;display:flex;flex-direction:column;justify-content:center;align-items:center;';
        introDiv.innerHTML = `
            <video id="intro-vid" autoplay muted playsinline style="width:100%;height:100%;object-fit:cover;position:absolute;top:0;left:0;opacity:0.8;">
                <source src="https://videos.pexels.com/video-files/3195394/3195394-uhd_2560_1440_25fps.mp4" type="video/mp4">
            </video>
            <div style="position:absolute;z-index:10;text-align:center;width:100%;">
                <h1 style="color:#D4AF37;font-family:'Amiri',serif;font-size:clamp(3rem,10vw,4rem);text-shadow:2px 2px 10px #000;margin:0;">محمد & سارة</h1>
            </div>
            <button id="skip-btn" style="position:absolute;bottom:10%;padding:10px 30px;background:linear-gradient(45deg,#D4AF37,#F3E5AB);color:#000000;font-weight:900;font-size:1.3rem;border:none;border-radius:30px;cursor:pointer;z-index:10;font-family:'Cairo',sans-serif;box-shadow:0 5px 15px rgba(212,175,55,0.5);transition:0.3s;">
                دخول للموقع 🤍
            </button>`;
        parentDoc.body.appendChild(introDiv);
        const vid    = parentDoc.getElementById('intro-vid');
        const skipBtn = parentDoc.getElementById('skip-btn');
        function removeIntro() { introDiv.style.opacity='0'; setTimeout(()=>{ introDiv.remove(); },1500); }
        vid.onended = removeIntro;
        skipBtn.onclick = removeIntro;
    }
</script>
    """
    components.html(cinematic_intro_html, width=0, height=0)

    st.markdown("""
<div style="margin-bottom:2rem;margin-top:1rem;">
    <h1 class="glowing-title">محمد & سارة</h1>
    <h3>ندعوكم لمشاركتنا أجمل لحظات العمر</h3>
</div>
    """, unsafe_allow_html=True)

    # =========================================================
    # التبويبات
    # =========================================================
    tab_home, tab_rsvp, tab_gallery, tab_house = st.tabs([
        "الرئيسية 🏠", "دعوة وتهنئة 💌", "صورنا 📸", "عشنا الصغير 🛋️"
    ])

    # =================== الرئيسية ===================
    with tab_home:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;color:#D4AF37;'>فيديو وصورة خاصة من العرسان 👇</h3>", unsafe_allow_html=True)
        col_vid, col_img = st.columns(2)
        with col_vid:
            # ← استبدل بفيديو خاص بكم
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        with col_img:
            # ← استبدل بصورتكم
            st.image("https://images.unsplash.com/photo-1583939000240-69279c118671", caption="أهلاً بكم في موقعنا")
        st.markdown("</div>", unsafe_allow_html=True)

        cal_url = "https://calendar.google.com/calendar/render?action=TEMPLATE&text=حفل+زفاف+محمد+وسارة&dates=20260531T160000Z/20260531T210000Z&details=بانتظاركم+لنصنع+أجمل+الذكريات!&location=Sofia+Palace,+Rmeileh,+Lebanon"
        st.markdown(f'<a href="{cal_url}" target="_blank" style="display:block;background:rgba(255,255,255,0.1);border:1px solid #D4AF37;color:#D4AF37 !important;padding:12px 20px;border-radius:30px;text-decoration:none;font-family:\'Cairo\',sans-serif;font-weight:bold;text-align:center;max-width:300px;margin:20px auto;transition:0.3s;backdrop-filter:blur(5px);">📅 أضف الموعد إلى تقويمك</a>', unsafe_allow_html=True)

        # ---- العداد التنازلي ----
        custom_timer_html = """
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap" rel="stylesheet">
<style>
body { display:flex; justify-content:center; align-items:center; background-color:transparent; margin:0; font-family:'Cairo',sans-serif; }
.glass-container { background:rgba(255,255,255,0.05); backdrop-filter:blur(12px); border-radius:20px; border:1px solid rgba(255,255,255,0.15); padding:30px 50px; display:flex; gap:40px; box-shadow:0 8px 32px 0 rgba(0,0,0,0.5); direction:rtl; flex-wrap:wrap; justify-content:center; }
.time-box { display:flex; flex-direction:column; align-items:center; min-width:70px; }
.number { font-size:3.5rem; font-weight:700; color:#D4AF37; margin:0; line-height:1; text-shadow:0 0 15px rgba(212,175,55,0.5); }
.label  { font-size:1.2rem; color:#F8FAFC; margin-top:5px; }
@media(max-width:600px){ .glass-container{gap:15px;padding:20px;} .number{font-size:2.2rem;} .label{font-size:0.9rem;} .time-box{min-width:55px;} }
</style></head><body>
<div class="glass-container">
    <div class="time-box"><span class="number" id="days">00</span><span class="label">يوم</span></div>
    <div class="time-box"><span class="number" id="hours">00</span><span class="label">ساعة</span></div>
    <div class="time-box"><span class="number" id="minutes">00</span><span class="label">دقيقة</span></div>
    <div class="time-box"><span class="number" id="seconds">00</span><span class="label">ثانية</span></div>
</div>
<script>
const weddingDate = new Date("May 31, 2026 19:00:00").getTime();
setInterval(function(){
    const distance = weddingDate - new Date().getTime();
    document.getElementById("days").innerHTML    = Math.floor(distance/(1000*60*60*24)).toString().padStart(2,'0');
    document.getElementById("hours").innerHTML   = Math.floor((distance%(1000*60*60*24))/(1000*60*60)).toString().padStart(2,'0');
    document.getElementById("minutes").innerHTML = Math.floor((distance%(1000*60*60))/(1000*60)).toString().padStart(2,'0');
    document.getElementById("seconds").innerHTML = Math.floor((distance%(1000*60))/1000).toString().padStart(2,'0');
},1000);
</script></body></html>
        """
        components.html(custom_timer_html, height=220)

        st.markdown("<h2>جدول الليلة ⏳</h2>", unsafe_allow_html=True)
        st.markdown("""
<div class="timeline-container">
    <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content"><h4>🕖 07:00 م</h4><p>استقبال الأحباب وبداية التجمع</p></div></div>
    <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content"><h4>🕗 08:00 م</h4><p>الزفة الملكية ودخول العرسان</p></div></div>
    <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content"><h4>🍽️ 09:30 م</h4><p>عشاء العرسان (بوفيه مفتوح)</p></div></div>
    <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content"><h4>🎂 11:00 م</h4><p>قطع الكيكة وصنع الذكريات</p></div></div>
</div>
        """, unsafe_allow_html=True)

        st.markdown("<h2>موقع الحفل 📍</h2>", unsafe_allow_html=True)
        interactive_map_html = """
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700&display=swap" rel="stylesheet">
<style>
.map-container { position:relative; width:100%; max-width:900px; margin:20px auto; border-radius:25px; overflow:hidden; box-shadow:0 15px 40px rgba(0,0,0,0.5),0 0 15px rgba(212,175,55,0.2); border:2px solid rgba(212,175,55,0.4); transform:perspective(1200px) rotateX(4deg) scale(0.96); transition:all 0.6s cubic-bezier(0.25,0.8,0.25,1); }
.map-container:hover { transform:perspective(1200px) rotateX(0deg) scale(1); box-shadow:0 25px 60px rgba(0,0,0,0.8),0 0 30px rgba(212,175,55,0.5); border:2px solid rgba(212,175,55,0.9); }
.map-iframe { width:100%; height:450px; border:0; filter:grayscale(30%) contrast(1.1); transition:all 0.6s ease; }
.map-container:hover .map-iframe { filter:grayscale(0%) contrast(1); }
.floating-card { position:absolute; bottom:25px; right:25px; background:rgba(15,23,42,0.85); backdrop-filter:blur(12px); padding:25px; border-radius:20px; border-right:4px solid #D4AF37; box-shadow:0 10px 30px rgba(0,0,0,0.7); direction:rtl; text-align:right; max-width:280px; transform:translateY(30px); opacity:0; transition:all 0.5s ease 0.1s; }
.map-container:hover .floating-card { transform:translateY(0); opacity:1; }
.venue-title { color:#D4AF37; margin:0 0 8px 0; font-family:'Amiri',serif; font-size:1.5rem; }
.venue-desc  { color:#E2E8F0; margin:0 0 20px 0; font-family:'Cairo',sans-serif; font-size:0.9rem; line-height:1.6; }
.btn-directions { display:block; background:linear-gradient(45deg,#D4AF37,#F3E5AB); color:#000000 !important; padding:10px 0; border-radius:30px; text-decoration:none; font-weight:900; font-size:1.1rem; font-family:'Cairo',sans-serif; text-align:center; }
@media(max-width:768px){ .map-container{transform:none;} .map-container:hover{transform:none;} .floating-card{position:relative;bottom:0;right:0;max-width:100%;border-radius:0 0 25px 25px;transform:none;opacity:1;border-right:none;border-top:2px solid #D4AF37;} .map-iframe{height:300px;filter:none;} }
</style></head><body style="margin:0;background:transparent;padding:10px;">
<div class="map-container">
    <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3322.993864119795!2d35.3934256764207!3d33.60546367332862!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x151ee52e784728f9%3A0xaa57f0e88d65b592!2sSofia%20Palace!5e0!3m2!1sen!2slb!4v1772620814491!5m2!1sen!2slb" class="map-iframe" allowfullscreen="" loading="lazy"></iframe>
    <div class="floating-card">
        <h3 class="venue-title">Sofia Palace</h3>
        <p class="venue-desc">قاعة الاحتفالات الكبرى<br>الرميلة، لبنان<br>بانتظاركم بكل حب 🤍</p>
        <a href="https://maps.app.goo.gl/YZCjR4FNNa5tCE8G6" target="_blank" class="btn-directions">احصل على الاتجاهات 🚗</a>
    </div>
</div>
</body></html>
        """
        components.html(interactive_map_html, height=550)

    # =================== دعوة وتهنئة ===================
    with tab_rsvp:
        # رابط الموقع الفعلي ← غيّره لرابطك
        BASE_URL = "https://mohamad-sarahwedding-pycf9neap43w7zh9pewmhu.streamlit.app/"
        # رابط Wish Money ← ضع رابطك الحقيقي
        WISH_MONEY_LINK = "https://wishmoneylink.com/YOUR_LINK"

        st.markdown("<h2>تأكيد الحضور 🎟️</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='content-box'>", unsafe_allow_html=True)
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                rsvp_name  = st.text_input("الاسم الكريم (الثنائي)", placeholder="مثال: أحمد خليل...")
            with col_form2:
                guest_side = st.selectbox("من أي جهة؟", ["جهة العريس 🤵", "جهة العروس 👰"])
            guests_count = st.selectbox("عدد المرافقين (بدون احتسابك)", [
                "بدون مرافقين", "مرافق واحد", "مرافقان", "3 مرافقين", "4 مرافقين"
            ])

            if st.button("تأكيد الحضور واستخراج التذكرة 🎫"):
                if rsvp_name:
                    companions_map = {"بدون مرافقين":0,"مرافق واحد":1,"مرافقان":2,"3 مرافقين":3,"4 مرافقين":4}
                    total_persons  = 1 + companions_map.get(guests_count, 0)

                    encoded_name = urllib.parse.quote(rsvp_name.strip())
                    ticket_url   = f"{BASE_URL}/?vip=true&name={encoded_name}"

                    # QR Code
                    qr = qrcode.QRCode(version=1, box_size=10, border=2)
                    qr.add_data(ticket_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="#D4AF37", back_color="#0F172A")
                    buf = BytesIO()
                    img.save(buf, format="PNG")

                    if guest_exists(rsvp_name):
                        st.info(f"أهلاً بعودتك يا {rsvp_name}! لقد قمت بتأكيد حضورك مسبقاً. تذكرتك جاهزة أدناه 👇")
                    else:
                        add_guest(rsvp_name, guest_side, guests_count, total_persons)
                        send_telegram_notification(rsvp_name, guest_side, total_persons)
                        st.success(f"تم تأكيد حضورك يا {rsvp_name}! نحن بانتظارك.")
                        st.balloons()

                    # جيب رقم الطاولة من Supabase
                    row = get_guest_row(rsvp_name)
                    current_table = row["table_number"] if row else "قيد الانتظار ⏳"

                    st.markdown(f"""
<div style='background:linear-gradient(135deg,rgba(30,41,59,0.9),rgba(15,23,42,0.9));border:2px dashed #D4AF37;padding:20px;border-radius:15px;text-align:center;margin-top:20px;box-shadow:0 0 20px rgba(212,175,55,0.2);'>
    <h3 style='color:#D4AF37;font-family:Amiri;'>تذكرة دخول VIP 🌟</h3>
    <p style='color:#E2E8F0;font-family:Cairo;font-size:1.2rem;'>الضيف المُميز: <b>{rsvp_name}</b></p>
    <p style='color:#cbd5e1;font-family:Cairo;font-size:0.9rem;'>امسح الرمز أو احتفظ به — سيتم تحديث رقم الطاولة تلقائياً يوم الحفل</p>
</div>
                    """, unsafe_allow_html=True)

                    col_qr1, col_qr2, col_qr3 = st.columns([1,1,1])
                    with col_qr2:
                        st.image(buf, use_container_width=True, caption="امسحني بكاميرا الهاتف 📸")

                    wa_message = (
                        f"✨ تذكرة زفاف محمد وسارة ✨\n\n"
                        f"👤 الاسم: {rsvp_name}\n"
                        f"🎫 الطاولة: {current_table}\n"
                        f"🔗 رابط التذكرة: {ticket_url}\n\n"
                        f"🎁 لإرسال النقوط عبر Wish Money:\n{WISH_MONEY_LINK}"
                    )
                    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_message)}"
                    st.markdown(f"""
<a href="{wa_url}" target="_blank" style="display:block;background:#25D366;color:white;text-align:center;padding:12px;border-radius:30px;text-decoration:none;font-family:'Cairo',sans-serif;font-weight:bold;margin-top:15px;box-shadow:0 5px 15px rgba(37,211,102,0.4);">
    💬 احتفظ بالتذكرة ورابط الـ Wish Money عبر واتساب
</a>
                    """, unsafe_allow_html=True)
                else:
                    st.error("يرجى إدخال اسمك أولاً!")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h2>سجل التهاني والنقوط 💌</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='content-box'>", unsafe_allow_html=True)
            st.markdown(f"""
<div class="wish-money-box">
    <h3 style="color:#E11D48;font-family:'Amiri',serif;font-size:clamp(1.8rem,5vw,2.5rem);margin-top:0;margin-bottom:10px;">💖 تكتمل فرحتنا بوجودكم بيننا</h3>
    <p style="color:#E2E8F0;font-family:'Cairo',sans-serif;font-size:clamp(1rem,3vw,1.2rem);margin-bottom:20px;line-height:1.8;">
        مشاركتكم لنا هذه اللحظات السعيدة تعني لنا الكثير وهي أكبر هدية.<br>
        ولمن يحب إرسال النقوط إلكترونياً، خصصنا هذا الرابط السريع والآمن.
    </p>
    <a href="{WISH_MONEY_LINK}" target="_blank" class="wish-btn">✨ إرسال النقوط عبر Wish Money ✨</a>
</div>
            """, unsafe_allow_html=True)

            guest_msg_name = st.text_input("اسمك (لكي نشكرك)", key="msg_name")
            message = st.text_area("اترك لنا ذكرى جميلة من قلبك...", key="msg", height=100)
            if st.button("إرسال التهنئة 🕊️"):
                if message:
                    import random
                    name_to_use = guest_msg_name if guest_msg_name else "ضيفنا الغالي"
                    ai_replies  = [
                        f"يا لها من كلمات تلامس القلب! شكراً لك يا {name_to_use} 🤍",
                        f"لقد أسعدتنا جداً رسالتك يا {name_to_use}، وجودك معنا سيزيد فرحتنا أضعافاً! ✨",
                        f"أمنياتك تعني لنا الكثير يا {name_to_use}، شكراً لمشاركتنا هذه اللحظات التي لا تُنسى. 💍"
                    ]
                    st.info(random.choice(ai_replies), icon="🤖")
                else:
                    st.warning("الرسالة فارغة! لا تحرمنا من كلماتك الطيبة.")
            st.markdown("</div>", unsafe_allow_html=True)

    # =================== صورنا ===================
    with tab_gallery:
        st.markdown("<h2>جدار الذكريات 📸</h2>", unsafe_allow_html=True)
        st.markdown("<p>التقطوا أجمل اللحظات وارفعوها هنا!</p>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='content-box'>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("التقط صورة أو اختر من هاتفك 🤳", type=["jpg","jpeg","png"])
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                if upload_photo(file_bytes, uploaded_file.name):
                    st.success("تم رفع الصورة بنجاح! 🤍")

            photo_urls = get_all_photos()
            if photo_urls:
                st.markdown("<hr style='border-color:rgba(212,175,55,0.3);'>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align:center;color:#D4AF37;'>الصور المرفوعة ✨</h4><br>", unsafe_allow_html=True)
                cols = st.columns(3)
                for i, url in enumerate(photo_urls):
                    cols[i % 3].image(url, use_container_width=True)
            else:
                st.info("جدار الذكريات ينتظر إبداعاتكم! 🌟")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h2>قصتنا في صور 📷</h2>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("https://images.unsplash.com/photo-1511285560929-80b456fea0bc", caption="اللقاء الأول 🤍")
            st.image("https://images.unsplash.com/photo-1522673607200-164d1b6ce486", caption="لحظات لا تنسى ✨")
        with col2:
            st.image("https://images.unsplash.com/photo-1544928147-79a2dbc1f389", caption="يوم الخطوبة 💍")
            st.image("https://images.unsplash.com/photo-1606800052052-a08af7148866", caption="رحلتنا معاً ✈️")
        with col3:
            st.image("https://images.unsplash.com/photo-1583939000240-69279c118671", caption="عائلتنا الصغيرة 👨‍👩‍👧")
            st.image("https://images.unsplash.com/photo-1620063994354-9ce535560b0e", caption="في انتظار اليوم الكبير 🎉")
        st.markdown("</div>", unsafe_allow_html=True)

    # =================== عشنا الصغير ===================
    with tab_house:
        st.markdown("<h2>عشنا الصغير 🛋️</h2>", unsafe_allow_html=True)
        st.markdown("<p>نظرة خاطفة على تفاصيل وتصميم مملكتنا القادمة...</p>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.image("https://images.unsplash.com/photo-1600210492486-724fe5c67fb0", caption="زوايا دافئة وتفاصيل ذكية 💡")
        with col_h2:
            st.image("https://images.unsplash.com/photo-1616594039964-ae9021a400a0", caption="غرفة النوم الرئيسية 🤍")
        st.markdown("</div>", unsafe_allow_html=True)

    # =================== Footer ===================
    st.markdown("""
<div style="text-align:center;margin-top:50px;padding-bottom:20px;">
    <p style="font-size:0.9rem !important;color:rgba(226,232,240,0.5) !important;">
        Designed & Powered by <span style="color:var(--primary-gold);font-weight:bold;letter-spacing:1px;">MK Technology</span> © 2026
    </p>
</div>
    """, unsafe_allow_html=True)
