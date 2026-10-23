import os
import sys
import hashlib
from datetime import datetime, timedelta

try:
    import frappe
    from frappe.utils import today, add_days
except ImportError:
    frappe = None

# ==============================================================================
# SPECIFICATIONS & REFERENCE MASTER DATA (R3, R4)
# ==============================================================================

SIMULATION_SUPPLIERS = [
    {
        "supplier_name": "Pandora Jewelry Ltd",
        "supplier_group": "Jewelry & Luxury Goods",
        "country": "Thailand",
        "address": {
            "title": "Pandora Gemopolis Facility",
            "line1": "88/1 Soi Sukhaphiban 2, Prawet",
            "city": "Bangkok",
            "country": "Thailand",
            "pincode": "10250"
        }
    },
    {
        "supplier_name": "Apple Inc.",
        "supplier_group": "IT & Consumer Electronics",
        "country": "United States",
        "address": {
            "title": "Apple Park Headquarters",
            "line1": "1 Apple Park Way",
            "city": "Cupertino",
            "country": "United States",
            "pincode": "95014"
        }
    },
    {
        "supplier_name": "Dell Technologies",
        "supplier_group": "IT & Consumer Electronics",
        "country": "Malaysia",
        "address": {
            "title": "Dell APCC2 Bukit Minyak Hub",
            "line1": "Plot 24, Bukit Minyak Industrial Park",
            "city": "Penang",
            "country": "Malaysia",
            "pincode": "14100"
        }
    },
    {
        "supplier_name": "Lenovo Group",
        "supplier_group": "IT & Consumer Electronics",
        "country": "China",
        "address": {
            "title": "Lenovo LCFC Hefei Manufacturing",
            "line1": "No. 3188-1 Yiqi Road, Hefei Economic Hub",
            "city": "Hefei",
            "country": "China",
            "pincode": "230601"
        }
    },
    {
        "supplier_name": "Toyota Motor Thailand",
        "supplier_group": "Automotive & Vehicles",
        "country": "Thailand",
        "address": {
            "title": "Toyota Gateway Plant",
            "line1": "256 Moo 7, Gateway City Industrial Estate",
            "city": "Chachoengsao",
            "country": "Thailand",
            "pincode": "24140"
        }
    },
    {
        "supplier_name": "Honda Vietnam/Thailand Co.",
        "supplier_group": "Automotive & Vehicles",
        "country": "Thailand",
        "address": {
            "title": "Honda Rojana Plant",
            "line1": "49 Moo 4, Rojana Industrial Park",
            "city": "Ayutthaya",
            "country": "Thailand",
            "pincode": "13210"
        }
    },
    {
        "supplier_name": "Yamaha Motor Co., Ltd.",
        "supplier_group": "Automotive & Vehicles",
        "country": "Japan",
        "address": {
            "title": "Yamaha Motor Iwata Headquarters",
            "line1": "2500 Shingai",
            "city": "Iwata",
            "country": "Japan",
            "pincode": "438-8501"
        }
    }
]

SIMULATION_WAREHOUSES = [
    "Cat Lai Port",
    "Hai Phong Port",
    "Tan Son Nhat Airport",
    "Hiep Phuoc Port",
    "Noi Bai Airport",
    "VN-NORTH-DC",
    "VN-SOUTH-DC",
    "Toyota VN Vehicle DC / PDI Yard",
    "Honda VN Vehicle DC / PDI Yard",
    "VN-NORTH Vehicle DC"
]

SIMULATION_ITEMS = [
    # --- Phần XIV (Chương 71): Trang sức Pandora ---
    {
        "item_code": "PANDORA-MOMENTS-BRACELET",
        "item_name": "Pandora Moments Heart & Snake Chain Bracelet",
        "item_group": "Jewelry & Luxury Goods",
        "hs_code": "7113.11",
        "stock_uom": "Pcs",
        "buying_rate_usd": 75.0,
        "selling_rate_usd": 90.0,
        "default_warehouse": "VN-SOUTH-DC - CK",
        "supplier": "Pandora Jewelry Ltd",
        "description": "[HS: 7113.11] Vòng đeo tay bạc 925 tráng men cao cấp Pandora Moments Heart"
    },
    {
        "item_code": "PANDORA-PAVE-RING",
        "item_name": "Pandora Timeless Pavé Single-row Ring",
        "item_group": "Jewelry & Luxury Goods",
        "hs_code": "7113.11",
        "stock_uom": "Pcs",
        "buying_rate_usd": 55.0,
        "selling_rate_usd": 70.0,
        "default_warehouse": "VN-SOUTH-DC - CK",
        "supplier": "Pandora Jewelry Ltd",
        "description": "[HS: 7113.11] Nhẫn bạc đính đá Cubic Zirconia Pandora Timeless Pavé"
    },
    {
        "item_code": "PANDORA-TRIPLE-NECKLACE",
        "item_name": "Triple Stone Heart Collier Necklace",
        "item_group": "Jewelry & Luxury Goods",
        "hs_code": "7113.11",
        "stock_uom": "Pcs",
        "buying_rate_usd": 110.0,
        "selling_rate_usd": 135.0,
        "default_warehouse": "VN-SOUTH-DC - CK",
        "supplier": "Pandora Jewelry Ltd",
        "description": "[HS: 7113.11] Dây chuyền bạc đính đá Triple Stone Heart Collier"
    },

    # --- Phần XVI (Chương 84, 85): Thiết bị CNTT & Điện tử ---
    {
        "item_code": "IPHONE-17",
        "item_name": "Apple iPhone 17 256GB Midnight Black",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8517.13",
        "stock_uom": "Nos",
        "buying_rate_usd": 950.0,
        "selling_rate_usd": 1150.0,
        "default_warehouse": "VN-NORTH-DC - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8517.13] Điện thoại thông minh Apple iPhone 17 256GB Midnight Black"
    },
    {
        "item_code": "MACBOOK-AIR-M5",
        "item_name": "Apple MacBook Air 13\" M5 16GB/512GB",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 1250.0,
        "selling_rate_usd": 1490.0,
        "default_warehouse": "VN-NORTH-DC - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8471.30] Laptop Apple MacBook Air 13 inch chip Apple M5 16GB/512GB"
    },
    {
        "item_code": "AIRPODS-PRO-3",
        "item_name": "Apple AirPods Pro 3 Wireless Earbuds",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8518.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 220.0,
        "selling_rate_usd": 279.0,
        "default_warehouse": "VN-NORTH-DC - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8518.30] Tai nghe không dây cao cấp Apple AirPods Pro 3"
    },
    {
        "item_code": "DELL-PRO-14",
        "item_name": "Dell Pro 14 Laptop Core Ultra 7 32GB",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 1350.0,
        "selling_rate_usd": 1590.0,
        "default_warehouse": "VN-SOUTH-DC - CK",
        "supplier": "Dell Technologies",
        "description": "[HS: 8471.30] Laptop doanh nghiệp Dell Pro 14 inch Intel Core Ultra 7 32GB RAM"
    },
    {
        "item_code": "DELL-OPTIPLEX",
        "item_name": "Dell OptiPlex Micro Desktop PC 16GB",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.49",
        "stock_uom": "Nos",
        "buying_rate_usd": 780.0,
        "selling_rate_usd": 950.0,
        "default_warehouse": "VN-SOUTH-DC - CK",
        "supplier": "Dell Technologies",
        "description": "[HS: 8471.49] Máy tính để bàn siêu nhỏ Dell OptiPlex Micro Form Factor 16GB RAM"
    },
    {
        "item_code": "DELL-ULTRASHARP-U2725QE",
        "item_name": "Dell UltraSharp U2725QE 27\" 4K Monitor",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8528.52",
        "stock_uom": "Nos",
        "buying_rate_usd": 590.0,
        "selling_rate_usd": 720.0,
        "default_warehouse": "VN-SOUTH-DC - CK",
        "supplier": "Dell Technologies",
        "description": "[HS: 8528.52] Màn hình chuyên đồ họa 4K Dell UltraSharp U2725QE 27 inch IPS Black"
    },
    {
        "item_code": "THINKPAD-X1-CARBON",
        "item_name": "ThinkPad X1 Carbon Gen 14 Intel Core Ultra",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 1680.0,
        "selling_rate_usd": 1990.0,
        "default_warehouse": "VN-NORTH-DC - CK",
        "supplier": "Lenovo Group",
        "description": "[HS: 8471.30] Laptop doanh nhân cao cấp Lenovo ThinkPad X1 Carbon Gen 14"
    },
    {
        "item_code": "THINKCENTRE-M75S",
        "item_name": "ThinkCentre M75s Gen 6 Small Form Factor",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.50",
        "stock_uom": "Nos",
        "buying_rate_usd": 720.0,
        "selling_rate_usd": 880.0,
        "default_warehouse": "VN-NORTH-DC - CK",
        "supplier": "Lenovo Group",
        "description": "[HS: 8471.50] Máy trạm để bàn văn phòng Lenovo ThinkCentre M75s Gen 6 SFF"
    },
    {
        "item_code": "THINKVISION-MONITOR",
        "item_name": "ThinkVision P27h-30 27\" QHD Monitor",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8528.52",
        "stock_uom": "Nos",
        "buying_rate_usd": 410.0,
        "selling_rate_usd": 510.0,
        "default_warehouse": "VN-NORTH-DC - CK",
        "supplier": "Lenovo Group",
        "description": "[HS: 8528.52] Màn hình chuyên nghiệp đồ họa Lenovo ThinkVision P27h-30 27 inch QHD"
    },

    # --- Phần XVII (Chương 87): Phương tiện & Xe CBU ---
    {
        "item_code": "TOYOTA-HILUX-2026",
        "item_name": "Toyota Hilux 2026 Double Cab 4x4 CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8704.21",
        "stock_uom": "Unit",
        "buying_rate_usd": 23500.0,
        "selling_rate_usd": 28000.0,
        "default_warehouse": "Toyota VN Vehicle DC / PDI Yard - CK",
        "supplier": "Toyota Motor Thailand",
        "description": "[HS: 8704.21] Xe bán tải chở hàng Toyota Hilux 2026 4x4 nhập khẩu nguyên chiếc CBU"
    },
    {
        "item_code": "TOYOTA-CAMRY-2026",
        "item_name": "Toyota Camry 2026 2.5 HEV Premium CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8703.40",
        "stock_uom": "Unit",
        "buying_rate_usd": 28900.0,
        "selling_rate_usd": 35000.0,
        "default_warehouse": "Toyota VN Vehicle DC / PDI Yard - CK",
        "supplier": "Toyota Motor Thailand",
        "description": "[HS: 8703.40] Xe ô tô du lịch hybrid cao cấp Toyota Camry 2026 2.5 HEV CBU"
    },
    {
        "item_code": "TOYOTA-COROLLA-CROSS",
        "item_name": "Toyota Corolla Cross 1.8 HEV CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8703.40",
        "stock_uom": "Unit",
        "buying_rate_usd": 21200.0,
        "selling_rate_usd": 25500.0,
        "default_warehouse": "Toyota VN Vehicle DC / PDI Yard - CK",
        "supplier": "Toyota Motor Thailand",
        "description": "[HS: 8703.40] Xe ô tô SUV 5 chỗ hybrid Toyota Corolla Cross 1.8 HEV CBU"
    },
    {
        "item_code": "HONDA-HR-V",
        "item_name": "Honda HR-V e:HEV RS 2026 CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8703.40",
        "stock_uom": "Unit",
        "buying_rate_usd": 22800.0,
        "selling_rate_usd": 27500.0,
        "default_warehouse": "Honda VN Vehicle DC / PDI Yard - CK",
        "supplier": "Honda Vietnam/Thailand Co.",
        "description": "[HS: 8703.40] Xe ô tô du lịch crossover Honda HR-V e:HEV RS 2026 CBU Thái Lan"
    },
    {
        "item_code": "HONDA-REBEL-500",
        "item_name": "Honda Rebel 500 Cruiser CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8711.40",
        "stock_uom": "Unit",
        "buying_rate_usd": 5600.0,
        "selling_rate_usd": 7000.0,
        "default_warehouse": "Honda VN Vehicle DC / PDI Yard - CK",
        "supplier": "Honda Vietnam/Thailand Co.",
        "description": "[HS: 8711.40] Mô tô phân khối lớn Honda Rebel 500 phong cách Cruiser CBU"
    },
    {
        "item_code": "HONDA-CBR650R",
        "item_name": "Honda CBR650R 4-Cylinder Sportbike CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8711.50",
        "stock_uom": "Unit",
        "buying_rate_usd": 8400.0,
        "selling_rate_usd": 10500.0,
        "default_warehouse": "Honda VN Vehicle DC / PDI Yard - CK",
        "supplier": "Honda Vietnam/Thailand Co.",
        "description": "[HS: 8711.50] Mô tô thể thao 4 xi-lanh Honda CBR650R CBU Thái Lan"
    },
    {
        "item_code": "YAMAHA-MT07",
        "item_name": "Yamaha MT-07 CP2 Hyper Naked CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8711.50",
        "stock_uom": "Unit",
        "buying_rate_usd": 7500.0,
        "selling_rate_usd": 9200.0,
        "default_warehouse": "VN-NORTH Vehicle DC - CK",
        "supplier": "Yamaha Motor Co., Ltd.",
        "description": "[HS: 8711.50] Mô tô phân khối lớn động cơ CP2 Yamaha MT-07 CBU Nhật Bản"
    },
    {
        "item_code": "YAMAHA-MT09",
        "item_name": "Yamaha MT-09 CP3 Triple Cylinder CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8711.50",
        "stock_uom": "Unit",
        "buying_rate_usd": 9900.0,
        "selling_rate_usd": 12000.0,
        "default_warehouse": "VN-NORTH Vehicle DC - CK",
        "supplier": "Yamaha Motor Co., Ltd.",
        "description": "[HS: 8711.50] Mô tô phân khối lớn 3 xi-lanh CP3 Yamaha MT-09 CBU Nhật Bản"
    },
    {
        "item_code": "YAMAHA-TENERE-700",
        "item_name": "Yamaha Ténéré 700 Rally Adventure CBU",
        "item_group": "Automotive & Vehicles",
        "hs_code": "8711.50",
        "stock_uom": "Unit",
        "buying_rate_usd": 10800.0,
        "selling_rate_usd": 13200.0,
        "default_warehouse": "VN-NORTH Vehicle DC - CK",
        "supplier": "Yamaha Motor Co., Ltd.",
        "description": "[HS: 8711.50] Mô tô địa hình đường trường Rally Adventure Yamaha Ténéré 700 CBU"
    },

    # --- 4 Legacy Items Apple ---
    {
        "item_code": "IPHONE-16-PROMAX",
        "item_name": "Apple iPhone 16 Pro Max 256GB Desert Titanium",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8517.13",
        "stock_uom": "Nos",
        "buying_rate_usd": 1100.0,
        "selling_rate_usd": 1377.5,
        "default_warehouse": "Stores - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8517.13] Flagship iPhone 16 Pro Max 256GB Titan sa mạc"
    },
    {
        "item_code": "MACBOOK-PRO-M3",
        "item_name": "Apple MacBook Pro 14\" M3 Pro 18GB/512GB Space Black",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 1800.0,
        "selling_rate_usd": 1968.1,
        "default_warehouse": "Stores - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8471.30] Laptop Apple MacBook Pro 14 inch chip M3 Pro"
    },
    {
        "item_code": "IPAD-PRO-M4",
        "item_name": "Apple iPad Pro 11\" M4 Ultra Retina Tandem OLED 256GB",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8471.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 950.0,
        "selling_rate_usd": 1141.3,
        "default_warehouse": "Stores - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8471.30] Máy tính bảng Apple iPad Pro 11 inch chip M4"
    },
    {
        "item_code": "AIRPODS-PRO-2",
        "item_name": "Apple AirPods Pro 2 MagSafe USB-C (2nd Gen)",
        "item_group": "IT & Consumer Electronics",
        "hs_code": "8518.30",
        "stock_uom": "Nos",
        "buying_rate_usd": 220.0,
        "selling_rate_usd": 243.7,
        "default_warehouse": "Stores - CK",
        "supplier": "Apple Inc.",
        "description": "[HS: 8518.30] Tai nghe True Wireless Apple AirPods Pro 2 USB-C"
    }
]

