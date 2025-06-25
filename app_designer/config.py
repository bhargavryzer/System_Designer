# app_designer/config.py

# Default Gemini Model Name
# This can be overridden by the --model_name CLI argument.
# In a more complex application, you might load this from a .env file,
# a YAML file, or other configuration sources.
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash" # Using a more recent default

# Example of other potential configurations:
# DEFAULT_TEMPERATURE = 0.7
# MAX_OUTPUT_TOKENS = 2048
# LOG_LEVEL = "INFO" # Could be read by logging setup

# Note: Avoid storing sensitive information like API keys directly in version-controlled
# config files. Use environment variables or a secrets management system for those.

print(f"Config loaded: DEFAULT_GEMINI_MODEL set to '{DEFAULT_GEMINI_MODEL}'")
