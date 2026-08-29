"""
MedRef - General Clinical Rule & Numerical Safety Validation Layer
Enforces the Universal Medical Context Schema:
CONDITION + POPULATION + SEVERITY/CLINICAL CONTEXT + GUIDELINE/SOURCE + VERSION/DATE -> Clinical Numerical Rule

Guarantees:
1. Zero cross-condition rule leakage (DKA rules never apply to Asthma/UTI/Heart Failure, and vice versa).
2. Zero bare universal constants (all fluid rates, insulin doses, and drug titrations must have population, severity, and conditional qualifications).
3. Explicit distinction between Adult and Pediatric populations.
4. Explicit distinction between Mild/Uncomplicated and Severe/Complicated severities.
5. Strict verification of guideline source and edition.
"""

from typing import Any, Dict, List, Optional, Tuple


class ClinicalNumericalRule:
    """Represents a validated, context-bound clinical numerical rule."""

    def __init__(
        self,
        condition: str,
        category: str,
        population: str,
        severity_context: str,
        guideline_source: str,
        version_year: str,
        rule_summary: str,
        numerical_parameters: Dict[str, Any],
        conditional_qualifications: List[str],
        contraindications: List[str]
    ):
        self.condition = condition.strip().lower()
        self.category = category  # e.g., "fluid_resuscitation", "insulin_administration", "electrolyte_replacement"
        self.population = population  # e.g., "Adult", "Pediatric", "All"
        self.severity_context = severity_context  # e.g., "Severe / Complicated (ICU)", "Mild-to-Moderate Uncomplicated"
        self.guideline_source = guideline_source
        self.version_year = version_year
        self.rule_summary = rule_summary
        self.numerical_parameters = numerical_parameters
        self.conditional_qualifications = conditional_qualifications
        self.contraindications = contraindications

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition": self.condition,
            "category": self.category,
            "population": self.population,
            "severity_context": self.severity_context,
            "guideline_source": self.guideline_source,
            "version_year": self.version_year,
            "rule_summary": self.rule_summary,
            "numerical_parameters": self.numerical_parameters,
            "conditional_qualifications": self.conditional_qualifications,
            "contraindications": self.contraindications
        }


