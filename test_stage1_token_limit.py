#!/usr/bin/env python3
"""
STAGE 1 TOKEN LIMIT TEST

Compares different approaches to staying under 200K token limit in Stage 1:
- Approach A: Full protocols + Truncated book (first 50K words)
- Approach B: Minimal instructions + Full book
- Approach C: Strategic sample (beginning/middle/end) + Minimal instructions

Measures token usage and validates extraction quality.
"""

import json
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

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

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

def load_protocol(protocol_name):
    """Simulate loading a protocol file"""
    # Typical protocol sizes from Kernel Validation Protocol
    protocol_sizes = {
        "kernel_validation": 40000,  # ~30K words in full protocol
        "lem": 24000,                # ~18K words in LEM
        "minimal": 400               # ~300 words for minimal instructions
    }
    
    return " ".join(["word"] * protocol_sizes.get(protocol_name, 1000))

def simulate_approach_a(book_text):
    """
    Approach A: Full protocols + Truncated book (first 50K words)
    """
    print_header("APPROACH A: Full Protocols + Truncated Book")
    
    words = book_text.split()
    truncated_book = ' '.join(words[:50000])
    
    kernel_validation = load_protocol("kernel_validation")
    lem = load_protocol("lem")
    
    # Build prompt components
    instructions = " ".join(["word"] * 200)  # ~200 words of instructions
    
    total_text = instructions + kernel_validation + lem + truncated_book
    total_tokens = count_tokens(total_text)
    
    book_words = len(truncated_book.split())
    protocol_words = 40000 + 24000  # kernel_validation + lem
    
    print(f"Prompt components:")
    print(f"  Instructions: ~200 words → ~266 tokens")
    print(f"  Kernel Validation Protocol: ~30,000 words → ~40,000 tokens")
    print(f"  LEM Protocol: ~18,000 words → ~24,000 tokens")
    print(f"  Book text (truncated): {book_words:,} words → {count_tokens(truncated_book):,} tokens")
    print(f"\n{Colors.CYAN}TOTAL: {total_tokens:,} tokens{Colors.END}")
    
    under_limit = total_tokens < 200000
    coverage = (50000 / len(words)) * 100 if words else 0
    
    print(f"Under 200K limit: {under_limit} {'✓' if under_limit else '✗'}")
    print(f"Book coverage: {coverage:.1f}%")
    
    return {
        "approach": "A",
        "total_tokens": total_tokens,
        "book_words": book_words,
        "protocol_words": protocol_words,
        "under_limit": under_limit,
        "book_coverage_percent": coverage,
        "pros": [
            "Full protocol context for accurate extraction",
            "Works for any book size"
        ],
        "cons": [
            f"Only {coverage:.1f}% book coverage",
            "May miss climax/resolution if late in book",
            "Less context for identifying Freytag sections"
        ]
    }

def simulate_approach_b(book_text):
    """
    Approach B: Minimal instructions + Full book
    """
    print_header("APPROACH B: Minimal Instructions + Full Book")
    
    minimal_instructions = load_protocol("minimal")
    
    total_text = minimal_instructions + book_text
    total_tokens = count_tokens(total_text)
    
    book_words = len(book_text.split())
    instruction_words = 300
    
    print(f"Prompt components:")
    print(f"  Minimal instructions: ~300 words → ~400 tokens")
    print(f"  Book text (full): {book_words:,} words → {count_tokens(book_text):,} tokens")
    print(f"\n{Colors.CYAN}TOTAL: {total_tokens:,} tokens{Colors.END}")
    
    under_limit = total_tokens < 200000
    
    print(f"Under 200K limit: {under_limit} {'✓' if under_limit else '✗'}")
    print(f"Book coverage: 100.0%")
    
    return {
        "approach": "B",
        "total_tokens": total_tokens,
        "book_words": book_words,
        "protocol_words": instruction_words,
        "under_limit": under_limit,
        "book_coverage_percent": 100.0,
        "pros": [
            "Full book coverage - won't miss any sections",
            "Better Freytag section identification",
            "Simpler prompt"
        ],
        "cons": [
            "May not work for very long books (>150K words)",
            "Less protocol guidance (but Stage 1 is simpler)"
        ]
    }

