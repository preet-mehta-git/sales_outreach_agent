import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel
from app.schemas.agent import AgentInput, AgentOutput
from app.schemas.enums import ConfidenceLevel
from app.core.logging import get_logger

T = TypeVar("T")


class BaseAgent(ABC, Generic[T]):
    name: str
    version: str = "1.0"
    
    def __init__(self):
        self.logger = get_logger(f"Agent.{self.name}")

    @abstractmethod
    def run(self, input_data: AgentInput) -> T:
        """Core execution logic implemented by subclasses."""
        pass

    def execute(self, input_data: AgentInput) -> AgentOutput[T]:
        """Wrapper method enforcing execution duration, logging, and output wrapping."""
        start_time = time.time()
        self.logger.info(f"Executing agent {self.name} v{self.version} for lead {input_data.lead_id}")
        
        try:
            result_data = self.run(input_data)
            duration_ms = (time.time() - start_time) * 1000
            
            output = AgentOutput[T](
                agent_name=self.name,
                agent_version=self.version,
                lead_id=input_data.lead_id,
                success=True,
                data=result_data,
                confidence=getattr(result_data, "confidence", ConfidenceLevel.HIGH),
                evidence=getattr(result_data, "evidence", []),
                duration_ms=duration_ms
            )
            self.logger.info(f"Agent {self.name} completed successfully in {duration_ms:.1f}ms")
            return output
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Agent {self.name} failed: {str(e)}", exc_info=True)
            return AgentOutput[T](
                agent_name=self.name,
                agent_version=self.version,
                lead_id=input_data.lead_id,
                success=False,
                data=None,
                confidence=ConfidenceLevel.NOT_FOUND,
                errors=[str(e)],
                duration_ms=duration_ms
            )
