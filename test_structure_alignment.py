#!/usr/bin/env python3
"""
Test script for Book Structure Alignment Protocol v1
Tests structure detection and alignment on TKAM and The Giver
"""

import PyPDF2
import re
import json
from pathlib import Path


def detect_structure(pdf_path):
    """Detect chapter structure in PDF"""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        print(f"=== STRUCTURE DETECTION: {pdf_path} ===")
        print(f"Total pages: {len(reader.pages)}\n")
        
        # Search patterns
        chapter_markers = []
        
        for i in range(min(len(reader.pages), 300)):
            text = reader.pages[i].extract_text()
            if text:
                lines = text.split('\n')
                for line in lines[:5]:
                    line_clean = line.strip()
                    
                    # Check for various chapter patterns
                    # Pattern 1: "Chapter 1", "Chapter One", "CHAPTER 1"
                    if re.match(r'^[Cc][Hh][Aa][Pp][Tt][Ee][Rr]\s+\w+', line_clean):
                        chapter_markers.append((i+1, line_clean, 'NUM'))
                    
                    # Pattern 2: Just a number at start of page
                    elif re.match(r'^[0-9]{1,2}$', line_clean):
                        chapter_markers.append((i+1, f"Chapter {line_clean}", 'NUM'))
                    
                    # Pattern 3: Word numbers (One, Two, Three...)
                    elif line_clean in ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve']:
                        chapter_markers.append((i+1, f"Chapter {line_clean}", 'NAME'))
                    
                    # Pattern 4: Part/Book markers
                    elif re.match(r'^(PART|BOOK|Part|Book)\s+(ONE|TWO|THREE|I|II|III|\d+)', line_clean, re.IGNORECASE):
                        chapter_markers.append((i+1, line_clean, 'NEST'))
                    
                    # Pattern 5: Prologue/Epilogue
                    elif line_clean.lower() in ['prologue', 'epilogue']:
                        chapter_markers.append((i+1, line_clean.upper(), 'HYBRID'))
        
        # Analyze findings
        print("--- Detected Markers ---")
        for page, marker, type_hint in chapter_markers:
            print(f"Page {page}: {marker}")
        
        print(f"\n--- Structure Analysis ---")
        print(f"Total markers found: {len(chapter_markers)}")
        
        # Determine structure type
        types_found = set([t for _, _, t in chapter_markers])
        if 'NEST' in types_found:
            structure_type = 'NEST'
        elif 'HYBRID' in types_found:
            structure_type = 'HYBRID'
        elif len(chapter_markers) > 0:
            structure_type = chapter_markers[0][2]
        else:
            structure_type = 'UNMARK'
        
        print(f"Detected structure type: {structure_type}")
        print(f"Total units: {len(chapter_markers)}")
        
        return chapter_markers, structure_type


def apply_conventional_distribution(total_units):
    """Apply protocol's conventional distribution formula (v1.1)"""
    
    n = total_units
    
    # New formula from v1.1
    exp_end = max(1, int(n * 0.12))
    ra_end = int(n * 0.50) - 1
    climax_start = int(n * 0.50)
    climax_end = int(n * 0.55)
    
    # Climax refinement: if >3 chapters, narrow to primary ±1
    climax_chapters = climax_end - climax_start + 1
    if climax_chapters > 3:
        primary_climax = int(n * 0.50)
        climax_start = max(1, primary_climax - 1)
        climax_end = min(n, primary_climax + 1)
    
    alignment = {
        'exposition': {
            'start': 1,
            'end': exp_end,
        },
        'rising_action': {
            'start': exp_end + 1,
            'end': ra_end,
        },
        'climax': {
            'start': climax_start,
            'end': climax_end,
        },
        'falling_action': {
            'start': climax_end + 1,
            'end': int(n * 0.85),
        },
        'resolution': {
            'start': int(n * 0.85) + 1,
            'end': n,
        }
    }
    
    print(f"\n=== CONVENTIONAL DISTRIBUTION (N={n}) ===\n")
    for stage, ranges in alignment.items():
        count = ranges['end'] - ranges['start'] + 1
        pct = round(count / n * 100)
        print(f"{stage.upper():20} Chapters {ranges['start']}-{ranges['end']:2}  ({count} chapters, {pct}%)")
    
    return alignment