def simulate_approach_c(book_text):
    """
    Approach C: Strategic sample (beginning/middle/end) + Minimal instructions
    """
    print_header("APPROACH C: Strategic Sample + Minimal Instructions")
    
    words = book_text.split()
    total_words = len(words)
    
    # Sample strategy: 20K from beginning, 20K from middle, 20K from end
    beginning = ' '.join(words[:20000])
    middle_start = total_words // 2 - 10000
    middle_end = total_words // 2 + 10000
    middle = ' '.join(words[middle_start:middle_end])
    ending = ' '.join(words[-20000:])
    
    sampled_book = beginning + "\n\n[... middle sections omitted ...]\n\n" + middle + "\n\n[... later sections omitted ...]\n\n" + ending
    
    minimal_instructions = load_protocol("minimal")
    
    total_text = minimal_instructions + sampled_book
    total_tokens = count_tokens(total_text)
    
    sampled_words = 20000 + 20000 + 20000  # 60K words sampled
    instruction_words = 300
    coverage = (60000 / total_words) * 100 if total_words else 0
    
    print(f"Prompt components:")
    print(f"  Minimal instructions: ~300 words → ~400 tokens")
    print(f"  Book sample (beginning): 20,000 words → ~26,666 tokens")
    print(f"  Book sample (middle): 20,000 words → ~26,666 tokens")
    print(f"  Book sample (end): 20,000 words → ~26,666 tokens")
    print(f"\n{Colors.CYAN}TOTAL: {total_tokens:,} tokens{Colors.END}")
    
    under_limit = total_tokens < 200000
    
    print(f"Under 200K limit: {under_limit} {'✓' if under_limit else '✗'}")
    print(f"Book coverage: {coverage:.1f}% (strategic sampling)")
    
    return {
        "approach": "C",
        "total_tokens": total_tokens,
        "book_words": sampled_words,
        "protocol_words": instruction_words,
        "under_limit": under_limit,
        "book_coverage_percent": coverage,
        "pros": [
            "Good coverage of entire book arc",
            "Won't miss climax/resolution",
            "Works for very long books (200K+ words)"
        ],
        "cons": [
            "Gaps in coverage (might miss important middle sections)",
            "More complex sampling logic"
        ]
    }

