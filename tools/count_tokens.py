#!/usr/bin/env python3
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

"""
Token counting utility for AI context management.

Provides rough token count estimates for style guide files to help
manage AI context limits.
"""

import argparse
import re
from pathlib import Path


def estimate_tokens(text):
    """
    Estimate token count using word-based approximation.
    
    This is a rough estimate. Actual token counts vary by model.
    Generally: 1 token ≈ 0.75 words for English text.
    """
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Count words
    words = len(text.split())
    
    # Estimate tokens (words / 0.75)
    estimated_tokens = int(words / 0.75)
    
    return words, estimated_tokens


def analyze_file(file_path):
    """Analyze a single file for token count."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None, f"Error reading file: {e}"
    
    words, tokens = estimate_tokens(content)
    
    return {
        'file': str(file_path),
        'words': words,
        'estimated_tokens': tokens,
        'characters': len(content),
        'lines': len(content.splitlines())
    }, None


def main():
    """Main token counting script."""
    parser = argparse.ArgumentParser(
        description='Count tokens in files for AI context management'
    )
    parser.add_argument('files', nargs='+', help='Files to analyze')
    parser.add_argument('--target', type=int, help='Target token count')
    parser.add_argument('--format', choices=['table', 'json', 'simple'],
                       default='table', help='Output format')
    
    args = parser.parse_args()
    
    results = []
    total_words = 0
    total_tokens = 0
    
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: File {file_path} does not exist")
            continue
        
        result, error = analyze_file(path)
        if error:
            print(f"Error processing {file_path}: {error}")
            continue
        
        results.append(result)
        total_words += result['words']
        total_tokens += result['estimated_tokens']
    
    # Output results
    if args.format == 'json':
        import json
        output = {
            'files': results,
            'totals': {
                'words': total_words,
                'estimated_tokens': total_tokens
            }
        }
        print(json.dumps(output, indent=2))
    
    elif args.format == 'simple':
        for result in results:
            print(f"{result['file']}: {result['estimated_tokens']} tokens")
        print(f"Total: {total_tokens} tokens")
    
    else:  # table format
        print(f"{'File':<40} {'Words':<8} {'Tokens':<8} {'Lines':<6}")
        print("-" * 70)
        
        for result in results:
            filename = Path(result['file']).name
            if len(filename) > 37:
                filename = "..." + filename[-34:]
            
            print(f"{filename:<40} {result['words']:<8} "
                  f"{result['estimated_tokens']:<8} {result['lines']:<6}")
        
        print("-" * 70)
        print(f"{'TOTAL':<40} {total_words:<8} {total_tokens:<8}")
        
        if args.target:
            if total_tokens <= args.target:
                status = "✅ Within target"
            else:
                excess = total_tokens - args.target
                status = f"❌ Exceeds target by {excess} tokens"
            print(f"\nTarget: {args.target} tokens - {status}")


if __name__ == '__main__':
    main()