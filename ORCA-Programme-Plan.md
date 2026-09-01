# ORCA — Agentic AI Marine Intelligence Platform for Indian Waters

**Engineering & Programme Plan**
Version 0.1 (Draft for internal review) · 1 September 2026

---

## 0. Document status and how to read it

This is the master planning document for Project ORCA. It is written to government-proposal
standard: it names real systems, states methodology explicitly, and separates what we know from
what we must confirm.

**Critical caveat on external facts.** This draft was prepared without live network access.
Every claim about a third-party system, endpoint, policy or programme carries a confidence tier:

| Tier | Meaning | Usable in a submitted bid? |
|---|---|---|
| **[A]** | Structurally reliable. Standards, physics, well-established institutional facts. | Yes |
| **[B]** | Probably correct, but a specific detail (URL, resolution, cadence, cost) must be checked. | Only after checking |
| **[C]** | Lead only. Name, scale or existence uncertain. | No — verify or delete |

**§7.6 is the Verification Ledger** — the consolidated list of every [B] and [C] item, ordered by
how much damage an error would do. Nothing in Tier B or C should reach a reviewer unchecked. A
government evaluator will check exactly these details, and an invented endpoint or a misstated
scheme outlay is the fastest way to lose credibility on an otherwise strong bid.

**Reading paths.** Executives: §1, §2, §12, §14. Engineers: §5–§9. Reviewers and compliance:
§11, §13, §15, and the traceability matrix in §16.

---

## 1. Executive summary

India generates world-class marine Earth Observation data. Roughly four million people depend on
marine fisheries for their livelihood, and the majority put to sea in small craft with no
instrumentation beyond a mobile phone that loses signal a few kilometres out. The gap is not data
production. **The gap is synthesis, language, last-mile reach, and trust.**

Today a fisherman deciding whether to sail tomorrow morning must mentally join a wave-height
forecast, a wind forecast, a tide table, a fishing-zone advisory, and a cyclone bulletin — five
products from three institutions, published in different formats, mostly in English or standard
written registers, most of them not designed to answer his actual question, which is simply:
*"should I go, and where?"*

ORCA answers that question. It is a conversational, multi-agent decision-support platform that
interprets intent in the user's own language, autonomously plans and executes a chain of retrieval
and analysis over satellite EO, model forecast, and in-situ data, and returns a verdict with the
reasoning and evidence attached.

**The four capability tracks in scope:**

1. **Potential Fishing Zone guidance and a go/no-go safety verdict** — vessel-class-aware, with the
   binding constraint named.
2. **Multilingual and voice interaction** — automatic language identification, response in the same
   language, speech in and out, because literacy cannot be assumed.
3. **Geofencing and proactive alerts** — predictive time-to-boundary warnings for international
   maritime boundaries, marine protected areas and restricted waters; push alerts for cyclones,
   high waves and lightning.
4. **Maps, safe-route optimisation, and causal explanation** — interactive geospatial output, routing
   over a time-varying sea-state cost field, and structured attribution for questions like
   "why has fish productivity declined here?"

**The three design commitments that make this defensible.**

The first is the **numerical integrity invariant**: no quantitative claim ever reaches a user unless
a deterministic tool computed it. The language model plans, selects tools, and explains. It never
performs the physics and never authors a number. Every figure in every response is bound by
reference to a computed evidence record. This single constraint is what separates a life-safety
system from a chatbot that sounds confident (§6.4).

The second is **asymmetric safety calibration**. Telling someone the sea is safe when it is not is
categorically worse than the reverse. We therefore tune, measure and report against an explicit
asymmetric loss function, rather than optimising overall accuracy (§10.3).

The third is **graceful degradation by architecture**. Indian institutional marine data is largely
not programmatically accessible today; much of it requires formal agreements (§7.3). Rather than
predicate the build on access we do not yet have, ORCA runs on an open, no-agreement-required data
foundation from day one, and treats each institutional feed as an accuracy *upgrade* that slots into
a stable internal contract. The system works before any MoU is signed, and works better after (§7.2).

