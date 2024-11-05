from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from starlette.responses import RedirectResponse

from autogen_server import serve_autogen
from data_model import Input, ModelInformation
from autogen_agents import models

load_dotenv()

# 读取环境变量中的keys
AUTH_KEYS = os.getenv("AUTH_KEYS").split(",")

# 验证请求头中是否有正确的api_key
def authorization(req: Request):
    if(not req.headers.get("Authorization")):
        raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
    token = req.headers["Authorization"].replace("Bearer ", "")
    if token not in AUTH_KEYS:
        raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
    return True

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
async def route_query(model_input: Input, authorized: bool = Depends(authorization)):
    # model_services = {
    #     model_info.name: serve_autogen,
    # }

    # service = model_services.get(model_input.model)
    service = models.get(model_input.model)
    if not service:
        raise HTTPException(status_code=404, detail="Model not found")
    return serve_autogen(model_input)
