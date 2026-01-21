# Release Checklist for PyPI and GitHub

This checklist ensures a smooth release process for Context-as-a-Service.

## Pre-Release Checklist

### 1. Version Updates
- [ ] Update version in `caas/__init__.py`
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `setup.py`
- [ ] Update `CHANGELOG.md` with release notes

### 2. Documentation
- [ ] README badges are up-to-date
- [ ] All documentation is current
- [ ] Examples in README work correctly
- [ ] API documentation is generated and accessible

### 3. Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Linting passes: `ruff check caas/ tests/`
- [ ] Code formatting passes: `black --check caas/ tests/`
- [ ] Type checking passes (if enabled): `mypy caas/`
- [ ] CI/CD pipeline is green

### 4. Package Building
- [ ] Clean build artifacts: `rm -rf dist/ build/ *.egg-info`
- [ ] Build package: `python -m build`
- [ ] Validate package: `twine check dist/*`
- [ ] Test installation in fresh venv:
  ```bash
  python -m venv test_env
  source test_env/bin/activate
  pip install dist/*.whl
  python -c "import caas; print(caas.__version__)"
  deactivate
  rm -rf test_env
  ```

### 5. Docker
- [ ] Docker build succeeds: `docker build -t context-as-a-service:latest .`
- [ ] Docker compose works: `docker-compose up`
- [ ] Health check passes: `curl http://localhost:8000/health`

## Release Process

### Option A: GitHub Release (Recommended - Triggers Auto-Publish)

1. **Create and Push Git Tag**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Create GitHub Release**
   - Go to: https://github.com/imran-siddique/context-as-a-service/releases/new
   - Select tag: `v0.1.0`
   - Release title: `v0.1.0 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

3. **Automated Actions**
   - GitHub Actions will automatically:
     - Build the package
     - Run tests
     - Publish to PyPI
     - Upload signed artifacts to GitHub Release

4. **Verify Release**
   - Check PyPI: https://pypi.org/project/context-as-a-service/
   - Test install: `pip install context-as-a-service`
   - Verify version: `python -c "import caas; print(caas.__version__)"`

### Option B: Manual PyPI Upload (Backup Method)

If automated publishing fails, use this manual process:

1. **Set up PyPI credentials**
   ```bash
   # Create ~/.pypirc file
   cat > ~/.pypirc << EOF
   [pypi]
   username = __token__
   password = pypi-YOUR-API-TOKEN-HERE
   EOF
   chmod 600 ~/.pypirc
   ```

2. **Build and Upload**
   ```bash
   # Clean and build
   rm -rf dist/ build/ *.egg-info
   python -m build
   
   # Check
   twine check dist/*
   
   # Upload to PyPI
   twine upload dist/*
   ```

3. **Verify on PyPI**
   - Visit: https://pypi.org/project/context-as-a-service/
   - Test install: `pip install context-as-a-service`

### Option C: Test on TestPyPI First

For testing before publishing to main PyPI:

1. **Trigger GitHub Action**
   - Go to: Actions → "Publish to PyPI"
   - Click "Run workflow"
   - Check "Publish to TestPyPI"
   - Click "Run workflow"

2. **Test Installation from TestPyPI**
   ```bash
   pip install -i https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     context-as-a-service
   ```

3. **Verify**
   ```bash
   python -c "import caas; print(caas.__version__)"
   caas --help
   ```

4. **If successful, proceed with main PyPI release**

## Post-Release Checklist

### 1. Verify Installation
- [ ] Install works: `pip install context-as-a-service`
- [ ] CLI works: `caas --help`
- [ ] Python import works: `import caas`
- [ ] Version is correct: `caas.__version__`

### 2. Update Documentation
- [ ] PyPI page looks correct
- [ ] README badges show correct version
- [ ] Documentation links work
- [ ] Docker image builds with new version

### 3. Announce Release
- [ ] Update README with installation instructions
- [ ] Post in project channels (Slack, Discord, etc.)
- [ ] Tweet/social media announcement (if applicable)
- [ ] Update project website (if applicable)

### 4. Monitor
- [ ] Watch PyPI download stats
- [ ] Monitor GitHub issues for release-related problems
- [ ] Check CI/CD is still green
- [ ] Verify Docker Hub build (if configured)

## Troubleshooting

### Build Fails
```bash
# Clean everything
rm -rf dist/ build/ *.egg-info __pycache__ .pytest_cache .ruff_cache .mypy_cache

# Reinstall build tools
pip install --upgrade build twine

# Try again
python -m build
```

### Upload Fails
- Check PyPI credentials
- Verify package name isn't taken
- Ensure version number is unique (can't re-upload same version)
- Check file sizes (PyPI has limits)

### Tests Fail After Release
- Ensure all dependencies are specified correctly
- Check version constraints aren't too strict
- Test in fresh environment
- Verify optional dependencies are truly optional

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Breaking changes
- **MINOR** version (0.1.0): New features (backwards compatible)
- **PATCH** version (0.0.1): Bug fixes

Current version: **0.1.0** (Initial release)

## Rollback Procedure

If a release has critical issues:

1. **Yank the release on PyPI** (doesn't delete, but marks as unusable)
   - Go to PyPI project page
   - Click "Manage" → "Releases"
   - Click "Options" → "Yank release"

2. **Fix the issue**
   - Create hotfix branch
   - Fix bug
   - Bump patch version

3. **Release new version**
   - Follow release process above
   - Document what was fixed

## Contacts

- **PyPI Package**: https://pypi.org/project/context-as-a-service/
- **GitHub Releases**: https://github.com/imran-siddique/context-as-a-service/releases
- **Issues**: https://github.com/imran-siddique/context-as-a-service/issues

---

*Last Updated: January 21, 2026*
