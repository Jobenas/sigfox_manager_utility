# Sigfox Manager Release Notes

## Version 0.2.0 - Enhanced Pagination Support

### 🚀 Major Features Added

#### Automatic Pagination Handling
- **Enhanced `get_devices_by_contract()`**: Now supports `fetch_all_pages` parameter
- **Enhanced `get_contracts()`**: Now supports `fetch_all_pages` parameter  
- **Automatic page traversal**: Fetches all pages automatically when `fetch_all_pages=True` (default)
- **Backward compatibility**: Existing code continues to work unchanged
- **Massive data retrieval**: Can now fetch thousands of devices instead of being limited to first 100

#### Real-world Impact
- **Before**: Limited to ~100 devices per contract (first page only)
- **After**: Retrieves ALL devices (tested with 3,178+ devices from single contract)
- **Example**: EAT-ELECTRODUNAS contract went from 100 → 3,178 devices (31× improvement!)

#### New Method Signatures
```python
# Get all pages (default behavior)
devices = mgr.get_devices_by_contract(contract_id)

# Get only first page (for performance-critical scenarios)  
devices = mgr.get_devices_by_contract(contract_id, fetch_all_pages=False)

# Same for contracts
contracts = mgr.get_contracts()  # All pages
contracts = mgr.get_contracts(fetch_all_pages=False)  # First page only
```

### 🔧 Performance Considerations
- **Default behavior**: Fetches all pages for completeness
- **Performance option**: Set `fetch_all_pages=False` for faster response when only first page needed
- **Smart pagination**: Automatically handles Sigfox API pagination URLs
- **Error resilience**: Gracefully handles pagination failures

---

## Version 0.1.1 - Authentication and Schema Fixes

### 🐛 Authentication Bug Fix

#### Issue
The HTTP Basic Authentication header was incorrectly formatted, causing 401 Unauthorized errors when making API calls to the Sigfox backend.

#### Root Cause
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

#### Solution
Added `.decode('utf-8')` to properly convert the base64 bytes to a string in both `do_get()` and `do_post()` functions.

### 🔧 Schema Validation Fixes

#### Issue
Pydantic validation errors occurred because several device fields that were marked as required in the schema are actually optional in the Sigfox API responses.

#### Fields Made Optional
In the `Device` model in `schemas.py`:
- `sequenceNumber: int` → `sequenceNumber: Optional[int] = None`
- `lastCom: int` → `lastCom: Optional[int] = None` 
- `activationTime: int` → `activationTime: Optional[int] = None`

In the `Option` model:
- `parameters: Dict[str, Any]` → `parameters: Optional[Dict[str, Any]] = None`

#### Impact
These changes allow the library to handle real-world API responses where devices may not have all fields populated, particularly for newly registered or inactive devices.

### 📊 Testing Results

The comprehensive test successfully processed:
- ✅ 15 contracts
- ✅ 3,232+ devices total (with pagination)
- ✅ All authentication calls returning 200 OK
- ✅ All schema validation passing
- ✅ Pagination working correctly for large datasets

### 📁 Files Modified
1. `sigfox_manager/utils/http_utils.py` - Fixed authentication header encoding
2. `sigfox_manager/models/schemas.py` - Made device fields optional as needed
3. `sigfox_manager/sigfox_manager.py` - Added pagination support

### ✅ Verification
Created comprehensive tests which confirm:
- Authentication works correctly
- Device retrieval works for all contracts
- Schema validation handles optional fields properly
- Real-world API responses are parsed successfully
- Pagination retrieves complete datasets automatically