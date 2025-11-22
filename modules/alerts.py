import streamlit as st
import requests

def send_telegram_alert(token, chat_id, message):
    if not token or not chat_id:
        st.warning("Please configure Telegram settings in the sidebar.")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.toast("Alert sent successfully!", icon="🚀")
        else:
            st.error(f"Failed to send alert: {response.text}")
    except Exception as e:
        st.error(f"Error sending alert: {e}")
