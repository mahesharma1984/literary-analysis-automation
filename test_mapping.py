#!/usr/bin/env python3
"""
Test script to apply device taxonomy mapping to The Giver kernel
Shows how devices would be categorized using the new mapping file
"""

import json
from typing import Dict, List

def load_mapping(mapping_path: str) -> Dict:
    """Load the device taxonomy mapping"""
    with open(mapping_path, 'r') as f:
        return json.load(f)

def load_kernel(kernel_path: str) -> Dict:
    """Load the kernel file"""
    with open(kernel_path, 'r') as f:
        return json.load(f)

def categorize_device(device_name: str, mapping: Dict) -> tuple[str, str]:
    """
    Categorize a device using the mapping file
    Returns: (week_key, week_label)
    """
    # Check each week's mappings
    for week_key, devices in mapping['device_mappings'].items():
        for mapped_device in devices:
            if mapped_device['device_name'] == device_name:
                week_label = mapping['week_definitions'][week_key]['label']
                return week_key, week_label
    
    # If not found in explicit mappings, return None
    return None, "NOT MAPPED"

def main():
    # Load files
    mapping = load_mapping('device_taxonomy_mapping.json')
    kernel = load_kernel('kernels/The_Old_Man_and_the_sea_kernel_v3.3.json')
    
    print("=" * 80)
    print("DEVICE CATEGORIZATION TEST: The Giver")
    print("=" * 80)
    print()
    
    # Extract devices from kernel
    devices = kernel.get('devices', [])
    
    # Categorize each device
    categorized = {}
    unmapped = []
    
    for device in devices:
        device_name = device['name']
        classification = device.get('classification', '')
        student_facing = device.get('student_facing_type', '')
        
        week_key, week_label = categorize_device(device_name, mapping)
        
        if week_key:
            if week_key not in categorized:
                categorized[week_key] = []
            categorized[week_key].append({
                'name': device_name,
                'classification': classification,
                'student_facing': student_facing
            })
        else:
            unmapped.append({
                'name': device_name,
                'classification': classification,
                'student_facing': student_facing
            })
    
    # Display results by week
    week_order = [
        'week_1_exposition',
        'week_2_literary_devices',
        'week_3_structure',
        'week_4_narrative_voice',
        'week_5_rhetorical_voice'
    ]
    
    for week_key in week_order:
        if week_key in categorized:
            week_def = mapping['week_definitions'][week_key]
            print(f"\n{'─' * 80}")
            print(f"{week_def['label']}")
            print(f"Focus: {week_def['focus']}")
            print(f"{'─' * 80}")
            
            for device in categorized[week_key]:
                print(f"\n  • {device['name']}")
                print(f"    Classification: {device['classification']}")
                print(f"    Student Type: {device['student_facing']}")
    
    # Show unmapped devices
    if unmapped:
        print(f"\n{'─' * 80}")
        print("UNMAPPED DEVICES (need to be added to mapping)")
        print(f"{'─' * 80}")
        for device in unmapped:
            print(f"\n  • {device['name']}")
            print(f"    Classification: {device['classification']}")
            print(f"    Student Type: {device['student_facing']}")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total devices in kernel: {len(devices)}")
    print(f"Successfully mapped: {sum(len(d) for d in categorized.values())}")
    print(f"Unmapped: {len(unmapped)}")
    print()
    
    # Week distribution
    print("Distribution by week:")
    for week_key in week_order:
        if week_key in categorized:
            count = len(categorized[week_key])
            week_label = mapping['week_definitions'][week_key]['label']
            print(f"  {week_label}: {count} devices")

if __name__ == '__main__':
    main()
