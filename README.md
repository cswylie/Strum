## README/Ableton AI Assistant

- If you want to run locally, you can install the dependencies by using the command:
```python
pip install -r requirements.txt
```
- Then you can navigate to ui.py in the app directory and run:
```python
python3 ui.py
```
- Otherwise, I recommend running it in the provided docker container.
## Docker Run Instructions:
- Build the image:
```bash
docker build -t ai-music-assistant .
```
- Run the container:
```bash
docker run --gpus all -e GRADIO_HOST=0.0.0.0 -e GRADIO_PORT=7860 -p 7860:7860 ai-music-assistant
```
## Running Mistral
- If you run the code by itself, the ui.py file should execute it properly and run it locally.
- Because I don't want to push a massive dataset, I have included a small webscraper that will scrape data from webpages based on the search provided.
- Fill up the data folder with relevent data and it will essentially alloq you to specialize the AI in anything, I just happened to use it for music based functions.
- I'm going to add a little bit more functionality as time goes on, but for now this is base version.
- Make sure to have access to the GPU from the container.
    - The LLM leverages a lot of GPU power to work, so in order for it to actually compute tasks, it needs access to the GPU.
- The Dockerfile will install Ollama into the image and then pull the Mistral model to allow everything to work properly.
    - As such, the image will be fairly large, but that is to be expected with LLM models running locally.