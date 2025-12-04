"""
Project IRIS - Agent 7: Q&A RAG System
Natural language Q&A system using ChromaDB vector storage and Gemini 2.0 for financial analysis queries
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os
import hashlib

import chromadb
from chromadb.config import Settings as ChromaSettings
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np

from src.config import settings

logger = logging.getLogger(__name__)


class QASystem:
    """Agent 7: Q&A RAG System for financial queries"""

    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.gemini_model = None

        # Initialize components
        self._initialize_chroma()
        self._initialize_embedding_model()
        self._initialize_gemini()

        logger.info("Q&A RAG System initialized successfully")

    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory
            )

            # Create or get collection for financial documents
            self.collection = self.chroma_client.get_or_create_collection(
                name="financial_documents",
                metadata={"description": "Financial analysis documents and company data"}
            )

            logger.info(f"ChromaDB initialized with collection: financial_documents")

        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            raise

    def _initialize_embedding_model(self):
        """Initialize sentence transformer for embeddings"""
        try:
            # Use a financial domain-specific model if available, otherwise use general purpose
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

            logger.info("Embedding model initialized successfully")

        except Exception as e:
            logger.error(f"Embedding model initialization failed: {e}")
            raise

    def _initialize_gemini(self):
        """Initialize Gemini 2.0 model"""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                    top_p=0.9,
                    top_k=40
                )
            )

            logger.info("Gemini 2.0 model initialized successfully")

        except Exception as e:
            logger.error(f"Gemini model initialization failed: {e}")
            raise

    def add_document(self, document_id: str, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Add document to vector database"""
        try:
            if metadata is None:
                metadata = {}

            # Generate embedding
            embedding = self.embedding_model.encode(text).tolist()

            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[document_id]
            )

            logger.info(f"Document {document_id} added to vector database")
            return True

        except Exception as e:
            logger.error(f"Failed to add document {document_id}: {e}")
            return False

    def search_similar_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'distance': results['distances'][0][i]
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []

    def generate_answer(self, query: str, context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using Gemini with RAG context"""
        try:
            # Prepare context from similar documents
            context = "\n\n".join([doc['document'] for doc in context_documents[:3]])

            # Create prompt with context
            prompt = f"""
You are a financial analysis expert specializing in Indian public companies. Answer the following question using the provided context from financial documents and analysis.

**Context from Financial Documents:**
{context}

**Question:** {query}

**Instructions:**
- Use only information from the provided context
- If the context doesn't contain enough information to answer the question, say so clearly
- Provide specific financial metrics, ratios, or data points when relevant
- Use formal, professional language suitable for financial analysis
- Structure your answer with clear sections if needed
- Include confidence level if the information is partial or uncertain

**Response Format:**
- Start with a direct answer
- Provide supporting evidence from the context
- End with any relevant caveats or limitations
"""

            # Generate response with Gemini
            response = self.gemini_model.generate_content(prompt)

            if response and response.text:
                answer_text = response.text.strip()

                return {
                    "success": True,
                    "answer": answer_text,
                    "context_used": len(context_documents),
                    "confidence": self._assess_confidence(query, context_documents, answer_text),
                    "sources": [doc.get('metadata', {}).get('source', 'Unknown') for doc in context_documents[:3]]
                }
            else:
                return {
                    "success": False,
                    "error": "No response from Gemini API",
                    "answer": "I apologize, but I couldn't generate a response at this time. Please try rephrasing your question."
                }

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "I apologize, but I encountered an error while processing your question. Please try again."
            }

    def _assess_confidence(self, query: str, context_documents: List[Dict[str, Any]], answer: str) -> str:
        """Assess confidence level of the answer"""
        if not context_documents:
            return "Low"

        # Check if answer contains specific financial terms from context
        context_text = " ".join([doc['document'] for doc in context_documents])
        financial_terms = ['revenue', 'profit', 'ratio', 'score', 'analysis', 'financial', 'company']

        term_matches = sum(1 for term in financial_terms if term.lower() in answer.lower())
        context_relevance = min(context_documents[0]['similarity_score'], 1.0) if context_documents else 0

        # Calculate confidence score
        confidence_score = (term_matches / len(financial_terms) * 0.5) + (context_relevance * 0.5)

        if confidence_score > 0.7:
            return "High"
        elif confidence_score > 0.4:
            return "Medium"
        else:
            return "Low"

    async def answer_question(self, query: str, company_symbol: str = None) -> Dict[str, Any]:
        """Main method to answer financial questions with RAG"""
        try:
            # Search for relevant documents
            search_results = self.search_similar_documents(query)

            if not search_results:
                return {
                    "success": False,
                    "answer": "I don't have sufficient information in my knowledge base to answer this question. Please try asking about specific financial metrics, ratios, or analysis methods.",
                    "confidence": "Low",
                    "context_used": 0
                }

            # Generate answer with context
            result = self.generate_answer(query, search_results)

            # Add metadata
            result.update({
                "query": query,
                "company_symbol": company_symbol,
                "timestamp": datetime.now().isoformat(),
                "system": "Q&A RAG System (Agent 7)"
            })

            logger.info(f"Question answered successfully: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Q&A system error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "I apologize, but I encountered an error while processing your question. Please try again later.",
                "confidence": "Low"
            }

    def index_company_data(self, company_symbol: str, company_data: Dict[str, Any]) -> bool:
        """Index company financial data for future queries"""
        try:
            # Create documents from company data
            documents = []

            # Financial ratios document
            if 'financial_ratios' in company_data:
                ratios_text = f"Financial ratios for {company_symbol}:\n"
                for period, ratios in company_data['financial_ratios'].items():
                    ratios_text += f"Period {period}:\n"
                    for ratio_name, ratio_value in ratios.items():
                        ratios_text += f"- {ratio_name.replace('_', ' ').title()}: {ratio_value}\n"
                documents.append({
                    'id': f"{company_symbol}_ratios_{hashlib.md5(ratios_text.encode()).hexdigest()[:8]}",
                    'text': ratios_text,
                    'metadata': {
                        'type': 'financial_ratios',
                        'company': company_symbol,
                        'source': 'financial_analysis'
                    }
                })

            # Risk assessment document
            if 'risk_assessment' in company_data:
                risk_data = company_data['risk_assessment']
                risk_text = f"Risk assessment for {company_symbol}:\n"
                risk_text += f"- Overall Risk Score: {risk_data.get('overall_risk_score', 'N/A')}\n"
                risk_text += f"- Risk Level: {risk_data.get('risk_level', 'N/A')}\n"
                if 'category_scores' in risk_data:
                    risk_text += "- Risk Categories:\n"
                    for category, data in risk_data['category_scores'].items():
                        risk_text += f"  - {category.replace('_', ' ').title()}: {data.get('score', 'N/A')}%\n"

                documents.append({
                    'id': f"{company_symbol}_risk_{hashlib.md5(risk_text.encode()).hexdigest()[:8]}",
                    'text': risk_text,
                    'metadata': {
                        'type': 'risk_assessment',
                        'company': company_symbol,
                        'source': 'risk_analysis'
                    }
                })

            # Forensic analysis document
            if 'forensic_analysis' in company_data:
                forensic_text = f"Forensic analysis for {company_symbol}:\n"
                forensic_data = company_data['forensic_analysis']

                if 'altman_z_score' in forensic_data:
                    altman = forensic_data['altman_z_score']
                    if altman.get('success'):
                        z_score = altman['altman_z_score']
                        forensic_text += f"- Altman Z-Score: {z_score.get('z_score', 'N/A')} ({z_score.get('classification', 'Unknown')})\n"

                if 'beneish_m_score' in forensic_data:
                    beneish = forensic_data['beneish_m_score']
                    if beneish.get('success'):
                        m_score = beneish['beneish_m_score']
                        forensic_text += f"- Beneish M-Score: {m_score.get('m_score', 'N/A')} (Likely Manipulator: {'Yes' if m_score.get('is_likely_manipulator') else 'No'})\n"

                documents.append({
                    'id': f"{company_symbol}_forensic_{hashlib.md5(forensic_text.encode()).hexdigest()[:8]}",
                    'text': forensic_text,
                    'metadata': {
                        'type': 'forensic_analysis',
                        'company': company_symbol,
                        'source': 'forensic_analysis'
                    }
                })

            # Add all documents to vector database
            success_count = 0
            for doc in documents:
                if self.add_document(doc['id'], doc['text'], doc['metadata']):
                    success_count += 1

            logger.info(f"Indexed {success_count}/{len(documents)} documents for {company_symbol}")
            return success_count > 0

        except Exception as e:
            logger.error(f"Failed to index company data for {company_symbol}: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "financial_documents",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}


# Global Q&A system instance
qa_system = QASystem()


async def answer_financial_question(query: str, company_symbol: str = None) -> Dict[str, Any]:
    """Convenience function to answer financial questions"""
    return await qa_system.answer_question(query, company_symbol)


def index_company_for_qa(company_symbol: str, company_data: Dict[str, Any]) -> bool:
    """Convenience function to index company data for Q&A"""
    return qa_system.index_company_data(company_symbol, company_data)


def get_qa_system_status() -> Dict[str, Any]:
    """Get Q&A system status and statistics"""
    return qa_system.get_collection_stats()
