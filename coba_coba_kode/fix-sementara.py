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
    
    # Track branch depths and widths
    branch_stack = []
    
    # Track loops for backward edges
    loops = {}
    
    # Track try-except blocks
    try_blocks = {}
    
    # Track visited line numbers (for unreachable code detection)
    visited_lines = set()
    
    def get_position(depth=0, branch_index=0, is_else=False):
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
        
        display_text = lineno if lineno else label
        
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
        if any(e["source"] == source and e["target"] == target for e in edges):
            return
            
        edge_style = {
            "strokeWidth": 2, 
            "stroke": "#000000"
        }
        
        if is_loop:
            edge_style["stroke"] = "#E74C3C"  # Red color for loop edges
            edge_style["animated"] = True
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
            # Debug: Print seluruh node untuk melihat struktur AST sebenarnya
            print(f"DEBUG - Function node: {ast.dump(node)}")
            
            # 1. Mengambil list parameter dengan jelas dan eksplisit
            param_list = []
            for arg in node.args.args:
                # Pastikan arg.arg diambil sebagai string lengkap
                full_param_name = str(arg.arg)
                param_list.append(full_param_name)
                # Debug untuk melihat parameter yang diambil
                print(f"DEBUG - Parameter extracted: '{full_param_name}'")
            
            # 2. Memeriksa apakah nama parameter kosong atau hanya 1 karakter
            for i, param in enumerate(param_list):
                if not param or len(param) <= 1:
                    print(f"WARNING - Parameter at index {i} has suspicious length: '{param}'")
            
            # 3. Tambahkan informasi parameter lengkap ke daftar parameters
            parameters.append({"function": node.name, "params": param_list})
            
            # 4. Buat string parameter yang lengkap dengan pengecekan
            param_str = ", ".join(param_list) if param_list else ""
            func_label = f"def {node.name}({param_str}):"
            print(f"DEBUG - Final function label: '{func_label}'")

            func_pos = {"x": x_offset, "y": len(nodes) * y_spacing + 50}
            func_id = add_node(func_label, node.lineno, func_pos, "function")

            if parent_id is not None:
                create_edge(parent_id, func_id)

            loops[node.name] = func_id
            
            body_depth = depth + 1
            
            last_node = func_id
            
            # 5. Debug tambahan - dump node args lengkap
            print(f"DEBUG - Node args structure: {ast.dump(node.args)}")
            print(f"DEBUG - Extracted parameters: {param_list}")
            
            # Sisa kode tetap sama
            i = 0
            while i < len(node.body):
                stmt = node.body[i]
                result = visit(stmt, last_node, body_depth, 0)
                
                if isinstance(result, dict) and "if_node" in result:
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
                                create_edge(result["if_node"], next_id)
                        
                        last_node = next_id
                        
                        i += 2
                        continue
                    else:
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
            # Create if node with the actual if condition
            if_pos = get_position(depth, branch_index, is_else)
            if_condition = ast.unparse(node.test)
            if_id = add_node(f"if {if_condition}:", node.lineno, if_pos, "condition")
            
            if parent_id is not None:
                create_edge(parent_id, if_id)
            
            # Process true branch with offset to the right
            true_branch = None
            true_last = None
            branch_stack.append(True)
            for i, stmt in enumerate(node.body):
                true_branch = visit(stmt, if_id if i == 0 else true_branch, depth + 1, branch_index + 1)
                if i == len(node.body) - 1:
                    true_last = true_branch
            branch_stack.pop()
            
            # Process false branch with offset to the left
            false_branch = None
            false_last = None
            if node.orelse:
                branch_stack.append(False)
                for i, stmt in enumerate(node.orelse):
                    false_branch = visit(stmt, if_id if i == 0 else false_branch, depth + 1, branch_index + 1, True)
                    if i == len(node.orelse) - 1:
                        false_last = false_branch
                branch_stack.pop()
            
            # Add edges with labels and styles
            if true_branch:
                create_edge(if_id, true_branch, "true", False, "true")
            
            if false_branch:
                create_edge(if_id, false_branch, "false", False, "false")
            
            # Instead of creating a visible merge node, we'll return a "virtual" merge point
            # by returning both end points of the branches
            # This is done by creating a special object that will be handled by the parent caller
            if_else_ends = {
                "if_node": if_id,
                "true_end": true_last or if_id,
                "false_end": false_last or if_id,
                "has_else": bool(node.orelse)
            }
            
            # Return the special object for the parent caller to handle
            return if_else_ends


        elif isinstance(node, ast.While) or isinstance(node, ast.For):
    # Buat node untuk kondisi loop
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

            # Simpan id node awal loop
            first_body_node_id = None
            last_body_node_id = loop_id  # default fallback

            for i, stmt in enumerate(node.body):
                current_id = visit(stmt, last_body_node_id, depth + 1, branch_index + 1)
                if i == 0:
                    first_body_node_id = current_id
                last_body_node_id = current_id

            # Tambahkan edge balik ke node loop
            if first_body_node_id:
                create_edge(last_body_node_id, loop_id, "loop back", is_loop=True)

            # Setelah loop selesai, kita anggap keluar dari loop
            return loop_id

        elif isinstance(node, ast.Try):
            # Handle try-except-finally blocks
            try_pos = get_position(depth, branch_index, is_else)
            try_id = add_node("try:", node.lineno, try_pos, "try")
            
            if parent_id is not None:
                create_edge(parent_id, try_id)
            
            # Remember try block for exception handlers
            try_blocks[try_id] = {"handlers": []}
            
            # Process try body
            try_body_last = try_id
            for stmt in node.body:
                try_body_last = visit(stmt, try_body_last, depth + 1, branch_index)
            
            # Process except handlers
            for handler in node.handlers:
                handler_pos = get_position(depth, branch_index + 2, False)
                
                # Get exception type
                if handler.type:
                    exc_type = ast.unparse(handler.type)
                    exc_name = handler.name if handler.name else ""
                    handler_text = f"except {exc_type}" + (f" as {exc_name}" if exc_name else "") + ":"
                else:
                    handler_text = "except:"
                    
                handler_id = add_node(handler_text, handler.lineno, handler_pos, "except")
                try_blocks[try_id]["handlers"].append(handler_id)
                
                # Create edge from try to except
                create_edge(try_id, handler_id, "exception", False, "exception")
                
                # Process except body
                handler_last = handler_id
                for stmt in handler.body:
                    handler_last = visit(stmt, handler_last, depth + 1, branch_index + 2)
            
            # Process else clause if present
            else_last = None
            if node.orelse:
                else_pos = get_position(depth, branch_index + 1, True)
                else_id = add_node("else:", node.orelse[0].lineno if node.orelse else None, else_pos, "else")
                create_edge(try_body_last, else_id, "no exception")
                
                else_last = else_id
                for stmt in node.orelse:
                    else_last = visit(stmt, else_last, depth + 1, branch_index + 1)
            
            # Process finally if present
            finally_last = None
            if node.finalbody:
                finally_pos = get_position(depth, branch_index, False)
                finally_id = add_node("finally:", node.finalbody[0].lineno if node.finalbody else None, finally_pos, "finally")
                
                # Connect try body to finally
                if try_body_last:
                    create_edge(try_body_last, finally_id, "finally")
                
                # Connect all except handlers to finally
                for handler_id in try_blocks[try_id]["handlers"]:
                    create_edge(handler_id, finally_id, "finally")
                
                # Connect else to finally if present
                if else_last:
                    create_edge(else_last, finally_id, "finally")
                
                finally_last = finally_id
                for stmt in node.finalbody:
                    finally_last = visit(stmt, finally_last, depth + 1, branch_index)
                
                return finally_last
            
            # If no finally, return the last relevant node
            return finally_last or else_last or try_body_last or try_id

        elif isinstance(node, ast.With):
            # Handle with statements
            with_pos = get_position(depth, branch_index, is_else)
            
            # Format with statement
            items = []
            for item in node.items:
                context_expr = ast.unparse(item.context_expr)
                var = f" as {ast.unparse(item.optional_vars)}" if item.optional_vars else ""
                items.append(f"{context_expr}{var}")
            
            with_text = f"with {', '.join(items)}:"
            with_id = add_node(with_text, node.lineno, with_pos, "with")
            
            if parent_id is not None:
                create_edge(parent_id, with_id)
            
            # Process with body
            last_in_with = with_id
            for stmt in node.body:
                last_in_with = visit(stmt, last_in_with, depth + 1, branch_index)
            
            return last_in_with

        elif isinstance(node, ast.Return):
            # Position return statements slightly to the side based on nesting
            ret_pos = get_position(depth, branch_index, is_else)
            return_id = add_node(f"return {ast.unparse(node.value)}", node.lineno, ret_pos, "return")
            
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
            # Handle augmented assignments like x += 1
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
                
        elif isinstance(node, ast.Call):
            # Handle function calls, check if it's a loop to a known function
            call_pos = get_position(depth, branch_index, is_else)
            func_call = ast.unparse(node)
            call_id = add_node(func_call, getattr(node, 'lineno', None), call_pos, "call")
            
            if parent_id is not None:
                create_edge(parent_id, call_id)
            
            # Try to get the function name
            if hasattr(node.func, 'id'):
                func_name = node.func.id
                # If calling a known function (which could be recursive), add edge
                if func_name in loops:
                    create_edge(call_id, loops[func_name], "call", True)
                
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

    root_x = x_offset
    root_y = 50  # Starting Y position
    # Can comment out the following line if you don't want to display the "Start" node
    start_id = add_node("Start", None, {"x": root_x, "y": root_y}, "control")
    
    last_root = start_id
    for stmt in tree.body:
        last_root = visit(stmt, last_root)

    if nodes:
        end_pos = {"x": x_offset, "y": (len(nodes) + 1) * y_spacing}
        end_id = add_node("End", None, end_pos, "control")
        for last_node in last_nodes:
            create_edge(last_node, end_id)
    
    return nodes, edges, parameters 
