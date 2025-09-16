# Multi-Agent Market Research System — Architecture Diagrams

This document visualizes the complete system architecture, covering UI, orchestration, agents, utilities, external services, data flow, and execution sequences.

## Complex Workflow (Detailed Flowchart)

```mermaid
flowchart TD
    Start([User Opens Streamlit App]) --> LoadEnv[Load Environment Variables]
    LoadEnv --> ValidateEnv{Validate .env File}
    ValidateEnv -- Invalid --> ShowError[Display Configuration Error]
    ValidateEnv -- Valid --> InitUI[Initialize Streamlit UI]
    
    InitUI --> UserInput[User Enters Company Name]
    UserInput --> ValidateInput{Validate Company Input}
    ValidateInput -- Empty/Invalid --> InputError[Show Input Error]
    ValidateInput -- Valid --> StartAnalysis[Initialize Orchestrator]
    
    StartAnalysis --> InitPerf[Start Performance Tracking]
    InitPerf --> InitResearchAgent[Initialize Research Agent]
    
    %% Research Agent Flow
    InitResearchAgent --> SearchCompany[Tavily Web Search: Company Info]
    SearchCompany --> TavilyLimit{Tavily API Limit?}
    TavilyLimit -- Yes --> TavilyError[Log Tavily Error\nContinue with Limited Data]
    TavilyLimit -- No --> ProcessSearch[Process Search Results]
    
    TavilyError --> FallbackResearch[Use Fallback Research Data]
    ProcessSearch --> SearchIndustry[Tavily Web Search: Industry Info]
    SearchIndustry --> ProcessIndustry[Process Industry Results]
    
    FallbackResearch --> CallOpenAIResearch[OpenAI: Synthesize Research]
    ProcessIndustry --> CallOpenAIResearch
    
    CallOpenAIResearch --> OpenAILimit1{OpenAI API Limit?}
    OpenAILimit1 -- Yes --> OpenAIError1[Log OpenAI Error\nRetry with Fallback]
    OpenAILimit1 -- No --> StructureResearch[Structure Research JSON]
    
    OpenAIError1 --> RetryResearch{Retry Count < 3?}
    RetryResearch -- Yes --> CallOpenAIResearch
    RetryResearch -- No --> FailResearch[Research Failed\nUse Mock Data]
    
    StructureResearch --> ValidateResearchOutput{Valid Research JSON?}
    ValidateResearchOutput -- No --> FailResearch
    ValidateResearchOutput -- Yes --> SaveResearchTemp[Save Research to Memory]
    
    FailResearch --> SaveResearchTemp
    SaveResearchTemp --> InitUseCaseAgent[Initialize Use Case Agent]
    
    %% Use Case Agent Flow
    InitUseCaseAgent --> ProcessResearchData[Process Research Input]
    ProcessResearchData --> GenerateUseCases[OpenAI: Generate Use Cases]
    
    GenerateUseCases --> OpenAILimit2{OpenAI API Limit?}
    OpenAILimit2 -- Yes --> OpenAIError2[Log OpenAI Error\nRetry]
    OpenAILimit2 -- No --> ParseUseCases[Parse Use Cases JSON]
    
    OpenAIError2 --> RetryUseCases{Retry Count < 3?}
    RetryUseCases -- Yes --> GenerateUseCases
    RetryUseCases -- No --> FailUseCases[Use Cases Failed\nGenerate Fallback]
    
    ParseUseCases --> ValidateUseCases{Valid Use Cases?}
    ValidateUseCases -- No --> FailUseCases
    ValidateUseCases -- Yes --> CheckDistribution{Check Distribution Constraints}
    
    CheckDistribution -- Fails --> RewriteUseCases[Rewrite Use Cases for Balance]
    RewriteUseCases --> ValidateUseCases
    CheckDistribution -- Passes --> PrioritizeUseCases[Prioritize Use Cases]
    
    FailUseCases --> PrioritizeUseCases
    PrioritizeUseCases --> SaveUseCasesTemp[Save Use Cases to Memory]
    SaveUseCasesTemp --> InitResourceAgent[Initialize Resource Agent]
    
    %% Resource Agent Flow
    InitResourceAgent --> ExtractKeywords[Extract Keywords from Use Cases]
    ExtractKeywords --> ParallelResourceSearch{Start Parallel Resource Collection}
    
    ParallelResourceSearch --> SearchKaggle[Search Kaggle Datasets]
    ParallelResourceSearch --> SearchHuggingFace[Search HuggingFace Models/Datasets]
    ParallelResourceSearch --> SearchGitHub[Search GitHub Repositories]
    
    SearchKaggle --> KaggleLimit{Kaggle API Available?}
    KaggleLimit -- No --> SkipKaggle[Skip Kaggle Resources]
    KaggleLimit -- Yes --> ProcessKaggle[Process Kaggle Results]
    
    SearchHuggingFace --> HFLimit{HuggingFace API Available?}
    HFLimit -- No --> SkipHF[Skip HuggingFace Resources]
    HFLimit -- Yes --> ProcessHF[Process HuggingFace Results]
    
    SearchGitHub --> GitHubLimit{GitHub API Available?}
    GitHubLimit -- No --> SkipGitHub[Skip GitHub Resources]
    GitHubLimit -- Yes --> ProcessGitHub[Process GitHub Results]
    
    SkipKaggle --> MergeResources[Merge All Resources]
    ProcessKaggle --> MergeResources
    SkipHF --> MergeResources
    ProcessHF --> MergeResources
    SkipGitHub --> MergeResources
    ProcessGitHub --> MergeResources
    
    MergeResources --> DeduplicateResources[Deduplicate Resources]
    DeduplicateResources --> ScoreResources[Score Resource Relevance]
    ScoreResources --> EnforceMixRatio[Enforce Platform Mix Ratio]
    EnforceMixRatio --> GenerateMarkdown[Generate Resource Markdown]
    
    GenerateMarkdown --> CallOpenAIResource[OpenAI: Format Resources]
    CallOpenAIResource --> OpenAILimit3{OpenAI API Limit?}
    OpenAILimit3 -- Yes --> OpenAIError3[Use Raw Resource Format]
    OpenAILimit3 -- No --> FormatResources[Format Final Resources]
    
    OpenAIError3 --> SaveResourcesTemp[Save Resources to Memory]
    FormatResources --> SaveResourcesTemp
    
    %% Final Orchestration
    SaveResourcesTemp --> CombineResults[Combine All Agent Results]
    CombineResults --> GenerateReports[Generate JSON Reports]
    GenerateReports --> GenerateMarkdownFiles[Generate Markdown Files]
    GenerateMarkdownFiles --> SaveToOutput[Save to output/ and reports/]
    
    SaveToOutput --> UpdateUIProgress[Update UI Progress: 100%]
    UpdateUIProgress --> DisplayResults[Display Results in Streamlit Tabs]
    
    DisplayResults --> ShowCompanyAnalysis[Tab: Company Analysis]
    DisplayResults --> ShowUseCases[Tab: Use Cases]
    DisplayResults --> ShowResources[Tab: Resources]
    DisplayResults --> ShowExecutiveSummary[Tab: Executive Summary]
    DisplayResults --> ShowDownloads[Tab: Downloads]
    
    %% Error Handling Paths
    ShowError --> End1[End with Error]
    InputError --> UserInput
    
    %% Success Path
    ShowDownloads --> StopPerf[Stop Performance Tracking]
    StopPerf --> LogCompletion[Log Analysis Completion]
    LogCompletion --> End2[End Successfully]
    
    %% Styling
    classDef errorNode fill:#ffcccc,stroke:#ff0000,stroke-width:2px
    classDef successNode fill:#ccffcc,stroke:#00ff00,stroke-width:2px
    classDef processNode fill:#cceeff,stroke:#0066cc,stroke-width:2px
    classDef decisionNode fill:#ffffcc,stroke:#ffaa00,stroke-width:2px
    classDef agentNode fill:#e6ccff,stroke:#9900cc,stroke-width:2px
    
    class ShowError,TavilyError,OpenAIError1,OpenAIError2,OpenAIError3,FailResearch,FailUseCases,InputError errorNode
    class End2,LogCompletion,StopPerf successNode
    class InitResearchAgent,InitUseCaseAgent,InitResourceAgent agentNode
    class ValidateEnv,ValidateInput,TavilyLimit,OpenAILimit1,OpenAILimit2,OpenAILimit3,ValidateResearchOutput,ValidateUseCases,CheckDistribution,KaggleLimit,HFLimit,GitHubLimit decisionNode
```

