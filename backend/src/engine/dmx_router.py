
from pydantic import BaseModel
from typing import Type, Any
import inspect
import re
from fastapi import WebSocket
from ..core.security.access import ACL_VIEWER

VALID_COMMAND = re.compile(r"^[a-z]+(\.[a-z]+)*$")


class DMXRouter:
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
        cmd_name = payload.get("cmd")

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