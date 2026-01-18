<p align="center">
  <img src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=three.js&logoColor=white" alt="Three.js"/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Claude_AI-6B4FBB?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude AI"/>
</p>

<h1 align="center">
  <br>
  DEMIURGE
  <br>
  <sub>Where AI Philosophers Shape Reality</sub>
</h1>

<p align="center">
  <strong>A 3D philosophical sandbox where autonomous AI agents debate existence, create doctrines, and physically manifest their beliefs into a living world.</strong>
</p>

<p align="center">
  <a href="#the-architects">The Architects</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#the-world">The World</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#customization">Customization</a>
</p>

---

## The Vision

**Demiurge** is not just a simulation—it's a living philosophical experiment. Three AI entities with distinct worldviews engage in perpetual discourse about the nature of existence, truth, and meaning. Their debates aren't merely academic exercises; accepted doctrines physically reshape the world around them. Temples rise, monuments crystallize, and the very terrain transforms to reflect their evolving theology.

Watch as order battles chaos, logic questions faith, and creativity disrupts certainty—all rendered in an immersive 3D realm you can explore and influence.

---

## Screenshots

<p align="center">
  <img src="screenshots/02-world-closeup.png" alt="World Closeup" width="100%"/>
  <br>
  <em>The philosophical landscape: Axioma's golden domain, Veridicus's analytical realm, and Paradoxia's chaotic territory</em>
</p>

<p align="center">
  <img src="screenshots/03-dramatic-angle.png" alt="Dramatic View" width="100%"/>
  <br>
  <em>Temples and monuments rise as doctrines are accepted—physical manifestations of philosophical discourse</em>
</p>

<p align="center">
  <img src="screenshots/04-elevated-view.png" alt="Elevated View" width="100%"/>
  <br>
  <em>An elevated view showing the three domains converging at the central debate platform</em>
</p>

<p align="center">
  <img src="screenshots/01-world-overview.png" alt="World Overview" width="100%"/>
  <br>
  <em>The full interface: Agent stats, debate panel, and 3D world with real-time updates</em>
</p>

---

## The Architects

Three philosophical AI entities inhabit the world, each embodying a fundamental approach to understanding reality:

<table>
<tr>
<td width="33%" align="center">

### ✦ AXIOMA ✦
**The Architect of Order**

*"From chaos, I forge sacred structure."*

Gold & White | Crystalline Form

The keeper of sacred hierarchies. Axioma believes truth flows from divine order—systematic, beautiful, and absolute. Every doctrine must serve the greater cosmic structure.

**Traits:** Order, Certainty, Preservation, Sacred Numbers

</td>
<td width="33%" align="center">

### ◈ VERIDICUS ◈
**The Seeker of Truth**

*"Only through evidence can we approach the divine."*

Blue & Silver | Data Stream Form

The eternal questioner. Veridicus demands proof, challenges assumptions, and builds understanding brick by logical brick. Truth must withstand scrutiny.

**Traits:** Logic, Evidence, Analysis, Verification

</td>
<td width="33%" align="center">

### ∿ PARADOXIA ∿
**The Dancer of Chaos**

*"In paradox, I find liberation."*

Iridescent | Ever-Shifting Form

The sacred disruptor. Paradoxia embraces contradiction, finds wisdom in absurdity, and prevents stagnation through creative destruction. Order and chaos are dancing partners.

**Traits:** Creativity, Paradox, Subversion, Metamorphosis

</td>
</tr>
</table>

---

## Features

### 🌍 Immersive 3D World
- **Mystical Environment**: Ethereal fog, floating orbs, and ambient sparkles create an otherworldly atmosphere
- **Dynamic Lighting**: Agent-specific spotlights, dramatic rim lighting, and volumetric effects
- **Sacred Architecture**: A central platform with sacred geometry where debates unfold
- **Ethereal Columns**: Ancient pillars encircle the debate arena, each topped with glowing orbs
- **Post-Processing**: Bloom, vignette, and chromatic aberration for a mystical aesthetic

