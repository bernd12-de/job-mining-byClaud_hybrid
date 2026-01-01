import requests
import json

# Use localhost when running from host (docker publishes ports)
KOTLIN = 'http://localhost:8080'
PYTHON = 'http://localhost:8000'

CHECKS = [
    # Kotlin
    (f"{KOTLIN}/api/v1/rules/stats", 'GET', 200, ['total_skills','ssot_skills_total']),
    (f"{KOTLIN}/api/v1/rules/esco-full", 'GET', 200, None),
    (f"{KOTLIN}/api/v1/rules/blacklist", 'GET', 200, None),
    (f"{KOTLIN}/api/v1/rules/role-mappings", 'GET', 200, None),
    (f"{KOTLIN}/api/v1/rules/industry-mappings", 'GET', 200, None),
    (f"{KOTLIN}/api/v1/test-python", 'GET', 200, None),
    (f"{KOTLIN}/api/v1/jobs/admin/system-health", 'GET', 200, None),

    # Python
    (f"{PYTHON}/system/status", 'GET', 200, ['status','skills_loaded']),
    (f"{PYTHON}/role-mappings", 'GET', 200, ['count','mappings']),
    (f"{PYTHON}/internal/admin/refresh-knowledge", 'POST', 200, ['status','skills']),
    (f"{PYTHON}/batch-process", 'POST', 200, ['status','count']),
]


def run_check(url, method='GET', expected_code=200, expected_keys=None):
    try:
        if method == 'GET':
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, timeout=30)
    except Exception as e:
        return False, f"Request to {url} failed: {e}"

    if r.status_code != expected_code:
        return False, f"{url} returned HTTP {r.status_code} (expected {expected_code})"

    if expected_keys:
        try:
            j = r.json()
        except Exception as e:
            return False, f"{url} returned non-json response: {e}"
        missing = [k for k in expected_keys if k not in j]
        if missing:
            return False, f"{url} missing keys: {missing}"

    return True, "OK"


if __name__ == '__main__':
    results = []
    for url, method, code, keys in CHECKS:
        ok, msg = run_check(url, method, code, keys)
        results.append((url, ok, msg))
        print(url, '->', 'OK' if ok else 'FAIL', '-', msg)

    fails = [r for r in results if not r[1]]
    print('\nSUMMARY:')
    print(f"Total checks: {len(results)}, Failures: {len(fails)}")
    if fails:
        for f in fails:
            print('FAIL:', f[0], f[2])
    exit(1 if fails else 0
)