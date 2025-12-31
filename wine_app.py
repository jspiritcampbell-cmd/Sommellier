import streamlit as st
import google.generativeai as genai
import requests
import json

# Hardcoded API key (replace with your actual key)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Wine API endpoint (using Sampleapis wine API)
WINE_API_URL = "https://api.sampleapis.com/wines/reds"

st.set_page_config(page_title="AI Sommelier Wine Shop", page_icon="🍷", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #8B0000;
        text-align: center;
        margin-bottom: 2rem;
    }
    .wine-card {
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #ddd;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🍷 AI Sommelier Wine Shop</h1>', unsafe_allow_html=True)

# Sidebar for wine preferences
st.sidebar.header("Your Wine Preferences")
wine_type = st.sidebar.selectbox(
    "Preferred Wine Type",
    ["Red", "White", "Rosé", "Sparkling", "Dessert", "Any"]
)
price_range = st.sidebar.select_slider(
    "Price Range",
    options=["Budget ($)", "Moderate ($$)", "Premium ($$$)", "Luxury ($$$$)"]
)
taste_profile = st.sidebar.multiselect(
    "Taste Preferences",
    ["Dry", "Sweet", "Fruity", "Oaky", "Bold", "Light", "Crisp", "Smooth"]
)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["🎯 Meal Pairing", "🍇 Browse Wines", "💬 Ask the Sommelier"])

# Tab 1: Meal Pairing
with tab1:
    st.header("Find the Perfect Wine for Your Meal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        meal_type = st.selectbox(
            "What are you eating?",
            ["Appetizers", "Seafood", "Poultry", "Red Meat", "Pasta", 
             "Vegetarian", "Dessert", "Cheese Board"]
        )
        
        meal_description = st.text_area(
            "Describe your dish (optional)",
            placeholder="e.g., Grilled salmon with lemon butter sauce",
            height=100
        )
    
    with col2:
        occasion = st.selectbox(
            "What's the occasion?",
            ["Casual Dinner", "Romantic Evening", "Celebration", 
             "Business Dinner", "Party", "Just Because"]
        )
        
        guests = st.number_input("Number of guests", min_value=1, max_value=20, value=2)
    
    if st.button("Get Wine Recommendations", type="primary"):
        with st.spinner("Our AI sommelier is selecting the perfect wines..."):
            # Build prompt for Gemini
            prompt = f"""As an expert sommelier, recommend 3 wines for the following:

Meal Type: {meal_type}
Dish Description: {meal_description if meal_description else 'Not specified'}
Occasion: {occasion}
Number of Guests: {guests}
Preferred Wine Type: {wine_type}
Price Range: {price_range}
Taste Preferences: {', '.join(taste_profile) if taste_profile else 'No specific preferences'}

For each wine recommendation, provide:
1. Wine name and type
2. Why it pairs well with this meal
3. Tasting notes
4. Approximate price range
5. Serving suggestions

Format your response in a clear, conversational way."""

            try:
                # Call Gemini API
                response = model.generate_content(prompt)
                response_text = response.text
                
                st.markdown("### 🎯 Sommelier's Recommendations")
                st.markdown(response_text)
            except Exception as e:
                st.error(f"Error getting recommendations: {str(e)}")
                st.info("Please check your API key and try again.")

# Tab 2: Browse Wines
with tab2:
    st.header("Browse Our Wine Collection")
    
    @st.cache_data
    def fetch_wines():
        try:
            # Fetch from multiple endpoints
            reds = requests.get("https://api.sampleapis.com/wines/reds").json()
            whites = requests.get("https://api.sampleapis.com/wines/whites").json()
            sparkling = requests.get("https://api.sampleapis.com/wines/sparkling").json()
            return reds[:5] + whites[:5] + sparkling[:5]  # Limit results
        except:
            return []
    
    wines = fetch_wines()
    
    if wines:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Search wines", placeholder="Enter wine name...")
        
        # Display wines
        for idx, wine in enumerate(wines):
            if search_term.lower() in wine.get('wine', '').lower() or not search_term:
                with st.container():
                    st.markdown('<div class="wine-card">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([2, 3, 1])
                    
                    with col1:
                        if 'image' in wine:
                            st.image(wine['image'], width=100)
                    
                    with col2:
                        st.markdown(f"**{wine.get('wine', 'Unknown Wine')}**")
                        st.write(f"Winery: {wine.get('winery', 'N/A')}")
                        st.write(f"Location: {wine.get('location', 'N/A')}")
                        if 'rating' in wine:
                            st.write(f"⭐ Rating: {wine['rating'].get('average', 'N/A')}")
                    
                    with col3:
                        if st.button("Learn More", key=f"wine_btn_{idx}"):
                            st.session_state['selected_wine'] = wine
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Unable to load wines from the API. Please try again later.")

# Tab 3: Ask the Sommelier
with tab3:
    st.header("Ask Our AI Sommelier Anything")
    
    st.markdown("""
    Have a question about wine? Our AI sommelier is here to help!
    
    **Example questions:**
    - What's the difference between Cabernet Sauvignon and Merlot?
    - How do I store wine properly?
    - What temperature should I serve Chardonnay?
    - Can you explain wine tannins?
    """)
    
    user_question = st.text_area(
        "Your question:",
        placeholder="Ask anything about wine...",
        height=100
    )
    
    if st.button("Ask Sommelier", type="primary"):
        if user_question:
            with st.spinner("Thinking..."):
                try:
                    prompt = f"""You are an expert sommelier. Answer this question in a helpful, friendly, and knowledgeable way:

{user_question}

Provide practical advice and interesting facts where relevant."""
                    
                    response = model.generate_content(prompt)
                    response_text = response.text
                    
                    st.markdown("### 🍷 Sommelier's Answer")
                    st.markdown(response_text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Please check your API key and try again.")
        else:
            st.warning("Please enter a question first.")

# Shopping Cart (in sidebar)
st.sidebar.markdown("---")
st.sidebar.header("🛒 Your Cart")
if 'cart' not in st.session_state:
    st.session_state['cart'] = []

if st.session_state['cart']:
    for item in st.session_state['cart']:
        st.sidebar.write(f"- {item}")
    if st.sidebar.button("Clear Cart"):
        st.session_state['cart'] = []
        st.rerun()
else:
    st.sidebar.write("Your cart is empty")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>🍷 Powered by Google Gemini AI | "
    "Drink Responsibly | Must be 21+ to order</p>",
    unsafe_allow_html=True
)
