from fastapi import APIRouter, HTTPException, Response
from services.action_service import action_service

router = APIRouter(prefix="/export", tags=["exports"])


@router.get("/overall-ledger")
async def export_overall_ledger():
    """Download overall business ledger as PDF."""
    try:
        pdf_bytes = await action_service.generate_overall_ledger_pdf()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=overall_ledger.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aging-debtors")
async def export_aging_debtors():
    """Download aging debtors report as Excel."""
    try:
        file_data = await action_service.generate_aging_debtors_excel()
        return Response(
            content=file_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=aging_debtors.xlsx"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overall-ledger-excel")
async def export_overall_ledger_excel():
    """Download overall business ledger as Excel."""
    try:
        file_data = await action_service.generate_overall_ledger_excel()
        return Response(
            content=file_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=overall_ledger.xlsx"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
