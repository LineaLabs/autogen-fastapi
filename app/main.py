from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from starlette.responses import RedirectResponse

from autogen_server import serve_autogen
from data_model import Input, ModelInformation
from autogen_agents import models

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

@app.get(path=base, include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url=docs_url)


@app.get(prefix + "/models")
async def get_models():
    return {
        "object": "list",
        "data": [model.dict(exclude={"agent_configs"}) for model in models.values()]
    }


@app.post(prefix + "/chat/completions")
async def route_query(model_input: Input):
    # model_services = {
    #     model_info.name: serve_autogen,
    # }

    # service = model_services.get(model_input.model)
    service = models.get(model_input.model)
    if not service:
        raise HTTPException(status_code=404, detail="Model not found")
    return serve_autogen(model_input)
