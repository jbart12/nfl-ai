"""
Qdrant Vector Store Service

Manages vector storage and semantic search for game performance narratives.
Enables RAG (Retrieval-Augmented Generation) by finding similar historical situations.
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
)
import structlog

logger = structlog.get_logger()


class VectorStoreService:
    """Service for vector storage and semantic search using Qdrant"""

    def __init__(self):
        # Support both QDRANT_URL and separate QDRANT_HOST/QDRANT_PORT
        qdrant_url = os.getenv("QDRANT_URL")
        if qdrant_url:
            self.client = QdrantClient(url=qdrant_url)
        else:
            # Build URL from host and port (for local development)
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = os.getenv("QDRANT_PORT", "6333")
            url = f"http://{qdrant_host}:{qdrant_port}"
            self.client = QdrantClient(url=url)
            logger.info("qdrant_client_initialized", url=url)

        self.collection_name = "game_performances"
        self.vector_size = 3072  # text-embedding-3-large dimensions

        # Initialize collection if it doesn't exist
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info("creating_qdrant_collection", collection=self.collection_name)

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE  # Cosine similarity for semantic search
                    )
                )

                logger.info("qdrant_collection_created", collection=self.collection_name)
            else:
                logger.info("qdrant_collection_exists", collection=self.collection_name)

        except Exception as e:
            logger.error("qdrant_collection_init_error", error=str(e))
            raise

    async def store_game_performance(
        self,
        player_id: str,
        player_name: str,
        stat_type: str,
        stat_value: float,
        game_date: str,
        week: int,
        season: int,
        opponent: str,
        narrative: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a game performance narrative with its embedding.

        Args:
            player_id: Unique player identifier
            player_name: Player name
            stat_type: Type of stat (receiving_yards, rushing_yards, etc.)
            stat_value: Actual stat value from the game
            game_date: Date of the game (ISO format)
            week: NFL week number
            season: NFL season year
            opponent: Opponent team abbreviation
            narrative: Full text narrative of the game performance
            embedding: Vector embedding of the narrative
            metadata: Additional metadata to store

        Returns:
            ID of the stored point
        """
        try:
            # Generate unique UUID for this performance
            # Use uuid5 for deterministic UUIDs based on player_id, season, week, stat_type
            unique_string = f"{player_id}_{season}_week{week}_{stat_type}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

            # Build payload with all metadata
            payload = {
                "player_id": player_id,
                "player_name": player_name,
                "stat_type": stat_type,
                "stat_value": stat_value,
                "game_date": game_date,
                "week": week,
                "season": season,
                "opponent": opponent,
                "narrative": narrative,
                "unique_key": unique_string,  # Store for easy lookups
                "created_at": datetime.utcnow().isoformat(),
            }

            # Add any additional metadata
            if metadata:
                payload.update(metadata)

            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            logger.info(
                "game_performance_stored",
                point_id=point_id,
                player=player_name,
                stat_type=stat_type,
                stat_value=stat_value
            )

            return point_id

        except Exception as e:
            logger.error(
                "store_game_performance_error",
                error=str(e),
                player=player_name
            )
            raise

    async def search_similar_performances(
        self,
        query_embedding: List[float],
        player_id: Optional[str] = None,
        stat_type: Optional[str] = None,
        season: Optional[int] = None,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar game performances using semantic search.

        Args:
            query_embedding: Vector embedding of the search query
            player_id: Filter by specific player (optional)
            stat_type: Filter by stat type (optional)
            season: Filter by season (optional)
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of similar performances with metadata and similarity scores
        """
        try:
            # Build filters
            filter_conditions = []

            if player_id:
                filter_conditions.append(
                    FieldCondition(
                        key="player_id",
                        match=MatchValue(value=player_id)
                    )
                )

            if stat_type:
                filter_conditions.append(
                    FieldCondition(
                        key="stat_type",
                        match=MatchValue(value=stat_type)
                    )
                )

            if season:
                filter_conditions.append(
                    FieldCondition(
                        key="season",
                        match=MatchValue(value=season)
                    )
                )

            # Build filter object
            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)

            logger.debug(
                "searching_similar_performances",
                player_id=player_id,
                stat_type=stat_type,
                limit=limit
            )

            # Perform semantic search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=score_threshold
            )

            # Format results
            similar_performances = []
            for result in results:
                performance = {
                    "id": result.id,
                    "similarity_score": result.score,
                    "player_name": result.payload.get("player_name"),
                    "stat_type": result.payload.get("stat_type"),
                    "stat_value": result.payload.get("stat_value"),
                    "game_date": result.payload.get("game_date"),
                    "week": result.payload.get("week"),
                    "season": result.payload.get("season"),
                    "opponent": result.payload.get("opponent"),
                    "narrative": result.payload.get("narrative"),
                    "game": f"Week {result.payload.get('week')}, {result.payload.get('season')} vs {result.payload.get('opponent')}",
                    "result": f"{result.payload.get('stat_value')} {result.payload.get('stat_type').replace('_', ' ')}",
                    "context": result.payload.get("narrative", "")[:200] + "..."
                }

                # Add any additional metadata
                for key, value in result.payload.items():
                    if key not in performance:
                        performance[key] = value

                similar_performances.append(performance)

            logger.info(
                "similar_performances_found",
                count=len(similar_performances),
                player_id=player_id,
                stat_type=stat_type
            )

            return similar_performances

        except Exception as e:
            logger.error("search_similar_performances_error", error=str(e))
            raise

    async def delete_performance(self, point_id: str):
        """Delete a specific game performance from the vector store"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )

            logger.info("performance_deleted", point_id=point_id)

        except Exception as e:
            logger.error("delete_performance_error", error=str(e), point_id=point_id)
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)

            stats = {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "status": collection_info.status,
            }

            logger.info("collection_stats_retrieved", **stats)

            return stats

        except Exception as e:
            logger.error("get_collection_stats_error", error=str(e))
            raise

    async def clear_collection(self):
        """Clear all data from the collection (use with caution!)"""
        try:
            logger.warning("clearing_collection", collection=self.collection_name)

            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()

            logger.warning("collection_cleared", collection=self.collection_name)

        except Exception as e:
            logger.error("clear_collection_error", error=str(e))
            raise


# Singleton instance
_vector_store_service = None


def get_vector_store_service() -> VectorStoreService:
    """Get or create vector store service singleton"""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service
