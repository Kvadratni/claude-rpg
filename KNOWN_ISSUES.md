# Known Issues

## AI Recipe Integration

### Issue: Subprocess Output Truncation
**Status**: Unresolved  
**Severity**: High  

**Description**: 
The Goose CLI subprocess calls are not capturing the full AI response output. When running Goose recipes via `subprocess.run()` or `subprocess.Popen()`, only the recipe loading information is captured, but the actual AI response is lost.

**Evidence**:
- Manual command works: `goose run --recipe recipes/village_elder.yaml --params "message=Hello" --params "context=test" --no-session`
- Subprocess calls only capture ~468 characters (recipe loading info)
- AI responses are generated (confirmed by manual testing) but not captured by Python subprocess

**Attempted Solutions**:
1. ✗ `subprocess.run()` with `capture_output=True`
2. ✗ `subprocess.Popen()` with `communicate()`
3. ✗ Redirecting stderr to stdout (`2>&1`)
4. ✗ Using `shell=True` with command strings
5. ✗ Unbuffered output (`bufsize=0`)
6. ✗ File-based output capture with delays
7. ✗ Background execution with polling

**Current Workaround**:
The system falls back to intelligent local responses that are tailored to each NPC type. While not as dynamic as AI responses, these provide character-appropriate dialogue.

**Impact**:
- Recipe system loads successfully ✅
- NPC personality mapping works ✅  
- Game integration is complete ✅
- AI responses are replaced with fallback responses ⚠️

**Next Steps**:
- Investigate Goose CLI output buffering behavior
- Test with different Python subprocess libraries
- Consider alternative AI integration approaches
- Examine Goose CLI source code for output handling

## System Status

### Working Components ✅
- Recipe loading and parsing (YAML format)
- NPC to recipe mapping system
- Game integration with debug logging
- Chat window interface
- Context passing (player stats, location, etc.)
- Multi-tier fallback system
- Comprehensive error handling

### Partially Working ⚠️
- AI responses (fallback to local responses)
- Recipe execution (loads but doesn't capture AI output)

### Debug Infrastructure ✅
- Comprehensive logging throughout the system
- Step-by-step execution tracking
- Error reporting and stack traces
- Performance monitoring