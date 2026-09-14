import uuid

from fastapi import APIRouter, UploadFile, status

from app.api.deps import get_current_user
from app.resume.database import SyncDbSession, get_sync_db
from fastapi import Depends
from app.resume.schemas.common import MessageResponse
from app.resume.schemas.resume import ResumeDetailOut, ResumeListItemOut, ResumeUploadResponse
from app.resume.services.resume_service import ResumeService
from app.resume.utils.file_validation import read_and_validate_upload

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    content, safe_filename = await read_and_validate_upload(file)
    service = ResumeService(db)
    resume = service.upload_resume(
        user_id=current_user.id,
        content=content,
        filename=safe_filename,
        content_type=file.content_type or "application/pdf",
    )
    message = (
        "Resume uploaded and parsed successfully."
        if resume.status.value == "parsed"
        else "Resume uploaded, but parsing encountered an issue. Check status for details."
    )
    return ResumeUploadResponse(id=resume.id, status=resume.status, message=message)


@router.get("", response_model=list[ResumeListItemOut])
def list_resumes(current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db), limit: int = 50, offset: int = 0):
    service = ResumeService(db)
    return service.list_resumes(current_user.id, limit=limit, offset=offset)


@router.get("/{resume_id}", response_model=ResumeDetailOut)
def get_resume(resume_id: uuid.UUID, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeService(db)
    return service.get_owned_resume_with_details(resume_id, current_user.id)


@router.delete("/{resume_id}", response_model=MessageResponse)
def delete_resume(resume_id: uuid.UUID, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeService(db)
    service.delete_resume(resume_id, current_user.id)
    return MessageResponse(message="Resume deleted successfully.")
