import sys

try:
    import frappe
    from frappe import _
except ImportError:
    import types
    class MockFrappeDB:
        def exists(self, doctype, name=None):
            return False
        def get_value(self, doctype, filters=None, fieldname=None, as_dict=False):
            return None
        def has_column(self, doctype, column):
            return False
        def sql(self, *args, **kwargs):
            return []
        def get_all(self, *args, **kwargs):
            return []

    mock_frappe = types.ModuleType("frappe")
    mock_frappe.db = MockFrappeDB()
    mock_frappe.whitelist = lambda *args, **kwargs: (lambda fn: fn)
    mock_frappe._ = lambda msg, *args, **kwargs: msg
    sys.modules["frappe"] = mock_frappe
    frappe = mock_frappe
    _ = mock_frappe._

# 1. IMPORT WORKFLOW (Quy trình Nhập khẩu - 7 bước)
IMPORT_WORKFLOW_STEPS = [
    {
        "step": 1,
        "doctype": "Material Request",
        "label": "1. Yêu cầu mua hàng (Material Request)",
        "slug": "material-request",
    },
    {
        "step": 2,
        "doctype": "Purchase Order",
        "label": "2. Đơn đặt hàng (Purchase Order)",
        "slug": "purchase-order",
    },
    {
        "step": 3,
        "doctype": "Payment Entry",
        "label": "3. Đặt cọc / Tạm ứng (Payment Entry)",
        "slug": "payment-entry",
    },
    {
        "step": 4,
        "doctype": "Shipment Tracking",
        "label": "4. Theo dõi hành trình (Shipment Tracking)",
        "slug": "managementLogistic",
    },
    {
        "step": 5,
        "doctype": "Purchase Receipt",
        "label": "5. Nhận hàng (Purchase Receipt)",
        "slug": "purchase-receipt",
    },
    {
        "step": 6,
        "doctype": "Landed Cost Voucher",
        "label": "6. Phân bổ giá vốn (Landed Cost)",
        "slug": "landed-cost-voucher",
    },
    {
        "step": 7,
        "doctype": "Stock Entry",
        "label": "7. Nhập kho (Stock Entry)",
        "slug": "stock-entry",
    },
]

# 2. EXPORT WORKFLOW (Quy trình Xuất khẩu - 7 bước)
EXPORT_WORKFLOW_STEPS = [
    {
        "step": 1,
        "doctype": "Sales Order",
        "label": "1. Đơn bán hàng (Sales Order)",
        "slug": "sales-order",
    },
    {
        "step": 2,
        "doctype": "Payment Entry",
        "label": "2. Thu tiền cọc (Payment Entry)",
        "slug": "payment-entry",
    },
    {
        "step": 3,
        "doctype": "Stock Entry",
        "label": "3. Chuyển kho cảng (Stock Entry)",
        "slug": "stock-entry",
    },
    {
        "step": 4,
        "doctype": "Delivery Note",
        "label": "4. Xuất kho giao hàng (Delivery Note)",
        "slug": "delivery-note",
    },
    {
        "step": 5,
        "doctype": "Shipment Tracking",
        "label": "5. Theo dõi hành trình (Shipment Tracking)",
        "slug": "managementLogistic",
    },
    {
        "step": 6,
        "doctype": "Sales Invoice",
        "label": "6. Hóa đơn thương mại (Sales Invoice)",
        "slug": "sales-invoice",
    },
    {
        "step": 7,
        "doctype": "Payment Entry",
        "label": "7. Tất toán ngoại tệ (Payment Entry)",
        "slug": "payment-entry",
    },
]

# Backward compatibility alias
WORKFLOW_STEPS = IMPORT_WORKFLOW_STEPS


