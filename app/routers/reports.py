from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult
from app.celery_worker import generate_employee_pdf_task

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("/generate-employee-pdf", status_code=status.HTTP_202_ACCEPTED)
async def trigger_pdf_generation():
    # If you have an auth dependency, you can add it like: Depends(get_current_user)
    task = generate_employee_pdf_task.delay()
    return {"success": True, "task_id": task.id, "message": "PDF generation task accepted."}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)

    if task_result.state == 'PENDING':
        return {"status": "PENDING", "ready": False}
    elif task_result.state == 'SUCCESS':
        result_data = task_result.get()
        return {
            "status": "SUCCESS",
            "ready": True,
            "download_url": result_data.get("download_url"),
            "filename": result_data.get("filename")
        }
    elif task_result.state == 'FAILURE':
        return {"status": "FAILURE", "ready": True, "error": str(task_result.info)}
    else:
        return {"status": task_result.state, "ready": False}