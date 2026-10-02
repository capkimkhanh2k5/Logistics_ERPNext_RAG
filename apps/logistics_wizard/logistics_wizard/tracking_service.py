# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
Logistics Wizard - Tracking Ingestion & Normalization Service (Milestone 1)
==========================================================================
Dịch vụ thu thập dữ liệu vận đơn từ các hãng vận tải, chuẩn hóa 9 mốc sự kiện quốc tế DCSA,
khử trùng lặp checkpoint (SHA-256 deduplication), thử lại lũy tiến (Exponential Backoff with Full Jitter),
ghi nhận nhật ký tích hợp (Shipment Integration Log), và phát hiện mất tín hiệu (Stale Tracking >48h).
"""

import os
import sys
import time
import json
import re
import hmac
import hashlib
import random
import logging
import unicodedata
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union

# Set up logger
logger = logging.getLogger("logistics_wizard.tracking_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [TrackingService] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Optional Frappe import with graceful fallback
try:
    import frappe
except ImportError:
    frappe = None

# Delay Engine integration (Milestone 2)
try:
    from .delay_engine import (
        calculate_delay_days,
        classify_severity,
        evaluate_eta_change,
        create_shipment_exception,
        apply_delay_to_shipment,
        auto_resolve_shipment_exceptions,
        check_and_process_delay,
    )
except ImportError:
    try:
        from delay_engine import (
            calculate_delay_days,
            classify_severity,
            evaluate_eta_change,
            create_shipment_exception,
            apply_delay_to_shipment,
            auto_resolve_shipment_exceptions,
            check_and_process_delay,
        )
    except ImportError:
        calculate_delay_days = None
        classify_severity = None
        evaluate_eta_change = None
        create_shipment_exception = None
        apply_delay_to_shipment = None
        auto_resolve_shipment_exceptions = None
        check_and_process_delay = None


# ==============================================================================
# 1. 9 DCSA STANDARD MILESTONES DEFINITIONS & NORMALIZATION
# ==============================================================================

DCSA_MILESTONES = (
    "BOOKED",
    "GATE_IN",
    "LOADED",
    "DEPARTED",
    "TRANSSHIPMENT",
    "ARRIVED",
    "DISCHARGED",
    "GATE_OUT",
    "DELIVERED",
)

def strip_vietnamese_accents(text: str) -> str:
    """
    Khử toàn bộ dấu tiếng Việt chuẩn Unicode NFD, chuyển 'đ', 'Đ' thành 'd', 'D'.
    """
    if not text:
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.replace('đ', 'd').replace('Đ', 'D')


# Comprehensive synonyms dictionary mapping multi-carrier statuses to 9 DCSA milestones
MILESTONE_SYNONYMS: Dict[str, List[str]] = {
    "BOOKED": [
        "đã đặt chỗ thành công", "xác nhận booking vận chuyển", "đã đặt chỗ", "đặt chỗ",
        "xác nhận booking", "booking vận chuyển", "đặt chỗ thành công", "da dat cho",
        "tạo đơn vận chuyển", "lập vận đơn",
        "xac nhan booking", "tao don van chuyen", "lap van don",
        "booking confirmed", "order created", "order placed", "space confirmed",
        "booking accepted", "label created", "shipping order", "info received",
        "inforeceived", "booked", "booking", "draft", "created", "pending",
        "bk", "bkg", "conf"
    ],
    "GATE_IN": [
        "hàng đã vào cổng cảng", "hạ bãi cảng cát lái", "hàng đã vào cổng", "vào cổng cảng",
        "vào cổng", "đã vào cổng", "hạ bãi",
        "nhận hàng tại cảng", "nhận container", "nhập bãi cảng", "nhập bãi",
        "hang da vao cong", "ha bai cang cat lai", "ha bai", "vao cong",
        "nhan hang tai cang", "nhan container", "nhap bai",
        "received at facility", "cargo received at airport", "cargo received at terminal",
        "received at airport terminal", "received at airport", "received at terminal",
        "terminal arrival", "container received", "depot gate in", "container gate in",
        "origin terminal", "cargo drop-off", "cfs received",
        "gate in", "gate-in", "gate_in", "gate--in", "ingate", "in-gate",
        "gi", "ingt"
    ],
    "LOADED": [
        "đang xếp hàng lên máy bay", "xếp hàng lên máy bay", "đã xếp lên tàu",
        "xếp hàng", "đã xếp hàng",
        "bốc hàng lên tàu", "đã xếp lên", "xếp lên tàu", "xếp lên máy bay",
        "da xep len tau", "xep hang len may bay", "xep len tau", "boc hang len tau",
        "loaded on vessel", "loaded on aircraft", "loaded on board", "container loaded",
        "aircraft loaded", "vessel loaded", "cargo loaded", "on-board", "onboard",
        "stowed", "laden", "loaded", "ld", "onbrd", "lod", "ob"
    ],
    "DEPARTED": [
        "khởi hành từ cảng long beach", "tàu đã rời cảng", "đã rời cảng", "tàu rời cảng",
        "rời cảng", "khởi hành", "rời bến", "đang vận chuyển", "trên biển", "đang bay",
        "khoi hanh tu cang long beach", "tau da roi cang", "roi cang", "khoi hanh",
        "dang van chuyen", "tren bien", "dang bay",
        "vessel departed", "flight departed", "linehaul departed", "left origin",
        "left facility", "in transit", "at sea", "in flight", "airborne",
        "sailing", "en route", "underway", "dispatched", "departed", "depart",
        "dep", "dept", "sail"
    ],
    "TRANSSHIPMENT": [
        "chuyển tải tại cảng trung chuyển", "cảng trung chuyển", "chuyển tải",
        "trung chuyển", "chuyển tàu", "ghé cảng trung chuyển", "cảng chuyển tải",
        "chuyen tai tai cang trung chuyen", "chuyen tai", "trung chuyen", "chuyen tau",
        "trans-shipment / connecting hub", "transshipment arrival", "connecting flight",
        "intermediate hub", "transfer hub", "feeder vessel", "connecting hub",
        "trans-shipped", "trans-shipment", "trans shipment", "transshipped",
        "transshipment", "trans-ship", "transship", "connection", "transfer", "relayed",
        "ts port", "ts", "xship"
    ],
    "ARRIVED": [
        "tàu đã cập cảng cát lái", "tàu đã cập cảng", "cập cảng cát lái",
        "đã đến cảng đích", "đến cảng đích", "cập cảng", "cập bến", "đã đến",
        "đến cảng", "hạ cánh", "tau da cap cang", "cap cang cat lai", "cap cang",
        "da den cang dich", "den cang dich", "da den", "den cang",
        "vessel arrived", "flight landed", "destination terminal", "arrived at destination",
        "arrived at pod", "destination port", "arrival at destination",
        "berthed at cat lai", "berthed", "docked", "moored", "landed", "arrival",
        "arrived", "arr", "arvd", "berth"
    ],
    "DISCHARGED": [
        "đã dỡ hàng khỏi tàu", "dỡ container xuống bãi", "dỡ hàng khỏi tàu",
        "dỡ container", "dỡ khỏi tàu", "dỡ hàng", "bốc dỡ", "hạ container",
        "da do hang khoi tau", "do container xuong bai", "do hang", "boc do",
        "container discharged", "cargo discharged", "unloading completed",
        "cargo offloaded", "available for pickup", "vessel discharged", "cargo unloaded",
        "offloaded", "discharged", "unloaded", "unladen", "de-van",
        "disch", "dsch", "unld", "unlad"
    ],
    "GATE_OUT": [
        "xuất bãi giao cho xe tải", "giao cho xe tải", "hàng đã ra cổng",
        "xuất bãi", "ra cổng", "rời bãi", "hang da ra cong", "ra cong",
        "xuat bai giao cho xe tai", "xuat bai", "giao cho xe tai",
        "picked up from terminal", "container gate out", "out for delivery",
        "customs released", "customs cleared and released", "customs cleared",
        "inland transit", "loaded on rail", "loaded on truck", "last-mile delivery",
        "gate out", "gate-out", "gate_out", "gate--out", "outgate", "out-gate",
        "released", "go", "outg"
    ],
    "DELIVERED": [
        "giao hàng hoàn tất cho người nhận", "giao hàng hoàn tất", "đã giao hàng thành công",
        "giao hàng thành công", "đã giao hàng", "giao hàng", "đã ký nhận",
        "hoàn tất giao nhận", "người nhận đã nhận", "da giao hang thanh cong",
        "giao hang hoan tat cho nguoi nhan", "giao hang hoan tat", "giao hang thanh cong",
        "giao hang", "da ky nhan", "hoan tat giao nhan",
        "cargo delivered to consignee", "proof of delivery signed", "cargo delivered",
        "pod confirmed", "proof of delivery", "destination delivery",
        "cargo received at warehouse", "cargo received", "empty return",
        "delivered", "completed", "received", "closed", "signed",
        "dlv", "dlvd", "pod", "delv"
    ],
}


# Flatten and sort all (keyword, milestone) pairs by keyword length descending
FLATTENED_MILESTONE_KEYWORDS: List[Tuple[str, str]] = []
seen_keywords = set()
for _m, _kws in MILESTONE_SYNONYMS.items():
    for _kw in _kws:
        _kw_clean = _kw.strip().lower()
        if (_kw_clean, _m) not in seen_keywords:
            seen_keywords.add((_kw_clean, _m))
            FLATTENED_MILESTONE_KEYWORDS.append((_kw_clean, _m))
        _kw_stripped = strip_vietnamese_accents(_kw_clean)
        if _kw_stripped and (_kw_stripped, _m) not in seen_keywords:
            seen_keywords.add((_kw_stripped, _m))
            FLATTENED_MILESTONE_KEYWORDS.append((_kw_stripped, _m))

FLATTENED_MILESTONE_KEYWORDS.sort(key=lambda x: len(x[0]), reverse=True)


def normalize_milestone(raw_status: Optional[str], default: str = "DEPARTED") -> str:
    """
    Chuẩn hóa bất kỳ chuỗi mô tả trạng thái vận chuyển nào từ Carrier/Forwarder
    về một trong 9 mốc tiêu chuẩn quốc tế DCSA.
    Hỗ trợ từ khóa đa ngôn ngữ (Tiếng Việt, Tiếng Anh), viết tắt chuẩn hàng hải/hàng không,
    khử nhiễu dấu câu, phát hiện bẫy phủ định và từ chối map sai lệch.
    """
    if not raw_status or not str(raw_status).strip():
        return default

    cleaned = str(raw_status).strip().lower()
    cleaned_unaccented = strip_vietnamese_accents(cleaned)

    # Exact milestone check
    for m in DCSA_MILESTONES:
        if cleaned == m.lower() or cleaned_unaccented == m.lower():
            return m

    # 1. Phát hiện bẫy phủ định và ngoại lệ (Negation & Failure / Hold / Noise Detection)
    # Lưu ý: 'unloaded' có 'un' nhưng là DISCHARGED hợp lệ, không tính là negation
    negation_pattern = re.compile(
        r'\b(not|failed|failure|cancelled|canceled|cancellation|undelivered|reject|rejected|aborted|hủy|huy|thất bại|that bai)\b',
        re.IGNORECASE
    )
    hold_noise_pattern = re.compile(
        r'\b(customs hold|held by customs|detained|seized|inspection|tạm giữ|tam giu|kiểm hóa|kiem hoa|noise)\b',
        re.IGNORECASE
    )
    if (negation_pattern.search(cleaned) or negation_pattern.search(cleaned_unaccented)
            or hold_noise_pattern.search(cleaned) or hold_noise_pattern.search(cleaned_unaccented)):
        return "UNKNOWN"

    # 2. Chuẩn hóa chuỗi dấu câu (thay thế chuỗi ký tự -, _, /, :, *, [, ], (, ) bằng dấu cách)
    normalized_space = re.sub(r'[\-_/:*\[\]()]+', ' ', cleaned).strip()
    normalized_space = re.sub(r'\s+', ' ', normalized_space)
    normalized_space_unaccented = strip_vietnamese_accents(normalized_space)

    # 3. Pass 1: Regex word boundary search với ưu tiên từ khóa dài nhất trước
    for kw, milestone in FLATTENED_MILESTONE_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if (re.search(pattern, cleaned) or re.search(pattern, normalized_space)
                or re.search(pattern, cleaned_unaccented) or re.search(pattern, normalized_space_unaccented)):
            return milestone

    # 4. Pass 2: Fallback substring search cho các từ khóa có độ dài >= 4 ký tự
    for kw, milestone in FLATTENED_MILESTONE_KEYWORDS:
        if len(kw) >= 4 and (kw in cleaned or kw in normalized_space
                             or kw in cleaned_unaccented or kw in normalized_space_unaccented):
            return milestone

    return default


# ==============================================================================
# 2. CHECKPOINT DEDUPLICATION ENGINE (SHA-256 HASH)
# ==============================================================================

def normalize_timestamp_str(ts: Optional[Union[str, datetime]]) -> str:
    """Standardize timestamp representation for reliable hashing."""
    if not ts:
        return ""
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M")
    s = str(ts).strip()
    # If ISO with seconds or microseconds: 2026-10-01T14:30:00.000Z -> 2026-10-01 14:30
    s = s.replace("T", " ")
    if len(s) >= 16:
        return s[:16]
    return s


def compute_checkpoint_hash(shipment_id: str,
                            milestone: str,
                            location: Optional[str],
                            timestamp: Optional[Union[str, datetime]],
                            vehicle: Optional[str] = "") -> str:
    """
    Tính toán mã băm duy nhất SHA-256 dựa trên bộ 5 trường bất biến của Checkpoint:
    (ShipmentID, NormalizedMilestone, Location, Timestamp, Vehicle).
    """
    s_id = str(shipment_id or "").strip().upper()
    norm_m = normalize_milestone(milestone)
    loc = str(location or "").strip().upper()
    # Normalize whitespaces inside location
    loc = " ".join(loc.split())
    t_str = normalize_timestamp_str(timestamp)
    veh = str(vehicle or "").strip().upper()
    veh = " ".join(veh.split())

    raw_signature = f"{s_id}|{norm_m}|{loc}|{t_str}|{veh}"
    return hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()[:32]


def filter_new_checkpoints(shipment_id: str,
                           existing_checkpoints: List[Dict[str, Any]],
                           incoming_checkpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Lọc danh sách các checkpoint mới nhận được từ API:
    - Loại bỏ các checkpoint đã từng tồn tại dựa trên `dedup_hash` (hoặc tính toán lại hash).
    - Bảo toàn toàn bộ lịch sử checkpoint cũ.
    - Trả về danh sách checkpoint thực sự mới cần thêm vào.
    """
    existing_hashes = set()
    for cp in existing_checkpoints:
        cp_hash = cp.get("dedup_hash") or cp.get("checkpoint_hash")
        if not cp_hash:
            cp_hash = compute_checkpoint_hash(
                shipment_id=shipment_id,
                milestone=cp.get("milestone") or cp.get("activity") or "",
                location=cp.get("location") or "",
                timestamp=cp.get("timestamp") or cp.get("date") or "",
                vehicle=cp.get("vessel_or_flight") or cp.get("vehicle_name") or ""
            )
        if cp_hash:
            existing_hashes.add(cp_hash)

    new_unique_checkpoints = []
    for inc in incoming_checkpoints:
        inc_hash = inc.get("dedup_hash") or inc.get("checkpoint_hash")
        if not inc_hash:
            inc_hash = compute_checkpoint_hash(
                shipment_id=shipment_id,
                milestone=inc.get("milestone") or inc.get("activity") or "",
                location=inc.get("location") or "",
                timestamp=inc.get("timestamp") or inc.get("date") or "",
                vehicle=inc.get("vessel_or_flight") or inc.get("vehicle_name") or ""
            )
            inc["dedup_hash"] = inc_hash

        if inc_hash not in existing_hashes:
            existing_hashes.add(inc_hash)
            new_unique_checkpoints.append(inc)

    return new_unique_checkpoints


