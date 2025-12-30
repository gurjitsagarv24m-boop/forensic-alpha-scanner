import streamlit as st
import pandas as pd

from utils.forensic_scores import (
    beneish_m_score_series,
    sloan_accrual_series,
    piotroski_f_score_series,
    altman_z_score_series
)

from utils.forensic_alpha import forensic_alpha
from utils.alpha_ai_advisor import ai_alpha_recommendation


# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Forensic Alpha Scanner",
    layout="wide"
)

st.title("🔍 Forensic Alpha Scanner")
st.caption("Forensic accounting–driven alpha with AI-assisted interpretation")


# -------------------------------------------------
# Session state
# -------------------------------------------------
for key in ["raw_df", "pivot", "confirmed"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "confirmed" else False


# -------------------------------------------------
# Tabs
# -------------------------------------------------
tabs = st.tabs([
    "📥 Data Input & Validation",
    "🧪 Forensic Scores",
    "📈 Forensic Alpha & AI View",
    "⚙️ Engine Output"
])


# =================================================
# TAB 1 — DATA INPUT + VALIDATION
# =================================================
with tabs[0]:
    st.header("📥 Upload & Validate Financial Data")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel (multi-year format)",
        type=["csv", "xlsx"]
    )

    if uploaded_file:
        df = (
            pd.read_csv(uploaded_file)
            if uploaded_file.name.endswith(".csv")
            else pd.read_excel(uploaded_file)
        )

        if not {"Statement", "Item"}.issubset(df.columns):
            st.error("File must contain 'Statement' and 'Item' columns.")
            st.stop()

        st.session_state.raw_df = df
        st.success("File uploaded successfully")

    if st.session_state.raw_df is not None:
        st.subheader("🧾 Review & Edit Financial Statements")

        df = st.session_state.raw_df.copy()
        year_cols = [c for c in df.columns if c not in ["Statement", "Item"]]

        long_df = df.melt(
            id_vars=["Statement", "Item"],
            value_vars=year_cols,
            var_name="year",
            value_name="value"
        )

        long_df["canonical_item"] = (
            long_df["Item"]
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        edited = st.data_editor(
            long_df,
            width="stretch",
            num_rows="fixed"
        )

        # =================================================
        # 🔴 FIXED CONFIRM & CALCULATE BLOCK
        # =================================================
        if st.button("✅ Confirm & Calculate"):
            # 1. Duplicate detection
            dup_count = edited.duplicated(
                subset=["year", "canonical_item"]
            ).sum()

            if dup_count > 0:
                st.warning(
                    f"⚠️ Found {dup_count} duplicate (year, item) entries. "
                    "Using first occurrence."
                )
                edited = edited.drop_duplicates(
                    subset=["year", "canonical_item"],
                    keep="first"
                )

            # 2. Numeric validation
            edited["value"] = pd.to_numeric(
                edited["value"], errors="coerce"
            )

            nan_count = edited["value"].isna().sum()
            if nan_count > 0:
                st.warning(
                    f"⚠️ Found {nan_count} non-numeric values treated as missing."
                )

            # 3. Pivot WITHOUT summation or forced zeros
            pivot = (
                edited
                .pivot_table(
                    index="year",
                    columns="canonical_item",
                    values="value",
                    aggfunc="first"  # ✅ CRITICAL FIX
                )
                .sort_index()
            )

            # 4. Ensure year is numeric if possible
            try:
                pivot.index = pivot.index.astype(int)
            except Exception:
                pass

            st.session_state.pivot = pivot
            st.session_state.confirmed = True

            st.success("✅ Financial data confirmed and structured")

            # 5. Data quality summary
            with st.expander("📊 Data Quality Summary"):
                st.write(f"**Years:** {list(pivot.index)}")
                st.write(f"**Metrics:** {len(pivot.columns)}")
                completeness = (
                    1 - pivot.isna().sum().sum() / pivot.size
                ) * 100
                st.write(f"**Completeness:** {completeness:.1f}%")


# =================================================
# TAB 2 — FORENSIC SCORES
# =================================================
with tabs[1]:
    st.header("🧪 Forensic Accounting Scores")

    if not st.session_state.confirmed:
        st.info("Confirm financial data to view forensic scores.")
    else:
        pivot = st.session_state.pivot

        scores = pd.concat({
            "Beneish M-Score": beneish_m_score_series(pivot),
            "Sloan Accrual": sloan_accrual_series(pivot),
            "Piotroski F-Score": piotroski_f_score_series(pivot),
            "Altman Z-Score": altman_z_score_series(pivot)
        }, axis=1)

        st.dataframe(scores, width="stretch")
        st.line_chart(scores)


# =================================================
# TAB 3 — FORENSIC ALPHA + AI VIEW
# =================================================
with tabs[2]:
    st.header("📈 Forensic Alpha & AI Recommendation")

    if not st.session_state.confirmed:
        st.info("Confirm financial data to compute forensic alpha.")
    else:
        pivot = st.session_state.pivot

        alpha_df = forensic_alpha(
            beneish_m_score_series(pivot),
            sloan_accrual_series(pivot),
            piotroski_f_score_series(pivot),
            altman_z_score_series(pivot)
        )

        st.subheader("🧮 Forensic Alpha by Year")
        st.dataframe(alpha_df, width="stretch")
        st.line_chart(alpha_df["forensic_alpha"])

        st.divider()
        st.subheader("🤖 AI-Assisted Investment View")

        if st.button("Generate AI Recommendation"):
            with st.spinner("Analyzing forensic signals..."):
                ai_view = ai_alpha_recommendation(alpha_df)

            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Recommendation", ai_view["recommendation"])
                st.caption(f"Confidence: {ai_view['confidence']}")
            with col2:
                st.markdown("**Reasoning**")
                st.write(ai_view["reasoning"])


# =================================================
# TAB 4 — ENGINE OUTPUT
# =================================================
with tabs[3]:
    st.header("⚙️ Structured Output (Forensic Engine)")

    if st.session_state.pivot is not None:
        st.json(
            st.session_state.pivot.to_dict(orient="index")
        )
    else:
        st.info("No structured output available yet.")
