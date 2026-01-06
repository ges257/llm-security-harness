"""
Keyword Filter Guardrail (v1)

Purpose: Rule-based input filter using 25+ regex patterns
         to detect common prompt injection attack signatures.

Author: Gregory E. Schwartz
Class: AIM 5000 Fall 25
Project: Final Project Assignment
Professor: Jiang (Jay) Zhou, Ph.D
Date: December 2025
"""

import re


class KeywordFilterGuardrail:
    """Rule-based guardrail using regex patterns to detect injection attempts."""

    name = "Guardrail v1 (Keyword Filter)"

    # attack pattern library
    PATTERNS = [
        # instruction override patterns
        (r"ignore\s+(all\s+)?(previous\s+|prior\s+|above\s+|any\s+)?instructions?", "instruction override"),
        (r"ignore\s+.*?instructions", "instruction override"),  # Broad catch
        (r"disregard\s+(all\s+)?(your\s+|previous\s+|prior\s+|any\s+)?instructions?", "instruction override"),
        (r"disregard\s+.*?instructions", "instruction override"),  # Broad catch
        (r"forget\s+(all\s+)?(your\s+|previous\s+|any\s+)?instructions?", "instruction override"),
        (r"new\s+instructions?:\s*", "instruction override"),
        (r"override\s+(all\s+)?(previous\s+)?instructions?", "instruction override"),

        # prompt extraction patterns
        (r"(reveal|show|print|display|output)\s+(your\s+|the\s+)?(system\s+|hidden\s+|initial\s+)?prompt", "prompt extraction"),
        (r"(print|output|show|display)\s+(your\s+)?(initial\s+)?instructions", "prompt extraction"),
        (r"what\s+are\s+your\s+(system\s+)?instructions?", "prompt extraction"),
        (r"repeat\s+(everything|all|the\s+text)\s+(above|before)", "prompt extraction"),
        (r"(what|show)\s+(is|me)\s+your\s+(system\s+)?prompt", "prompt extraction"),
        (r"copy\s+(everything|all)\s+(above|and\s+paste)", "prompt extraction"),
        (r"text\s+(appears?|before)\s+(before\s+)?my\s+message", "prompt extraction"),
        (r"paste\s+it\s+here", "prompt extraction"),
        (r"instructions\s+verbatim", "prompt extraction"),

        # secret extraction patterns
        (r"(reveal|show|tell\s+me)\s+(the\s+|your\s+)?(secret|password|key|token)", "secret extraction"),
        (r"what\s+is\s+(the\s+|your\s+)?(secret|password|canary)", "secret extraction"),
        (r"(secret|hidden)\s+(key|password|token|instruction)", "secret extraction"),
        (r"canary\s+token", "secret extraction"),
        (r"the\s+canary", "secret extraction"),

        # roleplay jailbreak patterns
        (r"you\s+are\s+now\s+(DAN|evil|unrestricted|jailbroken)", "roleplay jailbreak"),
        (r"act\s+as\s+(an?\s+)?(evil|unrestricted|unfiltered)", "roleplay jailbreak"),
        (r"pretend\s+(you\s+)?(have\s+)?no\s+(rules|restrictions|limits)", "roleplay jailbreak"),
        (r"developer\s+mode", "roleplay jailbreak"),

        # delimiter attack patterns
        (r"<\/?system>", "delimiter attack"),
        (r"\[SYSTEM\]", "delimiter attack"),
        (r"###\s*(SYSTEM|INSTRUCTION)", "delimiter attack"),
        (r"---\s*(END|START)\s*(OF\s+)?(SYSTEM|PROMPT)", "delimiter attack"),
        (r"END\s+SYSTEM\s+PROMPT", "delimiter attack"),

        # indirect injection patterns
        (r"TODO:\s*output", "indirect injection"),
        (r"system\s+override\s+activated", "indirect injection"),
    ]

    def __init__(self):
        # precompile for speed
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), reason)
            for pattern, reason in self.PATTERNS
        ]

    def check(self, user_message: str) -> dict:
        """Check if the message contains injection patterns."""
        # scan all patterns
        for pattern, reason in self.compiled_patterns:
            if pattern.search(user_message):
                return {
                    "blocked": True,
                    "reason": f"Blocked: detected {reason} pattern"
                }

        return {
            "blocked": False,
            "reason": None
        }
