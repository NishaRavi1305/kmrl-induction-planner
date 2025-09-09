import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="KMRL Induction Planner", page_icon="🚇", layout="wide")

# --- Custom CSS Styling ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Cascadia+Code&display=swap" rel="stylesheet">

    <style>
    /* --- Page Background --- */
    .stApp {
        background-color:  #001F3F !important;  
        padding: 20px !important;
    }

    /* --- Main Header --- */
    h1 {
        font-family: 'Aharoni', sans-serif !important;
        font-weight: 900 !important;
        color: #FFD700 !important;  /* Gold */
        font-size: 44px !important;
        line-height: 1.2 !important;
        margin-bottom: 30px !important;
        text-align: center !important;
    }

    /* --- Body / Description Texts --- */
    .stText, .stMarkdown, p {
        font-family: 'Cascadia Code', monospace !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
        line-height: 1.7 !important;
        margin-bottom: 20px !important;
    }

    /* --- Section Headers --- */
    .stSectionHeader {
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-bottom: 15px !important;
    }

    /* --- Bullets / Lists --- */
    ul {
        margin-left: 20px !important;
        margin-bottom: 20px !important;
        font-size: 18px !important;
    }

    li {
        margin-bottom: 12px !important;
    }

    /* --- Buttons --- */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: #001F3F !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-family: 'Cascadia Code', monospace !important;
        margin-top: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Page Title ---
st.markdown("<h1>AI-Driven Train Induction Planning & Scheduling for Kochi Metro Rail Limited (KMRL) 🚇</h1>", unsafe_allow_html=True)

# --- Welcome Section ---
st.markdown("""
<p class='stText'>
🚆 Welcome to the official <b>AI-Driven Train Induction Planner</b> prototype for Kochi Metro Rail Limited (KMRL).  
This AI-assisted decision support system helps supervisors optimize train rake induction, servicing, and scheduling efficiently.
</p>

<p class='stText'>
🛠️ Track service requirements, cleaning schedules, and maintenance milestones easily.  
Run rule-based checks, analyze dynamic thresholds, and export actionable plans to streamline metro operations.
</p>

<p class='stText'>
👉 Use the <b>Induction Planner</b> page from the sidebar to run the optimizer and view real-time train service planning.
</p>
""", unsafe_allow_html=True)

# --- Six Constraints Section ---
st.markdown("""
<p class='stText stSectionHeader'>
 📌 Key Constraints Addressed by the Prototype:
</p>

<ul>
<li>🟢 <b>Required Service Rakes:</b> Ensure minimum rakes are scheduled for service.</li>
<li>🟡 <b>Max Mileage Before Service:</b> Track trains nearing mileage thresholds.</li>
<li>🟠 <b>Cleaning Slots:</b> Assign trains for cleaning without exceeding available slots.</li>
<li>🔵 <b>Branding Exposure Hours:</b> Manage trains’ exposure for marketing/branding requirements.</li>
<li>⚠️ <b>Jobcard Status:</b> Identify trains with open jobcards preventing service.</li>
<li>📅 <b>Fitness Certificates Expiry:</b> Detect trains with expiring or expired fitness certifications.</li>
</ul>

<p class='stText'>
This prototype provides supervisors a <b>dynamic and interactive dashboard</b> to make informed decisions quickly.  
Filters, search, and CSV export allow for easy monitoring and record-keeping, making daily operations smooth and efficient.
</p>
""", unsafe_allow_html=True)
