
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Data Classes & Business Logic ---
class Ingredient:
    def __init__(self, name, quantity_g, cost, supplier="", supplier_link=""):
        self.name = name
        self.quantity_g = quantity_g
        self.cost = cost
        self.supplier = supplier
        self.supplier_link = supplier_link

    @property
    def cost_per_g(self):
        return self.cost / self.quantity_g if self.quantity_g else 0

class BusinessManager:
    def __init__(self):
        self.ingredients = {}
        self.formulations = {}
        self.sales = []
        self.expenses = []

    def add_ingredient(self, name, qty, cost, supplier="", link=""):
        self.ingredients[name] = Ingredient(name, qty, cost, supplier, link)

    def add_formulation(self, name, formula_dict):
        self.formulations[name] = formula_dict

    def calc_units_possible(self, formulation_name, unit_weight=100):
        if formulation_name not in self.formulations:
            return 0
        formula = self.formulations[formulation_name]
        possible_units = float('inf')
        for ing, percent in formula.items():
            if ing not in self.ingredients:
                return 0
            req_per_unit = (percent / 100) * unit_weight
            available = self.ingredients[ing].quantity_g
            units = available // req_per_unit
            possible_units = min(possible_units, units)
        return int(possible_units)

    def calc_cost_per_unit(self, formulation_name, unit_weight=100):
        if formulation_name not in self.formulations:
            return 0
        formula = self.formulations[formulation_name]
        cost = 0
        for ing, percent in formula.items():
            if ing in self.ingredients:
                grams = (percent / 100) * unit_weight
                cost += grams * self.ingredients[ing].cost_per_g
        return round(cost, 2)

bm = BusinessManager()

# --- Preload Default Formulations ---
bm.add_formulation("Sensitive Balm", {
    "Coconut Oil": 25,
    "Shea Butter": 25,
    "Jojoba Oil": 14,
    "Mango Butter": 10,
    "Castor Oil": 13,
    "Beeswax": 10,
    "Calendula Extract": 2,
    "Vitamin E Oil": 1
})
bm.add_formulation("Regular Balm", {
    "Shea Butter": 30,
    "Coconut Oil": 14,
    "Mango Butter": 14,
    "Beeswax": 10,
    "Jojoba Oil": 8,
    "Castor Oil": 6,
    "Argan OIl": 5,
    "Sweet Almond Oil": 6,
    "Black Seed Oil": 3.5,
    "Neem Oil": 2,
    "Vitamin E Oil": 1,
    "Rosemary Oil": 0.25,
    "Tea Tree Oil": 0.25
})
bm.add_formulation("Hair Oil", {
    "Castor Oil": 25,
    "Amla Oil": 20,
    "Jojoba Oil": 20,
    "Almond Oil": 15,
    "Black Seed Oil": 14,
    "Neem Oil": 3,
    "Rosemary Oil": 1,
    "Tea Tree Oil": 1,
    "Vitamin E Oil": 1
})
bm.add_formulation("Bath Soak", {
    "Colloidal Oatmeal": 35,
    "Goat’s Milk Powder": 5,
    "Baking Soda": 10,
    "Epsom Salt": 35,
    "Honey Powder": 5,
    "Oat Exfoliator": 5,
    "Jojoba Oil": 5
})

# ---------- Streamlit App ----------
st.set_page_config(page_title="Skincare Business Dashboard", layout="wide")
st.title("🧴 Skincare & Superfood Business Manager")

# ---------- Ingredient Manager ----------
st.header("📦 Editable Ingredient Manager")
if "editable_ingredients" not in st.session_state:
    st.session_state.editable_ingredients = []

edited_df = st.data_editor(
    pd.DataFrame(st.session_state.editable_ingredients),
    num_rows="dynamic",
    use_container_width=True,
    column_config={"Cost per g (£)": st.column_config.NumberColumn(disabled=True)},
    key="ingredients_editor"
)

edited_df["Cost per g (£)"] = edited_df.apply(
    lambda row: round(row["Cost (£)"] / row["Quantity (g)"], 4) if row["Quantity (g)"] > 0 else 0,
    axis=1
)

if st.button("🔄 Update Ingredients"):
    st.session_state.editable_ingredients = edited_df.to_dict(orient="records")
    bm.ingredients.clear()
    for row in st.session_state.editable_ingredients:
        try:
            name = row["Name"]
            qty = float(row["Quantity (g)"])
            cost = float(row["Cost (£)"])
            supplier = row.get("Supplier", "")
            link = row.get("Link", "")
            bm.add_ingredient(name, qty, cost, supplier, link)
        except Exception as e:
            st.error(f"Error updating ingredient '{row}': {e}")
    st.success("Ingredients updated successfully.")

# ---------- Formulation Calculator ----------
st.header("🧪 Formulation & Cost Calculator")
for name in bm.formulations:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**{name}**")
    with col2:
        st.markdown(f"Can make: `{bm.calc_units_possible(name)} units`")
    with col3:
        st.markdown(f"Cost per unit: `£{bm.calc_cost_per_unit(name)}`")

# ---------- Low Stock Alerts ----------
st.header("⚠️ Low Stock Alerts")
low_stock_items = []
for ing in bm.ingredients.values():
    if ing.quantity_g < 100:
        low_stock_items.append({
            "Ingredient": ing.name,
            "Qty (g)": ing.quantity_g,
            "Supplier": ing.supplier,
            "Restock Needed": "Yes"
        })
if low_stock_items:
    st.error("The following ingredients are low:")
    st.dataframe(pd.DataFrame(low_stock_items))
else:
    st.success("All ingredients are sufficiently stocked.")

# ---------- Wholesale Inventory ----------
st.header("🧺 Wholesale Product Inventory")
if "wholesale_inventory" not in st.session_state:
    st.session_state.wholesale_inventory = [
        {"Product": "Honey", "Quantity (g)": 0, "Cost (£)": 0},
        {"Product": "Dates", "Quantity (g)": 0, "Cost (£)": 0},
        {"Product": "Saffron", "Quantity (g)": 0, "Cost (£)": 0},
        {"Product": "Black Seed Oil", "Quantity (g)": 0, "Cost (£)": 0}
    ]
wholesale_df = st.data_editor(
    pd.DataFrame(st.session_state.wholesale_inventory),
    num_rows="dynamic",
    use_container_width=True,
    key="wholesale_editor"
)
if st.button("💾 Save Wholesale Inventory"):
    st.session_state.wholesale_inventory = wholesale_df.to_dict(orient="records")
    st.success("Wholesale product inventory saved!")

# ---------- Product Development Tracker ----------
st.header("🧪 Product Development Notes")
if "product_dev" not in st.session_state:
    st.session_state.product_dev = []

dev_df = st.data_editor(
    pd.DataFrame(st.session_state.product_dev),
    num_rows="dynamic",
    use_container_width=True,
    key="dev_notes"
)

if st.button("💾 Save Dev Notes"):
    st.session_state.product_dev = dev_df.to_dict(orient="records")
    st.success("Product development notes saved!")
