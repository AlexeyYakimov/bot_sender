import os
import random

def get_message(state: str) -> str:
    """
    Get a random message from the appropriate message file based on state.
    
    Args:
        state: Current state ('occupy' or 'empty')
        
    Returns:
        A random message string from the specified file
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct filename based on state
    filename = os.path.join(current_dir, "messages", f"{state}.txt")
    
    # Check if file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Message file not found: {filename}")
        
    # Read all messages from file
    with open(filename, 'r', encoding='utf-8') as f:
        messages = f.read().splitlines()
        
    # Filter out empty lines
    messages = [msg for msg in messages if msg.strip()]
    
    if not messages:
        raise ValueError(f"No messages found in file: {filename}")
        
    # Return random message
    return random.choice(messages) 