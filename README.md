# 🕸️ Fraud Ring Detection & Visualization

A beautiful, Apple-inspired Streamlit application for detecting and visualizing fraud rings through network graph analysis.

## Features

- **Interactive Network Visualization** - Powered by Vis.js with Apple-style design
- **Smart Fraud Detection** - Identifies connections between entities based on shared features
- **Risk Scoring** - Calculates risk levels based on connection patterns and feature types
- **Flexible Field Mapping** - Supports up to 9 customizable data fields
- **Real-time Updates** - Visualization auto-updates when settings change
- **PNG Export** - Export high-quality network diagrams with title and timestamp

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Enter your data in the 9 field grid (minimum: Client ID + 1 other field)
2. Customize field names to match your data
3. Click "Detect Fraud Rings" to analyze
4. Adjust visualization settings (layout algorithm, edge style, transparency, etc.)
5. Export results as PNG

## Node Color Legend

- **Light Blue** - Low Risk (1 feature type match)
- **Medium Blue** - Medium Risk (2 feature types match)
- **Apple Blue** - High Risk (3+ feature types match)
- **Gray** - No connections (filtered view)

## Tech Stack

- **Streamlit** - Web application framework
- **Pandas** - Data processing
- **NetworkX** - Graph analysis
- **Vis.js** - Interactive network visualization
- **Apple Design Language** - Beautiful, minimalist UI

## Design Philosophy

This application follows Apple's Human Interface Guidelines with:
- Clean, minimal aesthetics
- Soft, elegant color palette
- Smooth animations and transitions
- Intuitive interactions
- Professional typography

---

Built with ❤️ using Apple-inspired design principles

