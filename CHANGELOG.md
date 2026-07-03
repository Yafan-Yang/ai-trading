# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-02

### Added
- **Multi-platform skill support** for 70+ AI agents (Claude Code, Codex, Cursor, OpenCode, Cline, Windsurf, etc.)
- **9 comprehensive skills** for stock analysis workflow
  - `analyze` - Complete multi-agent analysis pipeline (~5 min)
  - `quick` - 60-second snapshot (single agent, ~1 min)
  - `market` - Technical analysis (trends, indicators, ~2 min)
  - `fundamentals` - Fundamental analysis (financials, valuation, ~2 min)
  - `news` - News sentiment analysis (~2 min)
  - `sentiment` - Social media sentiment analysis (~2 min)
  - `china` - A-share specific insights (policy, capital flow, ~2 min)
  - `debate` - Bull vs Bear debate (~3 min)
  - `risk-panel` - Three-way risk debate (~3 min)
- **Three installation methods**
  - Claude Code: `bash scripts/install-claude.sh`
  - Codex: `bash scripts/install-codex.sh`
  - Universal: `npx skills add Yafan-Yang/ai-trading`
- **Python data tools** for standalone usage
  - `market_data.py` - Price data + technical indicators
  - `fundamentals.py` - Financial statements + valuation metrics
  - `news_fetch.py` - News aggregation with macro context
  - `verify.py` - Numerical validation with Decimal precision
  - `export_pdf.py` - Research report PDF export
- **skills.sh standard format** (`.agents/skills/`)
- **CI/CD workflow** for auto-sync between skill formats
- **Comprehensive documentation**
  - Installation guide (INSTALL.md)
  - Publication guide (PUBLISH.md)
  - Quick start (QUICKSTART.md)
  - Migration guide (MIGRATION_GUIDE.md)
  - Future optimization roadmap (OPTIMIZATION_PLAN.md)

### Features
- **Zero-cost data sources** - 100% free (akshare for A/H-shares, yfinance for US stocks)
- **Multi-market coverage** - A-share, Hong Kong, US markets
- **Multi-agent debate** - Five parallel analysts + bull/bear debate + risk panel
- **Decimal precision** - All valuation calculations use `decimal.Decimal` to avoid float errors
- **Structured output** - Markdown reports with clear investment recommendations
- **Caching & retry** - Built-in data fetching reliability

### Technical
- Symlink-based installation for efficient disk usage
- Auto-sync script (`scripts/sync-skills.py`) to maintain format consistency
- Support for custom installation directories via `AITRADING_HOME`
- Configurable caching via `AITRADING_CACHE` and `AITRADING_NOCACHE`

## [Unreleased]

### Planned
- Bias detection tool (`bias_check.py`) - 8 quick rejection rules + inverse analysis
- Enhanced report template with tiered recommendations (aggressive/balanced/conservative)
- Information richness rating (A/B/C grade)
- Industry screening skill
- Moat analysis skill  
- Portfolio alert monitoring skill

---

## Version History

- **v1.0.0** (2026-07-02) - Initial public release with multi-platform support
- **v0.1.0** (2026-07-01) - Internal prototype

[1.0.0]: https://github.com/Yafan-Yang/ai-trading/releases/tag/v1.0.0
