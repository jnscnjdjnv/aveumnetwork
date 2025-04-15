from migrations.add_is_mining_column import upgrade

if __name__ == "__main__":
    print("Running database migration to add is_mining column...")
    upgrade()
    print("Migration completed successfully!") 