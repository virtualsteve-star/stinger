# API Key Handling Guide

## 🔑 Recommended Way to Handle API Keys (for Developers & Cursor Users)

### 1. **Set Your API Key Securely (macOS/Unix, e.g., Cursor, VSCode, Terminal)**

For development, we recommend storing your API key securely using your system's keychain or environment variable system. On macOS, the best practice is to use the Keychain and expose the key as an environment variable:

#### **macOS Keychain (Recommended for Cursor/AI Devs)**

1. **Store your key in the Keychain and expose it as an environment variable:**

    ```bash
    # Replace sk-... with your actual key
    security add-generic-password -a "$USER" -s openai-api-key -w 'sk-...'
    launchctl setenv OPENAI_API_KEY $(security find-generic-password -w -s openai-api-key)
    launchctl getenv OPENAI_API_KEY  # (Optional) Verify
    ```

2. **You only need to do this once per login session.**

#### **Alternative: .env File (for local scripts, not recommended for shared repos)**

- Create a `.env` file in your project root:
    ```env
    OPENAI_API_KEY=sk-...
    ```
- Use a tool like [`python-dotenv`](https://pypi.org/project/python-dotenv/) to load it, or source it in your shell.
- **Never commit `.env` files with secrets to version control!**

### 2. **How the Key is Picked Up**

- The Stinger system automatically looks for the `OPENAI_API_KEY` environment variable at startup.
- You do **not** need to put your key in YAML config files. If you use `${OPENAI_API_KEY}` in a config, it will be substituted automatically.
- The centralized API key manager loads the key from the environment and makes it available to all filters and services.

---

## 🏢 **How the Centralized Key Manager Works**

- On startup, the key manager checks for `OPENAI_API_KEY` (and other supported keys) in the environment.
- It securely stores the key in memory for the duration of the process.
- All AI filters (code generation, PII, toxicity, etc.) and any other service that needs an API key **must** use the centralized manager to access the key.
- The manager supports additional services (e.g., Azure, Anthropic) via their own environment variables (e.g., `AZURE_OPENAI_API_KEY`).

---

## 🛠️ **How to Use the Centralized Key Manager in Code**

**For any service or filter that needs an API key:**

```python
from src.stinger.core.api_key_manager import get_api_key, get_openai_key

# For OpenAI
api_key = get_openai_key()

# For other services
azure_key = get_api_key('azure_openai')
anthropic_key = get_api_key('anthropic')
```

- **Do not** read API keys directly from config files or environment variables in your own code—always use the centralized manager.
- The manager will handle validation, secure storage, and future enhancements (like rotation or encryption).

---

## 🔒 **Security Best Practices**

- **Never commit API keys or secrets to version control.**
- Use your system's secure storage (Keychain, Windows Credential Manager, etc.) whenever possible.
- Use environment variables for ephemeral, session-based key access.
- Always use the centralized key manager for all key access in Stinger.

---

For more details, see the [API Key Security Fix Plan](../plans/API_Key_Security_Fix_Plan.md) and the code in `src/stinger/core/api_key_manager.py`. 