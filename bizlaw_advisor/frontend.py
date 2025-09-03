"""
Enhanced Streamlit frontend for BizLaw Advisor
"""
import streamlit as st
from typing import Dict, List
import time
import json
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .config import AppConfig
from .models import BusinessContext, LegalResponse
from .search_service import SearchService
from .llm_service import LLMService

class StreamlitApp:
    """Enhanced Streamlit frontend for BizLaw Advisor"""
    
    def __init__(self):
        self.config = AppConfig()
        self.search_service = None
        self.llm_service = LLMService()
        self.sources_path = Path(__file__).parent / 'sources'
        self.sources_path.mkdir(exist_ok=True)
        self.applicable_laws_path = Path(__file__).parent / 'applicable_laws'
        self.applicable_laws_path.mkdir(exist_ok=True)
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'business_context' not in st.session_state:
            st.session_state.business_context = None
            
    async def initialize_services(self):
        """Initialize async services"""
        if self.search_service is None:
            self.search_service = SearchService()
    
    def run(self):
        """Run the Streamlit application"""
        st.title("BizLaw Advisor")
        
        # Apply custom styling
        st.markdown("""
        <style>
        .law-card {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .federal {
            border-left: 5px solid #2196F3;
        }
        .state {
            border-left: 5px solid #4CAF50;
        }
        .local {
            border-left: 5px solid #FFC107;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Sidebar inputs
        self._render_sidebar()
        
        # Main chat interface
        self._render_chat_interface()
    
    def _render_sidebar(self):
        """Render the enhanced sidebar inputs"""
        with st.sidebar:
            st.title("Business Context")
            
            # Location inputs with validation
            city = st.text_input("Business Location (City)", 
                            placeholder="e.g., St. Louis City",
                            help="Enter the city/county where your business operates")
            
            state = st.text_input("Business Location (State)", 
                            placeholder="e.g., Missouri",
                            help="Enter the state where your business operates")
            
            # Business inputs
            business_type = st.text_input("Business Type", 
                                    placeholder="e.g., Residential property management",
                                    help="Enter your type of business (e.g., Restaurant, Retail Store)")
            
            area_of_law = st.selectbox(
                "Area of Law",
                ['Select Area of Law from dropdown'] + self.config.LAW_CATEGORIES.CATEGORIES,
                help="Select the legal area you need information about"
            )
            
            # Submit with validation
            if st.button("Submit", type="primary"):
                if not all([city, state, business_type, area_of_law]):
                    st.error("Please fill in all fields")
                else:
                    st.session_state.business_context = BusinessContext(
                        city=city,
                        state=state,
                        business_type=business_type,
                        area_of_law=area_of_law
                    )
                    # Clear chat history when context changes
                    st.session_state.chat_history = []
                    st.success("Context updated successfully!")
                    with st.spinner("Searching applicable laws..."):
                        prompt = "Provide Summary of Laws/Rules applicable to the Business"
                        response = asyncio.run(self._generate_response(prompt))
                        with open(self.applicable_laws_path / 'applicable_laws.txt', "w") as file:
                            file.write(str(response))
    
    def _render_chat_interface(self):
        """Render the enhanced chat interface"""
        if st.session_state.business_context is None:
            st.info("Please provide business context in the sidebar to start.")
            return
        
        # Display current context
        with st.expander("Current Business Context", expanded=False):
            context = st.session_state.business_context
            st.write(f"🏢 Business Type: {context.business_type}")
            st.write(f"📍 Location: {context.city}, {context.state}")
            st.write(f"⚖️ Area of Law: {context.area_of_law}")

        # Display rules applicable to the business
        with st.expander("Rules Applicable to the Business", expanded=False):
            context = st.session_state.business_context
            with open(self.applicable_laws_path / 'applicable_laws.txt', "r") as file:
                response = file.read()
                response = eval(response)
            # message_content = {
            #         "summary": response.summary,
            #         "key_points": response.key_points,
            #         "jurisdiction_analysis": response.jurisdiction_analysis,
            #         "compliance_steps": response.compliance_steps,
            #         "overlapping_regulations": response.overlapping_regulations,
            #         "sources": response.sources,
            #         "response_time": response.response_time
            #     }
            # self._display_structured_message(message_content)
            st.write(f"Summary: {response.summary}")
            for source in response.sources[:10]:
                st.write(f"• {source}")
            st.write(f"Response Time: {response.response_time}")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], dict):
                    self._display_structured_message(message["content"])
                else:
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about the business laws..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Researching applicable laws..."):
                    response = asyncio.run(self._generate_response(prompt))
                    
                message_content = {
                    "summary": response.summary,
                    "key_points": response.key_points,
                    "jurisdiction_analysis": response.jurisdiction_analysis,
                    "compliance_steps": response.compliance_steps,
                    "overlapping_regulations": response.overlapping_regulations,
                    "sources": response.sources,
                    "response_time": response.response_time
                }
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": message_content
                })
                
                self._display_structured_message(message_content)
    
    async def _generate_response(self, query: str) -> LegalResponse:
        """Generate response using parallel search"""
        await self.initialize_services()
        
        context = st.session_state.business_context
        
        try:
            # Parallel search for laws
            federal_laws, state_laws, local_laws = await asyncio.gather(
                self.search_service.get_federal_laws(query),
                self.search_service.get_state_laws(query, context.state),
                self.search_service.get_local_laws(query, context.city, context.state)
            )
            with open(self.sources_path / "identified_sources.json", "w") as file:
                json.dump({
                    "Federal Laws": federal_laws,
                    "State Laws": state_laws,
                    "Local Laws": local_laws
                }, file, indent=4)
            # Generate response using LLM
            response = self.llm_service.generate_response(
                context, federal_laws, state_laws, local_laws
            )
            
            return response
            
        finally:
            # Ensure we clean up the session
            if self.search_service:
                await self.search_service.close()
    
    def _display_structured_message(self, content: Dict):
        """Display a structured message with enhanced formatting"""
        # Main summary
        st.markdown("### Summary")
        st.write(content["summary"])
        
        # Key points in an expander
        with st.expander("Key Points to Remember", expanded=False):
            for point in content["key_points"]:
                st.write(f"• {point}")
        
        # Jurisdiction analysis
        st.markdown("### Analysis by Jurisdiction")
        cols = st.columns(3)
        
        if "Federal" in content["jurisdiction_analysis"]:
            with cols[0]:
                st.markdown('<div class="law-card federal">', unsafe_allow_html=True)
                st.markdown("#### 🏛️ Federal")
                st.write(content["jurisdiction_analysis"]["Federal"])
                st.markdown('</div>', unsafe_allow_html=True)
        
        if "State" in content["jurisdiction_analysis"]:
            with cols[1]:
                st.markdown('<div class="law-card state">', unsafe_allow_html=True)
                st.markdown("#### 🏪 State")
                st.write(content["jurisdiction_analysis"]["State"])
                st.markdown('</div>', unsafe_allow_html=True)
        
        if "Local" in content["jurisdiction_analysis"]:
            with cols[2]:
                st.markdown('<div class="law-card local">', unsafe_allow_html=True)
                st.markdown("#### 🏠 Local")
                st.write(content["jurisdiction_analysis"]["Local"])
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Compliance steps
        with st.expander("Compliance Steps", expanded=False):
            for i, step in enumerate(content["compliance_steps"], 1):
                st.write(f"{i}. {step}")
        
        # Overlapping regulations
        if content["overlapping_regulations"]:
            with st.expander("Overlapping Regulations", expanded=False):
                for reg in content["overlapping_regulations"]:
                    st.write(f"• {reg}")
        
        # Sources with copy button
        with st.expander("Sources", expanded=False):
            for source in content["sources"][:10]:
                st.write(f"• {source}")
        
        # Response time
        st.caption(f"⚡ Response generated in {content['response_time']:.2f} seconds")
