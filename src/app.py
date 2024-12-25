from flask import Flask, request, jsonify, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import os
from models import db, Location, Item, Tag, ItemType, ItemProperty, ItemPropertyValue, ItemCategory, User, Role
from datetime import timedelta, datetime
from functools import wraps
import qrcode
from PIL import Image
from io import BytesIO
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy import and_
from sqlalchemy.orm import aliased
import mimetypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
            static_url_path='/static')
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')  # Change in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['PORT'] = int(os.environ.get('FLASK_PORT', 5000))
app.config['HOST'] = os.environ.get('FLASK_HOST', '127.0.0.1')
jwt = JWTManager(app)

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token error: {error}")
    return jsonify({'error': 'Invalid token'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"Expired token error: {jwt_payload}")
    return jsonify({'error': 'Token has expired'}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    print(f"Unauthorized error: {error}")
    return jsonify({'error': 'No token provided'}), 401

# Database configuration
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'pictures')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'items'), exist_ok=True)

db.init_app(app)

def require_permission(permission):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            if not user or not user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 401

    # Create access token with user's roles and permissions
    roles = [role.name for role in user.roles]
    permissions = []
    for role in user.roles:
        permissions.extend(role.permissions)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'roles': roles,
            'permissions': list(set(permissions))
        }
    )

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': roles,
            'permissions': list(set(permissions))
        }
    })

@app.route('/api/auth/register', methods=['POST'])
@jwt_required()
@require_permission('manage_users')
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    # Assign roles
    if 'roles' in data:
        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [role.name for role in user.roles]
        }
    })

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': [role.name for role in user.roles],
        'permissions': list(set(
            permission
            for role in user.roles
            for permission in role.permissions
        ))
    })

