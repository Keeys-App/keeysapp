#!/usr/bin/env python3
"""
Тест SendPulse через campaigns API (может работать на free tier)
"""
import requests
import json
import time

CLIENT_ID = "3b4a42782410087d80ffe36d5f74b3ce"
CLIENT_SECRET = "159e0df89df0dc243f42b243097af507"
RECIPIENT_EMAIL = "mbrtn@icloud.com"

def get_token():
    response = requests.post(
        "https://api.sendpulse.com/oauth/access_token",
        json={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    return response.json().get("access_token")

def check_sender_status(token):
    """Проверяем детальный статус отправителя"""
    print("\n🔍 Проверяю статус отправителя...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получаем список отправителей
    response = requests.get(
        "https://api.sendpulse.com/smtp/senders",
        headers=headers
    )
    
    if response.status_code == 200:
        senders = response.json()
        print(f"Отправители: {senders}")
        
        # Пробуем получить детальную инфу
        for sender in senders:
            email = sender if isinstance(sender, str) else sender.get('email')
            print(f"\n📧 Проверяю {email}...")
            
            # Пробуем разные endpoints
            endpoints = [
                f"/smtp/senders/{email}",
                "/smtp/senders/info",
                "/smtp/emails/info"
            ]
            
            for endpoint in endpoints:
                resp = requests.get(
                    f"https://api.sendpulse.com{endpoint}",
                    headers=headers
                )
                if resp.status_code == 200:
                    print(f"  {endpoint}: {resp.json()}")

def create_addressbook_and_send(token):
    """Пробуем создать address book и отправить через него"""
    print("\n📚 Попытка создать address book...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Создаем временный address book
    addressbook_data = {
        "bookName": f"Test_{int(time.time())}"
    }
    
    response = requests.post(
        "https://api.sendpulse.com/addressbooks",
        headers=headers,
        json=addressbook_data
    )
    
    print(f"Create addressbook: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201 or response.status_code == 200:
        book_id = response.json().get('id')
        print(f"✅ Address book создан: {book_id}")
        
        # Добавляем email в book
        print("\n📧 Добавляю получателя...")
        add_response = requests.post(
            f"https://api.sendpulse.com/addressbooks/{book_id}/emails",
            headers=headers,
            json={
                "emails": [
                    {"email": RECIPIENT_EMAIL}
                ]
            }
        )
        print(f"Add email: {add_response.status_code}")
        print(f"Response: {add_response.json()}")
        
        # Создаем кампанию
        print("\n📨 Создаю кампанию...")
        campaign_data = {
            "sender_name": "Locales Test",
            "sender_email": "mail@keeys.app",
            "subject": "🧪 Test SendPulse",
            "body": "<h1>Тестовое письмо</h1><p>Это работает!</p>",
            "list_id": book_id
        }
        
        campaign_response = requests.post(
            "https://api.sendpulse.com/campaigns",
            headers=headers,
            json=campaign_data
        )
        
        print(f"Create campaign: {campaign_response.status_code}")
        print(f"Response: {campaign_response.json()}")

def test_templates(token):
    """Проверяем доступны ли templates"""
    print("\n📝 Проверяю templates...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        "https://api.sendpulse.com/templates",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        templates = response.json()
        print(f"Templates: {json.dumps(templates, indent=2)}")

def main():
    print("=" * 70)
    print("🧪 Расширенная диагностика SendPulse")
    print("=" * 70)
    
    token = get_token()
    print(f"✅ Token получен")
    
    # Проверяем статус отправителя
    check_sender_status(token)
    
    # Пробуем templates
    test_templates(token)
    
    # Пробуем через campaigns
    create_addressbook_and_send(token)
    
    print("\n" + "=" * 70)
    print("ℹ️  Если ничего не работает:")
    print("  • Проверьте, что mail@keeys.app полностью верифицирован")
    print("  • Возможно нужна платная подписка для SMTP")
    print("  • Попробуйте добавить другой email в SendPulse")
    print("=" * 70)

if __name__ == "__main__":
    main()

