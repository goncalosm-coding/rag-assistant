from query_data import query_rag
from openai import OpenAI
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

EVAL_PROMPT = """
You are evaluating the correctness of an answer based on the expected response and the actual response.

Expected Response: "{expected_response}"

Actual Response: "{actual_response}"

Does the actual response match the expected response in terms of meaning, even if it includes additional context or wording? Please consider the core information and disregard minor additions.

Respond with 'true' if the actual response conveys the expected meaning, and 'false' if it does not.
"""


def test_question_one():
    assert query_and_validate(
        question="Who was the responsible for the editing and review of the article writing?",
        expected_response="Wondmagegn Taye Abebe",
    )


def test_question_two():
    assert query_and_validate(
        question="What machine learning models were used in this study?",
        expected_response="Extreme Gradient Boosting, K-Nearest Neighbors, Support Vector Machine and Multilayer Perceptron",
    )


def query_and_validate(question: str, expected_response: str):

    client = OpenAI()

    response_text = query_rag(question)
    prompt = EVAL_PROMPT.format(
        expected_response=expected_response, actual_response=response_text
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    evaluation_results_str = response.choices[0].message.content
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()

    print(prompt)

    if "true" in evaluation_results_str_cleaned:
        # Print response in Green if it is correct.
        print("\033[92m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return True
    elif "false" in evaluation_results_str_cleaned:
        # Print response in Red if it is incorrect.
        print("\033[91m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return False
    else:
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false'."
        )
    
# Testing: pytest -s  --disable-warnings