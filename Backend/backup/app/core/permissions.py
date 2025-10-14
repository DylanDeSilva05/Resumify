"""
Role-based access control (RBAC) system for the HR application
Implements the unified role hierarchy with multi-tenancy
"""
from enum import Enum
from typing import List, Dict, Set
from fastapi import HTTPException, status

from app.models.user import UserRole


class Permission(str, Enum):
    """Available permissions in the system"""

    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    MANAGE_USER_ROLES = "manage_user_roles"

    # CV and Candidate Management
    UPLOAD_CV = "upload_cv"
    READ_CANDIDATE = "read_candidate"
    UPDATE_CANDIDATE = "update_candidate"
    DELETE_CANDIDATE = "delete_candidate"
    BULK_CV_ANALYSIS = "bulk_cv_analysis"

    # Job Posting Management
    CREATE_JOB_POSTING = "create_job_posting"
    READ_JOB_POSTING = "read_job_posting"
    UPDATE_JOB_POSTING = "update_job_posting"
    DELETE_JOB_POSTING = "delete_job_posting"
    PUBLISH_JOB_POSTING = "publish_job_posting"

    # CV Analysis and Matching
    RUN_CV_ANALYSIS = "run_cv_analysis"
    VIEW_ANALYSIS_RESULTS = "view_analysis_results"
    EXPORT_ANALYSIS_RESULTS = "export_analysis_results"
    MODIFY_ANALYSIS_CRITERIA = "modify_analysis_criteria"

    # Interview Management
    SCHEDULE_INTERVIEW = "schedule_interview"
    VIEW_INTERVIEW = "view_interview"
    UPDATE_INTERVIEW = "update_interview"
    CANCEL_INTERVIEW = "cancel_interview"

    # Reports and Analytics
    VIEW_REPORTS = "view_reports"
    EXPORT_REPORTS = "export_reports"
    VIEW_SYSTEM_ANALYTICS = "view_system_analytics"

    # System Administration
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SECURITY_SETTINGS = "manage_security_settings"
    BACKUP_RESTORE_DATA = "backup_restore_data"


class RolePermissions:
    """Define permissions for each role in the unified system"""

    # SUPER_ADMIN: Platform owner - can do everything across all companies
    SUPER_ADMIN_PERMISSIONS: Set[Permission] = {
        # Full user management
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.MANAGE_USER_ROLES,

        # All CV and candidate operations
        Permission.UPLOAD_CV,
        Permission.READ_CANDIDATE,
        Permission.UPDATE_CANDIDATE,
        Permission.DELETE_CANDIDATE,
        Permission.BULK_CV_ANALYSIS,

        # All job posting operations
        Permission.CREATE_JOB_POSTING,
        Permission.READ_JOB_POSTING,
        Permission.UPDATE_JOB_POSTING,
        Permission.DELETE_JOB_POSTING,
        Permission.PUBLISH_JOB_POSTING,

        # All analysis operations
        Permission.RUN_CV_ANALYSIS,
        Permission.VIEW_ANALYSIS_RESULTS,
        Permission.EXPORT_ANALYSIS_RESULTS,
        Permission.MODIFY_ANALYSIS_CRITERIA,

        # All interview operations
        Permission.SCHEDULE_INTERVIEW,
        Permission.VIEW_INTERVIEW,
        Permission.UPDATE_INTERVIEW,
        Permission.CANCEL_INTERVIEW,

        # All reports and analytics
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_SYSTEM_ANALYTICS,

        # System administration
        Permission.MANAGE_SYSTEM_SETTINGS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_SECURITY_SETTINGS,
        Permission.BACKUP_RESTORE_DATA
    }

    # COMPANY_ADMIN: Company owner - full access within their company
    COMPANY_ADMIN_PERMISSIONS: Set[Permission] = {
        # Full user management (within company)
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.MANAGE_USER_ROLES,

        # All CV and candidate operations
        Permission.UPLOAD_CV,
        Permission.READ_CANDIDATE,
        Permission.UPDATE_CANDIDATE,
        Permission.DELETE_CANDIDATE,
        Permission.BULK_CV_ANALYSIS,

        # All job posting operations
        Permission.CREATE_JOB_POSTING,
        Permission.READ_JOB_POSTING,
        Permission.UPDATE_JOB_POSTING,
        Permission.DELETE_JOB_POSTING,
        Permission.PUBLISH_JOB_POSTING,

        # All analysis operations
        Permission.RUN_CV_ANALYSIS,
        Permission.VIEW_ANALYSIS_RESULTS,
        Permission.EXPORT_ANALYSIS_RESULTS,
        Permission.MODIFY_ANALYSIS_CRITERIA,

        # All interview operations
        Permission.SCHEDULE_INTERVIEW,
        Permission.VIEW_INTERVIEW,
        Permission.UPDATE_INTERVIEW,
        Permission.CANCEL_INTERVIEW,

        # All reports and analytics (company-level)
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_SYSTEM_ANALYTICS,

        # Company settings (not system-wide)
        Permission.MANAGE_SYSTEM_SETTINGS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_SECURITY_SETTINGS
    }

    # COMPANY_USER: Standard HR operations within company
    COMPANY_USER_PERMISSIONS: Set[Permission] = {
        # Limited user management (read only)
        Permission.READ_USER,

        # Full CV and candidate operations
        Permission.UPLOAD_CV,
        Permission.READ_CANDIDATE,
        Permission.UPDATE_CANDIDATE,
        Permission.BULK_CV_ANALYSIS,

        # Job posting operations (no delete)
        Permission.CREATE_JOB_POSTING,
        Permission.READ_JOB_POSTING,
        Permission.UPDATE_JOB_POSTING,
        Permission.PUBLISH_JOB_POSTING,

        # Full analysis operations
        Permission.RUN_CV_ANALYSIS,
        Permission.VIEW_ANALYSIS_RESULTS,
        Permission.EXPORT_ANALYSIS_RESULTS,
        Permission.MODIFY_ANALYSIS_CRITERIA,

        # Full interview operations
        Permission.SCHEDULE_INTERVIEW,
        Permission.VIEW_INTERVIEW,
        Permission.UPDATE_INTERVIEW,
        Permission.CANCEL_INTERVIEW,

        # Reports (no system analytics)
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS
    }

    # RECRUITER: CV screening, interview scheduling (limited access)
    RECRUITER_PERMISSIONS: Set[Permission] = {
        # No user management

        # Basic CV and candidate operations
        Permission.UPLOAD_CV,
        Permission.READ_CANDIDATE,
        Permission.UPDATE_CANDIDATE,

        # Read-only job postings
        Permission.READ_JOB_POSTING,

        # Basic analysis operations
        Permission.RUN_CV_ANALYSIS,
        Permission.VIEW_ANALYSIS_RESULTS,

        # Full interview operations (core responsibility)
        Permission.SCHEDULE_INTERVIEW,
        Permission.VIEW_INTERVIEW,
        Permission.UPDATE_INTERVIEW,
        Permission.CANCEL_INTERVIEW,

        # Basic reporting
        Permission.VIEW_REPORTS
    }

    @classmethod
    def get_permissions_for_role(cls, role: UserRole) -> Set[Permission]:
        """Get all permissions for a given role"""
        role_mapping = {
            UserRole.SUPER_ADMIN: cls.SUPER_ADMIN_PERMISSIONS,
            UserRole.COMPANY_ADMIN: cls.COMPANY_ADMIN_PERMISSIONS,
            UserRole.COMPANY_USER: cls.COMPANY_USER_PERMISSIONS,
            UserRole.RECRUITER: cls.RECRUITER_PERMISSIONS
        }
        return role_mapping.get(role, set())


