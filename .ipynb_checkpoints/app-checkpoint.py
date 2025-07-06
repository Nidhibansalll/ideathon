import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# Page setup
st.set_page_config(page_title="Smart Stock Dashboard", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("📊 Navigate", ["📦 Pending Orders", "🗃️ History", "📈 Analysis"])
uploaded_file = st.sidebar.file_uploader("📁 Upload Walmart CSV", type=["csv"])

# Load history file
history_file = "stock_history.csv"
try:
    history_df = pd.read_csv(history_file)
    if 'Completed At' in history_df.columns:
        history_df['Completed At'] = pd.to_datetime(history_df['Completed At'])
except FileNotFoundError:
    history_df = pd.DataFrame()

if uploaded_file:
    @st.cache_data
    def load_data(file):
        return pd.read_csv(file)

    df = load_data(uploaded_file)

    # Add required columns
    if 'Status' not in df.columns:
        df['Status'] = 'Pending'
    if 'Current Stock' not in df.columns:
        df['Current Stock'] = 0

    df['Current Stock'] = df['Current Stock'].astype(int)
    df['Needed Stock'] = df['Predicted Quantity']
    df['Gap to Fulfill'] = df['Needed Stock'] - df['Current Stock']

    # ====================
    # 📦 PENDING ORDERS
    # ====================
    if page == "📦 Pending Orders":
        st.title("📦 Pending Orders Dashboard")

        pending_df = df[df['Status'] != "Completed"].copy()
        updated_rows = []

        st.subheader("✏️ Edit Pending Orders")

        for i in range(len(pending_df)):
            st.markdown("---")
            cols = st.columns([3, 3, 2, 2, 2, 2])

            cols[0].markdown(f"**🛍️ {pending_df.at[i, 'Product line']}**")
            cols[1].markdown(f"📍 {pending_df.at[i, 'City']}")

            pending_df.at[i, 'Current Stock'] = cols[2].number_input(
                "Current Stock", min_value=0, max_value=10000,
                value=int(pending_df.at[i, 'Current Stock']), key=f"stock_{i}"
            )

            pending_df.at[i, 'Gap to Fulfill'] = (
                pending_df.at[i, 'Needed Stock'] - pending_df.at[i, 'Current Stock']
            )

            cols[3].markdown(f"📦 Needed: **{int(pending_df.at[i, 'Needed Stock'])}**")
            cols[4].markdown(f"📉 Gap: **{int(pending_df.at[i, 'Gap to Fulfill'])}**")

            pending_df.at[i, 'Status'] = cols[5].selectbox(
                "Status", options=["Pending", "Completed"],
                index=["Pending", "Completed"].index(pending_df.at[i, 'Status']),
                key=f"status_{i}"
            )

            updated_rows.append(pending_df.iloc[i])

        # Rebuild DataFrame after edits
        updated_df = pd.DataFrame(updated_rows)

        # Separate completed and pending
        completed_df = updated_df[updated_df['Status'] == "Completed"].copy()
        still_pending_df = updated_df[updated_df['Status'] != "Completed"].copy()

        # Add timestamp and save completed
        if not completed_df.empty:
            completed_df['Completed At'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            history_df = pd.concat([history_df, completed_df], ignore_index=True)
            history_df.to_csv(history_file, index=False)

        # Update the original df by keeping non-completed rows and untouched rows
        untouched_df = df[(df['Status'] != "Completed") & ~df.index.isin(updated_df.index)]
        df = pd.concat([still_pending_df, untouched_df], ignore_index=True)

        # Show pending only
        st.subheader("📋 Current Pending Inventory")
        st.dataframe(df[df['Status'] != "Completed"], use_container_width=True)

    # ====================
    # 🗃️ HISTORY PAGE
    # ====================
    elif page == "🗃️ History":
        st.title("🗃️ Completed Orders History")

        if not history_df.empty:
            min_date = history_df['Completed At'].min().date()
            max_date = history_df['Completed At'].max().date()

            date_range = st.date_input("📅 Filter by Completion Date", (min_date, max_date))

            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                filtered_history = history_df[
                    (history_df['Completed At'].dt.date >= start_date) &
                    (history_df['Completed At'].dt.date <= end_date)
                ]
                st.dataframe(filtered_history, use_container_width=True)
            else:
                st.warning("Please select a valid date range.")
        else:
            st.info("No completed records found yet.")

    # ====================
    # 📈 ANALYSIS PAGE
    # ====================
    elif page == "📈 Analysis":
        st.title("📈 Stock Analysis Dashboard")

        active_df = df[df['Status'] != "Completed"].copy()

        st.subheader("🔍 Filter by City & Product")
        col1, col2 = st.columns(2)

        cities = col1.multiselect("🏙️ Cities", active_df['City'].unique(), default=active_df['City'].unique())
        products = col2.multiselect("🛍️ Products", active_df['Product line'].unique(), default=active_df['Product line'].unique())

        filtered_df = active_df[
            (active_df['City'].isin(cities)) & 
            (active_df['Product line'].isin(products))
        ]

        st.subheader("📊 Needed vs Current Stock (Top 10 Products)")
        bar_df = filtered_df.groupby('Product line')[['Needed Stock', 'Current Stock']].sum().reset_index()
        bar_df = bar_df.sort_values('Needed Stock', ascending=False).head(10)

        if not bar_df.empty:
            st.bar_chart(bar_df.set_index('Product line'))
        else:
            st.warning("No data to display in bar chart.")

        st.subheader("🥧 Product Demand Share")
        pie_df = filtered_df.groupby('Product line')['Needed Stock'].sum().reset_index()

        if not pie_df.empty:
            fig = px.pie(pie_df, names='Product line', values='Needed Stock', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display in pie chart.")

    # 📥 Download Updated Data
    st.sidebar.download_button("💾 Download Updated Data", df.to_csv(index=False), "updated_stock_data.csv", "text/csv")

else:
    st.info("📥 Please upload your cleaned Walmart dataset to begin.")
