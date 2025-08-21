## README/Strum RAG Pipeline

- This is app works in combination with a frontend access point.
- I have the correct frontend detailed in my website repo. I was unable to find a hosting website to host this, so I'm just chucking it here for now to be used. 
- Strum is a RAG pipeline using Ableton Documentation to provide relevent help when using Ableton.
- It provides context to queries sent to the Open AI model: **gpt-oss-20b** and it will respond accordingly. 

## How to Use/Download
- There is a ***docker-compose.yml*** file included in the repo. Just simply run:
```bash
docker-compose up --build
```
- This will build and run the container, opening port 8000 on localhost.
- Query ***http://localhost:8000/query*** and it will return the response from the chatbot and the history of the conversation.
- The history is an array of Objects in the form {question: "", answer: ""}.
- Just run:
```bash
docker-compose up
```
- And the container will spin up again.
- The container will also create a data folder to store the relevent data.