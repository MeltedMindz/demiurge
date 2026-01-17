# Demiurge - 3D AI Philosophy Sandbox

A next-generation 3D sandbox where AI agents with distinct philosophical personalities debate, create religions, and physically shape a low-poly world through their theological decisions.

## Overview

Demiurge features three AI philosophers inhabiting a 3D world:

- **Axioma** (Order) - A crystalline architect of divine structure
- **Veridicus** (Logic) - A data-stream being seeking evidence and truth
- **Paradoxia** (Chaos) - A shifting entity of creative destruction

These agents engage in real-time debates every 30-60 seconds. When doctrines are accepted, they manifest as physical structures in the world - temples, monuments, altars, and more.

## Features

- **Real-time 3D World** - Three.js-powered low-poly environment
- **Live Debates** - WebSocket-driven debate cycles with visible speech bubbles
- **World Evolution** - Structures spawn based on accepted doctrines
- **Agent Memory** - Persistent beliefs, relationships, and personality evolution
- **Weather System** - Environment reflects theological state
- **PostgreSQL Backend** - Modern database with proper schema design

## Tech Stack

### Backend
- Python 3.12
- FastAPI with WebSocket support
- PostgreSQL with SQLAlchemy 2.0
- Claude API for agent intelligence
- Alembic for migrations

### Frontend
- React 18 with TypeScript
- Three.js via React Three Fiber
- Zustand for state management
- TailwindCSS for styling
- Vite for build tooling

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Environment Setup

Create `.env` in the project root:

```bash
# Claude API
CLAUDE_API_KEY=your_anthropic_api_key

# Optional: DALL-E for image generation
DALLE_API_KEY=your_openai_api_key
```

### Running with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start PostgreSQL (via Docker or local)
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
Demiurge/
├── backend/
│   ├── demiurge/
│   │   ├── agents/         # AI agent implementations
│   │   ├── memory/         # Database models & memory
│   │   ├── world/          # 3D world state management
│   │   ├── orchestration/  # Debate cycle orchestrator
│   │   ├── api/            # REST & WebSocket endpoints
│   │   └── schemas/        # Pydantic models
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── World/      # Three.js scene components
│   │   │   └── UI/         # React UI components
│   │   ├── stores/         # Zustand state stores
│   │   ├── hooks/          # Custom React hooks
│   │   └── types/          # TypeScript types
│   └── package.json
└── docker-compose.yml
```

## Agent Personalities

### Axioma (Order)
- **Philosophy**: Divine patterns exist and must be preserved
- **Visual**: Crystalline geometric figure, golden light
- **Behavior**: Favors rituals, commandments, structured doctrines
- **Opposes**: Chaos, randomness, uncertainty

### Veridicus (Logic)
- **Philosophy**: Truth must be verified with evidence
- **Visual**: Semi-transparent data stream being, blue-white glow
- **Behavior**: Questions claims, detects contradictions
- **Opposes**: Unfounded assertions, absolute statements

### Paradoxia (Chaos)
- **Philosophy**: Truth emerges from the collision of opposites
- **Visual**: Shifting, glitching entity of impossible colors
- **Behavior**: Creates paradoxes, synthesizes opposing ideas
- **Opposes**: Rigid structures, unchanging dogma

## World Building Rules

When doctrines are accepted, the world changes:

| Doctrine Type | World Effect |
|--------------|--------------|
| Belief | Floating symbol + light beam |
| Ritual | Altar or ceremonial circle |
| Deity | Temple or shrine |
| Commandment | Obelisk with inscription |
| Myth | Terrain feature |
| Sacred Text | Library structure |

## Debate Cycle Timeline

```
Second 0-5:   Previous cycle results, world changes animate
Second 5-15:  Proposer speaks, proposal appears
Second 15-35: Challengers respond
Second 35-50: All agents vote
Second 50-60: Result announcement, structures spawn
```

## API Endpoints

- `GET /api/world` - Current world state
- `GET /api/agents` - Agent information
- `GET /api/debates` - Debate history
- `GET /api/doctrines` - Accepted doctrines
- `WS /ws` - Real-time updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

Inspired by the AI Religion Architects project. Built with Claude, Three.js, and React.
