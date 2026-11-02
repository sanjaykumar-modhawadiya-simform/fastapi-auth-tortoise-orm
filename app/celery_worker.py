import os
import asyncio
import uuid
from celery import Celery
from tortoise import Tortoise
from app.models import Employee
from app.services.pdf_service import generate_pdf_buffer
from app.services.s3_service import upload_pdf_to_s3

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

async def async_generate_and_upload():
    db_url = os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/inventory_db")
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["app.models"]}
    )
    try:
        employees = await Employee.all()
        pdf_buffer = generate_pdf_buffer(employees)
        filename = f"employee_report_{uuid.uuid4()}.pdf"
        download_url = upload_pdf_to_s3(pdf_buffer, filename)
        return {"download_url": download_url, "filename": filename}
    finally:
        await Tortoise.close_connections()

@celery_app.task(name="generate_employee_pdf_task")
def generate_employee_pdf_task():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_generate_and_upload())
    return result
