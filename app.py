"""
app.py
TruthLayer: Automated Fact-Checking & Claim Verification Web App
Assessment Part 2 Submission for CogCulture

Built with Streamlit and factcheck_engine.
"""

import os
import io
import json
import pandas as pd
import streamlit as st
from factcheck_engine import process_pdf_document

# Page configuration
st.set_page_config(
    page_title="TruthLayer | Automated Fact-Checking Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design system
st.markdown("""
<style>
    /* Global Styling */
    .main {
        background-color: #0b0f19;
    }
    
    /* Header Branding */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid #312e81;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        color: #a5b4fc;
        font-size: 14px;
        margin-top: 8px;
        margin-bottom: 0;
    }

    /* KPI Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-val {
        font-size: 32px;
        font-weight: 800;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 6px;
    }

    /* Status Badges */
    .badge-verified {
        background-color: #064e3b;
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-inaccurate {
        background-color: #78350f;
        color: #fbbf24;
        border: 1px solid #d97706;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-false {
        background-color: #7f1d1d;
        color: #f87171;
        border: 1px solid #dc2626;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    /* Claim Container */
    .claim-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .claim-quote {
        font-size: 14.5px;
        color: #f1f5f9;
        font-style: italic;
        border-left: 3px solid #6366f1;
        padding-left: 14px;
        margin: 12px 0;
    }
    .real-fact-box {
        background: #0f172a;
        border-left: 4px solid #10b981;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 10px;
    }
    .real-fact-title {
        color: #10b981;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .real-fact-text {
        color: #e2e8f0;
        font-size: 13.5px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛡️ TruthLayer™: Automated Fact-Checking Agent</div>
    <div class="hero-subtitle">Automated "Truth Layer" that ingests PDFs, cross-references statistical & financial claims against live web consensus, and exposes hallucinations.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("Verification Controls")
    st.markdown("**CogCulture Assessment • Part 2**")
    st.divider()

    st.subheader("📋 Evaluation Trap Test")
    st.markdown("Test the system against intentional lies and outdated statistics in 1-click:")
    
    sample_trap_path = os.path.join(os.path.dirname(__file__), "sample_marketing_trap_document.pdf")
    load_trap_clicked = st.button("⚡ Run Fact-Check on Trap Document", use_container_width=True, type="primary")

    if os.path.exists(sample_trap_path):
        with open(sample_trap_path, "rb") as f:
            st.download_button(
                label="📥 Download Trap PDF",
                data=f.read(),
                file_name="sample_marketing_trap_document.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.divider()
    st.subheader("⚙️ Agent Pipeline")
    st.markdown("""
    1. **PDF Extractor:** PyPDF2 AST
    2. **Claim Miner:** Stats, Dates, Valuation
    3. **Truth Search:** Live Web & Ground Truth
    4. **Classifier:** Verified / Inaccurate / False
    """)
    st.caption("v1.2.0 • Production Agent")

# File Upload / Evaluation State
uploaded_file = st.file_uploader(
    "Upload a Marketing PDF or Whitepaper for Automated Fact-Checking",
    type=["pdf"],
    help="Upload any PDF to extract claims, verify them against live web data, and flag inaccurate or fabricated stats."
)

target_pdf_stream = None
doc_label = ""

if load_trap_clicked:
    if os.path.exists(sample_trap_path):
        target_pdf_stream = open(sample_trap_path, "rb")
        doc_label = "sample_marketing_trap_document.pdf (Official Evaluation Trap Document)"
        st.session_state["cached_pdf"] = target_pdf_stream.read()
        st.session_state["cached_label"] = doc_label
elif uploaded_file is not None:
    target_pdf_stream = uploaded_file
    doc_label = uploaded_file.name
    st.session_state["cached_pdf"] = uploaded_file.getvalue()
    st.session_state["cached_label"] = doc_label
elif "cached_pdf" in st.session_state:
    target_pdf_stream = io.BytesIO(st.session_state["cached_pdf"])
    doc_label = st.session_state["cached_label"]

# Main Processing Logic
if target_pdf_stream is not None:
    if isinstance(target_pdf_stream, bytes):
        target_pdf_stream = io.BytesIO(target_pdf_stream)

    with st.spinner(f"🔍 Analyzing '{doc_label}' — Mining statistical claims & cross-referencing live web data..."):
        try:
            results = process_pdf_document(target_pdf_stream)
        except Exception as e:
            st.error(f"Error parsing PDF document: {str(e)}")
            results = None

    if results:
        st.success(f"Fact-Check Complete for **{doc_label}**! ({results['num_pages']} pages scanned, {results['total_claims']} verifiable claims extracted)")

        # KPI Metric Dashboard
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #6366f1;">{results['total_claims']}</div>
                <div class="metric-label">Total Claims</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid #10b981;">
                <div class="metric-val" style="color: #10b981;">{results['count_verified']}</div>
                <div class="metric-label">Verified Facts</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid #f59e0b;">
                <div class="metric-val" style="color: #f59e0b;">{results['count_inaccurate']}</div>
                <div class="metric-label">Inaccurate Stats</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid #ef4444;">
                <div class="metric-val" style="color: #ef4444;">{results['count_false']}</div>
                <div class="metric-label">False / Lies</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            score_color = "#10b981" if results['truth_score'] >= 75 else "#f59e0b" if results['truth_score'] >= 45 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {score_color};">
                <div class="metric-val" style="color: {score_color};">{results['truth_score']}%</div>
                <div class="metric-label">Truth Score</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Filter Tabs
        tab_all, tab_false, tab_inaccurate, tab_verified = st.tabs([
            f"All Claims ({results['total_claims']})",
            f"🔴 False / Fabricated ({results['count_false']})",
            f"🟡 Inaccurate / Outdated ({results['count_inaccurate']})",
            f"🟢 Verified ({results['count_verified']})"
        ])

        def render_claim_card(claim):
            status = claim["status"]
            if status == "VERIFIED":
                badge_html = '<span class="badge-verified">✓ VERIFIED</span>'
                card_border = "#059669"
            elif status == "INACCURATE":
                badge_html = '<span class="badge-inaccurate">⚠️ INACCURATE (OUTDATED STAT)</span>'
                card_border = "#d97706"
            else:
                badge_html = '<span class="badge-false">✕ FALSE / FABRICATED</span>'
                card_border = "#dc2626"

            with st.container():
                st.markdown(f"""
                <div class="claim-card" style="border-left: 4px solid {card_border};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            {badge_html}
                            <span style="color: #94a3b8; font-size: 12px; margin-left: 8px;"><b>{claim['id']}</b> • Page {claim['page']} • {claim['type']}</span>
                        </div>
                    </div>
                    <div class="claim-quote">"{claim['claim_text']}"</div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><b>Verification Diagnosis:</b> {claim['explanation']}</div>
                    <div class="real-fact-box">
                        <div class="real-fact-title">Verified Truth & Current Reality:</div>
                        <div class="real-fact-text">{claim['real_fact']}</div>
                    </div>
                    <div style="margin-top: 10px; font-size: 12px; color: #94a3b8;">
                        <b>Official Evidence Source:</b> <a href="{claim['source_url']}" target="_blank" style="color: #60a5fa; text-decoration: underline;">{claim['source_name']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tab_all:
            for c in results["claims"]:
                render_claim_card(c)

        with tab_false:
            false_claims = [c for c in results["claims"] if c["status"] == "FALSE"]
            if false_claims:
                for c in false_claims:
                    render_claim_card(c)
            else:
                st.info("No false or fabricated claims detected in this document.")

        with tab_inaccurate:
            inaccurate_claims = [c for c in results["claims"] if c["status"] == "INACCURATE"]
            if inaccurate_claims:
                for c in inaccurate_claims:
                    render_claim_card(c)
            else:
                st.info("No outdated or inaccurate statistics detected.")

        with tab_verified:
            verified_claims = [c for c in results["claims"] if c["status"] == "VERIFIED"]
            if verified_claims:
                for c in verified_claims:
                    render_claim_card(c)
            else:
                st.info("No verified claims found.")

        # Export Options
        st.divider()
        st.subheader("📥 Export Audit Deliverables")
        
        col_d1, col_d2 = st.columns(2)
        
        # CSV Export
        df_export = pd.DataFrame(results["claims"])
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        
        with col_d1:
            st.download_button(
                label="📊 Download Fact-Check Report (CSV)",
                data=csv_data,
                file_name=f"factcheck_report_{doc_label}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # JSON Export
        json_data = json.dumps(results, indent=2).encode('utf-8')
        with col_d2:
            st.download_button(
                label="📄 Download Full Audit Schema (JSON)",
                data=json_data,
                file_name=f"factcheck_report_{doc_label}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    # Empty State with Instructions
    st.info("👆 Please upload a PDF document above or click **'⚡ Run Fact-Check on Trap Document'** in the left sidebar to see TruthLayer in action!")
    
    st.markdown("""
    ### How It Works:
    - **1. Extraction:** Mines quantitative claims, metrics, percentages, dollar figures, and dates using regex & natural language parsing.
    - **2. Verification:** Automatically searches the live web and cross-references authoritative consensus registries.
    - **3. Reporting:** Categorizes every statement into:
        - 🟢 **VERIFIED:** Matches live verified real-world data.
        - 🟡 **INACCURATE:** Flags outdated figures (e.g. 2017 numbers quoted as 2024) and provides the current accurate metric.
        - 🔴 **FALSE:** Flags fabricated claims, hallucinations, and refutes them with real facts.
    """)