**Shape of the programme:** 18 months, five phases, each with measurable exit criteria; a
single-district vertical slice proven against buoy observations before any breadth is attempted;
independent security audit and a supervised field pilot with a state fisheries department before
any unsupervised safety advisory is issued to a real user.

---

## 2. Problem framing — what is actually broken

A proposal that restates the brief adds nothing. This section states our own diagnosis, because it
drives every architectural decision that follows.

### 2.1 Five real failure modes

**Cognitive load at the decision point.** The decision "do I sail, and where do I go" requires
joining five or more products. Each is individually good. None answers the question. The user is
performing the integration, at 4 a.m., on a phone, often with limited formal schooling. Every
existing product optimises its own layer and pushes the fusion cost onto the least-resourced actor
in the chain.

**Language and modality mismatch.** Coastal fishing communities speak Tamil, Malayalam, Telugu,
Odia, Bengali, Marathi, Gujarati, Konkani, Tulu and many local dialects. Advisories are frequently
issued in English or in a formal written register distant from spoken coastal usage, and in text form
to users for whom audio is the native channel. Fishing vocabulary is intensely local: fishing grounds
are named after landmarks and wrecks, not coordinates, and fish names vary between adjacent districts.

**The last mile is a hard physical constraint, not a UX problem.** Cellular coverage typically
degrades within roughly 10–20 km of shore [B — verify with operator coverage data per coast].
Precisely when conditions change and the advisory matters most, the user is unreachable by the
channel the advisory was designed for. Any architecture that assumes live connectivity at the moment
of need is designing for a user who is not there.

**Products are not designed for the actual hazard.** Significant wave height alone is a poor
predictor of danger to a small boat. The lethal conditions are typically: crossing a river-mouth bar
or surf zone in long-period swell, being caught in beam or following seas, sudden squall and
lightning, and fog. A forecast of "Hs 1.8 m" is technically accurate and operationally useless
without the vessel class, the departure and landing point geometry, and the wave period and
direction (§8.1.3).

**Trust is earned and easily lost.** Advisories that are too conservative get ignored, because
ignoring them is usually rewarded — the sea is usually fine. An advisory system's credibility rests
on being right about the *unusual* day, and on being transparent about why it says what it says.
This is the strongest argument for making the reasoning visible rather than emitting a verdict from
a black box. It is also why we treat human-verified evidence chains as a product feature, not
engineering hygiene.

### 2.2 What ORCA does not claim

Honesty about scope strengthens a bid.

- ORCA **does not produce new forecasts.** It does not run its own numerical weather or wave model.
  It consumes authoritative model output and adds intent understanding, fusion, reasoning,
  explanation, and delivery. Where we derive a quantity ourselves (frontal gradients, thermocline
  depth, anomaly fields), we say so and show the method.
- ORCA is **not a certified navigation system.** Route output is decision support. It is not ECDIS,
  it is not built on IHO S-57/S-101 electronic navigational charts, and it must not be presented as
  a substitute for either [A].
- ORCA **does not adjudicate legality.** Geofencing output is advisory proximity information. The
  system warns that a boundary is near; it never asserts that a user has committed an offence.
- ORCA **does not replace INCOIS, IMD or the Coast Guard.** It is an intelligence and delivery layer
  over their authoritative products, and it attributes them explicitly. Positioning it as a
  competitor would be both strategically foolish and factually wrong.

### 2.3 Users and the jobs they need done

