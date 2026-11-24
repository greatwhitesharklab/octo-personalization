# Secret / IP audit — octo-personalization

Pre-publication sweep (M7 discipline, mirrors huamao-memory-bench docs/SECRET_AUDIT.md).

| Check | Status |
|---|---|
| Hardcoded `/home/fredgu` / NFS paths in distributed code | ✅ none (model path is a CLI arg; backend imports are package-relative) |
| AutoDL token / SSH password / proxy_host / instance ids | ✅ none |
| JEV / MaaS / typesafe API keys | ✅ none (judges here are script-level, no API) |
| Real customer data | ✅ none — all cases synthetic, non-commercial |
| Model weights / adapter weights | ✅ none distributed (.gitignore blocks *.pt/*.bin/*.safetensors; base Qwen3.5 Apache-2.0, download yourself) |
| MemT / thesis / client artifacts | ✅ excluded |
| Sibling-repo dependency | optional `huamao_bkv` import guarded by try/except; repo runs without it (RagBackend) |

## Notes
- `octo/memory.py` BkvBackend imports `huamao_bkv` lazily; absent → clear ImportError pointing to the sibling repo.
- Benchmark `--model` is a required CLI argument; no path baked in.
- Raw run logs / results.json are gitignored; only code + synthetic cases + docs are published.
