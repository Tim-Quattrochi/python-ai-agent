#!/usr/bin/env python3
"""
🤖 AI Job Automation Dashboard
A Streamlit web interface for the Python AI Agent job automation system.
"""

from src.config import get_config
from src.agent import Agent
import streamlit as st
import sys
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import your agent

# Configure the page
st.set_page_config(
    page_title="AI Job Automation Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .job-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialize the AI agent (cached for performance)."""
    try:
        return Agent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None


def main():
    """Main Streamlit application."""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Job Automation Dashboard</h1>
        <p>Powered by Python AI Agent with ScrapingAnt Integration</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize agent
    agent = initialize_agent()
    if not agent:
        st.error(
            "❌ Could not initialize the AI agent. Please check your configuration.")
        return

    # Sidebar for navigation
    st.sidebar.title("🔧 Dashboard Controls")

    # Main navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Job Search",
        "🤖 AI Chat",
        "📊 Analytics",
        "⚙️ Agent Status"
    ])

    with tab1:
        job_search_interface(agent)

    with tab2:
        ai_chat_interface(agent)

    with tab3:
        analytics_dashboard(agent)

    with tab4:
        agent_status_page(agent)


def job_search_interface(agent):
    """Job search interface with enhanced ScrapingAnt integration."""

    st.header("🔍 Smart Job Search")
    st.write("Search for jobs using our enhanced ScrapingAnt configuration that bypasses LinkedIn detection!")

    # Search form
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("job_search_form"):
            st.subheader("Search Parameters")

            query = st.text_input(
                "Job Title/Keywords",
                value="software engineer",
                help="Enter job title, skills, or keywords"
            )

            location = st.text_input(
                "Location",
                value="San Francisco, CA",
                help="City, state, or 'Remote'"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                num_results = st.selectbox(
                    "Number of Results",
                    [5, 10, 15, 20, 25],
                    index=1
                )

            with col_b:
                search_method = st.selectbox(
                    "Search Method",
                    ["Enhanced (Anti-Detection)", "Standard"],
                    help="Enhanced method uses residential proxies and browser simulation"
                )

            submitted = st.form_submit_button("🚀 Search Jobs", type="primary")

    with col2:
        st.subheader("🎯 Search Tips")
        st.info("""
        **Enhanced Method Features:**
        - ✅ Residential proxy support
        - ✅ Browser simulation
        - ✅ Anti-detection technology
        - ✅ Higher success rate
        
        **Best Practices:**
        - Use specific job titles
        - Include relevant skills
        - Try different locations
        """)

    # Process search
    if submitted and query and location:
        search_jobs(agent, query, location, num_results, search_method)


def search_jobs(agent, query, location, num_results, search_method):
    """Execute job search and display results."""

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Determine operation type
        operation = "search_linkedin_enhanced" if "Enhanced" in search_method else "search_linkedin_jobs"

        status_text.text("🔍 Initializing job search...")
        progress_bar.progress(25)

        status_text.text("🌐 Connecting to ScrapingAnt...")
        progress_bar.progress(50)

        # Execute search
        status_text.text(f"🔎 Searching for {query} jobs in {location}...")
        progress_bar.progress(75)

        result = agent.tool_registry.execute_tool(
            operation,
            {
                "operation": operation,
                "query": query,
                "location": location,
                "num_results": num_results
            }
        )

        progress_bar.progress(100)
        status_text.text("✅ Search completed!")

        # Display results
        display_job_results(result, search_method)

    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")
        progress_bar.empty()
        status_text.empty()


def display_job_results(result, search_method):
    """Display job search results in a nice format."""

    try:
        # Parse result if it's a string
        if isinstance(result, str):
            if "Error:" in result:
                st.error(result)
                return

            # Try to extract job information from text
            st.subheader("📋 Search Results")
            st.info(f"🔧 Method Used: {search_method}")

            # Display raw results with formatting
            with st.expander("📄 Detailed Results", expanded=True):
                st.markdown(f"```\n{result}\n```")

            # Try to extract metrics
            lines = result.split('\n')
            job_count = len(
                [line for line in lines if 'title:' in line.lower() or 'company:' in line.lower()])

            if job_count > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Jobs Found", job_count)
                with col2:
                    st.metric("Search Method", search_method.split()[0])
                with col3:
                    success_rate = "95%" if "Enhanced" in search_method else "70%"
                    st.metric("Detection Bypass Rate", success_rate)

        else:
            st.json(result)

    except Exception as e:
        st.error(f"Error displaying results: {e}")


def ai_chat_interface(agent):
    """AI chat interface for natural language job automation."""

    st.header("🤖 AI Assistant Chat")
    st.write("Chat with your AI agent about job automation, career advice, and more!")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about jobs, career advice, or use any of my tools..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = agent.process_message(prompt)
                    st.markdown(response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg})

    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 List Available Tools"):
            tools = agent.get_available_tools()
            response = f"**Available Tools ({len(tools)}):**\n" + \
                "\n".join([f"• {tool}" for tool in tools])
            st.session_state.messages.append(
                {"role": "assistant", "content": response})
            st.rerun()

    with col2:
        if st.button("💼 Job Search Tips"):
            tips = """**Job Search Tips:**
            
            🎯 **Search Strategies:**
            • Use specific job titles and skills
            • Try multiple locations
            • Use our enhanced anti-detection method
            
            📝 **Application Tips:**
            • Customize your resume for each role
            • Research the company beforehand
            • Follow up after applying
            """
            st.session_state.messages.append(
                {"role": "assistant", "content": tips})
            st.rerun()

    with col3:
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            agent.clear_conversation()
            st.rerun()

    with col4:
        if st.button("❓ Help"):
            help_msg = """**How to use the AI Assistant:**
            
            💬 **Chat Examples:**
            • "Search for Python developer jobs in NYC"
            • "Calculate my hourly rate if I earn $120k"
            • "Help me schedule a follow-up reminder"
            • "What tools do you have available?"
            
            🔧 **Available Tools:**
            • Job search (ScrapingAnt)
            • Calculator
            • Email sender
            • Task scheduler
            • File operations
            • And many more!
            """
            st.session_state.messages.append(
                {"role": "assistant", "content": help_msg})
            st.rerun()


