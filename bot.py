import yfinance as yf
import pandas as pd
import ta
import time
import requests
from datetime import datetime
import pytz

TOKEN = "8884146603:AAFitFKTVz-UChiQYec6XKUn1jTSgelwr5Q"
CHAT_ID = "6560153830"
ACTIVO = "BTC-USD"
NOMBRE_TG = "Bitcoin (Binary) - IQ Option REAL"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Error telegram: {e}")

def analizar():
    try:
        df = yf.download(ACTIVO, period="1d", interval="1m", progress=False, auto_adjust=True)
        if len(df) < 100: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()
        df['RSI'] = ta.momentum.RSIIndicator(close, window=14).rsi()
        df['ADX'] = ta.trend.ADXIndicator(high, low, close, window=14).adx()
        df['EMA9'] = ta.trend.EMAIndicator(close, window=9).ema_indicator()
        df['EMA21'] = ta.trend.EMAIndicator(close, window=21).ema_indicator()
        last = df.iloc[-1]
        rsi = float(last['RSI'])
        adx = float(last['ADX'])
        rango = float(df['High'].tail(20).max() - df['Low'].tail(20).min())
        if rango / float(last['Close']) * 100 < 0.12: return None
        if adx < 20: return None
        if 45 < rsi < 55: return None
        direccion = ""
        score = 0
        if last['EMA9'] > last['EMA21'] and 55 < rsi < 72:
            direccion = "COMPRA 🟢 (CALL)"
            score = 3
        elif last['EMA9'] < last['EMA21'] and 28 < rsi < 45:
            direccion = "VENTA 🔴 (PUT)"
            score = 3
        else:
            return None
        if adx > 25: score += 2
        if adx > 30: score += 1
        if score >= 4:
            prob = 65 + (score * 6)
            if prob > 92: prob = 92
            hora_mx = datetime.now(pytz.timezone('America/Mexico_City')).strftime('%H:%M:%S')
            msg = f"📈 *SEÑAL BITCOIN V1*\n💰 Activo: {NOMBRE_TG}\n⏰ Hora MX: {hora_mx}\n📊 Dirección: {direccion}\n🎯 Probabilidad: {prob}%\n📈 RSI: {round(rsi,1)} | ADX: {round(adx,1)}\n⏱️ Expiración: 2 minutos"
            send_telegram(msg)
            return True
    except Exception as e:
        print(f"Error: {e}")
    return None

print("BOT BITCOIN V1 INICIADO")
send_telegram("🤖 *BOT BITCOIN V1 CONECTADO* 24/7 Activo. Ya estoy analizando BTC para IQ Option.")
while True:
    try:
        analizar()
        time.sleep(60)
    except:
        time.sleep(60)
