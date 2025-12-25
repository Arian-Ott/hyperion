from ..core.database import AsyncSession

class AccountService:
    def __init__(self, session:AsyncSession):
        self.session = session
    
    async def get_user(self, )