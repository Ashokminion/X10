import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

st.set_page_config(
    page_title="Workforce AI | Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8fafc;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    div[data-testid="stMetricValue"] {
        font-weight: 700;
        color: #1e293b;
    }
    
    .stSidebar {
        background-color: #0f172a;
    }
    
    .stSidebar .sidebar-content {
        color: white;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Connection failed to backend: {e}")
        return None

def post_data(endpoint, data=None):
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data or {})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Connection failed to backend: {e}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Workforce AI")
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["Dashboard", "Employee Directory", "Shift Optimization", "Analytics", "HR Chatbot"],
        index=0
    )
    
    st.markdown("---")
    st.info("System Status: **Running**")
    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("🚀 Workforce Intelligence Dashboard")
    st.markdown("Real-time monitoring of blue-collar workforce efficiency and attrition risk.")
    
    stats = fetch_data("dashboard/stats")
    
    if stats:
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Employees", f"{stats['total_employees']:,}", "Active")
        m2.metric("High Risk Attrition", f"{stats['high_risk_employees']}", f"{round(stats['high_risk_employees']/stats['total_employees']*100, 1)}%", delta_color="inverse")
        m3.metric("Avg Weekly Hours", f"{stats['avg_weekly_hours']}", f"{round(stats['avg_weekly_hours']-48, 1)} OT")
        m4.metric("Shift Collapse Score", f"{stats['overall_shift_collapse_score']}", "-2.4", delta_color="inverse")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Attrition Risk Distribution")
            risk_data = stats['attrition_breakdown']
            fig_risk = px.pie(
                values=list(risk_data.values()), 
                names=list(risk_data.keys()),
                color=list(risk_data.keys()),
                color_discrete_map={'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'},
                hole=0.4
            )
            fig_risk.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_risk, use_container_width=True)
            
        with c2:
            st.subheader("Sector Breakdown")
            sectors = stats['sectors']
            sector_names = list(sectors.keys())
            sector_counts = [v['count'] for v in sectors.values()]
            fig_sector = px.bar(
                x=sector_names, 
                y=sector_counts,
                labels={'x': 'Sector', 'y': 'Employee Count'},
                color=sector_names,
                template="plotly_white"
            )
            st.plotly_chart(fig_sector, use_container_width=True)

# --- EMPLOYEE DIRECTORY ---
elif menu == "Employee Directory":
    st.title("👥 Employee Directory")
    
    col1, col2 = st.columns([3, 1])
    search_query = col1.text_input("Search by Name, Code, or Email", placeholder="Ex: Ashok Kumar...")
    company_filter = col2.selectbox("Company", ["All", "Swiggy", "Zomato", "Blinkit", "Zepto", "Amazon India", "Flipkart", "Larsen & Toubro"])
    
    params = f"?search={search_query}" if search_query else "?"
    if company_filter != "All":
        params += f"&company={company_filter}"
    
    emp_data = fetch_data(f"employees{params}")
    
    if emp_data:
        df = pd.DataFrame(emp_data['employees'])
        if not df.empty:
            # Clean up display
            display_df = df[['employee_code', 'full_name', 'company', 'department', 'shift_type', 'attrition_risk', 'performance_score']]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "attrition_risk": st.column_config.SelectboxColumn(
                        "Risk Level",
                        options=["HIGH", "MEDIUM", "LOW"],
                    ),
                    "performance_score": st.column_config.ProgressColumn(
                        "Performance",
                        min_value=0, max_value=100, format="%d"
                    )
                },
                hide_index=True
            )
        else:
            st.warning("No employees found matching filters.")

# --- SHIFT OPTIMIZATION ---
elif menu == "Shift Optimization":
    st.title("⚖️ AI Shift Optimization")
    st.markdown("Automatically reassign high-risk employees to safer shifts to prevent burnout and attrition.")
    
    with st.expander("Optimization Parameters", expanded=True):
        col1, col2 = st.columns(2)
        opt_company = col1.selectbox("Target Company", ["All", "Swiggy", "Zomato", "Blinkit", "Zepto", "Amazon India", "Flipkart", "Larsen & Toubro"], key="opt_co")
        include_med = col2.checkbox("Include Medium Risk Employees", value=False)
        
        if st.button("Run AI Optimization Engine", type="primary"):
            with st.spinner("Analyzing workforce patterns and generating new schedules..."):
                payload = {"include_medium": include_med}
                if opt_company != "All":
                    payload["company"] = opt_company
                
                result = post_data("optimization/reassign-risk", payload)
                
                if result:
                    st.success(f"Successfully reassigned {result['reassigned']} employees!")
                    
                    # Show Improvement
                    r1, r2, r3 = st.columns(3)
                    r1.metric("Before", f"{result['score_before']}", "")
                    r2.metric("After", f"{result['score_after']}", f"-{result['score_improvement']}", delta_color="normal")
                    r3.metric("Retention Potential", "+12%", "projected")
                    
                    if result['changes']:
                        st.subheader("Recent Reassignments")
                        changes_df = pd.DataFrame(result['changes'])
                        st.table(changes_df[['employee_code', 'full_name', 'old_risk', 'new_risk', 'old_shift', 'new_shift']].head(10))

# --- ANALYTICS ---
elif menu == "Analytics":
    st.title("📊 Workforce Analytics")
    
    comp_data = fetch_data("companies/compare/all")
    
    if comp_data:
        df_comp = pd.DataFrame(comp_data['comparison'])
        
        st.subheader("Shift Collapse Risk vs. High Risk %")
        fig_scatter = px.scatter(
            df_comp, 
            x="avg_weekly_hours", 
            y="shift_collapse_score",
            size="total_employees", 
            color="company",
            hover_name="company", 
            text="company",
            labels={'avg_weekly_hours': 'Average Weekly Hours', 'shift_collapse_score': 'Collapse Risk Score'},
            template="plotly_white",
            size_max=60
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.subheader("Company Performance Ranking")
        st.dataframe(df_comp.sort_values("shift_collapse_score"), hide_index=True)

# --- CHATBOT ---
elif menu == "HR Chatbot":
    st.title("🤖 AI HR Assistant")
    st.markdown("Ask questions about employee risks, optimization strategies, or company policies.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Call Chatbot API
                chat_res = post_data("chatbot/query", {"query": prompt, "user_id": "streamlit_user"})
                if chat_res:
                    response = chat_res['response']
                else:
                    response = "I'm sorry, I'm having trouble connecting to the brain center. Please try again later."
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 AI Workforce Intelligence System | Powered by Google Gemini & OR-Tools")
