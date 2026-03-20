# A CLI AGENT THAT JUST SITS AND GET ALL OF IT DONE TRHOUGH YOUR CLI ONLY :)

- Langchain 
    - chatnovita 
    - chatgooglegenai
    - chatollama 
- Langgraph 
- Langfuse 
- Rich logger 
- retry logic (tenacity)
- sqllite 
- qdrant vector store 
- pydantic 
- dotenv 
- loguru
- langchain_ollama 
- langchain_google_genai
- langchain_openai




- Python 
- Javascript
- Scaffold projects 
- Ruby 
- Go 
- java 
- rust 
- c 
- cpp

warnings

add in system prompt about memory related queries like "Remeber I am an Incapable developer" will be handled in the update_memory node no need of adding them in the future but if you need it for something else please you are free to do what ever the fuck you wanna do 


Add tabs feature so that you dont need to restart the app for a new chat just add a tab and continue to new chat 



No indexing for now

So basically what we need is an auth layer so that when using qdrant cloud or using the application with the help of cloud services then you literally just have to have an user_id , a token so that all of your data isnt a public access ( most importantly not in a LLM's traning corpus)

For now we are sticking with everything local so no need of a user_id

context summarization at the first node just chip off some of the ai-human messages by replacing them with a summary system message like Eariler you and the user discussed this-this 



INDEXING MUST BE SPECIFIED AS IN A USER SHOULD OPEN UP AND INIT INTO A PROJECT FOR TALKING WITH THE PROJECT 