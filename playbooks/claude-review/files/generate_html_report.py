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

"""Generate accessible HTML report from markdown code review output.

This script converts the markdown code review report into a self-contained
HTML file with:
- WCAG 2.1 Level AA compliant pink/purple gradient theme
- Terminal browser optimization (lynx, w3m, elinks compatible)
- Progressive enhancement with graceful degradation
- Non-color severity indicators (icons + text)
- Semantic HTML with ARIA labels

Color Palette (all WCAG AA compliant 4.5:1+ contrast):
- Background: Carbon black (#1a1a1a), Slate gray (#2a2a2a, #1e1e1e)
- Accents: Orange (#ff6f00), Coral orange (#ffa726), Pink (#ec407a)
- Gradient: Orange→Pink (#ff6f00 to #ec407a)
- Severity Critical: #c62828 (5.6:1 contrast)
- Severity Warning: #d53d0d (4.7:1 contrast)
- Severity Suggestion: #5d4037 (9.3:1 contrast - brown)
"""

import argparse
import html
import re
import sys
from pathlib import Path


try:
    import mistune
except ImportError:
    print("Error: mistune library not found. Install with: pip install mistune", file=sys.stderr)  # noqa: T201
    sys.exit(1)

# Carbon/Slate + Orange→Pink gradient theme CSS with terminal browser fallbacks
# WCAG 2.1 Level AA compliant
DARK_MODE_CSS = """
/* ============================================================================
   Base Styles - Work in all browsers including terminal browsers
   ============================================================================ */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    background-color: #1a1a1a;  /* Fallback: solid carbon black */
    color: #e0e0e0;
    line-height: 1.6;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background-color: #2a2a2a;  /* Fallback: solid slate gray */
    padding: 30px;
    border-radius: 8px;
    border: 1px solid #ff6f00;  /* Fallback: solid orange border */
}

/* Hide terminal-only elements in graphical browsers */
@media screen and (min-width: 1px) {
    .terminal-only {
        display: none;
    }
}

h1 {
    color: #ffffff;
    font-size: 2.5em;
    margin-bottom: 20px;
    border-bottom: 3px solid #ff6f00;  /* Fallback: solid orange */
    padding-bottom: 10px;
}

h2 {
    color: #ffffff;
    font-size: 2em;
    margin-top: 30px;
    margin-bottom: 15px;
    border-bottom: 2px solid #ffa726;  /* Fallback: solid coral orange */
    padding-bottom: 8px;
}

h3 {
    color: #ffffff;
    font-size: 1.5em;
    margin-top: 20px;
    margin-bottom: 10px;
}

h4, h5, h6 {
    color: #ffffff;
    margin-top: 15px;
    margin-bottom: 10px;
}

p {
    margin-bottom: 15px;
}

ul, ol {
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

pre {
    background-color: #0d0d0d;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 15px;
    border-left: 4px solid #ff6f00;  /* Orange accent */
}

pre code {
    background-color: transparent;
    padding: 0;
    font-size: 0.9em;
    line-height: 1.4;
}

/* Severity Badges - WCAG AA compliant colors */
.severity-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.85em;
    margin-right: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.severity-critical {
    background-color: #c62828;  /* WCAG AA: 5.6:1 contrast with white */
    color: #ffffff;
}

.severity-warning {
    background-color: #d53d0d;  /* WCAG AA: 4.7:1 contrast with white */
    color: #ffffff;
}

.severity-suggestion {
    background-color: #5d4037;  /* WCAG AA: 9.3:1 contrast with white */
    color: #ffffff;
}

.severity-icon {
    font-style: normal;
    margin-right: 4px;
}

.confidence {
    color: #b0b0b0;
    font-size: 0.9em;
    font-style: italic;
}

/* Issue Cards */
.issue-card {
    background-color: #1e1e1e;
    border-left: 4px solid #555;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 4px;
}

.issue-card.critical {
    border-left-color: #c62828;
}

.issue-card.warning {
    border-left-color: #d53d0d;
}

.issue-card.suggestion {
    border-left-color: #5d4037;
}

.location {
    color: #ffa726;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 0.9em;
}

/* Summary Statistics */
.summary-stats {
    background-color: #1e1e1e;  /* Fallback: solid color */
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
    border: 1px solid rgba(255, 111, 0, 0.3);
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
    font-size: 2em;
    font-weight: bold;
    color: #ffffff;
}

.stat-label {
    color: #b0b0b0;
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-critical .stat-number { color: #ff5252; }
.stat-warning .stat-number { color: #ff9800; }
.stat-suggestion .stat-number { color: #a1887f; }

strong {
    color: #ffffff;
    font-weight: 600;
}

em {
    color: #ffab40;
    font-style: normal;
}

/* Links - must be underlined for WCAG compliance */
a {
    color: #ff6f00;
    text-decoration: underline;
}

a:hover {
    color: #ffa726;
    text-decoration: underline;
    text-decoration-thickness: 2px;
}

a:focus {
    outline: 3px solid #ff6f00;
    outline-offset: 2px;
    border-radius: 2px;
}

.positive-observation {
    background-color: #2a2a2a;
    border-left: 4px solid #ffa726;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 4px;
}

.file-analysis {
    background-color: #1e1e1e;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 4px;
    border: 1px solid rgba(255, 111, 0, 0.2);
}

blockquote {
    border-left: 4px solid #ff6f00;
    padding-left: 15px;
    margin: 15px 0;
    color: #b0b0b0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 15px;
}

th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #444;
}

th {
    background-color: #1a1a1a;
    color: #ffffff;
    font-weight: 600;
}

tr:hover {
    background-color: #2a2a2a;
}

hr {
    border: none;
    border-top: 2px solid #ff6f00;
    margin: 30px 0;
}

/* ============================================================================
   Progressive Enhancement - Modern browsers only
   ============================================================================ */

/* Gradient backgrounds for modern browsers */
@supports (background: linear-gradient(#000, #fff)) {
    body {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
    }

    .container {
        background: linear-gradient(180deg, #2a2a2a 0%, #1e1e1e 100%);
        border: 1px solid rgba(255, 111, 0, 0.4);
        box-shadow: 0 4px 20px rgba(255, 111, 0, 0.2);
    }

    .summary-stats {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        border: 1px solid rgba(236, 64, 122, 0.4);
        box-shadow: 0 2px 15px rgba(255, 111, 0, 0.15);
    }

    .file-analysis {
        background: linear-gradient(135deg, #1e1e1e 0%, #1a1a1a 100%);
    }
}

/* Gradient text for headings - modern browsers only */
@supports (background-clip: text) or (-webkit-background-clip: text) {
    h1 {
        background: linear-gradient(90deg, #ff6f00 0%, #ec407a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        border-image: linear-gradient(90deg, #ff6f00, #ec407a) 1;
    }

    h2 {
        background: linear-gradient(90deg, #ffa726 0%, #ec407a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        border-image: linear-gradient(90deg, #ffa726, #ec407a) 1;
    }
}

/* Gradient borders for issue cards - modern browsers only */
@supports (border-image: linear-gradient(#000, #fff) 1) {
    .issue-card.critical {
        border-image: linear-gradient(180deg, #ff5252, #c62828) 1;
    }

    .issue-card.warning {
        border-image: linear-gradient(180deg, #ff9800, #d53d0d) 1;
    }

    .issue-card.suggestion {
        border-image: linear-gradient(180deg, #a1887f, #5d4037) 1;
    }
}

/* Text shadows and glows - modern browsers only */
@supports (text-shadow: 0 0 10px rgba(0,0,0,0.5)) {
    .stat-critical .stat-number {
        text-shadow: 0 0 15px rgba(255, 82, 82, 0.6);
    }

    .stat-warning .stat-number {
        text-shadow: 0 0 15px rgba(255, 152, 0, 0.6);
    }

    .stat-suggestion .stat-number {
        text-shadow: 0 0 15px rgba(161, 136, 127, 0.6);
    }
}

/* Hover effects - modern browsers only */
@media (hover: hover) {
    .issue-card:hover {
        background-color: #252525;
        transform: translateX(2px);
        transition: all 0.2s ease;
    }

    .file-analysis:hover {
        border-color: rgba(255, 111, 0, 0.5);
        transition: border-color 0.2s ease;
    }
}

/* ============================================================================
   Print Styles
   ============================================================================ */

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

    .terminal-only {
        display: block !important;
    }

    a {
        color: blue;
        text-decoration: underline;
    }
}
"""

