# Contract Registry

## Model Locations
| Model | Location | Defined By | Consumers |
|-------|----------|------------|-----------|
| TimestampMixin | backend/canvas/models/__init__.py | 001A-infrastructure/T-006 | 001-auth, 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review |
| User | backend/canvas/models/user.py | 001-auth/T-011 | 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review |
| UserRole | backend/canvas/models/user.py | 001-auth/T-011 | 001-auth, 002-canvas-management |
| VBU | backend/canvas/models/vbu.py | 002-canvas-management/T-003 | 003-portfolio-dashboard |
| Canvas | backend/canvas/models/canvas.py | 002-canvas-management/T-003 | 003-portfolio-dashboard, 004-monthly-review |
| Thesis | backend/canvas/models/thesis.py | 002-canvas-management/T-003 | |
| ProofPoint | backend/canvas/models/proof_point.py | 002-canvas-management/T-003 | |
| Attachment | backend/canvas/models/attachment.py | 002-canvas-management/T-003 | 004-monthly-review |
| MonthlyReview | backend/canvas/models/monthly_review.py | 004-monthly-review/T-001 | |
| Commitment | backend/canvas/models/commitment.py | 004-monthly-review/T-002 | |

## Service Locations
| Service | Location | Defined By | Consumers |
|---------|----------|------------|-----------|
| Settings | backend/canvas/config.py | 001A-infrastructure/T-006 | 001-auth, 002-canvas-management |
| AuthService | backend/canvas/auth/service.py | 001-auth/T-013 | 001-auth |
| UserService | backend/canvas/auth/user_service.py | 001-auth/T-014 | 001-auth |
| CanvasService | backend/canvas/services/canvas_service.py | 002-canvas-management/T-012 | 003-portfolio-dashboard, 004-monthly-review |
| AttachmentService | backend/canvas/services/attachment_service.py | 002-canvas-management/T-013 | 004-monthly-review |
| PortfolioService | backend/canvas/portfolio/service.py | 003-portfolio-dashboard/T-005 | |
| PDFService | backend/canvas/pdf/service.py | 003-portfolio-dashboard/T-006 | |
| ReviewService | backend/canvas/reviews/service.py | 004-monthly-review/T-013 | |

## Dependency Locations
| Dependency | Location | Defined By | Consumers |
|------------|----------|------------|-----------|
| get_db_session | backend/canvas/db.py | 001A-infrastructure/T-007 | all features |
| success_response | backend/canvas/__init__.py | 001A-infrastructure/T-006 | all features |
| list_response | backend/canvas/__init__.py | 001A-infrastructure/T-006 | all features |
| get_current_user | backend/canvas/auth/dependencies.py | 001-auth/T-015 | 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review |
| require_role | backend/canvas/auth/dependencies.py | 001-auth/T-015 | 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review |
| create_app | backend/canvas/main.py | 001A-infrastructure/T-008 | |

## Import Patterns
| Pattern | Correct | Wrong Variants |
|---------|---------|----------------|
| Models | `from canvas.models.{entity} import {Entity}` | `from backend.canvas.models...`, `from models...` |
| Auth deps | `from canvas.auth.dependencies import get_current_user, require_role` | `from auth.dependencies...`, `from backend.auth...` |
| DB session | `from canvas.db import get_db_session` | `from backend.canvas.db...`, `from db...` |
| Response helpers | `from canvas import success_response, list_response` | `from canvas.responses...`, `from backend.canvas...` |
| Config | `from canvas.config import Settings` | `from config...`, `from backend.canvas.config...` |
