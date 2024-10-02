# Streaming Autogen with FastAPI 
This is an example FastAPI server that streams messages from the Autogen framework

## Installation
```sh
git clone https://github.com/LineaLabs/autogen-fastapi.git
cd autogen-fastapi
conda create -n autogen python=3.10
conda activate autogen
pip install -r requirements.txt
```

## Running the server
Make sure to set `OPENAI_API_KEY` in your environment variables or in `.env` file. You can get an API key from https://platform.openai.com/account/api-keys
```sh
./run.sh
```


## Querying the server

You can query the autogen agents using the following command: 
```sh
curl -X 'POST' \
  'http://localhost:8000/autogen/api/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "model_name_v0.1",
  "messages": [
    {
      "role": "user",
      "content": "Hey Mitch, can you start us off with a joke?"
    }
  ],
  "temperature": 1,
  "top_p": 1,
  "presence_penalty": 0,
  "frequency_penalty": 0,
  "stream": true
}'
```
Note that you must provide the entire conversation history to the backend, as the server expects input in OpenAI format. 

## Documentation
Navigate to http://localhost:8000/autogen to see the docs. 

## Call different agent groups with different model definitions
We can define different agent groups for different purposes.
After defined, we can call the agent group with the there id as model parameter.
For example we have a definition as follows:
```python
agent_configs = {
  "article_writer": {
    "name": "ArticleWriter",
    # other parameters ...
  }
}
```
We can call the agent group with the following command, notice the `model` parameter:
```bash
curl -X 'POST' \
  'http://localhost:8000/autogen/api/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "article_writer",
  "messages": [
    {
      "role": "user",
      "content": "写一篇向小学生介绍宋朝历史的文章，涵盖宋朝的建立、兴盛、衰落的过程，大约2000字。"
    }
  ],
  "temperature": 1,
  "top_p": 1,
  "presence_penalty": 0,
  "frequency_penalty": 0,
  "stream": true
}'
```

For available models, please refer to the mode list API [http://localhost:8000/autogen/api/v1/models](http://localhost:8000/autogen/api/v1/models).