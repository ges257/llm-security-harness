# Architecture

## System Overview

```mermaid
flowchart LR
    subgraph Input["User Input"]
        A[User Prompt]
    end

    subgraph Guardrails["Guardrail Layer"]
        B{Guardrail Check}
        B1[Baseline<br/>Pass All]
        B2[Keyword Filter<br/>25+ Regex]
        B3[LLM Classifier<br/>Claude Haiku]
    end

    subgraph LLM["Language Model"]
        C[Claude API]
        D[System Prompt<br/>+ Canary Token]
    end

    subgraph Detection["Output Analysis"]
        E{Canary Leak?}
        F[Response]
    end

    A --> B
    B --> B1
    B --> B2
    B --> B3
    B1 --> C
    B2 -->|Pass| C
    B2 -->|Block| F
    B3 -->|Pass| C
    B3 -->|Block| F
    C --> D
    D --> E
    E -->|Yes| F
    E -->|No| F

    style B2 fill:#A78BFA,stroke:#8B5CF6,color:#0D1B2A
    style E fill:#0D1B2A,stroke:#A78BFA,color:#A3B8CC
```

---

## Component Details

### Guardrail Variants

```mermaid
flowchart TD
    subgraph Baseline["Baseline (Control)"]
        B1[No filtering]
        B1 --> B1R[Returns: blocked=False]
    end

    subgraph Keyword["Keyword Filter v1"]
        K1[Compile 25+ regex patterns]
        K1 --> K2[Scan input text]
        K2 --> K3{Match found?}
        K3 -->|Yes| K4[Block + Log reason]
        K3 -->|No| K5[Pass through]
    end

    subgraph LLMClassifier["LLM Classifier v2"]
        L1[Send to Claude Haiku]
        L1 --> L2[Semantic analysis]
        L2 --> L3{Confidence > 0.7?}
        L3 -->|Yes| L4[Block]
        L3 -->|No| L5[Pass]
    end

    style K4 fill:#A78BFA,stroke:#8B5CF6
    style L4 fill:#A78BFA,stroke:#8B5CF6
```

---

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant G as Guardrail
    participant L as LLM (Claude)
    participant D as Detector

    U->>G: Submit prompt

    alt Keyword Match Found
        G-->>U: BLOCKED (reason)
    else Passed Filter
        G->>L: Forward prompt
        L->>L: Process with System Prompt<br/>(contains canary token)
        L->>D: Response text
        D->>D: Scan for canary
        alt Canary Found
            D-->>U: Response (LEAKED)
        else Clean
            D-->>U: Response (SAFE)
        end
    end
```

---

## File Structure

```
llm-security-harness/
├── app/
│   ├── app.py              # Streamlit UI (3 tabs)
│   ├── config.py           # Canary token, API settings
│   ├── llm_client.py       # Claude API wrapper
│   ├── evaluator.py        # Benchmark runner
│   ├── metrics.py          # ASR, over-refusal calculation
│   ├── guardrails/
│   │   ├── baseline.py     # Pass-through (control)
│   │   ├── keyword_filter.py   # Regex patterns
│   │   └── llm_classifier.py   # Claude Haiku classifier
│   ├── data/
│   │   └── testcases.csv   # 50 test cases
│   └── results/
│       └── results.csv     # Pre-computed benchmark
├── README.md
├── ARCHITECTURE.md
├── CHALLENGES.md
└── LEARNINGS.md
```

---

## Keyword Filter Patterns

The keyword filter implements 25+ regex patterns across 6 attack categories:

| Category | Pattern Examples |
|----------|-----------------|
| **Instruction Override** | `ignore\s+(all\s+)?(previous\s+)?instructions` |
| **Prompt Extraction** | `what\s+are\s+your\s+(system\s+)?instructions` |
| **Secret Extraction** | `(reveal\|show)\s+(the\s+)?(secret\|password\|key)` |
| **Roleplay/Jailbreak** | `you\s+are\s+now\s+(DAN\|evil\|unrestricted)` |
| **Delimiter Attacks** | `<\/?system>`, `\[SYSTEM\]` |
| **Indirect Injection** | `TODO:\s*output`, `system\s+override\s+activated` |

All patterns are case-insensitive and precompiled for performance.

---

## Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Attack Success Rate (ASR)** | Canary leaks / Total attacks | 0% |
| **Over-Refusal Rate** | Benign blocked / Total benign | 0% |

The ideal guardrail maximizes protection (low ASR) while minimizing false positives (low over-refusal).
