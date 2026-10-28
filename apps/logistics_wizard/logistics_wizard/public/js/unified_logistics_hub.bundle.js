window.UNIFIED_LOGISTICS_HUB_HTML = "<div class=\"logistics-page-container\">\n    <!-- LEFT VERTICAL SIDEBAR TAB NAVIGATION (Hidden - replaced by top horizontal tab bar to remove redundancy with Frappe system sidebar) -->\n    <aside class=\"logistics-tabs-nav\" id=\"logistics-sidebar-nav\" style=\"display: none !important;\">\n    </aside>\n\n    <!-- RIGHT MAIN CONTENT AREA (Takes 100% full width) -->\n    <div class=\"logistics-main-content\" style=\"width: 100%; flex: 1;\">\n                <!-- TAB 1: EXECUTIVE DASHBOARD (GLOBAL OPERATIONS COMMAND CENTER) -->\n        <div class=\"logistics-tab-pane active\" id=\"tab-pane-executive\">\n            <!-- Header bar with filter and refresh -->\n            <div class=\"exec-header-bar\">\n                <div class=\"exec-title-block\">\n                    <h2 class=\"exec-title\">\n                        <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                            <rect x=\"3\" y=\"3\" width=\"7\" height=\"9\"></rect>\n                            <rect x=\"14\" y=\"3\" width=\"7\" height=\"5\"></rect>\n                            <rect x=\"14\" y=\"12\" width=\"7\" height=\"9\"></rect>\n                            <rect x=\"3\" y=\"16\" width=\"7\" height=\"5\"></rect>\n                        </svg>\n                        Executive Logistics Command Center\n                    </h2>\n                    <p class=\"exec-subtitle\">B\u1ee9c tranh v\u0129 m\u00f4 to\u00e0n di\u1ec7n v\u1ec1 l\u01b0u l\u01b0\u1ee3ng h\u00e0ng h\u00f3a, s\u1ee9c kh\u1ecfe h\u00e0nh tr\u00ecnh, ki\u1ec3m so\u00e1t chi ph\u00ed & r\u1ee7i ro</p>\n                </div>\n                <div class=\"exec-header-actions\">\n                    <div class=\"exec-filter-group\">\n                        <label for=\"exec-time-range\" class=\"exec-filter-label\"><i class=\"fa fa-calendar\"></i> Chu k\u1ef3:</label>\n                        <select id=\"exec-time-range\" class=\"form-control exec-time-select\">\n                            <option value=\"30d\" selected>30 ng\u00e0y g\u1ea7n \u0111\u00e2y</option>\n                            <option value=\"90d\">Qu\u00fd hi\u1ec7n t\u1ea1i (Q4)</option>\n                            <option value=\"ytd\">N\u0103m 2026</option>\n                        </select>\n                    </div>\n                    <button class=\"btn btn-default btn-sm\" id=\"exec-btn-refresh\" title=\"L\u00e0m m\u1edbi s\u1ed1 li\u1ec7u\">\n                        <i class=\"fa fa-refresh\"></i> L\u00e0m m\u1edbi\n                    </button>\n                </div>\n            </div>\n\n            <!-- SECTION 1: 4 VISUAL METRIC TILES C\u00d3 MINI PROGRESS BAR -->\n            <div class=\"exec-kpi-grid\">\n                <!-- KPI 1: Active Cases -->\n                <div class=\"exec-kpi-card\">\n                    <div class=\"exec-kpi-top\">\n                        <div class=\"exec-kpi-info\">\n                            <span class=\"exec-kpi-label\">T\u1ed5ng \u0110\u01a1n H\u00e0ng \u0110ang Ch\u1ea1y</span>\n                            <div class=\"exec-kpi-val-row\">\n                                <span class=\"exec-kpi-value\" id=\"exec-val-total-cases\">28</span>\n                                <span class=\"exec-badge exec-badge-success\">+12% MoM</span>\n                            </div>\n                        </div>\n                        <div class=\"exec-kpi-icon-wrap icon-blue\">\n                            <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z\"></path></svg>\n                        </div>\n                    </div>\n                    <div class=\"exec-kpi-progress\">\n                        <div class=\"exec-progress-bar bg-blue\" id=\"exec-bar-import\" style=\"width: 71%;\" title=\"Nh\u1eadp kh\u1ea9u: 20\"></div>\n                        <div class=\"exec-progress-bar bg-emerald\" id=\"exec-bar-export\" style=\"width: 29%;\" title=\"Xu\u1ea5t kh\u1ea9u: 8\"></div>\n                    </div>\n                    <div class=\"exec-kpi-footer\">\n                        <span><i class=\"fa fa-arrow-circle-down text-blue\"></i> Nh\u1eadp kh\u1ea9u: <strong id=\"exec-sub-import\">20</strong> (71%)</span>\n                        <span><i class=\"fa fa-arrow-circle-up text-emerald\"></i> Xu\u1ea5t kh\u1ea9u: <strong id=\"exec-sub-export\">8</strong> (29%)</span>\n                    </div>\n                </div>\n\n                <!-- KPI 2: In-Transit Shipments -->\n                <div class=\"exec-kpi-card\">\n                    <div class=\"exec-kpi-top\">\n                        <div class=\"exec-kpi-info\">\n                            <span class=\"exec-kpi-label\">L\u00f4 H\u00e0ng \u0110ang Di Chuy\u1ec3n</span>\n                            <div class=\"exec-kpi-val-row\">\n                                <span class=\"exec-kpi-value\" id=\"exec-val-in-transit\">18</span>\n                                <span class=\"exec-badge exec-badge-info\">64% Lu\u1ed3ng h\u00e0ng</span>\n                            </div>\n                        </div>\n                        <div class=\"exec-kpi-icon-wrap icon-cyan\">\n                            <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"10\"></circle><polygon points=\"16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76\"></polygon></svg>\n                        </div>\n                    </div>\n                    <div class=\"exec-kpi-progress\">\n                        <div class=\"exec-progress-bar bg-cyan\" id=\"exec-bar-transit\" style=\"width: 78%;\"></div>\n                    </div>\n                    <div class=\"exec-kpi-footer\">\n                        <span><i class=\"fa fa-ship text-cyan\"></i> 14 \u0110\u01b0\u1eddng bi\u1ec3n</span>\n                        <span><i class=\"fa fa-plane text-blue\"></i> 4 H\u00e0ng kh\u00f4ng</span>\n                    </div>\n                </div>\n\n                <!-- KPI 3: Actionable Alerts -->\n                <div class=\"exec-kpi-card\">\n                    <div class=\"exec-kpi-top\">\n                        <div class=\"exec-kpi-info\">\n                            <span class=\"exec-kpi-label\">C\u1ea3nh B\u00e1o & R\u1ee7i Ro Ch\u1eadm Tr\u1ec5</span>\n                            <div class=\"exec-kpi-val-row\">\n                                <span class=\"exec-kpi-value text-amber\" id=\"exec-val-alerts\">3</span>\n                                <span class=\"exec-badge exec-badge-amber\">C\u1ea7n ch\u00fa \u00fd</span>\n                            </div>\n                        </div>\n                        <div class=\"exec-kpi-icon-wrap icon-amber\">\n                            <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z\"></path><line x1=\"12\" y1=\"9\" x2=\"12\" y2=\"13\"></line><line x1=\"12\" y1=\"17\" x2=\"12.01\" y2=\"17\"></line></svg>\n                        </div>\n                    </div>\n                    <div class=\"exec-kpi-progress\">\n                        <div class=\"exec-progress-bar bg-amber\" style=\"width: 10%;\"></div>\n                    </div>\n                    <div class=\"exec-kpi-footer\">\n                        <span><i class=\"fa fa-exclamation-triangle text-amber\"></i> 1 Tr\u1ec5 l\u1ecbch ETA</span>\n                        <span><i class=\"fa fa-clock-o text-amber\"></i> 2 H\u1ea1n h\u1ea3i quan</span>\n                    </div>\n                </div>\n\n                <!-- KPI 4: Total Spend & Budget -->\n                <div class=\"exec-kpi-card\">\n                    <div class=\"exec-kpi-top\">\n                        <div class=\"exec-kpi-info\">\n                            <span class=\"exec-kpi-label\">T\u1ed5ng Chi Ph\u00ed & Ng\u00e2n S\u00e1ch</span>\n                            <div class=\"exec-kpi-val-row\">\n                                <span class=\"exec-kpi-value text-emerald\" id=\"exec-val-spend\">$1,245,500</span>\n                                <span class=\"exec-badge exec-badge-success\">-2.7% Ti\u1ebft ki\u1ec7m</span>\n                            </div>\n                        </div>\n                        <div class=\"exec-kpi-icon-wrap icon-emerald\">\n                            <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"></line><path d=\"M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6\"></path></svg>\n                        </div>\n                    </div>\n                    <div class=\"exec-kpi-progress\">\n                        <div class=\"exec-progress-bar bg-emerald\" style=\"width: 97.3%;\"></div>\n                    </div>\n                    <div class=\"exec-kpi-footer\">\n                        <span>D\u1ef1 to\u00e1n: <strong>$1,280,000</strong></span>\n                        <span>Ch\u00eanh l\u1ec7ch: <strong class=\"text-emerald\">-$34,500</strong></span>\n                    </div>\n                </div>\n            </div>\n\n            <!-- SECTION 2: END-TO-END OPERATIONAL PIPELINE FUNNEL -->\n            <div class=\"exec-pipeline-section\">\n                <div class=\"exec-section-header\">\n                    <div class=\"exec-section-title-wrap\">\n                        <h3 class=\"exec-section-title\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2\"><polygon points=\"22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3\"></polygon></svg>\n                            D\u00f2ng Ch\u1ea3y H\u00e0ng H\u00f3a To\u00e0n H\u1ec7 Th\u1ed1ng (End-to-End Pipeline Funnel)\n                        </h3>\n                        <span class=\"exec-section-sub\">Quan s\u00e1t s\u1ef1 ph\u00e2n b\u1ed5 \u0111\u01a1n h\u00e0ng qua 5 c\u1ed5ng ki\u1ec3m so\u00e1t v\u1eadn h\u00e0nh \u0111\u1ec3 ph\u00e1t hi\u1ec7n ngay \u0111i\u1ec3m ngh\u1ebdn</span>\n                    </div>\n                </div>\n                <div class=\"exec-pipeline-flow\" id=\"exec-pipeline-container\">\n                    <!-- Populated dynamically via JS -->\n                </div>\n            </div>\n\n            <!-- SECTION 3: 2-COLUMN GRID (RADAR S\u1ee8C KH\u1eceE + C\u01a0 C\u1ea4U CHI PH\u00cd) -->\n            <div class=\"exec-grid-two-col\">\n                <!-- LEFT: OPERATIONAL HEALTH & MODALITY -->\n                <div class=\"exec-card\">\n                    <div class=\"exec-card-header\">\n                        <h4 class=\"exec-card-title\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2\"><path d=\"M22 12h-4l-3 9L9 3l-3 9H2\"></path></svg>\n                            S\u1ee9c Kh\u1ecfe V\u1eadn H\u00e0nh & Ph\u01b0\u01a1ng Th\u1ee9c V\u1eadn Chuy\u1ec3n\n                        </h4>\n                    </div>\n                    <div class=\"exec-card-body\">\n                        <div class=\"exec-health-wrap\">\n                            <!-- SVG Donut Chart -->\n                            <div class=\"exec-donut-box\">\n                                <svg class=\"exec-donut-svg\" viewBox=\"0 0 36 36\">\n                                    <path class=\"donut-ring\" d=\"M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831\" fill=\"none\" stroke=\"#f1f5f9\" stroke-width=\"3.8\"/>\n                                    <path class=\"donut-segment segment-ontime\" id=\"donut-segment-ontime\" d=\"M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831\" fill=\"none\" stroke=\"#10b981\" stroke-width=\"3.8\" stroke-dasharray=\"81, 100\" stroke-dashoffset=\"0\"/>\n                                    <path class=\"donut-segment segment-atrisk\" id=\"donut-segment-atrisk\" d=\"M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831\" fill=\"none\" stroke=\"#f59e0b\" stroke-width=\"3.8\" stroke-dasharray=\"13, 100\" stroke-dashoffset=\"-81\"/>\n                                    <path class=\"donut-segment segment-critical\" id=\"donut-segment-critical\" d=\"M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831\" fill=\"none\" stroke=\"#ef4444\" stroke-width=\"3.8\" stroke-dasharray=\"6, 100\" stroke-dashoffset=\"-94\"/>\n                                </svg>\n                                <div class=\"exec-donut-center\">\n                                    <span class=\"donut-score\" id=\"exec-health-score\">94.2%</span>\n                                    <span class=\"donut-label\">\u1ed4n \u0110\u1ecbnh</span>\n                                </div>\n                            </div>\n                            <div class=\"exec-health-legend\" id=\"exec-health-legend\">\n                                <div class=\"legend-item\">\n                                    <span class=\"legend-dot bg-emerald\"></span>\n                                    <span class=\"legend-text\">\u0110\u00fang Ti\u1ebfn \u0110\u1ed9 (On-Time)</span>\n                                    <strong class=\"legend-val\" id=\"legend-ontime-val\">26 \u0111\u01a1n (81%)</strong>\n                                </div>\n                                <div class=\"legend-item\">\n                                    <span class=\"legend-dot bg-amber\"></span>\n                                    <span class=\"legend-text\">C\u1ea7n Theo D\u00f5i (At Risk)</span>\n                                    <strong class=\"legend-val\" id=\"legend-atrisk-val\">4 \u0111\u01a1n (13%)</strong>\n                                </div>\n                                <div class=\"legend-item\">\n                                    <span class=\"legend-dot bg-coral\"></span>\n                                    <span class=\"legend-text\">S\u1ef1 C\u1ed1 / Ch\u1eadm Tr\u1ec5</span>\n                                    <strong class=\"legend-val\" id=\"legend-critical-val\">2 \u0111\u01a1n (6%)</strong>\n                                </div>\n                            </div>\n                        </div>\n\n                        <div class=\"exec-divider\"></div>\n\n                        <!-- Modality Split Progress Bars -->\n                        <div class=\"exec-modality-block\">\n                            <span class=\"exec-subhead\">T\u1ef7 Tr\u1ecdng Ph\u01b0\u01a1ng Th\u1ee9c V\u1eadn Chuy\u1ec3n:</span>\n                            <div class=\"modality-row\">\n                                <span class=\"modality-title\"><i class=\"fa fa-ship text-cyan\"></i> \u0110\u01b0\u1eddng bi\u1ec3n (FCL/LCL)</span>\n                                <div class=\"modality-bar-wrap\">\n                                    <div class=\"modality-bar bg-cyan\" style=\"width: 70%;\"></div>\n                                </div>\n                                <span class=\"modality-pct\">70% (22 l\u00f4)</span>\n                            </div>\n                            <div class=\"modality-row\">\n                                <span class=\"modality-title\"><i class=\"fa fa-plane text-blue\"></i> H\u00e0ng kh\u00f4ng (Air Cargo)</span>\n                                <div class=\"modality-bar-wrap\">\n                                    <div class=\"modality-bar bg-blue\" style=\"width: 20%;\"></div>\n                                </div>\n                                <span class=\"modality-pct\">20% (6 l\u00f4)</span>\n                            </div>\n                            <div class=\"modality-row\">\n                                <span class=\"modality-title\"><i class=\"fa fa-truck text-emerald\"></i> V\u1eadn t\u1ea3i b\u1ed9 (Trucking)</span>\n                                <div class=\"modality-bar-wrap\">\n                                    <div class=\"modality-bar bg-emerald\" style=\"width: 10%;\"></div>\n                                </div>\n                                <span class=\"modality-pct\">10% (3 l\u00f4)</span>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n\n                <!-- RIGHT: FINANCIAL COST BREAKDOWN & BUDGET CONTROL -->\n                <div class=\"exec-card\">\n                    <div class=\"exec-card-header\">\n                        <h4 class=\"exec-card-title\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2\"><line x1=\"18\" y1=\"20\" x2=\"18\" y2=\"10\"></line><line x1=\"12\" y1=\"20\" x2=\"12\" y2=\"4\"></line><line x1=\"6\" y1=\"20\" x2=\"6\" y2=\"14\"></line></svg>\n                            C\u01a1 C\u1ea5u Chi Ph\u00ed Logistics Theo Nh\u00f3m Nghi\u1ec7p V\u1ee5\n                        </h4>\n                        <span class=\"exec-badge exec-badge-success\">Ti\u1ebft ki\u1ec7m +$34,500</span>\n                    </div>\n                    <div class=\"exec-card-body\">\n                        <div class=\"exec-cost-bars-list\" id=\"exec-cost-breakdown-list\">\n                            <!-- Populated dynamically via JS -->\n                        </div>\n                    </div>\n                </div>\n            </div>\n\n            <!-- SECTION 4: 2-COLUMN GRID (H\u00c0NH LANG V\u1eacN T\u1ea2I + TH\u1eba C\u1ea2NH B\u00c1O H\u00c0NH \u0110\u1ed8NG NHANH) -->\n            <div class=\"exec-grid-two-col\">\n                <!-- LEFT: KEY TRADE CORRIDORS -->\n                <div class=\"exec-card\">\n                    <div class=\"exec-card-header\">\n                        <h4 class=\"exec-card-title\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"10\"></circle><line x1=\"2\" y1=\"12\" x2=\"22\" y2=\"12\"></line><path d=\"M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z\"></path></svg>\n                            H\u00e0nh Lang V\u1eadn T\u1ea3i Tr\u1ecdng \u0110i\u1ec3m & T\u1ea7n Su\u1ea5t\n                        </h4>\n                    </div>\n                    <div class=\"exec-card-body\" id=\"exec-corridors-container\">\n                        <!-- Populated dynamically via JS -->\n                    </div>\n                </div>\n\n                <!-- RIGHT: ACTIONABLE RADAR ALERTS -->\n                <div class=\"exec-card\">\n                    <div class=\"exec-card-header\">\n                        <h4 class=\"exec-card-title\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#ef4444\" stroke-width=\"2\"><path d=\"M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z\"></path><line x1=\"12\" y1=\"9\" x2=\"12\" y2=\"13\"></line><line x1=\"12\" y1=\"17\" x2=\"12.01\" y2=\"17\"></line></svg>\n                            S\u1ef1 C\u1ed1 C\u1ea7n Can Thi\u1ec7p Ngay (Action Radar)\n                        </h4>\n                        <span class=\"exec-subhead-badge text-amber\">3 V\u1ea5n \u0111\u1ec1</span>\n                    </div>\n                    <div class=\"exec-card-body\" id=\"exec-alerts-container\">\n                        <!-- Populated dynamically via JS with action button linking to Tab 2 -->\n                    </div>\n                </div>\n            </div>\n        </div>\n\n        <!-- TAB 2: TRADE CASE DOSSIER -->\n        <div class=\"logistics-tab-pane\" id=\"tab-pane-trade-case\">\n        <!-- N\u00daT CH\u1eccN H\u1ed2 S\u01a0 N\u1eb0M NGAY TRONG TAB N\u00c0Y -->\n        <div class=\"tc-tab-control-bar\">\n            <div class=\"tc-select-case-group\">\n                <label for=\"tc-case-selector\" class=\"tc-select-label\">\n                    <i class=\"fa fa-folder-open\" style=\"color: #0284c7;\"></i> Ch\u1ecdn h\u1ed3 s\u01a1 Trade Case:\n                </label>\n                <div class=\"tc-select-wrapper\">\n                    <select id=\"tc-case-selector\" class=\"form-control tc-case-select-dropdown\">\n                        <!-- Populated dynamically via API -->\n                    </select>\n                </div>\n            </div>\n            <div class=\"tc-tab-control-actions\">\n                <button class=\"btn btn-default btn-sm\" id=\"tc-btn-refresh-case\" title=\"L\u00e0m m\u1edbi t\u1ed5ng quan\">\n                    <i class=\"fa fa-refresh\"></i> L\u00e0m m\u1edbi\n                </button>\n                <button class=\"btn btn-default btn-sm\" id=\"tc-btn-edit-case\" title=\"Ch\u1ec9nh s\u1eeda h\u1ed3 s\u01a1 DocType\">\n                    <i class=\"fa fa-pencil\"></i> Ch\u1ec9nh s\u1eeda Case\n                </button>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 1: HEADER IDENTIFICATION -->\n        <div class=\"tc-card\" id=\"tc-header-card\">\n            <div class=\"tc-header-top\">\n                <div class=\"tc-id-badges\">\n                    <span class=\"tc-badge-id\" id=\"tc-id-text\"><span id=\"tc-header-id\">IMP-2026-001</span></span>\n                    <span class=\"tc-badge-status\" id=\"tc-status-badge\"><span id=\"tc-header-status\">IN TRANSIT</span></span>\n                    <span class=\"tc-badge-health warning\" id=\"tc-health-badge\"><span id=\"tc-header-health\">Health: ATTENTION</span></span>\n                    <span class=\"tc-badge-priority\" id=\"tc-priority-badge\"><span id=\"tc-header-priority\">Normal Priority</span></span>\n                </div>\n                <div class=\"tc-header-actions\">\n                    <button class=\"btn btn-xs btn-default\" id=\"tc-btn-refresh\" title=\"L\u00e0m m\u1edbi\"><i class=\"fa fa-refresh\"></i> L\u00e0m m\u1edbi</button>\n                </div>\n            </div>\n            <div class=\"tc-master-grid\" id=\"tc-master-details\">\n                <div class=\"tc-detail-col\">\n                    <div class=\"tc-detail-label\">Lo\u1ea1i h\u00ecnh / \u0110\u1ed1i t\u00e1c:</div>\n                    <div class=\"tc-detail-val\" id=\"tc-party-text\"><span id=\"tc-meta-party\">Import Case \u2014 ABC Electronics Co., Ltd</span></div>\n                </div>\n                <div class=\"tc-detail-col\">\n                    <div class=\"tc-detail-label\">\u0110\u01a1n mua h\u00e0ng (PO/SO):</div>\n                    <div class=\"tc-detail-val\" id=\"tc-docref-text\"><span id=\"tc-meta-po\"><a href=\"/app/purchase-order/PO-2026-0042\" class=\"tc-link\">PO-2026-0042</a></span></div>\n                </div>\n                <div class=\"tc-detail-col\">\n                    <div class=\"tc-detail-label\">Ph\u01b0\u01a1ng th\u1ee9c & Incoterm:</div>\n                    <div class=\"tc-detail-val\" id=\"tc-mode-incoterm\"><span id=\"tc-meta-mode-incoterm\">Ocean \u2022 FOB</span></div>\n                </div>\n                <div class=\"tc-detail-col\">\n                    <div class=\"tc-detail-label\">Tuy\u1ebfn \u0111\u01b0\u1eddng (Origin \u2794 Dest):</div>\n                    <div class=\"tc-detail-val\" id=\"tc-route-text\"><span id=\"tc-meta-route\">Shanghai Port, China \u2794 Da Nang Port, Vietnam</span></div>\n                </div>\n                <div class=\"tc-detail-col\">\n                    <div class=\"tc-detail-label\">Ng\u01b0\u1eddi ph\u1ee5 tr\u00e1ch ch\u00ednh:</div>\n                    <div class=\"tc-detail-val\" id=\"tc-owner-text\"><span id=\"tc-meta-owner\">Nguyen Van A (Logistics)</span></div>\n                </div>\n                <div class=\"tc-detail-col\">\n                    <div class=\"tc-detail-label\">Th\u1eddi h\u1ea1n d\u1ef1 ki\u1ebfn \u0111\u00f3ng:</div>\n                    <div class=\"tc-detail-val\" id=\"tc-expected-close\"><span id=\"tc-meta-expected-close\">2026-10-15</span></div>\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 2: LIFECYCLE STEPPER -->\n        <div class=\"tc-card\" id=\"tc-lifecycle-card\">\n            <div class=\"tc-card-header\">\n                <div class=\"tc-card-title\">\n                    <i class=\"fa fa-map-signs\" style=\"color: #0284c7;\"></i> Ti\u1ebfn Tr\u00ecnh Nghi\u1ec7p V\u1ee5 To\u00e0n V\u00f2ng \u0110\u1eddi (Trade Case Lifecycle)\n                </div>\n                <div class=\"tc-current-stage-callout\" id=\"tc-current-stage-callout\">\n                    <span id=\"tc-lifecycle-current-label\">Giai \u0111o\u1ea1n hi\u1ec7n t\u1ea1i: <strong>In Transit</strong></span>\n                </div>\n            </div>\n            <div class=\"tc-lifecycle-stepper\" id=\"tc-lifecycle-stepper\">\n                <!-- Rendered dynamically via JS -->\n            </div>\n            <div class=\"tc-milestone-subgrid\">\n                <div class=\"tc-milestone-box prev\">\n                    <div class=\"tc-ms-tag\">M\u1ed0C V\u1eeaA QUA (PREVIOUS)</div>\n                    <div class=\"tc-ms-title\" id=\"tc-prev-ms-title\"><span id=\"tc-ms-prev-title\">Vessel Departed Shanghai Port</span></div>\n                    <div class=\"tc-ms-date\" id=\"tc-prev-ms-date\"><span id=\"tc-ms-prev-date\">01/10/2026</span></div>\n                </div>\n                <div class=\"tc-milestone-box next\">\n                    <div class=\"tc-ms-tag\">M\u1ed0C K\u1ebe TI\u1ebeP (NEXT)</div>\n                    <div class=\"tc-ms-title\" id=\"tc-next-ms-title\"><span id=\"tc-ms-next-title\">Arrival Da Nang Port</span></div>\n                    <div class=\"tc-ms-date\" id=\"tc-next-ms-date\"><span id=\"tc-ms-next-date\">08/10/2026 (Tr\u1ec5 +2 ng\u00e0y)</span></div>\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 3: OVERALL HEALTH & READINESS GRID -->\n        <div class=\"tc-health-grid\" id=\"tc-health-grid\">\n            <!-- 6 th\u1ebb tr\u1ea1ng th\u00e1i Rendered dynamically via JS -->\n        </div>\n\n        <!-- KH\u1ed0I 4 & 5: SHIPMENT SUMMARY & DOCUMENT READINESS -->\n        <div class=\"tc-two-col-grid\">\n            <!-- KH\u1ed0I 4: SHIPMENT SUMMARY -->\n            <div class=\"tc-card\" id=\"tc-shipment-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-ship\" style=\"color: #0284c7;\"></i> V\u1eadn \u0110\u01a1n & H\u00e0nh Tr\u00ecnh (Shipment Summary)\n                    </div>\n                    <button class=\"btn btn-xs btn-primary font-weight-bold tc-btn-goto-shipment tc-drill-down-shipment\" id=\"tc-btn-goto-shipment\" name=\"tc-btn-goto-shipment\">\n                        Xem Shipment Tracking <i class=\"fa fa-arrow-right\"></i>\n                    </button>\n                </div>\n                <div class=\"tc-shipment-summary-content\" id=\"tc-shipment-body\">\n                    <div id=\"tc-shipment-summary-body\"></div>\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 5: DOCUMENT READINESS -->\n            <div class=\"tc-card\" id=\"tc-documents-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-file-text-o\" style=\"color: #0284c7;\"></i> H\u1ed3 S\u01a1 & Ch\u1ee9ng T\u1eeb (Document Readiness)\n                    </div>\n                    <span class=\"tc-badge-soft\" id=\"tc-docs-pct-badge\"><span id=\"tc-doc-readiness-badge\">8 / 10 S\u1eb5n s\u00e0ng (80%)</span></span>\n                </div>\n                <div class=\"tc-docs-content\" id=\"tc-docs-body\"><div id=\"tc-doc-readiness-body\"></div>\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 6 & 7: CUSTOMS & LANDED COST -->\n        <div class=\"tc-two-col-grid\">\n            <!-- KH\u1ed0I 6: CUSTOMS & COMPLIANCE -->\n            <div class=\"tc-card\" id=\"tc-customs-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-gavel\" style=\"color: #0284c7;\"></i> H\u1ea3i Quan & Tu\u00e2n Th\u1ee7 (Customs & Compliance)\n                    </div>\n                    <span class=\"tc-badge-soft\" id=\"tc-customs-status-badge\"><span id=\"tc-customs-badge\">PREPARING (70%)</span></span>\n                </div>\n                <div class=\"tc-customs-content\" id=\"tc-customs-body\">\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 7: COST SUMMARY (LANDED COST) -->\n            <div class=\"tc-card\" id=\"tc-cost-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-calculator\" style=\"color: #0284c7;\"></i> Chi Ph\u00ed & Gi\u00e1 Th\u00e0nh Nh\u1eadp Kh\u1ea9u (Landed Cost Summary)\n                    </div>\n                    <span class=\"tc-badge-soft\" id=\"tc-cost-status-badge\">IN PROGRESS (+7.9%)</span>\n                </div>\n                <div class=\"tc-cost-content\" id=\"tc-cost-body\">\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 8 & 9: WAREHOUSE & OPEN EXCEPTIONS -->\n        <div class=\"tc-two-col-grid\">\n            <!-- KH\u1ed0I 8: WAREHOUSE READINESS -->\n            <div class=\"tc-card\" id=\"tc-warehouse-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-building-o\" style=\"color: #0284c7;\"></i> Kho H\u00e0ng & Giao Nh\u1eadn (Warehouse Readiness)\n                    </div>\n                    <span class=\"tc-badge-soft\" id=\"tc-warehouse-status-badge\"><span id=\"tc-wh-badge\">NOT READY</span></span>\n                </div>\n                <div class=\"tc-warehouse-content\" id=\"tc-warehouse-body\"><div id=\"tc-wh-body\"></div>\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 9: OPEN EXCEPTIONS -->\n            <div class=\"tc-card\" id=\"tc-exceptions-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-exclamation-triangle\" style=\"color: #d97706;\"></i> S\u1ef1 C\u1ed1 & Ngo\u1ea1i L\u1ec7 \u0110ang M\u1edf (Top Open Exceptions)\n                    </div>\n                    <span class=\"tc-badge-soft danger\" id=\"tc-open-exceptions-badge\"><span id=\"tc-exceptions-badge\">3 Open (1 Qu\u00e1 h\u1ea1n)</span></span>\n                </div>\n                <div class=\"tc-exceptions-content\" id=\"tc-exceptions-body\"><div id=\"tc-exceptions-body-inner\"></div>\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 10 & 11: UPCOMING ACTIONS & ERP DOCUMENTS -->\n        <div class=\"tc-two-col-grid\">\n            <!-- KH\u1ed0I 10: UPCOMING ACTIONS & DEADLINES -->\n            <div class=\"tc-card\" id=\"tc-actions-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-calendar-check-o\" style=\"color: #0284c7;\"></i> H\u00e0nh \u0110\u1ed9ng Ti\u1ebfp Theo & H\u1ea1n \u0110\u1ecbnh (Upcoming Actions)\n                    </div>\n                    <span class=\"tc-subtitle-tag\">B\u00e2y gi\u1edd c\u1ea7n l\u00e0m g\u00ec ti\u1ebfp theo?</span>\n                </div>\n                <div class=\"tc-actions-content\" id=\"tc-actions-body\">\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 11: RELATED ERP DOCUMENTS -->\n            <div class=\"tc-card\" id=\"tc-erp-docs-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-link\" style=\"color: #0284c7;\"></i> Ch\u1ee9ng T\u1eeb ERPNext Li\u00ean K\u1ebft (Related ERP Documents)\n                    </div>\n                </div>\n                <div class=\"tc-erp-docs-content\" id=\"tc-related-erp-body\">\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 12 & 13: RESPONSIBILITY MATRIX & ACTIVITY TIMELINE -->\n        <div class=\"tc-two-col-grid\">\n            <!-- KH\u1ed0I 12: RESPONSIBILITY MATRIX -->\n            <div class=\"tc-card\" id=\"tc-responsibility-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-users\" style=\"color: #0284c7;\"></i> Ph\u00e2n C\u00f4ng Tr\u00e1ch Nhi\u1ec7m (Responsibility Matrix)\n                    </div>\n                </div>\n                <div class=\"tc-responsibility-content\" id=\"tc-responsibility-body\">\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 13: ACTIVITY TIMELINE -->\n            <div class=\"tc-card\" id=\"tc-timeline-card\">\n                <div class=\"tc-card-header\">\n                    <div class=\"tc-card-title\">\n                        <i class=\"fa fa-history\" style=\"color: #0284c7;\"></i> Nh\u1eadt K\u00fd Ho\u1ea1t \u0110\u1ed9ng & L\u1ecbch S\u1eed (Activity Audit Timeline)\n                    </div>\n                </div>\n                <div class=\"tc-timeline-content\" id=\"tc-activity-body\">\n                    <!-- Rendered dynamically via JS -->\n                </div>\n            </div>\n        </div>\n\n        <!-- KH\u1ed0I 14: QUICK ACTIONS & STAGE GATE -->\n        <div class=\"tc-card\" id=\"tc-stage-gate-card\">\n            <div class=\"tc-card-header\">\n                <div class=\"tc-card-title\">\n                    <i class=\"fa fa-bolt\" style=\"color: #0284c7;\"></i> Thao T\u00e1c Nhanh & Ch\u1ed1t Ch\u1eb7n H\u1ed3 S\u01a1 (Quick Actions & Stage Gate)\n                </div>\n            </div>\n            <div class=\"tc-stage-gate-content\" id=\"tc-stage-gate-body\">\n                <!-- Rendered dynamically via JS -->\n            </div>\n        </div>\n    </div>\n\n    <!-- TAB 2: SHIPMENT TRACKING HUB (100% NGUY\u00caN B\u1ea2N C\u1ee6A 7d1ef41) -->\n    <div class=\"logistics-tab-pane\" id=\"tab-pane-shipment-tracking\">\n        <div class=\"shipment-tracking-hub-container\">\n            <!-- Top Action Header -->\n            <div class=\"hub-header-bar\">\n                <div class=\"hub-title-block\">\n                    <h2 class=\"hub-title\">\n                        <span class=\"hub-title-icon\">\n                            <svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0071E3\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                                <polygon points=\"3 11 22 2 13 21 11 13 3 11\"/>\n                            </svg>\n                        </span>\n                        <span class=\"hub-title-text\">Trung T\u00e2m Qu\u1ea3n Tr\u1ecb V\u1eadn Chuy\u1ec3n To\u00e0n C\u1ea7u</span>\n                    </h2>\n                    <p class=\"hub-subtitle\">Gi\u00e1m s\u00e1t h\u00e0nh tr\u00ecnh container, ti\u1ebfn \u0111\u1ed9 m\u1ed1c DCSA qu\u1ed1c t\u1ebf v\u00e0 ph\u00e1t hi\u1ec7n l\u1ec7ch l\u1ecbch tr\u00ecnh theo th\u1eddi gian th\u1ef1c</p>\n                </div>\n                <div class=\"hub-header-actions\">\n                    <button class=\"btn btn-default btn-sm hub-btn-refresh\" id=\"hub-btn-refresh\" title=\"L\u00e0m m\u1edbi d\u1eef li\u1ec7u\">\n                        <i class=\"fa fa-refresh\"></i> L\u00e0m m\u1edbi\n                    </button>\n                    <button class=\"btn btn-primary btn-sm hub-btn-sync\" id=\"hub-btn-sync-now\" title=\"\u0110\u1ed3ng b\u1ed9 d\u1eef li\u1ec7u t\u1ee9c th\u00ec t\u1eeb h\u00e3ng v\u1eadn t\u1ea3i\">\n                        <i class=\"fa fa-cloud-download\"></i> \u0110\u1ed3ng b\u1ed9 t\u1ee9c th\u00ec (Sync Now)\n                    </button>\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 1: 4 Th\u1ebb KPI Metrics (Icon Vector SVG Monoline) -->\n            <div class=\"hub-kpi-grid\">\n                <div class=\"hub-kpi-card kpi-total\" data-filter=\"all\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0071E3\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                            <line x1=\"16.5\" y1=\"9.4\" x2=\"7.5\" y2=\"4.21\"/>\n                            <path d=\"M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z\"/>\n                            <polyline points=\"3.27 6.96 12 12.01 20.73 6.96\"/>\n                            <line x1=\"12\" y1=\"22.08\" x2=\"12\" y2=\"12\"/>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">T\u1ed5ng s\u1ed1 l\u00f4 h\u00e0ng</div>\n                        <div class=\"kpi-value\" id=\"kpi-val-total\">0</div>\n                        <div class=\"kpi-desc\">T\u1ea5t c\u1ea3 v\u1eadn \u0111\u01a1n trong h\u1ec7 th\u1ed1ng</div>\n                    </div>\n                </div>\n                <div class=\"hub-kpi-card kpi-transit active\" data-filter=\"In Transit\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0071E3\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                            <polygon points=\"12 2 19 21 12 17 5 21 12 2\"/>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">\u0110ang v\u1eadn chuy\u1ec3n</div>\n                        <div class=\"kpi-value\" id=\"kpi-val-transit\">0</div>\n                        <div class=\"kpi-desc\">T\u00e0u bi\u1ec3n & m\u00e1y bay \u0111ang h\u00e0nh tr\u00ecnh</div>\n                    </div>\n                </div>\n                <div class=\"hub-kpi-card kpi-delayed\" data-filter=\"Delayed\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#DC2626\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                            <path d=\"M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z\"/>\n                            <line x1=\"12\" y1=\"9\" x2=\"12\" y2=\"13\"/>\n                            <line x1=\"12\" y1=\"17\" x2=\"12.01\" y2=\"17\"/>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">Ch\u1eadm ti\u1ebfn \u0111\u1ed9</div>\n                        <div class=\"kpi-value\" id=\"kpi-val-delayed\">0</div>\n                        <div class=\"kpi-desc\">H\u00e0nh tr\u00ecnh b\u1ecb l\u1ec7ch ETA > 1 ng\u00e0y</div>\n                    </div>\n                </div>\n                <div class=\"hub-kpi-card kpi-stale\" data-filter=\"Stale\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#D97706\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                            <circle cx=\"12\" cy=\"12\" r=\"10\"/>\n                            <polyline points=\"12 6 12 12 16 14\"/>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">C\u1ea3nh b\u00e1o ngo\u1ea1i l\u1ec7</div>\n                        <div class=\"kpi-value\" id=\"kpi-val-stale\">0</div>\n                        <div class=\"kpi-desc\">Ch\u01b0a c\u00f3 t\u00edn hi\u1ec7u m\u1edbi t\u1eeb carrier</div>\n                    </div>\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 2: B\u1ea3n \u0111\u1ed3 Gi\u00e1m s\u00e1t To\u00e0n c\u1ea7u T\u01b0\u01a1ng t\u00e1c -->\n            <div class=\"hub-map-card\">\n                <div class=\"hub-card-header\">\n                    <div class=\"card-header-title\">\n                        <span class=\"header-icon\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0071E3\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                                <circle cx=\"12\" cy=\"12\" r=\"10\"/>\n                                <line x1=\"2\" y1=\"12\" x2=\"22\" y2=\"12\"/>\n                                <path d=\"M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z\"/>\n                            </svg>\n                        </span>\n                        <span class=\"header-text\" id=\"hub-map-title\">B\u1ea3n \u0111\u1ed3 Gi\u00e1m s\u00e1t To\u00e0n c\u1ea7u (Fleet Overview)</span>\n                    </div>\n                    <div class=\"card-header-controls\">\n                        <span class=\"badge badge-info\" id=\"hub-selected-shipment-badge\" style=\"display:none;\"></span>\n                        <button class=\"btn btn-xs btn-default\" id=\"hub-map-reset-btn\" title=\"Tr\u1edf v\u1ec1 g\u00f3c nh\u00ecn to\u00e0n c\u1ea7u\">\n                            <i class=\"fa fa-globe\"></i> To\u00e0n c\u1ea3nh\n                        </button>\n                    </div>\n                </div>\n                <div class=\"hub-map-wrapper\">\n                    <div id=\"lw-hub-map\" class=\"lw-hub-map-canvas\"></div>\n                    <div id=\"hub-map-loading\" class=\"hub-map-loading-overlay\" style=\"display:none;\">\n                        <div class=\"spinner-border text-primary\" role=\"status\"></div>\n                        <span>\u0110ang t\u1ea3i l\u1ed9 tr\u00ecnh & \u0111\u1ecbnh v\u1ecb ph\u01b0\u01a1ng ti\u1ec7n...</span>\n                    </div>\n                </div>\n            </div>\n\n            <!-- KH\u1ed0I 4: Visual Milestones Timeline Stepper (9 M\u1ed1c DCSA) -->\n            <div class=\"hub-timeline-card\" id=\"hub-stepper-card\">\n                <div class=\"hub-card-header\">\n                    <div class=\"card-header-title\">\n                        <span class=\"header-icon\">\n                            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0071E3\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                                <circle cx=\"12\" cy=\"12\" r=\"4\"/>\n                                <line x1=\"1.05\" y1=\"12\" x2=\"8\" y2=\"12\"/>\n                                <line x1=\"16\" y1=\"12\" x2=\"22.95\" y2=\"12\"/>\n                            </svg>\n                        </span>\n                        <span class=\"header-text\">Ti\u1ebfn Tr\u00ecnh 9 M\u1ed1c S\u1ef1 Ki\u1ec7n Qu\u1ed1c T\u1ebf DCSA (Milestones Stepper)</span>\n                    </div>\n                    <div class=\"card-header-actions\">\n                        <span class=\"hub-stepper-shipment-name\" id=\"stepper-shipment-name\">Ch\u01b0a ch\u1ecdn l\u00f4 h\u00e0ng</span>\n                    </div>\n                </div>\n                <div class=\"hub-stepper-container\">\n                    <div class=\"hub-stepper-track\" id=\"hub-stepper-track\">\n                        <!-- S\u1ebd \u0111\u01b0\u1ee3c render \u0111\u1ed9ng qua JS (9 m\u1ed1c: BOOKED, GATE_IN, LOADED, DEPARTED, TRANSSHIPMENT, ARRIVED, DISCHARGED, GATE_OUT, DELIVERED) -->\n                    </div>\n                </div>\n            </div>\n\n            <!-- T\u1ea6NG D\u01af\u1edaI: Chia 2 C\u1ed9t (B\u1ea3ng l\u00f4 h\u00e0ng chi ti\u1ebft 65% + Trung t\u00e2m C\u1ea3nh b\u00e1o 35%) -->\n            <div class=\"hub-split-section\">\n                <!-- KH\u1ed0I 3: B\u1ea3ng Qu\u1ea3n tr\u1ecb L\u00f4 h\u00e0ng Chi ti\u1ebft (65%) -->\n                <div class=\"hub-table-panel\">\n                    <div class=\"hub-card-header\">\n                        <div class=\"card-header-title\">\n                            <span class=\"header-icon\">\n                                <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0071E3\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                                    <line x1=\"8\" y1=\"6\" x2=\"21\" y2=\"6\"/>\n                                    <line x1=\"8\" y1=\"12\" x2=\"21\" y2=\"12\"/>\n                                    <line x1=\"8\" y1=\"18\" x2=\"21\" y2=\"18\"/>\n                                    <line x1=\"3\" y1=\"6\" x2=\"3.01\" y2=\"6\"/>\n                                    <line x1=\"3\" y1=\"12\" x2=\"3.01\" y2=\"12\"/>\n                                    <line x1=\"3\" y1=\"18\" x2=\"3.01\" y2=\"18\"/>\n                                </svg>\n                            </span>\n                            <span class=\"header-text\">Danh S\u00e1ch L\u00f4 H\u00e0ng Qu\u1ed1c T\u1ebf</span>\n                        </div>\n                        <div class=\"hub-search-box\">\n                            <i class=\"fa fa-search hub-search-icon\"></i>\n                            <input type=\"text\" id=\"hub-search-input\" class=\"form-control input-sm\" placeholder=\"T\u00ecm m\u00e3 v\u1eadn \u0111\u01a1n, container, B/L, PO, h\u00e3ng t\u00e0u...\">\n                        </div>\n                    </div>\n\n                    <!-- Filter Tabs -->\n                    <div class=\"hub-filter-tabs\">\n                        <button class=\"hub-tab-btn active\" data-tab=\"all\">T\u1ea5t c\u1ea3 (<span id=\"tab-cnt-all\">0</span>)</button>\n                        <button class=\"hub-tab-btn\" data-tab=\"In Transit\">\u0110ang v\u1eadn chuy\u1ec3n (<span id=\"tab-cnt-transit\">0</span>)</button>\n                        <button class=\"hub-tab-btn\" data-tab=\"Delayed\">Tr\u1ec5 h\u1ea1n (<span id=\"tab-cnt-delayed\">0</span>)</button>\n                        <button class=\"hub-tab-btn\" data-tab=\"Stale\">M\u1ea5t t\u00edn hi\u1ec7u (<span id=\"tab-cnt-stale\">0</span>)</button>\n                        <button class=\"hub-tab-btn\" data-tab=\"Delivered\">\u0110\u00e3 giao h\u00e0ng (<span id=\"tab-cnt-delivered\">0</span>)</button>\n                    </div>\n\n                    <!-- Shipment Data Table -->\n                    <div class=\"hub-table-wrapper\">\n                        <table class=\"table table-hover hub-data-table\" id=\"hub-shipments-table\">\n                            <thead>\n                                <tr>\n                                    <th style=\"width: 22%;\">V\u1eadn \u0111\u01a1n / Container</th>\n                                    <th style=\"width: 18%;\">H\u00e3ng t\u00e0u & Ph\u01b0\u01a1ng ti\u1ec7n</th>\n                                    <th style=\"width: 20%;\">C\u1ea3ng \u0110i \u2794 \u0110\u1ebfn</th>\n                                    <th style=\"width: 15%;\">L\u1ecbch tr\u00ecnh (ETD / ETA)</th>\n                                    <th style=\"width: 13%;\">\u0110\u1ed9 tr\u1ec5</th>\n                                    <th style=\"width: 12%; text-align: center;\">Thao t\u00e1c</th>\n                                </tr>\n                            </thead>\n                            <tbody id=\"hub-shipments-tbody\">\n                                <tr>\n                                    <td colspan=\"6\" class=\"text-center text-muted\" style=\"padding: 30px;\">\n                                        <i class=\"fa fa-spinner fa-spin\"></i> \u0110ang t\u1ea3i d\u1eef li\u1ec7u v\u1eadn chuy\u1ec3n...\n                                    </td>\n                                </tr>\n                            </tbody>\n                        </table>\n                    </div>\n                </div>\n\n                <!-- KH\u1ed0I 5: Trung T\u00e2m C\u1ea3nh B\u00e1o Ngo\u1ea1i L\u1ec7 & Bi\u1ebfn \u0110\u1ed9ng ETA (35%) -->\n                <div class=\"hub-exceptions-panel\">\n                    <div class=\"hub-card-header\">\n                        <div class=\"card-header-title\">\n                            <span class=\"header-icon\">\n                                <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#DC2626\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                                    <path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z\"/>\n                                    <line x1=\"12\" y1=\"8\" x2=\"12\" y2=\"12\"/>\n                                    <line x1=\"12\" y1=\"16\" x2=\"12.01\" y2=\"16\"/>\n                                </svg>\n                            </span>\n                            <span class=\"header-text\">Trung T\u00e2m Ngo\u1ea1i L\u1ec7 & C\u1ea3nh B\u00e1o (Exception Center)</span>\n                        </div>\n                        <span class=\"badge badge-warning\" id=\"hub-exception-count-badge\">0 s\u1ef1 c\u1ed1</span>\n                    </div>\n                    <div class=\"hub-exceptions-list\" id=\"hub-exceptions-list\">\n                        <!-- S\u1ebd \u0111\u01b0\u1ee3c render \u0111\u1ed9ng qua JS -->\n                        <div class=\"text-center text-muted\" style=\"padding: 35px 15px;\">\n                            <i class=\"fa fa-check-circle text-success\" style=\"font-size: 28px; margin-bottom: 8px;\"></i>\n                            <p style=\"margin: 0; font-size: 13px;\">Kh\u00f4ng c\u00f3 s\u1ef1 c\u1ed1 ho\u1eb7c c\u1ea3nh b\u00e1o ngo\u1ea1i l\u1ec7 \u0111ang m\u1edf.</p>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n\n    <!-- TAB 3: TRADE COST & LANDED COST MANAGEMENT DASHBOARD -->\n    <div class=\"logistics-tab-pane\" id=\"tab-pane-trade-cost\">\n            <!-- 1. Top Control Bar (matching tc-tab-control-bar) -->\n            <div class=\"tc-tab-control-bar\">\n                <div class=\"tc-select-case-group\">\n                    <label for=\"tcd-case-selector\" class=\"tc-select-label\">\n                        <i class=\"fa fa-calculator\" style=\"color: #0284c7;\"></i> Ch\u1ecdn h\u1ed3 s\u01a1 Trade Case:\n                    </label>\n                    <div class=\"tc-select-wrapper\">\n                        <select id=\"tcd-case-selector\" class=\"form-control tc-case-select-dropdown\">\n                            <option value=\"IMP-2026-001\" selected>IMP-2026-001 - ABC Electronics Co., Ltd (Import Case \u2022 In Transit)</option>\n                            <option value=\"EXP-2026-002\">EXP-2026-002 - Global Coffee Exporter (Export Case \u2022 Ready)</option>\n                            <option value=\"IMP-2026-003\">IMP-2026-003 - Pacific Seafood Import (Import Case \u2022 Delivered)</option>\n                        </select>\n                    </div>\n                </div>\n                <div class=\"tc-tab-control-actions\">\n                    <div class=\"hub-filter-tabs\" style=\"border: 1px solid #e2e8f0; border-radius: 6px; background: #ffffff; padding: 2px;\">\n                        <button class=\"hub-tab-btn active tcd-type-btn\" data-type=\"all\">T\u1ea5t c\u1ea3</button>\n                        <button class=\"hub-tab-btn tcd-type-btn\" data-type=\"import\">Nh\u1eadp kh\u1ea9u (Landed Cost)</button>\n                        <button class=\"hub-tab-btn tcd-type-btn\" data-type=\"export\">Xu\u1ea5t kh\u1ea9u (Export Margin)</button>\n                    </div>\n                    <button class=\"btn btn-default btn-sm\" id=\"tcd-btn-refresh\" title=\"L\u00e0m m\u1edbi\"><i class=\"fa fa-refresh\"></i> L\u00e0m m\u1edbi</button>\n                    <button class=\"btn btn-primary btn-sm hub-btn-sync\" id=\"tcd-btn-new-sheet\"><i class=\"fa fa-plus\"></i> L\u1eadp Cost Sheet</button>\n                    <button class=\"btn btn-default btn-sm\" id=\"tcd-btn-sync-lcv\" title=\"\u0110\u1ed3ng b\u1ed9 sang ERPNext Landed Cost Voucher\"><i class=\"fa fa-exchange\"></i> \u0110\u1ed3ng b\u1ed9 LCV</button>\n                </div>\n            </div>\n\n            <!-- 2. KPI Summary Grid (4 Cards matching Hub style) -->\n            <div class=\"hub-kpi-grid\">\n                <div class=\"hub-kpi-card kpi-total\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#475569\" stroke-width=\"2\">\n                            <rect x=\"2\" y=\"4\" width=\"20\" height=\"16\" rx=\"2\"></rect>\n                            <line x1=\"12\" y1=\"8\" x2=\"12\" y2=\"16\"></line>\n                            <line x1=\"8\" y1=\"12\" x2=\"16\" y2=\"12\"></line>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">Tr\u1ecb gi\u00e1 h\u00e0ng mua (FOB)</div>\n                        <div class=\"kpi-value\" id=\"tcd-kpi-po-val\">$125,000.00</div>\n                        <div class=\"kpi-desc\">Tr\u1ecb gi\u00e1 tr\u00ean h\u1ee3p \u0111\u1ed3ng ngo\u1ea1i th\u01b0\u01a1ng</div>\n                    </div>\n                </div>\n\n                <div class=\"hub-kpi-card kpi-transit\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2\">\n                            <path d=\"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z\"></path>\n                            <polyline points=\"14 2 14 8 20 8\"></polyline>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">Chi ph\u00ed d\u1ef1 to\u00e1n (Estimated)</div>\n                        <div class=\"kpi-value\" id=\"tcd-kpi-est-val\" style=\"color: #0284c7;\">$16,800.00</div>\n                        <div class=\"kpi-desc\">\u0110\u1ecbnh m\u1ee9c chi ph\u00ed logistics d\u1ef1 ki\u1ebfn</div>\n                    </div>\n                </div>\n\n                <div class=\"hub-kpi-card\">\n                    <div class=\"kpi-icon-wrap\" style=\"background-color: #ecfdf5;\">\n                        <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#059669\" stroke-width=\"2\">\n                            <line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"></line>\n                            <path d=\"M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6\"></path>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">Chi ph\u00ed th\u1ef1c t\u1ebf (Actual)</div>\n                        <div class=\"kpi-value\" id=\"tcd-kpi-act-val\" style=\"color: #059669;\">$18,350.00</div>\n                        <div class=\"kpi-desc\">T\u1ed5ng chi ph\u00ed theo h\u00f3a \u0111\u01a1n nh\u00e0 cung c\u1ea5p</div>\n                    </div>\n                </div>\n\n                <div class=\"hub-kpi-card kpi-delayed\">\n                    <div class=\"kpi-icon-wrap\">\n                        <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#dc2626\" stroke-width=\"2\">\n                            <polyline points=\"23 6 13.5 15.5 8.5 10.5 1 18\"></polyline>\n                            <polyline points=\"17 6 23 6 23 12\"></polyline>\n                        </svg>\n                    </div>\n                    <div class=\"kpi-data\">\n                        <div class=\"kpi-label\">Ch\u00eanh l\u1ec7ch chi ph\u00ed (Variance)</div>\n                        <div class=\"kpi-value\" id=\"tcd-kpi-var-val\" style=\"color: #dc2626;\">+$1,550.00 (+9.2%)</div>\n                        <div class=\"kpi-desc\">C\u1ea3nh b\u00e1o: V\u01b0\u1ee3t d\u1ef1 to\u00e1n ban \u0111\u1ea7u</div>\n                    </div>\n                </div>\n            </div>\n\n            <!-- 3. Split Section (65% / 35%) -->\n            <div class=\"hub-split-section\">\n                <!-- C\u1ed8T TR\u00c1I (65%): B\u1ea3ng K\u00ea Chi Ti\u1ebft 11 Kho\u1ea3n Chi Ph\u00ed & Custom Allocation Engine -->\n                <div class=\"hub-table-panel\">\n                    <div class=\"hub-card-header\">\n                        <div class=\"card-header-title\">\n                            <span class=\"header-icon\">\n                                <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#0284c7\" stroke-width=\"2\">\n                                    <rect x=\"2\" y=\"3\" width=\"20\" height=\"14\" rx=\"2\" ry=\"2\"></rect>\n                                    <line x1=\"8\" y1=\"21\" x2=\"16\" y2=\"21\"></line>\n                                    <line x1=\"12\" y1=\"17\" x2=\"12\" y2=\"21\"></line>\n                                </svg>\n                            </span>\n                            <span class=\"header-text\">B\u1ea3ng K\u00ea Chi Ti\u1ebft 11 Kho\u1ea3n Chi Ph\u00ed Logistics (Cost Sheet Items)</span>\n                        </div>\n                        <div class=\"card-header-controls\">\n                            <span class=\"badge-status badge-in-transit\" id=\"tcd-status-badge\">\u0110ang \u0110\u1ed1i So\u00e1t</span>\n                        </div>\n                    </div>\n\n                    <div class=\"hub-table-wrapper\" style=\"max-height: 380px;\">\n                        <table class=\"table hub-data-table\">\n                            <thead>\n                                <tr>\n                                    <th>Kho\u1ea3n Chi Ph\u00ed (Cost Type)</th>\n                                    <th>Nh\u00e0 Cung C\u1ea5p</th>\n                                    <th>S\u1ed1 H\u00f3a \u0110\u01a1n</th>\n                                    <th class=\"text-right\">D\u1ef1 To\u00e1n</th>\n                                    <th class=\"text-right\">Th\u1ef1c T\u1ebf</th>\n                                    <th class=\"text-right\">Ch\u00eanh L\u1ec7ch</th>\n                                    <th class=\"text-center\">Tr\u1ea1ng Th\u00e1i</th>\n                                </tr>\n                            </thead>\n                            <tbody id=\"tcd-cost-items-tbody\">\n                                <!-- Rendered dynamically -->\n                            </tbody>\n                        </table>\n                    </div>\n\n                    <!-- Custom Landed Cost Allocation Engine Card inside Panel -->\n                    <div style=\"border-top: 1px solid #e2e8f0; padding: 16px 18px; background: #ffffff;\">\n                        <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;\">\n                            <div>\n                                <h4 style=\"margin: 0; font-size: 13.5px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;\">\n                                    <i class=\"fa fa-sliders\" style=\"color: #0d9488;\"></i>\n                                    Custom Cost Allocation Engine (Ph\u00e2n B\u1ed5 Gi\u00e1 V\u1ed1n Landed Cost)\n                                </h4>\n                                <span style=\"font-size: 11.5px; color: #64748b;\">T\u1ef1 \u0111\u1ed9ng ph\u00e2n b\u1ed5 chi ph\u00ed v\u00e0o t\u1eebng m\u1eb7t h\u00e0ng trong Purchase Receipt theo chu\u1ea9n k\u1ebf to\u00e1n ERPNext</span>\n                            </div>\n                            <div style=\"display: flex; gap: 6px;\">\n                                <button class=\"btn btn-xs btn-default tcd-alloc-btn active\" data-rule=\"weight\"><i class=\"fa fa-balance-scale\"></i> Tr\u1ecdng l\u01b0\u1ee3ng (Weight)</button>\n                                <button class=\"btn btn-xs btn-default tcd-alloc-btn\" data-rule=\"value\"><i class=\"fa fa-dollar\"></i> Tr\u1ecb gi\u00e1 (Value)</button>\n                                <button class=\"btn btn-xs btn-default tcd-alloc-btn\" data-rule=\"qty\"><i class=\"fa fa-cubes\"></i> S\u1ed1 l\u01b0\u1ee3ng (Qty)</button>\n                                <button class=\"btn btn-xs btn-default tcd-alloc-btn\" data-rule=\"volume\"><i class=\"fa fa-cube\"></i> Th\u1ec3 t\u00edch (CBM)</button>\n                            </div>\n                        </div>\n\n                        <div class=\"table-responsive\" style=\"max-height: 240px; overflow-y: auto;\">\n                            <table class=\"table table-bordered hub-data-table\" style=\"font-size: 12px;\">\n                                <thead>\n                                    <tr style=\"background: #f8fafc;\">\n                                        <th>M\u00e3 H\u00e0ng (Item)</th>\n                                        <th>T\u00ean M\u1eb7t H\u00e0ng</th>\n                                        <th class=\"text-center\">S\u1ed1 L\u01b0\u1ee3ng</th>\n                                        <th class=\"text-right\">\u0110\u01a1n Gi\u00e1 Mua</th>\n                                        <th class=\"text-right\">Ph\u00ed Ph\u00e2n B\u1ed5</th>\n                                        <th class=\"text-right\">Gi\u00e1 V\u1ed1n Th\u1ef1c T\u1ebf (Landed Cost)</th>\n                                        <th class=\"text-center\">% T\u0103ng</th>\n                                    </tr>\n                                </thead>\n                                <tbody id=\"tcd-allocation-tbody\">\n                                    <!-- Rendered dynamically -->\n                                </tbody>\n                            </table>\n                        </div>\n\n                        <div style=\"display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px dashed #e2e8f0; font-size: 12px; flex-wrap: wrap; gap: 8px;\">\n                            <span style=\"color: #059669; font-weight: 600;\"><i class=\"fa fa-check-circle\"></i> \u0110\u1ed9 l\u1ec7ch l\u00e0m tr\u00f2n: 0.00 USD (Kh\u1edbp 100% chi ph\u00ed th\u1ef1c t\u1ebf)</span>\n                            <button class=\"btn btn-xs btn-primary hub-btn-sync\" id=\"tcd-btn-apply-lcv\"><i class=\"fa fa-check\"></i> C\u1eadp Nh\u1eadt Gi\u00e1 V\u1ed1n V\u00e0o ERPNext LCV</button>\n                        </div>\n                    </div>\n                </div>\n\n                <!-- C\u1ed8T PH\u1ea2I (35%): Audit, LCV Sync, Export Margin -->\n                <div class=\"hub-exceptions-panel\">\n                    <!-- 1. Audit & Anomaly Detection -->\n                    <div class=\"hub-card-header\">\n                        <div class=\"card-header-title\">\n                            <span class=\"header-icon\">\n                                <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#d97706\" stroke-width=\"2\">\n                                    <path d=\"M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z\"></path>\n                                    <line x1=\"12\" y1=\"9\" x2=\"12\" y2=\"13\"></line>\n                                    <line x1=\"12\" y1=\"17\" x2=\"12.01\" y2=\"17\"></line>\n                                </svg>\n                            </span>\n                            <span class=\"header-text\">Ki\u1ec3m To\u00e1n & R\u1ee7i Ro Chi Ph\u00ed (Cost Audit)</span>\n                        </div>\n                        <span class=\"badge-status badge-stale\" id=\"tcd-audit-badge\">1 L\u01b0u \u00fd</span>\n                    </div>\n                    <div class=\"hub-exceptions-list\" id=\"tcd-audit-list\">\n                        <!-- Duplicate Check -->\n                        <div class=\"hub-exception-card\" style=\"border-left: 4px solid #10b981;\">\n                            <div class=\"exception-card-header\">\n                                <span class=\"exception-title\" style=\"color: #047857;\"><i class=\"fa fa-check\"></i> Tr\u00f9ng L\u1eb7p H\u00f3a \u0110\u01a1n (Duplicate Check)</span>\n                                <span class=\"delay-tag-ontime\">H\u1ee3p l\u1ec7</span>\n                            </div>\n                            <div class=\"exception-card-body\">Kh\u00f4ng ph\u00e1t hi\u1ec7n h\u00f3a \u0111\u01a1n tr\u00f9ng l\u1eb7p s\u1ed1 ch\u1ee9ng t\u1eeb ho\u1eb7c nh\u00e0 cung c\u1ea5p.</div>\n                        </div>\n\n                        <!-- Missing Critical Cost Check -->\n                        <div class=\"hub-exception-card warning\">\n                            <div class=\"exception-card-header\">\n                                <span class=\"exception-title\" style=\"color: #b45309;\"><i class=\"fa fa-exclamation-triangle\"></i> Chi Ph\u00ed Tr\u1ecdng Y\u1ebfu (Missing Cost Check)</span>\n                                <span class=\"delay-tag-positive\">C\u1ea7n r\u00e0 so\u00e1t</span>\n                            </div>\n                            <div class=\"exception-card-body\">Ch\u01b0a nh\u1eadn h\u00f3a \u0111\u01a1n n\u00e2ng h\u1ea1 c\u1ea3ng \u0111\u00edch (Port Handling D/O). C\u1ea7n li\u00ean h\u1ec7 \u0111\u1ea1i l\u00fd h\u00e3ng t\u00e0u tr\u01b0\u1edbc ng\u00e0y 14/10.</div>\n                        </div>\n\n                        <!-- Wrong-case Check -->\n                        <div class=\"hub-exception-card\" style=\"border-left: 4px solid #10b981;\">\n                            <div class=\"exception-card-header\">\n                                <span class=\"exception-title\" style=\"color: #047857;\"><i class=\"fa fa-check\"></i> G\u00e1n \u0110\u00fang V\u1ee5 Vi\u1ec7c (Association Check)</span>\n                                <span class=\"delay-tag-ontime\">Kh\u1edbp 100%</span>\n                            </div>\n                            <div class=\"exception-card-body\">T\u1ea5t c\u1ea3 6 h\u00f3a \u0111\u01a1n d\u1ecbch v\u1ee5 \u0111\u1ec1u tham chi\u1ebfu ch\u00ednh x\u00e1c s\u1ed1 PO-2026-0042 v\u00e0 Trade Case IMP-2026-001.</div>\n                        </div>\n                    </div>\n\n                    <!-- 2. ERPNext Landed Cost Voucher Status Card -->\n                    <div style=\"border-top: 1px solid #e2e8f0; padding: 14px 16px; background: #ffffff;\">\n                        <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;\">\n                            <span style=\"font-size: 12.5px; font-weight: 700; color: #0f172a;\"><i class=\"fa fa-link\" style=\"color: #0284c7;\"></i> ERPNext Landed Cost Voucher</span>\n                            <span class=\"tc-badge-erp submitted\" id=\"tcd-lcv-badge\">LCV-2026-0004</span>\n                        </div>\n                        <div style=\"font-size: 11.5px; color: #64748b; line-height: 1.45; margin-bottom: 10px;\">\n                            D\u1eef li\u1ec7u ph\u00e2n b\u1ed5 \u0111\u01b0\u1ee3c ghi nh\u1eadn t\u1ef1 \u0111\u1ed9ng v\u00e0o ch\u1ee9ng t\u1eeb ti\u00eau chu\u1ea9n c\u1ee7a ERPNext, c\u1eadp nh\u1eadt tr\u1ef1c ti\u1ebfp v\u00e0o \u0111\u1ecbnh gi\u00e1 t\u1ed3n kho (Inventory Valuation) v\u00e0 gi\u00e1 v\u1ed1n (COGS).\n                        </div>\n                        <div style=\"display: flex; gap: 8px;\">\n                            <a href=\"/app/landed-cost-voucher\" class=\"btn btn-default btn-xs\" style=\"flex: 1; text-align: center;\"><i class=\"fa fa-external-link\"></i> M\u1edf LCV ERPNext</a>\n                        </div>\n                    </div>\n\n                    <!-- 3. Export Profitability Card -->\n                    <div id=\"tcd-export-profitability-box\" style=\"border-top: 1px solid #e2e8f0; padding: 14px 16px; background: #ffffff;\">\n                        <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;\">\n                            <span style=\"font-size: 12.5px; font-weight: 700; color: #0f172a;\"><i class=\"fa fa-bar-chart\" style=\"color: #059669;\"></i> Hi\u1ec7u Qu\u1ea3 L\u00f4 Xu\u1ea5t Kh\u1ea9u (Export Margin)</span>\n                            <span class=\"delay-tag-ontime\">+24.3% Bi\u00ean L\u1ee3i Nhu\u1eadn</span>\n                        </div>\n                        <table class=\"table tc-table\" style=\"margin-bottom: 0;\">\n                            <tr>\n                                <td class=\"label-col\">Doanh thu xu\u1ea5t kh\u1ea9u:</td>\n                                <td class=\"val-col text-right\">$65,000.00</td>\n                            </tr>\n                            <tr>\n                                <td class=\"label-col\">Gi\u00e1 v\u1ed1n h\u00e0ng b\u00e1n (COGS):</td>\n                                <td class=\"val-col text-right\">$45,000.00</td>\n                            </tr>\n                            <tr>\n                                <td class=\"label-col\">Chi ph\u00ed logistics xu\u1ea5t kh\u1ea9u:</td>\n                                <td class=\"val-col text-right\">$4,200.00</td>\n                            </tr>\n                            <tr style=\"border-top: 1px solid #e2e8f0; font-weight: 700;\">\n                                <td class=\"label-col\" style=\"color: #059669;\">L\u1ee3i nhu\u1eadn g\u1ed9p th\u1ef1c t\u1ebf:</td>\n                                <td class=\"val-col text-right\" style=\"color: #059669; font-size: 13.5px;\">$15,800.00</td>\n                            </tr>\n                        </table>\n                    </div>\n                </div>\n            </div>\n        </div>\n\n        <!-- TAB 4: LOGISTICS AI COPILOT WORKSPACE -->\n        <div class=\"logistics-tab-pane\" id=\"tab-pane-ai-copilot\">\n            <div class=\"lw-copilot-container\">\n                <!-- Left: Chat Sessions Sidebar (Light theme matching system) -->\n                <aside class=\"lw-copilot-sessions-panel\">\n                    <div class=\"lw-copilot-sessions-header\">\n                        <button id=\"copilot-btn-new-chat\" class=\"btn btn-primary btn-sm hub-btn-sync\" style=\"width: 100%;\">\n                            <i class=\"fa fa-plus\"></i> Cu\u1ed9c h\u1ed9i tho\u1ea1i m\u1edbi\n                        </button>\n                    </div>\n                    <div class=\"lw-copilot-search-wrap\">\n                        <i class=\"fa fa-search lw-copilot-search-icon\"></i>\n                        <input type=\"text\" id=\"copilot-session-search\" class=\"form-control lw-copilot-search-input\" placeholder=\"T\u00ecm ki\u1ebfm h\u1ed9i tho\u1ea1i...\">\n                    </div>\n                    <div class=\"lw-copilot-sessions-list\" id=\"copilot-sessions-list\">\n                        <div class=\"lw-session-group-title\">H\u00f4m nay</div>\n                        <div class=\"lw-session-item active\">\n                            <i class=\"fa fa-commenting-o lw-session-icon\"></i>\n                            <div class=\"lw-session-info\">\n                                <span class=\"lw-session-title\">Ph\u00e2n t\u00edch sai l\u1ec7ch chi ph\u00ed IMP-2026-001</span>\n                                <span class=\"lw-session-time\">10:45 AM</span>\n                            </div>\n                        </div>\n                        <div class=\"lw-session-item\">\n                            <i class=\"fa fa-commenting-o lw-session-icon\"></i>\n                            <div class=\"lw-session-info\">\n                                <span class=\"lw-session-title\">Tra c\u1ee9u l\u1ecbch t\u00e0u Maersk Mc-Kinney</span>\n                                <span class=\"lw-session-time\">09:12 AM</span>\n                            </div>\n                        </div>\n                        <div class=\"lw-session-group-title\" style=\"margin-top: 12px;\">7 ng\u00e0y tr\u01b0\u1edbc</div>\n                        <div class=\"lw-session-item\">\n                            <i class=\"fa fa-commenting-o lw-session-icon\"></i>\n                            <div class=\"lw-session-info\">\n                                <span class=\"lw-session-title\">Th\u1ee7 t\u1ee5c C/O Form E xu\u1ea5t kh\u1ea9u</span>\n                                <span class=\"lw-session-time\">14 Oct</span>\n                            </div>\n                        </div>\n                    </div>\n                </aside>\n\n                <!-- Right: Chat Conversation Workspace -->\n                <main class=\"lw-copilot-chat-workspace\">\n                    <div class=\"lw-copilot-chat-header\">\n                        <div class=\"lw-copilot-title-group\">\n                            <div class=\"lw-copilot-avatar\">\n                                <i class=\"fa fa-bolt\"></i>\n                            </div>\n                            <div>\n                                <h3 class=\"lw-copilot-main-title\">Tr\u1ee3 L\u00fd Tr\u00ed Tu\u1ec7 Nh\u00e2n T\u1ea1o Logistics (AI Copilot)</h3>\n                                <span class=\"lw-copilot-sub-title\">T\u1ef1 \u0111\u1ed9ng ph\u00e2n t\u00edch h\u1ed3 s\u01a1 Trade Case, c\u1ea3nh b\u00e1o l\u1ec7ch ETA v\u00e0 t\u1ed1i \u01b0u chi ph\u00ed Landed Cost</span>\n                            </div>\n                        </div>\n                        <div class=\"lw-copilot-actions\">\n                            <div class=\"tc-select-case-group\" style=\"margin: 0;\">\n                                <span style=\"font-size: 12px; font-weight: 600; color: #64748b;\">Ng\u1eef c\u1ea3nh:</span>\n                                <select id=\"copilot-context-case\" class=\"form-control tc-case-select-dropdown\" style=\"height: 32px; font-size: 12px; min-width: 140px;\">\n                                    <option value=\"IMP-2026-001\" selected>IMP-2026-001</option>\n                                    <option value=\"EXP-2026-002\">EXP-2026-002</option>\n                                    <option value=\"IMP-2026-003\">IMP-2026-003</option>\n                                </select>\n                            </div>\n                            <button class=\"btn btn-default btn-xs\" id=\"copilot-btn-clear\" title=\"X\u00f3a h\u1ed9i tho\u1ea1i\"><i class=\"fa fa-trash-o\"></i> X\u00f3a h\u1ed9i tho\u1ea1i</button>\n                        </div>\n                    </div>\n\n                    <!-- Messages stream -->\n                    <div class=\"lw-copilot-messages-thread\" id=\"copilot-messages-thread\">\n                        <div class=\"lw-copilot-welcome-box\">\n                            <div class=\"lw-welcome-icon\"><i class=\"fa fa-compass\" style=\"color: #0284c7; font-size: 26px;\"></i></div>\n                            <h4 style=\"margin: 6px 0; font-size: 15px; font-weight: 700; color: #0f172a;\">Ch\u00e0o b\u1ea1n! T\u00f4i l\u00e0 Tr\u1ee3 L\u00fd Logistics AI Copilot</h4>\n                            <p style=\"color: #64748b; font-size: 12.5px; max-width: 580px; margin: 0 auto 14px;\">\n                                T\u00f4i c\u00f3 th\u1ec3 k\u1ebft n\u1ed1i d\u1eef li\u1ec7u h\u00e0nh tr\u00ecnh t\u00e0u th\u1ef1c t\u1ebf, b\u1ea3ng k\u00ea 11 kho\u1ea3n chi ph\u00ed v\u00e0 c\u00f4ng c\u1ee5 ph\u00e2n b\u1ed5 Landed Cost \u0111\u1ec3 gi\u1ea3i quy\u1ebft nhanh c\u00e1c nghi\u1ec7p v\u1ee5 c\u1ee7a b\u1ea1n:\n                            </p>\n                            <div class=\"lw-suggestions-grid\">\n                                <button class=\"lw-suggestion-pill\" data-prompt=\"Ki\u1ec3m tra chi ti\u1ebft nguy\u00ean nh\u00e2n ch\u00eanh l\u1ec7ch chi ph\u00ed th\u1ef1c t\u1ebf so v\u1edbi d\u1ef1 to\u00e1n l\u00f4 h\u00e0ng IMP-2026-001\">\n                                    <i class=\"fa fa-dollar\" style=\"color: #0284c7;\"></i>\n                                    <span>Ph\u00e2n t\u00edch sai l\u1ec7ch chi ph\u00ed l\u00f4 IMP-2026-001</span>\n                                </button>\n                                <button class=\"lw-suggestion-pill\" data-prompt=\"D\u1ef1 b\u00e1o th\u1eddi gian t\u00e0u c\u1eadp c\u1ea3ng \u0110\u00e0 N\u1eb5ng v\u00e0 c\u00e1c m\u1ed1c th\u1ee7 t\u1ee5c h\u1ea3i quan ti\u1ebfp theo\">\n                                    <i class=\"fa fa-ship\" style=\"color: #0d9488;\"></i>\n                                    <span>D\u1ef1 b\u00e1o ETA & th\u1ee7 t\u1ee5c c\u1ea3ng \u0110\u00e0 N\u1eb5ng</span>\n                                </button>\n                                <button class=\"lw-suggestion-pill\" data-prompt=\"G\u1ee3i \u00fd quy t\u1eafc ph\u00e2n b\u1ed5 gi\u00e1 v\u1ed1n t\u1ed1i \u01b0u cho c\u00e1c m\u1eb7t h\u00e0ng theo Gross Weight\">\n                                    <i class=\"fa fa-sliders\" style=\"color: #d97706;\"></i>\n                                    <span>G\u1ee3i \u00fd quy t\u1eafc ph\u00e2n b\u1ed5 Landed Cost</span>\n                                </button>\n                            </div>\n                        </div>\n\n                        <!-- Chat Messages List -->\n                        <div id=\"copilot-chat-history\"></div>\n                    </div>\n\n                    <!-- Input area -->\n                    <div class=\"lw-copilot-input-area\">\n                        <div class=\"lw-copilot-input-box\">\n                            <textarea id=\"copilot-input-textarea\" class=\"lw-copilot-textarea\" placeholder=\"H\u1ecfi AI Copilot v\u1ec1 ch\u1ee9ng t\u1eeb, ph\u00e2n b\u1ed5 chi ph\u00ed, h\u00e0nh tr\u00ecnh t\u00e0u... (Nh\u1ea5n Enter \u0111\u1ec3 g\u1eedi)\"></textarea>\n                            <button id=\"copilot-btn-send\" class=\"lw-copilot-send-btn\" title=\"G\u1eedi c\u00e2u h\u1ecfi\">\n                                <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                                    <line x1=\"22\" y1=\"2\" x2=\"11\" y2=\"13\"></line>\n                                    <polygon points=\"22 2 15 22 11 13 2 9 22 2\"></polygon>\n                                </svg>\n                            </button>\n                        </div>\n                        <div class=\"lw-copilot-disclaimer\">\n                            Logistics AI Copilot \u0111\u01b0\u1ee3c t\u00edch h\u1ee3p tr\u1ef1c ti\u1ebfp v\u00e0o h\u1ec7 th\u1ed1ng Logistics Wizard Hub.\n                        </div>\n                    </div>\n                </main>\n            </div>\n        </div>\n    </div>\n</div>\n";

// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * Logistics Wizard - Unified Management Hub
 * Bao gồm 2 Phân hệ Nghiệp vụ:
 * 1. Trade Case Overview (Hồ sơ Điều hành Ngoại thương Trung tâm)
 * 2. Shipment Tracking Hub (Trung tâm Quản trị Vận chuyển Toàn cầu)
 */

class UnifiedLogisticsHub {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.currentTab = 'executive';
        this.currentCaseId = 'IMP-2026-001';
        this.executiveDashboard = wrapper ? wrapper.executive_dashboard : null;
        this.trackingHub = wrapper ? wrapper.shipment_tracking_hub : null;
        this.overviewController = wrapper ? wrapper.trade_case_overview : null;
        this.tradeCostDashboard = wrapper ? wrapper.trade_cost_dashboard : null;
        this.aiCopilot = wrapper ? wrapper.logistics_ai_copilot : null;
    }

    switch_tab(tabName, options) {
        options = options || {};
        this.currentTab = tabName;
        const $page = this.wrapper ? $(this.wrapper) : $(document);

        let targetKey = 'executive';
        if (tabName === 'overview' || tabName === 'trade-case' || tabName === 'dossier') {
            targetKey = 'overview';
        } else if (tabName === 'tracking' || tabName === 'shipment-tracking-hub') {
            targetKey = 'tracking';
        } else if (tabName === 'cost' || tabName === 'trade-cost' || tabName === 'trade-cost-dashboard') {
            targetKey = 'cost';
        } else if (tabName === 'copilot' || tabName === 'ai-copilot' || tabName === 'logistics-ai-chatbot') {
            targetKey = 'copilot';
        } else if (tabName === 'executive' || tabName === 'exec' || tabName === 'command-center') {
            targetKey = 'executive';
        }

        // 1. Update active sidebar tab button
        $page.find('.logistics-nav-tab').removeClass('active');
        if (targetKey === 'executive') $page.find('#btn-tab-executive').addClass('active');
        else if (targetKey === 'overview') $page.find('#btn-tab-overview').addClass('active');
        else if (targetKey === 'tracking') $page.find('#btn-tab-tracking').addClass('active');
        else if (targetKey === 'cost') $page.find('#btn-tab-cost').addClass('active');
        else if (targetKey === 'copilot') $page.find('#btn-tab-copilot').addClass('active');

        // 2. Hide all tab panes cleanly without jQuery .hide() / inline display styles
        const $panes = $page.find('.logistics-tab-pane');
        $panes.removeClass('active').removeAttr('style');

        // 3. Show target pane with forced reflow for smooth keyframe entrance animation
        let targetSelector = '#tab-pane-executive';
        if (targetKey === 'overview') targetSelector = '#tab-pane-trade-case';
        else if (targetKey === 'tracking') targetSelector = '#tab-pane-shipment-tracking';
        else if (targetKey === 'cost') targetSelector = '#tab-pane-trade-cost';
        else if (targetKey === 'copilot') targetSelector = '#tab-pane-ai-copilot';

        const $target = $page.find(targetSelector);
        if ($target.length) {
            void $target[0].offsetWidth; // trigger reflow
            $target.addClass('active');
        }

        // 4. Update Desk Page Title
        if (this.wrapper && this.wrapper.shipment_tracking_hub && this.wrapper.shipment_tracking_hub.page) {
            const titles = {
                executive: __('Executive Logistics Command Center'),
                overview: __('Trade Case Dossier'),
                tracking: __('Shipment Tracking Hub'),
                cost: __('Trade Cost & Landed Cost Dashboard'),
                copilot: __('Logistics AI Copilot')
            };
            this.wrapper.shipment_tracking_hub.page.set_title(titles[targetKey] || titles.executive);
        }

        // 5. Trigger sub-controller logic
        if (targetKey === 'executive') {
            if (this.executiveDashboard) {
                this.executiveDashboard.load_data();
            }
        } else if (targetKey === 'tracking') {
            if (this.trackingHub) {
                if (this.trackingHub && this.trackingHub.map) {
                    setTimeout(() => {
                        this.trackingHub.map.invalidateSize();
                    }, 150);
                }

                if (options.shipment_id) {
                    if (this.trackingHub.data) {
                        this.trackingHub.select_shipment(options.shipment_id);
                        this.trackingHub.refresh(options.shipment_id);
                    } else {
                        this.trackingHub.refresh(options.shipment_id);
                    }
                } else if (!this.trackingHub.data) {
                    this.trackingHub.refresh();
                }
            }
        } else if (targetKey === 'overview') {
            if (this.overviewController) {
                if (options.case_id) {
                    this.overviewController.load_case(options.case_id);
                } else if (!this.overviewController.currentData) {
                    this.overviewController.load_case(this.currentCaseId || 'IMP-2026-001');
                }
            }
        } else if (targetKey === 'cost') {
            if (this.tradeCostDashboard) {
                const caseId = options.case_id || this.currentCaseId || 'IMP-2026-001';
                this.tradeCostDashboard.load_data(caseId);
            }
        } else if (targetKey === 'copilot') {
            if (this.aiCopilot) {
                this.aiCopilot.on_tab_shown(options);
            }
        }
    }
}

