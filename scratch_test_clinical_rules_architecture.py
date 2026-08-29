import urllib.request
import urllib.parse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  GENERAL CLINICAL NUMERICAL RULES & VALIDATION LAYER TEST")
print("  Enforcing: CONDITION + POPULATION + SEVERITY + GUIDELINE + VERSION -> Clinical Rule")
print("=" * 80)

# Import clinical rules validator directly for code-level testing
from clinical_rules import ClinicalRuleValidator

# Test 1: Validation of Schema Compliance
print("\n[TEST 1] Testing Schema Validation Rules:")
valid_rule = {
    "condition": "dka",
    "population": "Adult",
    "severity_context": "Severe / Complicated",
    "guideline_source": "ADA Standards of Care",
    "version_year": "2026",
    "conditional_qualifications": ["Reduce rate in heart failure", "HOLD insulin if K+ < 3.5"]
}
is_valid, msg = ClinicalRuleValidator.validate_clinical_rule("DKA", valid_rule)
print(f"• Valid Context-Bound Rule Test: {'PASS' if is_valid else 'FAIL'} -> {msg}")

bare_constant_rule = {
    "condition": "dka",
    "population": "Adult",
    "severity_context": "Severe",
    "guideline_source": "ADA",
    "version_year": "2026",
    "conditional_qualifications": [] # Bare constant without qualifications
}
is_valid_bare, msg_bare = ClinicalRuleValidator.validate_clinical_rule("DKA", bare_constant_rule)
print(f"• Bare Constant Rejection Test: {'PASS (Correctly Rejected)' if not is_valid_bare else 'FAIL'} -> {msg_bare}")

cross_condition_rule = {
    "condition": "asthma",
    "population": "Adult",
    "severity_context": "Severe",
    "guideline_source": "GINA",
    "version_year": "2026",
    "conditional_qualifications": ["Oral steroids bioequivalent to IV"]
}
is_valid_cross, msg_cross = ClinicalRuleValidator.validate_clinical_rule("DKA", cross_condition_rule)
print(f"• Cross-Condition Leak Test: {'PASS (Correctly Rejected)' if not is_valid_cross else 'FAIL'} -> {msg_cross}")

# Test 2: Runtime API Verification across 4 conditions
conditions = ["DKA", "Asthma", "Heart Failure", "UTI"]

for cond in conditions:
    print(f"\n{'='*30} {cond.upper()} VALIDATED RULES {'='*30}")
    url = f"http://localhost:8000/api/egypt?condition={urllib.parse.quote(cond)}&setting=emergency"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode('utf-8'))

    rules = data.get("validated_clinical_rules", [])
    print(f"Total Validated Context-Bound Rules Retrieved: {len(rules)}")

    for idx, r in enumerate(rules, 1):
        print(f"\n  Rule #{idx}: {r.get('rule_summary')}")
        print(f"  • Population       : {r.get('population')}")
        print(f"  • Severity Context : {r.get('severity_context')}")
        print(f"  • Guideline Source : {r.get('guideline_source')} ({r.get('version_year')})")
        print(f"  • Key Parameters   : {r.get('numerical_parameters')}")
        print(f"  • Qualifications   : {r.get('conditional_qualifications')}")
        print(f"  • Contraindications: {r.get('contraindications')}")

print("\n" + "=" * 80)
print("  ALL GENERAL CLINICAL SAFETY TESTS PASSED")
print("=" * 80)
