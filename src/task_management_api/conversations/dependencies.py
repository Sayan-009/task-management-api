from pathlib import Path

from task_management_api.core.config import settings
from task_management_api.conversations.storage.local_file_storage import (
    LocalFileStorage,
)
from task_management_api.conversations.attachment_service import (
    AttachmentService
)

def get_file_storage() -> LocalFileStorage:
    return LocalFileStorage(
        base_dir=Path(settings.upload_dir)
    )
    
def get_attachment_service() -> AttachmentService:
    return AttachmentService(
        storage=get_file_storage()
    )