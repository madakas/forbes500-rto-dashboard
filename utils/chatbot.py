"""
RAG Chatbot for America's Top 100 Innovators

Uses semantic search to find relevant companies and Claude to generate responses.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# Simple TF-IDF based search (no external API needed)
from collections import Counter
import re
import math

class CompanySearchEngine:
    """Simple TF-IDF based search engine for company data."""

    def __init__(self, companies: List[Dict[str, Any]]):
        self.companies = companies
        self.documents = []
        self.tfidf_matrix = []
        self.vocabulary = {}
        self._build_index()

    def _create_document(self, company: Dict[str, Any]) -> str:
        """Create a searchable text document from company data."""
        wp = company.get('work_policy', {})
        innovation = company.get('innovation', {})

        # Combine all relevant fields into a single document
        parts = [
            company.get('company', ''),
            company.get('sector', ''),
            company.get('industry_sector', ''),
            company.get('headquarters', ''),
            wp.get('type', ''),
            wp.get('category', ''),
            wp.get('details', ''),
            wp.get('trend_direction', ''),
            company.get('key_quote', ''),
            company.get('notes', ''),
            f"{wp.get('days_required', 0)} days",
            f"rank {innovation.get('overall_rank', '')}",
        ]

        # Add tags based on policy
        days = wp.get('days_required', 0)
        if days == 0:
            parts.append("remote fully remote work from home")
        elif days <= 2:
            parts.append("flexible hybrid remote-friendly")
        elif days == 3:
            parts.append("hybrid three days")
        elif days >= 4:
            parts.append("office-first strict in-office")
        if days == 5:
            parts.append("full office mandatory")

        # Add trend tags
        trend = wp.get('trend_direction', '').lower()
        if 'tightening' in trend:
            parts.append("tightening stricter more office")
        elif 'relaxing' in trend:
            parts.append("relaxing flexible less strict")

        return ' '.join(parts).lower()

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return re.findall(r'\b\w+\b', text.lower())

    def _build_index(self):
        """Build TF-IDF index for all companies."""
        # Create documents
        self.documents = [self._create_document(c) for c in self.companies]

        # Build vocabulary
        all_tokens = set()
        doc_tokens = []
        for doc in self.documents:
            tokens = self._tokenize(doc)
            doc_tokens.append(tokens)
            all_tokens.update(tokens)

        self.vocabulary = {word: i for i, word in enumerate(sorted(all_tokens))}
        vocab_size = len(self.vocabulary)

        # Calculate TF-IDF
        n_docs = len(self.documents)

        # Document frequency
        df = Counter()
        for tokens in doc_tokens:
            df.update(set(tokens))

        # Build TF-IDF matrix
        self.tfidf_matrix = []
        for tokens in doc_tokens:
            tf = Counter(tokens)
            tfidf = np.zeros(vocab_size)
            for word, count in tf.items():
                if word in self.vocabulary:
                    idx = self.vocabulary[word]
                    idf = math.log(n_docs / (1 + df[word]))
                    tfidf[idx] = count * idf
            # Normalize
            norm = np.linalg.norm(tfidf)
            if norm > 0:
                tfidf = tfidf / norm
            self.tfidf_matrix.append(tfidf)

        self.tfidf_matrix = np.array(self.tfidf_matrix)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for companies matching the query."""
        # Tokenize query
        tokens = self._tokenize(query)

        # Create query vector
        vocab_size = len(self.vocabulary)
        query_vec = np.zeros(vocab_size)
        for token in tokens:
            if token in self.vocabulary:
                query_vec[self.vocabulary[token]] = 1

        # Normalize
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        # Calculate similarities
        similarities = np.dot(self.tfidf_matrix, query_vec)

        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append({
                    'company': self.companies[idx],
                    'score': float(similarities[idx])
                })

        return results


def format_company_context(companies: List[Dict[str, Any]]) -> str:
    """Format company data as context for the LLM."""
    context_parts = []

    for result in companies:
        company = result['company']
        wp = company.get('work_policy', {})
        innovation = company.get('innovation', {})

        context = f"""
Company: {company.get('company', 'Unknown')}
Sector: {company.get('sector', 'Unknown')}
Industry: {company.get('industry_sector', 'Unknown')}
Headquarters: {company.get('headquarters', 'Unknown')}
Employees: {company.get('employee_count', 'Unknown'):,}
Innovation Rank: #{innovation.get('overall_rank', 'N/A')}

Work Policy:
- Type: {wp.get('type', 'Unknown')}
- Category: {wp.get('category', 'Unknown')}
- Days in Office: {wp.get('days_required', 'Unknown')}
- Trend: {wp.get('trend_direction', 'Unknown')}
- Effective Date: {wp.get('effective_date', 'Unknown')}
- Details: {wp.get('details', 'No details available')}

Key Quote: "{company.get('key_quote', 'No quote available')}"
"""
        context_parts.append(context.strip())

    return "\n\n---\n\n".join(context_parts)


def create_system_prompt() -> str:
    """Create the system prompt for the chatbot."""
    return """You are a helpful research assistant for the "America's Top 100 Innovators" work policy research platform.

Your role is to help users explore and understand work policies (remote, hybrid, office) across America's most innovative companies.

Guidelines:
- Be factual and cite specific data from the company information provided
- Present information neutrally without judging policies as good or bad
- If asked about companies not in the context, say you don't have information about them
- Keep responses concise but informative
- When comparing companies, use clear structure
- Include relevant quotes from executives when available

You have access to data on work policies including:
- Policy type (remote, hybrid, office-first)
- Days required in office
- Trend direction (tightening, stable, relaxing)
- Executive quotes explaining the rationale
- Innovation rankings (Culture, Process, Product)
- Company metadata (headquarters, employee count, sector)

Always base your answers on the provided company context. If the context doesn't contain relevant information, say so."""


def generate_response_prompt(query: str, context: str) -> str:
    """Generate the user prompt with context."""
    return f"""Based on the following company data, please answer the user's question.

COMPANY DATA:
{context}

USER QUESTION: {query}

Please provide a helpful, factual response based on the data above. If the data doesn't contain information to answer the question, say so."""
