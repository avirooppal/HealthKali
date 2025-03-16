"""
Setup script for Cancer Digital Twin Platform
This script creates necessary directories and files for the application
"""

import os
import shutil
import sys

# Define project structure
PROJECT_STRUCTURE = {
    "frontend": [
        "dashboard.html",
        "dashboard-styles.css",
        "patient-database.js",
        "enhanced-results.js",
        "simple-body-model.js",
        "dashboard.js"
    ],
    "backend": {
        "core": {
            "digital_twin": ["__init__.py", "digital_twin.py"],
            "simulation": ["__init__.py", "simulation_models.py"]
        },
        "api": ["__init__.py", "routes.py"]
    },
    "data": [],
    "validation": ["run_validation.py"]
}

def create_directory_structure(base_path="."):
    """Create the directory structure for the project"""
    print(f"Creating project structure in {os.path.abspath(base_path)}...")
    
    for directory, contents in PROJECT_STRUCTURE.items():
        if isinstance(contents, list):
            # Create directory
            dir_path = os.path.join(base_path, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
            
            # Create placeholder files
            for filename in contents:
                file_path = os.path.join(dir_path, filename)
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        f.write(f"# Placeholder for {filename}\n")
                    print(f"Created placeholder: {file_path}")
        elif isinstance(contents, dict):
            # Create nested directories
            parent_dir = os.path.join(base_path, directory)
            os.makedirs(parent_dir, exist_ok=True)
            print(f"Created directory: {parent_dir}")
            
            # Create nested structure
            for subdir, subcontents in contents.items():
                subdir_path = os.path.join(parent_dir, subdir)
                os.makedirs(subdir_path, exist_ok=True)
                print(f"Created directory: {subdir_path}")
                
                # Create files in subdirectory
                for filename in subcontents:
                    file_path = os.path.join(subdir_path, filename)
                    if not os.path.exists(file_path):
                        with open(file_path, 'w') as f:
                            f.write(f"# Placeholder for {filename}\n")
                        print(f"Created placeholder: {file_path}")

def create_main_file(base_path="."):
    """Create the main.py file"""
    main_path = os.path.join(base_path, "main.py")
    if not os.path.exists(main_path):
        with open(main_path, 'w') as f:
            f.write('"""Main application file for Cancer Digital Twin Platform"""\n\n')
            f.write('# Import necessary modules and run the server\n')
            f.write('from fastapi import FastAPI\n\n')
            f.write('# Initialize the app\n')
            f.write('app = FastAPI(title="Cancer Digital Twin Platform")\n\n')
            f.write('# Define routes\n\n')
            f.write('if __name__ == "__main__":\n')
            f.write('    import uvicorn\n')
            f.write('    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)\n')
        print(f"Created main file: {main_path}")

def create_readme(base_path="."):
    """Create README.md file"""
    readme_path = os.path.join(base_path, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write('# Cancer Digital Twin Platform\n\n')
            f.write('An interactive platform for cancer digital twins, prediction, and simulation.\n\n')
            f.write('## Features\n\n')
            f.write('- Patient digital twin creation and management\n')
            f.write('- Risk assessment and prediction\n')
            f.write('- Treatment scenario simulation\n')
            f.write('- 3D visualization of tumor location and growth\n\n')
            f.write('## Getting Started\n\n')
            f.write('1. Install dependencies: `pip install -r requirements.txt`\n')
            f.write('2. Run the application: `python main.py`\n')
            f.write('3. Open in browser: http://localhost:8000\n\n')
            f.write('## Documentation\n\n')
            f.write('See the `docs` directory for detailed documentation.\n')
        print(f"Created README: {readme_path}")

def create_requirements(base_path="."):
    """Create requirements.txt file"""
    req_path = os.path.join(base_path, "requirements.txt")
    if not os.path.exists(req_path):
        with open(req_path, 'w') as f:
            f.write('fastapi>=0.68.0\n')
            f.write('uvicorn>=0.15.0\n')
            f.write('pydantic>=1.8.2\n')
            f.write('python-multipart>=0.0.5\n')
            f.write('jinja2>=3.0.1\n')
            f.write('numpy>=1.21.0\n')
            f.write('pandas>=1.3.0\n')
            f.write('scikit-learn>=0.24.2\n')
        print(f"Created requirements: {req_path}")

def main():
    """Main setup function"""
    base_path = "."
    
    # Create structure
    create_directory_structure(base_path)
    create_main_file(base_path)
    create_readme(base_path)
    create_requirements(base_path)
    
    print("\nSetup completed! You can now run the application with:")
    print("1. pip install -r requirements.txt")
    print("2. python main.py")
    print("3. Open http://localhost:8000 in your browser")

if __name__ == "__main__":
    main() 