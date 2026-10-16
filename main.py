from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from graph import graph


app = FastAPI(
    title="LLM Data Analysis Agent",
    description="LLM-powered data analysis agent using LangGraph.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Natural language question about the dataset.",
    )


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {
        "name": "LLM Data Analysis Agent",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            }
        )

        final_answer = result["messages"][-1].content

        return ChatResponse(
            answer=final_answer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}",
        )