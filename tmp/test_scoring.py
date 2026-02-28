import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "lostnfound-backend", "LostNFound", "backend"))

from fraud_service import calculate_confidence_score

def test_scoring():
    print("Testing Confidence Scoring Logic...")
    
    # Case 1: Perfect match
    questions = [
        {"question": "Brand?", "correct_answer": "Sony"},
        {"question": "Color?", "correct_answer": "Black"}
    ]
    answers = [
        {"answer": "Sony"},
        {"answer": "Black"}
    ]
    proofs = ["file1.jpg", "file2.jpg"]
    
    result = calculate_confidence_score(answers, questions, proofs, {})
    print(f"Perfect Match: {result['confidence_score']}% - Status: {result['status']}")
    assert result['status'] == "VERIFIED"
    assert result['confidence_score'] == 100.0
    
    # Case 2: Partial match
    answers_partial = [
        {"answer": "Sony"},
        {"answer": "White"} # Wrong color
    ]
    result_partial = calculate_confidence_score(answers_partial, questions, proofs, {})
    print(f"Partial Match: {result_partial['confidence_score']}% - Status: {result_partial['status']}")
    # 60 * (1/2) + 25 + 10 + 5 = 30 + 40 = 70
    assert result_partial['confidence_score'] == 70.0
    assert result_partial['status'] == "MANUAL_REVIEW"

    # Case 3: Failed match
    answers_fail = [
        {"answer": "Bose"},
        {"answer": "White"}
    ]
    result_fail = calculate_confidence_score(answers_fail, questions, proofs, {})
    print(f"Failed Match: {result_fail['confidence_score']}% - Status: {result_fail['status']}")
    # 60 * (0) + 25 + 10 + 5 = 40
    assert result_fail['confidence_score'] == 40.0
    assert result_fail['status'] == "FAILED"

    print("Scoring tests passed!")

if __name__ == "__main__":
    test_scoring()
