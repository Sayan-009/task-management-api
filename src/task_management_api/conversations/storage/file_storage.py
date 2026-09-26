from abc import ABC, abstractmethod
from pathlib import Path

class FileStorage(ABC):
    
    @abstractmethod
    async def save(
        self,
        file, 
        stored_name: str,
        category: str,
        max_size: int
    ) -> tuple[str, int]:
        pass
    
    
    @abstractmethod
    async def delete(
        self,
        file_path: str,
    ) -> None:
        pass
    
    @abstractmethod
    def get_path(
        self,
        file_path: str
    ) -> Path:
        pass