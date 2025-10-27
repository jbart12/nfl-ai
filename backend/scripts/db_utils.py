"""
Database Utilities

Common database operations and helper functions.

Usage:
    # Check database status
    python -m scripts.db_utils status

    # Count records in all tables
    python -m scripts.db_utils count

    # Clear all data (WARNING: destructive!)
    python -m scripts.db_utils clear --confirm

    # Reset database (drop all, recreate, run migrations)
    python -m scripts.db_utils reset --confirm
"""
import asyncio
import sys
from pathlib import Path
import argparse

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.nfl import (
    Player,
    Team,
    Game,
    PlayerGameStats,
    PrizePicksProjection,
    TeamDefensiveStats,
    PlayerInjury,
    Prediction
)
import structlog

logger = structlog.get_logger()


async def check_database_status():
    """Check database connection and status"""
    print("Database Status Check")
    print("=" * 60)

    try:
        async with AsyncSessionLocal() as session:
            # Test connection
            result = await session.execute(text("SELECT 1"))
            print("✓ Database connection: OK")

            # Check if migrations have been run
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM alembic_version"))
                version_count = result.scalar()
                if version_count > 0:
                    result = await session.execute(text("SELECT version_num FROM alembic_version"))
                    version = result.scalar()
                    print(f"✓ Alembic migrations: Applied (version: {version})")
                else:
                    print("⚠ Alembic migrations: Not applied")
            except:
                print("✗ Alembic migrations: Table does not exist")

            print("\n" + "=" * 60)
            return True

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        logger.error("database_status_check_failed", error=str(e))
        return False


async def count_all_records():
    """Count records in all tables"""
    print("Record Counts")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        tables = [
            ("Teams", Team),
            ("Players", Player),
            ("Games", Game),
            ("Player Game Stats", PlayerGameStats),
            ("PrizePicks Projections", PrizePicksProjection),
            ("Team Defensive Stats", TeamDefensiveStats),
            ("Player Injuries", PlayerInjury),
            ("Predictions", Prediction),
        ]

        total_records = 0

        for table_name, model in tables:
            result = await session.execute(select(func.count()).select_from(model))
            count = result.scalar()
            total_records += count
            print(f"  {table_name:.<40} {count:>10,}")

        print("=" * 60)
        print(f"  {'Total Records':.<40} {total_records:>10,}")
        print("=" * 60)


async def clear_all_data():
    """Clear all data from all tables (keeps schema)"""
    print("Clearing All Data")
    print("=" * 60)
    print("⚠ WARNING: This will delete ALL data from the database!")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # Delete in reverse dependency order
            tables = [
                ("Predictions", Prediction),
                ("Player Injuries", PlayerInjury),
                ("Team Defensive Stats", TeamDefensiveStats),
                ("PrizePicks Projections", PrizePicksProjection),
                ("Player Game Stats", PlayerGameStats),
                ("Games", Game),
                ("Players", Player),
                ("Teams", Team),
            ]

            for table_name, model in tables:
                result = await session.execute(select(func.count()).select_from(model))
                count = result.scalar()

                if count > 0:
                    await session.execute(text(f"DELETE FROM {model.__tablename__}"))
                    print(f"  ✓ Cleared {table_name} ({count:,} records)")
                else:
                    print(f"  - {table_name} (already empty)")

            await session.commit()
            print("\n✓ All data cleared successfully")

        except Exception as e:
            await session.rollback()
            print(f"\n✗ Error clearing data: {e}")
            logger.error("clear_data_error", error=str(e))
            raise


async def reset_database():
    """Drop all tables and recreate schema"""
    print("Resetting Database")
    print("=" * 60)
    print("⚠ WARNING: This will DROP ALL TABLES and recreate the schema!")
    print("=" * 60)

    try:
        # Drop all tables
        print("\n1. Dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("   ✓ All tables dropped")

        # Create all tables
        print("\n2. Creating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✓ All tables created")

        print("\n3. You should now run Alembic migrations:")
        print("   cd backend && alembic upgrade head")

        print("\n✓ Database reset completed")

    except Exception as e:
        print(f"\n✗ Error resetting database: {e}")
        logger.error("reset_database_error", error=str(e))
        raise


async def show_sample_data():
    """Show sample data from key tables"""
    print("Sample Data")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # Teams
        print("\nTeams (first 5):")
        result = await session.execute(select(Team).limit(5))
        teams = result.scalars().all()
        for team in teams:
            print(f"  {team.id:.<5} {team.city} {team.name} ({team.conference} {team.division})")

        # Players
        print("\nPlayers (first 5):")
        result = await session.execute(select(Player).limit(5))
        players = result.scalars().all()
        for player in players:
            print(f"  {player.name:.<25} {player.player_position:.<4} {player.team_id or 'FA'}")

        # Recent predictions
        print("\nRecent Predictions (last 5):")
        result = await session.execute(
            select(Prediction)
            .order_by(Prediction.created_at.desc())
            .limit(5)
        )
        predictions = result.scalars().all()
        for pred in predictions:
            print(f"  {pred.prediction:.<6} Confidence: {pred.confidence}% (created: {pred.created_at})")

        if not predictions:
            print("  (No predictions yet)")

        print("\n" + "=" * 60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Database utilities")
    parser.add_argument(
        "command",
        choices=["status", "count", "clear", "reset", "sample"],
        help="Command to run"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm destructive operations"
    )

    args = parser.parse_args()

    print("NFL AI Database Utilities")
    print("=" * 60)

    try:
        if args.command == "status":
            await check_database_status()

        elif args.command == "count":
            await count_all_records()

        elif args.command == "sample":
            await show_sample_data()

        elif args.command == "clear":
            if not args.confirm:
                print("ERROR: --confirm flag required for destructive operations")
                sys.exit(1)
            await clear_all_data()

        elif args.command == "reset":
            if not args.confirm:
                print("ERROR: --confirm flag required for destructive operations")
                sys.exit(1)
            await reset_database()

        print("\n✓ Operation completed successfully")

    except Exception as e:
        print(f"\n✗ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
