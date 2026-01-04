import uuid
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.graph import graph

def get_content_text(content):
    """Helper to extract text from message content which might be a list or string."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extract text from blocks like {'type': 'text', 'text': '...'}
        return "".join([block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"])
    return str(content)

def main():
    print("Welcome to ESILV Smart Assistant (Terminal Mode)")
    print("Type 'quit' or 'exit' to stop.")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["quit", "exit"]:
                break
                
            # Stream the graph updates
            events = graph.stream(
                {"messages": [("user", user_input)]},
                config,
                stream_mode="values"
            )
            
            for event in events:
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    if last_msg.type == "ai":
                        print(f"Assistant: {get_content_text(last_msg.content)}")
                        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
