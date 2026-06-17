import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import os
from dotenv import load_dotenv
import joblib
from google import genai
from google.genai import types
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables
load_dotenv()

# Page configuration with modern styling
st.set_page_config(
    page_title="Cricket Analytics Project",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"  # We'll handle navigation ourselves
)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏆 Best XI Team Builder"

# COMPLETELY NEW SIDEBAR SOLUTION - Always visible custom navigation
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Hide default Streamlit sidebar completely */
    .css-1d391kg, [data-testid="stSidebar"] {
        display: none !important;
    }
    
    
    /* Navigation buttons */
    .nav-section {
        padding: 1.5rem;
    }
    
    .nav-button {
        display: block;
        width: 100%;
        background: rgba(255,255,255,0.05);
        color: white;
        border: 2px solid rgba(50, 205, 50, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        font-size: 1rem;
        font-weight: 500;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        font-family: 'Poppins', sans-serif;
    }
    
    .nav-button:hover {
        background: rgba(50, 205, 50, 0.2);
        border-color: #32CD32;
        transform: translateX(8px);
        box-shadow: 0 4px 12px rgba(50, 205, 50, 0.3);
        color: #90EE90;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #32CD32 0%, #2E8B57 100%);
        border-color: #32CD32;
        color: white;
        font-weight: 600;
        transform: translateX(12px);
        box-shadow: 0 6px 20px rgba(50, 205, 50, 0.4);
    }
    
    .nav-button.active:hover {
        background: linear-gradient(135deg, #90EE90 0%, #32CD32 100%);
    }
    
    /* Stats section in sidebar */
    .sidebar-stats {
        background: rgba(255,255,255,0.05);
        margin: 1.5rem;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(50, 205, 50, 0.3);
    }
    
    .sidebar-stats h4 {
        color: #32CD32;
        text-align: center;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .sidebar-stats p {
        color: rgba(255,255,255,0.8);
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
    }
    
    .sidebar-stats strong {
        color: #90EE90;
    }
    
    /* Adjust main content for custom sidebar */
    .main .block-container {
        margin-left: 340px;
        max-width: calc(100% - 360px);
        padding-left: 2rem;
    }
    
    /* Global Styles */
    .main {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Toggle button for mobile */
    .sidebar-toggle {
        display: none;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 10000;
        background: #2E8B57;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem;
        cursor: pointer;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .sidebar-toggle:hover {
        background: #32CD32;
    }
    
    /* Cricket-themed Header */
    .main-header {
        background: linear-gradient(135deg, #2E8B57 0%, #228B22 25%, #32CD32 50%, #90EE90 75%, #98FB98 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "🏏";
        position: absolute;
        font-size: 120px;
        opacity: 0.1;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    .main-header h1 {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        z-index: 1;
        position: relative;
    }
    
    .main-header p {
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 400;
        z-index: 1;
        position: relative;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 5px solid #32CD32;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        border-left: 5px solid #228B22;
    }
    
    .feature-card::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #32CD32, #90EE90);
        opacity: 0.1;
        border-radius: 50%;
        transform: translate(30px, -30px);
    }
    
    /* Stats Cards */
    .stats-card {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 10px 25px rgba(46, 139, 87, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stats-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 35px rgba(46, 139, 87, 0.4);
    }
    
    .stats-card::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF6347);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Chat Styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 20px;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .user-message {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        margin-left: 15%;
        border-bottom-right-radius: 8px;
        border-top-right-radius: 20px;
    }
    
    .user-message::before {
        content: "👤";
        position: absolute;
        left: -40px;
        top: 50%;
        transform: translateY(-50%);
        background: white;
        padding: 8px;
        border-radius: 50%;
        font-size: 1.2rem;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        color: #1e293b;
        margin-right: 15%;
        border: 2px solid #e2e8f0;
        border-bottom-left-radius: 8px;
        border-top-left-radius: 20px;
    }
    
    .ai-message::before {
        content: "🤖";
        position: absolute;
        right: -40px;
        top: 50%;
        transform: translateY(-50%);
        background: #2E8B57;
        color: white;
        padding: 8px;
        border-radius: 50%;
        font-size: 1.2rem;
    }
    
    /* Form Styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 500;
    }
    
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-family: 'Roboto', sans-serif;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #32CD32;
        box-shadow: 0 0 0 3px rgba(50, 205, 50, 0.1);
        outline: none;
    }
    
    /* Enhanced Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(46, 139, 87, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(46, 139, 87, 0.4);
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
    }
    
    .stButton > button::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Sample Question Buttons */
    .sample-question-btn {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #2E8B57;
        border: 2px solid #32CD32;
        border-radius: 25px;
        padding: 1rem;
        margin: 0.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .sample-question-btn:hover {
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(50, 205, 50, 0.3);
    }
    
    /* Player Card Styling */
    .player-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #32CD32;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .player-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        border-left-color: #2E8B57;
    }
    
    /* Performance Metrics */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-item {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .metric-item:hover {
        border-color: #32CD32;
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(50, 205, 50, 0.1);
    }
    
    /* Data Frame Styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: none;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: 500;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFA726 0%, #FFCC02 100%);
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: 500;
    }
    
    /* Animated Elements */
    @keyframes slideIn {
        from { 
            opacity: 0; 
            transform: translateX(-20px); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0); 
        }
    }
    
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        border: 2px solid #32CD32;
        color: #2E8B57;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        border: 2px solid #e2e8f0;
        border-top: none;
        border-radius: 0 0 12px 12px;
        background: white;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border: 2px dashed #32CD32;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2E8B57 0%, #32CD32 100%);
        border-radius: 10px;
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: #32CD32;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #2E8B57 0%, #1e3a8a 100%);
        color: white;
        text-align: center;
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-top: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: "🏆🏏⚡";
        position: absolute;
        font-size: 80px;
        opacity: 0.1;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        letter-spacing: 30px;
    }
    
    .footer h3 {
        font-size: 2rem;
        margin-bottom: 1rem;
        z-index: 1;
        position: relative;
    }
    
    .footer p {
        z-index: 1;
        position: relative;
        margin: 0.5rem 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .custom-sidebar {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .custom-sidebar.mobile-open {
            transform: translateX(0);
        }
        
        .sidebar-toggle {
            display: block !important;
        }
        
        .main .block-container {
            margin-left: 0;
            max-width: 100%;
            padding-left: 1rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .chat-message {
            margin-left: 5% !important;
            margin-right: 5% !important;
        }
        
        .stat-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)



# Page selection logic 
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 Cricket AI Chatbot", key="nav1", use_container_width=True, 
                 type="primary" if st.session_state.current_page == "🤖 Cricket AI Chatbot" else "secondary"):
        st.session_state.current_page = "🤖 Cricket AI Chatbot"
        st.rerun()

with col2:
    if st.button("💰 Price Predictor", key="nav2", use_container_width=True,
                 type="primary" if st.session_state.current_page == "💰 Price Predictor" else "secondary"):
        st.session_state.current_page = "💰 Price Predictor"
        st.rerun()

with col3:
    if st.button("🏆 Best XI Team Builder", key="nav3", use_container_width=True,
                 type="primary" if st.session_state.current_page == "🏆 Best XI Team Builder" else "secondary"):
        st.session_state.current_page = "🏆 Best XI Team Builder"
        st.rerun()

# Initialize Gemini client
@st.cache_resource
def init_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

# Load price prediction model
@st.cache_resource
def load_price_model():
    try:
        model = joblib.load('ipl_price_model.pkl')
        feature_columns = joblib.load('feature_columns.pkl')
        return model, feature_columns
    except FileNotFoundError as e:
        st.warning(f"⚠️ Model files not found: {e}. Please ensure 'ipl_price_model.pkl' and 'feature_columns.pkl' are in the project directory.")
        return None, None
    except Exception as e:
        st.error(f" Error loading model: {e}")
        return None, None

# Helper functions for feature engineering (from price_predictor.py)
def get_nationality_premium(country):
    country = country.lower()
    if country == 'india':
        return 1.0
    elif country in ['england', 'australia', 'south africa', 'new zealand']:
        return 0.8
    else:
        return 0.6

def get_experience_tier(ipl_matches):
    if ipl_matches == 0:
        return 0
    elif ipl_matches <= 20:
        return 1
    elif ipl_matches <= 50:
        return 2
    else:
        return 3

def get_age_bracket(age):
    if age < 25:
        return 'young_prospect'
    elif age <= 32:
        return 'prime'
    else:
        return 'veteran'

def calculate_batting_impact(ipl_runs, ipl_sr, ipl_avg, t20_runs, t20_sr, t20_avg):
    if ipl_runs > 0:
        ipl_sr = ipl_sr if ipl_sr > 0 else 100
        ipl_avg = ipl_avg if ipl_avg > 0 else 15
        return (ipl_runs ** 0.7) * (ipl_sr / 130) * (ipl_avg / 25)
    elif t20_runs > 0:
        t20_sr = t20_sr if t20_sr > 0 else 100
        t20_avg = t20_avg if t20_avg > 0 else 15
        return (t20_runs ** 0.7) * (t20_sr / 130) * (t20_avg / 25) * 0.6
    else:
        return 0.0

def calculate_bowling_impact(ipl_wkts, ipl_econ, ipl_sr, t20_wkts, t20_econ, t20_sr):
    if ipl_wkts > 0:
        ipl_econ = ipl_econ if ipl_econ > 0 else 8.5
        ipl_sr = ipl_sr if ipl_sr > 0 else 20
        return (ipl_wkts ** 0.7) * (8 / ipl_econ) * (20 / ipl_sr)
    elif t20_wkts > 0:
        t20_econ = t20_econ if t20_econ > 0 else 8.5
        t20_sr = t20_sr if t20_sr > 0 else 20
        return (t20_wkts ** 0.7) * (8 / t20_econ) * (20 / t20_sr) * 0.6
    else:
        return 0.0

def calculate_consistency(ipl_runs, ipl_avg, ipl_sr, ipl_wkts, ipl_econ, ipl_bowl_sr):
    if ipl_runs > 50:
        ipl_avg = ipl_avg if ipl_avg > 0 else 15
        ipl_sr = ipl_sr if ipl_sr > 0 else 100
        return ipl_avg / (ipl_sr / 100)
    elif ipl_wkts > 5:
        ipl_econ = ipl_econ if ipl_econ > 0 else 8.5
        ipl_bowl_sr = ipl_bowl_sr if ipl_bowl_sr > 0 else 20
        return 1 / (ipl_econ * ipl_bowl_sr / 100)
    else:
        return 0.0

def calculate_role_specialization(role, bat_impact, bowl_impact):
    if role == 'batsman':
        return bat_impact * 1.2
    elif role == 'bowler':
        return bowl_impact * 1.2
    elif role == 'batting-allrounder':
        return (bat_impact * 0.7) + (bowl_impact * 0.3)
    elif role == 'bowling-allrounder':
        return (bat_impact * 0.3) + (bowl_impact * 0.7)
    elif role == 'wk-batsman':
        return bat_impact * 1.1 + 10
    else:
        return bat_impact + bowl_impact

def engineer_features(player_data):
    """Engineer all 17 features from player data"""
    
    # Feature 1: Nationality Premium
    nationality_premium = get_nationality_premium(player_data['country'])
    
    # Feature 2: Role Demand Score (simplified - use fixed value)
    role_demand_score = 0.2  # Average value
    
    # Feature 3: Experience Tier
    experience_tier = get_experience_tier(player_data['ipl_matches'])
    
    # Feature 4: International Exposure
    international_exposure = np.log1p(player_data['t20_matches'])
    
    # Feature 5: Uncapped Flag
    uncapped_flag = 1 if (player_data['ipl_runs'] == 0 and player_data['ipl_wickets'] == 0) else 0
    
    # Feature 6: Batting Impact Index
    batting_impact_index = calculate_batting_impact(
        player_data['ipl_runs'], player_data['ipl_sr'], player_data['ipl_avg'],
        player_data['t20_runs'], player_data['t20_sr'], player_data['t20_avg']
    )
    
    # Feature 7: Bowling Impact Index
    bowling_impact_index = calculate_bowling_impact(
        player_data['ipl_wickets'], player_data['ipl_economy'], player_data['ipl_bowl_sr'],
        player_data['t20_wickets'], player_data['t20_economy'], player_data['t20_bowl_sr']
    )
    
    # Feature 8: Consistency Metric
    consistency_metric = calculate_consistency(
        player_data['ipl_runs'], player_data['ipl_avg'], player_data['ipl_sr'],
        player_data['ipl_wickets'], player_data['ipl_economy'], player_data['ipl_bowl_sr']
    )
    
    # Feature 9: Role Specialization Score
    role_specialization_score = calculate_role_specialization(
        player_data['role'], batting_impact_index, bowling_impact_index
    )
    
    # Feature 10: Form Momentum
    form_momentum = batting_impact_index + bowling_impact_index
    
    # Feature 11: Star Player Flag
    star_player_flag = 1 if (player_data['ipl_runs'] > 2000 or 
                             player_data['ipl_wickets'] > 100 or 
                             player_data['t20_matches'] > 50) else 0
    
    # Feature 12: Explosive Factor
    explosive_factor = 1 if (player_data['ipl_sr'] > 150 or 
                             player_data['ipl_sixes'] > 50 or
                             (player_data['ipl_economy'] > 0 and player_data['ipl_economy'] < 7.5)) else 0
    
    # Feature 13: Retention Proxy
    retention_proxy = 1 if player_data['ipl_matches'] > 20 else 0
    
    # Feature 14: Hype Prospect
    hype_prospect = 1 if (uncapped_flag and player_data['age'] < 25 and 
                          (player_data['t20_sr'] > 140 or player_data['t20_wickets'] > 20)) else 0
    
    # Feature 15-17: Age Brackets (one-hot encoded)
    age_bracket = get_age_bracket(player_data['age'])
    age_prime = 1 if age_bracket == 'prime' else 0
    age_veteran = 1 if age_bracket == 'veteran' else 0
    age_young_prospect = 1 if age_bracket == 'young_prospect' else 0
    
    # Return features in correct order
    features = [
        nationality_premium,
        role_demand_score,
        experience_tier,
        international_exposure,
        uncapped_flag,
        batting_impact_index,
        bowling_impact_index,
        consistency_metric,
        role_specialization_score,
        form_momentum,
        star_player_flag,
        explosive_factor,
        retention_proxy,
        hype_prospect,
        age_prime,
        age_veteran,
        age_young_prospect
    ]
    
    return features

# Initialize resources
gemini_client = init_gemini()
model_result = load_price_model()
if model_result[0] is not None:
    price_model, feature_columns = model_result
else:
    price_model, feature_columns = None, None

# Enhanced Main Header
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricket Analytics Pro</h1>
    <p>Advanced AI-Powered Cricket Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CRICKET AI CHATBOT 
# ============================================================================
if st.session_state.current_page == "🤖 Cricket AI Chatbot":
    st.markdown("""
    <div class="feature-card fade-in">
        <h2 style="color: #2E8B57; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            🤖 Cricket AI Chatbot <span style="font-size: 1rem; background: linear-gradient(135deg, #32CD32, #90EE90); color: white; padding: 0.3rem 0.8rem; border-radius: 20px;">Powered by Gemini AI</span>
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">Ask me anything about IPL Auctions, Best XI Teams, Players, Cricket Stats, and Match Analysis!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Function to handle submit
    def handle_submit():
        user_question = st.session_state.user_input.strip()
        if not user_question:
            return

        # Add user message to history
        st.session_state.chat_history.append(("user", user_question))

        with st.spinner("🏏 Cricket AI is analyzing your question..."):
            try:
                if gemini_client:
                    response = gemini_client.models.generate_content(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are a Cricket AI expert with deep knowledge of IPL, international cricket, player statistics, team strategies, and match analysis. "
                                "You ONLY reply to queries about cricket, IPL auctions, players, stats, team formations, match predictions, and cricket strategy. "
                                "If the user asks anything unrelated to cricket, reply politely and shut down the unrelated conversation. "
                                "If it is cricket-related, reply enthusiastically with detailed, insightful explanations including statistics where relevant."
                            )
                        ),
                        contents=user_question
                    )
                    ai_reply = response.text.strip() if response.text else "⚠️ No response from Gemini."
                else:
                    ai_reply = "⚠️ Gemini AI not configured. Please add your GOOGLE_API_KEY to the .env file to unlock full AI capabilities."
            except Exception as e:
                ai_reply = f"⚠️ Error connecting to Cricket AI: {str(e)}"

        # Add AI reply to history
        st.session_state.chat_history.append(("ai", ai_reply))
        st.session_state.user_input = ""

    # Display chat history with enhanced styling
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message"><strong>Cricket AI:</strong> {msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced input section
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input(
            "Ask your cricket question:",
            key="user_input",
            placeholder="e.g., 'Who is Virat Kohli?'",
            on_change=handle_submit,
            help="Press Enter to send your question to Cricket AI"
        )
    
    with col2:
        if st.button("🚀 Send", use_container_width=True):
            handle_submit()

    

# ============================================================================
# PRICE PREDICTOR 
# ============================================================================
elif st.session_state.current_page == "💰 Price Predictor":
    st.markdown("""
    <div class="feature-card fade-in">
        <h2 style="color: #2E8B57; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            💰 IPL Auction Price Predictor <span style="font-size: 1rem; background: linear-gradient(135deg, #FFD700, #FFA500); color: white; padding: 0.3rem 0.8rem; border-radius: 20px;">AI Powered</span>
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">Enter player performance statistics to predict their IPL auction value using advanced machine learning 🚀</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not price_model:
        st.error(" Price prediction model not loaded. Please ensure 'ipl_price_model.pkl' and 'feature_columns.pkl' are available.")
    else:
        # Display model info
        st.info("""
        **🤖 Model:** Ridge Regression | **📊 Dataset:** 236 IPL Players (2024-2025)  
        **⚠️ Accuracy:** 15.7% within ±20% | **Premium Players:** 29-35% accuracy
        """)
        
        # Enhanced input form with IPL + T20I stats
        with st.form("player_form", clear_on_submit=False):
            st.markdown("### 📊 Player Information")
            
            # Basic Info
            col1, col2, col3 = st.columns(3)
            with col1:
                player_name = st.text_input("🏏 Player Name", placeholder="e.g., Virat Kohli")
            with col2:
                country = st.selectbox("🌍 Country", 
                    ['india', 'australia', 'england', 'south africa', 'new zealand', 
                     'west indies', 'pakistan', 'sri lanka', 'bangladesh', 'afghanistan', 'other'])
            with col3:
                age = st.number_input("🎂 Age", min_value=16, max_value=45, value=30)
            
            role = st.selectbox("👤 Role", 
                ['batsman', 'bowler', 'batting-allrounder', 'bowling-allrounder', 'wk-batsman'])
            
            st.markdown("---")
            st.markdown("### 🏏 IPL Performance Stats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Batting**")
                ipl_matches = st.number_input("IPL Matches", min_value=0, max_value=2500, value=0, help="Total IPL matches played")
                ipl_runs = st.number_input("IPL Runs", min_value=0, max_value=10000, value=0)
                ipl_avg = st.number_input("IPL Batting Average", min_value=0.0, max_value=1000.0, value=0.0, step=0.1)
                ipl_sr = st.number_input("IPL Strike Rate", min_value=0.0, max_value=3000.0, value=0.0, step=0.1)
                ipl_sixes = st.number_input("IPL Sixes", min_value=0, max_value=5000, value=0)
            
            with col2:
                st.markdown("**Bowling**")
                ipl_wickets = st.number_input("IPL Wickets", min_value=0, max_value=3000, value=0)
                ipl_economy = st.number_input("IPL Economy", min_value=0.0, max_value=1500.0, value=0.0, step=0.1)
                ipl_bowl_sr = st.number_input("IPL Bowling SR", min_value=0.0, max_value=5000.0, value=0.0, step=0.1)
            
            st.markdown("---")
            st.markdown("### 🌏 T20 International Stats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Batting**")
                t20_matches = st.number_input("T20I Matches", min_value=0, max_value=15000, value=0)
                t20_runs = st.number_input("T20I Runs", min_value=0, max_value=50000, value=0)
                t20_avg = st.number_input("T20I Batting Average", min_value=0.0, max_value=1000.0, value=0.0, step=0.1)
                t20_sr = st.number_input("T20I Strike Rate", min_value=0.0, max_value=3000.0, value=0.0, step=0.1)
            
            with col2:
                st.markdown("**Bowling**")
                t20_wickets = st.number_input("T20I Wickets", min_value=0, max_value=2000, value=0)
                t20_economy = st.number_input("T20I Economy", min_value=0.0, max_value=1500.0, value=0.0, step=0.1)
                t20_bowl_sr = st.number_input("T20I Bowling SR", min_value=0.0, max_value=5000.0, value=0.0, step=0.1)

            submitted = st.form_submit_button("🔮 Predict Auction Price", use_container_width=True)

        # Enhanced prediction results 
        if submitted:
            try:
                # Prepare player data
                player_data = {
                    'country': country,
                    'age': age,
                    'role': role,
                    'ipl_matches': ipl_matches,
                    'ipl_runs': ipl_runs,
                    'ipl_avg': ipl_avg,
                    'ipl_sr': ipl_sr,
                    'ipl_sixes': ipl_sixes,
                    'ipl_wickets': ipl_wickets,
                    'ipl_economy': ipl_economy,
                    'ipl_bowl_sr': ipl_bowl_sr,
                    't20_matches': t20_matches,
                    't20_runs': t20_runs,
                    't20_avg': t20_avg,
                    't20_sr': t20_sr,
                    't20_wickets': t20_wickets,
                    't20_economy': t20_economy,
                    't20_bowl_sr': t20_bowl_sr
                }
                
                # Engineer features
                features = engineer_features(player_data)
                features_array = np.array(features).reshape(1, -1)
                
                # Make prediction
                log_price = price_model.predict(features_array)[0]
                predicted_price = np.expm1(log_price)
                predicted_price = np.clip(predicted_price, 0.2, 30)
                
                # Calculate confidence range (±25%)
                lower_bound = predicted_price * 0.75
                upper_bound = predicted_price * 1.25
                
                # Results display
                st.markdown("---")
                st.markdown("### 🎯 Prediction Results")
                
                # Row 1: Main Metrics (3 columns only)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stat-value">₹{predicted_price:.2f}Cr</div>
                        <div class="stat-label">Predicted Price</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stat-value" style="font-size: 1.3rem;">₹{lower_bound:.2f}-{upper_bound:.2f}Cr</div>
                        <div class="stat-label">Confidence Range (±25%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if predicted_price > 10:
                        category = "💎 Premium Player"
                        color = "#FFD700"
                    elif predicted_price >= 2:
                        category = "⭐ Core Player"
                        color = "#4ECDC4"
                    else:
                        category = "🔧 Base Player"
                        color = "#FF6B6B"
                    
                    st.markdown(f"""
                    <div class="stats-card" style="background: linear-gradient(135deg, {color}22 0%, {color}44 100%);">
                        <div class="stat-value" style="font-size: 1.5rem; color: {color};">{category}</div>
                        <div class="stat-label" style="color: #333;">Player Category</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Row 2: Impact Analysis
                st.markdown("---")
                st.markdown("### 📈 Impact Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%); color: white; border-radius: 15px; box-shadow: 0 8px 20px rgba(46, 139, 87, 0.3);">
                        <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">{features[5]:.2f}</div>
                        <div style="font-size: 1rem; opacity: 0.9; font-weight: 500;">🏏 BATTING IMPACT</div>
                        <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.5rem;">Runs, Strike Rate & Average</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%); color: white; border-radius: 15px; box-shadow: 0 8px 20px rgba(78, 205, 196, 0.3);">
                        <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">{features[6]:.2f}</div>
                        <div style="font-size: 1rem; opacity: 0.9; font-weight: 500;">🎳 BOWLING IMPACT</div>
                        <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.5rem;">Wickets, Economy & Strike Rate</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Row 3: Player Attributes
                st.markdown("---")
                st.markdown("### 🏆 Player Attributes")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    star_badge = " Yes" if features[10] else " No"
                    star_color = "#32CD32" if features[10] else "#FF6B6B"
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1.5rem; background: white; border: 2px solid {star_color}; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{star_badge}</div>
                        <div style="font-size: 0.95rem; color: {star_color}; font-weight: 600;">⭐ STAR PLAYER</div>
                        <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">2000+ runs or 100+ wickets</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    explosive_badge = " Yes" if features[11] else " No"
                    explosive_color = "#FF6347" if features[11] else "#999"
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1.5rem; background: white; border: 2px solid {explosive_color}; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{explosive_badge}</div>
                        <div style="font-size: 0.95rem; color: {explosive_color}; font-weight: 600;">💥 EXPLOSIVE FACTOR</div>
                        <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">SR > 150 or 50+ sixes</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    exp_tier = int(features[2])
                    exp_color = ["#999", "#4ECDC4", "#32CD32", "#FFD700"][exp_tier]
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1.5rem; background: white; border: 2px solid {exp_color}; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        <div style="font-size: 2.5rem; font-weight: 700; color: {exp_color}; margin-bottom: 0.5rem;">{exp_tier}/3</div>
                        <div style="font-size: 0.95rem; color: {exp_color}; font-weight: 600;">📊 EXPERIENCE TIER</div>
                        <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">IPL Matches Played</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    intl_exposure = features[3]
                    intl_color = "#2E8B57" if intl_exposure > 3 else "#4ECDC4" if intl_exposure > 1 else "#999"
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1.5rem; background: white; border: 2px solid {intl_color}; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        <div style="font-size: 2.5rem; font-weight: 700; color: {intl_color}; margin-bottom: 0.5rem;">{intl_exposure:.1f}</div>
                        <div style="font-size: 0.95rem; color: {intl_color}; font-weight: 600;">🌏 INT'L EXPOSURE</div>
                        <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">T20I Experience</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Visualization using Plotly 
                st.markdown("### 📊 Performance Analysis Dashboard")
                
                # Create 2x2 subplot
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Feature Contributions', 'IPL vs T20I Impact', 
                                  'Experience & Form', 'Price Category Gauge'),
                    specs=[[{"type": "bar"}, {"type": "bar"}],
                           [{"type": "scatter"}, {"type": "indicator"}]]
                )
                
                # Chart 1: Top Feature Contributions
                feature_names = ['Batting Impact', 'Bowling Impact', 'Role Spec', 'Form Momentum', 
                               'Consistency', 'Int\'l Exposure']
                feature_values = [features[5], features[6], features[8], features[9], 
                                features[7], features[3]]
                
                fig.add_trace(
                    go.Bar(x=feature_names, y=feature_values,
                          marker_color=['#2E8B57', '#32CD32', '#90EE90', '#98FB98', '#3CB371', '#20B2AA'],
                          name='Features'),
                    row=1, col=1
                )
                
                # Chart 2: IPL vs T20I Impact Comparison
                batting_impact_ipl = calculate_batting_impact(ipl_runs, ipl_sr, ipl_avg, 0, 0, 0)
                batting_impact_t20 = calculate_batting_impact(0, 0, 0, t20_runs, t20_sr, t20_avg)
                bowling_impact_ipl = calculate_bowling_impact(ipl_wickets, ipl_economy, ipl_bowl_sr, 0, 0, 0)
                bowling_impact_t20 = calculate_bowling_impact(0, 0, 0, t20_wickets, t20_economy, t20_bowl_sr)
                
                fig.add_trace(
                    go.Bar(x=['IPL Batting', 'T20I Batting', 'IPL Bowling', 'T20I Bowling'],
                          y=[batting_impact_ipl, batting_impact_t20, bowling_impact_ipl, bowling_impact_t20],
                          marker_color=['#FFD700', '#FFA500', '#4ECDC4', '#45B7D1'],
                          name='Performance'),
                    row=1, col=2
                )
                
                # Chart 3: Experience vs Form Scatter
                fig.add_trace(
                    go.Scatter(x=[features[2]], y=[features[9]], 
                              mode='markers+text',
                              marker=dict(size=predicted_price*10, color='#2E8B57', 
                                        line=dict(width=2, color='white')),
                              text=[player_name or 'Player'],
                              textposition='top center',
                              name=player_name or 'Player'),
                    row=2, col=1
                )
                
                # Add reference lines
                fig.add_hline(y=features[9], line_dash="dash", line_color="gray", 
                            opacity=0.5, row=2, col=1)
                fig.add_vline(x=features[2], line_dash="dash", line_color="gray", 
                            opacity=0.5, row=2, col=1)
                
                # Chart 4: Price Category Gauge
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number+delta",
                        value=predicted_price,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Price (Cr)", 'font': {'size': 16}},
                        delta={'reference': 5, 'increasing': {'color': "#2E8B57"}},
                        gauge={
                            'axis': {'range': [None, 30], 'tickwidth': 1},
                            'bar': {'color': "#2E8B57"},
                            'steps': [
                                {'range': [0, 2], 'color': "#FFE5E5"},
                                {'range': [2, 10], 'color': "#E5F5FF"},
                                {'range': [10, 30], 'color': "#E5FFE5"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': predicted_price
                            }
                        }
                    ),
                    row=2, col=2
                )
                
                # Update layout
                fig.update_xaxes(title_text="Features", row=1, col=1)
                fig.update_yaxes(title_text="Value", row=1, col=1)
                fig.update_xaxes(title_text="Performance Type", row=1, col=2)
                fig.update_yaxes(title_text="Impact Score", row=1, col=2)
                fig.update_xaxes(title_text="Experience Tier (0-3)", row=2, col=1)
                fig.update_yaxes(title_text="Form Momentum", row=2, col=1)
                
                fig.update_layout(
                    height=800, 
                    showlegend=False,
                    title_text=f"Performance Analysis: {player_name or 'Player'}",
                    title_font_size=20
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                
                
                
            except Exception as e:
                st.error(f" Prediction failed: {e}")
                st.exception(e)


# ============================================================================
# BEST XI TEAM BUILDER 
# ============================================================================
elif st.session_state.current_page == "🏆 Best XI Team Builder":
    st.markdown("""
    <div class="feature-card fade-in">
        <h2 style="color: #2E8B57; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            🏆 Best XI Team Builder <span style="font-size: 1rem; background: linear-gradient(135deg, #FF6B6B, #4ECDC4); color: white; padding: 0.3rem 0.8rem; border-radius: 20px;">Optimization Engine</span>
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">Build your optimal cricket team using advanced mathematical optimization algorithms! 🚀</p>
    </div>
    """, unsafe_allow_html=True)

    # Team constraints in main area instead of sidebar
    st.markdown("### ⚙️ Team Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        team_size = st.number_input("👥 Team Size", 0, 30, 11)
        max_overseas = st.slider("🌍 Max Overseas", 0, 10, 4)
        min_batsmen = st.slider("🏏 Min Batsmen", 0, 20, 3)
    
    with col2:
        min_bowlers = st.slider("🎳 Min Bowlers", 0, 20, 3)
        min_allrounders = st.slider("⚡ Min All-Rounders", 0, 20, 2)
        min_wk = st.slider("🧤 Min Wicketkeepers", 0, 20, 1)

    

    # Session state initialization 
    if "players" not in st.session_state:
        st.session_state.players = pd.DataFrame(columns=[
            "player_name", "role", "is_overseas",
            "runs_scored", "innings_batted", "balls_faced", "strike_rate", "fours", "sixes",
            "wickets", "balls_bowled", "runs_conceded", "economy", "dot_balls"
        ])

    # Impact Score function with format-specific formulas
    def compute_impact(df, format_type):
        """Calculate impact score based on format and role."""
        df = df.copy()
        
        # Calculate derived metrics
        df['batting_avg'] = df.apply(
            lambda x: x['runs_scored'] / x['innings_batted'] if x['innings_batted'] > 0 else 0,
            axis=1
        )
        df['bowling_avg'] = df.apply(
            lambda x: x['runs_conceded'] / x['wickets'] if x['wickets'] > 0 else 999,
            axis=1
        )
        df['bowler_sr'] = df.apply(
            lambda x: x['balls_bowled'] / x['wickets'] if x['wickets'] > 0 else 999,
            axis=1
        )
        df['boundary_pct'] = df.apply(
            lambda x: ((x['fours'] + x['sixes']) / x['balls_faced'] * 100) if x['balls_faced'] > 0 else 0,
            axis=1
        )
        df['dot_pct'] = df.apply(
            lambda x: (x['dot_balls'] / x['balls_bowled'] * 100) if x['balls_bowled'] > 0 else 0,
            axis=1
        )
        
        # Initialize impact columns
        df['batting_impact'] = 0.0
        df['bowling_impact'] = 0.0
        
        # Calculate Batting Impact (for Batsman, All-Rounder, Wicketkeeper)
        for idx, row in df.iterrows():
            if row['role'] in ['Batsman', 'All-Rounder', 'Wicketkeeper']:
                if format_type == 'Test':
                    df.loc[idx, 'batting_impact'] = (
                        (row['batting_avg'] * 0.75) +
                        ((row['runs_scored'] / row['innings_batted'] if row['innings_batted'] > 0 else 0) * 0.15) +
                        ((row['strike_rate'] / 2) * 0.10)
                    )
                elif format_type == 'ODI':
                    df.loc[idx, 'batting_impact'] = (
                        np.sqrt(row['batting_avg'] * row['strike_rate']) +
                        (0.5 * row['boundary_pct'])
                    )
                elif format_type == 'T20':
                    df.loc[idx, 'batting_impact'] = (
                        (row['strike_rate'] * 0.7) +
                        (row['batting_avg'] * 0.3) +
                        (0.7 * (row['batting_avg'] + row['strike_rate']))
                    )
        
        # Calculate Bowling Impact (for Bowler, All-Rounder)
        for idx, row in df.iterrows():
            if row['role'] in ['Bowler', 'All-Rounder']:
                if row['wickets'] > 0:
                    if format_type == 'Test':
                        # Prevent division by zero
                        if row['bowling_avg'] > 0 and row['bowler_sr'] > 0:
                            df.loc[idx, 'bowling_impact'] = (
                                (1000 / row['bowling_avg']) +
                                ((100 / row['bowler_sr']) * 2)
                            )
                    else:  # ODI or T20
                        if row['economy'] > 0:
                            df.loc[idx, 'bowling_impact'] = (
                                ((row['dot_pct'] * row['wickets']) / (row['economy'] ** 2)) * 100
                            )
        
        # Total Impact - For All-Rounders, use average
        df['impact'] = df.apply(
            lambda x: (x['batting_impact'] + x['bowling_impact']) / 2 if x['role'] == 'All-Rounder' 
            else x['batting_impact'] + x['bowling_impact'],
            axis=1
        )
        
        return df

    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📋 Player Database Management")
        
        # Format selector
        format_type = st.selectbox(
            "🏏 Cricket Format",
            options=["T20", "ODI", "Test"],
            index=0,
            help="Select format - impact formulas will adjust automatically"
        )
        st.markdown("---")
        
        # File upload 
        uploaded = st.file_uploader(
            "📁 Upload Player Data (CSV)",
            type=["csv"],
            help="Upload a CSV file with player statistics"
        )

        if uploaded:
            df = pd.read_csv(uploaded)
            st.session_state.players = df
            st.success(f" Successfully loaded {len(df)} players from CSV file!")
            
            # Show data preview
            with st.expander("👀 Preview Uploaded Data", expanded=True):
                st.dataframe(df.head(), use_container_width=True)
        
        # Manual player addition with dynamic fields based on role
        with st.expander("➕ Add Individual Player", expanded=len(st.session_state.players) == 0):
            with st.form("add_player_form"):
                st.markdown("**Player Information**")
                
                # Basic info
                form_col1, form_col2 = st.columns(2)
                with form_col1:
                    name = st.text_input("🏏 Player Name", placeholder="e.g., MS Dhoni")
                    role = st.selectbox("👤 Role", ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"])
                with form_col2:
                    overseas = st.checkbox("🌍 Overseas Player")
                
                # Batting fields (Visible for all roles)
                st.markdown("**📊 Batting Statistics**")
                bcol1, bcol2, bcol3 = st.columns(3)
                with bcol1:
                    runs = st.number_input("🏃‍♂️ Runs Scored", 0, 50000, 0)
                    innings = st.number_input("📈 Innings Batted", 0, 1000, 0)
                with bcol2:
                    balls_faced = st.number_input("⚾ Balls Faced", 0, 50000, 0)
                    sr = st.number_input("⚡ Strike Rate", 0.0, 300.0, 0.0)
                with bcol3:
                    fours = st.number_input("4️⃣ Fours", 0, 2000, 0)
                    sixes = st.number_input("6️⃣ Sixes", 0, 2000, 0)
                
                # Bowling fields (Visible for all roles)
                st.markdown("**🎳 Bowling Statistics**")
                bowcol1, bowcol2, bowcol3 = st.columns(3)
                with bowcol1:
                    wkts = st.number_input("🎯 Wickets", 0, 1000, 0)
                    balls_bowled = st.number_input("⚾ Balls Bowled", 0, 5000, 0)
                with bowcol2:
                    runs_conceded = st.number_input("🏃 Runs Conceded", 0, 5000, 0)
                    eco = st.number_input("📊 Economy", 0.0, 200.0, 0.0)
                with bowcol3:
                    dot_balls = st.number_input("⏹️ Dot Balls", 0, 5000, 0)

                if st.form_submit_button(" Add Player", use_container_width=True):
                    if name.strip():
                        new_row = pd.DataFrame([{
                            "player_name": name, "role": role, "is_overseas": 1 if overseas else 0,
                            "runs_scored": runs, "innings_batted": innings, "balls_faced": balls_faced,
                            "strike_rate": sr, "fours": fours, "sixes": sixes,
                            "wickets": wkts, "balls_bowled": balls_bowled, "runs_conceded": runs_conceded,
                            "economy": eco, "dot_balls": dot_balls
                        }])
                        st.session_state.players = pd.concat([st.session_state.players, new_row], ignore_index=True)
                        st.success(f"🎉 Added {name}!")
                        st.rerun()
                    else:
                        st.error(" Please enter a player name!")


    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        # Load ODI Players
        if st.button("📊 Load ODI Players", use_container_width=True, help="Load ODI player data"):
            try:
                import json
                with open('ODI_output.json', 'r') as f:
                    odi_data = json.load(f)
                
                # Map role names to match app format
                role_mapping = {
                    'Batter': 'Batsman',
                    'Allrounder': 'All-Rounder',
                    'Bowler': 'Bowler',
                    'All Rounder': 'All-Rounder'
                }
                
                for player in odi_data:
                    player['role'] = role_mapping.get(player['role'], player['role'])
                
                odi_players = pd.DataFrame(odi_data)
                st.session_state.players = pd.concat([st.session_state.players, odi_players], ignore_index=True)
                st.success(f" Loaded {len(odi_players)} ODI players!")
                st.rerun()
            except FileNotFoundError:
                st.error(" ODI_output.json not found!")
            except Exception as e:
                st.error(f" Error loading ODI data: {e}")
        
        # Load Test Players
        if st.button("🏏 Load Test Players", use_container_width=True, help="Load Test player data"):
            try:
                import json
                with open('test_output.json', 'r') as f:
                    test_data = json.load(f)
                
                # Map role names to match app format
                role_mapping = {
                    'Batsman': 'Batsman',
                    'All Rounder': 'All-Rounder',
                    'Bowler': 'Bowler'
                }
                
                for player in test_data:
                    player['role'] = role_mapping.get(player['role'], player['role'])
                
                test_players = pd.DataFrame(test_data)
                st.session_state.players = pd.concat([st.session_state.players, test_players], ignore_index=True)
                st.success(f" Loaded {len(test_players)} Test players!")
                st.rerun()
            except FileNotFoundError:
                st.error(" test_output.json not found!")
            except Exception as e:
                st.error(f" Error loading Test data: {e}")
        
        
        # Clear database button
        if st.button("🗑️ Clear Database", use_container_width=True, help="Remove all players from database"):
            st.session_state.players = pd.DataFrame(columns=[
                "player_name", "role", "is_overseas",
                "runs_scored", "innings_batted", "balls_faced", "strike_rate", "fours", "sixes",
                "wickets", "balls_bowled", "runs_conceded", "economy", "dot_balls"
            ])
            st.success("🗑️ Player database cleared!")
            st.rerun()
        
        # Database stats
        if not st.session_state.players.empty:
            st.markdown("### 📊 Database Stats")
            total_players = len(st.session_state.players)
            overseas_count = st.session_state.players['is_overseas'].sum()
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Total Players", total_players)
            with col_stat2:
                st.metric("Overseas Players", overseas_count)

    # Enhanced current player pool display
    if not st.session_state.players.empty:
        st.markdown("### 👥 Current Player Pool")
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            role_filter = st.multiselect("Filter by Role", 
                options=st.session_state.players['role'].unique(),
                default=st.session_state.players['role'].unique())
        with col2:
            overseas_filter = st.selectbox("Overseas Filter", 
                ["All Players", "Local Only", "Overseas Only"])
        
        # Apply filters
        filtered_df = st.session_state.players.copy()
        filtered_df = filtered_df[filtered_df['role'].isin(role_filter)]
        
        if overseas_filter == "Local Only":
            filtered_df = filtered_df[filtered_df['is_overseas'] == 0]
        elif overseas_filter == "Overseas Only":
            filtered_df = filtered_df[filtered_df['is_overseas'] == 1]
        
        # Calculate and display impact scores using format-specific formulas
        display_df = compute_impact(filtered_df.copy(), format_type)
        display_df = display_df.sort_values('impact', ascending=False)
        
        st.dataframe(
            display_df[[
                'player_name', 'role', 'batting_impact', 'bowling_impact', 'impact'
            ]],
            use_container_width=True,
            column_config={
                "player_name": "Player",
                "role": "Role",
                "batting_impact": st.column_config.NumberColumn("Batting Impact", format="%.1f"),
                "bowling_impact": st.column_config.NumberColumn("Bowling Impact", format="%.1f"),
                "impact": st.column_config.NumberColumn("Total Impact", format="%.1f")
            }
        )

    # Team selection logic with strategy
    def select_best_team(players_df, format_type):
        players_df = compute_impact(players_df.copy(), format_type)

        prob = LpProblem("BestXI", LpMaximize)
        choices = LpVariable.dicts("select", players_df.index, cat="Binary")

        # Objective: maximize impact
        prob += lpSum(players_df.loc[i, "impact"] * choices[i] for i in players_df.index)

        # Constraints (removed budget constraint)
        prob += lpSum(choices[i] for i in players_df.index) == team_size, "TeamSize"
        prob += lpSum(players_df.loc[i, "is_overseas"] * choices[i] for i in players_df.index) <= max_overseas, "OverseasLimit"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "Batsman") >= min_batsmen, "MinBatsmen"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "Bowler") >= min_bowlers, "MinBowlers"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "All-Rounder") >= min_allrounders, "MinAllRounders"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "Wicketkeeper") >= min_wk, "MinWicketkeepers"

        prob.solve()

        violated = []

        # Check constraint satisfaction
        if prob.status != 1:  # not optimal
            for cname, c in prob.constraints.items():
                if c.value() is not None and c.value() < -1e-6:  # constraint violated
                    violated.append(cname)

        if violated:
            st.error(f" Cannot build a valid team. Violated constraints: {', '.join(violated)}")
            return pd.DataFrame()

        selected = players_df[[choices[i].value() == 1 for i in players_df.index]]
        return selected

    # Team building button
    st.markdown("### 🚀 Team Generation")

    # Single column layout
    col1 = st.container()

    with col1:
        if st.button("🏆 Build Optimal Team", use_container_width=True, type="primary"):
            if st.session_state.players.empty:
                st.error("⚠️ Please add players to your database first!")
            else:
                with st.spinner("🔮 AI is optimizing your dream team..."):
                    best_team = select_best_team(st.session_state.players, format_type)

                if best_team.empty:
                    st.error(" No valid team found with current constraints. Please adjust your requirements.")
                else:
                    st.balloons()  # Celebration effect
                    st.success("🎉 Your optimal team has been assembled!")
                    st.info(f"🏏 Team optimized for **{format_type}** format using format-specific impact formulas")

                    # Team metrics
                    total_impact = best_team["impact"].sum()
                    overseas_count = best_team["is_overseas"].sum()
                    avg_sr = best_team[best_team["strike_rate"] > 0]["strike_rate"].mean()
                    
                    # Team summary cards
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{len(best_team)}</div>
                            <div class="stat-label">Players</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{total_impact:.0f}</div>
                            <div class="stat-label">Team Impact</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{overseas_count}/{max_overseas}</div>
                            <div class="stat-label">Overseas Quota</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{avg_sr:.1f}</div>
                            <div class="stat-label">Avg Strike Rate</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Team composition table 
                    st.markdown("### 🏏 Your Dream Team XI")
                    team_display = best_team.copy()
                    team_display['Captain Potential'] = team_display.apply(
                        lambda x: '⭐ Captain' if x['impact'] == team_display['impact'].max() else '👤 Player', axis=1
                    )
                    
                    st.dataframe(
                        team_display[['player_name', 'role', 'batting_impact', 'bowling_impact', 'impact', 'Captain Potential']],
                        use_container_width=True,
                        column_config={
                            "player_name": "🏏 Player",
                            "role": "👤 Role",
                            "batting_impact": st.column_config.NumberColumn("🏏 Batting Impact", format="%.1f"),
                            "bowling_impact": st.column_config.NumberColumn("🎳 Bowling Impact", format="%.1f"),
                            "impact": st.column_config.NumberColumn("🔥 Total Impact", format="%.1f"),
                            "Captain Potential": "🎖️ Role"
                        }
                    )


                    # Analytics with Plotly
                    st.markdown("### 📊 Team Analytics Dashboard")
                    
                    # Create comprehensive subplot
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=(
                            'Role Distribution', 
                            'Batting vs Bowling Impact', 
                            'Player Performance Radar',
                            'Impact Distribution'
                        ),
                        specs=[
                            [{"type": "pie"}, {"type": "scatter"}],
                            [{"type": "scatterpolar"}, {"type": "bar"}]
                        ]
                    )
                    
                    # Role distribution pie chart
                    role_counts = best_team["role"].value_counts()
                    fig.add_trace(
                        go.Pie(
                            labels=role_counts.index, 
                            values=role_counts.values,
                            marker_colors=['#2E8B57', '#32CD32', '#90EE90', '#98FB98']
                        ),
                        row=1, col=1
                    )
                    
                    # Batting vs Bowling Impact scatter
                    fig.add_trace(
                        go.Scatter(
                            x=best_team["batting_impact"], 
                            y=best_team["bowling_impact"],
                            mode='markers+text',
                            text=best_team["player_name"],
                            textposition="top center",
                            marker=dict(
                                size=15,
                                color=best_team["is_overseas"],
                                colorscale=['#2E8B57', '#FF6B6B'],
                                showscale=True,
                                colorbar=dict(title="Overseas")
                            ),
                            name="Players"
                        ),
                        row=1, col=2
                    )
                    
                    best_team["impact"] = pd.to_numeric(best_team["impact"], errors="coerce")

                    # Performance radar for top 3 players
                    top_players = best_team.nlargest(3, 'impact')

                    # Performance radar for top 3 players
                    top_players = best_team.nlargest(3, 'impact')
                    categories = ['Runs', 'Strike Rate', 'Wickets', 'Economy']
                    
                    for _, player in top_players.iterrows():
                        values = [
                            player['runs_scored']/10,  # Normalize
                            player['strike_rate']/2,
                            player['wickets']*5,
                            max(0, 50 - player['economy']*5)
                        ]
                        
                        fig.add_trace(
                            go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill='toself',
                                name=player['player_name']
                            ),
                            row=2, col=1
                        )
                    
                    fig.update_layout(height=800, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    
                    
                    # Download CSV
                    enhanced_csv = best_team.copy()
                    enhanced_csv['selection_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    csv_data = enhanced_csv.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download Team Sheet", 
                        data=csv_data, 
                        file_name=f"best_xi_team.csv", 
                        mime="text/csv", 
                        use_container_width=True
                    )


# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3>🏏 Cricket Analytics Pro</h3>
    <p><strong>The Ultimate AI-Powered Cricket Intelligence Platform</strong></p>
    <p>🤖 Advanced AI Analysis • 💰 Smart Price Predictions • 🏆 Optimal Team Building</p>
    <p><em>Empowering cricket decisions with cutting-edge technology</em></p>
    <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
        <p>Built with ❤️ from Vedant • Powered by Gemini AI • Optimized with PuLP</p>
    </div>
</div>
""", unsafe_allow_html=True)
