from pathlib import Path

from task_management_api.conversations.storage.file_storage import FileStorage


class LocalFileStorage(FileStorage):
    
    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = base_dir
        
    async def save(
        self,
        file,
        stored_name: str,
        category: str,
        max_size: int,
    ) -> tuple[str, int]:
        
        upload_dir = self.base_dir / category
        
        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        
        file_path = upload_dir / stored_name
        
        total_size = 0

        with file_path.open("wb") as destination:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    file_path.unlink(missing_ok=True)
                    raise ValueError("File size exceeds the allowed limit")

                destination.write(chunk)
                
        relative_path = f"{category}/{stored_name}"

        return relative_path, total_size
    
    
    async def delete(
        self,
        file_path: str,
    ) -> None:
        path = self.base_dir / file_path
        path.unlink(missing_ok=True)
        
        
    def get_path(self, file_path: str) -> Path:
        base_path = self.base_dir.resolve()
        
        requested_path = (self.base_dir / file_path).resolve()
        
        if not requested_path.is_relative_to(base_path):
            raise ValueError("Invalid file path")

        return requested_path