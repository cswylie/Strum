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
- I have added an interface that will open upon composing the docker build, and you can interact with the chatbot there.
- You can access the interface at ***localhost:7860***.
- Just run:
```bash
docker-compose up
```
- And the container will spin up again.
- The container will also create a data folder to store the relevent data.

## Important Info
- I was originally using this locally with the use of ollama to pull the LLM and run it locally. This can still be done, but I opted to instead use HuggingFace to query the chatbot for results because it was free and faster. 
- Of course, this means that you now need a **HuggingFace** account and an authentification token to be able to even access the chatbot, it's not open for everyone. While this is a pain, I opted to go this way because it makes the service as a whole smaller, faster, and more efficient.
- If you are going to clone this repo, **make sure** to create a ***.env*** file and add the **HF_TOKEN** as an environment variable, then everything should run smoothly.