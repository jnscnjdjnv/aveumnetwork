from migrations.add_balance_column import upgrade

if __name__ == '__main__':
    upgrade()
    print("Balance column migration completed successfully!") 