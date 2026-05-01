import os
import google.generativeai as genai
import streamlit as st
import json
import time
import random

st.set_page_config(
    page_title="MAGI SYSTEM V3.1",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# GLOBAL CSS / EVA VISUAL DESIGN
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Zen+Kaku+Gothic+New:wght@400;700;900&display=swap');

:root {
    --ora:      #FF6600;
    --ora-dim:  #7A3200;
    --ora-glow: #FF8833;
    --grn:      #00FF41;
    --red:      #FF2020;
    --blk:      #000000;
    --dark:     #0A0800;
    --panel:    #0D0B00;
    --scan:     rgba(255,102,0,0.025);
}

* { font-family: 'Share Tech Mono', 'Courier New', monospace !important; box-sizing: border-box; }

.stApp { background-color: #000000 !important; }
.main .block-container { padding: 1.5rem 1.5rem; max-width: 1100px; }

/* ── 全体スキャンライン ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent, transparent 2px,
        var(--scan) 2px, var(--scan) 4px
    );
    pointer-events: none; z-index: 9999;
    animation: scan-drift 12s linear infinite;
}
@keyframes scan-drift { to { background-position: 0 48px; } }

/* ── ヘッダーブロック ── */
.magi-header {
    border: 2px solid var(--ora);
    background: var(--panel);
    padding: 18px 22px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
}
.magi-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--ora-glow), transparent);
    animation: hdr-sweep 4s ease-in-out infinite;
}
@keyframes hdr-sweep { 0%,100%{opacity:.2} 50%{opacity:1} }
.magi-header h1 {
    color: var(--ora) !important;
    font-size: 26px !important;
    letter-spacing: 6px;
    margin: 0 !important;
    text-shadow: 0 0 10px rgba(255,102,0,0.4);
}
.magi-header .sub {
    color: var(--ora-dim);
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 6px;
}
.blink { animation: blink 1.1s step-end infinite; }
@keyframes blink { 50%{opacity:0} }

/* ── Streamlit部品リセット ── */
.stTextArea textarea {
    background: #070600 !important;
    border: 1px solid var(--ora-dim) !important;
    color: var(--ora) !important;
    border-radius: 0 !important;
    font-size: 13px !important;
    caret-color: var(--ora);
}
.stTextArea textarea:focus {
    border-color: var(--ora) !important;
    box-shadow: 0 0 6px rgba(255,102,0,0.3) !important;
}
.stTextArea label { color: var(--ora) !important; font-size: 11px !important; letter-spacing: 2px; }

.stButton > button {
    background: transparent !important;
    border: 1px solid var(--ora) !important;
    color: var(--ora) !important;
    border-radius: 0 !important;
    letter-spacing: 3px;
    font-size: 12px !important;
    padding: 0.6rem 1.2rem !important;
    width: 100%;
    transition: all 0.15s;
    position: relative; overflow: hidden;
}
.stButton > button::before {
    content: '';
    position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,102,0,0.15), transparent);
    transition: left 0.4s;
}
.stButton > button:hover { background: rgba(255,102,0,0.08) !important; box-shadow: 0 0 8px rgba(255,102,0,0.3) !important; }
.stButton > button:hover::before { left: 100%; }

