import json
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    base_url: str
    api_key: str
    model_name: str
    embedding_model: str


class SemanticService:
    DEFAULT_CATEGORIES = [
        "AI & Machine Learning",
        "Web Development",
        "Mobile Development",
        "DevOps & Infrastructure",
        "Security",
        "Data Science",
        "Database",
        "Programming Languages",
        "Frameworks & Libraries",
        "Tools & Utilities",
        "Documentation",
        "Testing",
        "Game Development",
        "IoT",
        "Blockchain & Crypto",
    ]

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            embedding_model=settings.LLM_EMBEDDING_MODEL,
        )

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def test_connection(self) -> Tuple[bool, str]:
        if not self.config.api_key:
            return False, "API key is not configured"
        
        try:
            base_url = self.config.base_url.rstrip("/")
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{base_url}/models",
                    headers=self._get_headers(),
                )
                if resp.status_code == 200:
                    return True, "Connection successful"
                else:
                    return False, f"API returned status {resp.status_code}: {resp.text[:200]}"
        except httpx.TimeoutException:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        if not self.config.api_key:
            logger.warning("LLM API key not configured, skipping embedding generation")
            return None
        
        try:
            base_url = self.config.base_url.rstrip("/")
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{base_url}/embeddings",
                    headers=self._get_headers(),
                    json={
                        "model": self.config.embedding_model,
                        "input": text[:8000],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
                return None
        except Exception as e:
            logger.error("Failed to generate embedding: %s", e)
            return None

    async def generate_tags(self, title: str, description: str, existing_tags: List[str] = None) -> List[str]:
        if not self.config.api_key:
            logger.warning("LLM API key not configured, using basic tagging")
            return self._basic_tagging(title, description, existing_tags)
        
        prompt = self._build_tag_prompt(title, description, existing_tags)
        
        try:
            base_url = self.config.base_url.rstrip("/")
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": self.config.model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a tech project classifier. Analyze the given project and return a JSON array of relevant tags. Tags should be concise, technical, and relevant. Return only the JSON array, no other text."
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 200,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                try:
                    if content.startswith("```"):
                        lines = content.split("\n")
                        content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
                    
                    tags = json.loads(content)
                    if isinstance(tags, list):
                        return [t.strip().lower() for t in tags if isinstance(t, str) and t.strip()]
                except json.JSONDecodeError:
                    pass
                
                return self._basic_tagging(title, description, existing_tags)
        except Exception as e:
            logger.error("Failed to generate tags with LLM: %s", e)
            return self._basic_tagging(title, description, existing_tags)

    async def categorize_project(self, title: str, description: str) -> str:
        if not self.config.api_key:
            return self._basic_categorize(title, description)
        
        prompt = f"""Categorize this project into ONE of the following categories:
{', '.join(self.DEFAULT_CATEGORIES)}

Project:
Title: {title}
Description: {description}

Return only the category name, nothing else."""
        
        try:
            base_url = self.config.base_url.rstrip("/")
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": self.config.model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a project categorizer. Return only the category name, no explanation."
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 50,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                category = data["choices"][0]["message"]["content"].strip()
                
                for cat in self.DEFAULT_CATEGORIES:
                    if category.lower() in cat.lower() or cat.lower() in category.lower():
                        return cat
                
                return self._basic_categorize(title, description)
        except Exception as e:
            logger.error("Failed to categorize project: %s", e)
            return self._basic_categorize(title, description)

    def _basic_tagging(self, title: str, description: str, existing_tags: List[str] = None) -> List[str]:
        text = (title + " " + description).lower()
        tags = set(existing_tags) if existing_tags else set()
        
        keyword_mappings = {
            "ai": ["artificial intelligence", "machine learning", "neural network", "gpt", "llm"],
            "ml": ["machine learning", "ml", "scikit-learn", "tensorflow", "pytorch"],
            "javascript": ["javascript", "js", "ecmascript"],
            "typescript": ["typescript", "ts"],
            "python": ["python"],
            "rust": ["rust"],
            "go": ["golang", " go "],
            "java": ["java"],
            "c++": ["c++", "cpp"],
            "react": ["react"],
            "vue": ["vue"],
            "angular": ["angular"],
            "nodejs": ["node.js", "nodejs", "node"],
            "web": ["web", "frontend", "backend"],
            "api": ["api", "rest", "graphql"],
            "database": ["database", "mysql", "postgres", "mongodb", "sql"],
            "devops": ["devops", "docker", "kubernetes", "k8s", "ci/cd"],
            "security": ["security", "encryption", "authentication", "authorization"],
            "mobile": ["mobile", "ios", "android", "react-native"],
            "cli": ["cli", "command-line", "terminal"],
            "framework": ["framework", "library"],
        }
        
        for tag, keywords in keyword_mappings.items():
            if any(kw in text for kw in keywords):
                tags.add(tag)
        
        return list(tags)

    def _basic_categorize(self, title: str, description: str) -> str:
        text = (title + " " + description).lower()
        
        category_keywords = {
            "AI & Machine Learning": ["ai", "ml", "machine learning", "neural", "gpt", "llm", "tensorflow", "pytorch"],
            "Web Development": ["web", "frontend", "backend", "react", "vue", "angular", "html", "css", "javascript"],
            "Mobile Development": ["mobile", "ios", "android", "flutter", "react-native"],
            "DevOps & Infrastructure": ["devops", "docker", "kubernetes", "k8s", "cloud", "aws", "azure", "gcp"],
            "Security": ["security", "encryption", "auth", "hack", "penetration"],
            "Data Science": ["data", "analytics", "visualization", "pandas", "numpy"],
            "Database": ["database", "mysql", "postgres", "mongodb", "redis", "sql"],
            "Programming Languages": ["python", "rust", "go", "java", "c++", "typescript"],
            "Frameworks & Libraries": ["framework", "library", "sdk", "package"],
            "Tools & Utilities": ["tool", "utility", "cli", "automation", "script"],
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                return category
        
        return "Tools & Utilities"

    async def cluster_items(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        clusters = {}
        for item in items:
            category = await self.categorize_project(
                item.get("title", ""),
                item.get("description", "")
            )
            if category not in clusters:
                clusters[category] = []
            clusters[category].append(item)
        
        return clusters


_semantic_service: Optional[SemanticService] = None


def get_semantic_service() -> SemanticService:
    global _semantic_service
    if _semantic_service is None:
        _semantic_service = SemanticService()
    return _semantic_service
