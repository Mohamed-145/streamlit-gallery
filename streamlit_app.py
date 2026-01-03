import streamlit as st
import pandas as pd
import cv2
import numpy as np
import google.generativeai as genai
from datetime import datetime

# ==========================================
# 1. إعدادات التصميم الاحترافي (Global Style)
# ==========================================
st.set_page_config(
    page_title="سنتر الأستاذ",
    page_icon="🎓",
    layout="centered", # التركيز في المنتصف أفضل للموبايل
    initial_sidebar_state="collapsed"
)

# حقن كود CSS لإصلاح مشاكل الموبايل والتجميل
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Tajawal:wght@400;700&display=swap');

/* توحيد الخط والاتجاه */
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
    text-align: right;
}

/* أهم إصلاح: منع تكسير الحروف العربية */
h1, h2, h3, p, div, span {
    white-space: normal !important;
    line-height: 1.6 !important;
}

/* خلفية التطبيق */
.stApp {
    background-color: #F8F9FA;
}

/* إخفاء القائمة الجانبية تماماً لتوسيع الشاشة */
[data-testid="stSidebar"] { display: none; }

/* تصميم العناوين */
h1 {
    font-family: 'Cairo', sans-serif !important;
    color: #1565C0 !important;
    text-align: center !important;
    font-size: 28px !important;
}

/* الأزرار الاحترافية */
.stButton>button {
    width: 100%;
    height: 55px;
    border-radius: 12px;
    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
    color: white;
    border: none;
    font-size: 18px;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(21, 101, 192, 0.2);
    transition: transform 0.2s;
}
.stButton>button:active { transform: scale(0.98); }

/* زر الكاميرا */
div[data-testid="stCameraInput"] button {
    background-color: #FF6F00 !important;
    color: white !important;
    border-radius: 50%;
    height: 65px;
    width: 65px;
    border: 3px solid white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

/* رسائل التنبيه */
.stSuccess, .stInfo, .stWarning {
    border-radius: 10px;
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الهيدر والإعدادات (بدون Sidebar)
# ==========================================
st.markdown("<h1>🎓 سنتر الأستاذ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555; margin-top:-15px;'>محمد السعيد أبوهاشم | خبير اللغة العربية</p>", unsafe_allow_html=True)

# وضع الإعدادات في قائمة منسدلة بالأعلى لتوفير المساحة
with st.expander("⚙️ اضغط هنا لإدخال مفتاح التشغيل (API Key)"):
    api_key = st.text_input("مفتاح Google API", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ تم الاتصال بنجاح")
    else:
        st.warning("⚠️ أدخل المفتاح ليعمل الذكاء الاصطناعي")

# تهيئة الذاكرة
if 'attendance' not in st.session_state: st.session_state.attendance = []
if 'scores' not in st.session_state: st.session_state.scores = []

# ==========================================
# 3. التطبيق (نظام التبويبات والكروت)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📸 الحضور", "🧠 الشرح", "📝 التصحيح", "📂 الملفات"])

# --- 1. الحضور ---
with tab1:
    with st.container(border=True): # كارت أنيق
        st.markdown("### 🤳 تسجيل الحضور")
        st.info("وجه الكاميرا نحو كود الطالب")
        
        cam = st.camera_input("الكاميرا", label_visibility="collapsed")
        
        if cam:
            bytes_data = cam.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(img)
            
            if data:
                now = datetime.now().strftime("%I:%M %p")
                date_now = datetime.now().strftime("%Y-%m-%d")
                
                # التحقق من التكرار
                if not any(d['id'] == data and d['date'] == date_now for d in st.session_state.attendance):
                    st.session_state.attendance.append({'id': data, 'name': "طالب", 'time': now, 'date': date_now})
                    st.success(f"✅ تم تسجيل: {data}")
                    st.balloons()
                else:
                    st.warning(f"⚠️ الطالب {data} مسجل مسبقاً!")

# --- 2. الشرح (الستتر) ---
with tab2:
    with st.container(border=True):
        st.markdown("### 🤖 المساعد الأكاديمي")
        
        col1, col2 = st.columns(2)
        with col1: subj = st.selectbox("المادة", ["لغة عربية", "تربية إسلامية"])
        with col2: grade = st.selectbox("الصف", ["الرابع", "الخامس", "السادس", "الإعدادي"])
        
        topic = st.text_input("عنوان الدرس", placeholder="مثال: المفعول المطلق")
        
        if st.button("🚀 تحضير الدرس"):
            if api_key and topic:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                أنت معلم خبير (30 سنة). حضر درس '{topic}' في مادة '{subj}' للصف '{grade}'.
                التنسيق (Markdown):
                1. **🪝 القصة:** قصة قصيرة جداً (سطرين).
                2. **💎 القاعدة:** شرح مبسط + شواهد.
                3. **🔥 خلي بالك:** (ضعها في مربع) التريكات.
                4. **❓ تدريب:** سؤال سريع.
                """
                with st.spinner("جارٍ إعداد الشرح..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        # تنسيق صندوق التريكات
                        final_res = response.text.replace("خلي بالك", "⚠️ **خلي بالك**").replace("تريكات", "🔥 **تريكات**")
                        st.markdown(final_res)
                    except:
                        st.error("تأكد من مفتاح الـ API")

# --- 3. التصحيح ---
with tab3:
    with st.container(border=True):
        st.markdown("### 🔍 المصحح الذكي")
        student_name = st.text_input("اسم الطالب")
        uploaded_file = st.camera_input("صورة الورقة", key="grading_cam")
        
        if uploaded_file and student_name and st.button("بدء التصحيح"):
            if api_key:
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("جارٍ تحليل الإجابات..."):
                    try:
                        res = model.generate_content([
                            "أنت مصحح. صحح الورقة، اعط درجة من 20، واكتب نصيحة.",
                            {"mime_type": "image/jpeg", "data": uploaded_file.getvalue()}
                        ])
                        st.success("تم التصحيح!")
                        st.markdown(res.text)
                        
                        st.session_state.scores.append({
                            'date': str(datetime.now().date()),
                            'name': student_name,
                            'result': res.text[:100]
                        })
                        
                        # رابط واتساب
                        wa_text = f"تقرير {student_name}: {res.text}"
                        st.link_button("📲 إرسال التقرير واتساب", f"https://wa.me/?text={wa_text.replace(' ', '%20').replace(chr(10), '%0A')}")
                    except:
                        st.error("حدث خطأ في قراءة الصورة")

# --- 4. الملفات ---
with tab4:
    with st.container(border=True):
        st.markdown("### 💾 تحميل البيانات")
        st.caption("احفظ ملفاتك قبل إغلاق التطبيق")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.attendance:
                df_att = pd.DataFrame(st.session_state.attendance)
                st.download_button("📥 ملف الحضور", df_att.to_csv(index=False).encode('utf-8-sig'), "attendance.csv")
            else:
                st.info("لا يوجد حضور اليوم")
                
        with c2:
            if st.session_state.scores:
                df_scr = pd.DataFrame(st.session_state.scores)
                st.download_button("📥 ملف الدرجات", df_scr.to_csv(index=False).encode('utf-8-sig'), "scores.csv")
            else:
                st.info("لا توجد درجات")
