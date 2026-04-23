
import os
import uuid
import json
import uvicorn
from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse
from litellm import acompletion
from privacy import redact_pii, unredact_pii, store_mapping, get_mapping

app = FastAPI()

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request, x_request_id: str = Header(None)):
    body = await request.json()
    request_id = x_request_id or str(uuid.uuid4())
    redacted_body, mapping = redact_pii(body)
    store_mapping(request_id, mapping)

    async def stream_generator():
        response = await acompletion(**redacted_body, stream=True)
        buffer = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content or ""
            buffer += content
            if not any(buffer.endswith(t[:i]) for t in mapping.keys() for i in range(1, len(t))):
                unmasked_content = unredact_pii(buffer, mapping)
                chunk.choices[0].delta.content = unmasked_content
                yield f"data: {json.dumps(chunk.dict())}\n\n"
                buffer = ""
        if buffer:
            final_unmasked = unredact_pii(buffer, mapping)
            # Optionally yield the last chunk if needed
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")

@app.get("/health")
def health():
    return {"status": "protected", "engine": "OpenAI-Privacy-Filter-1.5b"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
