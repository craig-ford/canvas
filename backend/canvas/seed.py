"""
Seed script for Canvas application.

This script creates development users and sample data.
"""
import asyncio
import json
import sys
import os
from canvas.db import AsyncSessionLocal

# Configuration from environment variables
SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
SEED_ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Admin User")
SEED_GM_EMAIL = os.getenv("SEED_GM_EMAIL", "gm@example.com")
SEED_GM_NAME = os.getenv("SEED_GM_NAME", "General Manager")
SEED_VBU_NAME = os.getenv("SEED_VBU_NAME", "Sample VBU")
SEED_PRODUCT_NAME = os.getenv("SEED_PRODUCT_NAME", "Sample Product")

# BLOCKED: awaiting 001-auth/T-011 for User model
# BLOCKED: awaiting 002-canvas-management/T-003 for VBU, Canvas models

async def seed_users():
    """Create dev users if they don't exist."""
    # BLOCKED: awaiting User model from 001-auth/T-011
    print(json.dumps({"error": "BLOCKED: awaiting User model from 001-auth/T-011"}))
    return False

async def seed_sample_data():
    """Create sample VBUs and canvases if they don't exist."""
    # BLOCKED: awaiting VBU, Canvas models from 002-canvas-management/T-003
    print(json.dumps({"error": "BLOCKED: awaiting VBU, Canvas models from 002-canvas-management/T-003"}))
    return False

async def main():
    """Main seed function - idempotent."""
    try:
        users_created = await seed_users()
        sample_data_created = await seed_sample_data()
        
        if not users_created and not sample_data_created:
            print(json.dumps({
                "status": "blocked",
                "message": "Seed script blocked on missing models from other features"
            }))
            return
            
        print(json.dumps({
            "status": "success",
            "users_created": users_created,
            "sample_data_created": sample_data_created
        }))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())