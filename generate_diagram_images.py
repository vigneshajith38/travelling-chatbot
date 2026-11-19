import os
import sys
from PIL import Image, ImageDraw, ImageFont

def get_font(name, size, bold=False):
    """Load system TrueType font or fallback to default."""
    font_dir = r"C:\Windows\Fonts"
    filename = name
    if name == "segoe":
        filename = "segoeuib.ttf" if bold else "segoeui.ttf"
    elif name == "arial":
        filename = "arialbd.ttf" if bold else "arial.ttf"
    elif name == "calibri":
        filename = "calibrib.ttf" if bold else "calibri.ttf"
    
    font_path = os.path.join(font_dir, filename)
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_rounded_card(draw, xy, radius=12, fill="#FFFFFF", outline="#E2E8F0", width=2):
    """Draws a smooth rounded rectangle card."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow_down(draw, x, y1, y2, color="#475569", width=3, label=None, font=None, label_color="#334155"):
    """Draws a vertical arrow pointing down with optional label."""
    draw.line([(x, y1), (x, y2)], fill=color, width=width)
    # Arrow head
    draw.polygon([(x, y2), (x - 6, y2 - 10), (x + 6, y2 - 10)], fill=color)
    if label and font:
        draw.text((x + 10, (y1 + y2) // 2 - 8), label, fill=label_color, font=font)

def draw_arrow_right(draw, x1, x2, y, color="#475569", width=3, label=None, font=None, label_color="#334155"):
    """Draws a horizontal arrow pointing right with optional label."""
    draw.line([(x1, y), (x2, y)], fill=color, width=width)
    # Arrow head
    draw.polygon([(x2, y), (x2 - 10, y - 6), (x2 - 10, y + 6)], fill=color)
    if label and font:
        draw.text(((x1 + x2) // 2 - 20, y - 18), label, fill=label_color, font=font)

# =========================================================================
# 1. GENERATE ARCHITECTURE BLOCK DIAGRAM
# =========================================================================
def generate_architecture_diagram(output_path="architecture_block_diagram.png"):
    W, H = 2200, 1400
    im = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(im)

    # Fonts
    f_title = get_font("segoe", 46, bold=True)
    f_subtitle = get_font("segoe", 22, bold=False)
    f_sec_title = get_font("segoe", 24, bold=True)
    f_card_title = get_font("segoe", 22, bold=True)
    f_card_sub = get_font("segoe", 17, bold=False)
    f_badge = get_font("segoe", 15, bold=True)
    f_body = get_font("segoe", 16, bold=False)
    f_flow = get_font("segoe", 16, bold=True)

    # Header Banner
    draw.rectangle([0, 0, W, 130], fill="#1E3A2F")
    draw.text((W // 2, 42), "WANDERWISE AI — SYSTEM ARCHITECTURE BLOCK DIAGRAM", fill="#FFFFFF", font=f_title, anchor="mm")
    draw.text((W // 2, 92), "Decoupled Multi-Tier Architecture Pipeline • LLM Reasoning • Transit & Hotel Telemetry", fill="#99F6E4", font=f_subtitle, anchor="mm")

    # -------------------------------------------------------------
    # LAYER 1: CLIENT PRESENTATION TIER (TOP)
    # -------------------------------------------------------------
    y_l1 = 170
    draw.rectangle([50, y_l1, W - 50, y_l1 + 45], fill="#E0F2FE", outline="#0284C7", width=2)
    draw.text((70, y_l1 + 22), "LAYER 1: PRESENTATION TIER (Client Web Application)", fill="#0369A1", font=f_sec_title, anchor="lm")
    draw.text((W - 70, y_l1 + 22), "React 18 • Vite • Tailwind CSS • Leaflet / OSM Maps", fill="#0284C7", font=f_card_sub, anchor="rm")

    cards_l1 = [
        {
            "xy": (60, y_l1 + 60, 560, y_l1 + 230),
            "title": "ChatbotView & Markdown",
            "badge": "UI STREAM",
            "color": "#0284C7",
            "badge_bg": "#E0F2FE",
            "bullets": [
                "• Full GitHub Flavored Markdown (Tables, Lists, Code)",
                "• ChatGPT-style 3-dot thinking indicator",
                "• Multi-turn conversational message history stream",
                "• Contextual suggested action chips & 1-tap prompts"
            ]
        },
        {
            "xy": (590, y_l1 + 60, 1090, y_l1 + 230),
            "title": "Interactive Route Map",
            "badge": "LEAFLET ENGINE",
            "color": "#0D9488",
            "badge_bg": "#CCFBF1",
            "bullets": [
                "• OpenStreetMap vector tiles & custom category pins",
                "• Connective road polylines with curvature calculations",
                "• Interactive popups with photography & secret spot tags",
                "• Tab switcher between Schedule, Map & Budget views"
            ]
        },
        {
            "xy": (1120, y_l1 + 60, 1620, y_l1 + 230),
            "title": "Specialized Widget Embeds",
            "badge": "RICH CARDS",
            "color": "#D97706",
            "badge_bg": "#FEF3C7",
            "bullets": [
                "• itinerary_preview: Day schedule accordions + budgets",
                "• transit_cost_card: Air, rail, bus, cab multimodal grid",
                "• hotel_suggestion_card: Budget, boutique, 5-star tiers",
                "• Direct booking buttons (Google Flights, Booking.com)"
            ]
        },
        {
            "xy": (1650, y_l1 + 60, 2140, y_l1 + 230),
            "title": "Trip & Context Store",
            "badge": "CLIENT STATE",
            "color": "#4F46E5",
            "badge_bg": "#EEF2FF",
            "bullets": [
                "• TripContext & AuthContext React state providers",
                "• DeepSearch toggle state & active destination caching",
                "• Persistent session list with rename/delete actions",
                "• Optimistic message dispatch with zero freeze UI"
            ]
        }
    ]

    for c in cards_l1:
        draw_rounded_card(draw, c["xy"], radius=10, fill="#FFFFFF", outline=c["color"], width=2)
        x1, y1, x2, y2 = c["xy"]
        draw.text((x1 + 18, y1 + 25), c["title"], fill=c["color"], font=f_card_title)
        # Badge
        draw.rounded_rectangle([x2 - 150, y1 + 14, x2 - 18, y1 + 38], radius=6, fill=c["badge_bg"], outline=c["color"], width=1)
        draw.text((x2 - 84, y1 + 26), c["badge"], fill=c["color"], font=f_badge, anchor="mm")
        # Line
        draw.line([(x1 + 18, y1 + 52), (x2 - 18, y1 + 52)], fill="#E2E8F0", width=1)
        # Bullets
        for i, b in enumerate(c["bullets"]):
            draw.text((x1 + 20, y1 + 64 + i * 26), b, fill="#334155", font=f_body)

    # Connecting Arrows: Layer 1 -> Layer 2
    for x_arr in [310, 840, 1370, 1895]:
        draw_arrow_down(draw, x_arr, y_l1 + 230, y_l1 + 295, color="#0D9488", width=3, label="REST / JSON", font=f_flow, label_color="#0D9488")

    # -------------------------------------------------------------
    # LAYER 2: APPLICATION GATEWAY & PERSISTENCE TIER (MIDDLE)
    # -------------------------------------------------------------
    y_l2 = 475
    draw.rectangle([50, y_l2, W - 50, y_l2 + 45], fill="#CCFBF1", outline="#0D9488", width=2)
    draw.text((70, y_l2 + 22), "LAYER 2: APPLICATION GATEWAY & PERSISTENCE (FastAPI Backend)", fill="#0F766E", font=f_sec_title, anchor="lm")
    draw.text((W - 70, y_l2 + 22), "Python 3.14 • FastAPI • Uvicorn • SQLAlchemy ORM • SQLite State DB", fill="#0D9488", font=f_card_sub, anchor="rm")

    cards_l2 = [
        {
            "xy": (60, y_l2 + 60, 720, y_l2 + 230),
            "title": "FastAPI REST API Gateway",
            "badge": "PORT 8000",
            "color": "#0D9488",
            "badge_bg": "#CCFBF1",
            "bullets": [
                "• POST /api/chat/message — Conversational dispatch endpoint",
                "• GET /api/chat/sessions — Multi-session list retrieval",
                "• Mounts compiled React production build directly at root (/)",
                "• Unified single-port deployment with zero CORS friction"
            ]
        },
        {
            "xy": (760, y_l2 + 60, 1420, y_l2 + 230),
            "title": "Session Memory & Context Machine",
            "badge": "STATE ENGINE",
            "color": "#1E3A2F",
            "badge_bg": "#DCFCE7",
            "bullets": [
                "• Context state parser (destination, origin, days, budget, travellers)",
                "• Multi-turn reference resolution ('there', 'that place', 'what about December?')",
                "• Word-boundary regex pipeline preventing false route capture",
                "• Full conversation turn serialization to/from database"
            ]
        },
        {
            "xy": (1460, y_l2 + 60, 2140, y_l2 + 230),
            "title": "Relational Persistence Layer (SQLite)",
            "badge": "DATABASE",
            "color": "#475569",
            "badge_bg": "#F1F5F9",
            "bullets": [
                "• ChatSessions: Session metadata, trip linkage & JSON context state",
                "• ChatMessages: User prompts, assistant answers & structured payloads",
                "• Trips, ItineraryDays & ActivityItems: Clustered schedule models",
                "• User accounts & JWT authentication token verification"
            ]
        }
    ]

    for c in cards_l2:
        draw_rounded_card(draw, c["xy"], radius=10, fill="#FFFFFF", outline=c["color"], width=2)
        x1, y1, x2, y2 = c["xy"]
        draw.text((x1 + 18, y1 + 25), c["title"], fill=c["color"], font=f_card_title)
        draw.rounded_rectangle([x2 - 150, y1 + 14, x2 - 18, y1 + 38], radius=6, fill=c["badge_bg"], outline=c["color"], width=1)
        draw.text((x2 - 84, y1 + 26), c["badge"], fill=c["color"], font=f_badge, anchor="mm")
        draw.line([(x1 + 18, y1 + 52), (x2 - 18, y1 + 52)], fill="#E2E8F0", width=1)
        for i, b in enumerate(c["bullets"]):
            draw.text((x1 + 20, y1 + 64 + i * 26), b, fill="#334155", font=f_body)

    # Connecting Arrows: Layer 2 -> Layer 3
    for x_arr in [390, 1090, 1800]:
        draw_arrow_down(draw, x_arr, y_l2 + 230, y_l2 + 295, color="#1E3A2F", width=3, label="ORCHESTRATION PIPELINE", font=f_flow, label_color="#1E3A2F")

    # -------------------------------------------------------------
    # LAYER 3: INTELLIGENCE & TELEMETRY DOMAIN ENGINES (BOTTOM)
    # -------------------------------------------------------------
    y_l3 = 780
    draw.rectangle([50, y_l3, W - 50, y_l3 + 45], fill="#FEF3C7", outline="#D97706", width=2)
    draw.text((70, y_l3 + 22), "LAYER 3: INTELLIGENCE & TELEMETRY DOMAIN SERVICES (ai_service.py Core)", fill="#92400E", font=f_sec_title, anchor="lm")
    draw.text((W - 70, y_l3 + 22), "Google Gemini Multi-Model Pool • Transit Engine • Hotel Service • Climate Sensors", fill="#D97706", font=f_card_sub, anchor="rm")

    cards_l3 = [
        {
            "xy": (60, y_l3 + 60, 560, y_l3 + 450),
            "title": "Google Gemini LLM Pool",
            "badge": "FAILOVER POOL",
            "color": "#4F46E5",
            "badge_bg": "#EEF2FF",
            "bullets": [
                "• Master Travel System Prompt (195 countries)",
                "• Cascading Candidate Pool:",
                "   1. gemini-3.1-flash-lite (ultra-fast)",
                "   2. gemini-3.5-flash-lite (high depth)",
                "   3. gemini-3.5-flash & 3.8-flash",
                "• 15s deadline timeout per candidate",
                "• Automatic recovery from 503/504 errors",
                "• True multi-turn conversation memory history",
                "• Zero hardcoded destination locks"
            ]
        },
        {
            "xy": (590, y_l3 + 60, 1090, y_l3 + 450),
            "title": "Worldwide Transit Engine",
            "badge": "FARE BENCHMARKS",
            "color": "#D97706",
            "badge_bg": "#FEF3C7",
            "bullets": [
                "• 4 Multimodal Travel Modes:",
                "   ✈️ Commercial Flights (Airlines / Stops)",
                "   🚄 High-Speed & Regional Rail (Eurostar)",
                "   🚌 Intercity Sleeper Buses (FlixBus)",
                "   🚕 Highway Cabs & Private Transfers",
                "• Haversine & geodesic distance modeling",
                "• Dual-currency pricing: INR (₹) & USD ($)",
                "• Pre-filled deep booking portal links:",
                "   Google Flights, Skyscanner, Trainline, RedBus"
            ]
        },
        {
            "xy": (1120, y_l3 + 60, 1620, y_l3 + 450),
            "title": "Worldwide Hotel & Stay Engine",
            "badge": "3-TIER LODGING",
            "color": "#E11D48",
            "badge_bg": "#FFE4E6",
            "bullets": [
                "• 3-Tier Categorization for Every City:",
                "   🎒 Budget & Hostels (₹1,000–₹3,500/nt)",
                "   ✨ Mid-Range Boutique (₹5,500–₹16k/nt)",
                "   👑 5-Star Luxury Resorts (₹22k–₹85k/nt)",
                "• Dynamic global heuristic accommodation generator",
                "• Verified neighborhood suitability & ratings",
                "• Key amenities (Pool, Breakfast, Spa, Balcony)",
                "• 1-Click Search: Booking.com, Agoda, Airbnb"
            ]
        },
        {
            "xy": (1650, y_l3 + 60, 2140, y_l3 + 450),
            "title": "Climate & Dynamic Replanner",
            "badge": "METEOROLOGY",
            "color": "#059669",
            "badge_bg": "#D1FAE5",
            "bullets": [
                "• Open-Meteo synchronous global API integration",
                "• Real-time temperature & apparent heat index",
                "• Rain probability (%) & precipitation volume",
                "• WMO meteorological condition code mapper",
                "• Rainy-day adaptive itinerary swaps:",
                "   Replaces rain-exposed trails with indoor",
                "   museums, artisanal cafes, and covered bazaars",
                "• Free cancellation & packing advisories"
            ]
        }
    ]

    for c in cards_l3:
        draw_rounded_card(draw, c["xy"], radius=10, fill="#FFFFFF", outline=c["color"], width=2)
        x1, y1, x2, y2 = c["xy"]
        draw.text((x1 + 18, y1 + 25), c["title"], fill=c["color"], font=f_card_title)
        draw.rounded_rectangle([x2 - 165, y1 + 14, x2 - 18, y1 + 38], radius=6, fill=c["badge_bg"], outline=c["color"], width=1)
        draw.text((x2 - 91, y1 + 26), c["badge"], fill=c["color"], font=f_badge, anchor="mm")
        draw.line([(x1 + 18, y1 + 52), (x2 - 18, y1 + 52)], fill="#E2E8F0", width=1)
        for i, b in enumerate(c["bullets"]):
            draw.text((x1 + 20, y1 + 64 + i * 24), b, fill="#334155", font=f_body)

    # Footer note banner
    draw.rectangle([0, H - 70, W, H], fill="#0F172A")
    draw.text((W // 2, H - 35), "WANDERWISE AI ARCHITECTURE • MULTI-TIER REASONING • RECONFIGURABLE CLOUD-READY DEPLOYMENT", fill="#94A3B8", font=f_card_sub, anchor="mm")

    im.save(output_path, "PNG", dpi=(300, 300))
    print(f"✅ Created Architecture Block Diagram Image: {output_path}")

# =========================================================================
# 2. GENERATE WORKFLOW / DATA FLOW DIAGRAM
# =========================================================================
def generate_workflow_diagram(output_path="workflow_diagram.png"):
    W, H = 2200, 1400
    im = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(im)

    f_title = get_font("segoe", 44, bold=True)
    f_subtitle = get_font("segoe", 22, bold=False)
    f_stage_num = get_font("segoe", 26, bold=True)
    f_card_title = get_font("segoe", 22, bold=True)
    f_card_sub = get_font("segoe", 17, bold=False)
    f_badge = get_font("segoe", 15, bold=True)
    f_body = get_font("segoe", 16, bold=False)
    f_flow = get_font("segoe", 16, bold=True)

    # Header Banner
    draw.rectangle([0, 0, W, 130], fill="#0F172A")
    draw.text((W // 2, 42), "WANDERWISE AI — CONVERSATIONAL WORKFLOW & DATA PIPELINE", fill="#FFFFFF", font=f_title, anchor="mm")
    draw.text((W // 2, 92), "End-to-End Execution Flow from Natural Language Prompt to Grounded Structured Delivery", fill="#38BDF8", font=f_subtitle, anchor="mm")

    # Flowchart Stages:
    # -------------------------------------------------------------
    # STAGE 1: USER INPUT & FRONTEND INGESTION (Top Left)
    # -------------------------------------------------------------
    s1_xy = (60, 170, 700, 370)
    draw_rounded_card(draw, s1_xy, radius=12, fill="#FFFFFF", outline="#0284C7", width=2)
    draw.rectangle([60, 170, 700, 220], fill="#0284C7")
    draw.text((75, 195), "STEP 1: USER INGESTION & DISPATCH", fill="#FFFFFF", font=f_card_title, anchor="lm")
    draw.text((80, 240), "• User types natural language prompt into chat:", fill="#334155", font=f_body)
    draw.text((95, 268), "\"3 day trip to Munnar\" / \"Flights Delhi to Bali\" / \"Where to stay in Paris?\"", fill="#0369A1", font=get_font("segoe", 15, bold=True))
    draw.text((80, 300), "• Client intercepts message, creates optimistic user bubble in chat window", fill="#334155", font=f_body)
    draw.text((80, 330), "• Dispatches POST /api/chat/message with active session_id & trip_id", fill="#334155", font=f_body)

    # Arrow S1 -> S2 (Right)
    draw_arrow_right(draw, 700, 780, 270, color="#0284C7", width=3, label="HTTP POST", font=f_flow, label_color="#0284C7")

    # -------------------------------------------------------------
    # STAGE 2: BACKEND GATEWAY & SESSION DESERIALIZATION (Top Mid)
    # -------------------------------------------------------------
    s2_xy = (780, 170, 1420, 370)
    draw_rounded_card(draw, s2_xy, radius=12, fill="#FFFFFF", outline="#0D9488", width=2)
    draw.rectangle([780, 170, 1420, 220], fill="#0D9488")
    draw.text((795, 195), "STEP 2: GATEWAY & SESSION RESTORATION", fill="#FFFFFF", font=f_card_title, anchor="lm")
    draw.text((800, 240), "• FastAPI endpoint authenticates user & resolves ChatSession record", fill="#334155", font=f_body)
    draw.text((800, 270), "• Deserializes JSON context_state from SQLite session row", fill="#334155", font=f_body)
    draw.text((800, 300), "• Fetches prior 20 conversational messages formatted as history turns", fill="#334155", font=f_body)
    draw.text((800, 330), "• Forwards message, context & history into ai_service.py orchestrator", fill="#334155", font=f_body)

    # Arrow S2 -> S3 (Right)
    draw_arrow_right(draw, 1420, 1500, 270, color="#0D9488", width=3, label="PARSER", font=f_flow, label_color="#0D9488")

    # -------------------------------------------------------------
    # STAGE 3: MEMORY & ENTITY DISAMBIGUATION (Top Right)
    # -------------------------------------------------------------
    s3_xy = (1500, 170, 2140, 370)
    draw_rounded_card(draw, s3_xy, radius=12, fill="#FFFFFF", outline="#1E3A2F", width=2)
    draw.rectangle([1500, 170, 2140, 220], fill="#1E3A2F")
    draw.text((1515, 195), "STEP 3: CONTEXT STATE EXTRACTION", fill="#FFFFFF", font=f_card_title, anchor="lm")
    draw.text((1520, 240), "• Priority word-boundary match against 195+ international destinations", fill="#334155", font=f_body)
    draw.text((1520, 270), "• Anaphora resolution: 'there', 'that place' resolve to previous destination", fill="#334155", font=f_body)
    draw.text((1520, 300), "• Dynamic extraction of duration, budget, companions & travel style", fill="#334155", font=f_body)
    draw.text((1520, 330), "• Origin-destination route pair extraction (e.g. 'Paris' to 'Amsterdam')", fill="#334155", font=f_body)

    # Big Connecting Arrow from S3 down to Central Intent Dispatcher
    draw_arrow_down(draw, 1820, 370, 440, color="#1E3A2F", width=3, label="EXTRACTED STATE", font=f_flow, label_color="#1E3A2F")

    # -------------------------------------------------------------
    # STAGE 4: MULTI-PATH INTENT CLASSIFICATION HUB (Middle)
    # -------------------------------------------------------------
    s4_xy = (60, 440, 2140, 520)
    draw_rounded_card(draw, s4_xy, radius=12, fill="#FEF3C7", outline="#D97706", width=2)
    draw.text((W // 2, 465), "STEP 4: MULTI-PATH INTENT CLASSIFICATION & TELEMETRY DISPATCH", fill="#92400E", font=f_card_title, anchor="mm")
    draw.text((W // 2, 495), "The AI Orchestrator classifies the utterance into specialized operational branches to fetch real-world telemetry before prompting Gemini", fill="#B45309", font=f_card_sub, anchor="mm")

    # 4 Intent Branches (Columns)
    branches = [
        {
            "xy": (60, 560, 550, 830),
            "title": "Branch A: Itinerary Planner",
            "icon": "🗺️",
            "color": "#059669",
            "bg": "#ECFDF5",
            "bullets": [
                "• Trigger: 'plan', '3 day trip', 'itinerary'",
                "• Resolves coordinates (Nominatim / cache)",
                "• Groups sights by geography & minimal transit",
                "• Structures morning, noon, and sunset stops",
                "• Output: itinerary_preview widget"
            ]
        },
        {
            "xy": (590, 560, 1080, 830),
            "title": "Branch B: Transit Cost Engine",
            "icon": "🧭",
            "color": "#D97706",
            "bg": "#FFFBEB",
            "bullets": [
                "• Trigger: 'flight', 'train', 'bus', 'costs'",
                "• Resolves origin & destination airports/stations",
                "• Models airfares, high-speed rail, sleeper buses",
                "• Injects dual currency brackets: ₹ INR & $ USD",
                "• Output: transit_cost_card widget"
            ]
        },
        {
            "xy": (1120, 560, 1610, 830),
            "title": "Branch C: Hotel & Stays Engine",
            "icon": "🏨",
            "color": "#E11D48",
            "bg": "#FFF1F2",
            "bullets": [
                "• Trigger: 'hotel', 'resort', 'hostel', 'where to stay'",
                "• Derives 3 tiers: Budget, Boutique, 5-Star",
                "• Neighborhood profiles & key verified amenities",
                "• Deep links: Booking.com, Agoda, Airbnb",
                "• Output: hotel_suggestion_card widget"
            ]
        },
        {
            "xy": (1650, 560, 2140, 830),
            "title": "Branch D: Open-Meteo Sensors",
            "icon": "🌦️",
            "color": "#0284C7",
            "bg": "#F0F9FF",
            "bullets": [
                "• Trigger: 'current weather', 'rain', 'temperature'",
                "• Fetches live temperature, rain probability & wind",
                "• Rainy-day adaptive replacement of outdoor sights",
                "• Advises seasonal packing & outdoor windows",
                "• Output: Grounded contextual weather telemetry"
            ]
        }
    ]

    for b in branches:
        draw_rounded_card(draw, b["xy"], radius=10, fill=b["bg"], outline=b["color"], width=2)
        x1, y1, x2, y2 = b["xy"]
        draw.text((x1 + 16, y1 + 25), f"{b['icon']} {b['title']}", fill=b["color"], font=f_card_title)
        draw.line([(x1 + 16, y1 + 50), (x2 - 16, y1 + 50)], fill="#CBD5E1", width=1)
        for i, bull in enumerate(b["bullets"]):
            draw.text((x1 + 18, y1 + 65 + i * 28), bull, fill="#334155", font=f_body)

    # Arrows down to Gemini LLM Pool
    for x_arr in [305, 835, 1365, 1895]:
        draw_arrow_down(draw, x_arr, 830, 890, color="#4F46E5", width=3)

    # -------------------------------------------------------------
    # STAGE 5: GEMINI LLM REASONING & MULTI-MODEL FAILOVER (Bottom Mid)
    # -------------------------------------------------------------
    s5_xy = (60, 890, 1420, 1110)
    draw_rounded_card(draw, s5_xy, radius=12, fill="#FFFFFF", outline="#4F46E5", width=2)
    draw.rectangle([60, 890, 1420, 940], fill="#4F46E5")
    draw.text((75, 915), "STEP 5: GEMINI GENERATIVE REASONING & RESILIENT FAILOVER POOL", fill="#FFFFFF", font=f_card_title, anchor="lm")
    draw.text((80, 960), "• Injects Ground Truth context (live telemetry, fare tables, hotel tiers) into MASTER_TRAVEL_SYSTEM_PROMPT", fill="#334155", font=f_body)
    draw.text((80, 990), "• Passes conversational turn history as types.Content objects (role: 'user', role: 'model')", fill="#334155", font=f_body)
    draw.text((80, 1020), "• Primary candidate: gemini-3.1-flash-lite (15s deadline for ultra-low conversational latency)", fill="#1E1B4B", font=get_font("segoe", 16, bold=True))
    draw.text((80, 1050), "• Automated Failover on 503/504 errors: Rolls to gemini-3.5-flash-lite -> gemini-3.5-flash -> gemini-3.8-flash", fill="#4338CA", font=f_body)
    draw.text((80, 1080), "• Generates nuanced, personalized travel prose formatted in GitHub-flavored Markdown", fill="#334155", font=f_body)

    # Arrow S5 -> S6 (Right)
    draw_arrow_right(draw, 1420, 1500, 1000, color="#4F46E5", width=3, label="SYNTHESIS", font=f_flow, label_color="#4F46E5")

    # -------------------------------------------------------------
    # STAGE 6: RESPONSE PACKAGING & DB COMMIT (Bottom Right)
    # -------------------------------------------------------------
    s6_xy = (1500, 890, 2140, 1110)
    draw_rounded_card(draw, s6_xy, radius=12, fill="#FFFFFF", outline="#1E3A2F", width=2)
    draw.rectangle([1500, 890, 2140, 940], fill="#1E3A2F")
    draw.text((1515, 915), "STEP 6: PERSISTENCE & PACKAGING", fill="#FFFFFF", font=f_card_title, anchor="lm")
    draw.text((1520, 960), "• Bundles markdown prose + structured widget data", fill="#334155", font=f_body)
    draw.text((1520, 990), "• Saves Assistant ChatMessage into SQLite database", fill="#334155", font=f_body)
    draw.text((1520, 1020), "• Updates and commits persistent session context_state", fill="#334155", font=f_body)
    draw.text((1520, 1050), "• Attaches dynamic suggested next action buttons", fill="#334155", font=f_body)
    draw.text((1520, 1080), "• Returns complete JSON response to frontend", fill="#334155", font=f_body)

    # Arrow S6 -> S7 (Down)
    draw_arrow_down(draw, 1820, 1110, 1160, color="#0284C7", width=3)

    # -------------------------------------------------------------
    # STAGE 7: CLIENT RENDERING & INTERACTIVE PRESENTATION (Bottom Full)
    # -------------------------------------------------------------
    s7_xy = (60, 1160, 2140, 1320)
    draw_rounded_card(draw, s7_xy, radius=12, fill="#F0FDF4", outline="#16A34A", width=2)
    draw.text((80, 1195), "STEP 7: INTERACTIVE CLIENT PRESENTATION & ENGAGEMENT", fill="#15803D", font=f_card_title, anchor="lm")
    draw.text((80, 1235), "• Markdown Renderer: Formats bold text, tables, blockquotes, and live hyperlinks smoothly without layout shifts", fill="#166534", font=f_body)
    draw.text((80, 1265), "• Specialized Interactive Widgets: Mounts Leaflet map markers, Day Schedule tabs, Transit Fare Grids, and Hotel Cards", fill="#166534", font=f_body)
    draw.text((80, 1295), "• Action Dispatcher: 1-Click action chips allow users to book live flights, inspect hotel deals, or request follow-ups instantly", fill="#166534", font=f_body)

    # Footer note banner
    draw.rectangle([0, H - 50, W, H], fill="#0F172A")
    draw.text((W // 2, H - 25), "WANDERWISE AI WORKFLOW PIPELINE • RESILIENT ASYNCHRONOUS EXECUTION • PERSISTENT CONTEXT RETENTION", fill="#94A3B8", font=f_badge, anchor="mm")

    im.save(output_path, "PNG", dpi=(300, 300))
    print(f"✅ Created Workflow Diagram Image: {output_path}")

if __name__ == "__main__":
    generate_architecture_diagram("architecture_block_diagram.png")
    generate_workflow_diagram("workflow_diagram.png")
