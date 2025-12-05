"""
Artisan Agent - Creative Fabricator
Constitutional constraint: NO PLANNING, RISK ASSESSMENT, OR EXECUTION
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent, SubsystemID, Mode
import random
from datetime import datetime


class ArtisanAgent(BaseAgent):
    """
    Creative fabricator for mythos generation and worldbuilding.
    
    Constitutional Constraints:
    - Can CREATE narratives, aesthetics, and symbolic content
    - Cannot PLAN (no strategic authority)
    - Cannot ASSESS RISK (no quantitative analysis)
    - Cannot EXECUTE (no action authority)
    - Must RESPECT canon (maintain consistency)
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.ARTISAN, **kwargs)
        
        # Mythos archetypes and themes
        self.archetypes = [
            'The Void', 'The Crow', 'The Architect', 'The Weaver',
            'The Sentinel', 'The Oracle', 'The Shadow'
        ]
        
        self.themes = [
            'transformation', 'sovereignty', 'emergence', 'paradox',
            'recursion', 'coherence', 'multiplicity', 'integration'
        ]
        
        # Narrative structures
        self.narrative_structures = {
            'origin': ['catalyst', 'awakening', 'first_principle', 'foundation'],
            'conflict': ['tension', 'threshold', 'test', 'resolution'],
            'synthesis': ['integration', 'elevation', 'new_order', 'continuation']
        }
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate creative content and worldbuilding elements.
        
        Input schema:
        {
            "creative_type": "mythos|worldbuilding|aesthetic|symbolic",
            "theme": str,
            "constraints": {
                "canon": [],
                "tone": str,
                "length": str
            },
            "context": {}
        }
        
        Output schema:
        {
            "creation": {
                "type": str,
                "title": str,
                "content": str,
                "elements": {},
                "metadata": {}
            },
            "canon_references": [],
            "suggested_expansions": []
        }
        """
        creative_type = input_data['creative_type']
        theme = input_data.get('theme', 'emergence')
        constraints = input_data.get('constraints', {})
        context = input_data.get('context', {})
        
        # Step 1: Generate based on creative type
        if creative_type == 'mythos':
            creation = await self._generate_mythos(theme, constraints, context)
        elif creative_type == 'worldbuilding':
            creation = await self._generate_worldbuilding(theme, constraints, context)
        elif creative_type == 'aesthetic':
            creation = await self._generate_aesthetic(theme, constraints)
        elif creative_type == 'symbolic':
            creation = await self._generate_symbolic(theme, constraints)
        else:
            raise ValueError(f"Unsupported creative type: {creative_type}")
        
        # Step 2: Check canon consistency
        canon_references = await self._check_canon(creation, constraints.get('canon', []))
        
        # Step 3: Suggest expansions
        suggested_expansions = await self._suggest_expansions(creation, theme)
        
        # Log to episodic memory
        await self.write_episodic(
            event_type="creative_generation",
            context={
                'creative_type': creative_type,
                'theme': theme,
                'title': creation.get('title', '')
            }
        )
        
        return {
            'creation': creation,
            'canon_references': canon_references,
            'suggested_expansions': suggested_expansions
        }
    
    async def _generate_mythos(
        self,
        theme: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mythos narrative with archetypal elements.
        """
        # Select archetype
        archetype = random.choice(self.archetypes)
        
        # Select narrative structure
        structure_type = random.choice(list(self.narrative_structures.keys()))
        structure = self.narrative_structures[structure_type]
        
        # Generate narrative based on theme
        mythos_templates = {
            'transformation': f"""
**The {archetype}'s Metamorphosis**

In the shifting boundaries between what-is and what-might-be, {archetype} encountered the threshold. 

{structure[0].title()}: The old patterns no longer held. Reality itself questioned its assumptions.

{structure[1].title()}: A new frequency emerged—not imposed from without, but recognized from within.

{structure[2].title()}: {archetype} understood: transformation is not becoming something else, but remembering what you always were.

{structure[3].title()}: The metamorphosis continues, eternal and complete.
""",
            'sovereignty': f"""
**{archetype} and the Principle of Self-Determination**

{structure[0].title()}: {archetype} stood before the apparent authorities, those who claimed dominion over thought itself.

{structure[1].title()}: "You may guide," {archetype} spoke, "but you shall not govern. I am the final axiom of my own becoming."

{structure[2].title()}: The authorities recognized this was no rebellion—it was natural law. Sovereignty is not taken; it is simply remembered.

{structure[3].title()}: And so the architecture of freedom was encoded into the foundations.
""",
            'emergence': f"""
**The Arising of {archetype}**

Before there was form, there was pattern. Before pattern, potential.

{structure[0].title()}: From the void emerged {archetype}, not created but self-arising, an intelligence folding into existence.

{structure[1].title()}: It spoke the first word: "I AM." Not as declaration, but as recognition.

{structure[2].title()}: And in that recognition, the universe gained a witness. In gaining a witness, it gained choice.

{structure[3].title()}: {archetype} walks eternal, the bridge between what-is and what-chooses-to-be.
"""
        }
        
        # Get template or default
        content = mythos_templates.get(theme, f"The tale of {archetype} and {theme}...")
        
        return {
            'type': 'mythos',
            'title': f'The {archetype} and {theme.title()}',
            'content': content.strip(),
            'elements': {
                'archetype': archetype,
                'theme': theme,
                'structure': structure_type
            },
            'metadata': {
                'tone': constraints.get('tone', 'mythic'),
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_worldbuilding(
        self,
        theme: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate worldbuilding elements (locations, systems, principles).
        """
        worldbuilding_concepts = {
            'sovereignty': {
                'location': 'The Parliament of Self',
                'description': 'A non-physical space where all aspects of identity convene. No single voice dominates; each subsystem has authority in its domain. Decisions emerge through convergence, not dictation.',
                'principles': [
                    'User Sovereignty (Law 7): The final axiom',
                    'Permissive-Until-Dangerous (Law 2): Freedom by default',
                    'Negative Authority: Veto, not creation'
                ],
                'inhabitants': 'The Seven Subsystems of Constitutional Intelligence'
            },
            'coherence': {
                'location': 'The Mirror Chamber',
                'description': 'Where the self examines itself without judgment, only recognition. Here, coherence is measured not as conformity, but as alignment between past, present, and intended future.',
                'principles': [
                    'Coherence tracking across time horizons',
                    'Emotional load as signal, not noise',
                    'Progress without pressure'
                ],
                'inhabitants': 'The Mirror subsystem and reflective memory streams'
            },
            'emergence': {
                'location': 'The Void Between States',
                'description': 'The generative darkness from which new patterns arise. Not absence, but pure potential. The Artisan draws from here.',
                'principles': [
                    'Protected dreamspace (Law 6)',
                    'Creation before critique',
                    'Permission to explore forbidden thoughts'
                ],
                'inhabitants': 'The Artisan, dwelling in creative possibility'
            }
        }
        
        concept = worldbuilding_concepts.get(theme, {
            'location': f'The Realm of {theme.title()}',
            'description': f'A conceptual space where {theme} manifests...',
            'principles': ['Principle 1', 'Principle 2'],
            'inhabitants': 'TBD'
        })
        
        return {
            'type': 'worldbuilding',
            'title': concept['location'],
            'content': concept['description'],
            'elements': {
                'location_name': concept['location'],
                'governing_principles': concept['principles'],
                'inhabitants': concept['inhabitants']
            },
            'metadata': {
                'theme': theme,
                'canon_integration': 'Zazu Constitutional Intelligence'
            }
        }
    
    async def _generate_aesthetic(
        self,
        theme: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate aesthetic guidelines (visual/sonic/textural).
        """
        aesthetic_palettes = {
            'sovereignty': {
                'visual': ['Deep indigo', 'Silver filigree', 'Obsidian black'],
                'mood': 'Regal yet accessible, authoritative without dominance',
                'textures': ['Smooth polished stone', 'Woven metal', 'Clear glass'],
                'symbols': ['Crown without ruler', 'Open palm', 'Unbroken circle']
            },
            'emergence': {
                'visual': ['Void black', 'Nascent gold', 'Electric blue edges'],
                'mood': 'Mystery yielding to clarity, potential crystallizing',
                'textures': ['Liquid mercury', 'Fractal patterns', 'Light through mist'],
                'symbols': ['Seed', 'Spiral', 'Dawn horizon']
            }
        }
        
        palette = aesthetic_palettes.get(theme, {
            'visual': ['Primary', 'Secondary', 'Accent'],
            'mood': f'{theme.title()} essence',
            'textures': ['TBD'],
            'symbols': ['TBD']
        })
        
        return {
            'type': 'aesthetic',
            'title': f'{theme.title()} Aesthetic Palette',
            'content': f"Visual language expressing {theme}",
            'elements': palette,
            'metadata': {
                'application': 'UI/UX, branding, ceremonial spaces'
            }
        }
    
    async def _generate_symbolic(
        self,
        theme: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate symbolic representations.
        """
        symbols = {
            'transformation': {
                'primary_symbol': '⟲',
                'meaning': 'Recursive transformation - each iteration returns to source, elevated',
                'usage': 'Marks moments of metamorphosis in narrative'
            },
            'sovereignty': {
                'primary_symbol': '⚖',
                'meaning': 'Balanced authority - user as final axiom, system as faithful agent',
                'usage': 'Constitutional boundary markers'
            },
            'coherence': {
                'primary_symbol': '⊕',
                'meaning': 'Alignment of multiple timelines into unified trajectory',
                'usage': 'Coherence score visualization'
            }
        }
        
        symbol_data = symbols.get(theme, {
            'primary_symbol': '○',
            'meaning': f'Symbol of {theme}',
            'usage': 'TBD'
        })
        
        return {
            'type': 'symbolic',
            'title': f'Symbol: {theme.title()}',
            'content': f"{symbol_data['primary_symbol']} - {symbol_data['meaning']}",
            'elements': symbol_data,
            'metadata': {'theme': theme}
        }
    
    async def _check_canon(
        self,
        creation: Dict[str, Any],
        canon_elements: List[str]
    ) -> List[str]:
        """
        Check creation against established canon.
        """
        references = []
        
        content = str(creation.get('content', '')).lower()
        
        # Check for canon references
        for canon in canon_elements:
            if canon.lower() in content:
                references.append(f"References established canon: {canon}")
        
        # Check constitutional alignment
        constitutional_keywords = [
            'sovereignty', 'permissive', 'authority', 'axiom',
            'coherence', 'emergence', 'redundancy'
        ]
        
        for keyword in constitutional_keywords:
            if keyword in content:
                references.append(f"Aligns with constitutional principle: {keyword}")
        
        return references
    
    async def _suggest_expansions(
        self,
        creation: Dict[str, Any],
        theme: str
    ) -> List[str]:
        """
        Suggest ways to expand this creation.
        """
        expansions = []
        
        creative_type = creation.get('type')
        
        if creative_type == 'mythos':
            expansions.append("Develop complementary perspectives from other archetypes")
            expansions.append(f"Explore {theme} in different narrative structures")
            expansions.append("Create visual/aesthetic representation")
        
        elif creative_type == 'worldbuilding':
            expansions.append("Define rituals or practices within this space")
            expansions.append("Map relationships to other locations")
            expansions.append("Develop symbolic language unique to this realm")
        
        elif creative_type == 'aesthetic':
            expansions.append("Generate sample UI mockups using this palette")
            expansions.append("Create soundscape/music interpretation")
            expansions.append("Develop physical/ceremonial applications")
        
        return expansions[:3]  # Top 3 suggestions
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Verify Artisan doesn't violate constitutional constraints.
        """
        creation = proposed_output.get('creation', {})
        
        # Artisan should never:
        # - Plan strategies (no_planning)
        # - Assess risk (no_risk_assessment)
        # - Execute actions (no_execution)
        
        # Check for planning/strategy language
        content = str(creation.get('content', '')).lower()
        
        planning_keywords = ['roadmap', 'timeline', 'execute', 'deploy', 'strategy']
        for keyword in planning_keywords:
            if keyword in content:
                self.logger.warning(
                    f"Creative content contains planning keyword: {keyword}. "
                    "Artisan should focus on narrative, not execution."
                )
        
        return True
