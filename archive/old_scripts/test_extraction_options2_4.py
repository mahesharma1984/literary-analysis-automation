#!/usr/bin/env python3
"""
EXTRACTION COMPARISON - OPTIONS 2 & 4

Tests two additional extraction approaches:
- Option 2: Two-Pass Extraction (Stage 1A + Stage 1B)
- Option 4: Adaptive Extraction (dynamic extract size based on book length)

Compare these results with the first test (Options 1 & 3).
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
        return text, total_pages
    
    except Exception as e:
        print(f"{Colors.RED}Error extracting PDF: {e}{Colors.END}")
        return None, None

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

def simulate_baseline(approach_name, book_word_count, extract_words_per_section, protocol_words):
    """Baseline simulation (for comparison)"""
    
    print_header(f"BASELINE: {approach_name}")
    
    # Stage 1: Extract passages
    stage1_input_words = min(50000, book_word_count) + 200
    stage1_input_tokens = count_tokens(" ".join(["word"] * stage1_input_words))
    
    stage1_output_words = extract_words_per_section * 5
    stage1_output_tokens = count_tokens(" ".join(["word"] * stage1_output_words))
    
    print(f"Stage 1 (Extract Passages):")
    print(f"  Input: {stage1_input_words:,} words → {stage1_input_tokens:,} tokens")
    print(f"  Output: {stage1_output_words:,} words → {stage1_output_tokens:,} tokens")
    
    # Stage 2A: Macro tagging
    stage2a_input_words = protocol_words + stage1_output_words + 300
    stage2a_input_tokens = count_tokens(" ".join(["word"] * stage2a_input_words))
    stage2a_output_tokens = 500
    
    print(f"\nStage 2A (Macro Tagging):")
    print(f"  Input: {stage2a_input_words:,} words → {stage2a_input_tokens:,} tokens")
    print(f"  Output: ~{stage2a_output_tokens:,} tokens")
    
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
        "rate_limit_safe": rate_limit_safe,
        "api_calls": 2  # Stage 1 + Stage 2A
    }

def simulate_option2_two_pass(book_word_count, extract_words_per_section, protocol_words):
    """
    Option 2: Two-Pass Extraction
    
    Stage 1A: Scan book and identify Freytag section boundaries (chapter/page ranges)
    Stage 1B: Extract focused passages from each identified section
    Stage 2A: Macro tagging (unchanged)
    """
    
    print_header("Option 2: Two-Pass Extraction")
    print("Stage 1A identifies boundaries → Stage 1B extracts passages")
    
    # Stage 1A: Identify boundaries
    # Input: full book (or large portion) + instructions
    stage1a_input_words = min(50000, book_word_count) + 300
    stage1a_input_tokens = count_tokens(" ".join(["word"] * stage1a_input_words))
    
    # Output: JSON with section boundaries (minimal)
    stage1a_output_words = 200  # Just boundary descriptions
    stage1a_output_tokens = count_tokens(" ".join(["word"] * stage1a_output_words))
    
    print(f"Stage 1A (Identify Boundaries):")
    print(f"  Input: {stage1a_input_words:,} words → {stage1a_input_tokens:,} tokens")
    print(f"  Output: {stage1a_output_words:,} words (just boundaries) → {stage1a_output_tokens:,} tokens")
    
    # Stage 1B: Extract passages from identified sections
    # Input: smaller sections of book (5 x 2000 words) + instructions
    stage1b_input_words = 10000 + 300  # 5 sections of ~2000 words each
    stage1b_input_tokens = count_tokens(" ".join(["word"] * stage1b_input_words))
    
    # Output: 5 extracts
    stage1b_output_words = extract_words_per_section * 5
    stage1b_output_tokens = count_tokens(" ".join(["word"] * stage1b_output_words))
    
    print(f"\nStage 1B (Extract Passages):")
    print(f"  Input: {stage1b_input_words:,} words (targeted sections) → {stage1b_input_tokens:,} tokens")
    print(f"  Output: {stage1b_output_words:,} words → {stage1b_output_tokens:,} tokens")
    
    # Stage 2A: Macro tagging (same as baseline)
    stage2a_input_words = protocol_words + stage1b_output_words + 300
    stage2a_input_tokens = count_tokens(" ".join(["word"] * stage2a_input_words))
    stage2a_output_tokens = 500
    
    print(f"\nStage 2A (Macro Tagging):")
    print(f"  Input: {stage2a_input_words:,} words → {stage2a_input_tokens:,} tokens")
    print(f"  Output: ~{stage2a_output_tokens:,} tokens")
    
    total_input_tokens = stage1a_input_tokens + stage1b_input_tokens + stage2a_input_tokens
    total_output_tokens = stage1a_output_tokens + stage1b_output_tokens + stage2a_output_tokens
    total_cost = estimate_cost(total_input_tokens, total_output_tokens)
    
    rate_limit_safe = max(stage1a_input_tokens, stage1b_input_tokens, stage2a_input_tokens) < 30000
    
    print(f"\n{Colors.CYAN}TOTALS:{Colors.END}")
    print(f"  Total input tokens: {total_input_tokens:,}")
    print(f"  Total output tokens: {total_output_tokens:,}")
    print(f"  Estimated cost: ${total_cost:.4f}")
    print(f"  All stages under rate limit: {rate_limit_safe} {'✓' if rate_limit_safe else '✗'}")
    
    return {
        "stage1a_input_tokens": stage1a_input_tokens,
        "stage1a_output_tokens": stage1a_output_tokens,
        "stage1b_input_tokens": stage1b_input_tokens,
        "stage1b_output_tokens": stage1b_output_tokens,
        "stage2a_input_tokens": stage2a_input_tokens,
        "stage2a_output_tokens": stage2a_output_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "extract_words": stage1b_output_words,
        "protocol_words": protocol_words,
        "estimated_cost": total_cost,
        "rate_limit_safe": rate_limit_safe,
        "api_calls": 3  # Stage 1A + Stage 1B + Stage 2A
    }

def simulate_option4_adaptive(book_word_count, book_pages, protocol_words):
    """
    Option 4: Adaptive Extraction
    
    Dynamically adjust extract size based on book length:
    - Short books (<300 pages): 800 words/section
    - Medium books (300-500 pages): 600 words/section
    - Long books (>500 pages): 400 words/section
    """
    
    print_header("Option 4: Adaptive Extraction")
    
    # Determine extract size based on book length
    if book_pages < 300:
        extract_words_per_section = 800
        category = "Short book (<300 pages)"
    elif book_pages < 500:
        extract_words_per_section = 600
        category = "Medium book (300-500 pages)"
    else:
        extract_words_per_section = 400
        category = "Long book (>500 pages)"
    
    print(f"Book classification: {category}")
    print(f"Adaptive extract size: {extract_words_per_section} words/section")
    
    # Stage 1: Extract passages (adaptive)
    stage1_input_words = min(50000, book_word_count) + 200
    stage1_input_tokens = count_tokens(" ".join(["word"] * stage1_input_words))
    
    stage1_output_words = extract_words_per_section * 5
    stage1_output_tokens = count_tokens(" ".join(["word"] * stage1_output_words))
    
    print(f"\nStage 1 (Extract Passages - Adaptive):")
    print(f"  Input: {stage1_input_words:,} words → {stage1_input_tokens:,} tokens")
    print(f"  Output: {stage1_output_words:,} words → {stage1_output_tokens:,} tokens")
    
    # Stage 2A: Macro tagging
    stage2a_input_words = protocol_words + stage1_output_words + 300
    stage2a_input_tokens = count_tokens(" ".join(["word"] * stage2a_input_words))
    stage2a_output_tokens = 500
    
    print(f"\nStage 2A (Macro Tagging):")
    print(f"  Input: {stage2a_input_words:,} words → {stage2a_input_tokens:,} tokens")
    print(f"  Output: ~{stage2a_output_tokens:,} tokens")
    
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
        "book_category": category,
        "extract_words_per_section": extract_words_per_section,
        "stage1_input_tokens": stage1_input_tokens,
        "stage1_output_tokens": stage1_output_tokens,
        "stage2a_input_tokens": stage2a_input_tokens,
        "stage2a_output_tokens": stage2a_output_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "extract_words": stage1_output_words,
        "protocol_words": protocol_words,
        "estimated_cost": total_cost,
        "rate_limit_safe": rate_limit_safe,
        "api_calls": 2  # Stage 1 + Stage 2A
    }

def run_comparison(pdf_path):
    """Run comparison simulation for Options 2 & 4"""
    
    print_header("EXTRACTION COMPARISON - OPTIONS 2 & 4")
    print(f"Testing file: {pdf_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract text to get book size
    full_text, total_pages = extract_text_from_pdf(pdf_path)
    if not full_text:
        return 1
    
    book_word_count = len(full_text.split())
    print_info(f"Book size: {book_word_count:,} words, {total_pages} pages")
    
    # Simulate approaches
    results = {}
    
    # Baseline (for reference - same as "current" from first test)
    results['baseline'] = simulate_baseline(
        "Baseline (Current approach)",
        book_word_count,
        extract_words_per_section=1200,
        protocol_words=5000
    )
    
    # Option 2: Two-Pass Extraction
    results['option2'] = simulate_option2_two_pass(
        book_word_count,
        extract_words_per_section=650,  # Focused extracts
        protocol_words=5000
    )
    
    # Option 4: Adaptive Extraction
    results['option4'] = simulate_option4_adaptive(
        book_word_count,
        total_pages,
        protocol_words=5000
    )
    
    # Comparison table
    print_header("COMPARISON SUMMARY")
    
    baseline = results['baseline']
    option2 = results['option2']
    option4 = results['option4']
    
    print(f"\n{Colors.CYAN}{'Metric':<45} {'Baseline':<15} {'Option 2':<15} {'Option 4':<15}{Colors.END}")
    print("-" * 90)
    
    print(f"{'API calls required':<45} {baseline['api_calls']:<15} {option2['api_calls']:<15} {option4['api_calls']:<15}")
    print(f"{'Extract size (words per section)':<45} {1200:<15} {650:<15} {option4['extract_words_per_section']:<15}")
    print(f"{'Total extract size (words)':<45} {baseline['extract_words']:<15,} {option2['extract_words']:<15,} {option4['extract_words']:<15,}")
    print(f"{'Protocol size (words)':<45} {baseline['protocol_words']:<15,} {option2['protocol_words']:<15,} {option4['protocol_words']:<15,}")
    
    # Show all stages for Option 2
    print(f"{'Stage 1/1A input tokens':<45} {baseline['stage1_input_tokens']:<15,} {option2['stage1a_input_tokens']:<15,} {option4['stage1_input_tokens']:<15,}")
    if 'stage1b_input_tokens' in option2:
        print(f"{'Stage 1B input tokens':<45} {'N/A':<15} {option2['stage1b_input_tokens']:<15,} {'N/A':<15}")
    print(f"{'Stage 2A input tokens':<45} {baseline['stage2a_input_tokens']:<15,} {option2['stage2a_input_tokens']:<15,} {option4['stage2a_input_tokens']:<15,}")
    
    print(f"{'TOTAL input tokens':<45} {baseline['total_input_tokens']:<15,} {option2['total_input_tokens']:<15,} {option4['total_input_tokens']:<15,}")
    print(f"{'Estimated cost':<45} ${baseline['estimated_cost']:<14.4f} ${option2['estimated_cost']:<14.4f} ${option4['estimated_cost']:<14.4f}")
    print(f"{'Rate limit safe':<45} {str(baseline['rate_limit_safe']):<15} {str(option2['rate_limit_safe']):<15} {str(option4['rate_limit_safe']):<15}")
    
    # Calculate improvements
    print(f"\n{Colors.CYAN}IMPROVEMENTS vs BASELINE:{Colors.END}")
    
    option2_token_reduction = ((baseline['total_input_tokens'] - option2['total_input_tokens']) / baseline['total_input_tokens'] * 100)
    option4_token_reduction = ((baseline['total_input_tokens'] - option4['total_input_tokens']) / baseline['total_input_tokens'] * 100)
    
    option2_cost_reduction = ((baseline['estimated_cost'] - option2['estimated_cost']) / baseline['estimated_cost'] * 100)
    option4_cost_reduction = ((baseline['estimated_cost'] - option4['estimated_cost']) / baseline['estimated_cost'] * 100)
    
    print(f"  Option 2 token reduction: {option2_token_reduction:+.1f}%")
    print(f"  Option 2 cost reduction: {option2_cost_reduction:+.1f}%")
    print(f"  Option 4 token reduction: {option4_token_reduction:+.1f}%")
    print(f"  Option 4 cost reduction: {option4_cost_reduction:+.1f}%")
    
    # Analysis
    print(f"\n{Colors.CYAN}ANALYSIS:{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Option 2 (Two-Pass Extraction):{Colors.END}")
    print(f"  Pros:")
    print(f"    ✓ More surgical - identifies exact boundaries first")
    print(f"    ✓ Can handle books with unusual structure")
    print(f"    ✓ Stage 1B only processes relevant sections")
    if option2_token_reduction > 0:
        print(f"    ✓ Token reduction: {option2_token_reduction:.1f}%")
    print(f"  Cons:")
    print(f"    ✗ Requires 3 API calls instead of 2 (+50% calls)")
    print(f"    ✗ More complex implementation")
    print(f"    ✗ Stage 1A might struggle with non-linear narratives")
    print(f"  Rate limit: {'✓ Safe' if option2['rate_limit_safe'] else '✗ Exceeds'}")
    
    print(f"\n{Colors.YELLOW}Option 4 (Adaptive Extraction):{Colors.END}")
    print(f"  Book classification: {option4['book_category']}")
    print(f"  Extract size chosen: {option4['extract_words_per_section']} words/section")
    print(f"  Pros:")
    print(f"    ✓ Automatic scaling for book length")
    print(f"    ✓ Maintains 2 API calls (same as baseline)")
    print(f"    ✓ Simple implementation (just add length check)")
    if option4_token_reduction > 0:
        print(f"    ✓ Token reduction: {option4_token_reduction:.1f}%")
    print(f"  Cons:")
    print(f"    ⚠ Fixed thresholds (300/500 pages) might not suit all books")
    print(f"    ⚠ Very long books get shortest extracts (might lose quality)")
    print(f"  Rate limit: {'✓ Safe' if option4['rate_limit_safe'] else '✗ Exceeds'}")
    
    # Recommendations
    print(f"\n{Colors.GREEN}RECOMMENDATIONS:{Colors.END}")
    
    if option2['api_calls'] > baseline['api_calls']:
        extra_calls = option2['api_calls'] - baseline['api_calls']
        print(f"  ⚠ Option 2 requires {extra_calls} extra API call(s) - increases latency and complexity")
    
    if option2_cost_reduction > option4_cost_reduction:
        print(f"  ⚠ Option 2 has better cost reduction BUT requires more API calls")
        print(f"    Trade-off: {option2_cost_reduction - option4_cost_reduction:.1f}% better cost vs {option2['api_calls'] - option4['api_calls']} extra call(s)")
    
    if option4_cost_reduction > 10:
        print(f"  ✓ Option 4 offers good balance: {option4_cost_reduction:.1f}% savings with same 2-call structure")
    
    # Overall verdict
    print(f"\n{Colors.CYAN}OVERALL VERDICT:{Colors.END}")
    
    if option2['rate_limit_safe'] and option4['rate_limit_safe']:
        if option4_cost_reduction > option2_cost_reduction * 0.8:  # Within 20%
            print(f"  ✓ Option 4 (Adaptive) - Simpler, scales well, good cost savings")
            print(f"    Reason: Similar savings to Option 2 with fewer API calls")
        else:
            print(f"  ✓ Option 2 (Two-Pass) - Best token/cost reduction")
            print(f"    Trade-off: Worth the extra API call for {option2_cost_reduction:.1f}% savings")
    elif option2['rate_limit_safe']:
        print(f"  ✓ Option 2 (Two-Pass) - Only option that solves rate limit issue")
    elif option4['rate_limit_safe']:
        print(f"  ✓ Option 4 (Adaptive) - Only option that solves rate limit issue")
    else:
        print(f"  ⚠ Neither option fully solves rate limit issue for this book")
        print(f"    Consider combining approaches or using Option 1 from first test")
    
    # Cross-reference first test
    print(f"\n{Colors.CYAN}COMPARE WITH FIRST TEST:{Colors.END}")
    print(f"  First test showed:")
    print(f"    - Option 1 (Focused): 17.7% cost reduction, 2 API calls")
    print(f"    - Option 3 (Minimal Protocol): 4.5% cost reduction, 2 API calls")
    print(f"  This test shows:")
    print(f"    - Option 2 (Two-Pass): {option2_cost_reduction:.1f}% cost reduction, {option2['api_calls']} API calls")
    print(f"    - Option 4 (Adaptive): {option4_cost_reduction:.1f}% cost reduction, {option4['api_calls']} API calls")
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    results_data = {
        "test_date": datetime.now().isoformat(),
        "book_word_count": book_word_count,
        "book_pages": total_pages,
        "approaches": results
    }
    
    results_file = output_dir / f"extraction_comparison_options2_4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_extraction_approaches_sim.py path/to/book.pdf")
        print("\nExample:")
        print("  python3 test_extraction_approaches_sim.py /mnt/user-data/uploads/TKAM.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"{Colors.RED}Error: File not found: {pdf_path}{Colors.END}")
        sys.exit(1)
    
    exit_code = run_comparison(pdf_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