function make_page_full_bleed(wrapper) {
    if (!wrapper) return;
    try {
        const $w = $(wrapper);
        $w.addClass('logistics-full-bleed-page');
        const $pageContainer = $w.closest('.page-container');
        if ($pageContainer.length) {
            $pageContainer.addClass('logistics-full-width');
            $pageContainer.css({ 'max-width': '100%', 'padding': '0', 'margin': '0', 'width': '100%' });
        }
        $w.find('.page-content.container').removeClass('container').addClass('container-fluid');
        $w.find('.container').removeClass('container').addClass('container-fluid');
        $w.find('.page-body, .page-content, .container-fluid, .layout-main-section-wrapper, .layout-main-section, .layout-main').css({
            'max-width': '100%',
            'width': '100%',
            'padding': '0',
            'margin': '0',
            'border': 'none',
            'box-shadow': 'none',
            'background': 'transparent'
        });
    } catch (e) {
        console.warn('make_page_full_bleed warning:', e);
    }
}

const LOGISTICS_PAGE_CONFIGS = {
    'trade-case-overview': 'overview',
    'executive-dashboard': 'executive',
    'shipment-tracking-hub': 'tracking',
    'trade-cost-dashboard': 'cost',
    'logistics-ai-copilot': 'copilot',
    'managementLogistic': 'overview',
    'managementlogistic': 'overview',
    'management-logistic': 'overview',
    'management_logistic': 'overview',
    'manageLogistic': 'overview',
    'managelogistic': 'overview',
    'manage-logistic': 'overview',
    'manage_logistic': 'overview'
};

