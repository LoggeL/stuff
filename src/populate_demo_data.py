from app import app, db
from models import ItemCategory, ItemType, ItemProperty, Location, Item, Tag
from datetime import datetime, timedelta

def populate_demo_data():
    with app.app_context():
        print("Creating categories...")
        props = ItemCategory(
            name="Requisiten",
            description="Requisiten und Bühnenausstattung",
            icon="box",
            color="primary"
        )
        costumes = ItemCategory(
            name="Kostüme",
            description="Kostüme und Accessoires",
            icon="person-badge",
            color="success"
        )
        tech = ItemCategory(
            name="Technik",
            description="Beleuchtung, Ton und andere technische Ausrüstung",
            icon="lightbulb",
            color="warning"
        )
        stage = ItemCategory(
            name="Bühnenbau",
            description="Bühnenelemente und Kulissen",
            icon="building",
            color="info"
        )

        db.session.add_all([props, costumes, tech, stage])
        db.session.commit()

        print("Creating item types...")
        # Props types
        hand_prop = ItemType(
            name="Handrequisit",
            description="Kleine, tragbare Requisiten",
            category=props
        )
        hand_prop.properties.extend([
            ItemProperty(name="Material", property_type="text", required=True),
            ItemProperty(name="Maße (cm)", property_type="text"),
            ItemProperty(name="Gewicht (g)", property_type="number"),
            ItemProperty(name="Zerbrechlich", property_type="boolean"),
            ItemProperty(name="Letzte Reparatur", property_type="date"),
        ])

        furniture = ItemType(
            name="Möbelstück",
            description="Möbel und große Requisiten",
            category=props
        )
        furniture.properties.extend([
            ItemProperty(name="Material", property_type="text", required=True),
            ItemProperty(name="Maße (cm)", property_type="text", required=True),
            ItemProperty(name="Epoche", property_type="text"),
            ItemProperty(name="Zerlegbar", property_type="boolean"),
            ItemProperty(name="Max. Belastung (kg)", property_type="number"),
        ])

        # Costume types
        costume = ItemType(
            name="Kostüm",
            description="Theaterkostüme",
            category=costumes
        )
        costume.properties.extend([
            ItemProperty(name="Größe", property_type="text", required=True),
            ItemProperty(name="Epoche/Stil", property_type="text"),
            ItemProperty(name="Material", property_type="text"),
            ItemProperty(name="Waschbar", property_type="boolean"),
            ItemProperty(name="Letzte Reinigung", property_type="date"),
        ])

        # Tech types
        light = ItemType(
            name="Scheinwerfer",
            description="Bühnenbeleuchtung",
            category=tech
        )
        light.properties.extend([
            ItemProperty(name="Typ", property_type="text", required=True),
            ItemProperty(name="Leistung (W)", property_type="number", required=True),
            ItemProperty(name="DMX-Adresse", property_type="text"),
            ItemProperty(name="Betriebsstunden", property_type="number"),
            ItemProperty(name="Letzte Wartung", property_type="date"),
        ])

        # Stage elements
        stage_element = ItemType(
            name="Bühnenelement",
            description="Kulissen und Bühnenaufbauten",
            category=stage
        )
        stage_element.properties.extend([
            ItemProperty(name="Art", property_type="text", required=True),
            ItemProperty(name="Maße (cm)", property_type="text", required=True),
            ItemProperty(name="Material", property_type="text"),
            ItemProperty(name="Gewicht (kg)", property_type="number"),
            ItemProperty(name="Feuergeschützt", property_type="boolean"),
        ])

        db.session.add_all([hand_prop, furniture, costume, light, stage_element])
        db.session.commit()

        print("Creating locations...")
        locations = [
            Location(name="Requisitenlager"),
            Location(name="Kostümfundus"),
            Location(name="Technikraum"),
            Location(name="Bühne"),
            Location(name="Werkstatt"),
            Location(name="Schneiderei")
        ]
        db.session.add_all(locations)
        db.session.commit()

        print("Creating tags...")
        tags = [
            Tag(name="Defekt", color="danger"),
            Tag(name="Neu", color="success"),
            Tag(name="In Verwendung", color="warning"),
            Tag(name="Wartung fällig", color="info"),
            Tag(name="Wichtig", color="primary"),
            Tag(name="Archiviert", color="secondary"),
            Tag(name="Reinigung nötig", color="warning"),
            Tag(name="Reparatur nötig", color="danger"),
            Tag(name="Ausgeliehen", color="info"),
            Tag(name="Historisch", color="dark")
        ]
        db.session.add_all(tags)
        db.session.commit()

        print("Creating items...")
        # Create props
        sword = Item(
            name="Theaterschwert",
            location=locations[0],  # Requisitenlager
            item_type=hand_prop
        )
        sword.set_property_value("Material", "Aluminium, Gummigriff")
        sword.set_property_value("Maße (cm)", "100x15x5")
        sword.set_property_value("Gewicht (g)", 800)
        sword.set_property_value("Zerbrechlich", False)
        sword.set_property_value("Letzte Reparatur", datetime.now() - timedelta(days=90))
        sword.tags.extend([tags[2], tags[3]])  # In Verwendung, Wartung fällig

        throne = Item(
            name="Königsthron",
            location=locations[0],  # Requisitenlager
            item_type=furniture
        )
        throne.set_property_value("Material", "Holz, vergoldet")
        throne.set_property_value("Maße (cm)", "120x80x160")
        throne.set_property_value("Epoche", "Barock")
        throne.set_property_value("Zerlegbar", True)
        throne.set_property_value("Max. Belastung (kg)", 150)
        throne.tags.extend([tags[4], tags[9]])  # Wichtig, Historisch

        # Create costumes
        king_costume = Item(
            name="Königskostüm",
            location=locations[1],  # Kostümfundus
            item_type=costume
        )
        king_costume.set_property_value("Größe", "L")
        king_costume.set_property_value("Epoche/Stil", "Mittelalter")
        king_costume.set_property_value("Material", "Samt, Brokat")
        king_costume.set_property_value("Waschbar", False)
        king_costume.set_property_value("Letzte Reinigung", datetime.now() - timedelta(days=60))
        king_costume.tags.extend([tags[2], tags[6]])  # In Verwendung, Reinigung nötig

        # Create lights
        spotlight = Item(
            name="LED-Profilscheinwerfer",
            location=locations[2],  # Technikraum
            item_type=light
        )
        spotlight.set_property_value("Typ", "LED Profile 250W")
        spotlight.set_property_value("Leistung (W)", 250)
        spotlight.set_property_value("DMX-Adresse", "001")
        spotlight.set_property_value("Betriebsstunden", 1500)
        spotlight.set_property_value("Letzte Wartung", datetime.now() - timedelta(days=45))
        spotlight.tags.extend([tags[1], tags[4]])  # Neu, Wichtig

        # Create stage elements
        wall = Item(
            name="Burgmauer",
            location=locations[3],  # Bühne
            item_type=stage_element
        )
        wall.set_property_value("Art", "Kulissenwand")
        wall.set_property_value("Maße (cm)", "400x250x50")
        wall.set_property_value("Material", "Holz, Styropor")
        wall.set_property_value("Gewicht (kg)", 80)
        wall.set_property_value("Feuergeschützt", True)
        wall.tags.extend([tags[2], tags[3]])  # In Verwendung, Wartung fällig

        db.session.add_all([sword, throne, king_costume, spotlight, wall])
        db.session.commit()

        print("Demo data created successfully!")

if __name__ == '__main__':
    populate_demo_data() 