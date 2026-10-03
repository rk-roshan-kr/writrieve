from typing import List
from datetime import datetime
from .models import MemoryItem, LifecycleStatus
from .store import MemoryStore

class MemoryLifecycleManager:
    """
    Governs the memory state machine:
      NEW -> CANDIDATE -> CONFIRMED -> ACTIVE -> STALE -> ARCHIVED
    Manages freshness decay, access frequency promotions, and user confirmations.
    """

    @classmethod
    def promote_candidate(cls, memory: MemoryItem, store: MemoryStore) -> MemoryItem:
        if memory.lifecycle_status == LifecycleStatus.CANDIDATE:
            memory.lifecycle_status = LifecycleStatus.CONFIRMED
            memory.touch()
            store.add_memory(memory)
        return memory

    @classmethod
    def check_staleness(cls, store: MemoryStore, max_age_days: int = 365) -> List[MemoryItem]:
        stale_items = []
        now = datetime.utcnow()

        for mem in store.get_all_memories():
            if mem.lifecycle_status in [LifecycleStatus.ACTIVE, LifecycleStatus.CONFIRMED]:
                # Check expiration date
                if mem.expires_at:
                    try:
                        exp_dt = datetime.fromisoformat(mem.expires_at.replace("Z", ""))
                        if now > exp_dt:
                            mem.lifecycle_status = LifecycleStatus.STALE
                            stale_items.append(mem)
                            continue
                    except Exception:
                        pass
        if stale_items:
            store.save()
        return stale_items