def detect_workflow_flow_type(doctype, docname=None):
    """
    Tự động nhận diện chứng từ hiện tại thuộc luồng 'import' hay 'export'.
    """
    if not doctype:
        return "import"

    import_doctypes = {"Material Request", "Purchase Order", "Purchase Receipt", "Landed Cost Voucher"}
    export_doctypes = {"Sales Order", "Delivery Note", "Sales Invoice"}

    if doctype in import_doctypes:
        return "import"
    if doctype in export_doctypes:
        return "export"

    # Xử lý các DocType dùng chung cả 2 luồng: Shipment Tracking, Payment Entry, Stock Entry
    if doctype == "Shipment Tracking" and docname:
        if frappe.db.has_column("Shipment Tracking", "flow_type"):
            ft = frappe.db.get_value("Shipment Tracking", docname, "flow_type")
            if ft and str(ft).lower() == "export":
                return "export"
            elif ft and str(ft).lower() == "import":
                return "import"
        if frappe.db.has_column("Shipment Tracking", "sales_order"):
            so = frappe.db.get_value("Shipment Tracking", docname, "sales_order")
            if so:
                return "export"
        if frappe.db.has_column("Shipment Tracking", "purchase_order"):
            po = frappe.db.get_value("Shipment Tracking", docname, "purchase_order")
            if po:
                return "import"

    if doctype == "Payment Entry" and docname:
        try:
            ref = frappe.db.sql("""
                SELECT reference_doctype FROM `tabPayment Entry Reference`
                WHERE parent = %s AND docstatus != 2 LIMIT 1
            """, (docname,))
            if ref and ref[0][0]:
                ref_dt = ref[0][0]
                if ref_dt in ("Sales Order", "Sales Invoice"):
                    return "export"
                elif ref_dt in ("Purchase Order", "Purchase Invoice"):
                    return "import"
        except Exception:
            pass

        if frappe.db.has_column("Payment Entry", "payment_type"):
            ptype = frappe.db.get_value("Payment Entry", docname, "payment_type")
            if ptype == "Receive":
                return "export"
            elif ptype == "Pay":
                return "import"

    if doctype == "Stock Entry" and docname:
        try:
            so = frappe.db.get_value(
                "Stock Entry Detail",
                {"parent": docname, "against_sales_order": ["is", "set"]},
                "against_sales_order"
            )
            if so:
                return "export"
        except Exception:
            pass

        if frappe.db.has_column("Stock Entry", "reference_no"):
            ref_no = frappe.db.get_value("Stock Entry", docname, "reference_no")
            if ref_no and frappe.db.exists("Sales Order", ref_no):
                return "export"

        ste_pr, ste_po, ste_mr = _get_links_from_ste(docname)
        if ste_pr or ste_po or ste_mr:
            return "import"

    return "import"


@frappe.whitelist(allow_guest=True)
def get_workflow_chain_status(doctype=None, docname=None, flow_type=None):
    """
    Điểm truy cập trung tâm trả về chuỗi 7 bước trạng thái luồng Nhập khẩu hoặc Xuất khẩu.
    Hỗ trợ tham số flow_type: 'import', 'export', hoặc None (tự động nhận diện).
    """
    if not doctype or not docname or not isinstance(doctype, str) or not isinstance(docname, str):
        return {
            "success": False,
            "error": _("Thiếu thông tin doctype hoặc docname hợp lệ"),
            "steps": [],
        }

    doctype = doctype.strip()
    docname = docname.strip()
    if not doctype or not docname:
        return {
            "success": False,
            "error": _("Thiếu thông tin doctype hoặc docname hợp lệ"),
            "steps": [],
        }

    # Xác định loại luồng
    target_flow = flow_type.strip().lower() if flow_type and isinstance(flow_type, str) else None
    if not target_flow:
        target_flow = detect_workflow_flow_type(doctype, docname)

    if target_flow == "export":
        res = get_export_workflow_chain_status(doctype, docname)
        res["flow_type"] = "export"
        return res
    else:
        res = get_import_workflow_chain_status(doctype, docname)
        res["flow_type"] = "import"
        return res