## 1) System Context Diagram

```mermaid
flowchart TD
    User([User])

    subgraph Local[Local Machine]
      UI[Streamlit App\n`streamlit_app.py`]
      Orchestrator[Orchestrator\n`orchestrator.py`]

      subgraph Agents[Agents]
        RA[Research Agent\n`agents/research_agent.py`]
        UA[Use Case Agent\n`agents/usecase_agent.py`]
        ResA[Resource Agent\n`agents/resource_agent.py`]
      end

      subgraph Utils[Utilities]
        Helpers[`utils/helpers.py`]
        Perf[`utils/performance.py`]
        EnvCleaner[`utils/env_cleaner.py`]
        Config[`config.py`]
      end

      subgraph Tools[Tools]
        WebSearch[`tools/web_search.py`]
      end

      subgraph Storage[Local Storage]
        Reports[Reports JSON\n`reports/complete_analysis_*.json`]
        Output[Markdown Outputs\n`output/resources_*.md`, `datasets.md`]
      end
    end

    subgraph External[External Services]
      OpenAI[OpenAI APIs]
      Tavily[Tavily Search]
      Kaggle[Kaggle API]
      HF[HuggingFace Hub]
      GitHub[GitHub API]
    end

    User -->|inputs company| UI
    UI --> Orchestrator
    Orchestrator --> RA
    Orchestrator --> UA
    Orchestrator --> ResA

    RA -->|web search| WebSearch
    WebSearch --> Tavily

    RA --> OpenAI
    UA --> OpenAI
    ResA --> OpenAI

    ResA --> Kaggle
    ResA --> HF
    ResA --> GitHub

    RA --> Reports
    UA --> Reports
    ResA --> Output
    Orchestrator --> Reports
    Orchestrator --> Output

    UI -->|renders results| Reports
    UI -->|renders datasets/resources| Output

    Orchestrator <---> Helpers
    Agents <---> Helpers
    Orchestrator <---> Perf
    Orchestrator <---> EnvCleaner
    Orchestrator <---> Config
```

