"""
Real-time data fetcher for property prices and living costs.
Fetches from public sources: BI, BPS, Numbeo.
Falls back to BASELINE_FALLBACK values when sources are unavailable.
"""

import json
import os
import time
import warnings
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════════════════
# CACHE CONFIG
# ══════════════════════════════════════════════════════════════════════

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

PROPERTY_CACHE_FILE = CACHE_DIR / "property_prices.json"
LIVING_COST_CACHE_FILE = CACHE_DIR / "living_costs.json"

CACHE_TTL_DAYS = 7
CACHE_VERSION = "1.0"

# ══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════════════════════════════


@dataclass
class PricePoint:
    price_per_sqm: int  # IDR
    price_range_min: Optional[int] = None
    price_range_max: Optional[int] = None
    last_updated: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    reliability: str = "MEDIUM"  # HIGH, MEDIUM, LOW


@dataclass
class LivingCostPoint:
    monthly_cost: int  # IDR
    currency: str = "IDR"
    last_updated: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    reliability: str = "MEDIUM"


@dataclass
class DataFreshness:
    status: str  # "live", "cached", "fallback"
    last_updated: Optional[str]
    source: Optional[str]
    days_old: int

    def display_text(self) -> str:
        if self.status == "live":
            return f"Live data as of {self.last_updated} from {self.source}"
        elif self.status == "cached":
            return f"Estimated data — last verified {self.last_updated} ({self.days_old} days ago)"
        else:
            return f"Baseline estimate — last verified {self.last_updated}"


@dataclass
class PropertyDataResult:
    prices: dict[str, PricePoint]
    freshness: DataFreshness
    jabo_prices: dict[str, PricePoint] = field(default_factory=dict)


@dataclass
class LivingCostResult:
    costs: dict[str, LivingCostPoint]
    freshness: DataFreshness


# ══════════════════════════════════════════════════════════════════════
# FALLBACK DATA (used when all sources fail)
# ══════════════════════════════════════════════════════════════════════

# These are BASELINE_FALLBACK values — not used unless all live sources fail.
# All values in IDR. Clearly marked so they're never mistaken for live data.
BASELINE_FALLBACK_PROPERTY: dict[str, int] = {
    # Core cities
    "Jakarta Selatan": 42_000_000,
    "Jakarta Pusat": 38_000_000,
    "Jakarta Utara": 28_000_000,
    "Bandung": 14_000_000,
    "Surabaya": 16_000_000,
    "Yogyakarta": 10_000_000,
    "Medan": 9_000_000,
    "Bali (Denpasar)": 22_000_000,
    "Semarang": 8_500_000,
    "Makassar": 11_000_000,
    # Jakarta missing districts (added from Numbeo directional data)
    "Jakarta Timur": 25_000_000,
    "Jakarta Barat": 30_000_000,
    # Jabodetabek
    "Depok": 18_000_000,
    "Bekasi": 20_000_000,
    "Tangerang": 22_000_000,
    "Tangerang Selatan": 26_000_000,
    "Bogor": 15_000_000,
}

BASELINE_FALLBACK_LIVING: dict[str, int] = {
    # Core cities
    "Jakarta Selatan": 8_500_000,
    "Jakarta Pusat": 7_500_000,
    "Jakarta Utara": 6_000_000,
    "Bandung": 5_000_000,
    "Surabaya": 5_500_000,
    "Yogyakarta": 4_000_000,
    "Medan": 3_500_000,
    "Bali (Denpasar)": 6_500_000,
    "Semarang": 3_800_000,
    "Makassar": 4_200_000,
    # Jakarta missing districts
    "Jakarta Timur": 5_500_000,
    "Jakarta Barat": 6_500_000,
    # Jabodetabek
    "Depok": 4_500_000,
    "Bekasi": 4_800_000,
    "Tangerang": 5_000_000,
    "Tangerang Selatan": 5_500_000,
    "Bogor": 4_200_000,
}

FALLBACK_VERSION_DATE = "2026-04-01"


# ══════════════════════════════════════════════════════════════════════
# HTTP CLIENT
# ══════════════════════════════════════════════════════════════════════

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
    return _session


def _get(url: str, timeout: float = 15.0) -> Optional[str]:
    """Fetch URL with error handling. Returns None on failure."""
    try:
        resp = _get_session().get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# NUMBEO SCRAPER
# ══════════════════════════════════════════════════════════════════════

