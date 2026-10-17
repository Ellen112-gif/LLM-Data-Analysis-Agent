# LLM Data Analysis Agent

An LLM-powered data analysis agent for structured datasets.

The agent uses **LangChain + LangGraph** to understand natural-language questions, automatically select analysis tools, execute data analysis, and return the final answer through a **FastAPI REST API**.

## Features

- **LLM Tool Calling** — automatically selects the appropriate analysis tool
- **SQL Analysis** — read-only SQL queries through SQLite
- **Statistical Analysis** — descriptive statistics and correlation analysis
- **LangGraph Agent** — tool execution and multi-step reasoning workflow
- **Tool Error Handling** — handles tool execution failures and returns errors to the agent
- **Agent Evaluation** — evaluates tool routing and final answer correctness
- **FastAPI Backend** — exposes the agent through REST APIs
- **Data Quality Profiling** — checks missing values, duplicates, outliers and other data issues

## Architecture

```text
User
  │
  ▼
FastAPI /chat
  │
  ▼
LangGraph Agent
  │
  ├── SQL Tool
  │
  ├── Statistics Tool
  │
  ├── Correlation Tool
  │
  └── Describe Column Tool
  │
  ▼
Tool Result
  │
  ▼
LLM
  │
  ▼
Final Answer
```

## Dataset

The project uses the **Online Retail** dataset.

- Rows: **541,909**
- Columns: **8**
- Format: Excel

Main fields:

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

The dataset is loaded into Pandas and can also be queried through an in-memory SQLite database.

## Example

The agent supports natural-language questions such as:

```text
How many rows are in the dataset?
```

```text
Which 5 countries have the most transactions?
```

```text
What is the average UnitPrice?
```

```text
What is the correlation between Quantity and UnitPrice?
```

```text
Which country has the highest average Quantity per transaction?
```

The agent automatically determines which tool should be used.

## FastAPI

Start the API:

```bash
uvicorn main:app --reload
```

API endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service information |
| GET | `/health` | Health check |
| POST | `/chat` | Ask a data analysis question |

Example request:

```json
{
  "question": "How many rows are in the dataset?"
}
```

Example response:

```json
{
  "answer": "The dataset contains 541,909 rows."
}
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Agent Evaluation

The project includes an evaluation suite covering:

- SQL analysis
- Statistical analysis
- Correlation analysis
- Numerical answer validation
- Tool routing
- Unsupported questions

Current evaluation result:

```text
Total Tests: 10
Routing Accuracy: 100.0%
Answer Accuracy: 100.0%
Overall Accuracy: 100.0%
Errors: 0
```

Run the evaluation with:

```bash
python -m tests.test_agent_evaluation
```

## Project Structure

```text
LLM-Data-Analysis-Agent/
│
├── data/
│   └── raw/
│       └── Online Retail.xlsx
│
├── outputs/
│   ├── profile.json
│   └── quality_report.json
│
├── src/
│   ├── profiler/
│   │   └── data_profiler.py
│   │
│   ├── quality/
│   │   └── quality_checker.py
│   │
│   └── tools/
│       ├── sql_tool.py
│       ├── statistics_tool.py
│       └── agent_tools.py
│
├── tests/
│   ├── test_agent_evaluation.py
│   └── test_agent_routing.py
│
├── graph.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Tech Stack

- Python
- Pandas
- NumPy
- SQLite
- LangChain
- LangGraph
- Qwen
- SiliconFlow
- FastAPI
- Pydantic

## Configuration

Create a `.env` file:

```env
SILICONFLOW_API_KEY=your_api_key_here
```

Do not commit `.env` to GitHub.

## Current Status

- [x] Dataset loading
- [x] Data profiling
- [x] Data quality analysis
- [x] SQL analysis tool
- [x] Statistical analysis tool
- [x] Correlation analysis
- [x] Descriptive statistics
- [x] LLM tool calling
- [x] Automatic tool selection
- [x] LangGraph agent workflow
- [x] Tool error handling
- [x] Agent evaluation
- [x] FastAPI backend
- [x] API validation and error handling

## Roadmap

- [ ] Docker deployment
- [ ] Web chat interface
- [ ] Performance and reliability improvements
```

