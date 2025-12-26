import sys
import whisper
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class DocumentManager:
    """Manages the state of the document being edited."""
    def __init__(self):
        self.content = ""

    def update(self, content: str) -> str:
        """Updates the document with the provided content."""
        self.content = content
        return f"Document has been updated successfully! The current content is:\n{self.content}"

    def save(self, filename: str) -> str:
        """Save the current document to a text file."""
        if not filename.endswith(".txt"):
            filename = f"{filename}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.content)
            return f"Document has been saved successfully to '{filename}'."
        except Exception as e:
            return f"Error saving document: {str(e)}"

    def get_content(self):
        return self.content

def create_agent():
    """Creates and compiles the LangGraph agent."""
    doc_manager = DocumentManager()
    
    # Define tools bound to the manager instance
    @tool
    def update(content: str) -> str:
        """Updates the document with the provided content"""
        return doc_manager.update(content)

    @tool
    def save(filename: str) -> str:
        """Save the current document to a text file and finish the proccess."""
        return doc_manager.save(filename)
    
    whisper_model = whisper.load_model("small")
    
    @tool
    def transcribe_audio(audio_data: str) -> str:
        """Transcribes an audio file to text."""
        try:
            result = whisper_model.transcribe(audio_data)
            return result["text"]
        except Exception as e:
            return f"Error transcribing audio: {e}"

    tools = [update, save, transcribe_audio]
    
    # Initialize model
    # Note: Ensure OPENAI_API_KEY is set in .env
    model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)


    
    def agent_node(state: AgentState) -> AgentState:
        system_prompt = SystemMessage(content=f"""
        You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
        
        - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
        - If the user wants to save and finish, you need to use the 'save' tool.
        - Make sure to always show the current document state after modifications.
        
        The current document content is:
        {doc_manager.get_content()}
        """)
        
        # Filter out previous system messages to avoid duplication if we were appending blindly,
        # but since we reconstruct the list for the model, it's fine.
        # However, we should ensure the system prompt is always first.
        messages = [system_prompt] + [m for m in state["messages"] if not isinstance(m, SystemMessage)]
        
        response = model.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the AI called a tool, go to tools
        if isinstance(last_message, BaseMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
            
        # Otherwise, stop and wait for user
        return END

    # Build graph
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    graph.add_edge("tools", "agent")

    return graph.compile()

def main():
    app = create_agent()
    print("\n ==== DRAFTER ====")
    print("I'm ready to help you update a document. What would you like to create?")

    chat_history = []

    while True:
        try:
            user_input = input("\n👤 USER: ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Add user message to history
            chat_history.append(HumanMessage(content=user_input))
            
            # Run the graph
            # We pass the full history. Since we don't use a checkpointer, 
            # the graph starts fresh but we feed it the history.
            inputs = {"messages": chat_history}
            
            # Stream the execution to show intermediate steps (tool calls)
            current_messages = []
            for event in app.stream(inputs, stream_mode="values"):
                current_messages = event["messages"]
                if not current_messages:
                    continue
                
                last_msg = current_messages[-1]
                
                # We only want to print the *new* messages generated in this turn
                # But stream_mode="values" returns the full state.
                # A simple heuristic: if it's a tool message or an AI message that is NOT in our initial chat_history (before this turn)
                # But chat_history is updated at the end.
                
                # Let's just print the last message if it's interesting
                if isinstance(last_msg, ToolMessage):
                    print(f"\n🛠️ TOOL RESULT: {last_msg.content}")
                elif isinstance(last_msg, BaseMessage) and hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    tool_names = [tc['name'] for tc in last_msg.tool_calls]
                    print(f"\n🔧 USING TOOLS: {tool_names}")
                elif isinstance(last_msg, BaseMessage) and not isinstance(last_msg, HumanMessage):
                    # Final AI response usually
                    pass 

            # Update chat history with the final state
            # We need to get the final state. The loop ends with the final state.
            # But `stream` yields intermediate states.
            # We can just run invoke to get the final state cleanly if we don't care about real-time streaming of tokens.
            # But we want to see tool usage.
            
            # Let's grab the final state from the last event
            final_messages = current_messages
            
            # Print the final response
            last_response = final_messages[-1]
            if isinstance(last_response, BaseMessage) and not isinstance(last_response, HumanMessage) and not isinstance(last_response, ToolMessage):
                 print(f"\n🤖 AI: {last_response.content}")

            # Update history
            chat_history = final_messages
            
            # Check if we should exit (if saved)
            # We look for a successful save in the recent messages of this turn
            for msg in reversed(chat_history[-3:]): # Check last few messages
                if isinstance(msg, ToolMessage) and "saved successfully" in msg.content:
                    print("\nDocument saved. Exiting...")
                    return

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            # Optionally break or continue
            break

if __name__ == "__main__":
    main()
