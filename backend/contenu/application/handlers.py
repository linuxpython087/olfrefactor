# backend/contenu/core/application/handlers.py
from contenu.core.domaine.dispatcher import EventDispatcher
from contenu.core.domaine.events import *

print("📌 handlers.py chargé")


# Exemple: notifier l'admin
def notify_admin(event: DocumentSubmitted):
    print(
        f"📨 Notification admin: Document {event.document_id} soumis par {event.submitted_by}"
    )


# Exemple: déclencher l'ETL
def trigger_etl(event: DocumentReadyForETL):
    print(f"⚙️ ETL déclenché pour le document {event.document_id}")


# Exemple: log simple
def log_upload_started(event: DocumentUploadStarted):
    print(f"🚀 Upload démarré pour {event.document_id} par {event.submitted_by}")


# Enregistrement des handlers
EventDispatcher.register(DocumentSubmitted, notify_admin)
EventDispatcher.register(DocumentReadyForETL, trigger_etl)
EventDispatcher.register(DocumentUploadStarted, log_upload_started)
