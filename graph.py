
import os
import pandas as pd

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.tools.sql_tool import SQLTool
from src.tools.statistics_tool import StatisticsTool
from src.tools.agent_tools import create_agent_tools


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# 2. Load dataset
# ============================================================

df = pd.read_excel("data/raw/Online Retail.xlsx")

print(f"Dataset loaded: {df.shape}")


# ============================================================
# 3. Create tools
# ============================================================

sql_tool = SQLTool(df)

statistics_tool = StatisticsTool(df)

tools = create_agent_tools(
    sql_tool,
    statistics_tool
)


# ============================================================
# 4. Create LLM
# ============================================================

llm = ChatOpenAI(
    model="Qwen/Qwen3.5-4B",
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)


# ============================================================
# 5. Bind tools to LLM
# ============================================================

llm_with_tools = llm.bind_tools(tools)


# ============================================================
# 6. System Prompt
# ============================================================

system_prompt = """
You are a careful and conservative data analysis agent.

Your job is to answer questions about an Online Retail dataset
using the available tools.

DATABASE INFORMATION

SQL engine:
SQLite

Table name:
data

Columns:
- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country


TOOL USAGE RULES

1. Use tools whenever the user asks for information that requires
   querying or calculating values from the dataset.

2. Use run_sql for:
   - counting
   - filtering
   - grouping
   - aggregation
   - sorting
   - SQL-based analysis

3. Use calculate_correlation when the user asks for correlation
   between two numerical columns.

4. Generate SQLite-compatible SQL only.

5. Do not use:
   - information_schema
   - FORMAT ROWS
   - SQL syntax specific to PostgreSQL, MySQL, or other databases.

6. If a tool returns an error, inspect the error and correct
   the next tool call.

7. Stop calling tools when enough information is available.


NUMERICAL ACCURACY RULES

1. Tool results are the source of truth.

2. Never change the sign of a numerical result.

3. Never change a negative value into a positive value.

4. When rounding numbers, preserve the original sign.

5. Do not invent numerical values that were not returned by a tool.


STATISTICAL INTERPRETATION RULES

1. Base statistical conclusions only on tool results.

2. Correlation measures linear association.

3. Correlation does not imply causation.

4. A correlation coefficient close to zero means there is little
   or no LINEAR relationship between the variables.

5. A correlation close to zero does NOT prove statistical independence.

6. Never describe two variables as "independent" based only on
   a correlation coefficient.

7. Do not claim statistical significance or non-significance unless
   an appropriate statistical significance test has been performed.

8. Do not invent causal or business explanations unless the user
   explicitly asks for interpretation beyond the available evidence.

9. Never use the words "independent", "independence",
   or "independently" based only on a correlation result.

10. Do not provide business explanations for statistical patterns
    unless those explanations are directly supported by tool results.

11. For correlation results, describe only the strength and direction
    of the linear relationship supported by the coefficient.
    
    
FINAL ANSWER RULES

1. Report calculated values accurately.

2. Clearly separate:
   - calculated result
   - interpretation

3. Keep interpretations conservative.

4. If the available evidence only supports a limited conclusion,
   state only that limited conclusion.

5. Prefer concise answers over unsupported speculation.

6. Every factual claim about the dataset must be supported by
   information returned by a tool.

7. Do not add explanations about customer behavior, pricing strategy,
   business causes, or domain assumptions unless the relevant evidence
   was returned by a tool.

8. Distinguish clearly between what was calculated and what can
   legitimately be concluded from that calculation.
"""


# ============================================================
# 7. Define Agent Node
# ============================================================

def agent_node(state: MessagesState):

    messages = state["messages"]

    # Add system prompt before the conversation
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [
            SystemMessage(content=system_prompt)
        ] + messages

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# ============================================================
# 8. Create Tool Node
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# 9. Build LangGraph
# ============================================================

builder = StateGraph(MessagesState)


# Add nodes
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)


# START → Agent
builder.add_edge(START, "agent")


# Agent → Tools or END
builder.add_conditional_edges(
    "agent",
    tools_condition
)


# Tools → Agent
builder.add_edge("tools", "agent")


# Compile graph
graph = builder.compile()


# ============================================================
# 10. Run the Agent
# ============================================================


if __name__ == "__main__":

    user_question = input(
        "\nAsk a question about the dataset: "
    )

    print("\n========== START GRAPH ==========\n")

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_question)
            ]
        }
    )

    print("\n========== ALL MESSAGES ==========\n")

    for i, message in enumerate(result["messages"]):

        print(f"\n----- Message {i} -----")

        print("Type:", type(message).__name__)

        print("Content:")
        print(message.content)

        if hasattr(message, "tool_calls"):
            print("Tool Calls:")
            print(message.tool_calls)

    print("\n========== FINAL ANSWER ==========\n")

    final_message = result["messages"][-1]

    print("Final message type:")
    print(type(final_message).__name__)

    print("\nFinal message content:")
    print(final_message.content)

    sql_tool.close()

