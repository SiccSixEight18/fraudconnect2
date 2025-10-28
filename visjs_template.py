"""
Vis.js Visualization Template
Generates HTML/JavaScript for interactive network visualization
"""


def get_visjs_html(nodes, edges, height=700, physics_enabled=True, field_colors=None, chart_title="Fraud Ring Network", 
                   layout_algorithm="forceAtlas2Based", edge_smooth_type="continuous", edge_opacity=1.0, 
                   min_edge_weight=1, show_edge_labels=True, use_hierarchical=False):
    """
    Generate HTML template with Vis.js network visualization.
    
    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries
        height: Height of the visualization in pixels
        physics_enabled: Whether to enable physics simulation
        field_colors: Optional dict mapping field names to colors for legend
        chart_title: Title displayed at top of chart
        layout_algorithm: Physics layout algorithm (barnesHut, forceAtlas2Based, repulsion, hierarchicalRepulsion)
        edge_smooth_type: Edge smoothing type (dynamic, continuous, discrete, diagonalCross, straightCross, horizontal, vertical, curvedCW, curvedCCW, cubicBezier)
        edge_opacity: Edge opacity (0.0-1.0)
        min_edge_weight: Minimum edge weight to display (filters edges)
        show_edge_labels: Whether to show edge labels
    
    Returns:
        HTML string containing the complete visualization
    """
    import json
    
    # Filter edges by weight/importance
    filtered_edges = [e for e in edges if len(e.get('shared_features', [])) >= min_edge_weight]
    
    # Apply opacity to edge colors
    def add_opacity_to_color(color_str, opacity):
        """Convert hex color to rgba with opacity"""
        if color_str.startswith('#'):
            hex_color = color_str.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f'rgba({r}, {g}, {b}, {opacity})'
        return color_str
    
    # Apply opacity to edges
    edges_with_opacity = []
    for edge in filtered_edges:
        edge_copy = edge.copy()
        if 'color' in edge_copy and edge_opacity < 1.0:
            edge_copy['color'] = add_opacity_to_color(edge_copy['color'], edge_opacity)
        if not show_edge_labels:
            edge_copy['label'] = ''
        edges_with_opacity.append(edge_copy)
    
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges_with_opacity)
    
    # Build legend HTML for edge colors (Apple-styled)
    edge_legend_html = ""
    if field_colors:
        edge_legend_html = '<div style="margin-top: 16px; border-top: 1px solid rgba(0, 0, 0, 0.06); padding-top: 12px;">'
        edge_legend_html += '<div style="font-weight: 600; margin-bottom: 12px; font-size: 13px; color: #1d1d1f;">Connection Types</div>'
        
        for field_name, color in field_colors.items():
            display_name = field_name.replace('_', ' ').title()
            edge_legend_html += f'''
                <div class="legend-item">
                    <div style="width: 32px; height: 2px; background-color: {color}; margin-right: 10px; border-radius: 1px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);"></div>
                    <div class="legend-label" style="font-size: 12px;">{display_name}</div>
                </div>
            '''
        
        # Add multiple fields indicator
        edge_legend_html += '''
            <div class="legend-item">
                <div style="width: 32px; height: 2px; background-color: #AF52DE; margin-right: 10px; border-radius: 1px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);"></div>
                <div class="legend-label" style="font-size: 12px;">Multiple Fields</div>
            </div>
        '''
        edge_legend_html += '</div>'
    else:
        # Default legend
        edge_legend_html = '''
            <div style="margin-top: 16px; border-top: 1px solid rgba(0, 0, 0, 0.06); padding-top: 12px;">
                <div style="font-weight: 600; margin-bottom: 12px; font-size: 13px; color: #1d1d1f;">Connection Types</div>
                <div class="legend-item">
                    <div style="width: 32px; height: 2px; background-color: #8E8E93; margin-right: 10px; border-radius: 1px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);"></div>
                    <div class="legend-label" style="font-size: 12px;">Connection</div>
                </div>
                <div class="legend-item">
                    <div style="width: 32px; height: 2px; background-color: #AF52DE; margin-right: 10px; border-radius: 1px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);"></div>
                    <div class="legend-label" style="font-size: 12px;">Multiple Fields</div>
                </div>
            </div>
        '''
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style type="text/css">
            body, html {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
            }}
            
            #mynetwork {{
                width: 100%;
                height: {height}px;
                border: 1px solid #d2d2d7;
                background: radial-gradient(ellipse at center, #ffffff 0%, #fafafa 100%);
                position: relative;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.02);
            }}
            
            #legend {{
                position: absolute;
                top: 70px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 0, 0, 0.04);
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
                z-index: 1000;
                transition: all 0.3s ease;
            }}
            
            #legend:hover {{
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 10px 0;
            }}
            
            .legend-color {{
                width: 18px;
                height: 18px;
                border-radius: 50%;
                margin-right: 12px;
                border: 2px solid rgba(0, 0, 0, 0.1);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }}
            
            .legend-label {{
                font-size: 13px;
                font-weight: 400;
                color: #1d1d1f;
                letter-spacing: -0.08px;
            }}
            
            #controls {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 0, 0, 0.04);
                border-radius: 16px;
                padding: 12px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
                z-index: 1000;
                display: flex;
                gap: 8px;
                transition: all 0.3s ease;
            }}
            
            #controls:hover {{
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
            }}
            
            .control-btn {{
                padding: 10px 18px;
                background: linear-gradient(135deg, #0071e3 0%, #005bb5 100%);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: -0.08px;
                transition: all 0.2s ease;
                box-shadow: 0 2px 8px rgba(0, 113, 227, 0.2);
            }}
            
            .control-btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
                background: linear-gradient(135deg, #005bb5 0%, #004a99 100%);
            }}
            
            .control-btn:active {{
                transform: translateY(0);
            }}
            
            #stats {{
                position: absolute;
                top: 70px;
                left: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 0, 0, 0.04);
                border-radius: 16px;
                padding: 16px 20px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
                z-index: 1000;
                font-size: 13px;
                transition: all 0.3s ease;
            }}
            
            #stats:hover {{
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
            }}
            
            .stat-item {{
                margin: 8px 0;
                color: #1d1d1f;
                letter-spacing: -0.08px;
            }}
            
            .stat-item strong {{
                font-weight: 600;
                color: #1d1d1f;
            }}
            
            #chart-title {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #1d1d1f 0%, #2d2d2f 100%);
                color: #F5F5F7;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
                font-size: 17px;
                font-weight: 600;
                text-align: center;
                padding: 16px 24px;
                z-index: 999;
                letter-spacing: -0.3px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 2px 16px rgba(0, 0, 0, 0.15);
            }}
            
            #mynetwork {{
                margin-top: 52px;
                position: relative;
            }}
            
            #export-controls {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 0, 0, 0.04);
                border-radius: 16px;
                padding: 12px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
                z-index: 1000;
                transition: all 0.3s ease;
            }}
            
            #export-controls:hover {{
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
            }}
        </style>
    </head>
    <body>
        <div id="visualization-wrapper" style="position: relative; width: 100%; height: {height + 50}px; margin: 0; padding: 0;">
            <div id="chart-title">{chart_title}</div>
            
            <div id="stats">
            <div class="stat-item"><strong>Nodes:</strong> <span id="node-count">0</span></div>
            <div class="stat-item"><strong>Edges:</strong> <span id="edge-count">0</span></div>
            <div class="stat-item"><strong>Selected:</strong> <span id="selected-node">None</span></div>
        </div>
        
        <div id="legend">
            <div style="font-weight: 600; margin-bottom: 12px; font-size: 15px; color: #1d1d1f;">Node Risk Levels</div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #E5E5EA; border: 1.5px solid rgba(0, 0, 0, 0.08);"></div>
                <div class="legend-label">No Connections</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #B4E4FF; border: 1.5px solid rgba(0, 122, 255, 0.2);"></div>
                <div class="legend-label">Low Risk (1 Type)</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #88C9FF; border: 1.5px solid rgba(0, 122, 255, 0.3);"></div>
                <div class="legend-label">Medium Risk (2 Types)</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #007AFF; border: 1.5px solid rgba(0, 122, 255, 0.4);"></div>
                <div class="legend-label">High Risk (3+ Types)</div>
            </div>
            
            {edge_legend_html}
        </div>
        
            <div id="mynetwork"></div>
        </div>
        
        <div id="controls">
            <button class="control-btn" onclick="fitNetwork()">Fit View</button>
            <button class="control-btn" onclick="togglePhysics()">Toggle Physics</button>
            <button class="control-btn" onclick="resetSelection()">Reset Selection</button>
        </div>
        
        <div id="export-controls">
            <button class="control-btn" onclick="exportPNG()">Export PNG</button>
        </div>
        
        <script type="text/javascript">
            // Create nodes and edges
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});
            
            // Create a network
            var container = document.getElementById('mynetwork');
            var data = {{
                nodes: nodes,
                edges: edges
            }};
            
            var options = {{
                nodes: {{
                    shape: 'dot',
                    size: 24,
                    font: {{
                        size: 14,
                        color: '#1d1d1f',
                        face: '-apple-system, BlinkMacSystemFont, SF Pro Display, Segoe UI, Arial',
                        bold: false,
                        strokeWidth: 0
                    }},
                    borderWidth: 1.5,
                    borderWidthSelected: 3,
                    shadow: {{
                        enabled: true,
                        color: 'rgba(0, 0, 0, 0.08)',
                        size: 8,
                        x: 0,
                        y: 2
                    }},
                    scaling: {{
                        min: 24,
                        max: 24
                    }},
                    shapeProperties: {{
                        borderRadius: 50
                    }}
                }},
                edges: {{
                    font: {{
                        size: 11,
                        align: 'middle',
                        color: '#86868b',
                        face: '-apple-system, BlinkMacSystemFont, SF Pro Display, Segoe UI, Arial'
                    }},
                    smooth: {{
                        type: '{edge_smooth_type}',
                        roundness: 0.5,
                        forceDirection: 'none'
                    }},
                    width: 1.5,
                    selectionWidth: 2.5,
                    hoverWidth: 2.5,
                    shadow: {{
                        enabled: false
                    }}
                }},
                physics: {{
                    enabled: {str(physics_enabled).lower()},
                    stabilization: {{
                        enabled: true,
                        iterations: 800,
                        updateInterval: 20,
                        fit: true
                    }},
                    barnesHut: {{
                        gravitationalConstant: -8000,
                        centralGravity: 0.05,
                        springLength: 300,
                        springConstant: 0.008,
                        damping: 0.35,
                        avoidOverlap: 1.0
                    }},
                    forceAtlas2Based: {{
                        gravitationalConstant: -100,
                        centralGravity: 0.001,
                        springLength: 250,
                        springConstant: 0.03,
                        damping: 0.6,
                        avoidOverlap: 1.0
                    }},
                    repulsion: {{
                        centralGravity: 0.01,
                        springLength: 350,
                        springConstant: 0.02,
                        nodeDistance: 250,
                        damping: 0.15
                    }},
                    hierarchicalRepulsion: {{
                        centralGravity: 0.0,
                        springLength: 120,
                        springConstant: 0.008,
                        nodeDistance: 170,
                        damping: 0.12,
                        avoidOverlap: 0.85
                    }},
                    minVelocity: 0.5,
                    solver: '{layout_algorithm}'
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 150,
                    navigationButtons: true,
                    keyboard: true,
                    dragNodes: true,
                    dragView: true,
                    zoomView: true,
                    zoomSpeed: 0.8,
                    hideEdgesOnDrag: false,
                    hideEdgesOnZoom: false
                }},
                layout: {{
                    improvedLayout: {str(not use_hierarchical).lower()},
                    randomSeed: undefined,
                    hierarchical: {f'''{{
                        enabled: true,
                        levelSeparation: 250,
                        nodeSpacing: 200,
                        treeSpacing: 300,
                        blockShifting: true,
                        edgeMinimization: true,
                        parentCentralization: true,
                        direction: '{use_hierarchical}',
                        sortMethod: 'directed',
                        shakeTowards: 'leaves'
                    }}''' if use_hierarchical else 'false'}
                }},
                manipulation: {{
                    enabled: false
                }},
                configure: {{
                    enabled: false
                }}
            }};
            
            var network = new vis.Network(container, data, options);
            var physicsEnabled = true;  // Always enable physics
            var selectedNodes = [];
            var highlightActive = false;
            
            // Update stats
            document.getElementById('node-count').innerText = nodes.length;
            document.getElementById('edge-count').innerText = edges.length;
            
            // Stabilization progress
            network.on("stabilizationProgress", function(params) {{
                var maxWidth = 200;
                var widthFactor = params.iterations/params.total;
                console.log("Stabilizing: " + Math.round(widthFactor * 100) + "%");
            }});
            
            // When stabilized, keep physics enabled
            network.on("stabilizationIterationsDone", function() {{
                console.log("Stabilization complete! Physics remains enabled.");
            }});
            
            // Node click event - highlight connections
            network.on("click", function(params) {{
                if (params.nodes.length > 0) {{
                    var selectedNodeId = params.nodes[0];
                    highlightConnections(selectedNodeId);
                    document.getElementById('selected-node').innerText = 'Node ' + selectedNodeId;
                }} else {{
                    resetSelection();
                }}
            }});
            
            // Hover effects
            network.on("hoverNode", function(params) {{
                container.style.cursor = 'pointer';
            }});
            
            network.on("blurNode", function(params) {{
                container.style.cursor = 'default';
            }});
            
            network.on("hoverEdge", function(params) {{
                container.style.cursor = 'pointer';
            }});
            
            network.on("blurEdge", function(params) {{
                container.style.cursor = 'default';
            }});
            
            // Double click to zoom to node
            network.on("doubleClick", function(params) {{
                if (params.nodes.length > 0) {{
                    network.focus(params.nodes[0], {{
                        scale: 1.5,
                        animation: {{
                            duration: 1000,
                            easingFunction: 'easeInOutQuad'
                        }}
                    }});
                }}
            }});
            
            // Highlight connections function
            function highlightConnections(nodeId) {{
                highlightActive = true;
                
                // Get all connected edges
                var connectedEdges = network.getConnectedEdges(nodeId);
                var connectedNodes = network.getConnectedNodes(nodeId);
                
                // Update all nodes
                var allNodes = nodes.get({{returnType: "Object"}});
                for (var id in allNodes) {{
                    if (id == nodeId) {{
                        // Selected node
                        allNodes[id].borderWidth = 6;
                        allNodes[id].font = {{size: 16, bold: true}};
                    }} else if (connectedNodes.indexOf(parseInt(id)) > -1) {{
                        // Connected nodes
                        allNodes[id].borderWidth = 4;
                        allNodes[id].font = {{size: 14}};
                    }} else {{
                        // Other nodes - fade them
                        allNodes[id].color = {{
                            background: allNodes[id].color,
                            border: '#cccccc'
                        }};
                        allNodes[id].font = {{size: 12, color: '#cccccc'}};
                        allNodes[id].borderWidth = 1;
                    }}
                }}
                
                // Store original edge colors if not already stored
                if (!window.originalEdgeColors) {{
                    window.originalEdgeColors = {{}};
                    var allEdges = edges.get();
                    allEdges.forEach(function(edge) {{
                        window.originalEdgeColors[edge.id] = edge.color || '#848484';
                    }});
                }}
                
                // Update all edges
                var allEdges = edges.get({{returnType: "Object"}});
                for (var id in allEdges) {{
                    if (connectedEdges.indexOf(parseInt(id)) > -1) {{
                        // Connected edges - highlight with original color but brighter
                        allEdges[id].width = allEdges[id].width * 2;
                        // Keep original color but make it stand out
                        var origColor = window.originalEdgeColors[id] || '#848484';
                        allEdges[id].color = {{color: origColor, opacity: 1}};
                    }} else {{
                        // Other edges - fade
                        allEdges[id].color = {{color: '#cccccc', opacity: 0.2}};
                    }}
                }}
                
                nodes.update(Object.values(allNodes));
                edges.update(Object.values(allEdges));
            }}
            
            // Reset selection
            function resetSelection() {{
                if (!highlightActive) return;
                
                highlightActive = false;
                document.getElementById('selected-node').innerText = 'None';
                
                // Reset all nodes
                var allNodes = nodes.get({{returnType: "Object"}});
                for (var id in allNodes) {{
                    allNodes[id].borderWidth = 2;
                    allNodes[id].font = {{size: 14, color: '#000000'}};
                    delete allNodes[id].color.border;
                }}
                
                // Reset all edges to original colors
                var allEdges = edges.get({{returnType: "Object"}});
                for (var id in allEdges) {{
                    // Restore original color
                    var origColor = window.originalEdgeColors[id] || '#848484';
                    allEdges[id].color = origColor;
                    // Reset width if it was modified
                    if (allEdges[id].width > 10) {{
                        allEdges[id].width = allEdges[id].width / 2;
                    }}
                }}
                
                nodes.update(Object.values(allNodes));
                edges.update(Object.values(allEdges));
            }}
            
            // Control functions
            function fitNetwork() {{
                network.fit({{
                    animation: {{
                        duration: 1000,
                        easingFunction: 'easeInOutQuad'
                    }}
                }});
            }}
            
            function togglePhysics() {{
                physicsEnabled = !physicsEnabled;
                network.setOptions({{ physics: physicsEnabled }});
                console.log("Physics: " + (physicsEnabled ? "ON" : "OFF"));
            }}
            
            // Export function (can be called from parent)
            function exportNetwork() {{
                return {{
                    nodes: nodes.get(),
                    edges: edges.get()
                }};
            }}
            
            // Export PNG function - captures entire visualization as you see it
            function exportPNG() {{
                try {{
                    // Hide export button temporarily
                    const exportControls = document.getElementById('export-controls');
                    exportControls.style.display = 'none';
                    
                    // Use html2canvas to capture the entire visualization wrapper as user sees it
                    const visualizationWrapper = document.getElementById('visualization-wrapper');
                    
                    html2canvas(visualizationWrapper, {{
                        backgroundColor: '#fafafa',
                        scale: 2,  // Higher quality
                        logging: false,
                        useCORS: true,
                        allowTaint: true
                    }}).then(function(canvas) {{
                        // Add timestamp
                        const ctx = canvas.getContext('2d');
                        const now = new Date();
                        const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
                        
                        ctx.fillStyle = '#666666';
                        ctx.font = '24px Arial, sans-serif';
                        ctx.textAlign = 'right';
                        ctx.fillText('Generated: ' + timestamp, canvas.width - 20, canvas.height - 20);
                        
                        // Download
                        const link = document.createElement('a');
                        const fileTimestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
                        link.download = 'fraud-network-' + fileTimestamp + '.png';
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                        
                        // Restore export button
                        exportControls.style.display = 'block';
                    }}).catch(function(error) {{
                        console.error('Export error:', error);
                        alert('Export failed: ' + error.message);
                        exportControls.style.display = 'block';
                    }});
                    
                }} catch (e) {{
                    console.error('Export setup error:', e);
                    alert('Export failed: ' + e.message);
                }}
            }}
            
            // Initial fit
            setTimeout(function() {{
                fitNetwork();
            }}, 100);
        </script>
    </body>
    </html>
    """
    
    return html


def get_empty_state_html():
    """Generate HTML for empty state (before any data is analyzed)."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .empty-state {
                text-align: center;
                color: white;
                padding: 40px;
            }
            
            .empty-state h1 {
                font-size: 48px;
                margin-bottom: 20px;
            }
            
            .empty-state p {
                font-size: 20px;
                opacity: 0.9;
            }
            
            .icon {
                font-size: 80px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="empty-state">
            <div class="icon">🕸️</div>
            <h1>Fraud Ring Visualization</h1>
            <p>Enter your data in the sidebar and click "Detect Fraud Rings" to begin</p>
        </div>
    </body>
    </html>
    """
    return html