def get_import_workflow_chain_status(doctype=None, docname=None):
    """
    Duyệt 7 bước chuỗi chứng từ Nhập khẩu:
    Material Request <-> Purchase Order <-> Payment Entry (Cọc) <-> Shipment Tracking <-> Purchase Receipt <-> Landed Cost Voucher <-> Stock Entry
    """
    chain = {s["doctype"]: None for s in IMPORT_WORKFLOW_STEPS}
    if doctype in chain:
        chain[doctype] = docname

    # 0. Traversal from/to Payment Entry
    if chain.get("Payment Entry") and not chain.get("Purchase Order"):
        chain["Purchase Order"] = _get_po_from_pe(chain["Payment Entry"])

    # 1. Traversal from/to Stock Entry
    if chain["Stock Entry"]:
        ste_pr, ste_po, ste_mr = _get_links_from_ste(chain["Stock Entry"])
        if ste_pr and not chain["Purchase Receipt"]:
            chain["Purchase Receipt"] = ste_pr
        if ste_po and not chain["Purchase Order"]:
            chain["Purchase Order"] = ste_po
        if ste_mr and not chain["Material Request"]:
            chain["Material Request"] = ste_mr

    # 2. Traversal from/to Landed Cost Voucher
    if chain["Landed Cost Voucher"] and not chain["Purchase Receipt"]:
        chain["Purchase Receipt"] = _get_pr_from_lcv(chain["Landed Cost Voucher"])

    # 3. Traversal from/to Shipment Tracking
    if chain["Shipment Tracking"]:
        st_po, st_pr = _get_links_from_st(chain["Shipment Tracking"])
        if st_po and not chain["Purchase Order"]:
            chain["Purchase Order"] = st_po
        if st_pr and not chain["Purchase Receipt"]:
            chain["Purchase Receipt"] = st_pr

    # 4. Traversal between Purchase Receipt and Purchase Order
    if chain["Purchase Receipt"] and not chain["Purchase Order"]:
        chain["Purchase Order"] = _get_po_from_pr(chain["Purchase Receipt"])
    elif chain["Purchase Order"] and not chain["Purchase Receipt"]:
        chain["Purchase Receipt"] = _get_pr_from_po(chain["Purchase Order"])

    # 5. Traversal between Purchase Order and Material Request
    if chain["Purchase Order"] and not chain["Material Request"]:
        chain["Material Request"] = _get_mr_from_po(chain["Purchase Order"])
    elif chain["Material Request"] and not chain["Purchase Order"]:
        chain["Purchase Order"] = _get_po_from_mr(chain["Material Request"])

    # 6. Secondary resolution for Material Request via Purchase Receipt if still missing
    if not chain["Material Request"] and chain["Purchase Receipt"]:
        chain["Material Request"] = _get_mr_from_pr(chain["Purchase Receipt"])
    elif not chain["Purchase Receipt"] and chain["Material Request"]:
        chain["Purchase Receipt"] = _get_pr_from_mr(chain["Material Request"])

    # 7. Secondary resolution for Payment Entry via Purchase Order
    if not chain.get("Payment Entry") and chain.get("Purchase Order"):
        chain["Payment Entry"] = _get_pe_from_po(chain["Purchase Order"])

    # 8. Secondary resolution for Landed Cost Voucher via Purchase Receipt
    if not chain["Landed Cost Voucher"] and chain["Purchase Receipt"]:
        chain["Landed Cost Voucher"] = _get_lcv_from_pr(chain["Purchase Receipt"])

    # 9. Secondary resolution for Stock Entry
    if not chain["Stock Entry"]:
        chain["Stock Entry"] = _get_ste_from_chain(
            chain["Purchase Receipt"],
            chain["Purchase Order"],
            chain["Material Request"],
        )

    # 10. Secondary resolution for Shipment Tracking
    if not chain["Shipment Tracking"]:
        chain["Shipment Tracking"] = _get_shipment_tracking(
            chain["Purchase Order"], chain["Purchase Receipt"]
        )

    # Compile result steps
    steps = []
    current_index = -1
    for idx, step_cfg in enumerate(IMPORT_WORKFLOW_STEPS):
        d_type = step_cfg["doctype"]
        d_name = chain.get(d_type)
        status_info = _get_doc_status_info(d_type, d_name) if d_name else None

        is_current = (d_type == doctype and d_name == docname)
        if is_current:
            current_index = idx

        steps.append(
            {
                "step": step_cfg["step"],
                "doctype": d_type,
                "label": step_cfg["label"],
                "slug": step_cfg["slug"],
                "docname": d_name,
                "docstatus": status_info["docstatus"] if status_info else None,
                "status": status_info["status"] if status_info else "Chưa tạo",
                "completed": status_info["completed"] if status_info else False,
                "url": f"/app/{step_cfg['slug']}/{d_name}" if d_name else f"/app/{step_cfg['slug']}",
                "is_current": is_current,
            }
        )

    # If current doc was found in chain, mark preceding completed steps accordingly
    if current_index != -1:
        for i in range(current_index):
            if steps[i]["docname"] and steps[i]["docstatus"] == 1:
                steps[i]["completed"] = True

    return {"success": True, "steps": steps}


