// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trade Cost Sheet', {
	refresh: function(frm) {
		// Custom status indicator badge
		frm.trigger('update_status_indicator');

		// Action buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('Tính lại Chi phí'), function() {
				frm.trigger('calculate_all');
				frappe.show_alert({
					message: __('Đã tính lại toàn bộ chi phí và tỷ lệ chênh lệch'),
					indicator: 'green'
				});
			}, __('Thao tác'));

			frm.add_custom_button(__('Kiểm toán Chi phí (Audit)'), function() {
				frappe.call({
					method: 'logistics_wizard.costing_engine.api.audit_case_costs',
					args: { case_id: frm.doc.trade_case },
					callback: function(r) {
						if (r && r.message) {
							const res = r.message;
							const errs = res.errors || [];
							const warns = res.warnings || [];
							const combined = errs.concat(warns).join('\n');
							frm.set_value('audit_warnings', combined);
							if (res.passed && warns.length === 0) {
								frappe.msgprint({
									title: __('Kiểm toán Hợp lệ'),
									indicator: 'green',
									message: __('Không phát hiện hóa đơn trùng lặp, sai lệch hồ sơ hoặc thiếu chi phí trọng yếu.')
								});
							} else {
								frappe.msgprint({
									title: res.passed ? __('Cảnh báo Kiểm toán') : __('Phát hiện Lỗi Kiểm toán'),
									indicator: res.passed ? 'orange' : 'red',
									message: '<pre style="white-space: pre-wrap;">' + frappe.utils.escape_html(combined) + '</pre>'
								});
							}
						}
					}
				});
			}, __('Thao tác'));

			if (frm.doc.trade_type === 'Import' && frm.doc.status !== 'Cancelled') {
				frm.add_custom_button(__('Phân bổ & Tạo LCV (ERPNext)'), function() {
					frappe.confirm(
						__('Hệ thống sẽ chạy Custom Cost Allocation Engine ({0}) và đồng bộ sang ERPNext Landed Cost Voucher. Tiếp tục?', [frm.doc.allocation_rule || 'By Value']),
						function() {
							frappe.call({
								method: 'logistics_wizard.costing_engine.api.allocate_and_sync_lcv',
								args: {
									cost_sheet_name: frm.doc.name,
									auto_submit: false
								},
								freeze: true,
								freeze_message: __('Đang tính toán phân bổ giá vốn và đồng bộ LCV...'),
								callback: function(r) {
									if (r && r.message && r.message.success) {
										const res = r.message;
										const rows = (res.allocated_items || []).map(it =>
											`<tr>
												<td><b>${frappe.utils.escape_html(it.item_code || '')}</b></td>
												<td style="text-align:right">${flt(it.qty, 2)}</td>
												<td style="text-align:right">${format_currency(it.base_amount, frm.doc.currency)}</td>
												<td style="text-align:right"><b>${format_currency(it.allocated_charges, frm.doc.currency)}</b></td>
												<td style="text-align:right; color:#0f766e;"><b>${format_currency(it.new_valuation_rate, frm.doc.currency)}</b></td>
											</tr>`
										).join('');
										frappe.msgprint({
											title: __('Đã đồng bộ Landed Cost Voucher: {0}', [res.lcv_name || 'LCV']),
											indicator: 'green',
											message: `
												<p>Đã phân bổ thành công chi phí thực tế cho từng mặt hàng theo quy tắc <b>${frm.doc.allocation_rule}</b>:</p>
												<table class="table table-bordered table-condensed" style="font-size:12px;">
													<thead>
														<tr>
															<th>Mã hàng (Item)</th>
															<th style="text-align:right">SL</th>
															<th style="text-align:right">Trị giá gốc</th>
															<th style="text-align:right">Chi phí phân bổ</th>
															<th style="text-align:right">Giá vốn thực tế / ĐV</th>
														</tr>
													</thead>
													<tbody>${rows}</tbody>
												</table>
											`
										});
										frm.reload_doc();
									} else {
										frappe.msgprint({
											title: __('Không thể tạo LCV'),
											indicator: 'red',
											message: (r && r.message && r.message.error) ? r.message.error : __('Vui lòng kiểm tra chứng từ Purchase Receipt liên kết.')
										});
									}
								}
							});
						}
					);
				}, __('Thao tác'));
			}
		}

		frm.trigger('toggle_export_fields');
	},

	trade_type: function(frm) {
		frm.trigger('toggle_export_fields');
	},

	toggle_export_fields: function(frm) {
		const is_export = frm.doc.trade_type === 'Export';
		frm.toggle_display('section_export_profitability', is_export);
	},

	currency: function(frm) {
		frm.trigger('calculate_all');
	},

	conversion_rate: function(frm) {
		frm.trigger('calculate_all');
	},

	total_purchase_value: function(frm) {
		frm.trigger('calculate_totals');
	},

	export_revenue: function(frm) {
		frm.trigger('calculate_export_profitability');
	},

	export_cogs: function(frm) {
		frm.trigger('calculate_export_profitability');
	},

	calculate_all: function(frm) {
		frm.trigger('calculate_item_bases');
		frm.trigger('calculate_totals');
		frm.trigger('calculate_status_rollups');
		if (frm.doc.trade_type === 'Export') {
			frm.trigger('calculate_export_profitability');
		}
	},

	calculate_item_bases: function(frm) {
		const sheet_rate = flt(frm.doc.conversion_rate) || 1.0;
		(frm.doc.cost_items || []).forEach(row => {
			if (row.status === 'Cancelled') return;

			let rate = flt(row.exchange_rate);
			if (rate <= 0) {
				rate = sheet_rate;
				frappe.model.set_value(row.doctype, row.name, 'exchange_rate', rate);
			}

			const est = flt(row.estimated_cost);
			const act = flt(row.actual_cost);

			const base_est = flt(est * rate, 2);
			const base_act = flt(act * rate, 2);

			frappe.model.set_value(row.doctype, row.name, 'base_estimated_cost', base_est);
			frappe.model.set_value(row.doctype, row.name, 'estimated_amount_base', base_est);
			frappe.model.set_value(row.doctype, row.name, 'base_actual_cost', base_act);
			frappe.model.set_value(row.doctype, row.name, 'actual_amount_base', base_act);

			const var_amt = flt(base_act - base_est, 2);
			let var_pct = 0.0;
			if (base_est > 0) {
				var_pct = flt((var_amt / base_est) * 100.0, 1);
			} else if (base_est === 0 && base_act === 0) {
				var_pct = 0.0;
			} else {
				var_pct = 100.0;
			}

			frappe.model.set_value(row.doctype, row.name, 'variance_amount', var_amt);
			frappe.model.set_value(row.doctype, row.name, 'variance_pct', var_pct);
		});
		frm.refresh_field('cost_items');
	},

	calculate_totals: function(frm) {
		const items = (frm.doc.cost_items || []).filter(r => r.status !== 'Cancelled');

		const total_est = flt(items.reduce((acc, r) => acc + flt(r.base_estimated_cost || 0), 0), 2);
		const total_act = flt(items.reduce((acc, r) => acc + flt(r.base_actual_cost || 0), 0), 2);

		frm.set_value('total_estimated_cost', total_est);
		frm.set_value('total_actual_cost', total_act);

		const purchase_val = flt(frm.doc.total_purchase_value || 0, 2);
		frm.set_value('actual_landed_cost', flt(purchase_val + total_act, 2));

		const var_amt = flt(total_act - total_est, 2);
		frm.set_value('variance_amount', var_amt);

		let var_pct = 0.0;
		if (total_est > 0) {
			var_pct = flt((var_amt / total_est) * 100.0, 1);
		} else if (total_est === 0 && total_act === 0) {
			var_pct = 0.0;
		} else {
			var_pct = 100.0;
		}
		frm.set_value('variance_pct', var_pct);
	},

	calculate_status_rollups: function(frm) {
		const active_items = (frm.doc.cost_items || []).filter(r => r.status !== 'Cancelled');
		const total_inv = active_items.length;
		const rcv_inv = active_items.filter(r => (r.invoice_number || '').trim().length > 0).length;
		const ver_costs = active_items.filter(r => ['Verified', 'Allocated'].includes(r.status)).length;
		const alloc_costs = active_items.filter(r => r.status === 'Allocated').length;

		frm.set_value('invoices_total', total_inv);
		frm.set_value('invoices_received', rcv_inv);
		frm.set_value('costs_verified', ver_costs);
		frm.set_value('costs_allocated', alloc_costs);

		let final_status = 'DRAFT';
		if (total_inv === 0) {
			final_status = 'DRAFT';
		} else if (alloc_costs === total_inv && total_inv > 0) {
			if (['Finalized', 'Submitted'].includes(frm.doc.status) || frm.doc.docstatus === 1) {
				final_status = 'FINALIZED';
			} else {
				final_status = 'ALLOCATED';
			}
		} else if (rcv_inv === total_inv && ver_costs === total_inv && total_inv > 0) {
			final_status = 'ALMOST READY';
		} else if (rcv_inv > 0 || ver_costs > 0 || alloc_costs > 0) {
			final_status = 'IN PROGRESS';
		} else {
			final_status = 'DRAFT';
		}

		frm.set_value('cost_finalization_status', final_status);
		frm.trigger('update_status_indicator');
	},

	calculate_export_profitability: function(frm) {
		const rev = flt(frm.doc.export_revenue || 0);
		const cogs = flt(frm.doc.export_cogs || 0);
		const logistics = flt(frm.doc.total_actual_cost || 0);

		frm.set_value('export_logistics_cost', flt(logistics, 2));

		const gross_margin = flt(rev - cogs, 2);
		frm.set_value('export_gross_margin', gross_margin);
		const gross_pct = rev > 0 ? flt((gross_margin / rev) * 100.0, 2) : 0.0;
		frm.set_value('export_gross_margin_pct', gross_pct);

		const net_profit = flt(rev - cogs - logistics, 2);
		frm.set_value('export_net_profit', net_profit);
		const net_pct = rev > 0 ? flt((net_profit / rev) * 100.0, 2) : 0.0;
		frm.set_value('export_net_margin_pct', net_pct);
	},

	update_status_indicator: function(frm) {
		const status_colors = {
			'DRAFT': 'blue',
			'IN PROGRESS': 'orange',
			'ALMOST READY': 'yellow',
			'ALLOCATED': 'cyan',
			'FINALIZED': 'green'
		};
		const status = frm.doc.cost_finalization_status || 'DRAFT';
		const color = status_colors[status] || 'blue';
		frm.page.set_indicator(status, color);
	}
});

