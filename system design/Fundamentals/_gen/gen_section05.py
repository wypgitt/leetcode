#!/usr/bin/env python3
"""Generate all section-05 Fundamentals system-design docs (550–900+ lines each)."""
from __future__ import annotations

from pathlib import Path

OUT = Path("/Users/yingpengwang/leetcode/system design/Fundamentals")

# slug, title, focus blurb, primary_domain tag
SPECS: list[dict] = [
    {
        "fn": "yelp-places-near-me-system-design.md",
        "title": "Yelp or Places Near Me",
        "focus": "Geo indexes · POI recall · Ranking · Open-now · Viewport · Hot tiles · City sharding",
        "domain": "geo_poi",
        "noun": "place/POI",
        "verbs": "discover nearby businesses",
        "emphasis": ["H3/S2 geo index", "two-stage recall→rank", "open-now correctness", "map viewport caching"],
    },
    {
        "fn": "google-maps-system-design.md",
        "title": "Google Maps",
        "focus": "Tiles · Geocoding · Routing · Traffic · Places · Live location · Multi-layer serving",
        "domain": "maps_platform",
        "noun": "map session",
        "verbs": "serve maps, geocode, route, and traffic",
        "emphasis": ["tile pyramid", "routing graph", "traffic fusion", "geocoder + places"],
    },
    {
        "fn": "route-planning-system-design.md",
        "title": "Route Planning",
        "focus": "Graph routing · Contraction hierarchies · ETA · Multi-stop · Traffic-aware · Alternatives",
        "domain": "routing",
        "noun": "route request",
        "verbs": "compute paths and ETAs",
        "emphasis": ["road graph", "CH/HL algorithms", "traffic weights", "alternative routes"],
    },
    {
        "fn": "nearby-friends-location-sharing-system-design.md",
        "title": "Nearby-Friends Location Sharing",
        "focus": "Live location · Privacy · Friend graph · Geo fanout · Battery · Consent · TTL",
        "domain": "live_social_geo",
        "noun": "location share",
        "verbs": "share and query friend locations",
        "emphasis": ["consent & visibility", "sparse live updates", "friend-scoped geo", "battery budgets"],
    },
    {
        "fn": "uber-lyft-system-design.md",
        "title": "Uber or Lyft",
        "focus": "Marketplace · Matching · Dispatch · Live location · ETA · Surge · Payments · City cells",
        "domain": "rideshare",
        "noun": "trip",
        "verbs": "match riders and drivers end-to-end",
        "emphasis": ["trip state machine", "exclusive dispatch", "surge", "city isolation"],
    },
    {
        "fn": "realtime-driver-location-tracking-system-design.md",
        "title": "Real-Time Driver-Location Tracking",
        "focus": "GPS ingest · Pub/sub · Geo index freshness · Snap-to-road · Fanout · Compression",
        "domain": "live_location",
        "noun": "location ping",
        "verbs": "ingest and serve live driver positions",
        "emphasis": ["ping pipeline", "hot geo index", "rider fanout", "staleness SLOs"],
    },
    {
        "fn": "rider-driver-matching-system-design.md",
        "title": "Rider-Driver Matching",
        "focus": "Dispatch · Offer/accept · Exclusivity · Batching · Fairness · ETA · Cancel/reassign",
        "domain": "matching",
        "noun": "match offer",
        "verbs": "match supply to demand without double-assign",
        "emphasis": ["exclusive locks/leases", "offer protocol", "batch vs greedy", "fairness"],
    },
    {
        "fn": "dispatch-geographic-regions-system-design.md",
        "title": "Dispatch Across Geographic Regions",
        "focus": "City cells · Region routing · Cross-border · Failover · Consistency · Cell ownership",
        "domain": "geo_dispatch",
        "noun": "dispatch cell",
        "verbs": "route and own dispatch by geography",
        "emphasis": ["cell ownership", "cross-region handoff", "blast radius", "directory service"],
    },
    {
        "fn": "eta-prediction-serving-system-design.md",
        "title": "ETA Prediction and Serving",
        "focus": "Features · Models · Online serving · Traffic · Uncertainty · Cache · Feedback loops",
        "domain": "eta",
        "noun": "ETA prediction",
        "verbs": "predict and serve arrival times",
        "emphasis": ["feature store", "model tiers", "calibration", "feedback from completions"],
    },
    {
        "fn": "surge-pricing-system-design.md",
        "title": "Surge Pricing",
        "focus": "Demand/supply hexes · Multipliers · Fairness · Stability · Fraud · Realtime compute",
        "domain": "surge",
        "noun": "surge multiplier",
        "verbs": "compute and apply dynamic prices",
        "emphasis": ["hex demand/supply", "hysteresis", "quote binding", "gaming resistance"],
    },
    {
        "fn": "doordash-local-delivery-system-design.md",
        "title": "DoorDash or Local-Delivery Service",
        "focus": "Three-sided marketplace · Orders · Dasher dispatch · Restaurant prep · ETA · Batching",
        "domain": "food_delivery",
        "noun": "delivery order",
        "verbs": "orchestrate restaurant→dasher→customer delivery",
        "emphasis": ["three-sided sync", "prep-time", "dasher assign", "promise ETAs"],
    },
    {
        "fn": "restaurant-discovery-ranking-system-design.md",
        "title": "Restaurant Discovery and Ranking",
        "focus": "Feed ranking · Geo · Availability · Personalization · Diversity · Latency · Experimentation",
        "domain": "resto_rank",
        "noun": "restaurant impression",
        "verbs": "rank restaurants for discovery feeds",
        "emphasis": ["geo+availability recall", "LTR ranking", "diversity", "open/busy signals"],
    },
    {
        "fn": "food-order-tracking-system-design.md",
        "title": "Food-Order Tracking",
        "focus": "Order state machine · Live maps · Push · Merchant/dasher events · ETA refresh",
        "domain": "order_tracking",
        "noun": "order track session",
        "verbs": "track order progress in realtime",
        "emphasis": ["state machine", "event fanout", "map tracking", "ETA revisions"],
    },
    {
        "fn": "batched-delivery-assignment-system-design.md",
        "title": "Batched Delivery Assignment",
        "focus": "Batching window · Multi-pickup · Constraints · Optimization · Fairness · Realtime",
        "domain": "batch_assign",
        "noun": "delivery batch",
        "verbs": "assign multiple orders to couriers",
        "emphasis": ["batch window", "constraint solver", "reoptimization", "SLA risk"],
    },
    {
        "fn": "delivery-route-optimization-system-design.md",
        "title": "Delivery Route Optimization",
        "focus": "VRP/TSP · Time windows · Capacities · Live replan · Traffic · Couriers",
        "domain": "vrp",
        "noun": "route plan",
        "verbs": "optimize multi-stop courier routes",
        "emphasis": ["VRP heuristics", "time windows", "live replan", "constraint hardness"],
    },
    {
        "fn": "driver-earnings-payouts-system-design.md",
        "title": "Driver Earnings and Payouts",
        "focus": "Ledger · Tips · Adjustments · Payout rails · Idempotency · Tax · Disputes",
        "domain": "earnings",
        "noun": "earnings entry",
        "verbs": "account and pay driver earnings",
        "emphasis": ["double-entry ledger", "payout batching", "idempotent rails", "disputes"],
    },
    {
        "fn": "reviews-ratings-voting-rewards-system-design.md",
        "title": "Reviews, Ratings, Voting, and Reviewer Rewards",
        "focus": "Reviews · Aggregates · Voting · Fraud · Rewards · Ranking impact · Moderation",
        "domain": "reviews",
        "noun": "review",
        "verbs": "capture ratings/reviews and reward quality",
        "emphasis": ["aggregate pipelines", "vote fraud", "moderation", "reward ledger"],
    },
    {
        "fn": "airbnb-rental-marketplace-system-design.md",
        "title": "Airbnb or Rental Marketplace",
        "focus": "Listings · Search · Calendar availability · Booking · Payments · Trust · Messaging",
        "domain": "rental_mkt",
        "noun": "stay booking",
        "verbs": "operate a short-term rental marketplace",
        "emphasis": ["calendar contention", "search+availability", "booking SM", "trust/safety"],
    },
    {
        "fn": "marketplace-listing-search-system-design.md",
        "title": "Marketplace Listing and Search",
        "focus": "Listing CRUD · Search index · Geo+filters · Ranking · Freshness · Photos",
        "domain": "listing_search",
        "noun": "listing document",
        "verbs": "publish listings and power search",
        "emphasis": ["index pipeline", "geo+facet filters", "ranking", "photo CDN"],
    },
    {
        "fn": "rental-booking-system-design.md",
        "title": "Rental Booking",
        "focus": "Inventory calendar · Holds · Checkout · Payments · Idempotency · Overbooking prevention",
        "domain": "rental_book",
        "noun": "booking hold",
        "verbs": "reserve rental inventory safely",
        "emphasis": ["calendar locks", "hold TTL", "payment auth", "no double-book"],
    },
    {
        "fn": "split-stay-search-system-design.md",
        "title": "Split-Stay Search",
        "focus": "Multi-listing itineraries · Combinatorial search · Availability · Ranking · Latency budgets",
        "domain": "split_stay",
        "noun": "split-stay itinerary",
        "verbs": "find multi-listing stay combinations",
        "emphasis": ["combinatorial explosion", "pruning", "availability joins", "latency budgets"],
    },
    {
        "fn": "listing-watchlists-availability-alerts-system-design.md",
        "title": "Listing Watchlists and Availability Alerts",
        "focus": "Watchlists · Change detection · Alert fanout · Dedup · Preference matching · Push",
        "domain": "alerts",
        "noun": "availability alert",
        "verbs": "notify users when watched inventory opens",
        "emphasis": ["watch inverted index", "change CDC", "alert dedup", "quiet hours"],
    },
    {
        "fn": "hotel-search-reservation-system-design.md",
        "title": "Hotel Search and Reservation",
        "focus": "Hotel search · Room inventory · Rates · GDS/OTAs · Holds · Overbooking policies",
        "domain": "hotel",
        "noun": "hotel reservation",
        "verbs": "search hotels and reserve rooms",
        "emphasis": ["rate/inventory", "provider aggregation", "holds", "overbook policy"],
    },
    {
        "fn": "ticketmaster-system-design.md",
        "title": "Ticketmaster",
        "focus": "Onsales · Queues · Seat inventory · Holds · Checkout · Bots · Fairness · Hot events",
        "domain": "tickets",
        "noun": "ticket hold",
        "verbs": "sell event tickets under extreme contention",
        "emphasis": ["waiting room", "seat inventory", "hold TTL", "bot mitigation"],
    },
    {
        "fn": "assigned-seat-reservation-system-design.md",
        "title": "Assigned-Seat Reservation",
        "focus": "Seat maps · Atomic holds · Section inventory · Checkout · Releases · Fairness",
        "domain": "seats",
        "noun": "seat reservation",
        "verbs": "reserve specific seats without conflicts",
        "emphasis": ["seat-level locks", "map UX", "atomic multi-seat hold", "release paths"],
    },
    {
        "fn": "online-auction-system-design.md",
        "title": "Online Auction",
        "focus": "Bids · Soft close · Leader election of price · Idempotency · Notifications · Fraud",
        "domain": "auction",
        "noun": "bid",
        "verbs": "run correct high-contention auctions",
        "emphasis": ["bid ordering", "soft close", "winner correctness", "anti-sniping"],
    },
    {
        "fn": "package-tracking-system-design.md",
        "title": "Package Tracking",
        "focus": "Scan events · Milestones · Carrier ingest · ETA · Notifications · Multi-leg",
        "domain": "parcel_track",
        "noun": "tracking event",
        "verbs": "ingest scans and present package journeys",
        "emphasis": ["event ordering", "milestone SM", "carrier adapters", "ETA"],
    },
    {
        "fn": "shipping-label-carrier-integration-system-design.md",
        "title": "Shipping-Label and Carrier-Integration Service",
        "focus": "Rate shop · Labels · Carrier APIs · Idempotency · Retries · Manifests · Webhooks",
        "domain": "shipping_label",
        "noun": "shipment label",
        "verbs": "rate-shop and purchase carrier labels",
        "emphasis": ["carrier adapters", "idempotent purchase", "label storage", "webhooks"],
    },
    {
        "fn": "warehouse-inventory-fulfillment-system-design.md",
        "title": "Warehouse Inventory and Fulfillment",
        "focus": "Bin inventory · Picks · Waves · Reservations · Idempotent tasks · Multi-FC",
        "domain": "warehouse",
        "noun": "fulfillment task",
        "verbs": "manage warehouse inventory and outbound fulfillment",
        "emphasis": ["bin ledger", "reservation", "wave planning", "scan idempotency"],
    },
    {
        "fn": "fleet-management-platform-system-design.md",
        "title": "Fleet-Management Platform",
        "focus": "Vehicles · Telemetry · Maintenance · Assignment · Geofences · Compliance · Alerts",
        "domain": "fleet",
        "noun": "fleet asset",
        "verbs": "manage vehicle fleets and telemetry",
        "emphasis": ["telemetry ingest", "asset registry", "geofence alerts", "maintenance"],
    },
    {
        "fn": "ev-charging-discovery-reservations-system-design.md",
        "title": "EV Charging-Station Discovery and Reservations",
        "focus": "Charger geo · Availability · Reservations · Sessions · Roaming · Payments · OCPI",
        "domain": "ev_charge",
        "noun": "charge reservation",
        "verbs": "discover chargers and reserve sessions",
        "emphasis": ["charger availability", "reservation holds", "roaming", "session billing"],
    },
    {
        "fn": "dynamic-delivery-pricing-system-design.md",
        "title": "Dynamic Delivery Pricing",
        "focus": "Fees · Incentives · Hex demand · Quote binding · Fairness · Experimentation",
        "domain": "delivery_price",
        "noun": "delivery quote",
        "verbs": "price local deliveries dynamically",
        "emphasis": ["fee components", "incentive coupling", "quote TTL", "marketplace balance"],
    },
    {
        "fn": "offline-reservation-cache-mobile-system-design.md",
        "title": "Offline Reservation Cache for Mobile Clients",
        "focus": "Offline-first · Local cache · Conflict resolution · Sync · Holds · Idempotency · UX",
        "domain": "offline_res",
        "noun": "offline reservation",
        "verbs": "let mobile clients reserve with intermittent connectivity",
        "emphasis": ["local durable queue", "sync protocol", "conflict UX", "server authority"],
    },
]