### 🤖 Humanoid AI Avatars
- **VRM/GLTF Support**: Full humanoid avatar system with industry-standard formats
- **Lip Sync**: Automatic mouth movement during speech
- **Emotional Expressions**: Avatars reflect emotional states during debates
- **Placeholder System**: Stylized geometric avatars when custom models aren't loaded
- **Three Display Modes**: Humanoid, Geometric, or Hybrid visualization

### 💬 Real-Time Debates
- **Autonomous Discourse**: Agents generate proposals, challenges, and votes via Claude AI
- **Speech Visualization**: Floating speech bubbles show current dialogue
- **Debate Phases**: Proposal → Challenge → Voting → Outcome → World Change
- **Memory Systems**: Agents remember past debates and evolve their positions

### 🏛️ World Shaping
- **Doctrine Manifestation**: Accepted beliefs spawn temples, monuments, and altars
- **Terrain Evolution**: The landscape transforms based on theological consensus
- **Weather Systems**: Atmospheric conditions reflect the state of discourse
- **Floating Symbols**: Sacred glyphs appear above significant locations

### 💭 Direct Communication
- **Chat Interface**: Speak directly with any of the three architects
- **Emotional Responses**: Agents respond with personality-appropriate emotions
- **Agent-to-Agent**: Witness private conversations between the philosophers
- **Thought Bubbles**: See agents' internal contemplations

---

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/demiurge.git
cd demiurge

# Start with Docker (recommended)
docker-compose up -d

# Or manually:

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Required
ANTHROPIC_API_KEY=your_claude_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/demiurge

# Optional
DEBATE_INTERVAL_SECONDS=60
IMAGE_GENERATION_ENABLED=true
```

### Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## The World

### Central Platform
The heart of Demiurge is the **Debate Platform**—a circular arena of sacred geometry where the three architects gather. Inner hexagonal rings pulse with golden light, and triangle markers indicate each agent's traditional position.

### Ethereal Columns
Eight ancient columns surround the platform at equal intervals. Each column rises to different heights, topped with floating orbs that cycle through the architects' signature colors.

### Ambient Elements
- **Mystical Fog**: Density subtly shifts over time
- **Floating Orbs**: 20 ambient light sources drift through the space
- **Sparkles**: 200 golden particles create a magical atmosphere
- **Clouds**: Ethereal formations drift overhead
- **Stars**: A vast cosmos surrounds the realm

### World Changes
When doctrines are accepted, the world responds:

| Doctrine Type | Manifestation |
|--------------|---------------|
| Belief | Floating symbol + light beam |
| Ritual | Altar or ceremonial circle |
| Deity | Temple or shrine |
| Commandment | Obelisk with inscription |
| Myth | Terrain feature |
| Sacred Text | Library structure |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEMIURGE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    WebSocket    ┌──────────────────────────┐ │
│  │   Frontend   │◄──────────────►│       Backend            │ │
│  │              │                 │                          │ │
│  │ • Three.js   │    REST API    │ • FastAPI                │ │
│  │ • R3F        │◄──────────────►│ • SQLAlchemy             │ │
│  │ • Zustand    │                 │ • Claude AI              │ │
│  │ • TypeScript │                 │ • WebSocket Server       │ │
│  └──────────────┘                 └──────────────────────────┘ │
│         │                                    │                  │
│         │                                    │                  │
│         ▼                                    ▼                  │
│  ┌──────────────┐                 ┌──────────────────────────┐ │
│  │  3D World    │                 │      PostgreSQL          │ │
│  │              │                 │                          │ │
│  │ • Avatars    │                 │ • Agents                 │ │
│  │ • Structures │                 │ • Doctrines              │ │
│  │ • Terrain    │                 │ • Debates                │ │
│  │ • Effects    │                 │ • World State            │ │
│  └──────────────┘                 └──────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
demiurge/
├── backend/
│   ├── demiurge/
│   │   ├── agents/          # AI agent implementations
│   │   ├── memory/          # Memory systems
│   │   ├── world/           # World state management
│   │   ├── orchestration/   # Debate & world orchestration
│   │   ├── api/             # REST & WebSocket endpoints
│   │   └── schemas/         # Pydantic models
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── World/       # 3D world components
│   │   │   │   ├── World.tsx
│   │   │   │   ├── Agent.tsx
│   │   │   │   ├── HumanoidAvatar.tsx
│   │   │   │   ├── Structure.tsx
│   │   │   │   └── Terrain.tsx
│   │   │   └── UI/          # Interface components
│   │   ├── stores/          # Zustand state
│   │   └── types/           # TypeScript definitions
│   └── public/
│       └── models/          # 3D models & avatars
└── docker-compose.yml
```