def get_export_workflow_chain_status(doctype=None, docname=None):
    """
    Duyệt 7 bước chuỗi chứng từ Xuất khẩu 2 chiều:
    1. Sales Order
    2. Payment Entry (Thu cọc 30%)
    3. Stock Entry (Chuyển kho ra cảng)
    4. Delivery Note (Xuất kho giao hàng)
    5. Shipment Tracking (Hải trình xuất khẩu Cát Lái -> Cảng quốc tế)
    6. Sales Invoice (Hóa đơn thương mại Commercial Invoice)
    7. Payment Entry (Tất toán ngoại tệ 70%)
    """
    # Khởi tạo chuỗi liên kết rỗng
    chain = {
        "Sales Order": None,
        "Payment Entry (Deposit)": None,
        "Stock Entry": None,
        "Delivery Note": None,
        "Shipment Tracking": None,
        "Sales Invoice": None,
        "Payment Entry (Final)": None,
    }

    current_step_name = None

    # Phân tích chứng từ đầu vào để tìm Sales Order làm hạt nhân liên kết
    if doctype == "Sales Order":
        chain["Sales Order"] = docname
        current_step_name = "Sales Order"

    elif doctype == "Payment Entry":
        so_name = _get_so_from_pe(docname)
        sinv_name = _get_sinv_from_pe(docname)

        if so_name:
            chain["Payment Entry (Deposit)"] = docname
            chain["Sales Order"] = so_name
            current_step_name = "Payment Entry (Deposit)"
        elif sinv_name:
            chain["Payment Entry (Final)"] = docname
            chain["Sales Invoice"] = sinv_name
            chain["Sales Order"] = _get_so_from_sinv(sinv_name)
            current_step_name = "Payment Entry (Final)"
        else:
            # Fallback nếu không gắn reference trực tiếp
            chain["Payment Entry (Deposit)"] = docname
            current_step_name = "Payment Entry (Deposit)"

    elif doctype == "Stock Entry":
        chain["Stock Entry"] = docname
        chain["Sales Order"] = _get_so_from_ste(docname)
        current_step_name = "Stock Entry"

    elif doctype == "Delivery Note":
        chain["Delivery Note"] = docname
        chain["Sales Order"] = _get_so_from_dn(docname)
        current_step_name = "Delivery Note"

    elif doctype == "Shipment Tracking":
        chain["Shipment Tracking"] = docname
        so_from_st, dn_from_st = _get_links_from_export_st(docname)
        if so_from_st:
            chain["Sales Order"] = so_from_st
        if dn_from_st:
            chain["Delivery Note"] = dn_from_st
            if not chain["Sales Order"]:
                chain["Sales Order"] = _get_so_from_dn(dn_from_st)
        current_step_name = "Shipment Tracking"

    elif doctype == "Sales Invoice":
        chain["Sales Invoice"] = docname
        chain["Sales Order"] = _get_so_from_sinv(docname)
        dn_from_sinv = _get_dn_from_sinv(docname)
        if dn_from_sinv and not chain["Delivery Note"]:
            chain["Delivery Note"] = dn_from_sinv
        current_step_name = "Sales Invoice"

    # Khi đã có Sales Order (hoặc từ các mắt xích khác), suy luận 2 chiều toàn bộ chuỗi
    so = chain["Sales Order"]
    if so:
        # Bước 2: Payment Entry (Cọc 30%)
        if not chain["Payment Entry (Deposit)"]:
            chain["Payment Entry (Deposit)"] = _get_pe_deposit_from_so(so)

        # Bước 3: Stock Entry (Chuyển cảng)
        if not chain["Stock Entry"]:
            chain["Stock Entry"] = _get_ste_from_so(so)

        # Bước 4: Delivery Note
        if not chain["Delivery Note"]:
            chain["Delivery Note"] = _get_dn_from_so(so)

        # Bước 5: Shipment Tracking
        if not chain["Shipment Tracking"]:
            chain["Shipment Tracking"] = _get_st_for_export(so, chain["Delivery Note"])

        # Bước 6: Sales Invoice
        if not chain["Sales Invoice"]:
            chain["Sales Invoice"] = _get_sinv_from_so(so, chain["Delivery Note"])

        # Bước 7: Payment Entry (Tất toán 70%)
        if not chain["Payment Entry (Final)"] and chain["Sales Invoice"]:
            chain["Payment Entry (Final)"] = _get_pe_final_from_sinv(chain["Sales Invoice"])

    # Xây dựng danh sách 7 bước trả về giao diện
    step_key_mapping = [
        ("Sales Order", "Sales Order"),
        ("Payment Entry", "Payment Entry (Deposit)"),
        ("Stock Entry", "Stock Entry"),
        ("Delivery Note", "Delivery Note"),
        ("Shipment Tracking", "Shipment Tracking"),
        ("Sales Invoice", "Sales Invoice"),
        ("Payment Entry", "Payment Entry (Final)"),
    ]

    steps = []
    current_index = -1

    for idx, step_cfg in enumerate(EXPORT_WORKFLOW_STEPS):
        d_type = step_cfg["doctype"]
        chain_key = step_key_mapping[idx][1]
        d_name = chain.get(chain_key)

        status_info = _get_doc_status_info(d_type, d_name) if d_name else None

        is_current = (chain_key == current_step_name) or (d_type == doctype and d_name == docname)
        if is_current:
            current_index = idx

        steps.append(
            {
                "step": step_cfg["step"],
                "doctype": d_type,
                "label": step_cfg["label"],
                "slug": step_cfg["slug"],
                "docname": d_name,
                "docstatus": status_info["docstatus"] if status_info else None,
                "status": status_info["status"] if status_info else "Chưa tạo",
                "completed": status_info["completed"] if status_info else False,
                "url": f"/app/{step_cfg['slug']}/{d_name}" if d_name else f"/app/{step_cfg['slug']}",
                "is_current": is_current,
            }
        )

    # Đánh dấu hoàn thành các bước trước đó nếu đã submit
    if current_index != -1:
        for i in range(current_index):
            if steps[i]["docname"] and steps[i]["docstatus"] == 1:
                steps[i]["completed"] = True

    return {"success": True, "steps": steps}


# ==============================================================================
# EXPORT TRAVERSAL HELPER FUNCTIONS (Truy vấn liên kết 2 chiều chuỗi Xuất khẩu)
# ==============================================================================

def _get_so_from_pe(pe_name):
    """Lấy Sales Order từ Payment Entry tham chiếu trực tiếp Sales Order"""
    if not pe_name:
        return None
    try:
        so = frappe.db.sql("""
            SELECT reference_name FROM `tabPayment Entry Reference`
            WHERE parent = %s AND reference_doctype = 'Sales Order' AND docstatus != 2
            LIMIT 1
        """, (pe_name,))
        if so and so[0][0]:
            return so[0][0]
    except Exception:
        pass
    return None


