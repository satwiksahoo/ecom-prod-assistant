import os
from langchain_astradb import AstraDBVectorStore
from typing import List
from langchain_core.documents import Document
from prod_assistant.utils.model_loader import ModelLoader
from prod_assistant.utils.config_loader import load_config
from dotenv import load_dotenv

from prod_assistant.evaluation.ragas_eval import evaluate_context_precision , evaluate_response_relevancy
# from langchain_community.document_compressors import LLMChainFilter
# from langchain_community.retrievers import ContextualCompressionRetriever


class Retriever:
    def __init__(self):
        
        self.model_loader = ModelLoader()
        self.config = load_config()
        self._load_env_variables()
        self.vstore = None
        self.retriever = None
        
    
    def _load_env_variables(self):
        
        load_dotenv()
        
        required_vars = ["OPENAI_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
        
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  #OPENAI_API_KEY
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")
        
    
    def load_retriver(self):
        
        if not self.vstore:
            collection_name = self.config['astra_db']['collection_name']
            
            self.vstore = AstraDBVectorStore(
                embedding = self.model_loader.load_embedding_model(),
                collection_name=collection_name,
                api_endpoint=self.db_api_endpoint,
                token = self.db_application_token,
                namespace=self.db_keyspace
            )
            
        if not self.retriever:
            
            top_k = self.config['retriever']['top_k'] if 'retriever' in self.config else 3
            
            retriever = self.vstore.as_retriever(  search_type = 'mmr' ,
                                                 search_kwargs = {'k' : top_k , 
                                                                  'fetch_k' : 20,
                                                                    'lambda_mult' : 0.7 , 
                                                                    'score_threshold' : 0.3 })
            
            
            
            print('Retriever loaded successfully')
            
            return retriever
        
        
        
        
    
    def call_retriever(self, query):
        
        self.retriever = self.load_retriver()
        
        output = self.retriever.invoke(query)
        
        return output
        
    
# if __name__=='__main__':
#     user_query = "Can you suggest good mobile with great camera?"
    
#     retriever_obj = Retriever()
    
#     retrieved_docs = retriever_obj.call_retriever(user_query)
    
#     retrieved_context = [ doc.page_content  for doc in retrieved_docs]
    
#     def format_docs( docs) -> str:
#         if not docs:
#             return "No relevant documents found."
#         formatted_chunks = []
#         for d in docs:
#             meta = d.metadata or {}
#             formatted = (
#                 f"Title: {meta.get('product_title', 'N/A')}\n"
#                 f"Price: {meta.get('price', 'N/A')}\n"
#                 f"Rating: {meta.get('rating', 'N/A')}\n"
#                 f"Reviews:\n{d.page_content.strip()}"
#             )
#             formatted_chunks.append(formatted)
#         return "\n\n---\n\n".join(formatted_chunks)
    
#     retrieved_formatted_docs = [ format_docs(doc) for doc in retrieved_context]
    
    
#     context_score = evaluate_context_precision()
#     relevancy_score = evaluate_response_relevancy()
    
#     context_score = evaluate_context_precision(
#     query=user_query,
#     response=response,
#     retrieved_context=retrieved_formatted_docs,
# )

#     relevancy_score = evaluate_response_relevancy(
#     query=user_query,
#     response=response,
#     retrieved_context=retrieved_formatted_docs,
# )

    
    
#     print(retrieved_docs)


if __name__ == "__main__":
    user_query = "what is the cost of iphone17"

    retriever_obj = Retriever()
    retrieved_docs = retriever_obj.call_retriever(user_query)

    def format_docs(docs) -> str:
        if not docs:
            return "No relevant documents found."
        formatted_chunks = []
        for d in docs:
            meta = d.metadata or {}
            formatted = (
                f"Title: {meta.get('product_title', 'N/A')}\n"
                f"Price: {meta.get('price', 'N/A')}\n"
                f"Rating: {meta.get('rating', 'N/A')}\n"
                f"Reviews:\n{d.page_content.strip()}"
            )
            formatted_chunks.append(formatted)
        return "\n\n---\n\n".join(formatted_chunks)
    
    
    def documents_to_string(docs):
        parts = []
        for d in docs:
            meta = d.metadata or {}
            parts.append(
                f"Product: {meta.get('product','N/A')}\n"
                f"Score: {meta.get('score','N/A')}\n"
                f"Review:\n{d.page_content.strip()}"
            )
        return "\n\n---\n\n".join(parts)


    # RAGAS expects: List[str]
    retrieved_contexts = [format_docs(retrieved_docs)]

    # Dummy response or from your RAG chain
    # response = "You can consider iPhone 15, Pixel 8 and Samsung S23 for great cameras."
    
    # print(type(retrieved_docs), retrieved_docs)
    # print(type(retrieved_contexts), retrieved_contexts)
    
    
    response = documents_to_string(retrieved_docs)
    
    # response = retriever.invoke(user_query)


    context_score = evaluate_context_precision(
        query=user_query,
        response=response,
        retrieved_context=retrieved_contexts,
    )

    relevancy_score = evaluate_response_relevancy(
        query=user_query,
        response=response,
        retrieved_context=retrieved_contexts,
    )

    print("Context Precision:", context_score)
    print("Response Relevancy:", relevancy_score)
    print(retrieved_docs)
    
