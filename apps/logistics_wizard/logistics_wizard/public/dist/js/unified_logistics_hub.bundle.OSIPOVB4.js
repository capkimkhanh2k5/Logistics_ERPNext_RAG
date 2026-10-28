(()=>{var Z=Object.defineProperty,ee=Object.defineProperties;var te=Object.getOwnPropertyDescriptors;var X=Object.getOwnPropertySymbols;var ne=Object.prototype.hasOwnProperty,ie=Object.prototype.propertyIsEnumerable;var Q=(u,e,t)=>e in u?Z(u,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):u[e]=t,W=(u,e)=>{for(var t in e||(e={}))ne.call(e,t)&&Q(u,t,e[t]);if(X)for(var t of X(e))ie.call(e,t)&&Q(u,t,e[t]);return u},J=(u,e)=>ee(u,te(e));window.UNIFIED_LOGISTICS_HUB_HTML=`<div class="logistics-page-container">
    <!-- LEFT VERTICAL SIDEBAR TAB NAVIGATION (Hidden - replaced by top horizontal tab bar to remove redundancy with Frappe system sidebar) -->
    <aside class="logistics-tabs-nav" id="logistics-sidebar-nav" style="display: none !important;">
    </aside>

    <!-- RIGHT MAIN CONTENT AREA (Takes 100% full width) -->
    <div class="logistics-main-content" style="width: 100%; flex: 1;">
        <!-- TOP HORIZONTAL TAB BAR (Sleek Modern SaaS Style) -->
        <div class="logistics-horizontal-tab-bar">
            <button class="logistics-nav-tab active" data-tab="overview" data-route="trade-case-overview" id="btn-tab-overview" title="Trade Case Dossier">
                <span class="tab-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                    </svg>
                </span>
                <span class="tab-text">Trade Case Dossier</span>
            </button>
            <button class="logistics-nav-tab" data-tab="executive" data-route="executive-dashboard" id="btn-tab-executive" title="Executive Dashboard">
                <span class="tab-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="7" height="9"></rect>
                        <rect x="14" y="3" width="7" height="5"></rect>
                        <rect x="14" y="12" width="7" height="9"></rect>
                        <rect x="3" y="16" width="7" height="5"></rect>
                    </svg>
                </span>
                <span class="tab-text">Executive Dashboard</span>
            </button>
            <button class="logistics-nav-tab" data-tab="tracking" data-route="shipment-tracking-hub" id="btn-tab-tracking" title="Shipment Tracking Hub">
                <span class="tab-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
                    </svg>
                </span>
                <span class="tab-text">Shipment Tracking Hub</span>
            </button>
            <button class="logistics-nav-tab" data-tab="cost" data-route="trade-cost-dashboard" id="btn-tab-cost" title="Trade Cost Dashboard">
                <span class="tab-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                </span>
                <span class="tab-text">Trade Cost Dashboard</span>
            </button>
            <button class="logistics-nav-tab" data-tab="copilot" data-route="logistics-ai-copilot" id="btn-tab-copilot" title="Logistics AI Copilot">
                <span class="tab-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8L12 2z"></path>
                    </svg>
                </span>
                <span class="tab-text">Logistics AI Copilot</span>
            </button>
            <button class="logistics-nav-tab" data-tab="rag-admin" data-route="rag-admin-center" id="btn-tab-rag-admin" title="RAG Admin Center">
                <span class="tab-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                    </svg>
                </span>
                <span class="tab-text" style="color: #0284c7; font-weight: 600;">RAG Admin Center</span>
            </button>
        </div>
        <!-- TAB 1: EXECUTIVE DASHBOARD (GLOBAL OPERATIONS COMMAND CENTER) -->
        <div class="logistics-tab-pane active" id="tab-pane-executive">
            <!-- Header bar with filter and refresh -->
            <div class="exec-header-bar">
                <div class="exec-title-block">
                    <h2 class="exec-title">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="3" width="7" height="9"></rect>
                            <rect x="14" y="3" width="7" height="5"></rect>
                            <rect x="14" y="12" width="7" height="9"></rect>
                            <rect x="3" y="16" width="7" height="5"></rect>
                        </svg>
                        Executive Logistics Command Center
                    </h2>
                    <p class="exec-subtitle">B\u1EE9c tranh v\u0129 m\xF4 to\xE0n di\u1EC7n v\u1EC1 l\u01B0u l\u01B0\u1EE3ng h\xE0ng h\xF3a, s\u1EE9c kh\u1ECFe h\xE0nh tr\xECnh, ki\u1EC3m so\xE1t chi ph\xED & r\u1EE7i ro</p>
                </div>
                <div class="exec-header-actions">
                    <div class="exec-filter-group">
                        <label for="exec-time-range" class="exec-filter-label"><i class="fa fa-calendar"></i> Chu k\u1EF3:</label>
                        <select id="exec-time-range" class="form-control exec-time-select">
                            <option value="30d" selected>30 ng\xE0y g\u1EA7n \u0111\xE2y</option>
                            <option value="90d">Qu\xFD hi\u1EC7n t\u1EA1i (Q4)</option>
                            <option value="ytd">N\u0103m 2026</option>
                        </select>
                    </div>
                    <button class="btn btn-default btn-sm" id="exec-btn-refresh" title="L\xE0m m\u1EDBi s\u1ED1 li\u1EC7u">
                        <i class="fa fa-refresh"></i> L\xE0m m\u1EDBi
                    </button>
                </div>
            </div>

            <!-- SECTION 1: 4 VISUAL METRIC TILES C\xD3 MINI PROGRESS BAR -->
            <div class="exec-kpi-grid">
                <!-- KPI 1: Active Cases -->
                <div class="exec-kpi-card">
                    <div class="exec-kpi-top">
                        <div class="exec-kpi-info">
                            <span class="exec-kpi-label">T\u1ED5ng \u0110\u01A1n H\xE0ng \u0110ang Ch\u1EA1y</span>
                            <div class="exec-kpi-val-row">
                                <span class="exec-kpi-value" id="exec-val-total-cases">28</span>
                                <span class="exec-badge exec-badge-success">+12% MoM</span>
                            </div>
                        </div>
                        <div class="exec-kpi-icon-wrap icon-blue">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                        </div>
                    </div>
                    <div class="exec-kpi-progress">
                        <div class="exec-progress-bar bg-blue" id="exec-bar-import" style="width: 71%;" title="Nh\u1EADp kh\u1EA9u: 20"></div>
                        <div class="exec-progress-bar bg-emerald" id="exec-bar-export" style="width: 29%;" title="Xu\u1EA5t kh\u1EA9u: 8"></div>
                    </div>
                    <div class="exec-kpi-footer">
                        <span><i class="fa fa-arrow-circle-down text-blue"></i> Nh\u1EADp kh\u1EA9u: <strong id="exec-sub-import">20</strong> (71%)</span>
                        <span><i class="fa fa-arrow-circle-up text-emerald"></i> Xu\u1EA5t kh\u1EA9u: <strong id="exec-sub-export">8</strong> (29%)</span>
                    </div>
                </div>

                <!-- KPI 2: In-Transit Shipments -->
                <div class="exec-kpi-card">
                    <div class="exec-kpi-top">
                        <div class="exec-kpi-info">
                            <span class="exec-kpi-label">L\xF4 H\xE0ng \u0110ang Di Chuy\u1EC3n</span>
                            <div class="exec-kpi-val-row">
                                <span class="exec-kpi-value" id="exec-val-in-transit">18</span>
                                <span class="exec-badge exec-badge-info">64% Lu\u1ED3ng h\xE0ng</span>
                            </div>
                        </div>
                        <div class="exec-kpi-icon-wrap icon-cyan">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
                        </div>
                    </div>
                    <div class="exec-kpi-progress">
                        <div class="exec-progress-bar bg-cyan" id="exec-bar-transit" style="width: 78%;"></div>
                    </div>
                    <div class="exec-kpi-footer">
                        <span><i class="fa fa-ship text-cyan"></i> 14 \u0110\u01B0\u1EDDng bi\u1EC3n</span>
                        <span><i class="fa fa-plane text-blue"></i> 4 H\xE0ng kh\xF4ng</span>
                    </div>
                </div>

                <!-- KPI 3: Actionable Alerts -->
                <div class="exec-kpi-card">
                    <div class="exec-kpi-top">
                        <div class="exec-kpi-info">
                            <span class="exec-kpi-label">C\u1EA3nh B\xE1o & R\u1EE7i Ro Ch\u1EADm Tr\u1EC5</span>
                            <div class="exec-kpi-val-row">
                                <span class="exec-kpi-value text-amber" id="exec-val-alerts">3</span>
                                <span class="exec-badge exec-badge-amber">C\u1EA7n ch\xFA \xFD</span>
                            </div>
                        </div>
                        <div class="exec-kpi-icon-wrap icon-amber">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                        </div>
                    </div>
                    <div class="exec-kpi-progress">
                        <div class="exec-progress-bar bg-amber" style="width: 10%;"></div>
                    </div>
                    <div class="exec-kpi-footer">
                        <span><i class="fa fa-exclamation-triangle text-amber"></i> 1 Tr\u1EC5 l\u1ECBch ETA</span>
                        <span><i class="fa fa-clock-o text-amber"></i> 2 H\u1EA1n h\u1EA3i quan</span>
                    </div>
                </div>

                <!-- KPI 4: Total Spend & Budget -->
                <div class="exec-kpi-card">
                    <div class="exec-kpi-top">
                        <div class="exec-kpi-info">
                            <span class="exec-kpi-label">T\u1ED5ng Chi Ph\xED & Ng\xE2n S\xE1ch</span>
                            <div class="exec-kpi-val-row">
                                <span class="exec-kpi-value text-emerald" id="exec-val-spend">$1,245,500</span>
                                <span class="exec-badge exec-badge-success">-2.7% Ti\u1EBFt ki\u1EC7m</span>
                            </div>
                        </div>
                        <div class="exec-kpi-icon-wrap icon-emerald">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                        </div>
                    </div>
                    <div class="exec-kpi-progress">
                        <div class="exec-progress-bar bg-emerald" style="width: 97.3%;"></div>
                    </div>
                    <div class="exec-kpi-footer">
                        <span>D\u1EF1 to\xE1n: <strong>$1,280,000</strong></span>
                        <span>Ch\xEAnh l\u1EC7ch: <strong class="text-emerald">-$34,500</strong></span>
                    </div>
                </div>
            </div>

            <!-- SECTION 2: END-TO-END OPERATIONAL PIPELINE FUNNEL -->
            <div class="exec-pipeline-section">
                <div class="exec-section-header">
                    <div class="exec-section-title-wrap">
                        <h3 class="exec-section-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
                            D\xF2ng Ch\u1EA3y H\xE0ng H\xF3a To\xE0n H\u1EC7 Th\u1ED1ng (End-to-End Pipeline Funnel)
                        </h3>
                        <span class="exec-section-sub">Quan s\xE1t s\u1EF1 ph\xE2n b\u1ED5 \u0111\u01A1n h\xE0ng qua 5 c\u1ED5ng ki\u1EC3m so\xE1t v\u1EADn h\xE0nh \u0111\u1EC3 ph\xE1t hi\u1EC7n ngay \u0111i\u1EC3m ngh\u1EBDn</span>
                    </div>
                </div>
                <div class="exec-pipeline-flow" id="exec-pipeline-container">
                    <!-- Populated dynamically via JS -->
                </div>
            </div>

            <!-- SECTION 3: 2-COLUMN GRID (RADAR S\u1EE8C KH\u1ECEE + C\u01A0 C\u1EA4U CHI PH\xCD) -->
            <div class="exec-grid-two-col">
                <!-- LEFT: OPERATIONAL HEALTH & MODALITY -->
                <div class="exec-card">
                    <div class="exec-card-header">
                        <h4 class="exec-card-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
                            S\u1EE9c Kh\u1ECFe V\u1EADn H\xE0nh & Ph\u01B0\u01A1ng Th\u1EE9c V\u1EADn Chuy\u1EC3n
                        </h4>
                    </div>
                    <div class="exec-card-body">
                        <div class="exec-health-wrap">
                            <!-- SVG Donut Chart -->
                            <div class="exec-donut-box">
                                <svg class="exec-donut-svg" viewBox="0 0 36 36">
                                    <path class="donut-ring" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#f1f5f9" stroke-width="3.8"/>
                                    <path class="donut-segment segment-ontime" id="donut-segment-ontime" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#10b981" stroke-width="3.8" stroke-dasharray="81, 100" stroke-dashoffset="0"/>
                                    <path class="donut-segment segment-atrisk" id="donut-segment-atrisk" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#f59e0b" stroke-width="3.8" stroke-dasharray="13, 100" stroke-dashoffset="-81"/>
                                    <path class="donut-segment segment-critical" id="donut-segment-critical" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#ef4444" stroke-width="3.8" stroke-dasharray="6, 100" stroke-dashoffset="-94"/>
                                </svg>
                                <div class="exec-donut-center">
                                    <span class="donut-score" id="exec-health-score">94.2%</span>
                                    <span class="donut-label">\u1ED4n \u0110\u1ECBnh</span>
                                </div>
                            </div>
                            <div class="exec-health-legend" id="exec-health-legend">
                                <div class="legend-item">
                                    <span class="legend-dot bg-emerald"></span>
                                    <span class="legend-text">\u0110\xFAng Ti\u1EBFn \u0110\u1ED9 (On-Time)</span>
                                    <strong class="legend-val" id="legend-ontime-val">26 \u0111\u01A1n (81%)</strong>
                                </div>
                                <div class="legend-item">
                                    <span class="legend-dot bg-amber"></span>
                                    <span class="legend-text">C\u1EA7n Theo D\xF5i (At Risk)</span>
                                    <strong class="legend-val" id="legend-atrisk-val">4 \u0111\u01A1n (13%)</strong>
                                </div>
                                <div class="legend-item">
                                    <span class="legend-dot bg-coral"></span>
                                    <span class="legend-text">S\u1EF1 C\u1ED1 / Ch\u1EADm Tr\u1EC5</span>
                                    <strong class="legend-val" id="legend-critical-val">2 \u0111\u01A1n (6%)</strong>
                                </div>
                            </div>
                        </div>

                        <div class="exec-divider"></div>

                        <!-- Modality Split Progress Bars -->
                        <div class="exec-modality-block">
                            <span class="exec-subhead">T\u1EF7 Tr\u1ECDng Ph\u01B0\u01A1ng Th\u1EE9c V\u1EADn Chuy\u1EC3n:</span>
                            <div class="modality-row">
                                <span class="modality-title"><i class="fa fa-ship text-cyan"></i> \u0110\u01B0\u1EDDng bi\u1EC3n (FCL/LCL)</span>
                                <div class="modality-bar-wrap">
                                    <div class="modality-bar bg-cyan" style="width: 70%;"></div>
                                </div>
                                <span class="modality-pct">70% (22 l\xF4)</span>
                            </div>
                            <div class="modality-row">
                                <span class="modality-title"><i class="fa fa-plane text-blue"></i> H\xE0ng kh\xF4ng (Air Cargo)</span>
                                <div class="modality-bar-wrap">
                                    <div class="modality-bar bg-blue" style="width: 20%;"></div>
                                </div>
                                <span class="modality-pct">20% (6 l\xF4)</span>
                            </div>
                            <div class="modality-row">
                                <span class="modality-title"><i class="fa fa-truck text-emerald"></i> V\u1EADn t\u1EA3i b\u1ED9 (Trucking)</span>
                                <div class="modality-bar-wrap">
                                    <div class="modality-bar bg-emerald" style="width: 10%;"></div>
                                </div>
                                <span class="modality-pct">10% (3 l\xF4)</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- RIGHT: FINANCIAL COST BREAKDOWN & BUDGET CONTROL -->
                <div class="exec-card">
                    <div class="exec-card-header">
                        <h4 class="exec-card-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                            C\u01A1 C\u1EA5u Chi Ph\xED Logistics Theo Nh\xF3m Nghi\u1EC7p V\u1EE5
                        </h4>
                        <span class="exec-badge exec-badge-success">Ti\u1EBFt ki\u1EC7m +$34,500</span>
                    </div>
                    <div class="exec-card-body">
                        <div class="exec-cost-bars-list" id="exec-cost-breakdown-list">
                            <!-- Populated dynamically via JS -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- SECTION 4: 2-COLUMN GRID (H\xC0NH LANG V\u1EACN T\u1EA2I + TH\u1EBA C\u1EA2NH B\xC1O H\xC0NH \u0110\u1ED8NG NHANH) -->
            <div class="exec-grid-two-col">
                <!-- LEFT: KEY TRADE CORRIDORS -->
                <div class="exec-card">
                    <div class="exec-card-header">
                        <h4 class="exec-card-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                            H\xE0nh Lang V\u1EADn T\u1EA3i Tr\u1ECDng \u0110i\u1EC3m & T\u1EA7n Su\u1EA5t
                        </h4>
                    </div>
                    <div class="exec-card-body" id="exec-corridors-container">
                        <!-- Populated dynamically via JS -->
                    </div>
                </div>

                <!-- RIGHT: ACTIONABLE RADAR ALERTS -->
                <div class="exec-card">
                    <div class="exec-card-header">
                        <h4 class="exec-card-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                            S\u1EF1 C\u1ED1 C\u1EA7n Can Thi\u1EC7p Ngay (Action Radar)
                        </h4>
                        <span class="exec-subhead-badge text-amber">3 V\u1EA5n \u0111\u1EC1</span>
                    </div>
                    <div class="exec-card-body" id="exec-alerts-container">
                        <!-- Populated dynamically via JS with action button linking to Tab 2 -->
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: TRADE CASE DOSSIER -->
        <div class="logistics-tab-pane" id="tab-pane-trade-case">
        <!-- N\xDAT CH\u1ECCN H\u1ED2 S\u01A0 N\u1EB0M NGAY TRONG TAB N\xC0Y -->
        <div class="tc-tab-control-bar">
            <div class="tc-select-case-group">
                <label for="tc-case-selector" class="tc-select-label">
                    <i class="fa fa-folder-open" style="color: #0284c7;"></i> Ch\u1ECDn h\u1ED3 s\u01A1 Trade Case:
                </label>
                <div class="tc-select-wrapper">
                    <select id="tc-case-selector" class="form-control tc-case-select-dropdown">
                        <!-- Populated dynamically via API -->
                    </select>
                </div>
            </div>
            <div class="tc-tab-control-actions">
                <button class="btn btn-default btn-sm" id="tc-btn-refresh-case" title="L\xE0m m\u1EDBi t\u1ED5ng quan">
                    <i class="fa fa-refresh"></i> L\xE0m m\u1EDBi
                </button>
                <button class="btn btn-default btn-sm" id="tc-btn-edit-case" title="Ch\u1EC9nh s\u1EEDa h\u1ED3 s\u01A1 DocType">
                    <i class="fa fa-pencil"></i> Ch\u1EC9nh s\u1EEDa Case
                </button>
            </div>
        </div>

        <!-- KH\u1ED0I 1: HEADER IDENTIFICATION -->
        <div class="tc-card" id="tc-header-card">
            <div class="tc-header-top">
                <div class="tc-id-badges">
                    <span class="tc-badge-id" id="tc-id-text"><span id="tc-header-id">IMP-2026-001</span></span>
                    <span class="tc-badge-status" id="tc-status-badge"><span id="tc-header-status">IN TRANSIT</span></span>
                    <span class="tc-badge-health warning" id="tc-health-badge"><span id="tc-header-health">Health: ATTENTION</span></span>
                    <span class="tc-badge-priority" id="tc-priority-badge"><span id="tc-header-priority">Normal Priority</span></span>
                </div>
                <div class="tc-header-actions">
                    <button class="btn btn-xs btn-default" id="tc-btn-refresh" title="L\xE0m m\u1EDBi"><i class="fa fa-refresh"></i> L\xE0m m\u1EDBi</button>
                </div>
            </div>
            <div class="tc-master-grid" id="tc-master-details">
                <div class="tc-detail-col">
                    <div class="tc-detail-label">Lo\u1EA1i h\xECnh / \u0110\u1ED1i t\xE1c:</div>
                    <div class="tc-detail-val" id="tc-party-text"><span id="tc-meta-party">Import Case \u2014 ABC Electronics Co., Ltd</span></div>
                </div>
                <div class="tc-detail-col">
                    <div class="tc-detail-label">\u0110\u01A1n mua h\xE0ng (PO/SO):</div>
                    <div class="tc-detail-val" id="tc-docref-text"><span id="tc-meta-po"><a href="/app/purchase-order/PO-2026-0042" class="tc-link">PO-2026-0042</a></span></div>
                </div>
                <div class="tc-detail-col">
                    <div class="tc-detail-label">Ph\u01B0\u01A1ng th\u1EE9c & Incoterm:</div>
                    <div class="tc-detail-val" id="tc-mode-incoterm"><span id="tc-meta-mode-incoterm">Ocean \u2022 FOB</span></div>
                </div>
                <div class="tc-detail-col">
                    <div class="tc-detail-label">Tuy\u1EBFn \u0111\u01B0\u1EDDng (Origin \u2794 Dest):</div>
                    <div class="tc-detail-val" id="tc-route-text"><span id="tc-meta-route">Shanghai Port, China \u2794 Da Nang Port, Vietnam</span></div>
                </div>
                <div class="tc-detail-col">
                    <div class="tc-detail-label">Ng\u01B0\u1EDDi ph\u1EE5 tr\xE1ch ch\xEDnh:</div>
                    <div class="tc-detail-val" id="tc-owner-text"><span id="tc-meta-owner">Nguyen Van A (Logistics)</span></div>
                </div>
                <div class="tc-detail-col">
                    <div class="tc-detail-label">Th\u1EDDi h\u1EA1n d\u1EF1 ki\u1EBFn \u0111\xF3ng:</div>
                    <div class="tc-detail-val" id="tc-expected-close"><span id="tc-meta-expected-close">2026-10-15</span></div>
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 2: LIFECYCLE STEPPER -->
        <div class="tc-card" id="tc-lifecycle-card">
            <div class="tc-card-header">
                <div class="tc-card-title">
                    <i class="fa fa-map-signs" style="color: #0284c7;"></i> Ti\u1EBFn Tr\xECnh Nghi\u1EC7p V\u1EE5 To\xE0n V\xF2ng \u0110\u1EDDi (Trade Case Lifecycle)
                </div>
                <div class="tc-current-stage-callout" id="tc-current-stage-callout">
                    <span id="tc-lifecycle-current-label">Giai \u0111o\u1EA1n hi\u1EC7n t\u1EA1i: <strong>In Transit</strong></span>
                </div>
            </div>
            <div class="tc-lifecycle-stepper" id="tc-lifecycle-stepper">
                <!-- Rendered dynamically via JS -->
            </div>
            <div class="tc-milestone-subgrid">
                <div class="tc-milestone-box prev">
                    <div class="tc-ms-tag">M\u1ED0C V\u1EEAA QUA (PREVIOUS)</div>
                    <div class="tc-ms-title" id="tc-prev-ms-title"><span id="tc-ms-prev-title">Vessel Departed Shanghai Port</span></div>
                    <div class="tc-ms-date" id="tc-prev-ms-date"><span id="tc-ms-prev-date">01/10/2026</span></div>
                </div>
                <div class="tc-milestone-box next">
                    <div class="tc-ms-tag">M\u1ED0C K\u1EBE TI\u1EBEP (NEXT)</div>
                    <div class="tc-ms-title" id="tc-next-ms-title"><span id="tc-ms-next-title">Arrival Da Nang Port</span></div>
                    <div class="tc-ms-date" id="tc-next-ms-date"><span id="tc-ms-next-date">08/10/2026 (Tr\u1EC5 +2 ng\xE0y)</span></div>
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 3: OVERALL HEALTH & READINESS GRID -->
        <div class="tc-health-grid" id="tc-health-grid">
            <!-- 6 th\u1EBB tr\u1EA1ng th\xE1i Rendered dynamically via JS -->
        </div>

        <!-- KH\u1ED0I 4 & 5: SHIPMENT SUMMARY & DOCUMENT READINESS -->
        <div class="tc-two-col-grid">
            <!-- KH\u1ED0I 4: SHIPMENT SUMMARY -->
            <div class="tc-card" id="tc-shipment-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-ship" style="color: #0284c7;"></i> V\u1EADn \u0110\u01A1n & H\xE0nh Tr\xECnh (Shipment Summary)
                    </div>
                    <button class="btn btn-xs btn-primary font-weight-bold tc-btn-goto-shipment tc-drill-down-shipment" id="tc-btn-goto-shipment" name="tc-btn-goto-shipment">
                        Xem Shipment Tracking <i class="fa fa-arrow-right"></i>
                    </button>
                </div>
                <div class="tc-shipment-summary-content" id="tc-shipment-body">
                    <div id="tc-shipment-summary-body"></div>
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>

            <!-- KH\u1ED0I 5: DOCUMENT READINESS -->
            <div class="tc-card" id="tc-documents-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-file-text-o" style="color: #0284c7;"></i> H\u1ED3 S\u01A1 & Ch\u1EE9ng T\u1EEB (Document Readiness)
                    </div>
                    <span class="tc-badge-soft" id="tc-docs-pct-badge"><span id="tc-doc-readiness-badge">8 / 10 S\u1EB5n s\xE0ng (80%)</span></span>
                </div>
                <div class="tc-docs-content" id="tc-docs-body"><div id="tc-doc-readiness-body"></div>
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 6 & 7: CUSTOMS & LANDED COST -->
        <div class="tc-two-col-grid">
            <!-- KH\u1ED0I 6: CUSTOMS & COMPLIANCE -->
            <div class="tc-card" id="tc-customs-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-gavel" style="color: #0284c7;"></i> H\u1EA3i Quan & Tu\xE2n Th\u1EE7 (Customs & Compliance)
                    </div>
                    <span class="tc-badge-soft" id="tc-customs-status-badge"><span id="tc-customs-badge">PREPARING (70%)</span></span>
                </div>
                <div class="tc-customs-content" id="tc-customs-body">
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>

            <!-- KH\u1ED0I 7: COST SUMMARY (LANDED COST) -->
            <div class="tc-card" id="tc-cost-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-calculator" style="color: #0284c7;"></i> Chi Ph\xED & Gi\xE1 Th\xE0nh Nh\u1EADp Kh\u1EA9u (Landed Cost Summary)
                    </div>
                    <span class="tc-badge-soft" id="tc-cost-status-badge">IN PROGRESS (+7.9%)</span>
                </div>
                <div class="tc-cost-content" id="tc-cost-body">
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 8 & 9: WAREHOUSE & OPEN EXCEPTIONS -->
        <div class="tc-two-col-grid">
            <!-- KH\u1ED0I 8: WAREHOUSE READINESS -->
            <div class="tc-card" id="tc-warehouse-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-building-o" style="color: #0284c7;"></i> Kho H\xE0ng & Giao Nh\u1EADn (Warehouse Readiness)
                    </div>
                    <span class="tc-badge-soft" id="tc-warehouse-status-badge"><span id="tc-wh-badge">NOT READY</span></span>
                </div>
                <div class="tc-warehouse-content" id="tc-warehouse-body"><div id="tc-wh-body"></div>
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>

            <!-- KH\u1ED0I 9: OPEN EXCEPTIONS -->
            <div class="tc-card" id="tc-exceptions-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-exclamation-triangle" style="color: #d97706;"></i> S\u1EF1 C\u1ED1 & Ngo\u1EA1i L\u1EC7 \u0110ang M\u1EDF (Top Open Exceptions)
                    </div>
                    <span class="tc-badge-soft danger" id="tc-open-exceptions-badge"><span id="tc-exceptions-badge">3 Open (1 Qu\xE1 h\u1EA1n)</span></span>
                </div>
                <div class="tc-exceptions-content" id="tc-exceptions-body"><div id="tc-exceptions-body-inner"></div>
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 10 & 11: UPCOMING ACTIONS & ERP DOCUMENTS -->
        <div class="tc-two-col-grid">
            <!-- KH\u1ED0I 10: UPCOMING ACTIONS & DEADLINES -->
            <div class="tc-card" id="tc-actions-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-calendar-check-o" style="color: #0284c7;"></i> H\xE0nh \u0110\u1ED9ng Ti\u1EBFp Theo & H\u1EA1n \u0110\u1ECBnh (Upcoming Actions)
                    </div>
                    <span class="tc-subtitle-tag">B\xE2y gi\u1EDD c\u1EA7n l\xE0m g\xEC ti\u1EBFp theo?</span>
                </div>
                <div class="tc-actions-content" id="tc-actions-body">
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>

            <!-- KH\u1ED0I 11: RELATED ERP DOCUMENTS -->
            <div class="tc-card" id="tc-erp-docs-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-link" style="color: #0284c7;"></i> Ch\u1EE9ng T\u1EEB ERPNext Li\xEAn K\u1EBFt (Related ERP Documents)
                    </div>
                </div>
                <div class="tc-erp-docs-content" id="tc-related-erp-body">
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 12 & 13: RESPONSIBILITY MATRIX & ACTIVITY TIMELINE -->
        <div class="tc-two-col-grid">
            <!-- KH\u1ED0I 12: RESPONSIBILITY MATRIX -->
            <div class="tc-card" id="tc-responsibility-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-users" style="color: #0284c7;"></i> Ph\xE2n C\xF4ng Tr\xE1ch Nhi\u1EC7m (Responsibility Matrix)
                    </div>
                </div>
                <div class="tc-responsibility-content" id="tc-responsibility-body">
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>

            <!-- KH\u1ED0I 13: ACTIVITY TIMELINE -->
            <div class="tc-card" id="tc-timeline-card">
                <div class="tc-card-header">
                    <div class="tc-card-title">
                        <i class="fa fa-history" style="color: #0284c7;"></i> Nh\u1EADt K\xFD Ho\u1EA1t \u0110\u1ED9ng & L\u1ECBch S\u1EED (Activity Audit Timeline)
                    </div>
                </div>
                <div class="tc-timeline-content" id="tc-activity-body">
                    <!-- Rendered dynamically via JS -->
                </div>
            </div>
        </div>

        <!-- KH\u1ED0I 14: QUICK ACTIONS & STAGE GATE -->
        <div class="tc-card" id="tc-stage-gate-card">
            <div class="tc-card-header">
                <div class="tc-card-title">
                    <i class="fa fa-bolt" style="color: #0284c7;"></i> Thao T\xE1c Nhanh & Ch\u1ED1t Ch\u1EB7n H\u1ED3 S\u01A1 (Quick Actions & Stage Gate)
                </div>
            </div>
            <div class="tc-stage-gate-content" id="tc-stage-gate-body">
                <!-- Rendered dynamically via JS -->
            </div>
        </div>
    </div>

    <!-- TAB 2: SHIPMENT TRACKING HUB (100% NGUY\xCAN B\u1EA2N C\u1EE6A 7d1ef41) -->
    <div class="logistics-tab-pane" id="tab-pane-shipment-tracking">
        <div class="shipment-tracking-hub-container">
            <!-- Top Action Header -->
            <div class="hub-header-bar">
                <div class="hub-title-block">
                    <h2 class="hub-title">
                        <span class="hub-title-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <polygon points="3 11 22 2 13 21 11 13 3 11"/>
                            </svg>
                        </span>
                        <span class="hub-title-text">Trung T\xE2m Qu\u1EA3n Tr\u1ECB V\u1EADn Chuy\u1EC3n To\xE0n C\u1EA7u</span>
                    </h2>
                    <p class="hub-subtitle">Gi\xE1m s\xE1t h\xE0nh tr\xECnh container, ti\u1EBFn \u0111\u1ED9 m\u1ED1c DCSA qu\u1ED1c t\u1EBF v\xE0 ph\xE1t hi\u1EC7n l\u1EC7ch l\u1ECBch tr\xECnh theo th\u1EDDi gian th\u1EF1c</p>
                </div>
                <div class="hub-header-actions">
                    <button class="btn btn-default btn-sm hub-btn-refresh" id="hub-btn-refresh" title="L\xE0m m\u1EDBi d\u1EEF li\u1EC7u">
                        <i class="fa fa-refresh"></i> L\xE0m m\u1EDBi
                    </button>
                    <button class="btn btn-primary btn-sm hub-btn-sync" id="hub-btn-sync-now" title="\u0110\u1ED3ng b\u1ED9 d\u1EEF li\u1EC7u t\u1EE9c th\xEC t\u1EEB h\xE3ng v\u1EADn t\u1EA3i">
                        <i class="fa fa-cloud-download"></i> \u0110\u1ED3ng b\u1ED9 t\u1EE9c th\xEC (Sync Now)
                    </button>
                </div>
            </div>

            <!-- KH\u1ED0I 1: 4 Th\u1EBB KPI Metrics (Icon Vector SVG Monoline) -->
            <div class="hub-kpi-grid">
                <div class="hub-kpi-card kpi-total" data-filter="all">
                    <div class="kpi-icon-wrap">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/>
                            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                            <line x1="12" y1="22.08" x2="12" y2="12"/>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">T\u1ED5ng s\u1ED1 l\xF4 h\xE0ng</div>
                        <div class="kpi-value" id="kpi-val-total">0</div>
                        <div class="kpi-desc">T\u1EA5t c\u1EA3 v\u1EADn \u0111\u01A1n trong h\u1EC7 th\u1ED1ng</div>
                    </div>
                </div>
                <div class="hub-kpi-card kpi-transit active" data-filter="In Transit">
                    <div class="kpi-icon-wrap">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="12 2 19 21 12 17 5 21 12 2"/>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">\u0110ang v\u1EADn chuy\u1EC3n</div>
                        <div class="kpi-value" id="kpi-val-transit">0</div>
                        <div class="kpi-desc">T\xE0u bi\u1EC3n & m\xE1y bay \u0111ang h\xE0nh tr\xECnh</div>
                    </div>
                </div>
                <div class="hub-kpi-card kpi-delayed" data-filter="Delayed">
                    <div class="kpi-icon-wrap">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">Ch\u1EADm ti\u1EBFn \u0111\u1ED9</div>
                        <div class="kpi-value" id="kpi-val-delayed">0</div>
                        <div class="kpi-desc">H\xE0nh tr\xECnh b\u1ECB l\u1EC7ch ETA > 1 ng\xE0y</div>
                    </div>
                </div>
                <div class="hub-kpi-card kpi-stale" data-filter="Stale">
                    <div class="kpi-icon-wrap">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">C\u1EA3nh b\xE1o ngo\u1EA1i l\u1EC7</div>
                        <div class="kpi-value" id="kpi-val-stale">0</div>
                        <div class="kpi-desc">Ch\u01B0a c\xF3 t\xEDn hi\u1EC7u m\u1EDBi t\u1EEB carrier</div>
                    </div>
                </div>
            </div>

            <!-- KH\u1ED0I 2: B\u1EA3n \u0111\u1ED3 Gi\xE1m s\xE1t To\xE0n c\u1EA7u T\u01B0\u01A1ng t\xE1c -->
            <div class="hub-map-card">
                <div class="hub-card-header">
                    <div class="card-header-title">
                        <span class="header-icon">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"/>
                                <line x1="2" y1="12" x2="22" y2="12"/>
                                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                            </svg>
                        </span>
                        <span class="header-text" id="hub-map-title">B\u1EA3n \u0111\u1ED3 Gi\xE1m s\xE1t To\xE0n c\u1EA7u (Fleet Overview)</span>
                    </div>
                    <div class="card-header-controls">
                        <span class="badge badge-info" id="hub-selected-shipment-badge" style="display:none;"></span>
                        <button class="btn btn-xs btn-default" id="hub-map-reset-btn" title="Tr\u1EDF v\u1EC1 g\xF3c nh\xECn to\xE0n c\u1EA7u">
                            <i class="fa fa-globe"></i> To\xE0n c\u1EA3nh
                        </button>
                    </div>
                </div>
                <div class="hub-map-wrapper">
                    <div id="lw-hub-map" class="lw-hub-map-canvas"></div>
                    <div id="hub-map-loading" class="hub-map-loading-overlay" style="display:none;">
                        <div class="spinner-border text-primary" role="status"></div>
                        <span>\u0110ang t\u1EA3i l\u1ED9 tr\xECnh & \u0111\u1ECBnh v\u1ECB ph\u01B0\u01A1ng ti\u1EC7n...</span>
                    </div>
                </div>
            </div>

            <!-- KH\u1ED0I 4: Visual Milestones Timeline Stepper (9 M\u1ED1c DCSA) -->
            <div class="hub-timeline-card" id="hub-stepper-card">
                <div class="hub-card-header">
                    <div class="card-header-title">
                        <span class="header-icon">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="4"/>
                                <line x1="1.05" y1="12" x2="8" y2="12"/>
                                <line x1="16" y1="12" x2="22.95" y2="12"/>
                            </svg>
                        </span>
                        <span class="header-text">Ti\u1EBFn Tr\xECnh 9 M\u1ED1c S\u1EF1 Ki\u1EC7n Qu\u1ED1c T\u1EBF DCSA (Milestones Stepper)</span>
                    </div>
                    <div class="card-header-actions">
                        <span class="hub-stepper-shipment-name" id="stepper-shipment-name">Ch\u01B0a ch\u1ECDn l\xF4 h\xE0ng</span>
                    </div>
                </div>
                <div class="hub-stepper-container">
                    <div class="hub-stepper-track" id="hub-stepper-track">
                        <!-- S\u1EBD \u0111\u01B0\u1EE3c render \u0111\u1ED9ng qua JS (9 m\u1ED1c: BOOKED, GATE_IN, LOADED, DEPARTED, TRANSSHIPMENT, ARRIVED, DISCHARGED, GATE_OUT, DELIVERED) -->
                    </div>
                </div>
            </div>

            <!-- T\u1EA6NG D\u01AF\u1EDAI: Chia 2 C\u1ED9t (B\u1EA3ng l\xF4 h\xE0ng chi ti\u1EBFt 65% + Trung t\xE2m C\u1EA3nh b\xE1o 35%) -->
            <div class="hub-split-section">
                <!-- KH\u1ED0I 3: B\u1EA3ng Qu\u1EA3n tr\u1ECB L\xF4 h\xE0ng Chi ti\u1EBFt (65%) -->
                <div class="hub-table-panel">
                    <div class="hub-card-header">
                        <div class="card-header-title">
                            <span class="header-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="8" y1="6" x2="21" y2="6"/>
                                    <line x1="8" y1="12" x2="21" y2="12"/>
                                    <line x1="8" y1="18" x2="21" y2="18"/>
                                    <line x1="3" y1="6" x2="3.01" y2="6"/>
                                    <line x1="3" y1="12" x2="3.01" y2="12"/>
                                    <line x1="3" y1="18" x2="3.01" y2="18"/>
                                </svg>
                            </span>
                            <span class="header-text">Danh S\xE1ch L\xF4 H\xE0ng Qu\u1ED1c T\u1EBF</span>
                        </div>
                        <div class="hub-search-box">
                            <i class="fa fa-search hub-search-icon"></i>
                            <input type="text" id="hub-search-input" class="form-control input-sm" placeholder="T\xECm m\xE3 v\u1EADn \u0111\u01A1n, container, B/L, PO, h\xE3ng t\xE0u...">
                        </div>
                    </div>

                    <!-- Filter Tabs -->
                    <div class="hub-filter-tabs">
                        <button class="hub-tab-btn active" data-tab="all">T\u1EA5t c\u1EA3 (<span id="tab-cnt-all">0</span>)</button>
                        <button class="hub-tab-btn" data-tab="In Transit">\u0110ang v\u1EADn chuy\u1EC3n (<span id="tab-cnt-transit">0</span>)</button>
                        <button class="hub-tab-btn" data-tab="Delayed">Tr\u1EC5 h\u1EA1n (<span id="tab-cnt-delayed">0</span>)</button>
                        <button class="hub-tab-btn" data-tab="Stale">M\u1EA5t t\xEDn hi\u1EC7u (<span id="tab-cnt-stale">0</span>)</button>
                        <button class="hub-tab-btn" data-tab="Delivered">\u0110\xE3 giao h\xE0ng (<span id="tab-cnt-delivered">0</span>)</button>
                    </div>

                    <!-- Shipment Data Table -->
                    <div class="hub-table-wrapper">
                        <table class="table table-hover hub-data-table" id="hub-shipments-table">
                            <thead>
                                <tr>
                                    <th style="width: 22%;">V\u1EADn \u0111\u01A1n / Container</th>
                                    <th style="width: 18%;">H\xE3ng t\xE0u & Ph\u01B0\u01A1ng ti\u1EC7n</th>
                                    <th style="width: 20%;">C\u1EA3ng \u0110i \u2794 \u0110\u1EBFn</th>
                                    <th style="width: 15%;">L\u1ECBch tr\xECnh (ETD / ETA)</th>
                                    <th style="width: 13%;">\u0110\u1ED9 tr\u1EC5</th>
                                    <th style="width: 12%; text-align: center;">Thao t\xE1c</th>
                                </tr>
                            </thead>
                            <tbody id="hub-shipments-tbody">
                                <tr>
                                    <td colspan="6" class="text-center text-muted" style="padding: 30px;">
                                        <i class="fa fa-spinner fa-spin"></i> \u0110ang t\u1EA3i d\u1EEF li\u1EC7u v\u1EADn chuy\u1EC3n...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- KH\u1ED0I 5: Trung T\xE2m C\u1EA3nh B\xE1o Ngo\u1EA1i L\u1EC7 & Bi\u1EBFn \u0110\u1ED9ng ETA (35%) -->
                <div class="hub-exceptions-panel">
                    <div class="hub-card-header">
                        <div class="card-header-title">
                            <span class="header-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                                    <line x1="12" y1="8" x2="12" y2="12"/>
                                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                                </svg>
                            </span>
                            <span class="header-text">Trung T\xE2m Ngo\u1EA1i L\u1EC7 & C\u1EA3nh B\xE1o (Exception Center)</span>
                        </div>
                        <span class="badge badge-warning" id="hub-exception-count-badge">0 s\u1EF1 c\u1ED1</span>
                    </div>
                    <div class="hub-exceptions-list" id="hub-exceptions-list">
                        <!-- S\u1EBD \u0111\u01B0\u1EE3c render \u0111\u1ED9ng qua JS -->
                        <div class="text-center text-muted" style="padding: 35px 15px;">
                            <i class="fa fa-check-circle text-success" style="font-size: 28px; margin-bottom: 8px;"></i>
                            <p style="margin: 0; font-size: 13px;">Kh\xF4ng c\xF3 s\u1EF1 c\u1ED1 ho\u1EB7c c\u1EA3nh b\xE1o ngo\u1EA1i l\u1EC7 \u0111ang m\u1EDF.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 3: TRADE COST & LANDED COST MANAGEMENT DASHBOARD -->
    <div class="logistics-tab-pane" id="tab-pane-trade-cost">
            <!-- 1. Top Control Bar (matching tc-tab-control-bar) -->
            <div class="tc-tab-control-bar">
                <div class="tc-select-case-group">
                    <label for="tcd-case-selector" class="tc-select-label">
                        <i class="fa fa-calculator" style="color: #0284c7;"></i> Ch\u1ECDn h\u1ED3 s\u01A1 Trade Case:
                    </label>
                    <div class="tc-select-wrapper">
                        <select id="tcd-case-selector" class="form-control tc-case-select-dropdown">
                            <option value="IMP-2026-001" selected>IMP-2026-001 - ABC Electronics Co., Ltd (Import Case \u2022 In Transit)</option>
                            <option value="EXP-2026-002">EXP-2026-002 - Global Coffee Exporter (Export Case \u2022 Ready)</option>
                            <option value="IMP-2026-003">IMP-2026-003 - Pacific Seafood Import (Import Case \u2022 Delivered)</option>
                        </select>
                    </div>
                </div>
                <div class="tc-tab-control-actions">
                    <div class="hub-filter-tabs" style="border: 1px solid #e2e8f0; border-radius: 6px; background: #ffffff; padding: 2px;">
                        <button class="hub-tab-btn active tcd-type-btn" data-type="all">T\u1EA5t c\u1EA3</button>
                        <button class="hub-tab-btn tcd-type-btn" data-type="import">Nh\u1EADp kh\u1EA9u (Landed Cost)</button>
                        <button class="hub-tab-btn tcd-type-btn" data-type="export">Xu\u1EA5t kh\u1EA9u (Export Margin)</button>
                    </div>
                    <button class="btn btn-default btn-sm" id="tcd-btn-refresh" title="L\xE0m m\u1EDBi"><i class="fa fa-refresh"></i> L\xE0m m\u1EDBi</button>
                    <button class="btn btn-primary btn-sm hub-btn-sync" id="tcd-btn-new-sheet"><i class="fa fa-plus"></i> L\u1EADp Cost Sheet</button>
                    <button class="btn btn-default btn-sm" id="tcd-btn-sync-lcv" title="\u0110\u1ED3ng b\u1ED9 sang ERPNext Landed Cost Voucher"><i class="fa fa-exchange"></i> \u0110\u1ED3ng b\u1ED9 LCV</button>
                </div>
            </div>

            <!-- 2. KPI Summary Grid (4 Cards matching Hub style) -->
            <div class="hub-kpi-grid">
                <div class="hub-kpi-card kpi-total">
                    <div class="kpi-icon-wrap">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2">
                            <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                            <line x1="12" y1="8" x2="12" y2="16"></line>
                            <line x1="8" y1="12" x2="16" y2="12"></line>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">Tr\u1ECB gi\xE1 h\xE0ng mua (FOB)</div>
                        <div class="kpi-value" id="tcd-kpi-po-val">$125,000.00</div>
                        <div class="kpi-desc">Tr\u1ECB gi\xE1 tr\xEAn h\u1EE3p \u0111\u1ED3ng ngo\u1EA1i th\u01B0\u01A1ng</div>
                    </div>
                </div>

                <div class="hub-kpi-card kpi-transit">
                    <div class="kpi-icon-wrap">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">Chi ph\xED d\u1EF1 to\xE1n (Estimated)</div>
                        <div class="kpi-value" id="tcd-kpi-est-val" style="color: #0284c7;">$16,800.00</div>
                        <div class="kpi-desc">\u0110\u1ECBnh m\u1EE9c chi ph\xED logistics d\u1EF1 ki\u1EBFn</div>
                    </div>
                </div>

                <div class="hub-kpi-card">
                    <div class="kpi-icon-wrap" style="background-color: #ecfdf5;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                            <line x1="12" y1="1" x2="12" y2="23"></line>
                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">Chi ph\xED th\u1EF1c t\u1EBF (Actual)</div>
                        <div class="kpi-value" id="tcd-kpi-act-val" style="color: #059669;">$18,350.00</div>
                        <div class="kpi-desc">T\u1ED5ng chi ph\xED theo h\xF3a \u0111\u01A1n nh\xE0 cung c\u1EA5p</div>
                    </div>
                </div>

                <div class="hub-kpi-card kpi-delayed">
                    <div class="kpi-icon-wrap">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2">
                            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                            <polyline points="17 6 23 6 23 12"></polyline>
                        </svg>
                    </div>
                    <div class="kpi-data">
                        <div class="kpi-label">Ch\xEAnh l\u1EC7ch chi ph\xED (Variance)</div>
                        <div class="kpi-value" id="tcd-kpi-var-val" style="color: #dc2626;">+$1,550.00 (+9.2%)</div>
                        <div class="kpi-desc">C\u1EA3nh b\xE1o: V\u01B0\u1EE3t d\u1EF1 to\xE1n ban \u0111\u1EA7u</div>
                    </div>
                </div>
            </div>

            <!-- 3. Split Section (65% / 35%) -->
            <div class="hub-split-section">
                <!-- C\u1ED8T TR\xC1I (65%): B\u1EA3ng K\xEA Chi Ti\u1EBFt 11 Kho\u1EA3n Chi Ph\xED & Custom Allocation Engine -->
                <div class="hub-table-panel">
                    <div class="hub-card-header">
                        <div class="card-header-title">
                            <span class="header-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2">
                                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                                    <line x1="8" y1="21" x2="16" y2="21"></line>
                                    <line x1="12" y1="17" x2="12" y2="21"></line>
                                </svg>
                            </span>
                            <span class="header-text">B\u1EA3ng K\xEA Chi Ti\u1EBFt 11 Kho\u1EA3n Chi Ph\xED Logistics (Cost Sheet Items)</span>
                        </div>
                        <div class="card-header-controls">
                            <span class="badge-status badge-in-transit" id="tcd-status-badge">\u0110ang \u0110\u1ED1i So\xE1t</span>
                        </div>
                    </div>

                    <div class="hub-table-wrapper" style="max-height: 380px;">
                        <table class="table hub-data-table">
                            <thead>
                                <tr>
                                    <th>Kho\u1EA3n Chi Ph\xED (Cost Type)</th>
                                    <th>Nh\xE0 Cung C\u1EA5p</th>
                                    <th>S\u1ED1 H\xF3a \u0110\u01A1n</th>
                                    <th class="text-right">D\u1EF1 To\xE1n</th>
                                    <th class="text-right">Th\u1EF1c T\u1EBF</th>
                                    <th class="text-right">Ch\xEAnh L\u1EC7ch</th>
                                    <th class="text-center">Tr\u1EA1ng Th\xE1i</th>
                                </tr>
                            </thead>
                            <tbody id="tcd-cost-items-tbody">
                                <!-- Rendered dynamically -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Custom Landed Cost Allocation Engine Card inside Panel -->
                    <div style="border-top: 1px solid #e2e8f0; padding: 16px 18px; background: #ffffff;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                            <div>
                                <h4 style="margin: 0; font-size: 13.5px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                                    <i class="fa fa-sliders" style="color: #0d9488;"></i>
                                    Custom Cost Allocation Engine (Ph\xE2n B\u1ED5 Gi\xE1 V\u1ED1n Landed Cost)
                                </h4>
                                <span style="font-size: 11.5px; color: #64748b;">T\u1EF1 \u0111\u1ED9ng ph\xE2n b\u1ED5 chi ph\xED v\xE0o t\u1EEBng m\u1EB7t h\xE0ng trong Purchase Receipt theo chu\u1EA9n k\u1EBF to\xE1n ERPNext</span>
                            </div>
                            <div style="display: flex; gap: 6px;">
                                <button class="btn btn-xs btn-default tcd-alloc-btn active" data-rule="weight"><i class="fa fa-balance-scale"></i> Tr\u1ECDng l\u01B0\u1EE3ng (Weight)</button>
                                <button class="btn btn-xs btn-default tcd-alloc-btn" data-rule="value"><i class="fa fa-dollar"></i> Tr\u1ECB gi\xE1 (Value)</button>
                                <button class="btn btn-xs btn-default tcd-alloc-btn" data-rule="qty"><i class="fa fa-cubes"></i> S\u1ED1 l\u01B0\u1EE3ng (Qty)</button>
                                <button class="btn btn-xs btn-default tcd-alloc-btn" data-rule="volume"><i class="fa fa-cube"></i> Th\u1EC3 t\xEDch (CBM)</button>
                            </div>
                        </div>

                        <div class="table-responsive" style="max-height: 240px; overflow-y: auto;">
                            <table class="table table-bordered hub-data-table" style="font-size: 12px;">
                                <thead>
                                    <tr style="background: #f8fafc;">
                                        <th>M\xE3 H\xE0ng (Item)</th>
                                        <th>T\xEAn M\u1EB7t H\xE0ng</th>
                                        <th class="text-center">S\u1ED1 L\u01B0\u1EE3ng</th>
                                        <th class="text-right">\u0110\u01A1n Gi\xE1 Mua</th>
                                        <th class="text-right">Ph\xED Ph\xE2n B\u1ED5</th>
                                        <th class="text-right">Gi\xE1 V\u1ED1n Th\u1EF1c T\u1EBF (Landed Cost)</th>
                                        <th class="text-center">% T\u0103ng</th>
                                    </tr>
                                </thead>
                                <tbody id="tcd-allocation-tbody">
                                    <!-- Rendered dynamically -->
                                </tbody>
                            </table>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px dashed #e2e8f0; font-size: 12px; flex-wrap: wrap; gap: 8px;">
                            <span style="color: #059669; font-weight: 600;"><i class="fa fa-check-circle"></i> \u0110\u1ED9 l\u1EC7ch l\xE0m tr\xF2n: 0.00 USD (Kh\u1EDBp 100% chi ph\xED th\u1EF1c t\u1EBF)</span>
                            <button class="btn btn-xs btn-primary hub-btn-sync" id="tcd-btn-apply-lcv"><i class="fa fa-check"></i> C\u1EADp Nh\u1EADt Gi\xE1 V\u1ED1n V\xE0o ERPNext LCV</button>
                        </div>
                    </div>
                </div>

                <!-- C\u1ED8T PH\u1EA2I (35%): Audit, LCV Sync, Export Margin -->
                <div class="hub-exceptions-panel">
                    <!-- 1. Audit & Anomaly Detection -->
                    <div class="hub-card-header">
                        <div class="card-header-title">
                            <span class="header-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2">
                                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                    <line x1="12" y1="9" x2="12" y2="13"></line>
                                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                                </svg>
                            </span>
                            <span class="header-text">Ki\u1EC3m To\xE1n & R\u1EE7i Ro Chi Ph\xED (Cost Audit)</span>
                        </div>
                        <span class="badge-status badge-stale" id="tcd-audit-badge">1 L\u01B0u \xFD</span>
                    </div>
                    <div class="hub-exceptions-list" id="tcd-audit-list">
                        <!-- Duplicate Check -->
                        <div class="hub-exception-card" style="border-left: 4px solid #10b981;">
                            <div class="exception-card-header">
                                <span class="exception-title" style="color: #047857;"><i class="fa fa-check"></i> Tr\xF9ng L\u1EB7p H\xF3a \u0110\u01A1n (Duplicate Check)</span>
                                <span class="delay-tag-ontime">H\u1EE3p l\u1EC7</span>
                            </div>
                            <div class="exception-card-body">Kh\xF4ng ph\xE1t hi\u1EC7n h\xF3a \u0111\u01A1n tr\xF9ng l\u1EB7p s\u1ED1 ch\u1EE9ng t\u1EEB ho\u1EB7c nh\xE0 cung c\u1EA5p.</div>
                        </div>

                        <!-- Missing Critical Cost Check -->
                        <div class="hub-exception-card warning">
                            <div class="exception-card-header">
                                <span class="exception-title" style="color: #b45309;"><i class="fa fa-exclamation-triangle"></i> Chi Ph\xED Tr\u1ECDng Y\u1EBFu (Missing Cost Check)</span>
                                <span class="delay-tag-positive">C\u1EA7n r\xE0 so\xE1t</span>
                            </div>
                            <div class="exception-card-body">Ch\u01B0a nh\u1EADn h\xF3a \u0111\u01A1n n\xE2ng h\u1EA1 c\u1EA3ng \u0111\xEDch (Port Handling D/O). C\u1EA7n li\xEAn h\u1EC7 \u0111\u1EA1i l\xFD h\xE3ng t\xE0u tr\u01B0\u1EDBc ng\xE0y 14/10.</div>
                        </div>

                        <!-- Wrong-case Check -->
                        <div class="hub-exception-card" style="border-left: 4px solid #10b981;">
                            <div class="exception-card-header">
                                <span class="exception-title" style="color: #047857;"><i class="fa fa-check"></i> G\xE1n \u0110\xFAng V\u1EE5 Vi\u1EC7c (Association Check)</span>
                                <span class="delay-tag-ontime">Kh\u1EDBp 100%</span>
                            </div>
                            <div class="exception-card-body">T\u1EA5t c\u1EA3 6 h\xF3a \u0111\u01A1n d\u1ECBch v\u1EE5 \u0111\u1EC1u tham chi\u1EBFu ch\xEDnh x\xE1c s\u1ED1 PO-2026-0042 v\xE0 Trade Case IMP-2026-001.</div>
                        </div>
                    </div>

                    <!-- 2. ERPNext Landed Cost Voucher Status Card -->
                    <div style="border-top: 1px solid #e2e8f0; padding: 14px 16px; background: #ffffff;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 12.5px; font-weight: 700; color: #0f172a;"><i class="fa fa-link" style="color: #0284c7;"></i> ERPNext Landed Cost Voucher</span>
                            <span class="tc-badge-erp submitted" id="tcd-lcv-badge">LCV-2026-0004</span>
                        </div>
                        <div style="font-size: 11.5px; color: #64748b; line-height: 1.45; margin-bottom: 10px;">
                            D\u1EEF li\u1EC7u ph\xE2n b\u1ED5 \u0111\u01B0\u1EE3c ghi nh\u1EADn t\u1EF1 \u0111\u1ED9ng v\xE0o ch\u1EE9ng t\u1EEB ti\xEAu chu\u1EA9n c\u1EE7a ERPNext, c\u1EADp nh\u1EADt tr\u1EF1c ti\u1EBFp v\xE0o \u0111\u1ECBnh gi\xE1 t\u1ED3n kho (Inventory Valuation) v\xE0 gi\xE1 v\u1ED1n (COGS).
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <a href="/app/landed-cost-voucher" class="btn btn-default btn-xs" style="flex: 1; text-align: center;"><i class="fa fa-external-link"></i> M\u1EDF LCV ERPNext</a>
                        </div>
                    </div>

                    <!-- 3. Export Profitability Card -->
                    <div id="tcd-export-profitability-box" style="border-top: 1px solid #e2e8f0; padding: 14px 16px; background: #ffffff;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 12.5px; font-weight: 700; color: #0f172a;"><i class="fa fa-bar-chart" style="color: #059669;"></i> Hi\u1EC7u Qu\u1EA3 L\xF4 Xu\u1EA5t Kh\u1EA9u (Export Margin)</span>
                            <span class="delay-tag-ontime">+24.3% Bi\xEAn L\u1EE3i Nhu\u1EADn</span>
                        </div>
                        <table class="table tc-table" style="margin-bottom: 0;">
                            <tr>
                                <td class="label-col">Doanh thu xu\u1EA5t kh\u1EA9u:</td>
                                <td class="val-col text-right">$65,000.00</td>
                            </tr>
                            <tr>
                                <td class="label-col">Gi\xE1 v\u1ED1n h\xE0ng b\xE1n (COGS):</td>
                                <td class="val-col text-right">$45,000.00</td>
                            </tr>
                            <tr>
                                <td class="label-col">Chi ph\xED logistics xu\u1EA5t kh\u1EA9u:</td>
                                <td class="val-col text-right">$4,200.00</td>
                            </tr>
                            <tr style="border-top: 1px solid #e2e8f0; font-weight: 700;">
                                <td class="label-col" style="color: #059669;">L\u1EE3i nhu\u1EADn g\u1ED9p th\u1EF1c t\u1EBF:</td>
                                <td class="val-col text-right" style="color: #059669; font-size: 13.5px;">$15,800.00</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: LOGISTICS AI COPILOT WORKSPACE -->
        <div class="logistics-tab-pane" id="tab-pane-ai-copilot">
            <div class="lw-copilot-container">
                <!-- Left: Chat Sessions Sidebar (Light theme matching system) -->
                <aside class="lw-copilot-sessions-panel">
                    <div class="lw-copilot-sessions-header">
                        <button id="copilot-btn-new-chat" class="btn btn-primary btn-sm hub-btn-sync" style="width: 100%;">
                            <i class="fa fa-plus"></i> Cu\u1ED9c h\u1ED9i tho\u1EA1i m\u1EDBi
                        </button>
                    </div>
                    <div class="lw-copilot-search-wrap">
                        <i class="fa fa-search lw-copilot-search-icon"></i>
                        <input type="text" id="copilot-session-search" class="form-control lw-copilot-search-input" placeholder="T\xECm ki\u1EBFm h\u1ED9i tho\u1EA1i...">
                    </div>
                    <div class="lw-copilot-sessions-list" id="copilot-sessions-list">
                        <div class="lw-session-group-title">H\xF4m nay</div>
                        <div class="lw-session-item active">
                            <i class="fa fa-commenting-o lw-session-icon"></i>
                            <div class="lw-session-info">
                                <span class="lw-session-title">Ph\xE2n t\xEDch sai l\u1EC7ch chi ph\xED IMP-2026-001</span>
                                <span class="lw-session-time">10:45 AM</span>
                            </div>
                        </div>
                        <div class="lw-session-item">
                            <i class="fa fa-commenting-o lw-session-icon"></i>
                            <div class="lw-session-info">
                                <span class="lw-session-title">Tra c\u1EE9u l\u1ECBch t\xE0u Maersk Mc-Kinney</span>
                                <span class="lw-session-time">09:12 AM</span>
                            </div>
                        </div>
                        <div class="lw-session-group-title" style="margin-top: 12px;">7 ng\xE0y tr\u01B0\u1EDBc</div>
                        <div class="lw-session-item">
                            <i class="fa fa-commenting-o lw-session-icon"></i>
                            <div class="lw-session-info">
                                <span class="lw-session-title">Th\u1EE7 t\u1EE5c C/O Form E xu\u1EA5t kh\u1EA9u</span>
                                <span class="lw-session-time">14 Oct</span>
                            </div>
                        </div>
                    </div>
                </aside>

                <!-- Right: Chat Conversation Workspace -->
                <main class="lw-copilot-chat-workspace">
                    <div class="lw-copilot-chat-header">
                        <div class="lw-copilot-title-group">
                            <div class="lw-copilot-avatar">
                                <i class="fa fa-bolt"></i>
                            </div>
                            <div>
                                <h3 class="lw-copilot-main-title">Tr\u1EE3 L\xFD Tr\xED Tu\u1EC7 Nh\xE2n T\u1EA1o Logistics (AI Copilot)</h3>
                                <span class="lw-copilot-sub-title">T\u1EF1 \u0111\u1ED9ng ph\xE2n t\xEDch h\u1ED3 s\u01A1 Trade Case, c\u1EA3nh b\xE1o l\u1EC7ch ETA v\xE0 t\u1ED1i \u01B0u chi ph\xED Landed Cost</span>
                            </div>
                        </div>
                        <div class="lw-copilot-actions">
                            <div class="tc-select-case-group" style="margin: 0;">
                                <span style="font-size: 12px; font-weight: 600; color: #64748b;">Ng\u1EEF c\u1EA3nh:</span>
                                <select id="copilot-context-case" class="form-control tc-case-select-dropdown" style="height: 32px; font-size: 12px; min-width: 140px;">
                                    <option value="IMP-2026-001" selected>IMP-2026-001</option>
                                    <option value="EXP-2026-002">EXP-2026-002</option>
                                    <option value="IMP-2026-003">IMP-2026-003</option>
                                </select>
                            </div>
                            <button class="btn btn-default btn-xs" id="copilot-btn-clear" title="X\xF3a h\u1ED9i tho\u1EA1i"><i class="fa fa-trash-o"></i> X\xF3a h\u1ED9i tho\u1EA1i</button>
                        </div>
                    </div>

                    <!-- Messages stream -->
                    <div class="lw-copilot-messages-thread" id="copilot-messages-thread">
                        <div class="lw-copilot-welcome-box">
                            <div class="lw-welcome-icon"><i class="fa fa-compass" style="color: #0284c7; font-size: 26px;"></i></div>
                            <h4 style="margin: 6px 0; font-size: 15px; font-weight: 700; color: #0f172a;">Ch\xE0o b\u1EA1n! T\xF4i l\xE0 Tr\u1EE3 L\xFD Logistics AI Copilot</h4>
                            <p style="color: #64748b; font-size: 12.5px; max-width: 580px; margin: 0 auto 14px;">
                                T\xF4i c\xF3 th\u1EC3 k\u1EBFt n\u1ED1i d\u1EEF li\u1EC7u h\xE0nh tr\xECnh t\xE0u th\u1EF1c t\u1EBF, b\u1EA3ng k\xEA 11 kho\u1EA3n chi ph\xED v\xE0 c\xF4ng c\u1EE5 ph\xE2n b\u1ED5 Landed Cost \u0111\u1EC3 gi\u1EA3i quy\u1EBFt nhanh c\xE1c nghi\u1EC7p v\u1EE5 c\u1EE7a b\u1EA1n:
                            </p>
                            <div class="lw-suggestions-grid">
                                <button class="lw-suggestion-pill" data-prompt="Ki\u1EC3m tra chi ti\u1EBFt nguy\xEAn nh\xE2n ch\xEAnh l\u1EC7ch chi ph\xED th\u1EF1c t\u1EBF so v\u1EDBi d\u1EF1 to\xE1n l\xF4 h\xE0ng IMP-2026-001">
                                    <i class="fa fa-dollar" style="color: #0284c7;"></i>
                                    <span>Ph\xE2n t\xEDch sai l\u1EC7ch chi ph\xED l\xF4 IMP-2026-001</span>
                                </button>
                                <button class="lw-suggestion-pill" data-prompt="D\u1EF1 b\xE1o th\u1EDDi gian t\xE0u c\u1EADp c\u1EA3ng \u0110\xE0 N\u1EB5ng v\xE0 c\xE1c m\u1ED1c th\u1EE7 t\u1EE5c h\u1EA3i quan ti\u1EBFp theo">
                                    <i class="fa fa-ship" style="color: #0d9488;"></i>
                                    <span>D\u1EF1 b\xE1o ETA & th\u1EE7 t\u1EE5c c\u1EA3ng \u0110\xE0 N\u1EB5ng</span>
                                </button>
                                <button class="lw-suggestion-pill" data-prompt="G\u1EE3i \xFD quy t\u1EAFc ph\xE2n b\u1ED5 gi\xE1 v\u1ED1n t\u1ED1i \u01B0u cho c\xE1c m\u1EB7t h\xE0ng theo Gross Weight">
                                    <i class="fa fa-sliders" style="color: #d97706;"></i>
                                    <span>G\u1EE3i \xFD quy t\u1EAFc ph\xE2n b\u1ED5 Landed Cost</span>
                                </button>
                            </div>
                        </div>

                        <!-- Chat Messages List -->
                        <div id="copilot-chat-history"></div>
                    </div>

                    <!-- Input area -->
                    <div class="lw-copilot-input-area">
                        <div class="lw-copilot-input-box">
                            <textarea id="copilot-input-textarea" class="lw-copilot-textarea" placeholder="H\u1ECFi AI Copilot v\u1EC1 ch\u1EE9ng t\u1EEB, ph\xE2n b\u1ED5 chi ph\xED, h\xE0nh tr\xECnh t\xE0u... (Nh\u1EA5n Enter \u0111\u1EC3 g\u1EEDi)"></textarea>
                            <button id="copilot-btn-send" class="lw-copilot-send-btn" title="G\u1EEDi c\xE2u h\u1ECFi">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="22" y1="2" x2="11" y2="13"></line>
                                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                                </svg>
                            </button>
                        </div>
                        <div class="lw-copilot-disclaimer">
                            Logistics AI Copilot \u0111\u01B0\u1EE3c t\xEDch h\u1EE3p tr\u1EF1c ti\u1EBFp v\xE0o h\u1EC7 th\u1ED1ng Logistics Wizard Hub.
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>
</div>
`;var P=class{constructor(e){this.wrapper=e,this.currentTab="executive",this.currentCaseId="IMP-2026-001",this.executiveDashboard=e?e.executive_dashboard:null,this.trackingHub=e?e.shipment_tracking_hub:null,this.overviewController=e?e.trade_case_overview:null,this.tradeCostDashboard=e?e.trade_cost_dashboard:null,this.aiCopilot=e?e.logistics_ai_copilot:null}switch_tab(e,t){t=t||{},this.currentTab=e;let i=this.wrapper&&this.wrapper.shipment_tracking_hub&&this.wrapper.shipment_tracking_hub.page?$(this.wrapper.shipment_tracking_hub.page.body):$(document),n="executive";e==="overview"||e==="trade-case"||e==="dossier"?n="overview":e==="tracking"||e==="shipment-tracking-hub"?n="tracking":e==="cost"||e==="trade-cost"||e==="trade-cost-dashboard"?n="cost":e==="copilot"||e==="ai-copilot"||e==="logistics-ai-chatbot"?n="copilot":(e==="executive"||e==="exec"||e==="command-center")&&(n="executive"),i.find(".logistics-nav-tab").removeClass("active"),n==="executive"?i.find("#btn-tab-executive").addClass("active"):n==="overview"?i.find("#btn-tab-overview").addClass("active"):n==="tracking"?i.find("#btn-tab-tracking").addClass("active"):n==="cost"?i.find("#btn-tab-cost").addClass("active"):n==="copilot"&&i.find("#btn-tab-copilot").addClass("active"),i.find(".logistics-tab-pane").removeClass("active").removeAttr("style");let c="#tab-pane-executive";n==="overview"?c="#tab-pane-trade-case":n==="tracking"?c="#tab-pane-shipment-tracking":n==="cost"?c="#tab-pane-trade-cost":n==="copilot"&&(c="#tab-pane-ai-copilot");let d=i.find(c);if(d.length&&(d[0].offsetWidth,d.addClass("active")),this.wrapper&&this.wrapper.shipment_tracking_hub&&this.wrapper.shipment_tracking_hub.page){let s={executive:__("Executive Logistics Command Center"),overview:__("Trade Case Dossier"),tracking:__("Shipment Tracking Hub"),cost:__("Trade Cost & Landed Cost Dashboard"),copilot:__("Logistics AI Copilot")};this.wrapper.shipment_tracking_hub.page.set_title(s[n]||s.executive)}if(n==="executive")this.executiveDashboard&&this.executiveDashboard.load_data();else if(n==="tracking")this.trackingHub&&(this.trackingHub&&this.trackingHub.map&&setTimeout(()=>{this.trackingHub.map.invalidateSize()},150),t.shipment_id?this.trackingHub.data?(this.trackingHub.select_shipment(t.shipment_id),this.trackingHub.refresh(t.shipment_id)):this.trackingHub.refresh(t.shipment_id):this.trackingHub.data||this.trackingHub.refresh());else if(n==="overview")this.overviewController&&(t.case_id?this.overviewController.load_case(t.case_id):this.overviewController.currentData||this.overviewController.load_case(this.currentCaseId||"IMP-2026-001"));else if(n==="cost"){if(this.tradeCostDashboard){let s=t.case_id||this.currentCaseId||"IMP-2026-001";this.tradeCostDashboard.load_data(s)}}else n==="copilot"&&this.aiCopilot&&this.aiCopilot.on_tab_shown(t)}};function K(u){if(!!u)try{let e=$(u);e.addClass("logistics-full-bleed-page");let t=e.closest(".page-container");t.length&&(t.addClass("logistics-full-width"),t.css({"max-width":"100%",padding:"0",margin:"0",width:"100%"})),e.find(".page-content.container").removeClass("container").addClass("container-fluid"),e.find(".container").removeClass("container").addClass("container-fluid"),e.find(".page-body, .page-content, .container-fluid, .layout-main-section-wrapper, .layout-main-section, .layout-main").css({"max-width":"100%",width:"100%",padding:"0",margin:"0",border:"none","box-shadow":"none",background:"transparent"})}catch(e){console.warn("make_page_full_bleed warning:",e)}}function U(u,e,t){!t||(K(t),t.unifiedHub||(t.executive_dashboard=new q(t),t.shipment_tracking_hub=new O(t,u),t.trade_case_overview=new N(t,t.shipment_tracking_hub),t.trade_cost_dashboard=new R(t),t.logistics_ai_copilot=new B(t),t.unifiedHub=new P(t),t.unifiedHub.executiveDashboard=t.executive_dashboard,t.unifiedHub.trackingHub=t.shipment_tracking_hub,t.unifiedHub.overviewController=t.trade_case_overview,t.unifiedHub.tradeCostDashboard=t.trade_cost_dashboard,t.unifiedHub.aiCopilot=t.logistics_ai_copilot,t.executive_dashboard.unifiedHub=t.unifiedHub,t.trade_case_overview.unifiedHub=t.unifiedHub,t.trade_cost_dashboard.unifiedHub=t.unifiedHub,t.logistics_ai_copilot.unifiedHub=t.unifiedHub,t.switch_to_tab=function(i,n){typeof n=="string"?i==="shipment-tracking-hub"||i==="tracking"?t.unifiedHub.switch_tab("tracking",{shipment_id:n}):i==="cost"||i==="trade-cost"||i==="trade-cost-dashboard"?t.unifiedHub.switch_tab("cost",{case_id:n}):i==="copilot"||i==="ai-copilot"?t.unifiedHub.switch_tab("copilot"):i==="executive"||i==="exec"?t.unifiedHub.switch_tab("executive"):t.unifiedHub.switch_tab("overview",{case_id:n}):t.unifiedHub.switch_tab(i,n)},ae(t),t.executive_dashboard.init(),t.trade_case_overview.init(),t.trade_cost_dashboard.init(),t.logistics_ai_copilot.init(),K(t)),G(t,e))}function G(u,e){if(!u||!u.unifiedHub)return;K(u);let t=null,i=null,n=e||"overview";frappe.route_options&&(frappe.route_options.shipment&&(t=frappe.route_options.shipment,n="tracking"),frappe.route_options.case_id&&(i=frappe.route_options.case_id,frappe.route_options.tab||(n="overview")),frappe.route_options.tab&&(n=frappe.route_options.tab),frappe.route_options=null),t&&u.switch_to_tab?u.switch_to_tab("tracking",t):i&&u.switch_to_tab?u.switch_to_tab(n,i):u.switch_to_tab&&u.switch_to_tab(n)}function Y(u,e){typeof frappe!="undefined"&&frappe.pages&&frappe.pages[u]&&(frappe.pages[u].on_page_load=function(t){U(u,e,t)},frappe.pages[u].on_page_show=function(t){G(t,e)})}var q=class{constructor(e){this.wrapper=e,this.data=null,this.currentTimeRange="30d",this.bind_events()}bind_events(){let e=this;$(document).off("click","#exec-btn-refresh").on("click","#exec-btn-refresh",function(t){t.preventDefault(),e.load_data()}),$(document).off("change","#exec-time-range").on("change","#exec-time-range",function(){e.currentTimeRange=$(this).val(),e.load_data()}),$(document).off("click",".exec-action-btn").on("click",".exec-action-btn",function(t){t.preventDefault();let i=$(this).data("case");typeof frappe!="undefined"&&frappe.set_route?(frappe.route_options={case_id:i,tab:"overview"},frappe.set_route("trade-case-overview")):i&&e.wrapper&&e.wrapper.unifiedHub&&e.wrapper.unifiedHub.switch_tab("overview",{case_id:i})}),$(document).off("click",".pipeline-step").on("click",".pipeline-step",function(t){t.preventDefault();let i=$(this).find(".pipeline-step-name").text();frappe&&frappe.show_alert&&frappe.show_alert({message:__("\u0110ang quan s\xE1t ch\u1EB7ng: ")+i,indicator:"blue"},3)})}init(){this.load_data()}load_data(){let e=this;frappe.call({method:"logistics_wizard.api.get_executive_dashboard_summary",args:{time_range:e.currentTimeRange},callback:function(t){t&&t.message&&t.message.status==="success"?(e.data=t.message.data,e.render()):t&&t.message&&t.message.metrics&&(e.data=t.message,e.render())}})}render(){if(!this.data)return;let e=this.data;if(e.metrics){$("#exec-val-total-cases").text(e.metrics.total_cases||28),$("#exec-sub-import").text(e.metrics.import_cases||20),$("#exec-sub-export").text(e.metrics.export_cases||8);let t=Math.round((e.metrics.import_cases||20)/(e.metrics.total_cases||28)*100);$("#exec-bar-import").css("width",t+"%"),$("#exec-bar-export").css("width",100-t+"%"),$("#exec-val-in-transit").text(e.metrics.in_transit_shipments||18),$("#exec-val-alerts").text(e.metrics.active_exceptions||3);let i=e.metrics.total_spend?"$"+Number(e.metrics.total_spend).toLocaleString():"$1,245,500";$("#exec-val-spend").text(i)}if(e.pipeline&&e.pipeline.length>0){let t=e.pipeline.map(i=>`
                    <div class="pipeline-step ${i.status==="warning"?"step-warning":""}" data-step="${i.key}">
                        <div class="pipeline-step-header">
                            <span class="pipeline-step-num">${i.step_no}</span>
                            <span class="pipeline-step-count">${i.count} \u0111\u01A1n</span>
                        </div>
                        <div class="pipeline-step-name">${i.label}</div>
                        <span class="pipeline-step-sub">${i.sub_label}</span>
                        <div class="pipeline-step-bar">
                            <div class="pipeline-step-fill ${i.status==="warning"?"bg-amber":"bg-blue"}" style="width: ${i.pct}%;"></div>
                        </div>
                    </div>
                `).join("");$("#exec-pipeline-container").html(t)}if(e.health_donut){let t=e.health_donut;$("#exec-health-score").text(t.score_pct+"%");let i=t.segments||[],n=0;i.forEach(a=>{a.key==="on_time"?($("#donut-segment-ontime").attr("stroke-dasharray",`${a.pct}, 100`).attr("stroke-dashoffset",n),$("#legend-ontime-val").text(`${a.count} \u0111\u01A1n (${a.pct}%)`)):a.key==="at_risk"?($("#donut-segment-atrisk").attr("stroke-dasharray",`${a.pct}, 100`).attr("stroke-dashoffset",-n),$("#legend-atrisk-val").text(`${a.count} \u0111\u01A1n (${a.pct}%)`)):a.key==="critical"&&($("#donut-segment-critical").attr("stroke-dasharray",`${a.pct}, 100`).attr("stroke-dashoffset",-n),$("#legend-critical-val").text(`${a.count} \u0111\u01A1n (${a.pct}%)`)),n+=a.pct})}if(e.cost_breakdown&&e.cost_breakdown.categories){let t=e.cost_breakdown.categories.map(i=>{let n=i.variance_pct>0?"+":"",a=i.variance_pct<=0?"bg-emerald":"bg-amber";return`
                    <div class="cost-bar-item">
                        <div class="cost-bar-header">
                            <span class="cost-bar-name">${i.name}</span>
                            <div class="cost-bar-figures">
                                <span class="cost-bar-amount">$${Number(i.amount).toLocaleString()}</span>
                                <span class="exec-badge ${i.variance_pct<=0?"exec-badge-success":"exec-badge-amber"}">${n}${i.variance_pct}%</span>
                            </div>
                        </div>
                        <div class="cost-bar-progress">
                            <div class="cost-bar-fill ${a}" style="width: ${i.pct_of_total}%;"></div>
                        </div>
                    </div>
                `}).join("");$("#exec-cost-breakdown-list").html(t)}if(e.corridors&&e.corridors.length>0){let t=e.corridors.map(i=>{let n=i.mode==="Air"?"fa-plane":"fa-ship",a=i.health_level==="warning"?"exec-badge-amber":"exec-badge-success";return`
                    <div class="corridor-item">
                        <div class="corridor-main">
                            <div class="corridor-mode-icon">
                                <i class="fa ${n}"></i>
                            </div>
                            <div>
                                <span class="corridor-name">${i.route}</span>
                                <span class="corridor-meta">${i.active_voyages} chuy\u1EBFn \u0111ang ch\u1EA1y \u2022 Th\u1EDDi gian: ${i.avg_transit}</span>
                            </div>
                        </div>
                        <div class="corridor-status">
                            <span class="exec-badge ${a}">${i.status}</span>
                        </div>
                    </div>
                `}).join("");$("#exec-corridors-container").html(t)}if(e.action_alerts&&e.action_alerts.length>0){let t=e.action_alerts.map(i=>{let n=i.severity==="critical",a=n?"alert-critical":"alert-warning",c=n?"text-coral":"text-amber",d=n?"fa-exclamation-circle":"fa-exclamation-triangle",s=n?"btn-primary":"btn-default";return`
                    <div class="exec-alert-card ${a}">
                        <div class="exec-alert-top">
                            <span class="exec-alert-title">
                                <i class="fa ${d} ${c}"></i>
                                ${i.title}
                            </span>
                            <span class="exec-badge ${n?"exec-badge-amber":"exec-badge-info"}">${i.badge_label}</span>
                        </div>
                        <p class="exec-alert-desc">${i.description}</p>
                        <div class="exec-alert-footer">
                            <span class="exec-alert-tags">H\u1ED3 s\u01A1: <strong>${i.case_id}</strong> (${i.shipment_id})</span>
                            <button class="btn btn-xs ${s} exec-action-btn" data-case="${i.case_id}">
                                ${i.action_text} &rarr;
                            </button>
                        </div>
                    </div>
                `}).join("");$("#exec-alerts-container").html(t)}}};function ae(u){(u&&u.shipment_tracking_hub&&u.shipment_tracking_hub.page?$(u.shipment_tracking_hub.page.body):$(document)).off("click",".logistics-nav-tab").on("click",".logistics-nav-tab",function(t){t.preventDefault();let i=$(this).data("tab"),n=$(this).attr("data-route")||$(this).data("route");if(n){let a=typeof frappe!="undefined"&&frappe.get_route_str?frappe.get_route_str():"";if(a!==n&&a!=="logistics-wizard/"+n){frappe.set_route(n);return}}if(i==="rag-admin"||i==="rag-admin-center"){typeof frappe!="undefined"&&frappe.set_route?frappe.set_route("rag-admin-center"):window.location.href="/app/rag-admin-center";return}i&&u.unifiedHub&&u.unifiedHub.switch_tab(i)})}var N=class{constructor(e,t){this.wrapper=e,this.trackingHub=t,this.currentCaseId="IMP-2026-001",this.availableCases=[],this.currentData=null,this.bind_events()}init(){let e=this;frappe.call({method:"logistics_wizard.api.get_trade_case_list",callback:function(t){if(t&&t.message&&t.message.length>0){e.availableCases=t.message;let i=t.message.map(n=>`<option value="${n.case_id}">${n.label||n.case_id+" - "+n.party}</option>`).join("");$("#tc-case-selector").html(i),e.currentCaseId&&$("#tc-case-selector").val(e.currentCaseId)}}}),this.load_case(this.currentCaseId||"IMP-2026-001")}bind_events(){let e=this;$(document).on("change","#tc-case-selector",function(){let t=$(this).val();t&&e.load_case(t)}),$(document).on("click","#tc-btn-refresh-case",function(){$(this).find("i").addClass("fa-spin"),e.load_case(e.currentCaseId),setTimeout(()=>{$("#tc-btn-refresh-case").find("i").removeClass("fa-spin")},600)}),$(document).on("click","#tc-btn-refresh",function(){$(this).find("i").addClass("fa-spin"),e.load_case(e.currentCaseId),setTimeout(()=>{$("#tc-btn-refresh").find("i").removeClass("fa-spin")},600)}),$(document).on("click","#tc-btn-edit-case",function(){e.currentData&&e.currentData.case_id&&frappe.set_route("Form","Trade Case",e.currentData.case_id)}),$(document).on("click","#tc-btn-goto-shipment, #tc-drill-down-shipment",function(){let t=null;e.currentData&&e.currentData.shipment_summary&&(t=e.currentData.shipment_summary.shipment_id),typeof frappe!="undefined"&&frappe.set_route?(frappe.route_options={shipment:t,tab:"tracking"},frappe.set_route("shipment-tracking-hub")):e.unifiedHub?e.unifiedHub.switch_tab("tracking",{shipment_id:t}):e.wrapper&&e.wrapper.switch_to_tab&&e.wrapper.switch_to_tab("shipment-tracking-hub",t)}),$(document).on("click","#tc-btn-close-case",function(){e.attempt_close_case()}),$(document).on("click","#btn-upload-doc",function(){frappe.msgprint({title:__("Upload Document"),message:__("Ch\u1EE9c n\u0103ng t\u1EA3i l\xEAn v\xE0 ph\xE2n lo\u1EA1i ch\u1EE9ng t\u1EEB (C/O, D/O, Packing List) s\u1EBD k\u1EBFt n\u1ED1i v\u1EDBi Module Document Readiness."),indicator:"blue"})}),$(document).on("click","#btn-update-customs",function(){frappe.msgprint({title:__("Update Customs"),message:__("Ch\u1EE9c n\u0103ng c\u1EADp nh\u1EADt ti\u1EBFn \u0111\u1ED9 t\u1EDD khai \u0111i\u1EC7n t\u1EED VNACCS v\xE0 r\xE0 so\xE1t m\xE3 HS RAG."),indicator:"blue"})}),$(document).on("click","#btn-add-cost",function(){frappe.msgprint({title:__("Add Cost Invoice"),message:__("Ch\u1EE9c n\u0103ng ghi nh\u1EADn chi ph\xED ph\xE1t sinh v\xE0 c\u1EADp nh\u1EADt Landed Cost Voucher."),indicator:"blue"})}),$(document).on("click","#btn-create-exception",function(){frappe.msgprint({title:__("Create Exception"),message:__("Khai b\xE1o s\u1EF1 c\u1ED1 v\u1EADn chuy\u1EC3n m\u1EDBi (Tr\u1EC5 l\u1ECBch, h\u01B0 h\u1ECFng cont, ph\xE1t sinh ph\xED)."),indicator:"orange"})}),$(document).on("click","#btn-add-action",function(){frappe.prompt([{fieldname:"action",fieldtype:"Data",label:"N\u1ED9i dung h\xE0nh \u0111\u1ED9ng",reqd:1},{fieldname:"department",fieldtype:"Select",label:"Ph\xF2ng ban",options:`Logistics
Customs
Purchasing
Accounting
Warehouse`,default:"Logistics"},{fieldname:"due_date",fieldtype:"Date",label:"H\u1EA1n x\u1EED l\xFD",default:frappe.datetime.nowdate()}],function(t){frappe.show_alert({message:`\u0110\xE3 th\xEAm vi\u1EC7c c\u1EA7n l\xE0m: ${t.action}`,indicator:"green"})},"Th\xEAm H\xE0nh \u0110\u1ED9ng Ti\u1EBFp Theo")})}attempt_close_case(){let e=this,t=this.currentData&&this.currentData.quick_actions?this.currentData.quick_actions:{};if(t.can_close)frappe.confirm(`B\u1EA1n c\xF3 ch\u1EAFc ch\u1EAFn mu\u1ED1n \u0111\xF3ng ho\xE0n t\u1EA5t h\u1ED3 s\u01A1 Trade Case <strong>${e.currentData.case_id}</strong>?`,function(){frappe.call({method:"logistics_wizard.api.close_trade_case",args:{case_id:e.currentData.case_id},callback:function(i){i&&i.message&&i.message.success?(frappe.show_alert({message:i.message.message,indicator:"green"}),e.load_case(e.currentData.case_id)):frappe.msgprint(i.message.message||"L\u1ED7i khi \u0111\xF3ng case.")}})});else{let i=(t.close_reasons||[]).map(n=>`<li style="margin-bottom: 4px; color: #b91c1c;">${n}</li>`).join("");frappe.msgprint({title:__("\u26D4 KH\xD4NG TH\u1EC2 \u0110\xD3NG H\u1ED2 S\u01A0 (STAGE GATE CH\u1EB6N)"),message:`
                    <div style="font-size: 13px;">
                        <p>H\u1ED3 s\u01A1 <strong>${e.currentData.case_id}</strong> ch\u01B0a th\u1ECFa m\xE3n c\xE1c ti\xEAu ch\xED ch\u1ED1t ch\u1EB7n \u0111\u1EC3 \u0111\xF3ng case:</p>
                        <ul style="padding-left: 18px; margin: 10px 0;">
                            ${i}
                        </ul>
                        <p style="color: #64748b; font-style: italic;">Vui l\xF2ng ho\xE0n t\u1EA5t b\xE0n giao h\xE0ng, th\xF4ng quan, ch\u1ED1t chi ph\xED v\xE0 gi\u1EA3i quy\u1EBFt tri\u1EC7t \u0111\u1EC3 c\xE1c s\u1EF1 c\u1ED1 tr\u01B0\u1EDBc khi \u0111\xF3ng h\u1ED3 s\u01A1!</p>
                    </div>
                `,indicator:"red"})}}load_case(e){let t=this;this.currentCaseId=e||this.currentCaseId||"IMP-2026-001",$("#tc-current-case-badge").text(this.currentCaseId),$("#tc-case-selector").val()!==this.currentCaseId&&$("#tc-case-selector").val(this.currentCaseId),frappe.call({method:"logistics_wizard.api.get_trade_case_overview_data",args:{case_id:this.currentCaseId},callback:function(i){i&&i.message&&(t.currentData=i.message,t.render(i.message))}})}render(e){if(!e)return;this.currentData=e;let t=e.header||{};$("#tc-id-text, #tc-header-id").text(t.case_id||"IMP-2026-001"),$("#tc-status-badge, #tc-header-status").text(t.status?t.status.toUpperCase():"ACTIVE");let i=(t.health||"Attention").toLowerCase(),n=i==="healthy"?"badge-success":i==="critical"?"badge-danger":"badge-warning";if($("#tc-health-badge, #tc-header-health").attr("class",`tc-badge-health ${i} ${n}`).text(`Health: ${(t.health||"Attention").toUpperCase()}`),$("#tc-priority-badge, #tc-header-priority").text(`${t.priority||"Normal"} Priority`),$("#tc-party-text, #tc-meta-party").text(`${t.trade_type||"Import"} Case \u2014 ${t.supplier||t.customer||"N/A"}`),$("#tc-docref-text, #tc-meta-po").html(`<a href="${t.purchase_order?"/app/purchase-order/"+t.purchase_order:"#"}" class="tc-link">${t.purchase_order||t.sales_order||"N/A"}</a>`),$("#tc-mode-incoterm, #tc-meta-mode-incoterm").text(`${t.mode||"Ocean"} \u2022 ${t.incoterm||"FOB"}`),$("#tc-route-text, #tc-meta-route").text(`${t.origin||"N/A"} \u2794 ${t.destination||"N/A"}`),$("#tc-owner-text, #tc-meta-owner").text(`${t.owner||"Nguyen Van A"} (${t.department||"Logistics"})`),$("#tc-expected-close, #tc-meta-expected-close").text(t.expected_close||"N/A"),e.lifecycle){let a=e.lifecycle;$("#tc-current-stage-callout, #tc-lifecycle-current-label").html(`Giai \u0111o\u1EA1n hi\u1EC7n t\u1EA1i: <strong>${a.current_stage||"IN TRANSIT"}</strong>`);let c=$("#tc-lifecycle-stepper");c.empty(),(a.stages||[]).forEach((s,o)=>{let l=s.status,h=`
                    <div class="tc-step-item ${l}">
                        <div class="tc-step-circle">${l==="completed"?"\u2713":l==="current"?"\u25CF":"\u25CB"}</div>
                        <div class="tc-step-label">${s.label}</div>
                    </div>
                `;c.append(h)}),a.previous_milestone&&($("#tc-prev-ms-title, #tc-ms-prev-title").text(a.previous_milestone.title),$("#tc-prev-ms-date, #tc-ms-prev-date").text(a.previous_milestone.date)),a.next_milestone&&($("#tc-next-ms-title, #tc-ms-next-title").text(a.next_milestone.title),$("#tc-next-ms-date, #tc-ms-next-date").text(a.next_milestone.eta))}if(e.overall_health&&e.overall_health.cards){let a=$("#tc-health-grid");a.empty(),e.overall_health.cards.forEach(c=>{let d=`
                    <div class="tc-health-card ${c.class||"neutral"}">
                        <div class="tc-hc-label">${c.label}</div>
                        <div class="tc-hc-val">${c.value}</div>
                        <div class="tc-hc-sub">${c.sub}</div>
                    </div>
                `;a.append(d)})}if(e.shipment_summary){let a=e.shipment_summary,c=a.total_shipments>1?`<div style="margin-top: 8px; font-size: 11px; color: #64748b; font-weight: 600;">T\u1ED5ng s\u1ED1: <strong>${a.total_shipments} Shipments</strong> (${a.shipment_counts.in_transit} \u0110ang \u0111i, ${a.shipment_counts.delivered} \u0110\xE3 \u0111\u1EBFn)</div>`:"",d=`
                <table class="tc-kv-table">
                    <tr><td class="tc-kv-key">M\xE3 v\u1EADn \u0111\u01A1n (Shipment ID):</td><td class="tc-kv-val font-weight-bold text-primary">${a.shipment_id||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">H\xE3ng v\u1EADn t\u1EA3i (Carrier):</td><td class="tc-kv-val">${a.carrier||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">T\xEAn ph\u01B0\u01A1ng ti\u1EC7n (Vessel/Flight):</td><td class="tc-kv-val">${a.vessel||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">S\u1ED1 l\u01B0\u1EE3ng Container:</td><td class="tc-kv-val">${a.container_count||1} Containers</td></tr>
                    <tr><td class="tc-kv-key">C\u1EA3ng xu\u1EA5t (POL):</td><td class="tc-kv-val">${a.pol||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">C\u1EA3ng nh\u1EADp (POD):</td><td class="tc-kv-val">${a.pod||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">Ng\xE0y kh\u1EDFi h\xE0nh (ATD):</td><td class="tc-kv-val">${a.atd||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">L\u1ECBch d\u1EF1 ki\u1EBFn ban \u0111\u1EA7u (Original ETA):</td><td class="tc-kv-val">${a.original_eta||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">ETA hi\u1EC7n t\u1EA1i:</td><td class="tc-kv-val text-primary font-weight-bold">${a.current_eta||"N/A"}</td></tr>
                    <tr><td class="tc-kv-key">\u0110\u1ED9 tr\u1EC5 h\xE0nh tr\xECnh (Delay):</td><td class="tc-kv-val ${a.delay_days>0?"text-danger":"text-success"} font-weight-bold">${a.delay_days>0?"+"+a.delay_days+" ng\xE0y (Delay)":"\u0110\xFAng h\u1EA1n (On-time)"}</td></tr>
                </table>
                ${c}
            `;$("#tc-shipment-summary-body, #tc-shipment-body").html(d)}if(e.document_readiness){let a=e.document_readiness;$("#tc-doc-readiness-badge, #tc-docs-pct-badge").text(`${a.ready_count} / ${a.total_count} S\u1EB5n s\xE0ng (${a.percentage}%)`);let c="";a.missing_urgent&&a.missing_urgent.length>0&&(c=a.missing_urgent.map(s=>`
                    <div class="tc-urgent-doc-alert">
                        <strong>\u26A0 Thi\u1EBFu kh\u1EA9n c\u1EA5p: ${s.name}</strong><br>
                        <span style="font-size: 11px;">H\u1EA1n ch\xF3t: ${s.deadline} \u2022 ${s.note}</span>
                    </div>
                `).join(""));let d=(a.categories||[]).map(s=>`
                <div class="tc-doc-cat-box">
                    <span>${s.name}</span>
                    <span class="${s.status==="completed"?"text-success":"text-warning"} font-weight-bold">
                        ${s.ready}/${s.total} ${s.status==="completed"?"\u2713":"\u26A0"}
                    </span>
                </div>
            `).join("");$("#tc-doc-readiness-body, #tc-docs-body").html(`
                ${c}
                <div class="progress" style="height: 10px; margin-bottom: 12px; border-radius: 5px;">
                    <div class="progress-bar ${a.percentage===100?"bg-success":"bg-warning"}" style="width: ${a.percentage}%;"></div>
                </div>
                <div class="tc-doc-cat-grid">
                    ${d}
                </div>
                <div style="margin-top: 14px; text-align: right;">
                    <button class="btn btn-xs btn-default" id="tc-btn-view-docs"><i class="fa fa-folder-open-o"></i> Qu\u1EA3n l\xFD H\u1ED3 s\u01A1 Chi ti\u1EBFt</button>
                </div>
            `)}if(e.customs_readiness){let a=e.customs_readiness;$("#tc-customs-badge, #tc-customs-status-badge").text(`${a.status} (${a.readiness_pct}%)`),$("#tc-customs-body").html(`
                <table class="tc-kv-table">
                    <tr><td class="tc-kv-key">M\xE3 ph\xE2n lo\u1EA1i HS:</td><td class="tc-kv-val font-weight-bold">${a.hs_classification}</td></tr>
                    <tr><td class="tc-kv-key">Tr\u1EA1ng th\xE1i ph\xEA duy\u1EC7t HS:</td><td class="tc-kv-val text-success">\u2713 ${a.hs_approval_status}</td></tr>
                    <tr><td class="tc-kv-key">X\xE1c th\u1EF1c Xu\u1EA5t x\u1EE9 (Origin):</td><td class="tc-kv-val text-success">${a.origin_verified?"\u2713 \u0110\xE3 x\xE1c th\u1EF1c":"Ch\u01B0a x\xE1c th\u1EF1c"}</td></tr>
                    <tr><td class="tc-kv-key">Tr\u1ECB gi\xE1 H\u1EA3i quan (Value):</td><td class="tc-kv-val text-success">${a.customs_value_verified?"\u2713 \u0110\xE3 x\xE1c th\u1EF1c":"Ch\u01B0a x\xE1c th\u1EF1c"}</td></tr>
                    <tr><td class="tc-kv-key">T\u1EDD khai H\u1EA3i quan (Declaration):</td><td class="tc-kv-val text-warning font-weight-bold">${a.declaration_status}</td></tr>
                    <tr><td class="tc-kv-key">Gi\u1EA5y ph\xE9p chuy\xEAn ng\xE0nh:</td><td class="tc-kv-val">${a.license}</td></tr>
                    <tr><td class="tc-kv-key">Ki\u1EC3m tra chuy\xEAn ng\xE0nh:</td><td class="tc-kv-val">${a.inspection}</td></tr>
                    <tr><td class="tc-kv-key">T\xECnh tr\u1EA1ng Th\xF4ng quan:</td><td class="tc-kv-val ${a.clearance_status==="CLEARED"?"text-success font-weight-bold":"text-danger font-weight-bold"}">${a.clearance_status}</td></tr>
                </table>
            `)}if(e.cost_summary){let a=e.cost_summary,c=e.header&&String(e.header.trade_type||"").toLowerCase()==="export",d=c?"Tr\u1ECB gi\xE1 L\xF4 xu\u1EA5t (SO/SI)":"Tr\u1ECB gi\xE1 H\xE0ng mua (PO)",s=c?"Chi ph\xED Xu\u1EA5t kh\u1EA9u Th\u1EF1c t\u1EBF":"T\u1ED5ng Chi ph\xED Logistics Th\u1EF1c t\u1EBF",o=a.variance_amount>=0?"+":"",l=a.variance_amount>0?"text-danger":"text-success";$("#tc-cost-status-badge").text(`${a.cost_finalization_status} (${o}${a.variance_pct}%)`);let r=(a.breakdown||[]).map(h=>`
                <tr>
                    <td style="padding: 4px 0; color: #64748b;">${h.label}</td>
                    <td style="padding: 4px 0; text-align: right; font-weight: 600;">$${Number(h.amount||0).toLocaleString()}</td>
                </tr>
            `).join("");$("#tc-cost-body").html(`
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
                    <div>
                        <div style="font-size: 11px; color: #64748b;">${d}</div>
                        <div style="font-size: 14px; font-weight: 800; color: #0f172a;">$${Number(a.purchase_value||0).toLocaleString()}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">D\u1EF1 to\xE1n: $${Number(a.estimated_cost||0).toLocaleString()}</div>
                        <div style="font-size: 14px; font-weight: 800;" class="${l}">
                            $${Number(a.actual_cost||0).toLocaleString()} <span style="font-size: 11px;">(${o}${a.variance_pct}%)</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">${c?"Ch\xEAnh l\u1EC7ch D\u1EF1 to\xE1n":"T\u1ED5ng Landed Cost"}</div>
                        <div style="font-size: 14px; font-weight: 800; color: #0f766e;">
                            ${c?o+"$"+Number(a.variance_amount||0).toLocaleString():"$"+Number(a.actual_landed_cost||0).toLocaleString()}
                        </div>
                    </div>
                </div>
                <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">${s} Theo Nh\xF3m:</div>
                <table style="width: 100%; font-size: 12px; margin-bottom: 12px;">
                    ${r}
                </table>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; border-top: 1px dashed #e2e8f0; padding-top: 8px;">
                    <span>H\xF3a \u0111\u01A1n nh\u1EADn: <strong>${a.invoices_received}/${a.invoices_total}</strong></span>
                    <span>\u0110\xE3 th\u1EA9m \u0111\u1ECBnh: <strong>${a.costs_verified}/${a.invoices_total}</strong></span>
                    <span>\u0110\xE3 ph\xE2n b\u1ED5 LCV: <strong>${a.costs_allocated}/${a.invoices_total}</strong></span>
                </div>
            `)}if(e.warehouse_readiness){let a=e.warehouse_readiness;$("#tc-wh-badge, #tc-warehouse-status-badge").text(a.receiving_status);let c=a.discrepancy_alert?'<div class="tc-urgent-doc-alert">\u26A0 PH\xC1T HI\u1EC6N L\u1EC6CH S\u1ED0 L\u01AF\u1EE2NG / H\u01AF H\u1ECENG H\xC0NG H\xD3A!</div>':"";$("#tc-wh-body, #tc-warehouse-body").html(`
                ${c}
                <table class="tc-kv-table">
                    <tr><td class="tc-kv-key">L\u1ECBch d\u1EF1 ki\u1EBFn nh\u1EADp kho:</td><td class="tc-kv-val font-weight-bold">${a.expected_arrival}</td></tr>
                    <tr><td class="tc-kv-key">\u0110\u1ECBa \u0111i\u1EC3m Kho nh\u1EADn:</td><td class="tc-kv-val">${a.warehouse}</td></tr>
                    <tr><td class="tc-kv-key">Tr\u1EA1ng th\xE1i Ti\u1EBFp nh\u1EADn:</td><td class="tc-kv-val text-warning font-weight-bold">${a.receiving_status}</td></tr>
                    <tr><td class="tc-kv-key">S\u1ED1 l\u01B0\u1EE3ng d\u1EF1 ki\u1EBFn (Expected):</td><td class="tc-kv-val">${a.expected_qty?a.expected_qty.toLocaleString():"N/A"} ki\u1EC7n</td></tr>
                    <tr><td class="tc-kv-key">M\u1EB7t b\u1EB1ng kho d\u1EF1 tr\u1EEF:</td><td class="tc-kv-val text-success">${a.space_reserved?"\u2713 \u0110\xE3 gi\u1EEF ch\u1ED7 s\u1EB5n s\xE0ng":"Ch\u01B0a b\u1ED1 tr\xED"}</td></tr>
                    <tr><td class="tc-kv-key">\u0110\u1ED9i ng\u0169 ti\u1EBFp nh\u1EADn:</td><td class="tc-kv-val">${a.receiving_team}</td></tr>
                </table>
            `)}if(e.open_exceptions){let a=e.open_exceptions;$("#tc-exceptions-badge, #tc-open-exceptions-badge").text(`${a.total_open} Open (${a.overdue} Qu\xE1 h\u1EA1n)`);let c=(a.items||[]).map(d=>{let s=(d.severity||"medium").toLowerCase();return`
                    <div class="tc-exception-item ${s}">
                        <div class="tc-exc-header">
                            <span class="badge ${s==="high"||s==="critical"?"badge-danger":"badge-warning"}">${d.severity}</span>
                            <span style="color: #64748b;">${d.id}</span>
                        </div>
                        <div class="tc-exc-title">${d.title}</div>
                        <div class="tc-exc-meta">
                            <span><i class="fa fa-user"></i> ${d.owner} (${d.department})</span>
                            <span><i class="fa fa-clock-o"></i> H\u1EA1n: ${d.due_date}</span>
                            <span class="font-weight-bold text-primary">${d.status}</span>
                        </div>
                    </div>
                `}).join("");c||(c='<div class="text-center text-success" style="padding: 20px;"><i class="fa fa-check-circle" style="font-size: 24px;"></i><p style="margin-top: 6px; font-weight: 600;">Kh\xF4ng c\xF3 s\u1EF1 c\u1ED1 n\xE0o \u0111ang m\u1EDF.</p></div>'),$("#tc-exceptions-body").html(c)}if(e.upcoming_actions){let a=e.upcoming_actions.map(c=>`
                <div class="tc-action-item">
                    <div class="tc-action-date">${c.date}</div>
                    <div class="tc-action-desc">${c.action}</div>
                    <div class="tc-action-dept"><span class="badge badge-default">${c.department}</span> (${c.owner})</div>
                </div>
            `).join("");$("#tc-actions-body").html(a||'<div class="text-muted">Kh\xF4ng c\xF3 l\u1ECBch h\xE0nh \u0111\u1ED9ng ti\u1EBFp theo.</div>')}if(e.related_erp_documents){let a=e.related_erp_documents.map(c=>`
                <tr>
                    <td style="padding: 6px 0; font-weight: 600; color: #64748b;">${c.doctype}</td>
                    <td style="padding: 6px 0;"><a href="${c.link}" class="tc-link font-weight-bold">${c.name}</a></td>
                    <td style="padding: 6px 0; text-align: right;">
                        <span class="tc-badge-erp ${c.status==="Submitted"||c.status==="Completed"?"submitted":"pending"}">${c.status}</span>
                    </td>
                </tr>
            `).join("");$("#tc-related-erp-body").html(`<table style="width: 100%; font-size: 12px;">${a}</table>`)}if(e.responsibility_matrix){let a=e.responsibility_matrix.map(c=>`
                <tr>
                    <td style="padding: 6px 0; font-weight: 700; color: #0284c7;">${c.role}</td>
                    <td style="padding: 6px 0; font-weight: 600; color: #0f172a;">${c.name}</td>
                    <td style="padding: 6px 0; color: #64748b; font-size: 11px;">${c.department}</td>
                </tr>
            `).join("");$("#tc-responsibility-body").html(`<table style="width: 100%; font-size: 12px;">${a}</table>`)}if(e.activity_timeline){let a=e.activity_timeline.map(c=>`
                <div class="tc-timeline-event">
                    <div class="tc-event-time">${c.time}</div>
                    <div class="tc-event-desc">
                        <strong style="color: #0284c7;">${c.actor}:</strong> ${c.event}
                    </div>
                </div>
            `).join("");$("#tc-activity-body").html(a||'<div class="text-muted">Ch\u01B0a c\xF3 nh\u1EADt k\xFD ho\u1EA1t \u0111\u1ED9ng.</div>')}if(e.quick_actions){let c=(e.quick_actions.close_reasons||[]).map(d=>`<div class="tc-sg-rule">${d}</div>`).join("");$("#tc-stage-gate-body").html(`
                <div class="tc-action-btn-group">
                    <button class="btn btn-default" id="btn-upload-doc"><i class="fa fa-upload"></i> Upload Document</button>
                    <button class="btn btn-default" id="btn-update-customs"><i class="fa fa-check-circle"></i> Update Customs</button>
                    <button class="btn btn-default" id="btn-add-cost"><i class="fa fa-dollar-sign"></i> Add Cost</button>
                    <button class="btn btn-default" id="btn-create-exception"><i class="fa fa-exclamation-triangle"></i> Create Exception</button>
                    <button class="btn btn-default" id="btn-add-action"><i class="fa fa-plus"></i> Add Action</button>
                </div>
                <div class="tc-stage-gate-box">
                    <div class="tc-sg-title">
                        <i class="fa fa-lock"></i> \u0110I\u1EC0U KI\u1EC6N CH\u1ED0T CH\u1EB6N \u0110\xD3NG CASE (STAGE GATE)
                    </div>
                    ${c}
                    <div style="margin-top: 10px; display: flex; justify-content: flex-end;">
                        <button class="btn btn-sm btn-danger font-weight-bold" id="tc-btn-close-case">
                            <i class="fa fa-check-square-o"></i> \u0110\xF3ng Trade Case (Close Case)
                        </button>
                    </div>
                </div>
            `)}}},O=class{constructor(e,t){this.wrapper=e,this.pageName=t||"trade-case-overview",e&&typeof frappe!="undefined"&&frappe.ui&&frappe.ui.make_app_page&&(this.page=frappe.ui.make_app_page({parent:e,title:__("Trade Case Dossier"),single_column:!0}),this.page&&this.page.container&&(this.page.container.removeClass("container").addClass("container-fluid"),this.page.container.css({"max-width":"100%",padding:"0",margin:"0"})),K(e)),this.data=null,this.selectedShipment=null,this.pendingFocusShipment=null,this.currentFilter="all",this.searchTerm="",this.map=null,this.mapLayers={baseLand:null,seaOverlay:null,routePolylines:[],markers:[],vehicleMarker:null,fleetVehicleMarkers:[]},this.debounceTimer=null,e&&this.init()}init(){this.render_skeleton(this.pageName),this.bind_events(),this.init_map()}render_skeleton(e){let t=window.UNIFIED_LOGISTICS_HUB_HTML||"";if(!t&&frappe.templates){let i=[e,e?e.replace(/-/g,"_"):null,"trade_case_overview","managementlogistic","managementLogistic","shipment_tracking_hub"];for(let n of i)if(n&&frappe.templates[n]){t=frappe.render_template(n,{});break}}this.page&&this.page.body?$(this.page.body).html(t):this.wrapper&&$(this.wrapper).html(t)}bind_events(){let e=this;$("#hub-btn-refresh").on("click",function(){$(this).find("i").addClass("fa-spin"),e.refresh(e.selectedShipment?e.selectedShipment.name:null,()=>{$("#hub-btn-refresh").find("i").removeClass("fa-spin")})}),$("#hub-btn-sync-now").on("click",function(){let t=e.selectedShipment?e.selectedShipment.name:null;e.sync_now(t)}),$(".hub-kpi-card").on("click",function(){let t=$(this).data("filter");$(".hub-kpi-card").removeClass("active"),$(this).addClass("active"),$(".hub-tab-btn").removeClass("active"),$(`.hub-tab-btn[data-tab="${t}"]`).addClass("active"),e.currentFilter=t,e.filter_and_render_table()}),$(".hub-tab-btn").on("click",function(){let t=$(this).data("tab");$(".hub-tab-btn").removeClass("active"),$(this).addClass("active"),$(".hub-kpi-card").removeClass("active"),$(`.hub-kpi-card[data-filter="${t}"]`).addClass("active"),e.currentFilter=t,e.filter_and_render_table()}),$("#hub-search-input").on("input",function(){clearTimeout(e.debounceTimer),e.debounceTimer=setTimeout(()=>{e.searchTerm=($(this).val()||"").trim().toLowerCase(),e.filter_and_render_table()},250)}),$("#hub-map-reset-btn").on("click",function(){e.reset_map_view()})}init_map(){let e=this,t=window.L||window.leaflet;if(!t){console.warn("[TrackingHub] Leaflet is not loaded yet");return}if(!!document.getElementById("lw-hub-map"))try{this.map=t.map("lw-hub-map",{center:[22,150],zoom:3,minZoom:2,maxZoom:18,zoomControl:!0,attributionControl:!0}),t.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"&copy; OpenStreetMap contributors",maxZoom:18,subdomains:["a","b","c"]}).addTo(this.map),setTimeout(()=>{e.map&&e.map.invalidateSize()},300)}catch(n){console.error("[TrackingHub] Error initializing map:",n)}}refresh(e=null,t=null){let i=this,n=e||this.pendingFocusShipment;frappe.call({method:"logistics_wizard.api.get_shipment_tracking_hub_data",args:n?{shipment:n}:{},callback:a=>{if(a&&a.message){this.data=a.message,this.render_all(n);let c=this.pendingFocusShipment||n;this.pendingFocusShipment=null,c&&this.select_shipment(c)}t&&t()},error:function(){t&&t()}})}render_all(e=null){if(!this.data)return;this.render_kpis(this.data.kpis||{});let t=this.data.shipments||[];e?this.selectedShipment=t.find(i=>i.name===e||i.purchase_order===e||i.tracking_number===e||i.container_id===e)||this.data.selected_shipment||null:this.selectedShipment=null,this.filter_and_render_table(),this.render_stepper(this.selectedShipment),this.render_exceptions(this.data.active_exceptions||[]),this.update_map_view(this.selectedShipment)}render_kpis(e){$("#kpi-val-total").text(e.total_shipments||0),$("#kpi-val-transit").text(e.in_transit||0),$("#kpi-val-delayed").text(e.delayed_exceptions||0),$("#kpi-val-stale").text(e.stale_tracking||0),$("#tab-cnt-all").text(e.total_shipments||0),$("#tab-cnt-transit").text(e.in_transit||0),$("#tab-cnt-delayed").text(e.delayed_exceptions||0),$("#tab-cnt-stale").text(e.stale_tracking||0);let t=(this.data.shipments||[]).filter(i=>i.status==="Delivered"||i.status==="Completed").length;$("#tab-cnt-delivered").text(t)}filter_and_render_table(){let e=this,t=this.data?this.data.shipments||[]:[];if(this.currentFilter==="In Transit"?t=t.filter(n=>n.status==="In Transit"):this.currentFilter==="Delayed"?t=t.filter(n=>n.is_delayed==1||n.status==="Delayed"):this.currentFilter==="Stale"?t=t.filter(n=>n.is_stale==1):this.currentFilter==="Delivered"&&(t=t.filter(n=>n.status==="Delivered"||n.status==="Completed")),this.searchTerm){let n=this.searchTerm;t=t.filter(a=>a.name&&a.name.toLowerCase().includes(n)||a.tracking_number&&a.tracking_number.toLowerCase().includes(n)||a.container_id&&a.container_id.toLowerCase().includes(n)||a.carrier&&a.carrier.toLowerCase().includes(n)||a.purchase_order&&a.purchase_order.toLowerCase().includes(n)||a.origin_port&&a.origin_port.toLowerCase().includes(n)||a.destination_port&&a.destination_port.toLowerCase().includes(n))}let i=$("#hub-shipments-tbody");if(i.empty(),t.length===0){i.html(`
                <tr>
                    <td colspan="6" class="text-center text-muted" style="padding: 30px;">
                        Kh\xF4ng t\xECm th\u1EA5y l\xF4 h\xE0ng n\xE0o ph\xF9 h\u1EE3p v\u1EDBi b\u1ED9 l\u1ECDc.
                    </td>
                </tr>
            `);return}t.forEach(n=>{let a=e.selectedShipment&&e.selectedShipment.name===n.name,c=n.current_vehicle||e.get_active_vehicle_mode(n,n.progress),d=c==="Air"||c==="Plane"?"\u2708\uFE0F":c==="Ocean"||c==="Ship"?"\u{1F6A2}":"\u{1F69A}",s="badge-in-transit";n.status==="Delayed"||n.is_delayed==1?s="badge-delayed":n.status==="Delivered"||n.status==="Completed"?s="badge-delivered":n.is_stale==1?s="badge-stale":n.status==="Draft"&&(s="badge-draft");let o='<span class="delay-tag-ontime">\u0110\xFAng h\u1EA1n</span>';n.delay_days&&n.delay_days>0&&(o=`<span class="delay-tag-positive">+${n.delay_days} ng\xE0y</span>`);let l=$(`
                <tr class="hub-row-clickable ${a?"selected":""}" data-name="${n.name}">
                    <td>
                        <div style="font-weight: 700; color: #0284c7;">
                            ${d} ${n.name}
                        </div>
                        <div style="font-size: 11px; color: #64748b; font-family: monospace;">
                            ${n.container_id?"Cont: "+n.container_id:n.tracking_number?"Track: "+n.tracking_number:""}
                        </div>
                    </td>
                    <td>
                        <div style="font-weight: 600;">${n.carrier||"Ch\u01B0a ch\u1EC9 \u0111\u1ECBnh"}</div>
                        <div style="font-size: 11px; color: #64748b;">${n.vessel_name||n.flight_number||""}</div>
                    </td>
                    <td>
                        <div style="font-weight: 500;">${n.origin_port||"N/A"} \u2794 ${n.destination_port||"N/A"}</div>
                        <div style="margin-top: 2px;"><span class="badge-status ${s}">${n.status}</span></div>
                    </td>
                    <td>
                        <div style="font-size: 11px;">ETD: ${n.atd||n.etd||"\u2014"}</div>
                        <div style="font-size: 11px; font-weight: 600; color: ${n.is_delayed?"#dc2626":"#1e293b"};">
                            ETA: ${n.eta||"\u2014"}
                        </div>
                    </td>
                    <td>${o}</td>
                    <td style="text-align: center;">
                        <button class="btn btn-xs btn-default hub-btn-select-shipment" data-name="${n.name}" title="Xem l\u1ED9 tr\xECnh tr\xEAn b\u1EA3n \u0111\u1ED3">
                            <i class="fa fa-crosshairs"></i>
                        </button>
                        ${n.purchase_order?`
                            <a href="/app/purchase-order/${n.purchase_order}" class="btn btn-xs btn-default" title="Xem PO ${n.purchase_order}">
                                <i class="fa fa-file-text-o"></i>
                            </a>
                        `:""}
                    </td>
                </tr>
            `);l.on("click",function(r){if($(r.target).closest("a").length)return;e.selectedShipment&&e.selectedShipment.name===n.name?e.reset_map_view():e.select_shipment(n.name)}),l.find(".hub-btn-select-shipment").on("click",function(r){r.stopPropagation(),e.selectedShipment&&e.selectedShipment.name===n.name?e.reset_map_view():e.select_shipment(n.name)}),i.append(l)})}select_shipment(e){let t=this,i=(this.data&&this.data.shipments?this.data.shipments:[]).find(n=>n.name===e);i?this.selectedShipment=i:this.pendingFocusShipment=e,frappe.call({method:"logistics_wizard.api.get_shipment_tracking_hub_data",args:{shipment:e},callback:function(n){n&&n.message&&n.message.selected_shipment&&(t.selectedShipment=n.message.selected_shipment),$("#hub-shipments-tbody tr").removeClass("selected"),$(`#hub-shipments-tbody tr[data-name="${e}"]`).addClass("selected"),t.render_stepper(t.selectedShipment),t.update_map_view(t.selectedShipment)}})}render_stepper(e){let t=$("#hub-stepper-track");if(t.empty(),!e){$("#stepper-shipment-name").text("Ch\u01B0a ch\u1ECDn l\xF4 h\xE0ng"),t.html(`
                <div class="hub-stepper-empty-hint">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="16" x2="12" y2="12"/>
                        <line x1="12" y1="8" x2="12.01" y2="8"/>
                    </svg>
                    \u0110ang \u1EDF ch\u1EBF \u0111\u1ED9 <b>To\xE0n c\u1EA3nh</b>. Ch\u1ECDn m\u1ED9t l\xF4 h\xE0ng t\u1EEB danh s\xE1ch b\xEAn d\u01B0\u1EDBi ho\u1EB7c nh\u1EA5p v\xE0o ph\u01B0\u01A1ng ti\u1EC7n tr\xEAn b\u1EA3n \u0111\u1ED3 \u0111\u1EC3 theo d\xF5i chi ti\u1EBFt 9 m\u1ED1c DCSA.
                </div>
            `);return}$("#stepper-shipment-name").text(`${e.name} (${e.carrier||""})`);let i=[{key:"BOOKED",label:"1. \u0110\u1EB7t ch\u1ED7"},{key:"GATE_IN",label:"2. V\xE0o b\xE3i"},{key:"LOADED",label:"3. X\u1EBFp h\xE0ng"},{key:"DEPARTED",label:"4. Kh\u1EDFi h\xE0nh"},{key:"TRANSSHIPMENT",label:"5. Trung chuy\u1EC3n"},{key:"ARRIVED",label:"6. C\u1EADp c\u1EA3ng"},{key:"DISCHARGED",label:"7. D\u1EE1 h\xE0ng"},{key:"GATE_OUT",label:"8. Ra c\u1ED5ng"},{key:"DELIVERED",label:"9. Giao kho"}],n=e.transit_route||[],a=new Set,c={};n.forEach(s=>{s.milestone&&(a.add(s.milestone.toUpperCase()),c[s.milestone.toUpperCase()]=s.date||s.timestamp||"")});let d=-1;for(let s=i.length-1;s>=0;s--)if(a.has(i[s].key)){d=s;break}d===-1&&(d=0),i.forEach((s,o)=>{let l=a.has(s.key),r=o===d,h=e.is_delayed==1,p="";l&&(p+=" completed"),r&&(p+=" current"),h&&(p+=" delayed");let b=c[s.key]?c[s.key].split("T")[0]:"";t.append(`
                <div class="hub-step-item ${p}">
                    <div class="hub-step-badge">
                        ${l?"\u2714":o+1}
                    </div>
                    <div class="hub-step-title">${s.label}</div>
                    <div class="hub-step-date">${b||(r?"\u0110ang th\u1EF1c hi\u1EC7n":"\u2014")}</div>
                </div>
            `)})}render_exceptions(e){let t=$("#hub-exceptions-list");t.empty();let i=e?e.length:0;if($("#hub-exception-count-badge").text(`${i} s\u1EF1 c\u1ED1`),!e||e.length===0){t.html(`
                <div class="text-center text-muted" style="padding: 35px 15px;">
                    <i class="fa fa-check-circle text-success" style="font-size: 28px; margin-bottom: 8px;"></i>
                    <p style="margin: 0; font-size: 13px;">Kh\xF4ng c\xF3 s\u1EF1 c\u1ED1 ho\u1EB7c c\u1EA3nh b\xE1o ngo\u1EA1i l\u1EC7 \u0111ang m\u1EDF.</p>
                </div>
            `);return}e.forEach(n=>{let a=n.severity==="Critical",c=a?"badge-danger":"badge-warning",d=a?"\u{1F534}":"\u{1F7E1}";t.append(`
                <div class="hub-exception-card ${a?"critical":"warning"}">
                    <div class="exception-card-header">
                        <span class="exception-title">${d} ${n.exception_type||"Ngo\u1EA1i l\u1EC7 V\u1EADn chuy\u1EC3n"}</span>
                        <span class="badge ${c}">${n.severity}</span>
                    </div>
                    <div class="exception-card-body">
                        <div><strong>L\xF4 h\xE0ng:</strong> ${n.shipment_tracking}</div>
                        ${n.purchase_order?`<div><strong>\u0110\u01A1n h\xE0ng:</strong> ${n.purchase_order}</div>`:""}
                        ${n.old_eta&&n.new_eta?`
                            <div class="exception-timeline-shift">
                                <span>ETA: ${n.old_eta} \u2794 <strong>${n.new_eta}</strong></span>
                                <span class="badge-status badge-delayed">+${n.delay_days||0} ng\xE0y</span>
                            </div>
                        `:""}
                        <div style="margin-top: 6px; color: #475569;">${n.description||""}</div>
                    </div>
                    <div class="exception-card-footer">
                        ${n.purchase_order?`
                            <a href="/app/purchase-order/${n.purchase_order}" class="btn btn-xs btn-default">
                                <i class="fa fa-external-link"></i> M\u1EDF PO
                            </a>
                        `:""}
                        <button class="btn btn-xs btn-primary hub-btn-resolve-exc" data-name="${n.name}">
                            \u0110\xE1nh d\u1EA5u \u0111\xE3 x\u1EED l\xFD
                        </button>
                    </div>
                </div>
            `)}),$(".hub-btn-resolve-exc").on("click",function(){let n=$(this).data("name");frappe.db.set_value("Shipment Exception",n,"status","Resolved").then(()=>{frappe.show_alert({message:__("\u0110\xE3 gi\u1EA3i quy\u1EBFt ngo\u1EA1i l\u1EC7!"),indicator:"green"}),$(this).closest(".hub-exception-card").fadeOut(300,function(){$(this).remove()})})})}update_marine_overlay(e){if(!this.map)return;let t=window.L||window.leaflet;!t||(e==="Ocean"?(this.mapLayers.seaOverlay||(this.mapLayers.seaOverlay=t.tileLayer("https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",{attribution:'H\u1EA3i \u0111\u1ED3 &copy; <a href="http://www.openseamap.org">OpenSeaMap</a>',maxZoom:18,opacity:.95})),this.map.hasLayer(this.mapLayers.seaOverlay)||this.mapLayers.seaOverlay.addTo(this.map)):this.mapLayers.seaOverlay&&this.map.hasLayer(this.mapLayers.seaOverlay)&&this.map.removeLayer(this.mapLayers.seaOverlay))}get_vehicle_svg(e){return e==="Air"?`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#007AFF" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1.5C11.2 1.5 10.6 2.3 10.6 3.2V8.8L2.4 13.5C1.8 13.8 1.5 14.5 1.5 15.1C1.5 15.9 2.2 16.5 3 16.5H10.6V20.2L8.2 21.8C7.9 22 7.7 22.3 7.7 22.7C7.7 23.4 8.3 24 9 24H15C15.7 24 16.3 23.4 16.3 22.7C16.3 22.3 16.1 22 15.8 21.8L13.4 20.2V16.5H21C21.8 16.5 22.5 15.9 22.5 15.1C22.5 14.5 22.2 13.8 21.6 13.5L13.4 8.8V3.2C13.4 2.3 12.8 1.5 12 1.5Z" stroke="#0047AB" stroke-width="0.5"/>
                </svg>
            `:e==="Ocean"?`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1 C14.8 3.5 18 8 18 14 V20 C18 21.7 16.7 23 15 23 H9 C7.3 23 6 21.7 6 20 V14 C6 8 9.2 3.5 12 1 Z" fill="#0055B3" stroke="#003380" stroke-width="0.8"/>
                    <rect x="8" y="6.5" width="8" height="2.2" rx="0.4" fill="#38BDF8"/>
                    <rect x="8" y="9.7" width="8" height="2.2" rx="0.4" fill="#BAE6FD"/>
                    <rect x="8" y="12.9" width="8" height="2.2" rx="0.4" fill="#38BDF8"/>
                    <rect x="8" y="16.1" width="8" height="2.2" rx="0.4" fill="#BAE6FD"/>
                    <rect x="8.5" y="19.2" width="7" height="2.6" rx="0.5" fill="#FFFFFF"/>
                    <rect x="10.5" y="20" width="3" height="1" fill="#0055B3"/>
                </svg>
            `:`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="6" y="8.5" width="12" height="14" rx="1.2" fill="#EA580C" stroke="#C2410C" stroke-width="0.6"/>
                    <line x1="7.5" y1="11.5" x2="16.5" y2="11.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <line x1="7.5" y1="14.5" x2="16.5" y2="14.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <line x1="7.5" y1="17.5" x2="16.5" y2="17.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <line x1="7.5" y1="20.5" x2="16.5" y2="20.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <rect x="7" y="1.5" width="10" height="5.8" rx="1.5" fill="#C2410C"/>
                    <rect x="8.5" y="2.5" width="7" height="2" rx="0.5" fill="#FEF08A"/>
                    <rect x="5.2" y="3" width="1.5" height="1" rx="0.3" fill="#C2410C"/>
                    <rect x="17.3" y="3" width="1.5" height="1" rx="0.3" fill="#C2410C"/>
                </svg>
            `}get_hub_icon_svg(e){return e==="Ocean"||e==="seaport"||e==="port"?`
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0055B3" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="5" r="3"/>
                    <line x1="12" y1="22" x2="12" y2="8"/>
                    <path d="M5 12H2a10 10 0 0 0 20 0h-3"/>
                </svg>
            `:`
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.2-1.1.6L2.5 8l6.4 3.3L7 15l-3.3-1.1-1.2 1.3 4.2 3.8 3.8 4.2 1.3-1.2L10.7 18.7l3.7-1.9 3.3 6.4 1.2-1.2-.4-2.6Z"/>
                </svg>
            `}get_active_vehicle_mode(e,t){if(!e)return"Ocean";let i=e.shipping_method||"Ocean",n=(e.status||"").toLowerCase();if(["delivered","completed","received","closed","giao h\xE0ng th\xE0nh c\xF4ng","giao h\xE0ng","nh\u1EADp kho","chu\u1EA9n b\u1ECB nh\u1EADp kho"].some(o=>n.includes(o))||["customs clearance","customs","th\xF4ng quan","h\u1EA3i quan","ch\u1EDD nh\u1EADp kho"].some(o=>n.includes(o)))return"Road";if(e.transit_route&&Array.isArray(e.transit_route)){let o=e.transit_route.find(l=>l.is_current==1||l.activity&&l.activity.includes("(Current Position)"));if(o){let l=(o.milestone||"").toUpperCase();if(["ARRIVED","DISCHARGED","GATE_OUT","DELIVERED"].includes(l)||["BOOKED","GATE_IN"].includes(l))return"Road"}}let a=typeof t=="number"?t:typeof e.progress=="number"?e.progress:.55,c=e.progress_thresholds||[0,.05,.95,1],d=c[1]!==void 0?c[1]:.05,s=c[2]!==void 0?c[2]:.95;return a<=d||a>=s?"Road":i==="Air"?"Air":"Ocean"}calculateBearing(e,t,i,n){let a=Math.PI/180,c=180/Math.PI,d=e*a,s=i*a,o=(n-t)*a;for(;o>Math.PI;)o-=2*Math.PI;for(;o<-Math.PI;)o+=2*Math.PI;let l=Math.sin(o)*Math.cos(s),r=Math.cos(d)*Math.sin(s)-Math.sin(d)*Math.cos(s)*Math.cos(o);return(Math.atan2(l,r)*c+360)%360}computePolylineMetrics(e){let t=[0],i=0;if(!e||e.length<=1)return{cumulative:[0],total:0};for(let n=0;n<e.length-1;n++){let[a,c]=e[n],[d,s]=e[n+1],o=s-c;o>180&&(o-=360),o<-180&&(o+=360);let l=d-a,r=Math.cos((a+d)/2*Math.PI/180);i+=Math.hypot(l,o*r),t.push(i)}return{cumulative:t,total:i}}interpolateAtProgress(e,t,i){if(!e||e.length===0)return{point:[0,0],bearing:0};if(e.length===1)return{point:e[0],bearing:0};let n=Math.max(0,Math.min(1,i));if(t.total===0)return{point:e[0],bearing:0};let a=n*t.total,c=0;for(let y=0;y<t.cumulative.length-1;y++)if(a>=t.cumulative[y]&&a<=t.cumulative[y+1]){c=y;break}c>=e.length-1&&(c=e.length-2);let d=t.cumulative[c],s=t.cumulative[c+1]-d,o=s===0?0:Math.max(0,Math.min(1,(a-d)/s)),l=e[c],r=e[c+1]||l,h=l[0]+o*(r[0]-l[0]),p=l[1],x=r[1]-p;x>180&&(x-=360),x<-180&&(x+=360);let C=p+o*x,A=this.calculateBearing(l[0],l[1],r[0],r[1]);return{point:[h,C],bearing:A}}perpendicularDistance(e,t,i){let[n,a]=e,[c,d]=t,[s,o]=i,l=o-d,r=s-c;l>180&&(l-=360),l<-180&&(l+=360);let h=a-d,p=n-c;h>180&&(h-=360),h<-180&&(h+=360);let b=l*l+r*r;if(b===0)return Math.hypot(h,p);let x=Math.max(0,Math.min(1,(h*l+p*r)/b)),C=x*l,A=x*r;return Math.hypot(h-C,p-A)}douglasPeucker(e,t=.002){if(!e||!Array.isArray(e)||e.length<=2)return e||[];let i=0,n=0,a=e.length-1;for(let c=1;c<a;c++){let d=this.perpendicularDistance(e[c],e[0],e[a]);d>i&&(i=d,n=c)}if(i>t){let c=this.douglasPeucker(e.slice(0,n+1),t),d=this.douglasPeucker(e.slice(n),t);return c.slice(0,c.length-1).concat(d)}else return[e[0],e[a]]}animateVehicle(e,t,i,n=1500,a="Ocean"){let c=this;if(this.currentAnimationId&&(cancelAnimationFrame(this.currentAnimationId),this.currentAnimationId=null),!e||!t||t.length===0)return;let d=this.computePolylineMetrics(t),s=typeof e._currentProgress=="number"?e._currentProgress:0,o=Math.max(0,Math.min(1,i)),l=performance.now();function r(h){let p=h-l,b=n<=0?1:Math.min(1,p/n),x=1-Math.pow(1-b,3),C=s+(o-s)*x,{point:A,bearing:y}=c.interpolateAtProgress(t,d,C);e.setLatLng(A);let T=e.getElement?e.getElement():null;if(T){if(e._shipment){let S=c.get_active_vehicle_mode(e._shipment,C);if(e._lastActiveMode!==S){e._lastActiveMode=S;let H=T.querySelector(".lw-vehicle-icon-svg");H&&(H.innerHTML=c.get_vehicle_svg(S));let I=T.querySelector(".lw-vehicle-box");I&&(I.style.borderColor=S==="Air"?"#007AFF":S==="Ocean"?"#0055B3":"#EA580C")}}let E=T.querySelector(".lw-vehicle-icon-svg")||T.querySelector("svg");E&&(E.style.transform=`rotate(${y}deg)`,E.style.transformOrigin="center center")}e._currentProgress=C,b<1?c.currentAnimationId=requestAnimationFrame(r):c.currentAnimationId=null}this.currentAnimationId=requestAnimationFrame(r)}update_map_view(e){!this.map||(e?this.render_single_shipment_map(e):this.render_fleet_overview_map(this.data?this.data.shipments||[]:[]))}align_route_coords(e,t=150){if(!e||!Array.isArray(e)||e.length===0)return e;let i=[],n=null,a=0;for(let l of e){if(!Array.isArray(l)||l.length<2||typeof l[1]!="number")continue;let r=l[0],h=l[1]+a;if(n!==null){let p=h-n;p>180?(a-=360,h-=360):p<-180&&(a+=360,h+=360)}n=h,i.push([r,h])}if(i.length===0)return e;let c=i.map(l=>l[1]),d=c.reduce((l,r)=>l+r,0)/c.length,s=0,o=Math.abs(d-t);for(let l of[-2,-1,1,2]){let r=Math.abs(d+l*360-t);r<o&&(o=r,s=l*360)}return s!==0?i.map(l=>[l[0],l[1]+s]):i}render_fleet_overview_map(e){if(!this.map)return;let t=window.L||window.leaflet;if(!t)return;let i=this;this.clear_map_layers(),$("#hub-map-title").text("B\u1EA3n \u0111\u1ED3 Gi\xE1m s\xE1t To\xE0n c\u1EA7u (Fleet Overview)"),$("#hub-map-reset-btn").addClass("active");let n=(e||[]).filter(s=>s.status==="In Transit"||s.status==="Customs Clearance");n.length===0&&(n=(e||[]).filter(s=>s.status!=="Draft")),n.length===0&&(n=e||[]),$("#hub-selected-shipment-badge").text(`To\xE0n c\u1EA3nh: ${n.length} l\xF4 h\xE0ng \u0111ang h\xE0nh tr\xECnh`).show(),this.update_marine_overlay("Ocean");let a=[],c={"san francisco":[37.619,-122.375],"tan son nhat":[10.8188,106.652],oakland:[37.804,-122.271],"hai phong":[20.865,106.683],"cat lai":[10.762,106.792],"long beach":[33.754,-118.216],"los angeles":[33.743,-118.267],shanghai:[31.23,121.473],singapore:[1.29,103.851],rotterdam:[51.924,4.477],busan:[35.179,129.075],tokyo:[35.676,139.65]};function d(s){if(!s)return null;let o=s.toLowerCase();for(let l in c)if(o.includes(l))return c[l];return null}if(n.forEach((s,o)=>{let l=s.shipping_method||"Ocean",r=l==="Air",h=l==="Road",p=[];if(s.full_route&&Array.isArray(s.full_route)&&s.full_route.length>=2?p=s.full_route:s.route&&Array.isArray(s.route)&&s.route.length>=2?p=s.route:s.legs&&Array.isArray(s.legs)&&s.legs.length>0&&s.legs.forEach(v=>{let m=v.coordinates_latlon||v.coordinates||[];m.length>0&&(p=p.concat(m))}),p.length<2){let v=d(s.origin_port)||[31.23,121.47],m=d(s.destination_port)||[10.76,106.79],k=v[1],w=m[1];k<0&&w>0&&Math.abs(k-w)>180?k+=360:w<0&&k>0&&Math.abs(w-k)>180&&(w+=360);let M=(v[0]+m[0])/2+(r?6:-3),F=(k+w)/2;p=[[v[0],k],[M,F],[m[0],w]]}p=i.align_route_coords(p,150);let b=i.douglasPeucker(p,.003);if((!b||b.length<2)&&(b=p),s.legs&&Array.isArray(s.legs)&&s.legs.length>0)s.legs.forEach(v=>{let m=v.coordinates_latlon||v.coordinates||[];if(m.length>=2){m=i.align_route_coords(m,150);let k=i.douglasPeucker(m,.003);(!k||k.length<2)&&(k=m);let w=v.mode||(v.vehicle_type==="Truck"?"Road":l),M=w==="Road",F=w==="Air",j=M?"#FF9500":F?"#0284c7":"#0055B3";s.is_delayed==1&&!M&&(j="#DC2626");let V=t.polyline(k,{color:j,weight:M?3:3.8,opacity:.85,dashArray:F||M?"6, 8":""}).addTo(i.map);V.bindTooltip(`<b>${s.name}</b> (${s.carrier||""})<br>${v.name||"H\xE0nh tr\xECnh"}<br><span style="color:#0071E3; font-weight:600;">\u{1F449} Nh\u1EA5p \u0111\u1EC3 xem \u0111\u01A1n n\xE0y</span>`,{sticky:!0}),V.on("click",()=>{i.select_shipment(s.name)}),i.mapLayers.routePolylines.push(V),a.push(V)}});else{let v=h?"#FF9500":r?"#0284c7":"#0055B3";s.is_delayed==1&&(v="#DC2626");let m=t.polyline(b,{color:v,weight:3.5,opacity:.82,dashArray:r||h?"6, 8":""}).addTo(i.map);m.bindTooltip(`<b>${s.name}</b> (${s.carrier||""})<br>${s.origin_port||"Origin"} \u2794 ${s.destination_port||"Dest"}<br><span style="color:#0071E3; font-weight:600;">\u{1F449} Nh\u1EA5p \u0111\u1EC3 xem \u0111\u01A1n n\xE0y</span>`,{sticky:!0}),m.on("click",()=>{i.select_shipment(s.name)}),i.mapLayers.routePolylines.push(m),a.push(m)}let C=b[0],A=b[b.length-1],y=s.origin&&s.origin.name||s.origin_port||s.name,T=t.circleMarker(C,{radius:5,color:"#16A34A",fillColor:"#FFFFFF",fillOpacity:1,weight:2}).addTo(i.map);T.bindTooltip(`Xu\u1EA5t ph\xE1t (Kho ngu\u1ED3n): ${y}`),T.on("click",()=>{i.select_shipment(s.name)}),i.mapLayers.markers.push(T);let E=s.destination&&s.destination.name||"Kho b\xE3i Logistics C\xE1p Kim Kh\xE1nh \u0110\xE0 N\u1EB5ng",S=t.circleMarker(A,{radius:5,color:"#DC2626",fillColor:"#FFFFFF",fillOpacity:1,weight:2}).addTo(i.map);S.bindTooltip(`\u0110\xEDch \u0111\u1EBFn: ${E}`),S.on("click",()=>{i.select_shipment(s.name)}),i.mapLayers.markers.push(S);let H=typeof s.progress=="number"?s.progress:.55,I=i.get_active_vehicle_mode(s,H),z=i.computePolylineMetrics(b),f=i.interpolateAtProgress(b,z,H),g=s.is_delayed==1?"#DC2626":I==="Air"?"#007AFF":I==="Ocean"?"#0055B3":"#EA580C",_=t.divIcon({className:"custom-fleet-vehicle-icon",html:`
                    <div style="background: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.3); border: 2.5px solid ${g}; cursor: pointer; transition: transform 0.2s;" title="${s.name} - ${s.carrier||""}">
                        <div style="display: flex; align-items: center; justify-content: center; transform: rotate(${f.bearing}deg); transform-origin: center center;">
                            ${i.get_vehicle_svg(I)}
                        </div>
                    </div>
                `,iconSize:[36,36],iconAnchor:[18,18]}),L=t.marker(f.point,{icon:_,zIndexOffset:500+o*10}).addTo(i.map),D=I==="Air"?"H\xE0ng kh\xF4ng (M\xE1y bay \u2708\uFE0F)":I==="Ocean"?"\u0110\u01B0\u1EDDng bi\u1EC3n (T\xE0u h\xE0ng \u{1F6A2})":"\u0110\u01B0\u1EDDng b\u1ED9 (Xe t\u1EA3i \u{1F69A})";L.bindTooltip(`
                <div style="font-size: 11.5px; line-height: 1.4;">
                    <strong style="color: #0071E3;">${s.name}</strong> (${s.carrier||""})<br>
                    ${s.origin?s.origin.name:s.origin_port||"Origin"} \u2794 ${s.destination?s.destination.name:"Kho b\xE3i Logistics C\xE1p Kim Kh\xE1nh \u0110\xE0 N\u1EB5ng"}<br>
                    Ph\u01B0\u01A1ng ti\u1EC7n hi\u1EC7n t\u1EA1i: <b>${D}</b><br>
                    Tr\u1EA1ng th\xE1i: <b>${s.status}</b><br>
                    <span style="color: #0071E3; font-weight: 600;">\u{1F449} Nh\u1EA5p \u0111\u1EC3 xem h\xE0nh tr\xECnh chi ti\u1EBFt</span>
                </div>
            `,{direction:"top",offset:[0,-12]}),L.on("click",()=>{i.select_shipment(s.name)}),i.mapLayers.fleetVehicleMarkers.push(L),a.push(L)}),a.length>0)try{let o=t.featureGroup(a).getBounds(),l=i.map.getBoundsZoom(o,!1,[50,50]);i.map.setView(o.getCenter(),Math.min(Math.max(l,2),3))}catch(s){i.map.setView([22,150],3)}else i.map.setView([22,150],3)}render_single_shipment_map(e){if(!this.map||!e)return;let t=window.L||window.leaflet;if(!t)return;this.clear_map_layers(),$("#hub-map-title").text(`H\xE0nh tr\xECnh Chi ti\u1EBFt: ${e.name}`),$("#hub-map-reset-btn").removeClass("active"),$("#hub-selected-shipment-badge").text(`L\xF4 h\xE0ng: ${e.name} (${e.carrier||""})`).show();let i=e.shipping_method||"Ocean";this.update_marine_overlay(i);let n=[];if(e.full_route&&Array.isArray(e.full_route)&&e.full_route.length>0?n=e.full_route:e.route&&Array.isArray(e.route)&&e.route.length>0?n=e.route:e.legs&&Array.isArray(e.legs)&&e.legs.length>0&&e.legs.forEach(f=>{let g=f.coordinates_latlon||f.coordinates||[];g.length>0&&(n=n.concat(g))}),n.length===0){let f=parseFloat(e.current_lat)||20,g=parseFloat(e.current_lon)||120;n=[[31.23,121.47],[f,g],[10.77,106.7]]}n=this.align_route_coords(n,150);let a=this.douglasPeucker(n,.002);(!a||a.length<2)&&(a=n);let c=[];if(e.legs&&Array.isArray(e.legs)&&e.legs.length>0&&e.legs.forEach(f=>{let g=f.coordinates_latlon||f.coordinates||[];if(g.length>=2){g=this.align_route_coords(g,150);let _=this.douglasPeucker(g,.002);(!_||_.length<2)&&(_=g);let L=f.mode==="Road",D=f.mode==="Air",v=L?"#FF9500":D?"#0284c7":"#0055B3",m=L||D?"6, 8":"",k=L?3.5:4,w=t.polyline(_,{color:v,weight:k,opacity:.9,dashArray:m}).addTo(this.map);c.push(w),this.mapLayers.routePolylines.push(w)}}),c.length===0){let f=i==="Air",g=i==="Road",_=t.polyline(a,{color:g?"#FF9500":f?"#0284c7":"#0055B3",weight:4,opacity:.9,dashArray:f||g?"6, 8":""}).addTo(this.map);c.push(_),this.mapLayers.routePolylines.push(_)}let d=a[0],s=e.origin&&e.origin.name||e.origin_port||"Kho/Nh\xE0 m\xE1y xu\u1EA5t ph\xE1t",o=t.divIcon({className:"hub-origin-marker-icon",html:'<div style="background: #16a34a; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); cursor: pointer;" title="\u0110i\u1EC3m xu\u1EA5t ph\xE1t (Kho ngu\u1ED3n - \u0110i\u1EC3m O)">O</div>',iconSize:[26,26],iconAnchor:[13,13]}),l=t.marker(d,{icon:o}).addTo(this.map),r=((d[1]+180)%360+360)%360-180;l.bindPopup(`<b>\u0110i\u1EC3m xu\u1EA5t ph\xE1t (Kho ngu\u1ED3n):</b><br>${s}<br><small>To\u1EA1 \u0111\u1ED9: ${d[0].toFixed(4)}, ${r.toFixed(4)}</small>`),this.mapLayers.markers.push(l);let h=a[a.length-1],p=e.destination&&e.destination.name||"Kho b\xE3i Logistics C\xE1p Kim Kh\xE1nh \u0110\xE0 N\u1EB5ng (G\u1EA7n \u0110H B\xE1ch Khoa)",b=t.divIcon({className:"hub-dest-marker-icon",html:'<div style="background: #dc2626; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); cursor: pointer;" title="\u0110i\u1EC3m \u0111\xEDch \u0111\u1EBFn (Kho C\xE1p Kim Kh\xE1nh \u0110\xE0 N\u1EB5ng - \u0110i\u1EC3m D)">D</div>',iconSize:[26,26],iconAnchor:[13,13]}),x=t.marker(h,{icon:b}).addTo(this.map),C=((h[1]+180)%360+360)%360-180;if(x.bindPopup(`<b>\u0110i\u1EC3m \u0111\xEDch \u0111\u1EBFn (Kho nh\u1EADn h\xE0ng):</b><br>${p}<br><small>To\u1EA1 \u0111\u1ED9: ${h[0].toFixed(4)}, ${C.toFixed(4)}</small>`),this.mapLayers.markers.push(x),e.legs&&e.legs.length>=2){let f=e.legs[0],g=e.legs[1],_=f.coordinates_latlon&&f.coordinates_latlon.length>0?f.coordinates_latlon[f.coordinates_latlon.length-1]:null,L=g.coordinates_latlon&&g.coordinates_latlon.length>0?g.coordinates_latlon[g.coordinates_latlon.length-1]:null;if(_){let D=t.divIcon({className:"hub-dep-port-icon",html:`<div style="background: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border: 2.5px solid #0055B3; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: pointer;" title="C\u1EA3ng/S\xE2n bay xu\u1EA5t ph\xE1t">
                        ${this.get_hub_icon_svg(i)}
                    </div>`,iconSize:[28,28],iconAnchor:[14,14]}),v=t.marker(_,{icon:D}).addTo(this.map);v.bindPopup(`<b>Tr\u1EA1m trung chuy\u1EC3n xu\u1EA5t:</b><br>${e.origin_port||"C\u1EA3ng/S\xE2n bay xu\u1EA5t"}`),this.mapLayers.markers.push(v)}if(L){let D=t.divIcon({className:"hub-arr-port-icon",html:`<div style="background: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border: 2.5px solid #0055B3; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: pointer;" title="C\u1EA3ng/S\xE2n bay \u0111\u1EBFn">
                        ${this.get_hub_icon_svg(i)}
                    </div>`,iconSize:[28,28],iconAnchor:[14,14]}),v=t.marker(L,{icon:D}).addTo(this.map);v.bindPopup(`<b>Tr\u1EA1m trung chuy\u1EC3n \u0111\u1EBFn:</b><br>${e.destination_port||"C\u1EA3ng/S\xE2n bay \u0111\u1EBFn"}`),this.mapLayers.markers.push(v)}}let A=typeof e.progress=="number"?e.progress:.55,y=this.get_active_vehicle_mode(e,A),T=this.computePolylineMetrics(a),E=this.interpolateAtProgress(a,T,0),S=y==="Air"?"#007AFF":y==="Ocean"?"#0055B3":"#EA580C",H=t.divIcon({className:"custom-vehicle-icon-hub",html:`
                <div class="lw-vehicle-box" style="background: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.3); border: 2.8px solid ${S};">
                    <div class="lw-vehicle-icon-svg" style="display: flex; align-items: center; justify-content: center; transform: rotate(${E.bearing}deg); transform-origin: center center;">
                        ${this.get_vehicle_svg(y)}
                    </div>
                </div>
            `,iconSize:[40,40],iconAnchor:[20,20]});this.mapLayers.vehicleMarker=t.marker(E.point,{icon:H,zIndexOffset:1e3}).addTo(this.map),this.mapLayers.vehicleMarker._currentProgress=0,this.mapLayers.vehicleMarker._shipment=e,this.mapLayers.vehicleMarker._lastActiveMode=y;let I=e.delay_days>0?`<div style="color: #dc2626; font-weight: 700; margin-top: 4px;">\u26A0\uFE0F L\u1EC7ch ETA: +${e.delay_days} ng\xE0y</div>`:'<div style="color: #16a34a; font-weight: 600; margin-top: 4px;">\u2705 H\xE0nh tr\xECnh \u0111\xFAng ti\u1EBFn \u0111\u1ED9</div>',z=y==="Air"?"H\xE0ng kh\xF4ng (M\xE1y bay \u2708\uFE0F)":y==="Ocean"?"\u0110\u01B0\u1EDDng bi\u1EC3n (T\xE0u h\xE0ng \u{1F6A2})":"\u0110\u01B0\u1EDDng b\u1ED9 (Xe t\u1EA3i \u{1F69A})";this.mapLayers.vehicleMarker.bindPopup(`
            <div style="font-size: 12px; min-width: 190px; line-height: 1.5;">
                <div style="font-weight: 700; color: #0284c7; font-size: 13px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; margin-bottom: 4px;">
                    ${e.name}
                </div>
                <div><b>Ph\u01B0\u01A1ng ti\u1EC7n hi\u1EC7n t\u1EA1i:</b> ${z}</div>
                <div><b>\u0110\u01A1n v\u1ECB v\u1EADn chuy\u1EC3n:</b> ${e.carrier||""} (${e.vessel_name||e.flight_number||"V\u1EADn t\u1EA3i \u0111a ph\u01B0\u01A1ng th\u1EE9c"})</div>
                <div><b>M\xE3 Container:</b> ${e.container_id||"N/A"}</div>
                <div><b>Tr\u1EA1ng th\xE1i:</b> ${e.status}</div>
                <div><b>L\u1ED9 tr\xECnh:</b> ${e.origin?e.origin.name:e.origin_port||"Origin"} \u2794 ${e.destination?e.destination.name:"Kho b\xE3i Logistics C\xE1p Kim Kh\xE1nh \u0110\xE0 N\u1EB5ng"}</div>
                ${I}
            </div>
        `),this.animateVehicle(this.mapLayers.vehicleMarker,a,A,1600);try{let g=t.featureGroup(c).getBounds(),_=this.map.getBoundsZoom(g,!1,[45,45]);this.map.setView(g.getCenter(),Math.min(Math.max(_,2),7))}catch(f){this.map.setView(E.point,4)}}clear_map_layers(){if(!!this.map){if(this.currentAnimationId&&(cancelAnimationFrame(this.currentAnimationId),this.currentAnimationId=null),this.mapLayers.routePolylines.forEach(e=>{try{this.map.removeLayer(e)}catch(t){}}),this.mapLayers.routePolylines=[],this.mapLayers.markers.forEach(e=>{try{this.map.removeLayer(e)}catch(t){}}),this.mapLayers.markers=[],this.mapLayers.vehicleMarker){try{this.map.removeLayer(this.mapLayers.vehicleMarker)}catch(e){}this.mapLayers.vehicleMarker=null}this.mapLayers.fleetVehicleMarkers&&(this.mapLayers.fleetVehicleMarkers.forEach(e=>{try{this.map.removeLayer(e)}catch(t){}}),this.mapLayers.fleetVehicleMarkers=[])}}reset_map_view(){this.selectedShipment=null,$("#hub-shipments-tbody tr").removeClass("selected"),this.render_stepper(null),this.render_fleet_overview_map(this.data?this.data.shipments||[]:[])}sync_now(e){let t=this,i=$("#hub-btn-sync-now");i.prop("disabled",!0).html('<i class="fa fa-spinner fa-spin"></i> \u0110ang \u0111\u1ED3ng b\u1ED9...'),frappe.call({method:"logistics_wizard.api.sync_shipment_now",args:{shipment:e},callback:function(n){i.prop("disabled",!1).html('<i class="fa fa-cloud-download"></i> \u0110\u1ED3ng b\u1ED9 t\u1EE9c th\xEC (Sync Now)'),n&&n.message&&n.message.success!==!1?(frappe.show_alert({message:__("\u0110\u1ED3ng b\u1ED9 h\xE0nh tr\xECnh th\xE0nh c\xF4ng!"),indicator:"green"}),t.refresh(e)):(frappe.msgprint({title:__("\u0110\u1ED3ng b\u1ED9 ho\xE0n t\u1EA5t"),message:n.message?n.message.message:__("\u0110\xE3 ki\u1EC3m tra d\u1EEF li\u1EC7u h\xE0nh tr\xECnh m\u1EDBi nh\u1EA5t."),indicator:"blue"}),t.refresh(e))},error:function(){i.prop("disabled",!1).html('<i class="fa fa-cloud-download"></i> \u0110\u1ED3ng b\u1ED9 t\u1EE9c th\xEC (Sync Now)'),frappe.show_alert({message:__("L\u1ED7i k\u1EBFt n\u1ED1i khi \u0111\u1ED3ng b\u1ED9!"),indicator:"red"})}})}},R=class{constructor(e){this.wrapper=e,this.currentCaseId="IMP-2026-001",this.currentRule="weight",this.currentCaseType="all",this.caseData=this.get_mock_cases_data()}init(){this.bind_events(),this.load_data(this.currentCaseId)}get_mock_cases_data(){return{"IMP-2026-001":{case_id:"IMP-2026-001",party:"ABC Electronics Co., Ltd",case_type:"import",po_value:125e3,estimated_cost:16800,actual_cost:18350,variance_amount:1550,variance_pct:9.2,status:"\u0110ang \u0110\u1ED1i So\xE1t",status_class:"badge-in-transit",lcv_id:"LCV-2026-0004",cost_items:[{type:"C\u01B0\u1EDBc v\u1EADn chuy\u1EC3n bi\u1EC3n (Ocean Freight)",supplier:"Maersk Line Vietnam",inv_no:"INV-MAE-8821",est:8500,act:9200,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"B\u1EA3o hi\u1EC3m h\xE0ng h\xF3a (Cargo Insurance)",supplier:"Bao Viet Insurance",inv_no:"BV-2026-091",est:600,act:650,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Thu\u1EBF nh\u1EADp kh\u1EA9u (Customs Import Duty)",supplier:"Chi c\u1EE5c H\u1EA3i Quan C\u1EA3ng SG KV4",inv_no:"HQ-77218-TK",est:3200,act:3200,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Thu\u1EBF GTGT h\xE0ng nh\u1EADp kh\u1EA9u (Import VAT)",supplier:"Chi c\u1EE5c H\u1EA3i Quan C\u1EA3ng SG KV4",inv_no:"HQ-77218-VAT",est:1500,act:1500,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Ph\xED THC & ph\u1EE5 ph\xED c\u1EA3ng (Port Surcharges)",supplier:"T\xE2n C\u1EA3ng S\xE0i G\xF2n (SNP)",inv_no:"SNP-2026-112",est:850,act:950,status:"\u0110ang \u0110\u1ED1i So\xE1t"},{type:"N\xE2ng h\u1EA1 & l\u01B0u kho (Handling & Storage)",supplier:"C\u1EA3ng C\xE1t L\xE1i ICD",inv_no:"ICD-44120",est:400,act:580,status:"\u0110ang \u0110\u1ED1i So\xE1t"},{type:"L\u01B0u b\xE3i container (Demurrage/Detention)",supplier:"Maersk Line Vietnam",inv_no:"DEM-8821-02",est:0,act:320,status:"C\u1EA7n R\xE0 So\xE1t"},{type:"V\u1EADn chuy\u1EC3n n\u1ED9i \u0111\u1ECBa (Trucking)",supplier:"Huu Toan Logistics",inv_no:"HT-9901-TRK",est:950,act:1100,status:"\u0110ang \u0110\u1ED1i So\xE1t"},{type:"Ph\xED d\u1ECBch v\u1EE5 h\u1EA3i quan (Customs Brokerage)",supplier:"Schenker Vietnam",inv_no:"DB-8812-FEE",est:500,act:500,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Ki\u1EC3m tra ch\u1EA5t l\u01B0\u1EE3ng (Inspection)",supplier:"Quatest 3",inv_no:"QT3-11029",est:300,act:350,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Chi ph\xED ph\u1EE5 kh\xE1c (Other Contingency)",supplier:"N\u1ED9i b\u1ED9 c\xF4ng ty",inv_no:"INT-EXP-01",est:0,act:0,status:"Ch\u1EDD H\xF3a \u0110\u01A1n"}],items_to_allocate:[{item_code:"CPU-INTEL-I9",name:"Intel Core i9-14900K Processor",qty:200,unit_price:350,weight:.15,volume:4e-4},{item_code:"RAM-DDR5-32G",name:"Corsair Vengeance 32GB DDR5 RAM",qty:500,unit_price:70,weight:.08,volume:2e-4},{item_code:"SSD-NVME-2TB",name:"Samsung 990 Pro 2TB NVMe SSD",qty:200,unit_price:100,weight:.06,volume:15e-5}],audit_checks:[{title:"Tr\xF9ng L\u1EB7p H\xF3a \u0110\u01A1n (Duplicate Check)",status:"H\u1EE3p l\u1EC7",status_class:"delay-tag-ontime",border:"#10b981",desc:"Kh\xF4ng ph\xE1t hi\u1EC7n h\xF3a \u0111\u01A1n tr\xF9ng l\u1EB7p s\u1ED1 ch\u1EE9ng t\u1EEB ho\u1EB7c nh\xE0 cung c\u1EA5p."},{title:"Chi Ph\xED Tr\u1ECDng Y\u1EBFu (Missing Cost Check)",status:"C\u1EA7n r\xE0 so\xE1t",status_class:"delay-tag-positive",border:"#d97706",desc:"Ch\u01B0a nh\u1EADn h\xF3a \u0111\u01A1n n\xE2ng h\u1EA1 c\u1EA3ng \u0111\xEDch (Port Handling D/O). C\u1EA7n li\xEAn h\u1EC7 \u0111\u1EA1i l\xFD h\xE3ng t\xE0u tr\u01B0\u1EDBc ng\xE0y 14/10."},{title:"G\xE1n \u0110\xFAng V\u1EE5 Vi\u1EC7c (Association Check)",status:"Kh\u1EDBp 100%",status_class:"delay-tag-ontime",border:"#10b981",desc:"T\u1EA5t c\u1EA3 6 h\xF3a \u0111\u01A1n d\u1ECBch v\u1EE5 \u0111\u1EC1u tham chi\u1EBFu ch\xEDnh x\xE1c s\u1ED1 PO-2026-0042 v\xE0 Trade Case IMP-2026-001."}]},"EXP-2026-002":{case_id:"EXP-2026-002",party:"Global Coffee Exporter JSC",case_type:"export",po_value:65e3,estimated_cost:3800,actual_cost:4200,variance_amount:400,variance_pct:10.5,status:"S\u1EB5n S\xE0ng Xu\u1EA5t Kh\u1EA9u",status_class:"badge-delivered",lcv_id:"LCV-2026-EXP-01",export_revenue:65e3,export_cogs:45e3,export_logistics:4200,cost_items:[{type:"C\u01B0\u1EDBc v\u1EADn chuy\u1EC3n bi\u1EC3n xu\u1EA5t (Ocean Freight Export)",supplier:"ONE Ocean Network Express",inv_no:"ONE-EX-3312",est:2200,act:2450,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"B\u1EA3o hi\u1EC3m h\xE0ng h\xF3a (Marine Cargo Insurance)",supplier:"Bao Minh Insurance",inv_no:"BM-2026-339",est:250,act:270,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Thu\u1EBF xu\u1EA5t kh\u1EA9u (Export Duty)",supplier:"H\u1EA3i Quan C\u1EA3ng Quy Nh\u01A1n",inv_no:"HQ-EXP-0081",est:0,act:0,status:"Mi\u1EC5n Thu\u1EBF"},{type:"Ph\xED THC c\u1EA3ng b\u1ED1c (Port Handling Surcharge)",supplier:"C\u1EA3ng Qu\u1ED1c T\u1EBF Quy Nh\u01A1n",inv_no:"QN-THC-881",est:350,act:380,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Hun tr\xF9ng & Ki\u1EC3m d\u1ECBch (Fumigation & Phytosanitary)",supplier:"VFC Fumigation Co.",inv_no:"VFC-2026-77",est:180,act:180,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"L\xE0m th\u1EE7 t\u1EE5c C/O Form ICO (Certificate of Origin)",supplier:"VCCI Chi nh\xE1nh \u0110\xE0 N\u1EB5ng",inv_no:"VCCI-CO-102",est:70,act:70,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"K\xE9o v\u1ECF & v\u1EADn chuy\u1EC3n n\u1ED9i \u0111\u1ECBa (Trucking)",supplier:"Binh Dinh Express Logistics",inv_no:"BD-TRK-551",est:500,act:580,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Ph\xED m\xF4i gi\u1EDBi h\u1EA3i quan (Brokerage Fee)",supplier:"Transimex Logistics",inv_no:"TMX-2026-44",est:150,act:170,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Chi ph\xED ph\u1EE5 kh\xE1c (Contingency)",supplier:"N\u1ED9i b\u1ED9",inv_no:"INT-EXP-02",est:100,act:100,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"}],items_to_allocate:[{item_code:"COFFEE-ROBUSTA-G1",name:"Robusta Green Coffee Beans Grade 1",qty:2e4,unit_price:2.25,weight:1,volume:.0015},{item_code:"COFFEE-ARABICA-S18",name:"Arabica Roasted Coffee Screen 18",qty:5e3,unit_price:4,weight:1,volume:.0018}],audit_checks:[{title:"Tr\xF9ng L\u1EB7p H\xF3a \u0110\u01A1n (Duplicate Check)",status:"H\u1EE3p l\u1EC7",status_class:"delay-tag-ontime",border:"#10b981",desc:"Kh\xF4ng c\xF3 ch\u1EE9ng t\u1EEB tr\xF9ng l\u1EB7p \u0111\u1ED1i t\xE1c xu\u1EA5t kh\u1EA9u."},{title:"Chi Ph\xED Tr\u1ECDng Y\u1EBFu (Missing Cost Check)",status:"\u0110\u1EA7y \u0111\u1EE7",status_class:"delay-tag-ontime",border:"#10b981",desc:"\u0110\xE3 nh\u1EADn \u0111\u1EE7 ch\u1EE9ng t\u1EEB hun tr\xF9ng, C/O v\xE0 bill of lading."},{title:"G\xE1n \u0110\xFAng V\u1EE5 Vi\u1EC7c (Association Check)",status:"Kh\u1EDBp 100%",status_class:"delay-tag-ontime",border:"#10b981",desc:"H\xF3a \u0111\u01A1n ONE v\xE0 VFC tham chi\u1EBFu ch\xEDnh x\xE1c Sales Order SO-2026-009."}]},"IMP-2026-003":{case_id:"IMP-2026-003",party:"Pacific Seafood Import Co.",case_type:"import",po_value:84e3,estimated_cost:11200,actual_cost:11050,variance_amount:-150,variance_pct:-1.3,status:"\u0110\xE3 Ho\xE0n T\u1EA5t",status_class:"badge-delivered",lcv_id:"LCV-2026-0002",cost_items:[{type:"C\u01B0\u1EDBc v\u1EADn chuy\u1EC3n h\xE0ng \u0111\xF4ng l\u1EA1nh (Reefer Freight)",supplier:"Hapag-Lloyd Vietnam",inv_no:"HL-RF-9021",est:6800,act:6700,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"B\u1EA3o hi\u1EC3m h\xE0ng h\xF3a (Reefer Cargo Insurance)",supplier:"PVI Insurance",inv_no:"PVI-RF-122",est:450,act:450,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Thu\u1EBF nh\u1EADp kh\u1EA9u (Customs Import Duty)",supplier:"Chi c\u1EE5c H\u1EA3i Quan C\u1EA3ng H\u1EA3i Ph\xF2ng",inv_no:"HQ-HP-3312",est:1800,act:1800,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"Ki\u1EC3m d\u1ECBch th\u1EE7y s\u1EA3n (Fisheries Quarantine)",supplier:"Chi c\u1EE5c Th\xFA Y V\xF9ng 2",inv_no:"KD-HP-0091",est:350,act:350,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"C\u1EAFm \u0111i\u1EC7n container l\u1EA1nh (Reefer Monitoring)",supplier:"C\u1EA3ng Qu\u1ED1c T\u1EBF L\u1EA1ch Huy\u1EC7n",inv_no:"LH-REEFER-11",est:500,act:450,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"},{type:"V\u1EADn chuy\u1EC3n xe l\u1EA1nh n\u1ED9i \u0111\u1ECBa (Reefer Trucking)",supplier:"Vinalines Cold Chain",inv_no:"VNL-COLD-88",est:1300,act:1300,status:"\u0110\xE3 \u0110\u1ED1i So\xE1t"}],items_to_allocate:[{item_code:"SEAFOOD-SALMON-NOR",name:"Fresh Norwegian Salmon Fillet",qty:4e3,unit_price:15,weight:1,volume:.0016},{item_code:"SEAFOOD-COD-ATL",name:"Atlantic Cod Fillet Frozen",qty:2e3,unit_price:12,weight:1,volume:.0015}],audit_checks:[{title:"Tr\xF9ng L\u1EB7p H\xF3a \u0110\u01A1n (Duplicate Check)",status:"H\u1EE3p l\u1EC7",status_class:"delay-tag-ontime",border:"#10b981",desc:"Kh\xF4ng ph\xE1t hi\u1EC7n tr\xF9ng s\u1ED1 h\xF3a \u0111\u01A1n."},{title:"Chi Ph\xED Tr\u1ECDng Y\u1EBFu (Missing Cost Check)",status:"\u0110\u1EA7y \u0111\u1EE7",status_class:"delay-tag-ontime",border:"#10b981",desc:"\u0110\u1EA7y \u0111\u1EE7 ph\xED c\u1EAFm \u0111i\u1EC7n kho l\u1EA1nh v\xE0 ki\u1EC3m d\u1ECBch th\xFA y."},{title:"G\xE1n \u0110\xFAng V\u1EE5 Vi\u1EC7c (Association Check)",status:"Kh\u1EDBp 100%",status_class:"delay-tag-ontime",border:"#10b981",desc:"Ch\u1EE9ng t\u1EEB L\u1EA1ch Huy\u1EC7n kh\u1EDBp 100% h\u1ED3 s\u01A1 h\u1EA3i quan."}]}}}load_data(e){this.currentCaseId=e||"IMP-2026-001",$("#tcd-case-selector").val(this.currentCaseId),this.render_dashboard()}bind_events(){let e=this;$(document).on("change","#tcd-case-selector",function(){e.load_data($(this).val())}),$(document).on("click",".tcd-type-btn",function(){$(".tcd-type-btn").removeClass("active"),$(this).addClass("active"),e.currentCaseType=$(this).data("type"),e.apply_type_filter()}),$(document).on("click",".tcd-alloc-btn",function(){$(".tcd-alloc-btn").removeClass("active"),$(this).addClass("active"),e.currentRule=$(this).data("rule"),e.render_allocation_table()}),$(document).on("click","#tcd-btn-refresh",function(){let t=$(this).find("i");t.addClass("fa-spin"),setTimeout(()=>{e.load_data(e.currentCaseId),t.removeClass("fa-spin"),frappe.show_alert({message:__("\u0110\xE3 l\xE0m m\u1EDBi d\u1EEF li\u1EC7u Trade Cost!"),indicator:"green"})},300)}),$(document).on("click","#tcd-btn-new-sheet",function(){typeof frappe!="undefined"&&frappe.new_doc&&frappe.new_doc("Trade Cost Sheet",{trade_case:e.currentCaseId})}),$(document).on("click","#tcd-btn-sync-lcv, #tcd-btn-apply-lcv",function(){frappe.show_alert({message:__("\u0110ang ti\u1EBFn h\xE0nh \u0111\u1ED3ng b\u1ED9 d\u1EEF li\u1EC7u sang Landed Cost Voucher..."),indicator:"green"}),setTimeout(()=>{frappe.show_alert({message:__("\u0110\u1ED3ng b\u1ED9 Landed Cost Voucher th\xE0nh c\xF4ng!"),indicator:"green"})},600)})}apply_type_filter(){let e=this.currentCaseType;e==="export"?($("#tcd-case-selector").val("EXP-2026-002"),this.load_data("EXP-2026-002")):e==="import"?($("#tcd-case-selector").val("IMP-2026-001"),this.load_data("IMP-2026-001")):this.load_data(this.currentCaseId)}render_dashboard(){let e=this.caseData[this.currentCaseId]||this.caseData["IMP-2026-001"];if(!e)return;$("#tcd-kpi-po-val").text("$"+e.po_value.toLocaleString("en-US",{minimumFractionDigits:2})),$("#tcd-kpi-est-val").text("$"+e.estimated_cost.toLocaleString("en-US",{minimumFractionDigits:2})),$("#tcd-kpi-act-val").text("$"+e.actual_cost.toLocaleString("en-US",{minimumFractionDigits:2}));let t=e.variance_amount>0?"+":"",i=e.variance_pct>0?"+":"",n=`${t}$${e.variance_amount.toLocaleString("en-US",{minimumFractionDigits:2})} (${i}${e.variance_pct}%)`;$("#tcd-kpi-var-val").text(n),e.variance_amount>0?$("#tcd-kpi-var-val").css("color","#dc2626"):e.variance_amount<0?$("#tcd-kpi-var-val").css("color","#059669"):$("#tcd-kpi-var-val").css("color","#64748b"),$("#tcd-status-badge").attr("class","badge-status "+(e.status_class||"badge-in-transit")).text(e.status),$("#tcd-lcv-badge").text(e.lcv_id||"Ch\u01B0a li\xEAn k\u1EBFt"),this.render_cost_items(e.cost_items||[]),this.render_allocation_table(),this.render_audit_checks(e.audit_checks||[]),e.case_type==="export"?$("#tcd-export-profitability-box").show():$("#tcd-export-profitability-box").hide()}render_cost_items(e){let t="";e.forEach(i=>{let n=i.act-i.est,a=n>0?"+":"",c=n>0?"tcd-var-positive":n<0?"tcd-var-negative":"tcd-var-zero";t+=`
                <tr>
                    <td style="font-weight: 600; color: #0f172a;">${i.type}</td>
                    <td style="color: #475569;">${i.supplier}</td>
                    <td><code>${i.inv_no}</code></td>
                    <td class="text-right" style="color: #64748b;">$${i.est.toLocaleString("en-US",{minimumFractionDigits:2})}</td>
                    <td class="text-right" style="font-weight: 600; color: #0f172a;">$${i.act.toLocaleString("en-US",{minimumFractionDigits:2})}</td>
                    <td class="text-right ${c}">${a}$${n.toLocaleString("en-US",{minimumFractionDigits:2})}</td>
                    <td class="text-center">
                        <span class="delay-tag-ontime" style="font-size: 11px;">${i.status}</span>
                    </td>
                </tr>
            `}),$("#tcd-cost-items-tbody").html(t)}render_allocation_table(){let e=this.caseData[this.currentCaseId]||this.caseData["IMP-2026-001"];if(!e||!e.items_to_allocate)return;let t=e.actual_cost,i=this.calculate_allocation(e.items_to_allocate,t,this.currentRule),n="";i.forEach(a=>{n+=`
                <tr>
                    <td style="font-weight: 700; color: #0284c7;">${a.item_code}</td>
                    <td style="color: #334155;">${a.name}</td>
                    <td class="text-center" style="font-weight: 600;">${a.qty.toLocaleString()}</td>
                    <td class="text-right">$${a.unit_price.toFixed(2)}</td>
                    <td class="text-right" style="color: #0284c7; font-weight: 600;">+$${a.allocated_cost.toFixed(2)}</td>
                    <td class="text-right" style="font-weight: 700; color: #059669;">$${a.landed_unit_cost.toFixed(2)}</td>
                    <td class="text-center" style="color: #d97706; font-weight: 600;">+${a.pct_increase}%</td>
                </tr>
            `}),$("#tcd-allocation-tbody").html(n)}calculate_allocation(e,t,i){let n=[];i==="weight"?n=e.map(o=>o.weight*o.qty):i==="value"?n=e.map(o=>o.unit_price*o.qty):i==="qty"?n=e.map(o=>o.qty):i==="volume"&&(n=e.map(o=>o.volume*o.qty));let a=n.reduce((o,l)=>o+l,0)||1,c=[],d=0;for(let o=0;o<e.length;o++){let l=n[o]/a*t,r=Math.round(l*100)/100;c.push(r),d+=r}let s=Math.round((t-d)*100)/100;if(Math.abs(s)>1e-4&&c.length>0){let o=0;for(let l=1;l<c.length;l++)c[l]>c[o]&&(o=l);c[o]=Math.round((c[o]+s)*100)/100}return e.map((o,l)=>{let r=c[l],h=Math.round((o.unit_price+r/o.qty)*100)/100,p=o.unit_price*o.qty,b=p>0?(r/p*100).toFixed(1):0;return J(W({},o),{allocated_cost:r,landed_unit_cost:h,pct_increase:b})})}render_audit_checks(e){let t="";e.forEach(i=>{t+=`
                <div class="hub-exception-card" style="border-left: 4px solid ${i.border||"#10b981"};">
                    <div class="exception-card-header">
                        <span class="exception-title" style="color: #0f172a; font-weight: 600;">${i.title}</span>
                        <span class="${i.status_class||"delay-tag-ontime"}">${i.status}</span>
                    </div>
                    <div class="exception-card-body">${i.desc}</div>
                </div>
            `}),$("#tcd-audit-list").html(t)}},B=class{constructor(e){this.wrapper=e,this.currentCaseId="IMP-2026-001"}init(){this.bind_events()}on_tab_shown(e){e&&e.case_id&&(this.currentCaseId=e.case_id,$("#copilot-context-case").val(this.currentCaseId)),$("#copilot-input-textarea").focus()}bind_events(){let e=this;$(document).on("change","#copilot-context-case",function(){e.currentCaseId=$(this).val()}),$(document).on("click",".lw-suggestion-pill",function(){let t=$(this).data("prompt")||$(this).text().trim();$("#copilot-input-textarea").val(t),e.send_message(t)}),$(document).on("click","#copilot-btn-send",function(){let t=$("#copilot-input-textarea").val().trim();t&&e.send_message(t)}),$(document).on("keydown","#copilot-input-textarea",function(t){if(t.key==="Enter"&&!t.shiftKey){t.preventDefault();let i=$(this).val().trim();i&&e.send_message(i)}}),$(document).on("click","#copilot-btn-new-chat",function(){$("#copilot-chat-history").empty(),$(".lw-copilot-welcome-box").show(),$("#copilot-input-textarea").val("").focus()}),$(document).on("click","#copilot-btn-clear",function(){$("#copilot-chat-history").empty(),$(".lw-copilot-welcome-box").show()}),$(document).on("click",".lw-session-item",function(){$(".lw-session-item").removeClass("active"),$(this).addClass("active");let t=$(this).find(".lw-session-title").text().trim();e.load_session_sample(t)}),$(document).on("input","#copilot-session-search",function(){let t=$(this).val().toLowerCase().trim();$(".lw-session-item").each(function(){let i=$(this).find(".lw-session-title").text().toLowerCase();$(this).toggle(i.includes(t))})}),$(document).on("click",".lw-thinking-header",function(){$(this).next(".lw-thinking-content").slideToggle(180),$(this).find(".fa-chevron-down, .fa-chevron-up").toggleClass("fa-chevron-down fa-chevron-up")}),$(document).on("click",".btn-copilot-copy",function(){let t=$(this).closest(".lw-chat-bubble").find(".lw-chat-text").text();navigator.clipboard&&(navigator.clipboard.writeText(t),frappe.show_alert({message:__("\u0110\xE3 sao ch\xE9p ph\u1EA3n h\u1ED3i v\xE0o clipboard!"),indicator:"green"}))}),$(document).on("click",".btn-copilot-view-cost",function(){typeof frappe!="undefined"&&frappe.set_route?frappe.set_route("trade-cost-dashboard"):e.wrapper&&e.wrapper.unifiedHub&&e.wrapper.unifiedHub.switch_tab("cost",{case_id:e.currentCaseId})}),$(document).on("click",".btn-copilot-view-tracking",function(){typeof frappe!="undefined"&&frappe.set_route?frappe.set_route("shipment-tracking-hub"):e.wrapper&&e.wrapper.unifiedHub&&e.wrapper.unifiedHub.switch_tab("tracking")})}send_message(e){$(".lw-copilot-welcome-box").hide(),$("#copilot-input-textarea").val("");let t=`
            <div class="lw-chat-message lw-chat-user">
                <div class="lw-chat-avatar"><i class="fa fa-user"></i></div>
                <div class="lw-chat-bubble">
                    <div class="lw-chat-text">${frappe.utils.escape_html(e)}</div>
                </div>
            </div>
        `;$("#copilot-chat-history").append(t),this.scroll_to_bottom();let i=this,n="ai-msg-"+Date.now(),a=`
            <div class="lw-chat-message lw-chat-assistant" id="${n}">
                <div class="lw-chat-avatar"><i class="fa fa-bolt"></i></div>
                <div class="lw-chat-bubble">
                    <div class="lw-thinking-block">
                        <div class="lw-thinking-header">
                            <i class="fa fa-cog fa-spin" style="color: #0284c7;"></i>
                            <span>AI \u0111ang suy lu\u1EADn & truy xu\u1EA5t d\u1EEF li\u1EC7u Trade Case...</span>
                            <i class="fa fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                        </div>
                        <div class="lw-thinking-content">
                            \u2022 \u0110ang k\u1EBFt n\u1ED1i h\u1ED3 s\u01A1 Trade Case ${i.currentCaseId}<br>
                            \u2022 Ki\u1EC3m tra d\u1EEF li\u1EC7u b\u1EA3ng k\xEA 11 kho\u1EA3n chi ph\xED v\xE0 h\xE0nh tr\xECnh t\xE0u...
                        </div>
                    </div>
                    <div class="lw-chat-text" style="color: #64748b;"><i class="fa fa-circle-o-notch fa-spin"></i> \u0110ang chu\u1EA9n b\u1ECB c\xE2u tr\u1EA3 l\u1EDDi chuy\xEAn m\xF4n...</div>
                </div>
            </div>
        `;$("#copilot-chat-history").append(a),i.scroll_to_bottom(),setTimeout(()=>{i.generate_response(n,e)},500)}generate_response(e,t){let i=this.currentCaseId||"IMP-2026-001",n="",a="",c=t.toLowerCase();c.includes("ch\xEAnh l\u1EC7ch")||c.includes("chi ph\xED")||c.includes("sai l\u1EC7ch")?(a=`1. Truy v\u1EA5n Trade Cost Sheet li\xEAn k\u1EBFt Trade Case ${i}.
2. Ph\xE1t hi\u1EC7n: Chi ph\xED d\u1EF1 to\xE1n (Estimated) = $16,800.00, Th\u1EF1c t\u1EBF (Actual) = $18,350.00.
3. Ch\xEAnh l\u1EC7ch v\u01B0\u1EE3t: +$1,550.00 (+9.2%).
4. Nguy\xEAn nh\xE2n ch\xEDnh:
   - C\u01B0\u1EDBc bi\u1EC3n Maersk Line t\u0103ng ph\u1EE5 ph\xED x\u0103ng d\u1EA7u BAF: +$700.00
   - Ph\xED l\u01B0u b\xE3i Demurrage ngo\xE0i d\u1EF1 ki\u1EBFn: +$320.00
   - Ph\xED trucking n\xE2ng h\u1EA1 T\xE2n C\u1EA3ng: +$150.00`,n=`
<p>D\u1EF1a tr\xEAn h\u1ED3 s\u01A1 t\xE0i ch\xEDnh c\u1EE7a v\u1EE5 vi\u1EC7c <strong>${i}</strong>, t\xF4i \u0111\xE3 ho\xE0n t\u1EA5t ph\xE2n t\xEDch \u0111\u1ED1i so\xE1t chi ph\xED:</p>
<ul>
    <li><strong>T\u1ED5ng chi ph\xED th\u1EF1c t\u1EBF:</strong> <code>$18,350.00 USD</code> so v\u1EDBi d\u1EF1 to\xE1n ban \u0111\u1EA7u <code>$16,800.00 USD</code> (V\u01B0\u1EE3t <strong>+$1,550.00</strong>, t\u01B0\u01A1ng \u0111\u01B0\u01A1ng <strong>+9.2%</strong>).</li>
    <li><strong>Kho\u1EA3n ph\xE1t sinh l\u1EDBn nh\u1EA5t:</strong> C\u01B0\u1EDBc t\xE0u bi\u1EC3n Ocean Freight t\u0103ng do ph\u1EE5 ph\xED nhi\xEAn li\u1EC7u kh\u1EA9n c\u1EA5p (+$700 USD) v\xE0 ph\xED l\u01B0u b\xE3i container Demurrage (+$320 USD) do tr\u1EC5 th\u1EE7 t\u1EE5c c\u1EA3ng.</li>
    <li><strong>Khuy\u1EBFn ngh\u1ECB h\xE0nh \u0111\u1ED9ng:</strong>
        <br>1. L\xE0m vi\u1EC7c v\u1EDBi h\xE3ng t\xE0u Maersk \u0111\u1EC3 xin mi\u1EC5n gi\u1EA3m (Demurrage Waiver) 3 ng\xE0y l\u01B0u b\xE3i container.
        <br>2. C\u1EADp nh\u1EADt ph\xE2n b\u1ED5 Landed Cost theo ti\xEAu chu\u1EA9n <strong>Gross Weight</strong> \u0111\u1EC3 gi\xE1 v\u1ED1n t\u1EEBng Item ph\u1EA3n \xE1nh ch\xEDnh x\xE1c nh\u1EA5t chi ph\xED v\u1EADn chuy\u1EC3n.
    </li>
</ul>`):c.includes("l\u1ECBch t\xE0u")||c.includes("h\xE0nh tr\xECnh")||c.includes("\u0111\xE0 n\u1EB5ng")||c.includes("c\u1EADp c\u1EA3ng")||c.includes("eta")?(a=`1. Ki\u1EC3m tra Tracking Hub cho chuy\u1EBFn t\xE0u v\u1EADn chuy\u1EC3n h\u1ED3 s\u01A1 ${i}.
2. T\xE0u container: Maersk Mc-Kinney Moller.
3. Tr\u1EA1ng th\xE1i h\xE0nh tr\xECnh: \u0110ang tr\xEAn bi\u1EC3n (In-Transit), t\u1ECDa \u0111\u1ED9 15.82\xB0N, 109.45\xB0E.
4. D\u1EF1 ki\u1EBFn c\u1EADp c\u1EA3ng \u0110\xE0 N\u1EB5ng (ETA): Ng\xE0y mai l\xFAc 16:30.
5. C\u1EA3nh b\xE1o th\u1EDDi ti\u1EBFt: Bi\u1EC3n \u0111\u1ED9ng c\u1EA5p 5, c\xF3 kh\u1EA3 n\u0103ng ch\u1EADm tr\u1EC5 c\u1EADp c\u1EA7u 2-4 ti\u1EBFng.`,n=`
<p>Th\xF4ng tin h\xE0nh tr\xECnh v\xE0 d\u1EF1 b\xE1o c\u1EA3ng \u0111\u1EBFn cho v\u1EE5 vi\u1EC7c <strong>${i}</strong>:</p>
<ul>
    <li><strong>T\xE0u chuy\xEAn ch\u1EDF:</strong> <code>Maersk Mc-Kinney Moller</code> (Chuy\u1EBFn h\u1EA3i tr\xECnh 2603W).</li>
    <li><strong>V\u1ECB tr\xED hi\u1EC7n t\u1EA1i:</strong> V\xF9ng bi\u1EC3n mi\u1EC1n Trung, c\xE1ch phao s\u1ED1 0 C\u1EA3ng Ti\xEAn Sa - \u0110\xE0 N\u1EB5ng x\u1EA5p x\u1EC9 48 h\u1EA3i l\xFD.</li>
    <li><strong>ETA c\u1EADp c\u1EA3ng:</strong> D\u1EF1 ki\u1EBFn <strong>16:30 ng\xE0y mai</strong> (Sai l\u1EC7ch d\u1EF1 b\xE1o: +3.5 ti\u1EBFng do gi\xF3 m\xF9a).</li>
    <li><strong>Khuy\u1EBFn ngh\u1ECB th\u1EE7 t\u1EE5c:</strong> B\u1ED9 ch\u1EE9ng t\u1EEB h\u1EA3i quan (B/L g\u1ED1c, Invoice, Packing List, C/O Form E) \u0111\xE3 s\u1EB5n s\xE0ng tr\xEAn h\u1EC7 th\u1ED1ng. \u0110\u1EA1i l\xFD giao nh\u1EADn n\xEAn \u0111\u0103ng k\xFD tr\u01B0\u1EDBc l\u1EC7nh giao h\xE0ng \u0111i\u1EC7n t\u1EED (eDO) tr\xEAn c\u1ED5ng th\xF4ng tin c\u1EA3ng \u0110\xE0 N\u1EB5ng.</li>
</ul>`):(a=`1. Ti\u1EBFp nh\u1EADn c\xE2u h\u1ECFi nghi\u1EC7p v\u1EE5 logistics: "${t}".
2. \xC1p d\u1EE5ng quy t\u1EAFc ph\xE2n b\u1ED5 gi\xE1 v\u1ED1n chu\u1EA9n Landed Cost Voucher c\u1EE7a ERPNext.
3. T\u1ED5ng h\u1EE3p khuy\u1EBFn ngh\u1ECB t\u1ED1i \u01B0u chi ph\xED v\xE0 \u0111i\u1EC1u h\xE0nh ngo\u1EA1i th\u01B0\u01A1ng.`,n=`
<p>\u0110\u1ED1i v\u1EDBi c\xE2u h\u1ECFi c\u1EE7a b\u1EA1n v\u1EC1 <strong>${i}</strong>:</p>
<p>H\u1EC7 th\u1ED1ng Logistics Wizard \u0111\xE3 t\u1EF1 \u0111\u1ED9ng li\xEAn k\u1EBFt d\u1EEF li\u1EC7u gi\u1EEFa H\u1EE3p \u0111\u1ED3ng th\u01B0\u01A1ng m\u1EA1i, H\xE0nh tr\xECnh v\u1EADn chuy\u1EC3n th\u1EF1c t\u1EBF v\xE0 Ph\xE2n b\u1ED5 gi\xE1 v\u1ED1n Landed Cost:</p>
<ul>
    <li>M\u1ECDi chi ph\xED h\u1EE3p l\u1EC7 (11 lo\u1EA1i chi ph\xED ti\xEAu chu\u1EA9n) \u0111\xE3 \u0111\u01B0\u1EE3c ki\u1EC3m tra t\xEDnh to\xE0n v\u1EB9n (kh\xF4ng tr\xF9ng h\xF3a \u0111\u01A1n, c\xF3 s\u1ED1 PO h\u1EE3p l\u1EC7).</li>
    <li>Thu\u1EADt to\xE1n ph\xE2n b\u1ED5 t\u1EF1 \u0111\u1ED9ng lo\u1EA1i b\u1ECF sai s\u1ED1 l\xE0m tr\xF2n (discrepancy &le; 0.01) tr\u01B0\u1EDBc khi \u0111\u1ED3ng b\u1ED9 sang <strong>ERPNext Landed Cost Voucher</strong>.</li>
</ul>
<p>B\u1EA1n c\xF3 th\u1EC3 chuy\u1EC3n sang tab <strong>Trade Cost Dashboard</strong> ho\u1EB7c <strong>Shipment Tracking Hub</strong> \u1EDF thanh \u0111i\u1EC1u h\u01B0\u1EDBng b\xEAn tr\xE1i \u0111\u1EC3 theo d\xF5i chi ti\u1EBFt t\u1EE9c th\xEC.</p>`);let d=`
            <div class="lw-thinking-block">
                <div class="lw-thinking-header">
                    <i class="fa fa-lightbulb-o" style="color: #0284c7;"></i>
                    <span>Ti\u1EBFn tr\xECnh suy lu\u1EADn & \u0111\u1ED1i so\xE1t d\u1EEF li\u1EC7u (Ho\xE0n t\u1EA5t)</span>
                    <i class="fa fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                </div>
                <div class="lw-thinking-content" style="display: none;">
                    <pre style="margin: 0; background: transparent; border: none; font-size: 11.5px; color: #475569; padding: 0;">${a}</pre>
                </div>
            </div>
            <div class="lw-chat-text">${n}</div>
            <div class="lw-chat-actions">
                <button class="lw-chat-action-btn btn-copilot-copy"><i class="fa fa-copy"></i> Sao ch\xE9p</button>
                <button class="lw-chat-action-btn btn-copilot-view-cost"><i class="fa fa-calculator"></i> B\u1EA3ng chi ph\xED Landed Cost</button>
                <button class="lw-chat-action-btn btn-copilot-view-tracking"><i class="fa fa-ship"></i> Tra c\u1EE9u h\xE0nh tr\xECnh</button>
            </div>
        `;$(`#${e} .lw-chat-bubble`).html(d),this.scroll_to_bottom()}scroll_to_bottom(){let e=$("#copilot-messages-thread");e.length&&e.scrollTop(e[0].scrollHeight)}load_session_sample(e){$("#copilot-chat-history").empty(),$(".lw-copilot-welcome-box").hide(),this.send_message(e)}};typeof window!="undefined"&&(window.ShipmentTrackingHub=O,window.TradeCaseOverviewController=N,window.UnifiedLogisticsHub=P,window.EmbeddedTradeCostDashboardController=R,window.EmbeddedLogisticsAICopilot=B,window.init_logistics_hub_page=U,window.show_logistics_hub_page=G,window.register_logistics_hub_page=Y);typeof global!="undefined"&&(global.ShipmentTrackingHub=O,global.TradeCaseOverviewController=N,global.UnifiedLogisticsHub=P,global.EmbeddedTradeCostDashboardController=R,global.EmbeddedLogisticsAICopilot=B,global.init_logistics_hub_page=U,global.show_logistics_hub_page=G,global.register_logistics_hub_page=Y);})();
//# sourceMappingURL=unified_logistics_hub.bundle.OSIPOVB4.js.map
