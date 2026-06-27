import os
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, answer_correctness
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from ragas.run_config import RunConfig
import time

load_dotenv()

# 1. Initialize Pipeline Infrastructure (Linked to LangSmith via Env Variables)
embeddings = OpenAIEmbeddings(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openai/text-embedding-3-small"
)

llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openrouter/free",
    temperature=0.0
)

# Load existing policy data asset
file_path = os.path.join("..", "..", "Day 8", "Chunking Comparison", "sample_policy.txt")
loader = TextLoader(file_path, encoding="utf-8")
documents = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40).split_documents(loader.load())
vector_store = Chroma.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# LCEL Setup
prompt = ChatPromptTemplate.from_template(
    "Answer using ONLY the provided context.\n\nCONTEXT:\n{context}\n\nQUESTION: {question}\nANSWER:"
)
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

lcel_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 2. Define the 10-Pair Golden Testing Evaluation Dataset
golden_dataset = [
    {
        "question": "What happens if a pod tries to scale manually?",
        "ground_truth": "Any manual scaling overrides will instantly trip the localized circuit breaker, which automatically isolates the offending sub-network instance within 45 seconds."
    },
    {
        "question": "What triggers an automatic horizontal node expansion?",
        "ground_truth": "It triggers whenever the aggregate CPU utilization stays above 78% for a continuous duration exceeding 12 minutes."
    },
    {
        "question": "How often do operational cryptographic key tokens expire?",
        "ground_truth": "These security keys expire automatically every 14 operating days."
    },
    {
        "question": "What type of validation matrices are required for key handshakes?",
        "ground_truth": "Cryptographic key handshakes require SHA-256 validation matrices executed inside a localized hardware security module (HSM)."
    },
    {
        "question": "Who must sign off on a manual security audit if a service is blocked?",
        "ground_truth": "A manual security audit must be signed off by the Operations Director."
    },
    {
        "question": "Can individual engineering pods manually override the baseline auto-scaling layers?",
        "ground_truth": "Under no circumstances should individual engineering pods override this baseline layer manually."
    },
    {
        "question": "What is immediately revoked if a service fails to rotate keys?",
        "ground_truth": "Its network communication layer is immediately revoked, and it will be permanently blocked from issuing remote database procedure calls."
    },
    {
        "question": "Within how many seconds is an offending sub-network isolated?",
        "ground_truth": "Within 45 seconds to protect the core data grid stability."
    },
    {
        "question": "Where are the SHA-256 validation matrices executed?",
        "ground_truth": "They are executed inside a localized hardware security module (HSM)."
    },
    {
        "question": "What happens to a service instance if it misses the 14-day key rotation window?",
        "ground_truth": "It is permanently blocked from issuing remote database procedure calls until a manual security audit is signed off."
    }
]

# --- 3. Collect Pipeline Execution Metrics ---
questions = [item["question"] for item in golden_dataset]
ground_truths = [item["ground_truth"] for item in golden_dataset] 
answers = []
contexts = []

print("🧪 Commencing Resilient Dataset Processing Loop via LCEL pipeline...")
for idx, q in enumerate(questions):
    print(f" -> Indexing pair [{idx + 1}/10]: Processing question vector...")
    
    generated_answer = None
    retrieved_chunks = []
    attempts = 0
    max_attempts = 5
    
    while attempts < max_attempts:
        try:
            # Capture generated answer via pipeline
            generated_answer = lcel_chain.invoke(q)
            retrieved_chunks = retriever.invoke(q)
            break  # Success! Break out of the retry loop
        except Exception as e:
            attempts += 1
            if "429" in str(e) or "RateLimitError" in e.__class__.__name__:
                wait_time = attempts * 15  # Exponential back-off: 15s, 30s, 45s...
                print(f"   ⚠️ Rate limited on item {idx + 1}. Backing off for {wait_time}s (Attempt {attempts}/{max_attempts})...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ Unexpected error: {e}")
                generated_answer = "Error: Generation failed."
                break
                
    # Fallback assignment if all retries fail
    if not generated_answer:
        generated_answer = "Error: Rate limit timeout."
        
    answers.append(generated_answer)
    contexts.append([chunk.page_content for chunk in retrieved_chunks])
    
    # 2-second buffer between normal successful requests
    time.sleep(2)

# --- 4. Formulate Evaluation Dataset Object ---
# ✅ UPDATED: Using explicit naming mappings matching the modern RAGAs schema
data_dict = {
    "user_input": questions,
    "response": answers,
    "retrieved_contexts": contexts,
    "reference": ground_truths
}
dataset = Dataset.from_dict(data_dict)

print("\n📊 Executing Throttled RAGAs Evaluation Scoring...")
eval_result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, answer_correctness],
    llm=llm,
    embeddings=embeddings,
    run_config=RunConfig(
        timeout=120,      # Give the API plenty of breathing room
        max_retries=10,    # Aggressively retry if an upstream model is busy
        max_workers=1     # 🛑 CRITICAL: Force sequential execution to prevent 429s
    )
)

# 5. Output Report Analytics
print("\n🏆 FINAL SYSTEM EVALUATION METRICS REPORT:")
print("=" * 50)
# Handle print out safely even if some rows are blank
for metric, score in eval_result.items():
    print(f"📈 {metric.upper()}: {score:.4f}")
print("=" * 50)