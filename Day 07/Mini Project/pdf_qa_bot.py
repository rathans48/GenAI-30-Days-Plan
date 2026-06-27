import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# Load environment configuration
load_dotenv(".env")

# Initialize the OpenAI-compatible gateway client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def extract_text_from_pdf(pdf_path: str) -> list:
    """Reads a local PDF file and slices the text into clear, manageable context blocks."""
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at target path: {pdf_path}")
        return []
        
    print(f"📄 Extracting text layers from: {os.path.basename(pdf_path)}...")
    reader = PdfReader(pdf_path)
    chunks = []
    
    # Extract text page by page
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            # Split the page text into paragraph paragraphs to build safe vector spaces
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for p in paragraphs:
                chunks.append(f"[Page {page_num + 1}] {p}")
                
    return chunks

def main():
    print("=== 🤖 INTERACTIVE PDF Q&A ASSISTANT (RAG ENGINE) ===")
    
    # 1. Ask user for a valid local PDF path file target
    pdf_path = input("Enter the absolute path to your target PDF file: ").strip()
    # Strip accidental quote marks if user dragged-and-dropped the file into the console
    pdf_path = pdf_path.strip("'\"")
    
    chunks = extract_text_from_pdf(pdf_path)
    if not chunks:
        print("Stopping engine. No text blocks could be processed.")
        return
        
    # 2. Spin up local database storage layer (Day 6 architecture)
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage")
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    collection_name = "pdf_knowledge_base"
    try:
        chroma_client.delete_collection(name=collection_name)
    except Exception:
        pass
        
    collection = chroma_client.create_collection(name=collection_name)
    
    # 3. Index the freshly extracted data chunks
    print(f"📥 Indexing {len(chunks)} structural vector coordinates locally...")
    doc_ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=doc_ids)
    print("✅ System indexing sequence complete! Your PDF data is loaded.")
    
    # 4. Initialize Interactive User Interface Query Loop
    print("\n🚀 System Ready! Ask any question about your document (Type 'exit' or 'quit' to close).")
    
    while True:
        query = input("\n🔎 Ask a Question: ").strip()
        if query.lower() in ['exit', 'quit']:
            print("Shutting down the assistant. Great session!")
            break
        if not query:
            continue
            
        # 5. Retrieval Phase: Query closest context frame (Day 5 architecture)
        retrieval = collection.query(query_texts=[query], n_results=1)
        if not retrieval['documents'] or not retrieval['documents'][0]:
            print("⚠️ The indexing layer failed to find any close semantic vectors.")
            continue
            
        context = retrieval['documents'][0][0]
        print(f"\n💡 Found closest text match in source document:\n{context}")
        
        # 6. Generation Phase: Secure grounded streaming context window instructions
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict technical document review agent. Answer the user's question using "
                    "ONLY the provided background documentation context. If the true answer cannot be confidently "
                    "deduced from the provided text, state clearly that the document does not contain the facts. "
                    "Keep answers crisp and accurate."
                    f"\n\nBACKGROUND CONTEXT DOCUMENTATION:\n{context}"
                )
            },
            {"role": "user", "content": query}
        ]
        
        print("\n🤖 Assistant: ", end="")
        try:
            stream = client.chat.completions.create(
                model="openrouter/free",
                messages=messages,
                stream=True,
                extra_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "GenAI 30 Day PDF Q&A App",
                }
            )
            
            # Continuous buffer trace to handle multi-engine formats smoothly
            for chunk in stream:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    content = getattr(chunk.choices[0].delta, 'content', None)
                    if content:
                        print(content, end="", flush=True)
                        continue
                if hasattr(chunk, 'text'):
                    print(chunk.text, end="", flush=True)
            print() # Print a clean trailing space for the next loop line
            
        except Exception as e:
            print(f"\n⚠️ Network transaction interrupted: {e}")

if __name__ == "__main__":
    main()