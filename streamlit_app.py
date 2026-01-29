
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

# 自定義 CSS
st.markdown("""
    <style>
    .main { background-color: #020617; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3rem; font-weight: bold; background: linear-gradient(45deg, #f59e0b, #ea580c); color: white; border: none; }
    .stButton>button:hover { transform: scale(1.02); transition: 0.2s; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; background-color: #0f172a; color: #cbd5e1; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全取得 API Key
def init_gemini():
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if not api_key:
        api_key = st.sidebar.text_input("🔑 請輸入 Gemini API Key", type="password", help="請前往 Google AI Studio 取得 Key")
    
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# 指令集定義
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
    ],
    "四. 語氣風格轉換": [
        {"label": "白話解讀", "template": "請幫我將以上分析，用白話的方式解讀。"},
        {"label": "身心靈解讀", "template": "請幫我將以上分析，用身心靈的方式解讀。"},
        {"label": "能量角度解讀", "template": "請幫我將以上分析，用能量的方式解讀。"}
    ]
}

# 側邊欄 UI
with st.sidebar:
    st.title("🔮 CelestialLens Pro")
    st.markdown("---")
    
    is_ready = init_gemini()
    
    st.subheader("⚙️ 模型設定")
    # 提供模型選擇，解決配額問題
    model_choice = st.radio(
        "選擇 AI 模型",
        ["gemini-3-flash-preview", "gemini-3-pro-preview"],
        index=0,
        help="如果 Pro 出現 Quota Exceeded (429) 錯誤，請切換至 Flash。Flash 速度更快且免費配額更多。"
    )
    
    st.markdown("---")
    st.subheader("1. 選擇策略指令")
    cat = st.selectbox("功能分類", list(PROMPT_CATEGORIES.keys()))
    selected_label = st.selectbox("具體指令", [i["label"] for i in PROMPT_CATEGORIES[cat]])
    template = next(i["template"] for i in PROMPT_CATEGORIES[cat] if i["label"] == selected_label)
    
    st.markdown("---")
    st.subheader("2. 參數設定")
    job = st.text_input("目前職業")
    sa = st.text_input("強項 A")
    sb = st.text_input("強項 B")
    
    final_prompt = template.replace("{current_job}", job).replace("{strength_a}", sa).replace("{strength_b}", sb)
    prompt_to_send = st.text_area("終端指令預覽：", value=final_prompt, height=200)

# 主畫面 UI
st.title("CelestialLens AI 命盤深度解讀")
st.markdown("---")

uploaded_files = st.file_uploader("📸 請上傳命盤截圖 (可多選)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 4))
    for i, file in enumerate(uploaded_files):
        with cols[i % 4]:
            st.image(file, use_container_width=True)

st.markdown("---")

if st.button("🌟 啟動 Pro 思考模式解讀", type="primary"):
    if not is_ready:
        st.error("請先設定 API Key")
    elif not uploaded_files:
        st.warning("請先上傳命盤圖片")
    else:
        with st.spinner(f"正在使用 {model_choice} 進行深度分析..."):
            try:
                model = genai.GenerativeModel(
                    model_name=model_choice,
                    system_instruction="你是一位精通八字與紫微的專家。請用 Markdown 表格與清單詳細解讀。若是思考模式模型，請展示深度推理過程。"
                )

                inputs = []
                for f in uploaded_files:
                    inputs.append(Image.open(f))
                inputs.append(prompt_to_send)

                # 嘗試帶入思考預算
                gen_config = genai.types.GenerationConfig(temperature=0.8)
                
                # 只有 Pro 模型或特定預覽版模型支援 thinking_config
                thinking_params = {"thinking_budget": 32768} if "pro" in model_choice else None

                if thinking_params:
                    response = model.generate_content(
                        inputs,
                        generation_config=gen_config,
                        thinking_config=thinking_params,
                        stream=True
                    )
                else:
                    response = model.generate_content(
                        inputs,
                        generation_config=gen_config,
                        stream=True
                    )

                st.subheader("📝 分析結果")
                res_area = st.empty()
                full_text = ""
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        res_area.markdown(full_text)
                st.success("分析完成")
                
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "quota" in err_msg.lower():
                    st.error("🚨 **配額超出限制 (Quota Exceeded)**")
                    st.info("""
                    **為什麼會這樣？**
                    1. 您使用的是免費版 API Key，Google 對 Pro 模型的限制非常嚴格。
                    2. 即使您有訂閱 Gemini Advanced，API 仍需獨立開啟 [Pay-as-you-go](https://ai.google.dev/pricing) 才能獲得高配額。
                    
                    **建議解決方法：**
                    *   在左側邊欄將模型切換為 **gemini-3-flash-preview** (配額多很多)。
                    *   等待一分鐘後再試。
                    """)
                else:
                    st.error(f"發生錯誤：{err_msg}")

st.markdown("---")
st.caption("© 2025 CelestialLens • 如果您已付費但仍看到 429，請確認是否已在 Google AI Studio 開啟 Billing。")
