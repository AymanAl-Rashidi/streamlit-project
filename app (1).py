import streamlit as st
import requests
import os
import base64
import io
import json
from gtts import gTTS
from streamlit_lottie import st_lottie
import time
from datetime import datetime, date, timedelta
from database import (
    init_db, get_db, get_or_create_user, User, MedicalHistory, 
    Doctor, Appointment, Medication, MedicationReminder, HealthMetric
)

# Page configuration
st.set_page_config(
    page_title="سند - المساعد الطبي الذكي",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphism UI and Arabic RTL
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    /* Global RTL and Font Settings */
    * {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    html, body, [class*="css"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Main gradient background */
    .stApp {
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
        min-height: 100vh;
    }
    
    /* Glassmorphism container */
    .glass-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(78, 84, 200, 0.95) !important;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    p, span, label, .stMarkdown {
        color: white !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 15px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: white !important;
        direction: rtl !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 15px 20px;
        border-radius: 20px;
        margin: 10px 0;
        max-width: 80%;
        animation: slideIn 0.3s ease;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-right: auto;
        margin-left: 20%;
        color: white;
    }
    
    .bot-message {
        background: rgba(255, 255, 255, 0.25);
        margin-left: auto;
        margin-right: 20%;
        color: white;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Persona cards */
    .persona-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .persona-card:hover {
        transform: scale(1.05);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .persona-card.selected {
        border-color: #FFD700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.4);
    }
    
    /* Emotion result cards */
    .result-card-safe {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
    }
    
    .result-card-danger {
        background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# Initialize database
init_db()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'farah_persona' not in st.session_state:
    st.session_state.farah_persona = None
if 'farah_messages' not in st.session_state:
    st.session_state.farah_messages = []
if 'doctor_messages' not in st.session_state:
    st.session_state.doctor_messages = []
if 'db' not in st.session_state:
    st.session_state.db = get_db()
if 'current_user' not in st.session_state:
    st.session_state.current_user = get_or_create_user(st.session_state.db)

# OpenFDA Drug Database API helper
def query_openfda_drug(drug_name):
    """Query OpenFDA for drug information"""
    try:
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}+openfda.generic_name:{drug_name}&limit=1"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                openfda = result.get('openfda', {})
                return {
                    'found': True,
                    'brand_name': openfda.get('brand_name', ['غير متوفر'])[0] if openfda.get('brand_name') else 'غير متوفر',
                    'generic_name': openfda.get('generic_name', ['غير متوفر'])[0] if openfda.get('generic_name') else 'غير متوفر',
                    'manufacturer': openfda.get('manufacturer_name', ['غير متوفر'])[0] if openfda.get('manufacturer_name') else 'غير متوفر',
                    'route': openfda.get('route', ['غير متوفر'])[0] if openfda.get('route') else 'غير متوفر',
                    'substance': openfda.get('substance_name', ['غير متوفر'])[0] if openfda.get('substance_name') else 'غير متوفر',
                    'warnings': result.get('warnings', ['لا توجد تحذيرات مسجلة'])[0] if result.get('warnings') else None,
                    'drug_interactions': result.get('drug_interactions', ['لا توجد تفاعلات مسجلة'])[0] if result.get('drug_interactions') else None,
                    'contraindications': result.get('contraindications', ['لا توجد موانع مسجلة'])[0] if result.get('contraindications') else None,
                    'dosage': result.get('dosage_and_administration', ['غير متوفر'])[0] if result.get('dosage_and_administration') else None,
                    'indications': result.get('indications_and_usage', ['غير متوفر'])[0] if result.get('indications_and_usage') else None,
                }
        return {'found': False}
    except Exception as e:
        return {'found': False, 'error': str(e)}

def search_openfda_drugs(query):
    """Search OpenFDA for matching drugs"""
    try:
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{query}*+openfda.generic_name:{query}*&limit=10"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            drugs = []
            if data.get('results'):
                for result in data['results']:
                    openfda = result.get('openfda', {})
                    brand = openfda.get('brand_name', [''])[0] if openfda.get('brand_name') else ''
                    generic = openfda.get('generic_name', [''])[0] if openfda.get('generic_name') else ''
                    if brand or generic:
                        drugs.append({
                            'brand_name': brand,
                            'generic_name': generic
                        })
            return drugs
        return []
    except:
        return []

# Hugging Face API helper
def query_huggingface(prompt, model="meta-llama/Llama-3.2-3B-Instruct"):
    api_key = os.environ.get("HUGGINGFACE_API_KEY", "")
    if not api_key:
        return "عذراً، مفتاح API غير متوفر. يرجى إضافة مفتاح Hugging Face."
    
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'لم أتمكن من فهم السؤال')
        return "عذراً، حدث خطأ في الاتصال بالخادم"
    except Exception as e:
        return f"عذراً، حدث خطأ: {str(e)}"

# Text to Speech function with voice type support
def text_to_speech(text, lang='ar', voice_type='male'):
    try:
        # gTTS doesn't support different voices, but we use slow=True for male (deeper)
        # and slow=False for female (faster, lighter)
        slow = (voice_type == 'male')
        tts = gTTS(text=text, lang=lang, slow=slow)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        return None

# Load Lottie animation
def load_lottie_url(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="font-size: 2.5em; margin-bottom: 10px;">🏥 سند</h1>
        <p style="font-size: 1.1em; opacity: 0.9;">المساعد الطبي الذكي</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons
    if st.button("🏠 الصفحة الرئيسية", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()
    
    if st.button("💜 فرح - الدعم النفسي", use_container_width=True):
        st.session_state.current_page = 'farah'
        st.rerun()
    
    if st.button("👨‍⚕️ الطبيب الذكي", use_container_width=True):
        st.session_state.current_page = 'doctor'
        st.rerun()
    
    if st.button("😊 مرآة المشاعر", use_container_width=True):
        st.session_state.current_page = 'emotion'
        st.rerun()
    
    if st.button("💊 تعارض الأدوية", use_container_width=True):
        st.session_state.current_page = 'drugs'
        st.rerun()
    
    st.markdown("---")
    st.markdown("<p style='opacity: 0.7; font-size: 0.9em;'>الخدمات الشخصية:</p>", unsafe_allow_html=True)
    
    if st.button("👤 الملف الشخصي", use_container_width=True):
        st.session_state.current_page = 'profile'
        st.rerun()
    
    if st.button("📅 المواعيد", use_container_width=True):
        st.session_state.current_page = 'appointments'
        st.rerun()
    
    if st.button("💊 الأدوية والتذكيرات", use_container_width=True):
        st.session_state.current_page = 'medications'
        st.rerun()
    
    if st.button("📊 مؤشرات الصحة", use_container_width=True):
        st.session_state.current_page = 'health_metrics'
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px; opacity: 0.8;">
        <small>صُنع بـ ❤️ للمجتمع العربي</small>
    </div>
    """, unsafe_allow_html=True)

# ==================== HOME PAGE ====================
def home_page():
    st.markdown("""
    <div class="glass-container fade-in" style="text-align: center; padding: 50px;">
        <h1 style="font-size: 3.5em; margin-bottom: 20px;">🏥 مرحباً بك في سند</h1>
        <p style="font-size: 1.4em; opacity: 0.9; max-width: 600px; margin: 0 auto;">
            مساعدك الطبي الذكي المدعوم بالذكاء الاصطناعي
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-container fade-in">
            <h2>💜 فرح - الدعم النفسي</h2>
            <p>تحدث مع شخصيات محبوبة تفهم مشاعرك وتدعمك نفسياً</p>
            <ul style="text-align: right; padding-right: 20px;">
                <li>باتمان - القوي الحامي</li>
                <li>باربي - المتفائلة اللطيفة</li>
                <li>كونغ فو باندا - الحكيم المرح</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-container fade-in">
            <h2>😊 مرآة المشاعر</h2>
            <p>اكتشف مشاعرك من خلال الكاميرا بتقنية الذكاء الاصطناعي</p>
            <p>تحليل فوري لتعبيرات الوجه</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-container fade-in">
            <h2>👨‍⚕️ الطبيب الذكي</h2>
            <p>استشر طبيبنا الذكي باللغة العربية</p>
            <p>إجابات طبية موثوقة على مدار الساعة</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-container fade-in">
            <h2>💊 تعارض الأدوية</h2>
            <p>تحقق من التفاعلات الدوائية بين أدويتك</p>
            <p>حماية صحتك من التداخلات الخطرة</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== FARAH PAGE ====================
def farah_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>💜 فرح - صديقك للدعم النفسي</h1>
        <p>اختر شخصيتك المفضلة وتحدث معها</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Persona definitions
    personas = {
        'batman': {
            'name': 'باتمان',
            'emoji': '🦇',
            'image': 'attached_assets/generated_images/3d_batman_character_hero.png',
            'description': 'القوي الحامي - سأكون درعك في الظلام',
            'style': 'قوي، حامي، حكيم، يستخدم استعارات عن القوة والظلام والنور',
            'color': '#1a1a2e',
            'voice': 'male'
        },
        'barbie': {
            'name': 'باربي',
            'emoji': '👸',
            'image': 'attached_assets/generated_images/3d_barbie_character_friendly.png',
            'description': 'المتفائلة اللطيفة - كل يوم هو فرصة جديدة',
            'style': 'متفائلة، لطيفة، مشجعة، تستخدم كلمات إيجابية ومحبة',
            'color': '#ff69b4',
            'voice': 'female'
        },
        'panda': {
            'name': 'كونغ فو باندا',
            'emoji': '🐼',
            'image': 'attached_assets/generated_images/3d_kung_fu_panda_wise.png',
            'description': 'الحكيم المرح - السر ليس سراً، بل هو أنت',
            'style': 'حكيم، مرح، يستخدم حكم صينية، يمزج بين الفكاهة والحكمة',
            'color': '#ffd700',
            'voice': 'male'
        }
    }
    
    # Persona selection
    if st.session_state.farah_persona is None:
        cols = st.columns(3)
        for idx, (key, persona) in enumerate(personas.items()):
            with cols[idx]:
                st.markdown(f"""
                <div class="persona-card" style="background: {persona['color']}40;">
                    <h3>{persona['name']}</h3>
                    <p style="font-size: 0.9em;">{persona['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                # Display character image
                if os.path.exists(persona['image']):
                    st.image(persona['image'], use_container_width=True)
                else:
                    st.markdown(f"<div style='font-size: 4em; text-align: center;'>{persona['emoji']}</div>", unsafe_allow_html=True)
                if st.button(f"اختر {persona['name']}", key=f"select_{key}", use_container_width=True):
                    st.session_state.farah_persona = key
                    st.session_state.farah_messages = []
                    st.rerun()
    else:
        persona = personas[st.session_state.farah_persona]
        
        # Back button
        if st.button("← العودة لاختيار الشخصية"):
            st.session_state.farah_persona = None
            st.session_state.farah_messages = []
            st.rerun()
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if os.path.exists(persona['image']):
                st.image(persona['image'], width=150)
        with col2:
            st.markdown(f"""
            <div class="glass-container" style="text-align: center;">
                <h2>محادثة مع {persona['name']}</h2>
                <p>{persona['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.farah_messages:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        {persona['emoji']} {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                    # Audio playback
                    if 'audio' in msg and msg['audio']:
                        st.audio(msg['audio'], format='audio/mp3')
        
        # Input
        user_input = st.text_input("شاركني ما تشعر به...", key="farah_input", placeholder="اكتب هنا...")
        
        if st.button("إرسال 💬", use_container_width=True) and user_input:
            st.session_state.farah_messages.append({'role': 'user', 'content': user_input})
            
            # Generate response
            prompt = f"""أنت {persona['name']}، شخصية {persona['style']}.
            المستخدم يقول: {user_input}
            
            قدم رداً داعماً ومشجعاً بأسلوب الشخصية. الرد يجب أن يكون:
            - باللغة العربية فقط
            - قصير ومؤثر (جملتين إلى ثلاث جمل)
            - يعكس شخصية {persona['name']}
            - داعم نفسياً ومحفز
            """
            
            with st.spinner(f"{persona['name']} يفكر..."):
                response = query_huggingface(prompt)
            
            # Generate audio with persona-specific voice
            audio_bytes = text_to_speech(response, voice_type=persona['voice'])
            
            st.session_state.farah_messages.append({
                'role': 'assistant',
                'content': response,
                'audio': audio_bytes
            })
            st.rerun()

# ==================== SMART DOCTOR PAGE ====================
def doctor_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>👨‍⚕️ الطبيب الذكي</h1>
        <p>استشر طبيبنا الذكي بأي سؤال طبي</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick question buttons
    st.markdown("""
    <div class="glass-container">
        <h4>أسئلة سريعة:</h4>
    </div>
    """, unsafe_allow_html=True)
    
    quick_questions = [
        "ما هي أعراض نقص فيتامين د؟",
        "كيف أتعامل مع الصداع المتكرر؟",
        "ما هي فوائد شرب الماء؟",
        "كيف أحسن جودة نومي؟"
    ]
    
    cols = st.columns(2)
    for idx, q in enumerate(quick_questions):
        with cols[idx % 2]:
            if st.button(q, key=f"quick_{idx}", use_container_width=True):
                st.session_state.doctor_messages.append({'role': 'user', 'content': q})
                # Generate AI response for quick question
                prompt = f"""أنت طبيب عربي ذكي ومتعاطف. أجب على السؤال التالي:
                
                السؤال: {q}
                
                قواعد الإجابة:
                - أجب باللغة العربية فقط
                - كن واضحاً ومختصراً
                - قدم معلومات طبية موثوقة
                - ذكّر المستخدم بأهمية استشارة طبيب حقيقي للحالات الخطيرة
                - لا تشخص أمراضاً محددة
                """
                response = query_huggingface(prompt)
                st.session_state.doctor_messages.append({'role': 'assistant', 'content': response})
                st.rerun()
    
    # Chat history
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    
    for msg in st.session_state.doctor_messages:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                🧑 {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                👨‍⚕️ {msg['content']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Input
    user_input = st.text_area("اكتب سؤالك الطبي هنا...", key="doctor_input", height=100)
    
    if st.button("اسأل الطبيب 🩺", use_container_width=True) and user_input:
        st.session_state.doctor_messages.append({'role': 'user', 'content': user_input})
        
        prompt = f"""أنت طبيب عربي ذكي ومتعاطف. أجب على السؤال التالي:
        
        السؤال: {user_input}
        
        قواعد الإجابة:
        - أجب باللغة العربية فقط
        - كن واضحاً ومختصراً
        - قدم معلومات طبية موثوقة
        - ذكّر المستخدم بأهمية استشارة طبيب حقيقي للحالات الخطيرة
        - لا تشخص أمراضاً محددة
        """
        
        with st.spinner("الطبيب يفكر..."):
            response = query_huggingface(prompt)
        
        st.session_state.doctor_messages.append({'role': 'assistant', 'content': response})
        st.rerun()
    
    if st.button("مسح المحادثة 🗑️"):
        st.session_state.doctor_messages = []
        st.rerun()

# ==================== EMOTION MIRROR PAGE ====================
def emotion_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>😊 مرآة المشاعر</h1>
        <p>اكتشف مشاعرك من خلال تحليل تعبيرات وجهك</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-container">
        <h3>🎥 كيفية الاستخدام:</h3>
        <ol style="padding-right: 30px;">
            <li>اضغط على زر "بدء الكاميرا" أدناه</li>
            <li>اسمح للمتصفح بالوصول إلى الكاميرا</li>
            <li>انظر إلى الكاميرا وسيتم تحليل مشاعرك</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # WebRTC for camera
    try:
        from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
        import av
        import cv2
        import numpy as np
        
        RTC_CONFIGURATION = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        class EmotionProcessor(VideoProcessorBase):
            def __init__(self):
                self.emotions = {
                    'سعيد': (0, 255, 0),      # Green
                    'حزين': (255, 0, 0),       # Blue (BGR format)
                    'غاضب': (0, 0, 255),       # Red
                    'متفاجئ': (255, 255, 0),   # Yellow
                    'خائف': (128, 0, 128),     # Purple
                    'محايد': (200, 200, 200)   # Gray
                }
                self.emotion_list = ['سعيد', 'حزين', 'غاضب', 'متفاجئ', 'خائف', 'محايد']
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                self.frame_count = 0
                self.last_emotion = 'محايد'
            
            def analyze_face_emotion(self, face_img):
                try:
                    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
                    mean_brightness = np.mean(gray)
                    std_brightness = np.std(gray)
                    
                    height, width = gray.shape[:2]
                    upper_half = gray[:height//2, :]
                    lower_half = gray[height//2:, :]
                    upper_mean = np.mean(upper_half)
                    lower_mean = np.mean(lower_half)
                    
                    left_half = gray[:, :width//2]
                    right_half = gray[:, width//2:]
                    symmetry = abs(np.mean(left_half) - np.mean(right_half))
                    
                    if std_brightness > 50 and lower_mean > upper_mean:
                        return 'سعيد'
                    elif std_brightness < 30 and mean_brightness < 100:
                        return 'حزين'
                    elif symmetry > 15 and std_brightness > 40:
                        return 'غاضب'
                    elif upper_mean > lower_mean + 10:
                        return 'متفاجئ'
                    elif std_brightness < 25:
                        return 'خائف'
                    else:
                        return 'محايد'
                except:
                    return 'محايد'
            
            def recv(self, frame):
                img = frame.to_ndarray(format="bgr24")
                self.frame_count += 1
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    face_roi = img[y:y+h, x:x+w]
                    
                    if self.frame_count % 10 == 0:
                        self.last_emotion = self.analyze_face_emotion(face_roi)
                    
                    emotion = self.last_emotion
                    color = self.emotions[emotion]
                    
                    cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
                    
                    label_bg_y = max(0, y - 40)
                    cv2.rectangle(img, (x, label_bg_y), (x + w, y), color, -1)
                    
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, emotion, (x + 10, y - 10), font, 1, (255, 255, 255), 2)
                
                return av.VideoFrame.from_ndarray(img, format="bgr24")
        
        webrtc_streamer(
            key="emotion-detection",
            video_processor_factory=EmotionProcessor,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": True, "audio": False},
            translations={
                "start": "بدء الكاميرا 📹",
                "stop": "إيقاف الكاميرا ⏹️",
                "select_device": "اختر الكاميرا",
                "media_api_not_available": "واجهة الوسائط غير متوفرة",
                "device_ask_permission": "يرجى السماح بالوصول للكاميرا",
                "device_not_available": "الكاميرا غير متوفرة",
                "device_access_denied": "تم رفض الوصول للكاميرا",
            }
        )
        
    except Exception as e:
        st.warning("⚠️ الكاميرا غير متوفرة في هذا المتصفح. يرجى استخدام متصفح يدعم WebRTC.")
    
    # Emotion descriptions
    st.markdown("""
    <div class="glass-container">
        <h3>🎨 دليل الألوان:</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center;">
            <span style="background: #00ff00; padding: 8px 15px; border-radius: 10px; color: black;">😊 سعيد</span>
            <span style="background: #ff0000; padding: 8px 15px; border-radius: 10px;">😠 غاضب</span>
            <span style="background: #0000ff; padding: 8px 15px; border-radius: 10px;">😢 حزين</span>
            <span style="background: #ffff00; padding: 8px 15px; border-radius: 10px; color: black;">😮 متفاجئ</span>
            <span style="background: #800080; padding: 8px 15px; border-radius: 10px;">😨 خائف</span>
            <span style="background: #c8c8c8; padding: 8px 15px; border-radius: 10px; color: black;">😐 محايد</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== DRUG INTERACTION PAGE ====================
def drugs_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>💊 فحص تعارض الأدوية</h1>
        <p>تحقق من التفاعلات الدوائية وابحث في قاعدة بيانات الأدوية العالمية</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-container">
        <h3>⚠️ تنبيه مهم:</h3>
        <p>هذه الأداة للإرشاد فقط ولا تغني عن استشارة الطبيب أو الصيدلي. المعلومات مستقاة من قاعدة بيانات OpenFDA الأمريكية.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 فحص التعارض", "📖 البحث عن دواء"])
    
    with tab1:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("فحص التفاعلات الدوائية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            drug1 = st.text_input("💊 الدواء الأول (بالإنجليزية):", placeholder="مثال: Aspirin", key="drug1_input")
        
        with col2:
            drug2 = st.text_input("💊 الدواء الثاني (بالإنجليزية):", placeholder="مثال: Ibuprofen", key="drug2_input")
        
        if st.button("فحص التعارض 🔍", use_container_width=True, key="check_interaction"):
            if drug1 and drug2:
                with st.spinner("جاري البحث في قاعدة البيانات..."):
                    drug1_info = query_openfda_drug(drug1)
                    drug2_info = query_openfda_drug(drug2)
                
                st.markdown("### 📋 معلومات الأدوية من OpenFDA")
                
                info_cols = st.columns(2)
                with info_cols[0]:
                    if drug1_info.get('found'):
                        st.markdown(f"""
                        <div style="background: rgba(102, 126, 234, 0.3); border-radius: 15px; padding: 15px;">
                            <h4>💊 {drug1_info['brand_name']}</h4>
                            <p><strong>الاسم العلمي:</strong> {drug1_info['generic_name']}</p>
                            <p><strong>الشركة:</strong> {drug1_info['manufacturer']}</p>
                            <p><strong>طريقة الاستخدام:</strong> {drug1_info['route']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"لم يتم العثور على {drug1} في قاعدة البيانات")
                
                with info_cols[1]:
                    if drug2_info.get('found'):
                        st.markdown(f"""
                        <div style="background: rgba(102, 126, 234, 0.3); border-radius: 15px; padding: 15px;">
                            <h4>💊 {drug2_info['brand_name']}</h4>
                            <p><strong>الاسم العلمي:</strong> {drug2_info['generic_name']}</p>
                            <p><strong>الشركة:</strong> {drug2_info['manufacturer']}</p>
                            <p><strong>طريقة الاستخدام:</strong> {drug2_info['route']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"لم يتم العثور على {drug2} في قاعدة البيانات")
                
                if drug1_info.get('drug_interactions') or drug2_info.get('drug_interactions'):
                    st.markdown("### ⚠️ تحذيرات التفاعلات الدوائية")
                    if drug1_info.get('drug_interactions'):
                        with st.expander(f"تفاعلات {drug1}", expanded=True):
                            interaction_text = drug1_info['drug_interactions'][:1000] + "..." if len(drug1_info['drug_interactions']) > 1000 else drug1_info['drug_interactions']
                            st.markdown(f"<p style='direction: ltr; text-align: left;'>{interaction_text}</p>", unsafe_allow_html=True)
                    
                    if drug2_info.get('drug_interactions'):
                        with st.expander(f"تفاعلات {drug2}", expanded=True):
                            interaction_text = drug2_info['drug_interactions'][:1000] + "..." if len(drug2_info['drug_interactions']) > 1000 else drug2_info['drug_interactions']
                            st.markdown(f"<p style='direction: ltr; text-align: left;'>{interaction_text}</p>", unsafe_allow_html=True)
                
                st.markdown("### 🤖 تحليل ذكي للتفاعل")
                prompt = f"""أنت صيدلي خبير. حلل التفاعل الدوائي بين:
                الدواء الأول: {drug1} ({drug1_info.get('generic_name', drug1) if drug1_info.get('found') else drug1})
                الدواء الثاني: {drug2} ({drug2_info.get('generic_name', drug2) if drug2_info.get('found') else drug2})
                
                قدم إجابة مختصرة تشمل:
                1. هل يوجد تعارض؟ (نعم/لا)
                2. شرح مختصر للتفاعل إن وجد
                3. نصيحة للمستخدم
                
                أجب باللغة العربية فقط.
                """
                
                with st.spinner("جاري تحليل التفاعل الدوائي..."):
                    result = query_huggingface(prompt)
                
                is_dangerous = any(word in result.lower() for word in ['خطر', 'تجنب', 'لا ينصح', 'تحذير', 'خطير'])
                
                if is_dangerous:
                    st.markdown(f"""
                    <div class="result-card-danger">
                        <h2>⚠️ تحذير - يوجد تعارض محتمل!</h2>
                        <p>{result}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card-safe">
                        <h2>✅ لا يوجد تعارض خطير</h2>
                        <p>{result}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ يرجى إدخال اسم الدوائين")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("📖 البحث في قاعدة بيانات الأدوية")
        
        search_query = st.text_input("ابحث عن دواء (بالإنجليزية):", placeholder="مثال: Tylenol, Aspirin...", key="drug_search")
        
        if st.button("🔍 بحث", use_container_width=True, key="search_drugs"):
            if search_query:
                with st.spinner("جاري البحث..."):
                    results = search_openfda_drugs(search_query)
                
                if results:
                    st.success(f"تم العثور على {len(results)} نتيجة")
                    for drug in results:
                        if st.button(f"💊 {drug['brand_name']} ({drug['generic_name']})", key=f"select_{drug['brand_name']}", use_container_width=True):
                            st.session_state.selected_drug = drug['brand_name'] or drug['generic_name']
                            st.rerun()
                else:
                    st.info("لم يتم العثور على نتائج. حاول استخدام اسم آخر.")
        
        if 'selected_drug' in st.session_state and st.session_state.selected_drug:
            st.markdown("---")
            st.subheader(f"📋 معلومات تفصيلية: {st.session_state.selected_drug}")
            
            with st.spinner("جاري تحميل المعلومات..."):
                drug_info = query_openfda_drug(st.session_state.selected_drug)
            
            if drug_info.get('found'):
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.15); border-radius: 15px; padding: 20px; margin: 10px 0;">
                    <h3>💊 {drug_info['brand_name']}</h3>
                    <p><strong>الاسم العلمي:</strong> {drug_info['generic_name']}</p>
                    <p><strong>المادة الفعالة:</strong> {drug_info['substance']}</p>
                    <p><strong>الشركة المصنعة:</strong> {drug_info['manufacturer']}</p>
                    <p><strong>طريقة الاستخدام:</strong> {drug_info['route']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if drug_info.get('indications'):
                    with st.expander("📌 دواعي الاستعمال"):
                        ind_text = drug_info['indications'][:1500] + "..." if len(drug_info['indications']) > 1500 else drug_info['indications']
                        st.markdown(f"<p style='direction: ltr; text-align: left;'>{ind_text}</p>", unsafe_allow_html=True)
                
                if drug_info.get('dosage'):
                    with st.expander("💉 الجرعة وطريقة الاستخدام"):
                        dosage_text = drug_info['dosage'][:1500] + "..." if len(drug_info['dosage']) > 1500 else drug_info['dosage']
                        st.markdown(f"<p style='direction: ltr; text-align: left;'>{dosage_text}</p>", unsafe_allow_html=True)
                
                if drug_info.get('warnings'):
                    with st.expander("⚠️ التحذيرات"):
                        warn_text = drug_info['warnings'][:1500] + "..." if len(drug_info['warnings']) > 1500 else drug_info['warnings']
                        st.markdown(f"<p style='direction: ltr; text-align: left;'>{warn_text}</p>", unsafe_allow_html=True)
                
                if drug_info.get('contraindications'):
                    with st.expander("🚫 موانع الاستعمال"):
                        contra_text = drug_info['contraindications'][:1500] + "..." if len(drug_info['contraindications']) > 1500 else drug_info['contraindications']
                        st.markdown(f"<p style='direction: ltr; text-align: left;'>{contra_text}</p>", unsafe_allow_html=True)
                
                if drug_info.get('drug_interactions'):
                    with st.expander("💊 التفاعلات الدوائية"):
                        inter_text = drug_info['drug_interactions'][:1500] + "..." if len(drug_info['drug_interactions']) > 1500 else drug_info['drug_interactions']
                        st.markdown(f"<p style='direction: ltr; text-align: left;'>{inter_text}</p>", unsafe_allow_html=True)
                
                if st.button("❌ إغلاق", key="close_drug_info"):
                    del st.session_state.selected_drug
                    st.rerun()
            else:
                st.error("لم يتم العثور على معلومات تفصيلية")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-container">
        <h3>📋 أمثلة على تعارضات شائعة:</h3>
        <ul style="padding-right: 30px;">
            <li><strong>Aspirin + Warfarin:</strong> يزيد خطر النزيف</li>
            <li><strong>Antibiotics + Birth Control:</strong> قد تقلل فعالية حبوب منع الحمل</li>
            <li><strong>Antacids + Antibiotics:</strong> تقلل امتصاص الدواء</li>
            <li><strong>ACE Inhibitors + Potassium:</strong> ارتفاع خطير في البوتاسيوم</li>
        </ul>
        <p style="opacity: 0.7; font-size: 0.9em;">البيانات من OpenFDA - إدارة الغذاء والدواء الأمريكية</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== PROFILE PAGE ====================
def profile_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>👤 الملف الشخصي</h1>
        <p>إدارة معلوماتك الشخصية والتاريخ الطبي</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    user = st.session_state.current_user
    
    db.refresh(user)
    
    tab1, tab2, tab3 = st.tabs(["📋 المعلومات الأساسية", "🏥 التاريخ الطبي", "🆘 الطوارئ"])
    
    with tab1:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("المعلومات الشخصية")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم الكامل", value=user.name or "", key="profile_name")
            email = st.text_input("البريد الإلكتروني", value=user.email or "", key="profile_email")
            phone = st.text_input("رقم الهاتف", value=user.phone or "", key="profile_phone")
        
        with col2:
            dob = st.date_input("تاريخ الميلاد", value=user.date_of_birth if user.date_of_birth else date(1990, 1, 1), key="profile_dob")
            gender = st.selectbox("الجنس", options=["", "ذكر", "أنثى"], index=["", "ذكر", "أنثى"].index(user.gender) if user.gender in ["", "ذكر", "أنثى"] else 0, key="profile_gender")
            blood_type = st.selectbox("فصيلة الدم", options=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                                     index=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(user.blood_type) if user.blood_type in ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] else 0,
                                     key="profile_blood")
        
        st.subheader("المعلومات الصحية")
        allergies = st.text_area("الحساسية (افصل بين كل نوع بفاصلة)", value=user.allergies or "", key="profile_allergies", placeholder="مثال: البنسلين، المكسرات، الغبار")
        chronic_conditions = st.text_area("الأمراض المزمنة (افصل بين كل مرض بفاصلة)", value=user.chronic_conditions or "", key="profile_chronic", placeholder="مثال: السكري، الضغط، الربو")
        
        if st.button("💾 حفظ المعلومات", use_container_width=True, key="save_profile"):
            user.name = name
            user.email = email
            user.phone = phone
            user.date_of_birth = dob
            user.gender = gender if gender else None
            user.blood_type = blood_type if blood_type else None
            user.allergies = allergies
            user.chronic_conditions = chronic_conditions
            db.commit()
            st.success("✅ تم حفظ المعلومات بنجاح!")
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("إضافة سجل طبي جديد")
        
        col1, col2 = st.columns(2)
        with col1:
            condition = st.text_input("الحالة/المرض", key="new_condition", placeholder="مثال: التهاب اللوزتين")
            diagnosis_date = st.date_input("تاريخ التشخيص", key="new_diagnosis_date")
        with col2:
            treatment = st.text_input("العلاج", key="new_treatment", placeholder="مثال: مضاد حيوي لمدة أسبوع")
            status = st.selectbox("الحالة", options=["active", "resolved", "ongoing"], format_func=lambda x: {"active": "نشط", "resolved": "تم الشفاء", "ongoing": "مستمر"}[x], key="new_status")
        
        notes = st.text_area("ملاحظات إضافية", key="new_notes")
        
        if st.button("➕ إضافة السجل", use_container_width=True, key="add_history"):
            if condition:
                new_history = MedicalHistory(
                    user_id=user.id,
                    condition=condition,
                    diagnosis_date=diagnosis_date,
                    treatment=treatment,
                    notes=notes,
                    status=status
                )
                db.add(new_history)
                db.commit()
                st.success("✅ تم إضافة السجل الطبي بنجاح!")
                st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال اسم الحالة/المرض")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("السجلات الطبية السابقة")
        
        history_records = db.query(MedicalHistory).filter(MedicalHistory.user_id == user.id).order_by(MedicalHistory.diagnosis_date.desc()).all()
        
        if history_records:
            for record in history_records:
                status_color = {"active": "#ff6b6b", "resolved": "#51cf66", "ongoing": "#ffd43b"}
                status_text = {"active": "نشط", "resolved": "تم الشفاء", "ongoing": "مستمر"}
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin: 10px 0; border-right: 4px solid {status_color.get(record.status, '#999')};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0;">{record.condition}</h4>
                        <span style="background: {status_color.get(record.status, '#999')}; padding: 5px 15px; border-radius: 20px; font-size: 0.8em;">
                            {status_text.get(record.status, record.status)}
                        </span>
                    </div>
                    <p style="opacity: 0.8; margin: 10px 0 5px 0;">📅 {record.diagnosis_date.strftime('%Y-%m-%d') if record.diagnosis_date else 'غير محدد'}</p>
                    <p style="margin: 5px 0;">💊 العلاج: {record.treatment or 'غير محدد'}</p>
                    {f'<p style="opacity: 0.7; font-size: 0.9em;">📝 {record.notes}</p>' if record.notes else ''}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ حذف", key=f"delete_history_{record.id}"):
                    db.delete(record)
                    db.commit()
                    st.rerun()
        else:
            st.info("📭 لا توجد سجلات طبية مسجلة بعد")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("معلومات الطوارئ")
        st.markdown("<p style='opacity: 0.8;'>أضف معلومات الاتصال في حالات الطوارئ</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            emergency_contact = st.text_input("اسم جهة الاتصال", value=user.emergency_contact or "", key="emergency_name")
        with col2:
            emergency_phone = st.text_input("رقم هاتف الطوارئ", value=user.emergency_phone or "", key="emergency_phone")
        
        if st.button("💾 حفظ معلومات الطوارئ", use_container_width=True, key="save_emergency"):
            user.emergency_contact = emergency_contact
            user.emergency_phone = emergency_phone
            db.commit()
            st.success("✅ تم حفظ معلومات الطوارئ بنجاح!")
        
        if user.emergency_contact and user.emergency_phone:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); border-radius: 15px; padding: 20px; margin-top: 20px;">
                <h3 style="margin: 0 0 10px 0;">🆘 جهة الاتصال في الطوارئ</h3>
                <p style="font-size: 1.2em; margin: 5px 0;">👤 {user.emergency_contact}</p>
                <p style="font-size: 1.2em; margin: 5px 0;">📞 {user.emergency_phone}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== APPOINTMENTS PAGE ====================
def appointments_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>📅 إدارة المواعيد</h1>
        <p>جدولة ومتابعة مواعيدك مع الأطباء</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    user = st.session_state.current_user
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 المواعيد القادمة", "➕ حجز موعد جديد", "👨‍⚕️ إدارة الأطباء", "📆 عرض التقويم"])
    
    with tab1:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("مواعيدك القادمة")
        
        db.expire_all()
        today = date.today()
        upcoming_appointments = db.query(Appointment).filter(
            Appointment.user_id == user.id,
            Appointment.appointment_date >= today,
            Appointment.status != "cancelled"
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        if upcoming_appointments:
            for apt in upcoming_appointments:
                doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
                doctor_name = doctor.name if doctor else "طبيب غير محدد"
                doctor_specialty = doctor.specialty if doctor else ""
                
                status_colors = {
                    "scheduled": "#667eea",
                    "completed": "#38ef7d",
                    "cancelled": "#ef473a"
                }
                status_labels = {
                    "scheduled": "مجدول",
                    "completed": "مكتمل",
                    "cancelled": "ملغي"
                }
                
                apt_color = status_colors.get(apt.status, "#667eea")
                apt_label = status_labels.get(apt.status, apt.status)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {apt_color}40 0%, {apt_color}20 100%); 
                            border-radius: 15px; padding: 20px; margin: 10px 0; border-right: 4px solid {apt_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0;">👨‍⚕️ {doctor_name}</h3>
                            <p style="opacity: 0.8; margin: 5px 0;">{doctor_specialty}</p>
                        </div>
                        <div style="text-align: left;">
                            <span style="background: {apt_color}; padding: 5px 15px; border-radius: 20px; font-size: 0.9em;">
                                {apt_label}
                            </span>
                        </div>
                    </div>
                    <hr style="border-color: rgba(255,255,255,0.2); margin: 10px 0;">
                    <p>📅 التاريخ: {apt.appointment_date.strftime('%Y-%m-%d')}</p>
                    <p>⏰ الوقت: {apt.appointment_time.strftime('%H:%M')}</p>
                    {f"<p>📝 السبب: {apt.reason}</p>" if apt.reason else ""}
                    {f"<p>📋 ملاحظات: {apt.notes}</p>" if apt.notes else ""}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if apt.status == "scheduled":
                        if st.button("✅ إكمال", key=f"complete_{apt.id}", use_container_width=True):
                            apt.status = "completed"
                            db.commit()
                            st.rerun()
                with col2:
                    if apt.status == "scheduled":
                        if st.button("❌ إلغاء", key=f"cancel_{apt.id}", use_container_width=True):
                            apt.status = "cancelled"
                            db.commit()
                            st.rerun()
                with col3:
                    if st.button("🗑️ حذف", key=f"delete_apt_{apt.id}", use_container_width=True):
                        db.delete(apt)
                        db.commit()
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("📭 لا توجد مواعيد قادمة. احجز موعدك الأول!")
        
        st.markdown("### 📜 المواعيد السابقة")
        past_appointments = db.query(Appointment).filter(
            Appointment.user_id == user.id,
            Appointment.appointment_date < today
        ).order_by(Appointment.appointment_date.desc()).limit(5).all()
        
        if past_appointments:
            for apt in past_appointments:
                doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
                doctor_name = doctor.name if doctor else "طبيب غير محدد"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 5px 0; opacity: 0.7;">
                    <p style="margin: 0;">👨‍⚕️ {doctor_name} - 📅 {apt.appointment_date.strftime('%Y-%m-%d')} - 
                    <span style="color: {'#38ef7d' if apt.status == 'completed' else '#ef473a'};">
                        {'مكتمل' if apt.status == 'completed' else 'ملغي'}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='opacity: 0.6;'>لا توجد مواعيد سابقة</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("➕ حجز موعد جديد")
        
        doctors = db.query(Doctor).all()
        
        if not doctors:
            st.warning("⚠️ لا يوجد أطباء مسجلين. يرجى إضافة طبيب أولاً من تبويب 'إدارة الأطباء'")
        else:
            doctor_options = {f"{d.name} - {d.specialty}": d.id for d in doctors}
            selected_doctor = st.selectbox("اختر الطبيب", options=list(doctor_options.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                apt_date = st.date_input("تاريخ الموعد", min_value=date.today(), key="new_apt_date")
            with col2:
                apt_time = st.time_input("وقت الموعد", key="new_apt_time")
            
            apt_reason = st.text_area("سبب الزيارة", placeholder="مثال: فحص دوري، استشارة، متابعة...", key="new_apt_reason")
            apt_notes = st.text_area("ملاحظات إضافية", placeholder="أي معلومات إضافية تود مشاركتها مع الطبيب...", key="new_apt_notes")
            
            if st.button("📅 حجز الموعد", use_container_width=True, key="book_apt"):
                if selected_doctor:
                    new_apt = Appointment(
                        user_id=user.id,
                        doctor_id=doctor_options[selected_doctor],
                        appointment_date=apt_date,
                        appointment_time=apt_time,
                        reason=apt_reason,
                        notes=apt_notes,
                        status="scheduled"
                    )
                    db.add(new_apt)
                    db.commit()
                    st.success("✅ تم حجز الموعد بنجاح!")
                    st.balloons()
                else:
                    st.error("❌ يرجى اختيار طبيب")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("👨‍⚕️ إدارة الأطباء")
        
        with st.expander("➕ إضافة طبيب جديد", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                doc_name = st.text_input("اسم الطبيب", key="doc_name")
                doc_specialty = st.selectbox("التخصص", [
                    "طب عام", "طب الأطفال", "طب النساء والتوليد", "طب القلب",
                    "طب العيون", "طب الأنف والأذن والحنجرة", "طب الأسنان",
                    "الطب النفسي", "طب الجلدية", "طب العظام", "طب الباطنية",
                    "جراحة عامة", "أخرى"
                ], key="doc_specialty")
                doc_phone = st.text_input("رقم الهاتف", key="doc_phone")
            with col2:
                doc_email = st.text_input("البريد الإلكتروني", key="doc_email")
                doc_location = st.text_input("العنوان / الموقع", key="doc_location")
                doc_hours = st.text_input("ساعات العمل", placeholder="مثال: 9 صباحاً - 5 مساءً", key="doc_hours")
            
            if st.button("✅ إضافة الطبيب", use_container_width=True, key="add_doctor"):
                if doc_name:
                    new_doctor = Doctor(
                        name=doc_name,
                        specialty=doc_specialty,
                        phone=doc_phone,
                        email=doc_email,
                        location=doc_location,
                        working_hours=doc_hours
                    )
                    db.add(new_doctor)
                    db.commit()
                    st.success(f"✅ تم إضافة د. {doc_name} بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ يرجى إدخال اسم الطبيب")
        
        st.markdown("### 📋 الأطباء المسجلين")
        doctors = db.query(Doctor).all()
        
        if doctors:
            for doc in doctors:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.15); border-radius: 15px; padding: 20px; margin: 10px 0;">
                    <h3 style="margin: 0 0 10px 0;">👨‍⚕️ د. {doc.name}</h3>
                    <p style="opacity: 0.9; margin: 5px 0;">🏥 التخصص: {doc.specialty or 'غير محدد'}</p>
                    <p style="opacity: 0.8; margin: 5px 0;">📞 {doc.phone or 'غير متوفر'}</p>
                    <p style="opacity: 0.8; margin: 5px 0;">📧 {doc.email or 'غير متوفر'}</p>
                    <p style="opacity: 0.8; margin: 5px 0;">📍 {doc.location or 'غير محدد'}</p>
                    <p style="opacity: 0.8; margin: 5px 0;">⏰ {doc.working_hours or 'غير محددة'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ حذف د. {doc.name}", key=f"delete_doc_{doc.id}", use_container_width=True):
                    db.query(Appointment).filter(Appointment.doctor_id == doc.id).delete()
                    db.delete(doc)
                    db.commit()
                    st.rerun()
        else:
            st.info("📭 لا يوجد أطباء مسجلين. أضف طبيبك الأول!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("📆 عرض التقويم")
        
        col1, col2 = st.columns(2)
        with col1:
            view_month = st.selectbox("الشهر", list(range(1, 13)), 
                                       index=date.today().month - 1,
                                       format_func=lambda x: ["يناير", "فبراير", "مارس", "أبريل", 
                                                               "مايو", "يونيو", "يوليو", "أغسطس",
                                                               "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"][x-1])
        with col2:
            view_year = st.selectbox("السنة", list(range(2024, 2030)), 
                                      index=date.today().year - 2024)
        
        import calendar
        cal = calendar.monthcalendar(view_year, view_month)
        
        month_appointments = db.query(Appointment).filter(
            Appointment.user_id == user.id,
            Appointment.appointment_date >= date(view_year, view_month, 1),
            Appointment.appointment_date <= date(view_year, view_month, 
                                                  calendar.monthrange(view_year, view_month)[1])
        ).all()
        
        apt_days = {apt.appointment_date.day: apt for apt in month_appointments}
        
        days_header = ["السبت", "الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"]
        header_cols = st.columns(7)
        for i, day in enumerate(days_header):
            with header_cols[i]:
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 10px;'>{day}</div>", 
                           unsafe_allow_html=True)
        
        for week in cal:
            week_cols = st.columns(7)
            for i, day in enumerate(week):
                with week_cols[i]:
                    if day == 0:
                        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
                    else:
                        has_apt = day in apt_days
                        is_today = (day == date.today().day and view_month == date.today().month 
                                   and view_year == date.today().year)
                        
                        bg_color = "#667eea" if has_apt else ("rgba(255,255,255,0.3)" if is_today else "rgba(255,255,255,0.1)")
                        border = "2px solid #FFD700" if is_today else "none"
                        
                        st.markdown(f"""
                        <div style="background: {bg_color}; border-radius: 10px; padding: 10px; 
                                    text-align: center; height: 60px; display: flex; align-items: center; 
                                    justify-content: center; border: {border};">
                            <span style="font-size: 1.2em;">{day}</span>
                            {"<span style='margin-right: 5px;'>📅</span>" if has_apt else ""}
                        </div>
                        """, unsafe_allow_html=True)
        
        if month_appointments:
            st.markdown("### 📋 مواعيد هذا الشهر")
            for apt in sorted(month_appointments, key=lambda x: (x.appointment_date, x.appointment_time)):
                doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
                doctor_name = doctor.name if doctor else "طبيب غير محدد"
                st.markdown(f"""
                <div style="background: rgba(102, 126, 234, 0.3); border-radius: 10px; padding: 10px; margin: 5px 0;">
                    <p style="margin: 0;">📅 {apt.appointment_date.day} - ⏰ {apt.appointment_time.strftime('%H:%M')} - 
                    👨‍⚕️ {doctor_name}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== MEDICATIONS PAGE ====================
def medications_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>💊 الأدوية والتذكيرات</h1>
        <p>إدارة أدويتك وتتبع مواعيد تناولها</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    user = st.session_state.current_user
    
    tab1, tab2, tab3 = st.tabs(["💊 أدويتي", "➕ إضافة دواء", "📋 سجل التناول"])
    
    with tab1:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("أدويتك الحالية")
        
        db.expire_all()
        active_medications = db.query(Medication).filter(
            Medication.user_id == user.id,
            Medication.is_active == True
        ).all()
        
        if active_medications:
            for med in active_medications:
                days_remaining = None
                if med.end_date:
                    days_remaining = (med.end_date - date.today()).days
                    if days_remaining < 0:
                        med.is_active = False
                        db.commit()
                        continue
                
                progress_color = "#38ef7d"
                if days_remaining is not None:
                    if days_remaining <= 3:
                        progress_color = "#ef473a"
                    elif days_remaining <= 7:
                        progress_color = "#ffd700"
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.15); border-radius: 15px; padding: 20px; margin: 10px 0;
                            border-right: 4px solid {progress_color};">
                    <h3 style="margin: 0 0 10px 0;">💊 {med.name}</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                        <p style="margin: 5px 0;">📊 الجرعة: {med.dosage or 'غير محددة'}</p>
                        <p style="margin: 5px 0;">🔄 التكرار: {med.frequency or 'غير محدد'}</p>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                        <p style="margin: 5px 0;">📅 تاريخ البدء: {med.start_date.strftime('%Y-%m-%d') if med.start_date else 'غير محدد'}</p>
                        <p style="margin: 5px 0;">📅 تاريخ الانتهاء: {med.end_date.strftime('%Y-%m-%d') if med.end_date else 'مستمر'}</p>
                    </div>
                    {f"<p style='margin: 5px 0;'>⏰ أوقات التذكير: {med.reminder_times}</p>" if med.reminder_times else ""}
                    {f"<p style='margin: 5px 0; opacity: 0.8;'>📝 تعليمات: {med.instructions}</p>" if med.instructions else ""}
                    {f"<p style='margin: 5px 0; color: {progress_color};'>⏳ متبقي: {days_remaining} أيام</p>" if days_remaining is not None else ""}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ تم التناول", key=f"taken_{med.id}", use_container_width=True):
                        today = date.today()
                        now_time = datetime.now().time()
                        reminder = MedicationReminder(
                            medication_id=med.id,
                            reminder_time=now_time,
                            reminder_date=today,
                            is_taken=True,
                            taken_at=datetime.now()
                        )
                        db.add(reminder)
                        db.commit()
                        st.success("✅ تم تسجيل تناول الدواء!")
                        st.rerun()
                with col2:
                    if st.button("⏸️ إيقاف", key=f"stop_{med.id}", use_container_width=True):
                        med.is_active = False
                        db.commit()
                        st.rerun()
                with col3:
                    if st.button("🗑️ حذف", key=f"delete_med_{med.id}", use_container_width=True):
                        db.query(MedicationReminder).filter(MedicationReminder.medication_id == med.id).delete()
                        db.delete(med)
                        db.commit()
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("📭 لا توجد أدوية نشطة. أضف دواءك الأول!")
        
        inactive_meds = db.query(Medication).filter(
            Medication.user_id == user.id,
            Medication.is_active == False
        ).all()
        
        if inactive_meds:
            with st.expander("📜 الأدوية السابقة/المتوقفة"):
                for med in inactive_meds:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 5px 0; opacity: 0.7;">
                        <p style="margin: 0;">💊 {med.name} - {med.dosage or ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("▶️ إعادة تفعيل", key=f"reactivate_{med.id}", use_container_width=True):
                            med.is_active = True
                            db.commit()
                            st.rerun()
                    with col2:
                        if st.button("🗑️ حذف نهائي", key=f"perm_delete_{med.id}", use_container_width=True):
                            db.query(MedicationReminder).filter(MedicationReminder.medication_id == med.id).delete()
                            db.delete(med)
                            db.commit()
                            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("➕ إضافة دواء جديد")
        
        med_name = st.text_input("اسم الدواء *", placeholder="مثال: باراسيتامول 500 ملغ", key="new_med_name")
        
        col1, col2 = st.columns(2)
        with col1:
            med_dosage = st.text_input("الجرعة", placeholder="مثال: حبة واحدة", key="new_med_dosage")
            med_frequency = st.selectbox("التكرار", [
                "مرة يومياً",
                "مرتين يومياً",
                "ثلاث مرات يومياً",
                "أربع مرات يومياً",
                "كل 6 ساعات",
                "كل 8 ساعات",
                "كل 12 ساعة",
                "عند الحاجة",
                "أسبوعياً",
                "أخرى"
            ], key="new_med_freq")
        with col2:
            med_start = st.date_input("تاريخ البدء", value=date.today(), key="new_med_start")
            med_end = st.date_input("تاريخ الانتهاء (اختياري)", value=None, key="new_med_end")
        
        st.markdown("### ⏰ أوقات التذكير")
        reminder_cols = st.columns(4)
        reminder_times_list = []
        
        with reminder_cols[0]:
            if st.checkbox("صباحاً (8:00)", key="rem_morning"):
                reminder_times_list.append("08:00")
        with reminder_cols[1]:
            if st.checkbox("ظهراً (12:00)", key="rem_noon"):
                reminder_times_list.append("12:00")
        with reminder_cols[2]:
            if st.checkbox("مساءً (18:00)", key="rem_evening"):
                reminder_times_list.append("18:00")
        with reminder_cols[3]:
            if st.checkbox("ليلاً (22:00)", key="rem_night"):
                reminder_times_list.append("22:00")
        
        custom_time = st.time_input("أو اختر وقتاً مخصصاً", value=None, key="custom_rem_time")
        if custom_time:
            reminder_times_list.append(custom_time.strftime("%H:%M"))
        
        med_instructions = st.text_area("تعليمات الاستخدام", placeholder="مثال: تناول بعد الأكل، مع كوب ماء كامل...", key="new_med_instructions")
        
        if st.button("💊 إضافة الدواء", use_container_width=True, key="add_medication"):
            if med_name:
                new_med = Medication(
                    user_id=user.id,
                    name=med_name,
                    dosage=med_dosage,
                    frequency=med_frequency,
                    start_date=med_start,
                    end_date=med_end,
                    reminder_times=", ".join(reminder_times_list) if reminder_times_list else None,
                    instructions=med_instructions,
                    is_active=True
                )
                db.add(new_med)
                db.commit()
                st.success(f"✅ تم إضافة {med_name} بنجاح!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ يرجى إدخال اسم الدواء")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("📋 سجل تناول الأدوية")
        
        db.expire_all()
        user_meds = db.query(Medication).filter(Medication.user_id == user.id).all()
        med_ids = [m.id for m in user_meds]
        
        if med_ids:
            recent_reminders = db.query(MedicationReminder).filter(
                MedicationReminder.medication_id.in_(med_ids)
            ).order_by(MedicationReminder.reminder_date.desc(), MedicationReminder.reminder_time.desc()).limit(20).all()
            
            if recent_reminders:
                st.markdown("### 📅 آخر 20 سجل")
                
                today_count = 0
                week_count = 0
                today = date.today()
                week_ago = today - timedelta(days=7)
                
                for rem in recent_reminders:
                    med = db.query(Medication).filter(Medication.id == rem.medication_id).first()
                    med_name = med.name if med else "دواء محذوف"
                    
                    if rem.reminder_date == today:
                        today_count += 1
                    if rem.reminder_date >= week_ago:
                        week_count += 1
                    
                    status_color = "#38ef7d" if rem.is_taken else "#ffd700"
                    status_text = "تم التناول" if rem.is_taken else "لم يتم"
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 5px 0;
                                border-right: 3px solid {status_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="margin: 0; font-weight: bold;">💊 {med_name}</p>
                                <p style="margin: 5px 0; opacity: 0.8;">📅 {rem.reminder_date.strftime('%Y-%m-%d')} - ⏰ {rem.reminder_time.strftime('%H:%M')}</p>
                            </div>
                            <span style="background: {status_color}; padding: 5px 15px; border-radius: 15px;">
                                {status_text}
                            </span>
                        </div>
                        {f"<p style='margin: 5px 0; opacity: 0.7;'>✅ تم التناول في: {rem.taken_at.strftime('%H:%M')}</p>" if rem.taken_at else ""}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 📊 إحصائيات سريعة")
                stat_cols = st.columns(2)
                with stat_cols[0]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                border-radius: 15px; padding: 20px; text-align: center;">
                        <h2 style="margin: 0;">{today_count}</h2>
                        <p style="margin: 5px 0;">جرعات اليوم</p>
                    </div>
                    """, unsafe_allow_html=True)
                with stat_cols[1]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                                border-radius: 15px; padding: 20px; text-align: center;">
                        <h2 style="margin: 0;">{week_count}</h2>
                        <p style="margin: 5px 0;">جرعات هذا الأسبوع</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 لا توجد سجلات تناول بعد")
        else:
            st.info("📭 أضف أدوية أولاً لتتبع سجل التناول")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== HEALTH METRICS PAGE ====================
def health_metrics_page():
    st.markdown("""
    <div class="glass-container" style="text-align: center;">
        <h1>📊 مؤشرات الصحة</h1>
        <p>تتبع مؤشراتك الصحية ومراقبة تقدمك</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    user = st.session_state.current_user
    
    metric_types = {
        "blood_pressure": {"name": "ضغط الدم", "icon": "❤️", "unit": "mmHg", "has_secondary": True},
        "heart_rate": {"name": "نبضات القلب", "icon": "💓", "unit": "نبضة/دقيقة", "has_secondary": False},
        "glucose": {"name": "السكر في الدم", "icon": "🩸", "unit": "mg/dL", "has_secondary": False},
        "weight": {"name": "الوزن", "icon": "⚖️", "unit": "كغ", "has_secondary": False},
        "temperature": {"name": "درجة الحرارة", "icon": "🌡️", "unit": "°C", "has_secondary": False},
        "oxygen": {"name": "نسبة الأكسجين", "icon": "💨", "unit": "%", "has_secondary": False}
    }
    
    tab1, tab2, tab3 = st.tabs(["📊 الملخص", "➕ تسجيل قراءة", "📈 التاريخ"])
    
    with tab1:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("ملخص المؤشرات الصحية")
        
        db.expire_all()
        
        cols = st.columns(3)
        col_idx = 0
        
        for metric_key, metric_info in metric_types.items():
            latest = db.query(HealthMetric).filter(
                HealthMetric.user_id == user.id,
                HealthMetric.metric_type == metric_key
            ).order_by(HealthMetric.recorded_at.desc()).first()
            
            with cols[col_idx % 3]:
                if latest:
                    if metric_key == "blood_pressure" and latest.secondary_value:
                        value_display = f"{int(latest.value)}/{int(latest.secondary_value)}"
                    else:
                        value_display = f"{latest.value:.1f}" if latest.value % 1 != 0 else f"{int(latest.value)}"
                    
                    status_color = "#38ef7d"
                    if metric_key == "blood_pressure":
                        if latest.value > 140 or latest.secondary_value > 90:
                            status_color = "#ef473a"
                        elif latest.value > 130 or latest.secondary_value > 85:
                            status_color = "#ffd700"
                    elif metric_key == "glucose":
                        if latest.value > 180 or latest.value < 70:
                            status_color = "#ef473a"
                        elif latest.value > 140:
                            status_color = "#ffd700"
                    elif metric_key == "heart_rate":
                        if latest.value > 100 or latest.value < 50:
                            status_color = "#ffd700"
                    elif metric_key == "oxygen":
                        if latest.value < 95:
                            status_color = "#ef473a"
                        elif latest.value < 97:
                            status_color = "#ffd700"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {status_color}40 0%, {status_color}20 100%); 
                                border-radius: 15px; padding: 20px; margin: 10px 0; text-align: center;
                                border-top: 4px solid {status_color};">
                        <span style="font-size: 2em;">{metric_info['icon']}</span>
                        <h3 style="margin: 10px 0 5px 0;">{metric_info['name']}</h3>
                        <h2 style="margin: 5px 0; color: {status_color};">{value_display}</h2>
                        <p style="opacity: 0.8; margin: 0;">{metric_info['unit']}</p>
                        <p style="opacity: 0.6; font-size: 0.8em; margin-top: 10px;">
                            آخر قراءة: {latest.recorded_at.strftime('%Y-%m-%d %H:%M')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; 
                                margin: 10px 0; text-align: center; opacity: 0.7;">
                        <span style="font-size: 2em;">{metric_info['icon']}</span>
                        <h3 style="margin: 10px 0 5px 0;">{metric_info['name']}</h3>
                        <p style="opacity: 0.6;">لا توجد قراءات</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            col_idx += 1
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("➕ تسجيل قراءة جديدة")
        
        selected_metric = st.selectbox(
            "نوع المؤشر",
            options=list(metric_types.keys()),
            format_func=lambda x: f"{metric_types[x]['icon']} {metric_types[x]['name']}"
        )
        
        metric_config = metric_types[selected_metric]
        
        if metric_config["has_secondary"]:
            col1, col2 = st.columns(2)
            with col1:
                primary_value = st.number_input(
                    f"القراءة العليا (الانقباضي) - {metric_config['unit']}",
                    min_value=0.0, max_value=300.0, value=120.0, step=1.0
                )
            with col2:
                secondary_value = st.number_input(
                    f"القراءة السفلى (الانبساطي) - {metric_config['unit']}",
                    min_value=0.0, max_value=200.0, value=80.0, step=1.0
                )
        else:
            primary_value = st.number_input(
                f"القراءة - {metric_config['unit']}",
                min_value=0.0, max_value=500.0, 
                value=100.0 if selected_metric == "glucose" else (70.0 if selected_metric == "heart_rate" else 37.0 if selected_metric == "temperature" else 98.0 if selected_metric == "oxygen" else 70.0),
                step=0.1 if selected_metric in ["weight", "temperature"] else 1.0
            )
            secondary_value = None
        
        record_time = st.datetime_input("وقت القراءة", value=datetime.now(), key="metric_time")
        
        notes = st.text_area("ملاحظات (اختياري)", placeholder="مثال: بعد الأكل، بعد التمرين...", key="metric_notes")
        
        if st.button("💾 حفظ القراءة", use_container_width=True, key="save_metric"):
            new_metric = HealthMetric(
                user_id=user.id,
                metric_type=selected_metric,
                value=primary_value,
                unit=metric_config["unit"],
                secondary_value=secondary_value,
                recorded_at=record_time,
                notes=notes
            )
            db.add(new_metric)
            db.commit()
            st.success(f"✅ تم حفظ قراءة {metric_config['name']} بنجاح!")
            st.balloons()
            st.rerun()
        
        st.markdown("### 📋 دليل القراءات الطبيعية")
        guide_cols = st.columns(2)
        with guide_cols[0]:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px;">
                <p><strong>❤️ ضغط الدم:</strong> 120/80 أو أقل</p>
                <p><strong>💓 نبضات القلب:</strong> 60-100 نبضة/دقيقة</p>
                <p><strong>🩸 السكر (صائم):</strong> 70-100 mg/dL</p>
            </div>
            """, unsafe_allow_html=True)
        with guide_cols[1]:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px;">
                <p><strong>🌡️ الحرارة:</strong> 36.1-37.2 °C</p>
                <p><strong>💨 الأكسجين:</strong> 95-100%</p>
                <p><strong>⚖️ الوزن:</strong> حسب مؤشر كتلة الجسم</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader("📈 تاريخ القراءات")
        
        filter_metric = st.selectbox(
            "تصفية حسب نوع المؤشر",
            options=["all"] + list(metric_types.keys()),
            format_func=lambda x: "جميع المؤشرات" if x == "all" else f"{metric_types[x]['icon']} {metric_types[x]['name']}",
            key="filter_metric"
        )
        
        db.expire_all()
        
        if filter_metric == "all":
            history = db.query(HealthMetric).filter(
                HealthMetric.user_id == user.id
            ).order_by(HealthMetric.recorded_at.desc()).limit(30).all()
        else:
            history = db.query(HealthMetric).filter(
                HealthMetric.user_id == user.id,
                HealthMetric.metric_type == filter_metric
            ).order_by(HealthMetric.recorded_at.desc()).limit(30).all()
        
        if history:
            for metric in history:
                m_info = metric_types.get(metric.metric_type, {"name": metric.metric_type, "icon": "📊", "unit": ""})
                
                if metric.metric_type == "blood_pressure" and metric.secondary_value:
                    value_display = f"{int(metric.value)}/{int(metric.secondary_value)}"
                else:
                    value_display = f"{metric.value:.1f}" if metric.value % 1 != 0 else f"{int(metric.value)}"
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 5px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.5em; margin-left: 10px;">{m_info['icon']}</span>
                            <strong>{m_info['name']}</strong>
                        </div>
                        <div style="text-align: left;">
                            <span style="font-size: 1.3em; font-weight: bold;">{value_display}</span>
                            <span style="opacity: 0.7;"> {m_info['unit']}</span>
                        </div>
                    </div>
                    <p style="opacity: 0.6; margin: 5px 0 0 0; font-size: 0.9em;">
                        📅 {metric.recorded_at.strftime('%Y-%m-%d %H:%M')}
                        {f" - 📝 {metric.notes}" if metric.notes else ""}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ حذف", key=f"delete_metric_{metric.id}"):
                    db.delete(metric)
                    db.commit()
                    st.rerun()
        else:
            st.info("📭 لا توجد قراءات سابقة")
        
        if filter_metric != "all" and history:
            st.markdown("### 📊 رسم بياني")
            
            chart_data = []
            for m in reversed(history):
                chart_data.append({
                    "التاريخ": m.recorded_at.strftime('%m-%d'),
                    "القيمة": m.value
                })
            
            if chart_data:
                import pandas as pd
                df = pd.DataFrame(chart_data)
                st.line_chart(df.set_index("التاريخ"))
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== PAGE ROUTER ====================
if st.session_state.current_page == 'home':
    home_page()
elif st.session_state.current_page == 'farah':
    farah_page()
elif st.session_state.current_page == 'doctor':
    doctor_page()
elif st.session_state.current_page == 'emotion':
    emotion_page()
elif st.session_state.current_page == 'drugs':
    drugs_page()
elif st.session_state.current_page == 'profile':
    profile_page()
elif st.session_state.current_page == 'appointments':
    appointments_page()
elif st.session_state.current_page == 'medications':
    medications_page()
elif st.session_state.current_page == 'health_metrics':
    health_metrics_page()
