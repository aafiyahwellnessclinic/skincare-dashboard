import streamlit as st
import pandas as pd
from datetime import datetime

# ---------- Business Manager Classes ----------
class Ingredient:
    def __init__(self, name, quantity_g, cost, supplier, supplier_link):
        self.name = name
        self.quantity_g = quantity_g
        self.cost = cost
        self.supplier = supplier
        self.supplier_link = supplier_link
        self.usage_notes = ""

class Product:
    def __init__(self, name, formulation):
        self.name = name
        self.formulation = formulation  # {ingredient_name: grams_used_per_unit}
        self.revenue = 0.0

class BusinessManager:
    def __init__(self):
        self.ingredients = {}
        self.products = {}
        self.notes = []
        self.low_stock_threshold = 100
        self.default_batch_sizes = {
            "Dry Skin Balm - Regular": 60,
            "Dry Skin Balm - Sensitive": 40,
            "Hair Oil": 20,
            "Bath Soak": 100
        }

    def add_ingredient(self, name, quantity_g, cost, supplier, supplier_link):
        self.ingredients[name] = Ingredient(name, quantity_g, cost, supplier, supplier_link)

    def add_product(self, name, formulation):
        self.products[name] = Product(name, formulation)

    def check_low_stock(self):
        low_stock = {}
        for name, ing in self.ingredients.items():
            if ing.quantity_g < self.low_stock_threshold:
                recommended_restock = {}
                for product_name, product in self.products.items():
                    if name in product.formulation:
                        batch_size = self.default_batch_sizes.get(product_name, 0)
                        recommended_restock[product_name] = batch_size * product.formulation[name]
                low_stock[name] = {
                    "Quantity": ing.quantity_g,
                    "Supplier": ing.supplier,
                    "Link": ing.supplier_link,
                    "Recommended Restock Amounts (g)": recommended_restock
                }
        return low_stock

    def show_ingredient_table(self):
        data = []
        for ing in self.ingredients.values():
            data.append([
                ing.name, ing.quantity_g, ing.cost, ing.cost / ing.quantity_g if ing.quantity_g else 0,
                ing.supplier, ing.supplier_link
            ])
        return pd.DataFrame(data, columns=["Name", "Quantity (g)", "Total Cost", "Cost/g", "Supplier", "Link"])

# ---------- Cost & Profit Functions ----------
def calculate_cost_per_unit(bm, product_name):
    if product_name not in bm.products:
        return 0.0
    product = bm.products[product_name]
    total_cost = 0.0
    for ingredient, amount in product.formulation.items():
        if ingredient in bm.ingredients:
            ing = bm.ingredients[ingredient]
            cost_per_g = ing.cost / ing.quantity_g if ing.quantity_g > 0 else 0
            total_cost += cost_per_g * amount
    return round(total_cost, 2)

def calculate_profit(product_sales, bm, other_expenses, start_date=None, end_date=None):
    total_revenue = 0.0
    total_cost = 0.0
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    for product, quantity, sale_date in product_sales:
        sale_date = datetime.strptime(sale_date, "%Y-%m-%d")
        if (not start_date or sale_date >= start_date) and (not end_date or sale_date <= end_date):
            unit_cost = calculate_cost_per_unit(bm, product)
            revenue_per_product = bm.products[product].revenue if hasattr(bm.products[product], 'revenue') else 0
            total_revenue += revenue_per_product * quantity
            total_cost += unit_cost * quantity
    total_other_expenses = sum(other_expenses.values())
    net_profit = total_revenue - total_cost - total_other_expenses
    return {
        'Total Revenue': round(total_revenue, 2),
        'Total Product Costs': round(total_cost, 2),
        'Other Expenses': round(total_other_expenses, 2),
        'Net Profit': round(net_profit, 2)
    }

