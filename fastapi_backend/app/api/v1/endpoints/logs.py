from fastapi import APIRouter
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/logs", tags=["Logs"])
logger = logging.getLogger("frontend_logger")

class LogMessage(BaseModel):
    level: str
    message: str
    timestamp: str
    source: str

@router.post("/", status_code=201)
async def receive_log(log_msg: LogMessage):
    formatted_msg = f"[FRONTEND - {log_msg.source}] {log_msg.timestamp} | {log_msg.message}"
    if log_msg.level.lower() == "error":
        logger.error(formatted_msg)
    elif log_msg.level.lower() == "warn":
        logger.warning(formatted_msg)
    elif log_msg.level.lower() == "debug":
        logger.debug(formatted_msg)
    else:
        logger.info(formatted_msg)
    
    return {"status": "success"}
