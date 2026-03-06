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
html, body, [class*="css"] {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
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
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
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
}
.bundle-type-badge {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #4f46e5);
    color: white;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 0.8rem;
}
.price-row {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}
.price-item { text-align: center; }
.price-label {
    font-size: 0.72rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.price-value {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
}
.price-bundle { color: #7c3aed; }
.price-retail { color: #6b7280; text-decoration: line-through; font-weight: 400; font-size: 1rem; }

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
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
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
.metric-chip {
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 0.88rem;
    display: inline-block;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.5rem !important;
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
            df = None
            for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    break
                except (UnicodeDecodeError, Exception):
                    df = None
            if df is None:
                raise ValueError("Could not decode file with any supported encoding.")

            df.columns = df.columns.str.strip()

            # Flexible column matching — tolerate "(MYR)" suffix in headers
            rename_map = {}
            for col in df.columns:
                for base in ["AirAsia Price", "Cost Price", "Retail Price"]:
                    if col.startswith(base) and col != base:
                        rename_map[col] = base
            df.rename(columns=rename_map, inplace=True)

            required_cols = {"Duty Free Code", "Domlux Code", "Item Name",
                             "AirAsia Price", "Cost Price", "Retail Price"}
            missing = required_cols - set(df.columns)
            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
                df = None
            else:
                for col in ["AirAsia Price", "Cost Price", "Retail Price"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                st.success(f"✅ {len(df)} products loaded")
                st.dataframe(
                    df[["Item Name", "Retail Price", "Cost Price"]],
                    use_container_width=True, height=300
                )
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
        <div style="font-size:1.3rem;font-weight:700;color:#4b5563;margin-top:0.5rem">No catalogue loaded</div>
        <div style="margin-top:0.5rem">Upload a CSV in the sidebar to begin building bundle deals.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # ── All config lives in the sidebar so the main area is full-width ────
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Bundle Configuration")

        bundle_type = st.radio(
            "Bundle Type",
            ["Buy 2 (Same Item × 2)", "Any 2 (Pick from Pool)",
             "Buy 3 (Same Item × 3)", "Any 3 (Pick from Pool)"],
            help=(
                "**Buy 2**: 2 of the same item.\n\n"
                "**Any 2**: Any 2 items from the pool.\n\n"
                "**Buy 3**: 3 of the same item.\n\n"
                "**Any 3**: Any 3 items from the pool."
            )
        )

        st.markdown("**Select Items**")
        item_names = df["Item Name"].tolist()

        pool_size = 3 if bundle_type in ["Any 3 (Pick from Pool)", "Buy 3 (Same Item × 3)"] else 2
        is_same   = bundle_type in ["Buy 2 (Same Item × 2)", "Buy 3 (Same Item × 3)"]
        n_items   = 3 if "3" in bundle_type else 2

        if is_same:
            selected_items = st.multiselect(
                f"Items for Buy {n_items} deal",
                options=item_names,
                placeholder="Select one or more items..."
            )
        else:
            selected_items = st.multiselect(
                f"Items for Any {n_items} pool",
                options=item_names,
                placeholder=f"Select {n_items} or more items...",
                help=f"Customers can pick any {n_items} items from this pool."
            )

        st.markdown("**Pricing Mode**")
        pricing_mode = st.radio(
            "Pricing Mode",
            ["Set Bundle Price", "Desired Savings (MYR)", "Desired Savings (%)", "Desired Margin (MYR)", "Desired Margin (%)"],
            label_visibility="collapsed",
            help=(
                "**Set Bundle Price** — enter a fixed price directly.\n\n"
                "**Desired Savings (MYR)** — bundle price = Retail Total − Savings.\n\n"
                "**Desired Savings (%)** — bundle price = Retail Total × (1 − %/100).\n\n"
                "**Desired Margin (MYR)** — bundle price = Cost Total + Margin.\n\n"
                "**Desired Margin (%)** — bundle price = Cost Total / (1 − %/100)."
            )
        )

        if pricing_mode == "Set Bundle Price":
            pricing_label, pricing_value, pricing_step, pricing_fmt, pricing_min = "Bundle Price (MYR)", 100.00, 0.50, "%.2f", 0.01
        elif pricing_mode == "Desired Savings (MYR)":
            pricing_label, pricing_value, pricing_step, pricing_fmt, pricing_min = "Customer Savings (MYR)", 20.00, 1.00, "%.2f", 0.01
        elif pricing_mode == "Desired Savings (%)":
            pricing_label, pricing_value, pricing_step, pricing_fmt, pricing_min = "Customer Savings (% of Retail)", 10.0, 0.5, "%.1f", 0.1
        elif pricing_mode == "Desired Margin (MYR)":
            pricing_label, pricing_value, pricing_step, pricing_fmt, pricing_min = "Desired Margin (MYR)", 20.00, 1.00, "%.2f", 0.01
        else:
            pricing_label, pricing_value, pricing_step, pricing_fmt, pricing_min = "Desired Margin (% of Bundle Price)", 20.0, 0.5, "%.1f", 0.1

        pricing_input = st.number_input(
            pricing_label,
            min_value=pricing_min, value=pricing_value, step=pricing_step, format=pricing_fmt,
        )

        st.markdown("---")
        generate = st.button("🎁 Generate Bundle Deals", use_container_width=True)

    # ── Full-width output area ─────────────────────────────────────────────
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
    elif bundle_type in ["Any 2 (Pick from Pool)", "Any 3 (Pick from Pool)"] and len(selected_items) < n_items:
        st.warning("⚠️ Select at least 2 items for an Any 2 pool.")
    else:
        selected_df = df[df["Item Name"].isin(selected_items)].reset_index(drop=True)
        bundles = []

        def calc_bundle_price(retail_total, cost_total):
            """Derive bundle price from the chosen pricing mode."""
            if pricing_mode == "Set Bundle Price":
                return pricing_input
            elif pricing_mode == "Desired Savings (MYR)":
                return max(retail_total - pricing_input, 0.01)
            elif pricing_mode == "Desired Savings (%)":
                return max(retail_total * (1 - pricing_input / 100), 0.01)
            elif pricing_mode == "Desired Margin (MYR)":
                return cost_total + pricing_input
            else:  # Desired Margin (%)
                if pricing_input >= 100:
                    return cost_total * 2  # guard against div/0
                return cost_total / (1 - pricing_input / 100)

        if is_same:
            # Buy N (same item repeated N times)
            for _, row in selected_df.iterrows():
                retail_total = row["Retail Price"] * n_items
                cost_total   = row["Cost Price"]   * n_items
                bundle_price = calc_bundle_price(retail_total, cost_total)
                savings      = retail_total - bundle_price
                margin_amt   = bundle_price - cost_total
                margin_pct   = (margin_amt / bundle_price * 100) if bundle_price > 0 else 0
                bundles.append({
                    "type":         f"Buy {n_items}",
                    "items":        [row["Item Name"]] * n_items,
                    "duty_codes":   [row["Duty Free Code"]],
                    "domlux_codes": [row["Domlux Code"]],
                    "retail_total": retail_total,
                    "cost_total":   cost_total,
                    "bundle_price": bundle_price,
                    "savings":      savings,
                    "margin_amt":   margin_amt,
                    "margin_pct":   margin_pct,
                })
        else:
            # Any N — all combinations of n_items from the pool
            records = [row for _, row in selected_df.iterrows()]
            combos  = list(itertools.combinations(records, n_items))
            for combo in combos:
                retail_total = sum(r["Retail Price"] for r in combo)
                cost_total   = sum(r["Cost Price"]   for r in combo)
                bundle_price = calc_bundle_price(retail_total, cost_total)
                savings      = retail_total - bundle_price
                margin_amt   = bundle_price - cost_total
                margin_pct   = (margin_amt / bundle_price * 100) if bundle_price > 0 else 0
                bundles.append({
                    "type":         f"Any {n_items}",
                    "items":        [r["Item Name"]     for r in combo],
                    "duty_codes":   [r["Duty Free Code"] for r in combo],
                    "domlux_codes": [r["Domlux Code"]    for r in combo],
                    "retail_total": retail_total,
                    "cost_total":   cost_total,
                    "bundle_price": bundle_price,
                    "savings":      savings,
                    "margin_amt":   margin_amt,
                    "margin_pct":   margin_pct,
                })

        if bundles:
            # ── Build display dataframe ───────────────────────────────
            show_item3 = n_items >= 3
            rows = []
            for b in bundles:
                row_data = {
                    "Item 1":       b["items"][0],
                    "Item 2":       b["items"][1] if len(b["items"]) > 1 else "",
                    "Bundle Price": round(b["bundle_price"], 2),
                    "Retail Total": round(b["retail_total"], 2),
                    "Cost Total":   round(b["cost_total"], 2),
                    "Savings":      round(b["savings"], 2),
                    "Margin (MYR)": round(b["margin_amt"], 2),
                    "Margin (%)":   round(b["margin_pct"], 1),
                }
                if show_item3:
                    row_data["Item 3"] = b["items"][2] if len(b["items"]) > 2 else ""
                rows.append(row_data)
            result_df = pd.DataFrame(rows)

            # Reorder columns so Item 3 appears after Item 2
            if show_item3:
                cols = ["Item 1", "Item 2", "Item 3", "Bundle Price", "Retail Total",
                        "Cost Total", "Savings", "Margin (MYR)", "Margin (%)"]
                result_df = result_df[cols]

            st.markdown(
                f"<div style='margin-bottom:0.5rem;font-family:Helvetica Neue,Helvetica,Arial,sans-serif'>"
                f"<b>{len(bundles)} bundle(s) generated</b> &nbsp;·&nbsp;"
                f"<span style='color:#6b7280;font-size:0.85rem'>Click table · Ctrl+A · Ctrl+C to copy</span>"
                f"</div>",
                unsafe_allow_html=True
            )

            col_cfg = {
                "Item 1":       st.column_config.TextColumn("Item 1",         width="large"),
                "Item 2":       st.column_config.TextColumn("Item 2",         width="large"),
                "Bundle Price": st.column_config.NumberColumn("Bundle (MYR)", format="%.2f", width="small"),
                "Retail Total": st.column_config.NumberColumn("Retail (MYR)", format="%.2f", width="small"),
                "Cost Total":   st.column_config.NumberColumn("Cost (MYR)",   format="%.2f", width="small"),
                "Savings":      st.column_config.NumberColumn("Savings",      format="%.2f", width="small"),
                "Margin (MYR)": st.column_config.NumberColumn("Margin (MYR)", format="%.2f", width="small"),
                "Margin (%)":   st.column_config.NumberColumn("Margin (%)",   format="%.1f%%", width="small"),
            }
            if show_item3:
                col_cfg["Item 3"] = st.column_config.TextColumn("Item 3", width="large")

            st.dataframe(
                result_df,
                use_container_width=True,
                height=min(38 * len(bundles) + 46, 520),
                hide_index=True,
                column_config=col_cfg,
            )

            # ── Summary metrics ───────────────────────────────────────
            st.markdown("")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Bundles",        len(bundles))
            m2.metric("Avg Savings / Bundle", f"MYR {result_df['Savings'].mean():,.2f}")
            m3.metric("Total Savings",        f"MYR {result_df['Savings'].sum():,.2f}")
            m4.metric("Avg Margin",           f"{result_df['Margin (%)'].mean():.1f}%")

            # ── CSV download as secondary option ──────────────────────
            st.markdown("---")
            csv_out = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download as CSV",
                data=csv_out,
                file_name="bundle_deals.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No bundles could be generated. Check your selection.")
