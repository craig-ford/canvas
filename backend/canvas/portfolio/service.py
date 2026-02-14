from typing import List
from canvas.models.user import User
from .schemas import VBUSummary, PortfolioFilters

class PortfolioService:
    async def get_summary(self, user: User, filters: PortfolioFilters) -> List[VBUSummary]:
        """Get portfolio summary with role-based filtering and health computation"""
        pass
    
    async def update_portfolio_notes(self, notes: str, user: User) -> None:
        """Update portfolio notes (admin only)"""
        pass