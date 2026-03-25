from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class GenerationProvider(Protocol):
    def generate_json(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass(slots=True)
class FakeGenerationProvider:
    responses: dict[str, Any]

    @classmethod
    def from_file(cls, path: Path) -> "FakeGenerationProvider":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("provider fixture must be a JSON object")
        return cls(responses=payload)

    def generate_json(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        _ = payload
        if task in self.responses:
            response = self.responses[task]
            if not isinstance(response, dict):
                raise ValueError(f"provider response for task '{task}' must be an object")
            return response
        return self.responses