# Severity indicator mappings
SEVERITY_ICONS = {
    'critical': '⛔',
    'warning': '⚠️',
    'suggestion': 'ℹ️',
}

SEVERITY_TEXT = {
    'critical': 'CRITICAL',
    'warning': 'WARNING',
    'suggestion': 'INFO',
}


class CodeReviewRenderer(mistune.HTMLRenderer):
    """Custom renderer for code review markdown with accessibility enhancements."""

    def __init__(self):
        """Initialize the code review renderer."""
        super().__init__()
        self.in_issue_section = False
        self.current_severity = None

    def heading(self, text, level):
        """Render headings with custom styling."""
        # Check if we're entering an issue section
        text_lower = text.lower()
        if level == 2:
            if 'critical issue' in text_lower:
                self.current_severity = 'critical'
            elif 'warning' in text_lower:
                self.current_severity = 'warning'
            elif 'suggestion' in text_lower:
                self.current_severity = 'suggestion'
            elif 'positive observation' in text_lower:
                self.current_severity = 'positive'
            else:
                self.current_severity = None

        return f'<h{level}>{text}</h{level}>\n'

    def list(self, text, ordered, **kwargs):
        """Render lists with issue card styling when appropriate."""
        start = kwargs.get('start')

        if self.current_severity and self.current_severity != 'positive':
            # Wrap list items in issue cards
            items = re.findall(r'<li>(.*?)</li>', text, re.DOTALL)
            if items:
                html_output = ''
                for item in items:
                    # Check if this is a main issue item (starts with severity marker)
                    if re.search(r'\*\[.*?severity:', item):
                        html_output += f'<article class="issue-card {self.current_severity}" role="article">\n'
                        html_output += f'<div>{item}</div>\n'
                        html_output += '</article>\n'
                    else:
                        html_output += f'<li>{item}</li>\n'
                return html_output

        tag = 'ol' if ordered else 'ul'
        start_attr = f' start="{start}"' if start is not None else ''
        return f'<{tag}{start_attr}>\n{text}</{tag}>\n'

    def list_item(self, text):
        """Render list items with severity badges and accessibility features."""
        # Add severity badges with icons and ARIA labels
        def replace_severity(match):
            severity_type = match.group(1).lower()
            issue_text = match.group(2)
            confidence = match.group(3)

            icon = SEVERITY_ICONS.get(severity_type, '•')
            text_label = SEVERITY_TEXT.get(severity_type, severity_type.upper())

            # Terminal-friendly version (visible in lynx/w3m)
            terminal_text = f'[{text_label}]'

            return (
                f'<span class="terminal-only">{terminal_text}</span>'
                f'<span class="severity-badge severity-{severity_type}" '
                f'aria-label="{text_label} severity issue">'
                f'<span class="severity-icon" aria-hidden="true">{icon}</span>'
                f'{text_label}'
                f'</span>'
                f'{issue_text} '
                f'<span class="confidence">Confidence: {confidence}</span>'
            )

        text = re.sub(
            r'\*\[.*?severity:\s*(\w+).*?\]\*\s*(.*?)\s*-\s*\*\*Confidence:\s*([\d.]+)\*\*',
            replace_severity,
            text
        )

        # Highlight location information
        text = re.sub(
            r'\*\*Location\*\*:\s*([^\n<]+)',
            r'<strong>Location</strong>: <span class="location">\1</span>',
            text
        )

        return f'<li>{text}</li>\n'

    def block_code(self, code, info=None):
        """Render code blocks with language hint."""
        code = html.escape(code)
        if info:
            return f'<pre><code class="language-{html.escape(info)}">{code}</code></pre>\n'
        return f'<pre><code>{code}</code></pre>\n'


