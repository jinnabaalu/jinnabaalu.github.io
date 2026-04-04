# Jinna Balu Profile Page

Personal website and profile site built with Jekyll.

## GitHub Repository Snapshot Sync

Syncs GitHub repository data from `jinnabaalu` and `VibhuviOiO` into [_data/github.yml](_data/github.yml). Forks are excluded and repos are ranked by stars.

Local refresh:

```bash
python3 scripts/sync_github_data.py
```

With token:

```bash
GITHUB_TOKEN=your_token_here python3 scripts/sync_github_data.py
```

Weekly auto-sync runs from [.github/workflows/refresh-github-data.yml](.github/workflows/refresh-github-data.yml) every Sunday at `02:00 UTC`, and commits + pushes changes automatically if [_data/github.yml](_data/github.yml) changed.

## Stack Overflow Snapshot Sync

Stack Overflow data is stored in [_data/stackoverflow.yml](_data/stackoverflow.yml).

```bash
python3 scripts/sync_stackoverflow_data.py
```

Weekly auto-sync runs from [.github/workflows/refresh-github-data.yml](.github/workflows/refresh-github-data.yml).

## Medium Snapshot Sync

Medium content is stored in [medium-rss.xml](medium-rss.xml) and [_data/external-articles.yml](_data/external-articles.yml).

```bash
python3 scripts/sync_medium_data.py
```

Weekly auto-sync runs from [.github/workflows/refresh-github-data.yml](.github/workflows/refresh-github-data.yml).

Need help in building the profile page [Connect with me on LinkedIN](https://www.linkedin.com/in/jinnabaalu/)
