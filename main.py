import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay

# --- Configuration ---
stock_data_dir = 'E:/DESKTOP-STUFF/py-code/stocks_data'  # <-- Update this to your folder
PAGE_TITLE = "Momentum Investment Scanner"
PAGE_ICON = "📈"
LOADING_TEXT = "Analyzing Stocks..."

# --- Streamlit Setup ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
def initialize_session_state():
    for key in ['view_universe_rankings', 'view_recommended_stocks', 'analyze_button_clicked']:
        if key not in st.session_state:
            st.session_state[key] = False
initialize_session_state()

# --- Styling ---
def inject_custom_css():
    st.markdown("""
        <style>
            header, footer {visibility: hidden;}
            .loading-container {
                display: flex; flex-direction: column; align-items: center;
                background: #1e1e1e; padding: 20px; border-radius: 10px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.4); margin: 20px 0;
            }
            .loading-text {
                color: #64ffda; font-size: 1.2rem; margin-top: 20px;
            }
        </style>
    """, unsafe_allow_html=True)
inject_custom_css()

# --- Title ---
st.markdown(f"""
    <h1 style='text-align: center;'>{PAGE_ICON} {PAGE_TITLE}</h1>
    <div style="text-align: center; font-size: 1.1rem; color: #aaa;">
       Select a sector to analyze top momentum stocks. Also view overall sector rankings and top picks.
    </div><br>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def get_sector_universes(stock_data_dir):
    sector_mapping = {}
    for filename in os.listdir(stock_data_dir):
        if filename.endswith('.csv'):
            ticker = os.path.splitext(filename)[0]
            path = os.path.join(stock_data_dir, filename)
            try:
                df = pd.read_csv(path, nrows=1)
                df.columns = [col.strip().upper() for col in df.columns]
                sector = df.get('SECTOR NAME', ['Unknown'])[0]
                sector_mapping.setdefault(sector or 'Unknown', []).append(ticker)
            except:
                continue
    return sector_mapping

SECTOR_UNIVERSE = get_sector_universes(stock_data_dir)

def create_sidebar():
    with st.sidebar:
        sector = st.radio("Select Sector", list(SECTOR_UNIVERSE.keys()))
        tickers = SECTOR_UNIVERSE[sector]
        st.info(f"'{sector}' sector: {len(tickers)} stocks")
        if st.button("Analyze Sector Universe"): st.session_state.analyze_button_clicked = True
        if st.button("Sector Rankings"): st.session_state.view_universe_rankings = True
        if st.button("Top Recommended Stocks"): st.session_state.view_recommended_stocks = True
    return sector, tickers

sector_universe_name, universe_tickers = create_sidebar()

def read_local_stock_data(ticker, start_date, end_date):
    path = os.path.join(stock_data_dir, f"{ticker}.csv")
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = [col.strip().upper() for col in df.columns]
    if 'DATE1' not in df.columns or 'CLOSE_PRICE' not in df.columns: return pd.DataFrame()
    df['DATE1'] = pd.to_datetime(df['DATE1'], errors='coerce')
    df = df.dropna(subset=['DATE1'])
    df = df[(df['DATE1'] >= pd.to_datetime(start_date)) & (df['DATE1'] <= pd.to_datetime(end_date))]
    df.rename(columns={'DATE1': 'Date', 'CLOSE_PRICE': 'Close'}, inplace=True)
    df.set_index('Date', inplace=True)
    return df.sort_index()

def calculate_returns(df, period):
    if df.empty or len(df) < 30: return np.nan
    df = df.sort_index()
    latest = df.index.max()
    try:
        past_date = latest - BDay(period)
        if past_date not in df.index:
            df_before = df[df.index <= past_date]
            if df_before.empty: return np.nan
            past_date = df_before.index[-1]
        start_price = df.loc[past_date, 'Close']
        end_price = df.loc[latest, 'Close']
        return (end_price - start_price) / start_price
    except: return np.nan

def analyze_universe(universe_name, universe_tickers):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=400)
    results = []
    for ticker in universe_tickers:
        df = read_local_stock_data(ticker, start_date, end_date)
        if df.empty: continue
        df = df[~df.index.duplicated()].sort_index()
        df_weekly = df.resample('W').last()
        df_weekly['Weekly Return'] = df_weekly['Close'].pct_change()
        volatility = df_weekly['Weekly Return'].dropna().std() * np.sqrt(52)
        r12 = calculate_returns(df, 252)
        r6 = calculate_returns(df, 126)
        r3 = calculate_returns(df, 63)
        score = ((0.6 * r12 + 0.3 * r6 + 0.1 * r3) / volatility) if all(pd.notna([r12, r6, r3])) and volatility else np.nan
        results.append({
            "Ticker": ticker,
            "Momentum Score": score,
            "12-Month Return (%)": r12 * 100 if pd.notna(r12) else np.nan,
            "6-Month Return (%)": r6 * 100 if pd.notna(r6) else np.nan,
            "3-Month Return (%)": r3 * 100 if pd.notna(r3) else np.nan,
            "Annualized Volatility": volatility
        })
    df_out = pd.DataFrame(results)
    avg_score = df_out["Momentum Score"].mean() if not df_out.empty else np.nan
    return df_out, avg_score

def get_top_universes_by_momentum():
    result = []
    for sector, tickers in SECTOR_UNIVERSE.items():
        _, avg_score = analyze_universe(sector, tickers)
        result.append({"Sector": sector, "Avg Momentum": avg_score})
    df = pd.DataFrame(result).sort_values("Avg Momentum", ascending=False)
    return df

def get_top_stocks_from_universe(name, tickers):
    df, _ = analyze_universe(name, tickers)
    return df.sort_values("Momentum Score", ascending=False)

# --- Main App Logic ---
def main():
    if st.session_state.analyze_button_clicked:
        st.subheader(f"Momentum Analysis for {sector_universe_name}")
        loading = st.empty()
        loading.markdown(f"<div class='loading-container'><p class='loading-text'>{LOADING_TEXT}</p></div>", unsafe_allow_html=True)
        try:
            df, _ = analyze_universe(sector_universe_name, universe_tickers)
            loading.empty()
            if not df.empty:
                df.sort_values("Momentum Score", ascending=False, inplace=True)
                st.dataframe(df.style.format({
                    "12-Month Return (%)": "{:.2f}%",
                    "6-Month Return (%)": "{:.2f}%",
                    "3-Month Return (%)": "{:.2f}%",
                    "Annualized Volatility": "{:.4f}",
                    "Momentum Score": "{:.4f}"
                }), use_container_width=True)
            else:
                st.warning("No data available for this sector.")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state.analyze_button_clicked = False

    if st.session_state.view_recommended_stocks:
        st.subheader("Top Recommended Stocks by Sector")
        loading = st.empty()
        loading.markdown(f"<div class='loading-container'><p class='loading-text'>{LOADING_TEXT}</p></div>", unsafe_allow_html=True)
        try:
            universes = get_top_universes_by_momentum()
            loading.empty()
            for _, row in universes.iterrows():
                st.markdown(f"### {row['Sector']} (Avg Score: {row['Avg Momentum']:.4f})")
                top_stocks = get_top_stocks_from_universe(row['Sector'], SECTOR_UNIVERSE[row['Sector']])
                if not top_stocks.empty:
                    st.dataframe(top_stocks[['Ticker', 'Momentum Score', '12-Month Return (%)', '6-Month Return (%)', '3-Month Return (%)']], height=300)
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state.view_recommended_stocks = False

    if st.session_state.view_universe_rankings:
        st.subheader("Sector Rankings by Average Momentum")
        loading = st.empty()
        loading.markdown(f"<div class='loading-container'><p class='loading-text'>{LOADING_TEXT}</p></div>", unsafe_allow_html=True)
        try:
            df = get_top_universes_by_momentum()
            loading.empty()
            st.dataframe(df.style.format({"Avg Momentum": "{:.4f}"}))
            st.success(f"Top Sector: {df.iloc[0]['Sector']} ({df.iloc[0]['Avg Momentum']:.4f})")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state.view_universe_rankings = False

if __name__ == '__main__':
    main()
