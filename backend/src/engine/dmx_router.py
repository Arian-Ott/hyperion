
from pydantic import BaseModel
from typing import Type, Any
import inspect
import re
from fastapi import WebSocket
from ..core.security.access import ACL_VIEWER

VALID_COMMAND = re.compile(r"^[a-z]+(\.[a-z]+)*$")


class DMXRouter:
    """DMXRouter receives incoming websocket traffic and calls predefined instructions accordingly.
    
    The websocket traffic comes from the authenticated user on the website and adheres to following pattern
    
    ```
    {
        "cmd": "foo.bar",
        "data": {
            
        }
    }
    ```
    
    `cmd` serves as the command a user wants to call through the UI.
    `data` is the actual payload needed to perform the command.
    
    The frontend just needs to send a JSON containing both the right command and data.


    """
    def __init__(self):
        self.commands = {}

    def command(self, name: str, acl = ACL_VIEWER, model: Any | None = None):
        if not VALID_COMMAND.match(name):
            raise ValueError(
                f"Function name violates policy: {VALID_COMMAND.pattern}")

        if name in self.commands:
            raise ValueError(f"Command '{name}' already exists")

        def decorator(func):
            self.commands[name] = (func, acl, model)
            return func
        return decorator

    async def dispatch(self, ws: WebSocket, payload: Any, user, redis, db):
        print(self.commands)
        cmd_name = payload.get("cmd")
        print(payload)
        if cmd_name not in self.commands.keys():
            await ws.send_json({"error": "Unknown command", "cmd": cmd_name})
            return

        func, acl, model = self.commands[cmd_name]

        if user.role.name not in acl:
            await ws.send_json({"error": "Forbidden"})
            return

        validated_data = None
        if model:
            try:
                data_to_validate = payload
                validated_data = model.model_validate(data_to_validate)
            except Exception as e:
                print(payload)
                await ws.send_json({"error": "Validation failed", "details": str(e)})
                return

        available_deps = {
            "ws": ws,
            "user": user,
            "redis": redis,
            "db": db,
            "data": validated_data,  
            "payload": payload       
        }

        sig = inspect.signature(func)
        kwargs = {k: v for k, v in available_deps.items()
                  if k in sig.parameters}

        try:
            if inspect.iscoroutinefunction(func):
                await func(**kwargs)
            else:
                func(**kwargs)
        except Exception as e:
            
            await ws.send_json({"error": "Internal Server Error"})

router = DMXRouter()