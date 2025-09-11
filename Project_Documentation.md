# AI-Powered Multi-Agent System for Industry Research, Use Case Generation, and Dataset Resource Mapping

## Introduction
This project delivers an end-to-end, AI-powered market research system that automates: industry/company research, generation of high-impact AI/GenAI use cases, and mapping of each use case to relevant datasets/resources (Kaggle, HuggingFace, GitHub). It increases speed, consistency, and coverage for strategy, product, and data teams.

## System Architecture (High-Level)
- Research Agent: Finds industries, segments, offerings, strategy, trends, competitors.
- Use Case Agent: Produces 10 detailed, distribution-constrained development use cases.
- Resource Agent: Collects 3–6 high-quality resources per use case from Kaggle/HF/GitHub.
- Orchestrator: Coordinates agents, handles fallbacks, saves reports and datasets mapping.

---

## Research Agent Workflow Diagram
```mermaid
flowchart TD
  %% Styling
  classDef agent fill:#eef6ff,stroke:#8bbcff,stroke-width:1px,color:#0b2e6f
  classDef tool fill:#f6ffec,stroke:#8ad28a,stroke-width:1px,color:#0b5f1a
  classDef llm fill:#fff2d6,stroke:#ffb84d,stroke-width:1px,color:#663c00
  classDef io fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,color:#0f172a

  subgraph Input & Guardrails
    A[Company Name]:::io --> B[Sanitizer & Validator\n(XSS/SQL patterns, charset)]:::agent
    B --> C[PII Scrubber (optional)]:::agent
  end

  subgraph Retrieval & Context
    C --> D[Tavily Search Tool\n(LangChain Tool)]:::tool
    D --> E[Content Normalizer\n(Clean HTML/JSON)]:::agent
    E --> F[Optional RAG Chunking\n(TextSplitter → Embeddings → VectorStore)]:::agent
  end

  subgraph Reasoning & Structuring
    F --> G[PromptTemplate\n(LangChain)]:::agent
    G --> H[LLM: GPT-4o]:::llm
    H --> I[Structured Output Parser\n(JSONSchema / Pydantic)]:::agent
  end

  subgraph Outputs
    I --> J[Company Analysis JSON\n(business model, offerings, segments)]:::io
    I --> K[Industry Analysis JSON\n(trends, opportunities, competitors)]:::io
    I --> L[Citations]:::io
  end
```

### Research Agent – Inputs, Process, Outputs
- Inputs: Company name
- Process: Validation/PII scrub → Search via Tavily → (optional RAG) → LLM with PromptTemplate → Structured JSON via OutputParser
- Outputs: `company_analysis`, `industry_analysis`, citations

---

## Use Case Agent Workflow Diagram
```mermaid
flowchart TD
  classDef agent fill:#eef6ff,stroke:#8bbcff,stroke-width:1px,color:#0b2e6f
  classDef llm fill:#fff2d6,stroke:#ffb84d,stroke-width:1px,color:#663c00
  classDef tool fill:#f6ffec,stroke:#8ad28a,stroke-width:1px,color:#0b5f1a
  classDef check fill:#ffe6ea,stroke:#ff99aa,stroke-width:1px,color:#7a001a
  classDef io fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,color:#0f172a

  subgraph Inputs
    A[Company & Industry JSON]:::io --> B[LangChain RunnableSequence\n(Context Assembler)]:::agent
  end

  subgraph Generation Loop (AutoGen-inspired)
    B --> C[System Prompt +\nPromptTemplate]:::agent
    C --> D[LLM: GPT-4o]:::llm
    D --> E[Structured Output Parser\n(JSON blocks per use case)]:::agent
    E --> F[Constraint Checker\n(Distribution 50/30/20, No %)]:::check
    F -->|violations| C
  end

  subgraph Post-Processing
    F --> G[Rewriter & Normalizer\n(tone, length, headings)]:::agent
    G --> H[Prioritizer/Ranker\n(rule-based + signals)]:::agent
  end

  H --> I[formatted_use_cases + Citations]:::io
```

### Use Case Agent – Inputs, Process, Outputs
- Inputs: Research JSON (company + industry)
- Process: RunnableSequence → PromptTemplate → GPT-4o → Structured Output Parser → Constraint Checker (distribution) → Rewriter → Prioritizer
- Outputs: `generated_use_cases.formatted_use_cases`, `citations`

---