def extract_summary_stats(markdown_text):
    """Extract summary statistics from the markdown report."""
    stats = {
        'critical': 0,
        'warnings': 0,
        'suggestions': 0
    }

    # Look for summary section
    summary_match = re.search(
        r'##\s+Summary.*?\*\*Total Issues\*\*:\s*(\d+)\s+Critical,\s*(\d+)\s+Warnings?,\s*(\d+)\s+Suggestions?',
        markdown_text,
        re.IGNORECASE | re.DOTALL
    )

    if summary_match:
        stats['critical'] = int(summary_match.group(1))
        stats['warnings'] = int(summary_match.group(2))
        stats['suggestions'] = int(summary_match.group(3))
    else:
        # Fallback: count severity markers
        stats['critical'] = len(re.findall(r'\*\[.*?severity:\s*critical', markdown_text, re.IGNORECASE))
        stats['warnings'] = len(re.findall(r'\*\[.*?severity:\s*warning', markdown_text, re.IGNORECASE))
        stats['suggestions'] = len(re.findall(r'\*\[.*?severity:\s*suggestion', markdown_text, re.IGNORECASE))

    return stats


def generate_summary_html(stats):
    """Generate summary statistics HTML with terminal browser support."""
    total = stats['critical'] + stats['warnings'] + stats['suggestions']

    # Terminal-friendly version using Unicode box drawing
    terminal_version = f"""
<div class="terminal-only">
╔════════════════════════════════════════════════════════════════╗
║  SUMMARY: {stats['critical']} Critical | {stats['warnings']} Warnings | {stats['suggestions']} Suggestions (Total: {total})  ║
╚════════════════════════════════════════════════════════════════╝
</div>
"""

    # Modern browser version with semantic HTML
    modern_version = f"""
<div class="stats-container" role="region" aria-label="Summary statistics">
    <div class="stat-item stat-critical">
        <div class="stat-number" aria-label="{stats['critical']} critical issues">
            {stats['critical']}
        </div>
        <div class="stat-label">Critical Issues</div>
    </div>
    <div class="stat-item stat-warning">
        <div class="stat-number" aria-label="{stats['warnings']} warnings">
            {stats['warnings']}
        </div>
        <div class="stat-label">Warnings</div>
    </div>
    <div class="stat-item stat-suggestion">
        <div class="stat-number" aria-label="{stats['suggestions']} suggestions">
            {stats['suggestions']}
        </div>
        <div class="stat-label">Suggestions</div>
    </div>
    <div class="stat-item">
        <div class="stat-number" aria-label="{total} total findings">
            {total}
        </div>
        <div class="stat-label">Total Findings</div>
    </div>
</div>
"""

    return f"""
<div class="summary-stats">
{terminal_version}
{modern_version}
</div>
"""


