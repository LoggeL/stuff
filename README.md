# STUFF (**S**ystem für **T**heater-**U**tensilien, **F**undus und **F**ummel)

Ein Inventarverwaltungssystem mit QR-Code-Unterstützung, entwickelt mit Python Flask.

## Features

- Verwaltung von Lagerorten mit QR-Codes
- Item-Verwaltung mit Bildern und QR-Codes
- Hierarchische Item-Struktur (Items können Subitems enthalten)
- Flexible Tagging-Funktionalität
- Suchfunktionen:
  - Suche nach Name
  - Suche nach Tag
  - Suche nach Lagerort
  - QR-Code-Scanning

## Installation

1. Python-Umgebung erstellen und aktivieren:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. Umgebungsvariablen konfigurieren:
```bash
# .env Datei erstellen
SECRET_KEY=your-secret-key
```

## Entwicklung

1. Entwicklungsserver starten:
```bash
cd src
python app.py
```

2. Tests ausführen:
```bash
pytest
```

## API-Endpunkte

### Lagerorte
- `GET /locations` - Liste aller Lagerorte
- `POST /locations` - Neuen Lagerort erstellen
- `GET /locations/<id>/items` - Items in einem Lagerort anzeigen

### Items
- `GET /items` - Liste aller Items (mit Suchparametern)
- `POST /items` - Neues Item erstellen
- `GET /items/<id>` - Item-Details abrufen
- `GET /items/<id>/qr` - QR-Code für ein Item generieren
- `GET /items/<id>/subitems` - Subitems eines Items anzeigen
- `POST /items/<id>/subitems` - Subitem zu einem Item hinzufügen

### Tags
- `GET /tags` - Liste aller Tags
- `POST /tags` - Neuen Tag erstellen

## Projektstruktur

```
inventar/
├── src/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── app.py
│   └── models.py
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── requirements.txt
└── README.md
```

## Technologien

- Backend: Python Flask
- Datenbank: SQLite mit SQLAlchemy
- Frontend: Bootstrap 5
- QR-Codes: qrcode
- Tests: pytest
