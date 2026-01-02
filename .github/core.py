# core.py
# -*- coding: utf-8 -*-

"""
AYAR Scanner (InsCode: 34144395039913458)
- Fetch: MarketWatchInit (price + depth)
- Fetch: Financial.aspx (AvgVol20 + AvgVal5 proxy)
- Fetch: clienttype.aspx (infer RealPower + NetRealVol)
- Entry signal based on your checklist + depth gate
- Notification on ENTER (Android) using plyer if available
"""

import random
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

# -------------------------
# CONFIG (می‌توانید بعداً تغییر دهید)
# -------------------------
INS_CODE_AYAR = "34144395039913458"
TIMEOUT = 18

MIN_REAL_POWER = 1.5
VOL_MULT = 2.0
VAL_MULT = 2.0
MIN_SCORE = 3  # از 5

TIGHT_SPREAD_PCT = 0.15
DEPTH_IMB_MIN = 1.30
ASK_WALL_DOM_RATIO = 0.60
TOP_PRESSURE_ALERT = 3.0

# جلوگیری از اسپم نوتیفیکیشن
_LAST_NOTIFY_KEY = None
_LAST_NOTIFY_TS = 0.0
NOTIFY_COOLDOWN_SEC = 120.0

BASES = [
    "https://www.tsetmc.com",
    "https://members.tsetmc.com",
    "https://service.tsetmc.com",
    "https://cdn.tsetmc.com",
    "https://redirectcdn.tsetmc.com",
]

UAS = [
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
]

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

_num_token_re = re.compile(r"^-?\d+(\.\d+)?$")


def now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def safe_int(x, default=0) -> int:
    try:
        s = str(x).strip().replace(",", "")
        if s == "" or s.lower() == "nan":
            return default
        if "." in s:
            s = s.split(".")[0]
        return int(s)
    except Exception:
        return default


def safe_float(x, default=None) -> Optional[float]:
    try:
        s = str(x).strip().replace(",", "")
        if s == "" or s.lower() == "nan":
            return default
        return float(s)
    except Exception:
        return default


def fmt(x: Optional[float], nd: int = 2) -> str:
    if x is None:
        return "NA"
    return f"{x:.{nd}f}"


def http_get_any(path: str, params: Optional[dict] = None, min_len: int = 50, timeout: int = TIMEOUT) -> str:
    last_err = None
    sess = requests.Session()
    bases = BASES[:]
    random.shuffle(bases)

    for base in bases:
        url = base.rstrip("/") + path
        for _ in range(2):
            try:
                h = dict(HEADERS)
                h["User-Agent"] = random.choice(UAS)
                r = sess.get(url, headers=h, params=params, timeout=timeout)
                txt = (r.text or "").strip()

                if r.status_code != 200:
                    last_err = f"{url} -> HTTP {r.status_code} len={len(txt)}"
                    time.sleep(0.15 + random.random() * 0.2)
                    continue

                if len(txt) < min_len:
                    last_err = f"{url} -> short len={len(txt)}"
                    time.sleep(0.15 + random.random() * 0.2)
                    continue

                head = txt[:250].lower()
                if ("<html" in head) or ("<!doctype" in head):
                    last_err = f"{url} -> HTML/blocked len={len(txt)}"
                    time.sleep(0.15 + random.random() * 0.2)
                    continue

                return txt

            except Exception as e:
                last_err = f"{url} -> {e}"
                time.sleep(0.15 + random.random() * 0.2)

    raise RuntimeError(f"fetch failed: {path}. last={last_err}")


# -------- MarketWatchInit --------
def parse_marketwatchinit(text: str) -> Tuple[List[List[str]], List[List[str]]]:
    prices_rows: List[List[str]] = []
    best_rows: List[List[str]] = []
    for part in text.split("@"):
        part = part.strip()
        if not part:
            continue
        for row in [r for r in part.split(";") if r.strip()]:
            cols = row.split(",")
            if len(cols) == 8 and cols[0].strip().isdigit():
                best_rows.append(cols)
            elif len(cols) >= 23 and cols[0].strip().isdigit():
                prices_rows.append(cols)
    return prices_rows, best_rows


def get_price_row(prices_rows: List[List[str]], ins_code: str) -> Optional[List[str]]:
    for cols in prices_rows:
        if cols and cols[0] == ins_code:
            return cols
    return None


