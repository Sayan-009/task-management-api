from task_management_api.conversations.storage.cloudinary_storage import (
    CloudinaryFileStorage,
)

from task_management_api.conversations.attachment_service import (
    AttachmentService,
)


def get_file_storage() -> CloudinaryFileStorage:
    return CloudinaryFileStorage()


def get_attachment_service() -> AttachmentService:
    return AttachmentService(
        storage=get_file_storage()
    )
    