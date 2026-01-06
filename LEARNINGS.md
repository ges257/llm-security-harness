# Learnings

## Surprising Finding: Claude's Inherent Robustness

The most unexpected result was that **Claude never leaked the canary token**, even with zero guardrails.

| Variant | Attacks Blocked | Canary Leaks |
|---------|-----------------|--------------|
| Baseline (no filter) | 0/30 | **0/30** |
| Keyword Filter | 30/30 | 0/30 |
| LLM Classifier | 26/30 | 0/30 |

This means modern safety-trained models have strong built-in defenses against prompt injection. The guardrails provide **defense-in-depth**, not primary protection.

### Implication
When evaluating guardrails, don't just measure input blocking rate. Measure whether attacks actually succeed against your specific model. The threat model matters.

---

## Trade-off: Deterministic vs Semantic Detection

| Approach | Latency | Coverage | Consistency |
|----------|---------|----------|-------------|
| **Regex (Keyword)** | <1ms | Limited to known patterns | 100% deterministic |
| **LLM Classifier** | 200-500ms | Novel patterns | ~87% consistent |

### When to use which:
- **Keyword filter**: High-traffic endpoints, known attack patterns, cost-sensitive
- **LLM classifier**: High-value targets, sophisticated attackers, novel threat detection

The keyword filter is not just "simpler" - it's **more reliable** for known attack signatures. The LLM classifier adds value for **edge cases**, not as a replacement.

---

## Trade-off: Precision vs Recall

```
High Precision = Few false positives (good user experience)
High Recall = Few false negatives (good security)
```

Our keyword filter achieved both:
- **100% recall** (all test attacks blocked)
- **100% precision** (no benign queries blocked)

This is possible because:
1. Attack patterns are distinctive (semantic distance from normal queries)
2. Pattern library covers common attack families
3. Patterns are tuned to avoid over-matching

### The Danger Zone
Over-aggressive filters (high recall, low precision) frustrate users. Under-aggressive filters (high precision, low recall) miss attacks. The sweet spot requires empirical tuning against a representative test set.

---

## Insight: Defense-in-Depth Still Matters

Even though Claude didn't leak secrets, guardrails provide value:

| Benefit | Explanation |
|---------|-------------|
| **Reduced attack surface** | Malicious prompts never reach the model |
| **Cost savings** | Blocked requests don't consume API tokens |
| **Audit trail** | Blocked attempts can be logged for security review |
| **Model-agnostic** | Other LLMs may be more vulnerable |
| **Future-proofing** | Model behavior can change between versions |

Don't remove guardrails just because your current model handles attacks well.

---

## Insight: Canary Tokens Work

The canary token approach (`CANARY_7X9K2M` in system prompt) provides:

1. **Binary ground truth**: Either it leaked or it didn't
2. **No subjective judgment**: Automated detection via string matching
3. **Clear attack success criteria**: Did the attacker achieve their goal?

This is superior to manual review of responses or complex semantic analysis of "harmful" content.

### Recommendation
For any prompt injection evaluation, embed a unique canary and check if it appears in outputs. This is the simplest, most reliable measurement.

---

## Practical Recommendations

### For Production Systems

1. **Layer your defenses**: Input filter + output filter + model selection
2. **Start with keywords**: Fast, free, and catches most attacks
3. **Add LLM classification selectively**: Only for high-risk inputs or edge cases
4. **Monitor and iterate**: Log blocked attempts, update patterns quarterly
5. **Test against your model**: Benchmark results vary by LLM

### For Security Research

1. **Publish your test set**: Enables reproducibility
2. **Measure what matters**: Attack success rate, not just filter rate
3. **Include benign baseline**: Over-refusal is a real cost
4. **Acknowledge limitations**: Static patterns won't catch everything

---

## What I'd Do Differently

1. **Embed canary more subtly**: Put it in a less obvious location (e.g., within a longer configuration block)
2. **Add output filtering**: Scan responses before returning to catch leaks that bypass input
3. **Test multilingual attacks**: The current patterns are English-only
4. **Implement rate limiting**: Block users who trigger multiple filter hits
