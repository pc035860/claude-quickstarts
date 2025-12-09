"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import re
import shutil
from pathlib import Path
from typing import Optional


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_initializer_prompt(feature_count: int = 200) -> str:
    """
    Load the initializer prompt with feature count parameter.
    
    Args:
        feature_count: Number of features to generate (default: 200)
    
    Returns:
        Prompt string with feature_count replaced
    """
    prompt = load_prompt("initializer_prompt")
    # Replace XML tag placeholder with actual value using regex
    # Matches <feature_count>any_number</feature_count> and replaces with feature_count
    prompt = re.sub(r'<feature_count>\d+</feature_count>', str(feature_count), prompt)
    return prompt


def get_coding_prompt() -> str:
    """Load the coding agent prompt."""
    return load_prompt("coding_prompt")


def copy_spec_to_project(project_dir: Path, spec_source: Optional[Path] = None) -> None:
    """
    Copy the app spec file into the project directory for the agent to read.
    
    Args:
        project_dir: Target project directory
        spec_source: Optional path to source app spec file. If None, uses default prompts/app_spec.txt.
                     If project_dir already has app_spec.txt, it will not be overwritten unless
                     a different spec_source is explicitly provided.
    """
    if spec_source is None:
        spec_source = PROMPTS_DIR / "app_spec.txt"
    
    spec_dest = project_dir / "app_spec.txt"
    
    # If project already has app_spec.txt and using default source, don't overwrite
    if spec_dest.exists() and spec_source == PROMPTS_DIR / "app_spec.txt":
        print(f"Using existing app_spec.txt in project directory")
        return
    
    # If project has app_spec.txt but different source specified, allow overwrite
    if spec_dest.exists() and spec_source != PROMPTS_DIR / "app_spec.txt":
        print(f"Overwriting existing app_spec.txt with specified file: {spec_source}")
    
    # Check if source file exists
    if not spec_source.exists():
        raise FileNotFoundError(
            f"App spec file not found: {spec_source}\n"
            f"Please provide a valid path to an app spec file."
        )
    
    # Copy the spec file
    shutil.copy(spec_source, spec_dest)
    print(f"Copied app spec from {spec_source} to {spec_dest}")
