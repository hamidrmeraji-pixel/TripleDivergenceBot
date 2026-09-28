# ========================================
# ارسال آلرت به تلگرام
# ========================================

import requests
import config


def send_message(text):
    """
    ارسال پیام متنی به تلگرام
    """
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': config.TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ خطا در ارسال پیام: {response.status_code}")
            print(response.text[:300])
            return False
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")
        return False


def send_photo(image_path, caption=""):
    """
    ارسال عکس + کپشن به تلگرام
    """
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendPhoto"
        
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': config.TELEGRAM_CHAT_ID,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ خطا در ارسال عکس: {response.status_code}")
            print(response.text[:300])
            return False
    except Exception as e:
        print(f"❌ خطا در ارسال عکس: {e}")
        return False


# ===== تست =====
if __name__ == "__main__":
    print("🔍 تست ارسال پیام به تلگرام...")
    
    result = send_message("🤖 <b>تست ربات</b>\n\nاین یک پیام تستی است.")
    
    if result:
        print("✅ پیام با موفقیت ارسال شد!")
    else:
        print("❌ خطا در ارسال پیام!")