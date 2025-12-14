#!/bin/bash
# CouchDB entrypoint wrapper for OnRamp
# Creates system databases on first startup

# Start CouchDB in background
/docker-entrypoint.sh /opt/couchdb/bin/couchdb &
COUCHDB_PID=$!

# Wait for CouchDB to be ready
echo "Waiting for CouchDB to be ready..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:5984/ > /dev/null 2>&1; then
        echo "CouchDB is ready"
        break
    fi
    sleep 1
done

# Create system databases if they don't exist
echo "Initializing system databases..."
ADMIN_USER="${COUCHDB_USER:-admin}"
ADMIN_PASS="${COUCHDB_PASSWORD:-mysupersecretpassword}"
AUTH="http://${ADMIN_USER}:${ADMIN_PASS}@127.0.0.1:5984"

for db in _users _replicator _global_changes; do
    if ! curl -s "${AUTH}/${db}" | grep -q '"db_name"'; then
        echo "Creating ${db}..."
        curl -s -X PUT "${AUTH}/${db}" > /dev/null
    fi
done

echo "CouchDB initialization complete"

# Wait for main process
wait $COUCHDB_PID
