"""
Statistical Analysis Utilities for CMVK Experiments

Provides functions for computing statistical significance, confidence intervals,
and other metrics needed for academic publication.
"""

import json
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class StatisticalResult:
    """Container for statistical test results."""

    test_name: str
    statistic: float
    p_value: float
    significant: bool  # At α=0.05
    effect_size: float | None = None
    confidence_interval: tuple[float, float] | None = None
    sample_sizes: tuple[int, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "test": self.test_name,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "significant_at_0.05": self.significant,
            "effect_size": self.effect_size,
            "confidence_interval": self.confidence_interval,
            "sample_sizes": self.sample_sizes,
        }

    def __str__(self) -> str:
        sig = "✓" if self.significant else "✗"
        ci = f", 95% CI: {self.confidence_interval}" if self.confidence_interval else ""
        return f"{self.test_name}: stat={self.statistic:.4f}, p={self.p_value:.4f} {sig}{ci}"


def mean(values: list[float]) -> float:
    """Calculate arithmetic mean."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: list[float], ddof: int = 1) -> float:
    """Calculate sample variance with Bessel's correction."""
    if len(values) <= ddof:
        return 0.0
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - ddof)


def std(values: list[float], ddof: int = 1) -> float:
    """Calculate sample standard deviation."""
    return math.sqrt(variance(values, ddof))


def standard_error(values: list[float]) -> float:
    """Calculate standard error of the mean."""
    n = len(values)
    if n <= 1:
        return 0.0
    return std(values) / math.sqrt(n)


