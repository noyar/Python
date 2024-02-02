import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from streamlit.components.v1 import components


# 'https://www.cftc.gov/files/dea/history/deacot2023.zip'

def cot_data_prep():
    dff = pd.read_csv('annual.txt')
    df = dff.copy()

    df = df[['Market and Exchange Names', 'As of Date in Form YYYY-MM-DD', 'Noncommercial Positions-Long (All)',
            'Noncommercial Positions-Short (All)', 'Change in Noncommercial-Long (All)', 'Change in Noncommercial-Short (All)']]
    df.columns = ['currency', 'date', 'long' ,'short', 'long_change', 'short_change' ]
    df.date = pd.to_datetime(df.date)
    df['long_change'], df['short_change'] = df['long_change'].replace('.' ,0), df['short_change'].replace('.' ,0)
    df['currency'] = [i.replace("GOLD - COMMODITY EXCHANGE INC.", "GOLD") 
                        .replace("CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",  "CAD") 
                        .replace("AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE", "AUD") 
                        .replace("BRITISH POUND - CHICAGO MERCANTILE EXCHANGE", "GBP") 
                        .replace("SWISS FRANC - CHICAGO MERCANTILE EXCHANGE", "CHF")
                        .replace("USD INDEX - ICE FUTURES U.S.", "USD")
                        .replace("JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE", "JPY") 
                        .replace("NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE", "NZD") 
                        .replace("EURO FX - CHICAGO MERCANTILE EXCHANGE", "EUR")
                        .replace("S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE", "S&P500") 
                        .replace("NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE", "NAS100") 
                        .replace("WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE", "OIL") 
                        .replace("DJIA x $5 - CHICAGO BOARD OF TRADE", "US30")
                        .replace('SILVER - COMMODITY EXCHANGE INC.', 'SILVER')
                        .replace('PLATINUM - NEW YORK MERCANTILE EXCHANGE', 'PLATM')
                        .replace('BITCOIN - CHICAGO MERCANTILE EXCHANGE', 'BITCOIN')
                        .replace('RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE', 'RUSSELL')
                        .replace('UST 2Y NOTE - CHICAGO BOARD OF TRADE', 'US2Y')
                        .replace('UST 10Y NOTE - CHICAGO BOARD OF TRADE', 'US10Y')
                        for i in df['currency']]

    for r in ['long', 'short', 'long_change', 'short_change']:
        df[r] = df[r].astype(int)

    df.date  =pd.to_datetime(df.date)  

    def by_size(words,size):
        result = []
        for word in words:
            if len(word)<=size:
                result.append(word)
        return result

    cot_df= df[df['currency'].isin(by_size(df['currency'].unique(),7))]
    cot_df = cot_df[cot_df.date == cot_df.date.max()]
    cot_df['long%'] = round(cot_df['long'] / (cot_df['long'] + cot_df['short']),2)
    cot_df['short%'] = round(cot_df['short'] / (cot_df['long'] + cot_df['short']),2)
    cot_df['LongCh%'] = round(cot_df.long_change/(cot_df.long - cot_df.long_change) * 100, 2)
    cot_df['ShortCh%'] = round(cot_df.short_change/(cot_df.short - cot_df.short_change) * 100, 2)
    cot_df = cot_df[['date','currency', 'long', 'long%','long_change', 'LongCh%', 'short', 'short%','short_change', 'ShortCh%']]

    return cot_df
