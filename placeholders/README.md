# Placeholder Packages Directory

## Purpose

This directory contains placeholder packages that are published to PyPI to **reserve and protect** important package names for the Stinger AI Guardrails Framework project. This is an intentional security measure to prevent name squatting and protect users from potentially malicious packages.

## Why Placeholder Packages?

1. **Security**: Prevents bad actors from registering similar names that could confuse users
2. **Brand Protection**: Reserves key package names associated with the Stinger project
3. **User Safety**: Ensures users who accidentally type the wrong package name are directed to the correct package
4. **Future Flexibility**: Reserves names we might want to use in the future

## Current Placeholder Packages

### 1. `stinger`
- **Reserved Name**: `stinger`
- **Redirects To**: `stinger-guardrails`
- **Purpose**: Many users might naturally try `pip install stinger` first

### 2. `stinger-guardrails`
- **Reserved Name**: `stinger-guardrails`
- **Status**: Main package (coming soon)
- **Purpose**: The official package name for the Stinger framework

## How It Works

1. Each placeholder is a minimal Python package with just a README
2. The README clearly directs users to the correct package
3. No functional code is included - these are name reservations only
4. Published to PyPI to claim the namespace

## Building and Publishing

Use the `build_placeholders.sh` script to build all placeholder packages:

```bash
./build_placeholders.sh
```

## Important Notes

- These packages contain NO functional code
- They exist solely to protect the namespace
- Users are always directed to the correct, functional package
- This is a common and recommended practice for open source projects

## Security Best Practice

This approach follows security best practices recommended by:
- Python Software Foundation
- Open Source Security Foundation (OpenSSF)
- Various security researchers and package maintainers

By proactively reserving related package names, we prevent:
- Typosquatting attacks
- Dependency confusion attacks
- Brand impersonation
- User confusion

---

For the actual Stinger AI Guardrails Framework, please visit:
- **GitHub**: https://github.com/virtualsteve-star/stinger
- **PyPI**: https://pypi.org/project/stinger-guardrails/ (coming soon)
- **Alpha**: https://pypi.org/project/stinger-guardrails-alpha/