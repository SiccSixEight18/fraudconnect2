"""
Fraud Ring Detection and Visualization
A Streamlit application for detecting and visualizing fraud rings using Vis.js
"""

import streamlit as st
import pandas as pd
from io import StringIO
import json
from fraud_detector import FraudRingDetector
from visjs_template import get_visjs_html, get_empty_state_html
import streamlit.components.v1 as components


# Page configuration
st.set_page_config(
    page_title="Fraud Ring Detector",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Apple-like design
st.markdown("""
    <style>
    /* Import SF Pro Display font (Apple's system font) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    }
    
    .main {
        padding: 2rem 3rem;
        background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
    }
    
    /* Title styling */
    h1 {
        text-align: center;
        color: #1d1d1f;
        font-weight: 600;
        font-size: 3rem;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        color: #1d1d1f;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        padding: 12px 16px;
        font-size: 15px;
        background: #ffffff;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0071e3;
        box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
    }
    
    .stTextInput > label, .stTextArea > label {
        font-weight: 500;
        color: #1d1d1f;
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 15px;
        letter-spacing: -0.2px;
        border: none;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0071e3 0%, #005bb5 100%);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #005bb5 0%, #004a99 100%);
    }
    
    /* Select boxes and number inputs */
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        background: #ffffff;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: #d2d2d7;
    }
    
    .stSlider > div > div > div > div {
        background: #0071e3;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        font-weight: 400;
        color: #1d1d1f;
    }
    
    /* Markdown and text */
    .markdown-text-container {
        color: #6e6e73;
        line-height: 1.6;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #d2d2d7, transparent);
        margin: 2rem 0;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        padding: 16px 20px;
        background: #f5f5f7;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 12px;
        background: #f5f5f7;
        font-weight: 500;
        color: #1d1d1f;
    }
    
    /* Card-like sections */
    div[data-testid="column"] {
        background: transparent;
    }
    
    /* Remove Streamlit branding colors */
    .css-1d391kg, .css-1v3fvcr {
        background: transparent;
    }
    
    /* Tooltips */
    .stTooltipIcon {
        color: #86868b;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        background: #ffffff;
    }
    
    /* Subtle animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.3s ease-out;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def process_fraud_detection(field_data, field_names):
    """Cached function to process fraud detection."""
    detector = FraudRingDetector(field_names=field_names)
    graph_data = detector.process_data(field_data)
    return detector, graph_data


def parse_input_data(text_input):
    """Parse text input into a list, handling multiple formats."""
    if not text_input or text_input.strip() == '':
        return []
    
    # Split by newlines and clean up
    lines = [line.strip() for line in text_input.strip().split('\n')]
    return [line for line in lines if line]


def main():
    # Initialize session state
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    if 'detector' not in st.session_state:
        st.session_state.detector = None
    if 'graph_data' not in st.session_state:
        st.session_state.graph_data = None
    if 'chart_title' not in st.session_state:
        st.session_state.chart_title = "FRAUD RING NETWORK"
    if 'field_names' not in st.session_state:
        # Default 9 field names (2 required + 7 optional)
        st.session_state.field_names = [
            'Client ID', 'Device ID', 'Password', 'IP Address', 
            'Phone Number', 'Email', 'Affiliate Source', 'User Agent', 'Session ID'
        ]
    
    # Initialize visualization settings
    if 'layout_algorithm' not in st.session_state:
        st.session_state.layout_algorithm = 'forceAtlas2Based'
    if 'edge_smooth_type' not in st.session_state:
        st.session_state.edge_smooth_type = 'continuous'
    if 'edge_opacity' not in st.session_state:
        st.session_state.edge_opacity = 0.3
    if 'min_edge_weight' not in st.session_state:
        st.session_state.min_edge_weight = 1
    if 'show_edge_labels' not in st.session_state:
        st.session_state.show_edge_labels = False
    
    # Centered Title
    st.markdown("<h1>🕸️ Fraud Ring Detection & Visualization</h1>", unsafe_allow_html=True)
    
    # Chart Title Input (centered)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        chart_title = st.text_input(
            "Chart Title",
            value=st.session_state.chart_title,
            key="chart_title_input",
            help="Title displayed on the network visualization"
        )
        st.session_state.chart_title = chart_title if chart_title else "FRAUD RING NETWORK"
    
    st.markdown("---")
    
    # Data Input Section - 3x3 Grid
    st.subheader("Data Input")
    st.markdown("*Enter at least 2 fields (first field + one more)*")
    
    # Store field data
    field_data = {}
    
    # Row 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[0], key="name_0")
        st.session_state.field_names[0] = field_name
        field_input = st.text_area(
            f"{field_name} *",
            height=130,
            key="field_0",
            placeholder="One per line (REQUIRED)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    with col2:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[1], key="name_1")
        st.session_state.field_names[1] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_1",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    with col3:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[2], key="name_2")
        st.session_state.field_names[2] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_2",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    # Row 2
    col1, col2, col3 = st.columns(3)
    
    with col1:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[3], key="name_3")
        st.session_state.field_names[3] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_3",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    with col2:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[4], key="name_4")
        st.session_state.field_names[4] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_4",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    with col3:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[5], key="name_5")
        st.session_state.field_names[5] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_5",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    # Row 3
    col1, col2, col3 = st.columns(3)
    
    with col1:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[6], key="name_6")
        st.session_state.field_names[6] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_6",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    with col2:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[7], key="name_7")
        st.session_state.field_names[7] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_7",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    with col3:
        field_name = st.text_input("Field Name:", value=st.session_state.field_names[8], key="name_8")
        st.session_state.field_names[8] = field_name
        field_input = st.text_area(
            field_name,
            height=130,
            key="field_8",
            placeholder="One per line (optional)",
            label_visibility="collapsed"
        )
        field_data[field_name.lower().replace(' ', '_')] = parse_input_data(field_input)
    
    st.markdown("---")
    
    # Check if required data provided (client_id + at least 1 more field)
    client_id_key = st.session_state.field_names[0].lower().replace(' ', '_')
    has_client_id = len(field_data.get(client_id_key, [])) > 0
    
    # Count how many fields have data
    fields_with_data = sum(1 for v in field_data.values() if len(v) > 0)
    has_required_data = has_client_id and fields_with_data >= 2
    
    # Analyze button (centered)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Detect Fraud Rings",
            type="primary",
            use_container_width=True,
            disabled=not has_required_data
        )
        
        if st.session_state.analyzed:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.analyzed = False
                st.session_state.detector = None
                st.session_state.graph_data = None
                st.rerun()
    
    if analyze_button:
        # Convert field names for detector
        field_names_internal = [name.lower().replace(' ', '_') for name in st.session_state.field_names]
        
        # Store display names mapping for detector
        display_names_map = {name.lower().replace(' ', '_'): name for name in st.session_state.field_names}
        
        with st.spinner("🔍 Analyzing data and detecting fraud rings..."):
            try:
                detector, graph_data = process_fraud_detection(field_data, field_names_internal)
                # Store display names in detector for legend
                detector.field_display_names = display_names_map
                
                st.session_state.detector = detector
                st.session_state.graph_data = graph_data
                st.session_state.analyzed = True
                st.success(f"✅ Analysis complete! Found {len(graph_data['nodes'])} entities and {len(graph_data['edges'])} connections.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.stop()
    
    # Show visualization if analyzed
    if st.session_state.analyzed and st.session_state.detector:
        st.markdown("---")
        
        detector = st.session_state.detector
        graph_data = st.session_state.graph_data
        
        # Get available features from detector for initial defaults
        available_features = detector.all_fields
        
        # Settings Section - MOVED BEFORE VISUALIZATION for auto-reload
        st.markdown("### Settings")
        
        # Layout algorithm selector (full width)
        layout_algorithm = st.selectbox(
            "Layout Algorithm",
            options=['forceAtlas2Based', 'barnesHut', 'repulsion', 'hierarchicalRepulsion'],
            index=['forceAtlas2Based', 'barnesHut', 'repulsion', 'hierarchicalRepulsion'].index(st.session_state.layout_algorithm),
            format_func=lambda x: {
                'forceAtlas2Based': 'Force Atlas 2',
                'barnesHut': 'Barnes Hut',
                'repulsion': 'Repulsion',
                'hierarchicalRepulsion': 'Hierarchical'
            }[x],
            help="Choose how nodes are arranged",
            key="layout_select"
        )
        st.session_state.layout_algorithm = layout_algorithm
        
        st.markdown("#### Edge Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Edge smoothing/routing
            edge_smooth_type = st.selectbox(
                "Edge Style",
                options=['dynamic', 'continuous', 'discrete', 'cubicBezier', 'straightCross', 'curvedCW', 'curvedCCW'],
                index=['dynamic', 'continuous', 'discrete', 'cubicBezier', 'straightCross', 'curvedCW', 'curvedCCW'].index(st.session_state.edge_smooth_type),
                format_func=lambda x: {
                    'dynamic': 'Dynamic',
                    'continuous': 'Continuous',
                    'discrete': 'Discrete',
                    'cubicBezier': 'Cubic Bezier',
                    'straightCross': 'Straight',
                    'curvedCW': 'Curved CW',
                    'curvedCCW': 'Curved CCW'
                }[x],
                key="edge_style_select"
            )
            st.session_state.edge_smooth_type = edge_smooth_type
            
            # Edge opacity
            edge_opacity = st.slider(
                "Edge Transparency",
                min_value=0.1,
                max_value=1.0,
                value=st.session_state.edge_opacity,
                step=0.1,
                key="edge_opacity_slider"
            )
            st.session_state.edge_opacity = edge_opacity
        
        with col2:
            # Edge filtering by weight
            min_edge_weight = st.number_input(
                "Minimum Shared Features",
                min_value=1,
                max_value=10,
                value=st.session_state.min_edge_weight,
                step=1,
                key="min_edge_input"
            )
            st.session_state.min_edge_weight = min_edge_weight
            
            # Show edge labels toggle
            show_edge_labels = st.checkbox(
                "Show Edge Labels",
                value=st.session_state.show_edge_labels,
                key="edge_labels_check"
            )
            st.session_state.show_edge_labels = show_edge_labels
        
        st.markdown("---")
        st.markdown("### Fraud Ring Network")
        
        # Apply filter with current session state values (show all feature types)
        filtered_data = detector.filter_graph(
            min_risk=0,
            feature_types=None  # Show all features
        )
        
        # Network visualization
        if len(filtered_data['nodes']) == 0:
            st.warning("No entities match the current filter criteria.")
        else:
            # Determine physics based on size
            physics_enabled = len(filtered_data['nodes']) < 100
            
            # Generate and display visualization with field colors
            field_colors = detector.get_field_colors() if hasattr(detector, 'get_field_colors') else None
            
            vis_html = get_visjs_html(
                filtered_data['nodes'],
                filtered_data['edges'],
                height=700,
                physics_enabled=physics_enabled,
                field_colors=field_colors,
                chart_title=st.session_state.chart_title,
                layout_algorithm=st.session_state.layout_algorithm,
                edge_smooth_type=st.session_state.edge_smooth_type,
                edge_opacity=st.session_state.edge_opacity,
                min_edge_weight=st.session_state.min_edge_weight,
                show_edge_labels=st.session_state.show_edge_labels
            )
            
            components.html(vis_html, height=750, scrolling=False)
        
        # Show filter results
        if len(filtered_data['nodes']) < len(graph_data['nodes']):
            st.info(f"Showing {len(filtered_data['nodes'])} of {len(graph_data['nodes'])} entities and {len(filtered_data['edges'])} of {len(graph_data['edges'])} connections")


if __name__ == "__main__":
    main()
