---
command: db:backup-restore
plugin: databases
category: database-operations
description: Automated database backup and restore workflows with encryption, compression, and cloud storage integration
tags:
  - database
  - backup
  - restore
  - disaster-recovery
  - postgresql
  - mysql
  - mongodb
  - bigquery
  - encryption
  - cloud-storage
allowed-tools: Bash, Read, Write, Agent
tools:
  - @postgresql-expert
  - @mongodb-expert
version: 2.0.0
---

# db:backup-restore

Comprehensive database backup and restore automation with multi-database support, encryption, compression, cloud storage integration, and disaster recovery strategies.

## Description

Enterprise-grade backup and restore automation covering:
- **Multi-Database Support**: PostgreSQL, MySQL, MongoDB, BigQuery, Cosmos DB
- **Backup Strategies**: Full, incremental, differential, continuous (PITR)
- **Cloud Integration**: AWS S3, Google Cloud Storage, Azure Blob Storage
- **Security**: Encryption at rest, encryption in transit, credential management
- **Compression**: gzip, bzip2, custom compression with trade-off analysis
- **Validation**: Integrity checks, restore simulation, backup verification
- **Retention**: Automated retention policies, GFS rotation, lifecycle management
- **Cross-Environment**: Production to staging restore with data sanitization

## Required Documentation Access

**MANDATORY:** Before backup/restore operations, query Context7 for database-specific best practices:

**Documentation Queries:**
- `mcp://context7/postgresql/backup` - pg_dump, pg_restore, pg_basebackup best practices
- `mcp://context7/postgresql/pitr` - Point-in-time recovery and WAL archiving
- `mcp://context7/mysql/backup` - mysqldump, mysqlpump, binary log backup strategies
- `mcp://context7/mysql/pitr` - Point-in-time recovery using binary logs
- `mcp://context7/mongodb/backup` - mongodump, mongorestore, oplog strategies
- `mcp://context7/mongodb/replica-set` - Replica set backup consistency
- `mcp://context7/aws/rds-backups` - RDS automated backups and snapshots
- `mcp://context7/gcp/cloud-sql-backups` - Cloud SQL backup and restore strategies
- `mcp://context7/azure/database-backup` - Azure Database geo-redundant backups

**Why This is Required:**
- Ensures compliance with industry-standard disaster recovery methodologies (3-2-1 backup strategy)
- Applies proven backup patterns and best practices verified by Context7 documentation
- Prevents data loss through Context7-verified retention and validation procedures
- Validates encryption, compression, and restore strategies against current industry standards
- Ensures backup operations don't impact production database performance
- Provides accurate RPO/RTO estimates based on real-world proven methodologies and backup patterns

## Usage

```bash
/db:backup-restore [options]
```

## Options

### Action Options
- `--action <backup|restore>` - Operation to perform (required)
- `--database <connection-string>` - Database connection (required)
- `--type <postgresql|mysql|mongodb|bigquery>` - Database type (auto-detected if possible)

### Backup Options
- `--target <path|s3://|gs://|azure://>` - Backup destination (required for backup)
- `--backup-type <full|incremental|differential>` - Backup strategy (default: full)
- `--compression <none|gzip|bzip2|custom>` - Compression algorithm (default: gzip)
- `--compression-level <1-9>` - Compression level (default: 6)
- `--encrypt` - Enable encryption at rest
- `--encryption-key <path>` - Path to encryption key file
- `--parallel <jobs>` - Number of parallel backup jobs (PostgreSQL)

### Restore Options
- `--source <path|s3://|gs://|azure://>` - Backup source (required for restore)
- `--target-database <connection-string>` - Target database (required for restore)
- `--point-in-time <timestamp>` - Restore to specific point in time (PITR)
- `--dry-run` - Simulate restore without applying changes
- `--validate-only` - Only validate backup integrity
- `--parallel <jobs>` - Number of parallel restore jobs

### Retention Options
- `--retention-days <days>` - Delete backups older than N days
- `--retention-policy <gfs|simple>` - Retention strategy (GFS = Grandfather-Father-Son)
- `--keep-daily <count>` - Number of daily backups to keep
- `--keep-weekly <count>` - Number of weekly backups to keep
- `--keep-monthly <count>` - Number of monthly backups to keep

### Validation Options
- `--verify-backup` - Verify backup integrity after creation
- `--simulate-restore` - Test restore in isolated environment
- `--checksum <md5|sha256>` - Generate backup checksum

### Monitoring Options
- `--alert-on-failure <email|slack>` - Send alerts on backup failure
- `--metrics-output <path>` - Export backup metrics (JSON)
- `--progress` - Show progress during backup/restore

## Examples

### Full Backup with Compression

```bash
/db:backup-restore \
  --action backup \
  --database postgres://user:pass@localhost:5432/production \
  --target /backups/ \
  --compression gzip \
  --verify-backup
```

### Incremental Backup to S3 with Encryption

```bash
/db:backup-restore \
  --action backup \
  --database postgres://localhost/prod \
  --target s3://my-backups/postgres/ \
  --backup-type incremental \
  --compression bzip2 \
  --encrypt \
  --encryption-key /secure/backup.key \
  --parallel 4
```

### MySQL Full Backup with Binary Logs

```bash
/db:backup-restore \
  --action backup \
  --database mysql://root@localhost/production \
  --target gs://backups/mysql/ \
  --compression gzip \
  --encrypt \
  --verify-backup
```

### MongoDB Backup from Replica Set

