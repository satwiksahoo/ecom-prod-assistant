import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
def is_bad_result(text: str, query: str) -> bool:
    if not text or not text.strip():
        return True
    
    # too short
    if len(text) < 100:
        return True

    # check if any important word from query appears
    q_words = [w.lower() for w in query.split() if len(w) > 3]
    text_lower = text.lower()

    if not any(w in text_lower for w in q_words):
        return True

    return False

async def main():
    client = MultiServerMCPClient({
        "hybrid_search": {   # server name
            "command": "python",
            "args": [
                "/Users/satwiksahoo/Desktop/CodeBasics/LLMops/ecommerce_agent/ecom-prod-assistant/prod_assistant/mcp_servers/product_search_server.py"
            ],  # absolute path
            "transport": "streamable_http",
        }
    })
    
#     client = MultiServerMCPClient({
#     "hybrid_search": {
#         "url": "http://localhost:8000/mcp",
#         "transport": "streamable_http",
#     }
# })

    # Discover tools
    tools = await client.get_tools()
    print("Available tools:", [t.name for t in tools])

    # Pick tools by name
    retriever_tool = next(t for t in tools if t.name == "get_product_info")
    web_tool = next(t for t in tools if t.name == "web_search")

    # --- Step 1: Try retriever first ---
    #query = "Samsung Galaxy S25 price"
    # query = "iPhone 15"
    query = "what is the cost of Iphone17 pro?"
    retriever_result = await retriever_tool.ainvoke({"query": query})
    print("\nRetriever Result:\n", retriever_result)

    # --- Step 2: Fallback to web search if retriever fails ---
    # if not retriever_result.strip() or "No local results found." in retriever_result:
    #     print("\n No local results, falling back to web search...\n")
    #     web_result = await web_tool.ainvoke({"query": query})
    #     print("Web Search Result:\n", web_result)

    # --- Step 2: Smart fallback to web search ---
    if is_bad_result(retriever_result, query):
        print("\nRetriever result looks weak, falling back to web search...\n")
        web_result = await web_tool.ainvoke({"query": query})
        print("Web Search Result:\n", web_result)
    # else:
        # print("\nUsing retriever result (looks relevant).\n")
        # print("\nRetriever Result:\n", retriever_result)



# async def main():
#     client = MultiServerMCPClient({
#         "hybrid_search": {
#             "command": "python",
#             "args": [
#                 "/Users/satwiksahoo/Desktop/CodeBasics/LLMops/ecommerce_agent/ecom-prod-assistant/prod_assistant/mcp_servers/product_search_server.py"
#             ],
#             "transport": "stdio",
#         }
#     })

#     try:
#         tools = await client.get_tools()
#         print("Available tools:", [t.name for t in tools])

#         retriever_tool = next(t for t in tools if t.name == "get_product_info")
#         web_tool = next(t for t in tools if t.name == "web_search")

#         query = "give me weather of delhi during summer?"
#         retriever_result = await retriever_tool.ainvoke({"query": query})
#         print("\nRetriever Result:\n", retriever_result)

#         if not retriever_result.strip() or "No local results found." in retriever_result:
#             print("\nNo local results, falling back to web search...\n")
#             web_result = await web_tool.ainvoke({"query": query})
#             print("Web Search Result:\n", web_result)

    # finally:
    #     # 👇 this prevents the “event loop is closed” error
    #     await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())