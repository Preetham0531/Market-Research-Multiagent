# AI-Powered Multi-Agent System for Industry Research, Use Case Generation, and Dataset Resource Mapping

## Introduction
This project delivers an end-to-end, AI-powered market research system that automates: industry/company research, generation of high-impact AI/GenAI use cases, and mapping of each use case to relevant datasets/resources (Kaggle, HuggingFace, GitHub). It increases speed, consistency, and coverage for strategy, product, and data teams.

## System Architecture (High-Level)
- Research Agent: Finds industries, segments, offerings, strategy, trends, competitors.
- Use Case Agent: Produces 10 detailed, distribution-constrained development use cases.
- Resource Agent: Collects 3–6 high-quality resources per use case from Kaggle/HF/GitHub.
- Orchestrator: Coordinates agents, handles fallbacks, saves reports and datasets mapping.

 For full system diagrams (context, components, sequences, and data flow), see: `docs/ARCHITECTURE.md`.

---

### Research Agent – Inputs, Process, Outputs
- Inputs: Company name
- Process: Validation/PII scrub → Search via Tavily → (optional RAG) → LLM with PromptTemplate → Structured JSON via OutputParser
- Outputs: `company_analysis`, `industry_analysis`, citations

---

### Use Case Agent – Inputs, Process, Outputs
- Inputs: Research JSON (company + industry)
- Process: RunnableSequence → PromptTemplate → GPT-4o → Structured Output Parser → Constraint Checker (distribution) → Rewriter → Prioritizer
- Outputs: `generated_use_cases.formatted_use_cases`, `citations`

---

### Resource Agent – Inputs, Process, Outputs
- Inputs: Use case title/description
- Process: Keywordized search → Kaggle/HF/GitHub via SDKs → score/dedupe → enforce mix ratio → build Markdown/Excel outputs
- Outputs: `datasets.md` (table), `resources_{industry}.md`, Excel

---

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
