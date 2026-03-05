# ---------------------------------------------------------
# 1. حالة الرابط السري للعريس (إدارة الطاولات والمعازيم المتقدمة)
# ---------------------------------------------------------
if query_params.get("admin") == "mk1234":
    st.markdown("""
<style>
.stApp { background-color: #0F172A; }
h1, h2, h3, p { font-family: 'Cairo', sans-serif; color: #E2E8F0; direction: rtl; text-align: right; }

/* تصميم أزرار الفلترة */
div.row-widget.stRadio > div { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 15px; justify-content: center; }
div.row-widget.stRadio > div > label { cursor: pointer; transition: 0.3s; }

div.stButton > button { background: linear-gradient(45deg, #D4AF37, #F3E5AB) !important; border: none !important; border-radius: 30px !important; padding: 10px 25px !important; box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4) !important; transition: all 0.3s ease !important; width: 100%;}
div.stButton > button p { color: #000000 !important; font-family: 'Cairo', sans-serif !important; font-weight: 900 !important; font-size: 1.2rem !important; margin: 0 !important; }
</style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #D4AF37; font-family: Amiri; margin-top: 30px;'>👑 لوحة تحكم العريس الذكية 👑</h1>", unsafe_allow_html=True)
    
    df = load_db()
    
    if not df.empty:
        # فلترة تفاعلية أنيقة
        filter_option = st.radio("الفرز:", ["الكل 👥", "جهة العريس 🤵", "جهة العروس 👰"], horizontal=True, label_visibility="collapsed")
        
        # تحديد البيانات المعروضة بناءً على الفلتر
        if filter_option == "جهة العريس 🤵":
            view_df = df[df['الجهة'] == 'جهة العريس 🤵'].copy()
            count = view_df['إجمالي الأشخاص'].sum()
            st.markdown(f"<h3 style='text-align: center; color: #60A5FA;'>إجمالي معازيم العريس: <span style='font-size: 2.5rem; color: #FFFFFF;'>{count}</span> ضيف</h3>", unsafe_allow_html=True)
        elif filter_option == "جهة العروس 👰":
            view_df = df[df['الجهة'] == 'جهة العروس 👰'].copy()
            count = view_df['إجمالي الأشخاص'].sum()
            st.markdown(f"<h3 style='text-align: center; color: #F472B6;'>إجمالي معازيم العروس: <span style='font-size: 2.5rem; color: #FFFFFF;'>{count}</span> ضيف</h3>", unsafe_allow_html=True)
        else:
            view_df = df.copy()
            count = view_df['إجمالي الأشخاص'].sum()
            st.markdown(f"<h3 style='text-align: center; color: #D4AF37;'>الإجمالي الكلي للحضور: <span style='font-size: 2.5rem; color: #FFFFFF;'>{count}</span> ضيف</h3>", unsafe_allow_html=True)

        st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 1rem;'>💡 <b>تلميح:</b> انقر على (رقم الطاولة) لتعديله. ولحذف اسم مكرر، قم بتحديد المربع في عمود (حذف؟) ثم اضغط حفظ بالأسفل.</p>", unsafe_allow_html=True)
        
        # إضافة عمود وهمي للحذف للواجهة فقط
        view_df["حذف؟"] = False
        
        # عرض الجدول بتصميم فخم وأيقونات
        edited_df = st.data_editor(
            view_df,
            column_config={
                "حذف؟": st.column_config.CheckboxColumn("🗑️ حذف؟", default=False),
                "الاسم": st.column_config.TextColumn("👤 الاسم", disabled=True),
                "الجهة": st.column_config.TextColumn("📍 الجهة", disabled=True),
                "عدد المرافقين": st.column_config.TextColumn("👨‍👩‍👧‍👦 المرافقين", disabled=True),
                "إجمالي الأشخاص": st.column_config.NumberColumn("🔢 الإجمالي", disabled=True),
                "رقم الطاولة": st.column_config.TextColumn("🪑 رقم الطاولة")
            },
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("💾 تنفيذ التعديلات وحفظ (الطاولات / الحذف)"):
            # 1. استخراج الأسماء التي طُلب حذفها
            names_to_delete = edited_df[edited_df["حذف؟"] == True]["الاسم"].tolist()
            
            # 2. تحديث أرقام الطاولات في قاعدة البيانات الأصلية
            for index, row in edited_df.iterrows():
                name = row["الاسم"]
                new_table = row["رقم الطاولة"]
                df.loc[df["الاسم"] == name, "رقم الطاولة"] = new_table
            
            # 3. تنفيذ الحذف من القاعدة الأصلية
            if names_to_delete:
                df = df[~df["الاسم"].isin(names_to_delete)]
                
            # 4. الحفظ وإعادة التحميل
            save_db(df)
            st.success("✅ تم حفظ كل التعديلات بنجاح!")
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("تحميل القائمة كملف Excel/CSV 📥", data=csv, file_name="wedding_guests.csv", mime="text/csv")
    else:
        st.warning("لم يقم أحد بتأكيد الحضور حتى الآن.")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("تسجيل الخروج والعودة للموقع 🚪"):
        st.query_params.clear()
        st.rerun()
