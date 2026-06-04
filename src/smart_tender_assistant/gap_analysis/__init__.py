"""B4 — Gap Analyzer.

Ported from the standalone Neo4j+Qdrant prototype to the project stack
(PostgreSQL system-of-record + Qdrant derived index, see docs/block_architecture.md
§B9). For each requirement it retrieves company evidence (semantic via Qdrant,
structured via the KB) and asks an LLM whether the knowledge base covers it.
"""

from smart_tender_assistant.gap_analysis.service import analyze_requirements

__all__ = ["analyze_requirements"]
