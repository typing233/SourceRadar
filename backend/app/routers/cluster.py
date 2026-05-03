import logging
import math
import random
from typing import Optional, List, Dict, Any
from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.feed import score_item

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cluster", tags=["cluster"])

CATEGORY_COLORS = {
    "AI & Machine Learning": 0x00ff88,
    "Web Development": 0x4488ff,
    "Mobile Development": 0xff8844,
    "DevOps & Infrastructure": 0x88ff44,
    "Security": 0xff4488,
    "Data Science": 0x8844ff,
    "Database": 0xffff44,
    "Programming Languages": 0x44ffff,
    "Frameworks & Libraries": 0xff44ff,
    "Tools & Utilities": 0x888888,
    "Documentation": 0x44ff88,
    "Testing": 0xffaa44,
    "Game Development": 0x8844ff,
    "IoT": 0x44aaff,
    "Blockchain & Crypto": 0xffaa00,
}


def calculate_similarity(tags1: List[str], tags2: List[str]) -> float:
    if not tags1 or not tags2:
        return 0.0
    
    set1 = set(tags1)
    set2 = set(tags2)
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def generate_force_layout(
    nodes: List[Dict[str, Any]],
    links: List[Dict[str, Any]],
    iterations: int = 50
) -> List[Dict[str, Any]]:
    k = 50.0
    repulsion = 400.0
    damping = 0.85
    center_force = 0.02
    
    velocities = {n["id"]: {"x": 0.0, "y": 0.0, "z": 0.0} for n in nodes}
    positions = {n["id"]: {"x": n.get("x", random.uniform(-100, 100)), 
                           "y": n.get("y", random.uniform(-100, 100)),
                           "z": n.get("z", random.uniform(-100, 100))} for n in nodes}
    
    for _ in range(iterations):
        forces = {n["id"]: {"x": 0.0, "y": 0.0, "z": 0.0} for n in nodes}
        
        for i, n1 in enumerate(nodes):
            for j, n2 in enumerate(nodes):
                if i >= j:
                    continue
                
                pos1 = positions[n1["id"]]
                pos2 = positions[n2["id"]]
                
                dx = pos2["x"] - pos1["x"]
                dy = pos2["y"] - pos1["y"]
                dz = pos2["z"] - pos1["z"]
                dist_sq = dx*dx + dy*dy + dz*dz
                
                if dist_sq < 0.1:
                    dx = random.uniform(-1, 1)
                    dy = random.uniform(-1, 1)
                    dz = random.uniform(-1, 1)
                    dist_sq = 1.0
                
                dist = math.sqrt(dist_sq)
                force_mag = repulsion / dist_sq
                
                fx = (dx / dist) * force_mag
                fy = (dy / dist) * force_mag
                fz = (dz / dist) * force_mag
                
                forces[n1["id"]]["x"] -= fx
                forces[n1["id"]]["y"] -= fy
                forces[n1["id"]]["z"] -= fz
                forces[n2["id"]]["x"] += fx
                forces[n2["id"]]["y"] += fy
                forces[n2["id"]]["z"] += fz
        
        for link in links:
            source_id = link["source"]
            target_id = link["target"]
            strength = link.get("strength", 0.5)
            
            pos1 = positions[source_id]
            pos2 = positions[target_id]
            
            dx = pos2["x"] - pos1["x"]
            dy = pos2["y"] - pos1["y"]
            dz = pos2["z"] - pos1["z"]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < 0.1:
                continue
            
            target_dist = k * (1.5 - strength)
            force_mag = (dist - target_dist) * 0.1 * strength
            
            fx = (dx / dist) * force_mag
            fy = (dy / dist) * force_mag
            fz = (dz / dist) * force_mag
            
            forces[source_id]["x"] += fx
            forces[source_id]["y"] += fy
            forces[source_id]["z"] += fz
            forces[target_id]["x"] -= fx
            forces[target_id]["y"] -= fy
            forces[target_id]["z"] -= fz
        
        for node in nodes:
            node_id = node["id"]
            pos = positions[node_id]
            vel = velocities[node_id]
            force = forces[node_id]
            
            force["x"] -= pos["x"] * center_force
            force["y"] -= pos["y"] * center_force
            force["z"] -= pos["z"] * center_force
            
            vel["x"] = (vel["x"] + force["x"]) * damping
            vel["y"] = (vel["y"] + force["y"]) * damping
            vel["z"] = (vel["z"] + force["z"]) * damping
            
            pos["x"] += vel["x"]
            pos["y"] += vel["y"]
            pos["z"] += vel["z"]
    
    for node in nodes:
        node["x"] = positions[node["id"]]["x"]
        node["y"] = positions[node["id"]]["y"]
        node["z"] = positions[node["id"]]["z"]
    
    return nodes


