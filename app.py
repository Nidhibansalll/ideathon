import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Smart Stock Dashboard", layout="wide")

page = st.sidebar.radio("📊 Navigate", [
    "📦 Pending Orders", 
    "🚨 Low Stock Alerts", 
    "🗃️ History", 
    "📈 Analysis"
])
uploaded_file = st.sidebar.file_uploader("📁 Upload Walmart CSV", type=["csv"])

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

    if 'Status' not in df.columns:
        df['Status'] = 'Pending'
    if 'Current Stock' not in df.columns:
        df['Current Stock'] = 0

    df['Current Stock'] = df['Current Stock'].astype(int)
    df['Needed Stock'] = df['Predicted Quantity']
    df['Gap to Fulfill'] = df['Needed Stock'] - df['Current Stock']

    # 🔔 Alert Summary in Sidebar
    low_stock_count = df[df['Current Stock'] < 20].shape[0]
    high_gap_count = df[df['Gap to Fulfill'] > 100].shape[0]

    with st.sidebar.expander("🚨 Alerts Summary"):
        st.markdown(f"🔴 **Low Stock Items (<20)**: {low_stock_count}")
        st.markdown(f"⚠️ **High Gap Items (>100)**: {high_gap_count}")

    # ====================
    # 📦 PENDING ORDERS
    # ====================
    if page == "📦 Pending Orders":
        st.title("📦 Pending Orders Dashboard")

        pending_df = df[df['Status'] != "Completed"].copy()
        st.subheader("🔍 Search and Filter")

        search_product = st.text_input("🔍 Product Contains")
        search_city = st.text_input("🏙️ City Contains")

        filtered_df = pending_df[
            pending_df['Product line'].str.contains(search_product, case=False, na=False) &
            pending_df['City'].str.contains(search_city, case=False, na=False)
        ].copy().reset_index(drop=True)

        st.markdown("Showing up to 20 editable orders to prevent lag ⚡")
        updated_rows = []

        if not filtered_df.empty:
            for i in range(min(len(filtered_df), 20)):
                st.markdown("---")
                cols = st.columns([3, 3, 2, 2, 2, 2])

                cols[0].markdown(f"**🛍️ {filtered_df.at[i, 'Product line']}**")
                cols[1].markdown(f"📍 {filtered_df.at[i, 'City']}")

                filtered_df.at[i, 'Current Stock'] = cols[2].number_input(
                    "Current Stock", min_value=0, max_value=10000,
                    value=int(filtered_df.at[i, 'Current Stock']), key=f"stock_{i}"
                )

                filtered_df.at[i, 'Gap to Fulfill'] = (
                    filtered_df.at[i, 'Needed Stock'] - filtered_df.at[i, 'Current Stock']
                )

                cols[3].markdown(f"📦 Needed: **{int(filtered_df.at[i, 'Needed Stock'])}**")
                cols[4].markdown(f"📉 Gap: **{int(filtered_df.at[i, 'Gap to Fulfill'])}**")

                filtered_df.at[i, 'Status'] = cols[5].selectbox(
                    "Status", options=["Pending", "Completed"],
                    index=["Pending", "Completed"].index(filtered_df.at[i, 'Status']),
                    key=f"status_{i}"
                )

                # 🚨 Conditional Alerts
                alert_msg = ""
                if filtered_df.at[i, 'Current Stock'] < 20:
                    alert_msg += "🔴 **Low Stock!** "
                if filtered_df.at[i, 'Gap to Fulfill'] > 100:
                    alert_msg += "⚠️ **High Gap!**"

                if alert_msg:
                    st.warning(alert_msg)

                updated_rows.append(filtered_df.iloc[i])

            updated_df = pd.DataFrame(updated_rows)

            if 'Status' in updated_df.columns:
                completed_df = updated_df[updated_df['Status'] == "Completed"].copy()
                still_pending_df = updated_df[updated_df['Status'] != "Completed"].copy()

                if not completed_df.empty:
                    completed_df['Completed At'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    history_df = pd.concat([history_df, completed_df], ignore_index=True)
                    history_df.to_csv(history_file, index=False)

                df = still_pending_df.copy()
        else:
            st.warning("No pending records match your search. Try different filters.")

        st.subheader("📋 Current Pending Inventory")
        st.dataframe(df[df['Status'] != "Completed"], use_container_width=True)

    # ====================
    # 🚨 LOW STOCK ALERTS
    # ====================
    elif page == "🚨 Low Stock Alerts":
        st.title("🚨 Low Stock Alerts")

        alert_df = df[(df['Current Stock'] < 20) & (df['Status'] != "Completed")].copy()
        alert_df = alert_df.sort_values(by='Current Stock')

        if not alert_df.empty:
            st.subheader("🧯 Items with Stock < 20")
            st.dataframe(alert_df, use_container_width=True)
        else:
            st.success("✅ No critical low-stock items right now!")

    # ====================
    # 🗃️ HISTORY PAGE
    # ====================
    elif page == "🗃️ History":
        st.title("🗃️ Completed Orders History")

        if not history_df.empty:
            history_df['Completed At'] = pd.to_datetime(history_df['Completed At'])
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