## Resource Agent Workflow Diagram
```mermaid
flowchart TD
  classDef agent fill:#eef6ff,stroke:#8bbcff,stroke-width:1px,color:#0b2e6f
  classDef tool fill:#f6ffec,stroke:#8ad28a,stroke-width:1px,color:#0b5f1a
  classDef io fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,color:#0f172a
  classDef mix fill:#e8e7ff,stroke:#8f8be6,stroke-width:1px,color:#20106b

  subgraph Inputs
    A[Use Case Title & Description]:::io --> B[Keyword Extraction\n(n-grams + domain terms)]:::agent
  end

  subgraph Platform Queries
    B --> C[Kaggle API\n(kaggle)]:::tool
    B --> D[HuggingFace Hub\n(HfApi)]:::tool
    B --> E[GitHub Search\n(PyGithub)]:::tool
  end

  subgraph Aggregation & Scoring
    C --> F[Normalizer + Metadata Extract]:::agent
    D --> F
    E --> F
    F --> G[Relevance Scorer\n(string match + host score)]:::agent
    G --> H[Deduplicate & Canonicalize URLs]:::agent
    H --> I[Mix Ratio Enforcer\n(40% Kaggle / 30% HF / 30% GitHub)]:::mix
  end

  I --> J[Per-Use-Case Links (3–6)]:::io
  J --> K[datasets.md Table]:::io
  J --> L[Excel Export (Quick Download)]:::io
```

### Resource Agent – Inputs, Process, Outputs
- Inputs: Use case title/description
- Process: Keywordized search → Kaggle/HF/GitHub via SDKs → score/dedupe → enforce mix ratio → build Markdown/Excel outputs
- Outputs: `datasets.md` (table), `resources_{industry}.md`, Excel

---

## Combined End-to-End Workflow Diagram
```mermaid
flowchart LR
  classDef orch fill:#fff0f0,stroke:#ff8a8a,stroke-width:1px,color:#5a0000
  classDef agent fill:#eef6ff,stroke:#8bbcff,stroke-width:1px,color:#0b2e6f
  classDef tool fill:#f6ffec,stroke:#8ad28a,stroke-width:1px,color:#0b5f1a
  classDef io fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,color:#0f172a

  subgraph User/UI
    U[Streamlit UI]:::io --> I[Company Name Input]:::io
  end

  subgraph Orchestrator (AutoGen-style GroupChat)
    O[Coordinator\n(retries, fallbacks, logging)]:::orch
  end

  I --> O
  O --> R[Research Agent\n(Tavily Tool, PromptTemplate, Parser)]:::agent
  R -->|company & industry JSON| UC[Use Case Agent\n(LLM, Constraints, Rewriter)]:::agent
  UC -->|formatted use cases| RES[Resource Agent\n(Kaggle/HF/GitHub SDKs, Mixer)]:::agent

  RES --> D1[(datasets.md)]:::io
  O --> D2[(reports/*.json)]:::io
  O --> D3[(Excel Quick Download)]:::io
  O --> U
```

### End-to-End Flow – How Everything Connects
1. User provides company → Orchestrator triggers Research → Use Case → Resource.
2. Agents pass structured outputs downstream with constraint checks and normalization.
3. Results saved to reports and dataset markdown; UI provides Excel export.

---

## Workflow Explanations
- Research Diagram: Showcases input guardrails, LangChain PromptTemplate + OutputParser, and (optional) RAG chunking.
- Use Case Diagram: Demonstrates AutoGen-inspired generate–check–rewrite loop with strict distribution constraints.
- Resource Diagram: Illustrates platform SDK usage, relevance scoring, deduplication, and enforced mix ratios.
- Combined Diagram: Presents the full pipeline under an orchestrator akin to a GroupChat pattern.

---

## Strengths & Impact
- **Speed & Consistency**: Automates multi-hour research into minutes with standardized outputs.
- **Decision Support**: Produces examiner-ready use cases tied to high-quality resources.
- **Coverage**: Pulls from Kaggle, HuggingFace, and GitHub; links are curated/prioritized.
- **Scalable**: Modular agents; can run per company or batched.

---

## Future Enhancements
- Real-time APIs for pricing/news to enrich use cases dynamically
- Auto-fine-tuning or RAG pipelines for company-specific corpora
- Slack/Teams chatbot integration for live Q&A over results
- Caching + vector search for faster repeated runs

---

## Conclusion
This system operationalizes market research with an agentic pipeline that’s fast, auditable, and extensible. The diagrams and structured outputs make it easy to explain, evaluate, and adopt across teams.
