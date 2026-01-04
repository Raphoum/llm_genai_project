import os
import json
from typing import Annotated, Literal, TypedDict, Union, List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# --- Configuration ---
EMBEDDING_MODEL = "models/embedding-001"
LLM_MODEL = "gemini-2.5-flash" 
PERSIST_DIRECTORY = "chroma_db"
REGISTRATION_FILE = "data/registrations.json"

# --- Tools ---

@tool
def retrieve_esilv_info(query: str):
    """Retrieves information about ESILV (programs, admissions, courses) from the knowledge base."""
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(query)
        if not docs:
           return "No specific information found in the documents."
        return "\n\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"Error retrieving information: {e}"

@tool
def save_registration(name: str, email: str, interest: str):
    """Saves a user's registration details."""
    os.makedirs(os.path.dirname(REGISTRATION_FILE), exist_ok=True)
    
    data = {"name": name, "email": email, "interest": interest}
    
    existing_data = []
    if os.path.exists(REGISTRATION_FILE):
        try:
            with open(REGISTRATION_FILE, "r") as f:
                existing_data = json.load(f)
        except:
            pass
            
    existing_data.append(data)
    
    with open(REGISTRATION_FILE, "w") as f:
        json.dump(existing_data, f, indent=2)
        
    return "Registration saved successfully!"

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# --- Nodes ---

def chatbot_node(state: AgentState):
    """Main chatbot node."""
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
    
    # Bind tools including registration
    tools = [retrieve_esilv_info, save_registration]
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are the ESILV Smart Assistant.
    
    **Knowledge Base**:
    - Use `retrieve_esilv_info` to answer questions about programs, courses, or admissions.
    
    **Registration**:
    - If a user wants to register, apply, or be contacted:
      1. Ask for their Name.
      2. Ask for their Email.
      3. Ask for their Area of Interest (e.g., Data Science, Finance, IoT).
      4. Once you have ALL three, use the `save_registration` tool to save them.
      5. Confirm to the user that they are registered.
      
    **Behavior**:
    - Be helpful and polite.
    - If you miss information for registration, ask for it specifically.
    - Do not invent information.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# --- Graph Construction ---

tools = [retrieve_esilv_info, save_registration]
tool_node = ToolNode(tools)

workflow = StateGraph(AgentState)

workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "chatbot")
workflow.add_conditional_edges("chatbot", tools_condition)
workflow.add_edge("tools", "chatbot")

# Add memory
memory = MemorySaver()

graph = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    print("Agent Graph with Memory compiled.")