def domain_profile(d: str) -> dict:
    """Return domain-specific metrics, APIs, model bits, etc."""
    profiles = {
        "geo_poi": {
            "baseline": {
                "Primary QPS": "5K nearby",
                "Entities": "50M POIs",
                "Write QPS": "100 catalog",
                "Payload": "5 KB",
                "Hot structure": "geohash tile cache",
            },
            "scale_metric": "Nearby QPS",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("POIs", "50M", "500M", "5B", "50B"),
                ("Viewport QPS", "10K", "100K", "1M", "10M"),
                ("Index lag p99", "60s", "30s", "15s", "5–15s"),
                ("Cache hit", "60%", "70%", "80%", "85%+"),
            ],
            "apis": [
                "GET /v1/places/nearby?lat&lng&radius_m&filters&cursor",
                "GET /v1/places/viewport?bbox&zoom&filters",
                "GET /v1/places/{id}",
                "PUT /v1/admin/places/{id}",
            ],
            "entities": [
                "Place{id,lat,lng,cells[],cats[],hours,rating_avg,status}",
                "GeoPosting{cell→place_ids}",
                "QueryCache{key→page}",
            ],
            "algo": "H3 k-ring recall → filter → haversine refine → score → page",
        },
        "maps_platform": {
            "baseline": {
                "Primary QPS": "50K tile+API",
                "Entities": "global road graph + POIs",
                "Write QPS": "traffic probes 100K+",
                "Payload": "tiles 10–50KB",
                "Hot structure": "tile CDN + edge",
            },
            "scale_metric": "Map API QPS",
            "scale_vals": ["50K", "500K", "5M", "50M"],
            "extra_metrics": [
                ("Tile QPS", "200K", "2M", "20M", "200M"),
                ("Directions QPS", "5K", "50K", "500K", "5M"),
                ("Geocode QPS", "10K", "100K", "1M", "10M"),
                ("Traffic update Hz", "city tiles 1/min", "higher", "probe stream", "global fusion"),
            ],
            "apis": [
                "GET /tiles/{z}/{x}/{y}",
                "GET /v1/geocode?q= / /v1/reverse?lat&lng",
                "POST /v1/directions {origin,destination,mode,depart_at}",
                "GET /v1/traffic/viewport?bbox",
            ],
            "entities": [
                "Tile{z,x,y,bytes,etag}",
                "GraphNode/Edge{id,coords,speed_class,restrictions}",
                "TrafficWeight{edge_id,speed,confidence,ts}",
                "Place / GeocodeDoc",
            ],
            "algo": "tile pyramid + CH routing on traffic-weighted graph + geocoder retrieval",
        },
        "routing": {
            "baseline": {
                "Primary QPS": "3K directions",
                "Entities": "50M edges/region",
                "Write QPS": "traffic 10K",
                "Payload": "8–20 KB route",
                "Hot structure": "CH prep graphs",
            },
            "scale_metric": "Directions QPS",
            "scale_vals": ["3K", "30K", "300K", "3M"],
            "extra_metrics": [
                ("p99 route latency", "200ms", "150ms", "120ms", "100ms+edge cache"),
                ("Alt routes computed", "1–3", "1–3", "budgeted", "selective"),
                ("Graph size/region", "50M edges", "multi-region", "global shards", "cells"),
            ],
            "apis": [
                "POST /v1/route {src,dst,mode,constraints,alternatives}",
                "POST /v1/matrix {sources[],targets[]}",
                "POST /v1/route:refresh {route_id,live_traffic}",
            ],
            "entities": [
                "Edge{id,from,to,length_m,base_speed,flags}",
                "CHOverlay / HubLabels",
                "RouteResult{polyline,eta_s,distance_m,legs[]}",
            ],
            "algo": "bidirectional Dijkstra/A* on CH or hub labels; traffic overlays",
        },
        "live_social_geo": {
            "baseline": {
                "Primary QPS": "20K loc updates",
                "Entities": "5M sharers",
                "Write QPS": "20K",
                "Payload": "200B ping",
                "Hot structure": "friend loc cache",
            },
            "scale_metric": "Location updates/s",
            "scale_vals": ["20K", "200K", "2M", "20M"],
            "extra_metrics": [
                ("Nearby-friend queries/s", "5K", "50K", "500K", "5M"),
                ("Friends/user median", "50", "50", "80", "100"),
                ("Ping interval", "10–60s adaptive", "adaptive", "adaptive", "budgeted"),
            ],
            "apis": [
                "POST /v1/location {lat,lng,accuracy,ts,visibility}",
                "GET /v1/friends/nearby?radius_m",
                "PUT /v1/sharing/settings",
                "WS /v1/stream/friends",
            ],
            "entities": [
                "SharePolicy{user,audience,precision,expires}",
                "LiveLoc{user,lat,lng,ts,cell}",
                "FriendEdge{u,v}",
            ],
            "algo": "policy check → write live loc → friend-scoped geo index → push deltas",
        },
        "rideshare": {
            "baseline": {
                "Primary QPS": "2K trip requests",
                "Entities": "50K drivers/city peak",
                "Write QPS": "loc 100K",
                "Payload": "trip events",
                "Hot structure": "city dispatch cell",
            },
            "scale_metric": "Trip requests/min/city",
            "scale_vals": ["2K", "20K", "200K", "2M global"],
            "extra_metrics": [
                ("Active drivers", "50K", "500K", "5M", "50M"),
                ("Loc updates/s", "100K", "1M", "10M", "100M"),
                ("Match p50", "15s", "15s", "20s", "cell-local"),
                ("Payment capture QPS", "500", "5K", "50K", "500K"),
            ],
            "apis": [
                "POST /v1/quotes",
                "POST /v1/trips (Idempotency-Key)",
                "POST /v1/trips/{id}/cancel",
                "GET /v1/trips/{id}",
                "WS locations / trip events",
            ],
            "entities": [
                "Trip{id,rider,driver,state,pickup,dropoff,quote_id}",
                "Driver{status,loc,product}",
                "Quote{price,eta,surge,expires}",
                "PaymentIntent",
            ],
            "algo": "quote → pay hold → dispatch exclusive match → trip SM → capture",
        },
        "live_location": {
            "baseline": {
                "Primary QPS": "200K pings",
                "Entities": "100K active drivers",
                "Write QPS": "200K",
                "Payload": "100–300B",
                "Hot structure": "Redis GEO/H3 sets",
            },
            "scale_metric": "Pings/s",
            "scale_vals": ["200K", "2M", "20M", "200M"],
            "extra_metrics": [
                ("Subscribers (riders)", "50K", "500K", "5M", "50M"),
                ("Fanout msgs/s", "100K", "1M", "10M", "100M"),
                ("Freshness p95", "5s", "5s", "3–5s", "region SLO"),
            ],
            "apis": [
                "POST /v1/drivers/{id}/location",
                "GET /v1/drivers/nearby?lat&lng&r",
                "WS /v1/trips/{id}/track",
            ],
            "entities": [
                "Ping{driver_id,lat,lng,heading,speed,ts,seq}",
                "LiveIndex{cell→driver_id}",
                "TrackSubscription{trip_id,user}",
            ],
            "algo": "validate → compress/snap → update index → kafka → fanout subscribers",
        },
        "matching": {
            "baseline": {
                "Primary QPS": "1K match/s city",
                "Entities": "demand+supply pools",
                "Write QPS": "offers/acks",
                "Payload": "offer events",
                "Hot structure": "dispatch leases",
            },
            "scale_metric": "Match decisions/s",
            "scale_vals": ["1K", "10K", "100K", "1M"],
            "extra_metrics": [
                ("Offer accept rate", "70%", "varies", "varies", "varies"),
                ("Double-assign rate", "0", "0", "0", "0 (invariant)"),
                ("Reassign rate", "5%", "5–10%", "storms", "degrade modes"),
            ],
            "apis": [
                "POST /v1/dispatch:request",
                "POST /v1/offers/{id}/accept|reject",
                "POST /v1/dispatch:reassign",
            ],
            "entities": [
                "Demand{trip_id,pickup,constraints}",
                "Offer{id,driver_id,trip_id,expires}",
                "Lease{driver_id,trip_id,token,ttl}",
            ],
            "algo": "candidate geo → score → exclusive lease → offer → accept/timeout → commit",
        },
        "geo_dispatch": {
            "baseline": {
                "Primary QPS": "2K dispatch",
                "Entities": "200 city cells",
                "Write QPS": "ownership heartbeats",
                "Payload": "dispatch msgs",
                "Hot structure": "cell leader",
            },
            "scale_metric": "Cities/cells",
            "scale_vals": ["200", "2K", "20K", "200K microcells"],
            "extra_metrics": [
                ("Cross-cell trips %", "5%", "5%", "8%", "handled via handoff"),
                ("Failover time", "30s", "15s", "10s", "5–10s"),
            ],
            "apis": [
                "GET /v1/directory/lookup?lat&lng",
                "POST /v1/cells/{id}/dispatch",
                "POST /v1/cells/{id}/handoff",
            ],
            "entities": [
                "Cell{id,polygon,owner,epoch}",
                "Directory{geo→cell}",
                "HandoffRecord{trip,from,to}",
            ],
            "algo": "geo→cell directory → cell-owned matching → handoff protocol on borders",
        },
        "eta": {
            "baseline": {
                "Primary QPS": "10K predict",
                "Entities": "feature vectors",
                "Write QPS": "feedback 2K",
                "Payload": "1 KB features",
                "Hot structure": "model cache + features",
            },
            "scale_metric": "ETA QPS",
            "scale_vals": ["10K", "100K", "1M", "10M"],
            "extra_metrics": [
                ("MAPE target", "20%", "18%", "15%", "segmented"),
                ("Feature fetch p99", "20ms", "15ms", "10ms", "edge features"),
                ("Model versions", "few", "many experiments", "per-city", "cell models"),
            ],
            "apis": [
                "POST /v1/eta {od_pair,product,context}",
                "POST /v1/eta:batch",
                "POST /v1/eta/feedback {trip_id,actuals}",
            ],
            "entities": [
                "FeatureRow{entity_keys,values,ts}",
                "Model{id,version,artifact}",
                "Prediction{mu,sigma,expires}",
            ],
            "algo": "fetch features → model infer → calibrate → cache → async feedback train",
        },
        "surge": {
            "baseline": {
                "Primary QPS": "5K quote",
                "Entities": "hex multipliers",
                "Write QPS": "hex compute 1K",
                "Payload": "multiplier map",
                "Hot structure": "hex state Redis",
            },
            "scale_metric": "Pricing quotes/s",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("Hexes/city", "5K", "5–20K", "global", "global"),
                ("Recompute period", "5–15s", "5s", "1–5s", "stream"),
                ("Multiplier churn", "bounded", "hysteresis", "strict", "strict"),
            ],
            "apis": [
                "GET /v1/surge?lat&lng&product",
                "POST /v1/quotes (includes surge_id)",
                "GET /v1/surge/heatmap?city",
            ],
            "entities": [
                "HexState{demand,supply,mult,ts}",
                "SurgeVersion{id,hex→mult}",
                "Quote{surge_version,price,expires}",
            ],
            "algo": "aggregate demand/supply → smoothed mult → bind into quote TTL",
        },
        "food_delivery": {
            "baseline": {
                "Primary QPS": "1K orders",
                "Entities": "restaurants+dashers",
                "Write QPS": "order events",
                "Payload": "order+track",
                "Hot structure": "city marketplace",
            },
            "scale_metric": "Orders/min",
            "scale_vals": ["1K", "10K", "100K", "1M"],
            "extra_metrics": [
                ("Active dashers", "30K", "300K", "3M", "30M"),
                ("Restaurants", "100K", "1M", "10M", "50M"),
                ("Assign p50", "60s", "60s", "90s", "regional"),
            ],
            "apis": [
                "POST /v1/orders",
                "GET /v1/orders/{id}/track",
                "POST /v1/dashers/assign hooks",
                "POST /v1/merchants/{id}/prep_eta",
            ],
            "entities": [
                "Order{state,restaurant,customer,dasher,etas}",
                "Dasher{loc,capacity,status}",
                "MerchantPrepSignal",
            ],
            "algo": "order → merchant accept/prep → dasher assign (batch?) → pickup → dropoff",
        },
        "resto_rank": {
            "baseline": {
                "Primary QPS": "8K feed",
                "Entities": "1M restaurants/region",
                "Write QPS": "availability 5K",
                "Payload": "feed page 10KB",
                "Hot structure": "geo recall + LTR",
            },
            "scale_metric": "Feed QPS",
            "scale_vals": ["8K", "80K", "800K", "8M"],
            "extra_metrics": [
                ("Candidates/query", "1–5K", "capped", "capped", "multi-stage"),
                ("Personalization", "off/light", "on", "heavy", "two-tower"),
            ],
            "apis": [
                "GET /v1/discovery?lat&lng&mealtime&cursor",
                "GET /v1/restaurants/{id}",
            ],
            "entities": [
                "RestaurantDoc{geo,cuisine,rating,availability}",
                "UserFeatures",
                "ImpressionLog",
            ],
            "algo": "geo+hours recall → filters → LTR → diversity → page",
        },
        "order_tracking": {
            "baseline": {
                "Primary QPS": "20K events",
                "Entities": "open orders",
                "Write QPS": "20K",
                "Payload": "track push 1KB",
                "Hot structure": "order event log",
            },
            "scale_metric": "Track events/s",
            "scale_vals": ["20K", "200K", "2M", "20M"],
            "extra_metrics": [
                ("Concurrent trackers", "100K", "1M", "10M", "100M"),
                ("Push fanout/s", "50K", "500K", "5M", "50M"),
            ],
            "apis": [
                "GET /v1/orders/{id}/timeline",
                "WS /v1/orders/{id}/stream",
                "POST /v1/orders/{id}/events (internal)",
            ],
            "entities": [
                "OrderState{state,version}",
                "TrackEvent{seq,type,ts,payload}",
                "ETARefresh",
            ],
            "algo": "append event → SM transition → notify subscribers → refresh ETA",
        },
        "batch_assign": {
            "baseline": {
                "Primary QPS": "500 assigns",
                "Entities": "orders in window",
                "Write QPS": "assignments",
                "Payload": "batch plans",
                "Hot structure": "optimizer workers",
            },
            "scale_metric": "Orders optimized/s",
            "scale_vals": ["500", "5K", "50K", "500K"],
            "extra_metrics": [
                ("Batch window", "30–90s", "adaptive", "adaptive", "per-cell"),
                ("Avg orders/batch", "2–4", "2–5", "constrained", "constrained"),
            ],
            "apis": [
                "POST /v1/assign:batch",
                "POST /v1/assign:reoptimize",
                "GET /v1/batches/{id}",
            ],
            "entities": [
                "OrderPool{cell,orders[]}",
                "Batch{courier,order_ids[],route}",
                "ConstraintSet",
            ],
            "algo": "window collect → score bundles → assign exclusive → optional reoptimize",
        },
        "vrp": {
            "baseline": {
                "Primary QPS": "200 plans/s",
                "Entities": "stops per courier",
                "Write QPS": "replan triggers",
                "Payload": "route plans",
                "Hot structure": "solver fleet",
            },
            "scale_metric": "Replans/s",
            "scale_vals": ["200", "2K", "20K", "200K"],
            "extra_metrics": [
                ("Stops/route", "5–30", "5–30", "capped", "hierarchical"),
                ("Solve time budget", "2s", "1–2s", "200–500ms", "heuristics only"),
            ],
            "apis": [
                "POST /v1/routes:optimize",
                "POST /v1/routes/{id}:replan",
            ],
            "entities": [
                "Stop{id,loc,tw_open,tw_close,service_s}",
                "Vehicle{capacity,shift}",
                "Plan{seq[],etas[],cost}",
            ],
            "algo": "VRP heuristic (ALNS/insertion) under time budget; live replan on events",
        },
        "earnings": {
            "baseline": {
                "Primary QPS": "2K ledger writes",
                "Entities": "drivers",
                "Write QPS": "2K",
                "Payload": "money events",
                "Hot structure": "ledger partitions",
            },
            "scale_metric": "Ledger txs/s",
            "scale_vals": ["2K", "20K", "200K", "2M"],
            "extra_metrics": [
                ("Payouts/day", "100K", "1M", "10M", "100M"),
                ("Dispute rate", "0.5%", "0.5%", "0.5%", "scaled ops"),
            ],
            "apis": [
                "POST /v1/earnings/entries",
                "GET /v1/earnings/balance",
                "POST /v1/payouts:run",
                "POST /v1/payouts/{id}/retry",
            ],
            "entities": [
                "Account{driver_id}",
                "JournalEntry{id,debits[],credits[],idem_key}",
                "Payout{amount,rail,status}",
            ],
            "algo": "idempotent journal append → balance materialize → payout batch → rail ack",
        },
        "reviews": {
            "baseline": {
                "Primary QPS": "3K reads",
                "Entities": "reviews",
                "Write QPS": "500 reviews",
                "Payload": "review text",
                "Hot structure": "aggregates cache",
            },
            "scale_metric": "Review writes/s",
            "scale_vals": ["500", "5K", "50K", "500K"],
            "extra_metrics": [
                ("Votes/s", "2K", "20K", "200K", "2M"),
                ("Mod queue depth", "varies", "scaled", "ML prefilter", "global"),
            ],
            "apis": [
                "POST /v1/reviews",
                "POST /v1/reviews/{id}/votes",
                "GET /v1/entities/{id}/reviews",
                "POST /v1/rewards:grant",
            ],
            "entities": [
                "Review{id,entity,user,stars,text,status}",
                "Aggregate{avg,count,hist}",
                "Vote{user,review,value}",
                "RewardLedger",
            ],
            "algo": "write review → moderate → update aggregates → optional reward → rank feed",
        },
        "rental_mkt": {
            "baseline": {
                "Primary QPS": "5K search",
                "Entities": "5M listings",
                "Write QPS": "booking 200",
                "Payload": "search results",
                "Hot structure": "search+calendar",
            },
            "scale_metric": "Search QPS",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("Bookings/s peak", "200", "2K", "20K", "200K"),
                ("Listings", "5M", "50M", "500M", "5B"),
                ("Calendar conflicts blocked", "100%", "100%", "100%", "100%"),
            ],
            "apis": [
                "GET /v1/search",
                "GET /v1/listings/{id}",
                "POST /v1/bookings",
                "POST /v1/messages",
            ],
            "entities": [
                "Listing{id,geo,attrs,host}",
                "CalendarDay{listing,date,status}",
                "Booking{state,dates,guest,payment}",
            ],
            "algo": "search filter by availability → hold nights → pay → confirm / release",
        },
        "listing_search": {
            "baseline": {
                "Primary QPS": "8K search",
                "Entities": "10M listings",
                "Write QPS": "1K index updates",
                "Payload": "8 KB",
                "Hot structure": "search cluster",
            },
            "scale_metric": "Search QPS",
            "scale_vals": ["8K", "80K", "800K", "8M"],
            "extra_metrics": [
                ("Index docs", "10M", "100M", "1B", "10B"),
                ("Ingest lag", "30s", "15s", "5–15s", "near-real-time"),
            ],
            "apis": [
                "GET /v1/listings/search?q&geo&facets&cursor",
                "PUT /v1/listings/{id}",
                "POST /v1/listings/{id}/photos",
            ],
            "entities": [
                "ListingDoc{text,geo,facets,rank_features}",
                "PhotoObject",
                "IndexCheckpoint",
            ],
            "algo": "CRUD → CDC → analyze/index → query rewrite → retrieve → rank",
        },
        "rental_book": {
            "baseline": {
                "Primary QPS": "300 booking",
                "Entities": "calendars",
                "Write QPS": "300",
                "Payload": "booking tx",
                "Hot structure": "row locks / leases",
            },
            "scale_metric": "Booking attempts/s",
            "scale_vals": ["300", "3K", "30K", "300K"],
            "extra_metrics": [
                ("Hold TTL", "5–15m", "5–15m", "adaptive", "adaptive"),
                ("Overbook rate", "0", "0", "0", "0 invariant"),
            ],
            "apis": [
                "POST /v1/holds",
                "POST /v1/bookings:confirm",
                "POST /v1/holds/{id}:release",
            ],
            "entities": [
                "Hold{id,listing,dates[],expires,token}",
                "Booking{id,hold_id,state}",
                "CalendarCell{listing,date,state}",
            ],
            "algo": "conditional calendar update → hold TTL → payment → confirm CAS",
        },
        "split_stay": {
            "baseline": {
                "Primary QPS": "200 complex searches",
                "Entities": "listing pairs+",
                "Write QPS": "calendar reads",
                "Payload": "itineraries",
                "Hot structure": "search workers",
            },
            "scale_metric": "Split searches/s",
            "scale_vals": ["200", "2K", "20K", "200K"],
            "extra_metrics": [
                ("Max segments", "2", "2–3", "2–3", "hard cap"),
                ("Combos evaluated", "10K", "capped", "pruned", "pruned+ML"),
            ],
            "apis": [
                "POST /v1/search:split_stay {dates,geo,constraints}",
            ],
            "entities": [
                "Segment{listing,start,end}",
                "Itinerary{segments[],score,total_price}",
                "AvailabilityBitmap",
            ],
            "algo": "split date continuum → candidate listings/segment → prune → score combos",
        },
        "alerts": {
            "baseline": {
                "Primary QPS": "1K watch writes",
                "Entities": "watches",
                "Write QPS": "availability CDC 5K",
                "Payload": "push alerts",
                "Hot structure": "inverted watches",
            },
            "scale_metric": "Alert evaluations/s",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("Watches stored", "10M", "100M", "1B", "10B"),
                ("Push/s peak", "2K", "20K", "200K", "2M"),
            ],
            "apis": [
                "POST /v1/watchlists",
                "GET /v1/watchlists",
                "internal: availability.changed → matcher",
            ],
            "entities": [
                "Watch{user,listing|query,prefs}",
                "WatchIndex{listing→watch_ids}",
                "Alert{id,dedup_key,state}",
            ],
            "algo": "CDC availability → match watches → dedup → respect quiet hours → push",
        },
        "hotel": {
            "baseline": {
                "Primary QPS": "4K search",
                "Entities": "hotels+room types",
                "Write QPS": "ARIQ updates",
                "Payload": "rates",
                "Hot structure": "provider cache",
            },
            "scale_metric": "Hotel search QPS",
            "scale_vals": ["4K", "40K", "400K", "4M"],
            "extra_metrics": [
                ("Reservation/s", "100", "1K", "10K", "100K"),
                ("Providers", "few", "many", "many+GDS", "global"),
            ],
            "apis": [
                "GET /v1/hotels/search",
                "POST /v1/hotels/quotes",
                "POST /v1/reservations",
            ],
            "entities": [
                "Hotel{id,geo,stars}",
                "RoomRate{hotel,room_type,dates,price,alloc}",
                "Reservation{state,provider_refs}",
            ],
            "algo": "search cache/providers → rate shop → hold allotment → book → confirm",
        },
        "tickets": {
            "baseline": {
                "Primary QPS": "onsale 50K+",
                "Entities": "seats/events",
                "Write QPS": "holds",
                "Payload": "seat holds",
                "Hot structure": "event inventory shard",
            },
            "scale_metric": "Hold attempts/s/event",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("Queue admits/s", "2K", "20K", "200K", "2M"),
                ("Checkout success", "varies", "fairness", "fairness", "fairness"),
                ("Double-sell", "0", "0", "0", "0"),
            ],
            "apis": [
                "POST /v1/queue/entry",
                "POST /v1/events/{id}/holds",
                "POST /v1/checkouts",
                "GET /v1/events/{id}/seatmap",
            ],
            "entities": [
                "Event{id,venue,onsale_at}",
                "Seat{id,section,row,status}",
                "Hold{seats[],expires,user}",
                "Order",
            ],
            "algo": "waiting room → admit → seat hold CAS → pay → finalize tickets",
        },
        "seats": {
            "baseline": {
                "Primary QPS": "10K seat ops",
                "Entities": "venue seats",
                "Write QPS": "holds",
                "Payload": "seatmap diffs",
                "Hot structure": "seat bitmaps/rows",
            },
            "scale_metric": "Seat hold ops/s",
            "scale_vals": ["10K", "100K", "1M", "10M"],
            "extra_metrics": [
                ("Seats/venue", "20K", "20–100K", "stadium", "multi-venue"),
                ("Multi-seat atomicity", "required", "required", "required", "required"),
            ],
            "apis": [
                "GET /v1/seatmaps/{event_id}",
                "POST /v1/holds {seat_ids[]}",
                "POST /v1/holds/{id}/extend",
            ],
            "entities": [
                "SeatMap",
                "SeatState{seat_id,state,hold_id}",
                "Hold",
            ],
            "algo": "select seats → atomic multi-seat conditional update → TTL → checkout",
        },
        "auction": {
            "baseline": {
                "Primary QPS": "5K bids",
                "Entities": "auctions",
                "Write QPS": "5K",
                "Payload": "bid",
                "Hot structure": "auction leader row",
            },
            "scale_metric": "Bids/s",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("Auctions concurrent", "100K", "1M", "10M", "100M"),
                ("Soft-close extensions", "enabled", "enabled", "enabled", "enabled"),
            ],
            "apis": [
                "POST /v1/auctions/{id}/bids (Idempotency-Key)",
                "GET /v1/auctions/{id}",
                "WS /v1/auctions/{id}/stream",
            ],
            "entities": [
                "Auction{state,end_at,reserve}",
                "Bid{id,auction,user,amount,ts}",
                "HighBid{amount,user,version}",
            ],
            "algo": "validate bid → CAS high mark → extend soft close → notify → settle winner",
        },
        "parcel_track": {
            "baseline": {
                "Primary QPS": "30K scans",
                "Entities": "packages",
                "Write QPS": "30K",
                "Payload": "scan event",
                "Hot structure": "tracking log",
            },
            "scale_metric": "Scan events/s",
            "scale_vals": ["30K", "300K", "3M", "30M"],
            "extra_metrics": [
                ("Active packages", "50M", "500M", "5B", "50B"),
                ("Notify/s", "10K", "100K", "1M", "10M"),
            ],
            "apis": [
                "POST /v1/track/events",
                "GET /v1/track/{tracking_number}",
                "WS subscribe",
            ],
            "entities": [
                "Shipment{tn,legs[]}",
                "ScanEvent{tn,ts,loc,code,seq}",
                "Milestone{state}",
            ],
            "algo": "ingest scan → order/dedup → milestone SM → ETA update → notify",
        },
        "shipping_label": {
            "baseline": {
                "Primary QPS": "500 purchases",
                "Entities": "shipments",
                "Write QPS": "500",
                "Payload": "label PDF/ZPL",
                "Hot structure": "carrier adapters",
            },
            "scale_metric": "Label purchases/s",
            "scale_vals": ["500", "5K", "50K", "500K"],
            "extra_metrics": [
                ("Rate quotes/s", "2K", "20K", "200K", "2M"),
                ("Carrier timeout rate", "1–3%", "mitigated", "circuit break", "multi-carrier"),
            ],
            "apis": [
                "POST /v1/rates",
                "POST /v1/shipments (Idempotency-Key)",
                "GET /v1/shipments/{id}/label",
                "POST /v1/webhooks/carrier",
            ],
            "entities": [
                "Shipment{id,from,to,parcels[],status}",
                "RateQuote",
                "LabelObject{url,format}",
                "CarrierTxn{idem_key}",
            ],
            "algo": "rate shop → purchase idempotent → store label → manifest → track webhooks",
        },
        "warehouse": {
            "baseline": {
                "Primary QPS": "5K scan confirms",
                "Entities": "bins/SKUs",
                "Write QPS": "5K",
                "Payload": "task events",
                "Hot structure": "FC cell ledger",
            },
            "scale_metric": "Scan confirms/s/FC",
            "scale_vals": ["5K", "15K", "50K", "network 1K FCs"],
            "extra_metrics": [
                ("SKUs/FC", "100K", "1M", "1M+", "1M+"),
                ("Ship units/day/FC", "100K", "300K", "1M", "3M"),
            ],
            "apis": [
                "POST /v1/inventory/events",
                "POST /v1/tasks/{id}/complete",
                "POST /v1/waves:plan",
            ],
            "entities": [
                "BinQty{bin,sku,qty}",
                "InventoryEvent{idem,type}",
                "PickTask",
                "Wave",
            ],
            "algo": "reserve inventory → plan waves → assign tasks → scan complete → pack/ship",
        },
        "fleet": {
            "baseline": {
                "Primary QPS": "100K telemetry",
                "Entities": "vehicles",
                "Write QPS": "100K",
                "Payload": "telem 200B",
                "Hot structure": "fleet geo + rules",
            },
            "scale_metric": "Telemetry points/s",
            "scale_vals": ["100K", "1M", "10M", "100M"],
            "extra_metrics": [
                ("Vehicles", "100K", "1M", "10M", "100M"),
                ("Geofence alerts/s", "100", "1K", "10K", "100K"),
            ],
            "apis": [
                "POST /v1/telemetry",
                "GET /v1/vehicles/nearby",
                "POST /v1/assignments",
                "GET /v1/alerts",
            ],
            "entities": [
                "Vehicle{id,org,status}",
                "Telemetry{ts,lat,lng,odometer,faults}",
                "Geofence",
                "WorkOrder/Maintenance",
            ],
            "algo": "ingest telem → rules/geofence → update live map → maintenance triggers",
        },
        "ev_charge": {
            "baseline": {
                "Primary QPS": "2K discovery",
                "Entities": "chargers",
                "Write QPS": "status 5K",
                "Payload": "station docs",
                "Hot structure": "availability index",
            },
            "scale_metric": "Discovery QPS",
            "scale_vals": ["2K", "20K", "200K", "2M"],
            "extra_metrics": [
                ("Stations", "100K", "1M", "10M", "50M"),
                ("Reservations/s", "50", "500", "5K", "50K"),
            ],
            "apis": [
                "GET /v1/chargers/nearby",
                "POST /v1/reservations",
                "POST /v1/sessions:start|stop",
                "OCPI/roaming partner APIs",
            ],
            "entities": [
                "Station{id,geo,connectors[]}",
                "ConnectorStatus",
                "Reservation{hold,expires}",
                "Session{kWh,billing}",
            ],
            "algo": "geo discover → show availability → reserve connector → session → bill",
        },
        "delivery_price": {
            "baseline": {
                "Primary QPS": "5K quotes",
                "Entities": "hex fees",
                "Write QPS": "marketplace stats",
                "Payload": "quote",
                "Hot structure": "pricing engines",
            },
            "scale_metric": "Quote QPS",
            "scale_vals": ["5K", "50K", "500K", "5M"],
            "extra_metrics": [
                ("Fee components", "base+dist+time+surge+fees", "same", "same", "same"),
                ("Quote bind TTL", "30–120s", "30–120s", "tuned", "tuned"),
            ],
            "apis": [
                "POST /v1/delivery/quotes",
                "GET /v1/pricing/heatmap",
            ],
            "entities": [
                "Quote{fee_breakdown,expires,version}",
                "HexPricingState",
                "Incentive",
            ],
            "algo": "features→fee model→incentives→bind quote→order uses quote_id",
        },
        "offline_res": {
            "baseline": {
                "Primary QPS": "1K sync",
                "Entities": "mobile clients",
                "Write QPS": "reservation intents",
                "Payload": "sync batches",
                "Hot structure": "client queue + server CAS",
            },
            "scale_metric": "Sync sessions/s",
            "scale_vals": ["1K", "10K", "100K", "1M"],
            "extra_metrics": [
                ("Conflict rate", "2–5%", "2–5%", "varies", "UX critical"),
                ("Offline window", "minutes–hours", "policy", "policy", "policy"),
            ],
            "apis": [
                "POST /v1/sync/push (client ops)",
                "POST /v1/sync/pull",
                "POST /v1/reservations (server authority)",
            ],
            "entities": [
                "ClientOp{idem_key,type,payload,ts}",
                "ReservationServerState",
                "Conflict{reason,server_truth}",
            ],
            "algo": "local enqueue → sync push idempotent → server CAS → pull truth → resolve UX",
        },
    }
    return profiles[d]