def confidence_interval(values: list[float], confidence: float = 0.95) -> tuple[float, float]:
    """
    Calculate confidence interval for the mean using t-distribution.

    Args:
        values: Sample values
        confidence: Confidence level (default: 0.95 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    n = len(values)
    if n <= 1:
        m = mean(values)
        return (m, m)

    m = mean(values)
    se = standard_error(values)

    # t-critical value approximation for 95% CI
    # For large n, approaches 1.96 (z-score)
    # For small n, use approximation
    if n > 30:
        t_crit = 1.96
    else:
        # Rough approximation of t-critical for α=0.05, two-tailed
        t_crit = 2.0 + 3.0 / n

    margin = t_crit * se
    return (m - margin, m + margin)


def welch_t_test(sample1: list[float], sample2: list[float]) -> StatisticalResult:
    """
    Perform Welch's t-test for independent samples with unequal variances.

    This is more robust than Student's t-test when variances differ.

    Args:
        sample1: First sample (e.g., baseline results)
        sample2: Second sample (e.g., CMVK results)

    Returns:
        StatisticalResult with test statistics
    """
    n1, n2 = len(sample1), len(sample2)

    if n1 < 2 or n2 < 2:
        return StatisticalResult(
            test_name="Welch's t-test",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            sample_sizes=(n1, n2),
        )

    m1, m2 = mean(sample1), mean(sample2)
    v1, v2 = variance(sample1), variance(sample2)

    # Welch's t-statistic
    se_diff = math.sqrt(v1 / n1 + v2 / n2)
    if se_diff == 0:
        t_stat = 0.0
    else:
        t_stat = (m1 - m2) / se_diff

    # Welch-Satterthwaite degrees of freedom
    if v1 / n1 + v2 / n2 == 0:
        df = n1 + n2 - 2
    else:
        df = ((v1 / n1 + v2 / n2) ** 2) / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))

    # Approximate p-value using normal distribution (for large df)
    # For more accurate p-values, use scipy.stats.t.sf
    p_value = _approx_t_pvalue(abs(t_stat), df) * 2  # Two-tailed

    # Cohen's d effect size
    pooled_std = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    if pooled_std > 0:
        cohens_d = (m2 - m1) / pooled_std  # Positive if sample2 > sample1
    else:
        cohens_d = 0.0

    return StatisticalResult(
        test_name="Welch's t-test",
        statistic=t_stat,
        p_value=p_value,
        significant=p_value < 0.05,
        effect_size=cohens_d,
        sample_sizes=(n1, n2),
    )


def _approx_t_pvalue(t: float, df: float) -> float:
    """
    Approximate one-tailed p-value for t-distribution.
    Uses normal approximation for large df.
    """
    if df > 100:
        # Normal approximation
        return _normal_sf(t)
    else:
        # Rough approximation for smaller df
        # This is imprecise; use scipy for accurate values
        z = t * (1 - 1 / (4 * df)) / math.sqrt(1 + t**2 / (2 * df))
        return _normal_sf(z)


def _normal_sf(x: float) -> float:
    """Survival function (1 - CDF) for standard normal distribution."""
    # Approximation using error function
    return 0.5 * math.erfc(x / math.sqrt(2))


def wilcoxon_signed_rank(sample1: list[float], sample2: list[float]) -> StatisticalResult:
    """
    Perform Wilcoxon signed-rank test for paired samples.

    Non-parametric alternative to paired t-test.

    Args:
        sample1: First paired sample
        sample2: Second paired sample (same length as sample1)

    Returns:
        StatisticalResult with test statistics
    """
    if len(sample1) != len(sample2):
        raise ValueError("Samples must have equal length for paired test")

    n = len(sample1)
    if n < 5:
        return StatisticalResult(
            test_name="Wilcoxon signed-rank",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            sample_sizes=(n, n),
        )

    # Calculate differences
    diffs = [(sample2[i] - sample1[i]) for i in range(n)]

    # Remove zeros
    nonzero_diffs = [(i, d) for i, d in enumerate(diffs) if d != 0]
    if not nonzero_diffs:
        return StatisticalResult(
            test_name="Wilcoxon signed-rank",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            sample_sizes=(n, n),
        )

    # Rank by absolute value
    ranked = sorted(nonzero_diffs, key=lambda x: abs(x[1]))
    ranks = {}
    for rank, (i, d) in enumerate(ranked, 1):
        ranks[i] = rank

    # Calculate W+ (sum of ranks for positive differences)
    w_plus = sum(ranks[i] for i, d in nonzero_diffs if d > 0)
    w_minus = sum(ranks[i] for i, d in nonzero_diffs if d < 0)

    # Test statistic is the smaller of W+ and W-
    w = min(w_plus, w_minus)

    # Normal approximation for p-value
    n_eff = len(nonzero_diffs)
    mean_w = n_eff * (n_eff + 1) / 4
    std_w = math.sqrt(n_eff * (n_eff + 1) * (2 * n_eff + 1) / 24)

    if std_w > 0:
        z = (w - mean_w) / std_w
        p_value = 2 * _normal_sf(abs(z))  # Two-tailed
    else:
        p_value = 1.0

    return StatisticalResult(
        test_name="Wilcoxon signed-rank",
        statistic=w,
        p_value=p_value,
        significant=p_value < 0.05,
        sample_sizes=(n, n),
    )


def bootstrap_ci(
    values: list[float],
    statistic_fn=mean,
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    seed: int | None = None,
) -> tuple[float, float]:
    """
    Calculate bootstrap confidence interval.

    Args:
        values: Sample values
        statistic_fn: Function to compute the statistic (default: mean)
        confidence: Confidence level
        n_bootstrap: Number of bootstrap samples
        seed: Random seed for reproducibility

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    import random

    if seed is not None:
        random.seed(seed)

    n = len(values)
    if n == 0:
        return (0.0, 0.0)

    # Generate bootstrap samples
    bootstrap_stats = []
    for _ in range(n_bootstrap):
        sample = [random.choice(values) for _ in range(n)]
        bootstrap_stats.append(statistic_fn(sample))

    # Sort and get percentiles
    bootstrap_stats.sort()
    alpha = 1 - confidence
    lower_idx = int(alpha / 2 * n_bootstrap)
    upper_idx = int((1 - alpha / 2) * n_bootstrap) - 1

    return (bootstrap_stats[lower_idx], bootstrap_stats[upper_idx])


def compute_pass_rate_stats(
    results: list[dict[str, Any]], method_key: str = "method"
) -> dict[str, dict[str, float]]:
    """
    Compute pass rate statistics from experiment results.

    Args:
        results: List of result dictionaries with 'success' and method_key fields
        method_key: Key for grouping by method

    Returns:
        Dictionary mapping method names to statistics
    """
    from collections import defaultdict

    # Group by method
    by_method = defaultdict(list)
    for r in results:
        method = r.get(method_key, "unknown")
        success = 1.0 if r.get("success", False) else 0.0
        by_method[method].append(success)

    # Compute statistics for each method
    stats = {}
    for method, successes in by_method.items():
        m = mean(successes)
        ci = confidence_interval(successes)
        stats[method] = {
            "pass_rate": m,
            "n": len(successes),
            "std": std(successes),
            "ci_lower": ci[0],
            "ci_upper": ci[1],
        }

    return stats


