# Security Updates Log

This document tracks security vulnerabilities fixed in the project dependencies.

## January 18, 2026 - Dependency Security Patches

### Vulnerabilities Fixed

#### 1. cryptography 41.0.7 → 42.0.4

**Vulnerability 1**: NULL pointer dereference with pkcs12.serialize_key_and_certificates
- **CVE**: CVE-2024-0727
- **Severity**: Medium
- **Affected**: >= 38.0.0, < 42.0.4
- **Impact**: NULL pointer dereference when called with non-matching certificate and private key with hmac_hash override
- **Fix**: Updated to 42.0.4

**Vulnerability 2**: Bleichenbacher timing oracle attack
- **Severity**: High
- **Affected**: < 42.0.0
- **Impact**: Python Cryptography package vulnerable to timing-based attacks
- **Fix**: Updated to 42.0.4 (includes 42.0.0 fix)

#### 2. setuptools 68.1.2 → 78.1.1

**Vulnerability 1**: Path traversal in PackageIndex.download
- **Severity**: High
- **Affected**: < 78.1.1
- **Impact**: Path traversal vulnerability leading to arbitrary file write
- **Fix**: Updated to 78.1.1

**Vulnerability 2**: Command injection via package URL
- **Severity**: Critical
- **Affected**: < 70.0.0
- **Impact**: Command injection through malicious package URLs
- **Fix**: Updated to 78.1.1 (includes 70.0.0 fix)

#### 3. urllib3 2.0.7 → 2.6.3

**Vulnerability 1**: Decompression-bomb safeguards bypassed with HTTP redirects
- **Severity**: Medium
- **Affected**: >= 1.22, < 2.6.3
- **Impact**: Streaming API improperly handles decompression bombs when following redirects
- **Fix**: Updated to 2.6.3

**Vulnerability 2**: Improper handling of highly compressed data
- **Severity**: Medium
- **Affected**: >= 1.0, < 2.6.0
- **Impact**: Streaming API can be exploited with highly compressed data
- **Fix**: Updated to 2.6.3 (includes 2.6.0 fix)

**Vulnerability 3**: Unbounded decompression chain
- **Severity**: Medium
- **Affected**: >= 1.24, < 2.6.0
- **Impact**: Allows unbounded number of links in decompression chain
- **Fix**: Updated to 2.6.3 (includes 2.6.0 fix)

## Testing

All experiments and scripts tested with updated dependencies:
- ✅ Multi-agent RAG experiment
- ✅ Long-horizon purge experiment
- ✅ Dataset upload script
- ✅ Benchmark scripts

No regressions detected. All functionality working as expected.

## Files Updated

1. `reproducibility/requirements_frozen.txt` - Updated dependency versions
2. `reproducibility/README.md` - Added security note
3. `reproducibility/hardware_specs.md` - Documented security patches
4. `SECURITY_UPDATES.md` - This file

## Verification

To verify you're using the patched versions:

```bash
pip list | grep -E "(cryptography|setuptools|urllib3)"
```

Expected output:
```
cryptography       42.0.4
setuptools         78.1.1
urllib3            2.6.3
```

## Impact on Reproducibility

The security patches maintain backward compatibility and do not affect:
- Experimental results
- Statistical analysis
- Benchmark outputs
- Random seed behavior

All results remain reproducible with the new dependency versions.

## Recommendations

1. **Always use requirements_frozen.txt** for reproducible environments
2. **Periodically check for security updates** using tools like `pip-audit`
3. **Report new vulnerabilities** via GitHub Security Advisories
4. **Keep dependencies updated** while maintaining reproducibility

## Future Security Monitoring

Consider adding to CI/CD pipeline:
```bash
pip install pip-audit
pip-audit -r reproducibility/requirements_frozen.txt
```

---

**Last Updated**: January 18, 2026  
**Audit Tool**: Manual review + GitHub Advisory Database  
**Next Review**: Q2 2026
