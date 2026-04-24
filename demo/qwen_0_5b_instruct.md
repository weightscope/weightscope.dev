# Model diff: `Qwen/Qwen2.5-0.5B` vs `Qwen/Qwen2.5-0.5B-Instruct`

Threshold: `abs(a - b) > 1e-06`

## Summary

- Total params compared: **494,032,768**
- Changed params: **483,814,955** (97.93%)
- Sparsity (unchanged fraction): **2.07%**
- Full model size: **942.3 MB**
- Sparse delta size (estimated): **2.7 GB**
- Compression ratio: **0.3x**

## Interpretation

> **Looks like a full retrain or independently trained model — almost every parameter moved.**
> *(classification: `full_retrain`, confidence: **medium**)*

### Facts

- **Parameter footprint.** 494,032,768 parameters compared across 290 tensor(s). 483,814,955 (97.93%) differ beyond the threshold of 1e-06.

### Why we think this

- 97.93% of parameters changed beyond threshold 1e-06.
- Attention changed 97.70%, MLP 97.79%, embed 98.33%.
- A LoRA or targeted fine-tune would leave most parameters untouched; this does not.

## Most-changed layer groups

| Layer prefix | Tensors | Params | Changed | % changed |
|---|---:|---:|---:|---:|
| `model.norm.weight` | 1 | 896 | 891 | 99.44% |
| `model.embed_tokens.weight` | 1 | 136,134,656 | 133,866,116 | 98.33% |
| `model.layers.11` | 12 | 14,912,384 | 14,616,539 | 98.02% |
| `model.layers.12` | 12 | 14,912,384 | 14,609,321 | 97.97% |
| `model.layers.10` | 12 | 14,912,384 | 14,608,313 | 97.96% |
| `model.layers.9` | 12 | 14,912,384 | 14,606,644 | 97.95% |
| `model.layers.13` | 12 | 14,912,384 | 14,606,103 | 97.95% |
| `model.layers.14` | 12 | 14,912,384 | 14,600,377 | 97.91% |
| `model.layers.15` | 12 | 14,912,384 | 14,597,009 | 97.89% |
| `model.layers.8` | 12 | 14,912,384 | 14,594,954 | 97.87% |
| `model.layers.16` | 12 | 14,912,384 | 14,593,087 | 97.86% |
| `model.layers.17` | 12 | 14,912,384 | 14,589,337 | 97.83% |
| `model.layers.18` | 12 | 14,912,384 | 14,585,348 | 97.81% |
| `model.layers.7` | 12 | 14,912,384 | 14,577,675 | 97.76% |
| `model.layers.19` | 12 | 14,912,384 | 14,575,579 | 97.74% |

## Top tensors by absolute change

| Tensor | Shape | Params | Changed | % changed | Max delta |
|---|---|---:|---:|---:|---:|
| `model.embed_tokens.weight` | 151936x896 | 136,134,656 | 133,866,116 | 98.33% | 0.01904 |
| `model.layers.12.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,276,640 | 98.13% | 0.01733 |
| `model.layers.13.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,275,763 | 98.11% | 0.02051 |
| `model.layers.11.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,275,458 | 98.10% | 0.01367 |
| `model.layers.10.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,275,064 | 98.09% | 0.01562 |
| `model.layers.14.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,274,766 | 98.09% | 0.01562 |
| `model.layers.9.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,273,252 | 98.05% | 0.01367 |
| `model.layers.15.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,272,325 | 98.03% | 0.01553 |
| `model.layers.11.mlp.down_proj.weight` | 896x4864 | 4,358,144 | 4,271,687 | 98.02% | 0.01562 |
| `model.layers.10.mlp.up_proj.weight` | 4864x896 | 4,358,144 | 4,270,960 | 98.00% | 0.01233 |
| `model.layers.12.mlp.down_proj.weight` | 896x4864 | 4,358,144 | 4,270,514 | 97.99% | 0.01172 |
| `model.layers.10.mlp.down_proj.weight` | 896x4864 | 4,358,144 | 4,270,080 | 97.98% | 0.01855 |
| `model.layers.11.mlp.up_proj.weight` | 4864x896 | 4,358,144 | 4,270,025 | 97.98% | 0.01562 |
| `model.layers.8.mlp.gate_proj.weight` | 4864x896 | 4,358,144 | 4,269,989 | 97.98% | 0.01233 |
| `model.layers.9.mlp.down_proj.weight` | 896x4864 | 4,358,144 | 4,269,418 | 97.96% | 0.01172 |

---
> Need private diffs on your own checkpoints, hosted history, or signed compliance reports? See https://weightscope.dev