#=============================COT Table Data
def tableData():
    cot_table = cot_data_prep().copy()
    cot_table = cot_table[['currency', 'long%', 'short%','LongCh%',  'ShortCh%']]
    sig = []
    for i in range(len(cot_table)):
        if ((cot_table.iloc[i]['long%'] > cot_table.iloc[i]['short%']) and 
            ((cot_table.iloc[i]['ShortCh%']<0) and (cot_table.iloc[i]['LongCh%']<0) or #both Negative
            (cot_table.iloc[i]['ShortCh%']>0) and (cot_table.iloc[i]['LongCh%']>0) or #both Negative
            (cot_table.iloc[i]['ShortCh%']<0) and (cot_table.iloc[i]['LongCh%']>0)    #ShortCh-Negative |  LongCh-Positive  
            ) and (cot_table.iloc[i]['ShortCh%'] <  cot_table.iloc[i]['LongCh%'] )):
            sig.append('Buy') 
        
        elif ((cot_table.iloc[i]['long%'] < cot_table.iloc[i]['short%']) and
            ((cot_table.iloc[i]['ShortCh%']<0) and (cot_table.iloc[i]['LongCh%']<0) or #both Negative
            (cot_table.iloc[i]['ShortCh%']>0) and (cot_table.iloc[i]['LongCh%']>0) or #both Negative
            (cot_table.iloc[i]['ShortCh%']>0) and (cot_table.iloc[i]['LongCh%']<0)    #ShortCh-Positive |  LongCh-Negative  
            ) and (cot_table.iloc[i]['ShortCh%'] >  cot_table.iloc[i]['LongCh%'] )):
            sig.append('Sell') 
        else:
            sig.append('Neutral') 
    cot_table['Signal'] = sig
    cot_table['LongCh%'], cot_table['ShortCh%']  = [str(i)+'%' for i in cot_table['LongCh%']], [str(i)+'%' for i in cot_table['ShortCh%']]
    cot_table.columns = ['Currency', 'Longs', 'Shorts','Long Change', 'Short Change', 'Signal']

    fig = ff.create_table(cot_table, font_colors = ['#FFFFFF'], 
                            height_constant=21.8,
                            colorscale=[[0, '#77ab59'],[.5, '#404040'],[1, '#2C2C2C']], 
                            )
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 16

    return fig
#=============================COT BarChart Data 
def barchartData():
    cot_chart = cot_data_prep().copy()
    cot_chart = cot_chart.sort_values('long%', ascending = False).reset_index(drop = True)
    fig = px.bar(cot_chart, x='currency', y=['long%', 'short%'], barmode='stack', 
                color_discrete_sequence=['#00FF00', '#FF0000'])
    fig.update_layout(
    title='COT Report as of ',# + cot_chart.date.max().strftime('%Y-%m-%d'),
    xaxis_title=None, 
    yaxis_title=None,
    showlegend = False,
    title_x=0.35,
    height=500,  
    width=1200)

    return fig
#=============================News Data Pull
news = '''
<div id="economicCalendarWidget"></div>
<script async type="text/javascript" data-type="calendar-widget" src="https://www.tradays.com/c/js/widgets/calendar/widget.js?v=13">
  {"width":"100%","height":480,"mode":"1","theme":1}
</script>

'''
dailyBrief = '''
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
  {
  "feedMode": "all_symbols",
  "isTransparent": false,
  "displayMode": "regular",
  "width": "100%",
  "height": "600",
  "colorTheme": "dark",
  "locale": "en"
}
  </script>
</div>
<!-- TradingView Widget END -->
'''
#=============================Chart Data Pull
def chart(chart ='USOIL', TF ='H4', height ='500'):
        
    return '''
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
    <div id="tradingview_c2c0f"></div>
    <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" 
        target="_blank"><span class="blue-text"></span></a></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget(
        {
            "width": "100%",
            "height": '''+height+''',
            "symbol": "''' + chart +'''",
            "interval": "'''+TF+'''",
            "timezone": "America/New_York",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "enable_publishing": true,
            "allow_symbol_change": false,
            "studies": ["STD;EMA"], 
            "hide_volume": true,
            "container_id": "tradingview_c2c0f"
        }
        );
        </script>
        </div>
    <!-- TradingView Widget END -->
    '''
#=============================Retail Data Pull
retail_sent = '''
<!-- myfxbook.com outlook widget - Start -->
<div>
    <script class="powered" type="text/javascript"
            src="https://widgets.myfxbook.com/scripts/fxOutlook.js?type=1&symbols=,1,2,3,4,5,7,9,11,12,28,50,51,1209,1864,2348">
              
            </script>
</div>
<div style="font-size: 08px">
<a href="https://www.myfxbook.com" title="" class="myfxbookLink" target="_self" rel="noopener">
            Powered by Myfxbook.com</a>
    </div>

<script type="text/javascript">showOutlookWidget()</script>
<!-- myfxbook.com outlook widget - End -->
'''
#=============================TA Data Pull
def ta(sym =  "XAUUSD", tall = "360"):
    return '''

    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
    <div class="tradingview-widget-container__widget"></div>
    <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    {
    "interval": "4h",
    "width": "100%",
    "isTransparent": false,
    "height": '''+tall+''',
    "symbol": "OANDA:'''+sym+'''",
    "showIntervalTabs": false,
    "displayMode": "single",
    "locale": "en",
    "colorTheme": "dark"
    }
    </script>
    </div>
    <!-- TradingView Widget END -->

    '''

# ==================Page Setup=======================
st.set_page_config(page_title= 'Utimate Trading Tool', layout = 'wide')

