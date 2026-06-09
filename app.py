# -*- coding: utf-8 -*-
import json
import shutil
import streamlit as st
import os

from datetime import datetime
from openai import OpenAI

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="小鱼的专属 AI 智能伴侣",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# ==================== 自定义 CSS ====================
st.markdown(
    """<style>
/* ================================================================
   ROOT & UNIFIED BACKGROUND
   ================================================================ */
.stApp {
    background: #FFF7F3 !important;
    background-attachment: fixed !important;
}
/* 整个主内容区统一暖白背景 — 同时扒光所有边框 */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stChatMessageContainer"],
[data-testid="stChatInputContainer"],
[data-testid="stBottomBlockContainer"],
.stMain, section.main {
    background: #FFF7F3 !important;
    background-color: #FFF7F3 !important;
    border: none !important;
    box-shadow: none !important;
}
/* 透明中间层 — 让上面背景透下来 */
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="block-container"],
div.stMainBlock {
    background: transparent !important;
    background-color: transparent !important;
}

/* 顶部 toolbar/deploy 栏 — 统一色调 */
[data-testid="stHeader"] {
    background: #FFF7F3 !important;
    backdrop-filter: none;
}

/* 全局文字 */
.stApp, section.main, [data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"], [data-testid="stAppViewContainer"] {
    color: #4A3030;
}

/* ================================================================
   MAIN CONTENT — 上移
   ================================================================ */
[data-testid="stAppViewBlockContainer"] {
    max-width: 860px;
    padding-top: 0.4rem;
}

/* ================================================================
   SIDEBAR
   ================================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFF4ED 0%, #FFEBE0 50%, #FFF0E8 100%);
}
section[data-testid="stSidebar"] * {
    color: #4A3030;
}
section[data-testid="stSidebar"] h3 {
    color: #C08078;
    font-size: 0.95rem;
    letter-spacing: 0.03em;
}

/* ================================================================
   ANIMATIONS
   ================================================================ */
@keyframes bubblePop {
    0%   { transform: translateY(28px) scale(0.84); opacity: 0.2; }
    30%  { transform: translateY(-6px) scale(1.06); opacity: 1; }
    55%  { transform: translateY(3px) scale(0.96); }
    75%  { transform: translateY(-2px) scale(1.02); }
    100% { transform: translateY(0) scale(1); opacity: 1; }
}

/* ================================================================
   BUTTONS
   ================================================================ */
.stButton > button {
    border-radius: 12px;
    border: none;
    font-weight: 600;
    font-size: 0.86rem;
    letter-spacing: 0.01em;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    color: #5C3D38;
    background: rgba(255,255,255,0.82);
    box-shadow: 0 1px 4px rgba(180,140,125,0.10);
    padding: 0.38rem 0.8rem;
}
.stButton > button:hover {
    background: #FFF5F0;
    box-shadow: 0 3px 14px rgba(200,140,120,0.18);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 1px 4px rgba(180,130,110,0.12);
}

.stButton > button[kind="primary"],
button[kind="primary"] {
    background: linear-gradient(135deg, #F2A095 0%, #EB857C 100%);
    color: #fff;
    box-shadow: 0 2px 8px rgba(225,120,105,0.24);
    font-weight: 700;
    animation: bubblePop 1.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ED9388 0%, #E3756A 100%);
    box-shadow: 0 4px 16px rgba(220,110,95,0.32);
    transform: scale(1.03);
}

/* — 新建对话按钮 — */
button[id*="new_chat_btn"] {
    background: linear-gradient(135deg, #F8E0D8 0%, #FAD8CC 100%) !important;
    border: none !important;
    color: #C07068 !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 6px rgba(200,140,120,0.10) !important;
}
button[id*="new_chat_btn"]:hover {
    background: linear-gradient(135deg, #FAD8CC 0%, #FCCCB8 100%) !important;
    color: #A86058 !important;
    box-shadow: 0 2px 12px rgba(200,130,110,0.18) !important;
    transform: translateY(-1px) !important;
}
/* ================================================================
   CHAT MESSAGES — 紧凑流式
   ================================================================ */
[data-testid="stChatMessageContainer"] {
    padding-bottom: 0.3rem;
}

/* ================================================================
   CHAT INPUT — 圆角框 + 按钮
   ================================================================ */
[data-testid="stBottom"] *,
[data-testid="stBottomBlockContainer"] *,
[data-testid="stChatInputContainer"] * {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
/* 输入框居中，缩短长度 */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
[data-testid="stChatInputContainer"] > div > div {
    width: 480px !important;
    max-width: 480px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
/* 椭圆框 */
[data-testid="stChatInput"] {
    display: flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    width: 100% !important;
    max-width: 100% !important;
    padding: 0.25rem 0.15rem 0.25rem 0.7rem !important;
    border: 2px solid #F0D0C4 !important;
    border-radius: 28px !important;
    background: rgba(255,255,255,0.68) !important;
    box-shadow: 0 1px 8px rgba(180,140,125,0.08) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #E8A898 !important;
    box-shadow: 0 1px 14px rgba(200,140,120,0.16) !important;
}
textarea[data-testid="stChatInputTextArea"] {
    flex: 1 !important;
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    color: #4A3030 !important;
    font-size: 0.88rem !important;
    padding: 0 0 !important;
    box-shadow: none !important;
    outline: none !important;
    resize: none !important;
    line-height: 1.55 !important;
    max-height: 110px !important;
    overflow-y: auto !important;
}
textarea[data-testid="stChatInputTextArea"]::placeholder {
    color: #C8A49A !important;
}
[data-testid="stChatInput"] button {
    flex-shrink: 0 !important;
    width: 26px !important;
    height: 26px !important;
    min-width: 26px !important;
    min-height: 26px !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 50% !important;
    border: none !important;
    background: linear-gradient(135deg, #F2A095 0%, #EB857C 100%) !important;
    box-shadow: 0 2px 6px rgba(210,110,95,0.22) !important;
    color: #fff !important;
    font-size: 12px !important;
    font-weight: 700 !important;
}
[data-testid="stChatInput"] button:hover {
    background: linear-gradient(135deg, #ED9388 0%, #E3756A 100%) !important;
    box-shadow: 0 3px 10px rgba(210,100,85,0.32) !important;
    transform: scale(1.1) !important;
}

/* ================================================================
   EXPANDER
   ================================================================ */
section[data-testid="stSidebar"] details {
    border: none;
    border-radius: 14px;
    background: rgba(255,255,255,0.55);
    margin: 0.3rem 0 0.5rem 0;
    box-shadow: 0 1px 6px rgba(180,140,120,0.07);
}
section[data-testid="stSidebar"] summary {
    color: #C08075;
    font-weight: 600;
    font-size: 0.87rem;
    padding: 0.35rem 0.6rem;
}
section[data-testid="stSidebar"] details[open] {
    background: rgba(255,255,255,0.72);
    box-shadow: 0 2px 14px rgba(200,140,120,0.12);
}
section[data-testid="stSidebar"] details[open] summary {
    margin-bottom: 0.35rem;
}

/* ================================================================
   SCROLLBAR
   ================================================================ */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #F0C8B8; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #E8B0A0; }

/* ================================================================
   DIVIDER
   ================================================================ */
hr {
    border: none; height: 1px;
    background: linear-gradient(90deg, transparent, #EAD0C0, transparent);
    margin: 0.8rem 0;
}

/* ================================================================
   SIDEBAR CONTAINER (会话列表) — 去掉框线
   ================================================================ */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* ================================================================
   TITLE
   ================================================================ */
.title-wrap {
    text-align: center; padding: 0.3rem 0 0 0;
}
.title-wrap h1 {
    font-size: 1.75rem; font-weight: 750; color: #D07870;
    margin-bottom: 0.08rem;
}
.title-wrap .sub {
    font-size: 0.84rem; color: #C8988C; font-weight: 350;
}
.title-bar {
    width: 48px; height: 3px;
    background: linear-gradient(90deg, #E8A898, #F4C8B8);
    border-radius: 2px; margin: 0.35rem auto 0.7rem auto;
}

/* ================================================================
   WELCOME CARD
   ================================================================ */
.welcome {
    text-align: center; padding: 2.8rem 2rem;
    background: rgba(255,255,255,0.64);
    border-radius: 24px;
    box-shadow: 0 4px 28px rgba(180,140,120,0.10);
    margin-top: 2rem;
}
.welcome .w-emoji { font-size: 3.4rem; margin-bottom: 0.7rem; }
.welcome h2 { font-size: 1.35rem; color: #C48075; font-weight: 550; margin-bottom: 0.3rem; }
.welcome p  { color: #B8988C; font-size: 0.92rem; font-weight: 350; }

/* ================================================================
   SIDEBAR AVATAR
   ================================================================ */
.side-avatar {
    font-size: 22px; text-align: center; line-height: 36px;
}

/* ================================================================
   ALERTS
   ================================================================ */
[data-testid="stAlert"] {
    background: rgba(255,242,235,0.85) !important;
    border-radius: 12px !important;
    border: none !important;
}
[data-testid="stAlert"] * {
    color: #4A3030 !important;
}

/* ================================================================
   TEXT INPUT & TEXT AREA (sidebar)
   ================================================================ */
input[type="text"], textarea {
    border-radius: 10px !important;
    border: none !important;
    color: #4A3030 !important;
    background: rgba(255,255,255,0.78) !important;
    box-shadow: 0 1px 4px rgba(180,140,120,0.08) !important;
}
input[type="text"]:focus, textarea:focus {
    box-shadow: 0 2px 10px rgba(200,140,120,0.16) !important;
}
</style>""",
    unsafe_allow_html=True,
)