def make_dedup_hash(shipment_id: str, milestone: str, location: str, timestamp: str) -> str:
    content = f"{shipment_id}:{milestone}:{location}:{timestamp}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def get_simulation_shipments_specs():
    """
    Returns full specifications for the 7 multimodal simulation shipments (R4)
    each with 9 international DCSA milestones and complete tracking metadata.
    """
    return [
        # 1. PANDORA AIR (BKK -> SGN -> VN-SOUTH-DC)
        {
            "po_name": "PO-PANDORA-2026-001",
            "st_name": "ST-PANDORA-AIR-01",
            "supplier": "Pandora Jewelry Ltd",
            "supplier_address": "Pandora Gemopolis Facility-Billing",
            "shipping_method": "Air",
            "carrier": "Thai Airways Cargo",
            "flight_number": "TG556",
            "tracking_number": "TG-98210342",
            "air_waybill": "AWB-217-98210342",
            "origin_port": "Suvarnabhumi Airport (BKK)",
            "destination_port": "Tan Son Nhat Airport (SGN)",
            "dest_warehouse": "VN-SOUTH-DC - CK",
            "etd": "2026-10-02",
            "atd": "2026-10-02",
            "initial_eta": "2026-10-03",
            "eta": "2026-10-03",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "current_lat": 11.50,
            "current_lon": 104.50,
            "items": [
                {"item_code": "PANDORA-MOMENTS-BRACELET", "qty": 500, "rate": 75.0},
                {"item_code": "PANDORA-PAVE-RING", "qty": 300, "rate": 55.0},
                {"item_code": "PANDORA-TRIPLE-NECKLACE", "qty": 200, "rate": 110.0}
            ],
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ vận chuyển hàng không & Xác nhận Booking", "location": "Pandora Gemopolis Hub", "port_code": "THBKK", "date": "2026-10-01", "timestamp": "2026-10-01 10:00:00", "lat": 13.6875, "lon": 100.7025, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Hàng trang sức hoàn tất kiểm định và đóng gói an ninh tại xưởng Gemopolis."},
                {"milestone": "GATE_IN", "activity": "Xe an ninh vận chuyển tập kết vào Ga hàng hóa BKK", "location": "Suvarnabhumi Airport (BKK)", "port_code": "THBKK", "date": "2026-10-02", "timestamp": "2026-10-02 02:30:00", "lat": 13.6811, "lon": 100.7473, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Hàng qua cửa khẩu soi chiếu an ninh hàng không Suvarnabhumi."},
                {"milestone": "LOADED", "activity": "Bốc xếp hàng lên khoang máy bay chuyến bay TG556", "location": "Suvarnabhumi Airport (BKK)", "port_code": "THBKK", "date": "2026-10-02", "timestamp": "2026-10-02 05:15:00", "lat": 13.6811, "lon": 100.7473, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Hàng xếp vào container hàng không ULD an ninh cao."},
                {"milestone": "DEPARTED", "activity": "Chuyến bay TG556 cất cánh rời sân bay Suvarnabhumi", "location": "Suvarnabhumi Airport (BKK)", "port_code": "THBKK", "date": "2026-10-02", "timestamp": "2026-10-02 06:40:00", "lat": 13.6811, "lon": 100.7473, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Khởi hành đúng giờ theo hành lang hàng không Bangkok - Tân Sơn Nhất."},
                {"milestone": "TRANSSHIPMENT", "activity": "Bay hành trình trên không phận quốc tế Vịnh Thái Lan", "location": "Gulf of Thailand Airspace", "port_code": "THBKK", "date": "2026-10-02", "timestamp": "2026-10-02 07:25:00", "lat": 11.50, "lon": 104.50, "vessel_or_flight": "TG556", "is_current": 1, "notes": "Máy bay đang hành trình ở độ cao 33,000 ft hướng về Tân Sơn Nhất."},
                {"milestone": "ARRIVED", "activity": "Hạ cánh tại Sân bay Quốc tế Tân Sơn Nhất", "location": "Tan Son Nhat Airport (SGN)", "port_code": "VNSGN", "date": "2026-10-02", "timestamp": "2026-10-02 08:15:00", "lat": 10.8188, "lon": 106.6520, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Dự kiến hạ cánh đường băng 25R sân bay Tân Sơn Nhất."},
                {"milestone": "DISCHARGED", "activity": "Dỡ hàng khỏi máy bay đưa vào Kho hàng TCS", "location": "Tan Son Nhat Airport (SGN)", "port_code": "VNSGN", "date": "2026-10-02", "timestamp": "2026-10-02 09:30:00", "lat": 10.8188, "lon": 106.6520, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Khai thác hàng nhập khẩu tại kho hàng không Tân Sơn Nhất."},
                {"milestone": "GATE_OUT", "activity": "Hoàn tất thông quan hải quan & Xe chuyên dụng kéo hàng ra cổng", "location": "Tan Son Nhat Airport (SGN)", "port_code": "VNSGN", "date": "2026-10-02", "timestamp": "2026-10-02 14:00:00", "lat": 10.8188, "lon": 106.6520, "vessel_or_flight": "TG556", "is_current": 0, "notes": "Thông quan điện tử VNACCS và điều phối xe tải an ninh."},
                {"milestone": "DELIVERED", "activity": "Giao hàng và ký nhận tại Kho tổng VN-SOUTH-DC", "location": "VN-SOUTH-DC", "port_code": "VNSGN", "date": "2026-10-03", "timestamp": "2026-10-03 09:00:00", "lat": 10.9143, "lon": 106.7295, "vessel_or_flight": "Truck-Secured", "is_current": 0, "notes": "Bàn giao đầy đủ seal chì an ninh tại kho phân phối Sóng Thần."}
            ]
        },

        # 2. APPLE AIR (SZX -> HAN -> VN-NORTH-DC)
        {
            "po_name": "PO-APPLE-2026-002",
            "st_name": "ST-APPLE-AIR-02",
            "supplier": "Apple Inc.",
            "supplier_address": "Apple Park Headquarters-Billing",
            "shipping_method": "Air",
            "carrier": "SF Airlines Cargo",
            "flight_number": "O36988",
            "tracking_number": "SF-77881234",
            "air_waybill": "AWB-921-77881234",
            "origin_port": "Shenzhen Bao'an Airport (SZX)",
            "destination_port": "Noi Bai Airport (HAN)",
            "dest_warehouse": "VN-NORTH-DC - CK",
            "etd": "2026-10-02",
            "atd": "2026-10-02",
            "initial_eta": "2026-10-03",
            "eta": "2026-10-03",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "current_lat": 21.50,
            "current_lon": 108.50,
            "items": [
                {"item_code": "IPHONE-17", "qty": 400, "rate": 950.0},
                {"item_code": "MACBOOK-AIR-M5", "qty": 150, "rate": 1250.0},
                {"item_code": "AIRPODS-PRO-3", "qty": 500, "rate": 220.0}
            ],
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ lô hàng điện tử cao cấp & Phát hành AWB", "location": "South China Consolidation Hub", "port_code": "CNSZX", "date": "2026-10-01", "timestamp": "2026-10-01 11:30:00", "lat": 22.6500, "lon": 114.0167, "vessel_or_flight": "O36988", "is_current": 0, "notes": "Hàng điện tử đóng pallet tiêu chuẩn tại Hub Thâm Quyến Longhua."},
                {"milestone": "GATE_IN", "activity": "Pallet iPhone 17 & MacBook nhập ga hàng hóa SZX", "location": "Shenzhen Bao'an Airport (SZX)", "port_code": "CNSZX", "date": "2026-10-02", "timestamp": "2026-10-02 01:15:00", "lat": 22.6393, "lon": 113.8107, "vessel_or_flight": "O36988", "is_current": 0, "notes": "Kiểm tra an ninh và cân tải trọng pallet hàng không."},
                {"milestone": "LOADED", "activity": "Bốc xếp hàng lên tàu bay chuyên dụng Boeing 757-200F", "location": "Shenzhen Bao'an Airport (SZX)", "port_code": "CNSZX", "date": "2026-10-02", "timestamp": "2026-10-02 04:00:00", "lat": 22.6393, "lon": 113.8107, "vessel_or_flight": "O36988", "is_current": 0, "notes": "Hàng khóa chốt an toàn trên sàn chuyên chở hàng không."},
                {"milestone": "DEPARTED", "activity": "Chuyến bay SF Airlines O36988 cất cánh từ Thâm Quyến", "location": "Shenzhen Bao'an Airport (SZX)", "port_code": "CNSZX", "date": "2026-10-02", "timestamp": "2026-10-02 05:45:00", "lat": 22.6393, "lon": 113.8107, "vessel_or_flight": "O36988", "is_current": 0, "notes": "Bay theo hành lang quốc tế Thâm Quyến - Vịnh Bắc Bộ - Nội Bài."},
                {"milestone": "TRANSSHIPMENT", "activity": "Bay qua không phận Vịnh Bắc Bộ vào vùng thông báo bay Hà Nội", "location": "Gulf of Tonkin Airspace", "port_code": "CNSZX", "date": "2026-10-02", "timestamp": "2026-10-02 06:40:00", "lat": 21.50, "lon": 108.50, "vessel_or_flight": "O36988", "is_current": 1, "notes": "Tiếp cận kiểm soát không lưu Nội Bài Approach."},
                {"milestone": "ARRIVED", "activity": "Hạ cánh tại Cảng Hàng không Quốc tế Nội Bài", "location": "Noi Bai Airport (HAN)", "port_code": "VNHAN", "date": "2026-10-02", "timestamp": "2026-10-02 07:30:00", "lat": 21.2212, "lon": 105.8072, "vessel_or_flight": "O36988", "is_current": 0, "notes": "Hạ cánh an toàn tại Nội Bài, lăn vào bãi đỗ hàng hóa."},
                {"milestone": "DISCHARGED", "activity": "Dỡ hàng pallet chuyển vào Nhà ga Hàng hóa ACSV Nội Bài", "location": "Noi Bai Airport (HAN)", "port_code": "VNHAN", "date": "2026-10-02", "timestamp": "2026-10-02 08:45:00", "lat": 21.2212, "lon": 105.8072, "vessel_or_flight": "O36988", "is_current": 0, "notes": "Khai thác và phân loại hàng công nghệ cao."},
                {"milestone": "GATE_OUT", "activity": "Hoàn tất thủ tục hải quan nhập khẩu Nội Bài & Drayage xuất bãi", "location": "Noi Bai Airport (HAN)", "port_code": "VNHAN", "date": "2026-10-02", "timestamp": "2026-10-02 13:30:00", "lat": 21.2212, "lon": 105.8072, "vessel_or_flight": "Truck-Bonded", "is_current": 0, "notes": "Đoàn xe vận chuyển ngoại quan di chuyển về Bắc Ninh."},
                {"milestone": "DELIVERED", "activity": "Giao hàng hoàn tất tại Trung tâm phân phối VN-NORTH-DC", "location": "VN-NORTH-DC", "port_code": "VNHAN", "date": "2026-10-03", "timestamp": "2026-10-03 08:30:00", "lat": 21.1400, "lon": 105.9500, "vessel_or_flight": "Truck-Bonded", "is_current": 0, "notes": "Nhập kho tổng miền Bắc, đối soát nguyên đai nguyên kiện."}
            ]
        },

        # 3. DELL SEA (MYPKG -> Cat Lai -> VN-SOUTH-DC)
        {
            "po_name": "PO-DELL-2026-003",
            "st_name": "ST-DELL-SEA-03",
            "supplier": "Dell Technologies",
            "supplier_address": "Dell APCC2 Bukit Minyak Hub-Billing",
            "shipping_method": "Ocean",
            "carrier": "Ocean Network Express (ONE)",
            "vessel_name": "ONE Continuity",
            "tracking_number": "ONE-MYVN-552203",
            "container_id": "ONEU7821901",
            "bill_of_lading": "BL-ONE-MYPKG-03",
            "origin_port": "Port Klang (MYPKG)",
            "destination_port": "Cat Lai Port (VNSGN)",
            "dest_warehouse": "VN-SOUTH-DC - CK",
            "etd": "2026-09-30",
            "atd": "2026-09-30",
            "initial_eta": "2026-10-03",
            "eta": "2026-10-03",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "current_lat": 3.50,
            "current_lon": 105.50,
            "items": [
                {"item_code": "DELL-PRO-14", "qty": 250, "rate": 1350.0},
                {"item_code": "DELL-OPTIPLEX", "qty": 200, "rate": 780.0},
                {"item_code": "DELL-ULTRASHARP-U2725QE", "qty": 300, "rate": 590.0}
            ],
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ hãng tàu ONE Line từ Nhà máy Dell Penang APCC2", "location": "Dell APCC2 Bukit Minyak Hub", "port_code": "MYPKG", "date": "2026-09-27", "timestamp": "2026-09-27 09:00:00", "lat": 5.2862, "lon": 100.4635, "vessel_or_flight": "ONE Continuity", "is_current": 0, "notes": "Phát hành Shipping Order đóng container 40HC."},
                {"milestone": "GATE_IN", "activity": "Container ONEU7821901 hạ bãi xuất khẩu Port Klang Westport", "location": "Port Klang (MYPKG)", "port_code": "MYPKG", "date": "2026-09-29", "timestamp": "2026-09-29 16:00:00", "lat": 2.9998, "lon": 101.3928, "vessel_or_flight": "ONE Continuity", "is_current": 0, "notes": "Hạ bãi container cảng Klang, niêm phong chì hãng tàu."},
                {"milestone": "LOADED", "activity": "Cẩu bốc container lên tàu mẹ ONE Continuity", "location": "Port Klang (MYPKG)", "port_code": "MYPKG", "date": "2026-09-30", "timestamp": "2026-09-30 08:30:00", "lat": 2.9998, "lon": 101.3928, "vessel_or_flight": "ONE Continuity", "is_current": 0, "notes": "Xếp vị trí boong tàu an toàn, kiểm tra cảm biến chống sốc."},
                {"milestone": "DEPARTED", "activity": "Tàu ONE Continuity nhổ neo rời Cảng Port Klang", "location": "Port Klang (MYPKG)", "port_code": "MYPKG", "date": "2026-09-30", "timestamp": "2026-09-30 14:00:00", "lat": 2.9998, "lon": 101.3928, "vessel_or_flight": "ONE Continuity", "is_current": 0, "notes": "Hành trình xuôi eo biển Malacca ra Biển Đông."},
                {"milestone": "TRANSSHIPMENT", "activity": "Hải trình hàng hải trên Biển Đông hướng vào phao số 0 Vũng Tàu", "location": "South China Sea Corridor", "port_code": "MYPKG", "date": "2026-10-02", "timestamp": "2026-10-02 08:00:00", "lat": 3.50, "lon": 105.50, "vessel_or_flight": "ONE Continuity", "is_current": 1, "notes": "Vận tốc hải trình 16.5 knots, thời tiết biển thuận lợi."},
                {"milestone": "ARRIVED", "activity": "Tàu cập Cảng Tân Cảng Cát Lái", "location": "Cat Lai Port (VNSGN)", "port_code": "VNCLI", "date": "2026-10-03", "timestamp": "2026-10-03 10:00:00", "lat": 10.7626, "lon": 106.7898, "vessel_or_flight": "ONE Continuity", "is_current": 0, "notes": "Hoa tiêu dẫn luồng cập cầu cảng Cát Lái B6."},
                {"milestone": "DISCHARGED", "activity": "Cẩu bờ dỡ container xuống bãi cảng Cát Lái", "location": "Cat Lai Port (VNSGN)", "port_code": "VNCLI", "date": "2026-10-03", "timestamp": "2026-10-03 14:30:00", "lat": 10.7626, "lon": 106.7898, "vessel_or_flight": "ONE Continuity", "is_current": 0, "notes": "Dỡ container an toàn và cấp phiếu EIR."},
                {"milestone": "GATE_OUT", "activity": "Thông quan hàng hóa & Xe đầu kéo drayage kéo hàng ra cổng cảng", "location": "Cat Lai Port (VNSGN)", "port_code": "VNCLI", "date": "2026-10-04", "timestamp": "2026-10-04 09:15:00", "lat": 10.7626, "lon": 106.7898, "vessel_or_flight": "Drayage-Truck", "is_current": 0, "notes": "Thanh lý hải quan cổng C và vận chuyển đi Sóng Thần."},
                {"milestone": "DELIVERED", "activity": "Giao hàng và rút ruột container tại Kho tổng VN-SOUTH-DC", "location": "VN-SOUTH-DC", "port_code": "VNCLI", "date": "2026-10-04", "timestamp": "2026-10-04 15:00:00", "lat": 10.9143, "lon": 106.7295, "vessel_or_flight": "Drayage-Truck", "is_current": 0, "notes": "Bàn giao thiết bị CNTT vào hệ thống giá kệ pallet kho DC."}
            ]
        },

        # 4. LENOVO SEA (CNSHA -> Hai Phong -> VN-NORTH-DC)
        {
            "po_name": "PO-LENOVO-2026-004",
            "st_name": "ST-LENOVO-SEA-04",
            "supplier": "Lenovo Group",
            "supplier_address": "Lenovo LCFC Hefei Manufacturing-Billing",
            "shipping_method": "Ocean",
            "carrier": "COSCO Shipping Lines",
            "vessel_name": "COSCO Shipping Galaxy",
            "tracking_number": "COSU-8812903",
            "container_id": "COSU8812903",
            "bill_of_lading": "BL-COSCO-SHA-04",
            "origin_port": "Shanghai Port (CNSHA)",
            "destination_port": "Hai Phong Port (VNHPH)",
            "dest_warehouse": "VN-NORTH-DC - CK",
            "etd": "2026-09-28",
            "atd": "2026-09-28",
            "initial_eta": "2026-10-03",
            "eta": "2026-10-03",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "current_lat": 24.20,
            "current_lon": 119.80,
            "items": [
                {"item_code": "THINKPAD-X1-CARBON", "qty": 200, "rate": 1680.0},
                {"item_code": "THINKCENTRE-M75S", "qty": 300, "rate": 720.0},
                {"item_code": "THINKVISION-MONITOR", "qty": 400, "rate": 410.0}
            ],
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ hãng tàu COSCO từ Trung tâm sản xuất Lenovo LCFC", "location": "Lenovo LCFC Hefei Hub", "port_code": "CNSHA", "date": "2026-09-25", "timestamp": "2026-09-25 10:00:00", "lat": 31.7685, "lon": 117.1852, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 0, "notes": "Đóng thùng máy tính ThinkPad đạt chuẩn chống ẩm đường biển."},
                {"milestone": "GATE_IN", "activity": "Container COSU8812903 hạ bãi Cảng Thượng Hải (Dương Sơn)", "location": "Shanghai Port (CNSHA)", "port_code": "CNSHA", "date": "2026-09-27", "timestamp": "2026-09-27 18:30:00", "lat": 31.3400, "lon": 121.6000, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 0, "notes": "Hạ bãi Yangshan Phase IV cảng tự động hóa Thượng Hải."},
                {"milestone": "LOADED", "activity": "Bốc xếp container lên tàu COSCO Shipping Galaxy", "location": "Shanghai Port (CNSHA)", "port_code": "CNSHA", "date": "2026-09-28", "timestamp": "2026-09-28 09:00:00", "lat": 31.3400, "lon": 121.6000, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 0, "notes": "Xếp hàng lên tàu mẹ tuyến Thượng Hải - Hải Phòng."},
                {"milestone": "DEPARTED", "activity": "Tàu COSCO Shipping Galaxy rời cảng Thượng Hải", "location": "Shanghai Port (CNSHA)", "port_code": "CNSHA", "date": "2026-09-28", "timestamp": "2026-09-28 15:30:00", "lat": 31.3400, "lon": 121.6000, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 0, "notes": "Hành trình ra biển Hoa Đông xuôi về phía nam."},
                {"milestone": "TRANSSHIPMENT", "activity": "Hải trình vượt Eo biển Đài Loan hướng vào Vịnh Bắc Bộ", "location": "Taiwan Strait Fairway", "port_code": "CNSHA", "date": "2026-10-02", "timestamp": "2026-10-02 06:00:00", "lat": 24.20, "lon": 119.80, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 1, "notes": "Vận tốc hải trình 17.2 knots, tiến vào Vịnh Bắc Bộ."},
                {"milestone": "ARRIVED", "activity": "Tàu cập Cảng Tân Vũ / Đình Vũ Hải Phòng", "location": "Hai Phong Port (VNHPH)", "port_code": "VNHPH", "date": "2026-10-03", "timestamp": "2026-10-03 11:00:00", "lat": 20.8656, "lon": 106.7620, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 0, "notes": "Dự kiến hoa tiêu cập cầu cảng Tân Vũ."},
                {"milestone": "DISCHARGED", "activity": "Cẩu dỡ container hàng công nghệ xuống bãi CFS", "location": "Hai Phong Port (VNHPH)", "port_code": "VNHPH", "date": "2026-10-03", "timestamp": "2026-10-03 16:00:00", "lat": 20.8656, "lon": 106.7620, "vessel_or_flight": "COSCO Shipping Galaxy", "is_current": 0, "notes": "Phân loại container nhập khẩu vào khu vực giám sát hải quan."},
                {"milestone": "GATE_OUT", "activity": "Hoàn tất kiểm hóa hải quan Đình Vũ & Rời cổng cảng", "location": "Hai Phong Port (VNHPH)", "port_code": "VNHPH", "date": "2026-10-04", "timestamp": "2026-10-04 10:00:00", "lat": 20.8656, "lon": 106.7620, "vessel_or_flight": "Truck-Heavy", "is_current": 0, "notes": "Vận chuyển đường cao tốc Hải Phòng - Hà Nội."},
                {"milestone": "DELIVERED", "activity": "Giao hàng và ký nhận tại Kho tổng VN-NORTH-DC", "location": "VN-NORTH-DC", "port_code": "VNHPH", "date": "2026-10-04", "timestamp": "2026-10-04 16:00:00", "lat": 21.1400, "lon": 105.9500, "vessel_or_flight": "Truck-Heavy", "is_current": 0, "notes": "Bàn giao lô máy trạm và laptop Lenovo cho kho tổng miền Bắc."}
            ]
        },

        # 5. TOYOTA RORO (THLCH -> Hiep Phuoc -> PDI Yard) — DELAY +2 DAYS SIMULATION
        {
            "po_name": "PO-TOYOTA-2026-005",
            "st_name": "ST-TOYOTA-RORO-05",
            "supplier": "Toyota Motor Thailand",
            "supplier_address": "Toyota Gateway Plant-Billing",
            "shipping_method": "Ocean",
            "carrier": "Toyofuji Shipping (RoRo Car Carrier)",
            "vessel_name": "Trans Future 7",
            "tracking_number": "TFS-THVN-994405",
            "container_id": "VIN-LOT-TYT2026",
            "bill_of_lading": "BL-TFS-RORO-05",
            "origin_port": "Laem Chabang Port (THLCH)",
            "destination_port": "Hiep Phuoc Port (VNHCM)",
            "dest_warehouse": "Toyota VN Vehicle DC / PDI Yard - CK",
            "etd": "2026-10-01",
            "atd": "2026-10-01",
            "initial_eta": "2026-10-04",
            "eta": "2026-10-06",
            "status": "Delayed",
            "is_delayed": 1,
            "delay_days": 2,
            "current_lat": 9.20,
            "current_lon": 103.50,
            "items": [
                {"item_code": "TOYOTA-HILUX-2026", "qty": 20, "rate": 23500.0},
                {"item_code": "TOYOTA-CAMRY-2026", "qty": 15, "rate": 28900.0},
                {"item_code": "TOYOTA-COROLLA-CROSS", "qty": 25, "rate": 21200.0}
            ],
            "exception": {
                "name": "EXC-TOYOTA-2026-005-01",
                "exception_type": "ETA Delay",
                "severity": "Warning",
                "old_eta": "2026-10-04",
                "new_eta": "2026-10-06",
                "delay_days": 2,
                "status": "Open",
                "description": "Lịch trình tàu RoRo dời 2 ngày (từ 04/10 sang 06/10) do kẹt cầu bến chuyên dụng và thời tiết xấu tại vịnh Thái Lan."
            },
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ tàu RoRo chuyên dụng chở xe CBU từ Nhà máy Gateway", "location": "Toyota Gateway Plant", "port_code": "THLCH", "date": "2026-09-28", "timestamp": "2026-09-28 08:30:00", "lat": 13.5855, "lon": 101.3712, "vessel_or_flight": "Trans Future 7", "is_current": 0, "notes": "Xuất xưởng lô 60 xe CBU Hilux, Camry và Corolla Cross HEV."},
                {"milestone": "GATE_IN", "activity": "Đoàn xe tập kết vào Bãi RoRo Terminal A1 Cảng Laem Chabang", "location": "Laem Chabang Port (THLCH)", "port_code": "THLCH", "date": "2026-09-30", "timestamp": "2026-09-30 14:00:00", "lat": 13.0833, "lon": 100.8833, "vessel_or_flight": "Trans Future 7", "is_current": 0, "notes": "Kiểm tra ngoại quan thân vỏ và chằng buộc bãi đỗ."},
                {"milestone": "LOADED", "activity": "Lái xe trực tiếp lên các tầng hầm tàu RoRo Trans Future 7", "location": "Laem Chabang Port (THLCH)", "port_code": "THLCH", "date": "2026-10-01", "timestamp": "2026-10-01 07:00:00", "lat": 13.0833, "lon": 100.8833, "vessel_or_flight": "Trans Future 7", "is_current": 0, "notes": "Cố định bánh xe bằng dây đai chuyên dụng RoRo an toàn."},
                {"milestone": "DEPARTED", "activity": "Tàu RoRo Trans Future 7 rời Cảng Laem Chabang", "location": "Laem Chabang Port (THLCH)", "port_code": "THLCH", "date": "2026-10-01", "timestamp": "2026-10-01 12:00:00", "lat": 13.0833, "lon": 100.8833, "vessel_or_flight": "Trans Future 7", "is_current": 0, "notes": "Khởi hành tuyến RoRo Thái Lan - Cảng Hiệp Phước Việt Nam."},
                {"milestone": "TRANSSHIPMENT", "activity": "Hải trình vòng qua Mũi Cà Mau — Phát hiện trễ hạn ETA (+2 ngày)", "location": "Gulf of Thailand / Ca Mau Waters", "port_code": "THLCH", "date": "2026-10-02", "timestamp": "2026-10-02 10:00:00", "lat": 9.20, "lon": 103.50, "vessel_or_flight": "Trans Future 7", "is_current": 1, "notes": "Vùng biển có giông gió lớn, tàu giảm tốc độ, ETA dời từ 04/10 sang 06/10."},
                {"milestone": "ARRIVED", "activity": "Tàu cập Cảng Hiệp Phước / SPCT (Lịch dời đến 06/10)", "location": "Hiep Phuoc Port (VNHCM)", "port_code": "VNHCM", "date": "2026-10-06", "timestamp": "2026-10-06 08:00:00", "lat": 10.6375, "lon": 106.7642, "vessel_or_flight": "Trans Future 7", "is_current": 0, "notes": "Cập cầu bến chuyên dụng RoRo cảng Hiệp Phước."},
                {"milestone": "DISCHARGED", "activity": "Hạ cầu dốc ramp và lái xe xuống bãi đỗ PDI tạm cảng Hiệp Phước", "location": "Hiep Phuoc Port (VNHCM)", "port_code": "VNHCM", "date": "2026-10-06", "timestamp": "2026-10-06 14:00:00", "lat": 10.6375, "lon": 106.7642, "vessel_or_flight": "Trans Future 7", "is_current": 0, "notes": "Kiểm tra số khung số máy VIN từng xe khi lăn bánh xuống bãi."},
                {"milestone": "GATE_OUT", "activity": "Hoàn tất đăng kiểm hải quan & Xe lồng vận chuyển ra cổng", "location": "Hiep Phuoc Port (VNHCM)", "port_code": "VNHCM", "date": "2026-10-07", "timestamp": "2026-10-07 09:30:00", "lat": 10.6375, "lon": 106.7642, "vessel_or_flight": "Car-Carrier-Truck", "is_current": 0, "notes": "Xe chuyên dụng car carrier vận chuyển về Trung tâm PDI."},
                {"milestone": "DELIVERED", "activity": "Bàn giao hoàn tất tại Trung tâm PDI Yard Toyota Việt Nam", "location": "Toyota VN Vehicle DC / PDI Yard", "port_code": "VNHCM", "date": "2026-10-07", "timestamp": "2026-10-07 15:30:00", "lat": 10.6385, "lon": 106.7455, "vessel_or_flight": "Car-Carrier-Truck", "is_current": 0, "notes": "Ký biên bản nghiệm thu xe mới và đưa vào quy trình PDI xuất xưởng."}
            ]
        },

        # 6. HONDA RORO / CONTAINER (THLCH -> Cat Lai -> Honda Vehicle DC)
        {
            "po_name": "PO-HONDA-2026-006",
            "st_name": "ST-HONDA-RORO-06",
            "supplier": "Honda Vietnam/Thailand Co.",
            "supplier_address": "Honda Rojana Plant-Billing",
            "shipping_method": "Ocean",
            "carrier": "\"K\" Line (Kawasaki Kisen Kaisha)",
            "vessel_name": "Drive Green Highway",
            "tracking_number": "KLINE-THVN-663306",
            "container_id": "KKFU9912045",
            "bill_of_lading": "BL-KLINE-TH-06",
            "origin_port": "Laem Chabang Port (THLCH)",
            "destination_port": "Cat Lai Port (VNSGN)",
            "dest_warehouse": "Honda VN Vehicle DC / PDI Yard - CK",
            "etd": "2026-10-01",
            "atd": "2026-10-01",
            "initial_eta": "2026-10-04",
            "eta": "2026-10-04",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "current_lat": 8.80,
            "current_lon": 104.90,
            "items": [
                {"item_code": "HONDA-HR-V", "qty": 30, "rate": 22800.0},
                {"item_code": "HONDA-REBEL-500", "qty": 50, "rate": 5600.0},
                {"item_code": "HONDA-CBR650R", "qty": 40, "rate": 8400.0}
            ],
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ vận tải xe máy PKL & Ô tô CBU từ Nhà máy Honda Rojana", "location": "Honda Ayutthaya Plant", "port_code": "THLCH", "date": "2026-09-28", "timestamp": "2026-09-28 09:30:00", "lat": 14.3388, "lon": 100.6338, "vessel_or_flight": "Drive Green Highway", "is_current": 0, "notes": "Xe máy đóng thùng sắt chuyên dụng, ô tô kiểm tra trước khi xuất cảng."},
                {"milestone": "GATE_IN", "activity": "Lô hàng hạ bãi tại Cảng Laem Chabang", "location": "Laem Chabang Port (THLCH)", "port_code": "THLCH", "date": "2026-09-30", "timestamp": "2026-09-30 15:30:00", "lat": 13.0833, "lon": 100.8833, "vessel_or_flight": "Drive Green Highway", "is_current": 0, "notes": "Hạ bãi cảng biển Laem Chabang, kiểm tra seal chì."},
                {"milestone": "LOADED", "activity": "Bốc xếp hàng lên tàu RoRo / Container Drive Green Highway", "location": "Laem Chabang Port (THLCH)", "port_code": "THLCH", "date": "2026-10-01", "timestamp": "2026-10-01 08:00:00", "lat": 13.0833, "lon": 100.8833, "vessel_or_flight": "Drive Green Highway", "is_current": 0, "notes": "Chằng buộc chắc chắn trong khoang tàu thân thiện môi trường \"K\" Line."},
                {"milestone": "DEPARTED", "activity": "Tàu Drive Green Highway rời Cảng Laem Chabang", "location": "Laem Chabang Port (THLCH)", "port_code": "THLCH", "date": "2026-10-01", "timestamp": "2026-10-01 13:00:00", "lat": 13.0833, "lon": 100.8833, "vessel_or_flight": "Drive Green Highway", "is_current": 0, "notes": "Hành trình hướng về Cát Lái theo đúng tiến độ."},
                {"milestone": "TRANSSHIPMENT", "activity": "Hành trình vùng biển Côn Đảo hướng vào luồng Soài Rạp / Lòng Tàu", "location": "Con Dao Fairway", "port_code": "THLCH", "date": "2026-10-02", "timestamp": "2026-10-02 09:00:00", "lat": 8.80, "lon": 104.90, "vessel_or_flight": "Drive Green Highway", "is_current": 1, "notes": "Vận tốc 16.0 knots, duy trì đúng kế hoạch cập cảng ngày 04/10."},
                {"milestone": "ARRIVED", "activity": "Tàu cập cảng Cát Lái", "location": "Cat Lai Port (VNSGN)", "port_code": "VNCLI", "date": "2026-10-04", "timestamp": "2026-10-04 07:30:00", "lat": 10.7626, "lon": 106.7898, "vessel_or_flight": "Drive Green Highway", "is_current": 0, "notes": "Hoa tiêu dẫn luồng cập bến an toàn."},
                {"milestone": "DISCHARGED", "activity": "Dỡ container xe máy và xe CBU xuống bãi cảng", "location": "Cat Lai Port (VNSGN)", "port_code": "VNCLI", "date": "2026-10-04", "timestamp": "2026-10-04 12:00:00", "lat": 10.7626, "lon": 106.7898, "vessel_or_flight": "Drive Green Highway", "is_current": 0, "notes": "Tiến hành rút ruột kiểm hóa mô tô phân khối lớn."},
                {"milestone": "GATE_OUT", "activity": "Hoàn tất đăng kiểm và xe chuyên dụng rời cổng cảng Cát Lái", "location": "Cat Lai Port (VNSGN)", "port_code": "VNCLI", "date": "2026-10-05", "timestamp": "2026-10-05 08:30:00", "lat": 10.7626, "lon": 106.7898, "vessel_or_flight": "Car-Carrier-Truck", "is_current": 0, "notes": "Vận chuyển nội địa về trung tâm xe chuyên dụng."},
                {"milestone": "DELIVERED", "activity": "Bàn giao xe tại Honda VN Vehicle DC / PDI Yard", "location": "Honda VN Vehicle DC / PDI Yard", "port_code": "VNCLI", "date": "2026-10-05", "timestamp": "2026-10-05 14:00:00", "lat": 10.6420, "lon": 106.7490, "vessel_or_flight": "Car-Carrier-Truck", "is_current": 0, "notes": "Nhập kho PDI hoàn tất, kiểm tra số khung xe mô tô Rebel và CBR."}
            ]
        },

        # 7. YAMAHA SEA (JPYOK -> Hai Phong -> VN-NORTH Vehicle DC)
        {
            "po_name": "PO-YAMAHA-2026-007",
            "st_name": "ST-YAMAHA-SEA-07",
            "supplier": "Yamaha Motor Co., Ltd.",
            "supplier_address": "Yamaha Motor Iwata Headquarters-Billing",
            "shipping_method": "Ocean",
            "carrier": "NYK Line (Nippon Yusen Kaisha)",
            "vessel_name": "NYK Apollo",
            "tracking_number": "NYK-JPYOK-771107",
            "container_id": "NYKU4490123",
            "bill_of_lading": "BL-NYK-YOK-07",
            "origin_port": "Yokohama Port (JPYOK)",
            "destination_port": "Hai Phong Port (VNHPH)",
            "dest_warehouse": "VN-NORTH Vehicle DC - CK",
            "etd": "2026-09-26",
            "atd": "2026-09-26",
            "initial_eta": "2026-10-03",
            "eta": "2026-10-03",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "current_lat": 26.50,
            "current_lon": 125.80,
            "items": [
                {"item_code": "YAMAHA-MT07", "qty": 40, "rate": 7500.0},
                {"item_code": "YAMAHA-MT09", "qty": 30, "rate": 9900.0},
                {"item_code": "YAMAHA-TENERE-700", "qty": 25, "rate": 10800.0}
            ],
            "milestones": [
                {"milestone": "BOOKED", "activity": "Đặt chỗ hãng tàu NYK Line từ Trụ sở chính Yamaha Motor Iwata", "location": "Yamaha Motor Iwata Headquarters", "port_code": "JPYOK", "date": "2026-09-23", "timestamp": "2026-09-23 09:00:00", "lat": 34.7228, "lon": 137.8773, "vessel_or_flight": "NYK Apollo", "is_current": 0, "notes": "Xe mô tô Nhật Bản CBU đóng khung thép bảo vệ chuyên dụng."},
                {"milestone": "GATE_IN", "activity": "Container NYKU4490123 hạ bãi Cảng Yokohama Honmoku Terminal", "location": "Yokohama Port (JPYOK)", "port_code": "JPYOK", "date": "2026-09-25", "timestamp": "2026-09-25 15:00:00", "lat": 35.4435, "lon": 139.6644, "vessel_or_flight": "NYK Apollo", "is_current": 0, "notes": "Hạ bãi xuất khẩu cảng Yokohama, hoàn tất thủ tục hải quan Nhật."},
                {"milestone": "LOADED", "activity": "Cẩu bốc container lên tàu mẹ NYK Apollo", "location": "Yokohama Port (JPYOK)", "port_code": "JPYOK", "date": "2026-09-26", "timestamp": "2026-09-26 08:30:00", "lat": 35.4435, "lon": 139.6644, "vessel_or_flight": "NYK Apollo", "is_current": 0, "notes": "Xếp container vào hầm hàng chuyên dụng tàu biển."},
                {"milestone": "DEPARTED", "activity": "Tàu NYK Apollo rời Cảng Yokohama", "location": "Yokohama Port (JPYOK)", "port_code": "JPYOK", "date": "2026-09-26", "timestamp": "2026-09-26 14:00:00", "lat": 35.4435, "lon": 139.6644, "vessel_or_flight": "NYK Apollo", "is_current": 0, "notes": "Hành trình ra Thái Bình Dương vượt qua chuỗi đảo Ryukyu."},
                {"milestone": "TRANSSHIPMENT", "activity": "Hải trình trên Biển Hoa Đông tiếp cận Eo biển Luzon", "location": "East China Sea / Ryukyu Fairway", "port_code": "JPYOK", "date": "2026-10-02", "timestamp": "2026-10-02 07:00:00", "lat": 26.50, "lon": 125.80, "vessel_or_flight": "NYK Apollo", "is_current": 1, "notes": "Vận tốc hải trình 17.8 knots, hướng thẳng vào Vịnh Bắc Bộ."},
                {"milestone": "ARRIVED", "activity": "Tàu cập Cảng Lạch Huyện Hải Phòng", "location": "Hai Phong Port (VNHPH)", "port_code": "VNHPH", "date": "2026-10-03", "timestamp": "2026-10-03 15:00:00", "lat": 20.8656, "lon": 106.7620, "vessel_or_flight": "NYK Apollo", "is_current": 0, "notes": "Dự kiến cập cảng nước sâu quốc tế Lạch Huyện."},
                {"milestone": "DISCHARGED", "activity": "Dỡ container xe mô tô CBU xuống bãi cảng Đình Vũ", "location": "Hai Phong Port (VNHPH)", "port_code": "VNHPH", "date": "2026-10-03", "timestamp": "2026-10-03 19:30:00", "lat": 20.8656, "lon": 106.7620, "vessel_or_flight": "NYK Apollo", "is_current": 0, "notes": "Kiểm tra tình trạng seal chì và thông báo hàng đến NOA."},
                {"milestone": "GATE_OUT", "activity": "Thông quan điện tử & Xe rơ-moóc kéo container ra cổng", "location": "Hai Phong Port (VNHPH)", "port_code": "VNHPH", "date": "2026-10-04", "timestamp": "2026-10-04 09:00:00", "lat": 20.8656, "lon": 106.7620, "vessel_or_flight": "Truck-Heavy", "is_current": 0, "notes": "Rời cảng di chuyển về Trung tâm phân phối phương tiện miền Bắc."},
                {"milestone": "DELIVERED", "activity": "Khui thùng và bàn giao xe tại VN-NORTH Vehicle DC", "location": "VN-NORTH Vehicle DC", "port_code": "VNHPH", "date": "2026-10-04", "timestamp": "2026-10-04 14:00:00", "lat": 20.8350, "lon": 106.7850, "vessel_or_flight": "Truck-Heavy", "is_current": 0, "notes": "Bàn giao lô mô tô MT-07, MT-09 và Ténéré 700 vào trung tâm phân phối."}
            ]
        }
    ]