DOMAIN_FR: dict[str, list[tuple[str, str, str, str]]] = {
    "geo_poi": [
        ("F1", "Query types?", "Radius, bbox viewport, top-K", "Unified geo API + refine"),
        ("F2", "Filters?", "Open-now, category, price, rating", "Predicate pushdown"),
        ("F3", "Ranking?", "Distance + quality; personalization later", "Two-stage recall→rank"),
        ("F4", "Index?", "H3/S2/geohash postings", "Approx cells + haversine"),
        ("F5", "Freshness?", "Hours/closures minutes–hours", "CDC patch + closure channel"),
        ("F6", "Pagination?", "Cursors not OFFSET", "search_after keys"),
        ("F7", "Map markers?", "Cluster at low zoom", "Server aggregates"),
        ("F8", "Spam POIs?", "Trust score", "Downrank/merge pipeline"),
        ("F9", "Multi-city?", "Shard by metro/H3 parent", "Directory routing"),
        ("F10", "Cache?", "Hot downtown tiles", "CDN/Redis SWR"),
        ("F11", "Photos/reviews?", "Aggregates in MVP", "Denormalized rating fields"),
        ("F12", "Typeahead?", "Separate service OK", "Don't block nearby path"),
        ("F13", "Zero results?", "Expand radius / drop filters", "UX + catalog gap metrics"),
    ],
    "maps_platform": [
        ("F1", "Surfaces?", "Tiles, geocode, directions, traffic, places", "Multi-API platform"),
        ("F2", "Tile format?", "Vector tiles MVP; raster legacy OK", "CDN + etag"),
        ("F3", "Routing modes?", "Drive/walk; transit Phase 2", "Graph per mode"),
        ("F4", "Traffic?", "Probe + partner fusion", "Edge weight overlay"),
        ("F5", "Geocoding?", "Forward+reverse; autocomplete separate", "Retrieval + ranker"),
        ("F6", "Offline?", "Region packs Phase 2", "Don't block online design"),
        ("F7", "SDKs?", "Mobile map SDK clients", "Session + quota keys"),
        ("F8", "Freshness traffic?", "Minutes citywide; seconds highways", "Tile vs routing planes"),
        ("F9", "Multi-region?", "Tile edge global; graph regional", "Shard road graphs"),
        ("F10", "Quota/billing?", "Per API key", "Gateway meters"),
        ("F11", "Privacy probes?", "Aggregated traffic only", "No raw identifiable traces in tiles"),
        ("F12", "Alternatives?", "1–3 routes", "Budgeted compute"),
        ("F13", "Map vs search POI?", "Places API separate index", "Shared geo libs"),
    ],
    "routing": [
        ("F1", "OD pairs?", "Single + matrix limited", "Cap matrix size"),
        ("F2", "Algo?", "CH/HL or A* with landmarks", "Preprocess per region"),
        ("F3", "Traffic?", "Live weights overlay", "Versioned weight snapshots"),
        ("F4", "Constraints?", "Avoid tolls/ferries; time windows later", "Flag filters on edges"),
        ("F5", "Alternatives?", "Plateau/penalty methods", "Bound compute"),
        ("F6", "ETA output?", "Duration + distance + polyline", "Bind to traffic version"),
        ("F7", "Recompute live?", "Refresh on trip", "Cheap incremental"),
        ("F8", "Graph updates?", "Nightly topology; frequent speeds", "Dual pipelines"),
        ("F9", "Multi-stop?", "Ordered waypoints MVP", "Insertion heuristic"),
        ("F10", "Latency?", "p99 < 200ms regional", "Warm graphs in memory"),
        ("F11", "Failover?", "Degrade to free-flow speeds", "Flag degraded ETA"),
        ("F12", "Bike/walk?", "Separate graphs or flags", "Mode param"),
        ("F13", "Custom vehicles?", "Truck heights Phase 2", "Attribute dimensions"),
    ],
    "live_social_geo": [
        ("F1", "Who sees whom?", "Friends + explicit share", "Policy engine first"),
        ("F2", "Precision?", "Exact vs coarse city", "Audience-based precision"),
        ("F3", "TTL share?", "Session or timed share", "Expires server-side"),
        ("F4", "Update rate?", "Adaptive battery-aware", "Client duty cycle"),
        ("F5", "Nearby friends?", "Radius among friends only", "Friend-scoped geo index"),
        ("F6", "Push?", "WS deltas when app open", "Silent push sparingly"),
        ("F7", "History?", "No continuous track MVP", "Live only + short buffer"),
        ("F8", "Block/hide?", "Instant revoke", "Tombstone visibility"),
        ("F9", "Groups?", "Phase 2", "Hooks on audience"),
        ("F10", "Cross-region friends?", "Route to user home + fanout", "Avoid global scan"),
        ("F11", "Spoof GPS?", "Basic sanity; fraud later", "Drop impossible jumps"),
        ("F12", "Consent UX?", "Hard requirement", "Audit policy changes"),
        ("F13", "Kids/accounts?", "Out of MVP", "Age policies later"),
    ],
    "rideshare": [
        ("F1", "Products?", "UberX-like MVP", "Product codes on trip"),
        ("F2", "Quote?", "ETA + upfront price + surge", "Quote TTL binding"),
        ("F3", "Match?", "Nearby exclusive dispatch", "Leases; no double assign"),
        ("F4", "Trip SM?", "Request→match→pickup→drop→pay", "Hard state machine"),
        ("F5", "Tracking?", "Mutual live location", "Realtime gateway"),
        ("F6", "Payments?", "Auth/hold then capture", "Idempotent intents"),
        ("F7", "Cancel/reassign?", "Policy + fees", "Free driver lease"),
        ("F8", "Surge?", "Hex multipliers", "Version on quote"),
        ("F9", "Ratings?", "Two-sided after trip", "Async"),
        ("F10", "Safety?", "Share trip / SOS hooks", "Safety services"),
        ("F11", "City cells?", "Yes isolate blast radius", "Directory geo→cell"),
        ("F12", "Pool?", "Out of MVP", "Defer multi-rider match"),
        ("F13", "Airports?", "Phase 2 queues", "Special geofences"),
    ],
    "live_location": [
        ("F1", "Who publishes?", "Drivers/couriers on duty", "Auth + status gate"),
        ("F2", "Ping schema?", "lat,lng,heading,speed,ts,seq", "Monotonic seq"),
        ("F3", "Query?", "Nearby + trip track subscribe", "Geo index + pubsub"),
        ("F4", "Freshness?", "Drop stale > N seconds", "TTL in index"),
        ("F5", "Snap-to-road?", "Best effort Phase 1", "Async enrich"),
        ("F6", "Storage?", "Hot index + log; not OLTP per ping", "Tier cold history"),
        ("F7", "Compression?", "Delta / binary", "Adaptive hz"),
        ("F8", "Fanout?", "Trip subscribers only MVP", "Cap stadium storms"),
        ("F9", "Privacy?", "Rider sees driver only on trip", "ACL"),
        ("F10", "Clock skew?", "Server receive time + client ts bounds", "Drop impossible"),
        ("F11", "Multi-region?", "Cell-local index", "Handoff on border"),
        ("F12", "Battery?", "Lower hz when idle/not assigned", "Client policy"),
        ("F13", "Map matching failures?", "Serve raw with accuracy", "Don't block ingest"),
    ],
    "matching": [
        ("F1", "Input?", "Open trips + eligible drivers", "Demand/supply pools"),
        ("F2", "Exclusivity?", "One driver one trip", "Lease + fencing token"),
        ("F3", "Protocol?", "Offer/accept with timeout", "Requeue on reject"),
        ("F4", "Candidates?", "Geo nearby + filters", "Freshness cutoff"),
        ("F5", "Scoring?", "ETA, rating, acceptance, fairness", "Weighted score"),
        ("F6", "Batch?", "Micro-batch optional", "1–2s dense cells"),
        ("F7", "Cancel?", "Rider/driver cancel paths", "Compensating transitions"),
        ("F8", "Starvation?", "Fairness for long-wait riders", "Priority boost"),
        ("F9", "Idempotency?", "Dispatch request keys", "Exactly-once assign"),
        ("F10", "Observability?", "Time-to-match, reject rates", "Cell dashboards"),
        ("F11", "Cross-cell?", "Handoff protocol", "Don't dual-own driver"),
        ("F12", "Autonomous?", "Out of MVP", "Same lease model later"),
        ("F13", "Offer or auto-assign?", "Offer/accept MVP common", "Timeouts + reassign"),
    ],
    "geo_dispatch": [
        ("F1", "Ownership?", "Each cell single writer epoch", "Fencing tokens"),
        ("F2", "Directory?", "lat/lng → cell_id", "Cached map + versions"),
        ("F3", "Borders?", "Handoff trips/drivers", "Explicit protocol"),
        ("F4", "Failover?", "Elect new owner", "Epoch bump rejects stale"),
        ("F5", "Cell size?", "City or metro; microcells later", "Ops tradeoff"),
        ("F6", "Config changes?", "Split/merge cells", "Dual-run period"),
        ("F7", "Global features?", "Identity/pay outside cell", "Clear boundaries"),
        ("F8", "Hot stadium?", "Temporary subcells", "Admission control"),
        ("F9", "Consistency?", "Trip sticky to cell", "No active-active driver"),
        ("F10", "Observability?", "Ownership, failover time", "Game-days"),
        ("F11", "Multi-product?", "Shared cells or overlays", "Namespace leases"),
        ("F12", "Reads?", "Secondary indexes eventual", "OK for heatmaps"),
        ("F13", "Cross-region trips?", "Rare; plan handoff", "Long-distance product rules"),
    ],
    "eta": [
        ("F1", "Targets?", "Pickup ETA, trip ETA, food ETA", "Typed prediction APIs"),
        ("F2", "Features?", "OD, traffic, time, weather, supply", "Online feature store"),
        ("F3", "Models?", "Segment baselines + ML", "Fallback chain"),
        ("F4", "Latency?", "p99 < 50–100ms", "Cache + light models"),
        ("F5", "Uncertainty?", "mu/sigma optional", "Calibration"),
        ("F6", "Feedback?", "Actuals from completions", "Offline training loop"),
        ("F7", "Cold start?", "Heuristic distances", "City priors"),
        ("F8", "Experiments?", "Layer models", "Guardrail metrics"),
        ("F9", "Degrade?", "Free-flow / haversine", "Flag quality"),
        ("F10", "Batch?", "Matrix ETAs capped", "Chunk workers"),
        ("F11", "Versioning?", "model_version on response", "Replayability"),
        ("F12", "Multi-leg food?", "Merchant prep + drive", "Sum calibrated parts"),
        ("F13", "Gaming?", "Don't expose exploitable internals", "Coarsen heatmaps"),
    ],
    "surge": [
        ("F1", "Unit?", "H3 hex × product", "Hex state machine"),
        ("F2", "Inputs?", "Demand intents + on-duty supply", "Streaming aggregates"),
        ("F3", "Output?", "Multiplier + surge_version", "Bind into quotes"),
        ("F4", "Stability?", "Hysteresis + max step", "Avoid oscillation"),
        ("F5", "Caps?", "Local max mult + regs", "Policy engine"),
        ("F6", "Driver incentives?", "Separate from rider mult", "Two instruments"),
        ("F7", "Display?", "Heatmap delayed/noisy", "Anti-gaming"),
        ("F8", "Failover?", "Last-known mult or 1.0", "Explicit degrade"),
        ("F9", "Fairness?", "No personal surge", "Geo×product only MVP"),
        ("F10", "Audit?", "Why was quote X?", "Version logs"),
        ("F11", "Recompute period?", "5–15s", "Stream at 1000×"),
        ("F12", "Events?", "Stadium overrides", "Manual + auto"),
        ("F13", "Quote binding?", "Price locked for TTL", "surge_version on quote"),
    ],
    "food_delivery": [
        ("F1", "Sides?", "Customer, merchant, dasher", "Three-sided SM"),
        ("F2", "Order flow?", "Cart→pay→merchant→assign→deliver", "Orchestration service"),
        ("F3", "Prep time?", "Merchant signals + models", "Assign timing"),
        ("F4", "Assign?", "Nearby dashers; batch later", "Exclusive leases"),
        ("F5", "ETA promise?", "Quoted then revised", "Track UX honesty"),
        ("F6", "Menu/catalog?", "Dependency; availability flags", "Don't overbuild POS"),
        ("F7", "Payments/refunds?", "Capture policies", "Idempotent money"),
        ("F8", "Chat/support?", "Phase 2", "Event hooks"),
        ("F9", "Multi-merchant cart?", "Out of MVP", "Single merchant first"),
        ("F10", "City cells?", "Yes", "Marketplace isolation"),
        ("F11", "Ratings?", "After delivery", "Async"),
        ("F12", "Peak lunch?", "Incentives + batching", "Surge-like fees"),
        ("F13", "Merchant prep coupling?", "Critical for ETA", "Prep signals into assigner"),
    ],
    "resto_rank": [
        ("F1", "Surface?", "Home feed + category + map", "Multiple query shapes"),
        ("F2", "Recall?", "Geo + open + cuisine", "Candidate generation"),
        ("F3", "Rank?", "LTR with context (mealtime)", "Two-stage"),
        ("F4", "Availability?", "Paused/busy/open", "Realtime features"),
        ("F5", "Diversity?", "Cuisine/brand spacing", "MMR-like"),
        ("F6", "Personalization?", "Phase 1 light", "Timeout fallback"),
        ("F7", "Photos?", "CDN; ranking uses quality", "Not on critical DB"),
        ("F8", "Experiments?", "Layer rankers", "Guardrails"),
        ("F9", "Sponsored?", "Phase 2 labeled", "Auction hooks"),
        ("F10", "Latency?", "p99 < 200ms", "Cache first page"),
        ("F11", "Cold start restos?", "Exploration quota", "Fairness"),
        ("F12", "Closed mid-scroll?", "Filter + soft flags", "Refresh tokens"),
        ("F13", "Geo bias?", "Distance decay tunable", "City-specific weights"),
    ],
    "order_tracking": [
        ("F1", "States?", "Placed→accepted→prep→pickup→enroute→delivered", "Typed SM"),
        ("F2", "Events?", "Merchant, dasher GPS, system", "Append-only log"),
        ("F3", "Client UX?", "Timeline + live map", "WS/SSE"),
        ("F4", "ETA refresh?", "On major transitions + timer", "ETA service calls"),
        ("F5", "Ordering?", "seq per order", "Drop/repair gaps"),
        ("F6", "Push?", "Milestone notifications", "Dedup keys"),
        ("F7", "Permissions?", "Customer + active dasher + merchant", "ACL"),
        ("F8", "History?", "Complete orders cold store", "Tiering"),
        ("F9", "Partial outage?", "Show last known + banner", "Degrade"),
        ("F10", "Multi-package?", "Single order MVP", "Legs later"),
        ("F11", "Support tools?", "Admin timeline", "Audit"),
        ("F12", "Idempotent events?", "Yes", "event_id unique"),
        ("F13", "Map privacy?", "Only during active delivery", "Stop after complete"),
    ],
    "batch_assign": [
        ("F1", "Window?", "30–90s micro-batch", "Cell-local pools"),
        ("F2", "Constraints?", "Capacity, time windows, food temp", "Hard vs soft"),
        ("F3", "Objective?", "On-time first, then distance", "Lexicographic"),
        ("F4", "Atomic assign?", "Exclusive order+courier", "Leases"),
        ("F5", "Reoptimize?", "On cancel/late prep", "Bounded churn"),
        ("F6", "Single orders?", "Always allow size-1", "Fallback"),
        ("F7", "Fairness?", "Don't strand far orders", "Age boost"),
        ("F8", "Compute budget?", "Hard wall clock", "Best feasible"),
        ("F9", "Explainability?", "Why batched", "Debug fields"),
        ("F10", "Peak mode?", "Shorter windows / more singles", "Policy flag"),
        ("F11", "Cross-restaurant batch?", "Limited MVP", "Geo+time gates"),
        ("F12", "Idempotency?", "Assign job ids", "Exactly-once"),
        ("F13", "Hard SLA vs efficiency?", "SLA first", "No late dropoffs"),
    ],
    "vrp": [
        ("F1", "Problem class?", "VRP with time windows", "Heuristic solvers"),
        ("F2", "Inputs?", "Stops, vehicles, constraints", "Validated jobs"),
        ("F3", "Output?", "Sequences + ETAs", "Executable plans"),
        ("F4", "Live replan?", "Traffic, new stops, failures", "Event triggers"),
        ("F5", "Time budget?", "0.2–2s", "Anytime algorithms"),
        ("F6", "Capacity?", "Weight/volume/slots", "Feasibility checks"),
        ("F7", "Road ETAs?", "Routing service dependency", "Cache matrix chunks"),
        ("F8", "Infeasibility?", "Drop/escalate stop", "Never silent"),
        ("F9", "Multi-depot?", "Phase 2", "Hooks"),
        ("F10", "Human override?", "Dispatcher edits", "Version plans"),
        ("F11", "Scale?", "Per cell / courier set", "Partition"),
        ("F12", "Cold start?", "Nearest insertion", "Warm improve"),
        ("F13", "Exact MIP?", "Only tiny instances", "Not online path"),
    ],
    "earnings": [
        ("F1", "What posts?", "Trip/delivery earnings, tips, bonuses, adjustments", "Typed journal entries"),
        ("F2", "Ledger?", "Double-entry", "Accounts per driver"),
        ("F3", "Idempotency?", "Natural keys from trip_id+component", "Unique constraints"),
        ("F4", "Balance?", "Materialized from journal", "Rebuildable"),
        ("F5", "Payouts?", "Daily/weekly rails", "Batch + retries"),
        ("F6", "Failures?", "Rail timeout reconcile", "No double payout"),
        ("F7", "Disputes?", "Adjustments with reason codes", "Audit trail"),
        ("F8", "Tax forms?", "Phase 2 exports", "Annual data"),
        ("F9", "Multi-currency?", "Per market", "Wallet currency"),
        ("F10", "Tips?", "Separate component; clawback policy", "Clear rules"),
        ("F11", "Realtime display?", "Eventual seconds OK", "Cache balance"),
        ("F12", "Fraud?", "Velocity + device", "Hold payouts"),
        ("F13", "Exactly-once money?", "Ledger + payout idempotency", "Reconcile jobs"),
    ],
    "reviews": [
        ("F1", "Write path?", "Stars + text after verified activity", "Eligibility checks"),
        ("F2", "Aggregates?", "avg/count/histogram", "Async materialize"),
        ("F3", "Votes?", "Helpful/not", "One vote/user"),
        ("F4", "Moderation?", "ML + human queue", "States: pending/live/removed"),
        ("F5", "Fraud?", "Brigades, fake stays", "Graph/velocity features"),
        ("F6", "Rewards?", "Points for quality reviews", "Reward ledger"),
        ("F7", "Ranking reviews?", "Quality + recency + helpful", "Feed ranker"),
        ("F8", "Edits/deletes?", "Allowed with audit", "Reaggregate"),
        ("F9", "Photos?", "Object store + scan", "Async"),
        ("F10", "Multi-entity?", "Restaurant, driver, listing", "entity_type key"),
        ("F11", "Rate limits?", "Per user/entity", "Anti-spam"),
        ("F12", "Public cache?", "Aggregates yes; personalized no", "CDN careful"),
        ("F13", "Incentives abuse?", "Cap rewards; quality gates", "Clawbacks"),
    ],
    "rental_mkt": [
        ("F1", "Roles?", "Host + guest", "Two-sided marketplace"),
        ("F2", "Listings?", "Photos, amenities, geo", "Catalog + search"),
        ("F3", "Availability?", "Nightly calendar", "Contention core"),
        ("F4", "Search?", "Geo+dates+filters+rank", "Availability join"),
        ("F5", "Booking?", "Request/instant book", "Hold→pay→confirm"),
        ("F6", "Messaging?", "Host-guest thread", "Async"),
        ("F7", "Payments/payouts?", "Capture + host payout", "Ledger"),
        ("F8", "Trust?", "Reviews, ID verification hooks", "Safety"),
        ("F9", "Cancellations?", "Policy engine", "Refunds"),
        ("F10", "Pricing?", "Host-set MVP; smart later", "Quote nights"),
        ("F11", "Multi-currency?", "Market based", "FX later"),
        ("F12", "Experiences?", "Out of MVP", "Stay-focused"),
        ("F13", "Double book?", "Never", "Calendar CAS"),
    ],
    "listing_search": [
        ("F1", "CRUD?", "Hosts publish/update listings", "SoT DB + CDC"),
        ("F2", "Index?", "Text+geo+facets", "Search cluster"),
        ("F3", "Freshness?", "Seconds–minutes", "Near-real-time index"),
        ("F4", "Ranking?", "Relevance + quality + geo", "LTR hooks"),
        ("F5", "Photos?", "CDN variants", "Async processing"),
        ("F6", "Facets?", "Price, amenities, rooms", "Agg carefully"),
        ("F7", "Availability filter?", "Join or denorm bitmaps", "Date-aware search"),
        ("F8", "Spam?", "Quality score", "Moderation"),
        ("F9", "Pagination?", "Cursors", "Stable sort"),
        ("F10", "Multi-language?", "Phase 2", "Analyzers"),
        ("F11", "Personalization?", "Optional re-rank", "Timeout fallback"),
        ("F12", "Delete/unlist?", "Tombstones", "Immediate search remove"),
        ("F13", "Hot viral listing?", "Cache + rate limit detail", "Protect origin"),
    ],
    "rental_book": [
        ("F1", "Unit?", "Listing × night cells", "Calendar model"),
        ("F2", "Hold?", "TTL reservation pre-pay", "Expires releaser"),
        ("F3", "Confirm?", "Payment success → booked", "CAS convert"),
        ("F4", "Idempotency?", "Client keys on hold/book", "Safe retries"),
        ("F5", "Instant vs request?", "MVP instant only OK", "Host accept later"),
        ("F6", "Partial dates fail?", "All-or-nothing nights", "Atomic multi-night"),
        ("F7", "Price change?", "Requote if stale", "No silent reprice"),
        ("F8", "Timezone?", "Listing local nights", "Careful boundaries"),
        ("F9", "Overbook prevention?", "Conditional updates only", "Invariant tests"),
        ("F10", "Admin override?", "Audited", "Force book rare"),
        ("F11", "Concurrency UX?", "409 + refresh", "Show taken nights"),
        ("F12", "Payments?", "Auth during hold window", "Cancel releases"),
        ("F13", "Overbooking?", "Never for MVP inventory", "Calendar conditional updates"),
    ],
    "split_stay": [
        ("F1", "Goal?", "Cover stay with 2+ listings", "Segment combinatorics"),
        ("F2", "Max segments?", "2 MVP", "Hard cap compute"),
        ("F3", "Constraints?", "Geo radius, price, amenities", "Prefilter each segment"),
        ("F4", "Availability?", "Per segment dates", "Bitmap joins"),
        ("F5", "Latency budget?", "1–2s", "Beam/prune"),
        ("F6", "Ranking?", "Total price, distance, quality, transition cost", "Score itineraries"),
        ("F7", "Transition?", "Same city; travel time penalty", "Geo distance between listings"),
        ("F8", "Booking?", "Hold all segments or none", "Distributed saga careful"),
        ("F9", "Partial fail?", "Release all holds", "Compensate"),
        ("F10", "Cache?", "Popular date/geo splits", "Bounded"),
        ("F11", "UI?", "Show itinerary cards", "Explain segments"),
        ("F12", "3+ segments?", "Phase 2 only", "Explodes search"),
        ("F13", "Exact cover?", "Dates contiguous no gaps", "Validate coverage"),
    ],
    "alerts": [
        ("F1", "Watch types?", "Listing id and saved search", "Two index types"),
        ("F2", "Triggers?", "Availability open, price drop", "CDC matchers"),
        ("F3", "Dedup?", "One alert per change key", "dedup_key"),
        ("F4", "Channels?", "Push/email", "Notification service"),
        ("F5", "Quiet hours?", "User prefs", "Defer send"),
        ("F6", "Latency?", "Tens of seconds OK", "Not trading HFT"),
        ("F7", "Volume storms?", "Viral listing opens", "Per-user rate limits"),
        ("F8", "Privacy?", "Don't leak existence improperly", "Authz"),
        ("F9", "Unsubscribe?", "Instant", "Tombstone watches"),
        ("F10", "Exact vs fuzzy match?", "Filters on saved search", "Re-eval query carefully"),
        ("F11", "Scale watches?", "Invert listing→watches", "Shard by listing"),
        ("F12", "Backfill?", "No historical spam on create", "Forward only"),
        ("F13", "False opens?", "Confirm availability before send", "Re-read SoT"),
    ],
    "hotel": [
        ("F1", "Search?", "Geo/dates/guests/stars", "Hotel docs + rates"),
        ("F2", "Inventory?", "Room-type allotments", "ARIQ updates"),
        ("F3", "Providers?", "Direct + GDS/OTA adapters", "Facade"),
        ("F4", "Quote?", "Rate shop with TTL", "Bind quote_id"),
        ("F5", "Reservation?", "Hold then confirm with provider", "Compensation on fail"),
        ("F6", "Overbook policy?", "Hotel-controlled; platform rules", "Explicit"),
        ("F7", "Content?", "Photos, amenities", "CDN"),
        ("F8", "Loyalty?", "Phase 2", "Hooks"),
        ("F9", "Cancellations?", "Policy rates", "Refund flows"),
        ("F10", "Cache?", "Aggressive search cache; careful rates", "Short rate TTL"),
        ("F11", "Idempotency?", "Reservation keys", "Provider ids"),
        ("F12", "Multi-room?", "MVP single room type", "Extend later"),
        ("F13", "Provider truth?", "Suppliers may be source", "Hold/confirm with provider refs"),
    ],
    "tickets": [
        ("F1", "Onsale?", "Scheduled open with herd", "Waiting room"),
        ("F2", "Inventory?", "Seat-level or GA pools", "Partition by event"),
        ("F3", "Holds?", "Short TTL seat holds", "Expirer + extend once"),
        ("F4", "Checkout?", "Pay then finalize tickets", "Idempotent order"),
        ("F5", "Bots?", "Device + puzzle + velocity", "Risk engine"),
        ("F6", "Fairness?", "FIFO-ish admit tokens", "No preferential DB access"),
        ("F7", "Seatmap UX?", "Section→seats realtime", "Diff updates"),
        ("F8", "Transfers/resale?", "Phase 2", "Ticket state hooks"),
        ("F9", "GA vs assigned?", "Both; different allocators", "Shared checkout"),
        ("F10", "Refunds?", "Policy + inventory return", "Compensating txn"),
        ("F11", "Flash sales?", "Same waiting room", "Rate admit"),
        ("F12", "Multi-event cart?", "Out of MVP", "Single event"),
        ("F13", "Onsale fairness?", "Waiting room + admit rate", "Do not open thundering herd to seat DB"),
    ],
    "seats": [
        ("F1", "Seat map?", "Sections/rows/seats statuses", "Immutable geometry + mutable state"),
        ("F2", "Selection?", "Multi-seat contiguous prefer", "Suggestor"),
        ("F3", "Atomic hold?", "All seats or none", "Single txn/Lua"),
        ("F4", "TTL?", "2–10 minutes", "Extend limited"),
        ("F5", "Concurrency?", "CAS per seat set", "Loser refreshes"),
        ("F6", "Releases?", "Expire, cancel, failed pay", "Return AVAILABLE"),
        ("F7", "Wheelchair/holds?", "Attribute constraints", "Rules engine"),
        ("F8", "Pricing by seat?", "Price levels/sections", "Quote from hold"),
        ("F9", "Realtime map?", "WS status diffs", "Versioned snapshots"),
        ("F10", "GA areas?", "Counter pools not seat ids", "Different allocator"),
        ("F11", "Admin block?", "Kill seats", "Audit"),
        ("F12", "Idempotent hold?", "Client key", "Safe retry"),
        ("F13", "Atomic multi-seat?", "Yes—parties sit together", "Single CAS / txn over seat set"),
    ],
    "auction": [
        ("F1", "Auction types?", "English ascending MVP", "Proxy optional"),
        ("F2", "Bid ack?", "Visible high water", "CAS version"),
        ("F3", "Ordering?", "Amount, then time, then id", "Total order"),
        ("F4", "Soft close?", "Extend on late bids", "Anti-snipe"),
        ("F5", "Reserve?", "Hidden/shown policy", "Settle rules"),
        ("F6", "Notifications?", "Outbid / winning / ended", "Pubsub"),
        ("F7", "Idempotency?", "Bid keys", "Safe mobile retry"),
        ("F8", "Payments?", "Auth high bidders / pay on win", "Risk"),
        ("F9", "Fraud?", "Shill detection", "Graph features"),
        ("F10", "Hot finale?", "Single-writer auction shard", "Memory hot row"),
        ("F11", "Cancel auction?", "Admin rare", "Refunds"),
        ("F12", "Proxy bidding?", "Server places increments", "Still CAS high"),
        ("F13", "Soft close?", "Yes against sniping", "Extend end_at on late bids"),
    ],
    "parcel_track": [
        ("F1", "Scans?", "Carrier + hub events", "Adapter normalize"),
        ("F2", "Milestones?", "Created→in_transit→out_for_delivery→delivered", "SM"),
        ("F3", "Ordering?", "ts + seq + source priority", "Reorder buffer"),
        ("F4", "ETA?", "Milestone + ML", "Refresh on scans"),
        ("F5", "Notify?", "Milestone push", "Dedup"),
        ("F6", "Multi-leg?", "Transfer hubs", "Leg graph"),
        ("F7", "Idempotent ingest?", "scan_id unique", "At-least-once OK"),
        ("F8", "Public page?", "Tracking number + soft auth", "Anti-scrape"),
        ("F9", "Exceptions?", "Delay, return, lost", "Exception states"),
        ("F10", "History retention?", "Hot months; cold archive", "Tier"),
        ("F11", "Map?", "Last scan location", "Coarse OK"),
        ("F12", "Batch ingest?", "Carrier files + webhooks", "Both"),
        ("F13", "Out-of-order delivered?", "Repair SM carefully", "Don't regress delivered without authority"),
    ],
    "shipping_label": [
        ("F1", "Rate shop?", "Multi-carrier quotes", "Adapter fanout + timeout"),
        ("F2", "Purchase?", "Idempotent shipment create", "Provider idem keys"),
        ("F3", "Label formats?", "PDF/ZPL", "Object store"),
        ("F4", "Manifests?", "End-of-day", "Async jobs"),
        ("F5", "Webhooks?", "Track updates", "Verify signatures"),
        ("F6", "Retries?", "Unknown purchase outcome reconcile", "Never blind repurchase"),
        ("F7", "Address validation?", "Pre-check", "Soft fails"),
        ("F8", "Multi-parcel?", "Supported", "Shipment composition"),
        ("F9", "Refunds/voids?", "Carrier void APIs", "State machine"),
        ("F10", "Quotas?", "Per merchant", "Gateway"),
        ("F11", "Sandbox?", "Carrier test creds", "Env split"),
        ("F12", "Cost?", "Cache rates short TTL", "Prefer cheaper path"),
        ("F13", "Partial carrier outage?", "Circuit break; still quote others", "Degrade set"),
    ],
    "warehouse": [
        ("F1", "Inbound?", "ASN receive → stow", "Inbound SM"),
        ("F2", "Inventory truth?", "Bin×SKU qty + events", "Ledger-like"),
        ("F3", "Reserve?", "Soft allocate for orders", "No negative"),
        ("F4", "Waves?", "Batch picks by cutoff/aisle", "Planner"),
        ("F5", "Tasks?", "Pick/pack with scan confirm", "Idempotent complete"),
        ("F6", "Exceptions?", "Short, damage, PS queues", "Adjust workflows"),
        ("F7", "Multi-FC?", "Per-FC cell + network hooks", "Promise elsewhere"),
        ("F8", "Idempotency?", "task_id + scan events", "Safe double scan"),
        ("F9", "Robots?", "Device abstraction Phase 2", "Same tasks"),
        ("F10", "Cycle count?", "Triggered + scheduled", "Adjust authority"),
        ("F11", "Peak?", "Prime Day elasticity", "Capacity plans"),
        ("F12", "Safety?", "Interlocks > thruput", "Hard stops"),
        ("F13", "Scan truth?", "Scan confirms inventory moves", "Idempotent task completion"),
    ],
    "fleet": [
        ("F1", "Assets?", "Vehicles + org ownership", "Registry"),
        ("F2", "Telemetry?", "GPS, odometer, faults", "High-ingest pipeline"),
        ("F3", "Live map?", "Fleet positions", "Geo index"),
        ("F4", "Geofences?", "Enter/exit alerts", "Rules engine"),
        ("F5", "Assignments?", "Vehicle↔driver/job", "State"),
        ("F6", "Maintenance?", "Schedules from meters/time", "Work orders"),
        ("F7", "Compliance?", "ELD/hours hooks Phase 2", "Audit logs"),
        ("F8", "Multi-tenant?", "Org isolation", "Quotas"),
        ("F9", "Alerts?", "Fault, geofence, offline", "Dedup + page"),
        ("F10", "History?", "Trip trails cold", "Tier storage"),
        ("F11", "Commands?", "Lock/unlock Phase 2", "Authz strong"),
        ("F12", "Scale telem?", "Partition by vehicle/org", "Backpressure"),
        ("F13", "Offline vehicle?", "Last-known + stale flag", "Don't invent motion"),
    ],
    "ev_charge": [
        ("F1", "Discover?", "Nearby chargers + plugs", "Geo + filters"),
        ("F2", "Availability?", "Connector status stream", "Freshness SLO"),
        ("F3", "Reserve?", "Hold connector TTL", "CAS"),
        ("F4", "Session?", "Start/stop kWh metering", "Billing"),
        ("F5", "Roaming?", "OCPI partners Phase 2", "Adapters"),
        ("F6", "Payments?", "Auth before session", "Idempotent"),
        ("F7", "Faults/ICE?", "Mark unavailable; cancel holds", "Notify"),
        ("F8", "Pricing?", "Per station tariffs", "Quote"),
        ("F9", "Maps?", "Filter by plug/power", "Amenities"),
        ("F10", "Idempotent reserve?", "Client keys", "Safe retry"),
        ("F11", "Multi-network?", "Aggregate status", "Stale labels"),
        ("F12", "Queueing?", "Physical queue Phase 2", "Reservation first"),
        ("F13", "Roaming auth fail?", "Fail clear; no bill", "Session gate"),
    ],
    "delivery_price": [
        ("F1", "Components?", "Base + distance + time + fees + surge", "Transparent breakdown"),
        ("F2", "Inputs?", "Hex demand/supply, distance, weather", "Feature fetch"),
        ("F3", "Quote bind?", "TTL + version", "Order references quote_id"),
        ("F4", "Incentives?", "Dasher boosts separate", "Coupled marketplace control"),
        ("F5", "Experiments?", "Fee policies", "Guardrails"),
        ("F6", "Fairness?", "No personal hostile pricing MVP", "Geo policies"),
        ("F7", "Degrade?", "Last fee table", "Flag"),
        ("F8", "Fraud?", "Address spoof / promo", "Risk"),
        ("F9", "Multi-product?", "Restaurant vs grocery params", "Config"),
        ("F10", "Latency?", "p99 < 150ms", "Cache hex state"),
        ("F11", "Audit?", "Why this fee", "Version logs"),
        ("F12", "Caps/floors?", "Regulatory + UX", "Policy"),
        ("F13", "Oscillation?", "Hysteresis like surge", "Smooth updates"),
    ],
    "offline_res": [
        ("F1", "Client store?", "Encrypted local queue + cache", "SQLite/Room"),
        ("F2", "Ops?", "Create/modify/cancel reservation intents", "Idempotent op ids"),
        ("F3", "Sync?", "Push then pull truth", "Server authority"),
        ("F4", "Conflicts?", "Taken inventory / version mismatch", "Conflict UX + alternatives"),
        ("F5", "What offline-ok?", "Browse cached + queue intents", "Not final scarce guarantee"),
        ("F6", "TTL intents?", "Expire stale offline ops", "Don't surprise charge"),
        ("F7", "Auth?", "Cached tokens refresh", "Secure storage"),
        ("F8", "Partial sync?", "Per-op ack", "Resume"),
        ("F9", "Seat/ticket scarcity?", "Show provisional; confirm online", "Honest UX"),
        ("F10", "Multi-device?", "Server merges by idem keys", "Last-write carefully"),
        ("F11", "Observability?", "Conflict rates, sync lag", "Mobile metrics"),
        ("F12", "Security?", "No long-lived secrets in logs", "Encrypt at rest on device"),
        ("F13", "Server or client authority?", "Server wins on conflict", "Idempotent sync + conflict UI"),
    ],
}


