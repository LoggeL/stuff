from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import shortuuid
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association tables for many-to-many relationships
item_tags = db.Table('item_tags',
    db.Column('item_id', db.String(22), db.ForeignKey('items.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

item_subitems = db.Table('item_subitems',
    db.Column('parent_id', db.String(22), db.ForeignKey('items.id')),
    db.Column('child_id', db.String(22), db.ForeignKey('items.id'))
)

# Association table for item links
item_links = db.Table('item_links',
    db.Column('item_a_id', db.String(22), db.ForeignKey('items.id', ondelete='CASCADE'), primary_key=True),
    db.Column('item_b_id', db.String(22), db.ForeignKey('items.id', ondelete='CASCADE'), primary_key=True)
)

# User roles association table
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.String(22), primary_key=True, default=lambda: shortuuid.uuid()[:8])
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.String(22), db.ForeignKey('locations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('Item', back_populates='location', lazy=True)
    parent = db.relationship('Location', remote_side=[id], backref=db.backref('children', lazy=True))

    def __repr__(self):
        return f'<Location {self.name}>'

class ItemCategory(db.Model):
    __tablename__ = 'item_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Bootstrap icon name
    color = db.Column(db.String(20))  # Bootstrap color class (primary, success, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    item_types = db.relationship('ItemType', backref='category', lazy=True)

class ItemType(db.Model):
    __tablename__ = 'item_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('item_categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    properties = db.relationship('ItemProperty', back_populates='item_type', lazy=True, cascade='all, delete-orphan')
    items = db.relationship('Item', back_populates='item_type', lazy=True)

class ItemProperty(db.Model):
    __tablename__ = 'item_properties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50), nullable=False)  # text, number, boolean, date, image, item_link
    required = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(500))
    options = db.Column(db.JSON)  # For storing options like select choices
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add validation for property types
    VALID_PROPERTY_TYPES = ['text', 'number', 'boolean', 'date', 'image', 'item_link']

    def __init__(self, *args, **kwargs):
        if 'property_type' in kwargs and kwargs['property_type'] not in self.VALID_PROPERTY_TYPES:
            raise ValueError(f"Invalid property type. Must be one of: {', '.join(self.VALID_PROPERTY_TYPES)}")
        super().__init__(*args, **kwargs)

    item_type = db.relationship('ItemType', back_populates='properties')
    values = db.relationship('ItemPropertyValue', back_populates='property', cascade='all, delete-orphan')

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.String(22), primary_key=True, default=lambda: shortuuid.uuid()[:8])
    name = db.Column(db.String(100), nullable=False)
    location_id = db.Column(db.String(22), db.ForeignKey('locations.id'))
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = db.relationship('Location', back_populates='items')
    item_type = db.relationship('ItemType', back_populates='items')
    property_values = db.relationship('ItemPropertyValue', 
                                   back_populates='item', 
                                   foreign_keys='ItemPropertyValue.item_id',
                                   cascade='all, delete-orphan')
    
    # Many-to-many relationships
    tags = db.relationship('Tag', secondary=item_tags, back_populates='items')
    
    # Self-referential many-to-many relationship for subitems
    subitems = db.relationship(
        'Item',
        secondary=item_subitems,
        primaryjoin=(id == item_subitems.c.parent_id),
        secondaryjoin=(id == item_subitems.c.child_id),
        back_populates='parent_items'
    )
    parent_items = db.relationship(
        'Item',
        secondary=item_subitems,
        primaryjoin=(id == item_subitems.c.child_id),
        secondaryjoin=(id == item_subitems.c.parent_id),
        back_populates='subitems'
    )

    # New relationship for linked items
    linked_items = db.relationship(
        'Item',
        secondary=item_links,
        primaryjoin=id==item_links.c.item_a_id,
        secondaryjoin=id==item_links.c.item_b_id,
        backref=db.backref('linked_by_items', lazy='dynamic'),
        lazy='dynamic'
    )

    def get_property_value(self, property_name):
        for value in self.property_values:
            if value.property.name == property_name:
                return value.get_typed_value()
        return None

    def set_property_value(self, property_name, value):
        for prop_value in self.property_values:
            if prop_value.property.name == property_name:
                prop_value.set_typed_value(value)
                return
        
        # If property value doesn't exist, create new one
        property = ItemProperty.query.filter_by(item_type_id=self.item_type_id, name=property_name).first()
        if property:
            prop_value = ItemPropertyValue(property=property, item=self)
            prop_value.set_typed_value(value)
            self.property_values.append(prop_value)

    def __repr__(self):
        return f'<Item {self.name}>' 

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(20), default='secondary')  # Bootstrap color class
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('Item', secondary=item_tags, back_populates='tags', lazy='dynamic')

    def __repr__(self):
        return f'<Tag {self.name}>'

class ItemPropertyValue(db.Model):
    __tablename__ = 'item_property_values'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(22), db.ForeignKey('items.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('item_properties.id'), nullable=False)
    value_text = db.Column(db.Text)
    value_number = db.Column(db.Float)
    value_boolean = db.Column(db.Boolean)
    value_date = db.Column(db.DateTime)
    value_item_id = db.Column(db.String(22), db.ForeignKey('items.id'))  # For item_link type
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    item = db.relationship('Item', 
                          back_populates='property_values', 
                          foreign_keys=[item_id])
    property = db.relationship('ItemProperty', back_populates='values')
    linked_item = db.relationship('Item', 
                                foreign_keys=[value_item_id])

    def get_typed_value(self):
        if self.property.property_type == 'text':
            return self.value_text
        elif self.property.property_type == 'number':
            return self.value_number
        elif self.property.property_type == 'boolean':
            return self.value_boolean
        elif self.property.property_type == 'date':
            return int(self.value_date.timestamp()) if self.value_date else None
        elif self.property.property_type == 'item_link':
            return self.linked_item
        return None

    def set_typed_value(self, value):
        if self.property.property_type == 'text':
            self.value_text = str(value)
        elif self.property.property_type == 'number':
            self.value_number = float(value)
        elif self.property.property_type == 'boolean':
            self.value_boolean = bool(value)
        elif self.property.property_type == 'date':
            if isinstance(value, (int, float)):
                self.value_date = datetime.fromtimestamp(value)
            elif isinstance(value, str):
                try:
                    # Try parsing as timestamp first
                    self.value_date = datetime.fromtimestamp(float(value))
                except ValueError:
                    # If that fails, try various date formats
                    try:
                        self.value_date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            self.value_date = datetime.strptime(value, '%a, %d %b %Y %H:%M:%S %Z')
                        except ValueError:
                            self.value_date = None
            elif isinstance(value, datetime):
                self.value_date = value
            else:
                self.value_date = None
        elif self.property.property_type == 'item_link':
            if isinstance(value, str):
                self.value_item_id = value
            elif isinstance(value, Item):
                self.value_item_id = value.id
            else:
                self.value_item_id = None

    def __repr__(self):
        return f'<ItemPropertyValue {self.property.name}: {self.get_typed_value()}>' 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                          backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission):
        return any(permission in role.permissions for role in self.roles)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    permissions = db.Column(db.JSON, default=list)  # List of permission strings
    description = db.Column(db.String(255)) 