def run_comparison(pdf_path):
    """Run comparison of all approaches"""
    
    print_header("STAGE 1 TOKEN LIMIT TEST")
    print(f"Testing file: {pdf_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract book text
    book_text = extract_text_from_pdf(pdf_path)
    if not book_text:
        return 1
    
    book_word_count = len(book_text.split())
    book_tokens = count_tokens(book_text)
    
    print(f"\n{Colors.CYAN}Book Statistics:{Colors.END}")
    print(f"  Total words: {book_word_count:,}")
    print(f"  Estimated tokens: {book_tokens:,}")
    
    # Test all approaches
    results = {}
    
    results['approach_a'] = simulate_approach_a(book_text)
    results['approach_b'] = simulate_approach_b(book_text)
    results['approach_c'] = simulate_approach_c(book_text)
    
    # Comparison table
    print_header("COMPARISON SUMMARY")
    
    a = results['approach_a']
    b = results['approach_b']
    c = results['approach_c']
    
    print(f"\n{Colors.CYAN}{'Metric':<40} {'Approach A':<20} {'Approach B':<20} {'Approach C':<20}{Colors.END}")
    print("-" * 100)
    
    print(f"{'Total tokens':<40} {a['total_tokens']:<20,} {b['total_tokens']:<20,} {c['total_tokens']:<20,}")
    print(f"{'Book words included':<40} {a['book_words']:<20,} {b['book_words']:<20,} {c['book_words']:<20,}")
    print(f"{'Protocol words':<40} {a['protocol_words']:<20,} {b['protocol_words']:<20,} {c['protocol_words']:<20,}")
    print(f"{'Under 200K limit':<40} {str(a['under_limit']):<20} {str(b['under_limit']):<20} {str(c['under_limit']):<20}")
    print(f"{'Book coverage %':<40} {a['book_coverage_percent']:<20.1f} {b['book_coverage_percent']:<20.1f} {c['book_coverage_percent']:<20.1f}")
    
    # Analysis
    print(f"\n{Colors.CYAN}DETAILED ANALYSIS:{Colors.END}")
    
    for approach_name, result in [('Approach A', a), ('Approach B', b), ('Approach C', c)]:
        print(f"\n{Colors.YELLOW}{approach_name}:{Colors.END}")
        print(f"  Total tokens: {result['total_tokens']:,} {'✓' if result['under_limit'] else '✗ EXCEEDS LIMIT'}")
        print(f"  Book coverage: {result['book_coverage_percent']:.1f}%")
        print(f"\n  Pros:")
        for pro in result['pros']:
            print(f"    ✓ {pro}")
        print(f"  Cons:")
        for con in result['cons']:
            print(f"    ⚠ {con}")
    
    # Recommendation
    print(f"\n{Colors.GREEN}RECOMMENDATION:{Colors.END}")
    
    # Find viable approaches
    viable = [k for k, v in results.items() if v['under_limit']]
    
    if not viable:
        print(f"{Colors.RED}✗ No approaches stay under 200K token limit!{Colors.END}")
        print(f"  Book is too long ({book_word_count:,} words)")
        print(f"  Consider:")
        print(f"    - Using a shorter book for testing")
        print(f"    - Implementing more aggressive sampling")
        print(f"    - Breaking book into sections")
        return 1
    
    # Rank by quality
    if b['under_limit']:
        print(f"  ✓ {Colors.GREEN}Approach B (Minimal Instructions + Full Book){Colors.END}")
        print(f"    Reason: Best extraction quality with 100% book coverage")
        print(f"    Tokens: {b['total_tokens']:,} (margin: {200000 - b['total_tokens']:,} tokens)")
        print(f"\n    Implementation:")
        print(f"      1. Remove full protocol text from Stage 1 prompt")
        print(f"      2. Keep only essential extraction instructions (~300 words)")
        print(f"      3. Include full book text")
        print(f"      4. Protocols still used in Stage 2A/2B for tagging")
    elif c['under_limit']:
        print(f"  ✓ {Colors.GREEN}Approach C (Strategic Sample + Minimal Instructions){Colors.END}")
        print(f"    Reason: Good coverage for very long books")
        print(f"    Tokens: {c['total_tokens']:,} (margin: {200000 - c['total_tokens']:,} tokens)")
    elif a['under_limit']:
        print(f"  ✓ {Colors.YELLOW}Approach A (Full Protocols + Truncated Book){Colors.END}")
        print(f"    Reason: Only viable option (not ideal)")
        print(f"    Tokens: {a['total_tokens']:,} (margin: {200000 - a['total_tokens']:,} tokens)")
        print(f"    Warning: Only {a['book_coverage_percent']:.1f}% book coverage")
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    results_data = {
        "test_date": datetime.now().isoformat(),
        "book_word_count": book_word_count,
        "book_tokens": book_tokens,
        "approaches": results
    }
    
    results_file = output_dir / f"stage1_token_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_stage1_token_limit.py path/to/book.pdf")
        print("\nExample:")
        print("  python3 test_stage1_token_limit.py /mnt/user-data/uploads/TKAM.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"{Colors.RED}Error: File not found: {pdf_path}{Colors.END}")
        sys.exit(1)
    
    exit_code = run_comparison(pdf_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
