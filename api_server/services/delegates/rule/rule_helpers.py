"""
Helper functions for management rule service.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class RuleHelpers:
    """Helper functions for management rule operations"""
    
    @staticmethod
    def parse_expiry(value: str | None) -> datetime | None:
        """
        Parse expiry date from string to datetime.
        
        Args:
            value: Expiry date string in various formats
            
        Returns:
            datetime object or None if invalid
        """
        if not value or str(value).lower() == "null":
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse expiry date: {value}")
        return None