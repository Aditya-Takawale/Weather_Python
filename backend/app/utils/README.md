# DEPRECATED - Legacy Code

This folder contains utilities that have been moved to **core/** module.

## New Location

All utilities have been reorganized:

- `logger.py` → `core/logging/logger.py`
- `helpers.py` → `core/utils/helpers.py`

## Updated Import Paths

**Old (DEPRECATED):**
```python
from app.utils.logger import get_logger
from app.utils.helpers import safe_float, safe_int
```

**New (CURRENT):**
```python
from app.core.logging import get_logger
from app.core.utils import safe_float, safe_int
```

See `ARCHITECTURE_PATTERN.md` for the full architecture documentation.
