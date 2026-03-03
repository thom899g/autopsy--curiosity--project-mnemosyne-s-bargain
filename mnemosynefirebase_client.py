"""
Firebase Client for Mnemosyne
Robust Firestore integration with connection pooling and automatic reconnection
"""

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
from google.cloud.firestore_v1.client import Client as FirestoreClient
from google.cloud.firestore_v1.document import DocumentReference
from typing import Optional, Dict, Any, List
import structlog
from datetime import datetime, timedelta
import json
import hashlib

logger = structlog.get_logger(__name__)


class FirebaseClient:
    """Managed Firebase client with connection lifecycle management"""
    
    _instance: Optional["FirebaseClient"] = None
    _app: Optional[firebase_admin.App] = None
    _client: Optional[FirestoreClient] = None
    _initialized: bool = False
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """Initialize Firebase connection"""
        self.project_id = project_id
        self.credentials_path = credentials_path
        self._connection_attempts = 0
        self._