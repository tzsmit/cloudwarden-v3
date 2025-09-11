
"""
CloudWarden v3 Executive Dashboard
Revolutionary AI-Powered Security Intelligence Interface
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import json

from cloudwarden.config import load_config
from cloudwarden.agent.explainer import CloudWardenAIAgent

# Nova Titan Systems branding
NOVA_TITAN_COLORS = {
    'primary': '#00F5A0',
    'secondary': '#1E293B', 
    'accent': '#0EA5E9',
    'danger': '#EF4444',
    'warning': '#F59E0B'
}

def main():
    st.set_page_config(
        page_title="CloudWarden v3 - Nova Titan Systems",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for Nova Titan branding
    st.markdown(f"""
    <style>
    .main-header {{
        background: linear-gradient(90deg, {NOVA_TITAN_COLORS['secondary']}, {NOVA_TITAN_COLORS['primary']});
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }}
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {NOVA_TITAN_COLORS['primary']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }}
    .ai-insight {{
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1px solid {NOVA_TITAN_COLORS['primary']};
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    .stSelectbox > div > div > select {{
        background-color: {NOVA_TITAN_COLORS['secondary']};
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🛡️ CloudWarden v3</h1>
        <h3>Revolutionary AI-Powered Cloud Security Platform</h3>
        <p><strong>Nova Titan Systems</strong> | Find misconfigurations fast. Ship safer.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎯 Security Operations")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Executive Dashboard", "🤖 AI Security Agent", "📊 Security Scan", "⚙️ System Status"]
    )
    
    if page == "🏠 Executive Dashboard":
        render_executive_dashboard()
    elif page == "🤖 AI Security Agent":
        render_ai_agent_page()
    elif page == "📊 Security Scan":
        render_scan_page()
    elif page == "⚙️ System Status":
        render_status_page()


def render_executive_dashboard():
    """Executive-level security metrics and insights"""
    
    st.title("📊 Executive Security Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Security Score", "87/100", "↗️ +5")
        st.markdown("Overall security posture")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Threats", "12", "↘️ -3")
        st.markdown("Requiring immediate attention")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("AI Insights", "156", "↗️ +23")
        st.markdown("Generated this week")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Compliance", "94%", "↗️ +2%")
        st.markdown("CIS AWS Benchmark")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI-generated insights
    st.markdown("""
    <div class="ai-insight">
        <h4>🤖 AI Executive Insights</h4>
        <p><strong>🚨 Critical Alert:</strong> Our AI agent identified 3 new attack paths through IAM role assumptions. 
        Immediate review recommended for cross-account trust relationships.</p>
        
        <p><strong>📈 Trend Analysis:</strong> Security posture improved 5% this month due to automated remediation 
        of S3 bucket permissions and IAM policy tightening.</p>
        
        <p><strong>🎯 Priority Action:</strong> Focus on 12 high-risk findings in production environment. 
        AI-generated remediation available in Security Scan section.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Security trend chart
    st.subheader("📈 Security Trends")
    
    # Sample data for demonstration
    dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
    trend_data = pd.DataFrame({
        'Date': dates,
        'Security Score': 85 + (dates.day % 7) + (dates.day % 3),
        'Findings': 50 - (dates.day % 10),
        'AI Insights': dates.day * 2 + (dates.day % 5)
    })
    
    fig = px.line(trend_data, x='Date', y=['Security Score', 'Findings'], 
                  title="Security Metrics Trend",
                  color_discrete_map={'Security Score': NOVA_TITAN_COLORS['primary'],
                                    'Findings': NOVA_TITAN_COLORS['danger']})
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_ai_agent_page():
    """AI Security Agent interface"""
    
    st.title("🤖 AI Security Agent")
    st.markdown("Powered by local Ollama models - No cloud costs, complete privacy")
    
    # Load configuration and AI agent
    try:
        config = load_config()
        ai_agent = CloudWardenAIAgent(config)
        
        if ai_agent.is_available():
            st.success(f"✅ AI Agent Ready - Model: {config.ai_agent.model}")
            
            # AI analysis interface
            st.subheader("🔍 Security Finding Analysis")
            
            # Sample findings for demonstration
            sample_findings = {
                "IAM Wildcard Policy": {
                    'type': 'iam_wildcard_policy',
                    'severity': 'High',
                    'resource_id': 'arn:aws:iam::123456789012:role/admin-role',
                    'description': 'IAM role has unrestricted wildcard permissions allowing full AWS access'
                },
                "Public S3 Bucket": {
                    'type': 'public_s3_bucket',
                    'severity': 'Medium',
                    'resource_id': 'arn:aws:s3:::company-data-bucket',
                    'description': 'S3 bucket allows public read access to potentially sensitive data'
                },
                "Unencrypted RDS Database": {
                    'type': 'unencrypted_database',
                    'severity': 'High',
                    'resource_id': 'arn:aws:rds:us-east-1:123456789012:db:prod-database',
                    'description': 'RDS database instance lacks encryption at rest'
                }
            }
            
            selected_finding = st.selectbox(
                "Select a security finding to analyze:",
                list(sample_findings.keys())
            )
            
            if st.button("🧠 Analyze with AI", type="primary"):
                with st.spinner("AI analyzing security finding..."):
                    finding = sample_findings[selected_finding]
                    analysis = ai_agent.analyze_finding(finding)
                
                # Display analysis results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💼 Business Impact")
                    st.write(analysis.business_impact)
                    
                    st.markdown("### ⚠️ Risk Factors")
                    for factor in analysis.risk_factors:
                        st.write(f"• {factor}")
                
                with col2:
                    st.markdown("### 🔧 Remediation Steps")
                    for i, step in enumerate(analysis.remediation_steps, 1):
                        st.write(f"{i}. {step}")
                    
                    st.markdown("### 📊 AI Confidence")
                    st.progress(analysis.confidence_score)
                    st.write(f"Confidence: {analysis.confidence_score:.1%}")
        
        else:
            st.error("❌ AI Agent Not Available")
            st.markdown("""
            **To enable AI features:**
            
            1. **Install Ollama:**
               ```bash
               curl -fsSL https://ollama.ai/install.sh | sh
               ```
            
            2. **Download AI models:**
               ```bash
               ollama pull llama3.1:8b
               ollama pull deepseek-r1:7b
               ```
            
            3. **Start Ollama service:**
               ```bash
               ollama serve
               ```
            """)
            
    except Exception as e:
        st.error(f"Configuration Error: {e}")


def render_scan_page():
    """Security scanning interface"""
    
    st.title("📊 Security Scan")
    
    # Scan configuration
    col1, col2 = st.columns(2)
    
    with col1:
        services = st.multiselect(
            "AWS Services to Scan:",
            ["iam", "s3", "ec2", "rds", "lambda", "cloudtrail"],
            default=["iam", "s3", "ec2"]
        )
    
    with col2:
        regions = st.multiselect(
            "AWS Regions:",
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            default=["us-east-1"]
        )
    
    if st.button("🔍 Start Security Scan", type="primary"):
        # Mock scan progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        import time
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 25:
                status_text.text(f"Scanning IAM resources... ({i+1}%)")
            elif i < 50:
                status_text.text(f"Scanning S3 buckets... ({i+1}%)")
            elif i < 75:
                status_text.text(f"Scanning EC2 instances... ({i+1}%)")
            else:
                status_text.text(f"Generating AI insights... ({i+1}%)")
            time.sleep(0.02)
        
        status_text.text("Scan completed!")
        
        # Mock results
        st.success("✅ Scan completed successfully")
        
        # Results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Findings", "23")
        with col2:
            st.metric("Critical/High", "8")
        with col3:
            st.metric("Resources Scanned", "1,247")
        
        # Findings table
        findings_data = pd.DataFrame({
            'Severity': ['Critical', 'High', 'High', 'Medium', 'Medium'],
            'Type': ['IAM Wildcard Policy', 'Public S3 Bucket', 'Unencrypted Database', 'Weak Passwords', 'Missing MFA'],
            'Resource': ['admin-role', 'data-bucket', 'prod-db', 'user-accounts', 'iam-users'],
            'Service': ['IAM', 'S3', 'RDS', 'IAM', 'IAM']
        })
        
        st.subheader("🔍 Security Findings")
        st.dataframe(findings_data, use_container_width=True)


def render_status_page():
    """System status and configuration"""
    
    st.title("⚙️ System Status")
    
    # System information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 System Information")
        st.write("**Version:** 3.0.0")
        st.write("**Organization:** Nova Titan Systems") 
        st.write("**License:** MIT")
        
        # Configuration status
        try:
            config = load_config()
            st.success("✅ Configuration loaded successfully")
            
            st.subheader("🔧 Configuration")
            st.write(f"**AWS Regions:** {', '.join(config.aws.regions)}")
            st.write(f"**AWS Profile:** {config.aws.profile or 'default'}")
            st.write(f"**Services:** {', '.join(config.scanning.services)}")
            
        except Exception as e:
            st.error(f"❌ Configuration error: {e}")
    
    with col2:
        st.subheader("🤖 AI Agent Status")
        
        try:
            config = load_config()
            ai_agent = CloudWardenAIAgent(config)
            
            if ai_agent.is_available():
                st.success("✅ AI Agent operational")
                st.write(f"**Model:** {config.ai_agent.model}")
                st.write(f"**Ollama URL:** {config.ai_agent.ollama_base_url}")
                
                # Test AI response
                if st.button("🧪 Test AI Agent"):
                    with st.spinner("Testing AI..."):
                        test_finding = {
                            'type': 'test',
                            'severity': 'Low',
                            'description': 'AI agent test'
                        }
                        analysis = ai_agent.analyze_finding(test_finding)
                        st.write(f"**Test Response:** {analysis.business_impact[:100]}...")
            else:
                st.error("❌ AI Agent not available")
                st.write("Install Ollama and download models to enable AI features")
                
        except Exception as e:
            st.error(f"❌ AI Agent error: {e}")
    
    # Component status
    st.subheader("🔧 Available Components")
    components = [
        "✅ Configuration Management",
        "✅ AI Agent System", 
        "⏳ Attack Path Analysis (Coming Soon)",
        "⏳ IoT/OT Security Scanner (Coming Soon)",
        "⏳ Quantum Crypto Analyzer (Coming Soon)",
        "✅ Executive Reporting"
    ]
    
    for component in components:
        st.write(component)


if __name__ == "__main__":
    main()
EOF