def compare_methods(
    baseline_results: list[float], cmvk_results: list[float], paired: bool = True
) -> dict[str, StatisticalResult]:
    """
    Compare baseline vs CMVK results with multiple statistical tests.

    Args:
        baseline_results: Results from baseline method (e.g., pass/fail as 0/1)
        cmvk_results: Results from CMVK method
        paired: Whether the samples are paired (same problems)

    Returns:
        Dictionary of test results
    """
    results = {}

    # T-test
    results["welch_t"] = welch_t_test(baseline_results, cmvk_results)

    # Wilcoxon (if paired)
    if paired and len(baseline_results) == len(cmvk_results):
        results["wilcoxon"] = wilcoxon_signed_rank(baseline_results, cmvk_results)

    # Summary statistics
    results["baseline_mean"] = mean(baseline_results)
    results["cmvk_mean"] = mean(cmvk_results)
    results["improvement"] = results["cmvk_mean"] - results["baseline_mean"]
    results["relative_improvement"] = (
        (results["cmvk_mean"] - results["baseline_mean"]) / results["baseline_mean"]
        if results["baseline_mean"] > 0
        else 0.0
    )

    return results


def format_results_table(
    stats: dict[str, dict[str, float]], comparison: dict[str, Any] | None = None
) -> str:
    """
    Format statistics as a markdown table for papers/README.

    Args:
        stats: Statistics by method (from compute_pass_rate_stats)
        comparison: Optional comparison results

    Returns:
        Markdown table string
    """
    lines = ["| Method | Pass@1 | 95% CI | N |", "|--------|--------|--------|---|"]

    for method, s in stats.items():
        pass_rate = f"{s['pass_rate']*100:.1f}%"
        ci = f"[{s['ci_lower']*100:.1f}%, {s['ci_upper']*100:.1f}%]"
        n = str(s["n"])
        lines.append(f"| {method} | {pass_rate} | {ci} | {n} |")

    table = "\n".join(lines)

    if comparison:
        table += "\n\n**Statistical Significance:**\n"
        if "welch_t" in comparison:
            t = comparison["welch_t"]
            table += f"- Welch's t-test: t={t.statistic:.3f}, p={t.p_value:.4f}"
            table += f" ({'significant' if t.significant else 'not significant'} at α=0.05)\n"
        if "improvement" in comparison:
            table += f"- Absolute improvement: {comparison['improvement']*100:.1f}%\n"
            table += f"- Relative improvement: {comparison['relative_improvement']*100:.1f}%\n"

    return table


def load_and_analyze_results(results_path: str) -> dict[str, Any]:
    """
    Load experiment results and perform full statistical analysis.

    Args:
        results_path: Path to results JSON file

    Returns:
        Complete analysis dictionary
    """
    with open(results_path) as f:
        data = json.load(f)

    # Extract baseline and CMVK results
    baseline = [1.0 if r.get("baseline_success", False) else 0.0 for r in data.get("results", [])]
    cmvk = [1.0 if r.get("cmvk_success", False) else 0.0 for r in data.get("results", [])]

    # Compute statistics
    stats = {
        "baseline": {
            "pass_rate": mean(baseline),
            "ci": confidence_interval(baseline),
            "n": len(baseline),
        },
        "cmvk": {"pass_rate": mean(cmvk), "ci": confidence_interval(cmvk), "n": len(cmvk)},
    }

    # Statistical comparison
    comparison = compare_methods(baseline, cmvk, paired=True)

    return {
        "stats": stats,
        "comparison": comparison,
        "table": format_results_table(
            {"Baseline": stats["baseline"], "CMVK": stats["cmvk"]}, comparison
        ),
    }


if __name__ == "__main__":
    # Example usage
    baseline = [0.84, 0.82, 0.85, 0.83, 0.84, 0.86, 0.82, 0.85, 0.83, 0.84]
    cmvk = [0.92, 0.94, 0.91, 0.93, 0.92, 0.95, 0.91, 0.93, 0.92, 0.94]

    print("=" * 60)
    print("Statistical Analysis Example")
    print("=" * 60)

    print(f"\nBaseline: mean={mean(baseline):.3f}, CI={confidence_interval(baseline)}")
    print(f"CMVK: mean={mean(cmvk):.3f}, CI={confidence_interval(cmvk)}")

    comparison = compare_methods(baseline, cmvk)
    print(f"\n{comparison['welch_t']}")
    print(f"{comparison['wilcoxon']}")
    print(
        f"\nImprovement: {comparison['improvement']*100:.1f}% absolute, {comparison['relative_improvement']*100:.1f}% relative"
    )
