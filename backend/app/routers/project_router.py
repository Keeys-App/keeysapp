from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging

from app.database import get_db
from app.services.project_service import ProjectService
from app.services.user_service import UserService
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_current_user_id(token: str, db: Session) -> Optional[int]:
    """
    Helper function to get current user ID from Bearer token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User ID or None
    """
    try:
        if not token or not token.startswith("Bearer "):
            return None
        
        token = token.replace("Bearer ", "")
        payload = decode_access_token(token)
        
        if not payload:
            return None
        
        public_id = payload.get("sub")
        if not public_id:
            return None
        
        user = UserService.get_user_by_public_id(db, public_id)
        if not user:
            return None
        
        return user.id
    except Exception as e:
        logger.error(f"Error getting current user: {type(e).__name__}: {str(e)}")
        return None


@router.get("/{project_id}/export")
async def export_project(
    project_id: str,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Export project data in i18n JSON format.
    
    Args:
        project_id: Project UUID
        authorization: Bearer token from header
        db: Database session
        
    Returns:
        JSON response with project data
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization or "", db)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Export project data
        project_data = ProjectService.export_project_data(db, project_id, user_id)
        
        if not project_data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        # Return JSON response with proper filename
        project_name = project_data.get('name', 'project').replace(' ', '_').lower()
        
        return JSONResponse(
            content=project_data,
            headers={
                'Content-Disposition': f'attachment; filename="{project_name}_export.json"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting project: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export project")


@router.post("/import")
async def import_project(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Import project from JSON file.
    
    Args:
        file: Uploaded JSON file
        authorization: Bearer token from header
        db: Database session
        
    Returns:
        JSON response with created project ID
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization or "", db)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse JSON
        content = await file.read()
        try:
            project_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Validate required fields
        if not project_data.get('name'):
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Import project
        project = ProjectService.import_project_data(db, user_id, project_data)
        
        if not project:
            raise HTTPException(status_code=500, detail="Failed to import project")
        
        return {
            'success': True,
            'project_id': str(project.public_id),
            'name': project.name,
            'message': 'Project imported successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing project: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import project: {str(e)}")

