# MWIS Agent

## Environment setup

To activate virtual environment:
```bash
source .venv/bin/activate
```

To test activation:
```bash
python3 .agents/skills/mwis-website/identify_forecast_area/scripts/query_region.py 'NH 123 123'
```

To deactivate virtual environment:
```bash
deactivate
```

## Project structure
```bash
mwis-agent/
├── .venv/                  # Virtual environment
├── .claude/                # Claude-specific files
│   ├── skills/
│   │   └── get-forecast/
│   │       ├── SKILL.md
│   │       └── assets/
│   │           └── template.md
│   └── tools/
│       └── query_region.py
├── scripts/                # Utility scripts
│   └── query_region.py
├── assets/                 # Assets
│   └── template.md
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── Dockerfile              # Docker configuration

```
