from __future__ import annotations
from typing import Any
from .gemini_service import generate_json
from .platforms import search_url
from .schemas import RecommendationItem, RecommendationResult


def _money(value: Any, default: float = 0.0) -> float:
    try:
        return round(max(0.0, float(value)), 2)
    except (TypeError, ValueError):
        return default


def _normalize(ai: dict[str, Any], budget: float, fallback_title: str) -> RecommendationResult | None:
    try:
        items: list[RecommendationItem] = []
        running = 0.0
        for raw in ai.get("recommendations", [])[:10]:
            price = _money(raw.get("estimated_price"))
            if price <= 0 or running + price > budget * 1.02:
                continue
            platform = str(raw.get("platform", "Amazon")).strip() or "Amazon"
            item_name = str(raw.get("item", "Budget option")).strip()
            items.append(RecommendationItem(
                category=str(raw.get("category", "General")).strip(),
                item=item_name,
                platform=platform,
                estimated_price=price,
                reason=str(raw.get("reason", "Fits the selected budget and preference.")).strip(),
                search_url=search_url(platform, item_name),
            ))
            running += price
        if not items:
            return None
        return RecommendationResult(
            title=str(ai.get("title") or fallback_title),
            summary=str(ai.get("summary") or "Budget-aware recommendations generated for your plan."),
            budget=budget,
            estimated_total=round(running, 2),
            remaining_budget=round(max(0, budget - running), 2),
            recommendations=items,
            tips=[str(x) for x in ai.get("tips", [])[:5]],
            outfit_analysis=ai.get("outfit_analysis"),
            source="gemini",
        )
    except Exception:
        return None


def home_recommendations(budget: float, rooms: str, style: str, needs: str) -> RecommendationResult:
    prompt = f"""
Create a home interior plan for a total budget of INR {budget:.2f}.
Rooms: {rooms}. Preferred style: {style}. Requested items/needs: {needs}.
Use only Amazon, Flipkart, and IKEA as platform names.
Balance functionality, style, and price. Recommend 4-8 useful items.
"""
    ai = generate_json(prompt)
    normalized = _normalize(ai, budget, "Home Interior Budget Plan") if ai else None
    if normalized:
        return normalized

    requested = [x.strip().title() for x in needs.replace(";", ",").split(",") if x.strip()]
    if not requested:
        requested = ["Lighting", "Storage", "Seating", "Decor"]
    requested = requested[:6]
    platforms = ["IKEA", "Amazon", "Flipkart"]
    usable = budget * 0.88
    each = usable / len(requested)
    items = []
    for i, name in enumerate(requested):
        platform = platforms[i % len(platforms)]
        items.append(RecommendationItem(
            category=rooms or "Home",
            item=f"{style.title()} {name}",
            platform=platform,
            estimated_price=round(each, 2),
            reason=f"Allocates a controlled share of the budget to {name.lower()} while matching the {style} preference.",
            search_url=search_url(platform, f"{style} {name}"),
        ))
    total = round(sum(x.estimated_price for x in items), 2)
    return RecommendationResult(
        title="Home Interior Budget Plan",
        summary=f"A balanced starter plan for {rooms or 'your selected rooms'} with a {style} theme.",
        budget=budget,
        estimated_total=total,
        remaining_budget=round(budget - total, 2),
        recommendations=items,
        tips=["Keep 10-15% of the budget as a delivery or installation buffer.", "Compare dimensions before ordering furniture.", "Treat shown prices as estimates and verify them on the linked platform."],
        source="fallback",
    )


def party_recommendations(budget: float, guests: int, event_type: str, venue: str, city: str) -> RecommendationResult:
    prompt = f"""
Plan a {event_type} event in {city or 'the user city'} for {guests} guests with total budget INR {budget:.2f}.
Venue preference: {venue}. Use only Swiggy, Zomato, OYO, Amazon, and Flipkart as platform names.
Allocate the budget across food/catering, venue, decorations, and entertainment. Return 4-7 recommendations.
"""
    ai = generate_json(prompt)
    normalized = _normalize(ai, budget, "Party Budget Plan") if ai else None
    if normalized:
        return normalized

    splits = [
        ("Food & catering", "Swiggy", 0.46),
        ("Venue / stay", "OYO", 0.24),
        ("Decorations", "Amazon", 0.15),
        ("Cake / refreshments", "Zomato", 0.10),
    ]
    items = []
    for label, platform, share in splits:
        price = round(budget * share, 2)
        query = f"{event_type} {label} {city}".strip()
        items.append(RecommendationItem(
            category=label,
            item=f"Budget {label.lower()} option",
            platform=platform,
            estimated_price=price,
            reason=f"Reserves about {int(share*100)}% of the total budget for {label.lower()} for {guests} guests.",
            search_url=search_url(platform, query),
        ))
    total = round(sum(x.estimated_price for x in items), 2)
    return RecommendationResult(
        title="Party Budget Plan",
        summary=f"A practical allocation for a {event_type} with {guests} guests.",
        budget=budget,
        estimated_total=total,
        remaining_budget=round(budget - total, 2),
        recommendations=items,
        tips=["Confirm guest count before placing food orders.", "Keep the remaining amount for transport, taxes, or last-minute needs.", "Verify current prices and availability directly on each platform."],
        source="fallback",
    )


def jewelry_recommendations(
    budget: float,
    occasion: str,
    style: str,
    metal: str,
    outfit_notes: str,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> RecommendationResult:
    prompt = f"""
Recommend jewelry for occasion: {occasion}; style: {style}; preferred metal/tone: {metal};
outfit notes: {outfit_notes or 'not provided'}; total budget: INR {budget:.2f}.
An outfit image may be attached. If present, analyze only visible colors and clothing style for coordination.
Use only Amazon and Flipkart as platform names. Recommend 3-6 options and stay within budget.
"""
    ai = generate_json(prompt, image_bytes=image_bytes, mime_type=mime_type)
    normalized = _normalize(ai, budget, "Jewelry Budget Plan") if ai else None
    if normalized:
        return normalized

    names = ["Necklace set", "Earrings", "Bracelet / bangles"]
    shares = [0.5, 0.3, 0.15]
    platforms = ["Amazon", "Flipkart", "Amazon"]
    items = []
    for name, share, platform in zip(names, shares, platforms):
        price = round(budget * share, 2)
        query = f"{style} {metal} {name} {occasion}"
        items.append(RecommendationItem(
            category="Jewelry",
            item=f"{style.title()} {name}",
            platform=platform,
            estimated_price=price,
            reason=f"Designed to coordinate with the selected {occasion} occasion and {metal} preference.",
            search_url=search_url(platform, query),
        ))
    total = round(sum(x.estimated_price for x in items), 2)
    outfit_analysis = "Image analysis is available when a Gemini API key is configured." if image_bytes else None
    return RecommendationResult(
        title="Jewelry Budget Plan",
        summary=f"A coordinated {style} jewelry set for {occasion} within the selected budget.",
        budget=budget,
        estimated_total=total,
        remaining_budget=round(budget - total, 2),
        recommendations=items,
        tips=["Match metal tone with the outfit's dominant accents.", "Check dimensions and material details before buying.", "Treat shown prices as estimates and verify current listings."],
        outfit_analysis=outfit_analysis,
        source="fallback",
    )