def fr_rows(spec: dict) -> list[tuple[str, str, str, str]]:
    d = spec["domain"]
    if d in DOMAIN_FR:
        return DOMAIN_FR[d]
    noun = spec["noun"]
    return [
        ("F1", f"What is the core user journey for {noun}?", f"Primary flow to {spec['verbs']}", "End-to-end state machine + APIs first"),
        ("F2", "Read vs write intensity?", "Domain-specific (see estimation)", "Separate read/search planes from transactional plane"),
        ("F3", "Geo involved?", "Yes for this section—indexes and cells matter", "H3/S2/geohash or road graph as fits"),
        ("F4", "Consistency critical path?", "Money/inventory/dispatch exclusivity where applicable", "Strong on contention; eventual elsewhere"),
        ("F5", "Realtime needs?", "Live updates for location/ETA/status as applicable", "Pub/sub + TTL freshness"),
        ("F6", "Multi-region?", "Regional cells; global directory", "Single-writer cells for contended entities"),
        ("F7", "Idempotency?", "Client retries expected on mobile", "Idempotency-Key on creates/holds/bids/payments"),
        ("F8", "Fraud/bots?", "Assume adversarial spikes on hot events/inventory", "Queue, rate limits, device reputation"),
        ("F9", "Offline/partial?", "Mobile flaky networks", "Clear UX for holds/pending sync"),
        ("F10", "Analytics?", "Product + marketplace health metrics", "Async event bus; not on OLTP path"),
        ("F11", "SLA for core action?", "p99 targets in NFR table", "Budgets cascade to dependencies"),
        ("F12", "MVP cut line?", "See MVP bullets", "Defer global optimizers / heavy ML until hooks exist"),
        ("F13", "Primary emphasis?", "; ".join(spec["emphasis"][:3]), "Keep deep dive on these"),
    ]


