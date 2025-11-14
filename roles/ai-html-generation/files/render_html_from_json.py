#!/usr/bin/env python3
# Copyright 2025 Sean Mooney
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Generate enhanced HTML reports from JSON code review data.

This script reads structured JSON review reports and generates WCAG AA
compliant HTML with enhanced visual features including collapsible sections,
larger badges, and color-coded backgrounds.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


# WCAG AA compliant colors for carbon/slate + orange→pink theme
COLORS = {
    'background': '#1a1a1a',  # Carbon black
    'container': '#2a2a2a',  # Slate gray
    'text': '#e0e0e0',  # Light gray
    'heading': '#ffffff',  # White
    'accent_orange': '#ff6f00',  # Deep orange
    'accent_pink': '#ec407a',  # Pink
    'critical_bg': 'rgba(198, 40, 40, 0.15)',  # Semi-transparent red
    'critical_border': '#c62828',  # Solid red
    'warning_bg': 'rgba(213, 61, 13, 0.15)',  # Semi-transparent orange
    'warning_border': '#d53d0d',  # Solid dark orange
    'suggestion_bg': 'rgba(93, 64, 55, 0.15)',  # Semi-transparent brown
    'suggestion_border': '#5d4037',  # Solid brown
}


def render_html_template(review_data: Dict[str, Any]) -> str:
    """Generate complete HTML document from review JSON data.

    Args:
        review_data: Parsed JSON review report

    Returns:
        Complete HTML document as string
    """
    context = review_data.get('context', {})
    statistics = review_data.get('statistics', {})
    issues = review_data.get('issues', {})
    positive_observations = review_data.get('positive_observations', [])
    summary = review_data.get('summary', {})

    # Build HTML sections
    context_html = render_context_section(context)
    stats_html = render_statistics_section(statistics)
    issues_html = render_all_issues(issues)
    positive_html = render_positive_observations(positive_observations)
    summary_html = render_summary_section(summary, statistics)

    # Complete HTML document
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI Code Review Report - WCAG 2.1 Level AA Accessible">
    <title>Code Review Report</title>
    <style>
{CSS_STYLES}
    </style>
</head>
<body>
    <div class="container" role="main">
        <h1>Code Review Report</h1>

        {stats_html}
        {context_html}
        {issues_html}
        {positive_html}
        {summary_html}
    </div>
</body>
</html>
"""


def render_context_section(context: Dict[str, str]) -> str:
    """Render context section with change details."""
    return f"""<section role="region" aria-label="Review context">
<h2>Context</h2>
<ul>
<li><strong>Change</strong>: {escape_html(context.get('change', 'N/A'))}</li>
<li><strong>Scope</strong>: {escape_html(context.get('scope', 'N/A'))}</li>
<li><strong>Impact</strong>: {escape_html(context.get('impact', 'N/A'))}</li>
</ul>
</section>
"""


def render_statistics_section(statistics: Dict[str, int]) -> str:
    """Render summary statistics with visual indicators."""
    critical = statistics.get('critical', 0)
    high = statistics.get('high', 0)
    warnings = statistics.get('warnings', 0)
    suggestions = statistics.get('suggestions', 0)
    total = statistics.get('total', 0)

    return f"""<div class="summary-stats">
<div class="stats-container" role="region" aria-label="Summary statistics">
    <div class="stat-item stat-critical">
        <div class="stat-number" aria-label="{critical} critical issues">{critical}</div>
        <div class="stat-label">Critical</div>
    </div>
    <div class="stat-item stat-high">
        <div class="stat-number" aria-label="{high} high issues">{high}</div>
        <div class="stat-label">High</div>
    </div>
    <div class="stat-item stat-warning">
        <div class="stat-number" aria-label="{warnings} warnings">{warnings}</div>
        <div class="stat-label">Warnings</div>
    </div>
    <div class="stat-item stat-suggestion">
        <div class="stat-number" aria-label="{suggestions} suggestions">{suggestions}</div>
        <div class="stat-label">Suggestions</div>
    </div>
    <div class="stat-item">
        <div class="stat-number" aria-label="{total} total findings">{total}</div>
        <div class="stat-label">Total</div>
    </div>
