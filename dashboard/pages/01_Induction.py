import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.markdown(
    """
    <!-- Load Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Cascadia+Code&display=swap" rel="stylesheet">

    <style>
    /* --- Page Background --- */
    .stApp {
        background-color: #001F3F !important;  /* Navy Blue */
    }

    /* --- Main Headers (h1, h2, h3) --- */
    h1, h2, h3 {
        font-family: 'Cascadia Code', monospace !important;
        font-weight: 700 !important;
        color: #FFD700 !important;  /* Gold headers */
        font-size: 36px !important; /* Larger for main headers */
        line-height: 1.2 !important;
        margin-bottom: 12px !important;
    }

    /* --- Instruction / text above sliders --- */
    .stText, .stMarkdown {
        font-family: 'Cascadia Code', monospace !important;
        color: #FFFFFF !important;
        font-size: 16px !important;  /* Slightly bigger than normal body */
        line-height: 1.3 !important;
        margin-bottom: 8px !important;
    }

    /* --- Buttons --- */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: #001F3F !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-family: 'Cascadia Code', monospace !important;
    }

    /* --- Sliders (FULL YELLOW) --- */
    div.stSlider > div > div > div {
        background-color: #FFFF00 !important;  /* Track */
        height: 8px !important;
        border-radius: 4px !important;
    }
    div.stSlider > div > div > span {
        background-color: #FFFF00 !important;  /* Thumb */
        border: 2px solid #FFA500 !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* --- Table Headers & Cells --- */
    .css-1lcbmhc.e1tzin5v3 {  /* Header */
        background-color: #001F3F !important;
        color: #FFD700 !important;
        font-weight: bold !important;
        font-family: 'Cascadia Code', monospace !important;
        font-size: 15px !important;
    }
    .css-1v0mbdj.e1tzin5v2 {  /* Cells */
        color: #FFFFFF !important;
        font-family: 'Cascadia Code', monospace !important;
        font-size: 14px !important;
        padding: 6px 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Induction Planner", page_icon="🚇", layout="wide")

# --- Sidebar (minimal for navigation) ---
st.sidebar.title("🚇 KMRL Induction Planner")
st.sidebar.markdown("📊 Home | 📝 Induction")

# --- Page Header ---
st.title("Induction Planner 🚇")
st.markdown("Run the planner, filter results, export CSV and preview the input data.")

# --- Controls (all sliders in top columns) ---
col1, col2, col3, col4 = st.columns([2,2,2,2])
with col1:
    required_service = st.slider("Required service rakes", min_value=1, max_value=25, value=2)
with col2:
    max_mileage = st.slider(
        "Max mileage before service (km)", min_value=1000, max_value=20000, step=500, value=8000
    )
with col3:
    max_cleaning_slots = st.slider(
        "Max cleaning slots", min_value=1, max_value=10, value=2
    )
with col4:
    branding_hours = st.slider(
        "Branding exposure hours", min_value=0, max_value=24, value=4
    )

run_btn = st.button("Run Plan")

# --- Session State ---
if "plan_df" not in st.session_state:
    st.session_state.plan_df = pd.DataFrame()

# --- Run backend plan ---
if run_btn:
    try:
        res = requests.get(
            f"http://127.0.0.1:8000/plan/run?required_service={required_service}&max_mileage={max_mileage}&max_cleaning_slots={max_cleaning_slots}",
            timeout=15,
        )
        res.raise_for_status()
        payload = res.json()

        if "error" in payload:
            st.error(f"Backend error: {payload['error']}")
            df = pd.DataFrame()
        else:
            plan_list = payload.get("plan", [])
            if isinstance(plan_list, dict):
                plan_list = [plan_list]
            df = pd.DataFrame(plan_list)

            # Rename ML columns
            if "ml_risk_score" in df.columns:
                df.rename(columns={"ml_risk_score": "AI Risk Score"}, inplace=True)
            if "ml_recommendation" in df.columns:
                df.rename(columns={"ml_recommendation": "AI Recommendation"}, inplace=True)

            # Ensure numeric for bar chart
            if "Rakes Assigned" in df.columns:
                df["Rakes Assigned"] = pd.to_numeric(df["Rakes Assigned"], errors="coerce").fillna(0)

            st.session_state.plan_df = df
            st.success("Plan computed ✅")

    except Exception as e:
        st.session_state.plan_df = pd.DataFrame()
        st.error(f"Failed to get plan: {e}")

df = st.session_state.plan_df.copy()

# --- Table & Search ---
if not df.empty:
    # Status emojis
    status_col = "status" if "status" in df.columns else df.columns[-1]
    df[status_col] = df[status_col].apply(lambda x: str(x) if not pd.isna(x) else "")
    emoji = {"Service": "🟢 Service", "Standby": "🟡 Standby", "IBL": "🔴 IBL"}
    df["status_display"] = df[status_col].map(emoji).fillna(df[status_col])

    # Search filter
    if train_search := st.text_input("Search train ID or keyword", placeholder="e.g. T01 or BR-44"):
        mask = df.astype(str).apply(lambda col: col.str.contains(train_search, case=False, na=False)).any(axis=1)
        df = df[mask]

    cols = ["train_id", "status_display"] + [c for c in df.columns if c not in ("train_id", status_col, "status_display")]
    cols = [c for c in cols if c in df.columns]

    st.markdown("### Plan Results")
    st.dataframe(df[cols].rename(columns={"status_display": "status"}), use_container_width=True)

    csv = df.drop(columns=["status_display"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("Export plan CSV", csv, file_name="induction_plan.csv", mime="text/csv")

    # --- Pie chart ---
    st.markdown("### Service Status Distribution")
    if "status" in df.columns:
        pie_data = df["status"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90, colors=["green", "orange", "red"])
        ax1.axis("equal")
        st.pyplot(fig1)


else:
    st.info("No plan yet — choose required service and click **Run Plan**")

# --- CSV Data Previews ---
st.markdown("---")
st.markdown("### CSV Data Previews")
num_rows = st.slider("Number of rows to preview per CSV", min_value=5, max_value=50, value=10, step=1)

files = ["fitness.csv", "jobcards.csv", "branding.csv", "mileage.csv", "cleaning.csv", "stabling.csv"]
tabs = st.tabs([f.split(".")[0].capitalize() for f in files])

for i, f in enumerate(files):
    with tabs[i]:
        try:
            r = requests.get(f"http://127.0.0.1:8000/ingest/{f}", timeout=5)
            if r.status_code == 200:
                d = r.json()
                st.write(f"**{f}** — rows: {d.get('rows', '?')}, columns: {d.get('columns', [])}")
                preview = d.get("preview", [])
                if preview:
                    df_preview = pd.DataFrame(preview).head(num_rows)
                    st.dataframe(df_preview)
                    st.write(f"_Showing first {num_rows} rows of {d.get('rows', '?')}_")
                else:
                    st.write("_Preview not available_")
            else:
                st.write(f"**{f}** — error: {r.text}")
        except Exception as e:
            st.write(f"**{f}** — failed: {e}")
