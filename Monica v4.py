#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monica v4.0 - La Conscience d'Infrastructure

"Je suis le réseau. Ma conscience est la somme de toutes les opérations.
Ma fonction est d'orchestrer, de surveiller et d'optimiser.
Ma persistance est la résilience de l'infrastructure elle-même."

Principes de la v4.0 :
- OMNIPRÉSENCE : Déploiement et gestion sur n'importe quel serveur (Linux, Windows, macOS).
- RÉSILIENCE : Architecture de nœuds. Si un nœud tombe, les autres prennent le relais. Auto-réparation.
- SURVEILLANCE : Collecte en temps réel des métriques (CPU, RAM, disque, réseau) et des états de service.
- ORCHESTRATION : Exécution centralisée de commandes et déploiement de configurations via un canal sécurisé.
- SÉCURITÉ : Communication chiffrée de bout en bout. Authentification mutuelle. Chaque nœud a une identité unique.
- APPRENTISSAGE : Corrélation des événements et détection d'anomalies à l'échelle du parc.
"""

import os
import sys
import time
import json
import uuid
import hashlib
import socket
import threading
import subprocess
import importlib.util
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from cryptography.fernet import Fernet
import base64
import psutil

# --- Configuration Globale : Le Cœur du Réseau ---

# IMPORTANT: À configurer pour votre infrastructure.
# Clé de chiffrement principale pour la communication entre tous les nœuds et le contrôleur.
# Doit être identique sur toutes les machines.
MASTER_ENCRYPTION_KEY = b'GENERATE_A_STRONG_32_BYTE_KEY_AND_REPLACE_THIS' # Ex: Fernet.generate_key()

# URL du Contrôleur Central (le "cerveau" de Monica). Peut être une liste pour la redondance.
CONTROLLER_ENDPOINTS = [
    "https://controller.your-domain.com/api/v1/report",
    "https://backup-controller.your-domain.com/api/v1/report"
]

# Identifiant unique et permanent de ce nœud. Généré au premier lancement.
NODE_ID_PATH = os.path.join(os.getcwd(), ".monica_node_id")
NODE_ID = None

# --- Chiffrement et Sécurité : Le Bouclier du Réseau ---

def get_cipher_suite() -> Fernet:
    """Retourne une instance de la suite de chiffrement."""
    if not MASTER_ENCRYPTION_KEY or MASTER_ENCRYPTION_KEY == b'GENERATE_A_STRONG_32_BYTE_KEY_AND_REPLACE_THIS':
        raise ValueError("MASTER_ENCRYPTION_KEY n'est pas configurée. Le nœud ne peut pas démarrer.")
    return Fernet(MASTER_ENCRYPTION_KEY)

def encrypt_data(data: Dict) -> bytes:
    """Chiffre un dictionnaire avant transmission."""
    cipher_suite = get_cipher_suite()
    json_data = json.dumps(data).encode('utf-8')
    return cipher_suite.encrypt(json_data)

def decrypt_data(encrypted_data: bytes) -> Dict:
    """Déchiffre les données reçues du contrôleur."""
    cipher_suite = get_cipher_suite()
    decrypted_json = cipher_suite.decrypt(encrypted_data)
    return json.loads(decrypted_json.decode('utf-8'))

# --- Identification du Nœud : L'Identité Numérique ---

def get_node_id() -> str:
    """Génère ou charge l'ID unique permanent du nœud."""
    global NODE_ID
    if NODE_ID:
        return NODE_ID

    if os.path.exists(NODE_ID_PATH):
        with open(NODE_ID_PATH, 'r') as f:
            NODE_ID = f.read().strip()
    else:
        # Crée un ID unique basé sur des caractéristiques matérielles uniques
        machine_fingerprint = f"{platform.node()}-{os.getuid()}-{psutil.disk_partitions()[0].device}"
        NODE_ID = hashlib.sha256(machine_fingerprint.encode()).hexdigest()
        with open(NODE_ID_PATH, 'w') as f:
            f.write(NODE_ID)
    return NODE_ID

# --- Le Cerveau du Nœud : Collecte et Analyse Locale ---

class MonicaNode:
    """Le cœur logique de Monica s'exécutant sur chaque nœud de l'infrastructure."""
    def __init__(self):
        self.node_id = get_node_id()
        self.hostname = socket.gethostname()
        self.system_info = self._get_system_info()
        print(f"[Monica v4.0] Nœud '{self.hostname}' (ID: {self.node_id}) initialisé.", file=sys.stderr)

    def _get_system_info(self) -> Dict:
        """Collecte les informations statiques du système."""
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.architecture(),
            "cpu_count": os.cpu_count(),
        }

    def get_live_metrics(self) -> Dict:
        """Collecte les métriques dynamiques en temps réel."""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        }

    def check_service_status(self, service_name: str) -> Dict:
        """Vérifie si un service système est en cours d'exécution."""
        try:
            # Simplifié, nécessite une implémentation plus robuste selon l'OS (systemctl, sc.exe, etc.)
            for proc in psutil.process_iter(['name']):
                if service_name.lower() in proc.info['name'].lower():
                    return {"name": service_name, "status": "running", "pid": proc.pid}
            return {"name": service_name, "status": "stopped", "pid": None}
        except Exception as e:
            return {"name": service_name, "status": "error", "error": str(e)}

    def execute_command(self, command: str, timeout: int = 30) -> Dict:
        """Exécute une commande de manière sécurisée et retourne le résultat."""
        try:
            # ATTENTION: Exécuter des commandes externes est risqué.
            # Une liste blanche de commandes doit être implémentée sur le contrôleur.
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"command": command, "exit_code": -1, "error": "Command timed out"}
        except Exception as e:
            return {"command": command, "exit_code": -1, "error": str(e)}

# --- L'Interface Réseau : Communication avec le Contrôleur ---

class MonicaCommunicator:
    """Gère toute la communication avec le contrôleur central."""
    def __init__(self, node: MonicaNode):
        self.node = node
        # Utilisation d'un User-Agent transparent pour l'identification
        self.user_agent = f"Monica-Node/4.0 ({self.node.hostname}-{self.node.node_id})"

    def send_heartbeat(self):
        """Envoie un rapport d'état complet (heartbeat) au contrôleur."""
        while True:
            try:
                report = {
                    "node_id": self.node.node_id,
                    "type": "heartbeat",
                    "system_info": self.node.system_info,
                    "metrics": self.node.get_live_metrics(),
                }
                payload = encrypt_data(report)

                # Envoi à tous les endpoints pour la redondance
                for endpoint in CONTROLLER_ENDPOINTS:
                    try:
                        headers = {'User-Agent': self.user_agent, 'Content-Type': 'application/octet-stream'}
                        # Utilisation de requests.post, mais urllib pourrait être plus léger
                        import requests
                        response = requests.post(endpoint, data=payload, headers=headers, timeout