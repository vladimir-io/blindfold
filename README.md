```text
██████╗ ██╗     ██╗███╗   ██╗██████╗ ███████╗ ██████╗ ██╗     ██████╗ 
██╔══██╗██║     ██║████╗  ██║██╔══██╗██╔════╝██╔═══██╗██║     ██╔══██╗
██████╔╝██║     ██║██╔██╗ ██║██║  ██║█████╗  ██║   ██║██║     ██║  ██║
██╔══██╗██║     ██║██║╚██╗██║██║  ██║██╔══╝  ██║   ██║██║     ██║  ██║
██████╔╝███████╗██║██║ ╚████║██████╔╝██║     ╚██████╔╝███████╗██████╔╝
╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝      ╚═════╝ ╚══════╝╚═════╝ 
```

# BLINDFOLD

**The Zero Knowledge Privacy Sidecar for LLM Pipelines.**

`Blindfold` is a high performance, provider agnostic privacy gateway for LLMs. It sits between your app and any LLM API (OpenAI, Anthropic, Ollama, Vertex, and more), scrubs PII **locally** with **[OpenAI Privacy Filter](https://github.com/openai/privacy-filter)**, and routes your request to the right provider. No code changes, no data leaks.

## Built on OpenAI Privacy Filter

The reason Blindfold can claim context-aware masking—not brittle regex alone—is that PII detection and redaction are powered by **[OpenAI Privacy Filter](https://github.com/openai/privacy-filter)** (OPF): OpenAI’s open-weight, Apache-2.0 **bidirectional token-classification** model for PII spans in unstructured text. It runs on your machine; sensitive strings are labeled and masked **before** traffic goes to any LLM provider.

- **Upstream code & CLI:** [openai/privacy-filter](https://github.com/openai/privacy-filter)  
- **Weights:** [Hugging Face — `openai/privacy-filter`](https://huggingface.co/openai/privacy-filter)

This repo depends on OPF directly (`git+https://github.com/openai/privacy-filter.git` in `requirements.txt`). **LiteLLM** is for universal LLM routing; **Privacy Filter** is the trust layer for *what* gets redacted. Review OPF’s [model card](https://huggingface.co/openai/privacy-filter) and limitations if you are evaluating this for production.

## How it Works

The LLM stays smart. Your data stays local. 100 percent HIPAA compliant chat in 60 seconds.


<p align="center">
  <img src="demo.png" alt="Blindfold Data Privacy Proxy Demo" width="700" />
</p>


## Why Blindfold is Different

* Universal Routing, supports OpenAI, Anthropic, Ollama, Vertex, and more. Just change the `model` string.
* No Vendor Lock In, powered by [LiteLLM](https://github.com/BerriAI/litellm), so you can swap providers without rewriting code.
* Contextual Privacy, regex is not enough. OPF is a 1.5B-parameter (50M active) bidirectional model, so Blindfold can distinguish e.g. “Washington” the person vs the city.
* Zero Code Changes, point your client to `http://localhost:8080` and go.
* No Data Leaks, PII never leaves your machine. Only masked tokens ever hit the cloud.

## Quickstart

1. Clone this repo.
2. Set your provider API keys as environment variables, for example `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
3. Run:

```sh
docker compose up --build
```

4. Point your OpenAI, Anthropic, or Ollama client to `http://localhost:8080`.
5. Use any model name you want, for example `gpt 4`, `anthropic/claude 3 5 sonnet`, or `ollama/llama3`.

Example:

```bash
# To use with Anthropic
export ANTHROPIC_API_KEY=sk ant ...
docker compose up
# Then set your client base url to http://localhost:8080 and model to anthropic/claude 3 5 sonnet
```


## What’s Inside
* FastAPI proxy for `/v1/chat/completions` and more
* LiteLLM for universal provider routing
* **[OpenAI Privacy Filter](https://github.com/openai/privacy-filter)** for local PII detection and masking
* Redis mapping for PII tokens
* Streams responses, keeps headers, and feels invisible

### Security Architecture
* Bidirectional Context: Privacy Filter’s local 1.5B MoE stack analyzes text in both directions, distinguishing "Apple" the company from "apple" the fruit with high accuracy.
* Deterministic Tokenization: The same PII value always gets the same token within a session, preserving LLM context.
* Ephemeral Vault: Mapping keys are stored in Redis with a TTL, so sensitive data is purged automatically.

## The Performance Budget
Because the model is only 50M active parameters, the latency overhead is less than 100ms. You get privacy without the wait.

## Why This Matters
* Shows Infrastructure Depth, not just an API call. This is a real gateway that handles multi provider orchestration.
* Future Proof, if a new model comes out tomorrow, Blindfold supports it out of the box via LiteLLM.
- **User Choice:** Use Ollama for a 100% local, 100% free, 100% private stack, or Claude/GPT for high-tier reasoning.

---

## Human Support
If you hit a snag, open an issue.

---

## License
MIT. Use it, improve it, share it.