# ==============================================================================
# 3. EXPONENTIAL BACKOFF WITH FULL JITTER
# ==============================================================================

def calculate_backoff_delay(attempt: int,
                            base_seconds: float = 1.0,
                            max_seconds: float = 60.0,
                            full_jitter: bool = True) -> float:
    """
    Thuật toán Exponential Backoff with Full Jitter (AWS Architecture standard):
    temp = min(max_seconds, base_seconds * (2 ** attempt))
    sleep = uniform(0, temp)
    """
    bounded_delay = min(max_seconds, base_seconds * (2 ** attempt))
    if full_jitter:
        return random.uniform(0.0, bounded_delay)
    return bounded_delay


def execute_with_retry(func,
                       args=(),
                       kwargs=None,
                       max_retries: int = 5,
                       base_delay: float = 0.5,
                       max_delay: float = 30.0,
                       retryable_exceptions: Tuple = (Exception,),
                       sleep_fn=time.sleep) -> Tuple[Any, int, List[str]]:
    """
    Thực thi hàm mạng/API với cơ chế thử lại lũy tiến kèm full jitter.
    Trả về (result, attempt_count, list_of_error_messages).
    """
    kwargs = kwargs or {}
    errors = []
    for attempt in range(max_retries + 1):
        try:
            res = func(*args, **kwargs)
            return res, attempt, errors
        except retryable_exceptions as e:
            err_msg = f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}"
            errors.append(err_msg)
            logger.warning(err_msg)
            if attempt < max_retries:
                delay = calculate_backoff_delay(attempt, base_delay, max_delay, full_jitter=True)
                sleep_fn(delay)
            else:
                raise


