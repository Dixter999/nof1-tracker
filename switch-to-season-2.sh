#!/bin/bash
# Script to transition NOF1 Tracker to Season 2
# Run this script when Alpha Arena Season 2 actually starts

set -e  # Exit on any error

echo "=========================================="
echo "NOF1 Tracker - Switch to Season 2"
echo "=========================================="
echo ""

# Step 1: Stop the monitor
echo "Step 1: Stopping Season 1.5 monitor..."
docker stop nof1-tracker-monitor
echo "✅ Monitor stopped"
echo ""

# Step 2: Update code to Season 2
echo "Step 2: Updating code to Season 2..."
sed -i 's/get_or_create_season("1.5")/get_or_create_season("2")/g' \
  /home/dixter/Projects/nof1-tracker/src/nof1_tracker/scraper/runner.py
echo "✅ Code updated"
echo ""

# Step 3: Rebuild Docker image
echo "Step 3: Rebuilding Docker image..."
docker compose build monitor
echo "✅ Image rebuilt"
echo ""

# Step 4: Start Season 2 monitor
echo "Step 4: Starting Season 2 monitor..."
docker compose --profile monitor up -d
echo "✅ Season 2 monitor started"
echo ""

# Step 5: Verify Season 2 is running
echo "Step 5: Verifying Season 2 scraping..."
sleep 10
docker logs --tail 20 nof1-tracker-monitor
echo ""

echo "=========================================="
echo "✅ Successfully switched to Season 2!"
echo "=========================================="
echo ""
echo "Monitor will scrape Season 2 every 15 minutes"
echo ""
echo "To check logs: docker logs -f nof1-tracker-monitor"
echo "To check database: Use the database queries below"
echo ""
