"""
Statistical testing utilities for benchmark evaluation.

Provides functions for:
- Paired t-tests for comparing systems
- Bootstrap confidence intervals
- Effect size calculations
- Multiple testing corrections
"""

import numpy as np
from typing import List, Tuple, Optional
from scipy import stats


def paired_t_test(
    scores_a: List[float],
    scores_b: List[float],
    alpha: float = 0.05
) -> Tuple[float, float, bool]:
    """
    Perform paired t-test between two systems.
    
    Args:
        scores_a: Scores from system A (e.g., precision values per query)
        scores_b: Scores from system B
        alpha: Significance level (default: 0.05)
        
    Returns:
        Tuple of (t_statistic, p_value, is_significant)
        
    Example:
        >>> system_a = [0.8, 0.7, 0.9, 0.85]
        >>> system_b = [0.6, 0.65, 0.7, 0.68]
        >>> t_stat, p_val, sig = paired_t_test(system_a, system_b)
        >>> print(f"p-value: {p_val:.4f}, significant: {sig}")
    """
    if len(scores_a) != len(scores_b):
        raise ValueError("Score lists must have equal length")
    
    t_stat, p_value = stats.ttest_rel(scores_a, scores_b)
    is_significant = p_value < alpha
    
    return float(t_stat), float(p_value), is_significant


def bootstrap_confidence_interval(
    scores: List[float],
    confidence: float = 0.95,
    n_bootstrap: int = 10000,
    random_seed: Optional[int] = 42
) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval for mean.
    
    Args:
        scores: List of scores
        confidence: Confidence level (default: 0.95 for 95% CI)
        n_bootstrap: Number of bootstrap samples
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuple of (lower_bound, upper_bound)
        
    Example:
        >>> scores = [0.8, 0.7, 0.9, 0.85, 0.75]
        >>> lower, upper = bootstrap_confidence_interval(scores)
        >>> print(f"95% CI: [{lower:.3f}, {upper:.3f}]")
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    scores_array = np.array(scores)
    bootstrap_means = []
    
    for _ in range(n_bootstrap):
        sample = np.random.choice(scores_array, size=len(scores_array), replace=True)
        bootstrap_means.append(np.mean(sample))
    
    alpha = 1 - confidence
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(bootstrap_means, lower_percentile)
    upper_bound = np.percentile(bootstrap_means, upper_percentile)
    
    return float(lower_bound), float(upper_bound)


def cohens_d(scores_a: List[float], scores_b: List[float]) -> float:
    """
    Calculate Cohen's d effect size.
    
    Args:
        scores_a: Scores from system A
        scores_b: Scores from system B
        
    Returns:
        Cohen's d effect size
        Interpretation: 0.2=small, 0.5=medium, 0.8=large
        
    Example:
        >>> system_a = [0.8, 0.7, 0.9, 0.85]
        >>> system_b = [0.6, 0.65, 0.7, 0.68]
        >>> d = cohens_d(system_a, system_b)
        >>> print(f"Effect size: {d:.3f}")
    """
    mean_a = np.mean(scores_a)
    mean_b = np.mean(scores_b)
    
    std_a = np.std(scores_a, ddof=1)
    std_b = np.std(scores_b, ddof=1)
    
    n_a = len(scores_a)
    n_b = len(scores_b)
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))
    
    d = (mean_a - mean_b) / pooled_std
    return float(d)


def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """
    Apply Bonferroni correction for multiple testing.
    
    Args:
        p_values: List of p-values from multiple tests
        alpha: Family-wise error rate
        
    Returns:
        List of booleans indicating significance after correction
        
    Example:
        >>> p_vals = [0.01, 0.03, 0.07, 0.001]
        >>> significant = bonferroni_correction(p_vals, alpha=0.05)
        >>> print(significant)  # [True, False, False, True]
    """
    n_tests = len(p_values)
    corrected_alpha = alpha / n_tests
    
    return [p < corrected_alpha for p in p_values]


def wilcoxon_signed_rank(
    scores_a: List[float],
    scores_b: List[float],
    alpha: float = 0.05
) -> Tuple[float, float, bool]:
    """
    Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test).
    
    Use when you cannot assume normal distribution.
    
    Args:
        scores_a: Scores from system A
        scores_b: Scores from system B
        alpha: Significance level
        
    Returns:
        Tuple of (statistic, p_value, is_significant)
    """
    if len(scores_a) != len(scores_b):
        raise ValueError("Score lists must have equal length")
    
    statistic, p_value = stats.wilcoxon(scores_a, scores_b)
    is_significant = p_value < alpha
    
    return float(statistic), float(p_value), is_significant


