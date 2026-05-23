# MIRROR Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MIRROR — SYSTEM OVERVIEW                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │   TELEGRAM   │     │   MIRROR     │     │   FACEBOOK   │           │
│   │   WAR ROOM   │◄───►│    CORE      │◄───►│   PLATFORM   │           │
│   │  (Control)   │     │  (Brain)     │     │  (Target)    │           │
│   └──────────────┘     └──────┬───────┘     └──────────────┘           │
│                               │                                         │
│              ┌────────────────┼────────────────┐                      │
│              ↓                ↓                ↓                        │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐                     │
│       │  GHOST   │   │ SHADOW   │   │  CANARY  │                     │
│       │ WRITER   │   │ MATRIX   │   │  GUARD   │                     │
│       │  (AI)    │   │(3 Accts) │   │(Safety)  │                     │
│       └──────────┘   └──────────┘   └──────────┘                     │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │                    FREE API AGGREGATOR                       │      │
│   │   Gemini → Groq → Cerebras → OpenRouter → Cloudflare AI   │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │                    LOCAL STORAGE (SQLite)                    │      │
│   │   leads.db | conversations.db | dna_profile.json | logs    │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Core (`mirror/core/`)
- **brain.py** — Main orchestrator, cycles through watch → analyze → write → post
- **scheduler.py** — APScheduler-based timing (active hours, breaks, sleep)
- **state_machine.py** — State management (IDLE, WATCHING, SLEEPING, PAUSED, ERROR)
- **memory.py** — SQLite interface with singleton pattern

### Modules (`mirror/modules/`)
| Module | Lines | Responsibility |
|--------|-------|----------------|
| `dna_cloner.py` | ~100 | Writing style extraction & profile management |
| `archaeologist.py` | ~140 | Lead personality, budget, urgency, pain point detection |
| `watcher.py` | ~120 | Keyword-based Facebook group monitoring |
| `ghost_writer.py` | ~100 | AI + template hybrid response generation |
| `shadow_matrix.py` | ~100 | 3-account browser profile coordination |
| `warmth_protocol.py` | ~90 | 14-day phased group infiltration |
| `nurture_loop.py` | ~90 | 30-day rejection recovery sequence |
| `competitor_radar.py` | ~90 | Pattern-based competitor detection |
| `portfolio_sniping.py` | ~80 | Project matching & showcase generation |
| `safety_guard.py` | ~100 | Action budgeting, rate limiting, canary monitoring |

### API Plugins (`mirror/api_plugins/`)
7 pre-configured free API providers with auto-failover chain:
1. Google Gemini (primary)
2. Groq (fallback)
3. Cerebras (heavy tasks)
4. OpenRouter (emergency)
5. Cloudflare Workers AI (edge)
6. GitHub Models (coding)
7. Mistral (model diversity)
8. TemplateEngine (no-API local fallback)

### Anti-Ban System
- Behavioral mimicry (typing speed, mouse movements, scroll patterns)
- Human schedule (active 10-13, 17-21; sleep 01-08)
- Action budgeting (8 comments/day, 2h gap minimum)
- Fingerprint randomization (canvas, WebGL, viewport, UA)
- Canary account (24h ahead, auto-pause on restriction)

## Data Flow

```
1. Watcher scans groups → keyword matching → score calculation
2. Score > threshold → Archaeologist investigates lead (15 posts, budget, urgency)
3. Warmth Protocol checks group score → determines pitch readiness
4. Ghost Writer generates response using DNA + Archaeology data
5. Shadow Matrix coordinates social proof (primary + vouches)
6. Safety Guard validates action budget → executes via Playwright
7. Response sent → Nurture Loop tracks for follow-up sequence
```
