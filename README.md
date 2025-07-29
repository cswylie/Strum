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
- You must start ollama with ```ollama serve```
- Then press Ctrl-C to stop it. 