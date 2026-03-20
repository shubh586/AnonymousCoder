from langchain_core.tools import tool


@tool 
def get_user_memory()->str:
    """
    Get user details stored as memories
    Returns:
        str: returned memories 
    """
    memories_path="user_space/memories.md"
    with open(memories_path,"r") as f:
        lines_read=f.readlines()
        memories=[]
        for line in lines_read:
            if line:
                memories.append(line.strip())
    return " ".join(memories)

@tool
def update_memories(updated_memories:str):
    """
    Update the current memories to new one
    Args:
        updated_memories (str): The new memories to be updated
    """
    
    memories_path="user_space/memories.md"
    with open(memories_path,"w") as f:
        f.write(updated_memories)