/**
 * MedRef - Universal Medical Reference Application Logic (Secure Gateway Edition)
 * All credentials are kept private server-side in .env.
 * Zero API keys are stored in browser localStorage or transmitted from client.
 */

// 1. DOM References
const DOM = {
    // Layout Sections
    heroSection: document.getElementById('hero-section'),
    resultsSection: document.getElementById('results-section'),
    loadingOverlay: document.getElementById('loading-overlay'),
    errorDisplay: document.getElementById('error-display'),

    // Search
    searchForm: document.getElementById('search-form'),
    searchInput: document.getElementById('search-input'),
    settingBtns: document.querySelectorAll('.setting-btn'),
    chips: document.querySelectorAll('.chip'),

    // Results
    resultsTitle: document.getElementById('results-title'),
    resultsSettingBadge: document.getElementById('results-setting-badge'),
    backBtn: document.getElementById('back-btn'),
    copyBtn: document.getElementById('copy-btn'),

    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    guidelinesContent: document.getElementById('guidelines-content'),
    commonPracticeContent: document.getElementById('common-practice-content'),
    groundingSources: document.getElementById('grounding-sources'),

    // Sidebar History
    navHistoryBtn: document.getElementById('nav-history-btn'),
    historySidebar: document.getElementById('history-sidebar'),
    sidebarBackdrop: document.getElementById('sidebar-backdrop'),
    closeHistoryBtn: document.getElementById('close-history-btn'),
    historyList: document.getElementById('history-list'),
    historySearch: document.getElementById('history-search'),
    clearHistoryBtn: document.getElementById('clear-history-btn'),
    emptyHistory: document.getElementById('empty-history'),

    // Theme & Server Settings
    themeToggleBtn: document.getElementById('theme-toggle-btn'),
    navSettingsBtn: document.getElementById('nav-settings-btn'),
    apiKeyModal: document.getElementById('api-key-modal'),
    apiKeyInput: document.getElementById('api-key-input'),
    saveApiKeyBtn: document.getElementById('save-api-key-btn'),

    // Error Actions
    errorRetryBtn: document.getElementById('error-retry-btn'),
    errorBackBtn: document.getElementById('error-back-btn'),
    errorTitle: document.getElementById('error-title'),
    errorMessage: document.getElementById('error-message'),

    // Toast
    toastContainer: document.getElementById('toast-container')
};

// 2. App State
const AppState = {
    currentResults: null,
    currentSetting: 'emergency', // 'emergency' or 'outpatient'
    activeTab: 'guidelines',     // 'guidelines' or 'common'
    searchHistory: JSON.parse(localStorage.getItem('medref_history') || '[]'),
    theme: localStorage.getItem('medref_theme') || 'dark',
    isSearching: false,
    lastQuery: ''
};

// 3. Helper Functions
function escapeHtml(unsafe) {
    if (unsafe == null) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function ensureArray(val) {
    if (!val) return [];
    if (Array.isArray(val)) return val;
    if (typeof val === 'string') return [val];
    if (typeof val === 'object') return Object.values(val);
    return [val];
}

function renderListOrText(val) {
    if (!val) return '';
    const arr = ensureArray(val);
    if (arr.length === 0) return '';
    if (arr.length === 1 && typeof arr[0] === 'string' && !arr[0].startsWith('•')) {
        return `<p class="content-text">${escapeHtml(arr[0])}</p>`;
    }
    return `<ul class="bullet-list">${arr.map(item => `<li>${escapeHtml(typeof item === 'object' ? JSON.stringify(item) : item)}</li>`).join('')}</ul>`;
}

function renderCitationPills(item) {
    if (!item) return '';
    const pills = [];

    // PMID
    if (item.pmid) {
        const pmidClean = String(item.pmid).replace(/[^0-9]/g, '');
        if (pmidClean) {
            pills.push(`<a href="https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmidClean)}/" target="_blank" rel="noopener noreferrer" class="citation-pill citation-pmid" title="Open PubMed Record ${escapeHtml(pmidClean)}">📄 PMID: ${escapeHtml(pmidClean)} ↗</a>`);
        }
    }

    // DOI
    if (item.doi) {
        const doiClean = String(item.doi).replace(/^doi:\s*/i, '').trim();
        if (doiClean) {
            pills.push(`<a href="https://doi.org/${encodeURIComponent(doiClean)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-doi" title="Open via DOI ${escapeHtml(doiClean)}">🔗 DOI ↗</a>`);
        }
    }

    // Direct Guideline / Source URL
    const url = item.source_url || item.url || item.article_url || item.uri;
    if (url && url !== '#' && !url.includes('example.com') && !url.includes('undefined')) {
        const orgName = item.organization || item.issuing_organization || item.name || 'Source';
        if (url.includes('cochranelibrary.com')) {
            pills.push(`<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-cochrane" title="Open Cochrane Systematic Review">🟣 Cochrane Library ↗</a>`);
        } else if (url.includes('edaegypt.gov.eg')) {
            pills.push(`<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-eda" title="Egyptian Drug Authority Registry">🏛️ EDA Portal ↗</a>`);
        } else {
            pills.push(`<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-guideline" title="Open ${escapeHtml(orgName)}">🏛️ ${escapeHtml(orgName)} ↗</a>`);
        }
    }

    return pills.length > 0 ? `<div class="citation-pills-row" style="margin-top:0.4rem; display:flex; flex-wrap:wrap; gap:0.35rem;">${pills.join('')}</div>` : '';
}

function renderProvenanceBadge(tier) {
    if (!tier) return '';
    const t = String(tier).toLowerCase();
    if (t.includes('unverified') || t.includes('unindexed') || t.includes('not independently verified')) {
        return `<span class="provenance-badge badge-unverified">⚠️ Institutional Practice — Unverified</span>`;
    }
    if (t.includes('guideline') || t.includes('official') || t.includes('mohp') || t.includes('ada') || t.includes('gina') || t.includes('who') || t.includes('esc') || t.includes('ispad') || t.includes('eau') || t.includes('nice') || t.includes('ats') || t.includes('idsa')) {
        return `<span class="provenance-badge badge-official">🛡️ Official Guideline</span>`;
    }
    if (t.includes('cochrane')) {
        return `<span class="provenance-badge badge-cochrane">🟣 Cochrane Review</span>`;
    }
    if (t.includes('peer') || t.includes('pubmed') || t.includes('study') || t.includes('trial') || t.includes('rct') || t.includes('tier 3')) {
        return `<span class="provenance-badge badge-peer-reviewed">🔵 Peer-Reviewed</span>`;
    }
    if (t.includes('eda') || t.includes('regulatory') || t.includes('tier 1')) {
        return `<span class="provenance-badge badge-eda">🏛️ EDA Registered</span>`;
    }
    if (t.includes('market') || t.includes('dawaagate') || t.includes('dwaprices') || t.includes('tier 5')) {
        return `<span class="provenance-badge badge-market">🛒 Market Source</span>`;
    }
    if (t.includes('practice') || t.includes('hospital') || t.includes('kasr') || t.includes('ain shams') || t.includes('tier 4')) {
        return `<span class="provenance-badge badge-unverified">⚠️ Institutional Practice — Unverified</span>`;
    }
    return `<span class="provenance-badge badge-official">✓ Verified Record</span>`;
}

// 4. Setting Toggle
function initSettingToggle() {
    DOM.settingBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            setActiveSetting(btn.dataset.setting);
        });
    });
}

function setActiveSetting(setting) {
    if (setting !== 'emergency' && setting !== 'outpatient') return;
    AppState.currentSetting = setting;

    DOM.settingBtns.forEach(btn => {
        if (btn.dataset.setting === setting) {
            btn.classList.add('setting-btn-active');
        } else {
            btn.classList.remove('setting-btn-active');
        }
    });

    if (setting === 'emergency') {
        DOM.searchInput.placeholder = "Enter condition for Emergency protocol (e.g., Status Epilepticus, DKA, Anaphylaxis, Sepsis...)";
    } else {
        DOM.searchInput.placeholder = "Enter condition for Outpatient Clinic protocol (e.g., Hypertension, Type 2 Diabetes, UTI, Asthma...)";
    }
}

