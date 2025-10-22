"""
Semantic search service for relationship contexts
Provides vector similarity search and intelligent matching
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from app.models.relationship import Relationship


class SemanticSearchService:
    """
    Semantic search service using vector embeddings
    
    Enables intelligent relationship discovery through:
    - Semantic similarity search
    - Domain-specific matching
    - Context-aware recommendations
    """
    
    def __init__(self, db: AsyncSession, model_name: str = "all-MiniLM-L6-v2"):
        self.db = db
        self.model_name = model_name
        self._model = None
        self._model_lock = asyncio.Lock()
    
    async def get_model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model"""
        if self._model is None:
            async with self._model_lock:
                if self._model is None:
                    # Load model in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    self._model = await loop.run_in_executor(
                        None, lambda: SentenceTransformer(self.model_name)
                    )
        return self._model
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate 384-dimensional embedding for text"""
        model = await self.get_model()
        
        # Run embedding generation in thread pool
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, lambda: model.encode(text, normalize_embeddings=True)
        )
        
        return embedding.tolist()
    
    async def generate_relationship_embedding(
        self, 
        context: str, 
        domain: str, 
        expertise: List[str],
        collaboration_type: str
    ) -> List[float]:
        """
        Generate contextual embedding for a relationship
        
        Combines multiple context signals into a single embedding
        """
        # Create comprehensive text representation
        expertise_text = ", ".join(expertise) if expertise else ""
        
        combined_text = (
            f"Domain: {domain}. "
            f"Collaboration: {collaboration_type}. "
            f"Expertise: {expertise_text}. "
            f"Context: {context}"
        )
        
        return await self.generate_embedding(combined_text)
    
    async def find_similar_relationships(
        self,
        query_embedding: List[float],
        entity_id: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.7,
        domain_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Find relationships with similar semantic context
        
        Uses cosine similarity with optional filtering
        """
        # Convert to numpy for efficient computation
        query_vector = np.array(query_embedding)
        
        # Build SQL query with vector similarity
        # Note: In production, would use pgvector for efficient similarity search
        base_query = """
        SELECT 
            r.id,
            r.entity_a_id,
            r.entity_b_id,
            r.strength,
            r.context,
            rc.domain,
            rc.expertise,
            rc.collaboration_type,
            rc.embedding,
            -- Calculate cosine similarity (simplified for demo)
            (1 - (rc.embedding <=> %s::vector)) as similarity
        FROM relationships r
        JOIN relationship_contexts rc ON r.id = rc.relationship_id
        WHERE rc.embedding IS NOT NULL
        """
        
        params = [query_embedding]
        
        if entity_id:
            base_query += " AND (r.entity_a_id = %s OR r.entity_b_id = %s)"
            params.extend([entity_id, entity_id])
            
        if domain_filter:
            base_query += " AND rc.domain = %s"
            params.append(domain_filter)
            
        base_query += f"""
        ORDER BY similarity DESC
        LIMIT {limit}
        """
        
        # Execute raw SQL for vector operations
        # In practice, would use proper pgvector integration
        result = await self.db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Process results
        similar_relationships = []
        for row in rows:
            if row.similarity >= min_similarity:
                similar_relationships.append({
                    "relationship_id": row.id,
                    "entity_a_id": row.entity_a_id,
                    "entity_b_id": row.entity_b_id,
                    "strength": row.strength,
                    "context": row.context,
                    "domain": row.domain,
                    "expertise": row.expertise,
                    "collaboration_type": row.collaboration_type,
                    "similarity_score": float(row.similarity)
                })
        
        return similar_relationships
    
    async def recommend_connections(
        self,
        entity_id: str,
        query_context: str,
        max_recommendations: int = 5
    ) -> List[Dict]:
        """
        Recommend potential connections based on semantic similarity
        
        Finds entities with similar expertise/context that aren't directly connected
        """
        # Generate embedding for query context
        query_embedding = await self.generate_embedding(query_context)
        
        # Find similar relationships that don't involve the query entity
        similar_rels = await self.find_similar_relationships(
            query_embedding=query_embedding,
            limit=50  # Cast wider net for recommendations
        )
        
        # Filter out relationships involving the query entity
        candidates = []
        seen_entities = set()
        
        for rel in similar_rels:
            # Identify potential connection targets
            if rel["entity_a_id"] != entity_id and rel["entity_a_id"] not in seen_entities:
                candidates.append({
                    "target_entity": rel["entity_a_id"],
                    "similarity_score": rel["similarity_score"],
                    "shared_context": rel["context"],
                    "domain": rel["domain"],
                    "expertise": rel["expertise"],
                    "reasoning": f"Similar {rel['collaboration_type']} experience in {rel['domain']}"
                })
                seen_entities.add(rel["entity_a_id"])
                
            if rel["entity_b_id"] != entity_id and rel["entity_b_id"] not in seen_entities:
                candidates.append({
                    "target_entity": rel["entity_b_id"],
                    "similarity_score": rel["similarity_score"],
                    "shared_context": rel["context"],
                    "domain": rel["domain"],
                    "expertise": rel["expertise"],
                    "reasoning": f"Similar {rel['collaboration_type']} experience in {rel['domain']}"
                })
                seen_entities.add(rel["entity_b_id"])
            
            if len(candidates) >= max_recommendations:
                break
        
        return candidates[:max_recommendations]
    
    async def find_expertise_matches(
        self,
        expertise_areas: List[str],
        exclude_entity: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find entities with matching expertise areas
        
        Uses both exact matching and semantic similarity
        """
        if not expertise_areas:
            return []
        
        # Generate embedding for combined expertise
        expertise_text = ", ".join(expertise_areas)
        expertise_embedding = await self.generate_embedding(
            f"Expertise in: {expertise_text}"
        )
        
        # Find semantically similar expertise
        matches = await self.find_similar_relationships(
            query_embedding=expertise_embedding,
            limit=limit * 2  # Get more candidates for filtering
        )
        
        # Process and rank matches
        expertise_matches = []
        seen_entities = set()
        
        for match in matches:
            # Extract unique entities from relationships
            for entity_id in [match["entity_a_id"], match["entity_b_id"]]:
                if (entity_id != exclude_entity and 
                    entity_id not in seen_entities):
                    
                    # Calculate expertise overlap
                    overlap_score = self._calculate_expertise_overlap(
                        expertise_areas, match["expertise"]
                    )
                    
                    expertise_matches.append({
                        "entity_id": entity_id,
                        "expertise": match["expertise"],
                        "domain": match["domain"],
                        "overlap_score": overlap_score,
                        "semantic_similarity": match["similarity_score"],
                        "combined_score": 0.6 * overlap_score + 0.4 * match["similarity_score"]
                    })
                    
                    seen_entities.add(entity_id)
                    
                    if len(expertise_matches) >= limit:
                        break
        
        # Sort by combined score
        expertise_matches.sort(key=lambda x: x["combined_score"], reverse=True)
        return expertise_matches[:limit]
    
    def _calculate_expertise_overlap(
        self, 
        query_expertise: List[str], 
        candidate_expertise: List[str]
    ) -> float:
        """Calculate Jaccard similarity between expertise lists"""
        if not query_expertise or not candidate_expertise:
            return 0.0
        
        query_set = set(skill.lower().strip() for skill in query_expertise)
        candidate_set = set(skill.lower().strip() for skill in candidate_expertise)
        
        intersection = len(query_set.intersection(candidate_set))
        union = len(query_set.union(candidate_set))
        
        return intersection / union if union > 0 else 0.0
    
    async def update_relationship_context(
        self,
        relationship_id: str,
        context: str,
        domain: str,
        expertise: List[str],
        collaboration_type: str,
        semantic_tags: List[str],
        project_names: Optional[List[str]] = None,
        geographic_scope: Optional[str] = None
    ) -> Dict:
        """
        Update or create relationship context with embedding generation
        """
        # Generate embedding for the relationship context
        embedding = await self.generate_relationship_embedding(
            context=context,
            domain=domain,
            expertise=expertise,
            collaboration_type=collaboration_type
        )
        
        # Create context record
        context_data = {
            "relationship_id": relationship_id,
            "domain": domain,
            "expertise": expertise,
            "collaboration_type": collaboration_type,
            "semantic_tags": semantic_tags,
            "embedding": embedding,
            "project_names": project_names or [],
            "geographic_scope": geographic_scope,
            "confidence_score": 85,  # Default confidence
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # In production, would save to relationship_contexts table
        # For now, return the context data
        return context_data
    
    async def batch_generate_embeddings(
        self, 
        contexts: List[Dict[str, any]]
    ) -> List[Dict]:
        """
        Efficiently generate embeddings for multiple contexts
        
        Uses batching for better performance
        """
        if not contexts:
            return []
        
        model = await self.get_model()
        
        # Prepare texts for batch processing
        texts = []
        for ctx in contexts:
            combined_text = (
                f"Domain: {ctx.get('domain', '')}. "
                f"Collaboration: {ctx.get('collaboration_type', '')}. "
                f"Expertise: {', '.join(ctx.get('expertise', []))}. "
                f"Context: {ctx.get('context', '')}"
            )
            texts.append(combined_text)
        
        # Generate embeddings in batch
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: model.encode(texts, normalize_embeddings=True)
        )
        
        # Combine with original contexts
        results = []
        for ctx, embedding in zip(contexts, embeddings):
            result = ctx.copy()
            result["embedding"] = embedding.tolist()
            results.append(result)
        
        return results