@dataclass
class DepthLevel:
    level: int
    bid_price: int
    bid_qty: int
    bid_orders: int
    ask_price: int
    ask_qty: int
    ask_orders: int


def extract_depth(best_rows: List[List[str]], ins_code: str, levels: int = 5) -> Optional[List[DepthLevel]]:
    rows = [r for r in best_rows if r and r[0] == ins_code]
    if not rows:
        return None
    rows.sort(key=lambda r: safe_int(r[1], 999))

    out: List[DepthLevel] = []
    for r in rows[:levels]:
        out.append(
            DepthLevel(
                level=safe_int(r[1]),
                bid_orders=safe_int(r[2]),
                ask_orders=safe_int(r[3]),
                bid_price=safe_int(r[4]),
                ask_price=safe_int(r[5]),
                bid_qty=safe_int(r[6]),
                ask_qty=safe_int(r[7]),
            )
        )
    return out if out else None


def depth_metrics_advanced(depth: Optional[List[DepthLevel]], last_price: int) -> Dict[str, Optional[float]]:
    out: Dict[str, Optional[float]] = {
        "spread_pct": None,
        "imb_simple": None,
        "imb_weighted": None,
        "top_pressure": None,
        "ask_share1": None,
        "tight_spread": 0.0,
        "demand_dom": 0.0,
        "ask_wall_strong": 0.0,
    }
    if not depth or last_price <= 0:
        return out

    top = depth[0]
    if top.bid_price > 0 and top.ask_price > 0:
        out["spread_pct"] = ((top.ask_price - top.bid_price) / last_price) * 100.0

    bid_sum = sum(d.bid_qty for d in depth if d.bid_qty > 0)
    ask_sum = sum(d.ask_qty for d in depth if d.ask_qty > 0)
    out["imb_simple"] = (bid_sum / ask_sum) if ask_sum > 0 else (10.0 if bid_sum > 0 else 0.0)

    weights = [5, 4, 3, 2, 1]
    wb = 0.0
    wa = 0.0
    for i, d in enumerate(depth[:5]):
        w = weights[i]
        wb += w * max(0, d.bid_qty)
        wa += w * max(0, d.ask_qty)
    out["imb_weighted"] = (wb / wa) if wa > 0 else (10.0 if wb > 0 else 0.0)

    out["top_pressure"] = top.ask_qty / max(1, top.bid_qty) if (top.ask_qty > 0 or top.bid_qty > 0) else None
    out["ask_share1"] = (top.ask_qty / ask_sum) if ask_sum > 0 else None

    tight = (out["spread_pct"] is not None) and (out["spread_pct"] <= TIGHT_SPREAD_PCT)
    demand_dom = (out["imb_weighted"] is not None) and (out["imb_weighted"] >= DEPTH_IMB_MIN)

    ask_wall = False
    if out["ask_share1"] is not None and out["ask_share1"] >= ASK_WALL_DOM_RATIO:
        ask_wall = True
    if out["top_pressure"] is not None and out["top_pressure"] >= TOP_PRESSURE_ALERT:
        ask_wall = True

    out["tight_spread"] = 1.0 if tight else 0.0
    out["demand_dom"] = 1.0 if demand_dom else 0.0
    out["ask_wall_strong"] = 1.0 if ask_wall else 0.0
    return out


# -------- Financial avgs --------
def fetch_financial_avgs(ins_code: str) -> Tuple[int, int]:
    txt = http_get_any(
        "/tsev2/chart/data/Financial.aspx",
        params={"i": ins_code, "t": "ph", "a": 1},
        min_len=200,
        timeout=TIMEOUT,
    )

    rows: List[Tuple[int, int]] = []
    for ln in txt.replace(";", "\n").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        cols = [c.strip() for c in ln.split(",")]
        if len(cols) < 5:
            continue
        vol = safe_int(cols[-2])
        close = safe_int(cols[-1])
        if vol > 0 and close > 0:
            rows.append((vol, close))

    if len(rows) < 5:
        return 0, 0

    vols = [v for v, _ in rows]
    avg_vol20 = int(sum(vols[-20:]) / max(1, min(20, len(vols))))

    proxy_vals = [v * c for v, c in rows]
    avg_val5_proxy = int(sum(proxy_vals[-5:]) / 5)
    return avg_vol20, avg_val5_proxy


