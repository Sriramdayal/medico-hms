// MongoDB Replica Set Initialization Script
// This runs on first container startup

// The replica set is initialized via the healthcheck command in docker-compose.yml
// This script creates application-level indexes and initial data

db = db.getSiblingDB("medico");

// Create indexes for audit_logs collection (append-only, TTL for retention)
db.createCollection("audit_logs", {
    capped: false
});

db.audit_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 31536000 }); // 1 year TTL
db.audit_logs.createIndex({ "user_id": 1, "timestamp": -1 });
db.audit_logs.createIndex({ "action": 1, "timestamp": -1 });
db.audit_logs.createIndex({ "resource_type": 1, "resource_id": 1 });

print("✅ Medico HMS: MongoDB initialized with audit_logs indexes");
