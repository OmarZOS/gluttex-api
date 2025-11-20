

# Base cost calculation
def calculate_base_cost(purchase_price, logistics_costs):
    return purchase_price + logistics_costs

# Broker’s margin or markup calculation
def apply_margin_or_markup(subtotal, margin_rate=None, markup_amount=None):
    if margin_rate:
        return subtotal * (1 + margin_rate)
    elif markup_amount:
        return subtotal + markup_amount
    return subtotal

# VAT calculation
def apply_vat(subtotal, vat_rate):
    return subtotal * (1 + vat_rate)

# Additional taxes and fees calculation
def add_additional_fees(subtotal, customs_duties=0, brokerage_fees=0):
    return subtotal + customs_duties + brokerage_fees

# Overhead costs calculation
def add_overheads(subtotal, operational_costs=0, finance_costs=0):
    return subtotal + operational_costs + finance_costs

# Apply discounts
def apply_discount(subtotal, discount=0):
    return subtotal - discount

# Currency fluctuation buffer (optional, for international products)
def add_currency_fluctuation(subtotal, buffer_percentage):
    return subtotal * (1 + buffer_percentage)

# Final price calculation using hierarchy
def calculate_final_price(purchase_price, logistics_costs, margin_rate=None, markup_amount=None,
                          vat_rate=0, customs_duties=0, brokerage_fees=0, operational_costs=0,
                          finance_costs=0, discount=0, currency_buffer=0):
    # Step 1: Calculate base cost
    subtotal_1 = calculate_base_cost(purchase_price, logistics_costs)
    
    # Step 2: Apply broker's margin or markup
    subtotal_2 = apply_margin_or_markup(0, margin_rate, markup_amount)
    
    # Step 3: Apply VAT
    subtotal_3 = apply_vat(subtotal_2, vat_rate)
    
    # Step 4: Add additional fees
    subtotal_4 = subtotal_1 + add_additional_fees(subtotal_3, customs_duties, brokerage_fees)
    
    # Step 5: Add overhead costs
    subtotal_5 = add_overheads(subtotal_4, operational_costs, finance_costs)
    
    # Step 6: Apply discounts
    subtotal_6 = apply_discount(subtotal_5, discount)
    
    # Step 7: Add currency fluctuation buffer
    final_price = add_currency_fluctuation(subtotal_6, currency_buffer)
    
    return final_price

# Example usage
# final_cost = calculate_final_price(
#     purchase_price=100,
#     logistics_costs=15,
#     margin_rate=0.2,
#     markup_amount = 20,
#     vat_rate=0.19,
#     customs_duties=10,
#     brokerage_fees=5,
#     operational_costs=20,
#     finance_costs=3,
#     discount=5,
#     currency_buffer=0.02
# )

# print(f"Final Price: {final_cost:.2f}")