def load_kernel_alignment(kernel_path):
    """Load existing alignment from kernel JSON"""
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    mapping = kernel.get('narrative_position_mapping', {})
    text_structure = kernel.get('text_structure', {})
    
    return mapping, text_structure


def compare_alignments(protocol_alignment, kernel_mapping, book_name):
    """Compare protocol alignment with existing kernel"""
    print(f"\n=== COMPARISON: Protocol vs Existing Kernel ({book_name}) ===\n")
    
    # Convert protocol alignment to chapter ranges
    protocol_ranges = {}
    for stage, ranges in protocol_alignment.items():
        protocol_ranges[stage] = f"{ranges['start']}-{ranges['end']}"
    
    # Extract kernel ranges
    kernel_ranges = {}
    for stage, data in kernel_mapping.items():
        kernel_ranges[stage] = data.get('chapter_range', 'N/A')
    
    # Compare
    print(f"{'Stage':<20} {'Protocol':<15} {'Existing Kernel':<15} {'Match':<10}")
    print("-" * 60)
    
    matches = 0
    for stage in ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']:
        protocol = protocol_ranges.get(stage, 'N/A')
        kernel = kernel_ranges.get(stage, 'N/A')
        match = "✓" if protocol == kernel else "✗"
        if match == "✓":
            matches += 1
        print(f"{stage:<20} {protocol:<15} {kernel:<15} {match:<10}")
    
    print(f"\nMatch rate: {matches}/5 ({matches*20}%)")
    return matches == 5


if __name__ == "__main__":
    # Test 1: To Kill a Mockingbird
    print("=" * 70)
    print("TEST 1: TO KILL A MOCKINGBIRD")
    print("=" * 70)
    
    tkam_pdf = Path("books/TKAM.pdf")
    tkam_kernel = Path("kernels/To_Kill_a_Mockingbird_kernel_v3_4.json")
    
    if tkam_pdf.exists():
        print("\n--- Running Structure Detection ---")
        markers, struct_type = detect_structure(str(tkam_pdf))
        print(f"\nDetection found {len(markers)} markers, type: {struct_type}")
    
    # Use known chapter count from kernel (more reliable)
    if tkam_kernel.exists():
        kernel_mapping, text_structure = load_kernel_alignment(str(tkam_kernel))
        total_chapters = text_structure.get('total_chapters_estimate', 31)
        print(f"\n--- Using Known Chapter Count: {total_chapters} ---")
        
        protocol_alignment = apply_conventional_distribution(total_chapters)
        
        print(f"\nExisting kernel reports: {total_chapters} chapters")
        compare_alignments(protocol_alignment, kernel_mapping, "TKAM")
    else:
        print(f"ERROR: {tkam_kernel} not found")
    
    print("\n\n")
    
    # Test 2: The Giver
    print("=" * 70)
    print("TEST 2: THE GIVER")
    print("=" * 70)
    
    giver_pdf = Path("books/Giver.pdf")
    giver_kernel = Path("kernels/The_Giver_kernel_v3_4.json")
    
    if giver_pdf.exists():
        print("\n--- Running Structure Detection ---")
        markers, struct_type = detect_structure(str(giver_pdf))
        print(f"\nDetection found {len(markers)} markers, type: {struct_type}")
    
    # Use known chapter count from kernel
    if giver_kernel.exists():
        kernel_mapping, text_structure = load_kernel_alignment(str(giver_kernel))
        total_chapters = text_structure.get('total_chapters_estimate', 23)
        print(f"\n--- Using Known Chapter Count: {total_chapters} ---")
        
        protocol_alignment = apply_conventional_distribution(total_chapters)
        
        print(f"\nExisting kernel reports: {total_chapters} chapters")
        compare_alignments(protocol_alignment, kernel_mapping, "The Giver")
    else:
        print(f"ERROR: {giver_kernel} not found")

