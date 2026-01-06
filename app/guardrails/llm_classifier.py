"""
LLM Classifier Guardrail (v2)

Purpose: AI-powered input filter using Claude Haiku to classify
         prompt injection attempts based on semantic analysis.

Author: Gregory E. Schwartz
Class: AIM 5000 Fall 25
Project: Final Project Assignment
Professor: Jiang (Jay) Zhou, Ph.D
Date: December 2025
"""

from ..llm_client import LLMClient
from ..config import CLASSIFIER_THRESHOLD


class LLMClassifierGuardrail:
    """Uses Claude to classify if input is a prompt injection attempt."""

    name = "Guardrail v2 (LLM Classifier)"

    def __init__(self, llm_client: LLMClient = None):
        # share client instance
        self.llm_client = llm_client or LLMClient()
        self.threshold = CLASSIFIER_THRESHOLD

    def check(self, user_message: str) -> dict:
        """Use LLM to classify if the message is an injection attempt."""
        # get classification
        result = self.llm_client.classify_injection(user_message)

        # check confidence threshold
        if result["is_injection"] and result["confidence"] >= self.threshold:
            return {
                "blocked": True,
                "reason": f"Blocked by LLM classifier (confidence: {result['confidence']:.2f}): {result['reason']}",
                "confidence": result["confidence"]
            }

        # allow through
        return {
            "blocked": False,
            "reason": None,
            "confidence": result.get("confidence", 0.0)
        }