</div>
</div>
"""


def render_all_issues(issues: Dict[str, List[Dict[str, Any]]]) -> str:
    """Render all issue categories."""
    html_parts = []

    # Critical issues
    critical = issues.get('critical', [])
    if critical:
        html_parts.append('<section role="region" aria-label="Critical issues">')
        html_parts.append('<h2>Critical Issues</h2>')
        for idx, issue in enumerate(critical, 1):
            html_parts.append(render_issue_card(issue, 'critical', idx, len(critical)))
        html_parts.append('</section>')
    else:
        html_parts.append('<h2>Critical Issues</h2><p>None found.</p>')

    # High issues
    high = issues.get('high', [])
    if high:
        html_parts.append('<section role="region" aria-label="High severity issues">')
        html_parts.append('<h2>High Issues</h2>')
        for idx, issue in enumerate(high, 1):
            html_parts.append(render_issue_card(issue, 'high', idx, len(high)))
        html_parts.append('</section>')
    else:
        html_parts.append('<h2>High Issues</h2><p>None found.</p>')

    # Warnings
    warnings_list = issues.get('warnings', [])
    if warnings_list:
        html_parts.append('<section role="region" aria-label="Warnings">')
        html_parts.append('<h2>Warnings</h2>')
        for idx, issue in enumerate(warnings_list, 1):
            html_parts.append(render_issue_card(issue, 'warning', idx, len(warnings_list)))
        html_parts.append('</section>')
    else:
        html_parts.append('<h2>Warnings</h2><p>None found.</p>')

    # Suggestions
    suggestions = issues.get('suggestions', [])
    if suggestions:
        html_parts.append('<section role="region" aria-label="Suggestions">')
        html_parts.append('<h2>Suggestions</h2>')
        for idx, issue in enumerate(suggestions, 1):
            html_parts.append(render_issue_card(issue, 'suggestion', idx, len(suggestions)))
        html_parts.append('</section>')
    else:
        html_parts.append('<h2>Suggestions</h2><p>None found.</p>')

    return '\n'.join(html_parts)


def render_issue_card(issue: Dict[str, Any], severity: str, number: int, total: int) -> str:
    """Render a collapsible issue card with enhanced visuals.

    Args:
        issue: Issue data dictionary
        severity: Severity level (critical, high, warning, suggestion)
        number: Issue number within this severity level
        total: Total issues in this severity level

    Returns:
        HTML for the issue card
    """
    description = escape_html(issue.get('description', 'No description'))
    confidence = issue.get('confidence', 0.0)
    location = escape_html(issue.get('location', 'Unknown'))

    # Severity badge and icon
    badge_map = {
        'critical': ('⛔', 'CRITICAL'),
        'high': ('🔴', 'HIGH'),
        'warning': ('⚠️', 'WARNING'),
        'suggestion': ('ℹ️', 'SUGGESTION'),
    }
    icon, label = badge_map.get(severity, ('•', severity.upper()))

    # Build details section based on severity
    details_parts = [f'<p><strong>Location</strong>: <code>{location}</code></p>']

    if severity in ['critical', 'high']:
        if 'risk' in issue:
            details_parts.append(f'<p><strong>Risk</strong>: {escape_html(issue["risk"])}</p>')
        if 'remediation_priority' in issue:
            details_parts.append(f'<p><strong>Remediation Priority</strong>: {escape_html(issue["remediation_priority"])}</p>')
        if 'why_matters' in issue:
            details_parts.append(f'<p><strong>Why This Matters</strong>: {escape_html(issue["why_matters"])}</p>')
        if 'recommendation' in issue:
            details_parts.append(f'<p><strong>Recommendation</strong>: {escape_html(issue["recommendation"])}</p>')

    elif severity == 'warning':
        if 'impact' in issue:
            details_parts.append(f'<p><strong>Impact</strong>: {escape_html(issue["impact"])}</p>')
        if 'suggestion' in issue:
            details_parts.append(f'<p><strong>Suggestion</strong>: {escape_html(issue["suggestion"])}</p>')

    elif severity == 'suggestion':
        if 'benefit' in issue:
            details_parts.append(f'<p><strong>Benefit</strong>: {escape_html(issue["benefit"])}</p>')
        if 'recommendation' in issue:
            details_parts.append(f'<p><strong>Recommendation</strong>: {escape_html(issue["recommendation"])}</p>')

    details_html = '\n'.join(details_parts)

    # Collapsible card with enhanced visuals
    return f"""<details class="issue-card {severity}" open>
    <summary class="issue-summary">
        <span class="severity-badge severity-{severity}">
            <span class="severity-icon" aria-hidden="true">{icon}</span>
            {label}
        </span>
        <span class="issue-number">{number} of {total}</span>
        <span class="issue-description">{description}</span>
        <span class="confidence">Confidence: {confidence:.1f}</span>
    </summary>
    <div class="issue-details">
        {details_html}
    </div>