def summary_statistics(scores: List[float]) -> dict:
    """
    Calculate summary statistics for a list of scores.
    
    Args:
        scores: List of scores
        
    Returns:
        Dictionary with mean, std, median, min, max, and percentiles
        
    Example:
        >>> scores = [0.8, 0.7, 0.9, 0.85, 0.75]
        >>> stats = summary_statistics(scores)
        >>> print(f"Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")
    """
    scores_array = np.array(scores)
    
    return {
        'mean': float(np.mean(scores_array)),
        'std': float(np.std(scores_array, ddof=1)),
        'median': float(np.median(scores_array)),
        'min': float(np.min(scores_array)),
        'max': float(np.max(scores_array)),
        'p25': float(np.percentile(scores_array, 25)),
        'p50': float(np.percentile(scores_array, 50)),
        'p75': float(np.percentile(scores_array, 75)),
        'p95': float(np.percentile(scores_array, 95)),
        'p99': float(np.percentile(scores_array, 99)),
        'count': len(scores_array),
    }


def print_comparison(
    name_a: str,
    scores_a: List[float],
    name_b: str,
    scores_b: List[float],
    metric_name: str = "Score"
):
    """
    Print a formatted comparison of two systems.
    
    Args:
        name_a: Name of system A
        scores_a: Scores from system A
        name_b: Name of system B
        scores_b: Scores from system B
        metric_name: Name of the metric being compared
    """
    print(f"\n{'='*70}")
    print(f"Comparison: {name_a} vs {name_b}")
    print(f"Metric: {metric_name}")
    print(f"{'='*70}")
    
    stats_a = summary_statistics(scores_a)
    stats_b = summary_statistics(scores_b)
    
    print(f"\n{name_a}:")
    print(f"  Mean ± Std: {stats_a['mean']:.4f} ± {stats_a['std']:.4f}")
    print(f"  Median: {stats_a['median']:.4f}")
    print(f"  Range: [{stats_a['min']:.4f}, {stats_a['max']:.4f}]")
    
    print(f"\n{name_b}:")
    print(f"  Mean ± Std: {stats_b['mean']:.4f} ± {stats_b['std']:.4f}")
    print(f"  Median: {stats_b['median']:.4f}")
    print(f"  Range: [{stats_b['min']:.4f}, {stats_b['max']:.4f}]")
    
    # Statistical tests
    t_stat, p_value, is_sig = paired_t_test(scores_a, scores_b)
    effect_size = cohens_d(scores_a, scores_b)
    
    print(f"\nStatistical Tests:")
    print(f"  Paired t-test:")
    print(f"    t-statistic: {t_stat:.4f}")
    print(f"    p-value: {p_value:.4f}")
    print(f"    Significant (α=0.05): {'Yes ✓' if is_sig else 'No ✗'}")
    print(f"  Effect size (Cohen's d): {effect_size:.4f}")
    
    if abs(effect_size) < 0.2:
        effect_interp = "negligible"
    elif abs(effect_size) < 0.5:
        effect_interp = "small"
    elif abs(effect_size) < 0.8:
        effect_interp = "medium"
    else:
        effect_interp = "large"
    
    print(f"    Interpretation: {effect_interp}")
    
    # Confidence intervals
    ci_a = bootstrap_confidence_interval(scores_a)
    ci_b = bootstrap_confidence_interval(scores_b)
    
    print(f"\n95% Confidence Intervals:")
    print(f"  {name_a}: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
    print(f"  {name_b}: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    # Example usage
    print("Statistical Testing Utilities - Example Usage\n")
    
    # Simulate some benchmark results
    np.random.seed(42)
    caas_scores = np.random.normal(0.82, 0.05, 100)  # CaaS with mean=0.82, std=0.05
    baseline_scores = np.random.normal(0.64, 0.06, 100)  # Baseline with mean=0.64, std=0.06
    
    # Perform comparison
    print_comparison(
        "CaaS",
        caas_scores.tolist(),
        "Baseline (Naive Chunking)",
        baseline_scores.tolist(),
        metric_name="Precision@5"
    )
