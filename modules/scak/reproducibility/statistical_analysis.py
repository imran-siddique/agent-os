"""
Statistical analysis utilities for SCAK experiments.

Provides functions for:
- Computing p-values (t-tests, Mann-Whitney U)
- Confidence intervals (bootstrap, normal approximation)
- Effect sizes (Cohen's d, Cliff's delta)
- Multiple comparison corrections (Bonferroni, Holm)
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats
from scipy.stats import bootstrap


@dataclass
class StatisticalResult:
    """Results from statistical test."""
    metric_name: str
    treatment_mean: float
    control_mean: float
    treatment_std: float
    control_std: float
    treatment_n: int
    control_n: int
    p_value: float
    confidence_interval_95: Tuple[float, float]
    effect_size: float
    test_type: str
    significant: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "metric_name": self.metric_name,
            "treatment_mean": self.treatment_mean,
            "control_mean": self.control_mean,
            "treatment_std": self.treatment_std,
            "control_std": self.control_std,
            "treatment_n": self.treatment_n,
            "control_n": self.control_n,
            "p_value": self.p_value,
            "confidence_interval_95": list(self.confidence_interval_95),
            "effect_size": self.effect_size,
            "test_type": self.test_type,
            "significant": self.significant,
            "interpretation": self._interpret()
        }
    
    def _interpret(self) -> str:
        """Human-readable interpretation."""
        if not self.significant:
            return f"No significant difference (p={self.p_value:.4f})"
        
        direction = "improvement" if self.treatment_mean > self.control_mean else "degradation"
        effect = "small" if abs(self.effect_size) < 0.5 else "medium" if abs(self.effect_size) < 0.8 else "large"
        
        return f"Significant {direction} (p={self.p_value:.4f}, {effect} effect size)"


def compute_statistics(
    treatment_data: List[float],
    control_data: List[float],
    metric_name: str,
    alpha: float = 0.05
) -> StatisticalResult:
    """
    Compute comprehensive statistics comparing treatment vs. control.
    
    Args:
        treatment_data: Results from treatment group (SCAK)
        control_data: Results from control group (baseline)
        metric_name: Name of metric being compared
        alpha: Significance level (default: 0.05)
    
    Returns:
        StatisticalResult with p-value, CI, effect size
    """
    # Convert to numpy arrays
    treatment = np.array(treatment_data)
    control = np.array(control_data)
    
    # Compute descriptive statistics
    treatment_mean = np.mean(treatment)
    control_mean = np.mean(control)
    treatment_std = np.std(treatment, ddof=1) if len(treatment) > 1 else 0
    control_std = np.std(control, ddof=1) if len(control) > 1 else 0
    
    # Check normality (Shapiro-Wilk test)
    if len(treatment) >= 3 and len(control) >= 3:
        _, p_normal_treatment = stats.shapiro(treatment)
        _, p_normal_control = stats.shapiro(control)
        is_normal = p_normal_treatment > 0.05 and p_normal_control > 0.05
    else:
        is_normal = True  # Assume normal for small samples
    
    # Choose appropriate test
    if is_normal:
        # Two-sample t-test (parametric)
        t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)
        test_type = "two_sample_t_test"
    else:
        # Mann-Whitney U test (non-parametric)
        u_stat, p_value = stats.mannwhitneyu(treatment, control, alternative='two-sided')
        test_type = "mann_whitney_u_test"
    
    # Compute confidence interval (bootstrap)
    ci_lower, ci_upper = bootstrap_confidence_interval(treatment, alpha=alpha)
    
    # Compute effect size (Cohen's d)
    pooled_std = np.sqrt(((len(treatment) - 1) * treatment_std**2 + (len(control) - 1) * control_std**2) / (len(treatment) + len(control) - 2))
    effect_size = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
    
    return StatisticalResult(
        metric_name=metric_name,
        treatment_mean=treatment_mean,
        control_mean=control_mean,
        treatment_std=treatment_std,
        control_std=control_std,
        treatment_n=len(treatment),
        control_n=len(control),
        p_value=p_value,
        confidence_interval_95=(ci_lower, ci_upper),
        effect_size=effect_size,
        test_type=test_type,
        significant=p_value < alpha
    )


def bootstrap_confidence_interval(
    data: np.ndarray,
    alpha: float = 0.05,
    n_bootstrap: int = 10000
) -> Tuple[float, float]:
    """
    Compute bootstrap confidence interval for mean.
    
    Args:
        data: Sample data
        alpha: Significance level (default: 0.05 for 95% CI)
        n_bootstrap: Number of bootstrap samples
    
    Returns:
        (lower_bound, upper_bound)
    """
    if len(data) == 0:
        return (0.0, 0.0)
    
    # Use scipy.stats.bootstrap (available in scipy 1.11+)
    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
    
    if len(data) == 1:
        # No variance for single sample
        return (float(data[0]), float(data[0]))
    
    # Manual bootstrap for compatibility
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))
    
    lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))
    
    return (lower, upper)


def analyze_experiment(
    treatment_results: Dict,
    control_results: Dict,
    metrics: List[str],
    output_file: Optional[str] = None
) -> Dict[str, StatisticalResult]:
    """
    Analyze experiment results comparing treatment vs. control.
    
    Args:
        treatment_results: Dict mapping metric names to list of values
        control_results: Dict mapping metric names to list of values
        metrics: List of metric names to analyze
        output_file: Optional path to save results as JSON
    
    Returns:
        Dict mapping metric names to StatisticalResult
    """
    results = {}
    
    for metric in metrics:
        if metric not in treatment_results or metric not in control_results:
            print(f"Warning: Metric '{metric}' not found in both treatment and control")
            continue
        
        result = compute_statistics(
            treatment_data=treatment_results[metric],
            control_data=control_results[metric],
            metric_name=metric
        )
        
        results[metric] = result
        
        print(f"\n{metric}:")
        print(f"  Treatment: {result.treatment_mean:.3f} ± {result.treatment_std:.3f} (n={result.treatment_n})")
        print(f"  Control:   {result.control_mean:.3f} ± {result.control_std:.3f} (n={result.control_n})")
        print(f"  p-value:   {result.p_value:.4f} ({'significant' if result.significant else 'not significant'})")
        print(f"  95% CI:    [{result.confidence_interval_95[0]:.3f}, {result.confidence_interval_95[1]:.3f}]")
        print(f"  Effect:    Cohen's d = {result.effect_size:.3f}")
    
    # Save to file if specified
    if output_file:
        output_dict = {
            metric: result.to_dict() for metric, result in results.items()
        }
        with open(output_file, 'w') as f:
            json.dump(output_dict, f, indent=2)
        print(f"\nResults saved to {output_file}")
    
    return results


def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """
    Apply Bonferroni correction for multiple comparisons.
    
    Args:
        p_values: List of p-values from multiple tests
        alpha: Family-wise error rate (default: 0.05)
    
    Returns:
        List of booleans indicating significance after correction
    """
    corrected_alpha = alpha / len(p_values)
    return [p < corrected_alpha for p in p_values]


def generate_latex_table(results: Dict[str, StatisticalResult]) -> str:
    """
    Generate LaTeX table from statistical results.
    
    Args:
        results: Dict mapping metric names to StatisticalResult
    
    Returns:
        LaTeX table string
    """
    latex = "\\begin{table}[h]\n"
    latex += "\\centering\n"
    latex += "\\begin{tabular}{l|cc|c|c}\n"
    latex += "\\hline\n"
    latex += "Metric & Treatment & Control & p-value & Effect Size \\\\\n"
    latex += "\\hline\n"
    
    for metric, result in results.items():
        treatment_str = f"{result.treatment_mean:.2f} $\\pm$ {result.treatment_std:.2f}"
        control_str = f"{result.control_mean:.2f} $\\pm$ {result.control_std:.2f}"
        p_str = f"{result.p_value:.4f}{'*' if result.significant else ''}"
        effect_str = f"{result.effect_size:.2f}"
        
        latex += f"{metric} & {treatment_str} & {control_str} & {p_str} & {effect_str} \\\\\n"
    
    latex += "\\hline\n"
    latex += "\\end{tabular}\n"
    latex += "\\caption{Statistical comparison of treatment vs. control. * indicates p<0.05.}\n"
    latex += "\\label{tab:statistical_results}\n"
    latex += "\\end{table}\n"
    
    return latex


if __name__ == "__main__":
    # Example usage
    print("Statistical Analysis Utilities - Example")
    print("=" * 50)
    
    # Simulate GAIA benchmark results
    treatment_results = {
        "detection_rate": [1.0] * 50,  # 100% detection
        "correction_rate": [0.72, 0.68, 0.75, 0.70, 0.74] * 10,  # 72% avg
        "post_patch_success": [0.81, 0.79, 0.85, 0.78, 0.82] * 10  # 81% avg
    }
    
    control_results = {
        "detection_rate": [0.0] * 50,  # 0% detection (no auditor)
        "correction_rate": [0.08, 0.10, 0.06, 0.09, 0.07] * 10,  # 8% avg (random)
        "post_patch_success": [0.08, 0.10, 0.06, 0.09, 0.07] * 10  # 8% avg
    }
    
    # Analyze
    results = analyze_experiment(
        treatment_results=treatment_results,
        control_results=control_results,
        metrics=["detection_rate", "correction_rate", "post_patch_success"],
        output_file="/tmp/statistical_results.json"
    )
    
    # Generate LaTeX table
    print("\n" + "=" * 50)
    print("LaTeX Table:")
    print("=" * 50)
    print(generate_latex_table(results))