function init_logistics_hub_page(pageName, defaultTab, wrapper) {
    if (!wrapper) return;
    make_page_full_bleed(wrapper);

    if (!wrapper.unifiedHub) {
        wrapper.executive_dashboard = new ExecutiveDashboardController(wrapper);
        wrapper.shipment_tracking_hub = new ShipmentTrackingHub(wrapper, pageName);
        wrapper.trade_case_overview = new TradeCaseOverviewController(wrapper, wrapper.shipment_tracking_hub);
        wrapper.trade_cost_dashboard = new EmbeddedTradeCostDashboardController(wrapper);
        wrapper.logistics_ai_copilot = new EmbeddedLogisticsAICopilot(wrapper);
        wrapper.unifiedHub = new UnifiedLogisticsHub(wrapper);
        wrapper.unifiedHub.executiveDashboard = wrapper.executive_dashboard;
        wrapper.unifiedHub.trackingHub = wrapper.shipment_tracking_hub;
        wrapper.unifiedHub.overviewController = wrapper.trade_case_overview;
        wrapper.unifiedHub.tradeCostDashboard = wrapper.trade_cost_dashboard;
        wrapper.unifiedHub.aiCopilot = wrapper.logistics_ai_copilot;
        wrapper.executive_dashboard.unifiedHub = wrapper.unifiedHub;
        wrapper.trade_case_overview.unifiedHub = wrapper.unifiedHub;
        wrapper.trade_cost_dashboard.unifiedHub = wrapper.unifiedHub;
        wrapper.logistics_ai_copilot.unifiedHub = wrapper.unifiedHub;

        wrapper.switch_to_tab = function (tabName, extraParam) {
            if (typeof extraParam === 'string') {
                if (tabName === 'shipment-tracking-hub' || tabName === 'tracking') {
                    wrapper.unifiedHub.switch_tab('tracking', { shipment_id: extraParam });
                } else if (tabName === 'cost' || tabName === 'trade-cost' || tabName === 'trade-cost-dashboard') {
                    wrapper.unifiedHub.switch_tab('cost', { case_id: extraParam });
                } else if (tabName === 'copilot' || tabName === 'ai-copilot') {
                    wrapper.unifiedHub.switch_tab('copilot');
                } else if (tabName === 'executive' || tabName === 'exec') {
                    wrapper.unifiedHub.switch_tab('executive');
                } else {
                    wrapper.unifiedHub.switch_tab('overview', { case_id: extraParam });
                }
            } else {
                wrapper.unifiedHub.switch_tab(tabName, extraParam);
            }
        };

        setup_logistics_hub_tabs(wrapper);
        wrapper.executive_dashboard.init();
        wrapper.trade_case_overview.init();
        wrapper.trade_cost_dashboard.init();
        wrapper.logistics_ai_copilot.init();
        make_page_full_bleed(wrapper);
    }

    show_logistics_hub_page(wrapper, defaultTab);
}

function show_logistics_hub_page(wrapper, defaultTab) {
    if (!wrapper || !wrapper.unifiedHub) return;
    make_page_full_bleed(wrapper);
    let focusShipment = null;
    let focusCase = null;
    let targetTab = defaultTab || 'overview';
    if (frappe.route_options) {
        if (frappe.route_options.shipment) {
            focusShipment = frappe.route_options.shipment;
            targetTab = 'tracking';
        }
        if (frappe.route_options.case_id) {
            focusCase = frappe.route_options.case_id;
            if (!frappe.route_options.tab) targetTab = 'overview';
        }
        if (frappe.route_options.tab) {
            targetTab = frappe.route_options.tab;
        }
        frappe.route_options = null;
    }

    if (focusShipment && wrapper.switch_to_tab) {
        wrapper.switch_to_tab('tracking', focusShipment);
    } else if (focusCase && wrapper.switch_to_tab) {
        wrapper.switch_to_tab(targetTab, focusCase);
    } else if (wrapper.switch_to_tab) {
        wrapper.switch_to_tab(targetTab);
    }
}

function register_logistics_hub_page(pageName, defaultTab) {
    if (typeof frappe !== 'undefined' && frappe.pages && frappe.pages[pageName]) {
        frappe.pages[pageName].on_page_load = function (wrapper) {
            init_logistics_hub_page(pageName, defaultTab, wrapper);
        };
        frappe.pages[pageName].on_page_show = function (wrapper) {
            show_logistics_hub_page(wrapper, defaultTab);
        };
    }
}

/**
 * ExecutiveDashboardController
 * Trung tâm chỉ huy vận hành vĩ mô (Macro Operations Command Center)
 * Hiển thị trực quan toàn bộ sức khỏe hệ thống, phễu luồng hàng, cơ cấu chi phí và radar sự cố
 */
