import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class CulqiService:
    def __init__(self):
        self.secret_key = os.getenv("CULQI_SECRET_KEY")
        self.public_key = os.getenv("CULQI_PUBLIC_KEY")
        self.base_url = "https://api.culqi.com/v2"
        
        if not self.secret_key or not self.public_key:
            raise ValueError("Culqi keys not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    def create_customer(self, email: str, first_name: str = "", last_name: str = "") -> Dict[str, Any]:
        """Crear un cliente en Culqi"""
        url = f"{self.base_url}/customers"
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def create_card(self, customer_id: str, token_id: str) -> Dict[str, Any]:
        """Crear una tarjeta para un cliente"""
        url = f"{self.base_url}/cards"
        data = {
            "customer_id": customer_id,
            "token_id": token_id
        }
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def create_subscription(self, customer_id: str, card_id: str, plan_id: str, 
                          trial_days: int = 0) -> Dict[str, Any]:
        """Crear una suscripción en Culqi"""
        url = f"{self.base_url}/subscriptions"
        data = {
            "customer_id": customer_id,
            "card_id": card_id,
            "plan_id": plan_id
        }
        
        if trial_days > 0:
            data["trial_days"] = trial_days
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def create_plan(self, name: str, amount: int, currency: str = "PEN", 
                   interval: str = "month", interval_count: int = 1) -> Dict[str, Any]:
        """Crear un plan en Culqi"""
        url = f"{self.base_url}/plans"
        data = {
            "name": name,
            "amount": amount,
            "currency": currency,
            "interval": interval,
            "interval_count": interval_count
        }
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Obtener información de una suscripción"""
        url = f"{self.base_url}/subscriptions/{subscription_id}"
        
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """Cancelar una suscripción"""
        url = f"{self.base_url}/subscriptions/{subscription_id}"
        data = {
            "cancel_at_period_end": at_period_end
        }
        
        response = requests.patch(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def create_charge(self, amount: int, currency: str, email: str, 
                     source_id: str, description: str = "") -> Dict[str, Any]:
        """Crear un cargo único"""
        url = f"{self.base_url}/charges"
        data = {
            "amount": amount,
            "currency": currency,
            "email": email,
            "source_id": source_id,
            "description": description
        }
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def get_charge(self, charge_id: str) -> Dict[str, Any]:
        """Obtener información de un cargo"""
        url = f"{self.base_url}/charges/{charge_id}"
        
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json() 