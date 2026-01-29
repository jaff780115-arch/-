
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 頁面配置 (必須是第一個 Streamlit 指令)
st.set_page_config(
    page_title="CelestialLens - AI 命理戰略家",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 讓 UI 更有質感
st.markdown("""
    <style>
    .main { background-color: #020617; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3rem; font-weight: bold; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全取得 API Key
def init_gemini():
    api_key = None
    # 優先從 Streamlit Secrets 取得
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    # 如果 Secrets 沒有，則允許從側邊欄手動輸入 (用於開發測試)
    if not api_key:
        api_key = st.sidebar.text_input("🔑 請輸入 Gemini API Key", type="password", help="請前往 Google AI Studio 取得 Key")
    
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# 3. 定義指令集
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
        {"label": "職業戰略家模式", "template": "請你進入『職業戰略家』模式。根據剛才解析的八字十神格局，我注意到我有 [強項 A：{strength_a}] 與 [強項 B：{strength_b}] 這兩種能量。\n\n請幫我依序進行以下探索：\na. 化學反應分析：這兩種能量結合時，會產生什麼樣的『獨特工作風格』？\nb. 跨領域提案：請提出 3 個非傳統、具備未來感的『職業組合』，這些組合必須能同時發揮我的技術才華與內在價值感。\nc. 避坑指南：在整合 these 能力時，我最容易遇到的『自我內耗』點是什麼？"}
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
    
    st.subheader("1. 選擇策略指令")
    cat = st.selectbox("功能分類", list(PROMPT_CATEGORIES.keys()))
    items = PROMPT_CATEGORIES[cat]
    selected_label = st.selectbox("具體指令", [i["label"] for i in items])
    
    template = next(i["template"] for i in items if i["label"] == selected_label)
    
    st.markdown("---")
    st.subheader("2. 參數設定")
    job = st.text_input("目前職業", placeholder="例如：產品經理")
    sa = st.text_input("強項 A", placeholder="例如：直覺")
    sb = st.text_input("強項 B", placeholder="例如：邏輯")
    
    # 合成指令
    final_prompt = template.replace("{current_job}", job).replace("{strength_a}", sa).replace("{strength_b}", sb)
    
    st.subheader("3. 終端指令預覽")
    prompt_to_send = st.text_area("您可以手動編輯最終指令：", value=final_prompt, height=250)

# 主畫面 UI
st.title("CelestialLens AI 命盤深度解讀")
st.markdown("---")

# 檔案上傳
uploaded_files = st.file_uploader("📸 請上傳命盤截圖 (可多選)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 4))
    for i, file in enumerate(uploaded_files):
        with cols[i % 4]:
            st.image(file, use_container_width=True, caption=f"圖片 {i+1}")

st.markdown("---")

# 執行按鈕
if st.button("🌟 啟動 Pro 思考模式解讀", type="primary", disabled=not is_ready):
    if not uploaded_files:
        st.warning("請先上傳命盤圖片！")
    else:
        with st.spinner("Gemini Pro 正在進行深度鏈式思考 (Thinking Mode)..."):
            try:
                # 初始化模型
                model = genai.GenerativeModel(
                    model_name='gemini-3-pro-preview',
                    system_instruction="你是一位精通八字、紫微斗數、三元九運與現代職業戰略的頂尖玄學專家。你擅長將古老的東方智慧轉化為具備未來感、跨領域且符合現代趨勢的實戰建議。請使用 Markdown 格式輸出，表格必須美觀且清晰。"
                )

                # 準備輸入內容
                inputs = []
                for f in uploaded_files:
                    img = Image.open(f)
                    inputs.append(img)
                inputs.append(prompt_to_send)

                # 呼叫 API (修正思考模式的傳參方式)
                # 在 Python SDK 中，thinking_config 是 generate_content 的直接參數
                # 這裡增加了一個 try-except 回退機制，以應對不同版本的 SDK
                try:
                    response = model.generate_content(
                        inputs,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.8,
                            top_p=0.95
                        ),
                        thinking_config={"thinking_budget": 32768},
                        stream=True
                    )
                except TypeError:
                    # 如果當前安裝的 SDK 版本不支援 thinking_config 參數，則回退到標準模式
                    st.info("💡 偵測到環境 SDK 版本，切換至標準高效解讀模式...")
                    response = model.generate_content(
                        inputs,
                        generation_config=genai.types.GenerationConfig(temperature=0.8),
                        stream=True
                    )

                # 顯示串流結果
                st.subheader("📝 策略分析結果")
                result_container = st.empty()
                full_text = ""
                
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        result_container.markdown(full_text)
                
                st.success("解讀完成！")
                st.balloons()

            except Exception as e:
                st.error(f"分析失敗：{str(e)}")
                st.info("請檢查您的 API Key 權限或圖片格式是否正確。")

elif not is_ready:
    st.error("❌ 尚未設定 API Key，請在側邊欄輸入或檢查 Secrets 配置。")

st.markdown("---")
st.caption("© 2025 CelestialLens Python Pro Edition • Powered by Gemini 3 Pro")
