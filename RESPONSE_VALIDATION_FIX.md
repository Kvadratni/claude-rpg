# AI NPC System - Response Validation & UI Character Fixes

## Issues Fixed

### 1. **Response Length Validation Too Strict**
**Problem:** The system required responses to be >10 characters, which rejected valid short answers like "five", "yes", "no", etc.

**Solution:** Lowered threshold from 10 characters to 1 character for valid responses.

**Before:**
```python
if response and len(response.strip()) > 10:
```

**After:**
```python  
if response and len(response.strip()) > 0:
```

### 2. **UI Dash Display Issues**
**Problem:** The UI was showing broken characters instead of dashes due to Unicode encoding issues.

**Solution:** Added character replacement in `_clean_response()` method to convert problematic Unicode characters to UI-safe alternatives.

**Characters Fixed:**
- `–` (en dash) → `-` (regular hyphen)
- `—` (em dash) → `-` (regular hyphen)  
- `−` (minus sign) → `-` (regular hyphen)
- `'` / `'` (smart quotes) → `'` (regular apostrophe)
- `"` / `"` (smart quotes) → `"` (regular quote)
- `…` (ellipsis) → `...` (three dots)

### 3. **Response Cleaning Logic Updates**
**Additional Improvements:**
- More permissive minimum response length (1 character vs 5)
- Only require punctuation for responses longer than 3 characters
- Preserve short valid responses like "Yes", "No", "Five", etc.

## Code Changes

### Updated `_clean_response()` Method:
```python
def _clean_response(self, response: str) -> str:
    """Clean up AI response to be more NPC-like"""
    if not response or len(response.strip()) < 1:
        return ""
    
    # Remove common artifacts
    response = response.strip()
    response = re.sub(r'\*.*?\*', '', response)  # Remove action text
    response = re.sub(r'\[.*?\]', '', response)  # Remove bracketed text
    
    # Fix character encoding issues that cause broken display in UI
    response = response.replace('–', '-')  # en dash
    response = response.replace('—', '-')  # em dash
    response = response.replace('−', '-')  # minus sign
    response = response.replace(''', "'")  # left single quote
    response = response.replace(''', "'")  # right single quote
    response = response.replace('"', '"')  # left double quote
    response = response.replace('"', '"')  # right double quote
    response = response.replace('…', '...')  # ellipsis
    
    # Remove AI-like phrases
    ai_phrases = [
        "As an AI", "I'm an AI", "I cannot", "I don't have the ability",
        "I'm not able to", "I can't actually", "In this game", "As your"
    ]
    
    for phrase in ai_phrases:
        response = re.sub(phrase, "", response, flags=re.IGNORECASE)
    
    response = response.strip()
    
    # Ensure it's not empty after cleaning
    if not response or len(response) < 1:
        return ""
    
    # Ensure it ends with punctuation (but don't require it for very short responses)
    if len(response) > 3 and not response.endswith(('.', '!', '?')):
        response += "."
    
    return response
```

## Expected Results

### **Response Validation:**
- ✅ "five" → Accepted (4 characters)
- ✅ "yes" → Accepted (3 characters)  
- ✅ "no" → Accepted (2 characters)
- ✅ "!" → Accepted (1 character)
- ❌ "" → Rejected (0 characters)

### **UI Character Display:**
- ✅ Dashes display correctly as hyphens
- ✅ Smart quotes display as regular quotes
- ✅ Ellipsis displays as three dots
- ✅ No more broken character artifacts

### **Response Quality:**
- ✅ Short valid responses preserved
- ✅ Long responses still get punctuation added
- ✅ AI artifacts still removed
- ✅ Action text still filtered out

## Files Modified
- `src/entities/ai_npc_base.py` - Updated response validation and character cleaning logic

These fixes ensure the AI NPC system accepts valid short responses while displaying all text correctly in the game UI.