def _get_sinv_from_pe(pe_name):
    """Lấy Sales Invoice từ Payment Entry tham chiếu Sales Invoice"""
    if not pe_name:
        return None
    try:
        sinv = frappe.db.sql("""
            SELECT reference_name FROM `tabPayment Entry Reference`
            WHERE parent = %s AND reference_doctype = 'Sales Invoice' AND docstatus != 2
            LIMIT 1
        """, (pe_name,))
        if sinv and sinv[0][0]:
            return sinv[0][0]
    except Exception:
        pass
    return None


def _get_so_from_ste(ste_name):
    """Lấy Sales Order từ Stock Entry (chuyển kho ra cảng)"""
    if not ste_name:
        return None
    try:
        # 1. Tìm qua delivery_note_no
        if frappe.db.has_column("Stock Entry", "delivery_note_no"):
            dn = frappe.db.get_value("Stock Entry", ste_name, "delivery_note_no")
            if dn:
                so = _get_so_from_dn(dn)
                if so:
                    return so

        # 2. Tìm qua remarks chứa Sales Order
        remarks = frappe.db.get_value("Stock Entry", ste_name, "remarks")
        if remarks:
            so_list = frappe.db.get_all("Sales Order", filters={"docstatus": ["!=", 2]}, pluck="name")
            for cand in so_list:
                if cand in remarks:
                    return cand

        # 3. Tìm qua Custom Field sales_order nếu có
        if frappe.db.has_column("Stock Entry", "sales_order"):
            so = frappe.db.get_value("Stock Entry", ste_name, "sales_order")
            if so:
                return so
    except Exception:
        pass
    return None


def _get_so_from_dn(dn_name):
    """Lấy Sales Order từ Delivery Note Item"""
    if not dn_name:
        return None
    try:
        so = frappe.db.get_value(
            "Delivery Note Item",
            {"parent": dn_name, "against_sales_order": ["is", "set"], "docstatus": ["!=", 2]},
            "against_sales_order",
        )
        if so:
            return so
    except Exception:
        pass
    return None


def _get_so_from_sinv(sinv_name):
    """Lấy Sales Order từ Sales Invoice Item"""
    if not sinv_name:
        return None
    try:
        so = frappe.db.get_value(
            "Sales Invoice Item",
            {"parent": sinv_name, "sales_order": ["is", "set"], "docstatus": ["!=", 2]},
            "sales_order",
        )
        if so:
            return so
    except Exception:
        pass
    return None


def _get_dn_from_sinv(sinv_name):
    """Lấy Delivery Note từ Sales Invoice Item"""
    if not sinv_name:
        return None
    try:
        dn = frappe.db.get_value(
            "Sales Invoice Item",
            {"parent": sinv_name, "delivery_note": ["is", "set"], "docstatus": ["!=", 2]},
            "delivery_note",
        )
        if dn:
            return dn
    except Exception:
        pass
    return None


def _get_links_from_export_st(st_name):
    """Lấy Sales Order và Delivery Note từ Shipment Tracking"""
    st_so, st_dn = None, None
    if not st_name or not frappe.db.exists("DocType", "Shipment Tracking"):
        return None, None

    try:
        if frappe.db.has_column("Shipment Tracking", "sales_order"):
            st_so = frappe.db.get_value("Shipment Tracking", st_name, "sales_order")
        if frappe.db.has_column("Shipment Tracking", "delivery_note"):
            st_dn = frappe.db.get_value("Shipment Tracking", st_name, "delivery_note")

        # Naming convention fallback: ST-{SO} hoặc SHIP-TRACK-{SO}
        if not st_so:
            for prefix in ("ST-", "SHIP-TRACK-"):
                if st_name.startswith(prefix):
                    cand = st_name.replace(prefix, "")
                    if frappe.db.exists("Sales Order", cand):
                        st_so = cand
                        break
                    elif frappe.db.exists("Delivery Note", cand):
                        st_dn = cand
                        break
    except Exception:
        pass

    return st_so, st_dn


def _get_pe_deposit_from_so(so_name):
    """Tìm Payment Entry đặt cọc (Bước 2) liên kết Sales Order"""
    if not so_name:
        return None
    try:
        pe = frappe.db.sql("""
            SELECT parent FROM `tabPayment Entry Reference`
            WHERE reference_doctype = 'Sales Order' AND reference_name = %s AND docstatus != 2
            ORDER BY creation ASC LIMIT 1
        """, (so_name,))
        if pe and pe[0][0]:
            return pe[0][0]
    except Exception:
        pass
    return None


