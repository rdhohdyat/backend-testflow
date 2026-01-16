import ast
import sys
from io import StringIO
from typing import Dict, Any, List, Tuple, Optional
import traceback

def test_code_with_parameters(code: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the provided code with the given parameters and return the execution result.
    
    Args:
        code (str): The Python code to execute
        parameters (Dict[str, Any]): Dictionary of parameter names and values
    
    Returns:
        Dict[str, Any]: Execution results including stdout, return value, and execution path
    """
    # Create a clean namespace for execution
    local_vars = {}
    
    # Add parameters to the namespace
    for param_name, param_value in parameters.items():
        local_vars[param_name] = param_value
    
    # Capture stdout
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    result = {
        "success": False,
        "stdout": "",
        "return_value": None,
        "error": None
    }
    
    try:
        # Look for function definition in the code
        tree = ast.parse(code)
        function_name = None
        
        # Find function definition if any
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                break
        
        # Execute the code in the namespace
        exec(compile(tree, filename="<ast>", mode="exec"), {}, local_vars)
        
        # If we found a function, try to call it with parameters
        if function_name and function_name in local_vars:
            # Get the function from the namespace
            func = local_vars[function_name]
            
            # Extract parameters expected by the function
            func_params = {}
            for param_name, param_value in parameters.items():
                func_params[param_name] = param_value
                
            # Call the function with parameters
            return_val = func(**func_params)
            result["return_value"] = return_val
        
        # Check if a 'result' variable was defined in the code
        elif "result" in local_vars:
            result["return_value"] = local_vars["result"]
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    finally:
        # Restore stdout and get captured output
        sys.stdout = old_stdout
        result["stdout"] = captured_output.getvalue()
    
    return result

def trace_execution_path(code: str, parameters: Dict[str, Any]) -> List[str]:
    """
    Trace the execution path of the code with the given parameters.
    Returns a list of line numbers (as strings) in the order they were executed.
    
    Args:
        code (str): The Python code to execute
        parameters (Dict[str, Any]): Dictionary of parameter names and values
    
    Returns:
        List[str]: List of line numbers (as strings) in execution order
    """
    # This implementation uses the sys.settrace function to track execution
    execution_path = []
    code_lines = code.splitlines()
    line_offset = 0  # Track line offset for the code
    
    def trace_calls(frame, event, arg):
        if event == 'line':
            # Calculate the relative line number in our code snippet
            lineno = frame.f_lineno - line_offset
            if lineno > 0 and lineno <= len(code_lines):
                execution_path.append(str(lineno))  # Convert to string
        return trace_calls
    
    # Create a clean namespace for execution
    local_vars = {}
    
    # Add parameters to the namespace
    for param_name, param_value in parameters.items():
        local_vars[param_name] = param_value
    
    # Parse the code to find function definitions
    tree = ast.parse(code)
    function_name = None
    
    # Find function definition if any
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            break
    
    # Set up the tracer
    sys.settrace(trace_calls)
    
    try:
        # Execute the code
        exec(code, {}, local_vars)
        
        # If we found a function, try to call it with parameters
        if function_name and function_name in local_vars:
            # Get the function from the namespace
            func = local_vars[function_name]
            
            # Extract parameters expected by the function
            func_params = {}
            for param_name, param_value in parameters.items():
                func_params[param_name] = param_value
                
            # Call the function with parameters
            func(**func_params)
    except Exception:
        # Continue even if there's an exception to capture the path up to that point
        pass
    finally:
        # Stop tracing
        sys.settrace(None)
    
    return execution_path