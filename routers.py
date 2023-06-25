import shutil
from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime


class File(BaseModel):
    operation: str = Field(..., example="check_exists")
    file_path: str = Field(..., example="/path/to/file")
    destination: str = Field(..., example="/path/to/destination")
    new_name: str = Field(..., example="newfile.txt")


class SuccessResponse(BaseModel):
    status: str = Field(..., example="success")
    exists: bool = Field(..., example=True)


class ValidationResponse(BaseModel):
    status: str = Field(..., example="success")
    size: int = Field(..., example=1024)
    type: str = Field(..., example="text/plain")
    extension: str = Field(..., example=".txt")
    last_modified: datetime
    created: datetime


class FileInformationResponse(BaseModel):
    status: str = Field(..., example="success")
    last_modified: datetime
    created: datetime


class CopyResponse(BaseModel):
    status: str = Field(..., example="success")
    new_file_path: str = Field(..., example="/path/to/new/file")


class RenameResponse(BaseModel):
    status: str = Field(..., example="success")
    new_file_path: str = Field(..., example="/path/to/renamed/file")


class DeleteResponse(BaseModel):
    status: str = Field(..., example="success")
    file_path: str = Field(..., example="/path/to/deleted/file")


class ErrorResponse(BaseModel):
    status: str = Field(..., example="failure")
    error: str = Field(..., example="An error occurred")


router = APIRouter()


@router.post("/file_operation", responses={400: {"model": ErrorResponse}})
async def perform_file_operation(file: File):
    file_path = Path(file.file_path)

    if file.operation == "check_exists":
        file_exists = file_path.exists()
        return SuccessResponse(status="success", exists=file_exists)
    elif file.operation == "validate":
        if not file_path.exists():
            return ErrorResponse(status="failure", error="File does not exist.")

        try:
            file_size = file_path.stat().st_size
            file_type = file_path.suffix[1:]
            file_extension = file_path.suffix
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            created = datetime.fromtimestamp(file_path.stat().st_ctime)

            return ValidationResponse(
                status="success",
                size=file_size,
                type=file_type,
                extension=file_extension,
                last_modified=last_modified,
                created=created
            )
        except Exception as e:
            return ErrorResponse(status="failure", error=str(e))
    elif file.operation == "retrieve_info":
        if not file_path.exists():
            return ErrorResponse(status="failure", error="File does not exist.")

        try:
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            created = datetime.fromtimestamp(file_path.stat().st_ctime)

            return FileInformationResponse(
                status="success",
                last_modified=last_modified,
                created=created
            )
        except Exception as e:
            return ErrorResponse(status="failure", error=str(e))
    elif file.operation == "copy":
        if not file_path.exists():
            return ErrorResponse(status="failure", error="Source file does not exist.")

        destination_path = Path(file.destination)
        try:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_path, destination_path)

            return CopyResponse(status="success", new_file_path=str(destination_path))
        except Exception as e:
            return ErrorResponse(status="failure", error=str(e))
    elif file.operation == "rename":
        if not file_path.exists():
            return ErrorResponse(status="failure", error="Source file does not exist.")

        new_file_path = file_path.with_name(file.new_name)
        try:
            file_path.rename(new_file_path)

            return RenameResponse(status="success", new_file_path=str(new_file_path))
        except Exception as e:
            return ErrorResponse(status="failure", error=str(e))
    elif file.operation == "delete":
        if not file_path.exists():
            return ErrorResponse(status="failure", error="File does not exist.")

        try:
            file_path.unlink()

            return DeleteResponse(status="success", file_path=str(file_path))
        except Exception as e:
            return ErrorResponse(status="failure", error=str(e))
    else:
        return ErrorResponse(status="failure", error=f"Unsupported operation: {file.operation}")
