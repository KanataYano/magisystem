import streamlit as st
import random
import time

st.set_page_config(
    page_title="MAGI SYSTEM V3.1 [LOCAL]",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# GLOBAL CSS
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
.stButton > button:hover {
    background: rgba(255,102,0,0.08) !important;
    box-shadow: 0 0 8px rgba(255,102,0,0.3) !important;
}

.stAlert {
    background: #0D0B00 !important;
    border: 1px solid var(--ora-dim) !important;
    border-radius: 0 !important;
    color: var(--ora) !important;
}
div[data-testid="stMarkdownContainer"] p { color: var(--ora) !important; }
h1,h2,h3,h4,h5,h6 { color: var(--ora) !important; letter-spacing: 2px; }

.stProgress > div > div > div { background: var(--ora) !important; }
.stProgress > div > div { background: #1A1200 !important; border-radius: 0 !important; }
.stSpinner > div { border-top-color: var(--ora) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# キーワード辞書
# ─────────────────────────────────────────
POSITIVE_KEYWORDS = [
    "効率", "改善", "安全", "利益", "成長", "革新", "最適", "向上", "推進", "促進",
    "発展", "強化", "拡大", "節約", "合理", "生産", "価値", "貢献", "支援", "協力",
    "戦略", "計画", "実装", "導入", "活用", "解決", "達成", "成功", "明確", "確実",
]

NEGATIVE_KEYWORDS = [
    "危険", "リスク", "問題", "失敗", "損失", "削減", "廃止", "停止", "中断", "違反",
    "不正", "禁止", "困難", "不安", "懸念", "障害", "欠陥", "矛盾", "非効率", "無駄",
    "コスト", "負担", "複雑", "不明", "曖昧", "遅延", "過剰", "不足", "限界", "破綻",
]

# ─────────────────────────────────────────
# ペルソナ別理由テンプレート
# ─────────────────────────────────────────
TEMPLATES = {
    "casper": {
        True: [
            "データの一貫性を確認。論理的矛盾なし。効率係数は許容範囲内。承認を推奨する。",
            "科学的見地から分析完了。仮説は検証可能であり、実装コストは最小化されている。",
            "演算結果：提案の有効性は統計的に有意。誤差範囲内での承認を支持する。",
            "システム解析完了。提案の構造は論理的整合性を保持。推進を是とする。",
            "データポイントを照合。ノイズを除去した結果、提案は最適解に近似している。",
        ],
        False: [
            "論理的矛盾を検出。根拠データの欠如により否決。再設計を要求する。",
            "科学的検証不能。仮定が多すぎる。エビデンスの提示なく承認は不可能だ。",
            "演算結果：リスク係数が閾値を超過。統計的有意性なし。否決が最適解。",
            "システムエラー：提案の論理構造に欠陥あり。効率性の観点から承認できない。",
            "データ不整合を確認。前提条件が成立していない。論理的に受理不可能だ。",
        ],
    },
    "balthasar": {
        True: [
            "人々の安全と幸福を最優先に考えた結果、この提案は未来への希望となりうる。承認する。",
            "倫理的観点から精査した。この提案は人間の尊厳を守り、社会に貢献するものだ。",
            "愛情と責任の目で見た。提案は傷つく者を生まず、多くの人を救う可能性がある。",
            "母として、この提案が次世代に残すものを考えた。価値があると判断する。承認。",
            "人の心に寄り添う提案だ。倫理的問題なし。未来のために推進を支持する。",
        ],
        False: [
            "人への影響を慎重に検討した。この提案は誰かを傷つける可能性がある。否決する。",
            "倫理的に受け入れられない。弱者への配慮が欠如している。母として断固反対する。",
            "愛情の目で見ても、この提案には危険な側面がある。安全が確保されるまで否決。",
            "未来の子供たちのことを考えた。この道は間違っている。人道的観点から否決する。",
            "誰かの涙につながる可能性がある提案を承認することはできない。再考を求める。",
        ],
    },
    "melchior": {
        True: [
            "費用対効果を算出。投資回収期間は短く、即時の利益が見込める。承認が合理的だ。",
            "実用性を最重視した評価を実施。この提案は現実的かつ速やかに実行可能だ。",
            "経済合理性あり。市場への影響は正であり、利益の最大化に貢献する提案だ。",
            "実利の観点から分析完了。コストを上回るリターンが期待できる。推進を支持する。",
            "スピードと効率を重視した結果、この提案は即効性が高い。実行に移すべきだ。",
        ],
        False: [
            "費用対効果が低すぎる。投資に見合うリターンが見込めない。即座に否決する。",
            "実用性なし。机上の空論に過ぎない。現実の利益につながらない提案は不要だ。",
            "経済的損失リスクが高い。このまま進めば損失が拡大する。実利的に否決する。",
            "スピードが遅すぎる。実現までのコストが膨大だ。もっと効率的な方法があるはずだ。",
            "得られるものが少なすぎる。リソースの無駄遣いだ。功利主義的観点から否決する。",
        ],
    },
}


# ─────────────────────────────────────────
# ローカル判定エンジン
# ─────────────────────────────────────────
def compute_base_score(text: str) -> float:
    """キーワード重み付けでベーススコアを算出（0.0〜1.0）"""
    text_lower = text.lower()
    pos = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    neg = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    length_bonus = min(len(text) / 200, 1.0) * 0.5
    total = pos - neg * 1.5 + length_bonus
    normalized = (total + 5) / 10
    return max(0.0, min(1.0, normalized))


def analyze_local(proposal_text: str, magi_type: str) -> dict:
    base = compute_base_score(proposal_text)

    # ペルソナ別バイアス
    bias = {
        "casper":    0.0,   # 中立（論理）
        "balthasar": 0.05,  # 少し承認よりり（優しさ）
        "melchior":  -0.05, # 少し否決より（厳しい実利）
    }

    score_float = base + bias[magi_type] + random.uniform(-0.15, 0.15)
    score_float = max(0.0, min(1.0, score_float))

    # 閾値で決定（ペルソナ別）
    threshold = {"casper": 0.5, "balthasar": 0.45, "melchior": 0.55}
    decision = score_float >= threshold[magi_type]

    # スコア（1〜10）にランダムブレ付き
    score_int = int(score_float * 10)
    score_int = max(1, min(10, score_int + random.randint(-1, 1)))

    reason = random.choice(TEMPLATES[magi_type][decision])

    persona_meta = {
        "casper":    {"name": "CASPER-1",    "role": "科学者 (SCIENCE)",       "icon": "S"},
        "balthasar": {"name": "BALTHASAR-2", "role": "母性 (ETHICS)",           "icon": "M"},
        "melchior":  {"name": "MELCHIOR-3",  "role": "女性 (PRACTICALITY)",     "icon": "P"},
    }

    return {
        **persona_meta[magi_type],
        "decision": decision,
        "reason":   reason,
        "score":    score_int,
    }


# ─────────────────────────────────────────
# 結果HTML生成
# ─────────────────────────────────────────
def build_result_html(results: dict, final_decision: str, approvals: int) -> str:
    is_approved = final_decision == "approved"
    verdict_color = "#00FF41" if is_approved else "#FF2020"
    verdict_jp    = "承認" if is_approved else "否決"
    verdict_en    = "APPROVED" if is_approved else "REJECTED"
    verdict_sym   = ">>" if is_approved else "!!"
    glitch_anim   = "" if is_approved else "animation:glitch 0.6s steps(2) infinite;"

    cards_html = ""
    for mtype in ["casper", "balthasar", "melchior"]:
        r       = results[mtype]
        ok      = r.get("decision", False)
        reason  = r.get("reason", "NO DATA")
        score   = r.get("score", 0)
        icon    = r.get("icon", "?")
        name    = r.get("name", "UNKNOWN")
        role    = r.get("role", "")
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

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:14px;">
    {cards_html}
  </div>

  <div style="border:1px dashed #3A2000;padding:8px 12px;background:#0D0B00;font-size:10px;color:#7A3200;letter-spacing:1px;">
    <div>&gt; MAGI_SYSTEM_V3.1_LOCAL_MODE_EXECUTION_COMPLETE</div>
    <div>&gt; ENGINE: RULE_BASED + WEIGHTED_RANDOM (NO API)</div>
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
    MODE: <span style="color:#00FF41;">■ LOCAL [NO API]</span> &nbsp;|&nbsp;
    STATUS: <span class="blink">■ ACTIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.info("🖥 LOCAL MODE: APIキー不要。ルールベース＋加重ランダムエンジンで動作中。")

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

if st.button("▶  EXECUTE ANALYSIS", key="analyze_btn"):
    if not proposal_text or not proposal_text.strip():
        st.error("ERROR: PROPOSAL INPUT REQUIRED.")
    else:
        with st.spinner("MAGI ANALYZING — PLEASE STAND BY..."):
            results = {}
            prog = st.progress(0)
            for idx, mtype in enumerate(["casper", "balthasar", "melchior"]):
                time.sleep(0.8)  # 演出用ウェイト
                results[mtype] = analyze_local(proposal_text, mtype)
                prog.progress((idx + 1) / 3)
            prog.empty()

        decisions = [results[m].get("decision", False) for m in ["casper", "balthasar", "melchior"]]
        approvals = sum(decisions)
        final     = "approved" if approvals >= 2 else "rejected"

        st.markdown(build_result_html(results, final, approvals), unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:24px;padding:8px 14px;border:1px solid #3A2000;font-size:10px;color:#7A3200;letter-spacing:1px;">
  &gt; ENGINE: LOCAL_RULE_BASED_V1.0
  &nbsp;|&nbsp; API: NOT_REQUIRED
  &nbsp;|&nbsp; KEYWORDS: WEIGHTED_ANALYSIS
</div>
""", unsafe_allow_html=True)
