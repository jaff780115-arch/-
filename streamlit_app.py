
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 頁面配置
st.set_page_config(
    page_title="CelestialLens - AI 命理戰略家",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS：隱藏開發者工具，同時確保 UI 比例正確
st.markdown("""
    <style>
    /* 隱藏頂部工具列 (包含 View Source, GitHub 圖示等) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    
    /* 隱藏底部標籤 */
    footer {
        visibility: hidden;
        height: 0%;
    }

    /* 頁面背景與按鈕樣式 */
    .main { background-color: #020617; color: #f8fafc; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5rem; 
        font-weight: bold; 
        background: linear-gradient(45deg, #f59e0b, #ea580c); 
        color: white; 
        border: none; 
        font-size: 1.1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        transition: 0.2s; 
        box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.4); 
    }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; background-color: #0f172a; color: #cbd5e1; border-color: #1e293b; }
    .stSelectbox label, .stTextInput label { color: #94a3b8 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 1px; }
    
    /* 調整主要內容區域，補償 header 隱藏後的間距 */
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全取得 API Key
def init_gemini():
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    # 手機版若 Secrets 讀不到，檢查 Session
    if not api_key and "manual_api_key" in st.session_state:
        api_key = st.session_state["manual_api_key"]
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            return True
        except:
            return False
    return False

# 3. 資料定義
PROMPT_CATEGORIES = {
    "一. 基本解讀": [
        {"label": "八字顧問綜合分析", "template": "請你當我的八字顧問，詳細分析這張截圖的命主性格，日主五行、身強或身弱。\n\n並請依序解讀：\na. 根據格局，提議多元且符合現代趨勢的工作事業方式。\nb. 分析我的財務能量與五行喜忌用神。\nc. 分析命盤所有不同階段的十年大運，與十神的特性(請附整理表格)。\n備註： 我是 [男] 性。"}
    ],
    "二. 探索天賦地圖": [
        {"label": "我的天賦是什麼？", "template": "根據我的命盤，你認為我有什麼天賦呢？"},
        {"label": "地球體驗天賦", "template": "根據我的八字，你認為我有什麼天賦，能讓我在地球上好好體驗呢？"},
        {"label": "事業現狀避坑", "template": "我目前正在做 {current_job}，根據我的八字能量，我該注意什麼才能事半功倍？"},
        {"label": "AI 與我的天賦發揮", "template": "AI對我發揮天賦的意義是什麼？我可以如何運用Gemini以及其他AI工具來發揮能力？請為我分析，謝謝。"},
        {"label": "生命設計顧問 (機器比喻)", "template": "你現在是我的生命設計顧問：如果我是一台精密機器，我的原廠設定『預設強項』與『容易耗能的地方』分別是什麼？"}
    ],
    "三. 進階運勢能量": [
        {"label": "未來趨勢工作方式", "template": "關於八字的能量，我適合什麼什麼類型的工作方式？（符合未來趨勢、多元彈性的）"},
        {"label": "三元九運：離火運策略", "template": "在三元九運的「離火運」下，如何發揮我的事業天賦與商業模式？"},
        {"label": "當前大運天賦發揮", "template": "在我目前的大運狀態下，如何發揮我的天賦？"},
        {"label": "職業戰略家模式", "template": "請你進入『職業戰略家』模式。根據剛才解析的八字十神格局，我注意到我有 [強項 A：{strength_a}] 與 [強項 B：{strength_b}] 這兩種能量。\n\n請幫我依序進行以下探索：\na. 化學反應分析：這兩種能量結合時，會產生什麼樣的『獨特工作風格』？\nb. 跨領域提案：請提出 3 個非傳統、具備未來感的『職業組合』，這些組合必須能同時發揮我的技術才華與內在價值感。\nc. 避坑指南：在整合這些能力時，我最容易遇到的『自我內耗』點是什麼？"}
    ]
}

STYLE_OPTIONS = {
    "預設風格": "",
    "白話解讀": "\n\n請幫我將以上分析，用非常白話、好理解的方式解讀。",
    "身心靈解讀": "\n\n請幫我將以上分析，用身心靈與內在探索的方式解讀。",
    "能量角度解讀": "\n\n請幫我將以上分析，從能量場與頻率的角度進行解讀。"
}

# 4. 初始化
is_ready = init_gemini()

# 5. 側邊欄 UI
with st.sidebar:
    st.title("🔮 CelestialLens")
    st.caption("AI 命理戰略系統 v3.1.1 (復原版)")
    st.markdown("---")
    
    st.subheader("🛠️ 指令配置")
    
    cat_name = st.selectbox("1. 功能分類", list(PROMPT_CATEGORIES.keys()))
    items_in_cat = PROMPT_CATEGORIES[cat_name]
    selected_label = st.selectbox("2. 具體指令", [i["label"] for i in items_in_cat])
    style_name = st.selectbox("3. 語氣風格", list(STYLE_OPTIONS.keys()))
    
    # 防止手機切換時的空值錯誤
    try:
        template = next(i["template"] for i in items_in_cat if i["label"] == selected_label)
    except StopIteration:
        template = items_in_cat[0]["template"]

    style_suffix = STYLE_OPTIONS[style_name]
    
    st.markdown("---")
    st.subheader("📝 參數輸入")
    job = st.text_input("目前職業", placeholder="例如：軟體工程師")
    sa = st.text_input("強項 A", placeholder="例如：邏輯分析")
    sb = st.text_input("強項 B", placeholder="例如：創意寫作")
    
    final_prompt = template.replace("{current_job}", job if job else "[自由業]") \
                           .replace("{strength_a}", sa if sa else "[未指定]") \
                           .replace("{strength_b}", sb if sb else "[未指定]")
    
    final_prompt += style_suffix
    
    st.markdown("---")
    prompt_to_send = st.text_area("終端指令預覽：", value=final_prompt, height=150)

# 6. 主畫面 UI
st.title("CelestialLens AI 深度解讀")

# API Key 安全檢查：若未就緒，顯示輸入框
if not is_ready:
    st.warning("🔑 請輸入您的 Gemini API Key 以開始使用。")
    m_key = st.text_input("API Key", type="password")
    if m_key:
        st.session_state["manual_api_key"] = m_key
        st.rerun()

st.info("💡 目前使用 **Gemini 3 Flash** 引擎。")

uploaded_files = st.file_uploader("📸 請上傳命盤截圖 (可多選)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if uploaded_files:
    # 恢復為寬螢幕 5 欄顯示，避免格式跑掉
    cols = st.columns(min(len(uploaded_files), 5))
    for i, file in enumerate(uploaded_files):
        with cols[i % 5]:
            st.image(file, use_container_width=True)

st.markdown("---")

if st.button("🌟 啟動 AI 智慧命理分析", type="primary"):
    if not is_ready:
        st.error("請先設定 API Key")
    elif not uploaded_files:
        st.warning("請先上傳命盤截圖")
    else:
        with st.spinner("正在接收星辰智慧..."):
            try:
                # 確保重新配置 API Key
                current_key = st.secrets.get("GEMINI_API_KEY") or st.session_state.get("manual_api_key")
                genai.configure(api_key=current_key)
                
                model = genai.GenerativeModel(
                    model_name="gemini-3-flash-preview",
                    system_instruction="你是一位精通八字、紫微斗數與現代職涯戰略的命理專家。請使用 Markdown 格式提供專業解讀。應包含表格整理與重點條列。"
                )

                inputs = []
                for f in uploaded_files:
                    img = Image.open(f)
                    inputs.append(img)
                inputs.append(prompt_to_send)

                response = model.generate_content(
                    inputs,
                    generation_config=genai.types.GenerationConfig(temperature=0.7),
                    stream=True
                )

                st.subheader("📝 深度分析報告")
                res_area = st.empty()
                full_text = ""
                
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        res_area.markdown(full_text)
                
                st.success("解讀完成")
                st.balloons()
                
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    st.error("🚨 配額超出限制：請等待 60 秒後再試。")
                else:
                    st.error(f"分析失敗：{err_msg}")

st.markdown("---")
st.caption("© 2025 CelestialLens • Powered by Gemini 3 Flash")
