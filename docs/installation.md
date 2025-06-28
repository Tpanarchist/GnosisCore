# Installation & Setup

This guide explains how to install and set up GnosisCore for development and usage.

## Prerequisites

- Python 3.8 or newer
- Git (for cloning the repository)
- Recommended: Virtual environment tool (venv, virtualenv, or conda)

## Installation Steps

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/GnosisCore.git
   cd GnosisCore
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```sh
   python -m unittest discover tests
   ```

## Directory Structure

- `gnosiscore/` — Core source code
- `configs/` — Configuration files
- `tests/` — Unit tests
- `docs/` — Documentation

## Notes

- For development, ensure your editor uses UTF-8 encoding and follows PEP8 style guidelines.
- If you encounter issues, check the [Changelog](changelog.md) and [Testing Instructions](testing.md).
