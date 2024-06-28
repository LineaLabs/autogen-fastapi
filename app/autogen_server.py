import json
import traceback
import uuid
from queue import Queue
from threading import Thread

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from autogen_workflow import AutogenWorkflow
from data_model import Input, Output

empty_usage = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
}


def serve_autogen(inp: Input):
    model_dump = inp.model_dump()
    model_messages = model_dump["messages"]
    workflow = AutogenWorkflow()

    if inp.stream:
        queue = Queue()
        workflow.set_queue(queue)
        Thread(
            target=workflow.run,
            args=(
                model_messages[-1],
                inp.stream,
            ),
        ).start()
        return StreamingResponse(
            return_streaming_response(inp, queue),
            media_type="text/event-stream",
        )
    else:
        chat_results = workflow.run(
            message=model_messages[-1],
            stream=inp.stream,
        )
        return return_non_streaming_response(
            chat_results, inp.model
        )


def return_streaming_response(inp: Input, queue: Queue):
    while True:
        message = queue.get()
        if message == "[DONE]":
            yield "data: [DONE]\n\n"
            break
        chunk = Output(
            id=str(uuid.uuid4()),
            object="chat.completion.chunk",
            choices=[message],
            usage=empty_usage,
            model=inp.model,
        )
        yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        queue.task_done()


def return_non_streaming_response(chat_results, model):
    try:
        if chat_results:
            return Output(
                id=str(chat_results.chat_id),
                choices=[
                    {"index": i, "message": msg, "finish_reason": "stop"}
                    for i, msg in enumerate(chat_results.chat_history)
                ],
                usage=chat_results.cost,
                model=model,
            ).model_dump()
        else:
            return Output(
                id="None",
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Sorry, I am unable to assist with that request at this time.",
                        },
                        "finish_reason": "stop",
                        "logprobs": None,
                    }
                ],
                usage=empty_usage,
                model=model,
            ).model_dump()

    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