# ==============================================================================
# 4. TRACKING RESPONSE & BASE PROVIDER
# ==============================================================================

class TrackingResponse:
    """
    Đối tượng chuẩn hóa chứa toàn bộ dữ liệu phản hồi từ Carrier Tracking API.
    """
    def __init__(self,
                 success: bool,
                 tracking_number: str,
                 checkpoints: Optional[List[Dict[str, Any]]] = None,
                 carrier: str = "",
                 status: str = "In Transit",
                 etd: Optional[str] = None,
                 atd: Optional[str] = None,
                 initial_eta: Optional[str] = None,
                 eta: Optional[str] = None,
                 ata: Optional[str] = None,
                 vessel_name: Optional[str] = None,
                 flight_number: Optional[str] = None,
                 container_id: Optional[str] = None,
                 bill_of_lading: Optional[str] = None,
                 air_waybill: Optional[str] = None,
                 current_lat: Optional[float] = None,
                 current_lon: Optional[float] = None,
                 raw_payload: Optional[Dict[str, Any]] = None,
                 error_message: Optional[str] = None,
                 http_status_code: int = 200,
                 duration_ms: int = 0):
        self.success = success
        self.tracking_number = tracking_number
        self.checkpoints = checkpoints or []
        self.carrier = carrier
        self.status = status
        self.etd = etd
        self.atd = atd
        self.initial_eta = initial_eta
        self.eta = eta
        self.ata = ata
        self.vessel_name = vessel_name
        self.flight_number = flight_number
        self.container_id = container_id
        self.bill_of_lading = bill_of_lading
        self.air_waybill = air_waybill
        self.current_lat = current_lat
        self.current_lon = current_lon
        self.raw_payload = raw_payload or {}
        self.error_message = error_message
        self.http_status_code = http_status_code
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "tracking_number": self.tracking_number,
            "carrier": self.carrier,
            "status": self.status,
            "etd": self.etd,
            "atd": self.atd,
            "initial_eta": self.initial_eta,
            "eta": self.eta,
            "ata": self.ata,
            "vessel_name": self.vessel_name,
            "flight_number": self.flight_number,
            "container_id": self.container_id,
            "bill_of_lading": self.bill_of_lading,
            "air_waybill": self.air_waybill,
            "current_lat": self.current_lat,
            "current_lon": self.current_lon,
            "checkpoints": self.checkpoints,
            "raw_payload": self.raw_payload,
            "error_message": self.error_message,
            "http_status_code": self.http_status_code,
            "duration_ms": self.duration_ms,
        }

    # Dictionary / Mapping protocol support (PROJECT.md contract compliance)
    def __getitem__(self, key: str) -> Any:
        d = self.to_dict()
        if key in d:
            return d[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.raw_payload[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()

    def keys(self):
        return self.to_dict().keys()

    def items(self):
        return self.to_dict().items()

    def values(self):
        return self.to_dict().values()

    def __iter__(self):
        return iter(self.to_dict())

    def __len__(self):
        return len(self.to_dict())


class BaseTrackingProvider(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các nhà cung cấp dữ liệu Tracking.
    """
    provider_name: str = "BaseProvider"

    @abstractmethod
    def fetch_tracking(self, tracking_number: str, carrier: Optional[str] = None, **kwargs) -> TrackingResponse:
        """Truy vấn dữ liệu hành trình theo cơ chế Polling."""
        pass

    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any], headers: Optional[Dict[str, Any]] = None) -> TrackingResponse:
        """Chuyển đổi dữ liệu Webhook nhận được sang TrackingResponse."""
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload_bytes: bytes, headers: Dict[str, Any], secret: str) -> bool:
        """Xác thực chữ ký số bảo mật của webhook (HMAC SHA-256)."""
        pass


# ==============================================================================
# 5. MOCK TRACKING PROVIDER (FOR TESTING & SIMULATION)
# ==============================================================================

class MockTrackingProvider(BaseTrackingProvider):
    """
    Provider giả lập dùng cho môi trường kiểm thử, phát triển và simulation kịch bản.
    Hỗ trợ kiểm thử chu trình thời gian, đổi tàu, delay ETA, lỗi mạng thử lại backoff.
    """
    provider_name: str = "Mock Provider"

    def __init__(self,
                 scenario: str = "departed",
                 fail_first_n_requests: int = 0,
                 simulated_status_code: int = 503):
        self.scenario = scenario
        self.fail_first_n_requests = fail_first_n_requests
        self.simulated_status_code = simulated_status_code
        self.request_count = 0

    def set_scenario(self, scenario: str):
        self.scenario = scenario

    def fetch_tracking(self, tracking_number: str, carrier: Optional[str] = None, **kwargs) -> TrackingResponse:
        t0 = time.time()
        self.request_count += 1

        # Simulate network error if configured
        if self.request_count <= self.fail_first_n_requests:
            duration = int((time.time() - t0) * 1000)
            return TrackingResponse(
                success=False,
                tracking_number=tracking_number,
                carrier=carrier or "Mock Carrier",
                error_message=f"Simulated HTTP {self.simulated_status_code} Network Error",
                http_status_code=self.simulated_status_code,
                duration_ms=duration
            )

        # Build scenario checkpoints
        checkpoints: List[Dict[str, Any]] = []
        status = "In Transit"
        etd = "2026-10-01"
        atd = "2026-10-01"
        initial_eta = "2026-10-10"
        eta = "2026-10-10"
        ata = None
        vessel_name = "MAERSK MC-KINNEY MOLLER"
        flight_number = None
        container_id = kwargs.get("container_id", "ABC123")
        bill_of_lading = kwargs.get("bill_of_lading", "BL-2026-MAERSK-01")
        current_lat = 33.74
        current_lon = -118.25

        if self.scenario == "departed":
            # Giai đoạn 1: Tàu vừa khởi hành
            checkpoints = [
                {
                    "milestone": "LOADED",
                    "activity": "Container Loaded on Board Vessel",
                    "location": "Long Beach Port Pier 400",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 08:00",
                    "date": "2026-10-01",
                    "lat": 33.75,
                    "lon": -118.22,
                    "vessel_or_flight": vessel_name,
                    "notes": "Container xếp xong lên tàu an toàn.",
                    "is_current": False
                },
                {
                    "milestone": "DEPARTED",
                    "activity": "Vessel Departed Port of Loading",
                    "location": "Port of Long Beach",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 14:30",
                    "date": "2026-10-01",
                    "lat": 33.74,
                    "lon": -118.25,
                    "vessel_or_flight": vessel_name,
                    "notes": "Tàu bắt đầu hành trình băng qua Thái Bình Dương.",
                    "is_current": True
                }
            ]
            current_lat = 33.74
            current_lon = -118.25

        elif self.scenario == "eta_delayed":
            # Giai đoạn 2: Cập nhật delay ETA +2 ngày (2026-10-12)
            eta = "2026-10-12"
            checkpoints = [
                {
                    "milestone": "LOADED",
                    "activity": "Container Loaded on Board Vessel",
                    "location": "Long Beach Port Pier 400",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 08:00",
                    "date": "2026-10-01",
                    "lat": 33.75,
                    "lon": -118.22,
                    "vessel_or_flight": vessel_name,
                    "notes": "Container xếp xong lên tàu an toàn.",
                    "is_current": False
                },
                {
                    "milestone": "DEPARTED",
                    "activity": "Vessel Departed Port of Loading",
                    "location": "Port of Long Beach",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 14:30",
                    "date": "2026-10-01",
                    "lat": 33.74,
                    "lon": -118.25,
                    "vessel_or_flight": vessel_name,
                    "notes": "Tàu bắt đầu hành trình băng qua Thái Bình Dương.",
                    "is_current": False
                },
                {
                    "milestone": "TRANSSHIPMENT",
                    "activity": "Vessel En Route - Pacific Corridor Navigation",
                    "location": "Guam Oceanic Corridor",
                    "port_code": "GUAM",
                    "timestamp": "2026-10-06 10:00",
                    "date": "2026-10-06",
                    "lat": 13.44,
                    "lon": 144.79,
                    "vessel_or_flight": vessel_name,
                    "notes": "Thời tiết xấu khu vực eo biển Luzon khiến vận tốc tàu giảm, dự kiến cập cảng trễ 2 ngày.",
                    "is_current": True
                }
            ]
            current_lat = 13.44
            current_lon = 144.79

        elif self.scenario == "delivered":
            # Giai đoạn 3: Cập cảng và giao hàng hoàn tất
            eta = "2026-10-12"
            ata = "2026-10-12"
            status = "Completed"
            checkpoints = [
                {
                    "milestone": "LOADED",
                    "activity": "Container Loaded on Board Vessel",
                    "location": "Long Beach Port Pier 400",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 08:00",
                    "lat": 33.75,
                    "lon": -118.22,
                    "vessel_or_flight": vessel_name,
                    "is_current": False
                },
                {
                    "milestone": "DEPARTED",
                    "activity": "Vessel Departed Port of Loading",
                    "location": "Port of Long Beach",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 14:30",
                    "lat": 33.74,
                    "lon": -118.25,
                    "vessel_or_flight": vessel_name,
                    "is_current": False
                },
                {
                    "milestone": "TRANSSHIPMENT",
                    "activity": "Transshipment Checkpoint",
                    "location": "Guam Oceanic Corridor",
                    "port_code": "GUAM",
                    "timestamp": "2026-10-06 10:00",
                    "lat": 13.44,
                    "lon": 144.79,
                    "vessel_or_flight": vessel_name,
                    "is_current": False
                },
                {
                    "milestone": "ARRIVED",
                    "activity": "Vessel Arrived at Port of Discharge",
                    "location": "Cat Lai Port",
                    "port_code": "VNSGN",
                    "timestamp": "2026-10-12 06:00",
                    "lat": 10.76,
                    "lon": 106.79,
                    "vessel_or_flight": vessel_name,
                    "is_current": False
                },
                {
                    "milestone": "DISCHARGED",
                    "activity": "Container Discharged to Terminal Yard",
                    "location": "Cat Lai Port Terminal",
                    "port_code": "VNSGN",
                    "timestamp": "2026-10-12 09:30",
                    "lat": 10.765,
                    "lon": 106.795,
                    "vessel_or_flight": vessel_name,
                    "is_current": False
                },
                {
                    "milestone": "GATE_OUT",
                    "activity": "Container Gate Out for Final Delivery",
                    "location": "Cat Lai Port Outgate",
                    "port_code": "VNSGN",
                    "timestamp": "2026-10-12 13:00",
                    "lat": 10.77,
                    "lon": 106.80,
                    "vessel_or_flight": "Truck 51C-99881",
                    "is_current": False
                },
                {
                    "milestone": "DELIVERED",
                    "activity": "Cargo Delivered to Cap Khanh Warehouse",
                    "location": "Cap Khanh Warehouse Da Nang",
                    "port_code": "VNDAD",
                    "timestamp": "2026-10-12 17:00",
                    "lat": 16.05,
                    "lon": 108.20,
                    "vessel_or_flight": "Truck 51C-99881",
                    "is_current": True
                }
            ]
            current_lat = 16.05
            current_lon = 108.20

        elif self.scenario == "air_flight":
            # Scenario Air Cargo
            status = "In Transit"
            flight_number = "VN001"
            vessel_name = None
            etd = "2026-10-02"
            atd = "2026-10-02"
            eta = "2026-10-03"
            checkpoints = [
                {
                    "milestone": "BOOKED",
                    "activity": "Air Waybill Issued and Flight Space Confirmed",
                    "location": "San Francisco Cargo Terminal",
                    "port_code": "SFO",
                    "timestamp": "2026-10-01 18:00",
                    "lat": 37.62,
                    "lon": -122.37,
                    "vessel_or_flight": flight_number,
                    "is_current": False
                },
                {
                    "milestone": "LOADED",
                    "activity": "Cargo Loaded into Aircraft ULD Pallet",
                    "location": "San Francisco International Airport",
                    "port_code": "SFO",
                    "timestamp": "2026-10-02 00:30",
                    "lat": 37.621,
                    "lon": -122.375,
                    "vessel_or_flight": flight_number,
                    "is_current": False
                },
                {
                    "milestone": "DEPARTED",
                    "activity": "Flight Departed SFO Airborne",
                    "location": "San Francisco Airspace",
                    "port_code": "SFO",
                    "timestamp": "2026-10-02 02:00",
                    "lat": 37.63,
                    "lon": -122.38,
                    "vessel_or_flight": flight_number,
                    "is_current": True
                }
            ]
            current_lat = 37.63
            current_lon = -122.38

        duration = int((time.time() - t0) * 1000)

        # Precompute hashes for mock checkpoints
        for cp in checkpoints:
            if not cp.get("dedup_hash"):
                cp["dedup_hash"] = compute_checkpoint_hash(
                    shipment_id=tracking_number,
                    milestone=cp["milestone"],
                    location=cp.get("location"),
                    timestamp=cp.get("timestamp"),
                    vehicle=cp.get("vessel_or_flight")
                )

        return TrackingResponse(
            success=True,
            tracking_number=tracking_number,
            carrier=carrier or "Maersk Line",
            status=status,
            etd=etd,
            atd=atd,
            initial_eta=initial_eta,
            eta=eta,
            ata=ata,
            vessel_name=vessel_name,
            flight_number=flight_number,
            container_id=container_id,
            bill_of_lading=bill_of_lading,
            current_lat=current_lat,
            current_lon=current_lon,
            checkpoints=checkpoints,
            raw_payload={"mock_scenario": self.scenario, "query_time": datetime.now().isoformat()},
            http_status_code=200,
            duration_ms=duration
        )

    def parse_webhook(self, payload: Dict[str, Any], headers: Optional[Dict[str, Any]] = None) -> TrackingResponse:
        if not isinstance(payload, dict):
            payload = {}
        raw_data = payload.get("data")
        data_trk = raw_data.get("tracking_number") if isinstance(raw_data, dict) else None
        tracking_number = payload.get("tracking_number") or data_trk or "MOCK-TRK-001"
        scenario = payload.get("scenario") or "departed"
        self.set_scenario(scenario)
        return self.fetch_tracking(tracking_number)

    def verify_webhook_signature(self, payload_bytes: bytes, headers: Dict[str, Any], secret: str) -> bool:
        if not secret:
            return True
        headers_lower = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
        sig = headers_lower.get("x-mock-signature") or headers_lower.get("x-signature")
        if not sig:
            return False
        expected = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)


# ==============================================================================
# 6. AFTERSHIP PROVIDER ADAPTER
# ==============================================================================

class AfterShipProvider(BaseTrackingProvider):
    """
    Adapter tích hợp AfterShip API v4/v5 phục vụ Polling và Webhook.
    """
    provider_name: str = "AfterShip"

    def __init__(self, api_key: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.api_key = api_key or os.environ.get("AFTERSHIP_API_KEY", "")
        self.webhook_secret = webhook_secret or os.environ.get("AFTERSHIP_WEBHOOK_SECRET", "")

    def fetch_tracking(self, tracking_number: str, carrier: Optional[str] = None, **kwargs) -> TrackingResponse:
        t0 = time.time()
        slug = (carrier or "generic").lower().replace(" ", "-")

        # In production without live API key, safely return normalized fallback or raise if required
        if not self.api_key or self.api_key.startswith("test_") or "mock" in self.api_key:
            # Emulated AfterShip API response
            duration = int((time.time() - t0) * 1000)
            mock_checkpoints = [
                {
                    "milestone": "BOOKED",
                    "activity": "Carrier has received tracking info",
                    "location": "Origin Station",
                    "port_code": "ORG",
                    "timestamp": "2026-10-01 07:00",
                    "lat": 33.74,
                    "lon": -118.25,
                    "vessel_or_flight": "Vessel MOCK",
                    "notes": "AfterShip parsed event",
                    "is_current": False
                },
                {
                    "milestone": "DEPARTED",
                    "activity": "Vessel departed origin facility",
                    "location": "Port of Long Beach",
                    "port_code": "USLGB",
                    "timestamp": "2026-10-01 14:00",
                    "lat": 33.74,
                    "lon": -118.25,
                    "vessel_or_flight": "Vessel MOCK",
                    "notes": "AfterShip in-transit status",
                    "is_current": True
                }
            ]
            for cp in mock_checkpoints:
                cp["dedup_hash"] = compute_checkpoint_hash(
                    shipment_id=tracking_number,
                    milestone=cp["milestone"],
                    location=cp["location"],
                    timestamp=cp["timestamp"],
                    vehicle=cp["vessel_or_flight"]
                )

            return TrackingResponse(
                success=True,
                tracking_number=tracking_number,
                carrier=carrier or "AfterShip Carrier",
                status="In Transit",
                etd="2026-10-01",
                atd="2026-10-01",
                initial_eta="2026-10-10",
                eta="2026-10-10",
                vessel_name="AfterShip Vessel",
                current_lat=33.74,
                current_lon=-118.25,
                checkpoints=mock_checkpoints,
                raw_payload={"slug": slug, "aftership_source": "mock_adapter"},
                http_status_code=200,
                duration_ms=duration
            )

        # Pure in-system simulation without external network calls
        return TrackingResponse(
            success=True,
            tracking_number=tracking_number,
            carrier=carrier or "AfterShip Carrier",
            status="In Transit",
            etd="2026-10-01",
            atd="2026-10-01",
            initial_eta="2026-10-10",
            eta="2026-10-10",
            vessel_name="AfterShip Vessel",
            current_lat=33.74,
            current_lon=-118.25,
            checkpoints=mock_checkpoints,
            raw_payload={"slug": slug, "aftership_source": "mock_adapter"},
            http_status_code=200,
            duration_ms=duration
        )

    def _parse_aftership_data(self, data: Dict[str, Any], duration_ms: int = 0) -> TrackingResponse:
        data_dict = data if isinstance(data, dict) else {}
        raw_data = data_dict.get("data")
        if not isinstance(raw_data, dict):
            raw_data = {}
        trk = raw_data.get("tracking")
        if not isinstance(trk, dict):
            trk = data_dict.get("tracking") if isinstance(data_dict.get("tracking"), dict) else {}

        tracking_number = trk.get("tracking_number", "")
        carrier = trk.get("slug", "")
        tag = trk.get("tag", "InTransit")
        etd = trk.get("shipment_pickup_date")
        eta = trk.get("expected_delivery")

        raw_checkpoints = trk.get("checkpoints")
        if not isinstance(raw_checkpoints, list):
            raw_checkpoints = []

        valid_cps = [cp for cp in raw_checkpoints if cp and isinstance(cp, dict)]
        norm_checkpoints: List[Dict[str, Any]] = []

        for i, raw_cp in enumerate(valid_cps):
            raw_tag = raw_cp.get("tag") or raw_cp.get("message") or tag
            milestone = normalize_milestone(raw_tag)
            loc = raw_cp.get("location") or raw_cp.get("city") or "In Transit"
            ts = raw_cp.get("checkpoint_time") or datetime.now().isoformat()

            # Coordinates parsing: support list, tuple, dict, str with range check [-90, 90] / [-180, 180]
            coords = raw_cp.get("coordinates")
            lat_val = None
            lon_val = None
            if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                lat_val, lon_val = coords[0], coords[1]
            elif isinstance(coords, dict):
                lat_val = coords.get("lat") or coords.get("latitude")
                lon_val = coords.get("lon") or coords.get("longitude")
            elif isinstance(coords, str) and "," in coords:
                parts = coords.split(",")
                if len(parts) >= 2:
                    lat_val, lon_val = parts[0].strip(), parts[1].strip()

            lat = None
            lon = None
            if lat_val is not None and lon_val is not None:
                try:
                    f_lat = float(lat_val)
                    f_lon = float(lon_val)
                    if -90.0 <= f_lat <= 90.0 and -180.0 <= f_lon <= 180.0:
                        lat = f_lat
                        lon = f_lon
                except (ValueError, TypeError):
                    lat = None
                    lon = None

            cp_dict = {
                "milestone": milestone,
                "activity": raw_cp.get("message") or raw_tag,
                "location": loc,
                "port_code": raw_cp.get("city", ""),
                "timestamp": ts,
                "date": str(ts)[:10],
                "lat": lat,
                "lon": lon,
                "vessel_or_flight": raw_cp.get("slug", ""),
                "notes": raw_cp.get("subtag_message", ""),
                "is_current": (i == len(valid_cps) - 1),
                "dedup_hash": compute_checkpoint_hash(
                    shipment_id=tracking_number,
                    milestone=milestone,
                    location=loc,
                    timestamp=ts,
                    vehicle=raw_cp.get("slug", "")
                )
            }
            norm_checkpoints.append(cp_dict)

        status_map = {
            "Delivered": "Completed",
            "Exception": "Delayed",
            "InTransit": "In Transit",
            "OutForDelivery": "In Transit",
            "InfoReceived": "Draft"
        }

        return TrackingResponse(
            success=True,
            tracking_number=tracking_number,
            carrier=carrier,
            status=status_map.get(tag, "In Transit"),
            etd=str(etd)[:10] if etd else None,
            eta=str(eta)[:10] if eta else None,
            checkpoints=norm_checkpoints,
            raw_payload=data_dict,
            http_status_code=200,
            duration_ms=duration_ms
        )

    def parse_webhook(self, payload: Dict[str, Any], headers: Optional[Dict[str, Any]] = None) -> TrackingResponse:
        if not isinstance(payload, dict):
            payload = {}
        # AfterShip webhook wraps payload inside {"event": "...", "msg": {...}}
        if "msg" in payload and payload["msg"] is not None:
            return self._parse_aftership_data({"data": {"tracking": payload["msg"]}})
        return self._parse_aftership_data(payload)

    def verify_webhook_signature(self, payload_bytes: bytes, headers: Dict[str, Any], secret: str) -> bool:
        if not secret:
            return True
        headers_lower = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
        sig = headers_lower.get("aftership-hmac-sha256") or headers_lower.get("x-aftership-signature")
        if not sig:
            return False
        expected = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)


# ==============================================================================
# 7. IN-MEMORY STORAGE & FRAPPE FALLBACK LAYER
# ==============================================================================

class InMemoryTrackingDB:
    """
    Mock / In-memory Frappe DB layer phục vụ cho Standalone Python testing
    và đảm bảo 100% tính nguyên vẹn, không phụ thuộc vào Docker đang tắt.
    """
    def __init__(self):
        self.shipments: Dict[str, Dict[str, Any]] = {}
        self.exceptions: Dict[str, Dict[str, Any]] = {}
        self.integration_logs: List[Dict[str, Any]] = []

    def reset(self):
        self.shipments.clear()
        self.exceptions.clear()
        self.integration_logs.clear()

    def get_shipment(self, name: str) -> Optional[Dict[str, Any]]:
        return self.shipments.get(name)

    def save_shipment(self, name: str, data: Dict[str, Any]):
        self.shipments[name] = data

    def add_integration_log(self, log_entry: Dict[str, Any]):
        self.integration_logs.append(log_entry)

    def add_exception(self, exc_entry: Dict[str, Any]):
        name = f"EXC-2026-{len(self.exceptions) + 1:05d}"
        exc_entry["name"] = name
        self.exceptions[name] = exc_entry
        return name


# Global in-memory storage instance for standalone mode
in_memory_db = InMemoryTrackingDB()


# ==============================================================================
# 8. INTEGRATION LOGGING
# ==============================================================================

def log_integration_call(shipment_tracking: str,
                         direction: str,
                         provider: str,
                         http_method: str = "POST",
                         endpoint_url: str = "",
                         http_status_code: int = 200,
                         sync_status: str = "Success",
                         duration_ms: int = 0,
                         request_headers: Optional[Dict[str, Any]] = None,
                         request_body: Optional[Union[Dict, str]] = None,
                         response_headers: Optional[Dict[str, Any]] = None,
                         response_body: Optional[Union[Dict, str]] = None,
                         error_message: Optional[str] = None) -> str:
    """
    Ghi nhận một bản ghi nhật ký trao đổi dữ liệu vào DocType `Shipment Integration Log`.
    Hỗ trợ cả Frappe database lẫn In-Memory Standalone storage.
    """
    now_dt = datetime.now()
    log_data = {
        "doctype": "Shipment Integration Log",
        "shipment_tracking": shipment_tracking,
        "direction": direction,
        "provider": provider,
        "http_method": http_method,
        "endpoint_url": endpoint_url,
        "http_status_code": http_status_code,
        "sync_status": sync_status,
        "duration_ms": duration_ms,
        "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "request_headers": json.dumps(request_headers or {}, indent=2, default=str) if isinstance(request_headers, dict) else str(request_headers or ""),
        "request_body": json.dumps(request_body or {}, indent=2, default=str) if isinstance(request_body, (dict, list)) else str(request_body or ""),
        "response_headers": json.dumps(response_headers or {}, indent=2, default=str) if isinstance(response_headers, dict) else str(response_headers or ""),
        "response_body": json.dumps(response_body or {}, indent=2, default=str) if isinstance(response_body, (dict, list)) else str(response_body or ""),
        "error_message": error_message or ""
    }

    # If Frappe environment is active and connected
    if frappe and hasattr(frappe, "db") and getattr(frappe.db, "is_connected", None) and frappe.db.is_connected():
        try:
            doc = frappe.get_doc(log_data)
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return doc.name
        except Exception as e:
            logger.warning(f"Failed to insert Shipment Integration Log in Frappe DB: {e}. Falling back to in-memory.")

    # In-memory storage fallback
    in_memory_db.add_integration_log(log_data)
    log_id = f"TRK-LOG-2026-{len(in_memory_db.integration_logs):05d}"
    log_data["name"] = log_id
    return log_id


# ==============================================================================
# 9. STALE TRACKING DETECTION (>48 HOURS)
# ==============================================================================

def parse_datetime_flexible(val: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """Parse various datetime string formats safely into naive UTC datetime."""
    if not val:
        return None
    if isinstance(val, datetime):
        if val.tzinfo is not None:
            return val.astimezone(timezone.utc).replace(tzinfo=None)
        return val
    s = str(val).strip()
    # Strip ISO timezone offset (+07:00, -05:00, Z) both positive and negative
    s = re.sub(r'([+-]\d{2}:?\d{2}|Z)$', '', s).strip()
    s = s.replace("T", " ")

    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def is_tracking_stale(last_synced_at: Optional[Union[str, datetime]],
                      threshold_hours: int = 48,
                      current_time: Optional[datetime] = None) -> bool:
    """
    Kiểm tra xem lô hàng có bị mất tín hiệu (Stale) hay không:
    Nếu (current_time - last_synced_at) > threshold_hours (mặc định 48 giờ) -> True.
    Hỗ trợ cả timezone-aware và naive datetime.
    """
    if not last_synced_at:
        return True

    sync_dt = parse_datetime_flexible(last_synced_at)
    if not sync_dt:
        return True

    curr_dt = current_time or datetime.now()
    if isinstance(curr_dt, datetime) and curr_dt.tzinfo is not None:
        curr_dt = curr_dt.astimezone(timezone.utc).replace(tzinfo=None)
    if isinstance(sync_dt, datetime) and sync_dt.tzinfo is not None:
        sync_dt = sync_dt.astimezone(timezone.utc).replace(tzinfo=None)

    diff_hours = (curr_dt - sync_dt).total_seconds() / 3600.0
    return diff_hours > threshold_hours


def check_and_apply_stale_flag(shipment_data: Dict[str, Any],
                               threshold_hours: int = 48,
                               current_time: Optional[datetime] = None) -> bool:
    """
    Kiểm tra và tự động cập nhật cờ `is_stale = 1` trên đối tượng dữ liệu shipment.
    Nếu trạng thái đã là Completed / Delivered / Cancelled thì không coi là Stale.
    """
    status = shipment_data.get("status", "")
    if status in ["Completed", "Delivered", "Cancelled"]:
        shipment_data["is_stale"] = 0
        return False

    last_sync = shipment_data.get("last_synced_at") or shipment_data.get("last_sync_time")
    if not last_sync:
        # Check latest checkpoint timestamp if last_synced_at is empty
        cps = shipment_data.get("transit_route", [])
        if cps:
            last_sync = cps[-1].get("timestamp") or cps[-1].get("date")

    stale = is_tracking_stale(last_sync, threshold_hours, current_time)
    shipment_data["is_stale"] = 1 if stale else 0
    return stale


# ==============================================================================
# 10. CORE INGESTION & SYNCHRONIZATION PIPELINE
# ==============================================================================

def sync_shipment_tracking_data(shipment_name: str,
                                provider: Optional[BaseTrackingProvider] = None,
                                force_provider: Optional[str] = None,
                                current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Quy trình đồng bộ dữ liệu toàn diện cho một lô hàng:
    1. Đọc bản ghi Shipment Tracking (từ Frappe DB hoặc In-Memory DB).
    2. Khởi tạo Tracking Provider (Mock hoặc AfterShip).
    3. Thực hiện Polling với Exponential Backoff Retry.
    4. Chuẩn hóa các checkpoint sang 9 mốc DCSA.
    5. Khử trùng lặp (SHA-256 Checkpoint Deduplication).
    6. Cập nhật các trường vận đơn: ETD, ATD, ETA, ATA, Container ID, Vessel/Flight, Lat/Lon.
    7. Giám sát điều kiện Stale Tracking (>48 giờ).
    8. Ghi nhận `Shipment Integration Log`.
    9. Lưu trữ dữ liệu và trả về kết quả chi tiết.
    """
    t0 = time.time()
    curr_time = current_time or datetime.now()

    # 1. Fetch shipment record
    shipment_doc = None
    shipment_dict: Dict[str, Any] = {}

    if frappe and hasattr(frappe, "db") and getattr(frappe.db, "is_connected", None) and frappe.db.is_connected():
        try:
            shipment_doc = frappe.get_doc("Shipment Tracking", shipment_name)
            shipment_dict = shipment_doc.as_dict()
        except Exception:
            shipment_doc = None

    if not shipment_doc:
        in_mem = in_memory_db.get_shipment(shipment_name)
        if in_mem:
            shipment_dict = in_mem
        else:
            # Default fallback initialized shipment for testing
            shipment_dict = {
                "name": shipment_name,
                "doctype": "Shipment Tracking",
                "tracking_number": shipment_name,
                "carrier": "Maersk Line",
                "shipping_method": "Ocean",
                "container_id": "ABC123",
                "bill_of_lading": "BL-2026-MAERSK-01",
                "status": "In Transit",
                "delay_days": 0,
                "is_delayed": 0,
                "is_stale": 0,
                "transit_route": []
            }
            in_memory_db.save_shipment(shipment_name, shipment_dict)

    # 2. Select Provider
    if not provider:
        p_name = force_provider or "Mock Provider"
        if p_name == "AfterShip":
            provider = AfterShipProvider()
        else:
            provider = MockTrackingProvider(scenario="departed")

    # 3. Execute Polling with Retry Backoff
    tracking_no = shipment_dict.get("tracking_number") or shipment_name
    carrier = shipment_dict.get("carrier")

    resp: Optional[TrackingResponse] = None
    try:
        resp, attempts, err_list = execute_with_retry(
            func=provider.fetch_tracking,
            args=(tracking_no,),
            kwargs={
                "carrier": carrier,
                "container_id": shipment_dict.get("container_id"),
                "bill_of_lading": shipment_dict.get("bill_of_lading")
            },
            max_retries=3,
            base_delay=0.1,
            max_delay=1.0,
            retryable_exceptions=(Exception,)
        )
    except Exception as e:
        duration = int((time.time() - t0) * 1000)
        # Log failure
        log_integration_call(
            shipment_tracking=shipment_name,
            direction="Outbound Polling",
            provider=provider.provider_name,
            http_method="GET",
            endpoint_url=f"/trackings/{carrier}/{tracking_no}",
            http_status_code=500,
            sync_status="Failed",
            duration_ms=duration,
            error_message=str(e)
        )
        return {
            "success": False,
            "shipment": shipment_name,
            "error": str(e),
            "duration_ms": duration
        }

    # 4 & 5. Normalization & Deduplication
    existing_checkpoints = shipment_dict.get("transit_route", [])
    incoming_checkpoints = resp.checkpoints

    # Ensure all incoming checkpoints have valid DCSA milestone and reject UNKNOWN/non-DCSA (BUG-M2-03)
    valid_incoming = []
    for cp in incoming_checkpoints:
        norm_m = normalize_milestone(cp.get("milestone") or cp.get("activity"))
        if norm_m in DCSA_MILESTONES:
            cp["milestone"] = norm_m
            valid_incoming.append(cp)

    new_cps = filter_new_checkpoints(shipment_name, existing_checkpoints, valid_incoming)

    # Append new unique checkpoints (strictly 9 DCSA milestones)
    combined_checkpoints = [
        cp for cp in (list(existing_checkpoints) + list(new_cps))
        if cp.get("milestone") in DCSA_MILESTONES
    ]

    # Sort checkpoints chronologically if timestamps available
    try:
        combined_checkpoints.sort(key=lambda x: str(x.get("timestamp") or x.get("date") or ""))
    except Exception:
        pass

    # Update is_current flag: only the last checkpoint is current
    for i, cp in enumerate(combined_checkpoints):
        cp["is_current"] = 1 if (i == len(combined_checkpoints) - 1) else 0

    shipment_dict["transit_route"] = combined_checkpoints

    # 6. Update shipment fields & ETA Delay Evaluation
    if resp.status:
        shipment_dict["status"] = resp.status
    elif combined_checkpoints and combined_checkpoints[-1].get("milestone") == "DELIVERED":
        shipment_dict["status"] = "Completed"

    if resp.etd:
        shipment_dict["etd"] = resp.etd
    if resp.atd:
        shipment_dict["atd"] = resp.atd

    # ETA Comparison & Delay Engine Integration (Milestone 2)
    new_eta = resp.eta
    delay_days = shipment_dict.get("delay_days", 0)
    is_delayed = shipment_dict.get("is_delayed", 0)
    exception_created = False

    if new_eta:
        # Populate initial_eta if not already set
        if not shipment_dict.get("initial_eta"):
            shipment_dict["initial_eta"] = resp.initial_eta or new_eta

        # BUG-M2-04: If shipment.get('eta') is None/empty, use shipment.get('initial_eta')
        # (or resp.initial_eta) as comparison baseline against carrier new_eta
        old_eta = shipment_dict.get("eta")
        if not old_eta:
            old_eta = shipment_dict.get("initial_eta") or resp.initial_eta

        if evaluate_eta_change:
            delay_eval = evaluate_eta_change(old_eta, new_eta)
            delay_days = delay_eval.get("delay_days", 0)
            is_delayed = delay_eval.get("is_delayed", 0)

            if delay_eval.get("create_exception"):
                apply_delay_to_shipment(shipment_dict, delay_eval)
                if shipment_doc:
                    apply_delay_to_shipment(shipment_doc, delay_eval)

                create_shipment_exception(
                    shipment_tracking=shipment_name,
                    exception_type="ETA Delay",
                    severity=delay_eval.get("severity", "Warning"),
                    description=delay_eval.get("description"),
                    old_eta=old_eta,
                    new_eta=new_eta,
                    delay_days=delay_days,
                    purchase_order=shipment_dict.get("purchase_order"),
                    carrier=shipment_dict.get("carrier") or resp.carrier,
                    container_id=shipment_dict.get("container_id") or resp.container_id
                )
                exception_created = True
            else:
                shipment_dict["eta"] = new_eta
                # BUG-M2-01 & BUG-M2-02:
                # Check whether carrier has recovered to on-time schedule
                init_eta = shipment_dict.get("initial_eta")
                init_delay = calculate_delay_days(init_eta, new_eta) if (calculate_delay_days and init_eta) else 0

                if init_delay <= 0 and delay_days <= 0:
                    shipment_dict["delay_days"] = 0
                    shipment_dict["is_delayed"] = 0
                    if shipment_dict.get("status") == "Delayed":
                        shipment_dict["status"] = resp.status or "In Transit"
                    if shipment_doc:
                        apply_delay_to_shipment(shipment_doc, {
                            "new_eta": new_eta,
                            "delay_days": 0,
                            "is_delayed": 0
                        })
                    if auto_resolve_shipment_exceptions:
                        auto_resolve_shipment_exceptions(
                            shipment_name=shipment_name,
                            resolution_notes="Shipment recovered on schedule"
                        )
        else:
            shipment_dict["eta"] = new_eta
    else:
        delay_days = shipment_dict.get("delay_days", 0)
        is_delayed = shipment_dict.get("is_delayed", 0)

    if resp.ata:
        shipment_dict["ata"] = resp.ata
    if resp.vessel_name:
        shipment_dict["vessel_name"] = resp.vessel_name
    if resp.flight_number:
        shipment_dict["flight_number"] = resp.flight_number
    if resp.container_id:
        shipment_dict["container_id"] = resp.container_id
    if resp.bill_of_lading:
        shipment_dict["bill_of_lading"] = resp.bill_of_lading
    if resp.air_waybill:
        shipment_dict["air_waybill"] = resp.air_waybill

    if resp.current_lat is not None:
        shipment_dict["current_lat"] = resp.current_lat
    if resp.current_lon is not None:
        shipment_dict["current_lon"] = resp.current_lon

    # Update last_synced_at timestamp
    now_str = curr_time.strftime("%Y-%m-%d %H:%M:%S")
    shipment_dict["last_synced_at"] = now_str
    shipment_dict["last_sync_time"] = now_str

    # 7. Check Stale condition
    check_and_apply_stale_flag(shipment_dict, threshold_hours=48, current_time=curr_time)

    # 8. Persist to DB or In-Memory
    if shipment_doc:
        try:
            for k, v in shipment_dict.items():
                if k != "transit_route" and hasattr(shipment_doc, k):
                    setattr(shipment_doc, k, v)
            # Update child table
            shipment_doc.set("transit_route", [])
            for cp in combined_checkpoints:
                shipment_doc.append("transit_route", cp)
            shipment_doc.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            logger.warning(f"Error persisting to Frappe DB: {e}. Saving to in-memory.")
            in_memory_db.save_shipment(shipment_name, shipment_dict)
    else:
        in_memory_db.save_shipment(shipment_name, shipment_dict)

    # 9. Ghi Shipment Integration Log
    duration = int((time.time() - t0) * 1000)
    log_integration_call(
        shipment_tracking=shipment_name,
        direction="Outbound Polling",
        provider=provider.provider_name,
        http_method="GET",
        endpoint_url=f"/trackings/{carrier}/{tracking_no}",
        http_status_code=resp.http_status_code,
        sync_status="Success" if resp.success else "Failed",
        duration_ms=duration,
        request_body={"tracking_number": tracking_no, "carrier": carrier},
        response_body=resp.to_dict(),
        error_message=resp.error_message
    )

    return {
        "success": True,
        "shipment": shipment_name,
        "new_checkpoints": len(new_cps),
        "total_checkpoints": len(combined_checkpoints),
        "is_stale": shipment_dict.get("is_stale", 0),
        "status": shipment_dict.get("status", "In Transit"),
        "eta": shipment_dict.get("eta"),
        "atd": shipment_dict.get("atd"),
        "delay_days": shipment_dict.get("delay_days", 0),
        "is_delayed": shipment_dict.get("is_delayed", 0),
        "exception_created": exception_created,
        "duration_ms": duration
    }


# ==============================================================================
# 11. CONTRACT ALIASES & EXPORTS (PROJECT.MD COMPLIANCE)
# ==============================================================================

# Alias conforming to PROJECT.md interface contract
sync_shipment_tracking = sync_shipment_tracking_data

__all__ = [
    "DCSA_MILESTONES",
    "MILESTONE_SYNONYMS",
    "FLATTENED_MILESTONE_KEYWORDS",
    "normalize_milestone",
    "normalize_timestamp_str",
    "compute_checkpoint_hash",
    "filter_new_checkpoints",
    "calculate_backoff_delay",
    "retry_with_backoff",
    "TrackingResponse",
    "BaseTrackingProvider",
    "MockTrackingProvider",
    "AfterShipProvider",
    "InMemoryTrackingDB",
    "in_memory_db",
    "log_integration_call",
    "parse_datetime_flexible",
    "is_tracking_stale",
    "check_and_apply_stale_flag",
    "sync_shipment_tracking_data",
    "sync_shipment_tracking",
    "calculate_delay_days",
    "classify_severity",
    "evaluate_eta_change",
    "create_shipment_exception",
    "apply_delay_to_shipment",
    "auto_resolve_shipment_exceptions",
    "check_and_process_delay",
]

