<div align="center">
  <img src="assets/logo.svg" alt="MIRROR Logo" width="200"/>
  <h1 align="center">MIRROR</h1>
  <p align="center">
    <strong>Autonomous Client Hunting Organism</strong>
    <br />
    A self-sustaining AI agent that operates 24/7 on Facebook Groups
    <br />
    to identify, engage, and convert potential clients — automatically.
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python" alt="Python 3.11+"/>
    <img src="https://img.shields.io/badge/license-Internal-red?style=flat-square" alt="License"/>
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform"/>
    <img src="https://img.shields.io/badge/RAM-2GB%20(min)-brightgreen?style=flat-square" alt="RAM"/>
    <img src="https://img.shields.io/badge/status-stable-brightgreen?style=flat-square" alt="Status"/>
  </p>
</div>

---

## Overview

**MIRROR** is a fully autonomous digital employee built for Facebook Groups client acquisition. Unlike conventional bots that spam generic pitches, MIRROR:

- 🧬 **Clones your writing DNA** — responds in your exact tone, vocabulary, and Banglish style
- 🕵️ **Archaeologists every lead** — analyzes 15+ posts before making contact
- 👥 **Operates a 3-account social proof matrix** — builds credibility naturally
- 🌡️ **Practices warmth-first infiltration** — 14-day authority building before pitching
- 🛡️ **Survives 6+ months** — advanced anti-ban system with behavioral mimicry

## Architecture

```
mirror/
├── core/              # Brain, scheduler, state machine, memory
├── modules/           # 10 feature modules (DNA, Watcher, Writer, etc.)
├── api_plugins/       # 7 free API providers + template fallback
├── config/            # Policy, safety rules, groups, secrets
├── templates/         # Response templates (web, app, nurture)
├── war_room/          # Telegram bot control center
├── utils/             # Humanizer, fingerprint, spintax, logger
├── portfolio/         # Project showcase data
└── database/          # SQLite storage
```

## Features

| Module | Function |
|--------|----------|
| **DNA Cloner** | Extracts your writing style from Facebook history |
| **Archaeologist** | Deep-dive lead intelligence (15 posts, budget, urgency) |
| **Watcher** | Monitors 50+ Facebook groups for client opportunities |
| **Ghost Writer** | AI response generation matching your exact style |
| **Shadow Matrix** | 3-account system for organic social proof |
| **Warmth Protocol** | 14-day authority-building → natural pitch |
| **Nurture Loop** | 30-day re-engagement sequence for cold leads |
| **Competitor Radar** | Real-time competitor intelligence |
| **Portfolio Sniping** | Lead-specific auto-generated showcases |
| **Safety Guard** | Anti-ban with canary account & behavioral mimicry |
| **War Room** | Telegram dashboard with full control |

## Quick Start

### Prerequisites

- Python 3.11+
- 2GB RAM (4GB recommended)
- Windows / Linux

### Installation

```bash
# Clone the repo
git clone https://github.com/Sarkar009765/MIRRO.git
cd MIRRO

# Install dependencies
pip install -r mirror/requirements.txt
python -m playwright install chromium

# Run setup wizard
python mirror/setup.py
```

### Configuration

```bash
# 1. Add your API keys
# Edit: mirror/config/secrets.env

# 2. (Optional) Clone your writing DNA
cd mirror
python cli.py --clone-me

# 3. Start the agent
python main.py
```

## Telegram Commands

Once running, control MIRROR via Telegram:

| Command | Description |
|---------|------------|
| `/status` | Full system health report |
| `/leads` | Today's hot leads |
| `/approve [id]` | Approve lead response |
| `/reject [id]` | Skip lead |
| `/autopilot on` | Auto-approve high-confidence leads |
| `/pause [hours]` | Pause all activity |
| `/resume` | Resume activity |
| `/quota` | API usage status |
| `/shadows` | Account health check |
| `/warmth` | Group infiltration scores |
| `/report` | Daily performance summary |

## Free API Stack

| Provider | Free Tier | Role |
|----------|-----------|------|
| Google Gemini | 1,500 req/day | Primary |
| Groq | 1K-14.4K req/day | Fallback |
| Cerebras | 1M tokens/day | Heavy tasks |
| OpenRouter | 50 req/day | Emergency |
| Cloudflare AI | 10K neurons/day | Edge |
| GitHub Models | 50 chat/mo | Coding |
| Mistral | 1B tokens/mo | Diversity |
| Template Engine | Unlimited | No-API fallback |

## Performance Targets

| Day | Activity |
|-----|----------|
| 1-7 | Warmth Protocol (0 pitches, authority building) |
| 8-14 | Soft engagement (5-10 interactions/day) |
| 15-21 | First pitches (2-5/day, 10-20% response) |
| 22-30 | Full operation (5-8 pitches/day) |
| 90-Day | 1,500+ leads, 30+ calls, 5-10 projects |

## License

Internal — Agency Use Only

---

<p align="center">
  <sub>Built with ❤️ for autonomous client acquisition</sub>
</p>