frappe.ui.form.on('Trade Cost Item', {
	cost_type: function(frm, cdt, cdn) {
		frm.trigger('calculate_all');
	},

	estimated_cost: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'estimated_amount', row.estimated_cost);
		frm.trigger('calculate_all');
	},

	estimated_amount: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'estimated_cost', row.estimated_amount);
		frm.trigger('calculate_all');
	},

	actual_cost: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'actual_amount', row.actual_cost);
		frm.trigger('calculate_all');
	},

	actual_amount: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'actual_cost', row.actual_amount);
		frm.trigger('calculate_all');
	},

	exchange_rate: function(frm, cdt, cdn) {
		frm.trigger('calculate_all');
	},

	invoice_number: function(frm, cdt, cdn) {
		frm.trigger('calculate_status_rollups');
	},

	status: function(frm, cdt, cdn) {
		frm.trigger('calculate_all');
	},

	cost_items_remove: function(frm) {
		frm.trigger('calculate_all');
	}
});

frappe.ui.form.on('Trade Cost Document Link', {
	document_type: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (['Purchase Receipt', 'Purchase Invoice'].includes(row.document_type)) {
			frappe.model.set_value(cdt, cdn, 'party_type', 'Supplier');
		} else if (['Sales Order', 'Delivery Note', 'Sales Invoice'].includes(row.document_type)) {
			frappe.model.set_value(cdt, cdn, 'party_type', 'Customer');
		} else {
			frappe.model.set_value(cdt, cdn, 'party_type', '');
			frappe.model.set_value(cdt, cdn, 'party', '');
		}
	}
});