```bash
/db:backup-restore \
  --action backup \
  --database mongodb://localhost:27017/production \
  --target /backups/mongodb/ \
  --compression gzip \
  --verify-backup
```

### Restore from Latest Backup

```bash
/db:backup-restore \
  --action restore \
  --source s3://my-backups/postgres/latest.dump \
  --target-database postgres://localhost/staging \
  --parallel 8 \
  --dry-run
```

### Point-in-Time Recovery (PITR)

```bash
/db:backup-restore \
  --action restore \
  --source s3://backups/postgres/base-backup.tar.gz \
  --target-database postgres://localhost/recovery \
  --point-in-time "2025-10-21 10:30:00 UTC"
```

### Cross-Environment Restore (Prod → Staging)

```bash
/db:backup-restore \
  --action restore \
  --source s3://prod-backups/latest.dump \
  --target-database postgres://staging-db/staging \
  --sanitize-data \
  --dry-run
```

### Apply Retention Policy

```bash
/db:backup-restore \
  --action cleanup \
  --target s3://backups/postgres/ \
  --retention-policy gfs \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 12
```

## Instructions

### Step 1: Query Context7 for Best Practices

**MANDATORY FIRST STEP**: Before any backup/restore operation, query Context7 for database-specific strategies:

```markdown
Query Context7 with:
- Database-specific backup tool options (pg_dump, mysqldump, mongodump)
- Compression and encryption best practices
- Cloud storage integration patterns
- Point-in-time recovery procedures
- Retention policy recommendations
```

### Step 2: Validate Prerequisites

Before starting backup/restore operations:

1. **Check Database Connectivity**
   ```bash
   psql -h localhost -U user -d production -c "SELECT version();"
   mysql -h localhost -u root -p -e "SELECT VERSION();"
   mongosh --eval "db.version()"
   ```

2. **Verify Disk Space**
   ```bash
   df -h /backups/
   # Ensure 2x database size available for backup + compression
   ```

3. **Check Permissions**
   ```bash
   # PostgreSQL: REPLICATION role for base backups
   # MySQL: SELECT, RELOAD, LOCK TABLES, REPLICATION CLIENT
   # MongoDB: backup role on admin database
   ```

4. **Validate Cloud Storage Access**
   ```bash
   aws s3 ls s3://my-backups/
   gsutil ls gs://backups/
   az storage blob list --account-name myaccount
   ```

### Step 3: Perform Backup Operation

#### PostgreSQL Full Backup

**pg_dump (Logical Backup):**
```bash
# Custom format (recommended for flexibility)
pg_dump -h localhost -U postgres -d production \
  --format=custom \
  --compress=6 \
  --verbose \
  --file=/backups/production_$(date +%Y%m%d_%H%M%S).dump

# Directory format (supports parallel dump)
pg_dump -h localhost -U postgres -d production \
  --format=directory \
  --jobs=4 \
  --verbose \
  --file=/backups/production_dir/

# Plain SQL format (human-readable)
pg_dump -h localhost -U postgres -d production \
  --format=plain \
  --file=/backups/production.sql
```

**pg_basebackup (Physical Backup for PITR):**
```bash
# Base backup with WAL archiving
pg_basebackup -h localhost -U replication \
  --format=tar \
  --gzip \
  --progress \
  --checkpoint=fast \
  --wal-method=stream \
  --pgdata=/backups/base_backup/
```

**Best Practices from Context7:**
- Use `--format=custom` or `--format=directory` for flexibility
- Enable parallel dumps with `--jobs` for large databases (>100GB)
- Use `CREATE INDEX CONCURRENTLY` option to avoid exclusive locks
- Always include `--verbose` for debugging
- Consider `--compress=9` for long-term storage, `--compress=1` for speed

#### MySQL Full Backup

**mysqldump (Logical Backup):**
```bash
# Full backup with best practices
mysqldump -h localhost -u root -p \
  --single-transaction \
  --quick \
  --lock-tables=false \
  --routines \
  --triggers \
  --events \
  --databases production \
  --result-file=/backups/production_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
mysqldump -h localhost -u root -p \
  --single-transaction \
  --quick \
  --databases production | gzip > /backups/production.sql.gz
```

**Binary Log Backup (for PITR):**
```bash
# Flush logs and backup binary logs
mysql -u root -p -e "FLUSH BINARY LOGS;"
cp /var/lib/mysql/binlog.* /backups/binlogs/

# Or use mysqlbinlog
mysqlbinlog --read-from-remote-server \
  --host=localhost \
  --user=root \
  --password \
  binlog.000001 > /backups/binlog.000001.sql
```

**Best Practices from Context7:**
- Always use `--single-transaction` for InnoDB tables (consistent backup without locks)
- Include `--routines --triggers --events` to backup all objects
- Backup binary logs separately for point-in-time recovery
- Use `--quick` to avoid buffering entire tables in memory
- For large databases (>10GB), consider Percona XtraBackup (physical backup)

#### MongoDB Backup

**mongodump (Logical Backup):**
```bash
# Full backup with oplog (PITR)
mongodump --host=localhost:27017 \
  --db=production \
  --oplog \
  --gzip \
  --out=/backups/mongodb_$(date +%Y%m%d_%H%M%S)

# Backup from secondary (recommended for replica sets)
mongodump --host=secondary:27017 \
  --readPreference=secondary \
  --db=production \
  --oplog \
  --gzip \
  --out=/backups/mongodb/
```

