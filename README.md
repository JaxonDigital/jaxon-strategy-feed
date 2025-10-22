# Jaxon Strategy Feed

Podcast RSS feed for Jaxon Digital Project Pivot strategy documents.

## Subscribe

Add this URL to your podcast app:

```
https://jaxondigital.github.io/jaxon-strategy-feed/feed.rss
```

## About

Project Pivot is Jaxon Digital's strategic transformation from an Optimizely services company to an AI Operations Platform SaaS company. This podcast feed contains audio versions of key strategy documents, including:

- Platform vision and strategy
- AI agent catalog (17+ agents)
- Product roadmaps
- Partnership materials
- Operational playbooks

## Episodes

Each episode is an audio version of a strategic planning document:

- **Platform Vision** - Complete platform strategy with 3-layer approach and optionality play
- **AI Agent Catalog** - Comprehensive catalog of all 17+ AI agents for Optimizely operations
- **SaaS Platform Roadmap** - 6-month transformation plan from operator-driven to self-service SaaS
- **Operator Platform Specification** - Technical specification for the operator-driven phase
- **AI-First Playbook** - Operational playbook for AI-first development approach
- **Week 1 Execution Plan** - First week strategic execution plan and priorities
- **Optimizely Leadership Pitch** - Partnership pitch for Optimizely leadership demo

## Workflow

This feed is automatically generated and hosted via GitHub Pages:

1. Strategy documents are written in Markdown
2. Audio files are generated using OpenAI TTS API
3. MP3 files are uploaded to Google Drive
4. RSS feed is generated with Google Drive URLs
5. Feed is committed to GitHub and served via GitHub Pages
6. Podcast apps auto-detect new episodes

## Listen On

Compatible with all podcast apps:
- Apple Podcasts
- Overcast
- Pocket Casts
- Spotify (via RSS)
- Castro
- Any app that supports RSS feeds

## Maintenance

To add new episodes:

```bash
# 1. Generate audio from new markdown documents
cd /Users/bgerby/Documents/dev/pivot
python3 sprint-0/generate-strategy-audio.py

# 2. Upload to Google Drive and generate RSS
cd /Users/bgerby/Documents/dev/ai/jaxon-strategy-feed
python3 sync-audio-to-drive.py
python3 generate-feed.py

# 3. Commit and push to GitHub
git add .
git commit -m "Add new strategy episode: [title]"
git push origin main
```

Podcast apps will automatically detect and download new episodes.

---

**Project:** Jaxon Digital Project Pivot
**Contact:** brian@jaxondigital.com
**Repository:** https://github.com/JaxonDigital/jaxon-strategy-feed
