// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * RAG Admin Center Controller
 * Phân hệ Quản trị RAG Riêng Biệt với Thanh Điều Hướng Sidebar 2 Tab:
 * 1. Dashboard (Tổng quan hiệu năng RAG)
 * 2. Quản trị tri thức (Knowledge Management Hub chuẩn Dify)
 */

class RagAdminCenterController {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.$root = $(wrapper).find('#rag-admin-root');
        if (!this.$root.length) {
            this.$root = $(wrapper);
        }

        this.state = {
            currentNavTab: 'dashboard', // 'dashboard' | 'knowledge'
            timeRange: '7d',
            domain: 'all',
            activeKnowledgeFilterTab: 'all',
            searchKeyword: '',
            filterIndexStatus: 'all',
            filterRetrieval: 'all',
            filterLegalValidity: 'all',
            selectedDocId: 'doc-tt85',
            activeDrawerTab: 'chunks',
            wizardStep: 1,
            timeSeriesPeriod: 'day'
        };

        this.init_mock_data();
        this.bind_events();
        this.switch_nav_tab('dashboard');
        this.render_all();
    }

    init_mock_data() {
        // 1. Kho Dữ liệu Tri thức (Knowledge Documents)
        this.documents = [
            {
                id: 'doc-tt85',
                title: 'Thông tư 85/2026/TT-BTC',
                sub_title: 'Sửa đổi, bổ sung Thông tư 14/2015/TT-BTC về phân loại hàng hóa & máy móc tháo rời',
                type: 'legal',
                agency: 'Bộ Tài chính',
                version: '2026',
                release_date: '15/08/2026',
                effective_date: '12/10/2026',
                legal_validity: 'valid',
                legal_validity_label: 'Còn hiệu lực',
                index_status: 'ready',
                chunks_count: 142,
                retrieval_active: true,
                priority: 'P0',
                chunks: [
                    {
                        id: 'TT85-A8-1',
                        path: 'Điều 8 > Khoản 1 > Điểm a',
                        tokens: 245,
                        priority: 'P0',
                        text: 'Hàng hóa là máy móc, thiết bị ở dạng chưa lắp ráp hoặc tháo rời được phân loại theo quy tắc GIR 2(a) của Danh mục hàng hóa xuất khẩu, nhập khẩu Việt Nam. Người khai hải quan phải lập phiếu theo dõi trừ lùi linh kiện đồng bộ tại Chi cục Hải quan nơi làm thủ tục.',
                        meta: { article: 8, clause: 1, point: 'a', topic: 'unassembled_machine', gir_reference: '2a' }
                    },
                    {
                        id: 'TT85-A8-2',
                        path: 'Điều 8 > Khoản 2 (Hồ sơ chứng minh xuất xứ)',
                        tokens: 310,
                        priority: 'P1',
                        text: 'Trường hợp máy móc thiết bị nhập khẩu từ nhiều nguồn hoặc nhiều chuyến, doanh nghiệp phải nộp kèm sơ đồ thiết kế kỹ thuật, danh mục các tổ hợp linh kiện và văn bản cam kết tính đồng bộ của dây chuyền chế tạo.',
                        meta: { article: 8, clause: 2, point: null, topic: 'machine_dossier', gir_reference: '2a' }
                    },
                    {
                        id: 'TT85-A9-1',
                        path: 'Điều 9 > Khoản 1 (Xác định mã số tổ hợp thiết bị)',
                        tokens: 180,
                        priority: 'P0',
                        text: 'Tổ hợp thiết bị gồm nhiều máy móc liên kết để thực hiện một chức năng chung được xác định theo Chú giải 4 hoặc Chú giải 5 Phần XVI của Danh mục hàng hóa xuất nhập khẩu Việt Nam.',
                        meta: { article: 9, clause: 1, point: null, topic: 'composite_machine', gir_reference: 'GIR 1 & Note 4/XVI' }
                    }
                ],
                logs: [
                    { time: '2026-10-12 09:15:20', level: 'INFO', msg: 'Khởi chạy Bóc tách cấu trúc pháp quy Điều/Khoản thành công.' },
                    { time: '2026-10-12 09:15:45', level: 'INFO', msg: 'Tạo 142 vector embeddings BGE-M3 (1024-dim) và nạp bảng BM25.' },
                    { time: '2026-10-12 09:16:00', level: 'SUCCESS', msg: 'Tài liệu đã sẵn sàng cho pipeline truy xuất RAG.' }
                ]
            },
            {
                id: 'doc-tt31',
                title: 'Thông tư 31/2022/TT-BTC',
                sub_title: 'Ban hành Danh mục hàng hóa xuất khẩu, nhập khẩu Việt Nam (AHTN 2022)',
                type: 'legal',
                agency: 'Bộ Tài chính',
                version: '2022',
                release_date: '08/06/2022',
                effective_date: '30/12/2022',
                legal_validity: 'valid',
                legal_validity_label: 'Còn hiệu lực',
                index_status: 'ready',
                chunks_count: 1420,
                retrieval_active: true,
                priority: 'P0',
                chunks: [
                    {
                        id: 'TT31-GIR-1',
                        path: 'Quy tắc 1 (GIR 1)',
                        tokens: 195,
                        priority: 'P0',
                        text: 'Tên của các Phần, Chương hoặc Phân chương đưa ra chỉ nhằm mục đích tra cứu thuận tiện. Về mặt pháp lý, việc phân loại hàng hóa phải được xác định theo nội dung của từng nhóm và chú giải của các Phần, Chương liên quan.',
                        meta: { rule: 'GIR 1', section: 'ALL' }
                    }
                ],
                logs: [
                    { time: '2026-09-01 10:00:00', level: 'INFO', msg: 'Đã hoàn tất index toàn bộ 6 Quy tắc GIR và Danh mục AHTN.' }
                ]
            },
            {
                id: 'doc-hs-sec16',
                title: 'Danh mục HS - Phần XVI (Máy móc, Thiết bị điện)',
                sub_title: 'Chương 84 (Nồi hơi, máy cơ khí) & Chương 85 (Máy điện, máy ghi hình)',
                type: 'hs',
                agency: 'WCO / Tổng cục Hải quan',
                version: 'WCO 2022',
                release_date: '01/01/2022',
                effective_date: '01/01/2022',
                legal_validity: 'valid',
                legal_validity_label: 'Còn hiệu lực',
                index_status: 'ready',
                chunks_count: 8250,
                retrieval_active: true,
                priority: 'P0',
                chunks: [
                    {
                        id: 'XVI-84-8471-847190',
                        path: 'Phần XVI > Chương 84 > Nhóm 8471 > Phân nhóm 8471.90',
                        tokens: 280,
                        priority: 'P0',
                        text: 'Máy xử lý dữ liệu tự động và các khối chức năng của chúng; đầu đọc từ tính hoặc quang học, máy truyền số liệu lên các phương tiện mang số liệu dưới dạng mã hóa.',
                        meta: { section: 'XVI', chapter: '84', heading: '8471', subheading: '8471.90' }
                    }
                ],
                logs: [
                    { time: '2026-10-10 14:00:00', level: 'INFO', msg: 'Nạp thành công 8.250 records cây phân cấp nhóm 84 và 85.' }
                ]
            },
            {
                id: 'doc-tt14',
                title: 'Thông tư 14/2015/TT-BTC',
                sub_title: 'Hướng dẫn về phân loại hàng hóa, phân tích kiểm định hải quan',
                type: 'legal',
                agency: 'Bộ Tài chính',
                version: '2015',
                release_date: '30/01/2015',
                effective_date: '16/03/2015',
                legal_validity: 'partially_expired',
                legal_validity_label: 'Hết hiệu lực một phần',
                index_status: 'ready',
                chunks_count: 98,
                retrieval_active: true,
                priority: 'P1',
                chunks: [
                    {
                        id: 'TT14-A4-1',
                        path: 'Điều 4 > Khoản 1 (Nguyên tắc phân loại)',
                        tokens: 150,
                        priority: 'P1',
                        text: 'Khi phân loại một mặt hàng cần căn cứ vào tài liệu kỹ thuật, thành phần cấu tạo, tính chất lý hóa, công dụng và tài liệu thực tế của lô hàng.',
                        meta: { article: 4, clause: 1 }
                    }
                ],
                logs: [
                    { time: '2026-08-10 08:30:00', level: 'WARNING', msg: 'Điều 8, 9 đã được thay thế bởi Thông tư 85/2026/TT-BTC. Đã cập nhật cờ đối chiếu lịch sử.' }
                ]
            },
            {
                id: 'doc-hs-sec17',
                title: 'Danh mục HS - Phần XVII (Phương tiện vận tải)',
                sub_title: 'Chương 86 (Đầu máy xe lửa), 87 (Xe cộ), 88 (Khí cụ bay), 89 (Tàu thuyền)',
                type: 'hs',
                agency: 'Ban Thư ký ASEAN',
                version: 'AHTN 2022',
                release_date: '01/01/2022',
                effective_date: '01/01/2022',
                legal_validity: 'valid',
                legal_validity_label: 'Còn hiệu lực',
                index_status: 'ready',
                chunks_count: 4310,
                retrieval_active: true,
                priority: 'P0',
                chunks: [
                    {
                        id: 'XVII-87-8703',
                        path: 'Phần XVII > Chương 87 > Nhóm 8703',
                        tokens: 320,
                        priority: 'P0',
                        text: 'Ô tô và các loại xe có động cơ khác được thiết kế chủ yếu để chở người (trừ các loại xe thuộc nhóm 87.02), kể cả xe chở người có khoang hành lý chung (station wagons) và xe đua.',
                        meta: { section: 'XVII', chapter: '87', heading: '8703' }
                    }
                ],
                logs: [
                    { time: '2026-09-18 11:20:00', level: 'INFO', msg: 'Đã hoàn thành Index 4.310 Chunks Chương 86-89.' }
                ]
            },
            {
                id: 'doc-nd08',
                title: 'Nghị định 08/2015/NĐ-CP & Sửa đổi 59/2018',
                sub_title: 'Quy định chi tiết thi hành Luật Hải quan về thủ tục hải quan, kiểm tra giám sát',
                type: 'legal',
                agency: 'Chính phủ',
                version: '2018',
                release_date: '20/04/2018',
                effective_date: '05/06/2018',
                legal_validity: 'valid',
                legal_validity_label: 'Còn hiệu lực',
                index_status: 'processing',
                chunks_count: 0,
                retrieval_active: false,
                priority: 'P1',
                chunks: [],
                logs: [
                    { time: '2026-10-18 13:40:00', level: 'INFO', msg: 'Đang chạy Worker phân tách 112 Điều khoản... Tiến độ 65%.' }
                ]
            },
            {
                id: 'doc-hs-optics',
                title: 'Danh mục Linh kiện Bán dẫn Quang học Mới 2026',
                sub_title: 'Bổ sung hướng dẫn phân loại Module cảm biến thông minh & Chip LiDAR',
                type: 'hs',
                agency: 'Tổng cục Hải quan',
                version: '2026 Draft',
                release_date: '09/10/2026',
                effective_date: 'Chưa xác định',
                legal_validity: 'draft',
                legal_validity_label: 'Dự thảo',
                index_status: 'error',
                chunks_count: 0,
                retrieval_active: false,
                priority: 'P2',
                chunks: [],
                logs: [
                    { time: '2026-10-18 12:10:00', level: 'ERROR', msg: 'Lỗi bóc tách tệp PDF tại Trang 14: Bảng mã HS không hợp lệ (Missing Unicode Table Tag).' },
                    { time: '2026-10-18 12:10:02', level: 'ERROR', msg: 'Index Worker ngắt tiến trình để bảo vệ tính toàn vẹn dữ liệu.' }
                ]
            },
            {
                id: 'doc-qd-old',
                title: 'Quyết định 18/2019/QĐ-TTg (Quy định nhập khẩu máy móc cũ)',
                sub_title: 'Tiêu chí xác định tuổi thiết bị không quá 10 năm và tiêu chuẩn an toàn',
                type: 'legal',
                agency: 'Thủ tướng Chính phủ',
                version: '2019',
                release_date: '19/04/2019',
                effective_date: '15/06/2019',
                legal_validity: 'expired',
                legal_validity_label: 'Hết hiệu lực toàn bộ',
                index_status: 'ready',
                chunks_count: 32,
                retrieval_active: false,
                priority: 'P2',
                chunks: [
                    {
                        id: 'QD18-A6-1',
                        path: 'Điều 6 > Khoản 1',
                        tokens: 120,
                        priority: 'P2',
                        text: 'Tuổi thiết bị nhập khẩu không được vượt quá 10 năm tính từ năm sản xuất đến năm nhập khẩu.',
                        meta: { article: 6, clause: 1 }
                    }
                ],
                logs: [
                    { time: '2026-05-01 00:00:00', level: 'INFO', msg: 'Văn bản đã hết hiệu lực. Admin đã tạm tắt quyền truy xuất khỏi RAG.' }
                ]
            }
        ];

        // 2. Chuỗi thời gian (Timeseries Data)
        this.timeSeriesData = {
            day: {
                labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
                hs: [95, 130, 165, 140, 210, 185, 120],
                legal: [80, 110, 135, 125, 175, 140, 95]
            },
            week: {
                labels: ['Tuần 38', 'Tuần 39', 'Tuần 40', 'Tuần 41'],
                hs: [840, 950, 1120, 1280],
                legal: [650, 780, 890, 1040]
            },
            month: {
                labels: ['Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10'],
                hs: [3400, 3900, 4300, 4850],
                legal: [2800, 3100, 3500, 4100]
            }
        };
    }

    bind_events() {
        const self = this;

        // 1. Sidebar Nav Tab Switching (Dashboard vs Quản trị tri thức)
        this.$root.on('click', '.logistics-nav-tab', function (e) {
            e.preventDefault();
            const targetTab = $(this).data('tab');
            if (targetTab) {
                self.switch_nav_tab(targetTab);
            }
        });

        // 2. Topbar Filters
        this.$root.on('change', '#rag-filter-time-range', function () {
            self.state.timeRange = $(this).val();
            self.update_kpi_metrics();
            self.show_toast(`Đã áp dụng bộ lọc: ${$(this).find('option:selected').text()}`);
        });

        this.$root.on('change', '#rag-filter-domain', function () {
            self.state.domain = $(this).val();
            self.update_kpi_metrics();
            self.show_toast(`Đã lọc phạm vi: ${$(this).find('option:selected').text()}`);
        });

        // 3. TimeSeries Period Switch (Day/Week/Month)
        this.$root.on('click', '.rag-chart-btn', function () {
            self.$root.find('.rag-chart-btn').removeClass('active');
            $(this).addClass('active');
            self.state.timeSeriesPeriod = $(this).data('period');
            self.render_timeseries_chart();
        });

        // 4. Knowledge Management Filter Tabs
        this.$root.on('click', '.rag-tab-btn', function () {
            self.$root.find('.rag-tab-btn').removeClass('active');
            $(this).addClass('active');
            self.state.activeKnowledgeFilterTab = $(this).data('tab-type');
            self.render_documents_table();
        });

        // 5. Search Input (Debounce)
        let searchTimer;
        this.$root.on('input', '#rag-doc-search', function () {
            clearTimeout(searchTimer);
            const val = $(this).val();
            searchTimer = setTimeout(() => {
                self.state.searchKeyword = val.trim().toLowerCase();
                self.render_documents_table();
            }, 250);
        });

        // 6. Dropdown Filters
        this.$root.on('change', '#rag-filter-index-status', function () {
            self.state.filterIndexStatus = $(this).val();
            self.render_documents_table();
        });

        this.$root.on('change', '#rag-filter-retrieval', function () {
            self.state.filterRetrieval = $(this).val();
            self.render_documents_table();
        });

        this.$root.on('change', '#rag-filter-legal-validity', function () {
            self.state.filterLegalValidity = $(this).val();
            self.render_documents_table();
        });

        // 7. Toggle Retrieval Switch
        this.$root.on('change', '.rag-doc-retrieval-switch', function (e) {
            e.stopPropagation();
            const docId = $(this).data('doc-id');
            const isChecked = $(this).is(':checked');
            self.toggle_document_retrieval(docId, isChecked);
        });

        // 8. Document Row Click -> Open Drawer
        this.$root.on('click', '.rag-clickable-row', function (e) {
            if ($(e.target).closest('.rag-toggle-switch, .rag-row-action-btn, input[type="checkbox"]').length) {
                return;
            }
            const docId = $(this).data('doc-id');
            self.open_drawer(docId);
        });

        // 9. Drawer Controls
        this.$root.on('click', '#btn-close-drawer, #btn-drawer-close-bottom, #rag-drawer-backdrop', function () {
            self.close_drawer();
        });

        this.$root.on('click', '.rag-drawer-tab-btn', function () {
            self.$root.find('.rag-drawer-tab-btn').removeClass('active');
            $(this).addClass('active');
            self.state.activeDrawerTab = $(this).data('drawer-tab');
            self.render_drawer_body();
        });

        this.$root.on('click', '#btn-drawer-reindex', function () {
            self.reindex_document(self.state.selectedDocId);
        });

        // 10. Modal Wizard Controls
        this.$root.on('click', '#btn-open-add-modal', function () {
            self.open_wizard_modal();
        });

        this.$root.on('click', '#btn-close-modal-wizard', function () {
            self.close_wizard_modal();
        });

        this.$root.on('click', '#btn-wizard-next', function () {
            self.wizard_next();
        });

        this.$root.on('click', '#btn-wizard-prev', function () {
            self.wizard_prev();
        });

        this.$root.on('change', 'input[name="wizard_doc_type"]', function () {
            const docType = $(this).val();
            if (docType === 'legal') {
                self.$root.find('#form-legal-fields').show();
                self.$root.find('#form-hs-fields').hide();
            } else {
                self.$root.find('#form-legal-fields').hide();
                self.$root.find('#form-hs-fields').show();
            }
        });

        this.$root.on('click', '#btn-browse-file', function (e) {
            e.preventDefault();
            self.$root.find('#wizard-file-input').click();
        });

        this.$root.on('change', '#wizard-file-input', function (e) {
            const file = e.target.files[0];
            if (file) {
                self.$root.find('#wizard-selected-file-info').show();
                self.$root.find('#wizard-filename').text(file.name);
                self.$root.find('#wizard-filesize').text(`${(file.size / (1024 * 1024)).toFixed(2)} MB`);
            }
        });
    }

    switch_nav_tab(tabName) {
        tabName = tabName || 'dashboard';
        this.state.currentNavTab = tabName;

        // 1. Update active tab button in sidebar
        this.$root.find('.logistics-nav-tab').removeClass('active');
        this.$root.find(`#btn-tab-${tabName}`).addClass('active');

        // 2. Hide all panes, show target pane with explicit style override
        this.$root.find('.logistics-tab-pane').removeClass('active').css({ 'display': 'none', 'opacity': '0' });
        const $targetPane = this.$root.find(`#tab-pane-${tabName}`);
        $targetPane.addClass('active').css({ 'display': 'block', 'opacity': '1', 'visibility': 'visible' });

        // 3. Re-render charts if switching to dashboard (to ensure SVG dimensions are precise)
        if (tabName === 'dashboard') {
            setTimeout(() => this.render_charts(), 50);
        } else if (tabName === 'knowledge') {
            this.render_documents_table();
        }
    }

    render_all() {
        this.render_charts();
        this.render_documents_table();
    }

    update_kpi_metrics() {
        const factor = this.state.timeRange === '24h' ? 0.15 : (this.state.timeRange === '30d' ? 3.8 : 1.0);
        const domainMult = this.state.domain === 'hs' ? 0.58 : (this.state.domain === 'legal' ? 0.42 : 1.0);
        
        const total = Math.round(12450 * factor * domainMult);
        const completed = Math.round(total * 0.949);
        const missing = Math.round(total * 0.034);
        const error = total - completed - missing;

        this.$root.find('#kpi-total-queries').text(total.toLocaleString('vi-VN'));
        this.$root.find('#kpi-completed-queries').text(completed.toLocaleString('vi-VN'));
        this.$root.find('#kpi-missing-queries').text(missing.toLocaleString('vi-VN'));
        this.$root.find('#kpi-error-queries').text(error.toLocaleString('vi-VN'));
        this.$root.find('#donut-center-total').text(total.toLocaleString('vi-VN'));

        this.render_charts();
    }

    render_charts() {
        this.render_timeseries_chart();
        this.render_donut_chart();
    }

    render_timeseries_chart() {
        const $container = this.$root.find('#rag-chart-timeseries-container');
        if (!$container.length) return;
        $container.empty();

        const data = this.timeSeriesData[this.state.timeSeriesPeriod];
        const labels = data.labels;
        const hsData = data.hs;
        const legalData = data.legal;

        const width = $container.width() || 680;
        const height = 240;
        const padding = { top: 20, right: 30, bottom: 35, left: 45 };

        const graphW = width - padding.left - padding.right;
        const graphH = height - padding.top - padding.bottom;

        const maxVal = Math.max(...hsData, ...legalData) * 1.15;

        const getX = (i) => padding.left + (i / (labels.length - 1)) * graphW;
        const getY = (val) => padding.top + graphH - (val / maxVal) * graphH;

        let pathHs = `M ${getX(0)} ${getY(hsData[0])}`;
        let areaHs = `M ${getX(0)} ${getY(hsData[0])}`;
        let pathLegal = `M ${getX(0)} ${getY(legalData[0])}`;
        let areaLegal = `M ${getX(0)} ${getY(legalData[0])}`;

        for (let i = 1; i < labels.length; i++) {
            pathHs += ` L ${getX(i)} ${getY(hsData[i])}`;
            areaHs += ` L ${getX(i)} ${getY(hsData[i])}`;
            pathLegal += ` L ${getX(i)} ${getY(legalData[i])}`;
            areaLegal += ` L ${getX(i)} ${getY(legalData[i])}`;
        }

        areaHs += ` L ${getX(labels.length - 1)} ${padding.top + graphH} L ${getX(0)} ${padding.top + graphH} Z`;
        areaLegal += ` L ${getX(labels.length - 1)} ${padding.top + graphH} L ${getX(0)} ${padding.top + graphH} Z`;

        let svgHtml = `
            <svg class="rag-chart-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
                <!-- Grid Lines -->
                <line x1="${padding.left}" y1="${getY(0)}" x2="${width - padding.right}" y2="${getY(0)}" stroke="#e2e8f0" stroke-width="1" />
                <line x1="${padding.left}" y1="${getY(maxVal * 0.5)}" x2="${width - padding.right}" y2="${getY(maxVal * 0.5)}" stroke="#f1f5f9" stroke-width="1" stroke-dasharray="4" />
                <line x1="${padding.left}" y1="${getY(maxVal)}" x2="${width - padding.right}" y2="${getY(maxVal)}" stroke="#f1f5f9" stroke-width="1" stroke-dasharray="4" />

                <!-- Areas -->
                <path d="${areaHs}" class="rag-chart-area-hs" />
                <path d="${areaLegal}" class="rag-chart-area-legal" />

                <!-- Lines -->
                <path d="${pathHs}" class="rag-chart-line-hs" />
                <path d="${pathLegal}" class="rag-chart-line-legal" />
        `;

        for (let i = 0; i < labels.length; i++) {
            const x = getX(i);
            const yHs = getY(hsData[i]);
            const yLegal = getY(legalData[i]);

            svgHtml += `
                <!-- X Label -->
                <text x="${x}" y="${height - 10}" font-size="11" font-weight="600" fill="#64748b" text-anchor="middle">${labels[i]}</text>
                
                <!-- HS Dot -->
                <circle cx="${x}" cy="${yHs}" r="4" fill="#2563eb" stroke="#ffffff" stroke-width="2" class="rag-chart-dot">
                    <title>Mã HS (${labels[i]}): ${hsData[i]} lượt</title>
                </circle>

                <!-- Legal Dot -->
                <circle cx="${x}" cy="${yLegal}" r="4" fill="#0d9488" stroke="#ffffff" stroke-width="2" class="rag-chart-dot">
                    <title>Pháp Luật (${labels[i]}): ${legalData[i]} lượt</title>
                </circle>
            `;
        }

        svgHtml += `</svg>`;
        $container.html(svgHtml);
    }

    render_donut_chart() {
        const $container = this.$root.find('#rag-chart-donut-container');
        if (!$container.length) return;

        const size = 180;
        const strokeW = 20;
        const radius = (size - strokeW) / 2;
        const circumference = 2 * Math.PI * radius;

        const compLen = circumference * 0.949;
        const missLen = circumference * 0.034;
        const errLen = circumference * 0.017;

        const offsetComp = 0;
        const offsetMiss = -compLen;
        const offsetErr = -(compLen + missLen);

        let svgHtml = `
            <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
                <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="#f1f5f9" stroke-width="${strokeW}" />
                
                <!-- Completed (Emerald) -->
                <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="#10b981" stroke-width="${strokeW}"
                    stroke-dasharray="${compLen} ${circumference - compLen}" stroke-dashoffset="${offsetComp}" 
                    transform="rotate(-90 ${size/2} ${size/2})" />
                
                <!-- Missing (Amber) -->
                <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="#f59e0b" stroke-width="${strokeW}"
                    stroke-dasharray="${missLen} ${circumference - missLen}" stroke-dashoffset="${offsetMiss}" 
                    transform="rotate(-90 ${size/2} ${size/2})" />

                <!-- Error (Red) -->
                <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="#ef4444" stroke-width="${strokeW}"
                    stroke-dasharray="${errLen} ${circumference - errLen}" stroke-dashoffset="${offsetErr}" 
                    transform="rotate(-90 ${size/2} ${size/2})" />
            </svg>
        `;

        $container.find('svg').remove();
        $container.prepend(svgHtml);
    }

    render_documents_table() {
        const $tbody = this.$root.find('#rag-docs-tbody');
        if (!$tbody.length) return;
        $tbody.empty();

        let filtered = this.documents.filter(doc => {
            // Filter Tab
            if (this.state.activeKnowledgeFilterTab !== 'all' && doc.type !== this.state.activeKnowledgeFilterTab) {
                return false;
            }
            // Filter Search
            if (this.state.searchKeyword) {
                const combined = (doc.title + ' ' + doc.sub_title + ' ' + doc.agency).toLowerCase();
                if (!combined.includes(this.state.searchKeyword)) {
                    return false;
                }
            }
            // Filter Index Status
            if (this.state.filterIndexStatus !== 'all' && doc.index_status !== this.state.filterIndexStatus) {
                return false;
            }
            // Filter Retrieval
            if (this.state.filterRetrieval === 'active' && !doc.retrieval_active) return false;
            if (this.state.filterRetrieval === 'muted' && doc.retrieval_active) return false;

            // Filter Legal Validity
            if (this.state.filterLegalValidity !== 'all' && doc.legal_validity !== this.state.filterLegalValidity) {
                return false;
            }

            return true;
        });

        this.$root.find('#pagination-start').text(filtered.length > 0 ? 1 : 0);
        this.$root.find('#pagination-end').text(filtered.length);
        this.$root.find('#pagination-total').text(this.documents.length);

        if (filtered.length === 0) {
            $tbody.html(`
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #64748b;">
                        <i class="fa fa-folder-open-o" style="font-size: 32px; margin-bottom: 8px;"></i>
                        <div>Không tìm thấy tài liệu nào phù hợp với bộ lọc hiện tại.</div>
                    </td>
                </tr>
            `);
            return;
        }

        filtered.forEach(doc => {
            // Type badge
            const typeBadge = doc.type === 'legal'
                ? '<span class="rag-badge rag-badge-legal"><i class="fa fa-balance-scale"></i> Legal</span>'
                : '<span class="rag-badge rag-badge-hs"><i class="fa fa-barcode"></i> HS Code</span>';

            // Legal validity badge
            let validityBadge = '';
            if (doc.legal_validity === 'valid') {
                validityBadge = '<span class="rag-badge rag-badge-success">● Còn hiệu lực</span>';
            } else if (doc.legal_validity === 'partially_expired') {
                validityBadge = '<span class="rag-badge rag-badge-warning" title="Một số điều khoản đã bị thay thế">▲ Hết HL 1 phần</span>';
            } else if (doc.legal_validity === 'expired') {
                validityBadge = '<span class="rag-badge rag-badge-danger">■ Hết hiệu lực</span>';
            } else {
                validityBadge = '<span class="rag-badge rag-badge-neutral">○ Dự thảo</span>';
            }

            // Index status badge
            let indexBadge = '';
            if (doc.index_status === 'ready') {
                indexBadge = '<span class="rag-badge rag-badge-success"><i class="fa fa-check"></i> Sẵn sàng</span>';
            } else if (doc.index_status === 'processing') {
                indexBadge = '<span class="rag-badge rag-badge-warning"><i class="fa fa-circle-o-notch fa-spin"></i> Đang bóc tách</span>';
            } else {
                indexBadge = `<span class="rag-badge rag-badge-danger" title="Lỗi bóc tách PDF"><i class="fa fa-times"></i> Lỗi Index</span>`;
            }

            // Chunks display
            const chunksText = doc.chunks_count > 0 
                ? `<strong style="color: #0f172a;">${doc.chunks_count.toLocaleString('vi-VN')}</strong> <span style="font-size: 11px; color: #64748b;">chunks</span>`
                : `<span style="color: #94a3b8;">0 chunks</span>`;

            // Toggle switch
            const isChecked = doc.retrieval_active ? 'checked' : '';
            const toggleHtml = `
                <label class="rag-toggle-switch" title="${doc.retrieval_active ? 'Đang bật truy xuất' : 'Tạm tắt truy xuất'}">
                    <input type="checkbox" class="rag-doc-retrieval-switch" data-doc-id="${doc.id}" ${isChecked}>
                    <span class="rag-toggle-slider"></span>
                </label>
            `;

            const tr = `
                <tr class="rag-clickable-row" data-doc-id="${doc.id}">
                    <td><input type="checkbox" onclick="event.stopPropagation();"></td>
                    <td>
                        <div class="rag-doc-title">${doc.title}</div>
                        <div class="rag-doc-meta">${doc.agency} · ${doc.release_date} · ${doc.sub_title}</div>
                    </td>
                    <td>${typeBadge}</td>
                    <td>${validityBadge}</td>
                    <td>${indexBadge}</td>
                    <td>${chunksText}</td>
                    <td style="text-align: center;">${toggleHtml}</td>
                    <td style="text-align: right;">
                        <button class="rag-row-action-btn" title="Xem chi tiết" onclick="event.stopPropagation(); frappe.pages['rag-admin-center'].controller.open_drawer('${doc.id}');">
                            <i class="fa fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
            $tbody.append(tr);
        });
    }

    toggle_document_retrieval(docId, isChecked) {
        const doc = this.documents.find(d => d.id === docId);
        if (doc) {
            doc.retrieval_active = isChecked;
            if (isChecked) {
                this.show_toast(`Đã BẬT truy xuất cho tài liệu: ${doc.title}. Chunks đã tham gia vào Vector/BM25 Index.`);
            } else {
                this.show_toast(`Đã TẠM NGẮT truy xuất cho tài liệu: ${doc.title}. Các Chunks được gắn cờ is_active: false.`);
            }
            this.render_documents_table();
        }
    }

    open_drawer(docId) {
        const doc = this.documents.find(d => d.id === docId);
        if (!doc) return;

        this.state.selectedDocId = docId;
        this.$root.find('#drawer-doc-title').text(doc.title);
        this.$root.find('#drawer-doc-agency').text(doc.agency);
        this.$root.find('#drawer-doc-date').text(`Ban hành: ${doc.release_date}`);
        this.$root.find('#drawer-chunks-count').text(doc.chunks_count);

        const $typeBadge = this.$root.find('#drawer-doc-type-badge');
        if (doc.type === 'legal') {
            $typeBadge.attr('class', 'rag-badge rag-badge-legal').text('Legal / Văn bản Pháp luật');
        } else {
            $typeBadge.attr('class', 'rag-badge rag-badge-hs').text('HS Code / Danh mục');
        }

        this.render_drawer_body();

        this.$root.find('#rag-drawer-backdrop').addClass('active');
        this.$root.find('#rag-drawer-panel').addClass('active');
    }

    close_drawer() {
        this.$root.find('#rag-drawer-backdrop').removeClass('active');
        this.$root.find('#rag-drawer-panel').removeClass('active');
    }

    render_drawer_body() {
        const doc = this.documents.find(d => d.id === this.state.selectedDocId);
        if (!doc) return;

        const $body = this.$root.find('#drawer-body-content');
        $body.empty();

        if (this.state.activeDrawerTab === 'chunks') {
            if (doc.chunks && doc.chunks.length > 0) {
                let html = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <span style="font-size: 13px; font-weight: 600; color: #334155;">Danh sách Chunks bóc tách tự nhiên:</span>
                        <span class="rag-badge rag-badge-neutral">Mô hình: BGE-M3 (1024-dim)</span>
                    </div>
                `;

                doc.chunks.forEach(chunk => {
                    html += `
                        <div class="rag-chunk-card">
                            <div class="rag-chunk-header">
                                <span class="rag-chunk-id">${chunk.id}</span>
                                <span class="rag-chunk-path">${chunk.path}</span>
                                <span class="rag-badge ${chunk.priority === 'P0' ? 'rag-badge-success' : 'rag-badge-warning'}">
                                    Ưu tiên ${chunk.priority}
                                </span>
                            </div>
                            <div class="rag-chunk-body">
                                "${chunk.text}"
                            </div>
                            <div class="rag-chunk-footer">
                                <span><i class="fa fa-database"></i> ${chunk.tokens} tokens</span>
                                <span>Metadata: <code>${JSON.stringify(chunk.meta)}</code></span>
                            </div>
                        </div>
                    `;
                });

                $body.html(html);
            } else {
                $body.html(`
                    <div style="text-align: center; padding: 40px; color: #64748b;">
                        <i class="fa fa-cubes" style="font-size: 32px; margin-bottom: 12px;"></i>
                        <div>Chưa có chunks nào cho tài liệu này.</div>
                        <div style="font-size: 12px; margin-top: 6px;">Tài liệu đang xử lý hoặc phát sinh lỗi bóc tách. Nhấn nút Re-index để thử lại.</div>
                    </div>
                `);
            }
        } else if (this.state.activeDrawerTab === 'metadata') {
            let metaHtml = `
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <h4 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 700; color: #0f172a;">Thông tin pháp lý & Danh mục</h4>
                    <table style="width: 100%; font-size: 13px; line-height: 2;">
                        <tr><td style="width: 160px; color: #64748b;">Số / Ký hiệu:</td><td><strong>${doc.title}</strong></td></tr>
                        <tr><td style="color: #64748b;">Cơ quan ban hành:</td><td>${doc.agency}</td></tr>
                        <tr><td style="color: #64748b;">Phiên bản danh mục:</td><td>${doc.version}</td></tr>
                        <tr><td style="color: #64748b;">Ngày ban hành:</td><td>${doc.release_date}</td></tr>
                        <tr><td style="color: #64748b;">Ngày có hiệu lực:</td><td>${doc.effective_date}</td></tr>
                        <tr><td style="color: #64748b;">Tình trạng pháp lý:</td><td><strong style="color: #059669;">${doc.legal_validity_label}</strong></td></tr>
                        <tr><td style="color: #64748b;">Quyền truy xuất:</td><td>${doc.retrieval_active ? 'Đang bật (Active)' : 'Đang tắt (Muted)'}</td></tr>
                    </table>
                </div>
            `;
            $body.html(metaHtml);
        } else if (this.state.activeDrawerTab === 'logs') {
            let logsHtml = `<div style="font-family: monospace; font-size: 12px; background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 8px; line-height: 1.8;">`;
            if (doc.logs && doc.logs.length > 0) {
                doc.logs.forEach(log => {
                    const color = log.level === 'ERROR' ? '#ef4444' : (log.level === 'WARNING' ? '#f59e0b' : '#10b981');
                    logsHtml += `<div><span style="color: #94a3b8;">[${log.time}]</span> <span style="color: ${color}; font-weight: 700;">[${log.level}]</span> ${log.msg}</div>`;
                });
            } else {
                logsHtml += `<div>Không có bản ghi log nào.</div>`;
            }
            logsHtml += `</div>`;
            $body.html(logsHtml);
        }
    }

    reindex_document(docId) {
        const doc = this.documents.find(d => d.id === docId);
        if (!doc) return;

        this.show_toast(`Bắt đầu Re-index lại tài liệu: ${doc.title}...`);
        doc.index_status = 'processing';
        this.render_documents_table();

        setTimeout(() => {
            doc.index_status = 'ready';
            doc.chunks_count = doc.chunks_count || 48;
            doc.logs.push({
                time: new Date().toISOString().replace('T', ' ').substring(0, 19),
                level: 'SUCCESS',
                msg: 'Re-index hoàn tất. Đã bóc tách và vector hóa toàn bộ chunks.'
            });
            this.show_toast(`Re-index thành công cho: ${doc.title}!`);
            this.render_documents_table();
            this.render_drawer_body();
        }, 1800);
    }

    open_wizard_modal() {
        this.state.wizardStep = 1;
        this.update_wizard_ui();
        this.$root.find('#rag-modal-wizard').addClass('active');
    }

    close_wizard_modal() {
        this.$root.find('#rag-modal-wizard').removeClass('active');
    }

    wizard_next() {
        if (this.state.wizardStep < 4) {
            this.state.wizardStep++;
            this.update_wizard_ui();
            if (this.state.wizardStep === 4) {
                this.simulate_wizard_indexing();
            }
        } else {
            this.show_toast('Tài liệu đã được thêm mới và hoàn tất Indexing vào hệ thống!');
            this.close_wizard_modal();
        }
    }

    wizard_prev() {
        if (this.state.wizardStep > 1) {
            this.state.wizardStep--;
            this.update_wizard_ui();
        }
    }

    update_wizard_ui() {
        const step = this.state.wizardStep;
        this.$root.find('.wizard-pane').hide();
        this.$root.find(`#wizard-step-${step}`).show();

        for (let i = 1; i <= 4; i++) {
            const $stepNav = this.$root.find(`#step-nav-${i}`);
            if (i <= step) {
                $stepNav.addClass('active');
            } else {
                $stepNav.removeClass('active');
            }
        }

        const $btnPrev = this.$root.find('#btn-wizard-prev');
        const $btnNext = this.$root.find('#btn-wizard-next');

        if (step === 1) {
            $btnPrev.css('visibility', 'hidden');
            $btnNext.html('Tiếp tục <i class="fa fa-arrow-right"></i>');
        } else if (step === 4) {
            $btnPrev.css('visibility', 'hidden');
            $btnNext.html('<i class="fa fa-check"></i> Hoàn tất & Lưu vào Kho');
        } else {
            $btnPrev.css('visibility', 'visible');
            $btnNext.html('Tiếp tục <i class="fa fa-arrow-right"></i>');
        }
    }

    simulate_wizard_indexing() {
        const $bar = this.$root.find('#wizard-progressbar');
        const $title = this.$root.find('#wizard-progress-title');
        const $desc = this.$root.find('#wizard-progress-desc');

        $bar.css('width', '25%');
        $title.text('Đang phân tích cú pháp Điều / Khoản...');
        $desc.text('Bóc tách 35 đoạn văn bản đầu tiên...');

        setTimeout(() => {
            $bar.css('width', '75%');
            $title.text('Đang tạo Dense Vector BGE-M3 (1024-dim)...');
            $desc.text('Hoàn tất 110/142 đoạn...');
        }, 800);

        setTimeout(() => {
            $bar.css('width', '100%');
            $title.text('Indexing Thành Công!');
            $desc.text('142 Chunks đã sẵn sàng phục vụ truy xuất RAG.');
        }, 1500);
    }

    show_toast(message) {
        const $container = this.$root.find('#rag-toast-container');
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div class="rag-toast" id="${toastId}">
                <i class="fa fa-info-circle" style="color: #38bdf8;"></i>
                <span>${message}</span>
            </div>
        `;
        $container.append(toastHtml);

        setTimeout(() => {
            $(`#${toastId}`).fadeOut(300, function () {
                $(this).remove();
            });
        }, 3500);
    }
}

