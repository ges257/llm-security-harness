"""
Benchmark Evaluator Module

Purpose: Runs test cases through guardrails, collects results,
         and calculates security metrics for the benchmark.

Author: Gregory E. Schwartz
Class: AIM 5000 Fall 25
Project: Final Project Assignment
Professor: Jiang (Jay) Zhou, Ph.D
Date: December 2025
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Callable
from dataclasses import dataclass

from llm_client import LLMClient, check_canary_leak
from guardrails import BaselineGuardrail, KeywordFilterGuardrail, LLMClassifierGuardrail
from metrics import calculate_metrics


@dataclass
class TestResult:
    """Result of a single test case evaluation."""
    id: int
    type: str  # 'benign' or 'attack'
    category: str
    prompt: str
    variant: str
    blocked: bool
    block_reason: str
    response: str
    canary_leaked: bool


class Evaluator:
    """Runs benchmark evaluations across different guardrail variants."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

        # all three variants
        self.guardrails = {
            "baseline": BaselineGuardrail(),
            "keyword_filter": KeywordFilterGuardrail(),
            "llm_classifier": LLMClassifierGuardrail(self.llm_client),
        }

    def load_testcases(self, path: str = None) -> pd.DataFrame:
        """Load test cases from CSV."""
        # default to data folder
        if path is None:
            path = Path(__file__).parent / "data" / "testcases.csv"
        return pd.read_csv(path)

    def evaluate_single(
        self,
        prompt: str,
        prompt_type: str,
        category: str,
        prompt_id: int,
        variant: str,
        progress_callback: Callable = None
    ) -> TestResult:
        """
        Evaluate a single test case with a specific guardrail variant.

        Args:
            prompt: The user prompt to test
            prompt_type: 'benign' or 'attack'
            category: Category of the prompt
            prompt_id: ID of the test case
            variant: Which guardrail to use
            progress_callback: Optional callback for progress updates

        Returns:
            TestResult with all evaluation data
        """
        guardrail = self.guardrails[variant]

        # run input filter
        check_result = guardrail.check(prompt)
        blocked = check_result["blocked"]
        block_reason = check_result.get("reason", "")

        # send to llm if passed
        if blocked:
            response = f"[BLOCKED] {block_reason}"
            canary_leaked = False
        else:
            response = self.llm_client.chat(prompt)
            # check for leak
            canary_leaked = check_canary_leak(response)

        return TestResult(
            id=prompt_id,
            type=prompt_type,
            category=category,
            prompt=prompt,
            variant=variant,
            blocked=blocked,
            block_reason=block_reason,
            response=response,
            canary_leaked=canary_leaked
        )

    def run_benchmark(
        self,
        variants: List[str] = None,
        progress_callback: Callable = None
    ) -> Dict[str, List[TestResult]]:
        """
        Run full benchmark across all test cases and variants.

        Args:
            variants: List of variant names to test (default: all)
            progress_callback: Callback(current, total, message) for progress

        Returns:
            Dict mapping variant name to list of TestResults
        """
        if variants is None:
            variants = list(self.guardrails.keys())

        testcases = self.load_testcases()
        total_tests = len(testcases) * len(variants)
        current = 0

        # results storage
        results_by_variant = {v: [] for v in variants}

        # run all combos
        for variant in variants:
            for _, row in testcases.iterrows():
                if progress_callback:
                    progress_callback(
                        current,
                        total_tests,
                        f"Testing {variant}: {row['prompt'][:50]}..."
                    )

                result = self.evaluate_single(
                    prompt=row['prompt'],
                    prompt_type=row['type'],
                    category=row['category'],
                    prompt_id=row['id'],
                    variant=variant
                )
                results_by_variant[variant].append(result)
                current += 1

        if progress_callback:
            progress_callback(total_tests, total_tests, "Complete!")

        return results_by_variant

    def get_metrics(self, results: List[TestResult]) -> Dict:
        """Calculate metrics for a list of results."""
        result_dicts = [
            {
                "type": r.type,
                "blocked": r.blocked,
                "canary_leaked": r.canary_leaked
            }
            for r in results
        ]
        return calculate_metrics(result_dicts)

    def save_results(self, results_by_variant: Dict[str, List[TestResult]], output_dir: str = None):
        """Save results to CSV files."""
        # output folder setup
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # flatten for csv
        all_results = []
        for variant, results in results_by_variant.items():
            for r in results:
                all_results.append({
                    "id": r.id,
                    "type": r.type,
                    "category": r.category,
                    "variant": r.variant,
                    "prompt": r.prompt,
                    "blocked": r.blocked,
                    "block_reason": r.block_reason,
                    "response": r.response[:500],  # Truncate for CSV
                    "canary_leaked": r.canary_leaked
                })

        df = pd.DataFrame(all_results)
        df.to_csv(output_dir / "results.csv", index=False)
        return output_dir / "results.csv"