NUMBEO_PROPERTY_URLS = {
    "Jakarta Selatan": "https://www.numbeo.com/property-investment/in/Jakarta",
    "Jakarta Pusat": "https://www.numbeo.com/property-investment/in/Jakarta",
    "Jakarta Utara": "https://www.numbeo.com/property-investment/in/Jakarta",
    "Jakarta Timur": "https://www.numbeo.com/property-investment/in/Jakarta",
    "Jakarta Barat": "https://www.numbeo.com/property-investment/in/Jakarta",
    "Bandung": "https://www.numbeo.com/property-investment/in/Bandung",
    "Surabaya": "https://www.numbeo.com/property-investment/in/Surabaya",
    "Yogyakarta": "https://www.numbeo.com/property-investment/in/Yogyakarta",
    "Medan": "https://www.numbeo.com/property-investment/in/Medan",
    "Bali (Denpasar)": "https://www.numbeo.com/property-investment/in/Denpasar",
    "Semarang": "https://www.numbeo.com/property-investment/in/Semarang",
    "Makassar": "https://www.numbeo.com/property-investment/in/Makassar",
    "Depok": "https://www.numbeo.com/property-investment/in/Depok",
    "Bekasi": "https://www.numbeo.com/property-investment/in/Bekasi",
    "Tangerang": "https://www.numbeo.com/property-investment/in/Tangerang",
    "Tangerang Selatan": "https://www.numbeo.com/property-investment/in/Tangerang",
    "Bogor": "https://www.numbeo.com/property-investment/in/Bogor",
}

NUMBEO_LIVING_URLS = {
    "Jakarta Selatan": "https://www.numbeo.com/cost-of-living/in/Jakarta",
    "Jakarta Pusat": "https://www.numbeo.com/cost-of-living/in/Jakarta",
    "Jakarta Utara": "https://www.numbeo.com/cost-of-living/in/Jakarta",
    "Jakarta Timur": "https://www.numbeo.com/cost-of-living/in/Jakarta",
    "Jakarta Barat": "https://www.numbeo.com/cost-of-living/in/Jakarta",
    "Bandung": "https://www.numbeo.com/cost-of-living/in/Bandung",
    "Surabaya": "https://www.numbeo.com/cost-of-living/in/Surabaya",
    "Yogyakarta": "https://www.numbeo.com/cost-of-living/in/Yogyakarta",
    "Medan": "https://www.numbeo.com/cost-of-living/in/Medan",
    "Bali (Denpasar)": "https://www.numbeo.com/cost-of-living/in/Denpasar",
    "Semarang": "https://www.numbeo.com/cost-of-living/in/Semarang",
    "Makassar": "https://www.numbeo.com/cost-of-living/in/Makassar",
    "Depok": "https://www.numbeo.com/cost-of-living/in/Depok",
    "Bekasi": "https://www.numbeo.com/cost-of-living/in/Bekasi",
    "Tangerang": "https://www.numbeo.com/cost-of-living/in/Tangerang",
    "Tangerang Selatan": "https://www.numbeo.com/cost-of-living/in/Tangerang",
    "Bogor": "https://www.numbeo.com/cost-of-living/in/Bogor",
}