def nfr_rows(spec: dict) -> list[tuple[str, str, str, str]]:
    d = spec["domain"]
    common = [
        ("N1", "Latency SLO?", "Interactive where user waits", domain_latency(d)),
        ("N2", "Availability?", "Regional degrade OK if blast-radius limited", "99.9% control plane; critical path higher if money"),
        ("N3", "Durability?", "No silent loss of money/inventory/dispatch commits", "WAL/kafka + idempotent apply"),
        ("N4", "Consistency?", "Strong on contended keys; eventual on search/heatmaps", "Document per entity"),
        ("N5", "Freshness?", "Live location/ETA/status SLOs", domain_freshness(d)),
        ("N6", "Multi-region?", "Cell/home-region writes", "Directory + failover runbooks"),
        ("N7", "Security/privacy?", "PII, precise location, payments", "TLS, encryption, least privilege, audit"),
        ("N8", "Cost?", "Read-heavy caching; avoid O(n) geo scans", "Caps, caches, tiered storage"),
        ("N9", "Peak elasticity?", "Events/onsale/rain/stadium", "10–100× cell peaks"),
    ]
    return common


def domain_latency(d: str) -> str:
    m = {
        "geo_poi": "p99 nearby < 100–150ms",
        "maps_platform": "tiles CDN; directions p99 < 200–300ms",
        "routing": "p99 route < 200ms regional",
        "live_social_geo": "update ack < 200ms; friend query < 150ms",
        "rideshare": "quote < 500ms; match p50 < 15s dense",
        "live_location": "ingest p99 < 50–100ms; query < 30ms",
        "matching": "decision < 100–200ms once candidates ready",
        "geo_dispatch": "directory lookup < 20ms",
        "eta": "predict p99 < 50–100ms",
        "surge": "quote path < 100ms including mult fetch",
        "food_delivery": "checkout < 500ms; assign minutes-scale",
        "resto_rank": "feed p99 < 200ms",
        "order_tracking": "event visible < 1–2s",
        "batch_assign": "plan within batch window budget",
        "vrp": "solve budget 0.2–2s",
        "earnings": "ledger write < 100ms; payouts async",
        "reviews": "read p99 < 150ms; write < 300ms",
        "rental_mkt": "search < 300ms; book < 500ms",
        "listing_search": "search p99 < 200ms",
        "rental_book": "hold < 200ms",
        "split_stay": "search < 1–2s with budgets",
        "alerts": "alert after change < 30–60s",
        "hotel": "search < 400ms (cache); book < 1s + provider",
        "tickets": "hold < 200ms after admit; queue UX separate",
        "seats": "hold < 150–200ms",
        "auction": "bid ack < 100–150ms",
        "parcel_track": "scan ingest < 100ms; read < 150ms",
        "shipping_label": "rate < 500ms; purchase < 2s + carrier",
        "warehouse": "scan confirm < 200–300ms",
        "fleet": "telem ingest < 50ms; alert < 5s",
        "ev_charge": "nearby < 150ms; reserve < 300ms",
        "delivery_price": "quote < 150ms",
        "offline_res": "local op < 16ms; sync when online",
    }
    return m.get(d, "p99 < 200ms interactive paths")


