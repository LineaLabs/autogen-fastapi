# Streaming Autogen with FastAPI 
This is an example FastAPI server that streams messages from the Autogen framework

## Installation
```sh
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

