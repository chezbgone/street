import dataclasses
from dataclasses import dataclass
import json
from typing import Any

@dataclass
class TwitchMessage:
    metadata: dict[str, Any]
    display_name: str
    content: str

    def encode(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def decode(cls, o: str) -> 'TwitchMessage':
        data = json.loads(o)
        for key in ['metadata', 'display_name', 'content']:
            if key not in data:
                msg = f'error decoding TwitchMessage: key {key} not found'
                raise ValueError(msg)
        return TwitchMessage(data['metadata'], data['display_name'], data['content'])
