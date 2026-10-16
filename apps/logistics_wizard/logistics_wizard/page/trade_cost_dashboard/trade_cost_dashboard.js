// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * Trade Cost & Landed Cost Financial Hub Controller
 * Page route: /app/trade-cost-dashboard
 */

frappe.pages['trade-cost-dashboard'] = frappe.pages['trade-cost-dashboard'] || {};

frappe.pages['trade-cost-dashboard'].on_page_load = function (wrapper) {
    wrapper.tradeCostDashboard = new TradeCostDashboardController(wrapper);
};

frappe.pages['trade-cost-dashboard'].on_page_show = function (wrapper) {
    if (wrapper.tradeCostDashboard) {
        wrapper.tradeCostDashboard.refresh();
    }
};

class TradeCostDashboardController {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.currentCaseId = 'IMP-2026-001';
        this.currentRule = 'weight';
        this.currentCaseType = 'all';

        this.init_page();
        this.bind_events();
        this.load_dashboard_data(this.currentCaseId);
    }

    init_page() {
        if (this.wrapper && typeof frappe !== 'undefined' && frappe.ui && frappe.ui.make_app_page) {
            this.page = frappe.ui.make_app_page({
                parent: this.wrapper,
                title: __('Trade Cost & Landed Cost Dashboard'),
                single_column: true
            });
            if (this.page && this.page.container) {
                this.page.container.removeClass('container').addClass('container-fluid');
                this.page.container.css({ 'max-width': '100%', 'padding': '0', 'margin': '0' });
            }
            const $w = $(this.wrapper);
            $w.closest('.page-container').addClass('logistics-full-width').css({ 'max-width': '100%', 'padding': '0', 'margin': '0' });
            $w.find('.page-content.container').removeClass('container').addClass('container-fluid');
            $w.find('.page-body, .page-content, .layout-main-section-wrapper, .layout-main-section').css({ 'max-width': '100%', 'padding': '0', 'margin': '0', 'border': 'none', 'box-shadow': 'none' });
            this.$body = $(this.page.body);
        } else {
            this.$body = $(this.wrapper || document.body);
        }

        let renderedHtml = '';
        if (typeof frappe !== 'undefined' && frappe.templates && frappe.templates['trade_cost_dashboard']) {
            renderedHtml = frappe.render_template('trade_cost_dashboard', {});
        }
        if (renderedHtml && !this.$body.find('#trade-cost-dashboard-app').length) {
            this.$body.html(renderedHtml);
        }

        this.$app = this.$body.find('#trade-cost-dashboard-app');
    }

    bind_events() {
        const self = this;

        // 1. Refresh button
        this.$app.find('#btn-tcd-refresh').on('click', function () {
            $(this).addClass('fa-spin');
            self.load_dashboard_data(self.currentCaseId, () => {
                $(this).removeClass('fa-spin');
            });
        });

        // 2. New Cost Sheet
        this.$app.find('#btn-tcd-new-sheet').on('click', function () {
            if (typeof frappe !== 'undefined' && frappe.new_doc) {
                frappe.new_doc('Trade Cost Sheet', {
                    trade_case: self.currentCaseId
                });
            }
        });

        // 3. Sync LCV Button
        this.$app.find('#btn-tcd-sync-lcv').on('click', function () {
            if (typeof frappe !== 'undefined' && frappe.show_alert) {
                frappe.show_alert({
                    message: __('Đang tiến hành đồng bộ sang Landed Cost Voucher...'),
                    indicator: 'green'
                });
            }
        });

        // 4. Case Selection Change
        this.$app.find('#select-active-case').on('change', function () {
            self.currentCaseId = $(this).val();
            self.load_dashboard_data(self.currentCaseId);
        });

        // 5. Case Type Filter (All, Import, Export)
        this.$app.find('#filter-case-type .pill-tab').on('click', function () {
            self.$app.find('#filter-case-type .pill-tab').removeClass('active');
            $(this).addClass('active');
            self.currentCaseType = $(this).data('type');
            self.apply_case_type_filter();
        });

        // 6. Allocation Rule Playground Buttons
        this.$app.find('.btn-rule').on('click', function () {
            self.$app.find('.btn-rule').removeClass('active');
            $(this).addClass('active');
            self.currentRule = $(this).data('rule');
            self.render_allocation_simulation();
        });

        // 7. Search in Cost Sheets Ledger
        this.$app.find('#search-cost-sheets').on('input', function () {
            const query = $(this).val().toLowerCase().trim();
            self.$app.find('#tbody-cost-sheets-ledger tr').each(function () {
                const text = $(this).text().toLowerCase();
                $(this).toggle(text.includes(query));
            });
        });
    }

    apply_case_type_filter() {
        const $importSection = this.$app.find('#section-allocation-engine');
        const $exportSection = this.$app.find('#section-export-tracker');

        if (this.currentCaseType === 'import') {
            $importSection.show();
            $exportSection.hide();
        } else if (this.currentCaseType === 'export') {
            $importSection.hide();
            $exportSection.show();
        } else {
            $importSection.show();
            $exportSection.show();
        }
    }

    load_dashboard_data(caseId, callback) {
        const self = this;
        if (typeof frappe !== 'undefined' && frappe.call) {
            frappe.call({
                method: 'logistics_wizard.costing_engine.api.get_case_cost_summary',
                args: { case_id: caseId },
                callback: function (r) {
                    if (r && r.message) {
                        self.render_dashboard(r.message);
                    } else {
                        self.render_fallback_data(caseId);
                    }
                    if (callback) callback();
                },
                error: function () {
                    self.render_fallback_data(caseId);
                    if (callback) callback();
                }
            });
        } else {
            self.render_fallback_data(caseId);
            if (callback) callback();
        }
    }

    render_fallback_data(caseId) {
        const isExport = caseId.startsWith('EXP');
        const mockData = {
            case_id: caseId,
            case_type: isExport ? 'Export' : 'Import',
            purchase_value: isExport ? 198000.0 : 125000.0,
            estimated_cost: isExport ? 12500.0 : 16800.0,
            actual_cost: isExport ? 14200.0 : 18350.0,
            variance_amount: isExport ? 1700.0 : 1550.0,
            variance_pct: isExport ? 13.6 : 9.23,
            actual_landed_cost: isExport ? 212200.0 : 143350.0,
            invoices_received: 6,
            invoices_total: 6,
            costs_verified: 18350.0,
            costs_allocated: 18350.0,
            cost_finalization_status: 'Fully Allocated',
            items: [
                { item_code: 'STEEL-ROLL-05', item_name: 'Cuộn thép mạ kẽm SGCC 0.5mm', qty: 120, uom: 'Tấn', rate: 550, weight: 120, volume: 60 },
                { item_code: 'STEEL-ROLL-08', item_name: 'Cuộn thép mạ kẽm SGCC 0.8mm', qty: 80, uom: 'Tấn', rate: 580, weight: 80, volume: 40 },
                { item_code: 'STEEL-SPCC-10', item_name: 'Cuộn thép cán nguội SPCC 1.0mm', qty: 50, uom: 'Tấn', rate: 490, weight: 50, volume: 25 }
            ],
            cost_breakdown: [
                { type: 'Freight', supplier: 'Maersk Line A/S', invoice: 'INV-MSK-9921', est: 7500, act: 8200, status: 'Verified' },
                { type: 'Insurance', supplier: 'Bảo Việt Đà Nẵng', invoice: 'BV-DAN-8812', est: 600, act: 600, status: 'Verified' },
                { type: 'Duty', supplier: 'Hải Quan Cảng Tiên Sa', invoice: 'HQTS-2026-44', est: 3800, act: 4000, status: 'Verified' },
                { type: 'Tax', supplier: 'Chi cục Thuế Đà Nẵng', invoice: 'VAT-TS-2026-1', est: 1400, act: 1450, status: 'Verified' },
                { type: 'Port', supplier: 'Cảng Đà Nẵng JSC', invoice: 'PORT-DAD-002', est: 1100, act: 1250, status: 'Verified' },
                { type: 'Handling', supplier: 'Cảng Đà Nẵng JSC', invoice: 'PORT-DAD-003', est: 700, act: 850, status: 'Verified' },
                { type: 'Storage', supplier: 'Kho Ngoại Quan Tiên Sa', invoice: 'KQ-TS-114', est: 400, act: 400, status: 'Verified' },
                { type: 'Demurrage/Detention', supplier: 'Maersk Line A/S', invoice: 'DEM-MSK-019', est: 0, act: 300, status: 'Verified' },
                { type: 'Trucking', supplier: 'Vận Tải Miền Trung', invoice: 'VT-MT-550', est: 800, act: 800, status: 'Verified' },
                { type: 'Broker Fee', supplier: 'Logistics Đại Phát', invoice: 'DP-BROKER-77', est: 500, act: 500, status: 'Verified' },
                { type: 'Other', supplier: 'Chi phí phát sinh khác', invoice: '-', est: 0, act: 0, status: 'Draft' }
            ]
        };

        this.render_dashboard(mockData);
    }

    render_dashboard(data) {
        this.dashboardData = data;

        // 1. KPI Cards
        const fmt = (num) => '$' + (num || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        this.$app.find('#kpi-actual-cost').text(fmt(data.actual_cost));
        this.$app.find('#kpi-estimated-cost').text(fmt(data.estimated_cost));

        const varAmt = data.variance_amount || (data.actual_cost - data.estimated_cost);
        const varPct = data.variance_pct || ((varAmt / (data.estimated_cost || 1)) * 100);
        const sign = varAmt > 0 ? '+' : '';
        this.$app.find('#kpi-variance-badge').text(`${sign}${varPct.toFixed(2)}% (${sign}${fmt(varAmt)})`);
        if (varAmt > 0) {
            this.$app.find('#kpi-variance-badge').removeClass('trend-success').addClass('trend-up');
        } else {
            this.$app.find('#kpi-variance-badge').removeClass('trend-up').addClass('trend-success');
        }

        const surchargeRate = ((data.actual_cost / (data.purchase_value || 1)) * 100).toFixed(2);
        this.$app.find('#kpi-surcharge-rate').text(surchargeRate + '%');
        this.$app.find('#kpi-purchase-value').text(fmt(data.purchase_value));
        this.$app.find('#kpi-invoices-count').text(`${data.invoices_received || 6} / ${data.invoices_total || 6} hóa đơn`);

        // 2. Render 11 Cost Lines
        this.render_cost_breakdown_table(data.cost_breakdown || []);

        // 3. Render Allocation Simulation
        this.render_allocation_simulation();

        // 4. Render Master Ledger
        this.render_master_ledger();

        // 5. Apply filters
        this.apply_case_type_filter();
    }

    render_cost_breakdown_table(items) {
        const $tbody = this.$app.find('#tbody-cost-items');
        $tbody.empty();

        let totalEst = 0;
        let totalAct = 0;

        items.forEach((item, idx) => {
            totalEst += item.est;
            totalAct += item.act;
            const diff = item.act - item.est;
            const diffPct = item.est > 0 ? ((diff / item.est) * 100).toFixed(1) : (item.act > 0 ? '100.0' : '0.0');
            const diffClass = diff > 0 ? 'text-danger' : (diff < 0 ? 'text-success' : 'text-muted');
            const sign = diff > 0 ? '+' : '';

            const row = `
                <tr>
                    <td>${idx + 1}</td>
                    <td><strong>${frappe.utils.escape_html(item.type)}</strong></td>
                    <td>${frappe.utils.escape_html(item.supplier || '-')}</td>
                    <td><code>${frappe.utils.escape_html(item.invoice || '-')}</code></td>
                    <td class="text-right">$${item.est.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td class="text-right font-weight-bold">$${item.act.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td class="text-right ${diffClass}">${sign}$${diff.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td class="text-center ${diffClass}">${sign}${diffPct}%</td>
                    <td class="text-center"><span class="badge-pill-success">${frappe.utils.escape_html(item.status)}</span></td>
                </tr>
            `;
            $tbody.append(row);
        });

        const totalDiff = totalAct - totalEst;
        const totalDiffPct = totalEst > 0 ? ((totalDiff / totalEst) * 100).toFixed(2) : '0.00';
        this.$app.find('#foot-estimated-total').text('$' + totalEst.toLocaleString('en-US', { minimumFractionDigits: 2 }));
        this.$app.find('#foot-actual-total').text('$' + totalAct.toLocaleString('en-US', { minimumFractionDigits: 2 }));
        this.$app.find('#foot-variance-total').text((totalDiff > 0 ? '+' : '') + '$' + totalDiff.toLocaleString('en-US', { minimumFractionDigits: 2 }));
        this.$app.find('#foot-variance-pct').text((totalDiff > 0 ? '+' : '') + totalDiffPct + '%');
    }

    render_allocation_simulation() {
        const $tbody = this.$app.find('#tbody-allocation-items');
        $tbody.empty();

        const items = (this.dashboardData && this.dashboardData.items) || [
            { item_code: 'STEEL-ROLL-05', item_name: 'Cuộn thép mạ kẽm SGCC 0.5mm', qty: 120, uom: 'Tấn', rate: 550, weight: 120, volume: 60 },
            { item_code: 'STEEL-ROLL-08', item_name: 'Cuộn thép mạ kẽm SGCC 0.8mm', qty: 80, uom: 'Tấn', rate: 580, weight: 80, volume: 40 },
            { item_code: 'STEEL-SPCC-10', item_name: 'Cuộn thép cán nguội SPCC 1.0mm', qty: 50, uom: 'Tấn', rate: 490, weight: 50, volume: 25 }
        ];

        const totalCostToAllocate = (this.dashboardData && this.dashboardData.actual_cost) || 18350.0;

        // Calculate divisor based on rule
        let totalBasis = 0;
        items.forEach(it => {
            if (this.currentRule === 'value') totalBasis += (it.qty * it.rate);
            else if (this.currentRule === 'qty') totalBasis += it.qty;
            else if (this.currentRule === 'volume') totalBasis += it.volume;
            else totalBasis += it.weight; // default weight
        });

        items.forEach(it => {
            let basis = it.weight;
            if (this.currentRule === 'value') basis = it.qty * it.rate;
            else if (this.currentRule === 'qty') basis = it.qty;
            else if (this.currentRule === 'volume') basis = it.volume;

            const ratio = totalBasis > 0 ? (basis / totalBasis) : (1 / items.length);
            const allocatedCost = totalCostToAllocate * ratio;
            const costPerUnit = allocatedCost / (it.qty || 1);
            const finalUnitLandedCost = it.rate + costPerUnit;

            const row = `
                <tr>
                    <td><code>${frappe.utils.escape_html(it.item_code)}</code></td>
                    <td><strong>${frappe.utils.escape_html(it.item_name)}</strong></td>
                    <td class="text-right">${it.qty}</td>
                    <td class="text-right">${it.uom}</td>
                    <td class="text-right">${(ratio * 100).toFixed(2)}%</td>
                    <td class="text-right">$${it.rate.toFixed(2)}</td>
                    <td class="text-right text-primary font-weight-bold">$${allocatedCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td class="text-right text-success font-weight-bold">$${finalUnitLandedCost.toFixed(2)}</td>
                    <td class="text-right text-danger">+$${costPerUnit.toFixed(2)}</td>
                </tr>
            `;
            $tbody.append(row);
        });
    }

    render_master_ledger() {
        const $tbody = this.$app.find('#tbody-cost-sheets-ledger');
        $tbody.empty();

        const costSheets = [
            { name: 'TCS-IMP-2026-001', case_id: 'IMP-2026-001', type: 'Nhập khẩu', incoterm: 'FOB', value: 125000, est: 16800, act: 18350, var: 1550, lcv: 'Đã Đồng Bộ (LCV-2026-0004)' },
            { name: 'TCS-EXP-2026-002', case_id: 'EXP-2026-002', type: 'Xuất khẩu', incoterm: 'CIF', value: 198000, est: 12500, act: 14200, var: 1700, lcv: 'Không Áp Dụng (Export)' },
            { name: 'TCS-IMP-2026-003', case_id: 'IMP-2026-003', type: 'Nhập khẩu', incoterm: 'EXW', value: 89000, est: 9500, act: 9400, var: -100, lcv: 'Đã Phê Duyệt' }
        ];

        costSheets.forEach(cs => {
            const varClass = cs.var > 0 ? 'text-danger' : (cs.var < 0 ? 'text-success' : 'text-muted');
            const sign = cs.var > 0 ? '+' : '';
            const row = `
                <tr>
                    <td><code><a href="/app/trade-cost-sheet/${cs.name}" class="tcd-action-link">${cs.name}</a></code></td>
                    <td><strong><a href="/app/trade-case/${cs.case_id}" class="tcd-action-link">${cs.case_id}</a></strong></td>
                    <td>${cs.type}</td>
                    <td><span class="badge-pill-warning">${cs.incoterm}</span></td>
                    <td class="text-right">$${cs.value.toLocaleString('en-US')}</td>
                    <td class="text-right">$${cs.est.toLocaleString('en-US')}</td>
                    <td class="text-right font-weight-bold">$${cs.act.toLocaleString('en-US')}</td>
                    <td class="text-right ${varClass}">${sign}$${cs.var.toLocaleString('en-US')}</td>
                    <td class="text-center"><span class="badge-status-green">${cs.lcv}</span></td>
                    <td class="text-center">
                        <a href="/app/trade-cost-sheet/${cs.name}" class="tcd-action-link">Chi tiết &rarr;</a>
                    </td>
                </tr>
            `;
            $tbody.append(row);
        });
    }

    refresh() {
        this.load_dashboard_data(this.currentCaseId);
    }
}

if (typeof window !== 'undefined') {
    window.TradeCostDashboardController = TradeCostDashboardController;
}
