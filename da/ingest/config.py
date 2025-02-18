
import os
from typing import List, Union
from pydantic import BaseModel, Field
import simplejson

class Config(BaseModel):
    framework:str = Field(default="python", description="Development framework")
    version: str = Field(default="", description="Language version")
    base_url: str = Field(default="", description="Base URL")
    only_current_dir: bool = Field(default=False, description="Only current directory"),
    exclude: List[str] = Field(default=[], description="Exclude files")
    ingester: str = Field(default="", description="Ingester")

def load_config(filepath: Union[str, None] = None) -> List[Config]:
    # if filepath == None:
    #     print(os.path.join(os.path.dirname(__file__), "config.json"))
    #     filepath == os.path.join(os.path.dirname(__file__), "config.json")
    filepath = filepath if filepath else os.path.join(os.path.dirname(__file__), "config.json")
    configs = []
    print(filepath)
    with open(filepath, "r") as f:
        configs = simplejson.load(f)

    return [Config(**c) for c in configs]
