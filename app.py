import streamlit as st
from ingest.document_loader import load_documents, load_uploaded_documents, chunk_documents
from retrieval.embedder import embed_chunks
from retrieval.vectorstore import QdrantVectorStore
from generation.llm_wrapper import generate_answer
from utils.logger import get_logger
from utils.timer import Timer
import config
import os
import time
import psutil
from streamlit_lottie import st_lottie
import requests
import json
from datetime import datetime
import base64

# Initialize logger
logger = get_logger()

# Page configuration
st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chat message display function
def display_chat_message(message, is_user=False):
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="avatar user-avatar">👤</div>
            <div class="message-content user-content">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message ai-message">
            <div class="avatar ai-avatar">🤖</div>
            <div class="message-content ai-content">{message}</div>
        </div>
        """, unsafe_allow_html=True)

# Initialize session state first
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'documents_processed' not in st.session_state:
    st.session_state.documents_processed = False
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'show_intro' not in st.session_state:
    st.session_state.show_intro = True

# Add CSS styles with theme support
if st.session_state.theme == "dark":
    css_theme = """
    <style>
    /* Dark theme - Modern & Elegant */
    body {
        background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e, #0f3460) !important;
        color: #ffffff !important;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e, #0f3460) !important;
        color: #ffffff !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e, #0f3460) !important;
    }
    
    /* Main content area styling for dark theme */
    .main .block-container {
        background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e, #0f3460) !important;
        color: #ffffff !important;
    }
    
    /* Headers in dark theme */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Text elements in dark theme */
    p, div, span {
        color: #ffffff !important;
    }
    
    /* Status indicators in dark theme */
    .status-indicator {
        background: rgba(45, 55, 72, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
        color: #ffffff !important;
    }
    
    /* Info boxes and alerts in dark theme */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(45, 55, 72, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
    }
    
    /* Streamlit info boxes */
    .element-container .stAlert {
        background: rgba(45, 55, 72, 0.8) !important;
        color: #ffffff !important;
    }
    
    /* Any remaining white backgrounds */
    .stMarkdown, .stText {
        color: #ffffff !important;
    }
    
    /* Force all main content to dark theme */
    .main .block-container > div {
        background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e, #0f3460) !important;
        color: #ffffff !important;
    }
    
    /* Force all Streamlit elements to dark theme */
    .stMarkdown, .stText, .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* Force all divs in main content to dark theme */
    .main div {
        color: #ffffff !important;
    }
    
    /* Footer styling for dark theme */
    .footer {
        color: #ffffff !important;
        background: rgba(45, 55, 72, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 20px 0 !important;
    }
    
    /* Custom scrollbar for dark theme */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    .chat-message {
        display: flex;
        margin: 20px 0;
        align-items: flex-start;
        transition: all 0.3s ease;
    }
    
    .chat-message:hover {
        transform: translateY(-3px);
    }
    
    .user-message {
        flex-direction: row-reverse;
    }
    
    .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin: 0 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .avatar:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    .ai-avatar {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }
    
    .message-content {
        padding: 20px 25px;
        border-radius: 25px;
        max-width: 75%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .message-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(120deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.05) 38%, rgba(255,255,255,0.05) 40%, rgba(255,255,255,0) 48%);
        background-size: 200% 100%;
        background-position: 100% 0;
        transition: background-position 0.5s ease-in-out;
    }
    
    .message-content:hover::before {
        background-position: -100% 0;
    }
    
    .user-content {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        border-top-right-radius: 5px;
    }
    
    .ai-content {
        background: linear-gradient(135deg, #2d3748, #4a5568);
        color: #f7fafc;
        border-top-left-radius: 5px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 12px 25px !important;
        font-weight: bold !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Dark theme form elements */
    .stSelectbox > div > div {
        background: rgba(45, 55, 72, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(45, 55, 72, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    
    .stChatInput > div > div > textarea {
        background: rgba(45, 55, 72, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
    }
    
    /* Enhanced Sidebar styling for dark theme */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15, 15, 35, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 5px 0 25px rgba(0,0,0,0.3) !important;
    }
    
    /* Sidebar content styling for dark theme */
    .css-1d391kg .stMarkdown, .css-1d391kg .stHeader {
        color: #ffffff !important;
    }
    
    /* Ensure all sidebar text is white in dark theme */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: #ffffff !important;
    }
    
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span, .css-1d391kg strong, .css-1d391kg em {
        color: #ffffff !important;
    }
    
    .css-1d391kg .stMarkdown * {
        color: #ffffff !important;
    }
    
    .css-1d391kg .stText, .css-1d391kg .stMarkdown, .css-1d391kg .stAlert, .css-1d391kg .stInfo, .css-1d391kg .stSuccess, .css-1d391kg .stWarning, .css-1d391kg .stError {
        color: #ffffff !important;
    }
    
    /* File uploader text in dark theme */
    .css-1d391kg .stFileUploader > div > div > div > div {
        color: #ffffff !important;
    }
    
    .css-1d391kg .stFileUploader > div > div > div > div > div {
        color: #ffffff !important;
    }
    
    /* Progress bar text in dark theme */
    .css-1d391kg .stProgress > div > div > div > div {
        color: #ffffff !important;
    }
    
    /* All Streamlit elements in sidebar for dark theme */
    .css-1d391kg * {
        color: #ffffff !important;
    }
    
    /* Force all sidebar text to be white in dark theme - more specific */
    .css-1d391kg div, .css-1d391kg p, .css-1d391kg span, .css-1d391kg strong, .css-1d391kg em, .css-1d391kg label {
        color: #ffffff !important;
    }
    
    .css-1d391kg .stMarkdown div, .css-1d391kg .stMarkdown p, .css-1d391kg .stMarkdown span, .css-1d391kg .stMarkdown strong, .css-1d391kg .stMarkdown em {
        color: #ffffff !important;
    }
    
    .css-1d391kg .stText div, .css-1d391kg .stText p, .css-1d391kg .stText span, .css-1d391kg .stText strong, .css-1d391kg .stText em {
        color: #ffffff !important;
    }
    
    /* Override any remaining text elements */
    .css-1d391kg [class*="st"] {
        color: #ffffff !important;
    }
    
    .css-1d391kg [class*="st"] * {
        color: #ffffff !important;
    }
    
    /* Nuclear option - force all text in sidebar to be white */
    .css-1d391kg, .css-1d391kg *, .css-1d391kg *::before, .css-1d391kg *::after {
        color: #ffffff !important;
    }
    
    /* Target specific Streamlit sidebar elements */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] strong, [data-testid="stSidebar"] em, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Enhanced sidebar buttons for dark theme */
    .css-1d391kg .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        margin: 5px 0 !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Disabled buttons in sidebar for dark theme */
    .css-1d391kg .stButton > button:disabled {
        background: rgba(255,255,255,0.1) !important;
        color: rgba(255,255,255,0.5) !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }
    
    /* Enhanced file uploader in sidebar for dark theme */
    .css-1d391kg .stFileUploader > div {
        background: rgba(45, 55, 72, 0.6) !important;
        border: 2px dashed rgba(255,255,255,0.3) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        transition: all 0.3s ease !important;
    }
    
    .css-1d391kg .stFileUploader > div:hover {
        border-color: rgba(255,255,255,0.5) !important;
        background: rgba(45, 55, 72, 0.8) !important;
    }
    
    /* Progress bar styling for dark theme */
    .css-1d391kg .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Metric styling for dark theme */
    .css-1d391kg .stMetric {
        background: rgba(45, 55, 72, 0.3) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Theme toggle switch for dark theme */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        max-width: 120px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    </style>
    """
else:
    css_theme = """
    <style>
    /* Light theme - Clean & Modern (like Askk AI) */
    body {
        background: #ffffff !important;
        color: #333333 !important;
    }
    
    .main {
        background: #ffffff !important;
    }
    
    .stApp {
        background: #ffffff !important;
    }
    
    /* Custom scrollbar for light theme */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    .chat-message {
        display: flex;
        margin: 20px 0;
        align-items: flex-start;
        transition: all 0.3s ease;
    }
    
    .chat-message:hover {
        transform: translateY(-3px);
    }
    
    .user-message {
        flex-direction: row-reverse;
    }
    
    .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin: 0 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        border: 2px solid rgba(255,255,255,0.8);
    }
    
    .avatar:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    .ai-avatar {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }
    
    .message-content {
        padding: 20px 25px;
        border-radius: 25px;
        max-width: 75%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .message-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(120deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.3) 38%, rgba(255,255,255,0.3) 40%, rgba(255,255,255,0) 48%);
        background-size: 200% 100%;
        background-position: 100% 0;
        transition: background-position 0.5s ease-in-out;
    }
    
    .message-content:hover::before {
        background-position: -100% 0;
    }
    
    .user-content {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-top-right-radius: 5px;
    }
    
    .ai-content {
        background: #f8f9fa !important;
        color: #333333 !important;
        border: 1px solid #e9ecef !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    .user-content {
        background: #007bff !important;
        color: white !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,123,255,0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 12px 25px !important;
        font-weight: bold !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Light theme form elements */
    .stSelectbox > div > div {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    .stChatInput > div > div > textarea {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        padding: 12px !important;
    }
    
    /* Enhanced Sidebar styling for light theme */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-right: 1px solid #e9ecef !important;
        box-shadow: 5px 0 25px rgba(0,0,0,0.1) !important;
    }
    
    /* Ensure sidebar text is always visible in light theme */
    .css-1d391kg, .css-1d391kg * {
        color: #333333 !important;
    }
    
    /* Sidebar headers and labels */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: #333333 !important;
        font-weight: bold !important;
    }
    
    .css-1d391kg label, .css-1d391kg .stTextInput > label, .css-1d391kg .stSelectbox > label {
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar content styling for light theme */
    .css-1d391kg .stMarkdown, .css-1d391kg .stHeader {
        color: #333333 !important;
    }
    
    /* Ensure all text in sidebar is visible in light theme */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: #333333 !important;
    }
    
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span, .css-1d391kg label {
        color: #333333 !important;
    }
    
    .css-1d391kg .stText, .css-1d391kg .stMarkdown {
        color: #333333 !important;
    }
    
    /* Enhanced sidebar buttons for light theme */
    .css-1d391kg .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        margin: 5px 0 !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Disabled buttons in sidebar for light theme */
    .css-1d391kg .stButton > button:disabled {
        background: rgba(0,0,0,0.1) !important;
        color: rgba(0,0,0,0.5) !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }
    
    /* Enhanced file uploader in sidebar for light theme */
    .css-1d391kg .stFileUploader > div {
        background: rgba(248, 249, 250, 0.8) !important;
        border: 2px dashed #dee2e6 !important;
        border-radius: 15px !important;
        padding: 25px !important;
        transition: all 0.3s ease !important;
    }
    
    .css-1d391kg .stFileUploader > div:hover {
        border-color: #adb5bd !important;
        background: rgba(248, 249, 250, 1) !important;
    }
    
    /* Progress bar styling for light theme */
    .css-1d391kg .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Progress bar text in light theme */
    .css-1d391kg .stProgress > div > div > div > div {
        color: #333333 !important;
    }
    
    /* File uploader text in light theme */
    .css-1d391kg .stFileUploader > div > div > div {
        color: white !important;
    }
    
    /* All Streamlit text elements in sidebar for light theme */
    .css-1d391kg .stText, .css-1d391kg .stMarkdown, .css-1d391kg .stAlert, .css-1d391kg .stInfo, .css-1d391kg .stSuccess, .css-1d391kg .stWarning, .css-1d391kg .stError {
        color: white !important;
    }
    
    /* Comprehensive sidebar text visibility fix for light theme */
    .css-1d391kg div, .css-1d391kg p, .css-1d391kg span, .css-1d391kg strong, .css-1d391kg em {
        color: white !important;
    }
    
    /* File uploader specific text */
    .css-1d391kg .stFileUploader > div > div > div > div > div {
        color: white !important;
    }
    
    /* Any remaining text elements */
    .css-1d391kg * {
        color: white !important;
    }
    
    /* Metric styling for light theme */
    .css-1d391kg .stMetric {
        background: rgba(248, 249, 250, 0.8) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #e9ecef !important;
    }
    
    /* Ensure all Streamlit elements in sidebar are visible in light theme */
    .css-1d391kg .stAlert, .css-1d391kg .stInfo, .css-1d391kg .stSuccess, .css-1d391kg .stWarning, .css-1d391kg .stError {
        color: #333333 !important;
    }
    
    .css-1d391kg .stProgress > div > div > div > div {
        color: #333333 !important;
    }
    
    .css-1d391kg .stFileUploader > div > div {
        color: #333333 !important;
    }
    
    /* Force all text elements in sidebar to be visible in light theme */
    .css-1d391kg * {
        color: #333333 !important;
    }
    
    .css-1d391kg .stMarkdown * {
        color: #333333 !important;
    }
    
    /* Override any dark theme text colors in light mode */
    .css-1d391kg .stText, .css-1d391kg .stMarkdown, .css-1d391kg div, .css-1d391kg p, .css-1d391kg span {
        color: #333333 !important;
    }
    
    /* Specific overrides for sidebar text elements */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: #333333 !important;
        font-weight: bold !important;
    }
    
    .css-1d391kg label, .css-1d391kg .stTextInput > label {
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* File uploader text */
    .css-1d391kg .stFileUploader > div > div > div > div {
        color: #333333 !important;
    }
    
    /* Progress bar text */
    .css-1d391kg .stProgress > div > div > div > div {
        color: #333333 !important;
    }
    
    /* All Streamlit text components in sidebar */
    .css-1d391kg .stText, .css-1d391kg .stMarkdown, .css-1d391kg .stAlert, .css-1d391kg .stInfo, .css-1d391kg .stSuccess, .css-1d391kg .stWarning, .css-1d391kg .stError {
        color: #333333 !important;
    }
    
    /* Override specific sidebar elements to be white */
    .css-1d391kg .stFileUploader > div > div > div > div {
        color: white !important;
    }
    
    .css-1d391kg .stFileUploader > div > div > div > div > div {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown h3 {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown p {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown strong {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown ul {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown li {
        color: white !important;
    }
    
    .css-1d391kg .stProgress > div > div > div > div {
        color: white !important;
    }
    
    /* Tips section specific styling for light theme */
    .css-1d391kg .stMarkdown div[style*="background: rgba(255, 193, 7, 0.1)"] h4 {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown div[style*="background: rgba(255, 193, 7, 0.1)"] ul {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown div[style*="background: rgba(255, 193, 7, 0.1)"] li {
        color: white !important;
    }
    
    /* General tips section override for light theme */
    .css-1d391kg .stMarkdown div[style*="rgba(255, 193, 7, 0.1)"] * {
        color: white !important;
    }
    
    /* Force ALL sidebar text to be white in light theme */
    .css-1d391kg, .css-1d391kg * {
        color: white !important;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: white !important;
    }
    
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span, .css-1d391kg strong, .css-1d391kg em, .css-1d391kg label {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown * {
        color: white !important;
    }
    
    .css-1d391kg .stText, .css-1d391kg .stMarkdown, .css-1d391kg .stAlert, .css-1d391kg .stInfo, .css-1d391kg .stSuccess, .css-1d391kg .stWarning, .css-1d391kg .stError {
        color: white !important;
    }
    
    .css-1d391kg .stFileUploader > div > div > div > div {
        color: white !important;
    }
    
    .css-1d391kg .stFileUploader > div > div > div > div > div {
        color: white !important;
    }
    
    .css-1d391kg .stProgress > div > div > div > div {
        color: white !important;
    }
    
    /* Nuclear option - force ALL sidebar text to be white */
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] strong, [data-testid="stSidebar"] em, [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 {
        color: white !important;
    }
    
    /* Override any remaining black text in sidebar */
    .css-1d391kg [style*="color: black"], .css-1d391kg [style*="color: #000"], .css-1d391kg [style*="color: #333"] {
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    /* Main content text styling for light theme */
    .main .block-container {
        background: #ffffff !important;
        color: #333333 !important;
    }
    
    /* All text elements in light theme */
    p, div, span, .stMarkdown, .stText {
        color: #333333 !important;
    }
    
    /* Info boxes and alerts in light theme */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        color: #333333 !important;
    }
    
    /* Streamlit info boxes in light theme */
    .element-container .stAlert {
        background: #f8f9fa !important;
        color: #333333 !important;
    }
    
    /* Footer styling for light theme */
    .footer {
        color: #333333 !important;
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 20px 0 !important;
    }
    
    /* Status indicators */
    .status-indicator {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: #f8f9fa !important;
        border: 2px dashed #dee2e6 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* Regular buttons (except theme toggle) */
    .stButton > button:not([key*="toggle"]) {
        background: #007bff !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,123,255,0.2) !important;
    }
    
    .stButton > button:not([key*="toggle"]):hover {
        background: #0056b3 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,123,255,0.3) !important;
    }
    
    /* Theme toggle switch for light theme */
    .stButton > button[key*="toggle"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        max-width: 120px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    .stButton > button[key*="toggle"]:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    </style>
    """

st.markdown(css_theme, unsafe_allow_html=True)

# Intro page
if st.session_state.show_intro:
    # Create a simple, beautiful intro page using Streamlit components
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    ">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🤖 RAG Chat Assistant
        </h1>
        <p style="font-size: 1.5rem; margin-bottom: 3rem; opacity: 0.9;">
            Transform your documents into intelligent conversations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards using columns
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 25px rgba(240, 147, 251, 0.3);
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
            <h3 style="margin-bottom: 0.5rem;">Document Processing</h3>
            <p style="opacity: 0.9; font-size: 0.9rem;">
                Upload PDF, TXT, and DOCX files for instant analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🧠</div>
            <h3 style="margin-bottom: 0.5rem;">AI-Powered Chat</h3>
            <p style="opacity: 0.9; font-size: 0.9rem;">
                Ask questions and get intelligent answers from your documents
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 25px rgba(67, 233, 123, 0.3);
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
            <h3 style="margin-bottom: 0.5rem;">Lightning Fast</h3>
            <p style="opacity: 0.9; font-size: 0.9rem;">
                Powered by Qdrant vector database and Ollama LLM
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get Started button
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", key="start_app_btn", use_container_width=True):
            st.session_state.show_intro = False
            st.rerun()
    
    # Footer
    st.markdown("""
    <div style="
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
    ">
        <p>Built with ❤️ using Streamlit, Qdrant, and Ollama</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Main title
st.title("🤖 RAG Chat Assistant")
st.markdown("Upload documents and chat with your AI assistant!")

# Sidebar
with st.sidebar:
    # Enhanced sidebar header with gradient background
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    ">
        <h2 style="color: white !important; margin: 0; font-size: 1.5rem;">🎨 Settings</h2>
        <p style="color: rgba(255,255,255,0.8) !important; margin: 5px 0 0 0; font-size: 0.9rem;">Customize your experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme toggle with enhanced styling
    st.markdown("### 🌓 Appearance", help="Choose your preferred theme")
    
    # Create a more visually appealing theme toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.theme == "light":
            if st.button("☀️ Light", key="current_light", disabled=True):
                pass
        else:
            if st.button("☀️ Light", key="switch_to_light"):
                st.session_state.theme = "light"
                st.rerun()
    
    with col2:
        if st.session_state.theme == "dark":
            if st.button("🌙 Dark", key="current_dark", disabled=True):
                pass
        else:
            if st.button("🌙 Dark", key="switch_to_dark"):
                st.session_state.theme = "dark"
                st.rerun()
    
    st.markdown("---")
    
    # Document upload section with enhanced styling
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    ">
        <h3 style="color: white !important; margin: 0; font-size: 1.2rem;">📁 Document Upload</h3>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=True,
        help="Upload PDF, TXT, or DOCX files",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        # Enhanced file selection display
        st.markdown(f"""
        <div style="
            background: rgba(76, 175, 80, 0.1);
            border: 2px solid rgba(76, 175, 80, 0.3);
            border-radius: 10px;
            padding: 12px;
            margin: 10px 0;
            text-align: center;
        ">
            <p style="margin: 0; color: #4CAF50; font-weight: bold;">📄 {len(uploaded_files)} file(s) selected</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced process button
        if st.button("🚀 Process Documents", type="primary", use_container_width=True):
            with st.spinner("Processing documents..."):
                try:
                    # Load documents
                    documents = load_uploaded_documents(uploaded_files)
                    st.info(f"📚 Loaded {len(documents)} documents")
                    
                    # Chunk documents
                    chunks = chunk_documents(documents)
                    st.info(f"✂️ Created {len(chunks)} chunks")
                    
                    # Embed chunks
                    embeddings = embed_chunks(chunks)
                    st.info(f"🔢 Generated {len(embeddings)} embeddings")
                    
                    # Store in vector database
                    vectorstore = QdrantVectorStore()
                    vectorstore.reset_collection()
                    vectorstore.add_embeddings(embeddings, chunks)
                    st.session_state.vectorstore = vectorstore
                    st.session_state.documents_processed = True
                    
                    st.success("✅ Documents processed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error processing documents: {str(e)}")
                    logger.error(f"Document processing error: {e}")
    
    st.markdown("---")
    
    # Enhanced system status section
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    ">
        <h3 style="color: white !important; margin: 0; font-size: 1.2rem;">🔧 System Status</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Status indicators with enhanced styling
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        # Check Qdrant
        try:
            import requests
            response = requests.get("http://localhost:6333/", timeout=5)
            if response.status_code == 200:
                st.markdown("""
                <div style="
                    background: rgba(76, 175, 80, 0.1);
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    border-radius: 8px;
                    padding: 8px;
                    text-align: center;
                    margin: 5px 0;
                ">
                    <p style="margin: 0; color: #4CAF50; font-size: 0.8rem;">✅ Qdrant</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: rgba(244, 67, 54, 0.1);
                    border: 1px solid rgba(244, 67, 54, 0.3);
                    border-radius: 8px;
                    padding: 8px;
                    text-align: center;
                    margin: 5px 0;
                ">
                    <p style="margin: 0; color: #F44336; font-size: 0.8rem;">❌ Qdrant</p>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div style="
                background: rgba(244, 67, 54, 0.1);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 8px;
                padding: 8px;
                text-align: center;
                margin: 5px 0;
            ">
                <p style="margin: 0; color: #F44336; font-size: 0.8rem;">❌ Qdrant</p>
            </div>
            """, unsafe_allow_html=True)
    
    with status_col2:
        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                st.markdown("""
                <div style="
                    background: rgba(76, 175, 80, 0.1);
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    border-radius: 8px;
                    padding: 8px;
                    text-align: center;
                    margin: 5px 0;
                ">
                    <p style="margin: 0; color: #4CAF50; font-size: 0.8rem;">✅ Ollama</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: rgba(244, 67, 54, 0.1);
                    border: 1px solid rgba(244, 67, 54, 0.3);
                    border-radius: 8px;
                    padding: 8px;
                    text-align: center;
                    margin: 5px 0;
                ">
                    <p style="margin: 0; color: #F44336; font-size: 0.8rem;">❌ Ollama</p>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div style="
                background: rgba(244, 67, 54, 0.1);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 8px;
                padding: 8px;
                text-align: center;
                margin: 5px 0;
            ">
                <p style="margin: 0; color: #F44336; font-size: 0.8rem;">❌ Ollama</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Clear chat button with enhanced styling
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Add some helpful tips
    st.markdown("---")
    st.markdown("""
    <div style="
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 10px;
        padding: 12px;
        margin: 10px 0;
    ">
        <h4 style="margin: 0 0 8px 0; color: #white !important;">💡 Tips</h4>
        <ul style="margin: 0; padding-left: 20px; font-size: 0.85rem; color: #white !important;">
            <li style="color: #white !important;">Upload multiple documents for better context</li>
            <li style="color: #white !important;">Ask specific questions for better answers</li>
            <li style="color: #white !important;">Use the theme toggle for your preference</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Main chat area
if not st.session_state.documents_processed:
    st.info("📝 Please upload and process documents in the sidebar to start chatting!")
    
    # Show some example questions
    st.subheader("💡 Example questions you can ask:")
    st.markdown("""
    - What are the main topics covered in the documents?
    - Can you summarize the key points?
    - What are the important dates mentioned?
    - Explain the main concepts discussed
    """)
    
    # Footer for non-processed state
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit, Qdrant, and Ollama</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Chat interface
    st.subheader("💬 Chat with your documents")
    
    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message["content"], message["role"] == "user")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_chat_message(prompt, is_user=True)
        
        # Generate response
        with st.spinner("🤖 Thinking..."):
            try:
                # Retrieve relevant documents
                relevant_docs = st.session_state.vectorstore.search(prompt, top_k=5)
                
                # Generate answer
                response = generate_answer(prompt, relevant_docs)
                answer = response["text"] if isinstance(response, dict) else response
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": answer})
                display_chat_message(answer, is_user=False)

                # Display supporting chunks below the answer
                st.markdown("""
                <div style='margin: 1.5em 0 2em 0; padding: 1em; border-radius: 12px; background: rgba(102,126,234,0.07);'>
                <b>🔎 Supporting Chunks:</b>
                <ul style='margin-top: 0.5em;'>
                """, unsafe_allow_html=True)
                for chunk in relevant_docs:
                    st.markdown(f"""
                    <li style='margin-bottom: 0.7em;'>
                        <b>File:</b> {chunk.get('filename', 'N/A')}<br>
                        <b>Page:</b> {chunk.get('page', 'N/A')}<br>
                        <b>Chunk ID:</b> {chunk.get('chunk_id', 'N/A')}<br>
                        <b>Preview:</b> <span style='color:#444;'>{chunk.get('chunk_text', '')[:200]}{'...' if len(chunk.get('chunk_text','')) > 200 else ''}</span>
                    </li>
                    """, unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                display_chat_message(error_msg, is_user=False)
                logger.error(f"Chat error: {e}")
    
    # Add some spacing before footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer for chat state - positioned right after chat input
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px 0;'>
        <p>Built with ❤️ using Streamlit, Qdrant, and Ollama</p>
    </div>
    """, unsafe_allow_html=True)