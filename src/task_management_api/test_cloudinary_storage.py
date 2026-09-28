import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from task_management_api.conversations.storage.cloudinary_storage import (
    CloudinaryFileStorage,
)
from task_management_api.conversations.storage import cloudinary_config


async def main():
    storage = CloudinaryFileStorage()
    
    
    # result = await storage.delete(
    #     "chat/files/60b69194-f378-4723-a696-f8b9e25f56ef.txt"
    # )

    # print(result)
    
    url = storage.get_url(
        "the_public_id_from_your_database"
    )

    print(url)

    # with open("test.txt", "rb") as file:
    #     upload_file = UploadFile(
    #         filename="test.txt",
    #         file=file,
    #     )
        
    #     stored_name = f"{uuid4()}{Path(upload_file.filename).suffix}"
        
    #     public_id, file_size = await storage.save(
    #         upload_file,
    #         stored_name=stored_name,
    #         category="files",
    #         max_size=500
    #     )

    #     print("PUBLIC ID:", public_id)
        # print("FILE SIZE:", file_size)


asyncio.run(main())