**Best Practices from Context7:**
- Use `--oplog` for point-in-time recovery capability
- Run mongodump on secondary nodes to avoid production impact
- Use `--gzip` for compression (BSON is not compressed by default)
- For sharded clusters, use Percona Backup for MongoDB (PBM)
- For databases >100GB, consider filesystem snapshots or cloud-native backups

### Step 4: Apply Compression

**Compression Algorithms:**

1. **gzip (Recommended for most cases)**
   ```bash
   # Fast compression (level 1)
   pg_dump -Fc production | gzip -1 > backup.dump.gz

   # Balanced (level 6, default)
   pg_dump -Fc production | gzip -6 > backup.dump.gz

   # Maximum compression (level 9)
   pg_dump -Fc production | gzip -9 > backup.dump.gz
   ```

2. **bzip2 (Better compression, slower)**
   ```bash
   pg_dump -Fc production | bzip2 -9 > backup.dump.bz2
   ```

3. **zstd (Fast with good compression)**
   ```bash
   pg_dump -Fc production | zstd -3 > backup.dump.zst
   ```

**Compression Trade-offs:**
| Algorithm | Speed | Ratio | CPU | Recommended For |
|-----------|-------|-------|-----|-----------------|
| gzip -1   | Fast  | 3:1   | Low | Frequent backups |
| gzip -6   | Medium| 5:1   | Med | General purpose |
| gzip -9   | Slow  | 6:1   | High| Long-term storage |
| bzip2 -9  | Very Slow | 7:1 | Very High | Archive |
| zstd -3   | Very Fast | 4:1 | Low | Real-time backups |

### Step 5: Apply Encryption

**Encryption at Rest:**

1. **OpenSSL (Recommended)**
   ```bash
   # Encrypt backup with AES-256
   pg_dump -Fc production | \
     openssl enc -aes-256-cbc -salt -pbkdf2 \
     -pass file:/secure/backup.key \
     -out /backups/production.dump.enc

   # Encrypt with compression
   pg_dump -Fc production | gzip | \
     openssl enc -aes-256-cbc -salt -pbkdf2 \
     -pass file:/secure/backup.key \
     -out /backups/production.dump.gz.enc
   ```

2. **GPG (for public key encryption)**
   ```bash
   # Encrypt with GPG
   pg_dump -Fc production | \
     gpg --encrypt --recipient backup@company.com \
     --output /backups/production.dump.gpg
   ```

3. **Cloud Storage Encryption**
   ```bash
   # AWS S3 with server-side encryption
   aws s3 cp backup.dump s3://backups/ \
     --sse AES256

   # GCP with customer-managed encryption keys
   gsutil -o 'GSUtil:encryption_key=/path/to/key' \
     cp backup.dump gs://backups/
   ```

**Best Practices from Context7:**
- Always encrypt backups containing sensitive data
- Store encryption keys separately from backups (use key management services)
- Use AES-256 for encryption at rest
- Enable TLS/SSL for encryption in transit
- Rotate encryption keys regularly (quarterly recommended)

### Step 6: Upload to Cloud Storage

#### AWS S3

```bash
# Upload with encryption and metadata
aws s3 cp /backups/production.dump \
  s3://my-backups/postgres/production_$(date +%Y%m%d).dump \
  --sse AES256 \
  --storage-class STANDARD_IA \
  --metadata "database=production,type=full,timestamp=$(date +%s)"

# Multipart upload for large files (>5GB)
aws s3 cp /backups/large.dump s3://backups/ \
  --sse AES256 \
  --multipart-chunk-size 100MB
```

#### Google Cloud Storage

```bash
# Upload with compression and encryption
gsutil -m cp -r /backups/production.dump \
  gs://my-backups/postgres/production_$(date +%Y%m%d).dump

# Set lifecycle policy for auto-deletion
gsutil lifecycle set lifecycle.json gs://my-backups/
```

#### Azure Blob Storage

```bash
# Upload with encryption
az storage blob upload \
  --account-name mybackups \
  --container-name postgres \
  --file /backups/production.dump \
  --name production_$(date +%Y%m%d).dump \
  --tier Cool
```

### Step 7: Validate Backup Integrity

**Checksum Verification:**

```bash
# Generate MD5 checksum
md5sum /backups/production.dump > /backups/production.dump.md5

# Verify checksum
md5sum -c /backups/production.dump.md5

# SHA-256 (more secure)
sha256sum /backups/production.dump > /backups/production.dump.sha256
```

**PostgreSQL Backup Validation:**

```bash
# List contents without restoring
pg_restore --list /backups/production.dump

# Test restore to temporary database
createdb backup_test
pg_restore -d backup_test /backups/production.dump
psql -d backup_test -c "SELECT COUNT(*) FROM users;"
dropdb backup_test
```

**MySQL Backup Validation:**

```bash
# Parse SQL dump for errors
mysql --verbose --force < /backups/production.sql 2> /tmp/restore_errors.log

# Test restore to temporary database
mysql -e "CREATE DATABASE backup_test;"
mysql backup_test < /backups/production.sql
mysql -e "DROP DATABASE backup_test;"
```

**MongoDB Backup Validation:**

```bash
# Verify BSON integrity
bsondump /backups/mongodb/production/users.bson | head -10

# Test restore to temporary database
mongorestore --db=backup_test --drop \
  /backups/mongodb/production/
mongosh --eval "use backup_test; db.dropDatabase();"
```

### Step 8: Perform Restore Operation

#### PostgreSQL Restore

