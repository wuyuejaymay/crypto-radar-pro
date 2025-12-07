import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests, httpx
from datetime import datetime

st.set_page_config(page_title="AI加密雷达 Pro", layout="wide")
st.title("AI加密雷达 Pro – Grok 4 实时预测")

if st.secrets.TEST_MODE:
    st.success("免费测试模式（改 secrets.toml 可开启收费）")
else:
    st.warning("正式收费模式")

coins = ["BTC","ETH","SOL","DOGE","PEPE","WIF","TON","BNB","XRP"]
coin = st.selectbox("选择币种", coins)

@st.cache_data(ttl=10)
def get_price(c):
    try:
        d = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={c}USDT").json()
        return float(d['lastPrice']), float(d['priceChangePercent'])
    except: return 0,0

price, change = get_price(coin)
st.metric(coin, f"${price:,.2f}", f"{change:+.2f}%")

@st.cache_data(ttl=60)
def get_klines(c):
    df = pd.DataFrame(requests.get(f"https://api.binance.com/api/v3/klines?symbol={c}USDT&interval=1h&limit=300").json(),
                      columns=['time','open','high','low','close','vol','a','b','c','d','e','f'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df[['open','high','low','close']] = df[['open','high','low','close']].astype(float)
    return df

fig = go.Figure(data=[go.Candlestick(x=get_klines(coin)['time'],
                open=get_klines(coin)['open'], high=get_klines(coin)['high'],
                low=get_klines(coin)['low'], close=get_klines(coin)['close'])])
st.plotly_chart(fig, use_container_width=True)

if st.button("Grok 4 实时预测", type="primary"):
    with st.spinner("Grok 4 正在分析链上数据..."):
        try:
            r = httpx.post("https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {st.secrets.GROK_API_KEY}"},
                json={"model": "grok-4", "messages": [{"role": "user", "content": 
                    f"现在{datetime.now().strftime('%Y-%m-%d %H:%M')}，{coin}价格${price}，24h涨跌{change}%。预测未来1小时和4小时走势，给出多头/空头概率和具体建议（100字内）"}]}).json()
            st.success(r["choices"][0]["message"]["content"])
        except:
            st.error("请在 secrets.toml 填 GROK_API_KEY（免费申请 https://x.ai/api）")

if st.button("生成邀请链接（拉人返30%）"):
    link = f"https://crypto-radar-pro.streamlit.app/?ref=你的ID"
    st.code(link)
    st.success("复制发朋友，拉新返佣30%！")

if st.sidebar.text_input("管理员密码", type="password") == "grok2025":
    st.sidebar.success("管理员模式")
    if st.sidebar.button("切换收费模式"):
        st.sidebar.write("去 secrets.toml 把 TEST_MODE 改成 false 再 push 即可")