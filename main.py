import streamlit as st
import pandas as pd
import itertools

st.set_page_config(
    page_title="Bundle Deal Generator",
    page_icon="🛍️",
    layout="wide"
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
    font-family: 'Syne', sans-serif !important;
}

.main-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
}
.main-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin: 0;
}
.main-header p {
    color: #a78bfa;
    margin-top: 0.5rem;
    font-size: 1rem;
    font-weight: 300;
}

.bundle-card {
    background: white;
    border: 1.5px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.bundle-card:hover {
    box-shadow: 0 6px 20px rgba(48,43,99,0.12);
}
.bundle-type-badge {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #4f46e5);
    color: white;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 0.8rem;
}
.savings-badge {
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 0.9rem;
    display: inline-block;
    margin-top: 0.5rem;
}
.price-row {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}
.price-item {
    text-align: center;
}
.price-label {
    font-size: 0.72rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.price-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
}
.price-bundle { color: #7c3aed; }
.price-retail { color: #6b7280; text-decoration: line-through; font-weight: 400; font-size: 1rem; }
.price-savings { color: #15803d; }
.item-pill {
    background: #f5f3ff;
    color: #4338ca;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.82rem;
    font-weight: 500;
    display: inline-block;
    margin: 3px 4px 3px 0;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.2rem;
    color: #1e1b4b;
    margin-bottom: 0.4rem;
}
.empty-state {
    text-align: center;
    color: #9ca3af;
    padding: 3rem 1rem;
    font-size: 1rem;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛍️ Bundle Deal Generator</h1>
    <p>Upload your product catalogue · Select items · Set price · Generate bundles</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: Upload ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Upload Catalogue")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()

            required_cols = {
                "Duty Free Code", "Domlux Code", "Item Name",
                "AirAsia Price", "Cost Price", "Retail Price"
            }
            missing = required_cols - set(df.columns)
            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
                df = None
            else:
                # Clean numeric columns
                for col in ["AirAsia Price (MYR)", "Cost Price (MYR)", "Retail Price (MYR)"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                st.success(f"✅ {len(df)} products loaded")
                st.dataframe(df[["Item Name", "Retail Price (MYR)"]].rename(
                    columns={"Retail Price (MYR)": "Retail (MYR)"}
                ), use_container_width=True, height=300)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df = None
    else:
        df = None
        st.info("Upload a CSV to get started.")

# ── Main Area ─────────────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:3rem">📋</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700;color:#4b5563;margin-top:0.5rem">
            No catalogue loaded
        </div>
        <div style="margin-top:0.5rem">Upload a CSV in the sidebar to begin building bundle deals.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    col_left, col_right = st.columns([1.1, 1.9], gap="large")

    with col_left:
        st.markdown('<div class="section-title">⚙️ Bundle Configuration</div>', unsafe_allow_html=True)

        # Bundle type
        bundle_type = st.radio(
            "Bundle Type",
            ["Buy 2 (Same Item × 2)", "Any 2 (Pick from Pool)"],
            help="**Buy 2**: Customer buys 2 of the SAME item at the bundle price.\n\n**Any 2**: Customer picks any 2 items from the selected pool."
        )

        st.markdown("---")

        # Item selection
        st.markdown("**Select Items for Bundle Pool**")
        item_names = df["Item Name"].tolist()

        if bundle_type == "Buy 2 (Same Item × 2)":
            selected_items = st.multiselect(
                "Choose item(s) to offer as Buy 2 deal",
                options=item_names,
                placeholder="Select one or more items..."
            )
        else:
            selected_items = st.multiselect(
                "Choose items for the Any 2 pool",
                options=item_names,
                placeholder="Select 2 or more items...",
                help="Customers can pick any 2 items from this pool."
            )

        st.markdown("---")

        # Bundle price
        st.markdown("**Bundle Price (MYR)**")
        bundle_price = st.number_input(
            "Set the bundle deal price",
            min_value=0.01,
            value=100.00,
            step=0.50,
            format="%.2f",
            label_visibility="collapsed"
        )

        st.markdown("---")
        generate = st.button("🎁 Generate Bundle Deals", use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">🎁 Generated Bundle Deals</div>', unsafe_allow_html=True)

        if not generate:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size:2.5rem">✨</div>
                <div style="margin-top:0.5rem">Configure your bundle and click <b>Generate</b>.</div>
            </div>
            """, unsafe_allow_html=True)
        elif not selected_items:
            st.warning("⚠️ Please select at least one item.")
        elif bundle_type == "Any 2 (Pick from Pool)" and len(selected_items) < 2:
            st.warning("⚠️ Select at least 2 items for an Any 2 pool.")
        else:
            selected_df = df[df["Item Name"].isin(selected_items)].reset_index(drop=True)

            bundles = []

            if bundle_type == "Buy 2 (Same Item × 2)":
                for _, row in selected_df.iterrows():
                    retail_total = row["Retail Price (MYR)"] * 2
                    savings = retail_total - bundle_price
                    bundles.append({
                        "type": "Buy 2",
                        "items": [row["Item Name"], row["Item Name"]],
                        "duty_codes": [row["Duty Free Code"]],
                        "domlux_codes": [row["Domlux Code"]],
                        "retail_total": retail_total,
                        "bundle_price": bundle_price,
                        "savings": savings,
                    })
            else:
                # All combinations of any 2 from pool
                pairs = list(itertools.combinations(selected_df.itertuples(index=False), 2))
                for a, b in pairs:
                    retail_total = getattr(a, "Retail_Price_MYR_".replace(" ", "_"), 0)
                    # Access by column name safely
                    a_retail = a._asdict().get("Retail Price (MYR)", 0)
                    b_retail = b._asdict().get("Retail Price (MYR)", 0)
                    retail_total = a_retail + b_retail
                    savings = retail_total - bundle_price
                    bundles.append({
                        "type": "Any 2",
                        "items": [a._asdict()["Item Name"], b._asdict()["Item Name"]],
                        "duty_codes": [a._asdict()["Duty Free Code"], b._asdict()["Duty Free Code"]],
                        "domlux_codes": [a._asdict()["Domlux Code"], b._asdict()["Domlux Code"]],
                        "retail_total": retail_total,
                        "bundle_price": bundle_price,
                        "savings": savings,
                    })

            if bundles:
                st.markdown(f"**{len(bundles)} bundle(s) generated** at **MYR {bundle_price:,.2f}** each")
                st.markdown("")

                for i, b in enumerate(bundles, 1):
                    savings_color = "#15803d" if b["savings"] >= 0 else "#dc2626"
                    savings_label = f"Save MYR {b['savings']:,.2f}" if b["savings"] >= 0 else f"Over retail by MYR {abs(b['savings']):,.2f}"
                    savings_bg = "#f0fdf4" if b["savings"] >= 0 else "#fef2f2"
                    savings_border = "#bbf7d0" if b["savings"] >= 0 else "#fecaca"

                    items_html = "".join(f'<span class="item-pill">{item}</span>' for item in b["items"])
                    codes_html = ""
                    for dc, dlc in zip(b["duty_codes"], b["domlux_codes"]):
                        codes_html += f'<span style="font-size:0.75rem;color:#9ca3af;margin-right:12px">📦 DF: <b>{dc}</b> · DL: <b>{dlc}</b></span>'

                    st.markdown(f"""
                    <div class="bundle-card">
                        <span class="bundle-type-badge">{b["type"]}</span>
                        <div style="margin-bottom:6px">{items_html}</div>
                        <div>{codes_html}</div>
                        <div class="price-row">
                            <div class="price-item">
                                <div class="price-label">Bundle Price</div>
                                <div class="price-value price-bundle">MYR {b["bundle_price"]:,.2f}</div>
                            </div>
                            <div style="color:#d1d5db;font-size:1.2rem">vs</div>
                            <div class="price-item">
                                <div class="price-label">Retail Total</div>
                                <div class="price-value price-retail">MYR {b["retail_total"]:,.2f}</div>
                            </div>
                            <div>
                                <div style="background:{savings_bg};color:{savings_color};border:1px solid {savings_border};
                                    border-radius:8px;padding:6px 14px;font-weight:600;font-size:0.88rem;display:inline-block">
                                    {'💚' if b['savings'] >= 0 else '⚠️'} {savings_label}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Export ────────────────────────────────────────────────────
                st.markdown("---")
                export_rows = []
                for b in bundles:
                    export_rows.append({
                        "Bundle Type": b["type"],
                        "Item 1": b["items"][0],
                        "Item 2": b["items"][1] if len(b["items"]) > 1 else b["items"][0],
                        "Duty Free Code(s)": " / ".join(str(c) for c in b["duty_codes"]),
                        "Domlux Code(s)": " / ".join(str(c) for c in b["domlux_codes"]),
                        "Bundle Price (MYR)": round(b["bundle_price"], 2),
                        "Retail Total (MYR)": round(b["retail_total"], 2),
                        "Savings (MYR)": round(b["savings"], 2),
                    })
                export_df = pd.DataFrame(export_rows)
                csv_out = export_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Export Bundles as CSV",
                    data=csv_out,
                    file_name="bundle_deals.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No bundles could be generated. Check your selection.")
