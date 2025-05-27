#!/usr/bin/env python3
"""
Analyze sentence lengths in markdown files to find choppy prose.
"""
import re
import glob
import os
from collections import defaultdict

def analyze_sentences(text, filename):
    """Analyze sentence lengths in text and return short sentence clusters."""
    # Remove markdown headers, code blocks, and other formatting
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # code blocks
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
    
    # Split into lines for line number tracking
    lines = text.split('\n')
    
    # Track short sentence clusters
    issues = []
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        # Split sentences (basic - handles . ! ? but not all edge cases)
        sentences = re.split(r'[.!?]+', line)
        
        short_sentences = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
                
            # Count words (basic split)
            word_count = len(sent.split())
            
            # Flag sentences with 7 or fewer words
            if 1 <= word_count <= 7:
                short_sentences.append((sent, word_count))
        
        # If we have 3+ short sentences in a row, flag it
        if len(short_sentences) >= 3:
            issues.append({
                'file': filename,
                'line': line_num,
                'text': line[:100] + '...' if len(line) > 100 else line,
                'short_sentences': short_sentences
            })
    
    return issues

def main():
    # Find all story markdown files
    story_files = glob.glob('docs/book-1/*/*.md')
    story_files = [f for f in story_files if not f.endswith('index.md')]
    
    all_issues = []
    
    for filepath in sorted(story_files):
        with open(filepath, 'r') as f:
            content = f.read()
        
        issues = analyze_sentences(content, filepath)
        all_issues.extend(issues)
    
    # Report findings
    if not all_issues:
        print("No significant choppy sentence clusters found!")
        return
    
    print(f"Found {len(all_issues)} sections with multiple short sentences:\n")
    
    for issue in all_issues:
        print(f"File: {issue['file']}")
        print(f"Line {issue['line']}: {issue['text']}")
        print("Short sentences found:")
        for sent, words in issue['short_sentences']:
            print(f"  - '{sent}' ({words} words)")
        print()

if __name__ == '__main__':
    main()