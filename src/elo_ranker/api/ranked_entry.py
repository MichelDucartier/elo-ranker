from __future__ import annotations

from typing import Dict, Optional
import uuid

class RankedEntry:
    def __init__(self, title: str, 
                 attributes: Optional[Dict[str, str]] = None) -> None:
        self.title = title

        if attributes is None:
            attributes = dict()

        self.attributes = attributes
        self._uid = str(uuid.uuid4())

    def uid(self) -> str:
        return self._uid
                
    def __str__(self) -> str:
        return f"RankedEntry(title={self.title})"

        
