# This file makes the 'app_designer' directory a Python package.

# Expose key modules or variables for easier import if desired
# from . import config # This makes 'app_designer.config' available
# from .orchestrator import Orchestrator

VERSION = "0.1.1" # Incremented version

# It's generally not recommended to have print statements at the top level
# of __init__.py files for libraries/packages, as they execute on import.
# Logging is preferred if startup information is needed.
# print(f"app_designer package (version {VERSION}) loaded.")

# If you want to make config directly available as `app_designer.config`
# you can do `from . import config`
# If you want its members directly available, that's less common for config.
# For example, to make `app_designer.DEFAULT_GEMINI_MODEL` available:
# from .config import DEFAULT_GEMINI_MODEL

# For now, just ensuring the directory is treated as a package is sufficient.
# Child modules will use relative imports like `from . import config`.
pass
