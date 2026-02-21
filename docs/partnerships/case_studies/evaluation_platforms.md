# Arize / Weights & Biases / Ragas — composition audit layer

## Why it fits
Quality metrics answer “was the response good?”  
HUF answers “what drove the response?” (composition + discards).

## Integration path
- log HUF artifacts as run artifacts
- chart `items_to_cover_90pct` and top-regime mass over time
- attach `artifact_4_error_budget.json` as a governance ledger