**From Custom Format:**
```bash
# Restore with parallel jobs
pg_restore -h localhost -U postgres \
  --dbname=staging \
  --jobs=8 \
  --verbose \
  --clean \
  --if-exists \
  /backups/production.dump

# Restore specific tables only
pg_restore -h localhost -U postgres \
  --dbname=staging \
  --table=users \
  --table=orders \
  /backups/production.dump
```

**Point-in-Time Recovery:**
```bash
# 1. Restore base backup
tar -xzf /backups/base_backup.tar.gz -C /var/lib/postgresql/15/main/

# 2. Create recovery.conf (PostgreSQL 11 and earlier) or recovery.signal (PostgreSQL 12+)
cat > /var/lib/postgresql/15/main/recovery.signal <<EOF
restore_command = 'cp /backups/wal_archive/%f %p'
recovery_target_time = '2025-10-21 10:30:00 UTC'
recovery_target_action = 'promote'
EOF

# 3. Start PostgreSQL (automatically enters recovery mode)
systemctl start postgresql
```

#### MySQL Restore

**From SQL Dump:**
```bash
# Full restore
mysql -h localhost -u root -p staging < /backups/production.sql

# Restore with progress
pv /backups/production.sql | mysql -h localhost -u root -p staging
```

**Point-in-Time Recovery:**
```bash
# 1. Restore base backup
mysql staging < /backups/production_base.sql

# 2. Apply binary logs up to specific point
mysqlbinlog --stop-datetime="2025-10-21 10:30:00" \
  /backups/binlogs/binlog.* | mysql -u root -p staging
```

#### MongoDB Restore

**From mongodump:**
```bash
# Full restore with oplog replay
mongorestore --host=localhost:27017 \
  --db=staging \
  --drop \
  --oplogReplay \
  --gzip \
  /backups/mongodb/production/

# Restore specific collection
mongorestore --host=localhost:27017 \
  --db=staging \
  --collection=users \
  /backups/mongodb/production/users.bson.gz
```

### Step 9: Apply Retention Policy

**GFS (Grandfather-Father-Son) Rotation:**

```bash
# Keep:
# - Daily backups: Last 7 days
# - Weekly backups: Last 4 weeks (Sundays)
# - Monthly backups: Last 12 months (1st of month)

# Implementation
BACKUP_DIR="/backups/postgres"
CURRENT_DATE=$(date +%Y%m%d)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
DAY_OF_MONTH=$(date +%d)

# Delete backups older than 7 days (except weekly/monthly)
find $BACKUP_DIR -name "*.dump" -mtime +7 -type f \
  ! -name "*-weekly-*" ! -name "*-monthly-*" -delete

# Delete weekly backups older than 4 weeks
find $BACKUP_DIR -name "*-weekly-*.dump" -mtime +28 -type f \
  ! -name "*-monthly-*" -delete

# Delete monthly backups older than 365 days
find $BACKUP_DIR -name "*-monthly-*.dump" -mtime +365 -type f -delete
```

**Simple Retention (Delete after N days):**

```bash
# Delete backups older than 30 days
find /backups/ -name "*.dump" -mtime +30 -type f -delete

# Cloud storage lifecycle (AWS S3)
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-backups \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json
{
  "Rules": [{
    "Id": "Delete old backups",
    "Status": "Enabled",
    "Prefix": "postgres/",
    "Expiration": {
      "Days": 30
    }
  }]
}
```

### Step 10: Cross-Environment Restore with Data Sanitization

**Production → Staging Restore:**

```bash
# 1. Restore base backup
pg_restore -h staging-db -U postgres -d staging \
  --clean --if-exists \
  /backups/production.dump

# 2. Sanitize sensitive data
psql -h staging-db -U postgres -d staging <<EOF
-- Anonymize email addresses
UPDATE users SET email = 'user' || id || '@staging.local';

-- Mask phone numbers
UPDATE users SET phone = '555-000-' || LPAD(id::text, 4, '0');

-- Reset passwords
UPDATE users SET password = crypt('staging123', gen_salt('bf'));

-- Clear API keys and tokens
UPDATE integrations SET api_key = NULL, api_secret = NULL;

-- Anonymize PII
UPDATE customers SET
  name = 'Customer ' || id,
  address = 'Address ' || id,
  ssn = NULL;
EOF
```

## PostgreSQL-Specific Features

### Advanced Backup Options

**Parallel Dump (Directory Format):**
```bash
# Dump with 4 parallel jobs
pg_dump -h localhost -U postgres -d production \
  --format=directory \
  --jobs=4 \
  --file=/backups/production_dir/

# Restore with 8 parallel jobs
pg_restore -h localhost -U postgres \
  --dbname=staging \
  --jobs=8 \
  --format=directory \
  /backups/production_dir/
```

**Selective Backup:**
```bash
# Backup specific schemas
pg_dump -h localhost -U postgres -d production \
  --schema=public \
  --schema=analytics \
  --file=/backups/schemas.dump

# Backup specific tables
pg_dump -h localhost -U postgres -d production \
  --table=users \
  --table=orders \
  --file=/backups/tables.dump

# Exclude specific tables
pg_dump -h localhost -U postgres -d production \
  --exclude-table=logs \
  --exclude-table=audit_trail \
  --file=/backups/production_no_logs.dump
```

**Continuous Archiving and PITR:**

```bash
# 1. Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backups/wal_archive/%f'
archive_timeout = 300  # Force WAL switch every 5 minutes

# 2. Take base backup
pg_basebackup -h localhost -U replication \
  --format=tar \
  --gzip \
  --wal-method=stream \
  --pgdata=/backups/base_backup/

# 3. Restore to specific point in time (see Step 8)
```

