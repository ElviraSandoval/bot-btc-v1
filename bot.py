import yfinance as yf
import pandas as pd
import ta
import requests
import time
from datetime import datetime
import pytz

# --- CONFIG ---
TOKEN = "8322501362:AAHiCcYtA4g7bik2w3p2i2aR7U2v3sS9l8M" # Tu token, no lo cambies
CHAT_ID = "7853364550"
SYMBOL = "BTC-USD"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def get_data(interval):
    df = yf.download(SYMBOL, period="2d", interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def analizar():
    # Revisión de 1 min y 3 min como el de oro
    df1 = get_data("1m")
    df3 = get_data("3m")
    
    if len(df1) < 100 or len(df3) < 100:
        return None

    for df in [df1, df3]:
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        df['EMA9'] = ta.trend.EMAIndicator(df['Close'], 9).ema_indicator()
        df['EMA21'] = ta.trend.EMAIndicator(df['Close'], 21).ema_indicator()
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], 14)
        df['ADX'] = adx.adx()
        df['DI+'] = adx.adx_pos()
        df['DI-'] = adx.adx_neg()

    c1 = df1.iloc[-1]
    c3 = df3.iloc[-1]
    
    prob = 0
    direccion = None

    # LOGICA DUPLICADA DEL ORO - COMPRA
    if c1['RSI'] > 50 and c1['EMA9'] > c1['EMA21'] and c1['DI+'] > c1['DI-'] and c1['ADX'] > 20:
        if c3['EMA9'] > c3['EMA21'] and c3['RSI'] > 50:
            direccion = "COMPRA 🟢 (CALL)"
            prob = 78 + (c1['ADX'] - 20)

    # LOGICA DUPLICADA DEL ORO - VENTA
    if c1['RSI'] < 50 and c1['EMA9'] < c1['EMA21'] and c1['DI-'] > c1['DI+'] and c1['ADX'] > 20:
        if c3['EMA9'] < c3['EMA21'] and c3['RSI'] < 50:
            direccion = "VENTA 🔴 (PUT)"
            prob = 78 + (c1['ADX'] - 20)

    if direccion and prob >= 75:
        if prob > 92: prob = 92
        tz = pytz.timezone('America/Mexico_City')
        hora_mx = datetime.now(tz).strftime("%H:%M:%S")
        
        mensaje = f"""📈 *SEÑAL BITCOIN V1 - DUPLICADO ORO*
💰 *Activo:* Bitcoin - IQ Option REAL
⏰ *Hora MX:* {hora_mx}
📊 *Dirección:* {direccion}
🎯 *Probabilidad:* {int(prob)}%
📈 *RSI:* {c1['RSI']:.1f} | *ADX:* {c1['ADX']:.1f}
⏱️ *Expiración:* 5 minutos
*Revisión: 1m y 3m*"""
        return mensaje
    return None

# --- INICIO ---
send_telegram("🤖 *BOT BITCOIN V1 CONECTADO*\nDuplicado del ORO - 5 Min - BTC REAL")
print("BOT BITCOIN V1 INICIADO - 5 MIN")

ultima_senal = ""
while True:
    try:
        senal = analizar()
        if senal and senal != ultima_senal:
            send_telegram(senal)
            ultima_senal = senal
            time.sleep(300) # 5 min cooldown como el de oro
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
