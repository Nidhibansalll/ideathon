import streamlit as st

def render_help_demo_page():
    st.title("🆘 Help Center & Demo")

    # 🛍️ Walmart Intro
    st.markdown("""
    <h3 style='color:#FF4B00;'>🛒 Welcome to <strong>Walmart Smart Stock Dashboard</strong></h3>

    <p style='font-size:16px;'>
    Walmart, one of the world’s largest retail giants, operates thousands of stores across multiple countries.<br><br>
    Efficient <strong style='color:#FF6F00;'>inventory management</strong> is crucial to ensure that every store remains stocked with the right products at the right time.
    </p>

    <p style='font-size:16px;'>
    This <strong style='color:#0078D7;'>Smart Stock Dashboard</strong> uses <strong>Machine Learning</strong> to predict stock needs based on <em>location, product type, and previous sales.</em><br>
    It helps store managers stay ahead of demand, prevent stockouts, and optimize warehouse replenishment.
    </p>

    <hr style='border: 1px solid #FF6F00;'>
    """, unsafe_allow_html=True)

    st.header("📽️ How to Use the Dashboard")
    st.markdown("""
    <ol style='font-size:16px;'>
        <li><strong>Upload the Cleaned Walmart CSV</strong> from the sidebar.</li>
        <li>ML will predict <span style='color:#FF6F00;'><strong>Needed Stock</strong></span> using product & location.</li>
        <li>Check the 📦 <strong>Pending Orders</strong> and mark as <span style='color:#28A745;'><strong>Completed</strong></span> when fulfilled.</li>
        <li>Get 🚨 <span style='color:#DC3545;'><strong>Low Stock Alerts</strong></span> instantly.</li>
        <li>View 🗃️ <strong>History</strong> of completed orders.</li>
        <li>Analyze patterns under 📈 <strong>Analysis</strong>.</li>
    </ol>
    """, unsafe_allow_html=True)

    st.subheader("🎬 Demo Video")
    try:
        video_file = open("demo_video.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes)
    except FileNotFoundError:
        st.warning("🚫 Demo video not found. Please place <em>'demo_video.mp4'</em> in the project folder.")

    st.header("💡 Frequently Asked Questions")

    with st.expander("🛒 What is the goal of this dashboard?"):
        st.markdown("<span style='font-size:15px;'>This tool helps <strong>Walmart stores</strong> manage inventory and predict stock needs using <span style='color:#0078D7;'>Machine Learning</span>.</span>", unsafe_allow_html=True)

    with st.expander("📁 What format should the CSV be in?"):
        st.markdown("<span style='font-size:15px;'>It should contain columns like <strong>Date, City, Product line, Unit price, Quantity</strong>, etc.</span>", unsafe_allow_html=True)

    with st.expander("📉 What is 'Needed Stock'?"):
        st.markdown("<span style='font-size:15px;'>It’s the predicted number of units required, calculated using a trained <strong>ML model</strong>.</span>", unsafe_allow_html=True)

    with st.expander("⚠️ What happens if Current Stock is too low?"):
        st.markdown("<span style='font-size:15px; color:#DC3545;'>You’ll receive <strong>Low Stock Alerts</strong> so you can restock timely.</span>", unsafe_allow_html=True)

    with st.expander("📦 Can I update stock and status manually?"):
        st.markdown("<span style='font-size:15px;'>Yes! Go to <strong>Pending Orders</strong> to edit stock and mark orders as <span style='color:#28A745;'>Completed</span>.</span>", unsafe_allow_html=True)

    # Replacing st.success with styled markdown to allow HTML
    st.markdown(
        """
        <div style='padding:10px; background-color:#d4edda; border:1px solid #c3e6cb; border-radius:5px; color:#155724; font-size:16px;'>
        📧 For more help, contact <a href='mailto:support@walmartdemo.com' style='color:#155724; text-decoration:underline;'>support@walmartdemo.com</a>
        </div>
        """,
        unsafe_allow_html=True
    )
