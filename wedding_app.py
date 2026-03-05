import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

# 1. إعداد الصفحة الأساسي (يجب أن يكون أول سطر)
st.set_page_config(page_title="Mohammad & Sarah Wedding", page_icon="✨", layout="wide")

# =========================================================
# نظام التوجيه الذكي (Router): فصل الموقع الرئيسي عن صفحة تذكرة الـ VIP
# =========================================================
query_params = st.query_params

if "vip" in query_params:
    # ---------------------------------------------------------
    # صفحة الـ VIP المستقلة (تظهر فقط عند مسح الـ QR Code)
    # ---------------------------------------------------------
    guest_name = query_params.get("name", "ضيفنا الكريم")
    guests_count = query_params.get("count", "بدون مرافقين")
    
    # إخفاء واجهة ستريملت وتغيير الخلفية مع دعم الشاشات الصغيرة
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;700;900&display=swap');
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1544078755-6b8d2b2c938a?q=80&w=2070&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
        }
        .stApp::before {
            content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(10, 10, 10, 0.85); z-index: 0;
        }
        header {visibility: hidden;}
        .main .block-container { z-index: 1; position: relative; padding-top: 3rem; display: flex; flex-direction: column; align-items: center; }
        
        .ticket-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(212, 175, 55, 0.4);
            border-radius: 20px;
            padding: clamp(20px, 5vw, 40px);
            text-align: center;
            box-shadow: 0 20px 50px rgba(212, 175, 55, 0.2);
            max-width: 500px;
            width: 90%; /* تجاوب مع الهاتف */
            animation: slide-up 1s ease-out forwards;
        }
        @keyframes slide-up {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .vip-badge {
            background: linear-gradient(45deg, #D4AF37, #F3E5AB);
            color: #000;
            padding: 5px 20px;
            border-radius: 30px;
            font-weight: bold;
            font-family: 'Cairo', sans-serif;
            font-size: clamp(1rem, 3vw, 1.2rem);
            display: inline-block;
            margin-bottom: 20px;
        }
        .ticket-title {
            color: #D4AF37; font-family: 'Amiri', serif; 
            font-size: clamp(2rem, 8vw, 3rem); /* تصغير الخط على الهاتف */
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown(f"""
        <div class="ticket-card">
            <div class="vip-badge">VIP PASS 🌟</div>
            <h1 class="ticket-title">أهلاً بك يا {guest_name}</h1>
            <p style="color: #E2E8F0; font-family: 'Cairo', sans-serif; font-size: clamp(1rem, 3vw, 1.2rem);">تذكرتك الملكية مفعلة وجاهزة.</p>
            <hr style="border-color: rgba(212,175,55,0.3); margin: 20px 0;">
            <p style="color: #cbd5e1; font-family: 'Cairo', sans-serif; font-size: clamp(0.9rem, 3vw, 1.1rem); text-align: right; direction: rtl;">
                <b>الحدث:</b> حفل زفاف محمد وسارة 💍<br>
                <b>عدد المرافقين المسجلين:</b> {guests_count}<br>
                <b>الحالة:</b> <span style="color: #4ade80;">تم تأكيد الحضور والتسجيل بنجاح ✔️</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("العودة إلى تفاصيل الحفل ↩️"):
        st.query_params.clear()
        st.rerun()

else:
    # =========================================================
    # الصفحة الرئيسية
    # =========================================================

    # ---------------------------------------------------------
    # 2. الدخول السينمائي (مع نصوص متجاوبة)
    # ---------------------------------------------------------
    cinematic_intro_html = """
    <script>
        const parentDoc = window.parent.document;
        if (!parentDoc.getElementById('cinematic-intro')) {
            const introDiv = parentDoc.createElement('div');
            introDiv.id = 'cinematic-intro';
            introDiv.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:black; z-index:999999; transition: opacity 1.5s ease; display:flex; flex-direction:column; justify-content:center; align-items:center;';
            
            introDiv.innerHTML = `
                <video id="intro-vid" autoplay muted playsinline style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0; opacity: 0.8;">
                    <source src="https://videos.pexels.com/video-files/3195394/3195394-uhd_2560_1440_25fps.mp4" type="video/mp4">
                </video>
                <div style="position:absolute; z-index:10; text-align:center; width: 100%;">
                    <h1 style="color:#D4AF37; font-family: 'Amiri', serif; font-size:clamp(3rem, 10vw, 4rem); text-shadow: 2px 2px 10px #000; margin:0;">محمد & سارة</h1>
                </div>
                <button id="skip-btn" style="position:absolute; bottom:10%; padding:10px 25px; font-size:clamp(1rem, 3vw, 1.2rem); background:rgba(212,175,55,0.3); color:white; border:1px solid #D4AF37; border-radius:30px; cursor:pointer; z-index:10; font-family:'Cairo', sans-serif; backdrop-filter: blur(5px); transition: 0.3s;">دخول للموقع 🤍</button>
            `;
            parentDoc.body.appendChild(introDiv);

            const vid = parentDoc.getElementById('intro-vid');
            const skipBtn = parentDoc.getElementById('skip-btn');
            
            function removeIntro() {
                introDiv.style.opacity = '0';
                setTimeout(() => { introDiv.remove(); }, 1500);
            }
            
            vid.onended = removeIntro;
            skipBtn.onclick = removeIntro;
        }
    </script>
    """
    components.html(cinematic_intro_html, width=0, height=0)

    # ---------------------------------------------------------
    # 3. تصميم الموقع الأساسي المتجاوب (Responsive CSS)
    # ---------------------------------------------------------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;700;900&display=swap');
        
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=2070&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .stApp::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.75);
            z-index: 0;
        }
        header, #MainMenu, footer {visibility: hidden;}
        .main .block-container {
            z-index: 1;
            position: relative;
            padding-top: 1rem;
        }
        
        @keyframes pulse-gold {
            0% { text-shadow: 0 0 10px rgba(212, 175, 55, 0.4); }
            50% { text-shadow: 0 0 25px rgba(212, 175, 55, 0.8); }
            100% { text-shadow: 0 0 10px rgba(212, 175, 55, 0.4); }
        }
        .glowing-title {
            font-family: 'Amiri', serif; 
            color: #D4AF37; 
            font-size: clamp(3rem, 12vw, 5rem); /* خط يتجاوب مع الشاشة */
            margin-bottom: 0;
            animation: pulse-gold 3s infinite;
        }
        .sub-title {
            font-family: 'Cairo', sans-serif; color: #E2E8F0; 
            font-size: clamp(1rem, 4vw, 1.5rem); 
            font-weight: 300; letter-spacing: 2px;
        }
        
        .content-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: clamp(15px, 4vw, 30px);
            margin: 20px 0;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 4. العنوان والعداد
    # ---------------------------------------------------------
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; margin-top: 2rem;">
            <h1 class="glowing-title">محمد & سارة</h1>
            <h3 class="sub-title">ندعوكم لمشاركتنا أجمل لحظات العمر</h3>
        </div>
    """, unsafe_allow_html=True)

    custom_timer_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap" rel="stylesheet">
    <style>
        body { display: flex; justify-content: center; align-items: center; background-color: transparent; margin: 0; font-family: 'Cairo', sans-serif; }
        .glass-container { 
            background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); border-radius: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.15); padding: 30px 50px; 
            display: flex; gap: 40px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); 
            direction: rtl; transition: 0.3s; flex-wrap: wrap; justify-content: center;
        }
        .glass-container:hover { transform: translateY(-5px); box-shadow: 0 12px 40px 0 rgba(212, 175, 55, 0.3); }
        .time-box { display: flex; flex-direction: column; align-items: center; min-width: 70px; }
        .number { font-size: 3.5rem; font-weight: 700; color: #D4AF37; margin: 0; line-height: 1; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
        .label { font-size: 1.2rem; color: #F8FAFC; margin-top: 5px; }
        
        /* استعلامات الهواتف للعداد */
        @media (max-width: 600px) {
            .glass-container { gap: 15px; padding: 20px; }
            .number { font-size: 2.2rem; }
            .label { font-size: 0.9rem; }
            .time-box { min-width: 55px; }
        }
    </style>
    </head>
    <body>
    <div class="glass-container">
        <div class="time-box"><span class="number" id="days">00</span><span class="label">يوم</span></div>
        <div class="time-box"><span class="number" id="hours">00</span><span class="label">ساعة</span></div>
        <div class="time-box"><span class="number" id="minutes">00</span><span class="label">دقيقة</span></div>
        <div class="time-box"><span class="number" id="seconds">00</span><span class="label">ثانية</span></div>
    </div>
    <script>
        const weddingDate = new Date("May 31, 2026 19:00:00").getTime();
        const x = setInterval(function() {
            const now = new Date().getTime();
            const distance = weddingDate - now;
            document.getElementById("days").innerHTML = Math.floor(distance / (1000 * 60 * 60 * 24)).toString().padStart(2, '0');
            document.getElementById("hours").innerHTML = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)).toString().padStart(2, '0');
            document.getElementById("minutes").innerHTML = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)).toString().padStart(2, '0');
            document.getElementById("seconds").innerHTML = Math.floor((distance % (1000 * 60)) / 1000).toString().padStart(2, '0');
        }, 1000);
    </script>
    </body>
    </html>
    """
    # زيادة الارتفاع قليلاً ليتسع للعداد إذا التف (Wrap) على الهاتف
    components.html(custom_timer_html, height=220)

    # ---------------------------------------------------------
    # 5. قسم مشوارنا
    # ---------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: #D4AF37; font-family: Amiri; font-size: clamp(2rem, 8vw, 3rem); margin-top: 20px;'>قصتنا في صور 📷</h2>", unsafe_allow_html=True)
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

    # ---------------------------------------------------------
    # 6. قسم خريطة القاعة - متجاوب مع الهواتف
    # ---------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: #D4AF37; font-family: Amiri; font-size: clamp(2rem, 8vw, 3rem); margin-top: 50px;'>موقع الحفل 📍</h2>", unsafe_allow_html=True)

    interactive_map_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        .map-container {
            position: relative; width: 100%; max-width: 900px; margin: 20px auto; border-radius: 25px; overflow: hidden;
            box-shadow: 0 15px 40px rgba(0,0,0,0.5), 0 0 15px rgba(212, 175, 55, 0.2); border: 2px solid rgba(212, 175, 55, 0.4);
            transform: perspective(1200px) rotateX(4deg) scale(0.96); transition: all 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .map-container:hover {
            transform: perspective(1200px) rotateX(0deg) scale(1); box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 30px rgba(212, 175, 55, 0.5);
            border: 2px solid rgba(212, 175, 55, 0.9);
        }
        .map-iframe {
            width: 100%; height: 450px; border: 0; filter: grayscale(30%) contrast(1.1); transition: all 0.6s ease;
        }
        .map-container:hover .map-iframe { filter: grayscale(0%) contrast(1); }
        .floating-card {
            position: absolute; bottom: 25px; right: 25px; background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 25px; border-radius: 20px;
            border-right: 4px solid #D4AF37; box-shadow: 0 10px 30px rgba(0,0,0,0.7); direction: rtl; text-align: right;
            max-width: 280px; transform: translateY(30px); opacity: 0; transition: all 0.5s ease 0.1s;
        }
        .map-container:hover .floating-card { transform: translateY(0); opacity: 1; }
        .venue-title { color: #D4AF37; margin: 0 0 8px 0; font-family: 'Amiri', serif; font-size: 1.5rem; }
        .venue-desc { color: #E2E8F0; margin: 0 0 20px 0; font-family: 'Cairo', sans-serif; font-size: 0.9rem; line-height: 1.6; }
        .btn-directions {
            display: block; background: linear-import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
import os

# 1. إعداد الصفحة الأساسي
st.set_page_config(page_title="Mohammad & Sarah Wedding", page_icon="✨", layout="wide")

# =========================================================
# قاعدة بيانات مصغرة لحفظ الحجوزات (ملف CSV محلي)
# =========================================================
DB_FILE = "guests_db.csv"

def load_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=["الاسم", "عدد المرافقين", "إجمالي الأشخاص"])
    return pd.read_csv(DB_FILE)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

# =========================================================
# نظام التوجيه الذكي (Router): اللوحة السرية / صفحة الـ VIP / الموقع الرئيسي
# =========================================================
query_params = st.query_params

# 1. حالة الرابط السري للعريس (لوحة الإدارة المخفية)
if query_params.get("admin") == "mk1234":
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        h1, h2, h3, p { font-family: 'Cairo', sans-serif; color: #E2E8F0; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #D4AF37; font-family: Amiri; margin-top: 50px;'>👑 لوحة تحكم العريس السرية 👑</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>هذه الصفحة لا تظهر لأحد غيرك يا محمد</p>", unsafe_allow_html=True)
    
    df = load_db()
    
    if not df.empty:
        total_guests = df["إجمالي الأشخاص"].sum()
        
        # عرض العدد الإجمالي بشكل ضخم
        st.markdown(f"""
        <div style='background: rgba(212, 175, 55, 0.1); border: 2px solid #D4AF37; border-radius: 15px; padding: 20px; text-align: center; margin: 30px auto; max-width: 400px;'>
            <h3 style='margin: 0; color: #D4AF37;'>إجمالي الحضور المتوقع</h3>
            <h1 style='font-size: 4rem; margin: 10px 0; color: #FFFFFF;'>{total_guests}</h1>
            <p style='margin: 0;'>شخص (يشمل المرافقين)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("تحميل قائمة الحضور (Excel/CSV) 📥", data=csv, file_name="wedding_guests.csv", mime="text/csv")
    else:
        st.info("لم يقم أحد بتأكيد الحضور حتى الآن.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("تسجيل الخروج والعودة للموقع 🚪"):
        st.query_params.clear()
        st.rerun()

# 2. حالة صفحة تذكرة الـ VIP
elif "vip" in query_params:
    guest_name = query_params.get("name", "ضيفنا الكريم")
    guests_count = query_params.get("count", "بدون مرافقين")
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;700;900&display=swap');
        
        :root { --vip-gold: #D4AF37; --vip-text: #E2E8F0; --vip-muted: #cbd5e1; }
        h1 { font-family: 'Amiri', serif !important; color: var(--vip-gold) !important; font-size: clamp(2rem, 8vw, 3rem); margin-bottom: 10px; }
        p { font-family: 'Cairo', sans-serif !important; color: var(--vip-text) !important; font-size: clamp(1rem, 3vw, 1.2rem); }
        
        .stApp { background-image: url("https://images.unsplash.com/photo-1544078755-6b8d2b2c938a?q=80&w=2070&auto=format&fit=crop"); background-size: cover; background-position: center; }
        .stApp::before { content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(10, 10, 10, 0.85); z-index: 0; }
        header {visibility: hidden;}
        .main .block-container { z-index: 1; position: relative; padding-top: 3rem; display: flex; flex-direction: column; align-items: center; }
        
        .ticket-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); border: 1px solid rgba(212, 175, 55, 0.4); border-radius: 20px; padding: clamp(20px, 5vw, 40px); text-align: center; box-shadow: 0 20px 50px rgba(212, 175, 55, 0.2); max-width: 500px; width: 90%; animation: slide-up 1s ease-out forwards; }
        @keyframes slide-up { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        
        .vip-badge { background: linear-gradient(45deg, #D4AF37, #F3E5AB); color: #000; padding: 5px 20px; border-radius: 30px; font-weight: bold; font-family: 'Cairo', sans-serif; font-size: clamp(1rem, 3vw, 1.2rem); display: inline-block; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown(f"""
        <div class="ticket-card">
            <div class="vip-badge">VIP PASS 🌟</div>
            <h1>أهلاً بك يا {guest_name}</h1>
            <p>تذكرتك الملكية مفعلة وجاهزة.</p>
            <hr style="border-color: rgba(212,175,55,0.3); margin: 20px 0;">
            <p style="color: var(--vip-muted) !important; font-size: clamp(0.9rem, 3vw, 1.1rem) !important; text-align: right; direction: rtl;">
                <b>الحدث:</b> حفل زفاف محمد وسارة 💍<br>
                <b>عدد المرافقين المسجلين:</b> {guests_count}<br>
                <b>الحالة:</b> <span style="color: #4ade80;">تم تأكيد الحضور والتسجيل بنجاح ✔️</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("العودة إلى تفاصيل الحفل ↩️"):
        st.query_params.clear()
        st.rerun()

# 3. حالة الموقع الرئيسي (إذا لم يكن الرابط سرياً ولا تذكرة VIP)
else:
    # =========================================================
    # الصفحة الرئيسية (التصميم والمحتوى)
    # =========================================================

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;700;900&display=swap');
        
        :root {
            --primary-gold: #D4AF37;
            --light-gold: #F3E5AB;
            --text-main: #FFFFFF;
            --text-muted: #E2E8F0;
            --overlay-color: rgba(10, 15, 30, 0.85);
        }

        h1 { font-family: 'Amiri', serif !important; color: var(--primary-gold) !important; text-align: center; }
        h2 { font-family: 'Amiri', serif !important; color: var(--primary-gold) !important; font-size: clamp(2rem, 8vw, 3rem) !important; text-align: center; margin-top: 50px !important; }
        h3 { font-family: 'Cairo', sans-serif !important; color: var(--text-main) !important; font-size: clamp(1rem, 4vw, 1.5rem) !important; font-weight: 300 !important; letter-spacing: 2px; text-align: center; }
        p { font-family: 'Cairo', sans-serif !important; color: var(--text-muted) !important; font-size: clamp(1rem, 3vw, 1.2rem) !important; text-align: center; }

        .stApp { background-image: url("https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=2070&auto=format&fit=crop"); background-size: cover; background-position: center; background-attachment: fixed; }
        .stApp::before { content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: var(--overlay-color); z-index: 0; }
        header, #MainMenu, footer {visibility: hidden;}
        .main .block-container { z-index: 1; position: relative; padding-top: 1rem; }
        
        @keyframes pulse-gold { 0% { text-shadow: 0 0 10px rgba(212, 175, 55, 0.4); } 50% { text-shadow: 0 0 25px rgba(212, 175, 55, 0.8); } 100% { text-shadow: 0 0 10px rgba(212, 175, 55, 0.4); } }
        .glowing-title { font-size: clamp(3rem, 12vw, 5rem) !important; margin-bottom: 0; animation: pulse-gold 3s infinite; }
        
        .content-box { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: clamp(15px, 4vw, 30px); margin: 20px 0; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # الدخول السينمائي
    # ---------------------------------------------------------
    cinematic_intro_html = """
    <script>
        const parentDoc = window.parent.document;
        if (!parentDoc.getElementById('cinematic-intro')) {
            const introDiv = parentDoc.createElement('div');
            introDiv.id = 'cinematic-intro';
            introDiv.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:black; z-index:999999; transition: opacity 1.5s ease; display:flex; flex-direction:column; justify-content:center; align-items:center;';
            
            introDiv.innerHTML = `
                <video id="intro-vid" autoplay muted playsinline style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0; opacity: 0.8;">
                    <source src="https://videos.pexels.com/video-files/3195394/3195394-uhd_2560_1440_25fps.mp4" type="video/mp4">
                </video>
                <div style="position:absolute; z-index:10; text-align:center; width: 100%;">
                    <h1 style="color:#D4AF37; font-family: 'Amiri', serif; font-size:clamp(3rem, 10vw, 4rem); text-shadow: 2px 2px 10px #000; margin:0;">محمد & سارة</h1>
                </div>
                <button id="skip-btn" style="position:absolute; bottom:10%; padding:10px 25px; font-size:clamp(1rem, 3vw, 1.2rem); background:rgba(212,175,55,0.3); color:white; border:1px solid #D4AF37; border-radius:30px; cursor:pointer; z-index:10; font-family:'Cairo', sans-serif; backdrop-filter: blur(5px); transition: 0.3s;">دخول للموقع 🤍</button>
            `;
            parentDoc.body.appendChild(introDiv);
            const vid = parentDoc.getElementById('intro-vid');
            const skipBtn = parentDoc.getElementById('skip-btn');
            function removeIntro() { introDiv.style.opacity = '0'; setTimeout(() => { introDiv.remove(); }, 1500); }
            vid.onended = removeIntro; skipBtn.onclick = removeIntro;
        }
    </script>
    """
    components.html(cinematic_intro_html, width=0, height=0)

    # ---------------------------------------------------------
    # العنوان والعداد
    # ---------------------------------------------------------
    st.markdown("""
        <div style="margin-bottom: 2rem; margin-top: 2rem;">
            <h1 class="glowing-title">محمد & سارة</h1>
            <h3>ندعوكم لمشاركتنا أجمل لحظات العمر</h3>
        </div>
    """, unsafe_allow_html=True)

    custom_timer_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap" rel="stylesheet">
    <style>
        body { display: flex; justify-content: center; align-items: center; background-color: transparent; margin: 0; font-family: 'Cairo', sans-serif; }
        .glass-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.15); padding: 30px 50px; display: flex; gap: 40px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); direction: rtl; transition: 0.3s; flex-wrap: wrap; justify-content: center; }
        .glass-container:hover { transform: translateY(-5px); box-shadow: 0 12px 40px 0 rgba(212, 175, 55, 0.3); }
        .time-box { display: flex; flex-direction: column; align-items: center; min-width: 70px; }
        .number { font-size: 3.5rem; font-weight: 700; color: #D4AF37; margin: 0; line-height: 1; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
        .label { font-size: 1.2rem; color: #F8FAFC; margin-top: 5px; }
        @media (max-width: 600px) { .glass-container { gap: 15px; padding: 20px; } .number { font-size: 2.2rem; } .label { font-size: 0.9rem; } .time-box { min-width: 55px; } }
    </style>
    </head>
    <body>
    <div class="glass-container">
        <div class="time-box"><span class="number" id="days">00</span><span class="label">يوم</span></div>
        <div class="time-box"><span class="number" id="hours">00</span><span class="label">ساعة</span></div>
        <div class="time-box"><span class="number" id="minutes">00</span><span class="label">دقيقة</span></div>
        <div class="time-box"><span class="number" id="seconds">00</span><span class="label">ثانية</span></div>
    </div>
    <script>
        const weddingDate = new Date("May 31, 2026 19:00:00").getTime();
        const x = setInterval(function() {
            const now = new Date().getTime();
            const distance = weddingDate - now;
            document.getElementById("days").innerHTML = Math.floor(distance / (1000 * 60 * 60 * 24)).toString().padStart(2, '0');
            document.getElementById("hours").innerHTML = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)).toString().padStart(2, '0');
            document.getElementById("minutes").innerHTML = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)).toString().padStart(2, '0');
            document.getElementById("seconds").innerHTML = Math.floor((distance % (1000 * 60)) / 1000).toString().padStart(2, '0');
        }, 1000);
    </script>
    </body>
    </html>
    """
    components.html(custom_timer_html, height=220)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # قسم الصور والخريطة
    # ---------------------------------------------------------
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

    st.markdown("<h2>موقع الحفل 📍</h2>", unsafe_allow_html=True)
    interactive_map_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        .map-container { position: relative; width: 100%; max-width: 900px; margin: 20px auto; border-radius: 25px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.5), 0 0 15px rgba(212, 175, 55, 0.2); border: 2px solid rgba(212, 175, 55, 0.4); transform: perspective(1200px) rotateX(4deg) scale(0.96); transition: all 0.6s cubic-bezier(0.25, 0.8, 0.25, 1); }
        .map-container:hover { transform: perspective(1200px) rotateX(0deg) scale(1); box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 30px rgba(212, 175, 55, 0.5); border: 2px solid rgba(212, 175, 55, 0.9); }
        .map-iframe { width: 100%; height: 450px; border: 0; filter: grayscale(30%) contrast(1.1); transition: all 0.6s ease; }
        .map-container:hover .map-iframe { filter: grayscale(0%) contrast(1); }
        .floating-card { position: absolute; bottom: 25px; right: 25px; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 25px; border-radius: 20px; border-right: 4px solid #D4AF37; box-shadow: 0 10px 30px rgba(0,0,0,0.7); direction: rtl; text-align: right; max-width: 280px; transform: translateY(30px); opacity: 0; transition: all 0.5s ease 0.1s; }
        .map-container:hover .floating-card { transform: translateY(0); opacity: 1; }
        .venue-title { color: #D4AF37; margin: 0 0 8px 0; font-family: 'Amiri', serif; font-size: 1.5rem; }
        .venue-desc { color: #E2E8F0; margin: 0 0 20px 0; font-family: 'Cairo', sans-serif; font-size: 0.9rem; line-height: 1.6; }
        .btn-directions { display: block; background: linear-gradient(45deg, #D4AF37, #F3E5AB); color: #0F172A !important; padding: 10px 0; border-radius: 30px; text-decoration: none; font-weight: 900; font-family: 'Cairo', sans-serif; text-align: center; transition: all 0.3s ease; box-shadow: 0 0 15px rgba(212,175,55,0.4); }
        .btn-directions:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(212,175,55,0.8); }
        @media (max-width: 768px) { .map-container { transform: none; box-shadow: 0 10px 20px rgba(0,0,0,0.5); border: 2px solid rgba(212, 175, 55, 0.6);} .map-container:hover { transform: none; } .floating-card { position: relative; bottom: 0; right: 0; max-width: 100%; border-radius: 0 0 25px 25px; transform: none; opacity: 1; border-right: none; border-top: 2px solid #D4AF37; padding: 15px; } .map-iframe { height: 300px; filter: none;} }
    </style>
    </head>
    <body style="margin:0; background: transparent; padding: 10px;">
        <div class="map-container">
            <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3322.993864119795!2d35.3934256764207!3d33.60546367332862!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x151ee52e784728f9%3A0xaa57f0e88d65b592!2sSofia%20Palace!5e0!3m2!1sen!2slb!4v1772620814491!5m2!1sen!2slb" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            <div class="floating-card">
                <h3 class="venue-title">Sofia Palace</h3>
                <p class="venue-desc">قاعة الاحتفالات الكبرى الكلاسيكية<br>الرميلة، لبنان<br>بانتظاركم بكل حب 🤍</p>
                <a href="https://maps.app.goo.gl/YZCjR4FNNa5tCE8G6" target="_blank" class="btn-directions">احصل على الاتجاهات 🚗</a>
            </div>
        </div>
    </body>
    </html>
    """
    components.html(interactive_map_html, height=550)
    st.markdown("<p style='font-family: Amiri !important; color: var(--primary-gold) !important; font-size: clamp(1.2rem, 4vw, 1.5rem) !important; margin-top: 10px;'>\"دمتم لنا أهلاً وأحباباً نشاركهم أفراحنا\"</p>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 7. نظام تأكيد الحضور (منع التكرار والتوجيه لموقعك)
    # ---------------------------------------------------------
    st.markdown("<h2>تأكيد الحضور 🎟️</h2>", unsafe_allow_html=True)
    st.markdown("<p>احجز مقعدك واستخرج تذكرتك الرقمية الخاصة</p>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            rsvp_name = st.text_input("الاسم الكريم", placeholder="اكتب اسمك هنا...")
        with col_form2:
            guests_count = st.selectbox("عدد المرافقين", ["بدون مرافقين", "مرافق واحد", "مرافقان", "3 مرافقين"])
        
        if st.button("تأكيد الحضور واستخراج التذكرة 🎫"):
            if rsvp_name:
                df = load_db()
                
                # التحقق من عدم التكرار
                if rsvp_name.strip() in df['الاسم'].values:
                    st.error(f"عذراً يا {rsvp_name}، لقد قمت بتأكيد حضورك مسبقاً! لا يمكن الحجز مرتين.")
                else:
                    import qrcode
                    from io import BytesIO
                    
                    companions_map = {"بدون مرافقين": 0, "مرافق واحد": 1, "مرافقان": 2, "3 مرافقين": 3}
                    total_persons = 1 + companions_map.get(guests_count, 0)
                    
                    new_guest = pd.DataFrame([{"الاسم": rsvp_name.strip(), "عدد المرافقين": guests_count, "إجمالي الأشخاص": total_persons}])
                    df = pd.concat([df, new_guest], ignore_index=True)
                    save_db(df)
                    
                    # رابطك الحقيقي
                    BASE_URL = "https://mohamad-sarahwedding-pycf9neap43w7zh9pewmhu.streamlit.app" 
                    encoded_name = urllib.parse.quote(rsvp_name)
                    encoded_count = urllib.parse.quote(guests_count)
                    ticket_url = f"{BASE_URL}/?vip=true&name={encoded_name}&count={encoded_count}"
                    
                    qr = qrcode.QRCode(version=1, box_size=10, border=2)
                    qr.add_data(ticket_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="#D4AF37", back_color="#0F172A")
                    
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    
                    st.success(f"تم تأكيد حضورك يا {rsvp_name}! نحن بانتظارك.")
                    st.balloons()
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9)); border: 2px dashed #D4AF37; padding: 20px; border-radius: 15px; text-align: center; margin-top: 20px; box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);'>
                        <h3 style='color: #D4AF37; font-family: Amiri;'>تذكرة دخول VIP 🌟</h3>
                        <p style='color: #E2E8F0; font-family: Cairo; font-size: 1.2rem;'>الضيف المُميز: <b>{rsvp_name}</b></p>
                        <p style='color: #cbd5e1; font-family: Cairo; font-size: 0.9rem;'>امسح الرمز أدناه بهاتفك للدخول لصفحة تذكرتك الخاصة</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_qr1, col_qr2, col_qr3 = st.columns([1, 1, 1])
                    with col_qr2:
                        st.image(buf, use_container_width=True, caption="امسحني بكاميرا الهاتف 📸")
                        
            else:
                st.error("يرجى إدخال اسمك أولاً لنتمكن من إصدار تذكرتك!")
                
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 8. سجل التهاني
    # ---------------------------------------------------------
    st.markdown("<h2>سجل التهاني 💌</h2>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        guest_msg_name = st.text_input("اسمك (لكي نشكرك)", key="msg_name")
        message = st.text_area("اترك لنا ذكرى جميلة من قلبك...", key="msg", height=100)
        
        if st.button("إرسال التهنئة 🕊️"):
            if message:
                import random
                name_to_use = guest_msg_name if guest_msg_name else "ضيفنا الغالي"
                ai_replies = [
                    f"يا لها من كلمات تلامس القلب! شكراً لك يا {name_to_use} على هذه الأمنيات الرائعة. 🤍",
                    f"لقد أسعدتنا جداً رسالتك يا {name_to_use}، وجودك معنا سيزيد فرحتنا أضعافاً! ✨",
                    f"أمنياتك تعني لنا الكثير يا {name_to_use}، شكراً لمشاركتنا هذه اللحظات التي لا تُنسى. 💍"
                ]
                st.info(random.choice(ai_replies), icon="🤖")
            else:
                st.warning("الرسالة فارغة! لا تحرمنا من كلماتك الطيبة.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 9. رحلة تصميم منزل العمر والتذييل
    # ---------------------------------------------------------
    st.markdown("<h2>عشنا الصغير 🛋️</h2>", unsafe_allow_html=True)
    st.markdown("<p>نظرة خاطفة على تفاصيل وتصميم مملكتنا القادمة...</p>", unsafe_allow_html=True)

    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    col_home1, col_home2 = st.columns(2)
    with col_home1:
        st.image("https://images.unsplash.com/photo-1600210492486-724fe5c67fb0", caption="زوايا دافئة وتفاصيل ذكية 💡")
    with col_home2:
        st.image("https://images.unsplash.com/photo-1616594039964-ae9021a400a0", caption="الغرفة التي أصرت عروستي أن تكون غرفة النوم الرئيسية 🤍")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-top: 60px; padding-bottom: 20px;">
            <p style="font-size: 0.9rem !important; color: rgba(226, 232, 240, 0.5) !important;">
                Designed & Powered by <span style="color: var(--primary-gold); font-weight: bold; letter-spacing: 1px;">MK Technology</span> © 2026
            </p>
        </div>
    """, unsafe_allow_html=True)
