"""
Importing this package (app.models) registers every model on Base.metadata,
which is what Alembic's autogenerate needs to see the full schema.

Always import models via `import app.models` (or `from app.models import User`,
etc.) rather than importing app.database.base directly for this purpose —
this avoids a circular import between base.py and the model files.
"""
from app.models.role import Role, RoleName  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.transplant_case import (  # noqa: F401
    TransplantCase,
    TransplantType,
    CaseStatus,
    CaseStatusHistory,
    PatientPreference,
)
from app.models.centre import (  # noqa: F401
    TransplantCentre,
    CentreCapability,
    CentreService,
    CentreVerification,
)
from app.models.document import (  # noqa: F401
    DocumentType,
    DocumentChecklist,
    DocumentRequirement,
    Document,
    DocumentAnalysis,
)
from app.models.matching import MatchingResult, MatchingFeature  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.notification import Notification, Message  # noqa: F401
from app.models.system import ModelVersion, SystemSetting  # noqa: F401
