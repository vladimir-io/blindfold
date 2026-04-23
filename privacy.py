import os
import re
import json
import redis
from typing import Tuple, Dict, List
from transformers import pipeline


import os
import redis
import json
from opf import Redactor

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def load_redactor():
    try:
        checkpoint_path = os.getenv("OPF_CHECKPOINT", "~/.opf/privacy_filter")
        return Redactor(checkpoint=checkpoint_path, device="cpu")
    except Exception as e:
        print(f"[Blindfold] OPF Native Load Failed: {e}")
        return None

redactor = load_redactor()

def redact_pii(body: dict):
    messages = body.get("messages", [])
    mapping = {}
    for msg in messages:
        content = msg.get("content", "")
        if not content:
            continue
        result = redactor.redact(content)
        for span in sorted(result.spans, key=lambda x: x.start, reverse=True):
            original_value = content[span.start:span.end]
            label = span.label
            if original_value not in mapping.values():
                idx = len(mapping) + 1
                token = f"<{label.upper()}_{idx}>"
                mapping[token] = original_value
            else:
                token = [k for k, v in mapping.items() if v == original_value][0]
            content = content[:span.start] + token + content[span.end:]
        msg["content"] = content
    return body, mapping

def store_mapping(request_id: str, mapping):
    redis_client.setex(f"blindfold:{request_id}", 3600, json.dumps(mapping))

def get_mapping(request_id: str):
    val = redis_client.get(f"blindfold:{request_id}")
    if val:
        return json.loads(val)
    return {}

def unredact_pii(text: str, mapping):
    for token in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(token, mapping[token])
    return text
    return json.loads(data) if data else {}

def unredact_pii(text: str, mapping: Dict[str, str]) -> str:
    if not mapping:
        return text
    # Sort by length descending to prevent partial token replacement (e.g., <NAME_10> vs <NAME_1>)
    for token in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(token, mapping[token])
    return text