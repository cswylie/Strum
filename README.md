## README/Ableton AI Assistant

- You can install the dependencies by using the command:
```python
pip install -r requirements.txt
```
## Docker Run Instructions:
- Build the image:
```bash
docker build -t ableton-ai-assistant
```
- Run the container:
```bash
docker run -p 7860:7860 ableton-ai-assistant
```
## Running Mistral
- If you run the code by itself, the ui.py file should execute it properly and run it locally.
- Because I don't want to push a massive dataset, I have included a small webscraper that will scrape data from webpages based on the search provided.
- Fill up the data folder with relevent data and it will essentially alloq you to specialize the AI in anything, I just happened to use it for music based functions.
- I'm going to add a little bit more functionality as time goes on, but for now this is base version.
- I also have a Docker file, but I'm currently running into some bugs with it, so I'll push it soon.