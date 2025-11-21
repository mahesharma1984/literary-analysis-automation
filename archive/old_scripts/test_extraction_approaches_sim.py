#!/usr/bin/env python3
"""
SIMPLIFIED EXTRACTION COMPARISON TEST

Tests token usage for different extraction approaches without running into JSON issues.

This version simulates the approaches and measures theoretical token counts
rather than making actual API calls (which are prone to JSON formatting issues).
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import PyPDF2

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def extract_text_from_pdf(pdf_path):
    """Extract full text from PDF"""
    print_info(f"Extracting text from: {pdf_path}")
    
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print_info(f"Total pages: {total_pages}")
            
            for i, page in enumerate(pdf_reader.pages):
                if i % 50 == 0:
                    print(f"  Processing page {i+1}/{total_pages}...")
                text += page.extract_text()
        
        word_count = len(text.split())
        print_success(f"Extracted {word_count:,} words")
        return text
    
    except Exception as e:
        print(f"{Colors.RED}Error extracting PDF: {e}{Colors.END}")
        return None

def count_tokens(text):
    """Estimate token count (1 token ≈ 0.75 words)"""
    words = len(text.split())
    tokens = int(words / 0.75)
    return tokens

def estimate_cost(input_tokens, output_tokens):
    """Estimate API cost"""
    input_cost = input_tokens * 0.000003  # $3 per 1M tokens
    output_cost = output_tokens * 0.000015  # $15 per 1M tokens
    return input_cost + output_cost

def simulate_approach(approach_name, book_word_count, extract_words_per_section, protocol_words):
    """Simulate an extraction approach and calculate token usage"""
    
    print_header(f"SIMULATING: {approach_name}")
    
    # Stage 1: Extract passages
    # Input: partial book text (first 50k words) + instructions
    stage1_input_words = min(50000, book_word_count) + 200  # book text + instructions
    stage1_input_tokens = count_tokens(" ".join(["word"] * stage1_input_words))
    
    # Output: 5 extracts
    stage1_output_words = extract_words_per_section * 5
    stage1_output_tokens = count_tokens(" ".join(["word"] * stage1_output_words))
    
    print(f"Stage 1 (Extract Passages):")
    print(f"  Input: {stage1_input_words:,} words → {stage1_input_tokens:,} tokens")
    print(f"  Output: {stage1_output_words:,} words ({extract_words_per_section} per section) → {stage1_output_tokens:,} tokens")
    
    # Stage 2A: Macro tagging
    # Input: protocol + 5 extracts + instructions
    stage2a_input_words = protocol_words + stage1_output_words + 300
    stage2a_input_tokens = count_tokens(" ".join(["word"] * stage2a_input_words))
    
    # Output: JSON with macro variables
    stage2a_output_tokens = 500  # typical macro tag output
    
    print(f"\nStage 2A (Macro Tagging):")
    print(f"  Input: {stage2a_input_words:,} words → {stage2a_input_tokens:,} tokens")
    print(f"    - Protocol text: {protocol_words:,} words")
    print(f"    - Extracts: {stage1_output_words:,} words")
    print(f"  Output: ~{stage2a_output_tokens:,} tokens")
    
    # Totals
    total_input_tokens = stage1_input_tokens + stage2a_input_tokens
    total_output_tokens = stage1_output_tokens + stage2a_output_tokens
    total_cost = estimate_cost(total_input_tokens, total_output_tokens)
    
    rate_limit_safe = stage2a_input_tokens < 30000
    
    print(f"\n{Colors.CYAN}TOTALS:{Colors.END}")
    print(f"  Total input tokens: {total_input_tokens:,}")
    print(f"  Total output tokens: {total_output_tokens:,}")
    print(f"  Estimated cost: ${total_cost:.4f}")
    print(f"  Stage 2A under rate limit: {rate_limit_safe} {'✓' if rate_limit_safe else '✗'}")
    
    return {
        "stage1_input_tokens": stage1_input_tokens,
        "stage1_output_tokens": stage1_output_tokens,
        "stage2a_input_tokens": stage2a_input_tokens,
        "stage2a_output_tokens": stage2a_output_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "extract_words": stage1_output_words,
        "protocol_words": protocol_words,
        "estimated_cost": total_cost,
        "rate_limit_safe": rate_limit_safe
    }

def run_comparison(pdf_path):
    """Run comparison simulation"""
    
    print_header("EXTRACTION APPROACH COMPARISON (SIMULATION)")
    print(f"Testing file: {pdf_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract text to get book size
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        return 1
    
    book_word_count = len(full_text.split())
    print_info(f"Book size: {book_word_count:,} words")
    
    # Simulate approaches
    results = {}
    
    # Current approach: 1200 words/section, 5000 word protocol
    results['current'] = simulate_approach(
        "Current Approach (Large extracts + Full protocol)",
        book_word_count,
        extract_words_per_section=1200,
        protocol_words=5000
    )
    
    # Option 1: 650 words/section, 5000 word protocol
    results['option1'] = simulate_approach(
        "Option 1: Focused Extracts (500-800 words + Full protocol)",
        book_word_count,
        extract_words_per_section=650,
        protocol_words=5000
    )
    
    # Option 3: 1200 words/section, 800 word protocol
    results['option3'] = simulate_approach(
        "Option 3: Minimal Protocol (Large extracts + Trimmed protocol)",
        book_word_count,
        extract_words_per_section=1200,
        protocol_words=800
    )
    
    # Comparison table
    print_header("COMPARISON SUMMARY")
    
    current = results['current']
    option1 = results['option1']
    option3 = results['option3']
    
    print(f"\n{Colors.CYAN}{'Metric':<45} {'Current':<15} {'Option 1':<15} {'Option 3':<15}{Colors.END}")
    print("-" * 90)
    
    print(f"{'Extract size (words per section)':<45} {1200:<15} {650:<15} {1200:<15}")
    print(f"{'Total extract size (words)':<45} {current['extract_words']:<15,} {option1['extract_words']:<15,} {option3['extract_words']:<15,}")
    print(f"{'Protocol size (words)':<45} {current['protocol_words']:<15,} {option1['protocol_words']:<15,} {option3['protocol_words']:<15,}")
    print(f"{'Stage 1 input tokens':<45} {current['stage1_input_tokens']:<15,} {option1['stage1_input_tokens']:<15,} {option3['stage1_input_tokens']:<15,}")
    print(f"{'Stage 2A input tokens':<45} {current['stage2a_input_tokens']:<15,} {option1['stage2a_input_tokens']:<15,} {option3['stage2a_input_tokens']:<15,}")
    print(f"{'TOTAL input tokens':<45} {current['total_input_tokens']:<15,} {option1['total_input_tokens']:<15,} {option3['total_input_tokens']:<15,}")
    print(f"{'Estimated cost':<45} ${current['estimated_cost']:<14.4f} ${option1['estimated_cost']:<14.4f} ${option3['estimated_cost']:<14.4f}")
    print(f"{'Stage 2A under rate limit (<30K)':<45} {str(current['rate_limit_safe']):<15} {str(option1['rate_limit_safe']):<15} {str(option3['rate_limit_safe']):<15}")
    
    # Calculate improvements
    print(f"\n{Colors.CYAN}IMPROVEMENTS vs CURRENT:{Colors.END}")
    
    option1_token_reduction = ((current['total_input_tokens'] - option1['total_input_tokens']) / current['total_input_tokens'] * 100)
    option3_token_reduction = ((current['total_input_tokens'] - option3['total_input_tokens']) / current['total_input_tokens'] * 100)
    
    option1_stage2a_reduction = ((current['stage2a_input_tokens'] - option1['stage2a_input_tokens']) / current['stage2a_input_tokens'] * 100)
    option3_stage2a_reduction = ((current['stage2a_input_tokens'] - option3['stage2a_input_tokens']) / current['stage2a_input_tokens'] * 100)
    
    print(f"  Option 1 total token reduction: {option1_token_reduction:+.1f}%")
    print(f"  Option 1 Stage 2A token reduction: {option1_stage2a_reduction:+.1f}%")
    print(f"  Option 3 total token reduction: {option3_token_reduction:+.1f}%")
    print(f"  Option 3 Stage 2A token reduction: {option3_stage2a_reduction:+.1f}%")
    
    # Recommendations
    print(f"\n{Colors.CYAN}ANALYSIS:{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Current Approach:{Colors.END}")
    if not current['rate_limit_safe']:
        print(f"  ✗ Stage 2A: {current['stage2a_input_tokens']:,} tokens (EXCEEDS 30K rate limit)")
        print(f"  ✗ Will trigger rate limit errors on longer books")
    else:
        print(f"  ✓ Stage 2A: {current['stage2a_input_tokens']:,} tokens (under rate limit)")
    
    print(f"\n{Colors.YELLOW}Option 1 (Focused Extracts):{Colors.END}")
    if option1['rate_limit_safe']:
        print(f"  ✓ Stage 2A: {option1['stage2a_input_tokens']:,} tokens (under rate limit)")
        print(f"  ✓ Reduces extract size by {((current['extract_words'] - option1['extract_words']) / current['extract_words'] * 100):.1f}%")
        print(f"  ✓ Maintains full protocol for accuracy")
        print(f"  ⚠ Requires modifying Stage 1 extraction logic")
    else:
        print(f"  ✗ Stage 2A: {option1['stage2a_input_tokens']:,} tokens (still exceeds limit)")
    
    print(f"\n{Colors.YELLOW}Option 3 (Minimal Protocol):{Colors.END}")
    if option3['rate_limit_safe']:
        print(f"  ✓ Stage 2A: {option3['stage2a_input_tokens']:,} tokens (under rate limit)")
        print(f"  ✓ Reduces protocol size by {((current['protocol_words'] - option3['protocol_words']) / current['protocol_words'] * 100):.1f}%")
        print(f"  ✓ No changes to Stage 1 extraction needed")
        print(f"  ⚠ May slightly reduce tagging accuracy due to less protocol context")
    else:
        print(f"  ✗ Stage 2A: {option3['stage2a_input_tokens']:,} tokens (still exceeds limit)")
    
    # Best recommendation
    print(f"\n{Colors.GREEN}RECOMMENDATION:{Colors.END}")
    
    if option1['rate_limit_safe'] and option3['rate_limit_safe']:
        if option1_token_reduction > option3_token_reduction:
            print(f"  ✓ Option 1 (Focused Extracts) - Better token reduction ({option1_token_reduction:.1f}%)")
        else:
            print(f"  ✓ Option 3 (Minimal Protocol) - Simpler implementation, good token reduction ({option3_token_reduction:.1f}%)")
    elif option1['rate_limit_safe']:
        print(f"  ✓ Option 1 (Focused Extracts) - Only approach that solves rate limit issue")
    elif option3['rate_limit_safe']:
        print(f"  ✓ Option 3 (Minimal Protocol) - Only approach that solves rate limit issue")
    else:
        print(f"  ⚠ Both options still exceed rate limit. Consider combining approaches:")
        print(f"    - Use focused extracts (500-800 words)")
        print(f"    - AND use minimal protocol")
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    results_data = {
        "test_date": datetime.now().isoformat(),
        "book_word_count": book_word_count,
        "approaches": results
    }
    
    results_file = output_dir / f"extraction_comparison_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_extraction_approaches.py path/to/book.pdf")
        print("\nExample:")
        print("  python3 test_extraction_approaches.py /mnt/user-data/uploads/TKAM.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"{Colors.RED}Error: File not found: {pdf_path}{Colors.END}")
        sys.exit(1)
    
    exit_code = run_comparison(pdf_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
