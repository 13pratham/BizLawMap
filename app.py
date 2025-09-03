"""
Demo script to run the BizLaw Advisor application
"""
import os
import asyncio
import warnings
from dotenv import load_dotenv
import streamlit as st
import nest_asyncio
from bizlaw_advisor.frontend import StreamlitApp
warnings.filterwarnings(action="ignore")

# Apply nest_asyncio to allow asyncio in Streamlit
nest_asyncio.apply()

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        st.error("""
        Please set your Gemini API key in the .env file:
        GEMINI_API_KEY=your_api_key_here
        """)
        return
    
    # Run the application
    app = StreamlitApp()
    
    # Create event loop if it doesn't exist
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    app.run()

if __name__ == "__main__":
    main()