# ==============================================================================
# MASTER SETUP (R3)
# ==============================================================================

def ensure_master_setup():
    if not frappe or not hasattr(frappe, "db") or not frappe.db:
        print("[!] Frappe not connected. Skipping DB schema migration.")
        return

    print(">>> 1. Kiểm tra và thiết lập Company, DocTypes, Kho bãi...")
    company = "Cap Khanh Logistics"

    # 1. Setup Wizard
    if not frappe.db.get_single_value("System Settings", "setup_complete") or not frappe.db.exists("Company", company):
        from erpnext.setup.setup_wizard.setup_wizard import setup_complete
        setup_data = frappe._dict({
            "language": "vi",
            "country": "Vietnam",
            "timezone": "Asia/Ho_Chi_Minh",
            "currency": "VND",
            "full_name": "Cap Kim Khanh",
            "email": "capkimkhanh@gmail.com",
            "company_name": company,
            "company_abbr": "CK",
            "chart_of_accounts": "Standard",
            "fy_start_date": "2026-01-01",
            "fy_end_date": "2026-12-31",
            "bank_account": "Vietcombank",
        })
        setup_complete(setup_data)
        frappe.db.set_single_value("System Settings", "setup_complete", 1)
        frappe.db.set_default("desktop:home_page", "workspace")
        frappe.db.commit()
        print("   ✓ Đã hoàn tất Setup Wizard cho Cap Khanh Logistics")
    for app in frappe.get_all("Installed Application"):
        frappe.db.set_value("Installed Application", app.name, "is_setup_complete", 1)
    frappe.db.set_single_value("System Settings", "setup_complete", 1)
    frappe.db.set_single_value("System Settings", "allow_login_using_user_name", 1)
    frappe.db.set_default("desktop:home_page", "workspace")

    from frappe.utils.password import update_password

    # Configure Administrator username 'admin' and password 'admin'
    admin = frappe.get_doc("User", "Administrator")
    admin.username = "admin"
    admin.save(ignore_permissions=True)
    update_password("Administrator", "admin")

    # Configure user capkimkhanh@gmail.com
    user_email = "capkimkhanh@gmail.com"
    if not frappe.db.exists("User", user_email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": user_email,
            "first_name": "Cap Kim Khanh",
            "enabled": 1,
            "send_welcome_email": 0,
            "user_type": "System User"
        })
        user.insert(ignore_permissions=True)
    else:
        user = frappe.get_doc("User", user_email)
        user.enabled = 1
        user.save(ignore_permissions=True)

    user.add_roles(
        "System Manager",
        "Purchase Manager",
        "Purchase User",
        "Stock Manager",
        "Stock User",
        "Accounts Manager",
        "Accounts User"
    )
    update_password(user_email, "admin")
    frappe.db.commit()

    # 2. Module Def
    if not frappe.db.exists("Module Def", "Logistics Wizard"):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "Logistics Wizard",
            "app_name": "logistics_wizard",
            "custom": 0
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    # 2.1 Bank Accounts (VND & USD)
    if not frappe.db.exists("Bank", "Vietcombank"):
        frappe.get_doc({
            "doctype": "Bank",
            "bank_name": "Vietcombank",
            "swift_number": "BFTVVNVX"
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Bank Account", {"account_name": "Vietcombank VND - CK"}):
        frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": "Vietcombank VND - CK",
            "bank": "Vietcombank",
            "account": "Vietcombank - CK",
            "bank_account_no": "0071001234567",
            "company": company,
            "is_default": 1
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Bank Account", {"account_name": "Vietcombank USD - CK"}):
        frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": "Vietcombank USD - CK",
            "bank": "Vietcombank",
            "account": "USD Bank Account - CK",
            "bank_account_no": "0071009876543",
            "company": company,
            "is_company_account": 1
        }).insert(ignore_permissions=True)

    # 2.2 Payment Terms Template
    tpl_name = "30% Advance, 70% on Delivery"
    if not frappe.db.exists("Payment Term", "30% Advance Deposit"):
        frappe.get_doc({
            "doctype": "Payment Term",
            "payment_term_name": "30% Advance Deposit",
            "invoice_portion": 30.0,
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 0,
            "description": "Thanh toán đặt cọc 30% ngay khi ký hợp đồng/phát hành PO"
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Payment Term", "70% on Delivery"):
        frappe.get_doc({
            "doctype": "Payment Term",
            "payment_term_name": "70% on Delivery",
            "invoice_portion": 70.0,
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 30,
            "description": "Thanh toán 70% còn lại sau khi nhận hàng tại cảng"
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Payment Terms Template", tpl_name):
        frappe.get_doc({
            "doctype": "Payment Terms Template",
            "template_name": tpl_name,
            "allocate_payment_based_on_payment_terms": 1,
            "terms": [
                {"payment_term": "30% Advance Deposit", "invoice_portion": 30.0, "due_date_based_on": "Day(s) after invoice date", "credit_days": 0},
                {"payment_term": "70% on Delivery", "invoice_portion": 70.0, "due_date_based_on": "Day(s) after invoice date", "credit_days": 30}
            ]
        }).insert(ignore_permissions=True)
    frappe.db.commit()

    # 3. Child DocType Transit Route (12 fields theo chuẩn DCSA quốc tế)
    tr_fields = [
        {"fieldname": "milestone", "fieldtype": "Select", "options": "BOOKED\nGATE_IN\nLOADED\nDEPARTED\nTRANSSHIPMENT\nARRIVED\nDISCHARGED\nGATE_OUT\nDELIVERED", "label": "Milestone / Mốc DCSA", "in_list_view": 1, "reqd": 1},
        {"fieldname": "activity", "fieldtype": "Data", "label": "Activity / Trạng thái", "in_list_view": 1, "reqd": 1},
        {"fieldname": "location", "fieldtype": "Data", "label": "Location / Địa điểm", "in_list_view": 1, "reqd": 1},
        {"fieldname": "port_code", "fieldtype": "Data", "label": "Port Code", "in_list_view": 1},
        {"fieldname": "date", "fieldtype": "Date", "label": "Date / Ngày", "in_list_view": 1},
        {"fieldname": "timestamp", "fieldtype": "Datetime", "label": "Timestamp / Thời điểm"},
        {"fieldname": "lat", "fieldtype": "Float", "label": "Vĩ độ (Lat)"},
        {"fieldname": "lon", "fieldtype": "Float", "label": "Kinh độ (Lon)"},
        {"fieldname": "vessel_or_flight", "fieldtype": "Data", "label": "Phương tiện (Vessel/Flight)"},
        {"fieldname": "dedup_hash", "fieldtype": "Data", "label": "Hash khử trùng lặp"},
        {"fieldname": "is_current", "fieldtype": "Check", "label": "Chặng hiện tại (Current)", "default": 0},
        {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes / Ghi chú"}
    ]

    if not frappe.db.exists("DocType", "Transit Route"):
        dt_tr = frappe.get_doc({
            "doctype": "DocType",
            "name": "Transit Route",
            "module": "Logistics Wizard",
            "custom": 1,
            "istable": 1,
            "editable_grid": 1,
            "fields": tr_fields
        })
        dt_tr.insert(ignore_permissions=True)
        frappe.db.commit()
    else:
        dt_tr = frappe.get_doc("DocType", "Transit Route")
        existing_tr_fields = {f.fieldname: f for f in dt_tr.fields}
        modified_tr = False
        for f_def in tr_fields:
            if f_def["fieldname"] not in existing_tr_fields:
                dt_tr.append("fields", f_def)
                modified_tr = True
        if modified_tr:
            dt_tr.save(ignore_permissions=True)
            frappe.db.commit()

    # 4. Master DocType Shipment Tracking
    st_fields = [
        {"fieldname": "section_details", "fieldtype": "Section Break", "label": "Thông tin Vận đơn (Shipment Details)"},
        {"fieldname": "flow_type", "fieldtype": "Select", "options": "Import\nExport", "label": "Loại hình Logistics (Flow Type)", "default": "Import", "in_list_view": 1},
        {"fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "label": "Purchase Order / Đơn mua hàng", "in_list_view": 1},
        {"fieldname": "purchase_receipt", "fieldtype": "Link", "options": "Purchase Receipt", "label": "Purchase Receipt / Phiếu nhận hàng"},
        {"fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "label": "Sales Order / Đơn bán hàng xuất khẩu"},
        {"fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "label": "Delivery Note / Phiếu xuất kho giao hàng"},
        {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Khách hàng quốc tế (Customer)"},
        {"fieldname": "shipping_method", "fieldtype": "Select", "options": "Air\nOcean\nRoad", "label": "Phương thức vận chuyển (Method)", "in_list_view": 1, "default": "Ocean", "reqd": 1},
        {"fieldname": "carrier", "fieldtype": "Data", "label": "Hãng vận chuyển (Carrier)", "in_list_view": 1},
        {"fieldname": "col_break_1", "fieldtype": "Column Break"},
        {"fieldname": "tracking_number", "fieldtype": "Data", "label": "Mã vận đơn (Tracking Number)", "in_list_view": 1},
        {"fieldname": "container_id", "fieldtype": "Data", "label": "Số Container (Container No.)", "in_list_view": 1},
        {"fieldname": "bill_of_lading", "fieldtype": "Data", "label": "Số Vận đơn (B/L No.)", "in_list_view": 1},
        {"fieldname": "air_waybill", "fieldtype": "Data", "label": "Vận đơn hàng không (AWB No.)", "in_list_view": 1},
        {"fieldname": "vessel_name", "fieldtype": "Data", "label": "Tên tàu (Vessel Name)"},
        {"fieldname": "flight_number", "fieldtype": "Data", "label": "Số hiệu chuyến bay (Flight No.)"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nIn Transit\nCustoms Clearance\nCompleted\nCancelled\nDelayed", "label": "Trạng thái vận đơn", "default": "Draft", "in_list_view": 1},
        {"fieldname": "etd", "fieldtype": "Date", "label": "Ngày khởi hành dự kiến (ETD)"},
        {"fieldname": "atd", "fieldtype": "Date", "label": "Ngày khởi hành thực tế (ATD)"},
        {"fieldname": "initial_eta", "fieldtype": "Date", "label": "ETA ban đầu"},
        {"fieldname": "eta", "fieldtype": "Date", "label": "Ngày đến dự kiến (ETA)"},
        {"fieldname": "delay_days", "fieldtype": "Int", "label": "Số ngày trễ (Delay Days)", "default": 0},
        {"fieldname": "is_delayed", "fieldtype": "Check", "label": "Bị trễ lịch trình (Delayed)", "default": 0},
        {"fieldname": "is_stale", "fieldtype": "Check", "label": "Dữ liệu quá hạn (Stale Tracking)", "default": 0},
        {"fieldname": "current_lat", "fieldtype": "Float", "label": "Vĩ độ hiện tại (Current Latitude)"},
        {"fieldname": "current_lon", "fieldtype": "Float", "label": "Kinh độ hiện tại (Current Longitude)"},
        {"fieldname": "section_route", "fieldtype": "Section Break", "label": "Hành trình vận chuyển (Transit Route)"},
        {"fieldname": "origin_port", "fieldtype": "Data", "label": "Cảng/Sân bay xuất phát (Origin)"},
        {"fieldname": "col_break_2", "fieldtype": "Column Break"},
        {"fieldname": "destination_port", "fieldtype": "Data", "label": "Cảng/Sân bay đến (Destination)"},
        {"fieldname": "section_checkpoints", "fieldtype": "Section Break", "label": "Các trạm lộ trình (Checkpoints)"},
        {"fieldname": "transit_route", "fieldtype": "Table", "options": "Transit Route", "label": "Lộ trình chi tiết"}
    ]

    if not frappe.db.exists("DocType", "Shipment Tracking"):
        dt_st = frappe.get_doc({
            "doctype": "DocType",
            "name": "Shipment Tracking",
            "module": "Logistics Wizard",
            "custom": 1,
            "is_submittable": 0,
            "track_changes": 1,
            "autoname": "Prompt",
            "naming_rule": "Set by user",
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Stock User", "read": 1, "write": 1, "create": 1},
                {"role": "Purchase User", "read": 1, "write": 1, "create": 1}
            ],
            "fields": st_fields
        })
        dt_st.insert(ignore_permissions=True)
        frappe.db.commit()
    else:
        dt_st = frappe.get_doc("DocType", "Shipment Tracking")
        existing_fn = {f.fieldname: f for f in dt_st.fields}
        modified = False
        for f_def in st_fields:
            if f_def["fieldname"] not in existing_fn:
                dt_st.append("fields", f_def)
                modified = True
        if modified:
            dt_st.save(ignore_permissions=True)
            frappe.db.commit()

    # 4.1 Master DocType Shipment Exception
    exc_fields = [
        {"fieldname": "shipment_tracking", "fieldtype": "Link", "options": "Shipment Tracking", "label": "Shipment Tracking", "in_list_view": 1, "reqd": 1},
        {"fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "label": "Purchase Order", "in_list_view": 1},
        {"fieldname": "carrier", "fieldtype": "Data", "label": "Carrier / Hãng vận chuyển", "in_list_view": 1},
        {"fieldname": "container_id", "fieldtype": "Data", "label": "Container / Lot ID"},
        {"fieldname": "exception_type", "fieldtype": "Select", "options": "ETA Delay\nCustoms Hold\nRoute Deviation\nCarrier Rollover\nStale Tracking", "label": "Loại ngoại lệ", "in_list_view": 1, "default": "ETA Delay"},
        {"fieldname": "severity", "fieldtype": "Select", "options": "Warning\nCritical", "label": "Mức độ nghiêm trọng", "in_list_view": 1, "default": "Warning"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Open\nAcknowledged\nInvestigating\nResolved", "label": "Trạng thái xử lý", "in_list_view": 1, "default": "Open"},
        {"fieldname": "delay_days", "fieldtype": "Int", "label": "Số ngày delay", "default": 0},
        {"fieldname": "old_eta", "fieldtype": "Date", "label": "ETA cũ"},
        {"fieldname": "new_eta", "fieldtype": "Date", "label": "ETA mới"},
        {"fieldname": "description", "fieldtype": "Small Text", "label": "Mô tả nguyên nhân"}
    ]
    if not frappe.db.exists("DocType", "Shipment Exception"):
        dt_exc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Shipment Exception",
            "module": "Logistics Wizard",
            "custom": 1,
            "autoname": "Prompt",
            "naming_rule": "Set by user",
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Stock User", "read": 1, "write": 1, "create": 1},
                {"role": "Purchase User", "read": 1, "write": 1, "create": 1}
            ],
            "fields": exc_fields
        })
        dt_exc.insert(ignore_permissions=True)
        frappe.db.commit()

    # 5. Custom Fields on Purchase Order
    po_custom_fields = [
        {"dt": "Purchase Order", "fieldname": "etd", "label": "Ngày khởi hành dự kiến (ETD)", "fieldtype": "Date", "insert_after": "schedule_date"},
        {"dt": "Purchase Order", "fieldname": "customs_declaration_number", "label": "Số tờ khai hải quan", "fieldtype": "Data", "insert_after": "etd"},
        {"dt": "Purchase Order", "fieldname": "shipping_method", "label": "Phương thức vận chuyển", "fieldtype": "Select", "options": "Air\nOcean\nRoad", "insert_after": "customs_declaration_number"}
    ]
    for cf_data in po_custom_fields:
        cf_name = f"{cf_data['dt']}-{cf_data['fieldname']}"
        if not frappe.db.exists("Custom Field", cf_name):
            frappe.get_doc({"doctype": "Custom Field", **cf_data}).insert(ignore_permissions=True)

    # 5.1 UOMs (Pcs, Nos, Unit, Set)
    for uom in ["Nos", "Unit", "Pcs", "Set"]:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)

    # 5.2 Item Groups (3 nhóm ngành chuyên nghiệp R3)
    all_item_groups = "All Item Groups"
    for ig_name in ["Jewelry & Luxury Goods", "IT & Consumer Electronics", "Automotive & Vehicles"]:
        if not frappe.db.exists("Item Group", ig_name):
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": ig_name,
                "parent_item_group": all_item_groups,
                "is_group": 0
            }).insert(ignore_permissions=True)

    # 5.3 Supplier Groups (3 nhóm ngành)
    for sg_name in ["Jewelry & Luxury Goods", "IT & Consumer Electronics", "Automotive & Vehicles"]:
        if not frappe.db.exists("Supplier Group", sg_name):
            frappe.get_doc({
                "doctype": "Supplier Group",
                "supplier_group_name": sg_name,
                "parent_supplier_group": "All Supplier Groups",
                "is_group": 0
            }).insert(ignore_permissions=True)
    frappe.db.commit()

    # 6. Warehouses (Đầy đủ 10 kho phân vùng Bắc / Nam / Cảng / Sân bay / PDI Yard)
    all_wh = frappe.db.get_value("Warehouse", {"warehouse_name": "All Warehouses", "company": company}, "name")
    for wh_name in SIMULATION_WAREHOUSES:
        full_wh = f"{wh_name} - CK"
        if not frappe.db.exists("Warehouse", full_wh):
            frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": wh_name,
                "company": company,
                "parent_warehouse": all_wh,
                "is_group": 0
            }).insert(ignore_permissions=True)
    frappe.db.commit()

    # 7. Currency & Exchange Rate
    if frappe.db.exists("Currency", "USD"):
        frappe.db.set_value("Currency", "USD", "enabled", 1)
    if not frappe.db.exists("Currency Exchange", {"from_currency": "USD", "to_currency": "VND", "date": "2026-09-19"}):
        frappe.get_doc({
            "doctype": "Currency Exchange",
            "date": "2026-09-19",
            "from_currency": "USD",
            "to_currency": "VND",
            "exchange_rate": 25400.0,
            "for_buying": 1,
            "for_selling": 1
        }).insert(ignore_permissions=True)

    # 8. Accounts
    current_liabilities = frappe.db.get_value("Account", {"account_name": "Current Liabilities", "company": company}, "name")
    bank_accounts = frappe.db.get_value("Account", {"account_name": "Bank Accounts", "company": company}, "name")
    if not frappe.db.exists("Account", "Creditors USD - CK"):
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "Creditors USD",
            "company": company,
            "parent_account": current_liabilities,
            "account_type": "Payable",
            "account_currency": "USD"
        }).insert(ignore_permissions=True)
    if not frappe.db.exists("Account", "USD Bank Account - CK"):
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "USD Bank Account",
            "company": company,
            "parent_account": bank_accounts,
            "account_type": "Bank",
            "account_currency": "USD"
        }).insert(ignore_permissions=True)

    current_assets = frappe.db.get_value("Account", {"account_name": "Current Assets", "company": company}, "name")
    if not frappe.db.exists("Account", "Debtors USD - CK"):
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "Debtors USD",
            "company": company,
            "parent_account": current_assets,
            "account_type": "Receivable",
            "account_currency": "USD"
        }).insert(ignore_permissions=True)

    # 9. Opening Balance
    temp_opening = frappe.db.get_value("Account", {"account_name": "Temporary Opening", "company": company}, "name")
    if not frappe.db.exists("Journal Entry", {"voucher_type": "Opening Entry", "company": company}):
        jv = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Opening Entry",
            "company": company,
            "posting_date": "2026-01-01",
            "multi_currency": 1,
            "accounts": [
                {"account": "USD Bank Account - CK", "account_currency": "USD", "debit_in_account_currency": 5000000.0, "exchange_rate": 25400.0, "cost_center": "Main - CK"},
                {"account": temp_opening, "account_currency": "VND", "credit_in_account_currency": 5000000.0 * 25400.0, "exchange_rate": 1.0, "cost_center": "Main - CK"}
            ]
        })
        jv.insert(ignore_permissions=True)
        jv.submit()

    # 10. 7 Suppliers Quốc tế (R3)
    for s_info in SIMULATION_SUPPLIERS:
        s_name = s_info["supplier_name"]
        if not frappe.db.exists("Supplier", s_name):
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": s_name,
                "supplier_group": s_info["supplier_group"],
                "default_currency": "USD",
                "country": s_info["country"],
                "accounts": [{"company": company, "account": "Creditors USD - CK"}]
            }).insert(ignore_permissions=True)

        addr = s_info.get("address")
        if addr:
            addr_id = f"{addr['title']}-Billing"
            if not frappe.db.exists("Address", addr_id):
                frappe.get_doc({
                    "doctype": "Address",
                    "address_title": addr["title"],
                    "address_type": "Billing",
                    "address_line1": addr["line1"],
                    "city": addr["city"],
                    "country": addr["country"],
                    "pincode": addr.get("pincode", "100000"),
                    "is_primary_address": 1,
                    "links": [{"link_doctype": "Supplier", "link_name": s_name}]
                }).insert(ignore_permissions=True)

    # Company warehouse address
    if not frappe.db.exists("Address", "Cap Khanh Logistics Warehouse-Shipping"):
        frappe.get_doc({
            "doctype": "Address",
            "address_title": "Cap Khanh Logistics Warehouse",
            "address_type": "Shipping",
            "address_line1": "Khu Cong Nghe Cao, Duong D1, Quan 9",
            "city": "Ho Chi Minh City",
            "country": "Vietnam",
            "pincode": "700000",
            "is_primary_address": 1,
            "is_your_company_address": 1,
            "is_shipping_address": 1,
            "links": [{"link_doctype": "Company", "link_name": company}]
        }).insert(ignore_permissions=True)

    # Customer Global Importer LLC
    customer = "Global Importer LLC"
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer,
            "customer_group": "Commercial",
            "customer_type": "Company",
            "default_currency": "USD",
            "territory": "Rest Of The World",
            "accounts": [{"company": company, "account": "Debtors USD - CK"}]
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Address", "Global Importer LLC HQ-Billing"):
        frappe.get_doc({
            "doctype": "Address",
            "address_title": "Global Importer LLC HQ",
            "address_type": "Billing",
            "address_line1": "456 World Trade Center Blvd",
            "city": "Los Angeles",
            "state": "California",
            "country": "United States",
            "pincode": "90071",
            "is_primary_address": 1,
            "links": [{"link_doctype": "Customer", "link_name": customer}]
        }).insert(ignore_permissions=True)

    # 10.5 Customs Tariff Numbers (HS Codes)
    hs_codes_list = [
        ("7113.11", "Trang sức bằng bạc, có hoặc không mạ hoặc dát kim loại quý khác"),
        ("8517.13", "Điện thoại thông minh (Smartphones)"),
        ("8471.30", "Máy xử lý dữ liệu tự động xách tay dung lượng dưới 10kg (Laptops)"),
        ("8518.30", "Tai nghe có hoặc không kèm micro (Earphones & Headphones)"),
        ("8471.49", "Máy tính để bàn hoặc hệ thống máy tính khác"),
        ("8528.52", "Màn hình có khả năng kết nối trực tiếp với máy tính"),
        ("8471.50", "Khối xử lý dữ liệu tự động khác máy xách tay"),
        ("8704.21", "Xe ô tô chở hàng (Xe bán tải) tổng trọng lượng có tải không quá 5 tấn"),
        ("8703.40", "Xe ô tô chở người kết hợp động cơ đốt trong và mô tơ điện (Hybrid HEV)"),
        ("8711.40", "Mô tô có dung tích xi lanh từ trên 250cc đến 500cc"),
        ("8711.50", "Mô tô có dung tích xi lanh trên 500cc đến 800cc+")
    ]
    for hs, desc in hs_codes_list:
        if not frappe.db.exists("Customs Tariff Number", hs):
            frappe.get_doc({
                "doctype": "Customs Tariff Number",
                "tariff_number": hs,
                "description": desc
            }).insert(ignore_permissions=True)
    frappe.db.commit()

    # 11. 21 Items (R3: HS Chương 71, 84/85, 87) + 4 Items cũ
    exchange_rate = 25400.0
    for itm in SIMULATION_ITEMS:
        item_code = itm["item_code"]
        buying_rate_vnd = itm["buying_rate_usd"] * exchange_rate
        selling_rate_vnd = itm["selling_rate_usd"] * exchange_rate

        if not frappe.db.exists("Item", item_code):
            doc_itm = {
                "doctype": "Item",
                "item_code": item_code,
                "item_name": itm["item_name"],
                "item_group": itm["item_group"],
                "stock_uom": itm["stock_uom"],
                "is_stock_item": 1,
                "valuation_method": "FIFO",
                "standard_rate": selling_rate_vnd,
                "customs_tariff_number": itm.get("hs_code", ""),
                "description": itm["description"],
                "default_warehouse": itm.get("default_warehouse", "Stores - CK")
            }
            frappe.get_doc(doc_itm).insert(ignore_permissions=True)
        else:
            if itm.get("hs_code"):
                frappe.db.set_value("Item", item_code, "customs_tariff_number", itm["hs_code"])

        # Price Lists: Standard Buying & Standard Selling
        if not frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Buying"}):
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": "Standard Buying",
                "price_list_rate": buying_rate_vnd,
                "currency": "VND",
                "buying": 1
            }).insert(ignore_permissions=True)

        if not frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}):
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": "Standard Selling",
                "price_list_rate": selling_rate_vnd,
                "currency": "VND",
                "selling": 1
            }).insert(ignore_permissions=True)

    frappe.db.commit()
    print("   ✓ Master Data & System Setup hoàn tất 100% (7 Suppliers, 21 Items, 10 Warehouses)!")