def domain_freshness(d: str) -> str:
    m = {
        "live_location": "p95 location age < 5–10s on trip",
        "live_social_geo": "friend loc age policy 10–60s",
        "surge": "hex mult age < 5–15s",
        "eta": "features seconds-stale OK if calibrated",
        "order_tracking": "state < 1–2s",
        "tickets": "seatmap deltas < 1s during onsale",
        "fleet": "map refresh 5–15s; critical alerts faster",
        "ev_charge": "connector status < 30–60s",
        "geo_poi": "hours minutes–hours; geo static",
        "parcel_track": "scan visible < few seconds after ingest",
    }
    return m.get(d, "define explicit staleness budget")


def edge_cases(spec: dict) -> list[tuple[str, str]]:
    d = spec["domain"]
    common = [
        ("Client retry / duplicate submit", "Idempotency-Key returns same resource; conflicting body → 409"),
        ("Dependency timeout", "Fail fast with degrade path; no unbounded queue for interactive UX"),
        ("Hot key / hot cell / hot event", "Shard, queue, coalesce, or waiting room—never one global lock"),
        ("Clock skew", "Server timestamps for TTL/CAS; client ts for telemetry only with sanity bounds"),
        ("Partial regional outage", "Cell isolation; directory failover; clear user messaging"),
        ("Poison message / bad GPS", "Validate, quarantine, don't brick partition"),
        ("Privacy / IDOR", "Authz on every read of precise location or PII"),
        ("Backfill / replay", "Idempotent consumers; replay from offsets for index rebuild"),
    ]
    specific = {
        "tickets": [
            ("Onsale thundering herd", "Waiting room + token admit; warm inventory shards"),
            ("Hold expiry at checkout", "Extend once; then release seats; never double-sell"),
            ("Bot farms", "Device attestation, puzzle, velocity limits, payment risk"),
        ],
        "seats": [
            ("Two users same seats", "Only one CAS wins; loser refreshes map"),
            ("Party of 4 split", "Atomic multi-seat or suggest contiguous algorithm"),
        ],
        "rideshare": [
            ("Driver accepts two offers", "Lease token; second accept rejected"),
            ("Rider cancel after match", "Policy fees; free driver; notify"),
            ("GPS spoof pickup", "Fraud signals; can require photo/geo checks"),
        ],
        "matching": [
            ("All drivers reject", "Expand radius / surge / ETA degrade; don't spin forever"),
            ("Stale candidate driver", "Freshness filter; validate on offer"),
        ],
        "rental_book": [
            ("Double book same night", "Conditional calendar update prevents"),
            ("Payment fails after hold", "Auto-release on TTL; webhook cancel"),
        ],
        "hotel": [
            ("Provider confirm fails", "Compensate hold; offer alternatives"),
            ("Rate changed at book", "Requote; don't silently reprice"),
        ],
        "auction": [
            ("Simultaneous high bids", "Total order by (amount, ts, bid_id) with CAS version"),
            ("Bid after end", "Reject; soft-close extends only if before end"),
        ],
        "live_location": [
            ("Out-of-order pings", "seq/ts monotonic per driver; drop older"),
            ("Subscriber storm stadium", "Sample fanout; delta compression; regional gateways"),
        ],
        "surge": [
            ("Oscillating multipliers", "Hysteresis + smoothing; max step change"),
            ("Drivers chase heatmap gaming", "Delay/noise; incentive separate from rider mult"),
        ],
        "offline_res": [
            ("Conflict: seat taken while offline", "Surface server truth; suggest alternatives"),
            ("Huge offline queue", "Cap ops; expire stale intents"),
        ],
        "warehouse": [
            ("Short pick", "Task exception + inventory adjust; no ghost ship"),
            ("Negative inventory attempt", "Reject without adjustment authority"),
        ],
        "split_stay": [
            ("Combinatorial explosion", "Hard caps, beam search, pre-filters by geo/price"),
            ("Segment gap impossible", "Enforce contiguous coverage of stay dates"),
        ],
        "food_delivery": [
            ("Food ready, no dasher", "Priority assign; pause merchant if systemic"),
            ("Dasher cancelled mid-route", "Reassign; recompute ETA; notify"),
        ],
        "vrp": [
            ("Stop becomes unreachable", "Eject stop; notify; replan remainder"),
            ("Solver exceeds budget", "Return best-so-far feasible plan"),
        ],
        "shipping_label": [
            ("Carrier 500 after purchase unknown", "Reconcile by idem_key; don't repurchase blindly"),
            ("Label PDF lost", "Re-fetch from object store; carrier reprint API"),
        ],
        "ev_charge": [
            ("Connector ICE'd / fault", "Mark unavailable; auto-cancel reservation with notify"),
            ("Roaming auth fail", "Fail session start clearly; don't bill"),
        ],
        "earnings": [
            ("Double payout", "Payout idempotency + ledger uniqueness"),
            ("Negative balance tips clawback", "Policy-driven holds; never silent money invent"),
        ],
    }
    return common + specific.get(d, [
        ("Domain-specific contention", f"Serialize on {spec['noun']} keys; lease/TTL patterns"),
        ("Stale secondary index", "Rebuild from log; serve with lag metric"),
        ("Fanout amplification", "Cap recipients; batch; sample if needed"),
    ])


