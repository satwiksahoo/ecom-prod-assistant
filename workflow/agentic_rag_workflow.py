from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_mcp_adapters.client import MultiServerMCPClient
from  prod_assistant.prompt_library.prompts import PROMPT_REGISTRY, PromptType
from prod_assistant.retriever.retrieval import Retriever
from prod_assistant.utils.model_loader import ModelLoader
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from prod_assistant.evaluation.ragas_eval import evaluate_context_precision, evaluate_response_relevancy

from prod_assistant.evaluation.ragas_eval import evaluate_context_precision , evaluate_response_relevancy

class AgenticRAG:
    """Agentic RAG pipeline using LangGraph."""

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
        rewrite_count: int  #

    def __init__(self):
        self.retriever_obj = Retriever()
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_llm()
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)
        
        
        self.mcp_client = MultiServerMCPClient({
        "product_retriever": {
            "command": "python",
            "args": ["prod_assistant/mcp_servers/product_search_server.py"],
            "transport": "stdio"
        }
    })
        self.mcp_tools = asyncio.run(self.mcp_client.get_tools())

    # ---------- Helpers ----------
    def _format_docs(self, docs) -> str:
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
    
    
    def documents_to_string(self,docs):
        parts = []
        for d in docs:
            meta = d.metadata or {}
            parts.append(
                f"Product: {meta.get('product','N/A')}\n"
                f"Score: {meta.get('score','N/A')}\n"
                f"Review:\n{d.page_content.strip()}"
            )
        return "\n\n---\n\n".join(parts)

    # ---------- Nodes ----------
    
    def _start(self, state: AgentState):
        return state
    
    def _llm_call(self, state : AgentState):
        
        messages = state["messages"]
        last_message = messages[-1].content
        
        prompt = ChatPromptTemplate.from_template(
                "You are a helpful assistant. Answer the user directly.\n\nQuestion: {question}\nAnswer:"
            )
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"question": last_message})
        # return {"messages": [HumanMessage(content=response)]}
        
        return {
        "messages": [HumanMessage(content=response)],
        "rewrite_count": state.get("rewrite_count")
    }
        
        
    
    def _ai_assistant(self, state: AgentState):
        print("--- CALL ASSISTANT ---")
        messages = state["messages"]
        last_message = messages[-1].content
        
        prompt = ChatPromptTemplate.from_template('''you are a smart assistant. with the knowledge of this message -> {last_message}, 
                                                recommend me which tool should i call between retriever or llm_call ,
                                                retriever will use vector database to search from records of mobile phones reviews and then generate output using llm,
                                                while llm_call will simply generate output using llm not using the vector database, llm_call only used when the input 
                                                message does not contain anything related to the phone or mobiles
                                                
                                                else for normal conversation use llm_call
                                                
                                                only output should be between retriever or llm_call
                                                ''')
        
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({"last_message": last_message})

        # if any(word in last_message.lower() for word in ["price", "review", "product" , 'which' , 'how' , 'what' , 'where', 'can']):
        #     # return {"messages": [HumanMessage(content="TOOL: retriever")]}
        #     return 'retriever'
        # else:
            
        #     return 'llm_call'
        
        
        if response.lower() == 'retriever':
            print('retriever tool is called from assistant')
            return 'retriever'
        
        else:
            print('direct llm_call tool is called from assistant')
            
            return 'llm_call'
            # prompt = ChatPromptTemplate.from_template(
            #     "You are a helpful assistant. Answer the user directly.\n\nQuestion: {question}\nAnswer:"
            # )
            # chain = prompt | self.llm | StrOutputParser()
            # response = chain.invoke({"question": last_message})
            # return {"messages": [HumanMessage(content=response)]}

    # def _vector_retriever(self, state: AgentState):
        
    #     print("--- RETRIEVER ---")
    #     query = state["messages"][-1].content
    #     retriever = self.retriever_obj.load_retriver()
    #     docs = retriever.invoke(query)
    #     context = self._format_docs(docs)
    #     return {"messages": [HumanMessage(content=context)]}
    
    # def _vector_retriever(self, state: AgentState):
    #     print("--- RETRIEVER (MCP) ---")
    #     query = state["messages"][-1].content

    #     # Pick MCP tool by name
    #     tool = next(t for t in self.mcp_tools if t.name == "get_product_info")
    #     tool = next(t for t in self.mcp_tools)
        

    #     # Call MCP tool
    #     result = asyncio.run(tool.ainvoke({"query": query}))

    #     context = result if result else "No data"
    #     # return {"messages": [HumanMessage(content=context)]}
    
    #     return {
    #     "messages": [HumanMessage(content=context)],
    #     "rewrite_count": state.get("rewrite_count")
    # }
    
    def _vector_retriever(self, state: AgentState):
        print("--- TOOL SELECTOR (LLM + MCP) ---")
        query = state["messages"][-1].content

        # Step 1: Ask LLM which tool to use
        tool_prompt = ChatPromptTemplate.from_template("""
    You are a tool selector.

    Tools:
    1. get_product_info → Use when query is about products, phones, reviews, price, features.
    2. web_search → Use when query is general, recent, news, or not in local product database.

    User query: {query}

    Respond with only one word:
    get_product_info OR web_search
    """)

        chain = tool_prompt | self.llm | StrOutputParser()
        chosen_tool = chain.invoke({"query": query}).strip()

        print("LLM chose tool: ", chosen_tool)

        # Step 2: Pick MCP tool by name
        try:
            tool = next(t for t in self.mcp_tools if t.name == chosen_tool)
        except StopIteration:
            print("Invalid tool from LLM, defaulting to get_product_info")
            tool = next(t for t in self.mcp_tools if t.name == "get_product_info")

        # Step 3: Call MCP tool
        result = asyncio.run(tool.ainvoke({"query": query}))

        context = result if result else "No data"

        return {
            "messages": [HumanMessage(content=context)],
            "rewrite_count": state.get("rewrite_count", 0)
        }


    def _web_search(self , state : AgentState):
        
        print('----- WEB SEARCH -------')
        
        
        question = state["messages"][0].content
        docs = state["messages"][-1].content
        
        
        tool = next(t for t in self.mcp_tools if t.name == "web_search")
    
        

        # Call MCP tool
        result = asyncio.run(tool.ainvoke({"query": question}))
        
        
        
        return {
        "messages": [HumanMessage(content=result)],
        "rewrite_count": state.get("rewrite_count")
    }


    def _grade_documents(self, state: AgentState) -> Literal["generator", "rewriter"]:
        print("--- GRADER ---")
        question = state["messages"][0].content
        docs = state["messages"][-1].content
        
        
        if state.get("rewrite_count", 0) >= 2:
        #     tool = next(t for t in self.mcp_tools if t.name == "web_search")
    
        

        # # Call MCP tool
        #     result = asyncio.run(tool.ainvoke({"query": question}))
            
        #     message =  state.get("messages")
        #     message.append(HumanMessage(content=result))
        
            new_state = self._web_search(state)
            
            state['messages'] = new_state['messages']
            state["rewrite_count"] = new_state.get("rewrite_count", state.get("rewrite_count", 0))
            
            return "generator"

        # prompt = PromptTemplate(
        #     template="""You are a grader. Question: {question}\nDocs: {docs}\n
        #     Are docs relevant to the question? Answer yes or no.""",
        #     input_variables=["question", "docs"],
        # )
        
        retrieved_contexts = [docs]  #
        
        response = docs
        
        
        
        context_score = evaluate_context_precision(
        query= question,
        response=response,
        retrieved_context=retrieved_contexts,
    )

        relevancy_score = evaluate_response_relevancy(
        query=question,
        response=response,
        retrieved_context=retrieved_contexts,
    )
        
        
        # chain = prompt | self.llm | StrOutputParser()
        # score = chain.invoke({"question": question, "docs": docs})
        # return "generator" if "yes" in score.lower() else "rewriter"
        
        
        prompt = PromptTemplate(
            template="""You are a grader. Question: {question}\nDocs: {docs}\n
            Are docs relevant to the question using the relevancy_score {relevancy_score} ? Answer yes or no.""",
            input_variables=["question", "docs" , 'relevancy_score' ],
            
        )
        
        
        chain = prompt | self.llm | StrOutputParser()
        score = chain.invoke({"question": question, "docs": docs  , 'relevancy_score' : relevancy_score})
        return "generator" if "yes" in score.lower() else "rewriter"
        
        # return "generator" if context_score > 0.80 and relevancy_score > 0.35  else "rewriter"
        

    def _generate(self, state: AgentState):
        print("--- GENERATE ---")
        question = state["messages"][0].content
        docs = state["messages"][-1].content
        prompt = ChatPromptTemplate.from_template(
            PROMPT_REGISTRY[PromptType.PRODUCT_BOT].template
        )
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": docs, "question": question})
        # return {"messages": [HumanMessage(content=response)]}
        return {
        "messages": [HumanMessage(content=response)],
        "rewrite_count": state.get("rewrite_count")
    }

    # def _rewrite(self, state: AgentState):
    #     print("--- REWRITE ---")
    #     question = state["messages"][0].content
    #     new_q = self.llm.invoke(
    #         [HumanMessage(content=f"Rewrite the query to be clearer: {question}")]
    #     )
    #     return {"messages": [HumanMessage(content=new_q.content)]}
    
    
    def _rewrite(self, state: AgentState):
        print("--- REWRITE (SEARCH OPTIMIZED) ---")
        
        count = state.get("rewrite_count", 0) + 1

        question = state["messages"][0].content

        prompt = ChatPromptTemplate.from_template("""
    You are a query optimizer for a product search engine.

    Your job:
    - Rewrite the user query to make it work well with a vector database of mobile phone reviews.
    - Add missing product keywords if needed (like phone, mobile, smartphone, model names).
    - Remove vague or conversational words.
    - Keep it short, specific, and searchable.
    - Do NOT answer the question.

    Original query: {question}

    Optimized search query:
    """)

        chain = prompt | self.llm | StrOutputParser()
        rewritten = chain.invoke({"question": question}).strip()

        print("Rewritten query:", rewritten)

        # return {"messages": [HumanMessage(content=rewritten)]}
        
        return {
        "messages": [HumanMessage(content=rewritten)],
        "rewrite_count": count
    }


    # ---------- Build Workflow ----------
    def _build_workflow(self):
        workflow = StateGraph(self.AgentState)
        workflow.add_node("Assistant", self._ai_assistant)
        workflow.add_node("retriever", self._vector_retriever)
        workflow.add_node("Generator", self._generate)
        workflow.add_node("Rewriter", self._rewrite)
        workflow.add_node('grader', self._grade_documents)
        workflow.add_node('start' , self._start)
        workflow.add_node('llm_call' , self._llm_call)

        workflow.add_edge(START, "start")
        workflow.add_conditional_edges(
            
            'start' , self._ai_assistant,
            
            {
        "retriever": "retriever",
        "llm_call": "llm_call",
                
                
            }
        )
        
        workflow.add_conditional_edges(
            "retriever",
            self._grade_documents,
            {"generator": "Generator", "rewriter": "Rewriter"},
        )
        
        
        workflow.add_edge("Generator", END)
        workflow.add_edge("llm_call", END)
        
        # workflow.add_edge("Rewriter", "Assistant")
        workflow.add_edge("Rewriter", "start")
        
        
        
        
        return workflow

    # ---------- Public Run ----------
    # async def run(self, query: str,thread_id: str = "default_thread") -> str:
    #     """Run the workflow for a given query and return the final answer."""
    #     result = await self.app.invoke({"messages": [HumanMessage(content=query)] , 'rewrite_count' : 0},
    #     config={"configurable": {"thread_id": thread_id}})
    #     return result["messages"][-1].content
    # async def run(self, query: str, thread_id: str = "default_thread") -> str:
        
    #     print("RUN CALLED FROM:", __file__)
    #     result = await self.app.ainvoke(
    #         {"messages": [HumanMessage(content=query)], "rewrite_count": 0},
    #         config={"configurable": {"thread_id": thread_id}}
    #     )
    #     return result["messages"][-1].content
    
    
    async def run(self, query: str, thread_id: str = "default_thread") -> str:
        print("RUN FROM FILE:", __file__)
        result = await self.app.ainvoke(
            {"messages": [HumanMessage(content=query)], "rewrite_count": 0},
            config={"configurable": {"thread_id": thread_id}}
        )
        return result["messages"][-1].content


        # function call with be asscoiate
        # you will get some score
        # put condition behalf on that score
        # if relevany>0.75
            #return
        #else:
            #contine


# if __name__ == "__main__":
    
    
#     rag_agent = AgenticRAG()
#     answer = rag_agent.run("what is the temperature of delhi")
#     print("\nFinal Answer:\n", answer)


if __name__ == "__main__":
    import asyncio

    rag_agent = AgenticRAG()

    async def main():
        answer = await rag_agent.run("what is the temperature of delhi")
        print("\nFinal Answer:\n", answer)

    asyncio.run(main())

    
    # retrieved_contexts,response = invoke_chain(user_query)
    
    # #this is not an actual output this have been written to test the pipeline
    # #response="iphone 16 plus, iphone 16, iphone 15 are best phones under 1,00,000 INR."
    
    # context_score = evaluate_context_precision(user_query,response,retrieved_contexts)
    # relevancy_score = evaluate_response_relevancy(user_query,response,retrieved_contexts)
    
    # print("\n--- Evaluation Metrics ---")
    # print("Context Precision Score:", context_score)
    # print("Response Relevancy Score:", relevancy_score)