from json import dumps
from typing import Any
from fastapi.responses import StreamingResponse
import httpx
from fastapi import FastAPI, Request
from starlette.background import BackgroundTask

app = FastAPI()
SSE_ADDRESS = ("sse", 8000)

class ChangingReferece[T]:
    def __init__(self, object: T):
        self._object = object
    
    @property
    def object(self) -> T:
        return self._object

    @object.setter
    def object(self, new: T):
        self._object = new
    


def gen_sse_event(**kwargs):
    return "\n".join([f'{k}: {v if not isinstance(v, dict) else dumps(v)}' for k, v in kwargs.items()])+"\n\n"


async def relay(request: Request):
    is_first_time = True
    request_content = b""
    current_conn = ChangingReferece(None)
    async for i in request.stream():
        request_content += i

    while True:

        try:
            url = httpx.URL(path=request.url.path,
                            query=request.url.query.encode("utf-8"))
            client = httpx.AsyncClient(base_url=f"http://{SSE_ADDRESS[0]}:{SSE_ADDRESS[1]}")
            rp_req = client.build_request(request.method, url,
                                    headers=request.headers.raw,
                                    content=request_content,
                                    timeout=float('inf'))

            rp_resp = await client.send(rp_req, stream=True)
        except Exception as e:
            print("Conn error", e)
            if is_first_time:
                continue
            yield gen_sse_event(id=-1, event="backend_timeout")
            continue
        

        current_conn.object = rp_resp
        if is_first_time:
            yield current_conn
            is_first_time = False
            yield gen_sse_event(id=-1, event="gateway_accepted")
            yield gen_sse_event(id=-1, event="connection_transfer_notice")
        elif rp_resp.status_code not in [200, 201, 202]:
            print(f"{rp_resp.status_code=}")
            yield gen_sse_event(id=-1, event="backend_refused", data={'code': rp_resp.status_code})
            return
        else:
            yield gen_sse_event(id=-1, event="connection_transfer_notice")
        
        try:
            async for data in rp_resp.aiter_raw():
                yield data
        except:
            print("read error")
            await current_conn.object.aclose()
            yield gen_sse_event(id=-1, event="backend_disconnected")
            continue


@app.route("/{path:path}", include_in_schema=False)
async def route(request: Request):
    relayer = relay(request)
    rp_resp = await anext(relayer)
    print(rp_resp.object)

    return StreamingResponse(
        relayer,
        status_code=rp_resp.object.status_code,
        headers={k:v for k, v in rp_resp.object.headers.items()},
        background=BackgroundTask(rp_resp.object.aclose),
    )
