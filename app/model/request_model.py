from pydantic import BaseModel
from typing import List, Dict, Any, Tuple, Set, Optional, Union

class CodeRequest(BaseModel):
    code: str

class TestCaseRequest(BaseModel):
    code: str
    parameters: Dict[str, Any]
    
class ProjectCreate(BaseModel):
    name: str
    description: str = ""  # optional