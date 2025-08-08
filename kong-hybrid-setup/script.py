# Create directory structure and files for the complete Kong hybrid setup
import os

# Create the directory structure
dirs = [
    "kong-hybrid-setup",
    "kong-hybrid-setup/certificates",
    "kong-hybrid-setup/control-plane", 
    "kong-hybrid-setup/data-plane",
    "kong-hybrid-setup/custom-plugins",
    "kong-hybrid-setup/custom-plugins/api-version",
    "kong-hybrid-setup/custom-plugins/api-version/kong/plugins/api-version",
    "kong-hybrid-setup/database",
    "kong-hybrid-setup/scripts",
    "kong-hybrid-setup/monitoring",
    "kong-hybrid-setup/examples"
]

for dir_path in dirs:
    os.makedirs(dir_path, exist_ok=True)
    
print("Directory structure created successfully!")
print("\nCreated directories:")
for dir_path in dirs:
    print(f"  {dir_path}")