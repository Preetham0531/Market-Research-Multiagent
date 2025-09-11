"""
Agent 3: Resource Asset Collection Agent
Collects relevant datasets and resources from Kaggle, HuggingFace, and GitHub
"""

import json
import logging
import requests
import time
import signal
from typing import Dict, List, Any
from github import Github
from huggingface_hub import HfApi
from config import Config
from tools.web_search import WebSearchTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceAgent:
    """
    Agent responsible for collecting datasets and resources for AI/ML use cases
    """
    
    def __init__(self):
        """Initialize the Resource Agent"""
        self.github = Github(Config.GITHUB_TOKEN) if Config.GITHUB_TOKEN else None
        self.hf_api = HfApi(token=Config.HUGGINGFACE_TOKEN) if Config.HUGGINGFACE_TOKEN else None
        self.web_search = WebSearchTool()
        
    def search_kaggle_datasets(self, search_terms: List[str], industry: str) -> List[Dict[str, Any]]:
        """
        Search for relevant datasets on Kaggle
        
        Args:
            search_terms: List of search terms related to use cases
            industry: Industry name for context
            
        Returns:
            List of Kaggle dataset information
        """
        datasets = []
        
        try:
            # Combine industry with search terms - REDUCED to 2 searches max
            all_search_terms = [industry] + search_terms[:1]  # Only industry + 1 term
            
            for term in all_search_terms[:2]:  # Limit to 2 searches max
                # Use Kaggle API if available, otherwise use web search
                if Config.KAGGLE_USERNAME and Config.KAGGLE_KEY:
                    try:
                        # Use Kaggle API (requires kaggle package and credentials)
                        import kaggle
                        
                        search_results = kaggle.api.dataset_list(
                            search=term,
                            max_size=1000000000,  # 1GB limit
                            min_size=1000,       # 1KB minimum
                            sort_by="votes"
                        )
                        
                        for dataset in search_results[:Config.MAX_DATASETS_PER_PLATFORM]:
                            datasets.append({
                                "title": dataset.title,
                                "url": f"https://www.kaggle.com/datasets/{dataset.ref}",
                                "description": dataset.subtitle or "",
                                "size": dataset.totalBytes,
                                "votes": dataset.voteCount,
                                "download_count": dataset.downloadCount,
                                "platform": "Kaggle",
                                "search_term": term
                            })
                            
                    except Exception as e:
                        logger.warning(f"Kaggle API error for term '{term}': {str(e)}")
                        # Fallback to manual dataset suggestions
                        datasets.extend(self._get_kaggle_fallback_datasets(term, industry))
                else:
                    # Fallback to manual dataset suggestions
                    datasets.extend(self._get_kaggle_fallback_datasets(term, industry))
                    
        except Exception as e:
            logger.error(f"Error searching Kaggle datasets: {str(e)}")
            
        return datasets
    
    def search_huggingface_datasets(self, search_terms: List[str], industry: str) -> List[Dict[str, Any]]:
        """
        Search for relevant datasets and models on HuggingFace
        
        Args:
            search_terms: List of search terms related to use cases
            industry: Industry name for context
            
        Returns:
            List of HuggingFace dataset and model information
        """
        resources = []
        
        try:
            # REDUCED to 2 searches max for speed
            all_search_terms = [industry] + search_terms[:1]  # Only industry + 1 term
            
            for term in all_search_terms[:2]:  # Limit to 2 searches max
                try:
                    if self.hf_api:
                        # Search for datasets
                        datasets = self.hf_api.list_datasets(
                            search=term,
                            limit=Config.MAX_DATASETS_PER_PLATFORM
                        )
                        
                        for dataset in datasets:
                            resources.append({
                                "title": dataset.id,
                                "url": f"https://huggingface.co/datasets/{dataset.id}",
                                "description": dataset.description or "",
                                "downloads": getattr(dataset, 'downloads', 0),
                                "likes": getattr(dataset, 'likes', 0),
                                "platform": "HuggingFace",
                                "type": "dataset",
                                "search_term": term
                            })
                        
                        # Search for models
                        models = self.hf_api.list_models(
                            search=term,
                            limit=Config.MAX_DATASETS_PER_PLATFORM
                        )
                        
                        for model in models:
                            resources.append({
                                "title": model.id,
                                "url": f"https://huggingface.co/{model.id}",
                                "description": model.description or "",
                                "downloads": getattr(model, 'downloads', 0),
                                "likes": getattr(model, 'likes', 0),
                                "platform": "HuggingFace",
                                "type": "model",
                                "search_term": term
                            })
                    else:
                        # Fallback to manual suggestions
                        resources.extend(self._get_huggingface_fallback_resources(term, industry))
                        
                except Exception as e:
                    logger.warning(f"HuggingFace API error for term '{term}': {str(e)}")
                    resources.extend(self._get_huggingface_fallback_resources(term, industry))
                    
        except Exception as e:
            logger.error(f"Error searching HuggingFace resources: {str(e)}")
            
        return resources
    
    def search_github_repositories(self, search_terms: List[str], industry: str) -> List[Dict[str, Any]]:
        """
        Search for relevant repositories on GitHub
        
        Args:
            search_terms: List of search terms related to use cases
            industry: Industry name for context
            
        Returns:
            List of GitHub repository information
        """
        repositories = []
        
        try:
            # REDUCED to 2 searches max for speed
            all_search_terms = [industry] + search_terms[:1]  # Only industry + 1 term
            
            for term in all_search_terms[:2]:  # Limit to 2 searches max
                try:
                    if self.github:
                        # Search GitHub repositories
                        search_query = f"{term} machine learning AI dataset"
                        repos = self.github.search_repositories(
                            query=search_query,
                            sort="stars",
                            order="desc"
                        )
                        
                        for repo in repos[:Config.MAX_DATASETS_PER_PLATFORM]:
                            repositories.append({
                                "title": repo.name,
                                "url": repo.html_url,
                                "description": repo.description or "",
                                "stars": repo.stargazers_count,
                                "forks": repo.forks_count,
                                "language": repo.language,
                                "updated_at": repo.updated_at.isoformat() if repo.updated_at else "",
                                "platform": "GitHub",
                                "search_term": term
                            })
                    else:
                        # Fallback to manual suggestions
                        repositories.extend(self._get_github_fallback_repos(term, industry))
                        
                except Exception as e:
                    logger.warning(f"GitHub API error for term '{term}': {str(e)}")
                    repositories.extend(self._get_github_fallback_repos(term, industry))
                    
        except Exception as e:
            logger.error(f"Error searching GitHub repositories: {str(e)}")
            
        return repositories
    
    def _safe_collect_resources(self, collection_func, platform_name: str, start_time: float, max_time: float) -> List[Dict[str, Any]]:
        """
        Safely collect resources with timeout protection
        
        Args:
            collection_func: Function to call for resource collection
            platform_name: Name of the platform for logging
            start_time: Start time of the overall collection process
            max_time: Maximum time allowed for collection
            
        Returns:
            List of collected resources or empty list if timeout/error
        """
        try:
            # Check if we're still within time limits
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_time:
                logger.warning(f"Timeout reached, skipping {platform_name} collection")
                return []
            
            # Calculate remaining time for this platform
            remaining_time = max_time - elapsed_time
            if remaining_time <= 5:  # Less than 5 seconds left
                logger.warning(f"Not enough time left for {platform_name}, skipping")
                return []
            
            logger.info(f"Collecting {platform_name} resources (max {remaining_time:.1f}s)...")
            
            # Call the collection function
            resources = collection_func()
            
            # Check if we're still within time limits after collection
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_time:
                logger.warning(f"Collection took too long, returning partial {platform_name} results")
            
            return resources if resources else []
            
        except Exception as e:
            logger.warning(f"Error collecting {platform_name} resources: {str(e)}")
            return []
    
    def collect_resources_for_use_cases(self, use_case_data: Dict) -> Dict[str, Any]:
        """
        Main method to collect resources based on generated use cases
        
        Args:
            use_case_data: Use case data from Agent 2
            
        Returns:
            Collected resources organized by platform
        """
        logger.info("Starting resource collection process...")
        
        # Extract search terms from use cases
        search_terms = self._extract_search_terms_from_use_cases(use_case_data)
        industry = use_case_data.get("industry", "")
        
        # Set a maximum time limit for resource collection (30 seconds)
        start_time = time.time()
        max_collection_time = 30  # seconds
        
        # Collect resources from all platforms with timeout protection
        kaggle_datasets = self._safe_collect_resources(
            lambda: self.search_kaggle_datasets(search_terms, industry),
            "Kaggle", start_time, max_collection_time
        )
        
        huggingface_resources = self._safe_collect_resources(
            lambda: self.search_huggingface_datasets(search_terms, industry),
            "HuggingFace", start_time, max_collection_time
        )
        
        github_repositories = self._safe_collect_resources(
            lambda: self.search_github_repositories(search_terms, industry),
            "GitHub", start_time, max_collection_time
        )
        
        # Organize and deduplicate resources
        organized_resources = {
            "kaggle": {
                "datasets": kaggle_datasets,
                "count": len(kaggle_datasets)
            },
            "huggingface": {
                "resources": huggingface_resources,
                "count": len(huggingface_resources)
            },
            "github": {
                "repositories": github_repositories,
                "count": len(github_repositories)
            },
            "search_terms_used": search_terms,
            "industry": industry,
            "agent": "ResourceAgent",
            "status": "completed"
        }
        
        # Calculate total time taken
        total_time = time.time() - start_time
        
        logger.info(f"Resource collection completed in {total_time:.1f}s. Found {len(kaggle_datasets)} Kaggle datasets, "
                   f"{len(huggingface_resources)} HuggingFace resources, "
                   f"{len(github_repositories)} GitHub repositories")
        
        return organized_resources

    # ---------- NEW: Use-case specific dataset fetching and markdown table ----------
    def fetch_datasets(self, use_case: str, description: str) -> List[Dict[str, Any]]:
        """
        Fetch top dataset/repo links for a specific use case by combining
        the use case name with key description terms and querying Kaggle,
        HuggingFace, and GitHub via the web search tool.
        
        Returns a list of dicts with keys: title, url
        """
        # Build multiple queries per platform
        base = f"{use_case} {description[:120]}"
        queries = [
            f"{base} dataset site:kaggle.com",
            f"{use_case} dataset site:kaggle.com",
            f"{base} dataset site:huggingface.co",
            f"{use_case} dataset site:huggingface.co",
            f"{base} (dataset OR api OR repository) site:github.com",
            f"{use_case} (dataset OR api OR repository) site:github.com",
        ]
        results: List[Dict[str, Any]] = []
        seen = set()
        for q in queries:
            hits = self.web_search._perform_search(q, max_results=10)
            for h in hits:
                url = h.get('url', '')
                title = h.get('title', '') or url
                if not url or url in seen:
                    continue
                # prioritize platforms by simple ordering later when trimming
                results.append({
                    'title': title,
                    'url': url
                })
                seen.add(url)
        # Prioritize Kaggle, then HuggingFace, then GitHub
        def score(u: str) -> int:
            if 'kaggle.com' in u:
                return 0
            if 'huggingface.co' in u:
                return 1
            if 'github.com' in u:
                return 2
            return 3
        results.sort(key=lambda x: score(x['url']))
        # Enforce 40% Kaggle, 30% HF, 30% GitHub, 3–6 total (best-effort)
        kaggle = [r for r in results if 'kaggle.com' in r['url']]
        hf = [r for r in results if 'huggingface.co' in r['url']]
        gh = [r for r in results if 'github.com' in r['url']]
        total_target = min(max(3, len(kaggle) + len(hf) + len(gh)), 6)
        if total_target <= 3:
            return (kaggle + hf + gh)[:total_target]
        k_quota = min(len(kaggle), max(1, int(round(total_target * 0.40))))
        hf_quota = min(len(hf), max(1, int(round(total_target * 0.30))))
        gh_quota = min(len(gh), max(1, total_target - k_quota - hf_quota))
        picked: List[Dict[str, Any]] = kaggle[:k_quota] + hf[:hf_quota] + gh[:gh_quota]
        # If short, fill from remaining pools in priority order Kaggle -> HF -> GH
        while len(picked) < total_target:
            for pool in (kaggle, hf, gh):
                for item in pool:
                    if item not in picked:
                        picked.append(item)
                        break
                if len(picked) >= total_target:
                    break
        return picked

    def _parse_use_cases_for_table(self, generated_use_cases: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse formatted_use_cases text into a structured list with
        'name' and 'description'. Keeps it lightweight here to avoid cross-module imports.
        """
        rows: List[Dict[str, str]] = []
        if not isinstance(generated_use_cases, dict):
            return rows
        text = generated_use_cases.get('formatted_use_cases', '')
        if not text:
            return rows
        parts = text.split("**Use Case")
        for part in parts[1:]:
            # Extract title
            name = part.split("**", 1)[0]
            name = name.split(":", 1)[-1].strip() if ":" in name else name.strip()
            # Extract objective/description region
            desc = ""
            if "**Objective" in part:
                after = part.split("**Objective", 1)[1]
                # up to next bold section
                for marker in ["**AI Application:", "**Cross-Functional Benefit:", "**Business Impact:", "**KPIs:", "**Effort", "**Risks"]:
                    if marker in after:
                        desc = after.split(marker, 1)[0]
                        break
                if not desc:
                    desc = after
            desc = desc.replace(":", " ").replace("**", "").strip()
            if name:
                rows.append({'name': name, 'description': desc})
        return rows

    def create_datasets_markdown(self, use_case_data: Dict[str, Any], output_path: str = "datasets.md") -> str:
        """
        Create datasets.md mapping each use case to 3–5 reference links.
        """
        # Support both generated_use_cases (formatted text) and predefined_use_cases (list of dicts)
        rows: List[Dict[str, str]] = []
        if isinstance(use_case_data.get("predefined_use_cases"), list):
            for uc in use_case_data.get("predefined_use_cases", []):
                name = (uc.get("name") or uc.get("title") or "").strip()
                desc = (uc.get("description") or uc.get("objective") or "").strip()
                if name:
                    rows.append({"name": name, "description": desc})
        else:
            generated_use_cases = use_case_data.get("generated_use_cases", {})
            rows = self._parse_use_cases_for_table(generated_use_cases)
        if not rows:
            logger.warning("No use cases found to build datasets.md")
            return ""
        # Build table header
        md = "| Use Case | Description | References |\n|---|---|---|\n"
        for row in rows:
            refs = self.fetch_datasets(row['name'], row['description'])
            ref_links = []
            for r in refs:
                url = r['url']
                title = r['title'] if len(r['title']) < 80 else r['title'][:77] + '...'
                # Show as raw HTML anchor tag with target="_blank"
                ref_links.append(f"- <a href=\"{url}\" target=\"_blank\">{title}</a>")
            if not ref_links:
                ref_cell = "No dataset found"
            else:
                ref_cell = ' <br> '.join(ref_links)
            md += f"| {row['name']} | {row['description']} | {ref_cell} |\n"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)
            logger.info(f"Datasets markdown written to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed writing datasets.md: {e}")
            return ""
    
    def save_resources_to_file(self, resources: Dict, filename: str = None) -> str:
        """
        Save collected resources to a markdown file with clickable links
        
        Args:
            resources: Collected resources data
            filename: Optional filename, auto-generated if None
            
        Returns:
            Path to the saved file
        """
        if not filename:
            industry = resources.get("industry", "unknown").replace(" ", "_").lower()
            filename = f"{Config.OUTPUT_DIR}/resources_{industry}.md"
        
        try:
            markdown_content = self._generate_markdown_content(resources)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Resources saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving resources to file: {str(e)}")
            return ""
    
    def _extract_search_terms_from_use_cases(self, use_case_data: Dict) -> List[str]:
        """
        Extract relevant search terms from use case data
        
        Args:
            use_case_data: Use case data from Agent 2
            
        Returns:
            List of search terms
        """
        search_terms = []
        
        # Default AI/ML terms
        base_terms = [
            "machine learning", "artificial intelligence", "natural language processing",
            "computer vision", "predictive analytics", "recommendation system",
            "time series forecasting", "classification", "regression", "clustering"
        ]
        
        # Extract terms from use cases
        use_cases = use_case_data.get("generated_use_cases", {})
        if isinstance(use_cases, dict):
            use_case_text = json.dumps(use_cases)
            # Simple keyword extraction (could be enhanced with NLP)
            keywords = [
                "customer", "sales", "inventory", "supply chain", "operations",
                "fraud detection", "sentiment analysis", "chatbot", "automation",
                "optimization", "forecasting", "personalization", "recommendation"
            ]
            
            for keyword in keywords:
                if keyword.lower() in use_case_text.lower():
                    search_terms.append(keyword)
        
        # Combine and deduplicate
        all_terms = list(set(base_terms + search_terms))
        return all_terms[:10]  # Limit to 10 terms
    
    def _generate_markdown_content(self, resources: Dict) -> str:
        """
        Generate markdown content for the resources file
        
        Args:
            resources: Collected resources data
            
        Returns:
            Markdown formatted string
        """
        industry = resources.get("industry", "Unknown")
        
        markdown = f"""# AI/ML Resources for {industry} Industry

This document contains curated datasets, models, and repositories relevant for AI/ML implementation in the {industry} industry.

## Search Terms Used
{', '.join(resources.get('search_terms_used', []))}

---

## Kaggle Datasets

"""
        
        # Add Kaggle datasets
        kaggle_datasets = resources.get("kaggle", {}).get("datasets", [])
        if kaggle_datasets:
            for i, dataset in enumerate(kaggle_datasets, 1):
                markdown += f"""### {i}. <a href="{dataset['url']}" target="_blank">{dataset['title']}</a>
- **Description**: {dataset.get('description', 'No description available')}
- **Platform**: {dataset.get('platform', 'Kaggle')}
- **Search Term**: {dataset.get('search_term', 'N/A')}
- **Votes**: {dataset.get('votes', 'N/A')}
- **Downloads**: {dataset.get('download_count', 'N/A')}

"""
        else:
            markdown += "No Kaggle datasets found.\n\n"
        
        # Add HuggingFace resources
        markdown += "## HuggingFace Resources\n\n"
        hf_resources = resources.get("huggingface", {}).get("resources", [])
        if hf_resources:
            for i, resource in enumerate(hf_resources, 1):
                markdown += f"""### {i}. <a href="{resource['url']}" target="_blank">{resource['title']}</a>
- **Description**: {resource.get('description', 'No description available')}
- **Type**: {resource.get('type', 'N/A')}
- **Platform**: {resource.get('platform', 'HuggingFace')}
- **Search Term**: {resource.get('search_term', 'N/A')}
- **Downloads**: {resource.get('downloads', 'N/A')}
- **Likes**: {resource.get('likes', 'N/A')}

"""
        else:
            markdown += "No HuggingFace resources found.\n\n"
        
        # Add GitHub repositories
        markdown += "## GitHub Repositories\n\n"
        github_repos = resources.get("github", {}).get("repositories", [])
        if github_repos:
            for i, repo in enumerate(github_repos, 1):
                markdown += f"""### {i}. <a href="{repo['url']}" target="_blank">{repo['title']}</a>
- **Description**: {repo.get('description', 'No description available')}
- **Language**: {repo.get('language', 'N/A')}
- **Platform**: {repo.get('platform', 'GitHub')}
- **Search Term**: {repo.get('search_term', 'N/A')}
- **Stars**: {repo.get('stars', 'N/A')}
- **Forks**: {repo.get('forks', 'N/A')}
- **Last Updated**: {repo.get('updated_at', 'N/A')}

"""
        else:
            markdown += "No GitHub repositories found.\n\n"
        
        markdown += f"""---

*Generated by Multi-Agent Market Research System*
*Industry: {industry}*
*Total Resources: {len(kaggle_datasets) + len(hf_resources) + len(github_repos)}*
"""
        
        return markdown
    
    def _get_kaggle_fallback_datasets(self, term: str, industry: str) -> List[Dict[str, Any]]:
        """Fallback Kaggle datasets when API is not available"""
        fallback_datasets = {
            "healthcare": [
                {
                    "title": "Medical Cost Personal Datasets",
                    "url": "https://www.kaggle.com/datasets/mirichoi0218/insurance",
                    "description": "Healthcare insurance cost prediction dataset",
                    "platform": "Kaggle",
                    "search_term": term
                }
            ],
            "finance": [
                {
                    "title": "Credit Card Fraud Detection",
                    "url": "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
                    "description": "Dataset for credit card fraud detection",
                    "platform": "Kaggle",
                    "search_term": term
                }
            ],
            "retail": [
                {
                    "title": "Online Retail Dataset",
                    "url": "https://www.kaggle.com/datasets/vijayuv/onlineretail",
                    "description": "Online retail transaction data",
                    "platform": "Kaggle",
                    "search_term": term
                }
            ]
        }
        return fallback_datasets.get(industry.lower(), [])
    
    def _get_huggingface_fallback_resources(self, term: str, industry: str) -> List[Dict[str, Any]]:
        """Fallback HuggingFace resources when API is not available"""
        fallback_resources = [
            {
                "title": "bert-base-uncased",
                "url": "https://huggingface.co/bert-base-uncased",
                "description": "BERT model for text classification and NLP tasks",
                "type": "model",
                "platform": "HuggingFace",
                "search_term": term
            }
        ]
        return fallback_resources
    
    def _get_github_fallback_repos(self, term: str, industry: str) -> List[Dict[str, Any]]:
        """Fallback GitHub repositories when API is not available"""
        fallback_repos = [
            {
                "title": "awesome-machine-learning",
                "url": "https://github.com/josephmisiti/awesome-machine-learning",
                "description": "A curated list of awesome Machine Learning frameworks, libraries and software",
                "language": "Python",
                "platform": "GitHub",
                "search_term": term
            }
        ]
        return fallback_repos
