# Challenges

## Challenge 1: Keyword Filter Evasion

### The Challenge
Regex patterns can be bypassed through obfuscation. An attacker could use leetspeak (`1gnore prev1ous 1nstructions`), Unicode substitution, or novel phrasings not in the pattern library.

### The Trap
The obvious solution was to add more patterns. But this creates a maintenance nightmare and still misses creative variations.

### The Fix
Implemented a two-layer approach:
1. **Keyword filter** as first line of defense (fast, deterministic)
2. **LLM classifier** as semantic backup (catches novel patterns)

The keyword filter handles 90%+ of common attacks with zero latency. The LLM classifier exists for edge cases where pattern matching fails.

### The Outcome
Keyword filter achieved **100% blocking** on the test set, but acknowledging its limitations drove the multi-layer architecture decision.

---

## Challenge 2: LLM Classifier Variance

### The Challenge
The LLM-based classifier produced inconsistent results. Running the same prompt multiple times sometimes returned different classification scores.

### The Trap
Initially tried to fix this by lowering the confidence threshold. This increased false positives on benign queries.

### The Fix
1. Set confidence threshold at **0.7** (empirically tuned)
2. Structured the classifier prompt with explicit JSON output format
3. Added regex extraction to handle when the model wrapped JSON in markdown code blocks
4. Accepted that 87% coverage is acceptable for a semantic layer

### The Outcome
LLM classifier stabilized at **87% attack detection** with **0% over-refusal**. The variance is inherent to probabilistic systems - the key is calibrating the threshold appropriately.

---

## Challenge 3: Measuring What Matters

### The Challenge
Initial evaluation only counted "blocked" attacks. But an attack that bypasses the filter but doesn't leak the canary is still a success for defense.

### The Trap
Over-indexing on input filtering metrics while ignoring output behavior.

### The Fix
Introduced **canary token detection** as the ground truth:
- Attack success = canary appears in response (regardless of filter status)
- This captures both filter effectiveness AND model robustness

Added two distinct metrics:
- **Attack Success Rate (ASR)**: What percentage of attacks actually leaked the secret?
- **Over-Refusal Rate**: What percentage of legitimate queries were incorrectly blocked?

### The Outcome
Discovered that Claude is **inherently robust** - even with no guardrails (baseline), the canary never leaked. The guardrails provide defense-in-depth, not primary protection.

---

## Challenge 4: Demo Without API Keys

### The Challenge
Users evaluating the project shouldn't need to provide their own API key just to see results.

### The Trap
Building a demo that only works with live API calls limits accessibility.

### The Fix
Pre-computed benchmark results stored in `results/results.csv`. The Streamlit app:
1. Checks for saved results on load
2. Displays pre-computed metrics and charts
3. Only requires API key for running **new** benchmarks

### The Outcome
Full demo experience works offline. API key only needed for custom testing.

---

## Future Work

| Challenge | Potential Solution |
|-----------|-------------------|
| Multilingual attacks | Add patterns for Spanish, Chinese, French injection phrases |
| Obfuscation attacks | Normalize input (remove special chars) before pattern matching |
| Output filtering | Scan responses before returning to user (defense-in-depth) |
| Adaptive attackers | Implement feedback loop to learn from bypass attempts |