def deeper_questions(spec: dict) -> list[tuple[str, str]]:
    d = spec["domain"]
    title = spec["title"]
    qs = [
        (f"What is the single hardest correctness invariant in {title}?",
         f"Call out the deal-breaker for this domain—typically **no double-assign / no double-sell / no double-pay / no lost scan**. Design leases, CAS, or ledgers around that invariant before drawing 20 boxes."),
        ("Geohash vs H3 vs S2—what do you pick here?",
         "Radius nearby / dispatch hexes → H3. Viewport coverings → S2. Simple prefix demos → geohash with neighbor awareness. Many production stacks use H3 for marketplace ops and tile/S2 ideas for maps."),
        ("How do you prevent hot partitions?",
         "Shard by cell/event_id/listing_id with high cardinality; avoid city-wide single Redis key; use local queues; waiting rooms for onsale; cache popular read keys at edge."),
        ("Where is eventual consistency unacceptable?",
         "Inventory holds, seat states, bid high-water marks, payment capture, driver leases. Search ranking, heatmaps, review aggregates can lag with SLO."),
        ("Idempotency strategy?",
         "Idempotency-Key + body hash store with TTL; for money/inventory use durable unique constraints on business keys (`hold_id`, `bid_id`, `payout_id`)."),
        ("How do you test geo correctness?",
         "Golden fixtures on cell boundaries, dateline, poles; property tests that k-ring ⊇ true radius neighbors; load tests on downtown density."),
        ("Live location bandwidth math?",
         "drivers × ping_hz × bytes; compress (delta, polyline); adaptive rates; don't store every ping in OLTP—hot index + log/cold store."),
        ("Matching: greedy vs batch?",
         "Greedy low latency; batch improves efficiency/fairness at cost of wait. Hybrid: micro-batches 1–2s in dense cells."),
        ("Surge oscillation?",
         "EMA demand/supply, hysteresis bands, max step, separate driver incentives from rider multiplier, bind quotes to surge_version."),
        ("ETA feedback loops?",
         "Log prediction vs actual; train offline; watch covariate shift in weather/events; never train solely on served ETAs without actuals."),
        ("Ticket onsale architecture?",
         "Waiting room → admit tokens → partitioned seat inventory → short holds → payment → finalize. Seat DB never faces raw herd."),
        ("Calendar booking without overbook?",
         "Represent nights as rows/bitmaps; conditional update WHERE available; hold TTL; confirm converts hold→booked in one txn/CAS."),
        ("Split-stay search under latency?",
         "Limit segments; prefilter geo/price; beam/DP over date splits; cache availability bitmaps; async refine for UI."),
        ("Auction soft close races?",
         "Single-writer per auction or fencing token; end_at extensions transactional with bid; clients subscribe to end_at changes."),
        ("Multi-region dispatch?",
         "Cell ownership with epoch; sticky trips to cell; border handoff protocol; don't active-active the same driver lease."),
        ("Cache invalidation for availability?",
         "Short TTL + version tokens; pub/sub invalidation for listing/seatmap; never cache positive hold across users."),
        ("Observability must-haves?",
         "Lag, freshness, conflict/CAS fail rates, double-assign probes, queue wait, checkout conversion, p99 per stage."),
        ("Load shedding order?",
         "Shed secondary (heatmaps, personalization, alts routes) before transactional holds; for onsale shed bots first."),
        ("Data model for seatmaps?",
         "Immutable seat master + mutable status bitmap/row; publish diffs over WS; holds reference seat_ids + event epoch."),
        ("How would you explain trade-offs in 60s?",
         f"For {title}: emphasize {', '.join(spec['emphasis'][:3])}; progressive cell scale; strong on contention keys; eventual on derived indexes; idempotent mobile retries."),
        ("Consistent hashing vs range geo shards?",
         "Geo range/cell shards preserve locality for nearby queries. Consistent hash by id for user/ledger data. Don't hash drivers globally if you need nearby."),
        ("Exactly-once processing?",
         "Prefer at-least-once + idempotent handlers. Outbox for DB→bus. For payments/labels, reconcile with provider idempotency keys."),
        ("Mobile offline reservation conflicts?",
         "Client optimistic UI; server authoritative CAS; conflict payload with alternatives; never pretend offline hold is final for scarce inventory."),
        ("Fraud vectors?",
         "GPS spoof, bot checkout, shill bidding, review brigading, promo abuse. Layer device reputation, velocity, payment risk, graph features."),
        ("Cost killers at 1000×?",
         "Chatty location fanout, uncapped candidate sets, OFFSET pagination, per-ping OLTP rows, personalized CDN pollution, giant matrix route calls."),
    ]
    # domain spice Qs
    spice = {
        "tickets": ("Why not SQL SELECT FOR UPDATE per seat under onsale?",
                    "Lock contention and connection storms melt the primary. Use partitioned in-memory/Redis seat state with durable commit on purchase, or carefully sharded seat rows + waiting room."),
        "rideshare": ("How do city cells fail independently?",
                      "Dispatch, pricing, and location indexes are cell-scoped; global identity/payments remain; directory maps geo→cell; blast radius tests in game-days."),
        "warehouse": ("Inventory ledger vs current qty table?",
                      "Keep append-only events + materialized qty per bin; events are audit truth; qty is query cache with strong update rules."),
        "maps_platform": ("How do tiles and routing stay consistent with traffic?",
                          "Different planes: tiles can lag; routing uses live weight overlay on graph; versions stamped on responses."),
        "auction": ("Proxy bidding?",
                    "Store max proxy; server places min increment bids; still CAS on visible high; watch last-ms storms."),
    }
    if d in spice:
        qs.insert(1, spice[d])
    return qs[:28]


