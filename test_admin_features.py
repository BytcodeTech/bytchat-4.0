#!/usr/bin/env python3
"""
Script para probar las nuevas funcionalidades de administración de planes y tokens
"""

import requests
import json
import sys

BASE_URL = "http://161.132.45.210:8001"

def test_admin_login():
    """Obtener token de super administrador"""
    print("🔐 Probando autenticación de super administrador...")
    
    login_data = {
        "username": "admin@bytcode.tech",
        "password": "superagente123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Autenticación exitosa!")
            return access_token
        else:
            print(f"❌ Error de autenticación: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_get_users_with_plans(token):
    """Probar obtener usuarios con planes"""
    print("\n📊 Probando obtener usuarios con planes...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/users/with-plans/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Obtenidos {len(users)} usuarios con planes")
            
            # Mostrar algunos detalles
            for user in users[:3]:  # Mostrar solo los primeros 3
                plan = user.get('plan', {})
                print(f"   📋 {user['email']}: Plan {plan.get('plan_type', 'none')} - {plan.get('bytokens_remaining', 0)} BytTokens restantes")
            
            return users[0] if users else None  # Devolver primer usuario para pruebas
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_change_user_plan(token, user_id):
    """Probar cambiar plan de usuario"""
    print(f"\n🔄 Probando cambiar plan del usuario ID {user_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Cambiar a plan PRO con tokens adicionales
    plan_data = {
        "new_plan_type": "pro",
        "tokens_to_add": 50000,
        "reset_usage": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/users/{user_id}/change-plan/",
            json=plan_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Plan cambiado exitosamente!")
            print(f"   📝 Mensaje: {result['message']}")
            print(f"   📊 Nuevo plan: {result['updated_plan']['plan_type']}")
            print(f"   🪙 BytTokens incluidos: {result['updated_plan']['bytokens_included']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_modify_user_tokens(token, user_id):
    """Probar modificar tokens de usuario"""
    print(f"\n🪙 Probando modificar tokens del usuario ID {user_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Agregar 25000 tokens como bono
    token_data = {
        "tokens_to_add": 25000,
        "reason": "Bono de prueba - Script de testing",
        "reset_overage": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/users/{user_id}/modify-tokens/",
            json=token_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tokens modificados exitosamente!")
            print(f"   📝 Mensaje: {result['message']}")
            print(f"   🪙 BytTokens restantes: {result['updated_plan']['bytokens_remaining']}")
            print(f"   📊 BytTokens incluidos: {result['updated_plan']['bytokens_included']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_user_plan_details(token, user_id):
    """Probar obtener detalles del plan de usuario"""
    print(f"\n📋 Probando obtener detalles del plan del usuario ID {user_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/users/{user_id}/plan-details/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            details = response.json()
            plan = details['user_plan']
            stats = details['usage_stats']
            
            print("✅ Detalles obtenidos exitosamente!")
            print(f"   📊 Plan: {plan['plan_type']} - ${plan['monthly_price']/100:.2f}/mes")
            print(f"   🪙 BytTokens: {plan['bytokens_remaining']}/{plan['bytokens_included']}")
            print(f"   📈 Uso últimos 30 días: {stats['tokens_last_30_days']}")
            print(f"   🤖 Uso por proveedor: {stats['usage_by_provider']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 TESTING DE FUNCIONALIDADES DE ADMINISTRACIÓN")
    print("=" * 60)
    
    # 1. Autenticación
    token = test_admin_login()
    if not token:
        print("💥 No se pudo obtener token de autenticación. Abortando pruebas.")
        sys.exit(1)
    
    # 2. Obtener usuarios con planes
    users = test_get_users_with_plans(token)
    if not users:
        print("💥 No se pudieron obtener usuarios. Abortando pruebas.")
        sys.exit(1)
    
    user_id = users['id']
    print(f"\n🎯 Usando usuario de prueba: {users['email']} (ID: {user_id})")
    
    # 3. Probar todas las funcionalidades
    tests_passed = 0
    total_tests = 4
    
    if test_get_user_plan_details(token, user_id):
        tests_passed += 1
    
    if test_change_user_plan(token, user_id):
        tests_passed += 1
    
    if test_modify_user_tokens(token, user_id):
        tests_passed += 1
    
    # Verificar cambios finales
    if test_get_user_plan_details(token, user_id):
        tests_passed += 1
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"✅ Pruebas exitosas: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ¡TODAS LAS FUNCIONALIDADES FUNCIONAN CORRECTAMENTE!")
    else:
        print(f"⚠️  {total_tests - tests_passed} pruebas fallaron. Revisar logs arriba.")
    
    print("\n💡 Las funcionalidades de administración están listas para usar en el panel web.")

if __name__ == "__main__":
    main() 