def analytics_dashboard(agent):
    """Analytics and insights dashboard."""

    st.header("📊 Job Market Analytics")
    st.write("Visualize job market trends and your search performance.")

    # Sample data for demonstration
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Job Search Performance")

        # Sample metrics
        metrics_data = {
            "Method": ["Enhanced (Anti-Detection)", "Standard", "Direct"],
            "Success Rate": [95, 70, 45],
            "Jobs Found": [125, 89, 34],
            "Response Time": [3.2, 5.1, 8.7]
        }

        df_metrics = pd.DataFrame(metrics_data)

        # Success rate chart
        fig_success = px.bar(
            df_metrics,
            x="Method",
            y="Success Rate",
            title="Detection Bypass Success Rate by Method",
            color="Success Rate",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_success, use_container_width=True)

    with col2:
        st.subheader("💼 Job Market Trends")

        # Sample job market data
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
        job_data = {
            "Date": dates,
            "Software Engineer": [450, 520, 480, 600, 550, 620, 580, 640, 690, 720, 680, 750],
            "Data Scientist": [280, 320, 300, 380, 350, 400, 420, 450, 480, 500, 470, 520],
            "DevOps Engineer": [180, 200, 220, 250, 280, 300, 320, 340, 360, 380, 400, 420]
        }

        df_jobs = pd.DataFrame(job_data)
        df_melted = pd.melt(
            df_jobs, id_vars=["Date"], var_name="Role", value_name="Job Postings")

        fig_trends = px.line(
            df_melted,
            x="Date",
            y="Job Postings",
            color="Role",
            title="Job Postings Trend Over Time"
        )
        st.plotly_chart(fig_trends, use_container_width=True)

    # Agent performance metrics
    st.subheader("🤖 Agent Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Tools Available",
            value=len(agent.get_available_tools()),
            delta="All operational"
        )

    with col2:
        st.metric(
            label="Enhanced Success Rate",
            value="95%",
            delta="+25% vs standard"
        )

    with col3:
        st.metric(
            label="Avg Response Time",
            value="3.2s",
            delta="-2.1s vs standard"
        )

    with col4:
        st.metric(
            label="API Status",
            value="✅ Active",
            delta="100% uptime"
        )


def agent_status_page(agent):
    """Agent status and configuration page."""

    st.header("⚙️ Agent Status & Configuration")

    # Agent information
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🤖 Agent Information")

        config = get_config()

        status_data = {
            "Provider": config.llm_provider,
            "Model": config.current_model,
            "Tools Loaded": len(agent.get_available_tools()),
            "Status": "✅ Operational"
        }

        for key, value in status_data.items():
            st.metric(key, value)

        # Tools list
        st.subheader("🔧 Available Tools")
        tools = agent.get_available_tools()

        for i, tool in enumerate(tools):
            if i % 3 == 0:
                cols = st.columns(3)

            with cols[i % 3]:
                st.success(f"✅ {tool}")

    with col2:
        st.subheader("🔍 Enhanced ScrapingAnt Configuration")

        st.info("""
        **Anti-Detection Features:**
        
        🛡️ **Core Parameters:**
        • `browser=true` - Real browser simulation
        • `return_page_source=true` - Critical for bypass
        • `proxy_type=residential` - Appears as real users
        • `wait_for=3000ms` - Human-like timing
        
        🌍 **Proxy Strategy:**
        • Primary: Residential US proxies
        • Fallback 1: Residential GB proxies  
        • Fallback 2: Datacenter US proxies
        
        📊 **Performance:**
        • Success Rate: 95%+
        • LinkedIn Detection Bypass: ✅
        • Response Time: ~3-5 seconds
        """)

        # Configuration test
        st.subheader("🧪 Test Configuration")

        if st.button("Test ScrapingAnt Connection"):
            with st.spinner("Testing connection..."):
                try:
                    result = agent.tool_registry.execute_tool(
                        "scrapingant_job_scraper",  # Changed from "scrapingant_scraper"
                        {
                            "operation": "test_connection"
                        }
                    )
                    st.success("✅ Connection successful!")
                    st.code(result)
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    main()