# ==============================================================================
# TRANSACTIONAL DATA GENERATION & SIMULATION (R4)
# ==============================================================================

def run():
    if not frappe or not hasattr(frappe, "db") or not frappe.db:
        print("[!] Frappe not available. Cannot execute live DB transaction generator.")
        return

    frappe.set_user("Administrator")
    ensure_master_setup()

    company = "Cap Khanh Logistics"
    exchange_rate = 25400.0

    print("\n=== BẮT ĐẦU TẠO DỮ LIỆU ĐƠN HÀNG XUẤT NHẬP KHẨU VÀ 7 LÔ HÀNG MÔ PHỎNG DCSA ===")

    # Dọn dẹp giao dịch cũ để tạo mới đồng bộ
    try:
        frappe.db.sql("DELETE FROM `tabShipment Exception`")
        frappe.db.sql("DELETE FROM `tabTransit Route`")
        frappe.db.sql("DELETE FROM `tabShipment Tracking`")
        frappe.db.commit()
    except Exception:
        pass

    for dt in [
        "Payment Entry", "Sales Invoice", "Delivery Note", "Purchase Invoice",
        "Landed Cost Voucher", "Stock Entry", "Purchase Receipt",
        "Sales Order", "Purchase Order", "Material Request"
    ]:
        if not frappe.db.exists("DocType", dt):
            continue
        records = frappe.get_all(dt, filters={"docstatus": ["in", [0, 1]]}, fields=["name", "docstatus"])
        for r in records:
            try:
                doc = frappe.get_doc(dt, r.name)
                if doc.docstatus == 1:
                    doc.cancel()
                doc.delete()
            except Exception:
                pass
    frappe.db.commit()

    # --------------------------------------------------------------------------
    # BASELINE VERIFICATION SCENARIOS (Preserving compatibility for existing tests)
    # --------------------------------------------------------------------------
    print("\n[+] Khởi tạo baseline đơn hàng & shipment kiểm thử hệ thống:")

    # 1. PUR-ORD-2026-00001 & ST-2026-00001 (Ocean Long Beach -> Cat Lai)
    po0 = frappe.get_doc({
        "doctype": "Purchase Order",
        "name": "PUR-ORD-2026-00001",
        "company": company,
        "supplier": "Apple Inc.",
        "currency": "USD",
        "conversion_rate": exchange_rate,
        "buying_price_list": "Standard Buying",
        "transaction_date": "2026-08-12",
        "schedule_date": "2026-09-15",
        "shipping_method": "Ocean",
        "etd": "2026-08-15",
        "customs_declaration_number": "HQ-2026-APL-SEA01",
        "supplier_address": "Apple Park Headquarters-Billing",
        "shipping_address": "Cap Khanh Logistics Warehouse-Shipping",
        "items": [
            {"item_code": "IPHONE-16-PROMAX", "qty": 500, "rate": 1100.0, "schedule_date": "2026-09-15", "warehouse": "Cat Lai Port - CK"}
        ]
    })
    po0.insert(ignore_permissions=True)
    po0.submit()

    st0 = frappe.get_doc({
        "doctype": "Shipment Tracking",
        "name": "ST-2026-00001",
        "purchase_order": po0.name,
        "shipping_method": "Ocean",
        "carrier": "Maersk Line (Vessel: Maersk Mc-Kinney Moller)",
        "vessel_name": "Maersk Mc-Kinney Moller",
        "tracking_number": "MSK-USVN-882201",
        "bill_of_lading": "BL-2026-MSK-01",
        "container_id": "MSKU9988112",
        "origin_port": "Port of Long Beach",
        "destination_port": "Cat Lai Port, Ho Chi Minh",
        "etd": "2026-08-15",
        "atd": "2026-08-15",
        "initial_eta": "2026-09-14",
        "eta": "2026-09-14",
        "status": "Completed",
        "is_delayed": 0,
        "delay_days": 0,
        "current_lat": 10.7626,
        "current_lon": 106.7898,
        "transit_route": [
            {"milestone": "BOOKED", "activity": "Booking Confirmed", "location": "Apple Park, Cupertino", "date": "2026-08-12", "timestamp": "2026-08-12 09:00:00", "lat": 37.3346, "lon": -122.0090, "notes": "Hàng đóng container tại California."},
            {"milestone": "GATE_IN", "activity": "Container Gated In Terminal", "location": "Port of Long Beach", "date": "2026-08-14", "timestamp": "2026-08-14 14:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Hạ bãi cảng Long Beach."},
            {"milestone": "LOADED", "activity": "Container Loaded on Board", "location": "Port of Long Beach", "date": "2026-08-15", "timestamp": "2026-08-15 08:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Bốc container lên tàu Maersk."},
            {"milestone": "DEPARTED", "activity": "Vessel Departed Port of Loading", "location": "Port of Long Beach", "date": "2026-08-15", "timestamp": "2026-08-15 16:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Nhổ neo vượt Thái Bình Dương."},
            {"milestone": "TRANSSHIPMENT", "activity": "Mid-Pacific Transit", "location": "Hawaii Transit Hub", "date": "2026-08-25", "timestamp": "2026-08-25 12:00:00", "lat": 21.3069, "lon": -157.8583, "notes": "Hải trình qua Hawaii."},
            {"milestone": "ARRIVED", "activity": "Vessel Berthed at Terminal", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-09-14", "timestamp": "2026-09-14 07:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Cập cảng Cát Lái an toàn."},
            {"milestone": "DISCHARGED", "activity": "Container Discharged", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-09-14", "timestamp": "2026-09-14 11:30:00", "lat": 10.7626, "lon": 106.7898, "notes": "Dỡ container xuống bãi cảng."},
            {"milestone": "GATE_OUT", "activity": "Customs Cleared & Gate Out", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-09-15", "timestamp": "2026-09-15 10:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Xe drayage kéo hàng ra cổng."},
            {"milestone": "DELIVERED", "activity": "Final Delivery Completed", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-09-16", "timestamp": "2026-09-16 15:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Bàn giao kho hoàn tất."}
        ]
    })
    st0.insert(ignore_permissions=True)
    print(f"   ✓ Baseline PO: {po0.name} & Shipment: {st0.name}")

    # 2. ST-2026-00002 (Air SFO -> SGN)
    st_air0 = frappe.get_doc({
        "doctype": "Shipment Tracking",
        "name": "ST-2026-00002",
        "purchase_order": po0.name,
        "shipping_method": "Air",
        "carrier": "Vietnam Airlines Cargo (Flight: VN-CARGO-991)",
        "flight_number": "VN-CARGO-991",
        "tracking_number": "VN-AIR-774402",
        "air_waybill": "AWB-738-774402",
        "origin_port": "San Francisco Airport",
        "destination_port": "Tan Son Nhat Airport",
        "etd": "2026-09-18",
        "atd": "2026-09-18",
        "initial_eta": "2026-09-21",
        "eta": "2026-09-21",
        "status": "In Transit",
        "is_delayed": 0,
        "delay_days": 0,
        "current_lat": 35.7720,
        "current_lon": 140.3929,
        "transit_route": [
            {"milestone": "BOOKED", "activity": "Cargo Booking Confirmed", "location": "Apple Park, Cupertino", "date": "2026-09-17", "timestamp": "2026-09-17 10:00:00", "lat": 37.3346, "lon": -122.0090, "notes": "Hàng công nghệ cao xuất kho."},
            {"milestone": "GATE_IN", "activity": "Gated in SFO Cargo", "location": "San Francisco Airport", "date": "2026-09-18", "timestamp": "2026-09-18 01:00:00", "lat": 37.6213, "lon": -122.3790, "notes": "Soi chiếu an ninh hàng không SFO."},
            {"milestone": "LOADED", "activity": "Loaded on Aircraft", "location": "San Francisco Airport", "date": "2026-09-18", "timestamp": "2026-09-18 04:30:00", "lat": 37.6213, "lon": -122.3790, "notes": "Xếp hàng lên tàu bay."},
            {"milestone": "DEPARTED", "activity": "Flight Departed SFO", "location": "San Francisco Airport", "date": "2026-09-18", "timestamp": "2026-09-18 06:00:00", "lat": 37.6213, "lon": -122.3790, "notes": "Khởi hành qua Thái Bình Dương."},
            {"milestone": "TRANSSHIPMENT", "activity": "Cruising Tokyo Airspace", "location": "Tokyo Narita Airspace", "date": "2026-09-19", "timestamp": "2026-09-19 14:00:00", "lat": 35.7720, "lon": 140.3929, "is_current": 1, "notes": "Đang bay trên không phận Narita."},
            {"milestone": "ARRIVED", "activity": "Landing SGN", "location": "Tan Son Nhat Airport", "date": "2026-09-21", "timestamp": "2026-09-21 09:00:00", "lat": 10.8188, "lon": 106.6520, "notes": "Dự kiến hạ cánh Tân Sơn Nhất."},
            {"milestone": "DISCHARGED", "activity": "Discharged Cargo", "location": "Tan Son Nhat Airport", "date": "2026-09-21", "timestamp": "2026-09-21 11:00:00", "lat": 10.8188, "lon": 106.6520, "notes": "Dỡ hàng vào kho TCS."},
            {"milestone": "GATE_OUT", "activity": "Customs Cleared", "location": "Tan Son Nhat Airport", "date": "2026-09-21", "timestamp": "2026-09-21 15:00:00", "lat": 10.8188, "lon": 106.6520, "notes": "Thông quan xe tải ra cổng."},
            {"milestone": "DELIVERED", "activity": "Delivered to Warehouse", "location": "Tan Son Nhat Airport", "date": "2026-09-22", "timestamp": "2026-09-22 09:00:00", "lat": 10.8188, "lon": 106.6520, "notes": "Giao kho hoàn tất."}
        ]
    })
    st_air0.insert(ignore_permissions=True)
    print(f"   ✓ Baseline Air Shipment: {st_air0.name}")

    # 3. IMP-2026-001 (Container ABC123 with Delay Exception)
    po_imp = frappe.get_doc({
        "doctype": "Purchase Order",
        "name": "IMP-2026-001",
        "company": company,
        "supplier": "Apple Inc.",
        "currency": "USD",
        "conversion_rate": exchange_rate,
        "buying_price_list": "Standard Buying",
        "transaction_date": "2026-09-28",
        "schedule_date": "2026-10-12",
        "shipping_method": "Ocean",
        "etd": "2026-10-01",
        "customs_declaration_number": "HQ-2026-APL-IMP001",
        "supplier_address": "Apple Park Headquarters-Billing",
        "shipping_address": "Cap Khanh Logistics Warehouse-Shipping",
        "items": [
            {"item_code": "IPHONE-16-PROMAX", "qty": 300, "rate": 1100.0, "schedule_date": "2026-10-12", "warehouse": "Cat Lai Port - CK"}
        ]
    })
    po_imp.insert(ignore_permissions=True)
    po_imp.submit()

    st_imp = frappe.get_doc({
        "doctype": "Shipment Tracking",
        "name": "ST-IMP-2026-001",
        "purchase_order": po_imp.name,
        "shipping_method": "Ocean",
        "carrier": "Maersk Line",
        "vessel_name": "Maersk Mc-Kinney Moller",
        "tracking_number": "MAEU123456789",
        "container_id": "ABC123",
        "bill_of_lading": "BL-2026-MAERSK-01",
        "origin_port": "Port of Long Beach",
        "destination_port": "Cat Lai Port, Ho Chi Minh",
        "etd": "2026-10-01",
        "atd": "2026-10-01",
        "initial_eta": "2026-10-10",
        "eta": "2026-10-12",
        "delay_days": 2,
        "is_delayed": 1,
        "is_stale": 0,
        "status": "Delayed",
        "current_lat": 13.44,
        "current_lon": 144.79,
        "transit_route": [
            {"milestone": "BOOKED", "activity": "Container Loaded on Board Vessel", "location": "Port of Long Beach", "date": "2026-10-01", "timestamp": "2026-10-01 08:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Container ABC123 xếp xong lên tàu."},
            {"milestone": "GATE_IN", "activity": "Gate In Terminal", "location": "Port of Long Beach", "date": "2026-10-01", "timestamp": "2026-10-01 10:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Container hạ bãi."},
            {"milestone": "LOADED", "activity": "Vessel Loading Completed", "location": "Port of Long Beach", "date": "2026-10-01", "timestamp": "2026-10-01 14:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Đã bốc lên tàu."},
            {"milestone": "DEPARTED", "activity": "Vessel Departed Port of Loading", "location": "Port of Long Beach", "date": "2026-10-01", "timestamp": "2026-10-01 18:00:00", "lat": 33.7542, "lon": -118.2165, "notes": "Tàu xuất bến đúng lịch trình."},
            {"milestone": "TRANSSHIPMENT", "activity": "En Route Navigation Delay", "location": "Guam Oceanic Corridor", "date": "2026-10-06", "timestamp": "2026-10-06 12:00:00", "lat": 13.44, "lon": 144.79, "is_current": 1, "notes": "Vận tốc giảm do thời tiết, ETA dời từ 10/10 sang 12/10 (+2 ngày)."},
            {"milestone": "ARRIVED", "activity": "Scheduled Berth", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-10-12", "timestamp": "2026-10-12 08:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Dự kiến cập cảng."},
            {"milestone": "DISCHARGED", "activity": "Scheduled Discharge", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-10-12", "timestamp": "2026-10-12 14:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Dự kiến dỡ bãi."},
            {"milestone": "GATE_OUT", "activity": "Scheduled Gate Out", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-10-13", "timestamp": "2026-10-13 09:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Dự kiến ra cổng."},
            {"milestone": "DELIVERED", "activity": "Scheduled Delivery", "location": "Cat Lai Port, Ho Chi Minh", "date": "2026-10-13", "timestamp": "2026-10-13 16:00:00", "lat": 10.7626, "lon": 106.7898, "notes": "Dự kiến hoàn thành."}
        ]
    })
    st_imp.insert(ignore_permissions=True)

    exc_imp = frappe.get_doc({
        "doctype": "Shipment Exception",
        "name": "EXC-IMP-2026-001-01",
        "shipment_tracking": st_imp.name,
        "purchase_order": po_imp.name,
        "carrier": "Maersk Line",
        "container_id": "ABC123",
        "exception_type": "ETA Delay",
        "severity": "Warning",
        "old_eta": "2026-10-10",
        "new_eta": "2026-10-12",
        "delay_days": 2,
        "status": "Open",
        "description": "Lịch trình tàu bị dời 2 ngày (từ 10/10 sang 12/10) do thời tiết tại hành lang Guam."
    })
    frappe.flags.in_import = True
    try:
        exc_imp.insert(ignore_permissions=True)
    finally:
        frappe.flags.in_import = False
    print(f"   ✓ Baseline Delay Scenario: {st_imp.name} & Exception: {exc_imp.name}")


    # --------------------------------------------------------------------------
    # 7 SIMULATION SUPPLY CHAINS (R4)
    # --------------------------------------------------------------------------
    print("\n[+] Bắt đầu tạo 7 Chuỗi Cung Ứng Mô Phỏng Toàn Diện (R4):")

    shipment_specs = get_simulation_shipments_specs()
    for idx, spec in enumerate(shipment_specs, start=1):
        print(f"\n--- Chuỗi Cung Ứng {idx}/7: {spec['supplier']} ({spec['shipping_method']}) ---")

        # 1. Purchase Order
        po_items = []
        for itm in spec["items"]:
            po_items.append({
                "item_code": itm["item_code"],
                "qty": itm["qty"],
                "rate": itm["rate"],
                "schedule_date": spec["eta"],
                "warehouse": spec["dest_warehouse"]
            })

        po_doc = frappe.get_doc({
            "doctype": "Purchase Order",
            "name": spec["po_name"],
            "company": company,
            "supplier": spec["supplier"],
            "currency": "USD",
            "conversion_rate": exchange_rate,
            "buying_price_list": "Standard Buying",
            "transaction_date": spec["etd"],
            "schedule_date": spec["eta"],
            "shipping_method": spec["shipping_method"],
            "etd": spec["etd"],
            "customs_declaration_number": f"HQ-2026-{spec['st_name']}",
            "supplier_address": spec["supplier_address"],
            "shipping_address": "Cap Khanh Logistics Warehouse-Shipping",
            "items": po_items
        })
        po_doc.insert(ignore_permissions=True)
        po_doc.submit()
        print(f"   ✓ [1] Purchase Order: {po_doc.name} (${po_doc.grand_total:,.2f} USD)")

        # 2. Transit Route Checkpoints (9 DCSA Milestones)
        tr_data = []
        for cp in spec["milestones"]:
            cp_hash = make_dedup_hash(spec["st_name"], cp["milestone"], cp["location"], cp["timestamp"])
            tr_data.append({
                "milestone": cp["milestone"],
                "activity": cp["activity"],
                "location": cp["location"],
                "port_code": cp.get("port_code", ""),
                "date": cp["date"],
                "timestamp": cp["timestamp"],
                "lat": cp["lat"],
                "lon": cp["lon"],
                "vessel_or_flight": cp["vessel_or_flight"],
                "is_current": cp.get("is_current", 0),
                "notes": cp.get("notes", ""),
                "dedup_hash": cp_hash
            })

        # 3. Shipment Tracking
        st_data = {
            "doctype": "Shipment Tracking",
            "name": spec["st_name"],
            "flow_type": "Import",
            "purchase_order": po_doc.name,
            "shipping_method": spec["shipping_method"],
            "carrier": spec["carrier"],
            "tracking_number": spec["tracking_number"],
            "origin_port": spec["origin_port"],
            "destination_port": spec["destination_port"],
            "etd": spec["etd"],
            "atd": spec["atd"],
            "initial_eta": spec["initial_eta"],
            "eta": spec["eta"],
            "delay_days": spec["delay_days"],
            "is_delayed": spec["is_delayed"],
            "is_stale": 0,
            "status": spec["status"],
            "current_lat": spec["current_lat"],
            "current_lon": spec["current_lon"],
            "transit_route": tr_data
        }
        if spec.get("container_id"):
            st_data["container_id"] = spec["container_id"]
        if spec.get("bill_of_lading"):
            st_data["bill_of_lading"] = spec["bill_of_lading"]
        if spec.get("air_waybill"):
            st_data["air_waybill"] = spec["air_waybill"]
        if spec.get("vessel_name"):
            st_data["vessel_name"] = spec["vessel_name"]
        if spec.get("flight_number"):
            st_data["flight_number"] = spec["flight_number"]

        st_doc = frappe.get_doc(st_data)
        st_doc.insert(ignore_permissions=True)
        print(f"   ✓ [2] Shipment Tracking: {st_doc.name} (Đầy đủ 9 mốc DCSA)")

        # 4. Optional Exception (e.g. Toyota Delay Scenario)
        if spec.get("exception"):
            exc_spec = spec["exception"]
            exc_doc = frappe.get_doc({
                "doctype": "Shipment Exception",
                "name": exc_spec["name"],
                "shipment_tracking": st_doc.name,
                "purchase_order": po_doc.name,
                "carrier": spec["carrier"],
                "container_id": spec.get("container_id", ""),
                "exception_type": exc_spec["exception_type"],
                "severity": exc_spec["severity"],
                "old_eta": exc_spec["old_eta"],
                "new_eta": exc_spec["new_eta"],
                "delay_days": exc_spec["delay_days"],
                "status": exc_spec["status"],
                "description": exc_spec["description"]
            })
            frappe.flags.in_import = True
            try:
                exc_doc.insert(ignore_permissions=True)
            finally:
                frappe.flags.in_import = False
            print(f"   ✓ [3] Shipment Exception: {exc_doc.name} ({exc_spec['severity']} - Delay +{exc_spec['delay_days']} ngày)")

    frappe.db.commit()
    print("\n🎉 HOÀN THÀNH TẠO 100% MASTER DATA (R3) VÀ 7 LÔ HÀNG MÔ PHỎNG DCSA QUỐC TẾ (R4)!")

if __name__ == "__main__":
    sites_dir = "/home/frappe/frappe-bench/sites"
    if os.path.exists(sites_dir):
        os.chdir(sites_dir)
    elif os.path.exists("sites"):
        os.chdir("sites")
    if frappe:
        frappe.init(site="logistics.local")
        frappe.connect()
        run()
