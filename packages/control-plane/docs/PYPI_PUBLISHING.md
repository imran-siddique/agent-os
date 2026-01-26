# PyPI Publishing Guide

This guide explains how to publish Agent Control Plane to PyPI.

## Prerequisites

### 1. PyPI Account Setup
- Create accounts on:
  - [PyPI](https://pypi.org/account/register/) (production)
  - [Test PyPI](https://test.pypi.org/account/register/) (testing)
- Enable 2FA on both accounts
- Generate API tokens:
  - PyPI: Account Settings → API tokens → Add API token (scope: entire account or specific project)
  - Test PyPI: Same process

### 2. GitHub Secrets
Add the following secrets to the GitHub repository:
- `PYPI_API_TOKEN` - Your PyPI API token
- `TEST_PYPI_API_TOKEN` - Your Test PyPI API token

Go to: Repository Settings → Secrets and variables → Actions → New repository secret

## Publishing Workflow

### Option 1: Automatic Publishing (Recommended)

When you create a new GitHub release, the package is automatically published to PyPI.

1. **Update Version**
   ```bash
   # Update version in both files:
   # - pyproject.toml (line 7)
   # - setup.py (line 16)
   ```

2. **Update CHANGELOG.md**
   ```bash
   # Add new version section at the top
   ## [X.Y.Z] - YYYY-MM-DD
   ### Added
   - New features...
   ### Changed
   - Changes...
   ### Fixed
   - Bug fixes...
   ```

3. **Create Git Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

4. **Workflow Triggers**
   - The `release.yml` workflow creates a GitHub release
   - The `publish.yml` workflow publishes to PyPI
   - Both workflows run automatically

### Option 2: Manual Publishing

For manual control or testing:

1. **Test Locally**
   ```bash
   # Install build tools
   pip install build twine
   
   # Build the package
   python -m build
   
   # Check the build
   twine check dist/*
   
   # Test upload to Test PyPI
   twine upload --repository testpypi dist/*
   
   # Test installation from Test PyPI
   pip install --index-url https://test.pypi.org/simple/ agent-control-plane
   ```

2. **Publish to PyPI**
   ```bash
   # Upload to production PyPI
   twine upload dist/*
   
   # Enter your PyPI username (__token__) and API token when prompted
   ```

3. **Manual Workflow Dispatch**
   - Go to Actions → Publish to PyPI → Run workflow
   - Choose branch and Test PyPI option
   - Click "Run workflow"

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Pre-release Versions
- **Alpha**: `1.2.0a1`, `1.2.0a2`
- **Beta**: `1.2.0b1`, `1.2.0b2`
- **Release Candidate**: `1.2.0rc1`, `1.2.0rc2`

## Pre-release Checklist

Before publishing a new version:

- [ ] Update version in `pyproject.toml` and `setup.py`
- [ ] Update `CHANGELOG.md` with new version section
- [ ] Update `README.md` if necessary
- [ ] Run full test suite: `python -m pytest tests/ -v`
- [ ] Test installation locally: `pip install -e .`
- [ ] Test examples: `python examples/basic_usage.py`
- [ ] Review documentation for accuracy
- [ ] Create git tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
- [ ] Push tag: `git push origin vX.Y.Z`

## Post-release Checklist

After successful publication:

- [ ] Verify package on PyPI: https://pypi.org/project/agent-control-plane/
- [ ] Test installation: `pip install agent-control-plane==X.Y.Z`
- [ ] Verify GitHub release: https://github.com/imran-siddique/agent-control-plane/releases
- [ ] Announce in GitHub Discussions
- [ ] Update social media / blog if applicable
- [ ] Monitor for any issues

## Package Metadata

### Files Included in Distribution
Controlled by `MANIFEST.in`:
- README.md, LICENSE, CHANGELOG.md
- All Python files in `src/agent_control_plane/`
- Documentation in `docs/`
- Examples in `examples/`

### Files Excluded
- Tests (`tests/`)
- CI/CD configuration (`.github/`)
- Development files (`.gitignore`, etc.)
- Temporary and cache files

## Troubleshooting

### Common Issues

1. **"File already exists"**
   - You cannot overwrite a version on PyPI
   - Increment the version number

2. **"Invalid distribution"** or **"license-file" warning**
   - `twine check` may show warnings about the `license-file` field
   - This is a known issue with twine's validation being stricter than PyPI's requirements
   - The package will upload successfully to PyPI despite this warning
   - Run `twine check dist/* || true` to suppress the error

3. **"Authentication failed"**
   - Verify API token is correct
   - Check token has correct scope (project vs. entire account)
   - Ensure using `__token__` as username

4. **GitHub Actions failing**
   - Verify secrets are configured correctly
   - Check workflow logs for specific errors
   - Ensure tag format is `vX.Y.Z`

### Getting Help

- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)

## Security Notes

- **Never commit API tokens** to version control
- Use GitHub Secrets for CI/CD
- Enable 2FA on PyPI account
- Use token authentication (not username/password)
- Regularly rotate API tokens
- Use Test PyPI for testing before production

## Additional Resources

- [PyPI Official Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

*Last updated: January 18, 2026*