def _get_ste_from_so(so_name):
    """Tìm Stock Entry (Bước 3) chuyển hàng ra cảng theo Sales Order"""
    if not so_name:
        return None
    try:
        # 1. Tìm qua delivery_note_no của Stock Entry (thông qua Delivery Note của SO)
        dn_names = frappe.db.get_all(
            "Delivery Note Item",
            filters={"against_sales_order": so_name, "docstatus": ["!=", 2]},
            pluck="parent",
            distinct=True
        )
        if dn_names:
            ste = frappe.db.get_value(
                "Stock Entry",
                {"delivery_note_no": ["in", dn_names], "docstatus": ["!=", 2]},
                "name"
            )
            if ste:
                return ste

        # 2. Tìm qua remarks chứa SO name
        ste = frappe.db.sql("""
            SELECT name FROM `tabStock Entry`
            WHERE remarks LIKE %s AND docstatus != 2
            ORDER BY creation DESC LIMIT 1
        """, (f"%{so_name}%",))
        if ste and ste[0][0]:
            return ste[0][0]

        # 3. Tìm qua Custom Field sales_order nếu có
        if frappe.db.has_column("Stock Entry", "sales_order"):
            ste = frappe.db.get_value("Stock Entry", {"sales_order": so_name, "docstatus": ["!=", 2]}, "name")
            if ste:
                return ste

        # 4. Tìm qua Stock Entry Detail
        if frappe.db.has_column("Stock Entry Detail", "against_sales_order"):
            ste = frappe.db.get_value(
                "Stock Entry Detail",
                {"against_sales_order": so_name, "docstatus": ["!=", 2]},
                "parent",
            )
            if ste:
                return ste
    except Exception:
        pass
    return None


def _get_dn_from_so(so_name):
    """Tìm Delivery Note (Bước 4) xuất kho giao hàng theo Sales Order"""
    if not so_name:
        return None
    try:
        dn = frappe.db.get_value(
            "Delivery Note Item",
            {"against_sales_order": so_name, "docstatus": ["!=", 2]},
            "parent",
        )
        if dn:
            return dn
    except Exception:
        pass
    return None


def _get_st_for_export(so_name, dn_name=None):
    """Tìm Shipment Tracking (Bước 5) theo Sales Order hoặc Delivery Note"""
    if not frappe.db.exists("DocType", "Shipment Tracking"):
        return None

    try:
        # 1. Tìm theo sales_order field
        if so_name and frappe.db.has_column("Shipment Tracking", "sales_order"):
            st = frappe.db.get_value(
                "Shipment Tracking",
                {"sales_order": so_name, "docstatus": ["!=", 2]},
                "name",
            )
            if st:
                return st

        # 2. Tìm theo delivery_note field
        if dn_name and frappe.db.has_column("Shipment Tracking", "delivery_note"):
            st = frappe.db.get_value(
                "Shipment Tracking",
                {"delivery_note": dn_name, "docstatus": ["!=", 2]},
                "name",
            )
            if st:
                return st

        # 3. Naming convention: ST-{so_name}
        if so_name:
            candidates = [f"ST-{so_name}", f"SHIP-TRACK-{so_name}"]
            for cand in candidates:
                if frappe.db.exists("Shipment Tracking", cand):
                    return cand
    except Exception:
        pass

    return None


def _get_sinv_from_so(so_name, dn_name=None):
    """Tìm Sales Invoice (Bước 6) theo Sales Order hoặc Delivery Note"""
    try:
        if so_name:
            sinv = frappe.db.get_value(
                "Sales Invoice Item",
                {"sales_order": so_name, "docstatus": ["!=", 2]},
                "parent",
            )
            if sinv:
                return sinv

        if dn_name:
            sinv = frappe.db.get_value(
                "Sales Invoice Item",
                {"delivery_note": dn_name, "docstatus": ["!=", 2]},
                "parent",
            )
            if sinv:
                return sinv
    except Exception:
        pass
    return None


def _get_pe_final_from_sinv(sinv_name):
    """Tìm Payment Entry (Bước 7 - Tất toán ngoại tệ) theo Sales Invoice"""
    if not sinv_name:
        return None
    try:
        pe = frappe.db.sql("""
            SELECT parent FROM `tabPayment Entry Reference`
            WHERE reference_doctype = 'Sales Invoice' AND reference_name = %s AND docstatus != 2
            ORDER BY creation DESC LIMIT 1
        """, (sinv_name,))
        if pe and pe[0][0]:
            return pe[0][0]
    except Exception:
        pass
    return None


# ==============================================================================
# IMPORT TRAVERSAL HELPER FUNCTIONS (Kế thừa từ quy trình Nhập khẩu)
# ==============================================================================

def _get_mr_from_po(po_name):
    mr = frappe.db.get_value(
        "Purchase Order Item",
        {"parent": po_name, "material_request": ["is", "set"]},
        "material_request",
    )
    if not mr:
        records = frappe.get_all(
            "Purchase Order Item",
            filters={"parent": po_name},
            fields=["material_request"],
            limit=1,
        )
        if records and records[0].material_request:
            mr = records[0].material_request
    return mr