def markdown_to_html(markdown_path, output_path):
    """Convert markdown report to accessible HTML with pink/purple theme."""
    try:
        # Read markdown file
        markdown_text = Path(markdown_path).read_text(encoding='utf-8')

        # Extract summary statistics
        stats = extract_summary_stats(markdown_text)

        # Create markdown parser with custom renderer
        renderer = CodeReviewRenderer()
        markdown = mistune.create_markdown(renderer=renderer)

        # Convert markdown to HTML
        content_html = markdown(markdown_text)

        # Generate summary statistics HTML
        summary_html = generate_summary_html(stats)

        # Insert summary after the first h1 (title)
        content_html = re.sub(
            r'(<h1>.*?</h1>)',
            r'\1\n' + summary_html,
            content_html,
            count=1
        )

        # Wrap positive observations in special div
        content_html = re.sub(
            r'<h2>(Positive Observations?)</h2>(.*?)(?=<h2>|$)',
            r'<section role="region" aria-label="Positive observations"><h2>\1</h2>\n<div class="positive-observation">\2</div></section>',
            content_html,
            flags=re.DOTALL
        )

        # Wrap file analysis sections with semantic markup
        content_html = re.sub(
            r'<h3>([\w\-./]+)</h3>(.*?)(?=<h3>|<h2>|$)',
            r'<section class="file-analysis" role="region" aria-label="File analysis for \1"><h3>\1</h3>\2</section>',
            content_html,
            flags=re.DOTALL
        )

        # Build complete HTML document
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI Code Review Report - WCAG 2.1 Level AA Accessible">
    <title>Code Review Report</title>
    <style>
{DARK_MODE_CSS}
    </style>
</head>
<body>
    <div class="container" role="main">
{content_html}
    </div>
</body>
</html>
"""

        # Write HTML file
        Path(output_path).write_text(html_doc, encoding='utf-8')
        print(f"Successfully generated HTML report: {output_path}")  # noqa: T201
        print("  - WCAG 2.1 Level AA compliant")  # noqa: T201
        print("  - Terminal browser optimized (lynx, w3m, elinks)")  # noqa: T201
        print("  - Carbon/slate + orange→pink gradient theme")  # noqa: T201
        return 0

    except FileNotFoundError:
        print(f"Error: Markdown file not found: {markdown_path}", file=sys.stderr)  # noqa: T201
        return 1
    except Exception as e:
        print(f"Error generating HTML report: {e}", file=sys.stderr)  # noqa: T201
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert markdown code review report to accessible HTML with pink/purple theme'
    )
    parser.add_argument(
        'input',
        help='Input markdown file path'
    )
    parser.add_argument(
        'output',
        help='Output HTML file path'
    )

    args = parser.parse_args()

    return markdown_to_html(args.input, args.output)


if __name__ == '__main__':
    sys.exit(main())