**Best Practices from Context7:**
- Use custom format (`-Fc`) for flexibility and compression
- Use directory format (`-Fd`) with `--jobs` for parallel dumps (large databases)
- Enable WAL archiving for point-in-time recovery
- Use `CREATE INDEX CONCURRENTLY` in restore to avoid locks
- Optimize server parameters before restore:
  ```sql
  -- Faster restore (disable during restore only!)
  ALTER SYSTEM SET maintenance_work_mem = '2GB';
  ALTER SYSTEM SET max_wal_size = '32GB';
  ALTER SYSTEM SET checkpoint_timeout = '60min';
  ALTER SYSTEM SET autovacuum = off;
  ALTER SYSTEM SET wal_compression = on;
  SELECT pg_reload_conf();
  ```

## MySQL-Specific Features

### Advanced Backup Options

**mysqldump Best Practices:**
```bash
# Full backup with all recommended flags
mysqldump -h localhost -u root -p \
  --single-transaction \
  --quick \
  --lock-tables=false \
  --routines \
  --triggers \
  --events \
  --set-gtid-purged=OFF \
  --default-character-set=utf8mb4 \
  --databases production \
  --result-file=/backups/production.sql

# All databases
mysqldump -h localhost -u root -p \
  --single-transaction \
  --quick \
  --all-databases \
  --result-file=/backups/all_databases.sql
```

**Binary Log Management:**
```bash
# Enable binary logging in my.cnf
[mysqld]
log_bin = /var/log/mysql/binlog
expire_logs_days = 7
max_binlog_size = 100M
binlog_format = ROW

# Flush binary logs
mysql -u root -p -e "FLUSH BINARY LOGS;"

# Backup binary logs
mysqlbinlog --read-from-remote-server \
  --raw \
  --host=localhost \
  --user=root \
  --password \
  --result-file=/backups/binlogs/ \
  binlog.000001

# Apply binary logs for PITR
mysqlbinlog --start-datetime="2025-10-21 00:00:00" \
            --stop-datetime="2025-10-21 10:30:00" \
  /backups/binlogs/binlog.* | mysql -u root -p staging
```

**Best Practices from Context7:**
- **Always use `--single-transaction`** for InnoDB (consistent backup without locks)
- Include `--routines --triggers --events` to backup all database objects
- Use `--quick` to avoid buffering tables in memory
- Backup binary logs separately for point-in-time recovery
- For large databases (>10GB), consider Percona XtraBackup or MySQL Enterprise Backup

## MongoDB-Specific Features

### Advanced Backup Options

**Replica Set Backup:**
```bash
# Backup from secondary (recommended)
mongodump --host=secondary:27017 \
  --readPreference=secondary \
  --oplog \
  --gzip \
  --out=/backups/mongodb/

# Verify replica set member
mongosh --eval "rs.status()" | grep -A5 "stateStr.*SECONDARY"
```

**Sharded Cluster Backup:**
```bash
# Use Percona Backup for MongoDB (PBM) for sharded clusters
pbm config --set storage.s3.bucket=my-backups
pbm config --set storage.s3.region=us-east-1
pbm backup

# Restore from PBM
pbm list
pbm restore 2025-10-21T10:30:00Z
```

**Selective Backup:**
```bash
# Backup specific collection
mongodump --host=localhost:27017 \
  --db=production \
  --collection=users \
  --out=/backups/mongodb/

# Backup with query filter
mongodump --host=localhost:27017 \
  --db=production \
  --collection=orders \
  --query='{"status": "completed"}' \
  --out=/backups/mongodb/
```

**Best Practices from Context7:**
- Use `--oplog` for point-in-time recovery (captures changes during backup)
- Run backups on secondary nodes to avoid production impact
- For replica sets, ensure `--oplog` captures consistent snapshot
- For sharded clusters (>100GB), use Percona Backup for MongoDB (PBM)
- Use `--gzip` for compression (BSON is not compressed by default)
- Monitor oplog window size (must be larger than backup duration)

## Cloud Platform Features

### AWS RDS Automated Backups

**Automated Backups:**
```bash
# Enable automated backups (1-35 days retention)
aws rds modify-db-instance \
  --db-instance-identifier production \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"

# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier production \
  --db-snapshot-identifier production-snapshot-$(date +%Y%m%d)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier staging \
  --db-snapshot-identifier production-snapshot-20251021
```

**Point-in-Time Recovery:**
```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier production \
  --target-db-instance-identifier recovery \
  --restore-time 2025-10-21T10:30:00Z

# Latest restorable time
aws rds describe-db-instances \
  --db-instance-identifier production \
  --query 'DBInstances[0].LatestRestorableTime'
```

**Best Practices from Context7:**
- Set backup retention to 7-35 days (7 days minimum recommended)
- Schedule backup window during off-peak hours (3-4 AM)
- Use both continuous backups (PITR) and snapshot backups
- Enable multi-AZ for automatic failover
- Take manual snapshots before major changes
- Test restore process regularly (quarterly recommended)

### GCP Cloud SQL Backups

**Automated Backups:**
```bash
# Enable automated backups
gcloud sql instances patch production \
  --backup-start-time=03:00 \
  --retained-backups-count=7

# Create on-demand backup
gcloud sql backups create \
  --instance=production \
  --description="Pre-deployment backup"

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=production \
  --backup-id=1634567890000
```

**Point-in-Time Recovery:**
```bash
# Enable PITR
gcloud sql instances patch production \
  --enable-point-in-time-recovery \
  --retained-transaction-log-days=7

# Restore to specific time
gcloud sql instances clone production staging \
  --point-in-time '2025-10-21T10:30:00.000Z'
```

