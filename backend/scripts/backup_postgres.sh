#!/bin/bash
# Backup PostgreSQL database for migration

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/nfl_analytics_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p ${BACKUP_DIR}

echo "Creating PostgreSQL backup..."
PGPASSWORD=nfl_password pg_dump \
  -h localhost \
  -p 5434 \
  -U nfl_user \
  -d nfl_analytics \
  -F p \
  -f ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}

echo "✓ Backup created: ${BACKUP_FILE}.gz"
echo "  Size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
echo ""
echo "To restore on Digital Ocean:"
echo "  gunzip ${BACKUP_FILE}.gz"
echo "  psql -h <DO_HOST> -U <DO_USER> -d <DO_DATABASE> -f ${BACKUP_FILE}"