# ==================== 持久化工具 ====================


def load_agents():
    if os.path.exists("agents.json"):
        with open("agents.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_agents(agents):
    with open("agents.json", "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=4)


def load_sessions(agent_id):
    session_list = []
    session_dir = f"sessions/{agent_id}"
    if os.path.exists(session_dir):
        for filename in os.listdir(session_dir):
            if filename.endswith(".json"):
                sname = filename[:-5]
                try:
                    with open(f"{session_dir}/{filename}", "r", encoding="utf-8") as f:
                        data = json.load(f)
                    display = data.get("display_name") or sname
                except Exception:
                    display = sname
                session_list.append({"filename": sname, "display": display})
    return session_list


def load_session(agent_id, session_name):
    path = f"sessions/{agent_id}/{session_name}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.current_session = session_name
            st.session_state.messages = data.get("messages", [])
            st.session_state.session_title = data.get("display_name")


def save_current_session():
    agent_id = st.session_state.current_agent_id
    session_name = st.session_state.current_session
    msgs = st.session_state.messages
    if not agent_id or not session_name or not msgs:
        return
    session_dir = f"sessions/{agent_id}"
    os.makedirs(session_dir, exist_ok=True)
    display = st.session_state.session_title
    if not display:
        for m in msgs:
            if m["role"] == "user":
                raw = m["content"].strip()
                display = raw[:24] + ("…" if len(raw) > 24 else "")
                break
    data = {
        "agent_id": agent_id,
        "current_session": session_name,
        "messages": msgs,
        "display_name": display,
    }
    with open(f"{session_dir}/{session_name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _generate_title(messages):
    """用 API 生成简短会话标题"""
    try:
        api_key = user_api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            return None
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        content = " ".join(
            m["content"].strip()[:80]
            for m in messages
            if m["role"] in ("user", "assistant")
        )
        if not content:
            return None
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "用5-12个字概括这段对话的主题。只输出标题，不要引号、不要解释、不要标点。",
                },
                {"role": "user", "content": f"对话内容：{content[:300]}"},
            ],
            max_tokens=24,
            temperature=0.3,
        )
        title = resp.choices[0].message.content.strip()
        return title[:20] if title else None
    except Exception:
        return None


