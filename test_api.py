#!/usr/bin/env python3
"""
Restaurant API Test Script
Bu script ile API'nin tüm endpoint'lerini test edeceğiz
"""

import requests
import json
import sys
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

# Test verileri
TEST_USER = {
    "email": f"test_{datetime.now().timestamp()}@example.com",
    "password": "Test123456!"
}

def print_section(title):
    """Bölüm başlığı yazdır"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def test_health():
    """Health endpoint'ini test et"""
    print_section("1. HEALTH CHECK TESTİ")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            api_status = data.get('api', 'unknown')
            db_status = data.get('database', 'unknown')
            
            print(f"\n✓ API Durumu: {api_status}")
            print(f"✓ Database Durumu: {db_status}")
            
            if api_status == 'ok' and db_status == 'ok':
                print("\n✅ Health check başarılı!")
                return True
            else:
                print("\n⚠️ Health check kısmen başarılı")
                return False
    except Exception as e:
        print(f"\n❌ Health check hatası: {e}")
        return False

def test_register():
    """Kullanıcı kayıt endpoint'ini test et"""
    print_section("2. KULLANICI KAYIT TESTİ")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\n✅ Kullanıcı başarıyla kaydedildi!")
            return True
        elif response.status_code == 400:
            print("\n⚠️ Kullanıcı zaten mevcut (bu normal)")
            return True
        else:
            print(f"\n❌ Kayıt başarısız: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ Kayıt hatası: {e}")
        return False

def test_login():
    """Kullanıcı giriş endpoint'ini test et"""
    print_section("3. KULLANICI GİRİŞ TESTİ")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"Token Type: {data.get('token_type')}")
            print(f"Access Token: {token[:20]}..." if token else "Token alınamadı")
            print("\n✅ Giriş başarılı!")
            return token
        else:
            print(f"\n❌ Giriş başarısız: {response.text}")
            return None
    except Exception as e:
        print(f"\n❌ Giriş hatası: {e}")
        return None

def test_me(token):
    """Kullanıcı bilgisi endpoint'ini test et"""
    print_section("4. KULLANICI BİLGİSİ TESTİ (/api/v1/me)")
    
    if not token:
        print("⚠️ Token yok, test atlanıyor")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"\n✅ Kullanıcı bilgisi alındı!")
            print(f"  - ID: {data.get('id')}")
            print(f"  - Email: {data.get('email')}")
            return True
        else:
            print(f"\n❌ Kullanıcı bilgisi alınamadı: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ Kullanıcı bilgisi hatası: {e}")
        return False

def test_unauthorized_access():
    """Token olmadan erişim testi"""
    print_section("5. YETKİSİZ ERİŞİM TESTİ")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/me")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Yetkisiz erişim doğru şekilde engellendi!")
            return True
        else:
            print(f"❌ Beklenmeyen yanıt: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def check_swagger():
    """Swagger dokümantasyonu kontrolü"""
    print_section("6. SWAGGER DOKÜMANTASYON KONTROLÜ")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger dokümantasyonu aktif!")
            print(f"   📄 URL: {BASE_URL}/docs")
            return True
        else:
            print(f"⚠️ Swagger erişilemiyor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swagger kontrolü hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("\n" + "🚀 RESTAURANT API TEST BAŞLIYOR 🚀".center(50))
    
    results = []
    
    # 1. Health Check
    results.append(("Health Check", test_health()))
    
    # 2. Register
    results.append(("Register", test_register()))
    
    # 3. Login ve token al
    token = test_login()
    results.append(("Login", token is not None))
    
    # 4. Me endpoint
    results.append(("Me Endpoint", test_me(token)))
    
    # 5. Yetkisiz erişim
    results.append(("Unauthorized", test_unauthorized_access()))
    
    # 6. Swagger
    results.append(("Swagger", check_swagger()))
    
    # Test Özeti
    print_section("TEST ÖZETİ")
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:20} : {status}")
    
    print(f"\nToplam: {success_count}/{total_count} test başarılı")
    
    if success_count == total_count:
        print("\n🎉 TÜM TESTLER BAŞARILI! 🎉")
    else:
        print(f"\n⚠️ {total_count - success_count} test başarısız!")

if __name__ == "__main__":
    main()