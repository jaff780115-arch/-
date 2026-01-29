
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
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        # 兼容本地開發環境
        api_key = st.sidebar.text_input("請輸入 API Key (僅限本地測試)", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("請在 Streamlit Secrets 或側邊欄設定 GEMINI_API_KEY")
        st.stop()
except Exception as e:
    st.error("API 設定失敗，請檢查 Secrets 配置。")
    st.stop()

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
    
    category = st.selectbox("1. 選擇分類", list(PROMPT_CATEGORIES.keys()))
    sub_items = [i["label"] for i in PROMPT_CATEGORIES[category]]
    selected_label = st.selectbox("2. 選擇指令", sub_items)
    
    template = next(i["template"] for i in PROMPT_CATEGORIES[category] if i["label"] == selected_label)
    
    st.markdown("---")
    st.subheader("3. 填寫資料")
    job = st.text_input("目前職業", placeholder="例：自由接案")
    s_a = st.text_input("強項 A", placeholder="例：直覺")
    s_b = st.text_input("強項 B", placeholder="例：美感")
    
    final_prompt = template.replace("{current_job}", job).replace("{strength_a}", s_a).replace("{strength_b}", s_b)
    
    st.subheader("4. 指令預覽")
    prompt_text = st.text_area("可直接在此修改指令：", value=final_prompt, height=200)

# 5. 主內容區
st.title("CelestialLens AI 命盤深度解讀")
st.info("支援多圖上傳，AI 將進行跨圖整合分析。")

files = st.file_uploader("上傳命盤截圖", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if files:
    cols = st.columns(min(len(files), 4))
    for i, f in enumerate(files):
        with cols[i % 4]:
            st.image(f, use_container_width=True)

if st.button("🌟 啟動 Pro 思考模式解讀", type="primary"):
    if not files:
        st.warning("請先上傳至少一張截圖")
    else:
        with st.spinner("Gemini Pro 思考中..."):
            try:
                # 初始化模型
                model = genai.GenerativeModel(
                    model_name='gemini-3-pro-preview',
                    system_instruction="你是一位精通八字、紫微、三元九運的玄學專家，擅長將古老智慧轉化為現代職涯建議。請使用 Markdown 格式回答。"
                )

                # 準備內容 (圖片 + 文字)
                contents = []
                for f in files:
                    img = Image.open(f)
                    contents.append(img)
                contents.append(prompt_text)

                # 發送請求 (包含 Thinking Config)
                response = model.generate_content(
                    contents,
                    generation_config={
                        "temperature": 0.8,
                        "thinking_config": {"thinking_budget": 32768}
                    },
                    stream=True
                )

                # 顯示結果
                res_area = st.empty()
                full_res = ""
                for chunk in response:
                    if chunk.text:
                        full_res += chunk.text
                        res_area.markdown(full_res)
                
                st.success("解讀完成")
            except Exception as e:
                st.error(f"分析發生錯誤: {str(e)}")

st.markdown("---")
st.caption("CelestialLens Python Pro Edition")
