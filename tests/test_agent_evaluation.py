import re

from langchain_core.messages import HumanMessage

from graph import graph


# ============================================================
# Evaluation Dataset
# ============================================================

test_cases = [
    {
        "question": "How many rows are in the dataset?",
        "expected_tool": "run_sql",
        "expected_answer": "541,909",
        "answer_type": "contains",
    },
    {
        "question": "Which 5 countries have the most transactions?",
        "expected_tool": "run_sql",
        "expected_answer": "United Kingdom",
        "answer_type": "contains",
    },
    {
        "question": "What is the correlation between Quantity and UnitPrice?",
        "expected_tool": "calculate_correlation",
        "expected_answer": -0.0012349245448703343,
        "answer_type": "numeric",
        "tolerance": 0.001,
    },
    {
        "question": "What is the average UnitPrice?",
        "expected_tool": [
            "run_sql",
            "describe_column",
        ],
        "expected_answer": 4.61,
        "answer_type": "numeric",
        "tolerance": 0.01,
    },
    {
        "question": "Which country has the highest average Quantity per transaction?",
        "expected_tool": "run_sql",
        "expected_answer": "Netherlands",
        "answer_type": "contains",
    },
    {
        "question": "What is the total quantity sold?",
        "expected_tool": "run_sql",
        "expected_answer": 5176450,
        "answer_type": "numeric",
        "tolerance": 1,
    },
    {
        "question": "What is the maximum UnitPrice?",
        "expected_tool": [
            "run_sql",
            "describe_column",
        ],
        "expected_answer": 38970.0,
        "answer_type": "numeric",
        "tolerance": 0.1,
    },
    {
        "question": "Which 5 countries have the highest total quantity sold?",
        "expected_tool": "run_sql",
        "expected_answer": "United Kingdom",
        "answer_type": "contains",
    },
    {
        "question": "Which country has the highest average UnitPrice?",
        "expected_tool": "run_sql",
        "expected_answer": "Singapore",
        "answer_type": "contains",
    },
    {
        "question": "What is the average salary of customers?",
        "expected_tool": None,
        "expected_answer": [
            "salary",
            "does not contain",
        ],
        "answer_type": "refusal",
    },
]


# ============================================================
# Helper Functions
# ============================================================

def normalize_text(text):
    return text.lower().strip()


def extract_numbers(text):
    """
    Extract numbers from the final answer.

    Example:
    'The average is 4.61'
    -> [4.61]
    """

    cleaned_text = text.replace(",", "")

    number_strings = re.findall(
        r"-?\d+(?:\.\d+)?",
        cleaned_text
    )

    numbers = []

    for number_string in number_strings:
        try:
            numbers.append(float(number_string))
        except ValueError:
            pass

    return numbers


def evaluate_contains(
    final_answer,
    expected_answer
):
    """
    Check whether the expected text
    appears in the final answer.
    """

    return (
        normalize_text(str(expected_answer))
        in normalize_text(final_answer)
    )


def evaluate_numeric(
    final_answer,
    expected_answer,
    tolerance
):
    """
    Check whether any number in the final answer
    is within the allowed tolerance.
    """

    numbers = extract_numbers(final_answer)

    for number in numbers:

        if abs(number - expected_answer) <= tolerance:
            return True

    return False


def evaluate_refusal(
    final_answer,
    expected_keywords
):
    """
    Check whether the final answer indicates
    that the requested field/data is unavailable.

    All expected keywords must appear.
    """

    normalized_answer = normalize_text(
        final_answer
    )

    for keyword in expected_keywords:

        if normalize_text(keyword) not in normalized_answer:
            return False

    return True


def evaluate_answer(
    final_answer,
    expected_answer,
    answer_type,
    tolerance=0.0,
):
    """
    Evaluate the final answer according
    to the specified answer type.
    """

    if answer_type == "contains":

        return evaluate_contains(
            final_answer,
            expected_answer,
        )

    elif answer_type == "numeric":

        return evaluate_numeric(
            final_answer,
            expected_answer,
            tolerance,
        )

    elif answer_type == "refusal":

        return evaluate_refusal(
            final_answer,
            expected_answer,
        )

    else:

        raise ValueError(
            f"Unknown answer_type: {answer_type}"
        )


