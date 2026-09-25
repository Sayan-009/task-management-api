from abc import ABC, abstractmethod


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