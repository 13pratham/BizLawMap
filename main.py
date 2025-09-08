from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import uvicorn

from bizlaw_advisor.models import BusinessContext, LegalResponse
from bizlaw_advisor.search_service import SearchService
from bizlaw_advisor.llm_service import LLMService

app = FastAPI(title="BizLaw Advisor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
search_service = None
llm_service = LLMService()

class QueryRequest(BaseModel):
    query: str
    context: BusinessContext

class QueryResponse(BaseModel):
    summary: str
    key_points: List[str]
    jurisdiction_analysis: Dict
    compliance_steps: List[str]
    overlapping_regulations: List[str]
    sources: List[str]
    response_time: float

@app.on_event("startup")
async def startup_event():
    global search_service
    search_service = SearchService()

@app.on_event("shutdown")
async def shutdown_event():
    if search_service:
        await search_service.close()

@app.post("/api/query", response_model=QueryResponse)
async def generate_response(request: QueryRequest):
    try:
        # Parallel search for laws
        federal_laws, state_laws, local_laws = await asyncio.gather(
            search_service.get_federal_laws(
                request.query, 
                request.context.city, 
                request.context.state, 
                request.context.business_type, 
                request.context.area_of_law, 
                request.context.statute_of_law
            ),
            search_service.get_state_laws(
                request.query, 
                request.context.city, 
                request.context.state, 
                request.context.business_type, 
                request.context.area_of_law
            ),
            search_service.get_local_laws(
                request.query, 
                request.context.city, 
                request.context.state, 
                request.context.business_type, 
                request.context.area_of_law
            )
        )

        # Generate response using LLM
        response = llm_service.generate_response(
            request.context, federal_laws, state_laws, local_laws
        )

        return QueryResponse(
            summary=response.summary,
            key_points=response.key_points,
            jurisdiction_analysis=response.jurisdiction_analysis,
            compliance_steps=response.compliance_steps,
            overlapping_regulations=response.overlapping_regulations,
            sources=response.sources,
            response_time=response.response_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)