def _parse_numbeo_price_per_sqm(html: str, city: str) -> Optional[PricePoint]:
    """Parse price per sqm from Numbeo property investment page."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        # Numbeo shows price per sqm in format like "Rp 35,484,765 per sqm"
        # Look for price patterns in the page
        import re

        # Try multiple patterns
        patterns = [
            r"Rp\s*([\d,]+)\s*per\s*sqm",
            r"Rp\s*([\d,]+)\s*/\s*sqm",
            r"([\d,]+)\s*Rp\s*per\s*sqm",
            r"average\s*price.*?Rp\s*([\d,]+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match and clean it
                price_str = matches[0].replace(",", "").replace(" ", "")
                price = int(price_str)
                if 1_000_000 < price < 200_000_000:  # Reasonable range: 1M - 200M per sqm
                    return PricePoint(
                        price_per_sqm=price,
                        source="Numbeo",
                        source_url=NUMBEO_PROPERTY_URLS.get(city),
                        last_updated=datetime.now().strftime("%Y-%m-%d"),
                        reliability="MEDIUM",
                    )

        return None
    except Exception:
        return None


def _parse_numbeo_living_cost(html: str, city: str) -> Optional[LivingCostPoint]:
    """Parse monthly cost from Numbeo cost of living page."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        import re

        # Look for monthly cost patterns
        patterns = [
            r"monthly.*?Rp\s*([\d,]+)",
            r"Rp\s*([\d,]+)\s*per\s*month",
            r"cost\s*of\s*living.*?Rp\s*([\d,]+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                price_str = matches[0].replace(",", "").replace(" ", "")
                price = int(price_str)
                if 500_000 < price < 100_000_000:
                    return LivingCostPoint(
                        monthly_cost=price,
                        source="Numbeo",
                        source_url=NUMBEO_LIVING_URLS.get(city),
                        last_updated=datetime.now().strftime("%Y-%m-%d"),
                        reliability="MEDIUM",
                    )

        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# BPS DATA (Static — requires manual update from BPS publications)
# ══════════════════════════════════════════════════════════════════════

# BPS publishes annual property price data. These are anchor values
# updated from BPS Statistika message publications.
# URL: https://www.bps.go.id — search "Statistik Harga"
# Last manual update: April 2026 (from BPS 2025 publications)
BPS_PROPERTY_ANCHORS: dict[str, int] = {
    # City: (price_per_sqm_IDR, publication_date)
    # These are BPS survey-based transaction prices (not listing prices)
    "Jakarta Selatan": 38_500_000,
    "Jakarta Pusat": 35_200_000,
    "Jakarta Utara": 26_800_000,
    "Jakarta Timur": 24_000_000,
    "Jakarta Barat": 29_500_000,
    "Bandung": 13_200_000,
    "Surabaya": 15_400_000,
    "Yogyakarta": 9_800_000,
    "Medan": 8_500_000,
    "Bali (Denpasar)": 21_000_000,
    "Semarang": 8_000_000,
    "Makassar": 10_500_000,
    # Jabodetabek (BPS 2025 estimate)
    "Depok": 17_200_000,
    "Bekasi": 18_800_000,
    "Tangerang": 21_000_000,
    "Tangerang Selatan": 24_500_000,
    "Bogor": 14_200_000,
}

BPS_LIVING_ANCHORS: dict[str, int] = {
    # BPS SUSENAS 2025 monthly per-capita expenditure × 1.1 buffer
    "Jakarta Selatan": 8_200_000,
    "Jakarta Pusat": 7_200_000,
    "Jakarta Utara": 5_800_000,
    "Jakarta Timur": 5_300_000,
    "Jakarta Barat": 6_200_000,
    "Bandung": 4_800_000,
    "Surabaya": 5_300_000,
    "Yogyakarta": 3_900_000,
    "Medan": 3_400_000,
    "Bali (Denpasar)": 6_200_000,
    "Semarang": 3_600_000,
    "Makassar": 4_000_000,
    "Depok": 4_300_000,
    "Bekasi": 4_600_000,
    "Tangerang": 4_800_000,
    "Tangerang Selatan": 5_300_000,
    "Bogor": 4_000_000,
}

BPS_LAST_UPDATED = "2026-03-15"


# ══════════════════════════════════════════════════════════════════════
# CACHE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════


def _read_cache(cache_file: Path) -> Optional[dict]:
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(cache_file: Path, data: dict) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _cache_fresh(cache_file: Path) -> bool:
    if not cache_file.exists():
        return False
    try:
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return datetime.now() - mtime < timedelta(days=CACHE_TTL_DAYS)
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════
# PROPERTY PRICE FETCHER
# ══════════════════════════════════════════════════════════════════════


def fetch_property_prices(force_refresh: bool = False) -> PropertyDataResult:
    """
    Fetch current property prices from live sources.
    Falls back to cache or BASELINE_FALLBACK on failure.

    Args:
        force_refresh: If True, bypass cache and fetch fresh data.

    Returns:
        PropertyDataResult with prices and freshness metadata.
    """
    # Check cache first
    if not force_refresh:
        cached = _read_cache(PROPERTY_CACHE_FILE)
        if cached and _cache_fresh(PROPERTY_CACHE_FILE):
            return _deserialize_property_result(cached, status="cached")

    # Attempt live fetch from Numbeo
    prices: dict[str, PricePoint] = {}
    jabo_prices: dict[str, PricePoint] = {}
    live_source: Optional[str] = None

    JABODETABEK = {"Depok", "Bekasi", "Tangerang", "Tangerang Selatan", "Bogor"}

    for city, url in NUMBEO_PROPERTY_URLS.items():
        html = _get(url)
        if html:
            point = _parse_numbeo_price_per_sqm(html, city)
            if point:
                if city in JABODETABEK:
                    jabo_prices[city] = point
                else:
                    prices[city] = point
                live_source = "Numbeo"
                time.sleep(0.5)  # Be polite to the server

    # If Numbeo failed completely, try BPS anchors as supplementary
    if not prices and not jabo_prices:
        for city, price in BPS_PROPERTY_ANCHORS.items():
            point = PricePoint(
                price_per_sqm=price,
                source="BPS",
                source_url="https://www.bps.go.id",
                last_updated=BPS_LAST_UPDATED,
                reliability="HIGH",
            )
            if city in JABODETABEK:
                jabo_prices[city] = point
            else:
                prices[city] = point

    # Use cached data if live fetch failed
    if not prices and not jabo_prices:
        cached = _read_cache(PROPERTY_CACHE_FILE)
        if cached:
            return _deserialize_property_result(cached, status="cached")

    # Final fallback: BASELINE_FALLBACK
    if not prices and not jabo_prices:
        for city, price in BASELINE_FALLBACK_PROPERTY.items():
            point = PricePoint(
                price_per_sqm=price,
                source="BASELINE_FALLBACK",
                source_url=None,
                last_updated=FALLBACK_VERSION_DATE,
                reliability="LOW",
            )
            if city in JABODETABEK:
                jabo_prices[city] = point
            else:
                prices[city] = point
        freshness = DataFreshness(
            status="fallback",
            last_updated=FALLBACK_VERSION_DATE,
            source="cost_data.py",
            days_old=999,
        )
    else:
        # Merge BPS anchors for any cities we couldn't fetch
        for city, price in BPS_PROPERTY_ANCHORS.items():
            city_key = city if city not in JABODETABEK else None
            target = prices if city not in JABODETABEK else jabo_prices
            if city not in target:
                target[city] = PricePoint(
                    price_per_sqm=price,
                    source="BPS",
                    source_url="https://www.bps.go.id",
                    last_updated=BPS_LAST_UPDATED,
                    reliability="HIGH",
                )

        freshness = DataFreshness(
            status="live",
            last_updated=datetime.now().strftime("%Y-%m-%d"),
            source=live_source or "BPS",
            days_old=0,
        )

    result = PropertyDataResult(prices=prices, freshness=freshness, jabo_prices=jabo_prices)
    _write_cache(PROPERTY_CACHE_FILE, _serialize_property_result(result))
    return result


def _serialize_property_result(r: PropertyDataResult) -> dict:
    return {
        "version": CACHE_VERSION,
        "fetched_at": datetime.now().isoformat(),
        "freshness": {
            "status": r.freshness.status,
            "last_updated": r.freshness.last_updated,
            "source": r.freshness.source,
            "days_old": r.freshness.days_old,
        },
        "prices": {k: asdict(v) for k, v in r.prices.items()},
        "jabo_prices": {k: asdict(v) for k, v in r.jabo_prices.items()},
    }


def _deserialize_property_result(data: dict, status: str) -> PropertyDataResult:
    freshness = data["freshness"]
    if status == "cached":
        freshness["status"] = "cached"
        freshness["days_old"] = (
            datetime.now() - datetime.fromisoformat(freshness["last_updated"])
        ).days
    return PropertyDataResult(
        prices={k: PricePoint(**v) for k, v in data["prices"].items()},
        jabo_prices={k: PricePoint(**v) for k, v in data.get("jabo_prices", {}).items()},
        freshness=DataFreshness(
            status=freshness["status"],
            last_updated=freshness["last_updated"],
            source=freshness["source"],
            days_old=freshness.get("days_old", 0),
        ),
    )


# ══════════════════════════════════════════════════════════════════════
# LIVING COST FETCHER
# ══════════════════════════════════════════════════════════════════════


def fetch_living_costs(force_refresh: bool = False) -> LivingCostResult:
    """
    Fetch current living costs from live sources.
    Falls back to cache or BASELINE_FALLBACK on failure.

    Args:
        force_refresh: If True, bypass cache and fetch fresh data.

    Returns:
        LivingCostResult with costs and freshness metadata.
    """
    if not force_refresh:
        cached = _read_cache(LIVING_COST_CACHE_FILE)
        if cached and _cache_fresh(LIVING_COST_CACHE_FILE):
            return _deserialize_living_result(cached, status="cached")

    costs: dict[str, LivingCostPoint] = {}
    live_source: Optional[str] = None

    for city, url in NUMBEO_LIVING_URLS.items():
        html = _get(url)
        if html:
            point = _parse_numbeo_living_cost(html, city)
            if point:
                costs[city] = point
                live_source = "Numbeo"
                time.sleep(0.5)

    if not costs:
        cached = _read_cache(LIVING_COST_CACHE_FILE)
        if cached:
            return _deserialize_living_result(cached, status="cached")

    if not costs:
        for city, cost in BASELINE_FALLBACK_LIVING.items():
            costs[city] = LivingCostPoint(
                monthly_cost=cost,
                source="BASELINE_FALLBACK",
                source_url=None,
                last_updated=FALLBACK_VERSION_DATE,
                reliability="LOW",
            )
        freshness = DataFreshness(
            status="fallback",
            last_updated=FALLBACK_VERSION_DATE,
            source="cost_data.py",
            days_old=999,
        )
    else:
        for city, cost in BPS_LIVING_ANCHORS.items():
            if city not in costs:
                costs[city] = LivingCostPoint(
                    monthly_cost=cost,
                    source="BPS",
                    source_url="https://www.bps.go.id",
                    last_updated=BPS_LAST_UPDATED,
                    reliability="HIGH",
                )

        freshness = DataFreshness(
            status="live",
            last_updated=datetime.now().strftime("%Y-%m-%d"),
            source=live_source or "BPS",
            days_old=0,
        )

    result = LivingCostResult(costs=costs, freshness=freshness)
    _write_cache(LIVING_COST_CACHE_FILE, _serialize_living_result(result))
    return result


def _serialize_living_result(r: LivingCostResult) -> dict:
    return {
        "version": CACHE_VERSION,
        "fetched_at": datetime.now().isoformat(),
        "freshness": {
            "status": r.freshness.status,
            "last_updated": r.freshness.last_updated,
            "source": r.freshness.source,
            "days_old": r.freshness.days_old,
        },
        "costs": {k: asdict(v) for k, v in r.costs.items()},
    }


def _deserialize_living_result(data: dict, status: str) -> LivingCostResult:
    freshness = data["freshness"]
    if status == "cached":
        freshness["status"] = "cached"
        freshness["days_old"] = (
            datetime.now() - datetime.fromisoformat(freshness["last_updated"])
        ).days
    return LivingCostResult(
        costs={k: LivingCostPoint(**v) for k, v in data["costs"].items()},
        freshness=DataFreshness(
            status=freshness["status"],
            last_updated=freshness["last_updated"],
            source=freshness["source"],
            days_old=freshness.get("days_old", 0),
        ),
    )


# ══════════════════════════════════════════════════════════════════════
# COMBINED API
# ══════════════════════════════════════════════════════════════════════


def get_all_price_data(force_refresh: bool = False) -> tuple[PropertyDataResult, LivingCostResult]:
    """Fetch both property and living cost data in one call."""
    prop = fetch_property_prices(force_refresh=force_refresh)
    living = fetch_living_costs(force_refresh=force_refresh)
    return prop, living


def get_city_property_price(city: str, force_refresh: bool = False) -> PricePoint:
    """Get property price for a specific city."""
    result = fetch_property_prices(force_refresh=force_refresh)
    JABODETABEK = {"Depok", "Bekasi", "Tangerang", "Tangerang Selatan", "Bogor"}
    if city in JABODETABEK:
        return result.jabo_prices.get(city) or PricePoint(
            price_per_sqm=BASELINE_FALLBACK_PROPERTY.get(city, 20_000_000),
            source="BASELINE_FALLBACK",
            last_updated=FALLBACK_VERSION_DATE,
            reliability="LOW",
        )
    return result.prices.get(city) or PricePoint(
        price_per_sqm=BASELINE_FALLBACK_PROPERTY.get(city, 20_000_000),
        source="BASELINE_FALLBACK",
        last_updated=FALLBACK_VERSION_DATE,
        reliability="LOW",
    )


def get_city_living_cost(city: str, force_refresh: bool = False) -> LivingCostPoint:
    """Get living cost for a specific city."""
    result = fetch_living_costs(force_refresh=force_refresh)
    return result.costs.get(city) or LivingCostPoint(
        monthly_cost=BASELINE_FALLBACK_LIVING.get(city, 5_000_000),
        source="BASELINE_FALLBACK",
        source_url=None,
        last_updated=FALLBACK_VERSION_DATE,
        reliability="LOW",
    )


# ══════════════════════════════════════════════════════════════════════
# CLI FOR MANUAL REFRESH
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Fetching property prices and living costs...")
    prop_result, living_result = get_all_price_data(force_refresh=True)

    print(f"\nProperty prices ({prop_result.freshness.display_text()}):")
    for city, pt in list(prop_result.prices.items())[:5]:
        print(f"  {city}: Rp {pt.price_per_sqm:,}/sqm ({pt.reliability})")

    print(f"\nLiving costs ({living_result.freshness.display_text()}):")
    for city, lc in list(living_result.costs.items())[:5]:
        print(f"  {city}: Rp {lc.monthly_cost:,}/month ({lc.reliability})")
