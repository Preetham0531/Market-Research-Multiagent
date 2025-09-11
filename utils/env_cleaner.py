"""
Environment file cleaner utility
Automatically cleans .env files to prevent whitespace issues
"""

import os
import re
from typing import Dict, Any

def clean_env_file(env_path: str = ".env") -> bool:
    """
    Clean the .env file by removing extra whitespace and fixing formatting
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        True if file was cleaned successfully
    """
    try:
        if not os.path.exists(env_path):
            print(f"❌ .env file not found at {env_path}")
            return False
        
        # Read the current file
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Clean each line
        cleaned_lines = []
        for line in lines:
            # Skip empty lines and comments
            if line.strip() == "" or line.strip().startswith("#"):
                cleaned_lines.append(line)
                continue
            
            # Check if it's a key-value pair
            if "=" in line:
                key, value = line.split("=", 1)
                # Clean the key and value
                clean_key = key.strip()
                clean_value = value.strip()
                
                # Only add if both key and value exist
                if clean_key and clean_value:
                    cleaned_lines.append(f"{clean_key}={clean_value}\n")
            else:
                # Keep the line as is if it doesn't contain =
                cleaned_lines.append(line)
        
        # Write back the cleaned file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"✅ .env file cleaned successfully: {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning .env file: {str(e)}")
        return False

def validate_env_file(env_path: str = ".env") -> Dict[str, Any]:
    """
    Validate the .env file and return status
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "keys_found": []
    }
    
    try:
        if not os.path.exists(env_path):
            result["valid"] = False
            result["errors"].append(f".env file not found at {env_path}")
            return result
        
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                result["keys_found"].append(key)
                
                # Check for common issues
                if not value:
                    result["warnings"].append(f"Line {line_num}: {key} has empty value")
                elif value != value.strip():
                    result["warnings"].append(f"Line {line_num}: {key} has trailing whitespace")
                elif " " in value and not value.startswith('"') and not value.startswith("'"):
                    result["warnings"].append(f"Line {line_num}: {key} value contains spaces (consider quoting)")
        
        # Check for required keys
        required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
        for key in required_keys:
            if key not in result["keys_found"]:
                result["valid"] = False
                result["errors"].append(f"Missing required key: {key}")
        
        return result
        
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error reading .env file: {str(e)}")
        return result

def auto_fix_env_file(env_path: str = ".env") -> bool:
    """
    Automatically fix common .env file issues
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        True if file was fixed successfully
    """
    try:
        # First, clean the file
        if not clean_env_file(env_path):
            return False
        
        # Then validate
        validation = validate_env_file(env_path)
        
        if validation["valid"]:
            print("✅ .env file is valid and clean")
            return True
        else:
            print("❌ .env file has issues:")
            for error in validation["errors"]:
                print(f"  - {error}")
            for warning in validation["warnings"]:
                print(f"  - {warning}")
            return False
            
    except Exception as e:
        print(f"❌ Error auto-fixing .env file: {str(e)}")
        return False

if __name__ == "__main__":
    # Auto-fix the .env file when run directly
    auto_fix_env_file()
