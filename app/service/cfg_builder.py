import ast
from typing import List, Dict, Any, Tuple, Set, Optional, Union

def build_cfg(code: str):
    try:
        tree = ast.parse(code)
        nodes, edges, parameters = extract_cfg(tree)
        return {
            "nodes": nodes,
            "edges": edges,
            "parameters": parameters
        }
    except Exception as e:
        return {"message": f"Error parsing code: {str(e)}"}

def get_operator_symbol(op):
    """Convert AST operator to symbol"""
    op_map = {
        ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
        ast.Mod: '%', ast.Pow: '**', ast.LShift: '<<', ast.RShift: '>>',
        ast.BitOr: '|', ast.BitXor: '^', ast.BitAnd: '&', ast.FloorDiv: '//'
    }
    return op_map.get(type(op), '?')

def get_exit_nodes(result):
    """Return actual exit nodes from a visit result (especially if it's an if structure)"""
    if isinstance(result, dict) and "if_node" in result:
        exit_nodes = []
        if result.get("true_end") != result["if_node"]:
            exit_nodes.append(result["true_end"])
        if result.get("has_else") and result.get("false_end") != result["if_node"]:
            exit_nodes.append(result["false_end"])
        return exit_nodes
    else:
        return [result]

    
def extract_cfg(tree):
    nodes = []
    edges = []
    parameters = []
    node_id = 1
    last_nodes = []
    
    # Visual layout settings
    x_offset = 300
    y_spacing = 80
    x_spacing = 100
    
    # Track loops and control structures
    loop_stack = []
    try_blocks = {}
    visited_lines = set()
    
    def get_position(depth=0, branch_index=0, is_else=False):
        """Better positioning logic"""
        branch_offset = branch_index * (x_spacing + (depth * 5))
        if is_else:
            x = x_offset - branch_offset + branch_offset
        else:
            x = x_offset + branch_offset
        y = len(nodes) * y_spacing + 50
        
        return {"x": x, "y": y}

    def add_node(label, lineno=None, pos=None, node_type="default"):
        nonlocal node_id

        if pos is None:
            pos = get_position()
   
        tooltip = label
        display_text = str(lineno) if lineno else label
        
        node = {
            "id": str(node_id),
            "type": "custom",
            "position": pos,
            "data": {
                "label": display_text, 
                "tooltip": tooltip,     
                "lineno": lineno,     
                "node_type": node_type  
            }
        }
        nodes.append(node)
        node_id += 1
        
        if lineno:
            visited_lines.add(lineno)
            
        return str(node_id - 1)

    def create_edge(source, target, label=None, is_loop=False, edge_type="default"):
        if source == target:  # Avoid self-loops
            return
            
        # === MODIFIKASI: Cek edge yang sudah ada & UPDATE labelnya ===
        existing_edge = next((e for e in edges if e["source"] == str(source) and e["target"] == str(target)), None)
        
        if existing_edge:
            # Jika edge sudah ada, tapi kita ingin memberi label baru (misal True/False)
            if label and not existing_edge.get("label"):
                existing_edge["label"] = label
                # Update warna jika perlu
                if edge_type == "true":
                    existing_edge["style"]["stroke"] = "#2ECC71"
                elif edge_type == "false":
                    existing_edge["style"]["stroke"] = "#EF4444"
            return
        # ==============================================================
            
        edge_style = {
            "strokeWidth": 2, 
            "stroke": "#000000"
        }
        
        if is_loop:
            edge_style["stroke"] = "#E74C3C"  # Red color for loop edges
            edge_style["animated"] = True
            edge_style["strokeWidth"] = 3
        elif edge_type == "exception":
            edge_style["stroke"] = "#F39C12"  # Orange for exception flow
            edge_style["strokeDasharray"] = "5,5"
        elif edge_type == "true":
            edge_style["stroke"] = "#2ECC71"  # Green for true conditions
        elif edge_type == "false":
            edge_style["stroke"] = "#EF4444"  # Red for false conditions (Ganti ke Merah agar sesuai frontend)
        
        # FIXED: Always include label if provided
        edge_data = {
            "id": f"e{source}-{target}",
            "source": str(source),
            "target": str(target),
            "markerEnd": {"type": "arrowclosed", "color": edge_style["stroke"]},
            "style": edge_style
        }
        
        # Add label if provided
        if label:
            edge_data["label"] = label
            
        edges.append(edge_data)

    def visit(node, parent_id=None, depth=0, branch_index=0, is_else=False):
        if isinstance(node, ast.FunctionDef):
            # Extract parameters cleanly
            param_list = []
            for arg in node.args.args:
                param_list.append(str(arg.arg))
            
            parameters.append({"function": node.name, "params": param_list})
            
            param_str = ", ".join(param_list) if param_list else ""
            func_label = f"def {node.name}({param_str}):"

            func_pos = {"x": x_offset, "y": len(nodes) * y_spacing + 50}
            func_id = add_node(func_label, node.lineno, func_pos, "function")

            if parent_id is not None:
                create_edge(parent_id, func_id)

            body_depth = depth + 1
            last_node = func_id
            
            # Process function body with better flow control
            i = 0
            while i < len(node.body):
                stmt = node.body[i]
                result = visit(stmt, last_node, body_depth, 0)
                
                if isinstance(result, dict) and "if_node" in result:
                    # Handle if-else blocks with proper merging
                    if i + 1 < len(node.body):
                        next_stmt = node.body[i + 1]
                        next_result = visit(next_stmt, None, body_depth, 0)
                        
                        if isinstance(next_result, str):
                            next_id = next_result
                        elif isinstance(next_result, dict) and "if_node" in next_result:
                            next_id = next_result["if_node"]
                        else:
                            next_id = next_result 
                        
                        if next_id is not None:
                            create_edge(result["true_end"], next_id)
                            if result["has_else"]:
                                create_edge(result["false_end"], next_id)
                            else:
                                create_edge(result["if_node"], next_id, "False", False, "false")
                        
                        last_node = next_id
                        i += 2
                        continue
                    else:
                        # End of function body
                        last_nodes.append(result["true_end"])
                        if result["has_else"]:
                            last_nodes.append(result["false_end"])
                        else:
                            last_nodes.append(result["if_node"])
                        
                        last_node = result["true_end"]
                else:
                    last_node = result
                
                i += 1

            if last_node not in last_nodes:
                last_nodes.append(last_node)
            
            return func_id

        elif isinstance(node, ast.If):
            # Create if node with better positioning
            if_pos = get_position(depth, branch_index, is_else)
            if_condition = ast.unparse(node.test)
            if_id = add_node(f"if {if_condition}:", node.lineno, if_pos, "condition")
            
            if parent_id is not None:
                create_edge(parent_id, if_id)
            
            # Process true branch
            true_branch = None
            true_last = None
            for i, stmt in enumerate(node.body):
                # Saat i=0, parent adalah if_id. visit() akan otomatis membuat edge.
                true_branch = visit(stmt, if_id if i == 0 else true_branch, depth + 1, branch_index + 1)
                
                # === MODIFIKASI: Tambahkan Label True ke edge pertama ===
                if i == 0:
                    # Ambil ID target (jika result dict, ambil if_node-nya)
                    target_id = true_branch["if_node"] if isinstance(true_branch, dict) and "if_node" in true_branch else true_branch
                    # Update edge yang baru saja dibuat dengan label True
                    create_edge(if_id, target_id, "True", False, "true")
                # ========================================================
                
                if i == len(node.body) - 1:
                    true_last = true_branch
            
            # Process false branch
            false_branch = None
            false_last = None
            if node.orelse:
                for i, stmt in enumerate(node.orelse):
                    false_branch = visit(stmt, if_id if i == 0 else false_branch, depth + 1, branch_index + 1, True)
                    
                    # === MODIFIKASI: Tambahkan Label False ke edge pertama Else ===
                    if i == 0:
                        target_id = false_branch["if_node"] if isinstance(false_branch, dict) and "if_node" in false_branch else false_branch
                        create_edge(if_id, target_id, "False", False, "false")
                    # =============================================================
                    
                    if i == len(node.orelse) - 1:
                        false_last = false_branch
            
            # Return structure for proper merging
            return {
                "if_node": if_id,
                "true_end": true_last or if_id,
                "false_end": false_last or if_id,
                "has_else": bool(node.orelse)
            }

        elif isinstance(node, ast.While) or isinstance(node, ast.For):
            # Create loop header node
            loop_pos = get_position(depth, branch_index, is_else)
            
            if isinstance(node, ast.While):
                loop_condition = ast.unparse(node.test)
                loop_text = f"while {loop_condition}:"
            else:
                loop_target = ast.unparse(node.target)
                loop_iter = ast.unparse(node.iter)
                loop_text = f"for {loop_target} in {loop_iter}:"
            
            loop_id = add_node(loop_text, node.lineno, loop_pos, "loop")

            if parent_id is not None:
                create_edge(parent_id, loop_id)

            # Push loop info onto stack
            loop_stack.append(loop_id)

            # Process loop body - FIXED VERSION
            last_body_node_id = loop_id
            final_body_node = None
            
            for i, stmt in enumerate(node.body):
                result = visit(stmt, last_body_node_id, depth + 1, branch_index + 1)
                
                # For chaining statements in loop body
                if isinstance(result, dict) and "if_node" in result:
                    # Handle if-else inside loop
                    exit_nodes = get_exit_nodes(result)
                    final_body_node = exit_nodes[-1] if exit_nodes else result["if_node"]
                else:
                    final_body_node = result
                
                last_body_node_id = final_body_node

            # Create only ONE back edge from the final node of loop body
            if final_body_node and final_body_node != loop_id:
                create_edge(final_body_node, loop_id, "loop back", is_loop=True)

            # Pop loop from stack
            loop_stack.pop()
            
            return loop_id

        elif isinstance(node, ast.Try):
            # Handle try-except-finally blocks
            try_pos = get_position(depth, branch_index, is_else)
            try_id = add_node("try:", node.lineno, try_pos, "try")
            
            if parent_id is not None:
                create_edge(parent_id, try_id)
            
            # Process try body
            try_last = try_id
            for stmt in node.body:
                try_last = visit(stmt, try_last, depth + 1, branch_index)
            
            # Process except handlers
            for handler in node.handlers:
                handler_pos = get_position(depth, branch_index + 2, False)
                
                if handler.type:
                    exc_type = ast.unparse(handler.type)
                    exc_name = handler.name if handler.name else ""
                    handler_text = f"except {exc_type}" + (f" as {exc_name}" if exc_name else "") + ":"
                else:
                    handler_text = "except:"
                    
                handler_id = add_node(handler_text, handler.lineno, handler_pos, "except")
                
                # Create edge from try to except
                create_edge(try_id, handler_id, "exception", False, "exception")
                
                # Process except body
                handler_last = handler_id
                for stmt in handler.body:
                    handler_last = visit(stmt, handler_last, depth + 1, branch_index + 2)
            
            # Process else clause if present
            if node.orelse:
                else_pos = get_position(depth, branch_index + 1, True)
                else_id = add_node("else:", node.orelse[0].lineno if node.orelse else None, else_pos, "else")
                create_edge(try_last, else_id, "no exception")
                
                else_last = else_id
                for stmt in node.orelse:
                    else_last = visit(stmt, else_last, depth + 1, branch_index + 1)
                
                return else_last
            
            return try_last

        elif isinstance(node, ast.Return):
            ret_pos = get_position(depth, branch_index, is_else)
            return_value = ast.unparse(node.value) if node.value else ""
            return_id = add_node(f"return {return_value}", node.lineno, ret_pos, "return")
            
            if parent_id is not None:
                create_edge(parent_id, return_id)
                
            last_nodes.append(return_id)
            return return_id

        elif isinstance(node, ast.Assign):
            assign_code = f"{ast.unparse(node.targets[0])} = {ast.unparse(node.value)}"
            assign_pos = get_position(depth, branch_index, is_else)
            assign_id = add_node(assign_code, node.lineno, assign_pos, "assignment")
            
            if parent_id is not None:
                create_edge(parent_id, assign_id)
                
            return assign_id

        elif isinstance(node, ast.AugAssign):
            target = ast.unparse(node.target)
            op = get_operator_symbol(node.op)
            value = ast.unparse(node.value)
            assign_code = f"{target} {op}= {value}"
            
            assign_pos = get_position(depth, branch_index, is_else)
            assign_id = add_node(assign_code, node.lineno, assign_pos, "assignment")
            
            if parent_id is not None:
                create_edge(parent_id, assign_id)
                
            return assign_id

        elif isinstance(node, ast.Expr):
            expr_pos = get_position(depth, branch_index, is_else)
            expr_label = ast.unparse(node)
            expr_id = add_node(expr_label, node.lineno, expr_pos, "expression")
            
            if parent_id is not None:
                create_edge(parent_id, expr_id)
                
            return expr_id

        elif isinstance(node, ast.Break):
            break_pos = get_position(depth, branch_index, is_else)
            break_id = add_node("break", node.lineno, break_pos, "break")
            
            if parent_id is not None:
                create_edge(parent_id, break_id)
            
            return break_id

        elif isinstance(node, ast.Continue):
            continue_pos = get_position(depth, branch_index, is_else)
            continue_id = add_node("continue", node.lineno, continue_pos, "continue")
            
            if parent_id is not None:
                create_edge(parent_id, continue_id)
            
            # Continue goes back to loop header
            if loop_stack:
                create_edge(continue_id, loop_stack[-1], "continue", is_loop=True)
            
            return continue_id
                
        elif isinstance(node, ast.Call):
            call_pos = get_position(depth, branch_index, is_else)
            func_call = ast.unparse(node)
            call_id = add_node(func_call, getattr(node, 'lineno', None), call_pos, "call")
            
            if parent_id is not None:
                create_edge(parent_id, call_id)
                
            return call_id
        
        # Default for other node types
        else:
            node_pos = get_position(depth, branch_index, is_else)
            try:
                node_label = ast.unparse(node)
            except:
                node_label = f"{type(node).__name__}"
                
            new_id = add_node(node_label, getattr(node, 'lineno', None), node_pos)
            
            if parent_id is not None:
                create_edge(parent_id, new_id)
                
            return new_id

    # Create start node
    root_x = x_offset
    root_y = 50
    start_id = add_node("Start", None, {"x": root_x, "y": root_y}, "control")
    
    # Process all statements in the AST
    last_root = start_id
    for stmt in tree.body:
        last_root = visit(stmt, last_root)

    # Create end node and connect all final nodes
    if nodes:
        end_pos = {"x": x_offset, "y": (len(nodes) + 1) * y_spacing}
        end_id = add_node("End", None, end_pos, "control")
        
        # Connect final nodes to end
        for final_node in last_nodes:
            if final_node and final_node != end_id:
                create_edge(final_node, end_id)
    
    return nodes, edges, parameters