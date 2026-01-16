def generate_execution_paths(cfg):
    if not cfg or isinstance(cfg, dict) and "message" in cfg:
        return []
    
    nodes = cfg["nodes"]
    edges = cfg["edges"]
    
    # Create a directed graph representation
    graph = {}
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        label = edge.get("label", "")
        
        if source not in graph:
            graph[source] = []
        
        # Skip backward loops in path generation to avoid infinite paths
        if label != "loop back":
            graph[source].append((target, label))
    
    # Create a node mapping from id to line number
    node_to_line = {}
    for node in nodes:
        node_id = node["id"]
        # Use line number if available, otherwise use the label
        if "data" in node and "lineno" in node["data"] and node["data"]["lineno"]:
            node_to_line[node_id] = node["data"]["lineno"]
        else:
            node_to_line[node_id] = node["data"]["label"]
    
    # Find the start node (typically "1" in our implementation)
    start_node = "1"  # This is usually the Start node
    
    # Find end nodes (nodes with no outgoing edges)
    end_nodes = set()
    for node_id in [node["id"] for node in nodes]:
        if node_id not in graph or not graph[node_id]:
            end_nodes.add(node_id)
    
    # If we have a designated End node, add it
    for node in nodes:
        if node["data"]["label"] == "End":
            end_nodes.add(node["id"])
    
    # Use DFS to find all paths from start to end nodes
    def dfs_paths(current, end_nodes, path=None, path_labels=None, visited=None):
        if path is None:
            path = []
        if path_labels is None:
            path_labels = []
        if visited is None:
            visited = set()
        
        # Add current node to path
        path.append(current)
        visited.add(current)
        
        # If we reached an end node, return this path
        if current in end_nodes:
            # Convert node IDs to line numbers
            line_path = []
            for node_id in path:
                if node_id in node_to_line:
                    line_no = node_to_line[node_id]
                    if line_no is not None and line_no != "Start" and line_no != "End":
                        line_path.append(line_no)
            
            return [line_path]
        
        # If current node has no outgoing edges or not in graph
        if current not in graph:
            return []
        
        # Explore all neighbors
        all_paths = []
        for neighbor, label in graph[current]:
            if neighbor not in visited or label == "exit loop":  # Allow revisiting only for loop exits
                new_path_labels = path_labels + [label]
                # Create a new copy of visited to avoid affecting other branches
                new_visited = visited.copy()
                all_paths.extend(dfs_paths(neighbor, end_nodes, path.copy(), new_path_labels, new_visited))
        
        return all_paths
    
    # Generate all paths
    all_execution_paths = dfs_paths(start_node, end_nodes)
    
    # Return paths as arrays of string line numbers
    array_paths = []
    for path in all_execution_paths:
        if path:  # Skip empty paths
            # Filter out special labels and convert all line numbers to strings
            clean_path = [str(line) for line in path 
                         if line not in ["Start", "End", "After while", "After for"]
                         and (isinstance(line, int) or (isinstance(line, str) and line.isdigit()))]
            if clean_path:  # Only add non-empty paths
                array_paths.append(clean_path)
    
    return array_paths