def analyze_price_trends(price_data):
    """
    Calculates simple trends from the price data.
    """
    if not price_data or len(price_data) < 2:
        return {"trend": "Insufficient Data", "change": 0}
        
    current_price = price_data[-1]["price"]
    start_price = price_data[0]["price"]
    
    # Calculate simple percentage change over the period
    change_pct = ((current_price - start_price) / start_price) * 100
    
    # Determine trend direction
    if change_pct > 5:
        trend = "Upward 📈"
    elif change_pct < -5:
        trend = "Downward 📉"
    else:
        trend = "Stable ➡️"
        
    # Calculate volatility (standard deviation roughly)
    prices = [p["price"] for p in price_data]
    avg_price = sum(prices) / len(prices)
    
    # --- Seasonality Analysis ---
    # Group by month to find the "Best Month to Sell"
    monthly_prices = {} # {1: [p1, p2], 2: [...]}
    for p in price_data:
        # date format "YYYY-MM-DD"
        month = int(p["date"].split("-")[1])
        if month not in monthly_prices:
            monthly_prices[month] = []
        monthly_prices[month].append(p["price"])
        
    # Calculate average for each month
    month_avgs = {}
    for m, p_list in monthly_prices.items():
        month_avgs[m] = sum(p_list) / len(p_list)
        
    # Find Best and Worst months
    if month_avgs:
        best_month_num = max(month_avgs, key=month_avgs.get)
        worst_month_num = min(month_avgs, key=month_avgs.get)
        
        import calendar
        best_month = calendar.month_name[best_month_num]
        worst_month = calendar.month_name[worst_month_num]
        
        seasonality_note = f"Historically, prices peak in {best_month} and bottom out in {worst_month}."
    else:
        seasonality_note = "Insufficient data for seasonality."

    return {
        "current_price": current_price,
        "average_price": round(avg_price, 2),
        "trend": trend,
        "change_percent": round(change_pct, 1),
        "history_summary": f"Started at ${start_price}, ended at ${current_price}",
        "seasonality": seasonality_note
    }
