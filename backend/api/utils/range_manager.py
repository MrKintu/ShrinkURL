"""
Zookeeper-based distributed range manager for ID allocation.
Each Django instance requests a unique numeric range to prevent collisions.
"""

import os
import threading
import logging
from typing import Optional
from kazoo.client import KazooClient

logger = logging.getLogger(__name__)


class RangeManager:
    """
    Thread-safe range manager that allocates unique ID ranges from Zookeeper.
    Each instance gets a block of IDs (e.g., 1,000,000 IDs) to use locally.
    """
    
    def __init__(self):
        self.zk: Optional[KazooClient] = None
        self.range_size = int(os.getenv('ZK_RANGE_SIZE', '1000000'))  # 1M IDs per range
        self.current_id = 0
        self.range_end = 0
        self.lock = threading.Lock()
        self._initialized = False
        
    def initialize(self):
        """Initialize connection to Zookeeper and get first range."""
        if self._initialized:
            return
            
        zk_hosts = os.getenv('ZOOKEEPER_HOSTS', 'localhost:2181')
        
        try:
            self.zk = KazooClient(
                hosts=zk_hosts,
                timeout=5
            )
            self.zk.start(timeout=10)
            
            # Ensure the counter node exists
            self.zk.ensure_path('/tinyscale')
            if not self.zk.exists('/tinyscale/counter'):
                self.zk.create('/tinyscale/counter', b'0')
            
            self._acquire_new_range()
            self._initialized = True
            logger.info(f"RangeManager initialized with range: {self.current_id} to {self.range_end}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Zookeeper: {e}")
            # Fallback: use random offset for local development
            import random
            fallback_start = random.randint(1000000, 1000000000)
            self.current_id = fallback_start
            self.range_end = fallback_start + self.range_size
            self._initialized = True
            logger.warning(f"Using fallback range: {self.current_id} to {self.range_end}")
    
    def _acquire_new_range(self):
        """Request a new range from Zookeeper atomically using optimistic locking."""
        if not self.zk or not self.zk.connected:
            raise RuntimeError("Zookeeper not connected")
        
        max_retries = 10
        for attempt in range(max_retries):
            try:
                # Get current value and version
                data, stat = self.zk.get('/tinyscale/counter')
                current_value = int(data.decode('utf-8'))
                new_value = current_value + self.range_size
                
                # Try to update with version check (atomic compare-and-swap)
                self.zk.set('/tinyscale/counter', str(new_value).encode('utf-8'), version=stat.version)
                
                # Success - assign the range
                self.current_id = current_value
                self.range_end = current_value + self.range_size
                
                logger.info(f"Acquired new range: {self.current_id} to {self.range_end}")
                return
                
            except Exception as e:
                if "version mismatch" in str(e).lower() or "bad version" in str(e).lower():
                    # Another client modified the node, retry
                    logger.debug(f"Version conflict, retrying... (attempt {attempt + 1})")
                    continue
                raise
        
        raise RuntimeError(f"Failed to acquire range after {max_retries} attempts")
    
    def get_next_id(self) -> int:
        """
        Get the next unique ID. Thread-safe.
        Automatically acquires new range when current is exhausted.
        
        Returns:
            A unique integer ID
        """
        with self.lock:
            if self.current_id >= self.range_end:
                self._acquire_new_range()
            
            next_id = self.current_id
            self.current_id += 1
            return next_id
    
    def close(self):
        """Clean up Zookeeper connection."""
        if self.zk:
            self.zk.stop()
            self.zk.close()


# Global singleton instance
range_manager = RangeManager()
