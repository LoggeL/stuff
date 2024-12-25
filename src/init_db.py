from app import app, db
from models import User, Role, Location, ItemType, ItemProperty, ItemCategory, Item, ItemPropertyValue, ItemFile
from werkzeug.security import generate_password_hash
import os
import shutil
from datetime import datetime

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create roles
        admin_role = Role(name='admin', permissions=[
            'manage_users',
            'view_items', 'add_items', 'edit_items', 'delete_items',
            'view_locations', 'add_locations', 'edit_locations', 'delete_locations',
            'view_tags', 'add_tags', 'edit_tags', 'delete_tags',
            'view_item_types', 'add_item_types', 'edit_item_types', 'delete_item_types'
        ])
        user_role = Role(name='user', permissions=[
            'view_items', 'add_items',
            'view_locations',
            'view_tags',
            'view_item_types'
        ])
        db.session.add(admin_role)
        db.session.add(user_role)
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin'),
            is_active=True
        )
        admin.roles.append(admin_role)
        db.session.add(admin)
        
        # Create locations
        hauptlager = Location(name='Hauptlager', description='Hauptlagerraum für Kostüme und Requisiten')
        kostuemlager = Location(name='Kostümlager', description='Speziallager für historische Kostüme')
        requisitenlager = Location(name='Requisitenlager', description='Lager für Bühnenrequisiten')
        schneiderei = Location(name='Schneiderei', description='Werkstatt für Kostümanfertigungen')
        buehnenbildlager = Location(name='Bühnenbildlager', description='Lager für Bühnenbilder und große Requisiten')
        
        db.session.add_all([hauptlager, kostuemlager, requisitenlager, schneiderei, buehnenbildlager])
        
        # Create categories
        kostueme = ItemCategory(name='Kostüme', description='Theaterkostüme und Accessoires', icon='person-badge', color='primary')
        requisiten = ItemCategory(name='Requisiten', description='Bühnenrequisiten und Kleinteile', icon='box', color='success')
        buehne = ItemCategory(name='Bühnenbild', description='Bühnenbilder und Kulissen', icon='easel', color='info')
        technik = ItemCategory(name='Technik', description='Technische Ausrüstung', icon='gear', color='warning')
        
        db.session.add_all([kostueme, requisiten, buehne, technik])
        
        # Create item types with their properties
        historisches_kostuem = ItemType(name='Historisches Kostüm', description='Historische Theaterkostüme', category=kostueme)
        historisches_kostuem_props = [
            ItemProperty(name='Epoche', property_type='text', required=True, item_type=historisches_kostuem,
                        options=['Mittelalter', 'Renaissance', 'Barock', 'Rokoko', 'Biedermeier', '20er Jahre']),
            ItemProperty(name='Größe', property_type='text', required=True, item_type=historisches_kostuem,
                        options=['XS', 'S', 'M', 'L', 'XL', 'XXL']),
            ItemProperty(name='Geschlecht', property_type='text', required=True, item_type=historisches_kostuem,
                        options=['Damen', 'Herren', 'Unisex']),
            ItemProperty(name='Material', property_type='text', required=True, item_type=historisches_kostuem),
            ItemProperty(name='Zustand', property_type='text', required=True, item_type=historisches_kostuem,
                        options=['Neu', 'Sehr gut', 'Gut', 'Gebraucht', 'Restaurierungsbedürftig']),
            ItemProperty(name='Letzte Reinigung', property_type='date', required=False, item_type=historisches_kostuem)
        ]
        
        requisite = ItemType(name='Requisite', description='Einzelne Requisiten', category=requisiten)
        requisite_props = [
            ItemProperty(name='Material', property_type='text', required=True, item_type=requisite,
                        options=['Holz', 'Metall', 'Kunststoff', 'Stoff', 'Papier', 'Gemischt']),
            ItemProperty(name='Maße (cm)', property_type='text', required=True, item_type=requisite),
            ItemProperty(name='Gewicht (kg)', property_type='number', required=False, item_type=requisite),
            ItemProperty(name='Zustand', property_type='text', required=True, item_type=requisite,
                        options=['Neu', 'Sehr gut', 'Gut', 'Gebraucht', 'Restaurierungsbedürftig'])
        ]
        
        kulisse = ItemType(name='Kulisse', description='Bühnenbilder und Kulissenteile', category=buehne)
        kulisse_props = [
            ItemProperty(name='Art', property_type='text', required=True, item_type=kulisse,
                        options=['Backdrop', 'Seitenteil', 'Versatzstück', 'Möbel', 'Komplettes Set']),
            ItemProperty(name='Maße (m)', property_type='text', required=True, item_type=kulisse),
            ItemProperty(name='Material', property_type='text', required=True, item_type=kulisse),
            ItemProperty(name='Aufbauzeit (min)', property_type='number', required=True, item_type=kulisse),
            ItemProperty(name='Personen für Aufbau', property_type='number', required=True, item_type=kulisse)
        ]
        
        db.session.add_all([historisches_kostuem] + historisches_kostuem_props + 
                          [requisite] + requisite_props +
                          [kulisse] + kulisse_props)
        
        # Create demo items with their images
        items = [
            {
                'name': 'Rokoko Ballkleid',
                'type': historisches_kostuem,
                'location': kostuemlager,
                'image': 'rokoko_ballkleid.jpg',
                'properties': {
                    'Epoche': 'Rokoko',
                    'Größe': 'M',
                    'Geschlecht': 'Damen',
                    'Material': 'Seide, Spitze',
                    'Zustand': 'Sehr gut',
                    'Letzte Reinigung': '2023-12-01'
                }
            },
            {
                'name': 'Mittelalter Gewandung',
                'type': historisches_kostuem,
                'location': kostuemlager,
                'image': 'mittelalter_gewandung.jpg',
                'properties': {
                    'Epoche': 'Mittelalter',
                    'Größe': 'L',
                    'Geschlecht': 'Herren',
                    'Material': 'Leinen, Wolle',
                    'Zustand': 'Gut',
                    'Letzte Reinigung': '2023-11-15'
                }
            },
            {
                'name': 'Antiker Kerzenleuchter',
                'type': requisite,
                'location': requisitenlager,
                'image': 'kerzenleuchter.jpg',
                'properties': {
                    'Material': 'Metall',
                    'Maße (cm)': '30x30x50',
                    'Gewicht (kg)': 2.5,
                    'Zustand': 'Sehr gut'
                }
            },
            {
                'name': 'Venezianische Maske',
                'type': requisite,
                'location': requisitenlager,
                'image': 'venezianische_maske.jpg',
                'properties': {
                    'Material': 'Papier',
                    'Maße (cm)': '20x15x10',
                    'Gewicht (kg)': 0.2,
                    'Zustand': 'Neu'
                }
            },
            {
                'name': 'Waldkulisse',
                'type': kulisse,
                'location': buehnenbildlager,
                'image': 'waldkulisse.jpg',
                'properties': {
                    'Art': 'Backdrop',
                    'Maße (m)': '8x6',
                    'Material': 'Bemalte Leinwand',
                    'Aufbauzeit (min)': 45,
                    'Personen für Aufbau': 3
                }
            }
        ]
        
        # Add items with their properties and images
        for item_data in items:
            item = Item(
                name=item_data['name'],
                location=item_data['location'],
                item_type=item_data['type']
            )
            db.session.add(item)
            
            # Add property values
            for prop in item_data['type'].properties:
                if prop.name in item_data['properties']:
                    value = ItemPropertyValue(
                        item=item,
                        property=prop
                    )
                    value.set_typed_value(item_data['properties'][prop.name])
                    db.session.add(value)
            
            # Add image file if it exists
            if 'image' in item_data:
                image_path = os.path.join('uploads', 'items', item_data['image'])
                if os.path.exists(os.path.join(app.static_folder, image_path)):
                    file = ItemFile(
                        filename=image_path,
                        original_filename=item_data['image'],
                        mime_type='image/jpeg',
                        size=os.path.getsize(os.path.join(app.static_folder, image_path)),
                        item=item
                    )
                    db.session.add(file)
        
        # Commit all changes
        db.session.commit()

if __name__ == '__main__':
    init_db() 