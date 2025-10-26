"""
OpenAI Embeddings Service

Generates vector embeddings from text narratives for RAG (Retrieval-Augmented Generation).
Uses text-embedding-3-large model (3072 dimensions) for high-quality semantic search.
"""
import os
from typing import List, Union
import openai
from openai import OpenAI
import structlog
import tiktoken

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating vector embeddings from text"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        self.model = "text-embedding-3-large"
        self.dimensions = 3072  # Full dimensions for text-embedding-3-large
        self.max_tokens = 8191  # Maximum tokens for this model

        # Initialize tokenizer for token counting
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning("tiktoken_init_warning", error=str(e))
            self.encoding = None

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Text to embed (game narrative, query, etc.)

        Returns:
            List of floats representing the embedding vector (3072 dimensions)
        """
        try:
            # Check token count
            if self.encoding:
                token_count = len(self.encoding.encode(text))
                if token_count > self.max_tokens:
                    logger.warning(
                        "embedding_text_too_long",
                        token_count=token_count,
                        max_tokens=self.max_tokens
                    )
                    # Truncate text to fit within limits
                    text = self._truncate_text(text, self.max_tokens)

            logger.debug("embedding_request", text_length=len(text))

            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )

            embedding = response.data[0].embedding

            logger.info(
                "embedding_success",
                dimension=len(embedding),
                tokens_used=response.usage.total_tokens
            )

            return embedding

        except Exception as e:
            logger.error("embedding_error", error=str(e), text_preview=text[:100])
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        More efficient than calling embed_text multiple times.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            # Check and truncate texts if needed
            processed_texts = []
            for text in texts:
                if self.encoding:
                    token_count = len(self.encoding.encode(text))
                    if token_count > self.max_tokens:
                        text = self._truncate_text(text, self.max_tokens)
                processed_texts.append(text)

            logger.info("embedding_batch_request", batch_size=len(texts))

            response = self.client.embeddings.create(
                model=self.model,
                input=processed_texts,
                dimensions=self.dimensions
            )

            embeddings = [item.embedding for item in response.data]

            logger.info(
                "embedding_batch_success",
                batch_size=len(embeddings),
                total_tokens=response.usage.total_tokens
            )

            return embeddings

        except Exception as e:
            logger.error("embedding_batch_error", error=str(e), batch_size=len(texts))
            raise

    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum allowed tokens

        Returns:
            Truncated text
        """
        if not self.encoding:
            # Fallback: rough estimate (4 chars per token)
            max_chars = max_tokens * 4
            return text[:max_chars]

        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text

        # Truncate tokens and decode back to text
        truncated_tokens = tokens[:max_tokens]
        truncated_text = self.encoding.decode(truncated_tokens)

        logger.warning(
            "text_truncated",
            original_tokens=len(tokens),
            truncated_tokens=len(truncated_tokens)
        )

        return truncated_text

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Useful for estimating costs and checking limits.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not self.encoding:
            # Rough estimate if encoding unavailable
            return len(text) // 4

        return len(self.encoding.encode(text))

    def estimate_cost(self, token_count: int) -> float:
        """
        Estimate cost for embedding token count.

        Current pricing for text-embedding-3-large:
        $0.00013 per 1K tokens

        Args:
            token_count: Number of tokens

        Returns:
            Estimated cost in USD
        """
        price_per_1k_tokens = 0.00013
        return (token_count / 1000) * price_per_1k_tokens


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


# Utility functions for common use cases

async def embed_game_narrative(
    player_name: str,
    stat_type: str,
    stat_value: float,
    game_context: str,
    performance_notes: str
) -> List[float]:
    """
    Helper function to embed a game performance narrative.

    Args:
        player_name: Name of the player
        stat_type: Type of stat (receiving_yards, rushing_yards, etc.)
        stat_value: Actual stat value from the game
        game_context: Context about the game (weather, opponent, etc.)
        performance_notes: Analysis of the performance

    Returns:
        Embedding vector
    """
    service = get_embedding_service()

    narrative = f"""
Player: {player_name}
Stat Type: {stat_type}
Result: {stat_value}
Game Context: {game_context}
Performance Analysis: {performance_notes}
""".strip()

    return await service.embed_text(narrative)


async def embed_query(
    player_name: str,
    stat_type: str,
    search_context: str
) -> List[float]:
    """
    Helper function to embed a search query for RAG.

    Args:
        player_name: Name of the player
        stat_type: Type of stat to search for
        search_context: Description of what we're looking for

    Returns:
        Embedding vector for semantic search
    """
    service = get_embedding_service()

    query = f"""
Looking for: {player_name} {stat_type} performances
Similar to: {search_context}
""".strip()

    return await service.embed_text(query)
