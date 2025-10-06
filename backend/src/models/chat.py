"""
Project IRIS - Chat and Q&A Database Models
SQLAlchemy models for interactive Q&A system
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database.base import BaseModel, JSONBType


class AgentType(enum.Enum):
    """Types of AI agents"""
    FORENSIC = "forensic"
    SENTIMENT = "sentiment"
    PEER_BENCHMARK = "peer_benchmark"
    REGULATORY = "regulatory"
    GENERAL = "general"


class MessageType(enum.Enum):
    """Message types in chat"""
    USER_QUERY = "user_query"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_MESSAGE = "system_message"
    FOLLOW_UP_SUGGESTION = "follow_up_suggestion"


class ChatSession(BaseModel):
    """Chat session model for Q&A interactions"""

    __tablename__ = "chat_sessions"

    # Session identification
    session_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # Context
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    agent_type = Column(Enum(AgentType), nullable=False, index=True)
    
    # Session metadata
    session_title = Column(String(200))
    session_description = Column(Text)
    
    # User information
    user_id = Column(String(100), index=True)  # For future user management
    user_ip = Column(String(45))
    user_agent = Column(String(500))
    
    # Session status
    is_active = Column(Boolean, default=True, index=True)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Session statistics
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Configuration
    model_version = Column(String(50))
    temperature = Column(Float, default=0.1)
    max_tokens = Column(Integer, default=4000)
    
    # Relationships
    company = relationship("Company")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    # Indexes
    __table_args__ = (
        Index('idx_chat_session_company_agent', 'company_id', 'agent_type'),
        Index('idx_chat_session_active', 'is_active', 'last_activity'),
        Index('idx_chat_session_user', 'user_id'),
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id={self.session_id}, agent_type={self.agent_type.value})>"


class ChatMessage(BaseModel):
    """Individual chat messages"""

    __tablename__ = "chat_messages"

    # Foreign key
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    
    # Message details
    message_type = Column(Enum(MessageType), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Query processing (for user queries)
    original_query = Column(Text)
    processed_query = Column(Text)
    query_intent = Column(String(100))
    
    # Response generation (for agent responses)
    response_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    model_used = Column(String(50))
    
    # RAG system data (for agent responses)
    retrieved_chunks = Column(JSONBType)  # List of retrieved document chunks
    chunk_scores = Column(JSONBType)  # Similarity scores for chunks
    citations = Column(JSONBType)  # List of citations in response
    
    # Quality metrics
    confidence_score = Column(Float)  # 0-1 confidence in response
    relevance_score = Column(Float)  # 0-1 relevance to query
    
    # User feedback
    user_rating = Column(Integer)  # 1-5 star rating
    user_feedback = Column(Text)
    is_helpful = Column(Boolean)
    
    # Follow-up suggestions
    follow_up_questions = Column(JSONBType)  # List of suggested follow-ups
    
    # Error handling
    has_error = Column(Boolean, default=False)
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('idx_chat_message_session_type', 'session_id', 'message_type'),
        Index('idx_chat_message_created', 'created_at'),
        Index('idx_chat_message_confidence', 'confidence_score'),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, type={self.message_type.value})>"


class DocumentChunk(BaseModel):
    """Document chunks for RAG system"""

    __tablename__ = "document_chunks"

    # Source information
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False, index=True)  # financial_statement, annual_report, etc.
    source_id = Column(String(100), nullable=False)  # ID of source document
    
    # Chunk details
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_tokens = Column(Integer)
    
    # Metadata
    document_title = Column(String(500))
    document_date = Column(DateTime)
    page_number = Column(Integer)
    section_title = Column(String(200))
    
    # Embedding information
    embedding_model = Column(String(100))
    embedding_dimension = Column(Integer)
    embedding_created_at = Column(DateTime, default=datetime.utcnow)
    
    # ChromaDB reference
    chromadb_collection = Column(String(100))
    chromadb_id = Column(String(100), unique=True)
    
    # Usage statistics
    retrieval_count = Column(Integer, default=0)
    last_retrieved = Column(DateTime)
    
    # Relationships
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_chunk_company_source', 'company_id', 'source_type'),
        Index('idx_chunk_chromadb', 'chromadb_collection', 'chromadb_id'),
        Index('idx_chunk_document', 'source_id', 'chunk_index'),
    )

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, company_id={self.company_id}, source_type={self.source_type})>"


class QueryAnalytics(BaseModel):
    """Analytics for query patterns and performance"""

    __tablename__ = "query_analytics"

    # Query information
    query_text = Column(Text, nullable=False)
    query_hash = Column(String(64), index=True)  # Hash of normalized query
    query_category = Column(String(100), index=True)
    
    # Context
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    agent_type = Column(Enum(AgentType), nullable=False, index=True)
    
    # Performance metrics
    response_time_ms = Column(Integer)
    retrieval_time_ms = Column(Integer)
    generation_time_ms = Column(Integer)
    
    # Quality metrics
    confidence_score = Column(Float)
    user_satisfaction = Column(Float)  # Aggregated user ratings
    
    # Usage statistics
    query_count = Column(Integer, default=1)
    last_queried = Column(DateTime, default=datetime.utcnow)
    
    # Popular queries tracking
    is_trending = Column(Boolean, default=False)
    trend_score = Column(Float)
    
    # Relationships
    company = relationship("Company")

    # Indexes
    __table_args__ = (
        Index('idx_analytics_query_hash', 'query_hash'),
        Index('idx_analytics_category_agent', 'query_category', 'agent_type'),
        Index('idx_analytics_trending', 'is_trending', 'trend_score'),
    )

    def __repr__(self):
        return f"<QueryAnalytics(id={self.id}, query_hash={self.query_hash}, count={self.query_count})>"
