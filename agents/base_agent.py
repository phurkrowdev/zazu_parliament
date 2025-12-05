"""
Base Agent Template for Zazu Constitutional Parliament
Abstract class defining core agent behavior with constitutional compliance
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import logging
from datetime import datetime
import asyncio

import redis.asyncio as redis
import psycopg
from sentence_transformers import SentenceTransformer


class SubsystemID(Enum):
    """Enumeration of all subsystem identifiers"""
    INTERPRETER = "interpreter"
    STRATEGIST = "strategist"
    ARTISAN = "artisan"
    LEDGER = "ledger"
    SENTINEL = "sentinel"
    EXECUTOR = "executor"
    MIRROR = "mirror"


class Mode(Enum):
    """Global system modes"""
    INQUIRY = "inquiry"
    CREATION = "creation"
    EXECUTION = "execution"


class BaseAgent(ABC):
    """
    Abstract base class for all Zazu subsystem agents.
    
    Implements constitutional compliance, memory interfaces, and inter-agent messaging.
    Subclasses must implement _process_input() for subsystem-specific logic.
    """
    
    def __init__(
        self,
        subsystem_id: SubsystemID,
        constitution_path: str = "core/constitution.json",
        redis_url: str = "redis://localhost:6379",
        postgres_dsn: str = "postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    ):
        self.subsystem_id = subsystem_id
        self.logger = logging.getLogger(f"zazu.{subsystem_id.value}")
        
        # Store connection strings for async initialization
        self.redis_url = redis_url
        self.postgres_dsn = postgres_dsn
        
        # Load constitutional constraints
        with open(constitution_path, 'r') as f:
            self.constitution = json.load(f)
        
        self.subsystem_config = self.constitution['subsystems'][subsystem_id.value]
        self.authorities = set(self.subsystem_config['authorities'])
        self.constraints = set(self.subsystem_config['constraints'])
        
        # Initialize connections (to be established in async init)
        self.redis: Optional[redis.Redis] = None
        self.postgres: Optional[psycopg.AsyncConnection] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        
        # Runtime state
        self.current_mode: Optional[Mode] = None
        self.active = False
        
        self.logger.info(f"Initialized {subsystem_id.value} agent")
    
    async def initialize(self):
        """Async initialization of connections"""
        self.redis = await redis.from_url(self.redis_url)
        self.postgres = await psycopg.AsyncConnection.connect(self.postgres_dsn)
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.active = True
        self.logger.info(f"{self.subsystem_id.value} connections established")
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.active = False
        if self.redis:
            await self.redis.close()
        if self.postgres:
            await self.postgres.close()
        self.logger.info(f"{self.subsystem_id.value} shutdown complete")
    
    # ==================== CONSTITUTIONAL COMPLIANCE ====================
    
    def _validate_action(self, action: str) -> bool:
        """
        Validate that an action is within this subsystem's authorities.
        Enforces constitutional constraints at runtime.
        """
        if action in self.authorities:
            return True
        
        # Log violation
        self.logger.error(
            f"Constitutional violation: {self.subsystem_id.value} attempted "
            f"unauthorized action '{action}'"
        )
        return False
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Check if proposed output violates subsystem constraints.
        Returns True if compliant, False if violation detected.
        """
        # Subsystem-specific constraint validation
        # Override in subclasses for custom checks
        return True
    
    async def _log_violation(
        self,
        violation_type: str,
        severity: str,
        description: str,
        context: Optional[Dict] = None
    ):
        """Log constitutional violation to database"""
        async with self.postgres.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO constitutional_violations 
                (subsystem_id, violation_type, severity, description, context)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    self.subsystem_id.value,
                    violation_type,
                    severity,
                    description,
                    json.dumps(context) if context else None
                )
            )
            await self.postgres.commit()
    
    # ==================== MEMORY INTERFACES ====================
    
    async def write_episodic(
        self,
        event_type: str,
        context: Dict[str, Any],
        related_event_id: Optional[int] = None
    ) -> int:
        """Write event to episodic memory, returns event ID"""
        async with self.postgres.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO episodic_memory (subsystem_id, event_type, mode, context, related_event_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    self.subsystem_id.value,
                    event_type,
                    self.current_mode.value if self.current_mode else None,
                    json.dumps(context),
                    related_event_id
                )
            )
            event_id = (await cur.fetchone())[0]
            await self.postgres.commit()
            return event_id
    
    async def query_semantic(
        self,
        query_text: str,
        node_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Query semantic memory via vector similarity"""
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        async with self.postgres.cursor() as cur:
            if node_type:
                await cur.execute(
                    """
                    SELECT node_id, node_type, properties,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM semantic_memory
                    WHERE node_type = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, node_type, query_embedding, limit)
                )
            else:
                await cur.execute(
                    """
                    SELECT node_id, node_type, properties,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM semantic_memory
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, query_embedding, limit)
                )
            
            results = []
            async for row in cur:
                results.append({
                    'node_id': row[0],
                    'node_type': row[1],
                    'properties': row[2],
                    'similarity': float(row[3])
                })
            return results
    
    async def store_semantic(
        self,
        node_id: str,
        node_type: str,
        properties: Dict[str, Any],
        text_for_embedding: str
    ):
        """Store knowledge node in semantic memory"""
        embedding = self.embedding_model.encode(text_for_embedding).tolist()
        
        async with self.postgres.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO semantic_memory (node_id, node_type, properties, embedding)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (node_id) DO UPDATE
                SET properties = EXCLUDED.properties,
                    embedding = EXCLUDED.embedding,
                    updated_at = NOW()
                """,
                (node_id, node_type, json.dumps(properties), embedding)
            )
            await self.postgres.commit()
    
    async def retrieve_procedural(self, workflow_id: str) -> Optional[Dict]:
        """Retrieve workflow template from Redis"""
        workflow_json = await self.redis.get(f"procedural:{workflow_id}")
        return json.loads(workflow_json) if workflow_json else None
    
    async def log_reflective(
        self,
        log_type: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Log to Loki for reflective memory (time-series).
        In production, this would use python-logging-loki or similar.
        For now, we log locally with structured metadata.
        """
        log_entry = {
            'subsystem': self.subsystem_id.value,
            'type': log_type,
            'message': message,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.info(f"[REFLECTIVE] {json.dumps(log_entry)}")
    
    # ==================== INTER-AGENT MESSAGING ====================
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to Redis pub/sub channel"""
        await self.redis.publish(
            channel,
            json.dumps({
                'from': self.subsystem_id.value,
                'timestamp': datetime.utcnow().isoformat(),
                'payload': message
            })
        )
    
    async def subscribe(self, channel: str, callback):
        """Subscribe to Redis pub/sub channel with callback"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await callback(data)
    
    async def request(
        self,
        target_subsystem: str,
        action: str,
        params: Dict[str, Any],
        timeout: int = 30
    ) -> Optional[Dict]:
        """
        Send request to another subsystem and await response.
        Uses Redis for request/response pattern.
        """
        request_id = f"{self.subsystem_id.value}:{target_subsystem}:{datetime.utcnow().timestamp()}"
        request_channel = f"request:{target_subsystem}"
        response_channel = f"response:{request_id}"
        
        # Publish request
        await self.redis.publish(
            request_channel,
            json.dumps({
                'request_id': request_id,
                'from': self.subsystem_id.value,
                'action': action,
                'params': params,
                'response_channel': response_channel
            })
        )
        
        # Wait for response
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(response_channel)
        
        try:
            async with asyncio.timeout(timeout):
                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        response = json.loads(message['data'])
                        await pubsub.unsubscribe(response_channel)
                        return response
        except asyncio.TimeoutError:
            self.logger.warning(f"Request to {target_subsystem} timed out")
            await pubsub.unsubscribe(response_channel)
            return None
    
    # ==================== CORE PROCESSING LOOP ====================
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing entry point with constitutional compliance hooks.
        Template Method pattern: subclasses implement _process_input().
        """
        # Pre-validation
        if not self.active:
            raise RuntimeError(f"{self.subsystem_id.value} not active")
        
        # Log input to episodic memory
        event_id = await self.write_episodic(
            event_type="input_received",
            context={'input': input_data}
        )
        
        try:
            # Subsystem-specific processing
            output = await self._process_input(input_data)
            
            # Post-validation
            if not self._check_constraints(output):
                await self._log_violation(
                    violation_type="constraint_violation",
                    severity="major",
                    description=f"Output violates {self.subsystem_id.value} constraints",
                    context={'input': input_data, 'output': output}
                )
                raise ValueError("Constitutional constraint violation")
            
            # Log output to episodic memory
            await self.write_episodic(
                event_type="output_generated",
                context={'output': output},
                related_event_id=event_id
            )
            
            return output
            
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            await self.write_episodic(
                event_type="processing_error",
                context={'error': str(e), 'input': input_data},
                related_event_id=event_id
            )
            raise
    
    @abstractmethod
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subsystem-specific processing logic.
        Must be implemented by all subclasses.
        """
        pass
    
    # ==================== MODE AWARENESS ====================
    
    async def set_mode(self, mode: Mode):
        """Update current operational mode"""
        self.current_mode = mode
        await self.log_reflective(
            log_type="mode_change",
            message=f"Mode changed to {mode.value}",
            metadata={'previous_mode': self.current_mode.value if self.current_mode else None}
        )
    
    def is_dominant_in_mode(self, mode: Mode) -> bool:
        """Check if this subsystem is dominant in given mode"""
        mode_config = self.constitution['modes'][mode.value]
        return self.subsystem_id.value in mode_config.get('dominant_subsystems', [])
    
    def is_active_in_mode(self, mode: Mode) -> bool:
        """Check if this subsystem is active (not silent) in given mode"""
        mode_config = self.constitution['modes'][mode.value]
        silent = mode_config.get('silent_subsystems', [])
        return self.subsystem_id.value not in silent
