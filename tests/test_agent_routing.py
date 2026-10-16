from langchain_core.messages import HumanMessage

from graph import graph


test_questions = [
    {
        "question": "How many rows are in the dataset?",
        "expected_tool": "run_sql",
    },
    {
        "question": "Which 5 countries have the most transactions?",
        "expected_tool": "run_sql",
    },
    {
        "question": "What is the correlation between Quantity and UnitPrice?",
        "expected_tool": "calculate_correlation",
    },
    {
        "question": "What is the average UnitPrice?",
        "expected_tool": "run_sql",
    },
    {
        "question": "Which country has the highest average Quantity per transaction?",
        "expected_tool": "run_sql",
    },
]


passed = 0
failed = 0


for i, test_case in enumerate(test_questions, start=1):

    print("\n" + "=" * 70)
    print(f"TEST {i}")
    print("=" * 70)

    question = test_case["question"]
    expected_tool = test_case["expected_tool"]

    print("\nQuestion:")
    print(question)

    print("\nExpected tool:")
    print(expected_tool)

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        }
    )

    used_tools = []

    for message in result["messages"]:

        if hasattr(message, "tool_calls") and message.tool_calls:

            for tool_call in message.tool_calls:
                used_tools.append(tool_call["name"])

    print("\nUsed tools:")
    print(used_tools)

    if expected_tool in used_tools:
        print("\nResult: PASS")
        passed += 1
    else:
        print("\nResult: FAIL")
        failed += 1

    print("\nFinal answer:")
    print(result["messages"][-1].content)


# ============================================================
# Test Summary
# ============================================================

total = len(test_questions)

accuracy = (passed / total) * 100 if total > 0 else 0


print("\n" + "=" * 70)
print("ROUTING TEST SUMMARY")
print("=" * 70)

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {total}")
print(f"Routing Accuracy: {accuracy:.1f}%")