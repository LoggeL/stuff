import os
import requests
from app import app, db, ItemType, Item
from werkzeug.utils import secure_filename

def download_image(url, item_id, item_type_name):

    filename = f"{item_id}.jpg"

    headers = {
        'User-Agent': 'TheaterInventoryApp/1.0'
    }
    try:
        # Create the type-specific and item-specific folder
        type_folder = secure_filename(item_type_name.lower())
        item_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'items', type_folder, item_id)
        os.makedirs(item_folder, exist_ok=True)
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Save to the correct path with sanitized filename
        safe_filename = secure_filename(filename)
        file_path = os.path.join(item_folder, safe_filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename} for item {item_id}")
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")

def main():
    with app.app_context():
        print("Downloading demo images...")
        
        # Dictionary of image URLs and their target items
        images = {
            'Rokoko Ballkleid': {
                'url': 'https://picsum.photos/800/600?random=1',
                'filename': 'ballkleid.jpg',
                'type': 'Kostüme'
            },
            'Mittelalter Gewandung': {
                'url': 'https://picsum.photos/800/600?random=2',
                'filename': 'gewandung.jpg',
                'type': 'Kostüme'
            },
            'Kerzenleuchter': {
                'url': 'https://picsum.photos/800/600?random=3',
                'filename': 'leuchter.jpg',
                'type': 'Requisiten'
            },
            'Venezianische Maske': {
                'url': 'https://picsum.photos/800/600?random=4',
                'filename': 'maske.jpg',
                'type': 'Requisiten'
            },
            'Waldkulisse': {
                'url': 'https://picsum.photos/800/600?random=5',
                'filename': 'kulisse.jpg',
                'type': 'Kulissen'
            }
        }
        
        # Get all items
        items = Item.query.all()
        
        for item in items:
            # Find matching image data
            image_data = next(
                (data for name, data in images.items() if name.lower() in item.name.lower()),
                None
            )
            
            if image_data:
                download_image(
                    image_data['url'],
                    item.id,
                    item.item_type.name,
                    item.id
                )
        
        print("Done downloading images!")

if __name__ == '__main__':
    main() 