**Best Practices from Context7:**
- Use enhanced backups for 99-year retention
- Enable point-in-time recovery (5-minute RPO)
- Schedule backups during off-peak hours
- Test cross-region restore capability
- Use final backups before instance deletion
- Ensure storage capacity ≥ 2x database size for restore

### Azure Database Backups

**Automated Backups:**
```bash
# Configure geo-redundant backups
az postgres server update \
  --resource-group mygroup \
  --name production \
  --backup-retention 35 \
  --geo-redundant-backup Enabled

# Restore to new server
az postgres server restore \
  --resource-group mygroup \
  --name staging \
  --source-server production \
  --restore-point-in-time 2025-10-21T10:30:00Z
```

## Security Features

### Encryption at Rest

**OpenSSL Encryption:**
```bash
# Encrypt backup
openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in /backups/production.dump \
  -out /backups/production.dump.enc \
  -pass file:/secure/backup.key

# Decrypt backup
openssl enc -aes-256-cbc -d -pbkdf2 \
  -in /backups/production.dump.enc \
  -out /backups/production.dump \
  -pass file:/secure/backup.key
```

### Secure Credential Handling

**PostgreSQL .pgpass:**
```bash
# Create .pgpass file
cat > ~/.pgpass <<EOF
localhost:5432:production:postgres:SecurePassword123
EOF
chmod 600 ~/.pgpass

# Backup without password prompt
pg_dump -h localhost -U postgres -d production -f backup.dump
```

**MySQL option file:**
```bash
# Create .my.cnf
cat > ~/.my.cnf <<EOF
[client]
user=root
password=SecurePassword123
host=localhost
EOF
chmod 600 ~/.my.cnf

# Backup without password prompt
mysqldump --defaults-extra-file=~/.my.cnf production > backup.sql
```

**MongoDB URI with credentials:**
```bash
# Store connection string in environment variable
export MONGO_URI="mongodb://user:pass@localhost:27017/production"

# Backup using URI
mongodump --uri="$MONGO_URI" --out=/backups/mongodb/
```

### Access Control

**IAM Roles (AWS):**
```bash
# Attach IAM policy to allow S3 backup uploads
aws iam attach-role-policy \
  --role-name backup-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Upload using IAM role (no access keys needed)
aws s3 cp backup.dump s3://my-backups/
```

## Backup Validation

### Integrity Checking

**Checksum Verification:**
```bash
# Generate checksums
md5sum /backups/*.dump > /backups/checksums.md5
sha256sum /backups/*.dump > /backups/checksums.sha256

# Verify integrity
md5sum -c /backups/checksums.md5
sha256sum -c /backups/checksums.sha256
```

### Restore Simulation

**Dry Run Testing:**
```bash
# PostgreSQL: List backup contents without restoring
pg_restore --list /backups/production.dump

# MySQL: Check SQL syntax without executing
mysql --verbose --force --dry-run < /backups/production.sql 2> errors.log

# MongoDB: Validate BSON files
bsondump --quiet /backups/mongodb/production/users.bson > /dev/null
```

**Test Restore to Temporary Database:**
```bash
# PostgreSQL
createdb backup_test
pg_restore -d backup_test /backups/production.dump
psql -d backup_test -c "SELECT COUNT(*) FROM users;" && echo "✓ Restore successful"
dropdb backup_test

# MySQL
mysql -e "CREATE DATABASE backup_test;"
mysql backup_test < /backups/production.sql
mysql -e "SELECT COUNT(*) FROM backup_test.users;" && echo "✓ Restore successful"
mysql -e "DROP DATABASE backup_test;"

# MongoDB
mongorestore --db=backup_test --drop /backups/mongodb/production/
mongosh --eval "use backup_test; db.users.countDocuments()" && echo "✓ Restore successful"
mongosh --eval "use backup_test; db.dropDatabase()"
```

## Retention Policies

### GFS (Grandfather-Father-Son) Rotation

**Implementation:**
```bash
#!/bin/bash
# GFS Backup Rotation Script

BACKUP_DIR="/backups/postgres"
CURRENT_DATE=$(date +%Y%m%d)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
DAY_OF_MONTH=$(date +%d)

# Perform backup
BACKUP_FILE="${BACKUP_DIR}/production_${CURRENT_DATE}.dump"
pg_dump -Fc production -f "$BACKUP_FILE"

# Tag backup type
if [ "$DAY_OF_MONTH" = "01" ]; then
  # Monthly backup (1st of month)
  cp "$BACKUP_FILE" "${BACKUP_DIR}/production_${CURRENT_DATE}_monthly.dump"
elif [ "$DAY_OF_WEEK" = "7" ]; then
  # Weekly backup (Sunday)
  cp "$BACKUP_FILE" "${BACKUP_DIR}/production_${CURRENT_DATE}_weekly.dump"
fi
# else: Daily backup (no additional tag)

# Cleanup old backups
# Delete daily backups older than 7 days
find "$BACKUP_DIR" -name "production_*.dump" -mtime +7 -type f \
  ! -name "*_weekly_*" ! -name "*_monthly_*" -delete

# Delete weekly backups older than 28 days (4 weeks)
find "$BACKUP_DIR" -name "*_weekly_*.dump" -mtime +28 -type f \
  ! -name "*_monthly_*" -delete

# Delete monthly backups older than 365 days (12 months)
find "$BACKUP_DIR" -name "*_monthly_*.dump" -mtime +365 -type f -delete

echo "Backup complete: $BACKUP_FILE"
```

