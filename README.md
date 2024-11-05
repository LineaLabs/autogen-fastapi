# Streaming Autogen with FastAPI 
This is an example FastAPI server that streams messages from the Autogen framework

## Installation & Running
Clone the repo and build the docker image, set your LLM model and API key in the docker-compose.yml file.
```sh
git clone https://github.com/0000sir/autogen-fastapi.git
cd autogen-fastapi
docker compose build
docker compose up
```

## Documentation
Navigate to http://localhost:8000/autogen to see the docs. 

## Call different agent groups with different model definitions
We can define different agent groups for different purposes in a single json file (app/agent_configs.json).
After defined, we can call the agent group with the there id as model parameter.
For example we have a definition as follows:
```json
{
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
  -H 'Authorization: Bearer 976707f2ab39ebee343034b4b33db6f9' \
  -d '{
  "model": "article_writer",
  "messages": [
    {
      "role": "user",
      "content": "写一篇向小学生介绍明朝历史的文章，涵盖明朝的建立、兴盛、衰落的过程，大约3000字。"
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