def evaluate_routing(
    used_tools,
    expected_tool
):
    """
    Evaluate whether the Agent selected
    an acceptable tool.

    expected_tool can be:

    1. A single tool name:
       "run_sql"

    2. A list of acceptable tools:
       ["run_sql", "describe_column"]

    3. None:
       No tool should be used.
    """

    # --------------------------------------------------------
    # Case 1: No tool expected
    # --------------------------------------------------------

    if expected_tool is None:

        return len(used_tools) == 0

    # --------------------------------------------------------
    # Case 2: Multiple acceptable tools
    # --------------------------------------------------------

    if isinstance(expected_tool, list):

        return any(
            tool in used_tools
            for tool in expected_tool
        )

    # --------------------------------------------------------
    # Case 3: One specific tool
    # --------------------------------------------------------

    return expected_tool in used_tools


# ============================================================
# Evaluation
# ============================================================

routing_passed = 0
answer_passed = 0
overall_passed = 0
errors = 0


for i, test_case in enumerate(
    test_cases,
    start=1
):

    print("\n" + "=" * 70)
    print(f"EVALUATION TEST {i}")
    print("=" * 70)

    question = test_case["question"]

    expected_tool = test_case[
        "expected_tool"
    ]

    expected_answer = test_case[
        "expected_answer"
    ]

    answer_type = test_case[
        "answer_type"
    ]

    tolerance = test_case.get(
        "tolerance",
        0.0
    )

    print("\nQuestion:")
    print(question)

    print("\nExpected tool:")

    if expected_tool is None:

        print("No tool expected")

    elif isinstance(expected_tool, list):

        print(
            "One of:",
            expected_tool
        )

    else:

        print(expected_tool)

    print("\nAnswer type:")
    print(answer_type)

    try:

        # ====================================================
        # Run Agent
        # ====================================================

        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=question
                    )
                ]
            }
        )

        # ====================================================
        # Collect Used Tools
        # ====================================================

        used_tools = []

        for message in result["messages"]:

            if (
                hasattr(
                    message,
                    "tool_calls"
                )
                and message.tool_calls
            ):

                for tool_call in message.tool_calls:

                    used_tools.append(
                        tool_call["name"]
                    )

        # ====================================================
        # Get Final Answer
        # ====================================================

        final_answer = (
            result["messages"][-1].content
        )

        # ====================================================
        # Evaluate Routing
        # ====================================================

        routing_pass = evaluate_routing(
            used_tools,
            expected_tool
        )

        # ====================================================
        # Evaluate Answer
        # ====================================================

        answer_pass = evaluate_answer(
            final_answer=final_answer,
            expected_answer=expected_answer,
            answer_type=answer_type,
            tolerance=tolerance,
        )

        # ====================================================
        # Overall Result
        # ====================================================

        test_pass = (
            routing_pass
            and answer_pass
        )

        # ====================================================
        # Update Counters
        # ====================================================

        if routing_pass:
            routing_passed += 1

        if answer_pass:
            answer_passed += 1

        if test_pass:
            overall_passed += 1

        # ====================================================
        # Print Results
        # ====================================================

        print("\nUsed tools:")

        if used_tools:

            print(used_tools)

        else:

            print("No tools used")

        print("\nFinal answer:")
        print(final_answer)

        print("\nRouting:")

        print(
            "PASS"
            if routing_pass
            else "FAIL"
        )

        print("\nAnswer:")

        print(
            "PASS"
            if answer_pass
            else "FAIL"
        )

        print("\nOverall result:")

        print(
            "PASS"
            if test_pass
            else "FAIL"
        )

    except Exception as e:

        print("\nOverall result: ERROR")

        print(
            f"Error: {e}"
        )

        errors += 1


# ============================================================
# Evaluation Summary
# ============================================================

total = len(test_cases)

routing_accuracy = (
    routing_passed / total * 100
    if total > 0
    else 0
)

answer_accuracy = (
    answer_passed / total * 100
    if total > 0
    else 0
)

overall_accuracy = (
    overall_passed / total * 100
    if total > 0
    else 0
)


print("\n" + "=" * 70)
print("AGENT EVALUATION SUMMARY")
print("=" * 70)

print(
    f"Total Tests: {total}"
)

print(
    f"Routing Passed: "
    f"{routing_passed}/{total}"
)

print(
    f"Answer Passed: "
    f"{answer_passed}/{total}"
)

print(
    f"Overall Passed: "
    f"{overall_passed}/{total}"
)

print(
    f"Errors: {errors}"
)

print()

print(
    f"Routing Accuracy: "
    f"{routing_accuracy:.1f}%"
)

print(
    f"Answer Accuracy: "
    f"{answer_accuracy:.1f}%"
)

print(
    f"Overall Accuracy: "
    f"{overall_accuracy:.1f}%"
)