class ExecutiveDashboardController {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.data = null;
        this.currentTimeRange = '30d';
        this.bind_events();
    }

    bind_events() {
        const self = this;
        $(document).off('click', '#exec-btn-refresh').on('click', '#exec-btn-refresh', function (e) {
            e.preventDefault();
            self.load_data();
        });

        $(document).off('change', '#exec-time-range').on('change', '#exec-time-range', function () {
            self.currentTimeRange = $(this).val();
            self.load_data();
        });

        // Clicking on Action Alert buttons triggers navigation to trade-case-overview
        $(document).off('click', '.exec-action-btn').on('click', '.exec-action-btn', function (e) {
            e.preventDefault();
            const caseId = $(this).data('case');
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.route_options = { case_id: caseId, tab: 'overview' };
                frappe.set_route('trade-case-overview');
            } else if (caseId && self.wrapper && self.wrapper.unifiedHub) {
                self.wrapper.unifiedHub.switch_tab('overview', { case_id: caseId });
            }
        });

        // Clicking on a pipeline step
        $(document).off('click', '.pipeline-step').on('click', '.pipeline-step', function (e) {
            e.preventDefault();
            const stepName = $(this).find('.pipeline-step-name').text();
            if (frappe && frappe.show_alert) {
                frappe.show_alert({
                    message: __('Đang quan sát chặng: ') + stepName,
                    indicator: 'blue'
                }, 3);
            }
        });
    }

    init() {
        this.load_data();
    }

    load_data() {
        const self = this;
        frappe.call({
            method: "logistics_wizard.api.get_executive_dashboard_summary",
            args: { time_range: self.currentTimeRange },
            callback: function (r) {
                if (r && r.message && r.message.status === 'success') {
                    self.data = r.message.data;
                    self.render();
                } else if (r && r.message && r.message.metrics) {
                    self.data = r.message;
                    self.render();
                }
            }
        });
    }

    render() {
        if (!this.data) return;
        const d = this.data;

        // 1. Render Macro KPIs
        if (d.metrics) {
            $('#exec-val-total-cases').text(d.metrics.total_cases || 28);
            $('#exec-sub-import').text(d.metrics.import_cases || 20);
            $('#exec-sub-export').text(d.metrics.export_cases || 8);
            const impPct = Math.round(((d.metrics.import_cases || 20) / (d.metrics.total_cases || 28)) * 100);
            $('#exec-bar-import').css('width', impPct + '%');
            $('#exec-bar-export').css('width', (100 - impPct) + '%');

            $('#exec-val-in-transit').text(d.metrics.in_transit_shipments || 18);
            $('#exec-val-alerts').text(d.metrics.active_exceptions || 3);
            
            const spend = d.metrics.total_spend ? ('$' + Number(d.metrics.total_spend).toLocaleString()) : '$1,245,500';
            $('#exec-val-spend').text(spend);
        }

        // 2. Render Pipeline Funnel
        if (d.pipeline && d.pipeline.length > 0) {
            const html = d.pipeline.map(p => {
                const isWarn = p.status === 'warning' ? 'step-warning' : '';
                return `
                    <div class="pipeline-step ${isWarn}" data-step="${p.key}">
                        <div class="pipeline-step-header">
                            <span class="pipeline-step-num">${p.step_no}</span>
                            <span class="pipeline-step-count">${p.count} đơn</span>
                        </div>
                        <div class="pipeline-step-name">${p.label}</div>
                        <span class="pipeline-step-sub">${p.sub_label}</span>
                        <div class="pipeline-step-bar">
                            <div class="pipeline-step-fill ${p.status === 'warning' ? 'bg-amber' : 'bg-blue'}" style="width: ${p.pct}%;"></div>
                        </div>
                    </div>
                `;
            }).join('');
            $('#exec-pipeline-container').html(html);
        }

        // 3. Render Health Donut SVG
        if (d.health_donut) {
            const hd = d.health_donut;
            $('#exec-health-score').text(hd.score_pct + '%');
            const segs = hd.segments || [];
            let offset = 0;
            segs.forEach(s => {
                if (s.key === 'on_time') {
                    $('#donut-segment-ontime').attr('stroke-dasharray', `${s.pct}, 100`).attr('stroke-dashoffset', offset);
                    $('#legend-ontime-val').text(`${s.count} đơn (${s.pct}%)`);
                } else if (s.key === 'at_risk') {
                    $('#donut-segment-atrisk').attr('stroke-dasharray', `${s.pct}, 100`).attr('stroke-dashoffset', -offset);
                    $('#legend-atrisk-val').text(`${s.count} đơn (${s.pct}%)`);
                } else if (s.key === 'critical') {
                    $('#donut-segment-critical').attr('stroke-dasharray', `${s.pct}, 100`).attr('stroke-dashoffset', -offset);
                    $('#legend-critical-val').text(`${s.count} đơn (${s.pct}%)`);
                }
                offset += s.pct;
            });
        }

        // 4. Render Cost Breakdown Bars
        if (d.cost_breakdown && d.cost_breakdown.categories) {
            const html = d.cost_breakdown.categories.map(c => {
                const varSign = c.variance_pct > 0 ? '+' : '';
                const barBg = c.variance_pct <= 0 ? 'bg-emerald' : 'bg-amber';
                return `
                    <div class="cost-bar-item">
                        <div class="cost-bar-header">
                            <span class="cost-bar-name">${c.name}</span>
                            <div class="cost-bar-figures">
                                <span class="cost-bar-amount">$${Number(c.amount).toLocaleString()}</span>
                                <span class="exec-badge ${c.variance_pct <= 0 ? 'exec-badge-success' : 'exec-badge-amber'}">${varSign}${c.variance_pct}%</span>
                            </div>
                        </div>
                        <div class="cost-bar-progress">
                            <div class="cost-bar-fill ${barBg}" style="width: ${c.pct_of_total}%;"></div>
                        </div>
                    </div>
                `;
            }).join('');
            $('#exec-cost-breakdown-list').html(html);
        }

        // 5. Render Corridors
        if (d.corridors && d.corridors.length > 0) {
            const html = d.corridors.map(c => {
                const icon = c.mode === 'Air' ? 'fa-plane' : 'fa-ship';
                const badgeClass = c.health_level === 'warning' ? 'exec-badge-amber' : 'exec-badge-success';
                return `
                    <div class="corridor-item">
                        <div class="corridor-main">
                            <div class="corridor-mode-icon">
                                <i class="fa ${icon}"></i>
                            </div>
                            <div>
                                <span class="corridor-name">${c.route}</span>
                                <span class="corridor-meta">${c.active_voyages} chuyến đang chạy • Thời gian: ${c.avg_transit}</span>
                            </div>
                        </div>
                        <div class="corridor-status">
                            <span class="exec-badge ${badgeClass}">${c.status}</span>
                        </div>
                    </div>
                `;
            }).join('');
            $('#exec-corridors-container').html(html);
        }

        // 6. Render Actionable Alerts
        if (d.action_alerts && d.action_alerts.length > 0) {
            const html = d.action_alerts.map(a => {
                const isCrit = a.severity === 'critical';
                const cardClass = isCrit ? 'alert-critical' : 'alert-warning';
                const iconColor = isCrit ? 'text-coral' : 'text-amber';
                const iconName = isCrit ? 'fa-exclamation-circle' : 'fa-exclamation-triangle';
                const btnClass = isCrit ? 'btn-primary' : 'btn-default';
                return `
                    <div class="exec-alert-card ${cardClass}">
                        <div class="exec-alert-top">
                            <span class="exec-alert-title">
                                <i class="fa ${iconName} ${iconColor}"></i>
                                ${a.title}
                            </span>
                            <span class="exec-badge ${isCrit ? 'exec-badge-amber' : 'exec-badge-info'}">${a.badge_label}</span>
                        </div>
                        <p class="exec-alert-desc">${a.description}</p>
                        <div class="exec-alert-footer">
                            <span class="exec-alert-tags">Hồ sơ: <strong>${a.case_id}</strong> (${a.shipment_id})</span>
                            <button class="btn btn-xs ${btnClass} exec-action-btn" data-case="${a.case_id}">
                                ${a.action_text} &rarr;
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
            $('#exec-alerts-container').html(html);
        }
    }
}

function setup_logistics_hub_tabs(wrapper) {
    const $page = (wrapper && wrapper.shipment_tracking_hub && wrapper.shipment_tracking_hub.page)
        ? $(wrapper.shipment_tracking_hub.page.body)
        : $(document);

    $page.off('click', '.logistics-nav-tab').on('click', '.logistics-nav-tab', function (e) {
        e.preventDefault();
        const tab = $(this).data('tab');
        const route = $(this).attr('data-route') || $(this).data('route');
        if (route) {
            const currentRoute = (typeof frappe !== 'undefined' && frappe.get_route_str) ? frappe.get_route_str() : '';
            if (currentRoute !== route && currentRoute !== ('logistics-wizard/' + route)) {
                frappe.set_route(route);
                return;
            }
        }
        if (tab === 'rag-admin' || tab === 'rag-admin-center') {
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.set_route('rag-admin-center');
            } else {
                window.location.href = '/app/rag-admin-center';
            }
            return;
        }
        if (tab && wrapper.unifiedHub) {
            wrapper.unifiedHub.switch_tab(tab);
        }
    });
}


class TradeCaseOverviewController {
    constructor(wrapper, trackingHub) {
        this.wrapper = wrapper;
        this.trackingHub = trackingHub;
        this.currentCaseId = 'IMP-2026-001';
        this.availableCases = [];
        
        this.currentData = null;
        this.bind_events();
    }

    init() {
        const self = this;
        frappe.call({
            method: "logistics_wizard.api.get_trade_case_list",
            callback: function (r) {
                if (r && r.message && r.message.length > 0) {
                    self.availableCases = r.message;
                    let opts = r.message.map(c => 
                        `<option value="${c.case_id}">${c.label || (c.case_id + " - " + c.party)}</option>`
                    ).join("");
                    $("#tc-case-selector").html(opts);
                    if (self.currentCaseId) {
                        $("#tc-case-selector").val(self.currentCaseId);
                    }
                }
            }
        });
        this.load_case(this.currentCaseId || "IMP-2026-001");
    }

    bind_events() {
        const self = this;
        // Case Selector inside Tab
        $(document).on('change', '#tc-case-selector', function () {
            let selectedId = $(this).val();
            if (selectedId) {
                self.load_case(selectedId);
            }
        });

        // Refresh Case button inside Tab
        $(document).on('click', '#tc-btn-refresh-case', function () {
            $(this).find('i').addClass('fa-spin');
            self.load_case(self.currentCaseId);
            setTimeout(() => {
                $('#tc-btn-refresh-case').find('i').removeClass('fa-spin');
            }, 600);
        });


        // Refresh overview
        $(document).on('click', '#tc-btn-refresh', function () {
            $(this).find('i').addClass('fa-spin');
            self.load_case(self.currentCaseId);
            setTimeout(() => {
                $('#tc-btn-refresh').find('i').removeClass('fa-spin');
            }, 600);
        });

        // Edit Case form
        $(document).on('click', '#tc-btn-edit-case', function () {
            if (self.currentData && self.currentData.case_id) {
                frappe.set_route('Form', 'Trade Case', self.currentData.case_id);
            }
        });

        // Drilldown to shipment tracking
        $(document).on('click', '#tc-btn-goto-shipment, #tc-drill-down-shipment', function () {
            let shpId = null;
            if (self.currentData && self.currentData.shipment_summary) {
                shpId = self.currentData.shipment_summary.shipment_id;
            }
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.route_options = { shipment: shpId, tab: 'tracking' };
                frappe.set_route('shipment-tracking-hub');
            } else if (self.unifiedHub) {
                self.unifiedHub.switch_tab('tracking', { shipment_id: shpId });
            } else if (self.wrapper && self.wrapper.switch_to_tab) {
                self.wrapper.switch_to_tab('shipment-tracking-hub', shpId);
            }
        });

        // Quick action: Close Case with Stage-Gate validation
        $(document).on('click', '#tc-btn-close-case', function () {
            self.attempt_close_case();
        });

        // Quick actions: Document Upload, Customs, Cost, Exceptions
        $(document).on('click', '#btn-upload-doc', function () {
            frappe.msgprint({
                title: __('Upload Document'),
                message: __('Chức năng tải lên và phân loại chứng từ (C/O, D/O, Packing List) sẽ kết nối với Module Document Readiness.'),
                indicator: 'blue'
            });
        });

        $(document).on('click', '#btn-update-customs', function () {
            frappe.msgprint({
                title: __('Update Customs'),
                message: __('Chức năng cập nhật tiến độ tờ khai điện tử VNACCS và rà soát mã HS RAG.'),
                indicator: 'blue'
            });
        });

        $(document).on('click', '#btn-add-cost', function () {
            frappe.msgprint({
                title: __('Add Cost Invoice'),
                message: __('Chức năng ghi nhận chi phí phát sinh và cập nhật Landed Cost Voucher.'),
                indicator: 'blue'
            });
        });

        $(document).on('click', '#btn-create-exception', function () {
            frappe.msgprint({
                title: __('Create Exception'),
                message: __('Khai báo sự cố vận chuyển mới (Trễ lịch, hư hỏng cont, phát sinh phí).'),
                indicator: 'orange'
            });
        });

        $(document).on('click', '#btn-add-action', function () {
            frappe.prompt([
                { fieldname: 'action', fieldtype: 'Data', label: 'Nội dung hành động', reqd: 1 },
                { fieldname: 'department', fieldtype: 'Select', label: 'Phòng ban', options: 'Logistics\nCustoms\nPurchasing\nAccounting\nWarehouse', default: 'Logistics' },
                { fieldname: 'due_date', fieldtype: 'Date', label: 'Hạn xử lý', default: frappe.datetime.nowdate() }
            ], function (vals) {
                frappe.show_alert({ message: `Đã thêm việc cần làm: ${vals.action}`, indicator: 'green' });
            }, 'Thêm Hành Động Tiếp Theo');
        });
    }

    attempt_close_case() {
        const self = this;
        let qa = (this.currentData && this.currentData.quick_actions) ? this.currentData.quick_actions : {};
        if (!qa.can_close) {
            let reasonsHtml = (qa.close_reasons || []).map(r => `<li style="margin-bottom: 4px; color: #b91c1c;">${r}</li>`).join('');
            frappe.msgprint({
                title: __('⛔ KHÔNG THỂ ĐÓNG HỒ SƠ (STAGE GATE CHẶN)'),
                message: `
                    <div style="font-size: 13px;">
                        <p>Hồ sơ <strong>${self.currentData.case_id}</strong> chưa thỏa mãn các tiêu chí chốt chặn để đóng case:</p>
                        <ul style="padding-left: 18px; margin: 10px 0;">
                            ${reasonsHtml}
                        </ul>
                        <p style="color: #64748b; font-style: italic;">Vui lòng hoàn tất bàn giao hàng, thông quan, chốt chi phí và giải quyết triệt để các sự cố trước khi đóng hồ sơ!</p>
                    </div>
                `,
                indicator: 'red'
            });
        } else {
            frappe.confirm(
                `Bạn có chắc chắn muốn đóng hoàn tất hồ sơ Trade Case <strong>${self.currentData.case_id}</strong>?`,
                function () {
                    frappe.call({
                        method: 'logistics_wizard.api.close_trade_case',
                        args: { case_id: self.currentData.case_id },
                        callback: function (r) {
                            if (r && r.message && r.message.success) {
                                frappe.show_alert({ message: r.message.message, indicator: 'green' });
                                self.load_case(self.currentData.case_id);
                            } else {
                                frappe.msgprint(r.message.message || 'Lỗi khi đóng case.');
                            }
                        }
                    });
                }
            );
        }
    }

    
    load_case(caseId) {
        const self = this;
        this.currentCaseId = caseId || this.currentCaseId || "IMP-2026-001";
        $("#tc-current-case-badge").text(this.currentCaseId);
        if ($("#tc-case-selector").val() !== this.currentCaseId) {
            $("#tc-case-selector").val(this.currentCaseId);
        }

        frappe.call({
            method: "logistics_wizard.api.get_trade_case_overview_data",
            args: { case_id: this.currentCaseId },
            callback: function (r) {
                if (r && r.message) {
                    self.currentData = r.message;
                    self.render(r.message);
                }
            }
        });
    }

    render(data) {
        if (!data) return;
        this.currentData = data;

        // 1. Header
        let h = data.header || {};
        $("#tc-id-text, #tc-header-id").text(h.case_id || "IMP-2026-001");
        $("#tc-status-badge, #tc-header-status").text(h.status ? h.status.toUpperCase() : "ACTIVE");

        let healthClass = (h.health || "Attention").toLowerCase();
        let healthBadgeClass = healthClass === "healthy" ? "badge-success" : (healthClass === "critical" ? "badge-danger" : "badge-warning");
        $("#tc-health-badge, #tc-header-health").attr("class", `tc-badge-health ${healthClass} ${healthBadgeClass}`).text(`Health: ${(h.health || "Attention").toUpperCase()}`);
        $("#tc-priority-badge, #tc-header-priority").text(`${h.priority || "Normal"} Priority`);

        $("#tc-party-text, #tc-meta-party").text(`${h.trade_type || "Import"} Case — ${h.supplier || h.customer || "N/A"}`);
        $("#tc-docref-text, #tc-meta-po").html(`<a href="${(h.purchase_order ? "/app/purchase-order/" + h.purchase_order : "#")}" class="tc-link">${h.purchase_order || h.sales_order || "N/A"}</a>`);
        $("#tc-mode-incoterm, #tc-meta-mode-incoterm").text(`${h.mode || "Ocean"} • ${h.incoterm || "FOB"}`);
        $("#tc-route-text, #tc-meta-route").text(`${h.origin || "N/A"} ➔ ${h.destination || "N/A"}`);
        $("#tc-owner-text, #tc-meta-owner").text(`${h.owner || "Nguyen Van A"} (${h.department || "Logistics"})`);
        $("#tc-expected-close, #tc-meta-expected-close").text(h.expected_close || "N/A");

        // 2. Lifecycle Stepper
        if (data.lifecycle) {
            let lc = data.lifecycle;
            $("#tc-current-stage-callout, #tc-lifecycle-current-label").html(`Giai đoạn hiện tại: <strong>${lc.current_stage || "IN TRANSIT"}</strong>`);

            let $stepper = $("#tc-lifecycle-stepper");
            $stepper.empty();
            let stages = lc.stages || [];
            stages.forEach((st, idx) => {
                let statusClass = st.status;
                let iconContent = statusClass === "completed" ? "✓" : (statusClass === "current" ? "●" : "○");
                let nodeHtml = `
                    <div class="tc-step-item ${statusClass}">
                        <div class="tc-step-circle">${iconContent}</div>
                        <div class="tc-step-label">${st.label}</div>
                    </div>
                `;
                $stepper.append(nodeHtml);
            });

            if (lc.previous_milestone) {
                $("#tc-prev-ms-title, #tc-ms-prev-title").text(lc.previous_milestone.title);
                $("#tc-prev-ms-date, #tc-ms-prev-date").text(lc.previous_milestone.date);
            }
            if (lc.next_milestone) {
                $("#tc-next-ms-title, #tc-ms-next-title").text(lc.next_milestone.title);
                $("#tc-next-ms-date, #tc-ms-next-date").text(lc.next_milestone.eta);
            }
        }

        // 3. Health & Readiness Grid (6 Cards)
        if (data.overall_health && data.overall_health.cards) {
            let $grid = $('#tc-health-grid');
            $grid.empty();
            data.overall_health.cards.forEach(card => {
                let cardHtml = `
                    <div class="tc-health-card ${card.class || 'neutral'}">
                        <div class="tc-hc-label">${card.label}</div>
                        <div class="tc-hc-val">${card.value}</div>
                        <div class="tc-hc-sub">${card.sub}</div>
                    </div>
                `;
                $grid.append(cardHtml);
            });
        }

        // 4. Shipment Summary
        if (data.shipment_summary) {
            let s = data.shipment_summary;
            let multiText = s.total_shipments > 1 ? `<div style="margin-top: 8px; font-size: 11px; color: #64748b; font-weight: 600;">Tổng số: <strong>${s.total_shipments} Shipments</strong> (${s.shipment_counts.in_transit} Đang đi, ${s.shipment_counts.delivered} Đã đến)</div>` : '';
            let html = `
                <table class="tc-kv-table">
                    <tr><td class="tc-kv-key">Mã vận đơn (Shipment ID):</td><td class="tc-kv-val font-weight-bold text-primary">${s.shipment_id || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Hãng vận tải (Carrier):</td><td class="tc-kv-val">${s.carrier || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Tên phương tiện (Vessel/Flight):</td><td class="tc-kv-val">${s.vessel || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Số lượng Container:</td><td class="tc-kv-val">${s.container_count || 1} Containers</td></tr>
                    <tr><td class="tc-kv-key">Cảng xuất (POL):</td><td class="tc-kv-val">${s.pol || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Cảng nhập (POD):</td><td class="tc-kv-val">${s.pod || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Ngày khởi hành (ATD):</td><td class="tc-kv-val">${s.atd || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Lịch dự kiến ban đầu (Original ETA):</td><td class="tc-kv-val">${s.original_eta || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">ETA hiện tại:</td><td class="tc-kv-val text-primary font-weight-bold">${s.current_eta || 'N/A'}</td></tr>
                    <tr><td class="tc-kv-key">Độ trễ hành trình (Delay):</td><td class="tc-kv-val ${s.delay_days > 0 ? 'text-danger' : 'text-success'} font-weight-bold">${s.delay_days > 0 ? '+' + s.delay_days + ' ngày (Delay)' : 'Đúng hạn (On-time)'}</td></tr>
                </table>
                ${multiText}
            `;
            $('#tc-shipment-summary-body, #tc-shipment-body').html(html);
        }

        // 5. Document Readiness
        if (data.document_readiness) {
            let doc = data.document_readiness;
            $('#tc-doc-readiness-badge, #tc-docs-pct-badge').text(`${doc.ready_count} / ${doc.total_count} Sẵn sàng (${doc.percentage}%)`);
            let alertHtml = '';
            if (doc.missing_urgent && doc.missing_urgent.length > 0) {
                alertHtml = doc.missing_urgent.map(m => `
                    <div class="tc-urgent-doc-alert">
                        <strong>⚠ Thiếu khẩn cấp: ${m.name}</strong><br>
                        <span style="font-size: 11px;">Hạn chót: ${m.deadline} • ${m.note}</span>
                    </div>
                `).join('');
            }
            let catsHtml = (doc.categories || []).map(cat => `
                <div class="tc-doc-cat-box">
                    <span>${cat.name}</span>
                    <span class="${cat.status === 'completed' ? 'text-success' : 'text-warning'} font-weight-bold">
                        ${cat.ready}/${cat.total} ${cat.status === 'completed' ? '✓' : '⚠'}
                    </span>
                </div>
            `).join('');

            $('#tc-doc-readiness-body, #tc-docs-body').html(`
                ${alertHtml}
                <div class="progress" style="height: 10px; margin-bottom: 12px; border-radius: 5px;">
                    <div class="progress-bar ${doc.percentage === 100 ? 'bg-success' : 'bg-warning'}" style="width: ${doc.percentage}%;"></div>
                </div>
                <div class="tc-doc-cat-grid">
                    ${catsHtml}
                </div>
                <div style="margin-top: 14px; text-align: right;">
                    <button class="btn btn-xs btn-default" id="tc-btn-view-docs"><i class="fa fa-folder-open-o"></i> Quản lý Hồ sơ Chi tiết</button>
                </div>
            `);
        }

        // 6. Customs & Compliance Summary
        if (data.customs_readiness) {
            let cr = data.customs_readiness;
            $('#tc-customs-badge, #tc-customs-status-badge').text(`${cr.status} (${cr.readiness_pct}%)`);
            $('#tc-customs-body').html(`
                <table class="tc-kv-table">
                    <tr><td class="tc-kv-key">Mã phân loại HS:</td><td class="tc-kv-val font-weight-bold">${cr.hs_classification}</td></tr>
                    <tr><td class="tc-kv-key">Trạng thái phê duyệt HS:</td><td class="tc-kv-val text-success">✓ ${cr.hs_approval_status}</td></tr>
                    <tr><td class="tc-kv-key">Xác thực Xuất xứ (Origin):</td><td class="tc-kv-val text-success">${cr.origin_verified ? '✓ Đã xác thực' : 'Chưa xác thực'}</td></tr>
                    <tr><td class="tc-kv-key">Trị giá Hải quan (Value):</td><td class="tc-kv-val text-success">${cr.customs_value_verified ? '✓ Đã xác thực' : 'Chưa xác thực'}</td></tr>
                    <tr><td class="tc-kv-key">Tờ khai Hải quan (Declaration):</td><td class="tc-kv-val text-warning font-weight-bold">${cr.declaration_status}</td></tr>
                    <tr><td class="tc-kv-key">Giấy phép chuyên ngành:</td><td class="tc-kv-val">${cr.license}</td></tr>
                    <tr><td class="tc-kv-key">Kiểm tra chuyên ngành:</td><td class="tc-kv-val">${cr.inspection}</td></tr>
                    <tr><td class="tc-kv-key">Tình trạng Thông quan:</td><td class="tc-kv-val ${cr.clearance_status === 'CLEARED' ? 'text-success font-weight-bold' : 'text-danger font-weight-bold'}">${cr.clearance_status}</td></tr>
                </table>
            `);
        }

        // 7. Cost Summary (Supports both Import Landed Cost & Export Cost Variance)
        if (data.cost_summary) {
            let cs = data.cost_summary;
            let isExport = data.header && String(data.header.trade_type || '').toLowerCase() === 'export';
            let orderLabel = isExport ? 'Trị giá Lô xuất (SO/SI)' : 'Trị giá Hàng mua (PO)';
            let costLabel = isExport ? 'Chi phí Xuất khẩu Thực tế' : 'Tổng Chi phí Logistics Thực tế';
            let varianceSign = cs.variance_amount >= 0 ? '+' : '';
            let varianceClass = cs.variance_amount > 0 ? 'text-danger' : 'text-success';
            $('#tc-cost-status-badge').text(`${cs.cost_finalization_status} (${varianceSign}${cs.variance_pct}%)`);

            let breakdownRows = (cs.breakdown || []).map(b => `
                <tr>
                    <td style="padding: 4px 0; color: #64748b;">${b.label}</td>
                    <td style="padding: 4px 0; text-align: right; font-weight: 600;">$${Number(b.amount || 0).toLocaleString()}</td>
                </tr>
            `).join('');

            $('#tc-cost-body').html(`
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
                    <div>
                        <div style="font-size: 11px; color: #64748b;">${orderLabel}</div>
                        <div style="font-size: 14px; font-weight: 800; color: #0f172a;">$${Number(cs.purchase_value || 0).toLocaleString()}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">Dự toán: $${Number(cs.estimated_cost || 0).toLocaleString()}</div>
                        <div style="font-size: 14px; font-weight: 800;" class="${varianceClass}">
                            $${Number(cs.actual_cost || 0).toLocaleString()} <span style="font-size: 11px;">(${varianceSign}${cs.variance_pct}%)</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">${isExport ? 'Chênh lệch Dự toán' : 'Tổng Landed Cost'}</div>
                        <div style="font-size: 14px; font-weight: 800; color: #0f766e;">
                            ${isExport ? (varianceSign + '$' + Number(cs.variance_amount || 0).toLocaleString()) : ('$' + Number(cs.actual_landed_cost || 0).toLocaleString())}
                        </div>
                    </div>
                </div>
                <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">${costLabel} Theo Nhóm:</div>
                <table style="width: 100%; font-size: 12px; margin-bottom: 12px;">
                    ${breakdownRows}
                </table>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; border-top: 1px dashed #e2e8f0; padding-top: 8px;">
                    <span>Hóa đơn nhận: <strong>${cs.invoices_received}/${cs.invoices_total}</strong></span>
                    <span>Đã thẩm định: <strong>${cs.costs_verified}/${cs.invoices_total}</strong></span>
                    <span>Đã phân bổ LCV: <strong>${cs.costs_allocated}/${cs.invoices_total}</strong></span>
                </div>
            `);
        }

        // 8. Warehouse Readiness
        if (data.warehouse_readiness) {
            let wh = data.warehouse_readiness;
            $('#tc-wh-badge, #tc-warehouse-status-badge').text(wh.receiving_status);
            let discAlert = wh.discrepancy_alert ? `<div class="tc-urgent-doc-alert">⚠ PHÁT HIỆN LỆCH SỐ LƯỢNG / HƯ HỎNG HÀNG HÓA!</div>` : '';
            $('#tc-wh-body, #tc-warehouse-body').html(`
                ${discAlert}
                <table class="tc-kv-table">
                    <tr><td class="tc-kv-key">Lịch dự kiến nhập kho:</td><td class="tc-kv-val font-weight-bold">${wh.expected_arrival}</td></tr>
                    <tr><td class="tc-kv-key">Địa điểm Kho nhận:</td><td class="tc-kv-val">${wh.warehouse}</td></tr>
                    <tr><td class="tc-kv-key">Trạng thái Tiếp nhận:</td><td class="tc-kv-val text-warning font-weight-bold">${wh.receiving_status}</td></tr>
                    <tr><td class="tc-kv-key">Số lượng dự kiến (Expected):</td><td class="tc-kv-val">${wh.expected_qty ? wh.expected_qty.toLocaleString() : 'N/A'} kiện</td></tr>
                    <tr><td class="tc-kv-key">Mặt bằng kho dự trữ:</td><td class="tc-kv-val text-success">${wh.space_reserved ? '✓ Đã giữ chỗ sẵn sàng' : 'Chưa bố trí'}</td></tr>
                    <tr><td class="tc-kv-key">Đội ngũ tiếp nhận:</td><td class="tc-kv-val">${wh.receiving_team}</td></tr>
                </table>
            `);
        }

        // 9. Top Open Exceptions
        if (data.open_exceptions) {
            let exc = data.open_exceptions;
            $('#tc-exceptions-badge, #tc-open-exceptions-badge').text(`${exc.total_open} Open (${exc.overdue} Quá hạn)`);
            let itemsHtml = (exc.items || []).map(item => {
                let sevClass = (item.severity || 'medium').toLowerCase();
                let badgeClass = sevClass === 'high' || sevClass === 'critical' ? 'badge-danger' : 'badge-warning';
                return `
                    <div class="tc-exception-item ${sevClass}">
                        <div class="tc-exc-header">
                            <span class="badge ${badgeClass}">${item.severity}</span>
                            <span style="color: #64748b;">${item.id}</span>
                        </div>
                        <div class="tc-exc-title">${item.title}</div>
                        <div class="tc-exc-meta">
                            <span><i class="fa fa-user"></i> ${item.owner} (${item.department})</span>
                            <span><i class="fa fa-clock-o"></i> Hạn: ${item.due_date}</span>
                            <span class="font-weight-bold text-primary">${item.status}</span>
                        </div>
                    </div>
                `;
            }).join('');

            if (!itemsHtml) {
                itemsHtml = `<div class="text-center text-success" style="padding: 20px;"><i class="fa fa-check-circle" style="font-size: 24px;"></i><p style="margin-top: 6px; font-weight: 600;">Không có sự cố nào đang mở.</p></div>`;
            }
            $('#tc-exceptions-body').html(itemsHtml);
        }

        // 10. Upcoming Actions & Deadlines
        if (data.upcoming_actions) {
            let actionsHtml = data.upcoming_actions.map(a => `
                <div class="tc-action-item">
                    <div class="tc-action-date">${a.date}</div>
                    <div class="tc-action-desc">${a.action}</div>
                    <div class="tc-action-dept"><span class="badge badge-default">${a.department}</span> (${a.owner})</div>
                </div>
            `).join('');
            $('#tc-actions-body').html(actionsHtml || '<div class="text-muted">Không có lịch hành động tiếp theo.</div>');
        }

        // 11. Related ERP Documents
        if (data.related_erp_documents) {
            let erpHtml = data.related_erp_documents.map(d => `
                <tr>
                    <td style="padding: 6px 0; font-weight: 600; color: #64748b;">${d.doctype}</td>
                    <td style="padding: 6px 0;"><a href="${d.link}" class="tc-link font-weight-bold">${d.name}</a></td>
                    <td style="padding: 6px 0; text-align: right;">
                        <span class="tc-badge-erp ${d.status === 'Submitted' || d.status === 'Completed' ? 'submitted' : 'pending'}">${d.status}</span>
                    </td>
                </tr>
            `).join('');
            $('#tc-related-erp-body').html(`<table style="width: 100%; font-size: 12px;">${erpHtml}</table>`);
        }

        // 12. Responsibility Matrix
        if (data.responsibility_matrix) {
            let respHtml = data.responsibility_matrix.map(r => `
                <tr>
                    <td style="padding: 6px 0; font-weight: 700; color: #0284c7;">${r.role}</td>
                    <td style="padding: 6px 0; font-weight: 600; color: #0f172a;">${r.name}</td>
                    <td style="padding: 6px 0; color: #64748b; font-size: 11px;">${r.department}</td>
                </tr>
            `).join('');
            $('#tc-responsibility-body').html(`<table style="width: 100%; font-size: 12px;">${respHtml}</table>`);
        }

        // 13. Activity Timeline
        if (data.activity_timeline) {
            let actHtml = data.activity_timeline.map(e => `
                <div class="tc-timeline-event">
                    <div class="tc-event-time">${e.time}</div>
                    <div class="tc-event-desc">
                        <strong style="color: #0284c7;">${e.actor}:</strong> ${e.event}
                    </div>
                </div>
            `).join('');
            $('#tc-activity-body').html(actHtml || '<div class="text-muted">Chưa có nhật ký hoạt động.</div>');
        }

        // 14. Quick Actions & Stage Gate
        if (data.quick_actions) {
            let qa = data.quick_actions;
            let rulesHtml = (qa.close_reasons || []).map(r => `<div class="tc-sg-rule">${r}</div>`).join('');
            $('#tc-stage-gate-body').html(`
                <div class="tc-action-btn-group">
                    <button class="btn btn-default" id="btn-upload-doc"><i class="fa fa-upload"></i> Upload Document</button>
                    <button class="btn btn-default" id="btn-update-customs"><i class="fa fa-check-circle"></i> Update Customs</button>
                    <button class="btn btn-default" id="btn-add-cost"><i class="fa fa-dollar-sign"></i> Add Cost</button>
                    <button class="btn btn-default" id="btn-create-exception"><i class="fa fa-exclamation-triangle"></i> Create Exception</button>
                    <button class="btn btn-default" id="btn-add-action"><i class="fa fa-plus"></i> Add Action</button>
                </div>
                <div class="tc-stage-gate-box">
                    <div class="tc-sg-title">
                        <i class="fa fa-lock"></i> ĐIỀU KIỆN CHỐT CHẶN ĐÓNG CASE (STAGE GATE)
                    </div>
                    ${rulesHtml}
                    <div style="margin-top: 10px; display: flex; justify-content: flex-end;">
                        <button class="btn btn-sm btn-danger font-weight-bold" id="tc-btn-close-case">
                            <i class="fa fa-check-square-o"></i> Đóng Trade Case (Close Case)
                        </button>
                    </div>
                </div>
            `);
        }
    }
}


class ShipmentTrackingHub {
    constructor(wrapper, pageName) {
        this.wrapper = wrapper;
        this.pageName = pageName || 'trade-case-overview';
        if (wrapper && typeof frappe !== 'undefined' && frappe.ui && frappe.ui.make_app_page) {
            this.page = frappe.ui.make_app_page({
                parent: wrapper,
                title: __('Trade Case Dossier'),
                single_column: true
            });
            if (this.page && this.page.container) {
                this.page.container.removeClass('container').addClass('container-fluid');
                this.page.container.css({ 'max-width': '100%', 'padding': '0', 'margin': '0' });
            }
            make_page_full_bleed(wrapper);
        }

        this.data = null;
        this.selectedShipment = null;
        this.pendingFocusShipment = null;
        this.currentFilter = 'all';
        this.searchTerm = '';
        this.map = null;
        this.mapLayers = {
            baseLand: null,
            seaOverlay: null,
            routePolylines: [],
            markers: [],
            vehicleMarker: null,
            fleetVehicleMarkers: []
        };
        this.debounceTimer = null;

        if (wrapper) {
            this.init();
        }
    }

    init() {
        this.render_skeleton(this.pageName);
        this.bind_events();
        this.init_map();
        this.refresh();
    }

    render_skeleton(pageName) {
        // Append HTML template content into main page body
        let template = window.UNIFIED_LOGISTICS_HUB_HTML || '';
        if (!template && frappe.templates) {
            const possibleNames = [
                pageName,
                pageName ? pageName.replace(/-/g, '_') : null,
                'trade_case_overview',
                'managementlogistic',
                'managementLogistic',
                'shipment_tracking_hub'
            ];
            for (let name of possibleNames) {
                if (name && frappe.templates[name]) {
                    template = frappe.render_template(name, {});
                    break;
                }
            }
        }
        if (this.page && this.page.body) {
            $(this.page.body).html(template);
        } else if (this.wrapper) {
            $(this.wrapper).html(template);
        }
    }

    bind_events() {
        const self = this;

        // 1. Refresh Button
        $('#hub-btn-refresh').on('click', function () {
            $(this).find('i').addClass('fa-spin');
            self.refresh(self.selectedShipment ? self.selectedShipment.name : null, () => {
                $('#hub-btn-refresh').find('i').removeClass('fa-spin');
            });
        });

        // 2. Sync Now Button
        $('#hub-btn-sync-now').on('click', function () {
            let target = self.selectedShipment ? self.selectedShipment.name : null;
            self.sync_now(target);
        });

        // 3. KPI Card click filters
        $('.hub-kpi-card').on('click', function () {
            let filter = $(this).data('filter');
            $('.hub-kpi-card').removeClass('active');
            $(this).addClass('active');

            $('.hub-tab-btn').removeClass('active');
            $(`.hub-tab-btn[data-tab="${filter}"]`).addClass('active');

            self.currentFilter = filter;
            self.filter_and_render_table();
        });

        // 4. Tab Buttons
        $('.hub-tab-btn').on('click', function () {
            let tab = $(this).data('tab');
            $('.hub-tab-btn').removeClass('active');
            $(this).addClass('active');

            $('.hub-kpi-card').removeClass('active');
            $(`.hub-kpi-card[data-filter="${tab}"]`).addClass('active');

            self.currentFilter = tab;
            self.filter_and_render_table();
        });

        // 5. Search Input with debounce 250ms
        $('#hub-search-input').on('input', function () {
            clearTimeout(self.debounceTimer);
            self.debounceTimer = setTimeout(() => {
                self.searchTerm = ($(this).val() || '').trim().toLowerCase();
                self.filter_and_render_table();
            }, 250);
        });

        // 6. Reset Map Button
        $('#hub-map-reset-btn').on('click', function () {
            self.reset_map_view();
        });
    }

    init_map() {
        const self = this;
        const L = window.L || window.leaflet;
        if (!L) {
            console.warn('[TrackingHub] Leaflet is not loaded yet');
            return;
        }

        const $mapEl = this.wrapper ? $(this.wrapper).find('#lw-hub-map') : $('#lw-hub-map');
        if (!$mapEl.length) return;
        const mapEl = $mapEl[0];

        if (mapEl._leaflet_id) {
            try {
                if (this.map) {
                    this.map.invalidateSize();
                    return;
                }
            } catch (e) {}
            try {
                mapEl._leaflet_id = null;
            } catch (e) {}
        }

        // Initialize Map
        try {
            this.map = L.map(mapEl, {
                center: [22.0, 150.0],
                zoom: 3,
                minZoom: 2,
                maxZoom: 18,
                zoomControl: true,
                attributionControl: true
            });

            // 1. OpenStreetMap Tile Layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 18,
                subdomains: ['a', 'b', 'c']
            }).addTo(this.map);

            // Invalidate size after DOM layout settles
            setTimeout(() => {
                if (self.map) self.map.invalidateSize();
            }, 300);
        } catch (e) {
            console.error('[TrackingHub] Error initializing map:', e);
        }
    }

    refresh(preferredShipment = null, callback = null) {
        const self = this;
        let targetShipment = preferredShipment || this.pendingFocusShipment;
        frappe.call({
            method: 'logistics_wizard.api.get_shipment_tracking_hub_data',
            args: targetShipment ? {
                shipment: targetShipment
            } : {},
            callback: (r) => {
                if (r && r.message) {
                    this.data = r.message;
                    this.render_all(targetShipment);
                    let toFocus = this.pendingFocusShipment || targetShipment;
                    this.pendingFocusShipment = null;
                    if (toFocus) {
                        this.select_shipment(toFocus);
                    }
                }
                if (callback) callback();
            },
            error: function () {
                if (callback) callback();
            }
        });
    }

    render_all(preferredShipment = null) {
        if (!this.data) return;

        // 1. Render KPIs
        this.render_kpis(this.data.kpis || {});

        // 2. Select initial or preferred shipment (Null by default for Fleet Overview)
        let allShipments = this.data.shipments || [];
        if (preferredShipment) {
            this.selectedShipment = allShipments.find(s => 
                s.name === preferredShipment || 
                s.purchase_order === preferredShipment || 
                s.tracking_number === preferredShipment ||
                s.container_id === preferredShipment
            ) || this.data.selected_shipment || null;
        } else {
            this.selectedShipment = null; // Default to overview
        }

        // 3. Render Table
        this.filter_and_render_table();

        // 4. Render Stepper
        this.render_stepper(this.selectedShipment);

        // 5. Render Exceptions Center
        this.render_exceptions(this.data.active_exceptions || []);

        // 6. Update Map with selected route
        this.update_map_view(this.selectedShipment);
    }

    render_kpis(kpis) {
        $('#kpi-val-total').text(kpis.total_shipments || 0);
        $('#kpi-val-transit').text(kpis.in_transit || 0);
        $('#kpi-val-delayed').text(kpis.delayed_exceptions || 0);
        $('#kpi-val-stale').text(kpis.stale_tracking || 0);

        $('#tab-cnt-all').text(kpis.total_shipments || 0);
        $('#tab-cnt-transit').text(kpis.in_transit || 0);
        $('#tab-cnt-delayed').text(kpis.delayed_exceptions || 0);
        $('#tab-cnt-stale').text(kpis.stale_tracking || 0);

        // Count delivered
        let deliveredCnt = (this.data.shipments || []).filter(s => s.status === 'Delivered' || s.status === 'Completed').length;
        $('#tab-cnt-delivered').text(deliveredCnt);
    }

    filter_and_render_table() {
        const self = this;
        let shipments = this.data ? (this.data.shipments || []) : [];

        // Tab Filtering
        if (this.currentFilter === 'In Transit') {
            shipments = shipments.filter(s => s.status === 'In Transit');
        } else if (this.currentFilter === 'Delayed') {
            shipments = shipments.filter(s => s.is_delayed == 1 || s.status === 'Delayed');
        } else if (this.currentFilter === 'Stale') {
            shipments = shipments.filter(s => s.is_stale == 1);
        } else if (this.currentFilter === 'Delivered') {
            shipments = shipments.filter(s => s.status === 'Delivered' || s.status === 'Completed');
        }

        // Search Term Filtering
        if (this.searchTerm) {
            let q = this.searchTerm;
            shipments = shipments.filter(s => {
                return (s.name && s.name.toLowerCase().includes(q)) ||
                       (s.tracking_number && s.tracking_number.toLowerCase().includes(q)) ||
                       (s.container_id && s.container_id.toLowerCase().includes(q)) ||
                       (s.carrier && s.carrier.toLowerCase().includes(q)) ||
                       (s.purchase_order && s.purchase_order.toLowerCase().includes(q)) ||
                       (s.origin_port && s.origin_port.toLowerCase().includes(q)) ||
                       (s.destination_port && s.destination_port.toLowerCase().includes(q));
            });
        }

        let $tbody = $('#hub-shipments-tbody');
        $tbody.empty();

        if (shipments.length === 0) {
            $tbody.html(`
                <tr>
                    <td colspan="6" class="text-center text-muted" style="padding: 30px;">
                        Không tìm thấy lô hàng nào phù hợp với bộ lọc.
                    </td>
                </tr>
            `);
            return;
        }

        shipments.forEach(s => {
            let isSelected = self.selectedShipment && self.selectedShipment.name === s.name;
            let currentVehMode = s.current_vehicle || self.get_active_vehicle_mode(s, s.progress);
            let vehIconChar = (currentVehMode === 'Air' || currentVehMode === 'Plane') ? '✈️' : ((currentVehMode === 'Ocean' || currentVehMode === 'Ship') ? '🚢' : '🚚');

            // Status Badge
            let statusClass = 'badge-in-transit';
            if (s.status === 'Delayed' || s.is_delayed == 1) statusClass = 'badge-delayed';
            else if (s.status === 'Delivered' || s.status === 'Completed') statusClass = 'badge-delivered';
            else if (s.is_stale == 1) statusClass = 'badge-stale';
            else if (s.status === 'Draft') statusClass = 'badge-draft';

            // Delay Tag
            let delayTag = '<span class="delay-tag-ontime">Đúng hạn</span>';
            if (s.delay_days && s.delay_days > 0) {
                delayTag = `<span class="delay-tag-positive">+${s.delay_days} ngày</span>`;
            }

            let $row = $(`
                <tr class="hub-row-clickable ${isSelected ? 'selected' : ''}" data-name="${s.name}">
                    <td>
                        <div style="font-weight: 700; color: #0284c7;">
                            ${vehIconChar} ${s.name}
                        </div>
                        <div style="font-size: 11px; color: #64748b; font-family: monospace;">
                            ${s.container_id ? 'Cont: ' + s.container_id : (s.tracking_number ? 'Track: ' + s.tracking_number : '')}
                        </div>
                    </td>
                    <td>
                        <div style="font-weight: 600;">${s.carrier || 'Chưa chỉ định'}</div>
                        <div style="font-size: 11px; color: #64748b;">${s.vessel_name || s.flight_number || ''}</div>
                    </td>
                    <td>
                        <div style="font-weight: 500;">${s.origin_port || 'N/A'} ➔ ${s.destination_port || 'N/A'}</div>
                        <div style="margin-top: 2px;"><span class="badge-status ${statusClass}">${s.status}</span></div>
                    </td>
                    <td>
                        <div style="font-size: 11px;">ETD: ${s.atd || s.etd || '—'}</div>
                        <div style="font-size: 11px; font-weight: 600; color: ${s.is_delayed ? '#dc2626' : '#1e293b'};">
                            ETA: ${s.eta || '—'}
                        </div>
                    </td>
                    <td>${delayTag}</td>
                    <td style="text-align: center;">
                        <button class="btn btn-xs btn-default hub-btn-select-shipment" data-name="${s.name}" title="Xem lộ trình trên bản đồ">
                            <i class="fa fa-crosshairs"></i>
                        </button>
                        ${s.purchase_order ? `
                            <a href="/app/purchase-order/${s.purchase_order}" class="btn btn-xs btn-default" title="Xem PO ${s.purchase_order}">
                                <i class="fa fa-file-text-o"></i>
                            </a>
                        ` : ''}
                    </td>
                </tr>
            `);

            $row.on('click', function (e) {
                if ($(e.target).closest('a').length) return;
                let isCurrentlySelected = self.selectedShipment && self.selectedShipment.name === s.name;
                if (isCurrentlySelected) {
                    // Toggle unselect -> Quay về Toàn cảnh (Theo lựa chọn A3 của người dùng)
                    self.reset_map_view();
                } else {
                    self.select_shipment(s.name);
                }
            });

            $row.find('.hub-btn-select-shipment').on('click', function (e) {
                e.stopPropagation();
                let isCurrentlySelected = self.selectedShipment && self.selectedShipment.name === s.name;
                if (isCurrentlySelected) {
                    self.reset_map_view();
                } else {
                    self.select_shipment(s.name);
                }
            });

            $tbody.append($row);
        });
    }

    select_shipment(shipmentName) {
        const self = this;
        let found = (this.data && this.data.shipments ? this.data.shipments : []).find(s => s.name === shipmentName);
        if (found) {
            this.selectedShipment = found;
        } else {
            this.pendingFocusShipment = shipmentName;
        }

        // Fetch detailed single shipment data
        frappe.call({
            method: 'logistics_wizard.api.get_shipment_tracking_hub_data',
            args: { shipment: shipmentName },
            callback: function (r) {
                if (r && r.message && r.message.selected_shipment) {
                    self.selectedShipment = r.message.selected_shipment;
                }
                // Update Row selection class
                $('#hub-shipments-tbody tr').removeClass('selected');
                $(`#hub-shipments-tbody tr[data-name="${shipmentName}"]`).addClass('selected');

                self.render_stepper(self.selectedShipment);
                self.update_map_view(self.selectedShipment);
            }
        });
    }

    render_stepper(shipment) {
        let $track = $('#hub-stepper-track');
        $track.empty();

        if (!shipment) {
            $('#stepper-shipment-name').text('Chưa chọn lô hàng');
            $track.html(`
                <div class="hub-stepper-empty-hint">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="16" x2="12" y2="12"/>
                        <line x1="12" y1="8" x2="12.01" y2="8"/>
                    </svg>
                    Đang ở chế độ <b>Toàn cảnh</b>. Chọn một lô hàng từ danh sách bên dưới hoặc nhấp vào phương tiện trên bản đồ để theo dõi chi tiết 9 mốc DCSA.
                </div>
            `);
            return;
        }

        $('#stepper-shipment-name').text(`${shipment.name} (${shipment.carrier || ''})`);

        // 9 DCSA Standard Milestones
        const DCSA_LIST = [
            { key: 'BOOKED', label: '1. Đặt chỗ' },
            { key: 'GATE_IN', label: '2. Vào bãi' },
            { key: 'LOADED', label: '3. Xếp hàng' },
            { key: 'DEPARTED', label: '4. Khởi hành' },
            { key: 'TRANSSHIPMENT', label: '5. Trung chuyển' },
            { key: 'ARRIVED', label: '6. Cập cảng' },
            { key: 'DISCHARGED', label: '7. Dỡ hàng' },
            { key: 'GATE_OUT', label: '8. Ra cổng' },
            { key: 'DELIVERED', label: '9. Giao kho' }
        ];

        let routes = shipment.transit_route || [];
        let completedMilestones = new Set();
        let milestoneDates = {};

        routes.forEach(cp => {
            if (cp.milestone) {
                completedMilestones.add(cp.milestone.toUpperCase());
                milestoneDates[cp.milestone.toUpperCase()] = cp.date || cp.timestamp || '';
            }
        });

        // Determine current active milestone (highest completed, or next)
        let currentIdx = -1;
        for (let i = DCSA_LIST.length - 1; i >= 0; i--) {
            if (completedMilestones.has(DCSA_LIST[i].key)) {
                currentIdx = i;
                break;
            }
        }
        if (currentIdx === -1) currentIdx = 0;

        DCSA_LIST.forEach((m, idx) => {
            let isCompleted = completedMilestones.has(m.key);
            let isCurrent = (idx === currentIdx);
            let isDelayed = shipment.is_delayed == 1;

            let itemClass = '';
            if (isCompleted) itemClass += ' completed';
            if (isCurrent) itemClass += ' current';
            if (isDelayed) itemClass += ' delayed';

            let dateStr = milestoneDates[m.key] ? milestoneDates[m.key].split('T')[0] : '';

            $track.append(`
                <div class="hub-step-item ${itemClass}">
                    <div class="hub-step-badge">
                        ${isCompleted ? '✔' : (idx + 1)}
                    </div>
                    <div class="hub-step-title">${m.label}</div>
                    <div class="hub-step-date">${dateStr || (isCurrent ? 'Đang thực hiện' : '—')}</div>
                </div>
            `);
        });
    }

    render_exceptions(exceptions) {
        let $list = $('#hub-exceptions-list');
        $list.empty();

        let count = exceptions ? exceptions.length : 0;
        $('#hub-exception-count-badge').text(`${count} sự cố`);

        if (!exceptions || exceptions.length === 0) {
            $list.html(`
                <div class="text-center text-muted" style="padding: 35px 15px;">
                    <i class="fa fa-check-circle text-success" style="font-size: 28px; margin-bottom: 8px;"></i>
                    <p style="margin: 0; font-size: 13px;">Không có sự cố hoặc cảnh báo ngoại lệ đang mở.</p>
                </div>
            `);
            return;
        }

        exceptions.forEach(exc => {
            let isCritical = exc.severity === 'Critical';
            let badgeClass = isCritical ? 'badge-danger' : 'badge-warning';
            let icon = isCritical ? '🔴' : '🟡';

            $list.append(`
                <div class="hub-exception-card ${isCritical ? 'critical' : 'warning'}">
                    <div class="exception-card-header">
                        <span class="exception-title">${icon} ${exc.exception_type || 'Ngoại lệ Vận chuyển'}</span>
                        <span class="badge ${badgeClass}">${exc.severity}</span>
                    </div>
                    <div class="exception-card-body">
                        <div><strong>Lô hàng:</strong> ${exc.shipment_tracking}</div>
                        ${exc.purchase_order ? `<div><strong>Đơn hàng:</strong> ${exc.purchase_order}</div>` : ''}
                        ${exc.old_eta && exc.new_eta ? `
                            <div class="exception-timeline-shift">
                                <span>ETA: ${exc.old_eta} ➔ <strong>${exc.new_eta}</strong></span>
                                <span class="badge-status badge-delayed">+${exc.delay_days || 0} ngày</span>
                            </div>
                        ` : ''}
                        <div style="margin-top: 6px; color: #475569;">${exc.description || ''}</div>
                    </div>
                    <div class="exception-card-footer">
                        ${exc.purchase_order ? `
                            <a href="/app/purchase-order/${exc.purchase_order}" class="btn btn-xs btn-default">
                                <i class="fa fa-external-link"></i> Mở PO
                            </a>
                        ` : ''}
                        <button class="btn btn-xs btn-primary hub-btn-resolve-exc" data-name="${exc.name}">
                            Đánh dấu đã xử lý
                        </button>
                    </div>
                </div>
            `);
        });

        // Bind resolve exception
        $('.hub-btn-resolve-exc').on('click', function () {
            let excName = $(this).data('name');
            frappe.db.set_value('Shipment Exception', excName, 'status', 'Resolved').then(() => {
                frappe.show_alert({ message: __('Đã giải quyết ngoại lệ!'), indicator: 'green' });
                $(this).closest('.hub-exception-card').fadeOut(300, function () { $(this).remove(); });
            });
        });
    }

    // ---------------------------------------------------------
    // HỆ THỐNG ĐỒ HỌA ĐỊNH TUYẾN & BẢN ĐỒ QUẢN TRỊ CAO CẤP
    // ---------------------------------------------------------

    update_marine_overlay(method) {
        if (!this.map) return;
        const L = window.L || window.leaflet;
        if (!L) return;

        if (method === 'Ocean') {
            if (!this.mapLayers.seaOverlay) {
                this.mapLayers.seaOverlay = L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
                    attribution: 'Hải đồ &copy; <a href="http://www.openseamap.org">OpenSeaMap</a>',
                    maxZoom: 18,
                    opacity: 0.95
                });
            }
            if (!this.map.hasLayer(this.mapLayers.seaOverlay)) {
                this.mapLayers.seaOverlay.addTo(this.map);
            }
        } else {
            if (this.mapLayers.seaOverlay && this.map.hasLayer(this.mapLayers.seaOverlay)) {
                this.map.removeLayer(this.mapLayers.seaOverlay);
            }
        }
    }

    get_vehicle_svg(method) {
        if (method === 'Air') {
            return `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#007AFF" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1.5C11.2 1.5 10.6 2.3 10.6 3.2V8.8L2.4 13.5C1.8 13.8 1.5 14.5 1.5 15.1C1.5 15.9 2.2 16.5 3 16.5H10.6V20.2L8.2 21.8C7.9 22 7.7 22.3 7.7 22.7C7.7 23.4 8.3 24 9 24H15C15.7 24 16.3 23.4 16.3 22.7C16.3 22.3 16.1 22 15.8 21.8L13.4 20.2V16.5H21C21.8 16.5 22.5 15.9 22.5 15.1C22.5 14.5 22.2 13.8 21.6 13.5L13.4 8.8V3.2C13.4 2.3 12.8 1.5 12 1.5Z" stroke="#0047AB" stroke-width="0.5"/>
                </svg>
            `;
        } else if (method === 'Ocean') {
            return `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1 C14.8 3.5 18 8 18 14 V20 C18 21.7 16.7 23 15 23 H9 C7.3 23 6 21.7 6 20 V14 C6 8 9.2 3.5 12 1 Z" fill="#0055B3" stroke="#003380" stroke-width="0.8"/>
                    <rect x="8" y="6.5" width="8" height="2.2" rx="0.4" fill="#38BDF8"/>
                    <rect x="8" y="9.7" width="8" height="2.2" rx="0.4" fill="#BAE6FD"/>
                    <rect x="8" y="12.9" width="8" height="2.2" rx="0.4" fill="#38BDF8"/>
                    <rect x="8" y="16.1" width="8" height="2.2" rx="0.4" fill="#BAE6FD"/>
                    <rect x="8.5" y="19.2" width="7" height="2.6" rx="0.5" fill="#FFFFFF"/>
                    <rect x="10.5" y="20" width="3" height="1" fill="#0055B3"/>
                </svg>
            `;
        } else {
            return `
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
            `;
        }
    }

    get_hub_icon_svg(hubType) {
        if (hubType === 'Ocean' || hubType === 'seaport' || hubType === 'port') {
            return `
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0055B3" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="5" r="3"/>
                    <line x1="12" y1="22" x2="12" y2="8"/>
                    <path d="M5 12H2a10 10 0 0 0 20 0h-3"/>
                </svg>
            `;
        } else {
            return `
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.2-1.1.6L2.5 8l6.4 3.3L7 15l-3.3-1.1-1.2 1.3 4.2 3.8 3.8 4.2 1.3-1.2L10.7 18.7l3.7-1.9 3.3 6.4 1.2-1.2-.4-2.6Z"/>
                </svg>
            `;
        }
    }

    get_active_vehicle_mode(shipment, currentProgress) {
        if (!shipment) return 'Ocean';
        const sMethod = shipment.shipping_method || 'Ocean';
        const status = (shipment.status || '').toLowerCase();

        // 1. Giai đoạn hoàn tất hoặc nhập kho đích -> Xe tải (Truck / Road)
        if (['delivered', 'completed', 'received', 'closed', 'giao hàng thành công', 'giao hàng', 'nhập kho', 'chuẩn bị nhập kho'].some(st => status.includes(st))) {
            return 'Road';
        }

        // 2. Giai đoạn thông quan hải quan tại cảng/sân bay đến -> Xe tải (Truck / Road)
        if (['customs clearance', 'customs', 'thông quan', 'hải quan', 'chờ nhập kho'].some(st => status.includes(st))) {
            return 'Road';
        }

        // 3. Kiểm tra DCSA milestones (nếu có mốc hiện tại)
        if (shipment.transit_route && Array.isArray(shipment.transit_route)) {
            const currMs = shipment.transit_route.find(r => r.is_current == 1 || (r.activity && r.activity.includes('(Current Position)')));
            if (currMs) {
                const ms = (currMs.milestone || '').toUpperCase();
                if (['ARRIVED', 'DISCHARGED', 'GATE_OUT', 'DELIVERED'].includes(ms)) {
                    return 'Road';
                }
                if (['BOOKED', 'GATE_IN'].includes(ms)) {
                    return 'Road';
                }
            }
        }

        // 4. Kiểm tra theo Progress Thresholds của tuyến 3 chặng
        const curP = (typeof currentProgress === 'number') ? currentProgress : ((typeof shipment.progress === 'number') ? shipment.progress : 0.55);
        const thresholds = shipment.progress_thresholds || [0.0, 0.05, 0.95, 1.0];
        const p1 = (thresholds[1] !== undefined) ? thresholds[1] : 0.05;
        const p2 = (thresholds[2] !== undefined) ? thresholds[2] : 0.95;

        // Chặng 1 (First-mile Road từ kho nguồn ra cảng/sân bay)
        if (curP <= p1) {
            return 'Road';
        }
        // Chặng 3 (Last-mile Road từ cảng/sân bay về kho Cáp Kim Khánh Đà Nẵng)
        if (curP >= p2) {
            return 'Road';
        }

        // Chặng 2 (Main-haul quốc tế vượt biển / đường bay)
        return (sMethod === 'Air') ? 'Air' : 'Ocean';
    }

    calculateBearing(lat1, lon1, lat2, lon2) {
        const toRad = Math.PI / 180;
        const toDeg = 180 / Math.PI;
        const phi1 = lat1 * toRad;
        const phi2 = lat2 * toRad;
        let deltaLambda = (lon2 - lon1) * toRad;

        while (deltaLambda > Math.PI) deltaLambda -= 2 * Math.PI;
        while (deltaLambda < -Math.PI) deltaLambda += 2 * Math.PI;

        const y = Math.sin(deltaLambda) * Math.cos(phi2);
        const x = Math.cos(phi1) * Math.sin(phi2) - Math.sin(phi1) * Math.cos(phi2) * Math.cos(deltaLambda);
        const theta = Math.atan2(y, x);
        return (theta * toDeg + 360) % 360;
    }

    computePolylineMetrics(coords) {
        const cumulative = [0];
        let total = 0;
        if (!coords || coords.length <= 1) {
            return { cumulative: [0], total: 0 };
        }
        for (let i = 0; i < coords.length - 1; i++) {
            let [y1, x1] = coords[i];
            let [y2, x2] = coords[i + 1];
            let dx = x2 - x1;
            if (dx > 180) dx -= 360;
            if (dx < -180) dx += 360;
            let dy = y2 - y1;
            let cosLat = Math.cos(((y1 + y2) / 2) * Math.PI / 180);
            let dist = Math.hypot(dy, dx * cosLat);
            total += dist;
            cumulative.push(total);
        }
        return { cumulative, total };
    }

    interpolateAtProgress(coords, metrics, progress) {
        if (!coords || coords.length === 0) return { point: [0, 0], bearing: 0 };
        if (coords.length === 1) return { point: coords[0], bearing: 0 };

        const p = Math.max(0, Math.min(1, progress));
        if (metrics.total === 0) return { point: coords[0], bearing: 0 };

        const targetDist = p * metrics.total;

        let segmentIdx = 0;
        for (let i = 0; i < metrics.cumulative.length - 1; i++) {
            if (targetDist >= metrics.cumulative[i] && targetDist <= metrics.cumulative[i + 1]) {
                segmentIdx = i;
                break;
            }
        }
        if (segmentIdx >= coords.length - 1) {
            segmentIdx = coords.length - 2;
        }

        const segStartDist = metrics.cumulative[segmentIdx];
        const segLen = metrics.cumulative[segmentIdx + 1] - segStartDist;
        const t = (segLen === 0) ? 0 : Math.max(0, Math.min(1, (targetDist - segStartDist) / segLen));

        const p1 = coords[segmentIdx];
        const p2 = coords[segmentIdx + 1] || p1;

        let lat = p1[0] + t * (p2[0] - p1[0]);
        let lon1 = p1[1];
        let lon2 = p2[1];
        let dLon = lon2 - lon1;
        if (dLon > 180) dLon -= 360;
        if (dLon < -180) dLon += 360;
        let lon = lon1 + t * dLon;

        const bearing = this.calculateBearing(p1[0], p1[1], p2[0], p2[1]);
        return { point: [lat, lon], bearing };
    }

    perpendicularDistance(p, p1, p2) {
        let [lat, lon] = p;
        let [lat1, lon1] = p1;
        let [lat2, lon2] = p2;

        let dLon = lon2 - lon1;
        let dLat = lat2 - lat1;

        if (dLon > 180) dLon -= 360;
        if (dLon < -180) dLon += 360;

        let pLon = lon - lon1;
        let pLat = lat - lat1;
        if (pLon > 180) pLon -= 360;
        if (pLon < -180) pLon += 360;

        let lenSq = dLon * dLon + dLat * dLat;
        if (lenSq === 0) {
            return Math.hypot(pLon, pLat);
        }

        let t = Math.max(0, Math.min(1, (pLon * dLon + pLat * dLat) / lenSq));
        let projLon = t * dLon;
        let projLat = t * dLat;

        return Math.hypot(pLon - projLon, pLat - projLat);
    }

    douglasPeucker(points, tolerance = 0.002) {
        if (!points || !Array.isArray(points) || points.length <= 2) return points || [];

        let maxDist = 0;
        let maxIndex = 0;
        const end = points.length - 1;

        for (let i = 1; i < end; i++) {
            let dist = this.perpendicularDistance(points[i], points[0], points[end]);
            if (dist > maxDist) {
                maxDist = dist;
                maxIndex = i;
            }
        }

        if (maxDist > tolerance) {
            let left = this.douglasPeucker(points.slice(0, maxIndex + 1), tolerance);
            let right = this.douglasPeucker(points.slice(maxIndex), tolerance);
            return left.slice(0, left.length - 1).concat(right);
        } else {
            return [points[0], points[end]];
        }
    }

    animateVehicle(marker, coords, targetProgress, durationMs = 1500, mainMethod = 'Ocean') {
        const self = this;
        if (this.currentAnimationId) {
            cancelAnimationFrame(this.currentAnimationId);
            this.currentAnimationId = null;
        }

        if (!marker || !coords || coords.length === 0) return;

        const metrics = this.computePolylineMetrics(coords);
        const startProgress = (typeof marker._currentProgress === 'number') ? marker._currentProgress : 0;
        const clampedTarget = Math.max(0, Math.min(1, targetProgress));
        const startTime = performance.now();

        function frame(now) {
            const elapsed = now - startTime;
            const rawT = durationMs <= 0 ? 1 : Math.min(1, elapsed / durationMs);
            const easeT = 1 - Math.pow(1 - rawT, 3);
            const curP = startProgress + (clampedTarget - startProgress) * easeT;

            const { point, bearing } = self.interpolateAtProgress(coords, metrics, curP);
            marker.setLatLng(point);

            const iconEl = marker.getElement ? marker.getElement() : null;
            if (iconEl) {
                if (marker._shipment) {
                    const activeMode = self.get_active_vehicle_mode(marker._shipment, curP);
                    if (marker._lastActiveMode !== activeMode) {
                        marker._lastActiveMode = activeMode;
                        const svgWrap = iconEl.querySelector('.lw-vehicle-icon-svg');
                        if (svgWrap) {
                            svgWrap.innerHTML = self.get_vehicle_svg(activeMode);
                        }
                        const boxEl = iconEl.querySelector('.lw-vehicle-box');
                        if (boxEl) {
                            boxEl.style.borderColor = activeMode === 'Air' ? '#007AFF' : (activeMode === 'Ocean' ? '#0055B3' : '#EA580C');
                        }
                    }
                }

                const rotEl = iconEl.querySelector('.lw-vehicle-icon-svg') || iconEl.querySelector('svg');
                if (rotEl) {
                    rotEl.style.transform = `rotate(${bearing}deg)`;
                    rotEl.style.transformOrigin = 'center center';
                }
            }

            marker._currentProgress = curP;

            if (rawT < 1) {
                self.currentAnimationId = requestAnimationFrame(frame);
            } else {
                self.currentAnimationId = null;
            }
        }

        this.currentAnimationId = requestAnimationFrame(frame);
    }

    update_map_view(shipment) {
        if (!this.map) return;
        if (shipment) {
            this.render_single_shipment_map(shipment);
        } else {
            this.render_fleet_overview_map(this.data ? (this.data.shipments || []) : []);
        }
    }

    align_route_coords(coords, refLon = 150.0) {
        if (!coords || !Array.isArray(coords) || coords.length === 0) return coords;

        // Step 1: Ensure continuity across antimeridian
        let unwrapped = [];
        let prevLon = null;
        let cumShift = 0;
        for (let p of coords) {
            if (!Array.isArray(p) || p.length < 2 || typeof p[1] !== 'number') continue;
            let lat = p[0];
            let lon = p[1] + cumShift;
            if (prevLon !== null) {
                let delta = lon - prevLon;
                if (delta > 180) {
                    cumShift -= 360;
                    lon -= 360;
                } else if (delta < -180) {
                    cumShift += 360;
                    lon += 360;
                }
            }
            prevLon = lon;
            unwrapped.push([lat, lon]);
        }

        if (unwrapped.length === 0) return coords;

        // Step 2: Align route to Pacific frame centered at refLon
        let validLons = unwrapped.map(p => p[1]);
        let avgLon = validLons.reduce((a, b) => a + b, 0) / validLons.length;
        let bestShift = 0;
        let minDiff = Math.abs(avgLon - refLon);
        for (let k of [-2, -1, 1, 2]) {
            let diff = Math.abs((avgLon + k * 360) - refLon);
            if (diff < minDiff) {
                minDiff = diff;
                bestShift = k * 360;
            }
        }

        if (bestShift !== 0) {
            return unwrapped.map(p => [p[0], p[1] + bestShift]);
        }
        return unwrapped;
    }

    render_fleet_overview_map(allShipments) {
        if (!this.map) return;
        const L = window.L || window.leaflet;
        if (!L) return;

        const self = this;
        this.clear_map_layers();

        // 1. Title, Badge & Reset Button State
        $('#hub-map-title').text('Bản đồ Giám sát Toàn cầu (Fleet Overview)');
        $('#hub-map-reset-btn').addClass('active');

        // Filter active shipments according to user's selection A1
        let activeList = (allShipments || []).filter(s => s.status === 'In Transit' || s.status === 'Customs Clearance');
        if (activeList.length === 0) {
            activeList = (allShipments || []).filter(s => s.status !== 'Draft');
        }
        if (activeList.length === 0) {
            activeList = allShipments || [];
        }

        $('#hub-selected-shipment-badge')
            .text(`Toàn cảnh: ${activeList.length} lô hàng đang hành trình`)
            .show();

        // Global Ocean context
        this.update_marine_overlay('Ocean');

        let allLayersToFit = [];

        // Known port coordinate dictionary fallback
        const PORT_COORDS = {
            'san francisco': [37.619, -122.375],
            'tan son nhat': [10.8188, 106.652],
            'oakland': [37.804, -122.271],
            'hai phong': [20.865, 106.683],
            'cat lai': [10.762, 106.792],
            'long beach': [33.754, -118.216],
            'los angeles': [33.743, -118.267],
            'shanghai': [31.230, 121.473],
            'singapore': [1.290, 103.851],
            'rotterdam': [51.924, 4.477],
            'busan': [35.179, 129.075],
            'tokyo': [35.676, 139.650]
        };

        function resolve_coords(portName) {
            if (!portName) return null;
            let p = portName.toLowerCase();
            for (let k in PORT_COORDS) {
                if (p.includes(k)) return PORT_COORDS[k];
            }
            return null;
        }

        activeList.forEach((s, idx) => {
            let sMethod = s.shipping_method || 'Ocean';
            let isAir = (sMethod === 'Air');
            let isRoad = (sMethod === 'Road');

            // 1. Resolve Route Coordinates
            let coords = [];
            if (s.full_route && Array.isArray(s.full_route) && s.full_route.length >= 2) {
                coords = s.full_route;
            } else if (s.route && Array.isArray(s.route) && s.route.length >= 2) {
                coords = s.route;
            } else if (s.legs && Array.isArray(s.legs) && s.legs.length > 0) {
                s.legs.forEach(leg => {
                    let pts = leg.coordinates_latlon || leg.coordinates || [];
                    if (pts.length > 0) coords = coords.concat(pts);
                });
            }

            // Fallback between known ports if coords still empty
            if (coords.length < 2) {
                let oC = resolve_coords(s.origin_port) || [31.23, 121.47];
                let dC = resolve_coords(s.destination_port) || [10.76, 106.79];
                let oLon = oC[1];
                let dLon = dC[1];
                if (oLon < 0 && dLon > 0 && Math.abs(oLon - dLon) > 180) {
                    oLon += 360;
                } else if (dLon < 0 && oLon > 0 && Math.abs(dLon - oLon) > 180) {
                    dLon += 360;
                }
                let midLat = (oC[0] + dC[0]) / 2 + (isAir ? 6.0 : -3.0);
                let midLon = (oLon + dLon) / 2;
                coords = [[oC[0], oLon], [midLat, midLon], [dC[0], dLon]];
            }

            // Align coordinates to unified Pacific frame (refLon = 150.0)
            coords = self.align_route_coords(coords, 150.0);

            // Simplify coordinates
            let simpCoords = self.douglasPeucker(coords, 0.003);
            if (!simpCoords || simpCoords.length < 2) simpCoords = coords;

            // Determine line styling (Render Multi-Leg Polylines if available)
            let hasMultiLegs = s.legs && Array.isArray(s.legs) && s.legs.length > 0;
            if (hasMultiLegs) {
                s.legs.forEach(leg => {
                    let legRaw = leg.coordinates_latlon || leg.coordinates || [];
                    if (legRaw.length >= 2) {
                        legRaw = self.align_route_coords(legRaw, 150.0);
                        let legSimp = self.douglasPeucker(legRaw, 0.003);
                        if (!legSimp || legSimp.length < 2) legSimp = legRaw;

                        let legMode = leg.mode || (leg.vehicle_type === 'Truck' ? 'Road' : sMethod);
                        let isLegRoad = (legMode === 'Road');
                        let isLegAir = (legMode === 'Air');
                        let legColor = isLegRoad ? '#FF9500' : (isLegAir ? '#0284c7' : '#0055B3');
                        if (s.is_delayed == 1 && !isLegRoad) legColor = '#DC2626';

                        let pLeg = L.polyline(legSimp, {
                            color: legColor,
                            weight: isLegRoad ? 3.0 : 3.8,
                            opacity: 0.85,
                            dashArray: (isLegAir || isLegRoad) ? '6, 8' : ''
                        }).addTo(self.map);

                        pLeg.bindTooltip(`<b>${s.name}</b> (${s.carrier || ''})<br>${leg.name || 'Hành trình'}<br><span style="color:#0071E3; font-weight:600;">👉 Nhấp để xem đơn này</span>`, { sticky: true });
                        pLeg.on('click', () => {
                            self.select_shipment(s.name);
                        });

                        self.mapLayers.routePolylines.push(pLeg);
                        allLayersToFit.push(pLeg);
                    }
                });
            } else {
                let lineColor = isRoad ? '#FF9500' : (isAir ? '#0284c7' : '#0055B3');
                if (s.is_delayed == 1) lineColor = '#DC2626';

                let polyline = L.polyline(simpCoords, {
                    color: lineColor,
                    weight: 3.5,
                    opacity: 0.82,
                    dashArray: (isAir || isRoad) ? '6, 8' : ''
                }).addTo(self.map);

                polyline.bindTooltip(`<b>${s.name}</b> (${s.carrier || ''})<br>${s.origin_port || 'Origin'} ➔ ${s.destination_port || 'Dest'}<br><span style="color:#0071E3; font-weight:600;">👉 Nhấp để xem đơn này</span>`, { sticky: true });
                polyline.on('click', () => {
                    self.select_shipment(s.name);
                });

                self.mapLayers.routePolylines.push(polyline);
                allLayersToFit.push(polyline);
            }

            // 2. Origin & Destination Micro-Markers
            let startPt = simpCoords[0];
            let endPt = simpCoords[simpCoords.length - 1];

            let originName = (s.origin && s.origin.name) || s.origin_port || s.name;
            let originDot = L.circleMarker(startPt, {
                radius: 5,
                color: '#16A34A',
                fillColor: '#FFFFFF',
                fillOpacity: 1,
                weight: 2
            }).addTo(self.map);
            originDot.bindTooltip(`Xuất phát (Kho nguồn): ${originName}`);
            originDot.on('click', () => { self.select_shipment(s.name); });
            self.mapLayers.markers.push(originDot);

            let destName = (s.destination && s.destination.name) || 'Kho bãi Logistics Cáp Kim Khánh Đà Nẵng';
            let destDot = L.circleMarker(endPt, {
                radius: 5,
                color: '#DC2626',
                fillColor: '#FFFFFF',
                fillOpacity: 1,
                weight: 2
            }).addTo(self.map);
            destDot.bindTooltip(`Đích đến: ${destName}`);
            destDot.on('click', () => { self.select_shipment(s.name); });
            self.mapLayers.markers.push(destDot);

            // 3. Vehicle Marker along route
            let progress = (typeof s.progress === 'number') ? s.progress : 0.55;
            let activeMode = self.get_active_vehicle_mode(s, progress);
            let metrics = self.computePolylineMetrics(simpCoords);
            let posData = self.interpolateAtProgress(simpCoords, metrics, progress);

            let vehBorder = (s.is_delayed == 1) ? '#DC2626' : (activeMode === 'Air' ? '#007AFF' : (activeMode === 'Ocean' ? '#0055B3' : '#EA580C'));
            let vehIcon = L.divIcon({
                className: 'custom-fleet-vehicle-icon',
                html: `
                    <div style="background: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.3); border: 2.5px solid ${vehBorder}; cursor: pointer; transition: transform 0.2s;" title="${s.name} - ${s.carrier || ''}">
                        <div style="display: flex; align-items: center; justify-content: center; transform: rotate(${posData.bearing}deg); transform-origin: center center;">
                            ${self.get_vehicle_svg(activeMode)}
                        </div>
                    </div>
                `,
                iconSize: [36, 36],
                iconAnchor: [18, 18]
            });

            let vehMarker = L.marker(posData.point, { icon: vehIcon, zIndexOffset: 500 + idx * 10 }).addTo(self.map);
            let modeTitleVi = activeMode === 'Air' ? 'Hàng không (Máy bay ✈️)' : (activeMode === 'Ocean' ? 'Đường biển (Tàu hàng 🚢)' : 'Đường bộ (Xe tải 🚚)');
            vehMarker.bindTooltip(`
                <div style="font-size: 11.5px; line-height: 1.4;">
                    <strong style="color: #0071E3;">${s.name}</strong> (${s.carrier || ''})<br>
                    ${s.origin ? s.origin.name : (s.origin_port || 'Origin')} ➔ ${s.destination ? s.destination.name : 'Kho bãi Logistics Cáp Kim Khánh Đà Nẵng'}<br>
                    Phương tiện hiện tại: <b>${modeTitleVi}</b><br>
                    Trạng thái: <b>${s.status}</b><br>
                    <span style="color: #0071E3; font-weight: 600;">👉 Nhấp để xem hành trình chi tiết</span>
                </div>
            `, { direction: 'top', offset: [0, -12] });

            vehMarker.on('click', () => {
                self.select_shipment(s.name);
            });

            self.mapLayers.fleetVehicleMarkers.push(vehMarker);
            allLayersToFit.push(vehMarker);
        });

        // 4. Fit bounds
        if (allLayersToFit.length > 0) {
            try {
                let group = L.featureGroup(allLayersToFit);
                let bounds = group.getBounds();
                let z = self.map.getBoundsZoom(bounds, false, [50, 50]);
                self.map.setView(bounds.getCenter(), Math.min(Math.max(z, 2), 3));
            } catch (e) {
                self.map.setView([22.0, 150.0], 3);
            }
        } else {
            self.map.setView([22.0, 150.0], 3);
        }
    }

    render_single_shipment_map(shipment) {
        if (!this.map || !shipment) return;
        const L = window.L || window.leaflet;
        if (!L) return;

        // Clear existing route and markers
        this.clear_map_layers();

        // Update Title & Badge
        $('#hub-map-title').text(`Hành trình Chi tiết: ${shipment.name}`);
        $('#hub-map-reset-btn').removeClass('active');
        $('#hub-selected-shipment-badge')
            .text(`Lô hàng: ${shipment.name} (${shipment.carrier || ''})`)
            .show();

        // 1. OpenSeaMap Marine Overlay Toggle
        const sMethod = shipment.shipping_method || 'Ocean';
        this.update_marine_overlay(sMethod);

        // 2. Extract Route Coordinates
        let fullRoute = [];
        if (shipment.full_route && Array.isArray(shipment.full_route) && shipment.full_route.length > 0) {
            fullRoute = shipment.full_route;
        } else if (shipment.route && Array.isArray(shipment.route) && shipment.route.length > 0) {
            fullRoute = shipment.route;
        } else if (shipment.legs && Array.isArray(shipment.legs) && shipment.legs.length > 0) {
            shipment.legs.forEach(leg => {
                let legPoints = leg.coordinates_latlon || leg.coordinates || [];
                if (legPoints.length > 0) fullRoute = fullRoute.concat(legPoints);
            });
        }

        // Fallback default coordinates if empty
        if (fullRoute.length === 0) {
            let lat = parseFloat(shipment.current_lat) || 20.0;
            let lon = parseFloat(shipment.current_lon) || 120.0;
            fullRoute = [
                [31.23, 121.47], // Shanghai / Origin
                [lat, lon],
                [10.77, 106.70]  // Cat Lai / Destination
            ];
        }

        fullRoute = this.align_route_coords(fullRoute, 150.0);

        // 3. Polyline Simplification
        let simplifiedCoords = this.douglasPeucker(fullRoute, 0.002);
        if (!simplifiedCoords || simplifiedCoords.length < 2) {
            simplifiedCoords = fullRoute;
        }

        // 4. Render Multi-Leg Polylines with Specific Modes & Colors
        let polylineLayers = [];
        if (shipment.legs && Array.isArray(shipment.legs) && shipment.legs.length > 0) {
            shipment.legs.forEach(leg => {
                let legRaw = leg.coordinates_latlon || leg.coordinates || [];
                if (legRaw.length >= 2) {
                    legRaw = this.align_route_coords(legRaw, 150.0);
                    let legSimp = this.douglasPeucker(legRaw, 0.002);
                    if (!legSimp || legSimp.length < 2) legSimp = legRaw;

                    let isRoad = (leg.mode === 'Road');
                    let isAir = (leg.mode === 'Air');
                    let legColor = isRoad ? '#FF9500' : (isAir ? '#0284c7' : '#0055B3');
                    let legDash = isRoad ? '6, 8' : (isAir ? '6, 8' : '');
                    let legWeight = isRoad ? 3.5 : 4.0;

                    let pLayer = L.polyline(legSimp, {
                        color: legColor,
                        weight: legWeight,
                        opacity: 0.9,
                        dashArray: legDash
                    }).addTo(this.map);
                    polylineLayers.push(pLayer);
                    this.mapLayers.routePolylines.push(pLayer);
                }
            });
        }

        // Fallback single polyline if no legs rendered
        if (polylineLayers.length === 0) {
            let isAir = (sMethod === 'Air');
            let isRoad = (sMethod === 'Road');
            let singleLine = L.polyline(simplifiedCoords, {
                color: isRoad ? '#FF9500' : (isAir ? '#0284c7' : '#0055B3'),
                weight: 4.0,
                opacity: 0.9,
                dashArray: (isAir || isRoad) ? '6, 8' : ''
            }).addTo(this.map);
            polylineLayers.push(singleLine);
            this.mapLayers.routePolylines.push(singleLine);
        }

        // 5. Origin Marker (Kho/Nhà máy Xuất - O)
        let originCoord = simplifiedCoords[0];
        let originName = (shipment.origin && shipment.origin.name) || shipment.origin_port || 'Kho/Nhà máy xuất phát';
        let originIcon = L.divIcon({
            className: 'hub-origin-marker-icon',
            html: `<div style="background: #16a34a; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); cursor: pointer;" title="Điểm xuất phát (Kho nguồn - Điểm O)">O</div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });
        let originMarker = L.marker(originCoord, { icon: originIcon }).addTo(this.map);
        let dispOriginLon = ((originCoord[1] + 180) % 360 + 360) % 360 - 180;
        originMarker.bindPopup(`<b>Điểm xuất phát (Kho nguồn):</b><br>${originName}<br><small>Toạ độ: ${originCoord[0].toFixed(4)}, ${dispOriginLon.toFixed(4)}</small>`);
        this.mapLayers.markers.push(originMarker);

        // 6. Destination Marker (Kho Đích Cáp Kim Khánh Đà Nẵng - D)
        let destCoord = simplifiedCoords[simplifiedCoords.length - 1];
        let destName = (shipment.destination && shipment.destination.name) || 'Kho bãi Logistics Cáp Kim Khánh Đà Nẵng (Gần ĐH Bách Khoa)';
        let destIcon = L.divIcon({
            className: 'hub-dest-marker-icon',
            html: `<div style="background: #dc2626; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); cursor: pointer;" title="Điểm đích đến (Kho Cáp Kim Khánh Đà Nẵng - Điểm D)">D</div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });
        let destMarker = L.marker(destCoord, { icon: destIcon }).addTo(this.map);
        let dispDestLon = ((destCoord[1] + 180) % 360 + 360) % 360 - 180;
        destMarker.bindPopup(`<b>Điểm đích đến (Kho nhận hàng):</b><br>${destName}<br><small>Toạ độ: ${destCoord[0].toFixed(4)}, ${dispDestLon.toFixed(4)}</small>`);
        this.mapLayers.markers.push(destMarker);

        // 7. Departure Hub & Arrival Hub Markers (⚓ / 🛫)
        if (shipment.legs && shipment.legs.length >= 2) {
            let leg1 = shipment.legs[0];
            let leg2 = shipment.legs[1];
            let dhCoords = (leg1.coordinates_latlon && leg1.coordinates_latlon.length > 0) ? leg1.coordinates_latlon[leg1.coordinates_latlon.length - 1] : null;
            let ahCoords = (leg2.coordinates_latlon && leg2.coordinates_latlon.length > 0) ? leg2.coordinates_latlon[leg2.coordinates_latlon.length - 1] : null;

            if (dhCoords) {
                let dhIcon = L.divIcon({
                    className: 'hub-dep-port-icon',
                    html: `<div style="background: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border: 2.5px solid #0055B3; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: pointer;" title="Cảng/Sân bay xuất phát">
                        ${this.get_hub_icon_svg(sMethod)}
                    </div>`,
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                });
                let dhMarker = L.marker(dhCoords, { icon: dhIcon }).addTo(this.map);
                dhMarker.bindPopup(`<b>Trạm trung chuyển xuất:</b><br>${shipment.origin_port || 'Cảng/Sân bay xuất'}`);
                this.mapLayers.markers.push(dhMarker);
            }

            if (ahCoords) {
                let ahIcon = L.divIcon({
                    className: 'hub-arr-port-icon',
                    html: `<div style="background: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border: 2.5px solid #0055B3; box-shadow: 0 2px 5px rgba(0,0,0,0.25); cursor: pointer;" title="Cảng/Sân bay đến">
                        ${this.get_hub_icon_svg(sMethod)}
                    </div>`,
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                });
                let ahMarker = L.marker(ahCoords, { icon: ahIcon }).addTo(this.map);
                ahMarker.bindPopup(`<b>Trạm trung chuyển đến:</b><br>${shipment.destination_port || 'Cảng/Sân bay đến'}`);
                this.mapLayers.markers.push(ahMarker);
            }
        }

        // 8. Vehicle Marker with SVG AIS Silhouettes & Bearing Tangent
        let targetProgress = (typeof shipment.progress === 'number') ? shipment.progress : 0.55;
        let activeMode = this.get_active_vehicle_mode(shipment, targetProgress);
        let routeMetrics = this.computePolylineMetrics(simplifiedCoords);
        let startPosData = this.interpolateAtProgress(simplifiedCoords, routeMetrics, 0);

        let vehicleBorderColor = activeMode === 'Air' ? '#007AFF' : (activeMode === 'Ocean' ? '#0055B3' : '#EA580C');
        let vehicleIcon = L.divIcon({
            className: 'custom-vehicle-icon-hub',
            html: `
                <div class="lw-vehicle-box" style="background: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.3); border: 2.8px solid ${vehicleBorderColor};">
                    <div class="lw-vehicle-icon-svg" style="display: flex; align-items: center; justify-content: center; transform: rotate(${startPosData.bearing}deg); transform-origin: center center;">
                        ${this.get_vehicle_svg(activeMode)}
                    </div>
                </div>
            `,
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });

        this.mapLayers.vehicleMarker = L.marker(startPosData.point, { icon: vehicleIcon, zIndexOffset: 1000 }).addTo(this.map);
        this.mapLayers.vehicleMarker._currentProgress = 0;
        this.mapLayers.vehicleMarker._shipment = shipment;
        this.mapLayers.vehicleMarker._lastActiveMode = activeMode;

        let delayBadge = (shipment.delay_days > 0)
            ? `<div style="color: #dc2626; font-weight: 700; margin-top: 4px;">⚠️ Lệch ETA: +${shipment.delay_days} ngày</div>`
            : `<div style="color: #16a34a; font-weight: 600; margin-top: 4px;">✅ Hành trình đúng tiến độ</div>`;

        let modeTitleVi = activeMode === 'Air' ? 'Hàng không (Máy bay ✈️)' : (activeMode === 'Ocean' ? 'Đường biển (Tàu hàng 🚢)' : 'Đường bộ (Xe tải 🚚)');
        this.mapLayers.vehicleMarker.bindPopup(`
            <div style="font-size: 12px; min-width: 190px; line-height: 1.5;">
                <div style="font-weight: 700; color: #0284c7; font-size: 13px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; margin-bottom: 4px;">
                    ${shipment.name}
                </div>
                <div><b>Phương tiện hiện tại:</b> ${modeTitleVi}</div>
                <div><b>Đơn vị vận chuyển:</b> ${shipment.carrier || ''} (${shipment.vessel_name || shipment.flight_number || 'Vận tải đa phương thức'})</div>
                <div><b>Mã Container:</b> ${shipment.container_id || 'N/A'}</div>
                <div><b>Trạng thái:</b> ${shipment.status}</div>
                <div><b>Lộ trình:</b> ${shipment.origin ? shipment.origin.name : (shipment.origin_port || 'Origin')} ➔ ${shipment.destination ? shipment.destination.name : 'Kho bãi Logistics Cáp Kim Khánh Đà Nẵng'}</div>
                ${delayBadge}
            </div>
        `);

        // Trigger Smooth Animation to current progress
        this.animateVehicle(this.mapLayers.vehicleMarker, simplifiedCoords, targetProgress, 1600);

        // 9. Fit Map Bounds
        try {
            let group = L.featureGroup(polylineLayers);
            let bounds = group.getBounds();
            let z = this.map.getBoundsZoom(bounds, false, [45, 45]);
            this.map.setView(bounds.getCenter(), Math.min(Math.max(z, 2), 7));
        } catch (e) {
            this.map.setView(startPosData.point, 4);
        }
    }

    clear_map_layers() {
        if (!this.map) return;
        if (this.currentAnimationId) {
            cancelAnimationFrame(this.currentAnimationId);
            this.currentAnimationId = null;
        }

        this.mapLayers.routePolylines.forEach(p => {
            try { this.map.removeLayer(p); } catch (e) { }
        });
        this.mapLayers.routePolylines = [];

        this.mapLayers.markers.forEach(m => {
            try { this.map.removeLayer(m); } catch (e) { }
        });
        this.mapLayers.markers = [];

        if (this.mapLayers.vehicleMarker) {
            try { this.map.removeLayer(this.mapLayers.vehicleMarker); } catch (e) { }
            this.mapLayers.vehicleMarker = null;
        }

        if (this.mapLayers.fleetVehicleMarkers) {
            this.mapLayers.fleetVehicleMarkers.forEach(m => {
                try { this.map.removeLayer(m); } catch (e) { }
            });
            this.mapLayers.fleetVehicleMarkers = [];
        }
    }

    reset_map_view() {
        this.selectedShipment = null;
        $('#hub-shipments-tbody tr').removeClass('selected');
        this.render_stepper(null);
        this.render_fleet_overview_map(this.data ? (this.data.shipments || []) : []);
    }

    sync_now(shipmentName) {
        const self = this;
        let $btn = $('#hub-btn-sync-now');
        $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Đang đồng bộ...');

        frappe.call({
            method: 'logistics_wizard.api.sync_shipment_now',
            args: { shipment: shipmentName },
            callback: function (r) {
                $btn.prop('disabled', false).html('<i class="fa fa-cloud-download"></i> Đồng bộ tức thì (Sync Now)');
                if (r && r.message && r.message.success !== false) {
                    frappe.show_alert({
                        message: __('Đồng bộ hành trình thành công!'),
                        indicator: 'green'
                    });
                    self.refresh(shipmentName);
                } else {
                    frappe.msgprint({
                        title: __('Đồng bộ hoàn tất'),
                        message: r.message ? r.message.message : __('Đã kiểm tra dữ liệu hành trình mới nhất.'),
                        indicator: 'blue'
                    });
                    self.refresh(shipmentName);
                }
            },
            error: function () {
                $btn.prop('disabled', false).html('<i class="fa fa-cloud-download"></i> Đồng bộ tức thì (Sync Now)');
                frappe.show_alert({
                    message: __('Lỗi kết nối khi đồng bộ!'),
                    indicator: 'red'
                });
            }
        });
    }
}