## 2) Component Diagram (Modules and Responsibilities)

```mermaid
flowchart LR
    subgraph UI[UI Layer]
      SApp[`streamlit_app.py`\nPage layout, inputs, progress UI, rendering]
    end

    subgraph Core[Core]
      Orch[`orchestrator.py`\nCoordinates agents, validation, persistence]
      Cfg[`config.py`\nEnv + runtime config]
    end

    subgraph Agents[Agents Layer]
      RAgent[`agents/research_agent.py`\nCompany + industry research]
      UAgent[`agents/usecase_agent.py`\nGenerate & prioritize use cases]
      ResAgent[`agents/resource_agent.py`\nCollect datasets/models/repos]
    end

    subgraph Utils[Utilities]
      Help[`utils/helpers.py`\nFormatting, I/O helpers]
      PerfU[`utils/performance.py`\nTiming, metrics]
      EnvC[`utils/env_cleaner.py`\n.env validation/cleanup]
    end

    subgraph Tools[Tooling]
      WSearch[`tools/web_search.py`\nTavily wrapper]
    end

    subgraph External[External APIs]
      OAI[OpenAI]
      TV[Tavily]
      KG[Kaggle]
      HF[HuggingFace]
      GH[GitHub]
    end

    SApp --> Orch
    Orch --> RAgent
    Orch --> UAgent
    Orch --> ResAgent
    Orch --- Cfg
    Orch --- Help
    Orch --- PerfU
    Orch --- EnvC

    RAgent --> WSearch --> TV
    RAgent --> OAI
    UAgent --> OAI
    ResAgent --> OAI
    ResAgent --> KG
    ResAgent --> HF
    ResAgent --> GH
```

