// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * Logistics Wizard - Shipment Tracking Hub Controller
 * Trang Quản trị Vận chuyển Toàn diện (/app/shipment-tracking-hub)
 * 6 Khối chức năng: KPI Metrics, Bản đồ Toàn cầu, Bảng Lô hàng, Stepper 9 mốc DCSA, Exception Center, Action Toolbar.
 */

frappe.pages['shipment-tracking-hub'].on_page_load = function (wrapper) {
    wrapper.shipment_tracking_hub = new ShipmentTrackingHub(wrapper);
};

frappe.pages['shipment-tracking-hub'].on_page_show = function (wrapper) {
    let focusShipment = null;
    if (frappe.route_options && frappe.route_options.shipment) {
        focusShipment = frappe.route_options.shipment;
        frappe.route_options = null;
    }
    if (wrapper.shipment_tracking_hub) {
        wrapper.shipment_tracking_hub.refresh(focusShipment);
    }
};

class ShipmentTrackingHub {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: __('Shipment Tracking Hub'),
            single_column: true
        });

        this.data = null;
        this.selectedShipment = null;
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

        this.init();
    }

    init() {
        this.render_skeleton();
        this.bind_events();
        this.init_map();
    }

    render_skeleton() {
        // Append HTML template content into main page body
        let template = frappe.render_template('shipment_tracking_hub', {});
        $(this.page.body).html(template);
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

        const mapEl = document.getElementById('lw-hub-map');
        if (!mapEl) return;

        // Initialize Map
        try {
            this.map = L.map('lw-hub-map', {
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
        frappe.call({
            method: 'logistics_wizard.api.get_shipment_tracking_hub_data',
            args: {
                shipment: preferredShipment
            },
            callback: function (r) {
                if (r && r.message) {
                    self.data = r.message;
                    self.render_all(preferredShipment);
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
            let methodIcon = s.shipping_method === 'Air' ? '✈️' : (s.shipping_method === 'Road' ? '🚚' : '🚢');

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
                            ${methodIcon} ${s.name}
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
        let found = (this.data.shipments || []).find(s => s.name === shipmentName);
        if (found) {
            this.selectedShipment = found;
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

            // Determine line styling
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

            // 2. Origin & Destination Micro-Markers
            let startPt = simpCoords[0];
            let endPt = simpCoords[simpCoords.length - 1];

            let originDot = L.circleMarker(startPt, {
                radius: 5,
                color: '#16A34A',
                fillColor: '#FFFFFF',
                fillOpacity: 1,
                weight: 2
            }).addTo(self.map);
            originDot.bindTooltip(`Xuất phát: ${s.origin_port || s.name}`);
            originDot.on('click', () => { self.select_shipment(s.name); });
            self.mapLayers.markers.push(originDot);

            let destDot = L.circleMarker(endPt, {
                radius: 5,
                color: '#DC2626',
                fillColor: '#FFFFFF',
                fillOpacity: 1,
                weight: 2
            }).addTo(self.map);
            destDot.bindTooltip(`Đích đến: ${s.destination_port || s.name}`);
            destDot.on('click', () => { self.select_shipment(s.name); });
            self.mapLayers.markers.push(destDot);

            // 3. Vehicle Marker along route
            let progress = (typeof s.progress === 'number') ? s.progress : 0.55;
            let metrics = self.computePolylineMetrics(simpCoords);
            let posData = self.interpolateAtProgress(simpCoords, metrics, progress);

            let vehBorder = (s.is_delayed == 1) ? '#DC2626' : (isAir ? '#0284c7' : '#0055B3');
            let vehIcon = L.divIcon({
                className: 'custom-fleet-vehicle-icon',
                html: `
                    <div style="background: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.3); border: 2.5px solid ${vehBorder}; cursor: pointer; transition: transform 0.2s;" title="${s.name} - ${s.carrier || ''}">
                        <div style="display: flex; align-items: center; justify-content: center; transform: rotate(${posData.bearing}deg); transform-origin: center center;">
                            ${self.get_vehicle_svg(sMethod)}
                        </div>
                    </div>
                `,
                iconSize: [36, 36],
                iconAnchor: [18, 18]
            });

            let vehMarker = L.marker(posData.point, { icon: vehIcon, zIndexOffset: 500 + idx * 10 }).addTo(self.map);
            vehMarker.bindTooltip(`
                <div style="font-size: 11.5px; line-height: 1.4;">
                    <strong style="color: #0071E3;">${s.name}</strong> (${s.carrier || ''})<br>
                    ${s.origin_port || 'Origin'} ➔ ${s.destination_port || 'Dest'}<br>
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

        // 5. Origin Marker (Kho/Cảng Xuất - O)
        let originCoord = simplifiedCoords[0];
        let originName = (shipment.origin && shipment.origin.name) || shipment.origin_port || 'Kho/Cảng xuất phát';
        let originIcon = L.divIcon({
            className: 'hub-origin-marker-icon',
            html: `<div style="background: #16a34a; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); cursor: pointer;" title="Điểm xuất phát (Origin - Điểm O)">O</div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });
        let originMarker = L.marker(originCoord, { icon: originIcon }).addTo(this.map);
        let dispOriginLon = ((originCoord[1] + 180) % 360 + 360) % 360 - 180;
        originMarker.bindPopup(`<b>Điểm xuất phát (Origin):</b><br>${originName}<br><small>Toạ độ: ${originCoord[0].toFixed(4)}, ${dispOriginLon.toFixed(4)}</small>`);
        this.mapLayers.markers.push(originMarker);

        // 6. Destination Marker (Kho/Cảng Đích - D)
        let destCoord = simplifiedCoords[simplifiedCoords.length - 1];
        let destName = (shipment.destination && shipment.destination.name) || shipment.destination_port || 'Kho/Cảng đích đến';
        let destIcon = L.divIcon({
            className: 'hub-dest-marker-icon',
            html: `<div style="background: #dc2626; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); cursor: pointer;" title="Điểm đích đến (Destination - Điểm D)">D</div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });
        let destMarker = L.marker(destCoord, { icon: destIcon }).addTo(this.map);
        let dispDestLon = ((destCoord[1] + 180) % 360 + 360) % 360 - 180;
        destMarker.bindPopup(`<b>Điểm đích đến (Destination):</b><br>${destName}<br><small>Toạ độ: ${destCoord[0].toFixed(4)}, ${dispDestLon.toFixed(4)}</small>`);
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
        let routeMetrics = this.computePolylineMetrics(simplifiedCoords);
        let startPosData = this.interpolateAtProgress(simplifiedCoords, routeMetrics, 0);

        let vehicleBorderColor = sMethod === 'Air' ? '#007AFF' : (sMethod === 'Ocean' ? '#0055B3' : '#FF9500');
        let vehicleIcon = L.divIcon({
            className: 'custom-vehicle-icon-hub',
            html: `
                <div class="lw-vehicle-box" style="background: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.3); border: 2.8px solid ${vehicleBorderColor};">
                    <div class="lw-vehicle-icon-svg" style="display: flex; align-items: center; justify-content: center; transform: rotate(${startPosData.bearing}deg); transform-origin: center center;">
                        ${this.get_vehicle_svg(sMethod)}
                    </div>
                </div>
            `,
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });

        this.mapLayers.vehicleMarker = L.marker(startPosData.point, { icon: vehicleIcon, zIndexOffset: 1000 }).addTo(this.map);
        this.mapLayers.vehicleMarker._currentProgress = 0;

        let delayBadge = (shipment.delay_days > 0)
            ? `<div style="color: #dc2626; font-weight: 700; margin-top: 4px;">⚠️ Lệch ETA: +${shipment.delay_days} ngày</div>`
            : `<div style="color: #16a34a; font-weight: 600; margin-top: 4px;">✅ Hành trình đúng tiến độ</div>`;

        this.mapLayers.vehicleMarker.bindPopup(`
            <div style="font-size: 12px; min-width: 190px; line-height: 1.5;">
                <div style="font-weight: 700; color: #0284c7; font-size: 13px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; margin-bottom: 4px;">
                    ${shipment.name}
                </div>
                <div><b>Phương tiện:</b> ${shipment.carrier || ''} (${shipment.vessel_name || shipment.flight_number || 'Vận tải quốc tế'})</div>
                <div><b>Mã Container:</b> ${shipment.container_id || 'N/A'}</div>
                <div><b>Trạng thái:</b> ${shipment.status}</div>
                <div><b>Lộ trình:</b> ${shipment.origin_port || 'Origin'} ➔ ${shipment.destination_port || 'Dest'}</div>
                ${delayBadge}
            </div>
        `);

        // Trigger Smooth Animation to current progress
        this.animateVehicle(this.mapLayers.vehicleMarker, simplifiedCoords, targetProgress, 1600, sMethod);

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
