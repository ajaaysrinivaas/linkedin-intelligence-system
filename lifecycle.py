#!/usr/bin/env python3
"""Workspace lifecycle manager.

Archives stale dossier and feed-insight artifacts on workspace startup.
TTL: 7 days.
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def archive_stale_files(source_dir: Path, archive_base: Path, file_type: str, ttl_days: int = 7):
    """
    Archive files older than TTL (default 7 days).
    Recursively scans subdirectories.
    
    Args:
        source_dir: Source directory to scan
        archive_base: Base archive directory
        file_type: Type of file (dossiers, feed_insights, feed_summaries)
        ttl_days: Time-to-live in days
    """
    archive_dir = archive_base / file_type
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    if not source_dir.exists():
        logger.info(f"✓ No {file_type} directory found")
        return 0
    
    # Calculate cutoff date
    now = datetime.now()
    cutoff_date = now - timedelta(days=ttl_days)
    
    # Find and archive stale files — recurse into subdirectories
    archived_count = 0
    
    for data_file in source_dir.rglob("*"):
        if not data_file.is_file():
            continue
            
        file_time = datetime.fromtimestamp(data_file.stat().st_mtime)
        
        if file_time < cutoff_date:
            # Preserve relative subpath inside archive
            relative = data_file.relative_to(source_dir)
            archive_path = archive_dir / relative
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(data_file), str(archive_path))
            
            age_days = (now - file_time).days
            logger.info(f"📦 Archived: {file_type}/{relative} ({age_days}d old)")
            archived_count += 1
    
    return archived_count


def main():
    """Run lifecycle tasks on workspace startup."""
    logger.info("🔄 LinkedIn Intelligence System Startup")
    logger.info("=" * 50)
    
    try:
        archive_base = Path("archived")
        total_archived = 0
        
        # Archive stale dossiers
        active_dossiers = Path("data/dossiers/active")
        count = archive_stale_files(active_dossiers, archive_base, "dossiers", ttl_days=7)
        total_archived += count
        
        # Archive stale feed insights
        feed_insights = Path("data/feed_insights")
        count = archive_stale_files(feed_insights, archive_base, "feed_insights", ttl_days=7)
        total_archived += count

        if total_archived > 0:
            logger.info(f"✓ Archived {total_archived} file(s) total (TTL: 7 days)")
        else:
            logger.info("✓ No files to archive (TTL: 7 days)")
        
        logger.info("=" * 50)
        logger.info("✨ Startup complete")
    except Exception as e:
        logger.error(f"❌ Lifecycle error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