# ---------- Setup Business Manager ----------
bm = BusinessManager()
# Add ingredients (Add actual quantities and costs for real tracking)
bm.add_ingredient("Shea Butter", 1000, 20, "Supplier A", "http://example.com")
bm.add_ingredient("Coconut Oil", 2000, 15, "Supplier B", "http://example.com")
bm.add_ingredient("Castor Oil", 500, 10, "Supplier C", "http://example.com")
bm.add_ingredient("Jojoba Oil", 300, 12, "Supplier D", "http://example.com")
bm.add_ingredient("Mango Butter", 200, 8, "Supplier E", "http://example.com")
bm.add_ingredient("Beeswax", 400, 5, "Supplier F", "http://example.com")
bm.add_ingredient("Calendula Extract", 100, 6, "Supplier G", "http://example.com")
bm.add_ingredient("Vitamin E Oil", 50, 4, "Supplier H", "http://example.com")
bm.add_ingredient("Argan OIl", 100, 10, "Supplier I", "http://example.com")
bm.add_ingredient("Sweet Almond Oil", 200, 9, "Supplier J", "http://example.com")
bm.add_ingredient("Black Seed Oil", 100, 7, "Supplier K", "http://example.com")
bm.add_ingredient("Neem Oil", 100, 5, "Supplier L", "http://example.com")
bm.add_ingredient("Rosemary Oil", 50, 3, "Supplier M", "http://example.com")
bm.add_ingredient("Tea Tree Oil", 50, 3, "Supplier N", "http://example.com")
bm.add_ingredient("Amla Oil", 100, 6, "Supplier O", "http://example.com")
bm.add_ingredient("Colloidal Oatmeal", 500, 10, "Supplier P", "http://example.com")
bm.add_ingredient("Goat’s Milk Powder", 100, 5, "Supplier Q", "http://example.com")
bm.add_ingredient("Baking Soda", 100, 2, "Supplier R", "http://example.com")
bm.add_ingredient("Epsom Salt", 500, 5, "Supplier S", "http://example.com")
bm.add_ingredient("Honey Powder", 100, 4, "Supplier T", "http://example.com")
bm.add_ingredient("Oat Exfoliator", 100, 3, "Supplier U", "http://example.com")

# Add products and formulations
bm.add_product("Dry Skin Balm - Sensitive", {
    "Coconut Oil": 25, "Shea Butter": 25, "Jojoba Oil": 14, "Mango Butter": 10,
    "Castor Oil": 13, "Beeswax": 10, "Calendula Extract": 2, "Vitamin E Oil": 1
})
bm.add_product("Dry Skin Balm - Regular", {
    "Shea Butter": 30, "Coconut Oil": 14, "Mango Butter": 14, "Beeswax": 10,
    "Jojoba Oil": 8, "Castor Oil": 6, "Argan OIl": 5, "Sweet Almond Oil": 6,
    "Black Seed Oil": 3.5, "Neem Oil": 2, "Vitamin E Oil": 1,
    "Rosemary Oil": 0.25, "Tea Tree Oil": 0.25
})
bm.add_product("Hair Oil", {
    "Castor Oil": 25, "Amla Oil": 20, "Jojoba Oil": 20, "Sweet Almond Oil": 15,
    "Black Seed Oil": 14, "Neem Oil": 3, "Rosemary Oil": 1, "Tea Tree Oil": 1, "Vitamin E Oil": 1
})
bm.add_product("Bath Soak", {
    "Colloidal Oatmeal": 35, "Goat’s Milk Powder": 5, "Baking Soda": 10,
    "Epsom Salt": 35, "Honey Powder": 5, "Oat Exfoliator": 5, "Jojoba Oil": 5
})

# ---------- Streamlit App ----------
st.title("Natural Health Business Dashboard")
st.header("Ingredient Inventory")
st.dataframe(bm.show_ingredient_table())

st.subheader("Low Stock Alerts")
low_stock = bm.check_low_stock()
if low_stock:
    for item, info in low_stock.items():
        st.warning(f"{item} is low ({info['Quantity']}g). Supplier: [{info['Supplier']}]({info['Link']}). Recommended restock: {info['Recommended Restock Amounts (g)']}")
else:
    st.success("All ingredients are sufficiently stocked.")

st.header("Cost Per Unit")
costs = {product: calculate_cost_per_unit(bm, product) for product in bm.products}
st.dataframe(pd.DataFrame(costs.items(), columns=["Product", "Cost per Unit (£)"]))

st.subheader("Set Revenue Per Product")
for product in bm.products:
    bm.products[product].revenue = st.number_input(f"{product} Revenue (£)", min_value=0.0, value=bm.products[product].revenue, key=product)

st.header("Sales Data")
sales_input = st.text_area("Enter sales as: Product,Quantity,YYYY-MM-DD\nOne per line")
sales = []
if sales_input:
    for line in sales_input.strip().split("\n"):
        try:
            product, qty, date_str = [x.strip() for x in line.split(",")]
            sales.append((product, int(qty), date_str))
        except:
            st.error(f"Invalid format: {line}")

st.header("Other Expenses")
expenses = {
    'shipping': st.number_input("Shipping (£)", min_value=0.0, value=60.0),
    'packaging': st.number_input("Packaging (£)", min_value=0.0, value=40.0),
    'labels': st.number_input("Labels (£)", min_value=0.0, value=20.0),
    'website hosting': st.number_input("Website Hosting (£)", min_value=0.0, value=15.0)
}

st.header("Profit Calculator")
start_date = st.date_input("Start Date", value=datetime(2025, 6, 1))
end_date = st.date_input("End Date", value=datetime(2025, 6, 30))
if st.button("Calculate Profit"):
    summary = calculate_profit(sales, bm, expenses, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    st.subheader("Profit Summary")
    for key, value in summary.items():
        st.write(f"**{key}**: £{value}")
