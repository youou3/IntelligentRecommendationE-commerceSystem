from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.core.database import db
import app.models  # noqa: F401


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print('MySQL tables created successfully.')