# -------- clienttype inference --------
def fetch_clienttype_numbers(ins_code: str) -> List[float]:
    txt = http_get_any("/tsev2/data/clienttype.aspx", params={"i": ins_code}, min_len=20, timeout=TIMEOUT)
    tokens = re.split(r"[,\s;]+", txt.replace("\r", " ").replace("\n", " "))
    nums: List[float] = []
    for t in tokens:
        t = t.strip()
        if not t:
            continue
        if _num_token_re.match(t):
            v = safe_float(t, default=None)
            if v is not None:
                nums.append(v)
    return nums


def infer_realpower_and_netreal(nums: List[float]) -> Tuple[float, int]:
    if not nums or len(nums) < 6:
        return 0.0, 0

    nums2 = nums[:60]
    count_idx = [i for i, x in enumerate(nums2) if 0 < x <= 10_000_000]
    vol_idx = [i for i, x in enumerate(nums2) if 0 < x <= 10_000_000_000_000]

    best = None  # (score, rp, net)

    for i in count_idx:
        rb_cnt = int(nums2[i])
        if rb_cnt <= 0:
            continue
        for j in count_idx:
            if j == i:
                continue
            rs_cnt = int(nums2[j])
            if rs_cnt <= 0:
                continue

            for a in vol_idx:
                rb_vol = int(nums2[a])
                if rb_vol < rb_cnt:
                    continue
                for b in vol_idx:
                    if b == a:
                        continue
                    rs_vol = int(nums2[b])
                    if rs_vol < rs_cnt:
                        continue

                    sell_avg = rs_vol / rs_cnt if rs_vol > 0 else 0.0
                    if sell_avg <= 0:
                        continue
                    buy_avg = rb_vol / rb_cnt
                    rp = buy_avg / sell_avg
                    if not (0.05 <= rp <= 50):
                        continue

                    net = rb_vol - rs_vol

                    score = 0
                    if rp >= 1.0:
                        score += 2
                    if rp >= 1.5:
                        score += 2
                    if rp >= 2.0:
                        score += 1
                    if rb_cnt <= 10000:
                        score += 1
                    if rs_cnt <= 10000:
                        score += 1
                    if abs(net) <= 2_000_000_000:
                        score += 1

                    cand = (score, rp, net)
                    if best is None or cand[0] > best[0]:
                        best = cand

    if best is None:
        return 0.0, 0
    return float(best[1]), int(best[2])


# -------- Notification helpers --------
def should_notify(key: str) -> bool:
    global _LAST_NOTIFY_KEY, _LAST_NOTIFY_TS
    now = time.time()
    if _LAST_NOTIFY_KEY == key and (now - _LAST_NOTIFY_TS) < NOTIFY_COOLDOWN_SEC:
        return False
    _LAST_NOTIFY_KEY = key
    _LAST_NOTIFY_TS = now
    return True


def android_notify(title: str, message: str) -> None:
    """
    Uses plyer.notification when available. If not available, it silently ignores.
    """
    try:
        from plyer import notification
        notification.notify(title=title, message=message)
    except Exception:
        pass


