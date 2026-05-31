"""
RAGAS evaluation script to assess RAG pipeline quality.
Assesses:
- Context Precision
- Context Recall
- Faithfulness
- Answer Relevancy
"""
import os
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
)

# For Ragas to use Gemini LLM, we need to wrap it. 
# Langchain's ChatGoogleGenerativeAI and Embeddings can be passed.
from app.core.llm import get_llm, get_embeddings
from app.rag.vector_store import get_vector_store
from app.agents.graph import build_graph

# Setup basic evaluation
def prepare_test_dataset():
    """Prepare a synthetic test dataset for RAGAS evaluation."""
    return [
        {
            "question": "What are the major risks for Project Alpha in Q1?",
            "ground_truth": "The major risks include supply chain delays affecting material delivery by 3 weeks, and a 15% budget overrun risk due to unexpected foundational issues.",
        },
        {
            "question": "What is the completion percentage for Project Beta?",
            "ground_truth": "Project Beta is currently at 45% completion.",
        },
        {
            "question": "What is the total budget variance for Q1 2026?",
            "ground_truth": "The total budget variance across all projects in Q1 2026 is $150,000 over budget.",
        }
    ]

def run_evaluation():
    print("Starting RAGAS Evaluation...")
    agent = build_graph()
    
    test_cases = prepare_test_dataset()
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    for case in test_cases:
        print(f"Testing question: {case['question']}")
        
        initial_state = {
            "query": case["question"],
            "chat_history": [],
            "route": "",
            "context_docs": [],
            "dataframe_info": "",
            "answer": "",
            "sources": []
        }
        
        # We need the context docs to evaluate retrieval metrics
        # The agent graph fetches them in `retrieve_docs`, but it doesn't return the raw text
        # in the final state easily if we don't extract it. 
        # For evaluation, we can simulate retrieval or rely on the state.
        
        final_state = agent.invoke(initial_state)
        
        answer = final_state.get("answer", "")
        # Extract page_content from retrieved docs for RAGAS
        retrieved_contexts = [doc.page_content for doc in final_state.get("context_docs", [])]
        
        questions.append(case["question"])
        answers.append(answer)
        contexts.append(retrieved_contexts)
        ground_truths.append([case["ground_truth"]])  # Ragas expects list of strings
        
    # Build HuggingFace Dataset
    data_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    
    dataset = Dataset.from_dict(data_dict)
    
    llm = get_llm()
    embeddings = get_embeddings()
    
    print("Running metrics computation...")
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
        llm=llm,
        embeddings=embeddings,
    )
    
    print("\n=== Evaluation Results ===")
    print(result)
    
    # Save results
    with open("ragas_evaluation_results.json", "w") as f:
        # result is a dictionary-like object
        json.dump(result, f, indent=4)
    print("Saved results to ragas_evaluation_results.json")

if __name__ == "__main__":
    # Ensure environment variables are set before running
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Please set GOOGLE_API_KEY environment variable.")
        exit(1)
        
    run_evaluation()