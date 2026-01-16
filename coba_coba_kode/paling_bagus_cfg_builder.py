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
    
def extract_cfg(tree):
    nodes = []
    edges = []
    parameters = []
    node_id = 1
    last_nodes = []
    
    # Track the current horizontal position and depth for better positioning
    x_offset = 300  # Base X position
    y_spacing = 80  # Vertical spacing between nodes
    x_spacing = 100  # Horizontal spacing for branches
    
    # Track loops for backward edges
    loop_stack = []
    
    # Track try-except blocks
    try_blocks = {}
    
    # Track visited line numbers (for unreachable code detection)
    visited_lines = set()
    
    def get_position(depth=0, branch_index=0, is_else=False):
        branch_offset = branch_index * (x_spacing + (depth * 5))
        if is_else:
            x = x_offset - branch_offset
        else:
            x = x_offset + branch_offset
        y = len(nodes) * y_spacing + 50
        
        return {"x": x, "y": y}

    def add_node(label, lineno=None, pos=None, node_type="default"):
        nonlocal node_id

        if pos is None:
            pos = get_position()
   
        tooltip = label
        
        # Only show line number for display, keep full code in tooltip
        if lineno:
            display_text = str(lineno)
        else:
            display_text = label
        
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
            
        if any(e["source"] == source and e["target"] == target for e in edges):
            return
            
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
            edge_style["strokeDasharray"] = "5,5"  # Dashed line for exceptions
        elif edge_type == "true":
            edge_style["stroke"] = "#2ECC71"  # Green for true conditions
        elif edge_type == "false":
            edge_style["stroke"] = "#3498DB"  # Blue for false conditions
            
        edges.append({
            "id": f"e{source}-{target}",
            "source": str(source),
            "target": str(target),
            "markerEnd": {"type": "arrowclosed", "color": edge_style["stroke"]},
            "style": edge_style,
            **({"label": label} if label else {})
        })

    def visit(node, parent_id=None, depth=0, branch_index=0, is_else=False):
        if isinstance(node, ast.FunctionDef):
            # Extract parameters
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
            
            # Process function body sequentially
            for stmt in node.body:
                result = visit(stmt, last_node, body_depth, 0)
                if isinstance(result, dict) and "merge_point" in result:
                    last_node = result["merge_point"]
                else:
                    last_node = result
            
            return func_id

        elif isinstance(node, ast.If):
            # Create if node
            if_pos = get_position(depth, branch_index, is_else)
            if_condition = ast.unparse(node.test)
            if_id = add_node(f"if {if_condition}:", node.lineno, if_pos, "condition")
            
            if parent_id is not None:
                create_edge(parent_id, if_id)
            
            # Process true branch
            true_last = if_id
            for stmt in node.body:
                true_last = visit(stmt, true_last, depth + 1, branch_index + 1)
                if isinstance(true_last, dict) and "merge_point" in true_last:
                    true_last = true_last["merge_point"]
            
            # Create edge to true branch - only if there's a body
            if node.body:
                create_edge(if_id, true_last if true_last != if_id else if_id, "true", False, "true")
            
            # Process false branch (else)
            false_last = if_id
            if node.orelse:
                for stmt in node.orelse:
                    false_last = visit(stmt, false_last, depth + 1, branch_index + 1, True)
                    if isinstance(false_last, dict) and "merge_point" in false_last:
                        false_last = false_last["merge_point"]
                
                # Create edge to false branch - only if there's an else body
                create_edge(if_id, false_last if false_last != if_id else if_id, "false", False, "false")
            
            # Return merge point info
            return {
                "merge_point": true_last if not node.orelse else false_last,
                "if_node": if_id,
                "true_end": true_last,
                "false_end": false_last if node.orelse else if_id
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

            # Process loop body - FIXED: Only process, don't create duplicate edges
            body_last = loop_id
            for stmt in node.body:
                body_last = visit(stmt, body_last, depth + 1, branch_index + 1)
                if isinstance(body_last, dict) and "merge_point" in body_last:
                    body_last = body_last["merge_point"]
            
            # Create back edge from body end to loop header (only if there was a body)
            if body_last and body_last != loop_id:
                create_edge(body_last, loop_id, "loop back", is_loop=True)
            
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
                if isinstance(try_last, dict) and "merge_point" in try_last:
                    try_last = try_last["merge_point"]
            
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
                    if isinstance(handler_last, dict) and "merge_point" in handler_last:
                        handler_last = handler_last["merge_point"]
            
            # Process else clause if present
            if node.orelse:
                else_pos = get_position(depth, branch_index + 1, True)
                else_id = add_node("else:", node.orelse[0].lineno if node.orelse else None, else_pos, "else")
                create_edge(try_last, else_id, "no exception")
                
                else_last = else_id
                for stmt in node.orelse:
                    else_last = visit(stmt, else_last, depth + 1, branch_index + 1)
                    if isinstance(else_last, dict) and "merge_point" in else_last:
                        else_last = else_last["merge_point"]
                
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
        result = visit(stmt, last_root)
        if isinstance(result, dict) and "merge_point" in result:
            last_root = result["merge_point"]
        else:
            last_root = result

    # Create end node and connect all final nodes
    if nodes:
        end_pos = {"x": x_offset, "y": (len(nodes) + 1) * y_spacing}
        end_id = add_node("End", None, end_pos, "control")
        
        # Connect final nodes to end
        if last_root and last_root != end_id:
            create_edge(last_root, end_id)
        
        for final_node in last_nodes:
            if final_node and final_node != end_id:
                create_edge(final_node, end_id)
    
    return nodes, edges, parameters