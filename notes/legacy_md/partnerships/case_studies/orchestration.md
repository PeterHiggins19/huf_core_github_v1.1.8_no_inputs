# LangChain / LlamaIndex — retrieval callback → coherence report

## Why it fits
Orchestrators already intercept retrieval results per query. That is the ideal hook point:

- export per-query retrieval to JSONL
- run HUF coherence audit
- attach the artifacts to your evaluation/logging pipeline

## Output to emphasize
- per-query `items_to_cover_90pct` trends over time
- “top regimes changed” alerts (dominance drift)
