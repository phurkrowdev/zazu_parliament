"""
Zazu Parliamentary Intelligence REST API
FastAPI server for remote/web access to Zazu Parliament

Run: uvicorn api.server:app --reload
API Docs: http://localhost:8000/docs
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
from contextlib import asynccontextmanager

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chorus import Chorus

# Global chorus instance
chorus: Optional[Chorus] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage chorus lifecycle"""
    global chorus
    
    # Startup
    print("🎭 Initializing Zazu Parliament...")
    chorus = Chorus()
    await chorus.initialize()
    print("✅ Parliament ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down parliament...")
    if chorus:
        await chorus.shutdown()
    print("✅ Shutdown complete")


app = FastAPI(
    title="Zazu Parliamentary Intelligence API",
    description="REST API for constitutional multi-agent system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AskRequest(BaseModel):
    question: str = Field(..., description="Question to ask the parliament")
    mode: str = Field("auto", description="Mode: auto, inquiry, creation, or execution")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context")
    require_consensus: bool = Field(False, description="Require multi-agent consensus")


class ParliamentResponse(BaseModel):
    mode_used: str
    agents_involved: List[str]
    outputs: Dict[str, Any]
    reflection: Dict[str, Any]
    consensus: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    parliament_initialized: bool
    agents: Dict[str, bool]


class AgentOutput(BaseModel):
    agent_id: str
    output: Dict[str, Any]


# Endpoints
@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Zazu Parliamentary Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "agents": 7
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get parliament status"""
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    return {
        "parliament_initialized": chorus.initialized,
        "agents": chorus.get_agent_status()
    }


@app.post("/ask", response_model=ParliamentResponse)
async def ask_parliament(request: AskRequest):
    """
    Ask a question to the parliament.
    
    The parliament will automatically route your request to appropriate agents
    based on the mode and question content.
    """
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    try:
        result = await chorus.process_request(
            user_input=request.question,
            mode=request.mode,
            context=request.context or {},
            require_consensus=request.require_consensus
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create")
async def create_content(
    request: str,
    theme: Optional[str] = "sovereignty",
    creative_type: str = "mythos",
    require_consensus: bool = False
):
    """
    Create content (mythos, worldbuilding, aesthetics).
    
    Args:
        request: What to create
        theme: Theme (sovereignty, transformation, emergence, etc.)
        creative_type: Type (mythos, worldbuilding, aesthetic, symbolic)
        require_consensus: Whether to require multi-agent consensus
    """
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    try:
        result = await chorus.process_request(
            user_input=f"Create a {creative_type} about {theme}: {request}",
            mode="creation",
            require_consensus=require_consensus
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan")
async def create_plan(
    goal: str,
    constraints: Optional[List[str]] = None,
    time_horizon: str = "immediate"
):
    """
    Create a strategic plan.
    
    Args:
        goal: What to plan for
        constraints: Optional constraints
        time_horizon: immediate, seasonal, or epochal
    """
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    try:
        result = await chorus.process_request(
            user_input=f"Plan: {goal}",
            mode="creation",
            context={
                'constraints': constraints or [],
                'time_horizon': time_horizon
            },
            require_consensus=True
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assess-risk")
async def assess_risk(
    description: str,
    complexity: int = 5,
    uncertainty: float = 0.5,
    dependencies: Optional[List[str]] = None,
    timeline_days: int = 30
):
    """
    Assess risk for a given scenario.
    
    Args:
        description: What to assess
        complexity: Complexity score (1-10)
        uncertainty: Uncertainty level (0.0-1.0)
        dependencies: List of dependencies
        timeline_days: Timeline in days
    """
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    try:
        # Get Ledger directly
        ledger = chorus.agents.get('ledger')
        if not ledger:
            raise HTTPException(status_code=503, detail="Ledger not available")
        
        result = await ledger.process({
            'analysis_type': 'risk',
            'data': {
                'complexity': complexity,
                'uncertainty': uncertainty,
                'dependencies': dependencies or [],
                'timeline_days': timeline_days
            },
            'parameters': {}
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    """Get information about a specific agent"""
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    if agent_id not in chorus.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    agent = chorus.agents[agent_id]
    
    return {
        "agent_id": agent_id,
        "subsystem_id": str(agent.subsystem_id.value),
        "active": True,
        "authorities": agent.constitution['subsystems'].get(agent_id, {}).get('authorities', []),
        "constraints": agent.constitution['subsystems'].get(agent_id, {}).get('constraints', [])
    }


@app.get("/agents")
async def list_agents():
    """List all available agents"""
    if not chorus or not chorus.initialized:
        raise HTTPException(status_code=503, detail="Parliament not initialized")
    
    agents_info = []
    for agent_id, agent in chorus.agents.items():
        agents_info.append({
            "id": agent_id,
            "subsystem": str(agent.subsystem_id.value),
            "active": True
        })
    
    return {"agents": agents_info}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