| User | The question they actually ask | What a good answer contains |
|---|---|---|
| Small-craft fisherman (non-mechanised / motorised FRP, day trip, 0–20 nm) | "Can I go tomorrow morning, and where are the fish?" | One verdict, a direction and distance from a named landing centre, a bar-crossing note, a return-by time, in spoken local language |
| Skipper / owner, mechanised trawler (multi-day, 20–200 nm) | "Where do I fish this trip, what weather am I routing through, where do I not go?" | Zone options with confidence, route with sea-state exposure, boundary and restricted-area distances, fuel implication |
| Deep-sea / tuna longline operator | "Where is the thermal front and the right subsurface structure?" | Frontal maps, thermocline and mixed-layer depth, eddy structure, multi-day persistence |
| Fisheries department officer (state / district) | "Who is at risk right now, and is my advisory reaching them?" | Live risk map by landing centre, dissemination and acknowledgement telemetry, vessel-density overlay |
| Disaster management (SDMA / NDMA / Coast Guard) | "Who is at sea in the path of this system, and can I reach them?" | Cyclone-track exposure, last-known-position aggregate, multi-channel broadcast with delivery audit |
| Researcher / analyst | "Give me the data behind this, reproducibly." | Queryable archive, standards-conformant API, provenance and citation, notebook-friendly access |
| Maritime / shipping operator | "Sea state and hazards along my passage." | Route sea-state profile, warnings-in-force, port conditions |

The small-craft fisherman is the **primary design target**. Where his needs conflict with another
user's, his win. Every other persona has better alternatives available; he does not.

---

## 3. Scope

### 3.1 In scope for the 18-month programme

All four capability tracks, delivered in the phased order of §12, plus:

- Conversational interface (web, Android, voice) with multi-turn context and query refinement.
- Automatic language identification with response in the same language; eight coastal Indian
  languages plus English and Hindi by Phase 2.
- Autonomous data discovery, retrieval and fusion across satellite EO, model forecast, in-situ
  observation and vector GIS layers.
- Deterministic analytics library for risk scoring, frontal detection, anomaly attribution,
  geodesic geofencing and time-dependent routing.
- Explainable evidence bundles surfaced in the UI and available via API.
- Proactive monitoring: standing queries, watch areas, and push alerting with delivery audit.
- Offline-capable pre-departure briefing bundle and low-bandwidth advisory encoding.
- Standards-conformant outbound APIs (OGC API Features / EDR / Processes, CAP for alerts, STAC for
  the catalogue) so that the platform is a reusable national asset rather than a closed app.
- Full assurance programme: golden-set evaluation, hindcast skill verification against buoys,
  red-teaming, security audit, accessibility compliance.

### 3.2 Explicitly out of scope

- Running our own numerical ocean or atmospheric model.
- Hardware: we integrate with NavIC-enabled terminals and Distress Alert Transmitters where
  available, but we do not design or manufacture devices.
- Vessel monitoring system (VMS) or enforcement tooling. Building surveillance capability on top of
  fishermen's location data would destroy the trust the platform depends on, and we treat that as a
  design red line, not merely an out-of-scope item (§11.3).
- Catch marketplace, price discovery, or financial services.
- Certified electronic navigational charting.

### 3.3 Guiding principles

1. **Deterministic where it matters.** Safety-critical computation is code, tested and versioned.
   The LLM orchestrates and explains (§6.4).
2. **Open data foundation first.** No dependency on an unsigned agreement is on the critical path.
3. **Evidence or silence.** If evidence is insufficient, the system says so and says what is missing.
   It never fills a gap with plausible prose.
4. **Degrade, never fail.** Every layer has a defined behaviour when its inputs are stale, missing or
   contradictory, and the user is told which mode they are in.
5. **Design for the boat, not the browser.** Bandwidth, sunlight, salt, wet hands, one hand on the
   tiller, and audio-first interaction are the design context.
6. **Attribute everything.** Every number carries its source, timestamp and licence.

---

## 4. Solution overview