tabOV, tabCH, tabGold, tabDXY, tabTA = st.tabs(['OverView', 'Major Charts', 'Gold Multi TF Chart', 
                                                'USD Index Multi TF Chart', 'Technical Signals'])  

with tabOV:
                       
    col1, col2, col_space, col3, col4 = st.columns([0.01, 0.35, 0.005, 0.35, 0.01])
        
    with col2:
        st.plotly_chart(barchartData(), 500) #['#FFFFFF']
        st.plotly_chart(tableData(), use_container_width=True, )
        #st.components.v1.html(dailyBrief, height=600)
    with col3:
        st.markdown('') 
        st.markdown('',) 
        st.markdown('') 
        st.markdown('') 
        st.components.v1.html(retail_sent, height=400)
        st.markdown('') 
        st.markdown('') 
        st.components.v1.html(news, height=800)

with tabCH:
    with st.expander('USD Index'):
        st.components.v1.html(chart(chart = 'DXY', TF = '240', height=f'{900}'),  height = 1000)
    col5, col6, col7 = st.columns([0.33,0.33,0.33])
    tall = 450
    tf = '240'
    with col5:
        st.components.v1.html(chart(chart = "US30", TF = tf, height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = "NAS100",TF = tf, height=f'{tall}'),  height = tall)

    with col6:
        st.components.v1.html(chart(chart = "USOIL", TF = tf, height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = "SPX500", TF = tf, height=f'{tall}'),  height = tall)    
   
    with col7:
        st.components.v1.html(chart(chart = "EURUSD", TF = tf, height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = "XAUUSD", TF = tf, height=f'{tall}'),  height = tall)    
    
with tabTA:

    tab1, tab2 = st.tabs(['USD PAIRS', 'JPY Pairs'])

    with tab1:
        col8, col9, col10, col11 = st.columns((4))
        with col8:
            high = 360
            st.components.v1.html(ta("EURUSD"), height = high)
            st.components.v1.html(ta("GBPUSD"), height = high)
        
        with col9:
            st.components.v1.html(ta("AUDUSD"), height = high)
            st.components.v1.html(ta("NZDUSD"), height = high)
                
        with col10:
            st.components.v1.html(ta("USDJPY"), height = high)
            st.components.v1.html(ta("USDCAD"), height = high)

        with col11:
            st.components.v1.html(ta("USDCHF"), height = high)
            st.components.v1.html(ta("XAUUSD"), height = high)

    with tab2:
        col8, col9, col10, col11, col12  = st.columns([0.1,0.2,0.2,0.2,0.1])
        with col9:
            high = 360
            st.components.v1.html(ta("EURJPY"), height = high)
            st.components.v1.html(ta("GBPJPY"), height = high)
        
        with col10:
            st.components.v1.html(ta("AUDJPY"), height = high)
            st.components.v1.html(ta("NZDJPY"), height = high)
                
        with col11:
            st.components.v1.html(ta("CADJPY"), height = high)
            st.components.v1.html(ta("CHFJPY"), height = high)

        with col8:
            pass

with tabDXY:
    col5, col6, col7 = st.columns([0.33,0.33,0.33])
    tall = 450
    sym = 'DXY'
    with col5:
        st.components.v1.html(chart(chart = sym, TF = '12M', height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = sym,TF = '1M', height=f'{tall}'),  height = tall)

    with col6:
        st.components.v1.html(chart(chart = sym, TF = '6M', height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = sym, TF = 'W', height=f'{tall}'),  height = tall)    
   
    with col7:
        st.components.v1.html(chart(chart = sym, TF = '3M', height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = sym, TF = 'D', height=f'{tall}'),  height = tall) 

with tabGold:
    col5, col6, col7 = st.columns([0.33,0.33,0.33])
    tall = 450
    sym = 'XAUUSD'
    with col5:
        st.components.v1.html(ta(sym, str(tall)), height = tall)
        #st.components.v1.html(chart(chart = sym, TF = '6M', height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = sym,TF = 'W', height=f'{tall}'),  height = tall)

    with col6:
        st.components.v1.html(chart(chart = sym, TF = '3M', height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = sym, TF = 'D', height=f'{tall}'),  height = tall)    
   
    with col7:
        st.components.v1.html(chart(chart = sym, TF = 'M', height=f'{tall}'),  height = tall)
        st.components.v1.html(chart(chart = sym, TF = '240', height=f'{tall}'),  height = tall) 