class PermissionChecker:
    """Utility class for checking user permissions"""

    @staticmethod
    def user_has_permission(role: UserRole, permission: Permission) -> bool:
        """Check if user role has specific permission"""
        user_permissions = RolePermissions.get_permissions_for_role(role)
        return permission in user_permissions

    @staticmethod
    def user_has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
        """Check if user role has any of the specified permissions"""
        user_permissions = RolePermissions.get_permissions_for_role(role)
        return any(permission in user_permissions for permission in permissions)

    @staticmethod
    def user_has_all_permissions(role: UserRole, permissions: List[Permission]) -> bool:
        """Check if user role has all of the specified permissions"""
        user_permissions = RolePermissions.get_permissions_for_role(role)
        return all(permission in user_permissions for permission in permissions)

    @staticmethod
    def require_permission(role: UserRole, permission: Permission):
        """Raise HTTPException if user doesn't have required permission"""
        if not PermissionChecker.user_has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )

    @staticmethod
    def require_any_permission(role: UserRole, permissions: List[Permission]):
        """Raise HTTPException if user doesn't have any of the required permissions"""
        if not PermissionChecker.user_has_any_permission(role, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {', '.join(permission_names)}"
            )

    @staticmethod
    def require_all_permissions(role: UserRole, permissions: List[Permission]):
        """Raise HTTPException if user doesn't have all required permissions"""
        if not PermissionChecker.user_has_all_permissions(role, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required all of: {', '.join(permission_names)}"
            )


def get_role_hierarchy() -> Dict[UserRole, int]:
    """Get role hierarchy levels (higher number = more privileges)"""
    return {
        UserRole.RECRUITER: 1,
        UserRole.COMPANY_USER: 2,
        UserRole.COMPANY_ADMIN: 3,
        UserRole.SUPER_ADMIN: 4
    }


def user_can_manage_role(manager_role: UserRole, target_role: UserRole) -> bool:
    """Check if a user can manage another user's role"""
    hierarchy = get_role_hierarchy()
    return hierarchy.get(manager_role, 0) > hierarchy.get(target_role, 0)


def get_permissions_summary() -> Dict[str, List[str]]:
    """Get a summary of all role permissions for documentation/API responses"""
    return {
        "super_admin": [p.value for p in RolePermissions.SUPER_ADMIN_PERMISSIONS],
        "company_admin": [p.value for p in RolePermissions.COMPANY_ADMIN_PERMISSIONS],
        "company_user": [p.value for p in RolePermissions.COMPANY_USER_PERMISSIONS],
        "recruiter": [p.value for p in RolePermissions.RECRUITER_PERMISSIONS]
    }