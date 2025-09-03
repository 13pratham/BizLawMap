"""
Enhanced LLM Service using Langchain and Gemini
"""
from typing import List, Dict
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json
import re
from .config import AppConfig
from .models import BusinessContext, LegalResponse, LegalSource

class LegalAnalysisOutput(BaseModel):
    """Structure for LLM output"""
    summary: str = Field(description="A comprehensive summary of the applicable laws")
    key_points: List[str] = Field(description="Key points to remember about the laws")
    jurisdiction_analysis: Dict[str, str] = Field(description="Analysis by jurisdiction level")
    compliance_steps: List[str] = Field(description="Steps for compliance")
    overlapping_regulations: List[str] = Field(description="Identified overlapping regulations")

class LLMService:
    """Enhanced service for generating responses using Langchain and Gemini"""
    
    def __init__(self):
        self.config = AppConfig()
        self.llm = ChatGoogleGenerativeAI(
            model=self.config.MODEL_NAME,
            google_api_key=self.config.GEMINI_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.output_parser = PydanticOutputParser(pydantic_object=LegalAnalysisOutput)
    
    def generate_response(
        self,
        context: BusinessContext,
        federal_laws: List[Dict],
        state_laws: List[Dict],
        local_laws: List[Dict]
    ) -> LegalResponse:
        """Generate a comprehensive legal analysis"""
        start_time = time.time()
        
        # Create the prompt template
        template = """
        You are a legal advisor helping businesses understand applicable laws and regulations.
        
        Business Context:
        - Type: {business_type}
        - Location: {city}, {state}
        - Area of Law: {area_of_law}
        
        Available Legal Information:
        
        Federal Laws:
        {federal_laws}
        
        State Laws:
        {state_laws}
        
        Local Laws:
        {local_laws}
        
        Based on the provided information, analyze the legal requirements and provide:
        1. A comprehensive summary
        2. Key points to remember
        3. Analysis for each jurisdiction level
        4. Specific steps for compliance
        5. Identification of any overlapping regulations
        
        Provide response in json format without any additional text: {format_instructions}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Format the laws for the prompt
        federal_text = self._format_sources(federal_laws)
        state_text = self._format_sources(state_laws)
        local_text = self._format_sources(local_laws)
        
        # Create and run the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        format_instructions = {
            "summary": "A comprehensive summary of the applicable laws",
            "key_points": "List of Key points to remember about the laws",
            "jurisdiction_analysis": "Dictionary of Analysis by jurisdiction level: Federal, State, Local",
            "compliance_steps": "List of Steps for compliance",
            "overlapping_regulations": "List of Identified overlapping regulations"
        }
        # Generate response
        result = chain.run(
            business_type=context.business_type,
            city=context.city,
            state=context.state,
            area_of_law=context.area_of_law,
            federal_laws=federal_text,
            state_laws=state_text,
            local_laws=local_text,
            format_instructions=format_instructions
        )
        
        # Parse the output
        print("Result:", result)  # Debugging line to inspect the raw result
        # parsed_output = self.output_parser.parse(result)
        cleaned_result = re.sub(r"```json(.*?)```", r"\1", result, flags=re.DOTALL).strip()
        print("Cleaned Result:", cleaned_result)  # Debugging line to inspect the cleaned result
        parsed_output = json.loads(cleaned_result)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Collect all sources
        sources = [
            source['url'] for source in 
            federal_laws + state_laws + local_laws
        ]
        
        return LegalResponse(
            federal_laws=federal_laws,
            state_laws=state_laws,
            local_laws=local_laws,
            summary=parsed_output['summary'],
            key_points=parsed_output['key_points'],
            jurisdiction_analysis=parsed_output['jurisdiction_analysis'],
            compliance_steps=parsed_output['compliance_steps'],
            overlapping_regulations=parsed_output['overlapping_regulations'],
            sources=sources,
            response_time=response_time
        )
    
    def _format_sources(self, sources: List[Dict]) -> str:
        """Format sources for the prompt"""
        formatted_text = ""
        for source in sources:
            formatted_text += f"\nSource: {source['url']}\n"
            formatted_text += f"Title: {source['title']}\n"
            formatted_text += f"Content Summary: {source['content']}\n"  # Truncate long content
        return formatted_text
