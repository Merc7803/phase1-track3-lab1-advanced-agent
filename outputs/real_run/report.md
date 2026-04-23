# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpotQA_100.json
- Mode: live
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.95 | 1.0 | 0.05 |
| Avg attempts | 1 | 1.06 | 0.06 |
| Avg token estimate | 441.83 | 490.84 | 49.01 |
| Avg latency (ms) | 10577 | 2869.21 | -7707.79 |

## Failure modes
```json
{
  "none": 195,
  "wrong_final_answer": 0,
  "incomplete_multi_hop": 5,
  "entity_drift": 0,
  "looping": 0,
  "reflection_overfit": 0
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