ORCA is four layers with strictly defined boundaries. The contract between layers is the reason the
system can survive data sources changing underneath it.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  L4  DELIVERY          Web · Android · Voice/IVR · SMS · NavIC-class short   │
│                        message · CAP feed · OGC APIs · Dashboards            │
├──────────────────────────────────────────────────────────────────────────────┤
│  L3  REASONING         Orchestrator + specialised agents                     │
│      (agentic)         Deterministic analytics library (physics & geometry)   │
│                        Evidence assembly · Critic · Explanation generation    │
├──────────────────────────────────────────────────────────────────────────────┤
│  L2  CURATED STORE     Analysis-ready cubes (Zarr) · Tiles (COG/PMTiles)      │
│                        Vector & geofence (PostGIS) · Catalogue (STAC)         │
│                        Feature store · Climatology & anomaly baselines        │
├──────────────────────────────────────────────────────────────────────────────┤
│  L1  INGEST            Source adapters · Normalisation to CF conventions ·    │
│                        Regridding · QC · Provenance stamping · Freshness SLA  │
└──────────────────────────────────────────────────────────────────────────────┘
                    Cross-cutting: observability · audit log · authz ·
                    secrets · cost governance · evaluation harness
```

**Why this shape.** The single most important structural decision is that **agents never talk to
external data sources directly.** They query L2 through typed tool interfaces. Consequences:

- A source changing its format, or an MoU being signed, is an L1 change only. No agent is touched.
- Latency is predictable: agent-time queries hit pre-processed local stores, not remote portals of
  uncertain availability.
- Provenance is enforceable at one chokepoint rather than trusted at many.
- The same curated store serves the conversational path, the proactive alerting path, the public
  API, and the evaluation harness — so all four agree by construction. A system where the alert
  pipeline and the chat pipeline can disagree about the wave height is not auditable.

---

## 5. Architecture

### 5.1 Technology selections

Python core with a React client, as scoped. Each choice below is justified, because for a
government bid "we used the popular thing" is not a reason.

| Concern | Choice | Why this and not the alternative |
|---|---|---|
| Agent orchestration | **LangGraph** (explicit state-machine graphs) | We need auditable, bounded, resumable execution. Free-form ReAct loops give unbounded latency and cost, and are far harder to certify. A graph gives us a replayable state trace per turn, which is an audit requirement, not a nicety. |
| API services | **FastAPI** + Pydantic v2 | Typed contracts generate the OpenAPI spec that our tool schemas and public API share; one source of truth. Async suits the fan-out-heavy workload. |
| Gridded data | **xarray** + **Zarr**, Dask for out-of-core | Zarr gives chunked, parallel, cloud-native reads of exactly the spatial-temporal slice needed. NetCDF-per-timestep would make a 5-day multi-parameter query an I/O disaster. |
| Raster tiles | **COG** + TiTiler; **PMTiles** for vectors | Range-request reads, no tile server state, and PMTiles ships an entire offline basemap as one file — which is what makes the offline briefing bundle feasible (§8.2.4). |
| Vector / geofence | **PostgreSQL 16 + PostGIS 3.4**, `geography` type | Geodesic distance on the WGS84 ellipsoid natively. Planar approximation is unacceptable near international boundaries (§8.3.2). |
| Geodesy | **GeographicLib** / pyproj | Authoritative inverse-geodesic solutions for bearing, distance and forward projection of vessel tracks. |
| Catalogue | **STAC** (pystac, pgstac) | The interoperability standard for EO assets [A]; gives the Data Discovery Agent a uniform, searchable surface over heterogeneous sources instead of bespoke logic per source. |
| Time-series / features | TimescaleDB (same PG cluster) | Buoy and vessel-track series alongside spatial data without a second datastore. |
| Queue / workers | Redis Streams + Celery, or NATS if fan-out grows | Ingest scheduling, alert fan-out, standing-query evaluation. |
| Vector search | pgvector in the same cluster | For advisory-text and document retrieval only. Small corpus; a dedicated vector DB is unjustified operational overhead. |
| LLM serving | Managed frontier API for planning and explanation; self-hosted small open model (7–14 B class) for high-volume routine intents; strict routing between them | Cost and sovereignty. Routine intents are the volume; frontier reasoning is the minority of turns. §5.3 covers the sovereignty question, which a government reviewer will raise. |
| Frontend | React + TypeScript, **MapLibre GL JS** + **deck.gl** | MapLibre is BSD-licensed with no per-load billing or vendor lock — a procurement-relevant difference from Mapbox GL. deck.gl handles large point/track layers on the GPU. |
| Mobile | React Native (shared logic with web), targeting Android 9+ and low-end hardware | The realistic device population is low-end Android. A separate native codebase is not affordable at this team size. |
| Observability | OpenTelemetry → Prometheus/Grafana/Loki; Langfuse-class LLM tracing | Per-turn agent traces are both a debugging tool and the audit artefact. |
| Deployment | Docker + Kubernetes on MeitY-empanelled Indian cloud, or NIC/MeghRaj | Data localisation and procurement eligibility [B — confirm current empanelment list and any localisation mandate applicable to this data class]. |

### 5.2 Repository layout

A monorepo, because the tool schemas, the analytics library and the client types must not drift.

```
orca/
├── docs/                       # this plan, ADRs, data-source dossiers, methodology notes
│   ├── adr/                    # architecture decision records — numbered, immutable
│   └── methodology/            # risk-scoring spec, causal hypothesis library, eval protocol
├── packages/
│   ├── orca-core/              # domain types, EvidenceBundle, units, error taxonomy
│   ├── orca-geo/               # geodesy, geofencing, routing, spatial ops
│   ├── orca-ocean/             # deterministic analytics: fronts, MLD, anomalies, sea state
│   ├── orca-risk/              # vessel profiles, risk scoring, verdict computation
│   ├── orca-ingest/            # source adapters, one module per source, uniform interface
│   ├── orca-agents/            # LangGraph graphs, agent definitions, tool registry
│   ├── orca-lang/              # language ID, translation, ASR/TTS adapters, domain lexicon
│   └── orca-eval/              # golden sets, harness, skill scoring, red-team suites
├── services/
│   ├── api/                    # FastAPI: conversational + OGC-conformant public endpoints
│   ├── ingest-worker/          # scheduled retrieval, normalisation, QC
│   ├── alert-worker/           # standing queries, geofence evaluation, CAP emission
│   └── tiler/                  # TiTiler deployment
├── clients/
│   ├── web/                    # React console
│   └── mobile/                 # React Native
├── infra/                      # Terraform, Helm, Docker, CI/CD
└── data/                       # baseline static layers (boundaries, bathymetry refs), DVC-tracked
```

Two rules enforced in CI: `orca-agents` may not import an ingest adapter (enforces the L1/L3
boundary from §4), and `orca-risk` may not import any LLM client (enforces the numerical integrity
invariant of §6.4 structurally, not by convention).

### 5.3 The sovereignty and model-hosting question

A reviewer will ask why a national marine safety platform should depend on a foreign-hosted model.
The honest answer has three parts, and we should give it before being asked.

**First, the dependency is bounded by design.** Because of the numerical integrity invariant, the
LLM contributes intent parsing, planning, tool selection and prose. It contributes no physics and no
numbers. If every LLM were unavailable tomorrow, ORCA would degrade to a structured-query interface
over the same analytics — reduced usability, unchanged correctness. That is a materially different
risk posture from a system whose answers *are* model outputs.

**Second, routing limits exposure.** We expect the large majority of production turns to match a
small set of recurring intents ("safe tomorrow?", "nearest PFZ", "conditions here") which a
self-hosted small open model handles adequately once the planning step is a classification into a
recipe library (§6.3). Frontier capability is reserved for novel, multi-constraint and causal
queries.

**Third, we plan for substitution rather than asserting it.** The model layer sits behind one
interface with an evaluation harness that scores any candidate model on the same golden set.
Migrating to an Indian sovereign model — Bhashini-adjacent, IndiaAI-programme, or a commercial Indian
provider [B — confirm the current state of the IndiaAI foundation-model programme and available
Indian providers before naming any in a submitted bid] — becomes a measurable decision rather than a
rewrite. We commit to reporting the sovereign-model score alongside the incumbent at each phase gate.

---