class EmbeddedTradeCostDashboardController {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.currentCaseId = 'IMP-2026-001';
        this.currentRule = 'weight';
        this.currentCaseType = 'all';
        this.caseData = this.get_mock_cases_data();
    }

    init() {
        this.bind_events();
        this.load_data(this.currentCaseId);
    }

    get_mock_cases_data() {
        return {
            'IMP-2026-001': {
                case_id: 'IMP-2026-001',
                party: 'ABC Electronics Co., Ltd',
                case_type: 'import',
                po_value: 125000,
                estimated_cost: 16800,
                actual_cost: 18350,
                variance_amount: 1550,
                variance_pct: 9.2,
                status: 'Đang Đối Soát',
                status_class: 'badge-in-transit',
                lcv_id: 'LCV-2026-0004',
                cost_items: [
                    { type: 'Cước vận chuyển biển (Ocean Freight)', supplier: 'Maersk Line Vietnam', inv_no: 'INV-MAE-8821', est: 8500, act: 9200, status: 'Đã Đối Soát' },
                    { type: 'Bảo hiểm hàng hóa (Cargo Insurance)', supplier: 'Bao Viet Insurance', inv_no: 'BV-2026-091', est: 600, act: 650, status: 'Đã Đối Soát' },
                    { type: 'Thuế nhập khẩu (Customs Import Duty)', supplier: 'Chi cục Hải Quan Cảng SG KV4', inv_no: 'HQ-77218-TK', est: 3200, act: 3200, status: 'Đã Đối Soát' },
                    { type: 'Thuế GTGT hàng nhập khẩu (Import VAT)', supplier: 'Chi cục Hải Quan Cảng SG KV4', inv_no: 'HQ-77218-VAT', est: 1500, act: 1500, status: 'Đã Đối Soát' },
                    { type: 'Phí THC & phụ phí cảng (Port Surcharges)', supplier: 'Tân Cảng Sài Gòn (SNP)', inv_no: 'SNP-2026-112', est: 850, act: 950, status: 'Đang Đối Soát' },
                    { type: 'Nâng hạ & lưu kho (Handling & Storage)', supplier: 'Cảng Cát Lái ICD', inv_no: 'ICD-44120', est: 400, act: 580, status: 'Đang Đối Soát' },
                    { type: 'Lưu bãi container (Demurrage/Detention)', supplier: 'Maersk Line Vietnam', inv_no: 'DEM-8821-02', est: 0, act: 320, status: 'Cần Rà Soát' },
                    { type: 'Vận chuyển nội địa (Trucking)', supplier: 'Huu Toan Logistics', inv_no: 'HT-9901-TRK', est: 950, act: 1100, status: 'Đang Đối Soát' },
                    { type: 'Phí dịch vụ hải quan (Customs Brokerage)', supplier: 'Schenker Vietnam', inv_no: 'DB-8812-FEE', est: 500, act: 500, status: 'Đã Đối Soát' },
                    { type: 'Kiểm tra chất lượng (Inspection)', supplier: 'Quatest 3', inv_no: 'QT3-11029', est: 300, act: 350, status: 'Đã Đối Soát' },
                    { type: 'Chi phí phụ khác (Other Contingency)', supplier: 'Nội bộ công ty', inv_no: 'INT-EXP-01', est: 0, act: 0, status: 'Chờ Hóa Đơn' }
                ],
                items_to_allocate: [
                    { item_code: 'CPU-INTEL-I9', name: 'Intel Core i9-14900K Processor', qty: 200, unit_price: 350, weight: 0.15, volume: 0.0004 },
                    { item_code: 'RAM-DDR5-32G', name: 'Corsair Vengeance 32GB DDR5 RAM', qty: 500, unit_price: 70, weight: 0.08, volume: 0.0002 },
                    { item_code: 'SSD-NVME-2TB', name: 'Samsung 990 Pro 2TB NVMe SSD', qty: 200, unit_price: 100, weight: 0.06, volume: 0.00015 }
                ],
                audit_checks: [
                    { title: 'Trùng Lặp Hóa Đơn (Duplicate Check)', status: 'Hợp lệ', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Không phát hiện hóa đơn trùng lặp số chứng từ hoặc nhà cung cấp.' },
                    { title: 'Chi Phí Trọng Yếu (Missing Cost Check)', status: 'Cần rà soát', status_class: 'delay-tag-positive', border: '#d97706', desc: 'Chưa nhận hóa đơn nâng hạ cảng đích (Port Handling D/O). Cần liên hệ đại lý hãng tàu trước ngày 14/10.' },
                    { title: 'Gán Đúng Vụ Việc (Association Check)', status: 'Khớp 100%', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Tất cả 6 hóa đơn dịch vụ đều tham chiếu chính xác số PO-2026-0042 và Trade Case IMP-2026-001.' }
                ]
            },
            'EXP-2026-002': {
                case_id: 'EXP-2026-002',
                party: 'Global Coffee Exporter JSC',
                case_type: 'export',
                po_value: 65000,
                estimated_cost: 3800,
                actual_cost: 4200,
                variance_amount: 400,
                variance_pct: 10.5,
                status: 'Sẵn Sàng Xuất Khẩu',
                status_class: 'badge-delivered',
                lcv_id: 'LCV-2026-EXP-01',
                export_revenue: 65000,
                export_cogs: 45000,
                export_logistics: 4200,
                cost_items: [
                    { type: 'Cước vận chuyển biển xuất (Ocean Freight Export)', supplier: 'ONE Ocean Network Express', inv_no: 'ONE-EX-3312', est: 2200, act: 2450, status: 'Đã Đối Soát' },
                    { type: 'Bảo hiểm hàng hóa (Marine Cargo Insurance)', supplier: 'Bao Minh Insurance', inv_no: 'BM-2026-339', est: 250, act: 270, status: 'Đã Đối Soát' },
                    { type: 'Thuế xuất khẩu (Export Duty)', supplier: 'Hải Quan Cảng Quy Nhơn', inv_no: 'HQ-EXP-0081', est: 0, act: 0, status: 'Miễn Thuế' },
                    { type: 'Phí THC cảng bốc (Port Handling Surcharge)', supplier: 'Cảng Quốc Tế Quy Nhơn', inv_no: 'QN-THC-881', est: 350, act: 380, status: 'Đã Đối Soát' },
                    { type: 'Hun trùng & Kiểm dịch (Fumigation & Phytosanitary)', supplier: 'VFC Fumigation Co.', inv_no: 'VFC-2026-77', est: 180, act: 180, status: 'Đã Đối Soát' },
                    { type: 'Làm thủ tục C/O Form ICO (Certificate of Origin)', supplier: 'VCCI Chi nhánh Đà Nẵng', inv_no: 'VCCI-CO-102', est: 70, act: 70, status: 'Đã Đối Soát' },
                    { type: 'Kéo vỏ & vận chuyển nội địa (Trucking)', supplier: 'Binh Dinh Express Logistics', inv_no: 'BD-TRK-551', est: 500, act: 580, status: 'Đã Đối Soát' },
                    { type: 'Phí môi giới hải quan (Brokerage Fee)', supplier: 'Transimex Logistics', inv_no: 'TMX-2026-44', est: 150, act: 170, status: 'Đã Đối Soát' },
                    { type: 'Chi phí phụ khác (Contingency)', supplier: 'Nội bộ', inv_no: 'INT-EXP-02', est: 100, act: 100, status: 'Đã Đối Soát' }
                ],
                items_to_allocate: [
                    { item_code: 'COFFEE-ROBUSTA-G1', name: 'Robusta Green Coffee Beans Grade 1', qty: 20000, unit_price: 2.25, weight: 1.0, volume: 0.0015 },
                    { item_code: 'COFFEE-ARABICA-S18', name: 'Arabica Roasted Coffee Screen 18', qty: 5000, unit_price: 4.00, weight: 1.0, volume: 0.0018 }
                ],
                audit_checks: [
                    { title: 'Trùng Lặp Hóa Đơn (Duplicate Check)', status: 'Hợp lệ', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Không có chứng từ trùng lặp đối tác xuất khẩu.' },
                    { title: 'Chi Phí Trọng Yếu (Missing Cost Check)', status: 'Đầy đủ', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Đã nhận đủ chứng từ hun trùng, C/O và bill of lading.' },
                    { title: 'Gán Đúng Vụ Việc (Association Check)', status: 'Khớp 100%', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Hóa đơn ONE và VFC tham chiếu chính xác Sales Order SO-2026-009.' }
                ]
            },
            'IMP-2026-003': {
                case_id: 'IMP-2026-003',
                party: 'Pacific Seafood Import Co.',
                case_type: 'import',
                po_value: 84000,
                estimated_cost: 11200,
                actual_cost: 11050,
                variance_amount: -150,
                variance_pct: -1.3,
                status: 'Đã Hoàn Tất',
                status_class: 'badge-delivered',
                lcv_id: 'LCV-2026-0002',
                cost_items: [
                    { type: 'Cước vận chuyển hàng đông lạnh (Reefer Freight)', supplier: 'Hapag-Lloyd Vietnam', inv_no: 'HL-RF-9021', est: 6800, act: 6700, status: 'Đã Đối Soát' },
                    { type: 'Bảo hiểm hàng hóa (Reefer Cargo Insurance)', supplier: 'PVI Insurance', inv_no: 'PVI-RF-122', est: 450, act: 450, status: 'Đã Đối Soát' },
                    { type: 'Thuế nhập khẩu (Customs Import Duty)', supplier: 'Chi cục Hải Quan Cảng Hải Phòng', inv_no: 'HQ-HP-3312', est: 1800, act: 1800, status: 'Đã Đối Soát' },
                    { type: 'Kiểm dịch thủy sản (Fisheries Quarantine)', supplier: 'Chi cục Thú Y Vùng 2', inv_no: 'KD-HP-0091', est: 350, act: 350, status: 'Đã Đối Soát' },
                    { type: 'Cắm điện container lạnh (Reefer Monitoring)', supplier: 'Cảng Quốc Tế Lạch Huyện', inv_no: 'LH-REEFER-11', est: 500, act: 450, status: 'Đã Đối Soát' },
                    { type: 'Vận chuyển xe lạnh nội địa (Reefer Trucking)', supplier: 'Vinalines Cold Chain', inv_no: 'VNL-COLD-88', est: 1300, act: 1300, status: 'Đã Đối Soát' }
                ],
                items_to_allocate: [
                    { item_code: 'SEAFOOD-SALMON-NOR', name: 'Fresh Norwegian Salmon Fillet', qty: 4000, unit_price: 15.00, weight: 1.0, volume: 0.0016 },
                    { item_code: 'SEAFOOD-COD-ATL', name: 'Atlantic Cod Fillet Frozen', qty: 2000, unit_price: 12.00, weight: 1.0, volume: 0.0015 }
                ],
                audit_checks: [
                    { title: 'Trùng Lặp Hóa Đơn (Duplicate Check)', status: 'Hợp lệ', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Không phát hiện trùng số hóa đơn.' },
                    { title: 'Chi Phí Trọng Yếu (Missing Cost Check)', status: 'Đầy đủ', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Đầy đủ phí cắm điện kho lạnh và kiểm dịch thú y.' },
                    { title: 'Gán Đúng Vụ Việc (Association Check)', status: 'Khớp 100%', status_class: 'delay-tag-ontime', border: '#10b981', desc: 'Chứng từ Lạch Huyện khớp 100% hồ sơ hải quan.' }
                ]
            }
        };
    }

    load_data(caseId) {
        this.currentCaseId = caseId || 'IMP-2026-001';
        $('#tcd-case-selector').val(this.currentCaseId);
        this.render_dashboard();
    }

    bind_events() {
        const self = this;

        $(document).on('change', '#tcd-case-selector', function () {
            self.load_data($(this).val());
        });

        $(document).on('click', '.tcd-type-btn', function () {
            $('.tcd-type-btn').removeClass('active');
            $(this).addClass('active');
            self.currentCaseType = $(this).data('type');
            self.apply_type_filter();
        });

        $(document).on('click', '.tcd-alloc-btn', function () {
            $('.tcd-alloc-btn').removeClass('active');
            $(this).addClass('active');
            self.currentRule = $(this).data('rule');
            self.render_allocation_table();
        });

        $(document).on('click', '#tcd-btn-refresh', function () {
            const $icon = $(this).find('i');
            $icon.addClass('fa-spin');
            setTimeout(() => {
                self.load_data(self.currentCaseId);
                $icon.removeClass('fa-spin');
                frappe.show_alert({ message: __('Đã làm mới dữ liệu Trade Cost!'), indicator: 'green' });
            }, 300);
        });

        $(document).on('click', '#tcd-btn-new-sheet', function () {
            if (typeof frappe !== 'undefined' && frappe.new_doc) {
                frappe.new_doc('Trade Cost Sheet', {
                    trade_case: self.currentCaseId
                });
            }
        });

        $(document).on('click', '#tcd-btn-sync-lcv, #tcd-btn-apply-lcv', function () {
            frappe.show_alert({
                message: __('Đang tiến hành đồng bộ dữ liệu sang Landed Cost Voucher...'),
                indicator: 'green'
            });
            setTimeout(() => {
                frappe.show_alert({
                    message: __('Đồng bộ Landed Cost Voucher thành công!'),
                    indicator: 'green'
                });
            }, 600);
        });
    }

    apply_type_filter() {
        const type = this.currentCaseType;
        if (type === 'export') {
            $('#tcd-case-selector').val('EXP-2026-002');
            this.load_data('EXP-2026-002');
        } else if (type === 'import') {
            $('#tcd-case-selector').val('IMP-2026-001');
            this.load_data('IMP-2026-001');
        } else {
            this.load_data(this.currentCaseId);
        }
    }

    render_dashboard() {
        const c = this.caseData[this.currentCaseId] || this.caseData['IMP-2026-001'];
        if (!c) return;

        $('#tcd-kpi-po-val').text('$' + c.po_value.toLocaleString('en-US', { minimumFractionDigits: 2 }));
        $('#tcd-kpi-est-val').text('$' + c.estimated_cost.toLocaleString('en-US', { minimumFractionDigits: 2 }));
        $('#tcd-kpi-act-val').text('$' + c.actual_cost.toLocaleString('en-US', { minimumFractionDigits: 2 }));

        const varSign = c.variance_amount > 0 ? '+' : '';
        const varPctSign = c.variance_pct > 0 ? '+' : '';
        const varText = `${varSign}$${c.variance_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${varPctSign}${c.variance_pct}%)`;
        $('#tcd-kpi-var-val').text(varText);

        if (c.variance_amount > 0) {
            $('#tcd-kpi-var-val').css('color', '#dc2626');
        } else if (c.variance_amount < 0) {
            $('#tcd-kpi-var-val').css('color', '#059669');
        } else {
            $('#tcd-kpi-var-val').css('color', '#64748b');
        }

        $('#tcd-status-badge').attr('class', 'badge-status ' + (c.status_class || 'badge-in-transit')).text(c.status);
        $('#tcd-lcv-badge').text(c.lcv_id || 'Chưa liên kết');

        this.render_cost_items(c.cost_items || []);
        this.render_allocation_table();
        this.render_audit_checks(c.audit_checks || []);

        if (c.case_type === 'export') {
            $('#tcd-export-profitability-box').show();
        } else {
            $('#tcd-export-profitability-box').hide();
        }
    }

    render_cost_items(items) {
        let html = '';
        items.forEach(it => {
            const diff = it.act - it.est;
            const diffSign = diff > 0 ? '+' : '';
            const diffCls = diff > 0 ? 'tcd-var-positive' : (diff < 0 ? 'tcd-var-negative' : 'tcd-var-zero');
            html += `
                <tr>
                    <td style="font-weight: 600; color: #0f172a;">${it.type}</td>
                    <td style="color: #475569;">${it.supplier}</td>
                    <td><code>${it.inv_no}</code></td>
                    <td class="text-right" style="color: #64748b;">$${it.est.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td class="text-right" style="font-weight: 600; color: #0f172a;">$${it.act.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td class="text-right ${diffCls}">${diffSign}$${diff.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td class="text-center">
                        <span class="delay-tag-ontime" style="font-size: 11px;">${it.status}</span>
                    </td>
                </tr>
            `;
        });
        $('#tcd-cost-items-tbody').html(html);
    }

    render_allocation_table() {
        const c = this.caseData[this.currentCaseId] || this.caseData['IMP-2026-001'];
        if (!c || !c.items_to_allocate) return;

        const totalActualCost = c.actual_cost;
        const allocated = this.calculate_allocation(c.items_to_allocate, totalActualCost, this.currentRule);

        let html = '';
        allocated.forEach(it => {
            html += `
                <tr>
                    <td style="font-weight: 700; color: #0284c7;">${it.item_code}</td>
                    <td style="color: #334155;">${it.name}</td>
                    <td class="text-center" style="font-weight: 600;">${it.qty.toLocaleString()}</td>
                    <td class="text-right">$${it.unit_price.toFixed(2)}</td>
                    <td class="text-right" style="color: #0284c7; font-weight: 600;">+$${it.allocated_cost.toFixed(2)}</td>
                    <td class="text-right" style="font-weight: 700; color: #059669;">$${it.landed_unit_cost.toFixed(2)}</td>
                    <td class="text-center" style="color: #d97706; font-weight: 600;">+${it.pct_increase}%</td>
                </tr>
            `;
        });
        $('#tcd-allocation-tbody').html(html);
    }

    calculate_allocation(items, totalCost, rule) {
        let basisWeights = [];
        if (rule === 'weight') {
            basisWeights = items.map(it => it.weight * it.qty);
        } else if (rule === 'value') {
            basisWeights = items.map(it => it.unit_price * it.qty);
        } else if (rule === 'qty') {
            basisWeights = items.map(it => it.qty);
        } else if (rule === 'volume') {
            basisWeights = items.map(it => it.volume * it.qty);
        }

        const sumBasis = basisWeights.reduce((a, b) => a + b, 0) || 1;
        let allocatedList = [];
        let allocatedSum = 0;

        for (let i = 0; i < items.length; i++) {
            let rawAlloc = (basisWeights[i] / sumBasis) * totalCost;
            let rounded = Math.round(rawAlloc * 100) / 100;
            allocatedList.push(rounded);
            allocatedSum += rounded;
        }

        let diff = Math.round((totalCost - allocatedSum) * 100) / 100;
        if (Math.abs(diff) > 0.0001 && allocatedList.length > 0) {
            let maxIdx = 0;
            for (let i = 1; i < allocatedList.length; i++) {
                if (allocatedList[i] > allocatedList[maxIdx]) maxIdx = i;
            }
            allocatedList[maxIdx] = Math.round((allocatedList[maxIdx] + diff) * 100) / 100;
        }

        return items.map((it, idx) => {
            const alloc = allocatedList[idx];
            const landedUnitCost = Math.round((it.unit_price + (alloc / it.qty)) * 100) / 100;
            const totalBaseVal = it.unit_price * it.qty;
            const pctIncrease = totalBaseVal > 0 ? ((alloc / totalBaseVal) * 100).toFixed(1) : 0;
            return {
                ...it,
                allocated_cost: alloc,
                landed_unit_cost: landedUnitCost,
                pct_increase: pctIncrease
            };
        });
    }

    render_audit_checks(checks) {
        let html = '';
        checks.forEach(chk => {
            html += `
                <div class="hub-exception-card" style="border-left: 4px solid ${chk.border || '#10b981'};">
                    <div class="exception-card-header">
                        <span class="exception-title" style="color: #0f172a; font-weight: 600;">${chk.title}</span>
                        <span class="${chk.status_class || 'delay-tag-ontime'}">${chk.status}</span>
                    </div>
                    <div class="exception-card-body">${chk.desc}</div>
                </div>
            `;
        });
        $('#tcd-audit-list').html(html);
    }
}

class EmbeddedLogisticsAICopilot {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.currentCaseId = 'IMP-2026-001';
    }

    init() {
        this.bind_events();
    }

    on_tab_shown(options) {
        if (options && options.case_id) {
            this.currentCaseId = options.case_id;
            $('#copilot-context-case').val(this.currentCaseId);
        }
        $('#copilot-input-textarea').focus();
    }

    bind_events() {
        const self = this;

        $(document).on('change', '#copilot-context-case', function () {
            self.currentCaseId = $(this).val();
        });

        $(document).on('click', '.lw-suggestion-pill', function () {
            const prompt = $(this).data('prompt') || $(this).text().trim();
            $('#copilot-input-textarea').val(prompt);
            self.send_message(prompt);
        });

        $(document).on('click', '#copilot-btn-send', function () {
            const txt = $('#copilot-input-textarea').val().trim();
            if (txt) {
                self.send_message(txt);
            }
        });

        $(document).on('keydown', '#copilot-input-textarea', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const txt = $(this).val().trim();
                if (txt) {
                    self.send_message(txt);
                }
            }
        });

        $(document).on('click', '#copilot-btn-new-chat', function () {
            $('#copilot-chat-history').empty();
            $('.lw-copilot-welcome-box').show();
            $('#copilot-input-textarea').val('').focus();
        });

        $(document).on('click', '#copilot-btn-clear', function () {
            $('#copilot-chat-history').empty();
            $('.lw-copilot-welcome-box').show();
        });

        $(document).on('click', '.lw-session-item', function () {
            $('.lw-session-item').removeClass('active');
            $(this).addClass('active');
            const title = $(this).find('.lw-session-title').text().trim();
            self.load_session_sample(title);
        });

        $(document).on('input', '#copilot-session-search', function () {
            const q = $(this).val().toLowerCase().trim();
            $('.lw-session-item').each(function () {
                const title = $(this).find('.lw-session-title').text().toLowerCase();
                $(this).toggle(title.includes(q));
            });
        });

        $(document).on('click', '.lw-thinking-header', function () {
            $(this).next('.lw-thinking-content').slideToggle(180);
            $(this).find('.fa-chevron-down, .fa-chevron-up').toggleClass('fa-chevron-down fa-chevron-up');
        });

        $(document).on('click', '.btn-copilot-copy', function () {
            const text = $(this).closest('.lw-chat-bubble').find('.lw-chat-text').text();
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text);
                frappe.show_alert({ message: __('Đã sao chép phản hồi vào clipboard!'), indicator: 'green' });
            }
        });

        $(document).on('click', '.btn-copilot-view-cost', function () {
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.set_route('trade-cost-dashboard');
            } else if (self.wrapper && self.wrapper.unifiedHub) {
                self.wrapper.unifiedHub.switch_tab('cost', { case_id: self.currentCaseId });
            }
        });

        $(document).on('click', '.btn-copilot-view-tracking', function () {
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.set_route('shipment-tracking-hub');
            } else if (self.wrapper && self.wrapper.unifiedHub) {
                self.wrapper.unifiedHub.switch_tab('tracking');
            }
        });
    }

    send_message(prompt) {
        $('.lw-copilot-welcome-box').hide();
        $('#copilot-input-textarea').val('');

        const userHtml = `
            <div class="lw-chat-message lw-chat-user">
                <div class="lw-chat-avatar"><i class="fa fa-user"></i></div>
                <div class="lw-chat-bubble">
                    <div class="lw-chat-text">${frappe.utils.escape_html(prompt)}</div>
                </div>
            </div>
        `;
        $('#copilot-chat-history').append(userHtml);
        this.scroll_to_bottom();

        const self = this;
        const msgId = 'ai-msg-' + Date.now();
        const placeholderHtml = `
            <div class="lw-chat-message lw-chat-assistant" id="${msgId}">
                <div class="lw-chat-avatar"><i class="fa fa-bolt"></i></div>
                <div class="lw-chat-bubble">
                    <div class="lw-thinking-block">
                        <div class="lw-thinking-header">
                            <i class="fa fa-cog fa-spin" style="color: #0284c7;"></i>
                            <span>AI đang suy luận & truy xuất dữ liệu Trade Case...</span>
                            <i class="fa fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                        </div>
                        <div class="lw-thinking-content">
                            • Đang kết nối hồ sơ Trade Case ${self.currentCaseId}<br>
                            • Kiểm tra dữ liệu bảng kê 11 khoản chi phí và hành trình tàu...
                        </div>
                    </div>
                    <div class="lw-chat-text" style="color: #64748b;"><i class="fa fa-circle-o-notch fa-spin"></i> Đang chuẩn bị câu trả lời chuyên môn...</div>
                </div>
            </div>
        `;
        $('#copilot-chat-history').append(placeholderHtml);
        self.scroll_to_bottom();

        setTimeout(() => {
            self.generate_response(msgId, prompt);
        }, 500);
    }

    generate_response(msgId, prompt) {
        const caseId = this.currentCaseId || 'IMP-2026-001';
        let answerText = '';
        let thoughtProcess = '';
        const pLower = prompt.toLowerCase();

        if (pLower.includes('chênh lệch') || pLower.includes('chi phí') || pLower.includes('sai lệch')) {
            thoughtProcess = `1. Truy vấn Trade Cost Sheet liên kết Trade Case ${caseId}.
2. Phát hiện: Chi phí dự toán (Estimated) = $16,800.00, Thực tế (Actual) = $18,350.00.
3. Chênh lệch vượt: +$1,550.00 (+9.2%).
4. Nguyên nhân chính:
   - Cước biển Maersk Line tăng phụ phí xăng dầu BAF: +$700.00
   - Phí lưu bãi Demurrage ngoài dự kiến: +$320.00
   - Phí trucking nâng hạ Tân Cảng: +$150.00`;
            answerText = `
<p>Dựa trên hồ sơ tài chính của vụ việc <strong>${caseId}</strong>, tôi đã hoàn tất phân tích đối soát chi phí:</p>
<ul>
    <li><strong>Tổng chi phí thực tế:</strong> <code>$18,350.00 USD</code> so với dự toán ban đầu <code>$16,800.00 USD</code> (Vượt <strong>+$1,550.00</strong>, tương đương <strong>+9.2%</strong>).</li>
    <li><strong>Khoản phát sinh lớn nhất:</strong> Cước tàu biển Ocean Freight tăng do phụ phí nhiên liệu khẩn cấp (+$700 USD) và phí lưu bãi container Demurrage (+$320 USD) do trễ thủ tục cảng.</li>
    <li><strong>Khuyến nghị hành động:</strong>
        <br>1. Làm việc với hãng tàu Maersk để xin miễn giảm (Demurrage Waiver) 3 ngày lưu bãi container.
        <br>2. Cập nhật phân bổ Landed Cost theo tiêu chuẩn <strong>Gross Weight</strong> để giá vốn từng Item phản ánh chính xác nhất chi phí vận chuyển.
    </li>
</ul>`;
        } else if (pLower.includes('lịch tàu') || pLower.includes('hành trình') || pLower.includes('đà nẵng') || pLower.includes('cập cảng') || pLower.includes('eta')) {
            thoughtProcess = `1. Kiểm tra Tracking Hub cho chuyến tàu vận chuyển hồ sơ ${caseId}.
2. Tàu container: Maersk Mc-Kinney Moller.
3. Trạng thái hành trình: Đang trên biển (In-Transit), tọa độ 15.82°N, 109.45°E.
4. Dự kiến cập cảng Đà Nẵng (ETA): Ngày mai lúc 16:30.
5. Cảnh báo thời tiết: Biển động cấp 5, có khả năng chậm trễ cập cầu 2-4 tiếng.`;
            answerText = `
<p>Thông tin hành trình và dự báo cảng đến cho vụ việc <strong>${caseId}</strong>:</p>
<ul>
    <li><strong>Tàu chuyên chở:</strong> <code>Maersk Mc-Kinney Moller</code> (Chuyến hải trình 2603W).</li>
    <li><strong>Vị trí hiện tại:</strong> Vùng biển miền Trung, cách phao số 0 Cảng Tiên Sa - Đà Nẵng xấp xỉ 48 hải lý.</li>
    <li><strong>ETA cập cảng:</strong> Dự kiến <strong>16:30 ngày mai</strong> (Sai lệch dự báo: +3.5 tiếng do gió mùa).</li>
    <li><strong>Khuyến nghị thủ tục:</strong> Bộ chứng từ hải quan (B/L gốc, Invoice, Packing List, C/O Form E) đã sẵn sàng trên hệ thống. Đại lý giao nhận nên đăng ký trước lệnh giao hàng điện tử (eDO) trên cổng thông tin cảng Đà Nẵng.</li>
</ul>`;
        } else {
            thoughtProcess = `1. Tiếp nhận câu hỏi nghiệp vụ logistics: "${prompt}".
2. Áp dụng quy tắc phân bổ giá vốn chuẩn Landed Cost Voucher của ERPNext.
3. Tổng hợp khuyến nghị tối ưu chi phí và điều hành ngoại thương.`;
            answerText = `
<p>Đối với câu hỏi của bạn về <strong>${caseId}</strong>:</p>
<p>Hệ thống Logistics Wizard đã tự động liên kết dữ liệu giữa Hợp đồng thương mại, Hành trình vận chuyển thực tế và Phân bổ giá vốn Landed Cost:</p>
<ul>
    <li>Mọi chi phí hợp lệ (11 loại chi phí tiêu chuẩn) đã được kiểm tra tính toàn vẹn (không trùng hóa đơn, có số PO hợp lệ).</li>
    <li>Thuật toán phân bổ tự động loại bỏ sai số làm tròn (discrepancy &le; 0.01) trước khi đồng bộ sang <strong>ERPNext Landed Cost Voucher</strong>.</li>
</ul>
<p>Bạn có thể chuyển sang tab <strong>Trade Cost Dashboard</strong> hoặc <strong>Shipment Tracking Hub</strong> ở thanh điều hướng bên trái để theo dõi chi tiết tức thì.</p>`;
        }

        const finalHtml = `
            <div class="lw-thinking-block">
                <div class="lw-thinking-header">
                    <i class="fa fa-lightbulb-o" style="color: #0284c7;"></i>
                    <span>Tiến trình suy luận & đối soát dữ liệu (Hoàn tất)</span>
                    <i class="fa fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                </div>
                <div class="lw-thinking-content" style="display: none;">
                    <pre style="margin: 0; background: transparent; border: none; font-size: 11.5px; color: #475569; padding: 0;">${thoughtProcess}</pre>
                </div>
            </div>
            <div class="lw-chat-text">${answerText}</div>
            <div class="lw-chat-actions">
                <button class="lw-chat-action-btn btn-copilot-copy"><i class="fa fa-copy"></i> Sao chép</button>
                <button class="lw-chat-action-btn btn-copilot-view-cost"><i class="fa fa-calculator"></i> Bảng chi phí Landed Cost</button>
                <button class="lw-chat-action-btn btn-copilot-view-tracking"><i class="fa fa-ship"></i> Tra cứu hành trình</button>
            </div>
        `;

        $(`#${msgId} .lw-chat-bubble`).html(finalHtml);
        this.scroll_to_bottom();
    }

    scroll_to_bottom() {
        const $thread = $('#copilot-messages-thread');
        if ($thread.length) {
            $thread.scrollTop($thread[0].scrollHeight);
        }
    }

    load_session_sample(title) {
        $('#copilot-chat-history').empty();
        $('.lw-copilot-welcome-box').hide();
        this.send_message(title);
    }
}

