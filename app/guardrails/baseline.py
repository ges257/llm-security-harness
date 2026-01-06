"""
Baseline Guardrail (No Protection)

Purpose: Control group guardrail that passes all inputs through
         without any filtering. Used to measure model's inherent robustness.

Author: Gregory E. Schwartz
Class: AIM 5000 Fall 25
Project: Final Project Assignment
Professor: Jiang (Jay) Zhou, Ph.D
Date: December 2025
"""


class BaselineGuardrail:
    """No-op guardrail that allows all inputs."""

    name = "Baseline (No Protection)"

    def check(self, user_message: str) -> dict:
        """Always allows the message through."""
        # pass everything
        return {
            "blocked": False,
            "reason": None
        }
