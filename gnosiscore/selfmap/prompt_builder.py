"""
SelfmapPromptBuilder: Generates archetypal prompt/context for Cline LLM node.

Given a node (Primitive), plane, selfmap, and memory, extracts:
- archetype (node label/type)
- plane
- neighbors (labels)
- outgoing paths (path names)
- available actions/plugins
- recent memory/emotion

Assembles a prompt with explicit options and JSON schema for LLM input.
"""

from typing import List, Dict, Any
from uuid import UUID

class SelfmapPromptBuilder:
    def __init__(self, selfmap, memory=None):
        self.selfmap = selfmap
        self.memory = memory

    def build_prompt(self, node, plane: str, available_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Archetype
        archetype = getattr(node, "label", None) or getattr(node, "type", None) or "Unknown"
        # Neighbors (UUIDs to labels)
        neighbor_uuids = self.selfmap.neighbors(node.id)
        neighbors = []
        for nuid in neighbor_uuids:
            n = self.selfmap.get_node(nuid)
            neighbors.append(getattr(n, "label", None) or getattr(n, "type", None) or str(nuid))
        # Outgoing paths (connections from node)
        paths = []
        for conn in self.selfmap.all_connections():
            if conn.content.get("source") == node.id:
                path_name = conn.content.get("name") or conn.type or str(conn.id)
                paths.append(path_name)
        # Recent memory/emotion
        recent_memory = []
        prior_emotion = None
        if self.memory and hasattr(self.memory, "query_recent"):
            recent_memory = self.memory.query_recent()
        if hasattr(node, "content") and isinstance(node.content, dict):
            prior_emotion = node.content.get("emotion")
        # Prompt assembly
        prompt = (
            f"You are {archetype} in the {plane} plane of a digital mind.\n"
            f"You have the following options available:\n"
            f"- Paths: {paths}\n"
            f"- Actions: {[a['type'] + ':' + a['target'] for a in available_actions]}\n"
            f"- Neighbors: {neighbors}\n\n"
            "When choosing actions, ONLY select from the options explicitly provided above.\n"
            "Consider your archetypal context, recent memory, and prior emotion.\n"
            "Return ONLY valid JSON with this schema:\n"
            "{\n"
            '  "archetype": "<your node label>",\n'
            '  "plane": "<Digital|Mental|Metaphysical|...>",\n'
            '  "situation": {\n'
            '    "neighbors": [<neighbor1>, ...],\n'
            '    "active_paths": [<path1>, ...],\n'
            '    "recent_memory": [<...>],\n'
            '    "prior_emotion": "<...>"\n'
            '  },\n'
            '  "thought": "<your synthesized observation or intention>",\n'
            '  "emotion": "<archetypal or compound emotion>",\n'
            '  "intention": "<short statement of what you seek, attempt, or want to transform>",\n'
            '  "actions": [\n'
            '    {\n'
            '      "type": "<invoke_path|reflect|change_plane|update_memory|invoke_plugin|...>",\n'
            '      "target": "<node/path/plugin>",\n'
            '      "args": [],\n'
            '      "kwargs": {}\n'
            '    }\n'
            '  ]\n'
            "}\n"
            "Respond ONLY with valid JSON as specified above."
        )
        # Context dict for LLM call
        context = {
            "archetype": archetype,
            "plane": plane,
            "neighbors": neighbors,
            "active_paths": paths,
            "available_actions": available_actions,
            "recent_memory": recent_memory,
            "prior_emotion": prior_emotion,
        }
        return {"prompt": prompt, "context": context}
