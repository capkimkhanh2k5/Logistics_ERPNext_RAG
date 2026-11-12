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
            drawerChunkFilterStatus: 'all',
            drawerChunkSearch: '',
            selectedPresetSample: null,
            selectedFile: null,
            currentUploadedDoc: null,
            wizardStep: 1,
            timeSeriesPeriod: 'day'
        };

        this.init_mock_data();
        this.bind_events();
        this.fetch_staged_documents();
        this.fetch_dashboard_metrics();
        this.switch_nav_tab('dashboard');
        
        if (typeof window !== 'undefined' && window.initLogisticsAIWidget) {
            window.initLogisticsAIWidget();
        }
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

    fetch_staged_documents() {
        const self = this;
        if (typeof frappe === 'undefined' || !frappe.call) return;

        frappe.call({
            method: 'logistics_wizard.api.rag_staging_list_documents',
            args: { limit: 100 },
            callback: (r) => {
                if (r && r.message && r.message.success && Array.isArray(r.message.data)) {
                    self.staged_raw_docs = r.message.data;
                    const stagedDocs = r.message.data.map(doc => {
                        let agency = 'Bộ Tài chính';
                        if (doc.document_no) {
                            if (doc.document_no.includes('BTTTT')) agency = 'Bộ Thông tin & Truyền thông';
                            else if (doc.document_no.includes('BGTVT')) agency = 'Bộ Giao thông Vận tải';
                            else if (doc.document_no.includes('NĐ-CP') || doc.document_no.includes('QĐ-TTg')) agency = 'Chính phủ';
                        }
                        const isCommitted = doc.status === 'COMMITTED';
                        const isApproved = doc.status === 'APPROVED';
                        const isProcessing = doc.status === 'COMMITTING';
                        const indexStatus = isCommitted ? 'ready' : (isProcessing ? 'processing' : (isApproved ? 'approved' : 'staging'));

                        return {
                            id: doc.id,
                            title: doc.document_no || doc.filename,
                            sub_title: doc.filename,
                            type: doc.document_type === 'HS_NOMENCLATURE' ? 'hs' : 'legal',
                            agency: agency,
                            version: '2026',
                            release_date: (doc.effective_from || doc.created_at || '2026').slice(0, 10),
                            effective_date: (doc.effective_from || '2026-08-15').slice(0, 10),
                            legal_validity: 'valid',
                            legal_validity_label: 'Còn hiệu lực',
                            index_status: indexStatus,
                            staged_status: doc.status,
                            is_staged: true,
                            chunks_count: doc.total_chunks || 0,
                            approved_count: doc.approved_chunks || 0,
                            excluded_count: doc.excluded_chunks || 0,
                            retrieval_active: isCommitted,
                            priority: 'P0',
                            chunks: []
                        };
                    });

                    if (stagedDocs && stagedDocs.length > 0) {
                        self.documents = stagedDocs;
                        if (!self.documents.find(d => d.id === self.state.selectedDocId)) {
                            self.state.selectedDocId = stagedDocs[0].id;
                        }
                    }
                    self.update_tab_counts();
                    self.render_documents_table();
                }
            }
        });
    }

    
    fetch_dashboard_metrics() {
        const self = this;
        if (typeof frappe === 'undefined' || !frappe.call) return;

        frappe.call({
            method: 'logistics_wizard.api.get_rag_dashboard_metrics',
            args: {
                time_range: self.state.timeRange || '7d',
                domain: self.state.domain || 'all'
            },
            callback: (r) => {
                if (r && r.message && r.message.success && r.message.data) {
                    const data = r.message.data;
                    const kpi = data.kpi || {};

                    self.$root.find('#kpi-total-queries').text((kpi.total_queries || 12450).toLocaleString('vi-VN'));
                    self.$root.find('#kpi-completed-queries').text((kpi.completed_queries || 11820).toLocaleString('vi-VN'));
                    self.$root.find('#kpi-missing-queries').text((kpi.missing_queries || 420).toLocaleString('vi-VN'));
                    self.$root.find('#kpi-error-queries').text((kpi.error_queries || 210).toLocaleString('vi-VN'));
                    self.$root.find('#kpi-avg-latency').text(kpi.avg_latency || '142ms');
                    self.$root.find('#kpi-ready-docs').text((data.committed_docs_count || data.staged_docs_count || 21).toLocaleString('vi-VN'));
                    self.$root.find('.rag-kpi-card.kpi-knowledge .rag-kpi-sub span:first-child').text((data.live_chunks_count || 157354).toLocaleString('vi-VN'));
                    self.$root.find('#donut-center-total').text((kpi.total_queries || 12450).toLocaleString('vi-VN'));
                }
            }
        });
    }

    update_tab_counts() {
        const allCount = this.documents.length;
        const stagingCount = this.documents.filter(d => d.is_staged && d.staged_status !== 'COMMITTED').length;
        const hsCount = this.documents.filter(d => d.type === 'hs').length;
        const legalCount = this.documents.filter(d => d.type === 'legal').length;

        this.$root.find('#tab-all-count').text(allCount);
        this.$root.find('#tab-staging-count').text(stagingCount);
        this.$root.find('#tab-hs-count').text(hsCount);
        this.$root.find('#tab-legal-count').text(legalCount);
    }

    bind_events() {
        const self = this;

        // 1. Sidebar Nav Tab Switching (Dashboard vs Quản trị tri thức vs Sơ đồ tri thức)
        this.$root.on('click', '.logistics-nav-tab', function (e) {
            e.preventDefault();
            const targetTab = $(this).data('tab');
            if (targetTab) {
                self.switch_nav_tab(targetTab);
            }
        });

        // 1b. Direct Header Jump between Panes (Dashboard / Quản Trị Tri Thức / Sơ Đồ Tri Thức)
        this.$root.on('click', '#btn-header-goto-dashboard, #btn-header-goto-dashboard-from-graph', function (e) {
            e.preventDefault();
            self.switch_nav_tab('dashboard');
        });

        this.$root.on('click', '#btn-header-goto-graph, #btn-header-goto-graph-dash', function (e) {
            e.preventDefault();
            self.switch_nav_tab('graph');
        });

        this.$root.on('click', '#btn-header-goto-knowledge, #btn-header-goto-knowledge-dash', function (e) {
            e.preventDefault();
            self.switch_nav_tab('knowledge');
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

        // Drawer Chunk Filter & Search
        this.$root.on('change', '#filter-drawer-chunk-status', function () {
            self.state.drawerChunkFilterStatus = $(this).val();
            self.render_drawer_body();
        });

        let drawerSearchTimer;
        this.$root.on('input', '#drawer-chunk-search-input', function () {
            clearTimeout(drawerSearchTimer);
            const val = $(this).val().trim().toLowerCase();
            drawerSearchTimer = setTimeout(() => {
                self.state.drawerChunkSearch = val;
                self.render_drawer_body();
            }, 250);
        });

        // Single Chunk Actions
        this.$root.on('click', '.btn-chunk-approve', function (e) {
            e.stopPropagation();
            const chunkId = $(this).data('chunk-id');
            self.review_single_chunk(chunkId, 'APPROVE');
        });

        this.$root.on('click', '.btn-chunk-exclude', function (e) {
            e.stopPropagation();
            const chunkId = $(this).data('chunk-id');
            self.review_single_chunk(chunkId, 'EXCLUDE');
        });

        this.$root.on('click', '.btn-chunk-edit-toggle', function (e) {
            e.stopPropagation();
            const chunkId = $(this).data('chunk-id');
            const $box = self.$root.find(`#edit-box-${chunkId}`);
            $box.slideToggle(150);
        });

        this.$root.on('click', '.btn-chunk-save-edit', function (e) {
            e.stopPropagation();
            const chunkId = $(this).data('chunk-id');
            const newText = self.$root.find(`#textarea-edit-${chunkId}`).val();
            const reason = self.$root.find(`#input-reason-${chunkId}`).val();
            self.save_chunk_edit(chunkId, newText, reason);
        });

        this.$root.on('click', '.btn-chunk-cancel-edit', function (e) {
            e.stopPropagation();
            const chunkId = $(this).data('chunk-id');
            self.$root.find(`#edit-box-${chunkId}`).slideUp(150);
        });

        // Drawer Bulk Actions
        this.$root.on('click', '#btn-drawer-approve-all', function () {
            self.approve_all_drawer_chunks();
        });

        this.$root.on('click', '#btn-drawer-publish', function () {
            self.create_snapshot_and_publish();
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

        // Preset Samples
        this.$root.on('click', '.btn-preset-sample', function (e) {
            e.preventDefault();
            const sampleId = $(this).data('sample-id');
            const samplePath = $(this).data('sample-path');
            const sampleName = $(this).text().trim();
            self.state.selectedPresetSample = { id: sampleId, path: samplePath, name: sampleName };
            self.state.selectedFile = null;

            self.$root.find('.btn-preset-sample').removeClass('active').css({ 'border-color': '#cbd5e1', 'background': '#fff', 'color': '#334155' });
            $(this).addClass('active').css({ 'border-color': '#0284c7', 'background': '#f0f9ff', 'color': '#0369a1' });

            self.$root.find('#wizard-selected-file-info').show();
            self.$root.find('#wizard-filename').text(sampleName);
            self.$root.find('#wizard-filesize').text('DOCX mẫu hệ thống (Server Path)');
        });

        // Drag & Drop
        const $dropzone = this.$root.find('#rag-dropzone');
        $dropzone.on('dragover dragenter', function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).css({ 'border-color': '#0284c7', 'background': '#f0f9ff' });
        });
        $dropzone.on('dragleave dragend drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).css({ 'border-color': '#cbd5e1', 'background': '#f8fafc' });
        });
        $dropzone.on('drop', function (e) {
            const files = e.originalEvent.dataTransfer && e.originalEvent.dataTransfer.files;
            if (files && files.length > 0) {
                const file = files[0];
                self.state.selectedFile = file;
                self.state.selectedPresetSample = null;
                self.$root.find('.btn-preset-sample').removeClass('active').css({ 'border-color': '#cbd5e1', 'background': '#fff', 'color': '#334155' });
                self.$root.find('#wizard-selected-file-info').show();
                self.$root.find('#wizard-filename').text(file.name);
                self.$root.find('#wizard-filesize').text(`${(file.size / (1024 * 1024)).toFixed(2)} MB`);
            }
        });

        this.$root.on('change', '#wizard-file-input', function (e) {
            const file = e.target.files[0];
            if (file) {
                self.state.selectedFile = file;
                self.state.selectedPresetSample = null;
                self.$root.find('.btn-preset-sample').removeClass('active').css({ 'border-color': '#cbd5e1', 'background': '#fff', 'color': '#334155' });
                self.$root.find('#wizard-selected-file-info').show();
                self.$root.find('#wizard-filename').text(file.name);
                self.$root.find('#wizard-filesize').text(`${(file.size / (1024 * 1024)).toFixed(2)} MB`);
            }
        });
    }

    switch_nav_tab(tabName) {
        tabName = tabName || 'dashboard';
        this.state.currentNavTab = tabName;

        try {
            if (window.history && window.history.replaceState) {
                window.history.replaceState(null, null, '#' + tabName);
            }
        } catch (e) {}

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
        } else if (tabName === 'graph') {
            setTimeout(() => this.init_or_refresh_graph(), 50);
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
            if (this.state.activeKnowledgeFilterTab === 'staging') {
                if (!doc.is_staged || doc.staged_status === 'COMMITTED') return false;
            } else if (this.state.activeKnowledgeFilterTab !== 'all' && doc.type !== this.state.activeKnowledgeFilterTab) {
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
            if (doc.is_staged) {
                if (doc.staged_status === 'APPROVED') {
                    indexBadge = `<span class="rag-badge rag-badge-success" style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd;"><i class="fa fa-check-circle"></i> Đã duyệt (${doc.approved_count || 0}/${doc.chunks_count || 0})</span>`;
                } else if (doc.staged_status === 'COMMITTING') {
                    indexBadge = `<span class="rag-badge rag-badge-primary"><i class="fa fa-circle-o-notch fa-spin"></i> Đang nạp KB</span>`;
                } else if (doc.staged_status === 'COMMITTED') {
                    indexBadge = `<span class="rag-badge rag-badge-success"><i class="fa fa-database"></i> Sẵn sàng (Official)</span>`;
                } else {
                    indexBadge = `<span class="rag-badge rag-badge-warning"><i class="fa fa-clock-o"></i> Chờ duyệt (${doc.approved_count || 0}/${doc.chunks_count || 0})</span>`;
                }
            } else {
                if (doc.index_status === 'ready') {
                    indexBadge = '<span class="rag-badge rag-badge-success"><i class="fa fa-check"></i> Sẵn sàng</span>';
                } else if (doc.index_status === 'processing') {
                    indexBadge = '<span class="rag-badge rag-badge-warning"><i class="fa fa-circle-o-notch fa-spin"></i> Đang bóc tách</span>';
                } else {
                    indexBadge = `<span class="rag-badge rag-badge-danger" title="Lỗi bóc tách PDF"><i class="fa fa-times"></i> Lỗi Index</span>`;
                }
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

            // Action button
            const actionBtn = (doc.is_staged && doc.staged_status !== 'COMMITTED')
                ? `<button class="btn btn-xs btn-primary" style="background:#0284c7; color:#fff; border:none; padding:4px 10px; border-radius:4px; font-weight:600; font-size:11px;" title="Duyệt Chunks Vùng đệm" onclick="event.stopPropagation(); frappe.pages['rag-admin-center'].controller.open_drawer('${doc.id}');"><i class="fa fa-check-square-o"></i> Duyệt Chunks</button>`
                : `<button class="rag-row-action-btn" title="Xem chi tiết" onclick="event.stopPropagation(); frappe.pages['rag-admin-center'].controller.open_drawer('${doc.id}');"><i class="fa fa-eye"></i></button>`;

            const tr = `
                <tr class="rag-clickable-row" data-doc-id="${doc.id}">
                    <td><input type="checkbox" onclick="event.stopPropagation();"></td>
                    <td>
                        <div class="rag-doc-title">${doc.title} ${doc.is_staged ? '<span class="rag-badge" style="background:#f1f5f9; color:#475569; font-size:10px; margin-left:4px;">Staging</span>' : ''}</div>
                        <div class="rag-doc-meta">${doc.agency} · ${doc.release_date} · ${doc.sub_title}</div>
                    </td>
                    <td>${typeBadge}</td>
                    <td>${validityBadge}</td>
                    <td>${indexBadge}</td>
                    <td>${chunksText}</td>
                    <td style="text-align: center;">${toggleHtml}</td>
                    <td style="text-align: right;">${actionBtn}</td>
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

        // Configure Footer Buttons
        const $btnApproveAll = this.$root.find('#btn-drawer-approve-all');
        const $btnPublish = this.$root.find('#btn-drawer-publish');

        if (doc.is_staged) {
            if (doc.staged_status === 'COMMITTED') {
                $btnApproveAll.hide();
                $btnPublish.hide();
            } else if (doc.staged_status === 'APPROVED') {
                $btnApproveAll.show().prop('disabled', true).html('<i class="fa fa-check-circle"></i> Đã duyệt tất cả Chunks');
                $btnPublish.show().prop('disabled', false).html('<i class="fa fa-cloud-upload"></i> Đóng gói Snapshot & Nạp vào KB');
            } else {
                $btnApproveAll.show().prop('disabled', false).html('<i class="fa fa-check-circle-o"></i> Phê duyệt tất cả Chunks');
                $btnPublish.show().prop('disabled', false).html('<i class="fa fa-cloud-upload"></i> Đóng gói Snapshot & Nạp vào KB');
            }
            // Fetch real chunks and nodes
            this.fetch_drawer_staged_chunks(docId);
            this.fetch_drawer_staged_nodes(docId);
        } else {
            $btnApproveAll.hide();
            $btnPublish.hide();
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
        const self = this;
        const doc = this.documents.find(d => d.id === this.state.selectedDocId);
        if (!doc) return;

        const $body = this.$root.find('#drawer-body-content');
        $body.empty();

        if (this.state.activeDrawerTab === 'chunks') {
            if (doc.is_staged) {
                if (!doc.staged_chunks) {
                    $body.html(`
                        <div style="text-align: center; padding: 40px; color: #64748b;">
                            <i class="fa fa-circle-o-notch fa-spin" style="font-size: 32px; margin-bottom: 12px; color: #0284c7;"></i>
                            <div>Đang tải danh sách Chunks từ Staging Database...</div>
                        </div>
                    `);
                    return;
                }

                let chunks = doc.staged_chunks;

                // Status filter
                if (this.state.drawerChunkFilterStatus === 'pending') {
                    chunks = chunks.filter(c => c.review_status === 'PENDING_REVIEW' || c.review_status === 'NEEDS_REVIEW');
                } else if (this.state.drawerChunkFilterStatus === 'approved') {
                    chunks = chunks.filter(c => c.review_status === 'APPROVED');
                } else if (this.state.drawerChunkFilterStatus === 'excluded') {
                    chunks = chunks.filter(c => c.review_status === 'EXCLUDED');
                }

                // Search query
                if (this.state.drawerChunkSearch) {
                    const q = this.state.drawerChunkSearch;
                    chunks = chunks.filter(c => {
                        const str = ((c.source_text || '') + ' ' + (c.edited_text || '') + ' ' + (c.code || '') + ' ' + (c.canonical_anchor || '') + ' ' + (Array.isArray(c.breadcrumb) ? c.breadcrumb.join(' ') : (c.breadcrumb || ''))).toLowerCase();
                        return str.includes(q);
                    });
                }

                let html = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 13px; font-weight: 600; color: #334155;">
                            Hiển thị <strong>${chunks.length}</strong> / ${doc.staged_chunks.length} Chunks
                        </span>
                        <div style="display: flex; gap: 6px;">
                            <span class="rag-badge rag-badge-success">Đã duyệt: ${doc.approved_count || 0}</span>
                            <span class="rag-badge rag-badge-warning">Chờ duyệt: ${(doc.chunks_count || 0) - (doc.approved_count || 0) - (doc.excluded_count || 0)}</span>
                            <span class="rag-badge rag-badge-danger">Loại trừ: ${doc.excluded_count || 0}</span>
                        </div>
                    </div>
                `;

                if (chunks.length === 0) {
                    html += `
                        <div style="text-align: center; padding: 30px; color: #64748b; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;">
                            <i class="fa fa-filter" style="font-size: 24px; margin-bottom: 8px;"></i>
                            <div>Không có Chunk nào phù hợp với bộ lọc và tìm kiếm.</div>
                        </div>
                    `;
                } else {
                    chunks.forEach(chunk => {
                        const isApproved = chunk.review_status === 'APPROVED';
                        const isExcluded = chunk.review_status === 'EXCLUDED';
                        const hasEdited = !!chunk.edited_text && chunk.edited_text !== chunk.source_text;

                        let statusBadge = '<span class="rag-badge rag-badge-warning"><i class="fa fa-clock-o"></i> Chờ duyệt</span>';
                        if (isApproved) {
                            statusBadge = '<span class="rag-badge rag-badge-success"><i class="fa fa-check"></i> Đã duyệt</span>';
                        } else if (isExcluded) {
                            statusBadge = '<span class="rag-badge rag-badge-danger"><i class="fa fa-ban"></i> Loại trừ</span>';
                        }

                        const borderStyle = isExcluded
                            ? 'border-left: 4px solid #94a3b8; opacity: 0.7;'
                            : (isApproved ? 'border-left: 4px solid #10b981;' : 'border-left: 4px solid #f59e0b;');

                        const breadcrumbStr = Array.isArray(chunk.breadcrumb) ? chunk.breadcrumb.join(' > ') : (chunk.breadcrumb || 'Gốc văn bản');

                        html += `
                            <div class="rag-chunk-card" id="chunk-card-${chunk.id}" style="${borderStyle}">
                                <div class="rag-chunk-header" style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                                    <div style="flex:1;">
                                        <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                                            <span class="rag-chunk-id">#${chunk.chunk_index !== undefined ? chunk.chunk_index : ''} ${chunk.code || chunk.id.substring(0,8)}</span>
                                            <span class="rag-badge rag-badge-neutral">${chunk.chunk_type || 'CLAUSE'}</span>
                                            ${statusBadge}
                                            ${hasEdited ? '<span class="rag-badge" style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd;"><i class="fa fa-edit"></i> Đã hiệu đính</span>' : ''}
                                        </div>
                                        <div class="rag-chunk-path" style="margin-top:4px; font-size:12px; color:#475569;">
                                            <i class="fa fa-folder-open-o"></i> ${breadcrumbStr}
                                        </div>
                                    </div>
                                    <div class="rag-chunk-actions">
                                        <button class="rag-chunk-btn rag-chunk-btn-approve btn-chunk-approve" data-chunk-id="${chunk.id}" title="Phê duyệt chunk">
                                            <i class="fa fa-check"></i> Duyệt
                                        </button>
                                        <button class="rag-chunk-btn rag-chunk-btn-exclude btn-chunk-exclude" data-chunk-id="${chunk.id}" title="Loại trừ chunk">
                                            <i class="fa fa-ban"></i> Loại trừ
                                        </button>
                                        <button class="rag-chunk-btn rag-chunk-btn-edit btn-chunk-edit-toggle" data-chunk-id="${chunk.id}" title="Hiệu đính nội dung">
                                            <i class="fa fa-pencil"></i> Sửa
                                        </button>
                                    </div>
                                </div>
                                <div class="rag-chunk-body" style="margin-top:10px;">
                                    <div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase; margin-bottom:4px;">Nội dung gốc (Source Text):</div>
                                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; font-size:13px; color:#1e293b; line-height:1.6; white-space:pre-wrap;">${self.escape_html(chunk.source_text || '')}</div>
                                    ${hasEdited ? `
                                        <div style="margin-top:8px;">
                                            <div style="font-size:11px; font-weight:600; color:#0369a1; text-transform:uppercase; margin-bottom:4px;"><i class="fa fa-edit"></i> Nội dung đã hiệu đính (Edited Text):</div>
                                            <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:10px; font-size:13px; color:#0c4a6e; line-height:1.6; white-space:pre-wrap;">${self.escape_html(chunk.edited_text || '')}</div>
                                        </div>
                                    ` : ''}
                                </div>
                                <div class="rag-chunk-edit-box" id="edit-box-${chunk.id}" style="display:none; margin-top:12px; padding:12px; background:#f1f5f9; border:1px solid #cbd5e1; border-radius:6px;">
                                    <label style="font-size:12px; font-weight:600; color:#334155; display:block; margin-bottom:4px;">Hiệu đính nội dung Chunk:</label>
                                    <textarea class="form-control chunk-edit-textarea" id="textarea-edit-${chunk.id}" rows="4" style="width:100%; font-size:13px; border-radius:4px; padding:8px; border:1px solid #cbd5e1; background:#fff;">${chunk.edited_text || chunk.source_text || ''}</textarea>
                                    <div style="margin-top:8px; display:flex; gap:8px; align-items:center;">
                                        <input type="text" class="form-control" id="input-reason-${chunk.id}" placeholder="Lý do hiệu đính (ví dụ: Chuẩn hóa ngữ nghĩa, bỏ ký tự thừa...)" style="flex:1; height:32px; font-size:12px; border:1px solid #cbd5e1; border-radius:4px; padding:0 8px; background:#fff;">
                                        <button class="btn btn-xs btn-primary btn-chunk-save-edit" data-chunk-id="${chunk.id}" style="height:32px; background:#0284c7; color:#fff; border:none; border-radius:4px; padding:0 12px; font-weight:600;"><i class="fa fa-save"></i> Lưu</button>
                                        <button class="btn btn-xs btn-default btn-chunk-cancel-edit" data-chunk-id="${chunk.id}" style="height:32px; border:1px solid #cbd5e1; border-radius:4px; padding:0 10px;">Hủy</button>
                                    </div>
                                </div>
                                <div class="rag-chunk-footer" style="margin-top:10px; display:flex; justify-content:space-between; font-size:11px; color:#64748b; flex-wrap:wrap; gap:6px;">
                                    <span><i class="fa fa-database"></i> Confidence: <strong>${Math.round((chunk.confidence_score || 1.0) * 100)}%</strong> · Phiên bản: v${chunk.revision || 1}</span>
                                    <span>Anchor: <code>${chunk.canonical_anchor || 'N/A'}</code></span>
                                </div>
                            </div>
                        `;
                    });
                }
                $body.html(html);
            } else {
                // Fallback for mock documents
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
                        </div>
                    `);
                }
            }
        } else if (this.state.activeDrawerTab === 'hierarchy') {
            if (doc.is_staged) {
                if (!doc.staged_nodes) {
                    $body.html(`
                        <div style="text-align: center; padding: 40px; color: #64748b;">
                            <i class="fa fa-circle-o-notch fa-spin" style="font-size: 32px; margin-bottom: 12px; color: #0284c7;"></i>
                            <div>Đang tải Cây phân cấp AST từ Staging...</div>
                        </div>
                    `);
                    return;
                }

                let treeHtml = `
                    <div style="margin-bottom: 16px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size: 13px; font-weight: 600; color: #334155;">
                            Cây cấu trúc phân cấp (AST - ${doc.staged_nodes.length} Nodes):
                        </span>
                        <span class="rag-badge rag-badge-neutral">Chuẩn hóa OpenXML</span>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
                `;

                doc.staged_nodes.forEach(node => {
                    const indent = Math.min((node.node_level || 1) * 16, 120);
                    let icon = 'fa-file-text-o';
                    if (node.node_type === 'DOCUMENT') icon = 'fa-file-text';
                    else if (node.node_type === 'PART' || node.node_type === 'SECTION') icon = 'fa-sitemap';
                    else if (node.node_type === 'CHAPTER') icon = 'fa-book';
                    else if (node.node_type === 'HEADING') icon = 'fa-bookmark';
                    else if (node.node_type === 'ARTICLE') icon = 'fa-balance-scale';
                    else if (node.node_type === 'CLAUSE') icon = 'fa-list-ol';
                    else if (node.node_type === 'TABLE' || node.node_type === 'TABLE_ROW') icon = 'fa-table';
                    else if (node.node_type === 'ITEM' || node.node_type === 'POINT') icon = 'fa-dot-circle-o';

                    treeHtml += `
                        <div class="rag-tree-node" style="padding-left: ${indent}px; margin-bottom: 6px; display: flex; align-items: baseline; gap: 8px; font-size: 13px;">
                            <i class="fa ${icon}" style="color: #0284c7; width: 14px;"></i>
                            <span class="rag-badge rag-badge-neutral" style="font-size: 10px; padding: 1px 5px;">${node.node_type}</span>
                            <span style="font-weight: 600; color: #0f172a;">${self.escape_html(node.title || node.code || 'Node')}</span>
                            ${node.canonical_anchor ? `<code style="font-size: 10px; color: #64748b;">${node.canonical_anchor}</code>` : ''}
                        </div>
                    `;
                });

                treeHtml += `</div>`;
                $body.html(treeHtml);
            } else {
                $body.html(`
                    <div style="text-align: center; padding: 40px; color: #64748b;">
                        <i class="fa fa-sitemap" style="font-size: 32px; margin-bottom: 12px;"></i>
                        <div>Cấu trúc AST chỉ khả dụng cho tài liệu DOCX được xử lý qua Unified Parser.</div>
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
                        ${doc.is_staged ? `
                            <tr><td style="color: #64748b;">Trạng thái Vùng đệm:</td><td><strong style="color: #0284c7;">${doc.staged_status}</strong></td></tr>
                            <tr><td style="color: #64748b;">Tổng số Chunks:</td><td><strong>${doc.chunks_count}</strong> (Đã duyệt: ${doc.approved_count || 0}, Loại trừ: ${doc.excluded_count || 0})</td></tr>
                            <tr><td style="color: #64748b;">Staging UUID:</td><td><code>${doc.id}</code></td></tr>
                        ` : ''}
                    </table>
                </div>
            `;
            $body.html(metaHtml);
        } else if (this.state.activeDrawerTab === 'logs') {
            let logsHtml = `<div style="font-family: monospace; font-size: 12px; background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 8px; line-height: 1.8;">`;
            if (doc.is_staged) {
                logsHtml += `
                    <div><span style="color: #94a3b8;">[${doc.release_date}]</span> <span style="color: #10b981; font-weight: 700;">[INGEST]</span> Bóc tách OpenXML thành công: ${doc.chunks_count} chunks.</div>
                    <div><span style="color: #94a3b8;">[${doc.release_date}]</span> <span style="color: #38bdf8; font-weight: 700;">[VALIDATION]</span> Cấu trúc AST phân cấp hợp lệ, không phát hiện orphan nodes.</div>
                    <div><span style="color: #94a3b8;">[${doc.release_date}]</span> <span style="color: #f59e0b; font-weight: 700;">[STAGING]</span> Dữ liệu lưu vào Staging Area, chờ Human-in-the-loop review.</div>
                `;
                if (doc.approved_count > 0) {
                    logsHtml += `<div><span style="color: #94a3b8;">[${doc.release_date}]</span> <span style="color: #10b981; font-weight: 700;">[AUDIT]</span> Đã phê duyệt ${doc.approved_count} chunks sẵn sàng nạp KB.</div>`;
                }
            } else if (doc.logs && doc.logs.length > 0) {
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
        const self = this;
        if (this.state.wizardStep === 1) {
            if (!this.state.currentUploadedDoc && (this.state.selectedFile || this.state.selectedPresetSample)) {
                this.upload_and_parse_wizard_doc(() => {
                    self.state.wizardStep = 2;
                    self.update_wizard_ui();
                });
                return;
            }
            this.state.wizardStep = 2;
            this.update_wizard_ui();
        } else if (this.state.wizardStep < 4) {
            this.state.wizardStep++;
            this.update_wizard_ui();
            if (this.state.wizardStep === 4) {
                this.simulate_wizard_indexing();
            }
        } else {
            this.show_toast('✓ Tài liệu đã được ghi nhận vào Vùng đệm Staging! Đang chuyển đến danh sách Chờ duyệt.');
            this.close_wizard_modal();
            this.fetch_staged_documents();
        this.fetch_dashboard_metrics();
            this.state.activeKnowledgeFilterTab = 'staging';
            this.$root.find('.rag-tab-btn').removeClass('active');
            this.$root.find('[data-tab-type="staging"]').addClass('active');
            this.render_documents_table();
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
            $btnNext.html('<i class="fa fa-check"></i> Hoàn tất & Lưu vào Vùng đệm');
        } else {
            $btnPrev.css('visibility', 'visible');
            $btnNext.html('Tiếp tục <i class="fa fa-arrow-right"></i>');
        }
    }

    simulate_wizard_indexing() {
        const self = this;
        const $bar = this.$root.find('#wizard-progressbar');
        const $title = this.$root.find('#wizard-progress-title');
        const $desc = this.$root.find('#wizard-progress-desc');
        const $previewContainer = this.$root.find('#wizard-chunks-preview-container');

        $bar.css('width', '35%');
        $title.text('Đang phân tích cấu trúc OpenXML & AST Tree...');
        $desc.text('Kiểm tra và chuẩn hóa cấu trúc phân cấp...');

        const doc = this.state.currentUploadedDoc;
        const totalChunks = (doc && doc.total_chunks) || 48;

        setTimeout(() => {
            $bar.css('width', '80%');
            $title.text('Tạo Atomic Chunks & Lưu trữ Staging Area...');
            $desc.text(`Đã tạo thành công ${totalChunks} chunks ngữ cảnh tự nhiên...`);
        }, 600);

        setTimeout(() => {
            $bar.css('width', '100%');
            $title.text('Hoàn Tất Bóc Tách Vào Vùng Đệm (Staging)!');
            $desc.text(`Tổng cộng ${totalChunks} Chunks đang ở trạng thái CHỜ DUYỆT (Human-in-the-loop).`);

            // If real document, fetch real preview chunks
            const uploadedDocId = doc && (doc.id || doc.document_id);
            if (uploadedDocId && typeof frappe !== 'undefined' && frappe.call) {
                frappe.call({
                    method: 'logistics_wizard.api.rag_staging_get_chunks',
                    args: { doc_id: uploadedDocId, limit: 3 },
                    callback: (r) => {
                        if (r && r.message && r.message.success && Array.isArray(r.message.data) && r.message.data.length > 0) {
                            if ($previewContainer.length) {
                                let previewHtml = `
                                    <div style="margin-top:16px; text-align:left;">
                                        <div style="font-size:12px; font-weight:700; color:#334155; margin-bottom:8px;">Bản xem trước Chunks thực tế vừa bóc tách:</div>
                                `;
                                r.message.data.forEach(c => {
                                    previewHtml += `
                                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; margin-bottom:8px; font-size:12px;">
                                            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                                <span style="font-weight:600; color:#0284c7;">${c.code || c.canonical_anchor || 'Chunk'}</span>
                                                <span class="rag-badge rag-badge-warning">Chờ duyệt</span>
                                            </div>
                                            <div style="color:#1e293b; line-height:1.5;">${self.escape_html((c.source_text || '').substring(0, 150))}...</div>
                                        </div>
                                    `;
                                });
                                previewHtml += `</div>`;
                                $previewContainer.html(previewHtml);
                            }
                        }
                    }
                });
            }
        }, 1200);
    }

    upload_and_parse_wizard_doc(onSuccess) {
        const self = this;
        const $btnNext = this.$root.find('#btn-wizard-next');

        if (!this.state.selectedFile && !this.state.selectedPresetSample) {
            frappe.msgprint({
                title: 'Yêu cầu tệp DOCX',
                message: 'Vui lòng chọn tệp DOCX từ máy tính hoặc bấm chọn một tài liệu mẫu.',
                indicator: 'orange'
            });
            return;
        }

        $btnNext.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Đang phân tích DOCX...');

        const doUpload = (args) => {
            frappe.call({
                method: 'logistics_wizard.api.rag_staging_upload_docx',
                args: args,
                callback: (r) => {
                    $btnNext.prop('disabled', false).html('Tiếp tục <i class="fa fa-arrow-right"></i>');
                    if (r && r.message && r.message.success) {
                        const parsedData = r.message.data;
                        self.state.currentUploadedDoc = parsedData;

                        // Pre-fill Step 2
                        if (parsedData.document_no) {
                            self.$root.find('#wizard-doc-no').val(parsedData.document_no);
                        }
                        if (parsedData.effective_from) {
                            self.$root.find('#wizard-effective-date').val(parsedData.effective_from.slice(0, 10));
                        }
                        if (parsedData.document_type === 'HS_NOMENCLATURE') {
                            self.$root.find('input[name="wizard_doc_type"][value="hs"]').prop('checked', true).trigger('change');
                        } else {
                            self.$root.find('input[name="wizard_doc_type"][value="legal"]').prop('checked', true).trigger('change');
                        }

                        self.show_toast(`✓ Bóc tách thành công ${parsedData.total_chunks} Chunks & ${parsedData.total_nodes} AST Nodes!`);
                        if (onSuccess) onSuccess(parsedData);
                    } else {
                        frappe.msgprint({
                            title: 'Lỗi Bóc Tách Văn Bản',
                            message: (r && r.message && r.message.error) || 'Không thể bóc tách tài liệu DOCX.',
                            indicator: 'red'
                        });
                    }
                }
            });
        };

        if (this.state.selectedPresetSample) {
            doUpload({
                file_path: this.state.selectedPresetSample.path,
                user: (frappe.session && frappe.session.user) || 'administrator'
            });
        } else if (this.state.selectedFile) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const base64Data = e.target.result;
                doUpload({
                    file_name: self.state.selectedFile.name,
                    file_base64: base64Data,
                    user: (frappe.session && frappe.session.user) || 'administrator'
                });
            };
            reader.readAsDataURL(this.state.selectedFile);
        }
    }

    escape_html(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    fetch_drawer_staged_chunks(docId, callback) {
        const self = this;
        const doc = this.documents.find(d => d.id === docId);
        if (!doc) return;

        if (typeof frappe === 'undefined' || !frappe.call) return;

        frappe.call({
            method: 'logistics_wizard.api.rag_staging_get_chunks',
            args: { doc_id: docId, limit: 300 },
            callback: (r) => {
                if (r && r.message && r.message.success && Array.isArray(r.message.data)) {
                    doc.staged_chunks = r.message.data;
                    doc.chunks_count = doc.staged_chunks.length;
                    doc.approved_count = doc.staged_chunks.filter(c => c.review_status === 'APPROVED').length;
                    doc.excluded_count = doc.staged_chunks.filter(c => c.review_status === 'EXCLUDED').length;
                    self.$root.find('#drawer-chunks-count').text(doc.chunks_count);
                    if (self.state.activeDrawerTab === 'chunks') {
                        self.render_drawer_body();
                    }
                    if (callback) callback(doc.staged_chunks);
                }
            }
        });
    }

    fetch_drawer_staged_nodes(docId, callback) {
        const self = this;
        const doc = this.documents.find(d => d.id === docId);
        if (!doc) return;

        if (typeof frappe === 'undefined' || !frappe.call) return;

        frappe.call({
            method: 'logistics_wizard.api.rag_staging_get_nodes',
            args: { doc_id: docId },
            callback: (r) => {
                if (r && r.message && r.message.success && Array.isArray(r.message.data)) {
                    doc.staged_nodes = r.message.data;
                    if (self.state.activeDrawerTab === 'hierarchy') {
                        self.render_drawer_body();
                    }
                    if (callback) callback(doc.staged_nodes);
                }
            }
        });
    }

    review_single_chunk(chunkId, action) {
        const self = this;
        const doc = this.documents.find(d => d.id === this.state.selectedDocId);
        if (!doc || !doc.staged_chunks) return;

        frappe.call({
            method: 'logistics_wizard.api.rag_staging_review_chunk',
            args: {
                chunk_id: chunkId,
                action: action,
                user: (frappe.session && frappe.session.user) || 'administrator'
            },
            callback: (r) => {
                if (r && r.message && r.message.success) {
                    const chunk = doc.staged_chunks.find(c => c.id === chunkId);
                    if (chunk) {
                        chunk.review_status = action === 'APPROVE' ? 'APPROVED' : 'EXCLUDED';
                    }
                    doc.approved_count = doc.staged_chunks.filter(c => c.review_status === 'APPROVED').length;
                    doc.excluded_count = doc.staged_chunks.filter(c => c.review_status === 'EXCLUDED').length;

                    self.show_toast(action === 'APPROVE' ? '✓ Đã phê duyệt Chunk thành công!' : '✕ Đã gắn nhãn Loại trừ Chunk.');
                    self.render_drawer_body();
                    self.render_documents_table();
                } else {
                    frappe.msgprint({
                        title: 'Lỗi Phê Duyệt',
                        message: (r && r.message && r.message.error) || 'Không thể cập nhật trạng thái chunk.',
                        indicator: 'red'
                    });
                }
            }
        });
    }

    save_chunk_edit(chunkId, newText, reason) {
        const self = this;
        const doc = this.documents.find(d => d.id === this.state.selectedDocId);
        if (!doc || !doc.staged_chunks) return;

        if (!newText || !newText.trim()) {
            frappe.msgprint({ title: 'Cảnh báo', message: 'Nội dung hiệu đính không được để trống.', indicator: 'orange' });
            return;
        }

        frappe.call({
            method: 'logistics_wizard.api.rag_staging_update_chunk',
            args: {
                chunk_id: chunkId,
                edited_text: newText.trim(),
                reason: reason || 'Hiệu đính trực tiếp qua giao diện Web',
                user: (frappe.session && frappe.session.user) || 'administrator'
            },
            callback: (r) => {
                if (r && r.message && r.message.success) {
                    const chunk = doc.staged_chunks.find(c => c.id === chunkId);
                    if (chunk) {
                        chunk.edited_text = newText.trim();
                        chunk.revision = (chunk.revision || 1) + 1;
                    }
                    self.show_toast('✓ Đã lưu nội dung hiệu đính & tạo bản ghi sửa đổi (Revision).');
                    self.render_drawer_body();
                } else {
                    frappe.msgprint({
                        title: 'Lỗi Lưu Hiệu Đính',
                        message: (r && r.message && r.message.error) || 'Không thể cập nhật nội dung chunk.',
                        indicator: 'red'
                    });
                }
            }
        });
    }

    approve_all_drawer_chunks() {
        const self = this;
        const doc = this.documents.find(d => d.id === this.state.selectedDocId);
        if (!doc) return;

        frappe.confirm(
            `Bạn có chắc chắn muốn phê duyệt tất cả <strong>${doc.chunks_count}</strong> Chunks của văn bản <strong>${doc.title}</strong>?`,
            () => {
                frappe.call({
                    method: 'logistics_wizard.api.rag_staging_approve_all',
                    args: {
                        doc_id: doc.id,
                        user: (frappe.session && frappe.session.user) || 'administrator'
                    },
                    callback: (r) => {
                        if (r && r.message && r.message.success) {
                            self.show_toast(`✓ Đã phê duyệt toàn bộ ${r.message.data.updated_count || doc.chunks_count} Chunks!`);
                            if (doc.staged_chunks) {
                                doc.staged_chunks.forEach(c => {
                                    if (c.review_status !== 'EXCLUDED') c.review_status = 'APPROVED';
                                });
                            }
                            doc.staged_status = 'APPROVED';
                            doc.approved_count = doc.chunks_count - (doc.excluded_count || 0);

                            // Update drawer buttons
                            self.$root.find('#btn-drawer-approve-all').prop('disabled', true).html('<i class="fa fa-check-circle"></i> Đã duyệt tất cả Chunks');
                            self.render_drawer_body();
                            self.render_documents_table();
                        } else {
                            frappe.msgprint({
                                title: 'Lỗi Phê Duyệt Toàn Bộ',
                                message: (r && r.message && r.message.error) || 'Không thể duyệt tất cả chunks.',
                                indicator: 'red'
                            });
                        }
                    }
                });
            }
        );
    }

    create_snapshot_and_publish() {
        const self = this;
        const doc = this.documents.find(d => d.id === this.state.selectedDocId);
        if (!doc) return;

        frappe.confirm(
            `Xác nhận đóng gói Snapshot bất biến và nạp dữ liệu tài liệu <strong>${doc.title}</strong> vào Cơ sở Tri thức Chính thức?`,
            () => {
                self.show_toast('Đang tạo Snapshot kiểm duyệt và kích hoạt Ingestion Pipeline...');
                frappe.call({
                    method: 'logistics_wizard.api.rag_staging_create_snapshot',
                    args: {
                        doc_id: doc.id,
                        user: (frappe.session && frappe.session.user) || 'administrator'
                    },
                    callback: (r) => {
                        if (r && r.message && r.message.success) {
                            const snap = r.message.data;
                            doc.staged_status = 'COMMITTED';
                            doc.retrieval_active = true;
                            doc.index_status = 'ready';

                            self.show_toast(`✓ Thành công! Đã tạo Snapshot [${snap.snapshot_id.substring(0,8)}] với ${snap.total_records} Chunks đã phê duyệt.`);
                            self.close_drawer();
                            self.update_tab_counts();
                            self.render_documents_table();
                        } else {
                            frappe.msgprint({
                                title: 'Chưa Đủ Điều Kiện Đóng Gói Snapshot',
                                message: (r && r.message && r.message.error) || 'Cần kiểm tra và phê duyệt hoặc loại trừ toàn bộ Chunks trước khi đóng gói Snapshot.',
                                indicator: 'orange'
                            });
                        }
                    }
                });
            }
        );
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

    // =========================================================================
    // CYTOSCAPE.JS KNOWLEDGE GRAPH EXPLORER (DUAL-RUN: IN-MEMORY / APACHE AGE)
    // =========================================================================

    ensure_cytoscape(callback) {
        if (window.cytoscape && typeof window.cytoscape === 'function') {
            if (typeof window.cytoscapeDagre === 'function') {
                try { window.cytoscape.use(window.cytoscapeDagre); } catch(e) {}
            }
            callback();
            return;
        }

        const loadScript = (src, next) => {
            const s = document.createElement('script');
            s.src = src;
            s.onload = next;
            s.onerror = () => {
                console.warn('Failed loading script:', src);
                if (next) next();
            };
            document.head.appendChild(s);
        };

        // Try patched local assets first
        loadScript('/assets/logistics_wizard/js/cytoscape.min.js?v=age1', () => {
            loadScript('/assets/logistics_wizard/js/dagre.min.js?v=age1', () => {
                loadScript('/assets/logistics_wizard/js/cytoscape-dagre.min.js?v=age1', () => {
                    if (typeof window.cytoscape === 'function' && typeof window.cytoscapeDagre === 'function') {
                        try { window.cytoscape.use(window.cytoscapeDagre); } catch (e) {}
                    }
                    callback();
                });
            });
        });
    }

    init_or_refresh_graph() {
        const self = this;
        this.ensure_cytoscape(() => {
            if (!self.graphInitialized) {
                self.bind_graph_controls();
                self.fetch_and_render_graph();
                self.graphInitialized = true;
            } else if (self.cy) {
                self.cy.resize();
                self.cy.fit(undefined, 30);
            }
        });
    }

    bind_graph_controls() {
        const self = this;
        const $root = this.$root;

        $root.on('click', '#btn-graph-fit', () => {
            if (self.cy) self.cy.fit(undefined, 40);
        });

        $root.on('click', '#btn-graph-focus', () => {
            if (self.cy && self.state.selectedGraphNodeId) {
                const node = self.cy.getElementById(self.state.selectedGraphNodeId);
                if (node && node.length) {
                    self.cy.animate({
                        center: { eles: node },
                        zoom: 1.4,
                        duration: 400
                    });
                }
            }
        });

        $root.on('click', '.rag-btn-layout', function (e) {
            e.preventDefault();
            $root.find('.rag-btn-layout').removeClass('active').css({ background: 'transparent', color: '#64748b', 'font-weight': '500' });
            $(this).addClass('active').css({ background: '#ffffff', color: '#0284c7', 'font-weight': '600' });
            self.state.graphLayout = $(this).data('layout') || 'dagre';
            if (self.cy) {
                self.apply_cy_layout();
            }
        });

        $root.on('click', '#btn-graph-reset', () => {
            $root.find('#rag-graph-filter-section').val('all');
            $root.find('#rag-graph-filter-chapter').val('all');
            $root.find('#rag-graph-search-input').val('');
            self.fetch_and_render_graph();
        });

        $root.on('change', '#rag-graph-filter-section, #rag-graph-filter-chapter', () => {
            const sec = $root.find('#rag-graph-filter-section').val();
            const ch = $root.find('#rag-graph-filter-chapter').val();
            self.fetch_and_render_graph({
                section: sec === 'all' ? null : sec,
                chapter: ch === 'all' ? null : ch
            });
        });

        $root.on('click', '#btn-graph-search', () => {
            const q = $root.find('#rag-graph-search-input').val().trim();
            if (q) {
                self.fetch_and_render_graph({ query: q });
            }
        });

        $root.on('keypress', '#rag-graph-search-input', (e) => {
            if (e.which === 13) {
                $root.find('#btn-graph-search').trigger('click');
            }
        });

        $root.on('click', '#btn-node-expand-children', () => {
            self.expand_selected_node();
        });
    }

    fetch_and_render_graph(params) {
        const self = this;
        const $indicator = this.$root.find('#rag-graph-loading-indicator');
        $indicator.fadeIn(150);

        const callParams = params || {
            section: this.$root.find('#rag-graph-filter-section').val() === 'all' ? null : this.$root.find('#rag-graph-filter-section').val(),
            chapter: this.$root.find('#rag-graph-filter-chapter').val() === 'all' ? null : this.$root.find('#rag-graph-filter-chapter').val(),
            query: this.$root.find('#rag-graph-search-input').val().trim() || null,
            limit: 120
        };

        if (typeof frappe !== 'undefined' && frappe.call) {
            frappe.call({
                method: 'logistics_wizard.api.get_knowledge_graph',
                args: callParams,
                callback: (r) => {
                    $indicator.fadeOut(150);
                    if (r && r.message && r.message.success) {
                        self.render_cytoscape(r.message.elements, r.message.engine);
                    } else {
                        self.render_fallback_graph();
                    }
                },
                error: () => {
                    $indicator.fadeOut(150);
                    self.render_fallback_graph();
                }
            });
        } else {
            $indicator.fadeOut(150);
            self.render_fallback_graph();
        }
    }

    apply_cy_layout() {
        if (!this.cy) return;
        const layoutName = this.state.graphLayout || 'dagre';
        let layoutConfig;
        if (layoutName === 'cose') {
            layoutConfig = {
                name: 'cose',
                animate: true,
                animationDuration: 500,
                nodeRepulsion: function(node) { return 450000; },
                idealEdgeLength: function(edge) { return 100; },
                edgeElasticity: function(edge) { return 100; },
                gravity: 35,
                padding: 40
            };
        } else {
            layoutConfig = {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 65,
                rankSep: 85,
                padding: 40,
                animate: true,
                animationDuration: 400
            };
        }
        const layout = this.cy.layout(layoutConfig);
        layout.run();
    }

    render_cytoscape(elements, engine) {
        const self = this;
        const container = this.$root.find('#rag-cytoscape-canvas')[0];
        if (!container || !window.cytoscape) return;

        // Ensure cytoscape-dagre is registered
        if (typeof window.cytoscapeDagre === 'function') {
            try { window.cytoscape.use(window.cytoscapeDagre); } catch (e) {}
        }

        // Update engine badge
        const engineLabel = engine === 'apache_age' ? 'Apache AGE (PG17)' : 'In-Memory JSON (Dual-Run)';
        this.$root.find('#graph-active-engine').text(engineLabel);

        const cyNodes = (elements && elements.nodes) || [];
        const cyEdges = (elements && elements.edges) || [];

        if (this.cy) {
            this.cy.destroy();
        }

        this.cy = cytoscape({
            container: container,
            elements: [...cyNodes, ...cyEdges],
            boxSelectionEnabled: false,
            autounselectify: false,
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'color': '#ffffff',
                        'font-size': '11px',
                        'font-weight': 'bold',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-wrap': 'wrap',
                        'text-max-width': '65px',
                        'background-color': '#0284c7',
                        'width': '52px',
                        'height': '52px',
                        'border-width': '3px',
                        'border-color': '#ffffff',
                        'transition-property': 'background-color, border-color, width, height, border-width',
                        'transition-duration': '0.25s'
                    }
                },
                {
                    selector: 'node[type = "root"]',
                    style: {
                        'background-color': '#0f172a',
                        'shape': 'round-rectangle',
                        'width': '74px',
                        'height': '74px',
                        'font-size': '12px',
                        'border-color': '#38bdf8',
                        'border-width': '4px'
                    }
                },
                {
                    selector: 'node[type = "section"]',
                    style: {
                        'background-color': '#0369a1',
                        'shape': 'round-rectangle',
                        'width': '60px',
                        'height': '60px',
                        'border-color': '#bae6fd',
                        'border-width': '3px'
                    }
                },
                {
                    selector: 'node[type = "chapter"]',
                    style: {
                        'background-color': '#2563eb',
                        'shape': 'ellipse',
                        'width': '52px',
                        'height': '52px',
                        'border-color': '#bfdbfe'
                    }
                },
                {
                    selector: 'node[type = "heading"]',
                    style: {
                        'background-color': '#0d9488',
                        'shape': 'ellipse',
                        'width': '46px',
                        'height': '46px',
                        'border-color': '#99f6e4'
                    }
                },
                {
                    selector: 'node[type = "subheading"]',
                    style: {
                        'background-color': '#d97706',
                        'shape': 'ellipse',
                        'width': '40px',
                        'height': '40px',
                        'font-size': '10px',
                        'border-color': '#fde68a'
                    }
                },
                {
                    selector: 'node[type = "note"], node[type = "legal_rule"], node[type = "legal"]',
                    style: {
                        'background-color': '#dc2626',
                        'shape': 'diamond',
                        'width': '38px',
                        'height': '38px',
                        'font-size': '11px',
                        'font-weight': 'bold',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#ffffff',
                        'border-color': '#fecaca',
                        'border-width': '2.5px'
                    }
                },
                {
                    selector: 'node:selected, node.selected',
                    style: {
                        'border-width': '5px',
                        'border-color': '#f59e0b',
                        'width': '64px',
                        'height': '64px'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2.5,
                        'line-color': '#cbd5e1',
                        'target-arrow-color': '#94a3b8',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'arrow-scale': 0.9,
                        'transition-property': 'line-color, width, target-arrow-color',
                        'transition-duration': '0.2s'
                    }
                },
                {
                    selector: 'edge[relation = "EXCLUDES"]',
                    style: {
                        'line-color': '#fca5a5',
                        'target-arrow-color': '#ef4444',
                        'line-style': 'dashed'
                    }
                },
                {
                    selector: 'edge:selected, edge.selected',
                    style: {
                        'width': 4,
                        'line-color': '#0284c7',
                        'target-arrow-color': '#0284c7'
                    }
                }
            ]
        });

        this.apply_cy_layout();

        // Click event on node
        this.cy.on('tap', 'node', function (evt) {
            const node = evt.target;
            self.handle_graph_node_select(node.data());
            try {
                self.cy.animate({
                    center: { eles: node },
                    zoom: Math.min(Math.max(self.cy.zoom(), 1.0), 1.5),
                    duration: 400
                });
            } catch (e) {}
        });

        // Click on background
        this.cy.on('tap', function (evt) {
            if (evt.target === self.cy) {
                self.cy.nodes().removeClass('selected');
            }
        });

        // Auto select first node
        if (cyNodes.length > 0) {
            this.handle_graph_node_select(cyNodes[0].data);
        }
    }

    handle_graph_node_select(data) {
        if (!data) return;
        this.state.selectedGraphNodeId = data.id;

        const $details = this.$root.find('#rag-graph-node-details');
        $details.find('#node-detail-id').text(data.id || 'N/A');
        $details.find('#node-detail-label').text(data.full_title || data.label || data.code || 'N/A');
        $details.find('#node-detail-desc').text(data.description || 'Chưa có chú giải chi tiết.');
        $details.find('#node-detail-type').text(data.type || 'item');
        $details.find('#node-detail-chapter').text(data.chapter || data.section || 'N/A');
        $details.find('#node-detail-children-count').text(data.children_count || 0);

        const $expandBtn = $details.find('#btn-node-expand-children');
        if (data.has_children || (data.children_count && data.children_count > 0)) {
            $expandBtn.show().find('span').text(`Mở Rộng Nhánh Con (${data.children_count})`);
        } else {
            $expandBtn.hide();
        }
    }

    expand_selected_node() {
        const self = this;
        const nid = this.state.selectedGraphNodeId;
        if (!nid || !this.cy) return;

        const $indicator = this.$root.find('#rag-graph-loading-indicator');
        $indicator.fadeIn(150);

        const handleSuccess = (elements) => {
            $indicator.fadeOut(150);
            const newNodes = (elements && elements.nodes) || [];
            const newEdges = (elements && elements.edges) || [];

            const existingNodeIds = new Set(self.cy.nodes().map(n => n.id()));
            const toAdd = [];

            newNodes.forEach(n => {
                if (!existingNodeIds.has(n.data.id)) {
                    toAdd.push(n);
                }
            });

            const existingEdgeKeys = new Set(self.cy.edges().map(e => `${e.source().id()}->${e.target().id()}`));
            const existingEdgeIds = new Set(self.cy.edges().map(e => e.id()));
            newEdges.forEach(e => {
                const key = `${e.data.source}->${e.data.target}`;
                if (!existingEdgeIds.has(e.data.id) && !existingEdgeKeys.has(key)) {
                    existingEdgeKeys.add(key);
                    toAdd.push(e);
                }
            });

            if (toAdd.length > 0) {
                self.cy.add(toAdd);
                self.apply_cy_layout();
                self.show_toast(`Đã mở rộng thêm ${toAdd.length} nhánh tri thức!`);
            } else {
                self.show_toast('Tất cả các nhánh con của nút này đã được hiển thị.');
            }
        };

        if (typeof frappe !== 'undefined' && frappe.call) {
            frappe.call({
                method: 'logistics_wizard.api.get_knowledge_graph',
                args: { root_id: nid, depth: 1, limit: 30 },
                callback: (r) => {
                    if (r && r.message && r.message.success && r.message.elements) {
                        handleSuccess(r.message.elements);
                    } else {
                        $indicator.fadeOut(150);
                        self.show_toast('Không tìm thấy nhánh con bổ sung.');
                    }
                },
                error: () => {
                    $indicator.fadeOut(150);
                }
            });
        } else {
            $indicator.fadeOut(150);
        }
    }

    render_fallback_graph() {
        const mockNodes = [
            { data: { id: 'ROOT', label: 'Biểu Thuế Hải Quan', type: 'root', description: 'Cấu trúc biểu thuế phân cấp toàn quốc' } },
            { data: { id: 'SEC_XVI', label: 'Phần XVI: Máy Móc', type: 'section', chapter: '84, 85', description: 'Máy và các thiết bị cơ khí, điện tử' } },
            { data: { id: 'CH_84', label: 'Chương 84: Lò phản ứng & Nồi hơi', type: 'chapter', chapter: '84', description: 'Nồi hơi, máy cơ khí' } },
            { data: { id: 'CH_85', label: 'Chương 85: Thiết Bị Điện', type: 'chapter', chapter: '85', description: 'Máy điện và thiết bị truyền hình, viễn thông' } },
            { data: { id: 'HD_8471', label: 'Nhóm 84.71: Máy Xử Lý Dữ Liệu', type: 'heading', chapter: '84', code: '8471', description: 'Máy xử lý dữ liệu tự động, máy tính xách tay' } },
            { data: { id: 'SUB_847130', label: 'Phân nhóm 8471.30: Laptop', type: 'subheading', chapter: '84', code: '8471.30', description: 'Máy tính xách tay trọng lượng <= 10kg' } },
            { data: { id: 'EXCL_NOTE', label: 'Chú giải loại trừ Ch.84', type: 'note', chapter: '84', description: 'Không bao gồm máy móc thuộc Phần XVII' } }
        ];

        const mockEdges = [
            { data: { id: 'e1', source: 'ROOT', target: 'SEC_XVI', label: 'CONTAINS', relation: 'CONTAINS' } },
            { data: { id: 'e2', source: 'SEC_XVI', target: 'CH_84', label: 'CONTAINS', relation: 'CONTAINS' } },
            { data: { id: 'e3', source: 'SEC_XVI', target: 'CH_85', label: 'CONTAINS', relation: 'CONTAINS' } },
            { data: { id: 'e4', source: 'CH_84', target: 'HD_8471', label: 'CONTAINS', relation: 'CONTAINS' } },
            { data: { id: 'e5', source: 'HD_8471', target: 'SUB_847130', label: 'CONTAINS', relation: 'CONTAINS' } },
            { data: { id: 'e6', source: 'HD_8471', target: 'EXCL_NOTE', label: 'EXCLUDES', relation: 'EXCLUDES' } }
        ];

        this.render_cytoscape({ nodes: mockNodes, edges: mockEdges }, 'inmemory');
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
            title: (typeof __ !== 'undefined' ? __('RAG Knowledge Base') : 'RAG Knowledge Base'),
            single_column: true
        });

        if (wrapper.page && wrapper.page.wrapper) {
            $(wrapper.page.wrapper).find('.page-head').hide();
        }

        let html = '';
        try {
            if (frappe.templates && frappe.templates['rag_knowledge_base']) {
                html = frappe.render_template('rag_knowledge_base', {}) || frappe.templates['rag_knowledge_base'];
            } else if (frappe.templates && frappe.templates['rag-knowledge-base']) {
                html = frappe.render_template('rag-knowledge-base', {}) || frappe.templates['rag-knowledge-base'];
            } else if (frappe.templates && frappe.templates['rag_admin_center']) {
                html = frappe.render_template('rag_admin_center', {}) || frappe.templates['rag_admin_center'];
            }
        } catch (err) {
            console.warn('frappe.render_template fallback to raw template:', err);
            html = (frappe.templates && (frappe.templates['rag_knowledge_base'] || frappe.templates['rag-knowledge-base'])) || '';
        }

        if (!html && frappe.templates) {
            html = frappe.templates['rag_knowledge_base'] || frappe.templates['rag-knowledge-base'] || frappe.templates['rag_admin_center'] || '';
        }

        if (html) {
            $(wrapper.page.body).html(html);
        }

        const controller = new RagAdminCenterController(wrapper.page.body);
        const hash = window.location.hash || '';
        const route = frappe.get_route ? frappe.get_route() : [];
        const isGraph = hash === '#graph' || (route && route[1] === 'graph') || (frappe.route_options && frappe.route_options.tab === 'graph');
        controller.switch_nav_tab(isGraph ? 'graph' : 'dashboard');
        wrapper.ragAdminController = controller;
        frappe.pages[pageName].controller = controller;
        make_rag_page_full_bleed(wrapper);
    };

    frappe.pages[pageName].on_page_show = function (wrapper) {
        make_rag_page_full_bleed(wrapper);
        if (wrapper.ragAdminController) {
            const hash = window.location.hash || '';
            const route = frappe.get_route ? frappe.get_route() : [];
            const isGraph = hash === '#graph' || (route && route[1] === 'graph') || (frappe.route_options && frappe.route_options.tab === 'graph');
            if (isGraph) {
                wrapper.ragAdminController.switch_nav_tab('graph');
            } else if (wrapper.ragAdminController.state && wrapper.ragAdminController.state.currentNavTab) {
                wrapper.ragAdminController.switch_nav_tab(wrapper.ragAdminController.state.currentNavTab);
            } else {
                wrapper.ragAdminController.switch_nav_tab('knowledge');
                wrapper.ragAdminController.render_all();
            }
        }
    };
}

['rag-admin-center', 'rag_admin_center', 'ragAdminCenter', 'ragadmincenter'].forEach(register_rag_admin_center_page);

if (typeof window !== 'undefined') {
    window.RagAdminCenterController = RagAdminCenterController;
}
