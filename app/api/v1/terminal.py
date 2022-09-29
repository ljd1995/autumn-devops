from app.services.terminal import TerminalService
from core.security import check_token_from_query
from fastapi import APIRouter, WebSocket, Depends
from starlette.websockets import WebSocketDisconnect

router = APIRouter(tags=["web终端"])


@router.websocket("/ws")
async def handle_web_terminal(
    websocket: WebSocket, host_id: int, username: str = Depends(check_token_from_query)
) -> None:
    """
    web terminal connect
    :param username: 当前请求的用户名
    :param host_id: 需要连接的主机ID
    :param websocket: websocket对象
    :return:
    """
    manager = TerminalService(websocket, username)
    try:
        await manager.connect(host_id)
        while True:
            message = await websocket.receive()
            websocket._raise_on_disconnect(message)
            await manager.receive(message.get("text", ""), message.get("bytes", b""))
    except WebSocketDisconnect:
        print(f"websocket disconnect-{host_id}")
        await manager.disconnect()
    except Exception as e:
        print(e)
