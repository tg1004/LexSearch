import json

import pytest

from app.services.rag.rag_service import RAGService


class TestParseRelatedQuestions:
    def test_parses_json_array(self):
        text = '["What is anticipatory bail?", "How does NDPS affect bail?", "Bail in murder cases?", "Conditions for regular bail?"]'
        result = RAGService._parse_related_questions(text)
        assert len(result) == 4
        assert "anticipatory bail" in result[0].lower()

    def test_parses_markdown_fenced_json(self):
        text = """```json
["Question one about law?", "Question two about courts?", "Question three about IPC?", "Question four about CrPC?"]
```"""
        result = RAGService._parse_related_questions(text)
        assert len(result) == 4

    def test_parses_bullet_list_fallback(self):
        text = """
1. What are bail grounds in murder?
2. How does Section 438 CrPC apply?
- What is the NDPS bail restriction?
• Can anticipatory bail be cancelled?
"""
        result = RAGService._parse_related_questions(text)
        assert len(result) >= 3

    def test_limits_to_four(self):
        text = json.dumps([f"Question number {i} about Indian law?" for i in range(10)])
        result = RAGService._parse_related_questions(text)
        assert len(result) == 4
