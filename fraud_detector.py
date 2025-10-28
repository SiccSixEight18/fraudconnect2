"""
Fraud Ring Detector - Core matching logic and risk scoring
"""
import pandas as pd
from collections import defaultdict
from typing import List, Dict, Tuple, Any
import json


class FraudRingDetector:
    """
    Detects fraud rings by finding clients who share common features
    and calculates risk scores based on connection patterns.
    """
    
    # Apple-inspired color palette (soft, elegant, muted tones)
    COLOR_PALETTE = [
        '#007AFF',  # Apple Blue (primary)
        '#FF9500',  # Apple Orange (softer)
        '#AF52DE',  # Apple Purple
        '#5AC8FA',  # Apple Teal
        '#FF3B30',  # Apple Red (softer)
        '#FFCC00',  # Apple Yellow
        '#34C759',  # Apple Green
        '#FF2D55',  # Apple Pink
        '#5856D6',  # Apple Indigo
        '#00C7BE',  # Apple Mint
        '#BF5AF2',  # Apple Violet
        '#FF6482',  # Apple Coral
        '#64D2FF',  # Apple Cyan
        '#30B0C7',  # Apple Ocean
        '#AC8E68',  # Apple Brown
        '#A2845E',  # Apple Sand
        '#8E8E93',  # Apple Gray
        '#636366',  # Apple Charcoal
        '#98989D',  # Apple Silver
        '#7C7C80',  # Apple Steel
    ]

    # Default field colors (Apple-inspired palette)
    FIELD_COLORS = {
        'client_id': '#007AFF',    # Apple Blue
        'device_id': '#FF9500',    # Apple Orange
        'password': '#AF52DE',     # Apple Purple
        'ip': '#5AC8FA',           # Apple Teal
        'phone_number': '#FF3B30', # Apple Red
        'affiliate_source': '#34C759' # Apple Green
    }
    
    def __init__(self, field_names=None):
        """
        Initialize the detector with configurable field names.
        
        Args:
            field_names: List of field names to use for matching
                        If None, uses default 6 fields
                        Can be any number of fields!
        """
        self.clients = []
        self.connections = []
        self.nodes = []
        self.edges = []
        self.communities = {}
        
        # Set field names
        if field_names is None:
            # Default 6 fields
            self.all_fields = ['client_id', 'device_id', 'password', 'ip', 'phone_number', 'affiliate_source']
        elif isinstance(field_names, dict):
            # Legacy format: dict with 'required' and 'optional'
            self.all_fields = field_names.get('required', []) + field_names.get('optional', [])
        else:
            # New format: simple list of field names
            self.all_fields = field_names if isinstance(field_names, list) else list(field_names)
        
        # Initialize field display names (can be overridden later)
        self.field_display_names = {}
        
        # Assign colors to each field
        self._assign_field_colors()
    
    def _assign_field_colors(self):
        """Assign colors to each field type."""
        self.field_color_map = {}
        
        for i, field_name in enumerate(self.all_fields):
            # Use default colors if available, otherwise cycle through palette
            if field_name in self.FIELD_COLORS:
                self.field_color_map[field_name] = self.FIELD_COLORS[field_name]
            else:
                # Cycle through color palette
                color_index = i % len(self.COLOR_PALETTE)
                self.field_color_map[field_name] = self.COLOR_PALETTE[color_index]
    
    def get_field_colors(self) -> Dict[str, str]:
        """Get the color mapping for fields with data only."""
        # Only include fields that have at least one non-empty value
        fields_with_data = {}
        for field, color in self.field_color_map.items():
            if field in self.df.columns:
                # Check if field has any data
                if self.df[field].notna().any() and (self.df[field] != '').any():
                    # Use custom display name if available
                    if self.field_display_names and field in self.field_display_names:
                        display_name = self.field_display_names[field]
                    else:
                        display_name = field.replace('_', ' ').title()
                    fields_with_data[display_name] = color
        return fields_with_data
        
    def process_data(self, field_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Process input data and detect fraud rings.
        
        Args:
            field_data: Dictionary mapping field names to lists of values
                       e.g., {'client_id': [...], 'device_id': [...], ...}
            
        Returns:
            Dictionary containing nodes and edges for visualization
        """
        # Clean and prepare data
        df = self._prepare_dataframe(field_data)
        
        # Find matches and build connections
        self._find_connections(df)
        
        # Calculate risk scores
        self._calculate_risk_scores()
        
        # Build graph structure
        return self._build_graph_data()
    
    def _prepare_dataframe(self, field_data: Dict[str, List[str]]) -> pd.DataFrame:
        """Prepare and clean input data into a DataFrame."""
        # Find max length across all fields
        max_len = max([len(v) for v in field_data.values()] + [0])
        
        if max_len == 0:
            # Create empty dataframe with columns
            df = pd.DataFrame(columns=['row_id'] + self.all_fields)
            self.df = df
            return df
        
        # Create base dataframe with row IDs
        df_data = {'row_id': range(1, max_len + 1)}
        
        # Add each field, padding shorter lists
        for field_name in self.all_fields:
            if field_name in field_data and field_data[field_name]:
                data = field_data[field_name]
                # Pad to max length
                data = data + [''] * (max_len - len(data))
                # Clean and normalize
                df_data[field_name] = [str(v).strip().lower() if v else '' for v in data]
            else:
                # Field not provided, fill with empty strings
                df_data[field_name] = [''] * max_len
        
        df = pd.DataFrame(df_data)
        
        # Remove rows where all feature fields are empty
        df = df[df[self.all_fields].ne('').any(axis=1)]
        df = df.reset_index(drop=True)
        
        self.df = df
        return df
    
    def _find_connections(self, df: pd.DataFrame):
        """Find all connections between clients based on shared features."""
        connections = []
        
        # Build index for each feature
        feature_index = defaultdict(list)
        
        for idx, row in df.iterrows():
            for feature in self.all_fields:
                if feature not in df.columns:
                    continue
                value = row[feature]
                if value and value != '' and value not in ['nan', 'none', 'null']:
                    feature_index[f"{feature}:{value}"].append(row['row_id'])
        
        # Find connections where 2+ clients share a feature
        seen_pairs = set()
        
        for feature_key, client_ids in feature_index.items():
            if len(client_ids) >= 2:
                feature_type, feature_value = feature_key.split(':', 1)
                
                # Create edges between all pairs
                for i, client1 in enumerate(client_ids):
                    for client2 in client_ids[i+1:]:
                        pair = tuple(sorted([client1, client2]))
                        
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            connections.append({
                                'source': pair[0],
                                'target': pair[1],
                                'feature_type': feature_type,
                                'feature_value': feature_value,
                                'shared_features': [feature_type]
                            })
                        else:
                            # Add to existing connection
                            for conn in connections:
                                if ((conn['source'] == pair[0] and conn['target'] == pair[1]) or
                                    (conn['source'] == pair[1] and conn['target'] == pair[0])):
                                    if feature_type not in conn['shared_features']:
                                        conn['shared_features'].append(feature_type)
                                    break
        
        self.connections = connections
    
    def _calculate_risk_scores(self):
        """Calculate fraud risk scores for each client."""
        # Count connections per client
        connection_count = defaultdict(int)
        shared_features_count = defaultdict(list)
        
        for conn in self.connections:
            connection_count[conn['source']] += 1
            connection_count[conn['target']] += 1
            shared_features_count[conn['source']].extend(conn['shared_features'])
            shared_features_count[conn['target']].extend(conn['shared_features'])
        
        # Calculate risk scores
        risk_scores = {}
        
        for client_id in self.df['client_id']:
            # Base score on number of connections
            num_connections = connection_count.get(client_id, 0)
            
            # Risk factors
            connection_score = min(num_connections * 15, 60)  # Max 60 points from connections
            
            # Feature diversity score (sharing multiple types is riskier)
            unique_features = len(set(shared_features_count.get(client_id, [])))
            feature_diversity_score = min(unique_features * 10, 30)  # Max 30 points
            
            # Frequency score (if a client shares many features, higher risk)
            feature_frequency = len(shared_features_count.get(client_id, []))
            frequency_score = min(feature_frequency * 2, 10)  # Max 10 points
            
            total_score = connection_score + feature_diversity_score + frequency_score
            risk_scores[client_id] = min(total_score, 100)
        
        self.risk_scores = risk_scores
        self.connection_count = connection_count
    
    def _build_graph_data(self) -> Dict[str, Any]:
        """Build the final graph structure for Vis.js."""
        # First, calculate the number of unique feature types each node is connected by
        node_feature_types = {}
        for conn in self.connections:
            source = conn['source']
            target = conn['target']
            features = set(conn['shared_features'])
            
            if source not in node_feature_types:
                node_feature_types[source] = set()
            if target not in node_feature_types:
                node_feature_types[target] = set()
            
            node_feature_types[source].update(features)
            node_feature_types[target].update(features)
        
        nodes = []
        
        for _, row in self.df.iterrows():
            row_id = row['row_id']
            risk_score = self.risk_scores.get(row_id, 0)
            num_connections = self.connection_count.get(row_id, 0)
            
            # Determine color based on number of TYPES of connections (feature types)
            # Apple-inspired soft, elegant node colors
            num_feature_types = len(node_feature_types.get(row_id, set()))
            
            if num_feature_types == 1:
                color = '#B4E4FF'  # Soft Blue - 1 feature type (Apple light blue)
                risk_level = 'Low'
            elif num_feature_types == 2:
                color = '#88C9FF'  # Medium Blue - 2 feature types (Apple blue)
                risk_level = 'Medium'
            else:  # 3+ feature types
                color = '#007AFF'  # Apple Blue - 3+ feature types (signature Apple blue)
                risk_level = 'High'
            
            # Build label - use first field's value as the entity name
            label = f"Row {row_id}"  # Default fallback
            if self.all_fields and len(self.all_fields) > 0:
                first_field = self.all_fields[0]
                if first_field in row and row[first_field]:
                    label = str(row[first_field])[:30]  # Use first field value, max 30 chars
            
            # Build tooltip with all fields
            title = f"<b>{label}</b><br>"
            title += f"Risk Score: {risk_score:.0f} ({risk_level})<br>"
            title += f"Connections: {num_connections}<br>"
            title += "<hr>"
            
            # Add all field values to tooltip with custom display names
            for field_name in self.all_fields:
                if field_name in row and row[field_name]:
                    # Use custom display name if available
                    if self.field_display_names and field_name in self.field_display_names:
                        display_name = self.field_display_names[field_name]
                    else:
                        display_name = field_name.replace('_', ' ').title()
                    title += f"<b>{display_name}:</b> {row[field_name]}<br>"
            
            nodes.append({
                'id': int(row_id),
                'label': label,
                'title': title,
                'color': color,
                'size': 24,  # Fixed size for all nodes
                'risk_score': risk_score,
                'connections': num_connections,
                'feature_types': num_feature_types,
                'risk_level': risk_level
            })
        
        # Build edges with color based on field type
        edges = []
        for i, conn in enumerate(self.connections):
            # Use display names if available, otherwise format field names
            if self.field_display_names:
                shared_display = ', '.join([
                    self.field_display_names.get(f, f.replace('_', ' ').title()) 
                    for f in conn['shared_features']
                ])
            else:
                shared_display = ', '.join([f.replace('_', ' ').title() for f in conn['shared_features']])
            
            edge_title = f"Shared: {shared_display}<br>"
            if len(conn['shared_features']) == 1:
                edge_title += f"Value: {conn['feature_value']}"
            
            shared = shared_display  # Use display names in edge label too
            
            # Determine edge color based on primary shared feature
            primary_feature = conn['shared_features'][0]
            edge_color = self.field_color_map.get(primary_feature, '#848484')
            
            # If multiple features, use magenta
            if len(conn['shared_features']) > 1:
                edge_color = '#AF52DE'  # Apple Purple for multiple feature types
            
            edges.append({
                'id': i,
                'from': int(conn['source']),
                'to': int(conn['target']),
                'title': edge_title,
                'width': len(conn['shared_features']) * 2,  # Thicker for multiple features
                'label': shared if len(conn['shared_features']) <= 2 else f"{len(conn['shared_features'])} features",
                'shared_features': conn['shared_features'],
                'color': edge_color
            })
        
        self.nodes = nodes
        self.edges = edges
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def get_high_risk_clients(self, threshold: int = 50) -> pd.DataFrame:
        """Get a DataFrame of high-risk clients."""
        high_risk = []
        
        for node in self.nodes:
            if node['risk_score'] >= threshold:
                client_data = self.df[self.df['row_id'] == node['id']].iloc[0]
                row_dict = {
                    'Row ID': node['id'],
                    'Risk Score': node['risk_score'],
                    'Risk Level': node['risk_level'],
                    'Connections': node['connections'],
                }
                
                # Add all field values
                for field_name in self.all_fields:
                    display_name = field_name.replace('_', ' ').title()
                    row_dict[display_name] = client_data.get(field_name, '')
                
                high_risk.append(row_dict)
        
        return pd.DataFrame(high_risk).sort_values('Risk Score', ascending=False) if high_risk else pd.DataFrame()
    
    def get_connection_details(self) -> pd.DataFrame:
        """Get a DataFrame of all connections."""
        details = []
        
        for edge in self.edges:
            details.append({
                'Client 1': edge['from'],
                'Client 2': edge['to'],
                'Shared Features': ', '.join(edge['shared_features']),
                'Feature Count': len(edge['shared_features'])
            })
        
        return pd.DataFrame(details)
    
    def filter_graph(self, min_risk: int = 0, feature_types: List[str] = None) -> Dict[str, Any]:
        """
        Filter the graph based on risk score and feature types.
        
        Args:
            min_risk: Minimum risk score to include
            feature_types: List of feature types to include (e.g., ['email', 'phone'])
        
        Returns:
            Filtered graph data with recalculated node colors
        """
        # Filter nodes by risk
        filtered_nodes = [n.copy() for n in self.nodes if n['risk_score'] >= min_risk]
        filtered_node_ids = {n['id'] for n in filtered_nodes}
        
        # Filter edges by feature types and node presence
        filtered_edges = []
        if feature_types:
            for edge in self.edges:
                # Check if edge connects filtered nodes
                if edge['from'] in filtered_node_ids and edge['to'] in filtered_node_ids:
                    # Check if edge has any of the selected feature types
                    if any(ft in edge['shared_features'] for ft in feature_types):
                        filtered_edges.append(edge)
        else:
            # No feature filter, just use node filter
            filtered_edges = [e for e in self.edges 
                            if e['from'] in filtered_node_ids and e['to'] in filtered_node_ids]
        
        # Recalculate feature types based on filtered edges
        node_feature_types = {}
        for edge in filtered_edges:
            source = edge['from']
            target = edge['to']
            features = set(edge['shared_features'])
            
            if source not in node_feature_types:
                node_feature_types[source] = set()
            if target not in node_feature_types:
                node_feature_types[target] = set()
            
            node_feature_types[source].update(features)
            node_feature_types[target].update(features)
        
        # Update node colors based on filtered feature types
        for node in filtered_nodes:
            num_feature_types = len(node_feature_types.get(node['id'], set()))
            
            # ALWAYS update the feature_types to reflect filtered state
            node['feature_types'] = num_feature_types
            
            # Update color based on filtered feature types (Apple-inspired soft colors)
            if num_feature_types == 0:
                # No connections in filtered view - make it very light gray
                node['color'] = '#E5E5EA'  # Apple System Gray 5
                node['risk_level'] = 'None'
            elif num_feature_types == 1:
                node['color'] = '#B4E4FF'  # Soft Blue (Apple light blue)
                node['risk_level'] = 'Low'
            elif num_feature_types == 2:
                node['color'] = '#88C9FF'  # Medium Blue (Apple blue)
                node['risk_level'] = 'Medium'
            else:  # 3+
                node['color'] = '#007AFF'  # Apple Blue (signature)
                node['risk_level'] = 'High'
        
        return {
            'nodes': filtered_nodes,
            'edges': filtered_edges
        }
    
    def export_to_json(self) -> str:
        """Export graph data to JSON string."""
        return json.dumps({
            'nodes': self.nodes,
            'edges': self.edges,
            'metadata': {
                'total_clients': len(self.nodes),
                'total_connections': len(self.edges),
                'high_risk_count': len([n for n in self.nodes if n['risk_score'] >= 80])
            }
        }, indent=2)