# -------- Core scan --------
def scan_once(ins_code: str = INS_CODE_AYAR) -> Dict[str, object]:
    mw = http_get_any("/tsev2/data/MarketWatchInit.aspx", params={"h": "0", "r": "0"}, min_len=200, timeout=TIMEOUT)
    prices_rows, best_rows = parse_marketwatchinit(mw)

    pr = get_price_row(prices_rows, ins_code)
    if not pr:
        raise RuntimeError("Price row not found in MarketWatchInit for this InsCode")

    last_price = safe_int(pr[7])
    close_price = safe_int(pr[6])
    yest_price = safe_int(pr[13])
    vol_today = safe_int(pr[9])
    val_today = safe_int(pr[10])
    low_today = safe_int(pr[11])
    high_today = safe_int(pr[12])

    chg_pct = ((last_price - yest_price) / yest_price * 100.0) if yest_price > 0 else None

    avg_vol20, avg_val5_proxy = fetch_financial_avgs(ins_code)

    nums = fetch_clienttype_numbers(ins_code)
    real_power, net_real_vol = infer_realpower_and_netreal(nums)

    depth = extract_depth(best_rows, ins_code, levels=5)
    dm = depth_metrics_advanced(depth, last_price)

    ask_wall = bool(dm["ask_wall_strong"])
    depth_ok = (bool(dm["demand_dom"]) or bool(dm["tight_spread"])) and (not ask_wall)

    cond = {
        "price_positive": (chg_pct is not None and chg_pct > 0),
        "value_ge_2x_avg5": (avg_val5_proxy > 0 and val_today >= VAL_MULT * avg_val5_proxy),
        "volume_suspicious": (avg_vol20 > 0 and vol_today >= VOL_MULT * avg_vol20),
        "real_power_ge_min": (real_power >= MIN_REAL_POWER),
        "net_real_positive": (net_real_vol > 0),
    }

    score = sum(1 for k in cond if cond[k])

    enter_raw = (score >= MIN_SCORE) and cond["price_positive"] and cond["real_power_ge_min"] and depth_ok

    topbook = None
    if depth:
        d0 = depth[0]
        topbook = {
            "bid_price": d0.bid_price, "bid_qty": d0.bid_qty,
            "ask_price": d0.ask_price, "ask_qty": d0.ask_qty,
        }

    return {
        "time": now_str(),
        "ins_code": ins_code,
        "last_price": last_price,
        "close_price": close_price,
        "yest_price": yest_price,
        "change_pct": chg_pct,
        "vol_today": vol_today,
        "val_today": val_today,
        "avg_vol20": avg_vol20,
        "avg_val5_proxy": avg_val5_proxy,
        "real_power": real_power,
        "net_real_vol": net_real_vol,
        "depth_metrics": dm,
        "ask_wall": ask_wall,
        "depth_ok": depth_ok,
        "conds": cond,
        "score": score,
        "enter_raw": enter_raw,
        "topbook": topbook,
    }


def run_once_text() -> str:
    """
    main.py calls this. If ENTER signal -> notify (if possible).
    """
    data = scan_once(INS_CODE_AYAR)

    lines = []
    lines.append("=" * 72)
    lines.append(f"Mode: DAILY | InsCode: {data['ins_code']} | Time: {data['time']}")
    lines.append(
        f"LastPrice: {data['last_price']:,} | Yest: {data['yest_price']:,} | Change%: {fmt(data['change_pct'])}"
    )
    lines.append(f"VolToday: {data['vol_today']:,} | AvgVol20: {data['avg_vol20']:,}")
    lines.append(f"ValToday: {data['val_today']:,} | AvgVal5(proxy): {data['avg_val5_proxy']:,}")
    lines.append(
        f"RealPower: {fmt(data['real_power'])} | NetRealVol: {data['net_real_vol']:,}"
    )

    dm = data["depth_metrics"]
    lines.append(
        f"DepthSpread%: {fmt(dm.get('spread_pct'),3)} | ImbW: {fmt(dm.get('imb_weighted'))} "
        f"| TopPressure: {fmt(dm.get('top_pressure'))} | AskWallStrong: {bool(dm.get('ask_wall_strong'))}"
    )
    if data["topbook"]:
        tb = data["topbook"]
        lines.append(f"TopBook | Bid: {tb['bid_price']:,} ({tb['bid_qty']:,}) | Ask: {tb['ask_price']:,} ({tb['ask_qty']:,})")

    lines.append("-" * 72)
    for k, v in data["conds"].items():
        lines.append(f"{k:22s}: {'OK' if v else 'NO'}")

    lines.append("-" * 72)
    lines.append(f"SCORE: {data['score']}/5 (min {MIN_SCORE}) | DepthOK: {data['depth_ok']}")
    lines.append(f"Signal: {'ENTER' if data['enter_raw'] else 'NO-ENTER'}")
    lines.append("=" * 72)

    # Notification on ENTER
    if data["enter_raw"]:
        key = f"ENTER:{data['ins_code']}:{data['last_price']}:{round(data['change_pct'] or 0,2)}"
        if should_notify(key):
            android_notify("Ayar Scanner", f"ENTER signal | Last={data['last_price']:,} | RP={fmt(data['real_power'])}")

    return "\n".join(lines)