## 3) End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant UI as Streamlit App
    participant OR as Orchestrator
    participant RA as Research Agent
    participant UA as Use Case Agent
    participant RE as Resource Agent
    participant TV as Tavily
    participant OAI as OpenAI
    participant KG as Kaggle
    participant HF as HuggingFace
    participant GH as GitHub

    U->>UI: Enter company and start analysis
    UI->>OR: init_run(company)
    OR->>OR: validate_config(.env)
    OR->>RA: run_research(company)
    RA->>TV: search company/industry
    TV-->>RA: results
    RA->>OAI: synthesize structured research
    OAI-->>RA: company/industry analysis JSON
    RA-->>OR: research_result

    OR->>UA: generate_use_cases(research_result)
    UA->>OAI: produce 8-12 use cases
    OAI-->>UA: structured use cases
    UA-->>OR: use_cases

    OR->>RE: collect_resources(use_cases)
    RE->>KG: search datasets (keywords)
    RE->>HF: search models/datasets
    RE->>GH: search repos/code
    KG-->>RE: dataset candidates
    HF-->>RE: hf resources
    GH-->>RE: repos
    RE->>OAI: rank/format as markdown
    OAI-->>RE: curated resources
    RE-->>OR: resources

    OR->>OR: persist reports and outputs
    OR-->>UI: final artifacts (reports, markdown)
    UI-->>U: Render tabs + downloads
```

## 4) Data Flow and Artifacts

```mermaid
flowchart TD
    Input[Company Input] --> Research[Research JSON]
    Research --> UseCases[Use Cases JSON]
    UseCases --> Resources[Resources Markdown]

    subgraph Persist[Persistence]
      Reports[reports/complete_analysis_*.json]
      MD[output/resources_*.md]
      DS[datasets.md]
    end

    Research --> Reports
    UseCases --> Reports
    Resources --> MD
    Resources --> DS
```

## 5) Deployment / Runtime View

```mermaid
flowchart LR
    Dev[VS Code + Terminal] -->|python -m venv .venv| VEnv[Virtual Env]
    VEnv -->|pip install -r requirements.txt| Deps[Installed Deps]
    Deps -->|streamlit run streamlit_app.py| Streamlit[Local Web Server :8501]
    Streamlit -->|.env keys| Ext[OpenAI, Tavily, Kaggle, HF, GitHub]
    Streamlit -->|writes| Files[reports/, output/]
```

## 6) Error Handling and Limits (Operational)

- **Configuration guardrails**: `.env` validated/sanitized via `utils/env_cleaner.py` before runs.
- **API usage limits**: External services may rate limit. System should surface errors in UI logs; operators may retry or adjust keys/plan.
- **Partial completion**: If any external source fails, downstream steps should still produce best-effort outputs from available data.
- **Observability**: `utils/performance.py` supports timing/metrics; Streamlit console shows detailed logs.

## 7) Environment & Keys

- Required: `OPENAI_API_KEY`, `TAVILY_API_KEY`
- Optional: `KAGGLE_USERNAME`, `KAGGLE_KEY`, `GITHUB_TOKEN`, `HUGGINGFACE_TOKEN`

---

Use these diagrams in design reviews and onboarding. They map directly to modules found under `agents/`, `utils/`, `tools/`, and the top-level `streamlit_app.py` and `orchestrator.py`.


