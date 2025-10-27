#!/bin/bash
# Backup Qdrant collection for migration

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COLLECTION_NAME="game_performances"

mkdir -p ${BACKUP_DIR}

echo "Creating Qdrant snapshot..."

# Create snapshot via API
SNAPSHOT_RESPONSE=$(curl -s -X POST "http://localhost:6333/collections/${COLLECTION_NAME}/snapshots" | python3 -m json.tool)

SNAPSHOT_NAME=$(echo ${SNAPSHOT_RESPONSE} | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['name'])")

echo "✓ Snapshot created: ${SNAPSHOT_NAME}"

# Download snapshot
curl -o "${BACKUP_DIR}/qdrant_${COLLECTION_NAME}_${TIMESTAMP}.snapshot" \
  "http://localhost:6333/collections/${COLLECTION_NAME}/snapshots/${SNAPSHOT_NAME}"

echo "✓ Snapshot downloaded: ${BACKUP_DIR}/qdrant_${COLLECTION_NAME}_${TIMESTAMP}.snapshot"
echo "  Size: $(du -h ${BACKUP_DIR}/qdrant_${COLLECTION_NAME}_${TIMESTAMP}.snapshot | cut -f1)"
echo ""
echo "To restore on production:"
echo "  1. Upload snapshot to Qdrant server"
echo "  2. POST to /collections/${COLLECTION_NAME}/snapshots/upload"
echo "  3. Or use Qdrant Cloud's snapshot restore feature"