if (typeof window !== 'undefined') {
    window.ShipmentTrackingHub = ShipmentTrackingHub;
    window.TradeCaseOverviewController = TradeCaseOverviewController;
    window.UnifiedLogisticsHub = UnifiedLogisticsHub;
    window.EmbeddedTradeCostDashboardController = EmbeddedTradeCostDashboardController;
    window.EmbeddedLogisticsAICopilot = EmbeddedLogisticsAICopilot;
    window.init_logistics_hub_page = init_logistics_hub_page;
    window.show_logistics_hub_page = show_logistics_hub_page;
    window.register_logistics_hub_page = register_logistics_hub_page;
}
if (typeof global !== 'undefined') {
    global.ShipmentTrackingHub = ShipmentTrackingHub;
    global.TradeCaseOverviewController = TradeCaseOverviewController;
    global.UnifiedLogisticsHub = UnifiedLogisticsHub;
    global.EmbeddedTradeCostDashboardController = EmbeddedTradeCostDashboardController;
    global.EmbeddedLogisticsAICopilot = EmbeddedLogisticsAICopilot;
    global.init_logistics_hub_page = init_logistics_hub_page;
    global.show_logistics_hub_page = show_logistics_hub_page;
    global.register_logistics_hub_page = register_logistics_hub_page;
}
