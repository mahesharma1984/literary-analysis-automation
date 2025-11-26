# Stage 1B v6.0: Complete Worksheet Content Generation via API

## Overview
Major rewrite of `run_stage1b.py` to expand API output to generate ALL worksheet content per device, not just `tvode_components`. This eliminates the need for worksheet generation in Stage 2 and ensures all content is text-specific and pedagogically sound.

## Version
- **Previous:** v5.1
- **New:** v6.0

## Key Changes

### 1. API Integration for Worksheet Content Generation

#### New Functions Added:
- **`initialize_api_client()`**: Initializes Anthropic API client with environment variable validation
- **`generate_worksheet_content(device, macro_focus, text_title, client)`**: Core function that generates complete worksheet content via API call
- **`validate_worksheet_content(device)`**: Validates that all required worksheet_content fields are present and correctly structured
- **`generate_validation_report(output_data, book_name)`**: Generates human-readable markdown validation report

#### API Prompt Features:
- **Multiple Choice Questions**: 
  - 4 options (A, B, C, D) with ~10-15 words each
  - 2 options are "quite plausible" (test understanding, not trick students)
  - Correct answer is most accurate description of device function
  - NO option mentions device name explicitly
  - Distractors wrong about FUNCTION, not device type
  - All options text-specific to the actual book

- **Sequencing Steps**:
  - 3 chronological steps showing HOW reading experience unfolds
  - Format: encounter → process → effect
  - Step 1: What reader encounters (specific text/chapter reference)
  - Step 2: How device processes/transforms that encounter
  - Step 3: Resulting effect on reader/meaning
  - Must be chronological (how reading unfolds), not analytical steps

- **Location Hints**: Specific chapter/scene guidance for students
- **Detail Samples**: Model answers for Step 5 with specific text evidence

### 2. Enhanced Device Package Structure

#### New Output Schema per Device:
```json
{
  "device_name": "...",
  "tvode_components": {...},
  "effects": [...],
  "examples": [...],
  "worksheet_content": {
    "mc_question": "What does [Device] DO in this text?",
    "mc_options": {
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    },
    "mc_correct": "C",
    "mc_explanation": "Two plausible options are B and C because...",
    "sequencing_steps": {
      "step_1": "...",
      "step_2": "...",
      "step_3": "..."
    },
    "sequencing_order": "1-B, 2-C, 3-A",
    "location_hint": "Chapter X, [specific scene description]",
    "detail_sample": "shown through [specific detail]: '[quote snippet]'"
  }
}
```

### 3. Updated `create_week_package()` Function
- Now accepts optional `client` parameter
- Generates worksheet_content for each device during package creation
- Includes comprehensive error handling and fallback content
- Rate limiting protection between API calls

### 4. Validation System
- **Real-time validation**: Validates worksheet_content after generation for each device
- **Final validation**: Comprehensive check of all devices before output
- **Validation report**: Generates markdown report showing:
  - Device name
  - Example chapter
  - MC question status (✓/✗)
  - Sequencing steps status (✓/✗)
  - Effects status (✓/✗)
  - Chapter range validation (TODO: implement)

### 5. Output File Naming
- Changed from `{title}_stage1b_v5.1.json` to `{title}_stage1b_v6_0.json`
- Validation report: `{title}_stage1b_v6_0_validation.md`

### 6. Error Handling & Retry Logic
- Automatic retry on API failures (up to 3 attempts)
- JSON parsing error handling with retry
- Fallback content generation if API fails completely
- Graceful degradation if API client unavailable

### 7. Rate Limiting
- 1 second delay between weeks to prevent API rate limits
- Configurable delays between retry attempts

## Technical Details

### Dependencies Added:
- `anthropic` (already in use)
- `os` (for environment variables)
- `time` (for rate limiting)

### API Model:
- Uses `claude-sonnet-4-20250514`
- Max tokens: 2000
- System prompt: Expert literary analysis educator

### Validation Requirements:
All devices must have:
- `mc_question` (string)
- `mc_options` (dict with A, B, C, D keys)
- `mc_correct` (A, B, C, or D)
- `mc_explanation` (string)
- `sequencing_steps` (dict with step_1, step_2, step_3)
- `sequencing_order` (string)
- `location_hint` (string)
- `detail_sample` (string)

## Benefits

1. **Text-Specific Content**: All worksheet content is generated with actual book details, not generic templates
2. **Pedagogical Quality**: MC questions test understanding, not device recognition
3. **Complete Pipeline**: Stage 1B now generates everything needed for worksheets
4. **Validation**: Comprehensive validation ensures quality before Stage 2
5. **Error Resilience**: Fallback content and retry logic ensure robustness

## Migration Notes

- Stage 2 can now use pre-generated worksheet_content instead of generating it
- Old Stage 1B outputs (v5.1) will need regeneration to include worksheet_content
- API key required: `ANTHROPIC_API_KEY` environment variable must be set

## Files Modified
- `run_stage1b.py`: Complete rewrite of worksheet content generation

## Testing
- Validation reports generated for Matilda test run
- All devices validated successfully
- API integration tested with retry logic