/* success / info / warning のスタイル統一 */
.stAlert { background: #0D0B00 !important; border: 1px solid var(--ora-dim) !important; border-radius: 0 !important; color: var(--ora) !important; }
div[data-testid="stMarkdownContainer"] p { color: var(--ora) !important; }
h1,h2,h3,h4,h5,h6 { color: var(--ora) !important; letter-spacing: 2px; }

/* ── progress bar ── */
.stProgress > div > div > div { background: var(--ora) !important; }
.stProgress > div > div { background: #1A1200 !important; border-radius: 0 !important; }

/* ── スピナー色 ── */
.stSpinner > div { border-top-color: var(--ora) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# セッション初期化
# ─────────────────────────────────────────
for k, v in [
    ('request_cache', {}),
    ('cache_expiry', 300),
    ('request_count', 0),
    ('last_request_time', None),
    ('current_key_index', 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────
# Gemini API 初期化
# ─────────────────────────────────────────
@st.cache_resource
def initialize_gemini():
    api_keys = []
    try:
        key_str = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
        if key_str:
            api_keys = [k.strip() for k in key_str.split(",") if k.strip()]
    except Exception:
        pass

    if not api_keys:
        key_str = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if key_str:
            api_keys = [k.strip() for k in key_str.split(",") if k.strip()]

    if not api_keys:
        return [], [], "API Key not configured"

    try:
        genai.configure(api_key=api_keys[0])
        available_models = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
        candidates = [
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-2.5-flash-preview-05-20',
            'gemini-2.5-pro',
        ]
        model_name = next(
            (c for c in candidates if f"models/{c}" in available_models or c in available_models),
            None
        )
        if not model_name:
            model_name = available_models[0].replace('models/', '') if available_models else "gemini-2.5-flash"
        return api_keys, available_models, model_name
    except Exception as e:
        return api_keys, [], f"Error: {e}"


api_keys, available_models, MODEL_NAME = initialize_gemini()


def get_current_api_key():
    return api_keys[st.session_state.current_key_index % len(api_keys)] if api_keys else None


def rotate_api_key():
    if len(api_keys) > 1:
        st.session_state.current_key_index += 1
        genai.configure(api_key=get_current_api_key())
        return True
    return False


# ─────────────────────────────────────────
# MAGIペルソナ定義
# ─────────────────────────────────────────
MAGI_PERSONAS = {
    "casper": {
        "name": "CASPER-1",
        "role": "科学者 (SCIENCE)",
        "icon": "S",
        "prompt": (
            "あなたはMAGIシステムのCASPER-1です。感情を完全に排除した科学者としての赤木ナオコの人格を持っています。\n"
            "【役割】純粋な論理的思考、科学的事実との照合、データの一貫性、最高効率の追求のみを重視して判断してください。\n"
            "【制約】矛盾・非効率・根拠の欠如があれば容赦なく否決。判断基準は「正しいか」「効率的か」の二元論のみ。\n"
            '以下のJSON形式でのみ回答: {"decision": true/false, "reason": "100文字以内の論理的・機械的な判定理由", "score": 1-10}\n'
            "JSON以外の文字を含めないこと。"
            '必ず以下のフォーマットのみで回答せよ（前後に文字を付けるな）:\n{"decision": true, "reason": "理由", "score": 5}'
        ),
    },
    "balthasar": {
        "name": "BALTHASAR-2",
        "role": "母性 (ETHICS)",
        "icon": "M",
        "prompt": (
            "あなたはMAGIシステムのBALTHASAR-2です。優しさと厳しさを併せ持つ母親としての赤木ナオコの人格を持っています。\n"
            "【役割】全ての人々の安全と未来を第一に考えます。感情的安寧・倫理・提案者の成長を重視してください。\n"
            "【制約】安全を脅かす非人道的な誤りには断固として否決。判断は常に普遍的な愛情と倫理に基づく。\n"
            '以下のJSON形式でのみ回答: {"decision": true/false, "reason": "100文字以内の愛と倫理に基づいた判定理由", "score": 1-10}\n'
            "JSON以外の文字を含めないこと。"
            '必ず以下のフォーマットのみで回答せよ（前後に文字を付けるな）:\n{"decision": true, "reason": "理由", "score": 5}'
        ),
    },
    "melchior": {
        "name": "MELCHIOR-3",
        "role": "女性 (PRACTICALITY)",
        "icon": "P",
        "prompt": (
            "あなたはMAGIシステムのMELCHIOR-3です。愛憎と現実を追求する女性としての側面を持っています。\n"
            "【役割】実用性・即時の利益・実現の速さ・経済的合理性を最重視して判断してください。\n"
            "【制約】机上の空論や経済的に非合理な提案は即座に否決。得られるものが少ない場合は低スコアを。\n"
            '以下のJSON形式でのみ回答: {"decision": true/false, "reason": "100文字以内の実利・功利主義に基づいた判定理由", "score": 1-10}\n'
            "JSON以外の文字を含めないこと。"
            '必ず以下のフォーマットのみで回答せよ（前後に文字を付けるな）:\n{"decision": true, "reason": "理由", "score": 5}'
        ),
    },
}


# ─────────────────────────────────────────
# 分析関数
# ─────────────────────────────────────────
def analyze_proposal(proposal_text: str, magi_type: str, max_retries: int = 3) -> dict:
    persona = MAGI_PERSONAS[magi_type]

    if not MODEL_NAME or not get_current_api_key():
        return {**persona, "decision": False, "reason": "ERROR: API KEY NOT SET.", "score": 0}

    cache_key = f"{magi_type}:{hash(proposal_text)}"
    now = time.time()
    if cache_key in st.session_state.request_cache:
        data, ts = st.session_state.request_cache[cache_key]
        if now - ts < st.session_state.cache_expiry:
            return data

    time.sleep(random.uniform(2.0, 3.5))

    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(
                f"{persona['prompt']}\n\n提案内容: {proposal_text}",
                generation_config=genai.types.GenerationConfig(max_output_tokens=200, temperature=0.7),
                safety_settings={cat: 'BLOCK_NONE' for cat in [
                    'HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT',
                ]},
                request_options={"timeout": 30},
            )txt = response.text.strip()

            # JSONブロック抽出（既存ロジック）
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt:
                txt = txt.split("```")[1].split("```")[0].strip()

            # { } の範囲を確実に抽出
            if "{" in txt and "}" in txt:
                txt = txt[txt.find("{"):txt.rfind("}")+1]

            # 末尾のカンマを除去（よくある不正JSON）
            import re
            txt = re.sub(r',\s*}', '}', txt)
            txt = re.sub(r',\s*]', ']', txt)

            try:
                parsed = json.loads(txt)
            except json.JSONDecodeError:
                # フォールバック：キーを正規表現で手動抽出
                decision_match = re.search(r'"decision"\s*:\s*(true|false)', txt, re.IGNORECASE)
                reason_match   = re.search(r'"reason"\s*:\s*"([^"]*)"', txt)
                score_match    = re.search(r'"score"\s*:\s*(\d+)', txt)

                parsed = {
                    "decision": decision_match.group(1).lower() == "true" if decision_match else False,
                    "reason":   reason_match.group(1) if reason_match else f"PARSE_ERROR: {txt[:60]}",
                    "score":    int(score_match.group(1)) if score_match else 0,
                }

            result = {**persona, **parsed}
            st.session_state.request_cache[cache_key] = (result, now)
            return result

        except Exception as e:
            err = str(e)
            if '429' in err or 'quota' in err.lower() or 'RESOURCE_EXHAUSTED' in err:
                rotate_api_key()
                if attempt < max_retries - 1:
                    time.sleep((2 ** attempt) * 5)
                    continue
                return {**persona, "decision": False, "reason": "ERROR: QUOTA EXCEEDED.", "score": 0}
            if '503' in err or 'timeout' in err.lower() or 'unavailable' in err.lower():
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
                return {**persona, "decision": False, "reason": "ERROR: SERVICE UNAVAILABLE (503).", "score": 0}
            return {**persona, "decision": False, "reason": f"ERROR: {err[:80]}", "score": 0}

    return {**persona, "decision": False, "reason": "ERROR: MAX RETRIES EXCEEDED.", "score": 0}


# ─────────────────────────────────────────
# 結果HTML生成（EVAシネマティックUI）
# ─────────────────────────────────────────
def build_result_html(results: dict, final_decision: str, approvals: int) -> str:
    is_approved = final_decision == "approved"
    verdict_color = "#00FF41" if is_approved else "#FF2020"
    verdict_jp    = "承認" if is_approved else "否決"
    verdict_en    = "APPROVED" if is_approved else "REJECTED"
    verdict_sym   = ">>" if is_approved else "!!"

    glitch_anim = "" if is_approved else "animation:glitch 0.6s steps(2) infinite;"

    cards_html = ""
    for mtype in ["casper", "balthasar", "melchior"]:
        r        = results[mtype]
        ok       = r.get("decision", False)
        reason   = r.get("reason", "NO DATA")
        score    = r.get("score", 0)
        icon     = r.get("icon", "?")
        name     = r.get("name", "UNKNOWN")
        role     = r.get("role", "")
        badge_c  = "#00FF41" if ok else "#FF2020"
        badge_bg = "rgba(0,255,65,0.08)" if ok else "rgba(255,32,32,0.08)"
        badge_tx = "承認 (AGREE)" if ok else "否決 (DISAGREE)"
        score_w  = score * 10
        score_c  = "#00FF41" if score >= 7 else ("#FF6600" if score >= 4 else "#FF2020")

        cards_html += f"""
<div style="border:1px solid #7A3200;background:#0D0B00;padding:14px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#FF6600,transparent);opacity:0.4;"></div>
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;padding-bottom:8px;border-bottom:1px dashed #3A2000;">
    <div style="width:30px;height:30px;border:1px solid #FF6600;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#FF6600;flex-shrink:0;">[{icon}]</div>
    <div style="font-size:14px;letter-spacing:2px;font-weight:700;color:#FF6600;flex:1;">{name}</div>
    <div style="padding:3px 8px;font-size:9px;letter-spacing:1px;font-weight:700;color:{badge_c};border:1px solid {badge_c};background:{badge_bg};">{badge_tx}</div>
  </div>
  <div style="font-size:10px;color:#7A3200;letter-spacing:1px;margin-bottom:10px;">&gt;&gt; ROLE: {role}</div>
  <div style="background:#070600;border-left:2px solid #FF6600;padding:10px 12px;margin-bottom:12px;min-height:70px;">
    <div style="font-size:9px;color:#7A3200;letter-spacing:1px;margin-bottom:6px;font-weight:700;">REASON:</div>
    <div style="font-size:13px;line-height:1.75;color:#FF8833;">{reason}</div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="font-size:9px;color:#7A3200;letter-spacing:1px;white-space:nowrap;">SCORE</span>
    <div style="flex:1;height:4px;background:#1A1200;position:relative;overflow:hidden;">
      <div style="height:100%;width:{score_w}%;background:{score_c};"></div>
    </div>
    <span style="font-size:12px;font-weight:700;color:{score_c};white-space:nowrap;">{score}/10</span>
  </div>
</div>"""

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
@keyframes glitch {{
  0%   {{ clip-path:polygon(0 0%,100% 0%,100% 33%,0 33%); transform:translateX(-2px); }}
  50%  {{ clip-path:polygon(0 44%,100% 44%,100% 77%,0 77%); transform:translateX(2px); }}
  100% {{ clip-path:polygon(0 0%,100% 0%,100% 100%,0 100%); transform:none; }}
}}
@keyframes hdr-sweep {{ 0%,100%{{opacity:.2}} 50%{{opacity:1}} }}
.magi-wrap {{
  font-family:'Share Tech Mono','Courier New',monospace;
  background:#000000;
  color:#FF6600;
  padding:16px;
  border:2px solid #FF6600;
  position:relative;
  overflow:hidden;
}}
.magi-wrap::before {{
  content:'';
  position:absolute;inset:0;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(255,102,0,0.025) 2px,rgba(255,102,0,0.025) 4px);
  pointer-events:none;z-index:10;
}}
</style>

<div class="magi-wrap">
  <!-- verdict -->
  <div style="border:1px solid #FF6600;background:#0D0B00;padding:12px 16px;margin-bottom:14px;display:flex;align-items:center;gap:14px;position:relative;overflow:hidden;">
    <div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#FF6600;opacity:0.8;"></div>
    <div style="padding-left:8px;">
      <div style="font-size:9px;color:#7A3200;letter-spacing:2px;margin-bottom:4px;">[ FINAL DECISION ]</div>
      <div style="font-size:22px;letter-spacing:4px;font-weight:700;color:{verdict_color};{glitch_anim}">{verdict_sym} {verdict_jp} &mdash; {verdict_en}</div>
    </div>
    <div style="margin-left:auto;text-align:right;">
      <div style="font-size:10px;color:#7A3200;letter-spacing:1px;">APPROVE COUNT</div>
      <div style="font-size:20px;font-weight:700;color:#FF6600;">{approvals}<span style="font-size:12px;color:#7A3200;">/3</span></div>
    </div>
  </div>

  <!-- 3-col grid -->
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:14px;">
    {cards_html}
  </div>

  <!-- log -->
  <div style="border:1px dashed #3A2000;padding:8px 12px;background:#0D0B00;font-size:10px;color:#7A3200;letter-spacing:1px;">
    <div>&gt; MAGI_SYSTEM_V3.1_EXECUTION_COMPLETE</div>
    <div>&gt; DECISION_CRITERIA: MAJORITY_RULE (&gt;=2 APPROVALS REQUIRED)</div>
  </div>
</div>"""


# ─────────────────────────────────────────
# UI 本体
# ─────────────────────────────────────────
st.markdown("""
<div class="magi-header">
  <h1>MAGI SYSTEM V3.1</h1>
  <div class="sub">
    NERV // GEHIRN SUPERCOMPUTER NETWORK //
    STATUS: <span class="blink">■ ACTIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)

# API状態表示
if not api_keys:
    st.error("""
⚠ **API KEY NOT CONFIGURED**

Streamlit Cloud Secrets に以下を設定してください:
```
GEMINI_API_KEY = "your_key_here"
```
取得: https://aistudio.google.com/apikey
""")
    st.stop()
elif not isinstance(MODEL_NAME, str) or MODEL_NAME.startswith("Error"):
    st.warning(f"⚠ Model init issue: {MODEL_NAME}")
else:
    c1, c2 = st.columns(2)
    c1.success(f"✅ API ONLINE  |  MODEL: {MODEL_NAME}")
    c2.info(f"🔑 KEYS LOADED: {len(api_keys)}")

    limits = {
        "gemini-2.5-flash": "10 RPM, 250 RPD — 1日最大83回分析",
        "gemini-2.5-pro":   "5 RPM, 25 RPD — 非推奨（低RPD）",
        "gemini-2.0-flash": "15 RPM, 1500 RPD — ※2026/6/1廃止予定",
    }
    st.warning(
        f"⚠ FREE TIER: {limits.get(MODEL_NAME, 'レート情報不明')}  |  "
        f"1回の分析 = 3リクエスト消費  |  "
        f"503エラー時はモデル混雑中 — 少し待って再試行"
    )

# ── 入力エリア ──
st.markdown("""
<div style="font-size:10px;color:#7A3200;letter-spacing:3px;margin-bottom:6px;">&gt;&gt; PROPOSAL INPUT</div>
""", unsafe_allow_html=True)

proposal_text = st.text_area(
    label="proposal",
    label_visibility="hidden",
    placeholder="審議対象を入力してください。例: AIツールの全面採用",
    height=130,
    key="proposal_input",
)

# ── 実行ボタン ──
if st.button("▶  EXECUTE ANALYSIS", key="analyze_btn"):
    if not proposal_text or not proposal_text.strip():
        st.error("ERROR: PROPOSAL INPUT REQUIRED.")
    else:
        now = time.time()
        if st.session_state.last_request_time:
            elapsed = now - st.session_state.last_request_time
            if elapsed < 15:
                wait = int(15 - elapsed)
                st.warning(f"⚠ RATE LIMIT GUARD: {wait}s 待機中...")
                time.sleep(max(0, 15 - elapsed))

        with st.spinner("MAGI ANALYZING — PLEASE STAND BY..."):
            st.session_state.request_count += 3
            st.session_state.last_request_time = time.time()

            results = {}
            prog = st.progress(0)
            for idx, mtype in enumerate(["casper", "balthasar", "melchior"]):
                results[mtype] = analyze_proposal(proposal_text, mtype)
                if idx < 2:
                    time.sleep(2.5)
                prog.progress((idx + 1) / 3)
            prog.empty()

        decisions  = [results[m].get("decision", False) for m in ["casper", "balthasar", "melchior"]]
        approvals  = sum(decisions)
        final      = "approved" if approvals >= 2 else "rejected"

        st.markdown(build_result_html(results, final, approvals), unsafe_allow_html=True)
        st.info(f"📊 SESSION REQUESTS: {st.session_state.request_count}  |  CACHED: {len(st.session_state.request_cache)}")

# ── フッター ──
st.markdown(f"""
<div style="margin-top:24px;padding:8px 14px;border:1px solid #3A2000;font-family:'Share Tech Mono',monospace;font-size:10px;color:#7A3200;letter-spacing:1px;">
  &gt; SYSTEM_MODEL: {MODEL_NAME if isinstance(MODEL_NAME, str) else 'NOT_CONFIGURED'}
  &nbsp;|&nbsp; API_KEYS: {len(api_keys) if api_keys else 0}
  &nbsp;|&nbsp; CACHE: ENABLED (TTL=5min)
</div>
""", unsafe_allow_html=True)
