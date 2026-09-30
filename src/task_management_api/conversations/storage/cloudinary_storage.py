import cloudinary.uploader
import os
import tempfile
import asyncio
from cloudinary import utils
from pathlib import Path

from task_management_api.conversations.storage.file_storage import FileStorage


class CloudinaryFileStorage(FileStorage):

    async def _prepare_upload(
        self,
        file,
        max_size: int,
    ) -> tuple[str, int]:

        await file.seek(0)

        total_size = 0

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
        )

        temp_path = temp_file.name

        try:
            with temp_file:
                while True:
                    chunk = await file.read(1024 * 1024)

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > max_size:
                        raise ValueError(
                            "File size exceeds the allowed limit"
                        )

                    temp_file.write(chunk)

        except Exception:
            os.unlink(temp_path)
            raise

        await file.seek(0)

        return temp_path, total_size
    
    
    async def save(
        self,
        file,
        stored_name: str,
        category: str,
        max_size: int,
    ) -> tuple[str, int]:

        temp_path = None

        try:
            temp_path, file_size = await self._prepare_upload(
                file,
                max_size,
            )

            resource_type = (
                "image"
                if category == "images"
                else "raw"
            )
            
            if resource_type == "image":
                public_id = f"chat/{category}/{Path(stored_name).stem}"
            else:
                public_id = f"chat/{category}/{stored_name}"

            result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                temp_path,
                public_id=public_id,
                resource_type=resource_type,
                type="authenticated",
            )

            return result["public_id"], file_size

        finally:
            if temp_path:
                os.unlink(temp_path)
                
                
    async def delete(
        self,
        file_path: str,
    ) -> None:

        resource_type = "image" if "/images/" in file_path else "raw"

        await asyncio.to_thread(
            cloudinary.uploader.destroy,
            file_path,
            resource_type=resource_type,
        )
        
    def get_url(
        self,
        file_path: str,
    ) -> str:

        resource_type = (
            "image"
            if "/images/" in file_path
            else "raw"
        )

        if resource_type == "raw":
            file_format = Path(file_path).suffix.lstrip(".")

            return utils.private_download_url(
                file_path,
                file_format,
                resource_type="raw",
                type="authenticated",
                secure=True,
            )

        url, _ = utils.cloudinary_url(
            file_path,
            resource_type="image",
            type="authenticated",
            secure=True,
            sign_url=True,
        )

        return url
        