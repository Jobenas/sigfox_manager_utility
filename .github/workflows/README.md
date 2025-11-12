# GitHub Actions Workflows

This directory contains automated workflows for the project.

## Workflows

### 1. `test.yml` - Run Tests
**Trigger**: Push to main/develop, Pull Requests to main

Runs the test suite across Python 3.8-3.12 and uploads coverage reports.

### 2. `release.yml` - Build and Release
**Trigger**: Git tag push (e.g., `v0.3.0`)

Automatically:
- Builds the package (wheel + source)
- Creates a GitHub Release
- Uploads build artifacts to the release

**Usage**:
```bash
git tag v0.3.0
git push origin v0.3.0
```

### 3. `publish-pypi.yml` - Publish to PyPI
**Trigger**: GitHub Release published

Automatically publishes the package to PyPI when a release is created.

**Setup Required**:
1. Go to GitHub repository Settings → Secrets and variables → Actions
2. Add secret: `PYPI_API_TOKEN` with your PyPI token

## Complete Release Process

### Option A: Automated (Recommended)
```bash
# 1. Update version in code
# 2. Commit and push changes
git add .
git commit -m "Release v0.3.0"
git push

# 3. Create and push tag
git tag v0.3.0
git push origin v0.3.0

# GitHub Actions will automatically:
# - Run tests
# - Build packages
# - Create GitHub Release with artifacts
# - Publish to PyPI
```

### Option B: Manual
```bash
# Build locally
python -m build

# Create release manually on GitHub
# Upload dist files

# Publish to PyPI
twine upload dist/*
```

## Setting Up PyPI Token Secret

1. Go to https://github.com/Jobenas/sigfox_manager_utility/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI API token (starts with `pypi-...`)
5. Click "Add secret"
