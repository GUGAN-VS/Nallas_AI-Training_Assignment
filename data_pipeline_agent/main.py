import asyncio
from dotenv import load_dotenv
from config import SYSTEM_PROMPT, MODEL, TEMPERATURE, MAX_TOKENS

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from datetime import datetime

load_dotenv()

MAX_HISTORY = 5  # number of past conversations to remember

async def main():
    today = datetime.now().strftime("%Y-%m-%d")
    DYNAMIC_SYSTEM_PROMPT = SYSTEM_PROMPT + f"\n\nCurrent date: {today}. Use this for any date-related questions — do NOT query the database for today's date."

    client = MultiServerMCPClient(
        {
            "etl": {
                "command": "python",
                "args": [r"C:\Users\Gugan\Desktop\AI-Training-Assignment\data_pipeline_agent\mcp_servers\etl_stdio_server.py"],
                "transport": "stdio",
                "cwd": r"C:\Users\Gugan\Desktop\AI-Training-Assignment\data_pipeline_agent",
            },
            "warehouse": {
                "url": "http://localhost:9001/mcp",
                "transport": "streamable-http",
            },
            "schema": {
                "url": "http://localhost:9002/mcp",
                "transport": "streamable-http",
            },
        }
    )

    tools = await client.get_tools()

    print("Connected Tools:")
    for tool in tools:
        print(" -", tool.name)

    llm = ChatGroq(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=DYNAMIC_SYSTEM_PROMPT
    )

    print("\nAgent Ready.\n")

    # ── Conversation history ──
    conversation_history = []  # stores (HumanMessage, AIMessage) pairs

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        # Keep only last MAX_HISTORY exchanges
        recent_history = conversation_history[-MAX_HISTORY:]

        # Build flat message list: system + past exchanges + current question
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for human_msg, ai_msg in recent_history:
            messages.append(human_msg)
            messages.append(ai_msg)
        messages.append(HumanMessage(content=user_input))

        response = await agent.ainvoke({"messages": messages})

        assistant_reply = response["messages"][-1].content

        # Save this exchange to history
        conversation_history.append((
            HumanMessage(content=user_input),
            AIMessage(content=assistant_reply)
        ))

        print("\nAssistant:", assistant_reply)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())