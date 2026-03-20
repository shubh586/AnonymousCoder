# As you know llms are stupid they will do what ever they want we cant let that happen right
# but we want autonomy right so we just provide this tool that hey you may just put in a string
# ask the user that is this ok or what changes do you want
from langchain_core.tools import tool


@tool
def ask_user_tool(question:str):
    """Tool to bring in user input

    Returns:
        The details needed by the user 
    """
    ans=input(question)
    return ans