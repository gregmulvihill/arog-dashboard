"""
Arog Dashboard - System monitoring and container management
FastAPI backend with htmx frontend
"""
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from app.docker_manager import DockerManager
from app.system_monitor import SystemMonitor
from app.python_agent import PythonAgent

# Global managers
docker_manager = None
system_monitor = None
python_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global docker_manager, system_monitor, python_agent

    # Initialize managers
    docker_manager = DockerManager()
    system_monitor = SystemMonitor()
    python_agent = PythonAgent()

    yield

    # Cleanup
    await python_agent.cleanup()


app = FastAPI(
    title="Arog Dashboard",
    description="System monitoring, container management, and Python agent",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard"""
    containers = await docker_manager.get_containers()
    system_stats = await system_monitor.get_stats()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "containers": containers,
            "system_stats": system_stats,
            "hostname": os.getenv("HOSTNAME", "arog"),
            "now": datetime.now()
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/containers")
async def get_containers():
    """Get Docker containers list"""
    return await docker_manager.get_containers()


@app.get("/api/system")
async def get_system_stats():
    """Get system statistics"""
    return await system_monitor.get_stats()


@app.get("/api/system/stream")
async def stream_system_stats():
    """Server-Sent Events stream for system stats"""
    async def event_generator():
        while True:
            stats = await system_monitor.get_stats()
            yield f"data: {stats.model_dump_json()}\n\n"
            await asyncio.sleep(2)  # Update every 2 seconds

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/agent/execute")
async def execute_python_code(request: Request):
    """Execute Python code in agent"""
    data = await request.json()
    code = data.get("code", "")

    result = await python_agent.execute(code)
    return result


@app.get("/api/agent/history")
async def get_agent_history():
    """Get execution history"""
    return await python_agent.get_history()


@app.delete("/api/agent/history")
async def clear_agent_history():
    """Clear execution history"""
    await python_agent.clear_history()
    return {"status": "cleared"}


@app.post("/api/containers/{container_id}/restart")
async def restart_container(container_id: str):
    """Restart a container"""
    return await docker_manager.restart_container(container_id)


@app.post("/api/containers/{container_id}/stop")
async def stop_container(container_id: str):
    """Stop a container"""
    return await docker_manager.stop_container(container_id)


@app.post("/api/containers/{container_id}/start")
async def start_container(container_id: str):
    """Start a container"""
    return await docker_manager.start_container(container_id)
