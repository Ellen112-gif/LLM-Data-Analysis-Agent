# LLM Data Analysis Agent

An LLM-powered data analysis agent that allows users to ask questions about structured datasets using natural language.

The agent automatically selects appropriate analysis tools, executes data queries or statistical calculations, and generates evidence-based answers from tool results.

The current implementation uses **LangGraph** to orchestrate the agent workflow.

---

## Overview

Traditional data analysis often requires users to write SQL queries or Python code manually.

This project explores how an LLM can interact with structured data through a set of controlled tools.

Given a natural-language question, the agent can:

1. Understand the user's question
2. Select an appropriate analysis tool
3. Execute the analysis
4. Receive the tool result
5. Continue the workflow when additional analysis is required
6. Generate a final answer based on the returned data

### Architecture

```text
User Question
      │
      ▼
┌───────────────┐
│   LLM Agent   │
└───────┬───────┘
        │
        ▼
  Tool Selection
        │
   ┌────┴─────┐
   │          │
   ▼          ▼
SQL Tool   Statistics Tool
   │          │
   └────┬─────┘
        │
        ▼
   Tool Result
        │
        ▼
┌───────────────┐
│   LLM Agent   │
└───────┬───────┘
        │
        ▼
  Final Answer
```

---

## Key Features

### LLM Tool Calling

The LLM automatically determines which tool should be used based on the user's question.

For example:

```text
How many rows are in the dataset?
```

The agent selects the SQL analysis tool and generates:

```sql
SELECT COUNT(*) FROM data;
```

---

### SQL Data Analysis

The project provides a custom SQL tool backed by an in-memory SQLite database.

It supports analytical operations including:

- Counting
- Filtering
- Aggregation
- Grouping
- Sorting
- Basic SQL analysis

The SQL interface is designed as a read-only analytical tool.

Data modification operations such as:

```text
INSERT
UPDATE
DELETE
DROP
```

are blocked.

Example:

```text
Question:
How many rows are in the dataset?

Result:
541,909
```

---

### Statistical Analysis

The agent can also perform statistical analysis through dedicated tools.

Current functionality includes correlation analysis between numerical columns.

Example:

```text
Question:
What is the correlation between Quantity and UnitPrice?

Result:
-0.0012349245448703343
```

The agent is instructed to distinguish between correlation and causation and to avoid interpreting a near-zero correlation as proof of statistical independence.

---

### Agentic Tool Loop

The agent can continue the workflow after receiving a tool result.

```text
User Question
      ↓
     LLM
      ↓
   Tool Call
      ↓
  Tool Result
      ↓
     LLM
      ↓
Final Answer
```

If a tool returns an error, the agent can inspect the returned error and attempt to correct the next tool call.

---

### LangGraph Workflow

The current agent workflow is implemented using LangGraph.

```text
             START
               │
               ▼
            Agent
               │
               ▼
       Tool call required?
          │           │
         YES          NO
          │            │
          ▼            ▼
        Tools         END
          │
          ▼
        Agent
```

The graph uses message-based state to maintain the conversation between the user, LLM, and tools.

---

## Dataset

The current demonstration uses the **Online Retail** dataset.

Dataset dimensions:

```text
541,909 rows
8 columns
```

Columns include:

```text
InvoiceNo
StockCode
Description
Quantity
InvoiceDate
UnitPrice
CustomerID
Country
```

The project also performs basic dataset profiling and data quality analysis.

Known data quality checks include:

- Missing values
- Duplicate records
- Outliers
- Invalid values
- High-cardinality columns
- Constant columns

Generated profiling and quality reports are stored in:

```text
outputs/
├── profile.json
└── quality_report.json
```

The raw dataset is excluded from the public repository.

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| LLM Framework | LangChain |
| Agent Framework | LangGraph |
| LLM | Qwen |
| Model API | SiliconFlow |
| Data Processing | Pandas |
| Database | SQLite |
| Numerical Analysis | Pandas / NumPy |
| Development | VS Code |
| Environment | Conda |

---

## Project Structure

```text
LLM-Data-Analysis-Agent/
│
├── data/
│   └── raw/
│
├── outputs/
│   ├── profile.json
│   └── quality_report.json
│
├── src/
│   └── tools/
│       ├── sql_tool.py
│       ├── statistics_tool.py
│       └── agent_tools.py
│
├── graph.py
├── test_tool_calling.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Example Questions

The agent can answer questions such as:

### Dataset statistics

```text
How many rows are in the dataset?
```

Example result:

```text
541,909 rows
```

### SQL aggregation

```text
Which country has the highest number of transactions,
and how many transactions does it have?
```

The agent can generate an appropriate SQL aggregation query and return the result.

### Statistical analysis

```text
What is the correlation between Quantity and UnitPrice?
```

Example result:

```text
-0.0012349245448703343
```

The result indicates that the two variables have little to no linear relationship in this dataset.

---

## Current Status

The current implementation includes:

- [x] Dataset loading
- [x] Dataset profiling
- [x] Data quality analysis
- [x] SQL analysis tool
- [x] Statistical analysis tool
- [x] LLM tool calling
- [x] Automatic tool selection
- [x] Multi-step agent workflow
- [x] Tool error handling
- [x] System prompt and analysis constraints
- [x] LangGraph-based agent

### Planned Improvements

- [ ] Modularize the LangGraph agent
- [ ] FastAPI backend
- [ ] Web-based chat interface
- [ ] Agent evaluation
- [ ] Query and answer quality evaluation
- [ ] Docker deployment
- [ ] Performance and reliability improvements

---

## Design Considerations

The project focuses on building a reliable tool-using data analysis agent rather than allowing the LLM to directly generate unsupported answers.

Key design principles include:

- **Tool-based data access**  
  Numerical results are obtained from executable analysis tools rather than generated purely by the LLM.

- **Evidence-based answers**  
  Final answers are based on returned tool results.

- **Controlled SQL execution**  
  SQL operations are restricted to read-only analytical queries.

- **Conservative statistical interpretation**  
  Correlation is not interpreted as causation or statistical independence.

- **Graph-based orchestration**  
  LangGraph manages the interaction between the LLM and analysis tools.

---

## Roadmap

The project will be gradually extended toward a more complete LLM-powered data analysis system.

Planned directions include:

```text
LangGraph Agent
      ↓
Modular Agent Architecture
      ↓
FastAPI Backend
      ↓
Web Chat Interface
      ↓
Agent Evaluation
      ↓
Docker Deployment
```

---

## Configuration

Create a `.env` file in the project root:

```text
SILICONFLOW_API_KEY=your_api_key_here
```

API credentials should never be committed to the repository.

A `.env.example` file is provided as a configuration template.

---

## License

This project is developed for learning, portfolio development, and experimentation with LLM-based data analysis systems.