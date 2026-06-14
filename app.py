import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ==============================================================================
# PAGE CONFIGURATION & THEME
# ==============================================================================
st.set_page_config(
    page_title="Offer 選擇障礙終結者 | 職涯決策加權分析儀",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design & Visual Polish (Glassmorphism, beautiful gradients, custom typography)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global styles */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    /* Standard headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 12px rgba(56, 189, 248, 0.1);
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.25rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Card design */
    .card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    
    .winner-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.1);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .winner-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .winner-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #e9d5ff;
        margin: 0.5rem 0;
        text-shadow: 0 2px 10px rgba(168, 85, 247, 0.3);
    }
    
    .badge {
        background: linear-gradient(90deg, #f43f5e 0%, #fb7185 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    /* Input container adjustments */
    .stSlider > div [data-baseweb="slider"] {
        margin-top: 10px;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    /* Customized Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        margin-bottom: 5px;
    }
    
    /* Styled tips */
    .tip-box {
        background: rgba(56, 189, 248, 0.05);
        border-left: 4px solid #38bdf8;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# APPLICATION HEADER
# ==============================================================================
st.markdown("<div class='main-title'>⚖️ Offer 選擇障礙終結者</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>別再擲筊、抽籤、問神明了！用科學加權演算法，挖掘你內心深處最真實的選擇。</div>", unsafe_allow_html=True)
st.write("---")

# ==============================================================================
# STATE INITIALIZATION
# ==============================================================================
# Default values to initialize state
if 'dimensions' not in st.session_state:
    st.session_state.dimensions = {
        "薪資福利": {"icon": "💰", "weight": 8, "desc": "含底薪、年終、分紅、認股與各類津貼"},
        "技術與職涯成長": {"icon": "📈", "weight": 7, "desc": "技術棧、學習空間、公司名氣、未來跳槽加分度"},
        "WLB與彈性": {"icon": "🏡", "weight": 6, "desc": "每日工時、通勤時間、加班頻率、遠端工作天數"},
        "團隊氛圍與主管": {"icon": "🤝", "weight": 5, "desc": "主管風格、同事好相處程度、組織政治文化強度"}
    }

# ==============================================================================
# INTERFACE LAYOUT
# ==============================================================================
col1, col2 = st.columns([1, 1.2], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: INPUT DATA & PREFERENCES
# ------------------------------------------------------------------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("1. 填入你的 Offer 資訊")
    
    # 1. 初始化 Session State (用來記憶目前有幾間公司)
    if "company_count" not in st.session_state:
        st.session_state.company_count = 2
        st.session_state.company_names = ["公司 A", "公司 B"]

    # 2. 定義按鈕點擊後的動作
    def add_company():
        st.session_state.company_count += 1
        st.session_state.company_names.append(f"新公司 {st.session_state.company_count}")

    # 3. 根據目前的數量，動態產生對應數量的輸入框
    updated_companies = []
    
    for i in range(st.session_state.company_count):
        # 確保名稱陣列長度足夠
        if i >= len(st.session_state.company_names):
            st.session_state.company_names.append(f"新公司 {i+1}")
            
        comp_name = st.text_input(
            f"第 {i+1} 間公司名稱", 
            value=st.session_state.company_names[i], 
            key=f"comp_input_{i}" # 每個輸入框必須有獨立的 key
        )
        updated_companies.append(comp_name)
                
    # 將使用者修改後的名字存回 Session State
    st.session_state.company_names = updated_companies
            
    # 4. 新增按鈕
    st.button("➕ 新增一間公司", on_click=add_company, use_container_width=True)
    
    # 整理出最終有效且不空白的公司名單，傳遞給後面的評分邏輯
    companies = list(dict.fromkeys([c.strip() for c in st.session_state.company_names if c.strip()]))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("2. 設定你有多在乎這些指標 (權重)")
    st.caption("數字愈大，代表你愈看重這個項目。你可以點擊下方自訂指標。")
    
    # Expandable customization for evaluation criteria
    with st.expander("🛠️ 自訂評估維度與說明"):
        # Allow adding a new dimension
        new_dim_col1, new_dim_col2 = st.columns([2, 1])
        with new_dim_col1:
            new_dim_name = st.text_input("新增自訂維度名稱", placeholder="例如：公司穩定度、出差頻率...")
        with new_dim_col2:
            new_dim_icon = st.text_input("圖示 (Emoji)", value="✨", max_chars=2)
            
        if st.button("➕ 新增維度", use_container_width=True):
            if new_dim_name and new_dim_name not in st.session_state.dimensions:
                st.session_state.dimensions[new_dim_name] = {
                    "icon": new_dim_icon,
                    "weight": 5,
                    "desc": "自訂評估項目"
                }
                st.rerun()
                
        # Show existing dimensions with delete button
        st.write("目前維度管理（可刪除不必要的項目）：")
        dims_to_delete = []
        for dim_name, info in st.session_state.dimensions.items():
            dim_row_col1, dim_row_col2 = st.columns([4, 1])
            with dim_row_col1:
                st.caption(f"{info['icon']} **{dim_name}** - {info['desc']}")
            with dim_row_col2:
                if st.button("🗑️", key=f"del_{dim_name}"):
                    dims_to_delete.append(dim_name)
                    
        if dims_to_delete:
            for d in dims_to_delete:
                del st.session_state.dimensions[d]
            st.rerun()

    # Dynamic Weight Sliders based on Session State
    weights = {}
    for dim_name, info in st.session_state.dimensions.items():
        weights[dim_name] = st.slider(
            f"{info['icon']} {dim_name} (權重)", 
            min_value=1, 
            max_value=10, 
            value=info['weight'],
            help=info['desc'],
            key=f"w_{dim_name}"
        )
        # Sync back to session state to preserve weights on reload
        st.session_state.dimensions[dim_name]['weight'] = weights[dim_name]
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("3. 請為各公司打分 (1-10分)")
    st.caption("1分代表極度不滿意或極差，10分代表完美夢幻")
    
    # Store scores in a dictionary
    scores = {}
    for comp in companies:
        with st.expander(f"🏢 評估 {comp} 的各項表現", expanded=True):
            scores[comp] = {}
            for dim_name, info in st.session_state.dimensions.items():
                scores[comp][dim_name] = st.slider(
                    f"{info['icon']} {dim_name} 得分",
                    min_value=1,
                    max_value=10,
                    value=5,
                    key=f"{comp}_{dim_name}_score"
                )
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# RIGHT COLUMN: ANALYTICS & DECISION REPORT
# ------------------------------------------------------------------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 數據分析診斷報告")
    
    if len(companies) < 2:
        st.warning("⚠️ 請在左側輸入至少兩間公司名稱（用逗號分開）進行比較！")
        
        # Example representation when no companies are evaluated yet
        st.info("💡 範例：輸入『公司 A, 公司 B』，然後在下方展開折疊欄位為它們評分。")
    else:
        # Calculate Weighted Scores
        results = []
        for comp in companies:
            total_score = 0
            max_possible_score = 0
            aspect_scores = {}
            
            for dim_name in weights:
                total_score += scores[comp][dim_name] * weights[dim_name]
                max_possible_score += 10 * weights[dim_name]
                aspect_scores[dim_name] = scores[comp][dim_name]
                
            # Normalized score out of 100 for better comprehension
            normalized_score = round((total_score / max_possible_score) * 100, 1) if max_possible_score > 0 else 0
            
            results.append({
                "公司": comp, 
                "加權總分": total_score,
                "滿意度百分比 (%)": normalized_score,
                **aspect_scores
            })
            
        df_results = pd.DataFrame(results).sort_values(by="加權總分", ascending=False)
        
        # Determine the winner
        winner = df_results.iloc[0]["公司"]
        winner_score = df_results.iloc[0]["加權總分"]
        winner_pct = df_results.iloc[0]["滿意度百分比 (%)"]
        
        # Check if there is a runner up and if the gap is very narrow (within 3% of total score)
        is_tie_or_narrow = False
        runner_up_text = ""
        if len(df_results) > 1:
            runner_up = df_results.iloc[1]["公司"]
            runner_up_score = df_results.iloc[1]["加權總分"]
            score_diff_pct = abs(winner_pct - df_results.iloc[1]["滿意度百分比 (%)"])
            if score_diff_pct < 4.0:
                is_tie_or_narrow = True
                runner_up_text = f"與第二名 **{runner_up}** 的差距僅有 {round(score_diff_pct, 1)}%！這是一場伯仲之間的對決。"

        # Premium Winner Card
        st.markdown(f"""
        <div class="winner-card">
            <div class="badge">🥇 演算法推薦首選</div>
            <div style="font-size: 1.1rem; color: #cbd5e1; margin-top: 5px;">你靈魂深處真正想去的公司是</div>
            <div class="winner-title">{winner}</div>
            <div style="font-size: 1.2rem; color: #a78bfa; font-weight: 600; margin-top: 5px;">
                滿意度：{winner_pct}% （加權總分：{winner_score} 分）
            </div>
            {f'<div style="font-size: 0.95rem; color: #f43f5e; margin-top: 10px; font-weight: 500;">⚠️ 警告：{runner_up_text}</div>' if is_tie_or_narrow else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Removed balloon effect to keep the interface clean and professional
            
        # Display summary dataframe
        st.subheader("📋 加權分數總表")
        display_cols = ["公司", "加權總分", "滿意度百分比 (%)"] + list(weights.keys())
        st.dataframe(
            df_results[display_cols], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "滿意度百分比 (%)": st.column_config.ProgressColumn(
                    "綜合滿意度 (%)",
                    help="加權後折合為百分比的分數",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )
        
        st.write("---")
        st.subheader("🕸️ 決策維度雷達圖對比")
        st.caption("分數愈往外圍愈好。覆蓋面積愈大，代表該 Offer 越符合你的理想標準。")
        
        # Plot Radar Chart (Plotly)
        categories = list(weights.keys())
        categories_closed = categories + [categories[0]]
        
        fig = go.Figure()
        
        # Color palette for modern aesthetics
        colors = [
            'rgba(56, 189, 248, ',   # Sky Blue
            'rgba(168, 85, 247, ',   # Purple
            'rgba(244, 63, 94, ',    # Rose Red
            'rgba(34, 197, 94, ',    # Green
            'rgba(234, 179, 8, ',    # Yellow
        ]
        
        for idx, row in enumerate(df_results.itertuples()):
            comp = row.公司
            r_values = [getattr(row, cat.replace(" ", "_").replace("/", "_").replace("-", "_")) for cat in categories]
            r_values.append(r_values[0])
            
            color_base = colors[idx % len(colors)]
            
            fig.add_trace(go.Scatterpolar(
                r=r_values,
                theta=categories_closed,
                fill='toself',
                name=comp,
                line=dict(color=color_base + "1)"),
                fillcolor=color_base + "0.15)",
                opacity=0.85
            ))
            
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(30, 41, 59, 0.5)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    linecolor='rgba(255, 255, 255, 0.1)',
                    tickfont=dict(color='#94a3b8')
                ),
                angularaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    linecolor='rgba(255, 255, 255, 0.1)',
                    tickfont=dict(color='#cbd5e1', size=11)
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color='#cbd5e1')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=20, b=40),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Dimension Breakdown chart (Bar Chart)
        st.subheader("📊 各維度滿意度直條圖")
        
        # Melt dataframe to long format for bar chart plotting
        melted_df = pd.melt(df_results, id_vars=['公司'], value_vars=categories, var_name='維度', value_name='得分')
        
        fig_bar = go.Figure()
        for idx, comp in enumerate(df_results['公司']):
            comp_data = melted_df[melted_df['公司'] == comp]
            color_base = colors[idx % len(colors)]
            fig_bar.add_trace(go.Bar(
                x=comp_data['維度'],
                y=comp_data['得分'],
                name=comp,
                marker_color=color_base + "0.85)"
            ))
            
        fig_bar.update_layout(
            barmode='group',
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#cbd5e1')),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, 10], tickfont=dict(color='#cbd5e1')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color='#cbd5e1')
            ),
            margin=dict(l=40, r=40, t=20, b=40),
            height=300
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

        # Download Report Option
        st.write("---")
        st.subheader("📥 匯出評估報告")
        csv_data = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 下載 CSV 評估數據",
            data=csv_data,
            file_name="offer_evaluation_report.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Actionable insights / tips based on results
        st.markdown(f"""
        <div class="tip-box">
            <h4>💡 決策大師的悄悄話：</h4>
            <ul>
                {"<li><b>糾結警報：</b>第一名與第二名差距極小，請點開左側評分說明，特別檢查那些被你設定為高權重的維度，你的評分是否摻雜了外部期望而非真實渴望。</li>" if is_tie_or_narrow else f"<li><b>決策明確度高：</b>首選 <b>{winner}</b> 與其他 Offer 有明顯差距，你的內心天秤已經傾斜，可以直接朝此目標前進。</li>"}
                <li><b>權重微調法：</b>你可以試著閉上眼睛，想像其中一個 Offer 被拒絕時的失落感，如果對某個 Offer 被拒絕毫無波瀾，可以適度調低該維度的權重或它的分數。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
