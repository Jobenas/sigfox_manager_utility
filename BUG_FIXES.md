# Sigfox Manager Bug Fixes - Version 0.1.1

## Authentication Bug Fix

### Issue
The HTTP Basic Authentication header was incorrectly formatted, causing 401 Unauthorized errors when making API calls to the Sigfox backend.

### Root Cause
In `http_utils.py`, the authentication bytes were being passed directly to an f-string, which automatically added the `b''` prefix representation instead of decoding the bytes to a string.

**Before (Buggy):**
```python
auth = base64.b64encode(f"{username}:{password}".encode("utf-8"))
headers = {"Authorization": f"Basic {auth}"}  # Results in "Basic b'base64string'"
```

**After (Fixed):**
```python
auth = base64.b64encode(f"{username}:{password}".encode("utf-8"))
headers = {"Authorization": f"Basic {auth.decode('utf-8')}"}  # Results in "Basic base64string"
```

### Solution
Added `.decode('utf-8')` to properly convert the base64 bytes to a string in both `do_get()` and `do_post()` functions.

## Schema Validation Fixes

### Issue
Pydantic validation errors occurred because several device fields that were marked as required in the schema are actually optional in the Sigfox API responses.

### Fields Made Optional
In the `Device` model in `schemas.py`:
- `sequenceNumber: int` → `sequenceNumber: Optional[int] = None`
- `lastCom: int` → `lastCom: Optional[int] = None` 
- `activationTime: int` → `activationTime: Optional[int] = None`

In the `Option` model:
- `parameters: Dict[str, Any]` → `parameters: Optional[Dict[str, Any]] = None`

### Impact
These changes allow the library to handle real-world API responses where devices may not have all fields populated, particularly for newly registered or inactive devices.

## Testing Results

The comprehensive test successfully processed:
- ✅ 15 contracts
- ✅ 515 devices total
- ✅ All authentication calls returning 200 OK
- ✅ All schema validation passing

## Files Modified
1. `sigfox_manager/utils/http_utils.py` - Fixed authentication header encoding
2. `sigfox_manager/models/schemas.py` - Made device fields optional as needed

## Verification
Created `test_auth_fix.py` which confirms:
- Authentication works correctly
- Device retrieval works for all contracts
- Schema validation handles optional fields properly
- Real-world API responses are parsed successfully