def _get_po_from_mr(mr_name):
    return frappe.db.get_value(
        "Purchase Order Item",
        {"material_request": mr_name, "docstatus": ["!=", 2]},
        "parent",
    )


def _get_pr_from_po(po_name):
    return frappe.db.get_value(
        "Purchase Receipt Item",
        {"purchase_order": po_name, "docstatus": ["!=", 2]},
        "parent",
    )


def _get_po_from_pr(pr_name):
    po = frappe.db.get_value(
        "Purchase Receipt Item",
        {"parent": pr_name, "purchase_order": ["is", "set"]},
        "purchase_order",
    )
    if not po:
        records = frappe.get_all(
            "Purchase Receipt Item",
            filters={"parent": pr_name},
            fields=["purchase_order"],
            limit=1,
        )
        if records and records[0].purchase_order:
            po = records[0].purchase_order
    return po


def _get_mr_from_pr(pr_name):
    mr = frappe.db.get_value(
        "Purchase Receipt Item",
        {"parent": pr_name, "material_request": ["is", "set"]},
        "material_request",
    )
    if not mr:
        records = frappe.get_all(
            "Purchase Receipt Item",
            filters={"parent": pr_name},
            fields=["material_request"],
            limit=1,
        )
        if records and records[0].material_request:
            mr = records[0].material_request
    return mr


def _get_pr_from_mr(mr_name):
    return frappe.db.get_value(
        "Purchase Receipt Item",
        {"material_request": mr_name, "docstatus": ["!=", 2]},
        "parent",
    )


def _get_lcv_from_pr(pr_name):
    return frappe.db.get_value(
        "Landed Cost Purchase Receipt",
        {"receipt_document": pr_name, "docstatus": ["!=", 2]},
        "parent",
    )


def _get_pr_from_lcv(lcv_name):
    return frappe.db.get_value(
        "Landed Cost Purchase Receipt",
        {
            "parent": lcv_name,
            "receipt_document_type": "Purchase Receipt",
            "docstatus": ["!=", 2],
        },
        "receipt_document",
    )


def _get_ste_from_chain(pr_name, po_name, mr_name):
    if pr_name and frappe.db.has_column("Stock Entry", "purchase_receipt_no"):
        ste = frappe.db.get_value(
            "Stock Entry",
            {"purchase_receipt_no": pr_name, "docstatus": ["!=", 2]},
            "name",
        )
        if ste:
            return ste

    if pr_name and frappe.db.has_column("Stock Entry", "reference_no"):
        ste = frappe.db.get_value(
            "Stock Entry",
            {"reference_no": pr_name, "docstatus": ["!=", 2]},
            "name",
        )
        if ste:
            return ste

    if pr_name and frappe.db.has_column("Stock Entry Detail", "reference_purchase_receipt"):
        ste = frappe.db.get_value(
            "Stock Entry Detail",
            {"reference_purchase_receipt": pr_name, "docstatus": ["!=", 2]},
            "parent",
        )
        if ste:
            return ste

    if mr_name:
        ste = frappe.db.get_value(
            "Stock Entry Detail",
            {"material_request": mr_name, "docstatus": ["!=", 2]},
            "parent",
        )
        if ste:
            return ste

    if po_name and frappe.db.has_column("Stock Entry", "purchase_order"):
        ste = frappe.db.get_value(
            "Stock Entry",
            {"purchase_order": po_name, "docstatus": ["!=", 2]},
            "name",
        )
        if ste:
            return ste

    return None


def _get_links_from_ste(ste_name):
    ste_pr, ste_po, ste_mr = None, None, None

    if frappe.db.has_column("Stock Entry", "purchase_receipt_no"):
        ste_pr = frappe.db.get_value("Stock Entry", ste_name, "purchase_receipt_no")
    if not ste_pr and frappe.db.has_column("Stock Entry", "reference_no"):
        ref = frappe.db.get_value("Stock Entry", ste_name, "reference_no")
        if ref and frappe.db.exists("Purchase Receipt", ref):
            ste_pr = ref

    if frappe.db.has_column("Stock Entry", "purchase_order"):
        ste_po = frappe.db.get_value("Stock Entry", ste_name, "purchase_order")

    items = frappe.get_all(
        "Stock Entry Detail",
        filters={"parent": ste_name},
        fields=["material_request", "name"],
        limit=10,
    )
    for item in items:
        if item.material_request and not ste_mr:
            ste_mr = item.material_request

    return ste_pr, ste_po, ste_mr


