# Avatar Creation Guide for Demiurge

This guide explains how to create human-like 3D avatars for the three philosophical agents.

## Quick Start Options

### Option 1: Ready Player Me (Easiest - Realistic Humans)

1. Go to [Ready Player Me](https://readyplayer.me/)
2. Create an avatar using their web tool
3. Download as GLB format
4. Rename and place in `avatars/` folder:
   - `axioma.glb` - For the Order/Structure agent
   - `veridicus.glb` - For the Logic/Evidence agent
   - `paradoxia.glb` - For the Chaos/Creativity agent

**Recommended Styles:**
- **Axioma**: Regal, composed, wise appearance. Gold/white tones. Think philosopher king.
- **Veridicus**: Analytical, precise, scholarly. Blue/silver tones. Think scientist/professor.
- **Paradoxia**: Dynamic, creative, unpredictable. Rainbow/iridescent. Think trickster/artist.

### Option 2: VRoid Studio (Free - Anime Style)

1. Download [VRoid Studio](https://vroid.com/en/studio) (free)
2. Create your character using the intuitive interface
3. Export as VRM format
4. Place in `avatars/` folder:
   - `axioma.vrm`
   - `veridicus.vrm`
   - `paradoxia.vrm`

### Option 3: Blender + VRM Add-on (Advanced - Full Custom)

1. Install [VRM Add-on for Blender](https://vrm-addon-for-blender.info/en/)
2. Create or import humanoid character
3. Set up VRM humanoid bone mapping
4. Export as VRM
5. Place in `avatars/` folder

## Adding Animations

### From Mixamo (Free)

1. Go to [Mixamo](https://www.mixamo.com/)
2. Upload your character or use a built-in one
3. Browse and select animations:
   - **Idle**: Standing idle, breathing idle
   - **Talking**: Talking gestures, explaining
   - **Gestures**: Thinking, pointing, celebrating, nodding
4. Download as FBX
5. Import to Blender, export as GLB
6. Place in `animations/` folder

### Recommended Animations per Agent

**Axioma (Order):**
- `idle_noble.glb` - Dignified standing pose
- `talk_formal.glb` - Measured, deliberate speaking
- `gesture_approval.glb` - Nodding, agreeing
- `gesture_think.glb` - Contemplative pose

**Veridicus (Logic):**
- `idle_analytical.glb` - Attentive, observing stance
- `talk_explain.glb` - Explaining with hand gestures
- `gesture_question.glb` - Curious, questioning pose
- `gesture_eureka.glb` - Discovery moment

**Paradoxia (Chaos):**
- `idle_playful.glb` - Relaxed, slightly mischievous
- `talk_animated.glb` - Energetic, expressive speaking
- `gesture_celebrate.glb` - Excited celebration
- `gesture_magic.glb` - Mysterious hand waves

## File Structure

```
public/models/
├── avatars/
│   ├── axioma.vrm (or .glb)
│   ├── veridicus.vrm (or .glb)
│   └── paradoxia.vrm (or .glb)
├── animations/
│   ├── idle_noble.glb
│   ├── idle_analytical.glb
│   ├── idle_playful.glb
│   ├── talk_formal.glb
│   ├── talk_explain.glb
│   ├── talk_animated.glb
│   └── ... (other animations)
└── AVATAR_GUIDE.md (this file)
```

## Technical Requirements

- **Format**: VRM (preferred) or GLB/GLTF
- **Polygon Count**: Under 50k triangles for performance
- **Texture Size**: Max 2048x2048 per texture
- **Skeleton**: VRM humanoid or Mixamo-compatible rig
- **Scale**: 1 unit = 1 meter (average human ~1.7 units tall)

## Placeholder Behavior

If avatar files are not found, the system will render stylized placeholder avatars:
- Capsule body with spherical head
- Agent-specific colors (gold, blue, magenta)
- Basic talking animation (head movement)
- Eye glow effects

This allows the system to run without custom models while still being visually distinctive.

## Tips for Best Results

1. **Keep file sizes reasonable** - Under 10MB per avatar for fast loading
2. **Test in VRM viewer** - Use [three-vrm viewer](https://pixiv.github.io/three-vrm/packages/three-vrm/examples/) to preview
3. **Match the theme** - Agents should feel like philosophers/mystics, not generic game characters
4. **Consider expressions** - VRM supports blend shapes for facial expressions

## Resources

- [Ready Player Me](https://readyplayer.me/) - Free realistic avatars
- [VRoid Studio](https://vroid.com/en/studio) - Free anime-style avatar creator
- [Mixamo](https://www.mixamo.com/) - Free animations
- [VRM Add-on for Blender](https://vrm-addon-for-blender.info/en/) - Custom VRM creation
- [three-vrm](https://github.com/pixiv/three-vrm) - VRM loader documentation