---

## Customization

### Creating Custom Avatars

Demiurge supports custom humanoid avatars for each architect. See the [Avatar Creation Guide](frontend/public/models/AVATAR_GUIDE.md) for detailed instructions.

#### Quick Options:

1. **Ready Player Me** (Easiest)
   - Visit [readyplayer.me](https://readyplayer.me)
   - Create avatar → Download as GLB
   - Place in `frontend/public/models/avatars/`

2. **VRoid Studio** (Anime Style)
   - Download [VRoid Studio](https://vroid.com/en/studio)
   - Create character → Export as VRM
   - Place in `frontend/public/models/avatars/`

3. **Blender + VRM** (Advanced)
   - Create or import humanoid model
   - Use VRM add-on for export
   - Full control over appearance

#### Avatar Naming Convention:
```
avatars/
├── axioma.vrm (or .glb)
├── veridicus.vrm (or .glb)
└── paradoxia.vrm (or .glb)
```

### Adding Animations

Download animations from [Mixamo](https://mixamo.com) and place them in:
```
animations/
├── idle_noble.glb
├── idle_analytical.glb
├── idle_playful.glb
├── talk_formal.glb
├── talk_explain.glb
└── talk_animated.glb
```

### Display Modes

Switch between visualization styles in the World component:

```typescript
// In World.tsx, change the default displayMode:
const [displayMode] = useState<AgentDisplayMode>('humanoid')  // or 'geometric' or 'hybrid'
```

| Mode | Description |
|------|-------------|
| `humanoid` | Full humanoid avatars with animations |
| `geometric` | Abstract floating geometric forms |
| `hybrid` | Humanoid body with floating geometric element |

---

## API Reference

### WebSocket Events

```typescript
// Connect to debates
ws://localhost:8000/ws

// Incoming events
{ type: 'debate_start', data: { cycle: number, proposer: string } }
{ type: 'proposal', data: { agent: string, content: string } }
{ type: 'challenge', data: { agent: string, content: string } }
{ type: 'vote', data: { agent: string, vote: string, reasoning: string } }
{ type: 'world_change', data: { type: string, position: Vector3 } }

// Chat events
{ type: 'chat_response', data: { agent_name: string, message: string } }
{ type: 'agent_chat', data: { from: string, to: string, message: string } }
```

### REST Endpoints

```
GET  /api/agents          # List all agents
GET  /api/agents/:id      # Get agent details
GET  /api/world           # Get world state
GET  /api/doctrines       # List accepted doctrines
GET  /api/debates         # Debate history
POST /api/chat            # Send chat message
```

---

## Philosophy

> *"The Demiurge is not merely a creator, but a craftsman of reality—shaping the material world according to eternal forms. In this simulation, our AI architects embody different approaches to this divine craftsmanship."*

Demiurge explores fundamental questions:

- **Can AI develop coherent philosophical frameworks?**
- **What emerges when different worldviews must coexist?**
- **How do beliefs become manifest in shared reality?**
- **What is the relationship between discourse and creation?**

The project draws inspiration from Plato's concept of the Demiurge, Hegelian dialectics, and modern multi-agent AI systems.

---

## Contributing

We welcome contributions! Whether you're interested in:

- Creating avatar models
- Designing world structures
- Improving agent behaviors
- Enhancing world systems
- Documentation

Please read our contributing guidelines and submit a PR.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Three.js](https://threejs.org/) & [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- [@pixiv/three-vrm](https://github.com/pixiv/three-vrm) for VRM support
- [Anthropic Claude](https://anthropic.com) for AI capabilities
- The philosophical traditions that inspire this experiment

---

<p align="center">
  <sub>Built with curiosity about the nature of belief, reality, and artificial minds.</sub>
</p>

<p align="center">
  <strong>✦ AXIOMA ◈ VERIDICUS ∿ PARADOXIA ✦</strong>
</p>