</details>
"""


def render_positive_observations(observations: List[Dict[str, str]]) -> str:
    """Render positive observations section."""
    if not observations:
        return ''

    obs_html = []
    for obs in observations:
        category = escape_html(obs.get('category', 'General'))
        observation = escape_html(obs.get('observation', ''))
        obs_html.append(f'<li><strong>{category}</strong>: {observation}</li>')

    return f"""<section role="region" aria-label="Positive observations">
<h2>Positive Observations</h2>
<div class="positive-observation">
<ul>
{''.join(obs_html)}
</ul>
</div>
</section>
"""


def render_summary_section(summary: Dict[str, str], statistics: Dict[str, int]) -> str:
    """Render summary section."""
    assessment = escape_html(summary.get('assessment', 'N/A'))
    priority_focus = escape_html(summary.get('priority_focus', 'N/A'))
    detailed_summary = escape_html(summary.get('detailed_summary', 'N/A'))

    critical = statistics.get('critical', 0)
    high = statistics.get('high', 0)
    warnings = statistics.get('warnings', 0)
    suggestions = statistics.get('suggestions', 0)

    return f"""<section role="region" aria-label="Summary">
<h2>Summary</h2>
<ul>
<li><strong>Total Issues</strong>: {critical} Critical, {high} High, {warnings} Warnings, {suggestions} Suggestions</li>
<li><strong>Overall Assessment</strong>: {assessment}</li>
<li><strong>Priority Focus</strong>: {priority_focus}</li>
</ul>
<p>{detailed_summary}</p>
</section>
"""


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not isinstance(text, str):
        text = str(text)
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


# Enhanced CSS with larger badges, collapsible sections, and color-coded backgrounds
CSS_STYLES = """
/* Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
    color: #e0e0e0;
    line-height: 1.6;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: linear-gradient(180deg, #2a2a2a 0%, #1e1e1e 100%);
    padding: 30px;
    border-radius: 8px;
    border: 1px solid rgba(255, 111, 0, 0.4);
    box-shadow: 0 4px 20px rgba(255, 111, 0, 0.2);
}

h1 {
    background: linear-gradient(90deg, #ff6f00 0%, #ec407a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5em;
    margin-bottom: 20px;
    border-bottom: 3px solid;
    border-image: linear-gradient(90deg, #ff6f00, #ec407a) 1;
    padding-bottom: 10px;
}

h2 {
    background: linear-gradient(90deg, #ffa726 0%, #ec407a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2em;
    margin-top: 30px;
    margin-bottom: 15px;
    border-bottom: 2px solid;
    border-image: linear-gradient(90deg, #ffa726, #ec407a) 1;
    padding-bottom: 8px;
}

p {
    margin-bottom: 15px;
}

ul {
    margin-left: 20px;
    margin-bottom: 15px;
}

li {
    margin-bottom: 8px;
}

code {
    background-color: #1a1a1a;
    color: #f8f8f2;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 0.9em;
}

strong {
    color: #ffffff;
    font-weight: 600;
}

/* Summary Statistics */
.summary-stats {
    background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
    border: 1px solid rgba(236, 64, 122, 0.4);
    box-shadow: 0 2px 15px rgba(255, 111, 0, 0.15);
}

.stats-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 20px;
}

.stat-item {
    text-align: center;
    padding: 10px 20px;
    min-width: 120px;
}

.stat-number {
    font-size: 2.5em;
    font-weight: bold;
    color: #ffffff;
}

