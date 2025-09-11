"""
Helper utilities for the Multi-Agent Market Research System
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup logging configuration for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save dictionary data to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save the file
        
    Returns:
        Success status
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {filepath}: {str(e)}")
        return False

def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load dictionary data from JSON file
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Loaded dictionary or None if failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {filepath}: {str(e)}")
        return None

def create_timestamped_filename(prefix: str, extension: str = "json") -> str:
    """
    Create a timestamped filename
    
    Args:
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        Timestamped filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    # Simple keyword extraction (could be enhanced with NLP libraries)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must'
    }
    
    words = text.lower().split()
    keywords = [word.strip('.,!?;:"()[]{}') for word in words 
                if len(word) > 3 and word.lower() not in stop_words]
    
    # Count frequency and return top keywords
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_keywords[:max_keywords]]

def calculate_relevance_score(resource: Dict[str, Any], search_terms: List[str]) -> float:
    """
    Calculate relevance score for a resource based on search terms
    
    Args:
        resource: Resource dictionary
        search_terms: List of search terms
        
    Returns:
        Relevance score (0.0 to 1.0)
    """
    score = 0.0
    text_fields = ['title', 'description', 'content']
    
    resource_text = ""
    for field in text_fields:
        if field in resource:
            resource_text += f" {resource[field]}"
    
    resource_text = resource_text.lower()
    
    for term in search_terms:
        if term.lower() in resource_text:
            score += 1.0
    
    # Normalize by number of search terms
    return min(score / len(search_terms), 1.0) if search_terms else 0.0

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage value
    
    Args:
        value: Percentage value (0.0 to 1.0)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"

def create_progress_tracker():
    """
    Create a simple progress tracker
    
    Returns:
        Progress tracker function
    """
    progress = {"current": 0, "total": 0}
    
    def update_progress(current: int, total: int = None, message: str = ""):
        progress["current"] = current
        if total is not None:
            progress["total"] = total
        
        if progress["total"] > 0:
            percentage = (progress["current"] / progress["total"]) * 100
            print(f"Progress: {percentage:.1f}% - {message}")
    
    return update_progress

def validate_api_keys(required_keys: List[str]) -> Dict[str, bool]:
    """
    Validate that required API keys are available
    
    Args:
        required_keys: List of required environment variable names
        
    Returns:
        Dictionary with validation results
    """
    results = {}
    for key in required_keys:
        value = os.getenv(key)
        results[key] = bool(value and len(value.strip()) > 0)
    
    return results

def estimate_analysis_time(company_name: str) -> Dict[str, int]:
    """
    Estimate analysis time based on company complexity
    
    Args:
        company_name: Name of the company
        
    Returns:
        Dictionary with time estimates in minutes
    """
    # Simple estimation logic (could be enhanced)
    base_time = 3  # minutes
    
    # Larger companies might take longer
    if len(company_name.split()) > 2:
        base_time += 1
    
    return {
        "research_agent": base_time,
        "usecase_agent": base_time + 1,
        "resource_agent": base_time - 1,
        "total_estimated": (base_time * 3) + 1
    }

def create_summary_statistics(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create summary statistics from analysis results
    
    Args:
        results: Complete analysis results
        
    Returns:
        Summary statistics dictionary
    """
    stats = {
        "total_analysis_time": 0,
        "agents_completed": 0,
        "total_use_cases": 0,
        "total_resources": 0,
        "success_rate": 0.0
    }
    
    try:
        # Count completed agents
        agent_results = results.get("agent_results", {})
        stats["agents_completed"] = len(agent_results)
        
        # Count use cases
        use_cases = agent_results.get("use_cases", {}).get("generated_use_cases", {})
        if isinstance(use_cases, dict):
            stats["total_use_cases"] = sum(len(v) if isinstance(v, list) else 1 
                                         for v in use_cases.values())
        
        # Count resources
        resources = agent_results.get("resources", {})
        for platform in ["kaggle", "huggingface", "github"]:
            if platform in resources:
                stats["total_resources"] += resources[platform].get("count", 0)
        
        # Calculate success rate
        if results.get("workflow_status") == "completed":
            stats["success_rate"] = 1.0
        
    except Exception as e:
        logger.warning(f"Error creating summary statistics: {str(e)}")
    
    return stats

def export_to_excel(data: Dict[str, Any], filename: str) -> bool:
    """
    Export analysis results to Excel format
    
    Args:
        data: Analysis results
        filename: Output filename
        
    Returns:
        Success status
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Company overview
            if "final_proposal" in data:
                proposal = data["final_proposal"]
                
                # Executive summary
                if "executive_summary" in proposal:
                    exec_df = pd.DataFrame([proposal["executive_summary"]])
                    exec_df.to_excel(writer, sheet_name="Executive Summary", index=False)
                
                # Use cases (if available)
                if "top_recommendations" in proposal:
                    recs = proposal["top_recommendations"]
                    if isinstance(recs, dict):
                        recs_df = pd.DataFrame([recs])
                        recs_df.to_excel(writer, sheet_name="Recommendations", index=False)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to export to Excel: {str(e)}")
        return False

def generate_unique_id() -> str:
    """
    Generate a unique ID for tracking
    
    Returns:
        Unique identifier string
    """
    import uuid
    return str(uuid.uuid4())[:8]

class PerformanceMonitor:
    """
    Simple performance monitoring utility
    """
    
    def __init__(self):
        self.start_time = None
        self.checkpoints = {}
    
    def start(self):
        """Start monitoring"""
        self.start_time = datetime.now()
        self.checkpoints = {}
    
    def checkpoint(self, name: str):
        """Add a checkpoint"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.checkpoints[name] = elapsed
    
    def get_summary(self) -> Dict[str, float]:
        """Get performance summary"""
        if not self.start_time:
            return {}
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        return {
            "total_time": total_time,
            "checkpoints": self.checkpoints.copy()
        }
