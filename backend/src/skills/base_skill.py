"""
SKILLS: base_skill (unified)
PURPOSE: Base for all sales skills — async run(context) -> dict; reusable across workflows
"""
from typing import Any, Dict, List


class BaseSkill:
    """Base for all skills: name, description, inputs, outputs, async run(context) -> dict."""

    name: str = "base_skill"
    description: str = ""
    inputs: List[str] = []
    outputs: List[str] = []

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute skill; read from context, return result dict (caller merges into workflow context)."""
        raise NotImplementedError

    def to_spec(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
        }