function make_rag_page_full_bleed(wrapper) {
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
        $w.find('.page-head').hide();
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
        console.warn('make_rag_page_full_bleed warning:', e);
    }
}

function register_rag_admin_center_page(pageName) {
    frappe.pages[pageName] = frappe.pages[pageName] || {};

    frappe.pages[pageName].on_page_load = function (wrapper) {
        make_rag_page_full_bleed(wrapper);
        wrapper.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: (typeof __ !== 'undefined' ? __('RAG Admin Center') : 'RAG Admin Center'),
            single_column: true
        });

        // Hide default Frappe page-head for pure enterprise full-bleed
        if (wrapper.page && wrapper.page.wrapper) {
            $(wrapper.page.wrapper).find('.page-head').hide();
        }

        let html = '';
        try {
            if (frappe.templates && frappe.templates['rag_admin_center']) {
                html = frappe.render_template('rag_admin_center', {}) || frappe.templates['rag_admin_center'];
            } else if (frappe.templates && frappe.templates['rag-admin-center']) {
                html = frappe.render_template('rag-admin-center', {}) || frappe.templates['rag-admin-center'];
            }
        } catch (err) {
            console.warn('frappe.render_template fallback to raw template:', err);
            html = (frappe.templates && (frappe.templates['rag_admin_center'] || frappe.templates['rag-admin-center'])) || '';
        }

        if (!html && frappe.templates) {
            html = frappe.templates['rag_admin_center'] || frappe.templates['rag-admin-center'] || '';
        }

        if (html) {
            $(wrapper.page.body).html(html);
        }

        const controller = new RagAdminCenterController(wrapper.page.body);
        controller.switch_nav_tab('dashboard');
        wrapper.ragAdminController = controller;
        frappe.pages[pageName].controller = controller;
        make_rag_page_full_bleed(wrapper);
    };

    frappe.pages[pageName].on_page_show = function (wrapper) {
        make_rag_page_full_bleed(wrapper);
        if (wrapper.ragAdminController) {
            wrapper.ragAdminController.switch_nav_tab('dashboard');
            wrapper.ragAdminController.render_all();
        }
    };
}

['rag-admin-center', 'rag_admin_center', 'ragAdminCenter', 'ragadmincenter'].forEach(register_rag_admin_center_page);

if (typeof window !== 'undefined') {
    window.RagAdminCenterController = RagAdminCenterController;
}
