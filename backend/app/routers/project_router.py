from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import logging
from urllib.parse import quote

from app.database import async_get_db
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from app.services.user_service import UserService
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


async def get_current_user_id(token: str, db: AsyncSession) -> Optional[int]:
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
        
        user = await UserService.get_user_by_public_id(db, public_id)
        if not user:
            return None
        
        return user.id
    except Exception as e:
        logger.error(f"Error getting current user: {type(e).__name__}: {str(e)}")
        return None


@router.get("/{project_id}/export")
async def export_project(
    project_id: str,
    db: AsyncSession = Depends(async_get_db),
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
        user_id = await get_current_user_id(authorization or "", db)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Export project data
        project_data = await ProjectService.export_project_data(db, project_id, user_id)
        
        if not project_data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        # Return JSON response with proper filename
        # Use RFC 5987 format for UTF-8 encoding in Content-Disposition header
        project_name = project_data.get('name', 'project').replace(' ', '_').lower()
        # URL encode the filename to handle UTF-8 characters (including Cyrillic)
        encoded_filename = quote(f'{project_name}_export.json')
        
        return JSONResponse(
            content=project_data,
            headers={
                # Use only filename* with UTF-8 encoding to avoid latin-1 encoding issues
                # Regular filename uses ASCII-safe fallback
                'Content-Disposition': f'attachment; filename="project_export.json"; filename*=UTF-8\'\'{encoded_filename}'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting project: {type(e).__name__}: {str(e)}")
        # NEVER expose technical details to users
        raise HTTPException(status_code=500, detail="Failed to export project. Please try again later.")


@router.post("/import")
async def import_project(
    file: UploadFile = File(...),
    team_id: str = Form(...),
    db: AsyncSession = Depends(async_get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Import project from JSON file into a team.
    
    Args:
        file: Uploaded JSON file
        team_id: Team UUID to import project into
        authorization: Bearer token from header
        db: Database session
        
    Returns:
        JSON response with created project ID
    """
    try:
        logger.info("Starting project import")
        
        # Get current user
        user_id = await get_current_user_id(authorization or "", db)
        if not user_id:
            logger.warning("Import failed: No authentication")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"Import requested by user_id: {user_id}")
        
        # Validate and get team
        try:
            team = await TeamService.get_team_by_public_id(db, team_id)
            if not team:
                logger.warning(f"Import failed: Team not found - {team_id}")
                raise HTTPException(status_code=404, detail="Team not found")
            
            # Check if user has access to team
            if not await TeamService.check_user_team_access(db, team.id, user_id):
                logger.warning(f"Import failed: User {user_id} has no access to team {team_id}")
                raise HTTPException(status_code=403, detail="Access denied")
        except (ValueError, AttributeError):
            logger.warning(f"Import failed: Invalid team_id format - {team_id}")
            raise HTTPException(status_code=400, detail="Invalid team ID")
        
        # Validate file type
        if not file.filename.endswith('.json'):
            logger.warning(f"Import failed: Invalid file type - {file.filename}")
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        logger.info(f"File validated: {file.filename}")
        
        # Read and parse JSON
        content = await file.read()
        logger.info(f"File read successfully, size: {len(content)} bytes")
        
        try:
            project_data = json.loads(content.decode('utf-8'))
            logger.info(f"JSON parsed successfully, keys: {list(project_data.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Validate required fields
        if not project_data.get('name'):
            logger.warning("Import failed: Project name is missing")
            raise HTTPException(status_code=400, detail="Project name is required")
        
        logger.info(f"Importing project: {project_data.get('name')} into team {team.name}")
        
        # Import project
        project = await ProjectService.import_project_data(db, user_id, team.id, project_data)
        
        if not project:
            logger.error("Import failed: ProjectService returned None")
            raise HTTPException(status_code=500, detail="Failed to import project")
        
        logger.info(f"Project imported successfully: {project.public_id}")
        
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
        logger.exception("Full traceback:")
        # NEVER expose technical details to users
        raise HTTPException(status_code=500, detail="Failed to import project. Please check the file format and try again.")

