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
            routePolylines: [],
            markers: [],
            vehicleMarker: null
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
                center: [20.0, 115.0],
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

        // 2. Select initial or preferred shipment
        let allShipments = this.data.shipments || [];
        if (preferredShipment) {
            this.selectedShipment = allShipments.find(s => s.name === preferredShipment) || this.data.selected_shipment || allShipments[0] || null;
        } else if (this.data.selected_shipment) {
            this.selectedShipment = this.data.selected_shipment;
        } else {
            this.selectedShipment = allShipments[0] || null;
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
                self.select_shipment(s.name);
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

    update_map_view(shipment) {
        if (!this.map || !shipment) return;
        const L = window.L || window.leaflet;
        if (!L) return;

        // Clear existing route and markers
        this.clear_map_layers();

        $('#hub-selected-shipment-badge')
            .text(`Lô hàng: ${shipment.name}`)
            .show();

        let coords = [];
        let waypoints = [];

        // Check if full_route coordinates exist
        if (shipment.full_route && shipment.full_route.length > 0) {
            coords = shipment.full_route;
        } else if (shipment.legs && shipment.legs.length > 0) {
            shipment.legs.forEach(leg => {
                if (leg.coordinates && leg.coordinates.length > 0) {
                    coords = coords.concat(leg.coordinates);
                }
            });
        }

        // Fallback default coordinates if empty
        if (coords.length === 0) {
            let lat = parseFloat(shipment.current_lat) || 12.0;
            let lon = parseFloat(shipment.current_lon) || 112.0;
            coords = [
                [31.23, 121.47], // Shanghai / Port of origin
                [lat, lon],
                [10.77, 106.70]  // Cat Lai / Port of destination
            ];
        }

        // Draw Polyline
        let isAir = (shipment.shipping_method === 'Air');
        let polyline = L.polyline(coords, {
            color: isAir ? '#0284c7' : '#0369a1',
            weight: 3.5,
            opacity: 0.85,
            dashArray: isAir ? '6, 8' : null
        }).addTo(this.map);
        this.mapLayers.routePolylines.push(polyline);

        // Origin Marker
        let originMarker = L.circleMarker(coords[0], {
            radius: 7,
            fillColor: '#16a34a',
            color: '#ffffff',
            weight: 2,
            fillOpacity: 0.95
        }).addTo(this.map).bindPopup(`<b>Cảng Xuất:</b> ${shipment.origin_port || 'Origin'}`);
        this.mapLayers.markers.push(originMarker);

        // Destination Marker
        let destMarker = L.circleMarker(coords[coords.length - 1], {
            radius: 7,
            fillColor: '#dc2626',
            color: '#ffffff',
            weight: 2,
            fillOpacity: 0.95
        }).addTo(this.map).bindPopup(`<b>Cảng Đích:</b> ${shipment.destination_port || 'Destination'}`);
        this.mapLayers.markers.push(destMarker);

        // Current Vehicle Marker
        let currentPos = coords[Math.floor(coords.length / 2)];
        if (shipment.current_lat && shipment.current_lon) {
            currentPos = [parseFloat(shipment.current_lat), parseFloat(shipment.current_lon)];
        }

        let vehicleIconHtml = shipment.shipping_method === 'Air' ? '✈️' : (shipment.shipping_method === 'Road' ? '🚚' : '🚢');
        let vehicleIcon = L.divIcon({
            html: `<div style="font-size: 24px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${vehicleIconHtml}</div>`,
            className: 'custom-vehicle-marker-hub',
            iconSize: [28, 28],
            iconAnchor: [14, 14]
        });

        this.mapLayers.vehicleMarker = L.marker(currentPos, { icon: vehicleIcon })
            .addTo(this.map)
            .bindPopup(`
                <div style="font-size: 12px; min-width: 160px;">
                    <div style="font-weight: 700; color: #0284c7;">${shipment.name}</div>
                    <div><b>Phương tiện:</b> ${shipment.carrier || ''}</div>
                    <div><b>Trạng thái:</b> ${shipment.status}</div>
                    ${shipment.delay_days > 0 ? `<div style="color: #dc2626; font-weight: 600;">Delay: +${shipment.delay_days} ngày</div>` : ''}
                </div>
            `);

        // Fit map bounds safely
        try {
            this.map.fitBounds(polyline.getBounds(), { padding: [40, 40] });
        } catch (e) {
            this.map.setView(currentPos, 4);
        }
    }

    clear_map_layers() {
        if (!this.map) return;
        this.mapLayers.routePolylines.forEach(p => this.map.removeLayer(p));
        this.mapLayers.routePolylines = [];

        this.mapLayers.markers.forEach(m => this.map.removeLayer(m));
        this.mapLayers.markers = [];

        if (this.mapLayers.vehicleMarker) {
            this.map.removeLayer(this.mapLayers.vehicleMarker);
            this.mapLayers.vehicleMarker = null;
        }
    }

    reset_map_view() {
        if (!this.map) return;
        this.map.setView([20.0, 115.0], 3);
        $('#hub-selected-shipment-badge').hide();
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
