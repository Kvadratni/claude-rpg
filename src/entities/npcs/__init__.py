"""
AI-powered NPC classes with embedded recipes
"""

from .village_elder import VillageElderNPC
from .master_merchant import MasterMerchantNPC
from .guard_captain import GuardCaptainNPC
from .master_smith import MasterSmithNPC
from .innkeeper import InnkeeperNPC
from .healer import HealerNPC
from .blacksmith import BlacksmithNPC
from .caravan_master import CaravanMasterNPC

__all__ = [
    'VillageElderNPC',
    'MasterMerchantNPC', 
    'GuardCaptainNPC',
    'MasterSmithNPC',
    'InnkeeperNPC',
    'HealerNPC',
    'BlacksmithNPC',
    'CaravanMasterNPC'
]