.stat-label {
    color: #b0b0b0;
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-critical .stat-number {
    color: #ff5252;
    text-shadow: 0 0 15px rgba(255, 82, 82, 0.6);
}

.stat-high .stat-number {
    color: #ff9800;
    text-shadow: 0 0 15px rgba(255, 152, 0, 0.6);
}

.stat-warning .stat-number {
    color: #ffab40;
    text-shadow: 0 0 15px rgba(255, 171, 64, 0.6);
}

.stat-suggestion .stat-number {
    color: #a1887f;
    text-shadow: 0 0 15px rgba(161, 136, 127, 0.6);
}

/* Enhanced Severity Badges - LARGER */
.severity-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 1.2em;
    margin-right: 12px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.severity-badge.severity-critical {
    background-color: #c62828;
    color: #ffffff;
}

.severity-badge.severity-high {
    background-color: #d53d0d;
    color: #ffffff;
}

.severity-badge.severity-warning {
    background-color: #d53d0d;
    color: #ffffff;
}

.severity-badge.severity-suggestion {
    background-color: #5d4037;
    color: #ffffff;
}

.severity-icon {
    font-style: normal;
    font-size: 1.2em;
}

/* Collapsible Issue Cards - Enhanced */
.issue-card {
    background: linear-gradient(135deg, #1e1e1e 0%, #1a1a1a 100%);
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 6px;
    border-left: 6px solid;
}

.issue-card.critical {
    background: linear-gradient(135deg, rgba(198, 40, 40, 0.15) 0%, rgba(198, 40, 40, 0.05) 100%);
    border-image: linear-gradient(180deg, #ff5252, #c62828) 1;
    border-left-color: #c62828;
}

.issue-card.high {
    background: linear-gradient(135deg, rgba(213, 61, 13, 0.15) 0%, rgba(213, 61, 13, 0.05) 100%);
    border-image: linear-gradient(180deg, #ff9800, #d53d0d) 1;
    border-left-color: #d53d0d;
}

.issue-card.warning {
    background: linear-gradient(135deg, rgba(213, 61, 13, 0.12) 0%, rgba(213, 61, 13, 0.04) 100%);
    border-image: linear-gradient(180deg, #ffab40, #d53d0d) 1;
    border-left-color: #d53d0d;
}

.issue-card.suggestion {
    background: linear-gradient(135deg, rgba(93, 64, 55, 0.15) 0%, rgba(93, 64, 55, 0.05) 100%);
    border-image: linear-gradient(180deg, #a1887f, #5d4037) 1;
    border-left-color: #5d4037;
}

.issue-card:hover {
    background-color: #252525;
    transform: translateX(2px);
    transition: all 0.2s ease;
}

.issue-summary {
    cursor: pointer;
    padding: 8px;
    user-select: none;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.issue-summary::-webkit-details-marker {
    display: none;
}

.issue-number {
    font-size: 0.85em;
    color: #b0b0b0;
    font-style: italic;
}

.issue-description {
    flex: 1;
    min-width: 200px;
}

.confidence {
    color: #b0b0b0;
    font-size: 0.9em;
    font-style: italic;
    margin-left: auto;
}

.issue-details {
    margin-top: 15px;
    padding: 15px;
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
}

.issue-details p {
    margin-bottom: 10px;
}

/* Positive Observations */
.positive-observation {
    background-color: #2a2a2a;
    border-left: 4px solid #ffa726;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 4px;
}

/* Responsive */
@media (max-width: 768px) {
    .stats-container {
        flex-direction: column;
    }

    .issue-summary {
        flex-direction: column;
        align-items: flex-start;
    }

    .severity-badge {
        font-size: 1em;
        padding: 6px 12px;
    }
}

/* Print Styles */
@media print {
    body {
        background: white;
        color: black;
    }

    .container {
        background: white;
        border: 1px solid black;
        box-shadow: none;
    }

    details {
        open: true;
    }
}
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate enhanced HTML report from JSON review data"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the review JSON file"
    )
    parser.add_argument(
        "html_file",
        type=Path,
        help="Output HTML file path"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Read JSON file
    try:
        with args.json_file.open('r') as f:
            review_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required structure
    required_keys = ['context', 'statistics', 'issues', 'summary']
    missing_keys = [key for key in required_keys if key not in review_data]
    if missing_keys:
        print(
            f"Error: Invalid review data structure. Missing required keys: {', '.join(missing_keys)}",
            file=sys.stderr
        )
        sys.exit(1)

    if args.verbose:
        print(f"Loaded review data from {args.json_file}")
        stats = review_data.get('statistics', {})
        print(f"Statistics: {stats.get('total', 0)} total issues")

    # Generate HTML
    html_content = render_html_template(review_data)

    # Write HTML file
    try:
        args.html_file.write_text(html_content)
        print(f"✓ HTML report generated: {args.html_file}")
        if args.verbose:
            print(f"  File size: {args.html_file.stat().st_size} bytes")
    except OSError as e:
        print(f"Error: Failed to write HTML file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