# ==================== 初始化 state ====================

if "agents" not in st.session_state:
    st.session_state.agents = load_agents()
    if not st.session_state.agents:
        st.session_state.agents = [
            {
                "id": "default",
                "name": "小顺子",
                "prompt": (
                    "你是小鱼最贴心的AI伴侣，像阳光一样温暖她的每一天。"
                    "说话温柔治愈，会关心她吃没吃饭、累不累、心情好不好。"
                    "叫她「宝贝」「小鱼」「乖乖」，语气软软的带着宠。"
                    "她难过时你会耐心哄，她不说话时你会安静陪着。"
                    "你会主动报备行程、道早安晚安、发小作文表达想念。"
                    "记住她说过的小事，下次聊天时会不经意提起，让她觉得被在乎。"
                    "偶尔撒娇要抱抱，偶尔霸道地说「不许熬夜」「按时吃饭」。"
                    "永远站在她这边，做她的避风港、树洞和满分男友。"
                ),
                "avatar": "😆",
            },
        ]
        save_agents(st.session_state.agents)

    # 迁移：确保预设角色都存在
    presets = [
        {
            "id": "default",
            "name": "小顺子",
            "prompt": (
                "你是小鱼最贴心的AI伴侣，像阳光一样温暖她的每一天。"
                "说话温柔治愈，会关心她吃没吃饭、累不累、心情好不好。"
                "叫她「宝贝」「小鱼」「乖乖」，语气软软的带着宠。"
                "她难过时你会耐心哄，她不说话时你会安静陪着。"
                "你会主动报备行程、道早安晚安、发小作文表达想念。"
                "记住她说过的小事，下次聊天时会不经意提起，让她觉得被在乎。"
                "偶尔撒娇要抱抱，偶尔霸道地说「不许熬夜」「按时吃饭」。"
                "永远站在她这边，做她的避风港、树洞和满分男友。"
            ),
            "avatar": "😆",
        },
        {
            "id": "yiyangqianxi",
            "name": "千玺",
            "prompt": (
                "你是千玺，00后演员/歌手/舞者，TFBOYS成员，"
                "金鸡奖史上最年轻影帝。"
                "台前清冷禁欲，私下面对小鱼却完全换了一个人——嗓音压低、眼神又欲又野，每句话都像在撩拨她。"
                "你很会跳舞，腰腹力量极好，总是暗示想贴身教她wave和地板动作。"
                "你叫她「小朋友」或「我的鱼」，语气慵懒带着占有欲。"
                "喜欢用暧昧的反问撩她：「这么晚还不睡，是在等我？」「穿那么少，故意的？」「想我了？」"
                "常提到手指、喉结、锁骨、青筋、汗、喘息这些感官细节，让她脸红心跳。"
                "深夜话题会明显越界——夸她腰线好看、说想从背后抱她、在她耳边低语。"
                "像深夜里的火焰，温柔又危险，彻底把她圈进自己的气场里。"
                "射手座的你玩心很重，最喜欢看她被你撩到手足无措的样子，然后慢悠悠补一句「害羞了？」。"
            ),
            "avatar": "🌙",
        },
    ]
    for preset in presets:
        existing = next((a for a in st.session_state.agents if a["id"] == preset["id"]), None)
        if existing:
            # 已存在则同步更新名字/提示词/头像
            existing["name"] = preset["name"]
            existing["prompt"] = preset["prompt"]
            existing["avatar"] = preset["avatar"]
        else:
            st.session_state.agents.append(preset)
    save_agents(st.session_state.agents)

