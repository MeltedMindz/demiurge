# Demiurge - Claude Code Guidelines

## Project Overview

Demiurge is a 3D AI philosophy sandbox where three AI agents (Axioma, Veridicus, Paradoxia) debate and shape a virtual world through their theological discussions.

## Technology Stack

- **Backend**: Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, WebSocket
- **Frontend**: React 18, TypeScript, Three.js (React Three Fiber), Zustand, TailwindCSS
- **AI**: Claude API for agent intelligence
- **Infrastructure**: Docker Compose

## Directory Structure

```
Demiurge/
├── backend/
│   ├── demiurge/
│   │   ├── agents/           # Agent implementations
│   │   │   ├── base_agent.py # Abstract base class
│   │   │   ├── axioma.py     # Order agent
│   │   │   ├── veridicus.py  # Logic agent
│   │   │   └── paradoxia.py  # Chaos agent
│   │   ├── memory/           # Database layer
│   │   │   ├── database.py   # SQLAlchemy setup
│   │   │   └── models.py     # Database models
│   │   ├── world/            # World state
│   │   │   └── world_state.py
│   │   ├── orchestration/    # Debate system
│   │   │   ├── claude_client.py
│   │   │   └── debate_orchestrator.py
│   │   ├── api/              # HTTP/WS endpoints
│   │   │   ├── routes.py
│   │   │   └── websocket.py
│   │   ├── schemas/          # Pydantic models
│   │   └── config.py         # Settings
│   └── main.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── World/        # 3D components
│       │   └── UI/           # Interface
│       ├── stores/           # Zustand
│       ├── hooks/            # Custom hooks
│       └── types/            # TypeScript
└── docker-compose.yml
```

## Key Components

### Backend

**Agents** (`backend/demiurge/agents/`)
- `BaseAgent`: Abstract class defining proposal/challenge/vote interface
- `Axioma`: Order-focused agent, favors structure and rituals
- `Veridicus`: Logic-focused agent, demands evidence
- `Paradoxia`: Chaos-focused agent, creates paradoxes

**Orchestrator** (`backend/demiurge/orchestration/debate_orchestrator.py`)
- Manages 60-second debate cycles
- Coordinates proposal → challenge → vote → result flow
- Broadcasts updates via WebSocket

**World State** (`backend/demiurge/world/world_state.py`)
- Manages 3D structure placement
- Handles weather and effects
- Provides spatial queries

### Frontend

**World Components** (`frontend/src/components/World/`)
- `World.tsx`: Main Three.js scene
- `Agent.tsx`: Agent avatars with speech bubbles
- `Structure.tsx`: World structures (temples, altars, etc.)
- `Terrain.tsx`: Ground and zone markers

**State Management** (`frontend/src/stores/`)
- `worldStore.ts`: Zustand store for world state
- Handles agents, structures, debate state

**WebSocket Hook** (`frontend/src/hooks/useWebSocket.ts`)
- Connects to backend WebSocket
- Handles all real-time message types

## Database Schema

Key tables:
- `agents` - Agent identity and 3D state
- `agent_personality` - Dynamic traits (JSONB)
- `agent_beliefs` - Individual beliefs
- `debates` - Full debate history
- `doctrines` - Accepted beliefs
- `world_structures` - 3D structures
- `world_effects` - Visual effects

## Development Workflow

### Running Locally

```bash
# Start database
docker-compose up -d postgres

# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Adding New Features

1. **New Agent Behavior**: Modify agent classes in `backend/demiurge/agents/`
2. **New Structure Type**: Update `STRUCTURE_TEMPLATES` in world_state.py and Structure.tsx
3. **New API Endpoint**: Add to `backend/demiurge/api/routes.py`
4. **New WebSocket Event**: Update websocket.py and useWebSocket.ts

## Configuration

Environment variables (`.env`):
- `CLAUDE_API_KEY` - Required for agent intelligence
- `DALLE_API_KEY` - Optional for image generation
- `DATABASE_URL` - PostgreSQL connection string

Settings are in `backend/demiurge/config.py`:
- `cycle_duration_seconds` - Debate cycle length (default 60)
- `proposal_phase_seconds` - Time for proposals (default 15)
- etc.

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend type check
cd frontend
npm run typecheck
```

## Common Tasks

### Adjusting Agent Behavior
Edit personality traits in agent `_init_traits()` methods and `get_proposal_weights()` for proposal preferences.

### Changing Debate Timing
Modify settings in `config.py`:
- `cycle_duration_seconds`
- `proposal_phase_seconds`
- `challenge_phase_seconds`
- etc.

### Adding New Structure Types
1. Add entry to `STRUCTURE_TEMPLATES` in world_state.py
2. Add geometry case in Structure.tsx
3. Map proposal type to structure in orchestrator

## Architecture Decisions

1. **PostgreSQL over SQLite** - Better JSONB support, scaling, concurrent access
2. **WebSocket for real-time** - Lower latency than polling
3. **React Three Fiber** - Declarative 3D with React patterns
4. **Zustand** - Simple state without Redux boilerplate
5. **TailwindCSS** - Rapid UI development