def _get_shipment_tracking(po_name, pr_name):
    if not frappe.db.exists("DocType", "Shipment Tracking"):
        return None

    st = None
    if po_name and frappe.db.has_column("Shipment Tracking", "purchase_order"):
        st = frappe.db.get_value(
            "Shipment Tracking",
            {"purchase_order": po_name, "docstatus": ["!=", 2]},
            "name",
        )
    if not st and pr_name and frappe.db.has_column("Shipment Tracking", "purchase_receipt"):
        st = frappe.db.get_value(
            "Shipment Tracking",
            {"purchase_receipt": pr_name, "docstatus": ["!=", 2]},
            "name",
        )
    if not st and po_name and frappe.db.has_column("Shipment Tracking", "tracking_number"):
        st = frappe.db.get_value(
            "Shipment Tracking",
            {"tracking_number": po_name, "docstatus": ["!=", 2]},
            "name",
        )
    if not st and po_name and frappe.db.has_column("Purchase Order", "shipment_tracking"):
        st = frappe.db.get_value("Purchase Order", po_name, "shipment_tracking")
    if not st and pr_name and frappe.db.has_column("Purchase Receipt", "shipment_tracking"):
        st = frappe.db.get_value("Purchase Receipt", pr_name, "shipment_tracking")

    if not st and po_name:
        candidate = f"SHIP-TRACK-{po_name}"
        if frappe.db.exists("Shipment Tracking", candidate):
            st = candidate

    return st


def _get_links_from_st(st_name):
    st_po, st_pr = None, None
    if frappe.db.has_column("Shipment Tracking", "purchase_order"):
        st_po = frappe.db.get_value("Shipment Tracking", st_name, "purchase_order")
    if frappe.db.has_column("Shipment Tracking", "purchase_receipt"):
        st_pr = frappe.db.get_value("Shipment Tracking", st_name, "purchase_receipt")

    if not st_po and st_name.startswith("SHIP-TRACK-"):
        possible_po = st_name.replace("SHIP-TRACK-", "")
        if frappe.db.exists("Purchase Order", possible_po):
            st_po = possible_po

    return st_po, st_pr


def _get_pe_from_po(po_name):
    if not po_name:
        return None
    pe = frappe.db.sql("""
        SELECT parent FROM `tabPayment Entry Reference`
        WHERE reference_doctype = 'Purchase Order' AND reference_name = %s AND docstatus != 2
        ORDER BY creation DESC LIMIT 1
    """, (po_name,))
    if pe:
        return pe[0][0]

    try:
        pi_names = frappe.db.get_all(
            "Purchase Invoice Item",
            filters={"purchase_order": po_name, "docstatus": ["!=", 2]},
            pluck="parent",
            distinct=True
        )
        if pi_names:
            pe_row = frappe.db.sql("""
                SELECT parent FROM `tabPayment Entry Reference`
                WHERE reference_doctype = 'Purchase Invoice' AND reference_name IN %s AND docstatus != 2
                ORDER BY creation DESC LIMIT 1
            """, (tuple(pi_names),))
            if pe_row:
                return pe_row[0][0]
    except Exception:
        pass

    return None


def _get_po_from_pe(pe_name):
    if not pe_name:
        return None
    po = frappe.db.sql("""
        SELECT reference_name FROM `tabPayment Entry Reference`
        WHERE parent = %s AND reference_doctype = 'Purchase Order' AND docstatus != 2
        LIMIT 1
    """, (pe_name,))
    if po:
        return po[0][0]

    try:
        pi = frappe.db.sql("""
            SELECT reference_name FROM `tabPayment Entry Reference`
            WHERE parent = %s AND reference_doctype = 'Purchase Invoice' AND docstatus != 2
            LIMIT 1
        """, (pe_name,))
        if pi:
            po_name = frappe.db.get_value(
                "Purchase Invoice Item",
                {"parent": pi[0][0], "docstatus": ["!=", 2]},
                "purchase_order"
            )
            if po_name:
                return po_name
    except Exception:
        pass

    return None


def _get_doc_status_info(doctype, docname):
    if not frappe.db.exists(doctype, docname):
        return None

    fields = ["docstatus"]
    if frappe.db.has_column(doctype, "status"):
        fields.append("status")

    data = frappe.db.get_value(doctype, docname, fields, as_dict=True)
    if not data:
        return None

    docstatus = data.get("docstatus", 0)
    status = data.get("status", "")

    if not status:
        if docstatus == 0:
            status = "Draft"
        elif docstatus == 1:
            status = "Submitted"
        elif docstatus == 2:
            status = "Cancelled"

    completed = False
    if docstatus == 1:
        if doctype == "Material Request":
            completed = status in ["Ordered", "Issued", "Transferred", "Received"]
        elif doctype == "Purchase Order":
            completed = status in ["To Receive and Bill", "To Bill", "To Receive", "Completed", "Closed"]
        elif doctype == "Sales Order":
            completed = status in ["To Deliver and Bill", "To Bill", "To Deliver", "Completed", "Closed"]
        elif doctype == "Payment Entry":
            completed = True
        elif doctype == "Shipment Tracking":
            completed = status in ["Delivered", "Completed", "Giao hàng thành công", "Received", "Closed"]
        elif doctype in ["Purchase Receipt", "Landed Cost Voucher", "Stock Entry", "Delivery Note", "Sales Invoice"]:
            completed = True

    return {
        "docstatus": docstatus,
        "status": status,
        "completed": completed,
    }
