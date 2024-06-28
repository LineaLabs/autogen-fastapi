from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from starlette.responses import RedirectResponse

from autogen_server import serve_autogen
from data_model import Input, ModelInformation

load_dotenv()

base = "/autogen/"
prefix = base + "api/v1"
openapi_url = prefix + "/openapi.json"
docs_url = prefix + "/docs"

app = FastAPI(
    title="Autogen FastAPI Backend",
    openapi_url=openapi_url,
    docs_url=docs_url,
    redoc_url=None,
)

model_info = ModelInformation(
    id="model_id_v0.1",
    name="model_name_v0.1",
    description="This is a state-of-the-art model.",
    pricing={
        "prompt": "0.00",
        "completion": "0.00",
        "image": "0.00",
        "request": "0.00",
    },
    context_length=1024 * 1000,
    architecture={
        "modality": "text",
        "tokenizer": "text2vec-openai",
        "instruct_type": "InstructGPT",
    },
    top_provider={"max_completion_tokens": None, "is_moderated": False},
    per_request_limits=None,
)


@app.get(path=base, include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url=docs_url)


@app.get(prefix + "/models")
async def get_models():
    return {
        "data": {"data": model_info.dict()}
    }


@app.post(prefix + "/chat/completions")
async def route_query(model_input: Input):
    model_services = {
        model_info.name: serve_autogen,
    }

    service = model_services.get(model_input.model)
    if not service:
        raise HTTPException(status_code=404, detail="Model not found")
    return service(model_input)