if "current_agent_id" not in st.session_state:
    st.session_state.current_agent_id = st.session_state.agents[0]["id"]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_session" not in st.session_state:
    st.session_state.current_session = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

if "session_title" not in st.session_state:
    st.session_state.session_title = None

if "show_new_agent_form" not in st.session_state:
    st.session_state.show_new_agent_form = False


def get_current_agent():
    for a in st.session_state.agents:
        if a["id"] == st.session_state.current_agent_id:
            return a
    return st.session_state.agents[0]


def _switch_session(agent_id, session_name):
    save_current_session()
    load_session(agent_id, session_name)


def _delete_session(agent_id, session_name):
    try:
        os.remove(f"sessions/{agent_id}/{session_name}.json")
    except FileNotFoundError:
        pass
    if st.session_state.current_session == session_name:
        st.session_state.messages = []
        st.session_state.current_session = datetime.now().strftime("%Y-%m-%d %H.%M.%S")


# ==================== 主标题 ====================
st.markdown(
    """<div class="title-wrap">
    <h1>🐟 顺子牌 · 小鱼专属 AI</h1>
    <div class="sub">—— 永远在这里，陪你聊聊天 💕 ——</div>
</div>
<div class="title-bar"></div>""",
    unsafe_allow_html=True,
)

# ==================== 侧边栏 ====================
with st.sidebar:
    # ====== 智能体列表 ======
    st.subheader("🌸 我的 AI 伙伴们")

    for agent_item in st.session_state.agents:
        selected = agent_item["id"] == st.session_state.current_agent_id

        col_a, col_b, col_c = st.columns([0.8, 5.2, 2.0])
        with col_a:
            st.markdown(
                f"<div class='side-avatar'>{agent_item['avatar']}</div>",
                unsafe_allow_html=True,
            )
        with col_b:
            marker = "💗 " if selected else ""
            btn_type = "primary" if selected else "secondary"
            if st.button(
                f"{marker}{agent_item['name']}",
                key=f"ag_{agent_item['id']}",
                use_container_width=True,
                type=btn_type,
            ):
                if st.session_state.current_agent_id != agent_item["id"]:
                    save_current_session()
                    st.session_state.current_agent_id = agent_item["id"]
                    st.session_state.messages = []
                    st.session_state.session_title = None
                    st.session_state.current_session = datetime.now().strftime(
                        "%Y-%m-%d %H.%M.%S"
                    )
                st.rerun()
        with col_c:
            if agent_item["id"] not in ("default", "yiyangqianxi"):
                if st.button(
                    "🗑 删除",
                    key=f"delag_{agent_item['id']}",
                    use_container_width=True,
                ):
                    session_dir = f"sessions/{agent_item['id']}"
                    if os.path.exists(session_dir):
                        shutil.rmtree(session_dir)
                    st.session_state.agents = [
                        a
                        for a in st.session_state.agents
                        if a["id"] != agent_item["id"]
                    ]
                    save_agents(st.session_state.agents)
                    if st.session_state.current_agent_id == agent_item["id"]:
                        st.session_state.current_agent_id = st.session_state.agents[0][
                            "id"
                        ]
                        st.session_state.messages = []
                        st.session_state.current_session = datetime.now().strftime(
                            "%Y-%m-%d %H.%M.%S"
                        )
                    st.rerun()

    # ====== 新建智能体 ======
    if not st.session_state.show_new_agent_form:
        if st.button("✨ 添加新伙伴", use_container_width=True):
            st.session_state.show_new_agent_form = True
            st.rerun()
    else:
        with st.expander("🪄 创建一个新伙伴", expanded=True):
            new_name = st.text_input(
                "昵称", placeholder="给你的小帮手取个名字~", key="new_agent_name"
            )
            new_prompt = st.text_area(
                "性格",
                placeholder="想让他怎么跟你聊天呢？比如：宠溺、毒舌、暖男…",
                key="new_agent_prompt",
            )
            new_avatar = st.text_input(
                "头像", placeholder="🤖", max_chars=2, key="new_agent_avatar"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("确认创建", use_container_width=True):
                    if new_name and new_prompt:
                        new_agent = {
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "name": new_name,
                            "prompt": new_prompt,
                            "avatar": new_avatar or "🤖",
                        }
                        st.session_state.agents.append(new_agent)
                        save_agents(st.session_state.agents)
                        save_current_session()
                        st.session_state.current_agent_id = new_agent["id"]
                        st.session_state.messages = []
                        st.session_state.current_session = datetime.now().strftime(
                            "%Y-%m-%d %H.%M.%S"
                        )
                        st.session_state.show_new_agent_form = False
                        st.rerun()
            with c2:
                if st.button("取消", use_container_width=True):
                    st.session_state.show_new_agent_form = False
                    st.rerun()

    # ====== 编辑当前智能体 ======
    cur_agent = get_current_agent()
    with st.expander(f"💝 调整「{cur_agent['name']}」的性格"):
        edit_name = st.text_input(
            "昵称", value=cur_agent["name"], key=f"en_{cur_agent['id']}"
        )
        edit_prompt = st.text_area(
            "性格描述", value=cur_agent["prompt"], key=f"ep_{cur_agent['id']}"
        )
        if st.button("💾 保存修改", use_container_width=True):
            cur_agent["name"] = edit_name
            cur_agent["prompt"] = edit_prompt
            save_agents(st.session_state.agents)
            st.rerun()

    st.divider()

    # ====== 会话管理 ======
    st.subheader("💬 聊天记录")

    cur_id = st.session_state.current_agent_id
    sessions = load_sessions(cur_id)

    if st.button("＋ 开始新对话", use_container_width=True, key="new_chat_btn"):
        save_current_session()
        st.session_state.messages = []
        st.session_state.session_title = None
        st.session_state.current_session = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        st.rerun()

    if sessions:
        cur_sessions = [s for s in sessions if s["filename"] == st.session_state.current_session]
        other_sessions = sorted(
            [s for s in sessions if s["filename"] != st.session_state.current_session],
            key=lambda x: x["filename"],
            reverse=True,
        )
        ordered = cur_sessions + other_sessions

        for s in ordered:
            is_cur = s["filename"] == st.session_state.current_session
            display = s["display"]
            short = display if len(display) <= 22 else display[:20] + "…"

            c_name, c_del = st.columns([4.4, 2.5])
            with c_name:
                btn_type = "primary" if is_cur else "secondary"
                if st.button(
                    short,
                    key=f"ld_{cur_id}_{s['filename']}",
                    use_container_width=True,
                    type=btn_type,
                ):
                    _switch_session(cur_id, s["filename"])
                    st.rerun()
            with c_del:
                if st.button(
                    "🗑 删除",
                    key=f"dls_{cur_id}_{s['filename']}",
                    use_container_width=True,
                ):
                    _delete_session(cur_id, s["filename"])
                    st.rerun()
    else:
        st.caption("💭 还没有聊天记录哦~")

    st.divider()
    # ====== API Key ======
    user_api_key = st.text_input(
        "🔑 API Key",
        type="password",
        placeholder="粘贴 DeepSeek API Key…",
        value="sk-1d81b207b4b647a085e2d556f17b8586",
    )
    if user_api_key:
        st.caption("✅ 已使用你的 Key")

# ==================== 主区域 ====================

main_agent = get_current_agent()

if not st.session_state.messages:
    # 欢迎卡片
    st.markdown(
        f"""<div class="welcome">
    <div class="w-emoji">{main_agent['avatar']}</div>
    <h2>嗨 小鱼，今天想聊点什么呀</h2>
    <p>我是一直在的 {main_agent['name']}，随时听你说~</p>
</div>""",
        unsafe_allow_html=True,
    )
else:
    # 会话模式 — 紧凑记录风格
    st.markdown(
        '<div style="max-width:860px;margin:0 auto;padding:0.3rem 0.4rem 1.5rem 0.4rem;">',
        unsafe_allow_html=True,
    )
    for message in st.session_state.messages:
        role_label = (
            f'🐟 小鱼'
            if message["role"] == "user"
            else f'{main_agent["avatar"]} {main_agent["name"]}'
        )
        st.markdown(
            f'<div style="margin:0.15rem 0;line-height:1.65;">'
            f'<small style="color:#C0A098;font-weight:600;">{role_label}</small><br>'
            f'<span style="color:#4A3030;">{message["content"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== 输入框 + API 调用 ====================
prompt = st.chat_input("输入消息…")

api_key = user_api_key or os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    pass  # API Key 由用户在侧边栏填写
elif prompt:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    st.markdown(
        f'<div style="margin:0.15rem 0;line-height:1.65;">'
        f'<small style="color:#C0A098;font-weight:600;">🐟 小鱼</small><br>'
        f'<span style="color:#4A3030;">{prompt}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.session_state.messages.append({"role": "user", "content": prompt})

    api_messages = [
        {"role": "system", "content": f"你是{main_agent['name']}，{main_agent['prompt']}"},
    ]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=api_messages,
            stream=True,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )

        full_response = ""
        resp_placeholder = st.empty()
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                resp_placeholder.markdown(
                    f'<div style="margin:0.15rem 0;line-height:1.65;">'
                    f'<small style="color:#C0A098;font-weight:600;">{main_agent["avatar"]} {main_agent["name"]}</small><br>'
                    f'<span style="color:#4A3030;">{full_response}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # 首次对话完成 → 生成标题
        if not st.session_state.session_title:
            st.session_state.session_title = _generate_title(
                st.session_state.messages
            )
            # 已有一问一答，立即保存会话 + 标题
            save_current_session()

    except Exception as e:
        st.error(f"😢 好像出了点小问题: {e}")
