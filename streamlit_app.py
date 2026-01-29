
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 頁面配置
st.set_page_config(
    page_title="CelestialLens - AI 命理戰略家",
    page_icon="🔮",
    layout="wide"
)

# 2. 安全取得 API Key (從 Streamlit Secrets)
# 在 Streamlit Cloud 部署後，請在 Settings -> Secrets 中設定 GEMINI_API_KEY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("請先在 .streamlit/secrets.toml 或 Streamlit 後台設定 GEMINI_API_KEY")
    st.stop()

# 3. 定義指令集 (與網頁版同步)
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

# 4. 側邊欄 UI
with st.sidebar:
    st.title("🔮 CelestialLens Pro")
    st.markdown("---")
    
    st.subheader("1. 選取解讀模式")
    category = st.selectbox("分類", list(PROMPT_CATEGORIES.keys()))
    selected_item = st.selectbox("子項目", [i["label"] for i in PROMPT_CATEGORIES[category]])
    
    # 找出選中的模板
    template = next(i["template"] for i in PROMPT_CATEGORIES[category] if i["label"] == selected_item)
    
    st.subheader("2. 填寫變數資料")
    current_job = st.text_input("目前從事職業 (OO)", placeholder="例如：產品經理")
    col1, col2 = st.columns(2)
    strength_a = col1.text_input("強項 A", placeholder="例如：直覺")
    strength_b = col2.text_input("強項 B", placeholder="例如：邏輯")
    
    # 替換變數
    final_prompt = template.replace("{current_job}", current_job).replace("{strength_a}", strength_a).replace("{strength_b}", strength_b)
    
    st.subheader("3. 最終指令預覽")
    editable_prompt = st.text_area("您可以手動微調指令內容：", value=final_prompt, height=200)

# 5. 主介面 UI
st.title("CelestialLens AI 命盤深度解讀")
st.info("💡 提示：您可以同時上傳多張截圖，AI 將自動進行整合推理。")

uploaded_files = st.file_uploader("上傳命盤截圖 (八字/紫微/占星)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if uploaded_files:
    cols = st.columns(len(uploaded_files))
    for idx, file in enumerate(uploaded_files):
        with cols[idx]:
            st.image(file, use_column_width=True)

if st.button("🌟 啟動 Pro 思考模式解讀", type="primary"):
    if not uploaded_files:
        st.warning("請先上傳命盤截圖！")
    else:
        with st.spinner("Gemini Pro 正在進行深度鏈式思考..."):
            try:
                # 準備模型
                # 注意：Python SDK 的思考模式設定方式
                model = genai.GenerativeModel(
                    model_name='gemini-3-pro-preview',
                    system_instruction="你是一位精通八字、紫微斗數、三元九運與現代職業戰略的頂尖玄學專家。你擅長將古老的東方智慧轉化為具備未來感、跨領域且符合現代趨勢的實戰建議。解讀時請使用 Markdown 格式，表格必須清晰。"
                )

                # 準備圖片資料
                content_parts = []
                for uploaded_file in uploaded_files:
                    img = Image.open(uploaded_file)
                    content_parts.append(img)
                
                content_parts.append(editable_prompt)

                # 呼叫 API (配置思考預算)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
            ),
            stream=True
        )
                # 串流輸出結果
                output_area = st.empty()
                full_text = ""
                for chunk in response:
                    full_text += chunk.text
                    output_area.markdown(full_text)
                
                st.success("解讀完成！")
                
            except Exception as e:
                st.error(f"發生錯誤：{str(e)}")

st.markdown("---")
st.caption("Powered by Gemini 3 Pro • CelestialLens Python Edition")
