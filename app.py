import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('GAFAMN株価可視化アプリ')

st.sidebar.write("""
# GAFAMN株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示期間選択
""")

days_dict = {
    '1日':'1d', '5日':'5d', '1ヶ月':'1mo', '3ヶ月':'3mo', '6ヶ月':'6mo', 
    '1年':'1y', '2年':'2y', '5年':'5y', '10年':'10y', '当会計年度':'ytd', '最大データ':'max'    
}

# days = st.sidebar.slider('日数', 1, 1000, 20)
days_key = st.sidebar.selectbox('表示期間を選んでください。', 
                 ('1日','5日','1ヶ月','3ヶ月','6ヶ月','1年','2年','5年','10年','当会計年度','最大データ'))

days = days_dict.get(days_key)

st.write(f"""
## 過去 **{days_key}間** のGAFAMNの株価
""")

@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=days)
        hist.index = hist.index.strftime('%d %B %Y')
        hist.index.name = 'Date'
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        df = pd.concat([df, hist], sort=False)
    return df



try:
    st.sidebar.write("""
    ## 株価の表示範囲
    """)

    ymin, ymax = st.sidebar.slider(
        '表示範囲を指定してください。', 
        0.0, 3600.0, (0.0, 3600.0)
    )

    tickers = {
        'Google': 'GOOG', 
        'Amazon': 'AMZN', 
        'Facebook': 'FB', 
        'Apple': 'AAPL', 
        'Microsoft': 'MSFT', 
        'Netflix': 'NFLX'
    }

    df = get_data(days, tickers)

    companies = st.multiselect(
        '会社名を選択してください。', 
        list(df.index), 
        ['Google', 'Amazon', 'Facebook', 'Apple'], 
    )

    if not companies:
        st.error('少なくとも1社を選んでください。')
    else:
        data = df.loc[companies]
        st.write('### 株価(USD)', data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'variable':'Name', 'value':'Stock Pricies(USD)'})
        
        # st.write(data)
        
        chart = (
        alt.Chart(data)
        .mark_line(opacity=0.8, clip=True)
        .encode(
            x="Date:T", 
            y=alt.Y("Stock Pricies(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])), 
            color='Name:N'
            )
        )

        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
    'エラーを検知しました。'
    )