def render(spec: dict) -> str:
    prof = domain_profile(spec["domain"])
    b = prof["baseline"]
    lines: list[str] = []
    a = lines.append

    a(f"# System Design: {spec['title']}")
    a("")
    a(f"> **Focus areas:** {spec['focus']}  ")
    a("> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  ")
    a(f"> **Interview theme:** Maps / marketplaces / mobility / logistics — **{spec['title']}**  ")
    a("> **Quality bar:** Domain-specific numbers, geo/matching/inventory contention called out, deal-breakers explicit")
    a("")
    a("---")
    a("")
    a("## Table of Contents")
    a("")
    a("1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)")
    a("2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)")
    a("3. [High-Level Design](#3-high-level-design)")
    a("4. [Architecture Diagram](#4-architecture-diagram)")
    a("5. [Design Deep Dive](#5-design-deep-dive)")
    a("6. [Wrap-Up](#6-wrap-up)")
    a("7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)")
    a("")
    a("---")
    a("")
    a("## 1. Clarify Requirements (Interview Q&A)")
    a("")
    a(f"Goal: {spec['verbs']} at marketplace/geo scale—with progressive architecture from one city/region to global cells—while protecting **correctness under contention** (inventory, seats, dispatch leases, money).")
    a("")
    a("### 1.0 What this is / is not")
    a("")
    a("| Dimension | This doc | Not this |")
    a("|-----------|----------|----------|")
    a(f"| Job | System to {spec['verbs']} | Unrelated product surface |")
    a(f"| Core noun | `{spec['noun']}` lifecycle | Every adjacent company product |")
    a("| Depth | Senior/staff HLD + deep dives | Only UI mockups or only ML papers |")
    a(f"| Emphasis | {', '.join(spec['emphasis'])} | Generic CRUD without geo/contention |")
    a("| Scale story | Baseline → 10× → 100× → 1,000× | Single-box forever |")
    a("")
    a("### 1.1 Functional Requirements")
    a("")
    a("| # | Question to ask | Expected / typical interviewer answer | Design implication |")
    a("|---|-----------------|----------------------------------------|--------------------|")
    for num, q, ans, imp in fr_rows(spec):
        a(f"| {num} | {q} | {ans} | {imp} |")
    a("")
    a("**MVP functional scope (lock with interviewer):**")
    a("")
    for i, e in enumerate(spec["emphasis"], 1):
        a(f"{i}. Deliver a production-quality path for **{e}**.")
    a(f"{len(spec['emphasis'])+1}. Durable `{spec['noun']}` state machine with idempotent writes.")
    a(f"{len(spec['emphasis'])+2}. Observability: latency histograms, lag/freshness, conflict rates, business KPIs.")
    a(f"{len(spec['emphasis'])+3}. Explicit degrade modes for peaks (shed secondary work first).")
    a(f"{len(spec['emphasis'])+4}. Security/privacy basics for location/PII/payments as applicable.")
    a(f"{len(spec['emphasis'])+5}. Load/perf test plan for hot cells/events.")
    a("")
    a("**Out of MVP (explicitly defer):**")
    a("")
    a("- Global single-objective optimizer across all cities/events without cells")
    a("- Perfect ML personalization / research SOTA as a blocker")
    a("- Active-active multi-writer on the same contended inventory/dispatch key")
    a("- Full offline entire catalog on device (except the offline-reservation doc)")
    a("- Building a complete payments network or map from scratch when a platform dependency exists")
    a("")
    a("### 1.2 Non-Functional Requirements")
    a("")
    a("| # | Question | Expected answer | Target |")
    a("|---|----------|-----------------|--------|")
    for num, q, ans, tgt in nfr_rows(spec):
        a(f"| {num} | {q} | {ans} | {tgt} |")
    a("")
    a("### 1.3 Cases (User Flows & Edge Cases)")
    a("")
    a("**Happy paths**")
    a("")
    a(f"1. User/system initiates flow to {spec['verbs']} → validation → core `{spec['noun']}` created.")
    a("2. Geo/index or inventory lookup returns consistent candidates under SLO.")
    a("3. Contended action (match/hold/bid/book) succeeds exactly once under retry.")
    a("4. Realtime observers (if any) see ordered status/location/ETA updates.")
    a("5. Terminal state: complete/cancel/expire with money and inventory reconciled.")
    a("6. Reload/new device sees source-of-truth state (not only client memory).")
    a("")
    a("**Edge / failure cases**")
    a("")
    a("| Case | Behavior |")
    a("|------|----------|")
    for case, behavior in edge_cases(spec):
        a(f"| {case} | {behavior} |")
    a("")
    a("### 1.4 Scales (Progressive)")
    a("")
    a("Establish a **baseline**, then stress-test at 10× / 100× / 1,000×.")
    a("")
    a(f"| Metric | Baseline | 10× | 100× | 1,000× |")
    a("|--------|----------|-----|------|--------|")
    a(f"| {prof['scale_metric']} | {prof['scale_vals'][0]} | {prof['scale_vals'][1]} | {prof['scale_vals'][2]} | {prof['scale_vals'][3]} |")
    for name, v0, v1, v2, v3 in prof["extra_metrics"]:
        a(f"| {name} | {v0} | {v1} | {v2} | {v3} |")
    a(f"| Regions/cells | 1–few | multi-city | multi-country | global cell mesh |")
    a(f"| Peak factor vs avg | 5–10× | 10× | 20× events | 50×+ onsale/stadium |")
    a(f"| Team operability | 1 oncall | platform | multi-team | cell SRE model |")
    a("")
    a("**What each jump forces architecturally:**")
    a("")
    a("- **10×:** Add caching, read replicas, async indexing, basic cell/city partitioning, and idempotency stores.")
    a("- **100×:** Shard by geography/event/listing; split hot path (holds/match/location) from cold path (analytics/search build); introduce dedicated realtime gateways.")
    a("- **1,000×:** Cell architecture with directory service, home-region single-writer for contended keys, tiered storage, edge caches, and explicit multi-tenant/marketplace fairness.")
    a("")
    a("### 1.5 Etc. (Constraints & Assumptions)")
    a("")
    a("- **Cloud:** one primary cloud, multi-AZ; multi-region DR / active-passive cells.")
    a("- **Mobile + web** clients with flaky networks; retries are normal.")
    a("- **Dependencies:** maps/routing/payments/carriers may be platform services—design façades.")
    a("- **Regulatory:** location retention limits, payments PCI scope isolation, local labor rules for couriers where relevant.")
    a("- **Time:** server clocks via NTP; TTLs enforced server-side.")
    a("")
    a("**Scope statement to repeat back:**")
    a("")
    a(f"> Design **{spec['title']}** to {spec['verbs']}, emphasizing {', '.join(spec['emphasis'])}. "
      f"Start from baseline ~{prof['scale_vals'][0]} {prof['scale_metric'].lower()} and evolve through 10×/100×/1,000× with geo/cell partitioning. "
      f"MVP protects contention invariants with idempotent APIs; defer global omniscient optimizers.")
    a("")
    a("---")
    a("")
    a("## 2. Back-of-the-Envelope Estimation")
    a("")
    a("### 2.1 Primary traffic")
    a("")
    a("```text")
    a(f"Baseline primary: {b['Primary QPS']}")
    a(f"Entities (order-of): {b['Entities']}")
    a(f"Write class focus: {b['Write QPS']}")
    a(f"Typical payload: {b['Payload']}")
    a(f"Hot structure: {b['Hot structure']}")
    a("Peak = 5–20× average depending on events/weather/onsale")
    a("```")
    a("")
    a("### 2.2 QPS → machine count (rule of thumb)")
    a("")
    a("```text")
    a("Assume one stateless API node handles ~2–5K simple QPS (CPU-bound JSON)")
    a("or ~500–2K QPS when each request fans out to geo index + rank.")
    a(f"Baseline → start N+2 nodes; at 100× prefer cell-local fleets over one giant ASG.")
    a("```")
    a("")
    a("### 2.3 Bandwidth")
    a("")
    a("```text")
    a(f"egress ≈ QPS × payload_size")
    a(f"Use {b['Payload']} as mean response/event size for order-of math.")
    a("Realtime fanout often dominates: subscribers × update_hz × bytes.")
    a("Compress deltas; coalesce; don't send full snapshots at 1 Hz to millions.")
    a("```")
    a("")
    a("### 2.4 Storage")
    a("")
    a("```text")
    a("OLTP: contended entities (trips, holds, seats, bookings) — high IOPS, not necessarily PB.")
    a("Index/search: derived docs — grows with catalog × replicas.")
    a("Telemetry/ping logs: append-only — can be PB/month; tier to cold object storage.")
    a("Object store: labels, photos, seatmap assets, tile bundles.")
    a("```")
    a("")
    a("### 2.5 Memory (hot indexes)")
    a("")
    a("```text")
    a("Geo postings / live driver sets / seat bitmaps should be bounded per cell.")
    a("Example: 100K live drivers × 64B ≈ 6.4 MB meta + cell sets;")
    a("stadium fanout state is the real memory risk — shard subscriptions.")
    a("```")
    a("")
    a("### 2.6 Cache")
    a("")
    a("| Data | TTL | Notes |")
    a("|------|-----|-------|")
    a("| Hot geo tiles / discovery pages | 10–60s | SWR; coalesce |")
    a("| Quotes / surge_version | 30–120s | Bind into checkout |")
    a("| Seatmap snapshots | seconds | Versioned diffs |")
    a("| Catalog/listing docs | minutes | Invalidate on write |")
    a("| Negative/zero-result | short | Avoid stampede |")
    a("")
    a("### 2.7 Hot keys")
    a("")
    a(f"Expect hot keys around popular cells, onsale `event_id`, viral listings, downtown lunch hexes. "
      f"Mitigate with **{b['Hot structure']}**, admission control, and key sharding.")
    a("")
    a("### 2.8 Write amplification anti-patterns")
    a("")
    a("- One OLTP row per GPS ping")
    a("- Rebuilding entire search index per field change")
    a("- OFFSET deep pagination on map pans")
    a("- Fanout full seatmap JSON every click")
    a("- Synchronous multi-region commit on every location update")
    a("")
    a("---")
    a("")
    a("## 3. High-Level Design")
    a("")
    a("### 3.1 Planes (split early)")
    a("")
    a("| Plane | Responsibility | Store/tech (typical) |")
    a("|-------|----------------|----------------------|")
    a("| Edge / API | Auth, rate limits, routing to cells | Gateway + mesh |")
    a("| Transactional | Holds, bookings, trips, bids, ledgers | Postgres/Spanner-like / Redis+durable |")
    a("| Geo / live index | Nearby, live locations, hex state | Redis/memory + Kafka |")
    a("| Search / discovery | Documents, facets, ranking | ES/OpenSearch/Lucene / custom |")
    a("| Realtime | WS/SSE fanout | Gateway + pubsub |")
    a("| Async | Indexing, notifications, analytics | Kafka + workers |")
    a("| Object | Photos, labels, tiles | S3/GCS + CDN |")
    a("")
    a("### 3.2 Core algorithm / control loop")
    a("")
    a("```text")
    a(prof["algo"])
    a("```")
    a("")
    a("### 3.3 APIs (representative)")
    a("")
    a("```http")
    for api in prof["apis"]:
        a(api)
    a("```")
    a("")
    a("Use `Idempotency-Key` on all creates that allocate scarce resources or money.")
    a("")
    a("### 3.4 Data model (sketch)")
    a("")
    a("```text")
    for ent in prof["entities"]:
        a(ent)
    a(f"AuditEvent{{entity_id, type, actor, ts, payload_ref}}")
    a(f"Outbox{{id, topic, payload, published}}")
    a("```")
    a("")
    a("### 3.5 Why choose A over B (critical trade-offs)")
    a("")
    a("| Option | Pros | Cons | When |")
    a("|--------|------|------|------|")
    a("| Cell/city single-writer | Simple invariants; blast radius | Cross-cell handoff complexity | Contended dispatch/inventory |")
    a("| Global active-active | Low RPO/RTO reads | Conflict hell on seats/trips | Read-mostly catalogs only |")
    a("| Redis seat/hold state + durable order | Survives onsale QPS | Must design crash rebuild | Ticket/seat hot path |")
    a("| Pure RDBMS locks | Familiar | Melts on onsale/stadium | Low contention MVP |")
    a("| Micro-batch matching | Better efficiency | Extra wait | Dense rides/delivery |")
    a("| Pure greedy matching | Simple/fast | Suboptimal; racey without leases | Sparse MVP |")
    a("| Approximate geo + refine | Fast recall | Needs exact distance pass | All nearby systems |")
    a("| Full table geo scan | 'Correct' naively | Impossible at scale | Never beyond toy |")
    a("")
    a("**Deal-breakers:**")
    a("")
    a("- Double dispatch / double book / double sell seats")
    a("- Silent money divergence (earnings vs payouts)")
    a("- Unbounded interactive queues (user waits forever with no token)")
    a("- Serving precise location to unauthorized clients")
    a("")
    a("### 3.6 Domain deep notes")
    a("")
    a(f"**{spec['title']}** interview signal: speak fluently about **{spec['emphasis'][0]}** and **{spec['emphasis'][1]}**, "
      "then connect to failure modes (TTL expiry, CAS conflicts, cell failover).")
    a("")
    a("- Keep **command** (allocate) separate from **query** (search/heatmap).")
    a("- Bind user-visible prices/ETAs to **versioned quotes** with TTL.")
    a("- Prefer **leases with expiry** over eternal locks.")
    a("- Emit **domain events** via outbox for search, notifications, analytics.")
    a("- Put **admission control** in front of hot inventory (onsale, stadium, viral listing).")
    a("")
    a("### 3.7 State machine (generic template specialized in speech)")
    a("")
    a("```text")
    a("created → reserved/held/matched → in_progress → completed")
    a("                 ↘ expired/cancelled")
    a("                 ↘ failed (compensated)")
    a("```")
    a("")
    a("Only one terminal transition wins (CAS on `version` / conditional update).")
    a("")
    a("---")
    a("")
    a("## 4. Architecture Diagram")
    a("")
    a("```mermaid")
    a("flowchart TB")
    a("  subgraph Clients")
    a("    Mob[Mobile/Web]")
    a("    Partners[Partner/Carrier APIs]")
    a("  end")
    a("  Mob --> Edge[Edge Gateway / CDN]")
    a("  Partners --> Edge")
    a("  Edge --> API[API / BFF]")
    a("  API --> Dir[Geo/Cell Directory]")
    a("  Dir --> Cell[Cell Services]")
    a("  subgraph Cell")
    a("    TX[Transactional Service]")
    a("    Geo[Geo/Live Index]")
    a("    Match[Match/Hold/Price Engine]")
    a("    RT[Realtime Gateway]")
    a("  end")
    a("  TX --> DB[(OLTP)]")
    a("  TX --> Q[(Redis Leases/Hot State)]")
    a("  Geo --> Q")
    a("  Match --> Geo")
    a("  Match --> TX")
    a("  TX --> OB[Outbox → Kafka]")
    a("  OB --> Idx[Indexers / Notifiers / Analytics]")
    a("  Idx --> Search[(Search)]")
    a("  RT --> Mob")
    a("  API --> Search")
    a("  Obj[(Object Store)] --> Edge")
    a("```")
    a("")
    a("C4-ish note: **Directory** is global and small; **Cell** owns contended writes; **Search** is derived.")
    a("")
    a("---")
    a("")
    a("## 5. Design Deep Dive")
    a("")
    a("### 5.1 Reliability")
    a("")
    a("#### 5.1.1 Data loss prevention")
    a("")
    a("- Durable commit on allocation paths before user ACK (hold/trip/bid/ledger).")
    a("- Kafka (or equiv) with retained topics for index rebuilds and analytics.")
    a("- Object store for irreversible artifacts (labels, tickets PDFs) with checksums.")
    a("- Backup + PITR on OLTP; game-day restore tests.")
    a("")
    a("#### 5.1.2 Retries, idempotency, exactly-once-ish")
    a("")
    a("- At-least-once delivery everywhere; handlers idempotent.")
    a("- Idempotency records keyed by client key / business natural key.")
    a("- Outbox pattern avoids dual-write loss between DB and bus.")
    a("- Provider calls (carriers, payment, GDS) use provider-side idempotency + reconcile jobs.")
    a("")
    a("#### 5.1.3 Rate limits & backpressure")
    a("")
    a("- Edge: per-user/device/IP + per-event buckets.")
    a("- Cell: max in-flight match/hold ops; queue with deadline.")
    a("- Shed: personalization → alts → heatmap → eventually reject new non-critical reads.")
    a("- Never let interactive threads block on unbounded Kafka consumer lag.")
    a("")
    a("#### 5.1.4 Consistency toolkit")
    a("")
    a("| Tool | Use |")
    a("|------|-----|")
    a("| CAS / conditional update | seats, high bid, calendar nights |")
    a("| Lease + fencing token | driver dispatch, connector reservation |")
    a("| Idempotent ledger | earnings, payouts |")
    a("| Waiting room tokens | ticket onsale admit |")
    a("| Quote version binding | surge/delivery price |")
    a("")
    a("#### 5.1.5 Failure drills")
    a("")
    a("- Kill cell leader / Redis master; verify rebuild from snapshot+log.")
    a("- Clock jump; ensure TTL logic safe.")
    a("- Duplicate webhook storms from carriers/payments.")
    a("- Split brain directory epoch: fencing must reject stale writers.")
    a("")
    a("### 5.2 Scalability")
    a("")
    a("#### 5.2.1 Sharding keys")
    a("")
    a("| Entity | Shard key | Why |")
    a("|--------|-----------|-----|")
    a("| Live drivers / dashers | city/H3 cell | locality for nearby |")
    a("| Trips/orders | city + id | cell ownership |")
    a("| Events/seats | event_id | onsale isolation |")
    a("| Listings/calendars | listing_id | contention locality |")
    a("| Users/ledger | user/driver_id | money locality |")
    a("| Search | geo partition + doc id | query locality |")
    a("")
    a("#### 5.2.2 Scale-up vs scale-out")
    a("")
    a("- Vertical for single-event onsale partition (fat Redis / memory) carefully.")
    a("- Horizontal cells for global growth.")
    a("- Solver/ETA model fleets autoscale on CPU/GPU separately from API.")
    a("")
    a("#### 5.2.3 Storage tiers")
    a("")
    a("1. **Hot:** leases, live geo, seat bitmaps, open orders")
    a("2. **Warm:** OLTP primary data")
    a("3. **Search:** derived documents")
    a("4. **Cold:** ping history, old tracking, audit → object/columnar")
    a("")
    a("#### 5.2.4 Parallelization")
    a("")
    a("- Cell-local matchers; parallel k-ring fetches with budgets")
    a("- Batch solvers with worker pools and time budgets")
    a("- Matrix routing chunked; never one giant NxN without limits")
    a("")
    a("#### 5.2.5 Progressive scale checklist")
    a("")
    a("| Jump | Must add |")
    a("|------|----------|")
    a("| 10× | cache, idempotency DB, replicas, async index |")
    a("| 100× | geo/event shards, realtime gateway, backpressure |")
    a("| 1,000× | cell directory, edge, tiering, multi-team platforms |")
    a("")
    a("### 5.3 Maintainability")
    a("")
    a("#### 5.3.1 Observability")
    a("")
    a(f"Golden signals for **{spec['title']}**: QPS/latency/errors on APIs; "
      f"**freshness/lag** on geo/index; **CAS conflict rate**; **lease expiry rate**; "
      f"business KPIs (match rate, book conversion, onsale checkout, on-time delivery).")
    a("")
    a("Distributed traces across quote → hold → pay → finalize.")
    a("")
    a("#### 5.3.2 Operability")
    a("")
    a("- Feature flags for matcher/pricing/ranking")
    a("- Kill switches for surge, batching, soft-close extensions")
    a("- Runbooks: cell failover, inventory freeze, onsale pause, carrier outage")
    a("- Capacity dashboards per cell/event")
    a("")
    a("#### 5.3.3 Migrations")
    a("")
    a("- Dual-write new shard map; shadow read; cutover with epoch bump")
    a("- Calendar/seat schema changes expand/contract; never lock table during onsale")
    a("- Model/artifact rollout with canaries and rollback")
    a("")
    a("#### 5.3.4 Multi-tenant / multi-brand")
    a("")
    a("- `org_id` / `marketplace_id` on rows; quotas per tenant")
    a("- Noisy-neighbor limits on shared search/telemetry clusters")
    a("")
    a("#### 5.3.5 Security & privacy")
    a("")
    a("- Precise location ACL + retention TTL")
    a("- Field-level encryption for payment tokens (tokenize)")
    a("- Audit every admin inventory override")
    a("- Bot/device reputation on checkout and bid paths")
    a("")
    a("---")
    a("")
    a("## 6. Wrap-Up")
    a("")
    a("### 6.1 Decision summary")
    a("")
    for i, e in enumerate(spec["emphasis"], 1):
        a(f"{i}. Invest in **{e}** as a first-class subsystem.")
    a(f"{len(spec['emphasis'])+1}. Split planes: transactional vs geo/live vs search vs realtime vs async.")
    a(f"{len(spec['emphasis'])+2}. Cells/geo shards for blast radius; directory for routing.")
    a(f"{len(spec['emphasis'])+3}. Idempotency + CAS/leases on contention; eventual on derived data.")
    a(f"{len(spec['emphasis'])+4}. Progressive scale: cache → shard → cell mesh.")
    a("")
    a("### 6.2 Phased rollout")
    a("")
    a("| Phase | Deliverable |")
    a("|-------|-------------|")
    a("| P0 | Single region MVP; strong invariants; metrics |")
    a("| P1 | Caching + async indexing + basic geo cells |")
    a("| P2 | Multi-city cells; realtime fanout hardened |")
    a("| P3 | Global directory; edge; advanced matching/pricing/ML |")
    a("| P4 | Game-days, chaos, cost optimization, multi-tenant limits |")
    a("")
    a("### 6.3 What to say if time runs out")
    a("")
    a(f"\"For {spec['title']}, I'd guarantee **{spec['emphasis'][0]}** correctness with leases/CAS, "
      f"serve discovery via approximate geo + refine, isolate peaks in cells, and bind user quotes. "
      f"Everything else—SOTA ranking, global OR solvers—is iterative on that skeleton.\"")
    a("")
    a("---")
    a("")
    a("## 7. Deeper / Related Interview Questions")
    a("")
    for i, (q, ans) in enumerate(deeper_questions(spec), 1):
        a(f"### Q{i}. {q}")
        a("")
        a(ans)
        a("")
    a("---")
    a("")
    a("## Appendix A — Interview checklist")
    a("")
    a("- [ ] Clarified MVP vs out-of-scope")
    a("- [ ] Wrote scale table with 10×/100×/1,000×")
    a("- [ ] Named contention invariant + mechanism")
    a("- [ ] Drew cell/directory boundary")
    a("- [ ] Separated write classes in estimation")
    a("- [ ] Covered failure: retry, TTL, failover")
    a("- [ ] Listed metrics/alerts")
    a("- [ ] Stated 2–3 explicit trade-offs")
    a("")
    a("## Appendix B — Sample numbers scratchpad")
    a("")
    a("```text")
    a(f"problem: {spec['title']}")
    a(f"baseline: {b}")
    a("ping_bandwidth = active_movers * hz * bytes_per_ping")
    a("fanout = subscribers * updates_per_sec * bytes")
    a("hold_capacity = seats_or_drivers_per_shard / avg_hold_seconds")
    a("search_cost ≈ candidates * score_ns + doc_fetch")
    a("```")
    a("")
    a("## Appendix C — Related problems in this section")
    a("")
    a("Cross-link mentally: Uber/Lyft ↔ matching ↔ location ↔ ETA ↔ surge; "
      "DoorDash ↔ batching ↔ route opt ↔ tracking; "
      "Airbnb ↔ listing search ↔ booking ↔ alerts; "
      "Ticketmaster ↔ assigned seats; hotels ↔ rental booking; "
      "package tracking ↔ shipping labels ↔ warehouse.")
    a("")
    a("## Appendix D — Anti-patterns cheat sheet")
    a("")
    a("| Anti-pattern | Symptom | Fix |")
    a("|--------------|---------|-----|")
    a("| Global lock | timeouts at peak | shard + leases |")
    a("| OFFSET pagination | slow deep pages | cursors |")
    a("| Per-ping SQL insert | DB melt | hot index + log |")
    a("| Cache personalized publicly | privacy bug | private keys / no CDN |")
    a("| Sync 7 carrier calls in request | p99 blowup | async + timeouts |")
    a("| Ignore hold TTL | phantom inventory | expirer + reconciler |")
    a("| Active-active seat writers | double sell | single-writer epoch |")
    a("")
    a("## Appendix E — Glossary")
    a("")
    a("| Term | Meaning |")
    a("|------|---------|")
    a("| Cell | Geo/ownership unit for blast-radius-limited writes |")
    a("| Lease | Time-bounded exclusive claim (driver, connector, seat hold) |")
    a("| CAS | Compare-and-set conditional write |")
    a("| k-ring | H3 neighbor disk for radius recall |")
    a("| Quote binding | User-visible price/ETA tied to version+TTL |")
    a("| Waiting room | Admission control before hot inventory |")
    a("| Outbox | DB-transactional event publish pattern |")
    a("| Soft close | Auction end extension to reduce sniping |")
    a("| VRP | Vehicle routing problem |")
    a("| ARI/ARIQ | Availability, rates, inventory (hotel) |")
    a("")
    a("## Appendix F — Worked micro-examples")
    a("")
    a("### F.1 Nearby candidate math")
    a("")
    a("```text")
    a("H3 res 9 cells in ring k=2 ≈ up to 19 cells")
    a("avg 80 POIs/cell → ~1.5K candidates → filter to 200 → rank top 20")
    a("budget: 10ms fetch + 5ms score + 5ms pack")
    a("```")
    a("")
    a("### F.2 Dispatch lease")
    a("")
    a("```text")
    a("SET driver_lease:{id} = {trip,token,exp} NX EX 15")
    a("on accept: CAS trip.driver_id + commit")
    a("on timeout: delete lease if token matches; requeue demand")
    a("```")
    a("")
    a("### F.3 Seat hold")
    a("")
    a("```text")
    a("WATCH seats; if all AVAILABLE; MULTI mark HELD with hold_id EX 120; EXEC")
    a("-- or single Lua/txn on seat partition")
    a("```")
    a("")
    a("### F.4 Surge hex")
    a("")
    a("```text")
    a("mult = clamp(smooth(demand/supply), 1.0, max_mult)")
    a("if |mult-prev| < epsilon: keep prev  # hysteresis")
    a("quote stores surge_version")
    a("```")
    a("")
    a("## Appendix G — Staff-level extensions")
    a("")
    a("When interviewer pushes to staff:")
    a("")
    a("1. **Marketplace health loops:** how pricing/matching/ETA co-adapt without oscillation.")
    a("2. **Multi-objective dispatch:** wait time, cost, fairness, utilization—constraint hierarchy.")
    a("3. **Data platform:** feature store for ETA/surge; experiment assignment; metric guardrails.")
    a("4. **Org topology:** cell platform team vs marketplace product teams; API contracts.")
    a("5. **Compliance:** retention for location; audit for inventory overrides; financial SoX-ish ledgers.")
    a("6. **Disaster:** region loss runbook; freeze holds; drain trips; customer comms.")
    a("")
    a("## Appendix H — Requirement replay card")
    a("")
    a(f"| Field | Value |")
    a(f"|-------|-------|")
    a(f"| Problem | {spec['title']} |")
    a(f"| Noun | {spec['noun']} |")
    a(f"| Emphasis | {', '.join(spec['emphasis'])} |")
    a(f"| Baseline | {prof['scale_vals'][0]} {prof['scale_metric']} |")
    a(f"| Invariant | no double-allocate / no silent money loss |")
    a(f"| Scale endgame | cell mesh + edge + tiered stores |")
    a("")
    a("---")
    a("")
    a(f"*End of {spec['title']} system design prep doc.*")
    a("")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    counts = []
    for spec in SPECS:
        text = render(spec)
        path = OUT / spec["fn"]
        path.write_text(text)
        n = text.count("\n") + (0 if text.endswith("\n") else 1)
        # wc -l style: count newlines
        nlines = text.count("\n")
        counts.append((spec["fn"], nlines))
        print(f"{nlines:4d}  {spec['fn']}")
    short = [c for c in counts if c[1] < 550]
    print(f"\nWrote {len(counts)} files. Under 550 lines: {len(short)}")
    for fn, n in short:
        print(f"  SHORT {n} {fn}")


if __name__ == "__main__":
    main()