### Cloud Storage Lifecycle Policies

**AWS S3 Lifecycle:**
```json
{
  "Rules": [
    {
      "Id": "Transition to Glacier",
      "Status": "Enabled",
      "Prefix": "postgres/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

**GCP Cloud Storage Lifecycle:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

## Monitoring and Alerting

### Backup Success Monitoring

**Email Alerts:**
```bash
#!/bin/bash
# Backup with email notification

BACKUP_FILE="/backups/production_$(date +%Y%m%d).dump"
pg_dump -Fc production -f "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "Backup successful: $BACKUP_FILE" | \
    mail -s "✓ Database Backup Successful" admin@company.com
else
  echo "Backup failed: $BACKUP_FILE" | \
    mail -s "✗ Database Backup FAILED" admin@company.com
fi
```

**Slack Integration:**
```bash
#!/bin/bash
# Send backup status to Slack

SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
BACKUP_FILE="/backups/production_$(date +%Y%m%d).dump"

pg_dump -Fc production -f "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"✓ Backup successful: $BACKUP_FILE ($BACKUP_SIZE)\"}"
else
  curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"✗ BACKUP FAILED: $BACKUP_FILE\"}"
fi
```

### Metrics Collection

**Backup Metrics (JSON):**
```bash
#!/bin/bash
# Collect backup metrics

BACKUP_FILE="/backups/production_$(date +%Y%m%d).dump"
START_TIME=$(date +%s)

pg_dump -Fc production -f "$BACKUP_FILE"
BACKUP_STATUS=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE")

# Export metrics as JSON
cat > /var/log/backup_metrics.json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "database": "production",
  "backup_file": "$BACKUP_FILE",
  "duration_seconds": $DURATION,
  "size_bytes": $BACKUP_SIZE,
  "status": "$BACKUP_STATUS",
  "success": $([ $BACKUP_STATUS -eq 0 ] && echo "true" || echo "false")
}
EOF
```

## Best Practices

### Context7-Verified Patterns

**From PostgreSQL Documentation (/websites/postgresql):**
- Use custom format (`-Fc`) or directory format (`-Fd`) for flexibility
- Enable parallel dumps/restores with `--jobs` for large databases
- Use `pg_basebackup` + WAL archiving for point-in-time recovery
- Always use `CREATE INDEX CONCURRENTLY` to avoid exclusive locks
- Optimize server parameters before restore (maintenance_work_mem, max_wal_size)

**From MySQL Documentation:**
- **Always use `--single-transaction`** for InnoDB (consistent backup without locks)
- Include `--routines --triggers --events` to backup all objects
- Backup binary logs separately for point-in-time recovery
- Use Percona XtraBackup for large databases (>10GB) or hot physical backups

**From MongoDB Documentation:**
- Use `--oplog` for point-in-time recovery capability
- Run backups on secondary nodes to avoid production impact
- For replica sets, ensure consistent snapshot with `--oplog`
- For sharded clusters, use Percona Backup for MongoDB (PBM)

**From AWS RDS Documentation:**
- Set backup retention to 7-35 days (7 days minimum recommended)
- Schedule backup windows during off-peak hours
- Use both continuous backups (PITR) and snapshot backups
- Enable multi-AZ for automatic failover
- Test restore process regularly (quarterly recommended)

**From GCP Cloud SQL Documentation:**
- Enable point-in-time recovery for 5-minute RPO
- Use enhanced backups for long-term retention (up to 99 years)
- Schedule backups during off-peak hours
- Ensure storage capacity ≥ 2x database size for restore

### 3-2-1 Backup Strategy

**Industry-Standard Disaster Recovery:**

- **3 Copies**: Original data + 2 backups
- **2 Media Types**: Different storage types (disk + cloud)
- **1 Offsite**: At least one copy in different location

**Implementation:**
```bash
# 1. Primary backup (local disk)
pg_dump -Fc production -f /backups/local/production.dump

# 2. Secondary backup (network storage)
rsync -avz /backups/local/ backup-server:/backups/remote/

# 3. Offsite backup (cloud storage)
aws s3 sync /backups/local/ s3://my-backups/postgres/
```

### Regular Testing

**Quarterly Restore Testing:**
```bash
#!/bin/bash
# Quarterly Restore Test Script

echo "Starting quarterly backup restore test..."

