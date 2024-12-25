import pytest
import os
import tempfile
from src.app import app as flask_app
from src.models import db, Location, Item, Tag

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def sample_data(app):
    with app.app_context():
        # Clear existing data
        db.session.query(Item).delete()
        db.session.query(Tag).delete()
        db.session.query(Location).delete()
        db.session.commit()

        # Create test locations
        location1 = Location(name='Test Location 1')
        location2 = Location(name='Test Location 2')
        db.session.add_all([location1, location2])
        db.session.commit()

        # Create test tags
        tag1 = Tag(name='test-tag-1')
        tag2 = Tag(name='test-tag-2')
        db.session.add_all([tag1, tag2])
        db.session.commit()

        # Create test items
        item1 = Item(
            name='Test Item 1',
            quantity=5,
            description='Test Description 1',
            location_id=location1.id
        )
        item1.tags.append(tag1)

        item2 = Item(
            name='Test Item 2',
            quantity=3,
            description='Test Description 2',
            location_id=location2.id
        )
        item2.tags.extend([tag1, tag2])

        db.session.add_all([item1, item2])
        db.session.commit()

        return {
            'locations': [location1, location2],
            'tags': [tag1, tag2],
            'items': [item1, item2]
        } 