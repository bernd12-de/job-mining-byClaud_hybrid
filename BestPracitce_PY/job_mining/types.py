from dataclasses import dataclass, asdict
import json
@dataclass
class Post:
    source_id: str
    title: str|None
    company: str|None
    posting_date_iso: str|None
    posting_date_source: str|None = None
    posting_date_precision: str|None = None
    tools: list = None
    methods: list = None
    fields: dict = None
    text: str|None = None
    def to_json(self):
        return json.dumps(asdict(self), ensure_ascii=False)