# 1. Get latest backup
LATEST_BACKUP=$(ls -t /backups/*.dump | head -1)
echo "Testing backup: $LATEST_BACKUP"

# 2. Create test database
createdb restore_test_$(date +%Y%m%d)

# 3. Restore backup
pg_restore -d restore_test_$(date +%Y%m%d) "$LATEST_BACKUP"

# 4. Verify data integrity
psql -d restore_test_$(date +%Y%m%d) <<EOF
SELECT 'User count: ' || COUNT(*) FROM users;
SELECT 'Order count: ' || COUNT(*) FROM orders;
EOF

# 5. Cleanup
dropdb restore_test_$(date +%Y%m%d)

echo "✓ Restore test complete"
```

**Automated Restore Validation:**
- Test restore monthly (minimum quarterly)
- Verify data integrity with row counts and checksums
- Test cross-region restore for disaster recovery
- Document restore procedures and RTO/RPO metrics

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Database Backup Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Backup Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: PostgreSQL 15.3 (production)
Type: Full backup
Started: 2025-10-21 03:00:00 UTC
Completed: 2025-10-21 03:45:23 UTC
Duration: 45 minutes 23 seconds

📁 Backup Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File: /backups/production_20251021.dump
Size: 12.5 GB (original: 45.3 GB)
Compression: gzip level 6 (72% reduction)
Encryption: AES-256 ✓
Format: Custom (pg_dump -Fc)
Parallel Jobs: 4

✅ Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Backup integrity verified (SHA-256 checksum)
✓ Restore simulation successful
✓ Data completeness: 100% (45.3M rows)
✓ Uploaded to S3: s3://my-backups/postgres/

📈 Performance Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backup Speed: 280 MB/min
Compression Ratio: 3.6:1
Upload Speed: 45 MB/s
Total I/O: 45.3 GB read, 12.5 GB written

🔄 Retention Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Policy: GFS (Grandfather-Father-Son)
Daily backups: 7 retained
Weekly backups: 4 retained
Monthly backups: 12 retained
Next cleanup: 2025-10-28

🎯 Recovery Point Objective (RPO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full Backup: 24 hours
WAL Archiving: 5 minutes (PITR enabled)
Latest Restorable Time: 2025-10-21 03:45:23 UTC
```

### Restore Report Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Database Restore Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Restore Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: PostgreSQL 15.3 (staging)
Source: s3://my-backups/production_20251021.dump
Type: Full restore
Started: 2025-10-21 10:00:00 UTC
Completed: 2025-10-21 10:32:15 UTC
Duration: 32 minutes 15 seconds

📁 Restore Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backup Date: 2025-10-21 03:45:23 UTC
Backup Size: 12.5 GB (compressed)
Restored Size: 45.3 GB
Parallel Jobs: 8
Format: Custom (pg_restore)

✅ Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Backup integrity verified
✓ Decompression successful
✓ Data completeness: 100% (45.3M rows)
✓ Indexes rebuilt: 287 indexes
✓ Constraints verified: 143 constraints

📈 Performance Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Restore Speed: 420 MB/min
Download Speed: 45 MB/s
Total I/O: 12.5 GB read, 45.3 GB written

🔍 Data Verification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Users: 1,234,567 rows ✓
Orders: 43,210,987 rows ✓
Products: 567,890 rows ✓
Total Tables: 127 tables restored

🎯 Recovery Time Objective (RTO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Target RTO: 60 minutes
Actual RTO: 32 minutes ✓ (53% faster)
Database Available: Yes
```

## Related Commands

- `/db:query-analyze` - Analyze SQL queries for performance bottlenecks
- `/db:db-optimize` - Comprehensive database optimization
- `/db:schema-migrate` - Database schema migrations with rollback
- `/cloud:cost-optimize` - Optimize cloud database and storage costs
- `/devops:disaster-recovery` - Complete DR planning and testing

## Troubleshooting

### PostgreSQL Issues

**Permission Denied:**
```bash
# Grant necessary permissions
psql -c "GRANT CONNECT ON DATABASE production TO backup_user;"
psql -c "GRANT USAGE ON SCHEMA public TO backup_user;"
psql -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;"

# Or use superuser/replication role
psql -c "ALTER USER backup_user WITH REPLICATION;"
```

**Out of Memory:**
```bash
# Reduce parallel jobs
pg_dump --jobs=2 ...

# Or split backup by schema
pg_dump --schema=public -f public.dump
pg_dump --schema=analytics -f analytics.dump
```

**Connection Timeout:**
```bash
# Increase timeout in connection string
pg_dump "postgresql://user@host/db?connect_timeout=300" -f backup.dump

# Or increase statement_timeout
psql -c "SET statement_timeout = '30min';"
```

### MySQL Issues

**Lock Wait Timeout:**
```bash
# Use --single-transaction to avoid locks
mysqldump --single-transaction --lock-tables=false ...

# Or increase lock wait timeout
mysql -e "SET GLOBAL innodb_lock_wait_timeout = 600;"
```

**Binary Log Position:**
```bash
# Record position at start of backup
mysqldump --master-data=2 ...

# Or use GTID for easier restore
mysqldump --set-gtid-purged=ON ...
```

### MongoDB Issues

**Oplog Window Too Small:**
```bash
# Check oplog size
mongosh --eval "db.getReplicationInfo()"

# Increase oplog size
mongosh --eval "db.adminCommand({replSetResizeOplog: 1, size: 10240})"  # 10GB
```

**Insufficient Disk Space:**
```bash
# Backup directly to cloud (skip local disk)
mongodump --archive | gzip | aws s3 cp - s3://backups/mongo.archive.gz

# Or use --gzip to compress on-the-fly
mongodump --gzip --out=/backups/mongodb/
```

### Cloud Storage Issues

**Upload Failed (Network Error):**
```bash
# Retry with exponential backoff
aws s3 cp backup.dump s3://backups/ --cli-connect-timeout 300 --cli-read-timeout 300

# Or use multipart upload for large files
aws s3 cp backup.dump s3://backups/ --multipart-chunk-size 100MB
```

**Access Denied (IAM):**
```bash
# Verify IAM permissions
aws s3 ls s3://my-backups/

# Check bucket policy
aws s3api get-bucket-policy --bucket my-backups
```

## Version History

- v2.0.0 - Initial Schema v2.0 release
  - Multi-database support (PostgreSQL, MySQL, MongoDB, BigQuery)
  - Context7-verified backup best practices
  - Cloud storage integration (AWS S3, GCS, Azure Blob)
  - Encryption and compression support
  - Point-in-time recovery (PITR)
  - GFS retention policies
  - Backup validation and restore simulation
  - Cross-environment restore with data sanitization