# Protect existing routes with JWT and permissions
@app.route('/api/items', methods=['GET', 'POST'])
@jwt_required()
def get_or_create_items():
    if request.method == 'GET':
        try:
            # Build query
            query = Item.query

            # Apply search filter
            if request.args.get('search'):
                search = f"%{request.args.get('search')}%"
                query = query.filter(Item.name.ilike(search))

            # Apply location filter
            if request.args.get('location_id'):
                query = query.filter(Item.location_id == request.args.get('location_id'))

            # Apply item type filter
            if request.args.get('item_type_id'):
                query = query.filter(Item.item_type_id == request.args.get('item_type_id'))

            # Apply property filters
            for key, value in request.args.items():
                if key.startswith('property_'):
                    try:
                        property_id = int(key.split('_')[1])
                        # Join with property values and filter
                        query = query.join(ItemPropertyValue).filter(
                            ItemPropertyValue.property_id == property_id,
                            ItemPropertyValue.value_text.ilike(f'%{value}%')
                        )
                    except (ValueError, IndexError):
                        continue

            # Execute query and get items
            items = query.all()

            # Get files for each item
            result = []
            for item in items:
                # Get item files
                type_folder = secure_filename(item.item_type.name.lower())
                item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item.id)
                files = []
                if os.path.exists(item_folder):
                    for filename in os.listdir(item_folder):
                        file_path = os.path.join(item_folder, filename)
                        if os.path.isfile(file_path):
                            files.append(get_file_info(item.id, type_folder, filename, file_path))

                result.append({
                    'id': item.id,
                    'name': item.name,
                    'location_id': item.location_id,
                    'item_type_id': item.item_type_id,
                    'created_at': item.created_at.isoformat(),
                    'location': {
                        'id': item.location.id,
                        'name': item.location.name
                    } if item.location else None,
                    'item_type': {
                        'id': item.item_type.id,
                        'name': item.item_type.name
                    },
                    'property_values': [{
                        'property_id': value.property_id,
                        'property_name': value.property.name,
                        'property_type': value.property.property_type,
                        'value': value.get_typed_value()
                    } for value in item.property_values],
                    'files': files
                })

            return jsonify(result)

        except Exception as e:
            print(f"Error fetching items: {str(e)}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403

        try:
            data = request.json
            if not data or not data.get('name') or not data.get('item_type_id'):
                return jsonify({'error': 'Name and Item Type are required'}), 400

            # Create new item
            item = Item(
                name=data['name'],
                location_id=data.get('location_id'),
                item_type_id=data['item_type_id']
            )
            db.session.add(item)

            # Add property values
            if 'property_values' in data:
                for pv_data in data['property_values']:
                    # Get the property first
                    property = ItemProperty.query.get(pv_data['property_id'])
                    if property and property.item_type_id == item.item_type_id:
                        value = ItemPropertyValue(
                            item=item,
                            property=property
                        )
                        value.set_typed_value(pv_data['value'])
                        db.session.add(value)

            db.session.commit()

            return jsonify({
                'id': item.id,
                'name': item.name,
                'location_id': item.location_id,
                'item_type_id': item.item_type_id,
                'created_at': item.created_at.isoformat(),
                'location': {
                    'id': item.location.id,
                    'name': item.location.name
                } if item.location else None,
                'item_type': {
                    'id': item.item_type.id,
                    'name': item.item_type.name
                },
                'property_values': [{
                    'property_id': value.property_id,
                    'property_name': value.property.name,
                    'property_type': value.property.property_type,
                    'value': value.get_typed_value()
                } for value in item.property_values],
                'files': []
            }), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating item: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def get_update_delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'GET':
        # Get files from filesystem
        type_folder = secure_filename(item.item_type.name.lower())
        item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
        files = []
        if os.path.exists(item_folder):
            for filename in os.listdir(item_folder):
                file_path = os.path.join(item_folder, filename)
                if os.path.isfile(file_path):
                    files.append(get_file_info(item_id, type_folder, filename, file_path))

        return jsonify({
            'id': item.id,
            'name': item.name,
            'location_id': item.location_id,
            'item_type_id': item.item_type_id,
            'created_at': item.created_at.isoformat(),
            'location': {
                'id': item.location.id,
                'name': item.location.name
            } if item.location else None,
            'item_type': {
                'id': item.item_type.id,
                'name': item.item_type.name
            },
            'property_values': [{
                'property_id': value.property_id,
                'property_name': value.property.name,
                'property_type': value.property.property_type,
                'value': value.get_typed_value()
            } for value in item.property_values],
            'files': files
        })
    
    elif request.method == 'PUT':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Handle image upload if present
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                # Create type-specific folder
                type_folder = secure_filename(item.item_type.name.lower())
                item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
                os.makedirs(item_folder, exist_ok=True)
                
                # Save file with original filename (sanitized)
                safe_filename = secure_filename(file.filename)
                file_path = os.path.join(item_folder, safe_filename)
                
                # If file exists, append number
                base, ext = os.path.splitext(safe_filename)
                counter = 1
                while os.path.exists(file_path):
                    safe_filename = f"{base}_{counter}{ext}"
                    file_path = os.path.join(item_folder, safe_filename)
                    counter += 1
                
                # Delete old files in the folder
                for old_file in os.listdir(item_folder):
                    old_file_path = os.path.join(item_folder, old_file)
                    if os.path.isfile(old_file_path):
                        os.remove(old_file_path)
                
                # Save new file
                file.save(file_path)
        
        # Handle form data
        data = request.form.to_dict() if request.form else request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update basic fields
        if 'name' in data:
            item.name = data['name']
        if 'location_id' in data:
            item.location_id = data['location_id']
        
        # Update property values
        if 'property_values' in data:
            # If data is from form, parse the JSON string
            property_values = data['property_values']
            if isinstance(property_values, str):
                import json
                property_values = json.loads(property_values)
            
            # Remove existing property values
            for pv in item.property_values:
                db.session.delete(pv)
            
            # Add new property values
            for pv_data in property_values:
                # Get the property first
                property = ItemProperty.query.get(pv_data['property_id'])
                if property and property.item_type_id == item.item_type_id:
                    value = ItemPropertyValue(
                        item=item,
                        property=property
                    )
                    value.set_typed_value(pv_data['value'])
                    db.session.add(value)
        
        db.session.commit()
        
        # Get updated files from filesystem
        type_folder = secure_filename(item.item_type.name.lower())
        item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
        files = []
        if os.path.exists(item_folder):
            for filename in os.listdir(item_folder):
                file_path = os.path.join(item_folder, filename)
                if os.path.isfile(file_path):
                    files.append(get_file_info(item_id, type_folder, filename, file_path))
        
        # Return updated item
        return jsonify({
            'id': item.id,
            'name': item.name,
            'location_id': item.location_id,
            'item_type_id': item.item_type_id,
            'created_at': item.created_at.isoformat(),
            'location': {
                'id': item.location.id,
                'name': item.location.name
            } if item.location else None,
            'item_type': {
                'id': item.item_type.id,
                'name': item.item_type.name
            },
            'property_values': [{
                'property_id': value.property_id,
                'property_name': value.property.name,
                'property_type': value.property.property_type,
                'value': value.get_typed_value()
            } for value in item.property_values],
            'files': files
        })
    
    elif request.method == 'DELETE':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('delete_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Delete item's files
        type_folder = secure_filename(item.item_type.name.lower())
        item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
        if os.path.exists(item_folder):
            for filename in os.listdir(item_folder):
                file_path = os.path.join(item_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(item_folder)
        
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_info(item_id, type_folder, filename, file_path):
    return {
        'filename': os.path.join('pictures', 'items', type_folder, item_id, filename).replace('\\', '/'),
        'original_filename': filename,
        'size': os.path.getsize(file_path),
        'mime_type': mimetypes.guess_type(filename)[0]
    }

@app.route('/api/items/<item_id>/image', methods=['POST'])
@jwt_required()
def upload_item_image(item_id):
    if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
        return jsonify({'error': 'Insufficient permissions'}), 403
        
    item = Item.query.get_or_404(item_id)
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Create type-specific folder
        type_folder = secure_filename(item.item_type.name.lower())
        item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
        os.makedirs(item_folder, exist_ok=True)
        
        # Save file with original filename (sanitized)
        safe_filename = secure_filename(file.filename)
        file_path = os.path.join(item_folder, safe_filename)
        
        # If file exists, append number
        base, ext = os.path.splitext(safe_filename)
        counter = 1
        while os.path.exists(file_path):
            safe_filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(item_folder, safe_filename)
            counter += 1
        
        # Delete old files in the folder
        for old_file in os.listdir(item_folder):
            old_file_path = os.path.join(item_folder, old_file)
            if os.path.isfile(old_file_path):
                os.remove(old_file_path)
        
        # Save new file
        file.save(file_path)
        
        relative_path = os.path.join('pictures', 'items', type_folder, item_id, safe_filename).replace('\\', '/')
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'location_id': item.location_id,
            'item_type_id': item.item_type_id,
            'created_at': item.created_at.isoformat(),
            'location': {
                'id': item.location.id,
                'name': item.location.name
            } if item.location else None,
            'item_type': {
                'id': item.item_type.id,
                'name': item.item_type.name
            },
            'property_values': [{
                'property_id': value.property_id,
                'property_name': value.property.name,
                'property_type': value.property.property_type,
                'value': value.get_typed_value()
            } for value in item.property_values],
            'files': [{
                'filename': relative_path,
                'original_filename': safe_filename,
                'mime_type': file.content_type,
                'size': os.path.getsize(file_path)
            }]
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/users', methods=['GET'])
@jwt_required()
@require_permission('manage_users')
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': [role.name for role in user.roles],
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat()
    } for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@require_permission('manage_users')
def handle_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [role.name for role in user.roles],
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        })
    
    elif request.method == 'PUT':
        data = request.json
        
        # Update basic info
        user.email = data.get('email', user.email)
        user.is_active = data.get('is_active', user.is_active)
        
        # Update password if provided
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Update roles
        if 'roles' in data:
            user.roles = []
            for role_name in data['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user.roles.append(role)
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    
    elif request.method == 'DELETE':
        # Prevent self-deletion
        if user.id == get_jwt_identity():
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

@app.route('/api/locations', methods=['GET', 'POST'])
@jwt_required()
def get_or_create_locations():
    if request.method == 'GET':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('view_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        try:
            locations = Location.query.all()
            return jsonify([{
                'id': location.id,
                'name': location.name,
                'description': location.description,
                'parent_id': location.parent_id,
                'created_at': location.created_at.isoformat()
            } for location in locations])
        except Exception as e:
            print(f"Error in get_locations: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('add_locations'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        try:
            data = request.json
            if not data or not data.get('name'):
                return jsonify({'error': 'Name is required'}), 400
            
            location = Location(
                name=data['name'],
                description=data.get('description'),
                parent_id=data.get('parent_id')
            )
            db.session.add(location)
            db.session.commit()
            
            return jsonify({
                'id': location.id,
                'name': location.name,
                'description': location.description,
                'parent_id': location.parent_id,
                'created_at': location.created_at.isoformat()
            }), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error creating location: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/locations/<int:location_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_location(location_id):
    if request.method == 'GET':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('view_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'PUT':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'DELETE':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('delete_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403

    location = Location.query.get_or_404(location_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': location.id,
            'name': location.name,
            'description': location.description,
            'parent_id': location.parent_id,
            'created_at': location.created_at.isoformat()
        })
    
    elif request.method == 'PUT':
        data = request.json
        location.name = data.get('name', location.name)
        location.description = data.get('description', location.description)
        location.parent_id = data.get('parent_id', location.parent_id)
        
        db.session.commit()
        return jsonify({'message': 'Location updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(location)
        db.session.commit()
        return jsonify({'message': 'Location deleted successfully'})

@app.route('/api/item_types', methods=['GET'])
@jwt_required()
@require_permission('view_items')
def get_item_types():
    try:
        print("Fetching item types...")
        item_types = ItemType.query.all()
        print(f"Found {len(item_types)} item types")
        return jsonify([{
            'id': item_type.id,
            'name': item_type.name,
            'description': item_type.description,
            'created_at': item_type.created_at.isoformat(),
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'property_type': prop.property_type,
                'required': prop.required,
                'options': prop.options
            } for prop in item_type.properties]
        } for item_type in item_types])
    except Exception as e:
        import traceback
        print(f"Error in get_item_types: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/item_types/<int:item_type_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_item_type(item_type_id):
    if request.method == 'GET':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('view_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'PUT':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'DELETE':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('delete_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403

    item_type = ItemType.query.get_or_404(item_type_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': item_type.id,
            'name': item_type.name,
            'description': item_type.description,
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'property_type': prop.property_type,
                'required': prop.required,
                'options': prop.options
            } for prop in item_type.properties]
        })
    
    elif request.method == 'PUT':
        data = request.json
        item_type.name = data.get('name', item_type.name)
        item_type.description = data.get('description', item_type.description)
        
        if 'properties' in data:
            # Update properties
            for prop_data in data['properties']:
                prop = next((p for p in item_type.properties if p.id == prop_data.get('id')), None)
                if prop:
                    prop.name = prop_data.get('name', prop.name)
                    prop.property_type = prop_data.get('property_type', prop.property_type)
                    prop.required = prop_data.get('required', prop.required)
                    prop.options = prop_data.get('options', prop.options)
                else:
                    new_prop = ItemProperty(
                        name=prop_data['name'],
                        property_type=prop_data['property_type'],
                        required=prop_data.get('required', False),
                        options=prop_data.get('options')
                    )
                    item_type.properties.append(new_prop)
        
        db.session.commit()
        return jsonify({'message': 'Item type updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(item_type)
        db.session.commit()
        return jsonify({'message': 'Item type deleted successfully'})

@app.route('/api/tags', methods=['GET'])
@jwt_required()
@require_permission('view_items')
def get_tags():
    tags = Tag.query.all()
    return jsonify([{
        'id': tag.id,
        'name': tag.name,
        'color': tag.color,
        'created_at': tag.created_at.isoformat()
    } for tag in tags])

@app.route('/api/tags/<int:tag_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_tag(tag_id):
    if request.method == 'GET':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('view_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'PUT':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'DELETE':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('delete_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403

    tag = Tag.query.get_or_404(tag_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': tag.id,
            'name': tag.name,
            'color': tag.color,
            'created_at': tag.created_at.isoformat()
        })
    
    elif request.method == 'PUT':
        data = request.json
        tag.name = data.get('name', tag.name)
        tag.color = data.get('color', tag.color)
        
        db.session.commit()
        return jsonify({'message': 'Tag updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(tag)
        db.session.commit()
        return jsonify({'message': 'Tag deleted successfully'})

@app.route('/api/tags', methods=['POST'])
@jwt_required()
@require_permission('edit_items')
def create_tag():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing tag name'}), 400

    tag = Tag(
        name=data['name'],
        color=data.get('color', 'primary')
    )
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag created successfully',
        'tag': {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color,
            'created_at': tag.created_at.isoformat()
        }
    })

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def format_property_value(value, property_type):
    """Format property value for JSON response"""
    if value is None:
        return None
    if property_type == 'item_link' and value:
        return {
            'id': value.id,
            'name': value.name,
            'type': value.item_type.name
        }
    return str(value)

@app.route('/api/categories', methods=['GET'])
@jwt_required()
@require_permission('view_items')
def get_categories():
    categories = ItemCategory.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'icon': category.icon,
        'color': category.color,
        'created_at': category.created_at.isoformat()
    } for category in categories])

@app.route('/api/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_category(category_id):
    if request.method == 'GET':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('view_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'PUT':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    elif request.method == 'DELETE':
        if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('delete_items'):
            return jsonify({'error': 'Insufficient permissions'}), 403

    category = ItemCategory.query.get_or_404(category_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'color': category.color,
            'created_at': category.created_at.isoformat()
        })
    
    elif request.method == 'PUT':
        data = request.json
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.icon = data.get('icon', category.icon)
        category.color = data.get('color', category.color)
        
        db.session.commit()
        return jsonify({'message': 'Category updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})

@app.route('/api/categories', methods=['POST'])
@jwt_required()
@require_permission('edit_items')
def create_category():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing category name'}), 400

    category = ItemCategory(
        name=data['name'],
        description=data.get('description'),
        icon=data.get('icon', 'box'),
        color=data.get('color', 'primary')
    )
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'message': 'Category created successfully',
        'category': {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'color': category.color,
            'created_at': category.created_at.isoformat()
        }
    })

@app.route('/api/item_types', methods=['POST'])
@jwt_required()
@require_permission('edit_items')
def create_item_type():
    try:
        data = request.json
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        # Create new item type
        item_type = ItemType(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(item_type)

        # Add properties
        if 'properties' in data:
            for prop_data in data['properties']:
                property = ItemProperty(
                    name=prop_data['name'],
                    property_type=prop_data['property_type'],
                    required=prop_data.get('required', False),
                    options=prop_data.get('options'),
                    item_type=item_type
                )
                db.session.add(property)

        db.session.commit()

        return jsonify({
            'id': item_type.id,
            'name': item_type.name,
            'description': item_type.description,
            'created_at': item_type.created_at.isoformat(),
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'property_type': prop.property_type,
                'required': prop.required,
                'options': prop.options
            } for prop in item_type.properties]
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error creating item type: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/items/<item_id>/files', methods=['GET'])
@jwt_required()
def get_item_files(item_id):
    if not get_jwt_identity():
        return jsonify({'error': 'Insufficient permissions'}), 403
        
    item = Item.query.get_or_404(item_id)
    type_folder = secure_filename(item.item_type.name.lower())
    item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
    
    files = []
    if os.path.exists(item_folder):
        for filename in os.listdir(item_folder):
            file_path = os.path.join(item_folder, filename)
            if os.path.isfile(file_path):
                files.append(get_file_info(item_id, type_folder, filename, file_path))
    
    return jsonify({'files': files})

@app.route('/api/items/<item_id>/files', methods=['POST'])
@jwt_required()
def upload_item_files(item_id):
    if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
        return jsonify({'error': 'Insufficient permissions'}), 403
        
    item = Item.query.get_or_404(item_id)
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
        
    files = request.files.getlist('files[]')
    uploaded_files = []
    
    # Create type and item specific folder
    type_folder = secure_filename(item.item_type.name.lower())
    item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
    os.makedirs(item_folder, exist_ok=True)
    
    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            # Save file with original filename (sanitized)
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(item_folder, safe_filename)
            
            # If file exists, append number
            base, ext = os.path.splitext(safe_filename)
            counter = 1
            while os.path.exists(file_path):
                safe_filename = f"{base}_{counter}{ext}"
                file_path = os.path.join(item_folder, safe_filename)
                counter += 1
            
            # Save file
            file.save(file_path)
            
            relative_path = os.path.join('pictures', 'items', type_folder, item_id, safe_filename).replace('\\', '/')
            uploaded_files.append({
                'filename': relative_path,
                'original_filename': file.filename,
                'mime_type': file.content_type,
                'size': os.path.getsize(file_path)
            })
    
    return jsonify({'files': uploaded_files})

@app.route('/api/items/<item_id>/files/<path:filename>', methods=['DELETE'])
@jwt_required()
def delete_item_file(item_id, filename):
    if not get_jwt_identity() or not User.query.get(get_jwt_identity()).has_permission('edit_items'):
        return jsonify({'error': 'Insufficient permissions'}), 403
        
    item = Item.query.get_or_404(item_id)
    
    # Ensure the file is in the correct folder
    type_folder = secure_filename(item.item_type.name.lower())
    item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
    file_path = os.path.join(item_folder, secure_filename(os.path.basename(filename)))
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Delete physical file
    os.remove(file_path)
    
    # Remove folder if empty
    if not os.listdir(item_folder):
        os.rmdir(item_folder)
    
    return jsonify({'message': 'File deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=True
    ) 