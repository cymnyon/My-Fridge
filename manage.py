from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import app, db  # Import the Flask app and SQLAlchemy object

# Create the migration object and associate it with your app and database
migrate = Migrate(app, db)

# Create the manager object to handle commands
manager = Manager(app)

# Add the MigrateCommand to the manager to handle migration commands
manager.add_command('db', MigrateCommand)

# Run the manager to execute commands
if __name__ == '__main__':
    manager.run()