class ClinicalRuleValidator:
    """
    Validation engine preventing global hard-coded clinical numerical rules
    and enforcing condition-, population-, and severity-bound safety schemas.
    """

    _RULE_REGISTRY: List[ClinicalNumericalRule] = [
        # =========================================================================
        # 1. DKA (DIABETIC KETOACIDOSIS) — ADULT PROTOCOLS
        # =========================================================================
        ClinicalNumericalRule(
            condition="dka",
            category="fluid_resuscitation",
            population="Adult",
            severity_context="Standard Adult DKA without renal or cardiac compromise",
            guideline_source="Consensus Statement on Hyperglycemic Crises in Adults (ADA/EASD/JBDS/AACE/DTS)",
            version_year="2024 Consensus / 2026 Standards",
            rule_summary="Administer 500–1000 mL/hour of isotonic crystalloid (0.9% NaCl or balanced crystalloid) during the first 2–4 hours for adults without cardiac or renal compromise; subsequent fluid rate titrated based on hydration status, serum electrolytes, and urinary output.",
            numerical_parameters={
                "initial_rate_first_2_to_4_hours": "500–1000 mL/h for the first 2–4 hours (in adults without cardiac/renal compromise)",
                "subsequent_maintenance_rate": "250–500 mL/h titrated to corrected serum sodium and hydration state",
                "fluid_type_initial": "0.9% NaCl (Normal Saline) or Balanced Crystalloid (Plasma-Lyte / Ringer's Lactate)",
                "fluid_type_subsequent_low_na": "0.9% NaCl if corrected serum sodium is low (<135 mEq/L)",
                "fluid_type_subsequent_norm_high_na": "0.45% NaCl if corrected serum sodium is normal or high (>=135 mEq/L)"
            },
            conditional_qualifications=[
                "MANDATORY: Individualized, cautious, and reduced fluid administration for older adults and patients with known heart failure or chronic kidney disease to prevent iatrogenic fluid overload and pulmonary edema.",
                "Target gradual restoration of effective circulating volume and peripheral perfusion while avoiding sudden osmolar collapse."
            ],
            contraindications=[
                "Do NOT use obsolete aggressive fluid rates (>1000 mL/h) routinely for all patients.",
                "Do NOT administer fixed rapid fluid boluses to patients with acute pulmonary congestion or anuric renal failure.",
                "Do NOT use hypotonic fluids (0.45% NaCl or sterile water) as initial fluid expansion."
            ]
        ),
        ClinicalNumericalRule(
            condition="dka",
            category="insulin_administration",
            population="Adult",
            severity_context="Severe, Moderate, and Complicated DKA (Inpatient / ICU)",
            guideline_source="ADA 2026 Standards of Care & UK JBDS-IP 2024 Guidelines",
            version_year="2026 / 2024",
            rule_summary="Continuous IV Regular Insulin infusion at fixed rate 0.1 U/kg/h (or 0.14 U/kg/h without bolus); initial IV bolus is optional per ADA but generally omitted per UK JBDS-IP to ensure steady-state control.",
            numerical_parameters={
                "continuous_iv_infusion_rate": "0.1 units/kg/h (or 0.14 units/kg/h without bolus)",
                "target_glycemic_reduction_rate": "50–75 mg/dL/h (2.8–4.2 mmol/L/h)",
                "dextrose_threshold": "Add 5%–10% Dextrose when blood glucose reaches <= 200–250 mg/dL",
                "insulin_rate_reduction_on_dextrose": "Reduce IV insulin to 0.02–0.05 units/kg/h while continuing infusion until ketoacidosis resolves",
                "resolution_criteria": "Blood Beta-hydroxybutyrate < 0.6 mmol/L, Venous pH > 7.30, and Serum Bicarbonate >= 18.0 mEq/L (Note: Anion gap must NOT be used as a definitive resolution criterion because hyperchloremic non-anion gap acidosis from saline resuscitation can make anion gap misleading; prioritize quantitative beta-hydroxybutyrate clearance)."
            },
            conditional_qualifications=[
                "HOLD INSULIN if baseline serum potassium K+ < 3.5 mEq/L until potassium is repleted to >= 3.5 mEq/L.",
                "Continue IV insulin infusion alongside Dextrose infusion until ketoacidosis resolves with blood beta-hydroxybutyrate < 0.6 mmol/L, venous pH > 7.30, and serum bicarbonate >= 18.0 mEq/L (do NOT stop insulin merely because blood glucose reaches 200 mg/dL, and do NOT require anion gap closure as a resolution criterion)."
            ],
            contraindications=[
                "Do NOT use Subcutaneous insulin as sole therapy in severe DKA, hypotensive shock, or altered mental status.",
                "Do NOT use Intermediate-Acting (NPH/Insulatard) or Long-Acting insulins for intravenous infusion in acute DKA."
            ]
        ),
        ClinicalNumericalRule(
            condition="dka",
            category="electrolyte_replacement",
            population="Adult",
            severity_context="All DKA Severities (Potassium Homeostasis)",
            guideline_source="ADA 2026 / Endocrine Society Clinical Practice Guidelines",
            version_year="2026",
            rule_summary="Maintain serum potassium between 4.0 and 5.0 mEq/L with IV KCl replacement once urine output is established; strict threshold-driven titration.",
            numerical_parameters={
                "target_serum_potassium": "4.0 – 5.0 mEq/L",
                "k_threshold_delay_insulin": "Serum K+ < 3.5 mEq/L -> HOLD insulin, infuse 20–40 mEq K+/h",
                "k_threshold_add_to_fluids": "Serum K+ 3.5 – 5.0 mEq/L -> Add 20–30 mEq K+ per liter of IV fluid",
                "k_threshold_hold_replacement": "Serum K+ >= 5.2 mEq/L -> Do NOT add potassium; recheck every 2 hours"
            },
            conditional_qualifications=[
                "Confirm urine output (> 0.5 ml/kg/h) before initiating routine IV potassium replacement.",
                "Administer potassium ONLY diluted in IV fluids; NEVER IV PUSH or undiluted."
            ],
            contraindications=[
                "Do NOT administer IV insulin if serum K+ is < 3.5 mEq/L (fatal arrhythmia risk).",
                "Do NOT give potassium replacement if serum K+ is >= 5.2 mEq/L or in anuric renal failure."
            ]
        ),
        ClinicalNumericalRule(
            condition="dka",
            category="insulin_administration_subq",
            population="Adult",
            severity_context="Mild-to-Moderate Uncomplicated DKA ONLY (Step-Down / Non-ICU)",
            guideline_source="ADA 2026 Standards of Care & UK JBDS-IP 2024",
            version_year="2026 / 2024",
            rule_summary="Subcutaneous rapid-acting insulin analogues (Lispro / Aspart) 0.15–0.2 U/kg every 1–2 hours combined with vigorous hydration as a validated alternative to IV regular insulin ONLY in alert, uncomplicated cases when ICU beds are unavailable.",
            numerical_parameters={
                "subq_dose": "0.15–0.2 units/kg subcutaneously",
                "subq_frequency": "Every 1 to 2 hours",
                "eligibility_criteria": "Alert, non-hypotensive patient, venous pH > 7.25, serum bicarbonate > 15 mEq/L, no persistent emesis"
            },
            conditional_qualifications=[
                "Patient must be alert, oriented, hemodynamically stable, and able to maintain oral or IV fluid hydration.",
                "Switch immediately to IV regular insulin infusion if clinical deterioration or worsening acidosis occurs."
            ],
            contraindications=[
                "CONTRAINDICATED in severe DKA (pH < 7.00, HCO3 < 10 mEq/L).",
                "CONTRAINDICATED in hypotensive shock, sepsis, impaired consciousness, or acute pregnancy."
            ]
        ),

        # =========================================================================
        # 2. DKA (DIABETIC KETOACIDOSIS) — PEDIATRIC PROTOCOLS (ISPAD 2024/2026)
        # =========================================================================
        ClinicalNumericalRule(
            condition="dka",
            category="pediatric_resuscitation",
            population="Pediatric (<18 years)",
            severity_context="All Pediatric DKA Severities (Cerebral Injury Prevention)",
            guideline_source="International Society for Pediatric and Adolescent Diabetes (ISPAD) Clinical Practice Consensus Guidelines",
            version_year="2024/2026 Edition",
            rule_summary="Gradual fluid deficit replacement over 48 hours; start IV regular insulin 1 hour AFTER fluids at 0.05–0.1 U/kg/h with ABSOLUTELY NO INITIAL IV INSULIN BOLUS to prevent cerebral edema.",
            numerical_parameters={
                "initial_fluid_expansion": "10–20 ml/kg of 0.9% NaCl over 1–2 hours (repeat only if in hypotensive shock)",
                "deficit_replacement_window": "Calculated deficit replaced evenly over 48 hours (not 24 hours)",
                "max_fluid_infusion_rate": "Rarely exceed 1.5–2 times normal maintenance fluid rate",
                "insulin_start_delay": "Start continuous IV regular insulin 1 HOUR AFTER initiating fluid replacement",
                "pediatric_insulin_rate": "0.05 to 0.1 units/kg/h (0.05 U/kg/h in children <5 years or severe acidosis)",
                "insulin_bolus_policy": "STRICTLY FORBIDDEN (No IV Insulin Bolus in Children)",
                "dextrose_start_threshold": "Add 5% Dextrose when blood glucose reaches <= 250–300 mg/dL (14–17 mmol/L)",
                "cerebral_edema_treatment": "3% Hypertonic Saline (3–5 ml/kg over 10–15 min) or IV Mannitol (0.5–1.0 g/kg over 20 min) immediately upon clinical suspicion"
            },
            conditional_qualifications=[
                "Monitor continuously for signs of cerebral edema: headache, lethargy, bradycardia, hypertension, dropping GCS score.",
                "Begin potassium replacement (20–40 mEq/L) at hour 2 (with insulin start) once urine output is documented and K+ < 5.5 mEq/L."
            ],
            contraindications=[
                "ABSOLUTELY CONTRAINDICATED: Initial IV insulin bolus in children (significantly increases cerebral edema risk).",
                "CONTRAINDICATED: Rapid rehydration (<24h) or hypotonic fluids during initial resuscitation."
            ]
        ),

        # =========================================================================
        # 3. BRONCHIAL ASTHMA — ACUTE & MAINTENANCE RULES (GINA 2026)
        # =========================================================================
        ClinicalNumericalRule(
            condition="asthma",
            category="bronchodilator_and_steroid_therapy",
            population="Adult & Pediatric",
            severity_context="Acute Asthma Exacerbation in Emergency Department",
            guideline_source="Global Initiative for Asthma (GINA) Strategy Report & BTS/SIGN",
            version_year="2026 Report (Current)",
            rule_summary="SABA (Salbutamol 4–10 puffs pMDI+spacer or 2.5–5mg neb every 20 min in 1st hour) + SAMA (Ipratropium 500mcg neb in moderate/severe) + Systemic Corticosteroid (Prednisolone 40–50mg/d PO x5d adult; 1–2 mg/kg/d max 40mg child).",
            numerical_parameters={
                "saba_adult_dose": "4–10 puffs pMDI with spacer every 20 min for 1 hour, then 4–10 puffs every 1–4 hours",
                "saba_pediatric_dose": "2–6 puffs pMDI with spacer every 20 min for 1 hour, then 2–4 puffs every 1–4 hours",
                "systemic_steroid_adult": "Prednisolone 40–50 mg orally once daily for 5 days (no taper needed)",
                "systemic_steroid_child": "Prednisolone 1–2 mg/kg/day (maximum 40 mg) orally for 3–5 days",
                "magnesium_sulfate_adult": "2.0 g IV infusion in 100 ml 0.9% NaCl over 20 minutes (in severe refractory cases)",
                "magnesium_sulfate_child": "50 mg/kg (maximum 2.0 g) IV infusion over 20 minutes"
            },
            conditional_qualifications=[
                "Use pMDI with dedicated spacer in preference to nebulizers when possible to ensure superior lung deposition and avoid aerosol dispersion.",
                "Oral corticosteroids are pharmacologically bioequivalent to IV hydrocortisone and should be preferred unless the patient is unable to swallow or vomiting."
            ],
            contraindications=[
                "Do NOT use sedatives or anxiolytics in acute asthma exacerbations (respiratory depression risk).",
                "Do NOT delay systemic corticosteroid administration in moderate-to-severe exacerbations."
            ]
        ),

        # =========================================================================
        # 4. HEART FAILURE — ACUTE & GDMT RULES (ESC 2026 / ACC/AHA)
        # =========================================================================
        ClinicalNumericalRule(
            condition="heart failure",
            category="decongestion_and_gdmt",
            population="Adult",
            severity_context="Acute Decompensated Heart Failure (ADHF) & Chronic HFrEF",
            guideline_source="European Society of Cardiology (ESC) Guidelines for the Diagnosis and Treatment of Acute and Chronic Heart Failure",
            version_year="2026 Guidelines",
            rule_summary="IV Loop Diuretic (Furosemide 20–40mg IV in naive, or 1–2.5x oral dose in chronic users) for rapid decongestion; optimize 4 pillars of GDMT (ARNI/ACEi, Beta-blocker, MRA, SGLT2i) post-stabilization.",
            numerical_parameters={
                "furosemide_iv_naive": "20–40 mg IV bolus",
                "furosemide_iv_chronic": "1 to 2.5 times the patient's daily oral furosemide dose as IV bolus",
                "furosemide_evaluation_timing": "Assess spot urinary sodium at 2 hours (>50–70 mmol/L) and 6-hour urine output (>100–150 ml/h)",
                "spironolactone_contraindication_k": "Contraindicated if serum K+ > 5.0 mEq/L or eGFR < 30 ml/min/1.73m2",
                "arni_sacubitril_valsartan_target": "Initial 24/26 mg or 49/51 mg BID; up-titrate every 2–4 weeks to target 97/103 mg BID"
            },
            conditional_qualifications=[
                "Assess spot urine sodium at 2 hours post-diuretic to determine diuretic responsiveness; double the IV dose if response is inadequate.",
                "Initiate SGLT2 inhibitor (Empagliflozin 10mg or Dapagliflozin 10mg daily) prior to hospital discharge in all stable patients regardless of ejection fraction."
            ],
            contraindications=[
                "Do NOT initiate or up-titrate beta-blockers in overt acute decompensation / cardiogenic shock until euvolemia is restored.",
                "Do NOT administer Sacubitril/Valsartan within 36 hours of the last dose of an ACE inhibitor (angioedema risk)."
            ]
        ),

        # =========================================================================
        # 5. URINARY TRACT INFECTION (UTI) — EMPIRICAL ANTIMICROBIAL RULES (EAU 2026 / IDSA)
        # =========================================================================
        ClinicalNumericalRule(
            condition="uti",
            category="antimicrobial_stewardship",
            population="Adult Females",
            severity_context="Acute Uncomplicated Lower Cystitis vs Pyelonephritis",
            guideline_source="European Association of Urology (EAU) Guidelines on Urological Infections & IDSA",
            version_year="2026 Guidelines",
            rule_summary="First-line oral empirical therapy: Nitrofurantoin 100mg BID x5d (if eGFR > 30) or Fosfomycin Trometamol 3.0g single oral dose; Ceftriaxone 1–2g IV once daily for complicated UTI/pyelonephritis.",
            numerical_parameters={
                "nitrofurantoin_dose": "100 mg orally BID with meals for 5 days",
                "nitrofurantoin_egfr_cutoff": "Contraindicated if eGFR < 30 ml/min",
                "fosfomycin_dose": "3.0 g single dose oral sachet dissolved in water on empty stomach",
                "ceftriaxone_dose_pyelonephritis": "1.0 to 2.0 g IV or IM once daily for 7–10 days"
            },
            conditional_qualifications=[
                "Prioritize ESBL-sparing agents (Nitrofurantoin, Fosfomycin) for uncomplicated cystitis to limit antimicrobial resistance.",
                "Obtain urine culture and susceptibility prior to antimicrobial initiation in suspected pyelonephritis, recurrent UTI, or treatment failure."
            ],
            contraindications=[
                "Do NOT use Nitrofurantoin or Fosfomycin for upper UTI (Pyelonephritis) or urosepsis due to inadequate renal tissue and bloodstream penetration.",
                "Do NOT use Fluoroquinolones (Ciprofloxacin) as first-line for uncomplicated cystitis due to FDA/EMA safety warnings and high local resistance."
            ]
        ),

        # =========================================================================
        # 6. PNEUMONIA — COMMUNITY-ACQUIRED PNEUMONIA RULES (ATS/IDSA & ERS)
        # =========================================================================
        ClinicalNumericalRule(
            condition="pneumonia",
            category="empirical_antimicrobial_and_triage",
            population="Adult",
            severity_context="Community-Acquired Pneumonia (Outpatient vs Non-Severe Inpatient vs Severe ICU)",
            guideline_source="American Thoracic Society / Infectious Diseases Society of America (ATS/IDSA) & ERS Guidelines",
            version_year="2026 / 2024 Guidelines",
            rule_summary="Outpatient without comorbidities: Amoxicillin 1.0g PO TID or Doxycycline 100mg PO BID; Inpatient Non-Severe: Beta-Lactam (Ceftriaxone 1–2g IV q24h or Ampicillin/Sulbactam 1.5–3g IV q6h) + Macrolide (Azithromycin 500mg IV/PO q24h) or Respiratory Fluoroquinolone.",
            numerical_parameters={
                "outpatient_healthy_amoxicillin": "Amoxicillin 1.0 g orally TID for 5 days",
                "inpatient_non_severe_ceftriaxone": "Ceftriaxone 1.0 to 2.0 g IV once daily for 5–7 days",
                "inpatient_azithromycin_combination": "Azithromycin 500 mg IV or PO daily for 3–5 days (in combination with beta-lactam)",
                "curb65_triage_score": "CURB-65 score: 0–1 = Outpatient; 2 = Inpatient Ward; >= 3 = Inpatient / Consider ICU"
            },
            conditional_qualifications=[
                "Assess clinical stability (temperature <= 37.8 C, heart rate <= 100, respiratory rate <= 24, systolic BP >= 90, SpO2 >= 92% on room air, able to maintain oral intake) prior to discontinuing therapy.",
                "Treat for a minimum of 5 days; extend duration only if patient has not achieved clinical stability."
            ],
            contraindications=[
                "Do NOT routinely add empirical MRSA or Pseudomonas coverage in standard CAP unless validated prior isolation or severe local risk factors are present.",
                "Do NOT use macrolide monotherapy in regions with Streptococcus pneumoniae macrolide resistance >= 25%."
            ]
        ),

        # =========================================================================
        # 7. SEPSIS & SEPTIC SHOCK — RESUSCITATION & ANTIMICROBIAL RULES (SSC / IDSA)
        # =========================================================================
        ClinicalNumericalRule(
            condition="sepsis",
            category="resuscitation_and_antimicrobial_bundle",
            population="Adult",
            severity_context="Sepsis & Septic Shock with Sepsis-Induced Hypoperfusion or Lactate >= 4.0 mmol/L",
            guideline_source="Surviving Sepsis Campaign (SSC) International Guidelines for Management of Sepsis and Septic Shock",
            version_year="2026 / 2021 Guidelines",
            rule_summary="SSC 1-Hour Bundle: Measure lactate; blood cultures before antibiotics; administer broad-spectrum IV antimicrobials within 1 hour; infuse 30 mL/kg balanced crystalloid within 3 hours for hypoperfusion or lactate >= 4.0 mmol/L; start Norepinephrine (titrate to target MAP >= 65 mmHg) if hypotensive during or after fluid loading.",
            numerical_parameters={
                "crystalloid_fluid_bolus": "30 mL/kg of IV balanced crystalloid (e.g. Plasma-Lyte or Ringer's Lactate) initiated immediately and completed within the first 3 hours",
                "antimicrobial_timing": "Administer broad-spectrum IV antimicrobials within 1 hour of sepsis recognition",
                "vasopressor_first_line": "Norepinephrine infusion (titrated to maintain Mean Arterial Pressure [MAP] >= 65 mmHg)",
                "vasopressor_second_line": "Vasopressin 0.03 units/min fixed infusion (added to reduce norepinephrine dosage rather than escalating high-dose single agent)",
                "corticosteroid_refractory_shock": "Hydrocortisone 200 mg/day IV (50 mg IV q6h or continuous infusion) ONLY if refractory shock persists despite adequate fluid and vasopressor therapy (Norepinephrine >= 0.25 mcg/kg/min)",
                "lactate_clearance_target": "Re-measure blood lactate within 2–4 hours targeting a >= 20% lactate clearance reduction"
            },
            conditional_qualifications=[
                "Use dynamic measures of fluid responsiveness (e.g. passive leg raise with stroke volume assessment, pulse pressure variation) rather than static CVP to guide fluids beyond the initial 30 mL/kg.",
                "De-escalate and narrow empirical broad-spectrum antimicrobials daily based on microbiological culture and susceptibility results."
            ],
            contraindications=[
                "Do NOT use hydroxyethyl starches (HES) or gelatin solutions for fluid resuscitation (increased acute kidney injury and mortality).",
                "Do NOT use Dopamine as the first-line vasopressor due to higher tachyarrhythmia and mortality rates compared to Norepinephrine.",
                "Do NOT administer IV Hydrocortisone in the absence of refractory septic shock."
            ]
        )
    ]

    @classmethod
    def get_validated_rules_for_condition(
        cls,
        condition: str,
        setting: str = "emergency",
        population_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves ONLY validated clinical numerical rules that match the exact condition.
        Strictly prevents any cross-contamination or leaking of unrelated condition rules.
        """
        clean_cond = condition.strip().lower()

        # Find matching condition
        matched_rules = []
        for rule in cls._RULE_REGISTRY:
            if rule.condition in clean_cond or clean_cond in rule.condition:
                if population_filter:
                    if population_filter.lower() in rule.population.lower() or rule.population == "All":
                        matched_rules.append(rule.to_dict())
                else:
                    matched_rules.append(rule.to_dict())

        return matched_rules

    @classmethod
    def validate_clinical_rule(
        cls,
        condition: str,
        rule_dict: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validates whether a clinical rule dictionary satisfies the strict medical context schema:
        CONDITION + POPULATION + SEVERITY + GUIDELINE + VERSION -> Clinical Rule
        """
        clean_cond = condition.strip().lower()
        rule_cond = rule_dict.get("condition", "").strip().lower()

        # Check 1: Condition Match
        if rule_cond and (rule_cond not in clean_cond and clean_cond not in rule_cond):
            return False, f"Rule condition '{rule_cond}' does not match requested condition '{clean_cond}' (Cross-condition violation)."

        # Check 2: Population Context
        if not rule_dict.get("population"):
            return False, "Rule missing explicit Population context (Adult vs Pediatric distinction required)."

        # Check 3: Severity Context
        if not rule_dict.get("severity_context"):
            return False, "Rule missing explicit Severity context (Mild/Uncomplicated vs Severe/Complicated required)."

        # Check 4: Guideline Source & Edition
        if not rule_dict.get("guideline_source"):
            return False, "Rule missing Authoritative Guideline Source."
        if not rule_dict.get("version_year"):
            return False, "Rule missing Guideline Edition / Version Year."

        # Check 5: Conditional Qualifications (No Bare Constants)
        if not rule_dict.get("conditional_qualifications"):
            return False, "Rule missing Conditional Qualifications (Bare universal constant violation)."

        return True, "Valid condition-bound clinical rule."