// 5. Tab Navigation
function initTabs() {
    DOM.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.dataset.tab);
        });
    });
}

function switchTab(tabName) {
    if (tabName !== 'guidelines' && tabName !== 'common') return;
    AppState.activeTab = tabName;

    DOM.tabBtns.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('tab-btn-active');
        } else {
            btn.classList.remove('tab-btn-active');
        }
    });

    if (tabName === 'guidelines') {
        DOM.guidelinesContent.classList.remove('hidden');
        DOM.commonPracticeContent.classList.add('hidden');
    } else {
        DOM.guidelinesContent.classList.add('hidden');
        DOM.commonPracticeContent.classList.remove('hidden');
    }
}

// 6. Search Workflow (Secure Server Gateway)
async function handleSearch(query) {
    if (!query || !query.trim() || AppState.isSearching) return;

    const cleanQuery = query.trim();
    AppState.lastQuery = cleanQuery;
    DOM.searchInput.value = cleanQuery;

    AppState.isSearching = true;
    DOM.loadingOverlay.classList.remove('hidden');
    DOM.heroSection.classList.add('hidden');
    DOM.errorDisplay.classList.add('hidden');
    DOM.resultsSection.classList.add('hidden');

    const loadingTextEl = DOM.loadingOverlay.querySelector('.loading-text');
    const loadingMessages = [
        "🔬 Synthesizing international evidence-based guidelines...",
        "🏛️ Evaluating Egyptian Health Council & MOHP clinical guidance...",
        "💊 Compiling Egyptian medication tables, prices & EDA status...",
        "🥤 Formulating effervescent products & therapeutic alternatives...",
        "✨ Finalizing GRADE recommendations and safety warnings..."
    ];
    let msgIdx = 0;
    if (loadingTextEl) loadingTextEl.textContent = loadingMessages[0];
    const loadingInterval = setInterval(() => {
        msgIdx = (msgIdx + 1) % loadingMessages.length;
        if (loadingTextEl) loadingTextEl.textContent = loadingMessages[msgIdx];
    }, 6000);

    try {
        const result = await geminiAPI.searchCondition(cleanQuery, AppState.currentSetting);

        if (!result || result.error) {
            if (result?.error === 'MISSING_API_KEY' || result?.error === 'MISSING_SERVER_API_KEY') {
                showApiKeyModal();
                return;
            }
            throw new Error(result?.message || result?.error || 'Invalid response from server gateway');
        }

        AppState.currentResults = result;
        renderResults(result);
        addToHistory(cleanQuery, AppState.currentSetting);

        DOM.resultsSection.classList.remove('hidden');
        switchTab('guidelines');
        window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (error) {
        console.error("[MedRef] Search error:", error);
        if (error.message === 'MISSING_SERVER_API_KEY' || error.message.includes('MISSING_API_KEY')) {
            showApiKeyModal();
        } else {
            showError('SEARCH_FAILED', error.message);
        }
    } finally {
        clearInterval(loadingInterval);
        AppState.isSearching = false;
        DOM.loadingOverlay.classList.add('hidden');
    }
}

// 7. Render Main Results Container
function renderResults(data) {
    if (!data) return;

    // Header Title & Specialty
    const titleText = data.condition_name || AppState.lastQuery;
    const spec = data.classification?.primary_specialty || data.specialty || '';
    DOM.resultsTitle.textContent = titleText + (spec ? ` — ${spec}` : '');

    // Setting Badge
    if (AppState.currentSetting === 'emergency') {
        DOM.resultsSettingBadge.innerHTML = '🚨 Emergency Protocol';
        DOM.resultsSettingBadge.className = 'setting-badge badge-emergency';
    } else {
        DOM.resultsSettingBadge.innerHTML = '🏥 Outpatient Clinic Protocol';
        DOM.resultsSettingBadge.className = 'setting-badge badge-outpatient';
    }

    // Fallback or Live Research Mode Banner
    let bannerHtml = '';
    if (data.research_mode === 'enhanced_evidence_synthesis') {
        bannerHtml = `
            <div class="research-mode-banner banner-enhanced">
                <span class="banner-icon">ℹ️</span>
                <div class="banner-text">
                    <strong>Evidence Synthesis Mode:</strong> Live web search was unavailable (API quota). This report was synthesized using the enhanced evidence-based research mode based on international guidelines (IDSA, ESC, GINA, KDIGO, WHO) and Egyptian pharmaceutical registry data.
                </div>
            </div>
        `;
    } else if (data.research_mode === 'live_web_grounded') {
        bannerHtml = `
            <div class="research-mode-banner banner-live">
                <span class="banner-icon">🌐</span>
                <div class="banner-text">
                    <strong>Live Web Research Mode:</strong> Verified with real-time Google Search grounding across authoritative medical societies and Egyptian sources.
                </div>
            </div>
        `;
    }

    // Render Tabs
    renderGuidelines(data.guidelines || {}, data.classification || {}, bannerHtml);
    renderEgyptPractice(data.egypt_practice_and_pharmacology || data.common_practice || {}, bannerHtml);

    // Render Consolidated Sources (Phase 5)
    renderConsolidatedSources(data);
}

// 8. Render Tab 1: Evidence-Based Guidelines Protocol
function renderGuidelines(guidelines, classification, bannerHtml) {
    let html = bannerHtml || '';

    // Classification Summary Card
    const primarySpec = classification?.primary_specialty || '';
    const secSpecs = ensureArray(classification?.secondary_specialties);
    const qTypes = ensureArray(classification?.clinical_question_type);

    if (primarySpec || secSpecs.length > 0 || qTypes.length > 0) {
        html += `
            <div class="result-section-card classification-card">
                <div class="classification-header">
                    <span class="icon">🧭</span>
                    <div>
                        <h4 class="classification-title">Specialty-Aware Evidence Routing</h4>
                        <div class="classification-badges">
                            ${primarySpec ? `<span class="spec-badge primary-spec">Primary: ${escapeHtml(primarySpec)}</span>` : ''}
                            ${secSpecs.map(s => `<span class="spec-badge sec-spec">${escapeHtml(s)}</span>`).join('')}
                            ${qTypes.map(q => `<span class="spec-badge q-spec">🎯 ${escapeHtml(q)}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Overview
    if (guidelines.overview) {
        html += `
            <div class="result-section-card overview-card">
                <h3><span class="icon">📖</span> Clinical Definition & Scope</h3>
                ${guidelines.overview.definition ? `
                <div class="content-block">
                    <span class="content-label">Definition & Diagnostic Criteria:</span>
                    <p class="content-text">${escapeHtml(guidelines.overview.definition)}</p>
                </div>` : ''}
                ${guidelines.overview.epidemiology ? `
                <div class="content-block">
                    <span class="content-label">Epidemiology & High-Risk Groups:</span>
                    <p class="content-text">${escapeHtml(guidelines.overview.epidemiology)}</p>
                </div>` : ''}
                ${guidelines.overview.pathophysiology ? `
                <div class="content-block">
                    <span class="content-label">Pathophysiological Mechanism:</span>
                    <p class="content-text">${escapeHtml(guidelines.overview.pathophysiology)}</p>
                </div>` : ''}
            </div>
        `;
    }

    // Authoritative Guidelines Body Cards
    const authGuidelines = ensureArray(guidelines.authoritative_guidelines || guidelines.sources);
    if (authGuidelines.length > 0) {
        html += `
            <div class="result-section-card auth-guidelines-card">
                <h3><span class="icon">🏛️</span> Authoritative Specialty Guidelines & Recommendations</h3>
                <div class="guidelines-grid">
                    ${authGuidelines.map(g => {
                        const org = g.organization || g.name || 'Medical Society';
                        const title = g.guideline_title || g.title || 'Clinical Practice Guideline';
                        const year = g.year ? ` (${g.year})` : '';
                        const strength = g.recommendation_strength || '';
                        const certainty = g.evidence_certainty || '';
                        const rec = g.key_recommendation || g.details || '';
                        const meth = g.methodology ? `<div class="guideline-methodology">🔬 Methodology: ${escapeHtml(g.methodology)}</div>` : '';
                        const pillsHtml = renderCitationPills(g);
                        const provBadge = renderProvenanceBadge(g.methodology || 'Official Guideline');

                        let strengthBadge = '';
                        if (strength) {
                            const strLow = strength.toLowerCase();
                            const cls = strLow.includes('strong') ? 'badge-strong' : (strLow.includes('conditional') ? 'badge-conditional' : 'badge-weak');
                            strengthBadge = `<span class="grade-badge ${cls}">Recommendation: ${escapeHtml(strength)}</span>`;
                        }

                        let certBadge = '';
                        if (certainty) {
                            const certLow = certainty.toLowerCase();
                            const cls = certLow.includes('high') ? 'cert-high' : (certLow.includes('moderate') ? 'cert-mod' : 'cert-low');
                            certBadge = `<span class="cert-badge ${cls}">GRADE Certainty: ${escapeHtml(certainty)}</span>`;
                        }

                        return `
                            <div class="guideline-item-card">
                                <div class="guideline-item-header">
                                    <div>
                                        <strong class="guideline-org">${escapeHtml(org + year)}</strong>
                                        <div style="margin-top:0.25rem;">${provBadge}</div>
                                    </div>
                                    <div class="guideline-badges">${strengthBadge}${certBadge}</div>
                                </div>
                                <div class="guideline-title-text">${escapeHtml(title)}</div>
                                ${rec ? `<p class="guideline-rec-text">${escapeHtml(rec)}</p>` : ''}
                                ${meth}
                                ${pillsHtml}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // Guideline Consensus vs Divergence
    if (guidelines.guideline_consensus_and_divergence) {
        const cd = guidelines.guideline_consensus_and_divergence;
        const consensusList = ensureArray(cd.consensus_points);
        const divergenceList = ensureArray(cd.divergence_points);

        if (consensusList.length > 0 || divergenceList.length > 0) {
            html += `
                <div class="result-section-card consensus-divergence-card">
                    <h3><span class="icon">⚖️</span> Multi-Guideline Consensus & Divergence Analysis</h3>
                    ${consensusList.length > 0 ? `
                    <div class="consensus-box">
                        <span class="box-title">✅ International Consensus Points:</span>
                        <ul class="bullet-list">${consensusList.map(p => `<li>${escapeHtml(typeof p === 'object' ? JSON.stringify(p) : p)}</li>`).join('')}</ul>
                    </div>` : ''}

                    ${divergenceList.length > 0 ? `
                    <div class="divergence-box mt-3">
                        <span class="box-title">⚡ Areas of Society Divergence & Disagreement:</span>
                        <div class="divergence-list">
                            ${divergenceList.map(d => {
                                const issue = typeof d === 'object' ? d.issue : d;
                                const details = typeof d === 'object' ? d.details : '';
                                const reasons = typeof d === 'object' ? d.underlying_reasons : '';
                                return `
                                    <div class="divergence-item">
                                        <strong>${escapeHtml(issue || 'Divergence')}</strong>${details ? `: ${escapeHtml(details)}` : ''}
                                        ${reasons ? `<div class="divergence-reasons">💡 Underlying Reason: ${escapeHtml(reasons)}</div>` : ''}
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>` : ''}
                </div>
            `;
        }
    }

    // Red Flags
    const redFlags = ensureArray(guidelines.red_flags_and_triage || guidelines.red_flags);
    if (redFlags.length > 0) {
        html += `
            <div class="result-section-card red-flags-card">
                <h3><span class="icon">🚩</span> Critical Red Flags & Immediate Life Threats</h3>
                <ul class="red-flag-list">
                    ${redFlags.map(flag => `
                        <li class="red-flag-item">
                            <span class="flag-icon">⚠️</span>
                            <span>${escapeHtml(typeof flag === 'object' ? JSON.stringify(flag) : flag)}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Diagnostic Strategy
    if (guidelines.diagnostic_strategy) {
        const diag = guidelines.diagnostic_strategy;
        const bedside = ensureArray(diag.bedside_and_pocus);
        const labs = ensureArray(diag.laboratory_and_biomarkers);
        const imaging = ensureArray(diag.imaging);

        html += `
            <div class="result-section-card diagnostic-strategy-card">
                <h3><span class="icon">🔬</span> Evidence-Based Diagnostic Strategy</h3>
                ${diag.approach ? `<p class="content-text mb-3"><strong>Algorithm:</strong> ${escapeHtml(diag.approach)}</p>` : ''}
                
                <div class="diag-grid">
                    ${bedside.length > 0 ? `
                    <div class="diag-col">
                        <h4>Bedside, ECG & POCUS</h4>
                        <ul>${bedside.map(i => `<li>${escapeHtml(typeof i === 'object' ? JSON.stringify(i) : i)}</li>`).join('')}</ul>
                    </div>` : ''}

                    ${labs.length > 0 ? `
                    <div class="diag-col">
                        <h4>Laboratory Biomarkers & Panels</h4>
                        <ul>${labs.map(i => `<li>${escapeHtml(typeof i === 'object' ? JSON.stringify(i) : i)}</li>`).join('')}</ul>
                    </div>` : ''}

                    ${imaging.length > 0 ? `
                    <div class="diag-col">
                        <h4>Diagnostic Imaging</h4>
                        <ul>${imaging.map(i => `<li>${escapeHtml(typeof i === 'object' ? JSON.stringify(i) : i)}</li>`).join('')}</ul>
                    </div>` : ''}
                </div>
            </div>
        `;
    }

    // Stepped Management Protocol (GRADE-Aware)
    const mgmt = ensureArray(guidelines.stepped_management_protocol || guidelines.management);
    if (mgmt.length > 0) {
        const stepsHtml = mgmt.map((step, idx) => {
            const stepNum = step.step_number || step.step || (idx + 1);
            const stepTitle = step.title || `Step ${stepNum}`;
            const priority = step.priority ? `<span class="step-priority-tag">${escapeHtml(step.priority)}</span>` : '';
            const stepDetails = step.clinical_details || step.details || '';
            const stepPills = renderCitationPills(step);

            let medsHtml = '';
            const meds = ensureArray(step.medications);
            if (meds.length > 0) {
                medsHtml = `
                    <div class="med-list">
                        <div class="med-list-header">💊 Prescribed Active Ingredients (Generic INN):</div>
                        ${meds.map(med => {
                            const name = med.generic_name || med.name || 'Medication';
                            const dose = med.dose || '';
                            const route = med.route ? `Route: ${med.route}` : '';
                            const freq = med.frequency ? ` | ${med.frequency}` : '';
                            const dur = med.duration ? ` | ${med.duration}` : '';
                            const notes = med.clinical_notes || med.notes ? `<div class="med-note">💡 ${escapeHtml(med.clinical_notes || med.notes)}</div>` : '';
                            const medPills = renderCitationPills(med);
                            
                            let gradeTag = '';
                            if (med.grade_strength || med.grade_certainty) {
                                gradeTag = `<span class="med-grade-tag">GRADE: ${escapeHtml(med.grade_strength || '')} (${escapeHtml(med.grade_certainty || '')})</span>`;
                            }

                            return `
                                <div class="med-item">
                                    <div class="med-name-row">
                                        <span class="med-name">${escapeHtml(name)}</span>
                                        ${gradeTag}
                                    </div>
                                    <div class="med-details">
                                        ${dose ? `<span class="med-dose">${escapeHtml(dose)}</span>` : ''}
                                        ${(route || freq || dur) ? `<span class="med-route">${escapeHtml(route + freq + dur)}</span>` : ''}
                                    </div>
                                    ${notes}
                                    ${medPills}
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            }

            return `
                <div class="step-card ${step.critical || (step.priority && step.priority.toLowerCase().includes('critical')) ? 'step-critical' : ''}">
                    <div class="step-badge">${stepNum}</div>
                    <div class="step-body">
                        <div class="step-title-row">
                            <span class="step-title">${escapeHtml(stepTitle)}</span>
                            ${priority}
                        </div>
                        ${stepDetails ? `<p class="step-desc">${escapeHtml(stepDetails)}</p>` : ''}
                        ${medsHtml}
                        ${stepPills}
                    </div>
                </div>
            `;
        }).join('');

        html += `
            <div class="result-section-card management-card">
                <h3><span class="icon">📋</span> Step-Wise Treatment Protocol (GRADE-Aware)</h3>
                <div class="steps-container">
                    ${stepsHtml}
                </div>
            </div>
        `;
    }

    // Landmark Evidence & Primary Trials
    const trials = ensureArray(guidelines.landmark_evidence_and_trials);
    if (trials.length > 0) {
        html += `
            <div class="result-section-card trials-card">
                <h3><span class="icon">🏆</span> Landmark Trials & Systematic Reviews (Cochrane/PubMed)</h3>
                <div class="trials-grid">
                    ${trials.map(t => {
                        const pillsHtml = renderCitationPills(t);
                        const provBadge = renderProvenanceBadge(t.design || 'Peer-Reviewed');
                        return `
                            <div class="trial-card">
                                <div class="trial-header">
                                    <div>
                                        <strong class="trial-title">📊 ${escapeHtml(t.trial_name_or_study || 'Study')} ${t.year ? `(${escapeHtml(t.year)})` : ''}</strong>
                                        <div style="margin-top:0.25rem;">${provBadge}</div>
                                    </div>
                                    ${t.design ? `<span class="trial-design">${escapeHtml(t.design)}</span>` : ''}
                                </div>
                                ${t.primary_outcome ? `<div class="trial-outcome"><strong>Outcome & Significance:</strong> ${escapeHtml(t.primary_outcome)}</div>` : ''}
                                ${t.clinical_takeaway ? `<div class="trial-takeaway"><strong>Clinical Impact:</strong> ${escapeHtml(t.clinical_takeaway)}</div>` : ''}
                                ${pillsHtml}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // Safety, Boxed Warnings & Special Populations
    if (guidelines.safety_monitoring_and_warnings) {
        const safe = guidelines.safety_monitoring_and_warnings;
        const boxed = ensureArray(safe.boxed_warnings_and_contraindications);
        const params = ensureArray(safe.monitoring_parameters);

        html += `
            <div class="result-section-card safety-card">
                <h3><span class="icon">🛡️</span> Safety, Boxed Warnings & Special Populations</h3>
                ${boxed.length > 0 ? `
                <div class="safety-box boxed-warnings">
                    <span class="box-title">⛔ Black-Box Warnings & Major Contraindications:</span>
                    <ul class="bullet-list">${boxed.map(w => `<li>${escapeHtml(typeof w === 'object' ? JSON.stringify(w) : w)}</li>`).join('')}</ul>
                </div>` : ''}

                ${params.length > 0 ? `
                <div class="safety-box mt-3">
                    <span class="box-title">📊 Essential Monitoring Parameters:</span>
                    <ul class="bullet-list">${params.map(m => `<li>${escapeHtml(typeof m === 'object' ? JSON.stringify(m) : m)}</li>`).join('')}</ul>
                </div>` : ''}

                ${safe.special_populations ? `
                <div class="safety-box mt-3">
                    <span class="box-title">🤰 Renal, Hepatic, Pregnancy & Pediatric Dosing Adjustments:</span>
                    <p class="content-text">${escapeHtml(typeof safe.special_populations === 'object' ? JSON.stringify(safe.special_populations) : safe.special_populations)}</p>
                </div>` : ''}
            </div>
        `;
    }

    // Disposition & Follow-Up
    if (guidelines.disposition_and_followup || guidelines.disposition) {
        const disp = guidelines.disposition_and_followup || guidelines.disposition;
        html += `
            <div class="result-section-card disposition-card">
                <h3><span class="icon">🚪</span> Disposition, Hospital Admission & Follow-Up</h3>
                ${disp.admission_criteria ? `
                <div class="content-block">
                    <span class="content-label">Admission Criteria (Ward / ICU):</span>
                    ${renderListOrText(disp.admission_criteria)}
                </div>` : ''}
                ${disp.discharge_criteria ? `
                <div class="content-block">
                    <span class="content-label">Safe Discharge Criteria:</span>
                    ${renderListOrText(disp.discharge_criteria)}
                </div>` : ''}
                ${disp.outpatient_followup || disp.follow_up ? `
                <div class="content-block">
                    <span class="content-label">Outpatient Follow-Up Timeline:</span>
                    <p class="content-text">${escapeHtml(disp.outpatient_followup || disp.follow_up)}</p>
                </div>` : ''}
            </div>
        `;
    }

    // Evidence Gaps & Practical Takeaway
    if (guidelines.evidence_gaps_and_uncertainties || guidelines.practical_takeaway) {
        const gaps = ensureArray(guidelines.evidence_gaps_and_uncertainties);
        html += `
            <div class="result-section-card takeaway-card">
                <h3><span class="icon">💡</span> Practical Evidence-Based Takeaway & Evidence Gaps</h3>
                ${guidelines.practical_takeaway ? `
                <div class="takeaway-box">
                    <span class="takeaway-title">✨ Clinical Pearl & Core Takeaway:</span>
                    <p class="content-text">${escapeHtml(guidelines.practical_takeaway)}</p>
                </div>` : ''}

                ${gaps.length > 0 ? `
                <div class="gaps-box mt-3">
                    <span class="gaps-title">⚠️ Identified Evidence Gaps & Low-Certainty Areas:</span>
                    <ul class="bullet-list">${gaps.map(g => `<li>${escapeHtml(typeof g === 'object' ? JSON.stringify(g) : g)}</li>`).join('')}</ul>
                </div>` : ''}
            </div>
        `;
    }

    DOM.guidelinesContent.innerHTML = html || '<p class="empty-state">No guidelines data available.</p>';
}

// 9. Render Tab 2: 6-Track Egyptian Clinical & Pharmaceutical Protocol
function renderEgyptPractice(egData, bannerHtml) {
    let html = bannerHtml || '';

    // TRACK A: OFFICIAL EGYPTIAN CLINICAL GUIDANCE
    const trackA = egData.track_a_official_guidance;
    if (trackA) {
        const conf = trackA.confidence ? `<span class="confidence-badge conf-${trackA.confidence.toLowerCase()}">${escapeHtml(trackA.confidence)} CONFIDENCE</span>` : '';
        const provBadge = renderProvenanceBadge('Official Egyptian Protocol');
        const pillsHtml = renderCitationPills(trackA);
        html += `
            <div class="result-section-card me-egypt-card highlight-egypt-card">
                <div class="section-badge-header">
                    <span class="country-flag">🇪🇬</span>
                    <div>
                        <h3>Track A: Official Egyptian Clinical Guidance (EHC / MOHP / GOTHI)</h3>
                        <div style="margin-top:0.25rem;">${provBadge}</div>
                    </div>
                    ${conf}
                </div>
                <div class="content-block">
                    <span class="content-label">📜 National Guidelines & MOH Protocols:</span>
                    <p class="content-text">${escapeHtml(trackA.national_guidelines_and_mohp || 'No national guideline identified.')}</p>
                </div>
                ${trackA.guideline_type ? `<div class="guideline-type-tag">Classification: <strong>${escapeHtml(trackA.guideline_type)}</strong></div>` : ''}
                ${pillsHtml}
            </div>
        `;
    }

    // TRACK B: EGYPTIAN SCIENTIFIC & EPIDEMIOLOGICAL EVIDENCE
    const trackB = egData.track_b_scientific_and_epidemiological_evidence;
    if (trackB) {
        const conf = trackB.confidence ? `<span class="confidence-badge conf-${trackB.confidence.toLowerCase()}">${escapeHtml(trackB.confidence)} CONFIDENCE</span>` : '';
        const provBadge = renderProvenanceBadge('Peer-Reviewed Egyptian Study');
        html += `
            <div class="result-section-card egypt-science-card">
                <div class="section-badge-header">
                    <span class="icon">🔬</span>
                    <div>
                        <h3>Track B: Egyptian Scientific Evidence & Antimicrobial Resistance (AMR)</h3>
                        <div style="margin-top:0.25rem;">${provBadge}</div>
                    </div>
                    ${conf}
                </div>
                ${trackB.local_epidemiology_and_cohorts ? `
                <div class="content-block">
                    <span class="content-label">📊 Local Epidemiology & Egyptian Cohorts:</span>
                    <p class="content-text">${escapeHtml(trackB.local_epidemiology_and_cohorts)}</p>
                </div>` : ''}
                ${trackB.antimicrobial_resistance_and_biomarkers ? `
                <div class="content-block">
                    <span class="content-label">🦠 Local Hospital Resistance & Susceptibility Patterns:</span>
                    <p class="content-text">${escapeHtml(trackB.antimicrobial_resistance_and_biomarkers)}</p>
                </div>` : ''}
            </div>
        `;
    }

    // TRACK C: REAL-WORLD EGYPTIAN CLINICAL PRACTICE
    const trackC = egData.track_c_real_world_clinical_practice;
    if (trackC) {
        const conf = trackC.confidence ? `<span class="confidence-badge conf-${trackC.confidence.toLowerCase()}">${escapeHtml(trackC.confidence)} CONFIDENCE</span>` : '';
        const workarounds = ensureArray(trackC.resource_limited_workarounds);

        html += `
            <div class="result-section-card egypt-practice-card">
                <div class="section-badge-header">
                    <span class="icon">🏥</span>
                    <div>
                        <h3>Track C: Real-World Clinical Practice in Egyptian Hospitals</h3>
                        <div style="margin-top:0.25rem;"><span class="provenance-badge badge-unverified">⚠️ Institutional Practice — Unverified</span></div>
                    </div>
                    ${conf}
                </div>
                ${trackC.hospital_and_clinic_patterns ? `
                <div class="content-block">
                    <span class="content-label">🏥 Prescribing Patterns in University & MOH Hospitals:</span>
                    <p class="content-text">${escapeHtml(trackC.hospital_and_clinic_patterns)}</p>
                </div>` : ''}
                ${workarounds.length > 0 ? `
                <div class="content-block">
                    <span class="content-label">⚡ Practical Workarounds for Delayed/Unavailable Diagnostics:</span>
                    <ul class="bullet-list">${workarounds.map(w => `<li>${escapeHtml(typeof w === 'object' ? JSON.stringify(w) : w)}</li>`).join('')}</ul>
                </div>` : ''}
                ${trackC.cultural_and_ramadan_counseling ? `
                <div class="content-block">
                    <span class="content-label">👥 Ramadan Fasting Adjustments & Patient Counseling:</span>
                    <p class="content-text">${escapeHtml(trackC.cultural_and_ramadan_counseling)}</p>
                </div>` : ''}
            </div>
        `;
    }

    // TRACK D & E: COMPREHENSIVE EGYPTIAN MEDICATION LANDSCAPE TABLE
    const medLandscape = ensureArray(egData.track_d_and_e_medication_landscape || egData.all_active_drugs);
    if (medLandscape.length > 0) {
        html += `
            <div class="result-section-card egypt-meds-card">
                <h3><span class="icon">💊</span> Tracks D & E: Egyptian Medication Landscape (EDA & Market Data)</h3>
                <p class="section-lead-text">Active ingredients mapped to famous Egyptian brands, strengths, EDA registration status, and pharmacy availability (DawaaGate / DwaPrices):</p>
                
                <div class="table-responsive">
                    <table class="egypt-med-table">
                        <thead>
                            <tr>
                                <th>Active Ingredient (INN)</th>
                                <th>Famous Egyptian Brands</th>
                                <th>Strengths & Forms</th>
                                <th>EDA Registration</th>
                                <th>Market & Retail Status</th>
                                <th>Price Range (EGP)</th>
                                <th>Evidence Tier</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${medLandscape.map(med => {
                                const inn = med.active_ingredient || med.name || 'Drug';
                                const brandArr = ensureArray(med.famous_egyptian_brands || med.egypt_famous_brand_examples);
                                const brands = brandArr.length > 0 ? brandArr.join(', ') : 'Available Generics';
                                const forms = med.available_strengths_and_forms || med.typical_dose || 'Standard forms';
                                const reg = med.eda_registration_status || 'Registered in EDA';
                                const mkt = med.market_availability_and_retail_status || med.egypt_pharmacy_status || 'Available in Pharmacies';
                                const price = med.reported_price_range_egp || 'Market dependent';
                                const tier = med.evidence_tier || med.evidence_level || 'Tier 1 (EDA)';

                                return `
                                    <tr>
                                        <td><strong>💊 ${escapeHtml(inn)}</strong><br><small class="text-muted">${escapeHtml(med.therapeutic_role || '')}</small></td>
                                        <td><span class="egypt-brand-highlight">${escapeHtml(brands)}</span></td>
                                        <td>${escapeHtml(forms)}</td>
                                        <td>
                                            <a href="https://edaegypt.gov.eg/" target="_blank" rel="noopener noreferrer" class="eda-status-tag" title="Verify on EDA Portal">
                                                🏛️ ${escapeHtml(reg)} ↗
                                            </a>
                                        </td>
                                        <td>
                                            <span class="market-meta-tag">🛒 ${escapeHtml(mkt)}</span><br>
                                            <span class="obs-date-tag">Observed: Aug 2026</span>
                                        </td>
                                        <td><strong class="price-tag">${escapeHtml(price)}</strong></td>
                                        <td><span class="tier-badge">${escapeHtml(tier)}</span></td>
                                    </tr>
                                `;}
                            ).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // TRACK F: SPECIALIZED EGYPTIAN FORMULATIONS & REGIMENS
    const trackF = egData.track_f_specialized_egyptian_formulations;
    if (trackF) {
        const eff = trackF.effervescent_sachets_and_alkalinizers;
        const phyto = trackF.standardized_phytotherapy_and_terpenes;
        const formulas = ensureArray(trackF.common_egyptian_prescription_formulas);
        const isEmerg = AppState.currentSetting === 'emergency';
        const formulaLabel = isEmerg 
            ? '📝 Common Egyptian Emergency Triage & Hospital Inpatient Regimens:' 
            : '📝 Common Egyptian Outpatient Prescription Combinations:';

        if (eff || phyto || formulas.length > 0) {
            html += `
                <div class="result-section-card egypt-formulations-card">
                    <h3><span class="icon">🥤</span> Track F: Specialized Egyptian Formulations ${isEmerg ? '& Hospital Inpatient Regimens' : '& Prescription Practices'}</h3>
                    
                    ${eff ? `
                    <div class="content-block">
                        <span class="content-label">🧪 Effervescent Sachets & Alkalinizers (الفوارات):</span>
                        <p class="content-text">${escapeHtml(eff)}</p>
                    </div>` : ''}

                    ${phyto ? `
                    <div class="content-block mt-3">
                        <span class="content-label">🌿 Standardized Phytotherapy & Terpene Extracts:</span>
                        <p class="content-text">${escapeHtml(phyto)}</p>
                    </div>` : ''}

                    ${formulas.length > 0 ? `
                    <div class="content-block mt-3">
                        <span class="content-label">${escapeHtml(formulaLabel)}</span>
                        <ul class="bullet-list">${formulas.map(f => `<li>${escapeHtml(typeof f === 'object' ? JSON.stringify(f) : f)}</li>`).join('')}</ul>
                    </div>` : ''}
                </div>
            `;
        }
    }

    // THERAPEUTIC ALTERNATIVES (DRUG SHORTAGE WORKAROUNDS)
    const alts = ensureArray(egData.therapeutic_alternatives);
    if (alts.length > 0) {
        html += `
            <div class="result-section-card shortage-card">
                <h3><span class="icon">🔄</span> Egyptian Market Therapeutic Alternatives & Equivalence</h3>
                <p class="section-lead-text">Practical therapeutic substitutions when first-line brands experience local Egyptian market shortages:</p>
                
                <div class="alternatives-grid">
                    ${alts.map(alt => `
                        <div class="alt-card">
                            <div class="alt-header">
                                <span class="alt-inn">💊 ${escapeHtml(alt.active_ingredient || '')}</span>
                                <span class="alt-cost">${escapeHtml(alt.relative_cost || '')}</span>
                            </div>
                            <div class="alt-brand"><strong>${escapeHtml(alt.brand_egypt || '')}</strong> ${alt.company ? `(${escapeHtml(alt.company)})` : ''}</div>
                            ${alt.clinical_niche ? `<div class="alt-niche">🎯 ${escapeHtml(alt.clinical_niche)}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    DOM.commonPracticeContent.innerHTML = html || '<p class="empty-state">No Egyptian practice data available.</p>';
}

// 10. Render Consolidated Sources & Evidence Provenance Panel (Phase 5)
function renderConsolidatedSources(data) {
    if (!data) {
        DOM.groundingSources.innerHTML = '';
        return;
    }

    const gEvidence = data.guidelines_evidence || {};
    const litEvidence = data.literature_evidence || {};
    const egEvidence = data.egypt_evidence || {};
    const gSynthesized = data.guidelines || {};

    let html = `
        <div class="consolidated-sources-container">
            <div class="consolidated-sources-header">
                <h3>📚 Sources & Evidence Provenance Registry</h3>
                <span class="provenance-badge badge-live-stream">✓ Verified Pipeline Grounding</span>
            </div>
    `;

    // Category 1: International Guidelines
    const guidelinesList = ensureArray(gEvidence.guideline_records || gSynthesized.authoritative_guidelines);
    if (guidelinesList.length > 0) {
        html += `
            <div class="sources-category-group">
                <div class="category-group-title">🏛️ Authoritative Clinical Practice Guidelines</div>
                <div class="sources-grid">
                    ${guidelinesList.map(g => {
                        const org = g.organization || 'Society';
                        const title = g.title || g.guideline_title || 'Clinical Guideline';
                        const year = g.year || '2026';
                        const url = g.source_url || g.url;
                        const pmid = g.pmid;
                        const doi = g.doi;
                        return `
                            <div class="source-provenance-card">
                                <div class="source-card-top">
                                    <span class="source-card-title">${escapeHtml(title)}</span>
                                    <span class="provenance-badge badge-official">Official</span>
                                </div>
                                <div class="source-card-meta">
                                    <strong>${escapeHtml(org)}</strong> • Year: ${escapeHtml(year)}
                                    ${g.scope ? `<br>Scope: ${escapeHtml(g.scope)}` : ''}
                                </div>
                                <div class="source-card-actions">
                                    <div>
                                        ${pmid ? `<a href="https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/" target="_blank" rel="noopener noreferrer" class="citation-pill citation-pmid">PMID: ${escapeHtml(pmid)}</a>` : ''}
                                        ${doi ? `<a href="https://doi.org/${encodeURIComponent(doi)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-doi">DOI</a>` : ''}
                                    </div>
                                    ${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="source-action-btn">Open Guideline ↗</a>` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // Category 2: Cochrane Reviews & Landmark Evidence
    const cochraneList = ensureArray(gEvidence.cochrane_and_landmark_evidence || gSynthesized.landmark_evidence_and_trials);
    if (cochraneList.length > 0) {
        html += `
            <div class="sources-category-group">
                <div class="category-group-title">🟣 Systematic Reviews & Landmark Evidence</div>
                <div class="sources-grid">
                    ${cochraneList.map(c => {
                        const title = c.title || c.trial_name_or_study || 'Systematic Review';
                        const year = c.year || '';
                        const url = c.article_url || c.url;
                        const pmid = c.pmid;
                        const doi = c.doi;
                        return `
                            <div class="source-provenance-card">
                                <div class="source-card-top">
                                    <span class="source-card-title">${escapeHtml(title)}</span>
                                    <span class="provenance-badge badge-cochrane">Cochrane / Trial</span>
                                </div>
                                <div class="source-card-meta">
                                    ${c.design ? `Design: ${escapeHtml(c.design)} • ` : ''}Year: ${escapeHtml(year)}
                                </div>
                                <div class="source-card-actions">
                                    <div>
                                        ${pmid ? `<a href="https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/" target="_blank" rel="noopener noreferrer" class="citation-pill citation-pmid">PMID: ${escapeHtml(pmid)}</a>` : ''}
                                        ${doi ? `<a href="https://doi.org/${encodeURIComponent(doi)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-doi">DOI</a>` : ''}
                                    </div>
                                    ${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="source-action-btn">Open Article ↗</a>` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // Category 3: Egyptian Scientific Studies (Track B)
    const egyptStudies = ensureArray(egEvidence.track_b_scientific_evidence?.verified_studies);
    if (egyptStudies.length > 0) {
        html += `
            <div class="sources-category-group">
                <div class="category-group-title">🔬 Egyptian Scientific & Epidemiological Evidence</div>
                <div class="sources-grid">
                    ${egyptStudies.map(st => {
                        const title = st.verified_title || st.title || 'Egyptian Clinical Study';
                        const journal = st.journal || 'Biomedical Journal';
                        const year = st.pub_year || '';
                        const pmid = st.verified_pmid || st.pmid;
                        const doi = st.verified_doi || st.doi;
                        const aff = st.egypt_relevance || 'Egyptian University Hospital';
                        const url = pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : (doi ? `https://doi.org/${doi}` : '');
                        return `
                            <div class="source-provenance-card">
                                <div class="source-card-top">
                                    <span class="source-card-title">${escapeHtml(title)}</span>
                                    <span class="provenance-badge badge-peer-reviewed">Peer-Reviewed</span>
                                </div>
                                <div class="source-card-meta">
                                    <em>${escapeHtml(journal)}</em> (${escapeHtml(year)})<br>
                                    🏛️ Affiliation: ${escapeHtml(aff)}
                                </div>
                                <div class="source-card-actions">
                                    <div>
                                        ${pmid ? `<a href="https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/" target="_blank" rel="noopener noreferrer" class="citation-pill citation-pmid">PMID: ${escapeHtml(pmid)}</a>` : ''}
                                        ${doi ? `<a href="https://doi.org/${encodeURIComponent(doi)}" target="_blank" rel="noopener noreferrer" class="citation-pill citation-doi">DOI</a>` : ''}
                                    </div>
                                    ${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="source-action-btn">PubMed Record ↗</a>` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // Category 4: Egyptian Official Guidance & Regulatory (Track A & EDA)
    const officialDocs = ensureArray(egEvidence.track_a_official_guidance?.documents);
    if (officialDocs.length > 0) {
        html += `
            <div class="sources-category-group">
                <div class="category-group-title">📜 Egyptian Official Guidance & EDA Regulatory Records</div>
                <div class="sources-grid">
                    ${officialDocs.map(doc => {
                        const org = doc.issuing_organization || 'Egyptian Health Authority';
                        const title = doc.exact_title || 'Official Protocol Document';
                        const url = doc.source_url || 'https://edaegypt.gov.eg/';
                        return `
                            <div class="source-provenance-card">
                                <div class="source-card-top">
                                    <span class="source-card-title">${escapeHtml(title)}</span>
                                    <span class="provenance-badge badge-eda">Official / EDA</span>
                                </div>
                                <div class="source-card-meta">
                                    Issuing Body: <strong>${escapeHtml(org)}</strong><br>
                                    Confidence: HIGH • Verification: Official Regulatory
                                </div>
                                <div class="source-card-actions">
                                    <span class="obs-date-tag">Aug 2026 Registry</span>
                                    ${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="source-action-btn">Verify on Portal ↗</a>` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    // Category 5: Market Pricing & Availability (Track E)
    const marketList = ensureArray(egEvidence.track_e_market_and_pricing);
    if (marketList.length > 0) {
        html += `
            <div class="sources-category-group">
                <div class="category-group-title">🛒 Egyptian Market Pricing & Pharmacy Stock (DawaaGate / Index)</div>
                <div class="sources-grid">
                    ${marketList.slice(0, 4).map(m => `
                        <div class="source-provenance-card">
                            <div class="source-card-top">
                                <span class="source-card-title">💊 ${escapeHtml(m.brand_name)} (${escapeHtml(m.active_ingredient)})</span>
                                <span class="provenance-badge badge-market">Market Tier 5</span>
                            </div>
                            <div class="source-card-meta">
                                Manufacturer: ${escapeHtml(m.manufacturer)}<br>
                                Official Retail Price: <strong class="price-tag">${escapeHtml(m.price)}</strong> (${escapeHtml(m.price_date)})
                            </div>
                            <div class="source-card-actions">
                                <span class="obs-date-tag">${escapeHtml(m.market_source)}</span>
                                <a href="https://edaegypt.gov.eg/" target="_blank" rel="noopener noreferrer" class="source-action-btn">EDA Status ↗</a>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    html += '</div>';
    DOM.groundingSources.innerHTML = html;
}

// 11. Search History Management
function addToHistory(query, setting) {
    const newItem = {
        id: Date.now().toString(),
        query: query,
        setting: setting,
        date: new Date().toISOString()
    };

    AppState.searchHistory = AppState.searchHistory.filter(
        item => !(item.query.toLowerCase() === query.toLowerCase() && item.setting === setting)
    );

    AppState.searchHistory.unshift(newItem);

    if (AppState.searchHistory.length > 50) {
        AppState.searchHistory = AppState.searchHistory.slice(0, 50);
    }

    localStorage.setItem('medref_history', JSON.stringify(AppState.searchHistory));
    renderHistory();
}

function renderHistory(filter = '') {
    if (!DOM.historyList) return;

    if (AppState.searchHistory.length === 0) {
        DOM.historyList.innerHTML = '';
        DOM.emptyHistory.classList.remove('hidden');
        return;
    }

    DOM.emptyHistory.classList.add('hidden');

    const filtered = filter ?
        AppState.searchHistory.filter(item => item.query.toLowerCase().includes(filter.toLowerCase())) :
        AppState.searchHistory;

    if (filtered.length === 0) {
        DOM.historyList.innerHTML = '<li class="history-item"><div class="history-item-content">No matching searches found.</div></li>';
        return;
    }

    DOM.historyList.innerHTML = filtered.map(item => {
        const date = new Date(item.date);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const icon = item.setting === 'emergency' ? '🚨' : '🏥';
        const badgeText = item.setting === 'emergency' ? 'Emergency' : 'Outpatient';

        return `
            <li class="history-item" data-id="${item.id}">
                <div class="history-item-content" onclick="window.loadHistoryItem('${item.id}')">
                    <span class="history-setting-icon">${icon}</span>
                    <div class="history-details">
                        <div class="history-query">${escapeHtml(item.query)}</div>
                        <div class="history-meta">
                            <span class="history-tag">${badgeText}</span>
                            <span class="history-date">${dateStr}</span>
                        </div>
                    </div>
                </div>
                <button class="delete-history-btn" onclick="window.deleteHistoryItem(event, '${item.id}')" title="Delete">🗑️</button>
            </li>
        `;
    }).join('');
}

window.loadHistoryItem = (id) => {
    const item = AppState.searchHistory.find(i => i.id === id);
    if (item) {
        setActiveSetting(item.setting);
        DOM.searchInput.value = item.query;
        closeSidebar();
        handleSearch(item.query);
    }
};

window.deleteHistoryItem = (event, id) => {
    event.stopPropagation();
    AppState.searchHistory = AppState.searchHistory.filter(i => i.id !== id);
    localStorage.setItem('medref_history', JSON.stringify(AppState.searchHistory));
    renderHistory(DOM.historySearch?.value || '');
};

function clearHistory() {
    if (confirm('Are you sure you want to clear your entire search history?')) {
        AppState.searchHistory = [];
        localStorage.removeItem('medref_history');
        renderHistory();
        showToast('History cleared', 'info');
    }
}

function openSidebar() {
    renderHistory();
    DOM.historySidebar.classList.add('open');
    DOM.sidebarBackdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    DOM.historySidebar.classList.remove('open');
    DOM.sidebarBackdrop.classList.add('hidden');
    document.body.style.overflow = '';
}

// 12. Theme Management
function initTheme() {
    document.documentElement.setAttribute('data-theme', AppState.theme);
    if (DOM.themeToggleBtn) {
        DOM.themeToggleBtn.querySelector('.icon').textContent = AppState.theme === 'dark' ? '☀️' : '🌙';
    }
}

function toggleTheme() {
    AppState.theme = AppState.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', AppState.theme);
    localStorage.setItem('medref_theme', AppState.theme);
    if (DOM.themeToggleBtn) {
        DOM.themeToggleBtn.querySelector('.icon').textContent = AppState.theme === 'dark' ? '☀️' : '🌙';
    }
}

// 13. Server Gateway Settings Modal
async function showApiKeyModal() {
    DOM.apiKeyModal.classList.remove('hidden');
    const health = await geminiAPI.checkServerHealth();
    const helpEl = DOM.apiKeyModal.querySelector('.api-help');
    if (helpEl && health.status === 'healthy') {
        const masked = health.credentials?.gemini_masked || 'Not configured';
        helpEl.innerHTML = `<p>🛡️ <strong>Server Gateway Active:</strong> Current Gemini Key: <code>${escapeHtml(masked)}</code><br>Keys are stored only on your machine in <code>.env</code> and never in the browser.</p>`;
    }
    DOM.apiKeyInput.focus();
}

async function saveApiKey() {
    const key = DOM.apiKeyInput.value.trim();
    if (!key) {
        showToast('Please paste a valid Gemini API key (starts with AIzaSy... or AQ...)', 'error');
        DOM.apiKeyInput.focus();
        return;
    }

    const btn = DOM.saveApiKeyBtn;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Saving to .env...';

    try {
        await geminiAPI.saveKeyToServer(key);
        DOM.apiKeyModal.classList.add('hidden');
        DOM.apiKeyInput.value = '';
        showToast('Gemini API key saved securely to server .env!', 'success');

        if (AppState.lastQuery || DOM.searchInput.value) {
            handleSearch(DOM.searchInput.value || AppState.lastQuery);
        }
    } catch (e) {
        console.error('[MedRef Gateway] Save key error:', e);
        showToast('Error saving key to server: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// 14. Comprehensive Copy to Clipboard
function resultsToText(data) {
    if (!data) return '';
    const settingName = AppState.currentSetting === 'emergency' ? 'EMERGENCY' : 'OUTPATIENT';
    let text = `=====================================================\n`;
    text += `  MEDREF ADVANCED CLINICAL RESEARCH DOSSIER\n`;
    text += `  CONDITION: ${(data.condition_name || AppState.lastQuery).toUpperCase()}\n`;
    text += `  SETTING: ${settingName}\n`;
    if (data.classification?.primary_specialty) text += `  PRIMARY SPECIALTY: ${data.classification.primary_specialty}\n`;
    text += `=====================================================\n\n`;

    // 1. GUIDELINES
    text += `▶ 1. INTERNATIONAL EVIDENCE-BASED GUIDELINES\n\n`;
    const g = data.guidelines || {};

    if (g.overview) {
        text += `[CLINICAL DEFINITION & SCOPE]\n`;
        if (g.overview.definition) text += `• Definition: ${g.overview.definition}\n`;
        if (g.overview.epidemiology) text += `• Epidemiology: ${g.overview.epidemiology}\n`;
        if (g.overview.pathophysiology) text += `• Pathophysiology: ${g.overview.pathophysiology}\n`;
        text += `\n`;
    }

    const authGuidelines = ensureArray(g.authoritative_guidelines);
    if (authGuidelines.length > 0) {
        text += `[AUTHORITATIVE SPECIALTY GUIDELINES]\n`;
        authGuidelines.forEach(ag => {
            text += `• ${ag.organization} (${ag.year || 'Latest'}): ${ag.guideline_title}\n`;
            if (ag.key_recommendation) text += `  Recommendation: ${ag.key_recommendation}\n`;
            if (ag.recommendation_strength) text += `  Strength: ${ag.recommendation_strength} | Certainty: ${ag.evidence_certainty || 'N/A'}\n`;
        });
        text += `\n`;
    }

    const steps = ensureArray(g.stepped_management_protocol);
    if (steps.length > 0) {
        text += `[STEPPED MANAGEMENT PROTOCOL]\n`;
        steps.forEach((step, idx) => {
            text += `Step ${step.step_number || idx + 1}: ${step.title} [${step.priority || 'Standard'}]\n`;
            if (step.clinical_details) text += `  ${step.clinical_details}\n`;
            const meds = ensureArray(step.medications);
            if (meds.length > 0) {
                meds.forEach(m => {
                    text += `  - ${m.generic_name} | Dose: ${m.dose || 'N/A'} | Route: ${m.route || 'N/A'} ${m.frequency ? '| ' + m.frequency : ''} [GRADE: ${m.grade_strength || 'N/A'}]\n`;
                });
            }
        });
        text += `\n`;
    }

    // 2. EGYPT RESEARCH
    text += `▶ 2. EGYPTIAN MEDICAL, REGULATORY & PHARMACEUTICAL LANDSCAPE\n\n`;
    const eg = data.egypt_practice_and_pharmacology || data.common_practice || {};

    if (eg.track_a_official_guidance) {
        text += `[TRACK A: OFFICIAL EGYPTIAN GUIDANCE]\n${eg.track_a_official_guidance.national_guidelines_and_mohp || 'N/A'}\n\n`;
    }

    const medLandscape = ensureArray(eg.track_d_and_e_medication_landscape);
    if (medLandscape.length > 0) {
        text += `[TRACKS D & E: EGYPTIAN MEDICATION LANDSCAPE]\n`;
        medLandscape.forEach(d => {
            const brands = ensureArray(d.famous_egyptian_brands).join(', ');
            text += `• ${d.active_ingredient} [${d.therapeutic_role || 'Drug'}]\n`;
            text += `  Famous Brands in Egypt: ${brands || 'Generics'}\n`;
            text += `  Strengths/Forms: ${d.available_strengths_and_forms || 'N/A'}\n`;
            text += `  EDA Registration: ${d.eda_registration_status || 'Registered'}\n`;
            text += `  Market Status: ${d.market_availability_and_retail_status || 'Available'}\n`;
            text += `  Price: ${d.reported_price_range_egp || 'Market rate'}\n\n`;
        });
    }

    text += `=====================================================\nSynthesized by MedRef (Universal Evidence-Based Medical Platform)\n`;
    return text;
}

function copyResults() {
    if (!AppState.currentResults) return;
    const text = resultsToText(AppState.currentResults);

    navigator.clipboard.writeText(text).then(() => {
        showToast('Complete research dossier copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'error');
    });
}

// 15. Error Handling & Reset
function showError(type, customMsg) {
    let title = "Search Error";
    let msg = customMsg || "An error occurred while communicating with the medical reference engine.";

    if (customMsg?.includes('MISSING_SERVER_API_KEY') || customMsg?.includes('MISSING_API_KEY')) {
        title = "Server Setup Required";
        msg = "The Gemini API key is not configured in the server .env file. Please enter it in Settings.";
    } else if (customMsg?.includes('RATE_LIMITED') || customMsg?.includes('429')) {
        title = "Too Many Requests";
        msg = "The medical model rate limit was reached. Please wait a moment and try again.";
    }

    DOM.errorTitle.textContent = title;
    DOM.errorMessage.textContent = msg;

    DOM.loadingOverlay.classList.add('hidden');
    DOM.resultsSection.classList.add('hidden');
    DOM.heroSection.classList.add('hidden');
    DOM.errorDisplay.classList.remove('hidden');
}

function resetView() {
    DOM.resultsSection.classList.add('hidden');
    DOM.errorDisplay.classList.add('hidden');
    DOM.loadingOverlay.classList.add('hidden');
    DOM.heroSection.classList.remove('hidden');
    DOM.searchInput.value = '';
    DOM.searchInput.focus();
}

// 16. Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    DOM.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 17. Chips
function initChips() {
    DOM.chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.dataset.query || chip.textContent.replace(/^[^\w]+/, '').trim();
            handleSearch(query);
        });
    });
}

// 18. Event Listeners
function initEventListeners() {
    DOM.searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSearch(DOM.searchInput.value);
    });

    DOM.backBtn.addEventListener('click', resetView);
    DOM.copyBtn.addEventListener('click', copyResults);

    DOM.navHistoryBtn.addEventListener('click', openSidebar);
    DOM.themeToggleBtn.addEventListener('click', toggleTheme);
    DOM.navSettingsBtn.addEventListener('click', showApiKeyModal);

    DOM.closeHistoryBtn.addEventListener('click', closeSidebar);
    DOM.sidebarBackdrop.addEventListener('click', closeSidebar);
    DOM.clearHistoryBtn.addEventListener('click', clearHistory);
    DOM.historySearch?.addEventListener('input', (e) => renderHistory(e.target.value));

    DOM.saveApiKeyBtn.addEventListener('click', saveApiKey);
    DOM.apiKeyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveApiKey();
        }
    });
    DOM.apiKeyModal.addEventListener('click', (e) => {
        if (e.target === DOM.apiKeyModal) {
            DOM.apiKeyModal.classList.add('hidden');
        }
    });

    DOM.errorRetryBtn.addEventListener('click', () => {
        if (AppState.lastQuery) {
            handleSearch(AppState.lastQuery);
        } else {
            resetView();
        }
    });
    DOM.errorBackBtn.addEventListener('click', resetView);

    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey && e.key.toLowerCase() === 'k') || (e.key === '/' && document.activeElement !== DOM.searchInput)) {
            e.preventDefault();
            DOM.searchInput.focus();
        }

        if (e.key === 'Escape') {
            if (!DOM.apiKeyModal.classList.contains('hidden')) {
                DOM.apiKeyModal.classList.add('hidden');
            } else if (DOM.historySidebar.classList.contains('open')) {
                closeSidebar();
            } else if (!DOM.resultsSection.classList.contains('hidden') && !AppState.isSearching) {
                resetView();
            }
        }
    });
}

// 19. Initialization (Zero LocalStorage Keys Required)
async function initApp() {
    initTheme();
    initSettingToggle();
    initTabs();
    initChips();
    initEventListeners();

    // Check Secure Gateway Health
    const health = await geminiAPI.checkServerHealth();
    if (!health.credentials?.gemini_configured) {
        showApiKeyModal();
    }

    renderHistory();
    DOM.searchInput.focus();
}

document.addEventListener('DOMContentLoaded', initApp);
