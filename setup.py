"""
Setup script for BizLaw Advisor
"""
import subprocess
import sys
import os
from typing import List

def setup_environment():
    """Setup the Python environment"""
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Activate virtual environment and install requirements
    if os.name == "nt":  # Windows
        pip = os.path.join("venv", "Scripts", "pip")
    else:  # Unix/MacOS
        pip = os.path.join("venv", "bin", "pip")
    
    subprocess.run([pip, "install", "-r", "requirements.txt"], check=True)

def setup_browser():
    """Setup Playwright browser"""
    subprocess.run(["playwright", "install", "chromium"], check=True)

def main():
    """Main setup function"""
    print("Setting up BizLaw Advisor...")
    
    try:
        # Setup Python environment
        print("\nSetting up Python environment...")
        setup_environment()
        print("✓ Python environment setup complete")
        
        # Setup browser
        print("\nSetting up browser for web scraping...")
        setup_browser()
        print("✓ Browser setup complete")
        
        print("\n✓ Setup complete! You can now run the application with:")
        print("streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
