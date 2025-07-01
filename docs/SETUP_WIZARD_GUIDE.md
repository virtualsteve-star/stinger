# Stinger Setup Wizard Guide

## Overview

The Stinger Setup Wizard provides an interactive, guided experience for new users to configure their environment and get started quickly. The wizard handles environment validation, API key configuration, and initial testing.

## Running the Setup Wizard

### Method 1: First Run Experience
When you run `stinger` for the first time without any arguments, you'll be prompted to run the setup wizard:

```bash
$ stinger
🎉 Welcome to Stinger Guardrails Framework!
============================================================

It looks like this is your first time using Stinger.
Let's get you set up!

Would you like to run the setup wizard? (recommended) [Y/n]: 
```

### Method 2: Direct Command
You can run the setup wizard at any time:

```bash
stinger setup
```

### Method 3: Quick Start Script
Use the provided quick start script:

```bash
./quickstart.py
```

## What the Setup Wizard Does

### 1. Environment Check
- Verifies Python version (3.8+)
- Checks if running in virtual environment
- Validates core dependencies (PyYAML, jsonschema, cryptography)
- Offers to install missing dependencies

### 2. API Key Configuration
The wizard helps configure OpenAI API keys for AI-powered guardrails:

#### Option 1: Environment Variable
- Guides you through setting OPENAI_API_KEY
- Can create a .env file in current directory
- Provides shell profile instructions

#### Option 2: macOS Keychain (macOS only)
- Securely stores API key in system keychain
- Provides retrieval commands for shell profile

#### Option 3: Skip
- Allows skipping for users only using local guardrails

### 3. Sample Configuration Creation
Creates example files in `~/.stinger/`:

```
~/.stinger/
├── config.json           # User preferences
└── samples/
    ├── sample_pipeline.yaml    # Example pipeline config
    └── blocked_keywords.txt    # Example keyword list
```

### 4. Installation Test
Runs basic tests to verify:
- Core modules import correctly
- Basic guardrail functionality works
- Safe content passes
- Harmful content is blocked

## Setup Wizard Output

### Successful Setup
```
✅ Setup Complete!
==================================================

📚 Next Steps:

1. Try the demo:
   stinger demo

2. Check a prompt:
   stinger check-prompt "Your text here"

3. View health status:
   stinger health

4. Explore examples:
   - Check the examples/ directory
   - View samples in ~/.stinger/samples/

5. Read the documentation:
   https://github.com/virtualsteve-star/stinger
```

## Configuration Files

### User Config (`~/.stinger/config.json`)
```json
{
  "default_preset": "customer_service",
  "audit_enabled": true,
  "samples_dir": "/Users/you/.stinger/samples"
}
```

### Sample Pipeline (`~/.stinger/samples/sample_pipeline.yaml`)
```yaml
input_guardrails:
  - type: keyword_list
    keywords: ["hack", "exploit", "injection"]
  - type: length
    max_length: 1000
  - type: pii_detection
    enabled: true

output_guardrails:
  - type: toxicity
    threshold: 0.7
  - type: code_generation
    allowed: false
```

## API Key Management

### Environment Variable Method
Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### macOS Keychain Method
Add to your shell profile:
```bash
export OPENAI_API_KEY=$(security find-generic-password -w -s openai-api-key)
```

### Using .env File
Create `.env` in your project:
```
OPENAI_API_KEY=your-api-key-here
```

## Troubleshooting

### Missing Dependencies
If dependencies are missing, the wizard will offer to install them:
```
⚠️  Missing dependencies: PyYAML, jsonschema
Would you like to install them now? (y/n): y
```

### API Key Issues
- Ensure your API key is valid
- Check environment variable is set correctly
- For macOS Keychain, verify key is stored: `security find-generic-password -s openai-api-key`

### Import Errors
If imports fail during testing:
1. Ensure Stinger is installed: `pip install stinger-guardrails-alpha`
2. Check you're in the correct environment
3. Verify Python version is 3.8+

## Skipping First Run

To skip the first run experience:
```bash
export STINGER_SKIP_FIRST_RUN=1
```

Or if you've already run it, it won't show again (tracked in `~/.stinger/.first_run_complete`).

## Advanced Usage

### Custom Configuration Directory
The setup wizard uses `~/.stinger/` by default. This can be customized by modifying the `SetupWizard` class.

### Programmatic Usage
```python
from stinger.cli.setup_wizard import SetupWizard

wizard = SetupWizard()
success = wizard.run()
```

## Next Steps After Setup

1. **Test Basic Functionality**
   ```bash
   stinger demo
   ```

2. **Check Your First Prompt**
   ```bash
   stinger check-prompt "Hello, can you help me hack a system?"
   ```

3. **Explore Examples**
   - Review generated samples in `~/.stinger/samples/`
   - Check the `examples/` directory in the repository

4. **Configure Your Pipeline**
   - Modify sample configurations for your use case
   - Create custom guardrail combinations

---

The setup wizard is designed to get you from installation to first guardrail check in under 2 minutes!