@router.get("/categories", response_model=List[str])
def get_categories():
    from app.services.semantic import SemanticService
    return SemanticService.DEFAULT_CATEGORIES


@router.get("/list", response_model=schemas.ClusterListResponse)
def get_clusters(
    source: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_tags = [ut.tag.name for ut in current_user.user_tags]
    
    query = db.query(models.Item)
    if source:
        query = query.filter(models.Item.source == source)
    if q:
        search = f"%{q}%"
        query = query.filter(
            models.Item.title.ilike(search) | models.Item.description.ilike(search)
        )
    
    all_items = query.all()
    
    scored = []
    for item in all_items:
        ms = score_item(item, user_tags)
        scored.append((item, ms))
    
    scored.sort(key=lambda x: (x[1], x[0].published_at or x[0].created_at), reverse=True)
    
    clusters: Dict[str, List[schemas.ItemOut]] = defaultdict(list)
    categories_set = set()
    
    for item, ms in scored:
        category = item.category or "Uncategorized"
        categories_set.add(category)
        
        clusters[category].append(
            schemas.ItemOut(
                id=item.id,
                title=item.title,
                url=item.url,
                description=item.description or "",
                source=item.source,
                raw_tags=item.get_raw_tags(),
                semantic_tags=item.get_semantic_tags(),
                category=item.category,
                score=item.score,
                published_at=item.published_at,
                created_at=item.created_at,
                analyzed_at=item.analyzed_at,
                match_score=ms,
            )
        )
    
    cluster_responses = []
    for category, items in sorted(clusters.items(), key=lambda x: -len(x[1])):
        cluster_responses.append(
            schemas.ClusterResponse(
                category=category,
                items=items,
                count=len(items),
            )
        )
    
    return schemas.ClusterListResponse(
        clusters=cluster_responses,
        total_items=len(all_items),
        categories=sorted(categories_set),
    )


@router.get("/topology", response_model=schemas.TopologyResponse)
def get_topology(
    source: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_tags = [ut.tag.name for ut in current_user.user_tags]
    
    query = db.query(models.Item)
    if source:
        query = query.filter(models.Item.source == source)
    if q:
        search = f"%{q}%"
        query = query.filter(
            models.Item.title.ilike(search) | models.Item.description.ilike(search)
        )
    
    all_items = query.all()
    
    scored = []
    for item in all_items:
        ms = score_item(item, user_tags)
        scored.append((item, ms))
    
    scored.sort(key=lambda x: (x[1], x[0].published_at or x[0].created_at), reverse=True)
    scored = scored[:limit]
    
    categories_set = set()
    nodes_data = []
    
    for item, ms in scored:
        category = item.category or "Uncategorized"
        categories_set.add(category)
        
        all_tags = item.get_all_tags()
        size = min(5.0, 1.0 + ms * 3.0 + (item.score / 10000.0))
        
        nodes_data.append({
            "id": item.id,
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "category": category,
            "tags": all_tags,
            "match_score": ms,
            "size": size,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        })
    
    links_data = []
    for i, n1 in enumerate(nodes_data):
        for j, n2 in enumerate(nodes_data):
            if i >= j:
                continue
            
            similarity = calculate_similarity(n1["tags"], n2["tags"])
            
            same_category = n1["category"] == n2["category"]
            if same_category:
                similarity = max(similarity, 0.3)
            
            if similarity > 0.15:
                links_data.append({
                    "source": n1["id"],
                    "target": n2["id"],
                    "strength": similarity,
                })
    
    nodes_data = generate_force_layout(nodes_data, links_data)
    
    nodes = []
    for n in nodes_data:
        nodes.append(schemas.ClusterNode(
            id=n["id"],
            title=n["title"],
            url=n["url"],
            source=n["source"],
            category=n["category"],
            tags=n["tags"],
            match_score=n["match_score"],
            x=n["x"],
            y=n["y"],
            z=n["z"],
            size=n["size"],
        ))
    
    links = []
    for l in links_data:
        links.append(schemas.ClusterLink(
            source=l["source"],
            target=l["target"],
            strength=l["strength"],
        ))
    
    return schemas.TopologyResponse(
        nodes=nodes,
        links=links,
        categories=sorted(categories_set),
        total_nodes=len(nodes),
    )
