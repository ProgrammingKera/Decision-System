from flask import Blueprint, jsonify
from flask_mysqldb import MySQL
from collections import defaultdict
import calendar
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
from pyDecision.algorithm import saw

# Create Blueprint for DSS routes
dss_bp = Blueprint('dss', __name__)

def init_dss_routes(mysql_instance):
    """Initialize DSS routes with MySQL instance"""
    global mysql
    mysql = mysql_instance

    @dss_bp.route('/dss', methods=['GET'])
    def decision_support_system():
        try:
            # MySQL connection establish
            conn = mysql.connection
            cursor = conn.cursor()

            # Data Extraction Query: Orders + Products + Order Items
            query = """
            SELECT oi.*, p.product_name, p.price, o.order_date
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            order_items = [dict(zip(column_names, row)) for row in rows]

            # Dictionaries for KPIs initialization
            product_sales = {}
            product_profit = {}
            product_sales_by_month = {}

            # Loop: KPI Calculation - Sales, Profit, and Monthly Trends
            for item in order_items:
                product_name = item['product_name']
                total_sales = float(item['total_price'])
                price = float(item['price'])
                quantity = item['quantity']

                # KPI: Total Profit calculation
                profit = total_sales - (quantity * price)

                # Initialize if not exists
                if product_name not in product_sales:
                    product_sales[product_name] = 0
                    product_profit[product_name] = 0
                    product_sales_by_month[product_name] = {}

                # Add to KPIs
                product_sales[product_name] += total_sales
                product_profit[product_name] += profit

                # Sales trend tracking by month
                month = item['order_date'].strftime('%Y-%m')
                if month not in product_sales_by_month[product_name]:
                    product_sales_by_month[product_name][month] = 0
                product_sales_by_month[product_name][month] += total_sales

            # KPI: Sales Trend Evaluation (Updated)
            product_trends = {}
            for product_name, monthly_sales in product_sales_by_month.items():
                months = sorted(monthly_sales.keys())
                if len(months) > 1:
                    last_month = months[-1]
                    second_last_month = months[-2]
                    last_month_sales = monthly_sales[second_last_month]
                    current_month_sales = monthly_sales[last_month]
                    sales_growth = current_month_sales - last_month_sales

                    product_trends[product_name] = {
                        'status': 'Growth' if sales_growth > 0 else 'Decline',
                        'last_month': second_last_month,
                        'last_month_sales': round(last_month_sales, 2),
                        'current_month': last_month,
                        'current_month_sales': round(current_month_sales, 2),
                        'growth_amount': round(sales_growth, 2)
                    }
                else:
                    month = months[-1]
                    current_month_sales = monthly_sales[month]
                    product_trends[product_name] = {
                        'status': 'Decline',
                        'last_month': None,
                        'last_month_sales': 0.0,
                        'current_month': month,
                        'current_month_sales': round(current_month_sales, 2),
                        'growth_amount': round(current_month_sales, 2)
                    }

            # FAHP-based weight assignment for each KPI (manually given here)
            weight_sales = 0.5
            weight_profit = 0.3
            weight_trend = 0.2

            # Normalization for SPA (Simple Additive Weighting)
            max_sales = max(product_sales.values()) if product_sales else 1
            max_profit = max(product_profit.values()) if product_profit else 1

            # Apply SPA: Normalize KPIs & Calculate Weighted Scores
            decision_scores = {}
            for product_name in product_sales:
                sales_norm = float(product_sales[product_name]) / max_sales
                profit_norm = float(product_profit[product_name]) / max_profit
                trend_score = 1 if product_trends[product_name]['status'] == 'Growth' else 0

                # SPA (Simple Additive Weighting) formula:
                score = (sales_norm * weight_sales) + (profit_norm * weight_profit) + (trend_score * weight_trend)
                decision_scores[product_name] = round(score, 4)

            top_selling_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

            # ✅ Prepare final list of product recommendation results
            results = []
            for product_name in product_sales:
                trend_info = product_trends.get(product_name, {})
                results.append({
                    'product_name': product_name,
                    'total_sales (Rs)': round(product_sales[product_name], 2),     # KPI 1
                    'total_profit (Rs)': round(product_profit[product_name], 2),   # KPI 2
                    'trend': trend_info,
                    'decision_score': decision_scores[product_name]                # Final Score from SPA
                })

            # ✅ Final JSON Response including KPIs and SPA Result
            cursor.close()
            return jsonify({
                "message": "Decision support system analysis completed successfully.",
                "criteria_used": ["Total Sales", "Total Profit", "Sales Trend"],
                "fahp_weights": {
                    "Total Sales": weight_sales,
                    "Total Profit": weight_profit,
                    "Sales Trend": weight_trend
                },
                "decision_method": "SPA ",
                "top_selling_products": [{"product_name": p[0], "total_sales": round(p[1], 2)} for p in top_selling_products],
                "total_records_analyzed": len(order_items),
                "unique_products_count": len(product_sales),
                "product_recommendation_scores": results
            })

        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    @dss_bp.route('/api/predict_restocks', methods=['GET'])
    def predict_restocks():
        try:
            conn = mysql.connection
            cursor = conn.cursor()

            query = """
            SELECT oi.product_id, p.product_name, oi.quantity, o.order_date, p.stock_quantity
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            order_items = [dict(zip(column_names, row)) for row in rows]

            product_data = {}
            restock_predictions = {}

            for item in order_items:
                pid = item['product_id']
                if pid not in product_data:
                    product_data[pid] = {
                        "name": item['product_name'],
                        "stock_quantity": item['stock_quantity'],
                        "sales": []
                    }
                # Store (date, quantity)
                product_data[pid]["sales"].append((item['order_date'], item['quantity']))

            for pid, pdata in product_data.items():
                sales = sorted(pdata["sales"], key=lambda x: x[0])
                if len(sales) < 2:
                    continue  # not enough data to train model

                # Prepare X (days since first order) and y (quantity)
                start_date = sales[0][0]
                X = np.array([(s[0] - start_date).days for s in sales]).reshape(-1, 1)
                y = np.array([s[1] for s in sales])

                model = LinearRegression()
                model.fit(X, y)

                # Predict future day when total stock will be depleted
                total_stock = pdata["stock_quantity"]
                days = 0
                predicted_total = 0

                while predicted_total < total_stock and days < 365:
                    qty = model.predict(np.array([[days]]))[0]
                    qty = max(qty, 0)
                    predicted_total += qty
                    days += 1

                restock_date = (start_date + timedelta(days=days)).date()

                restock_predictions[pid] = {
                    "product_name": pdata["name"],
                    "stock_quantity": total_stock,
                    "predicted_days_until_restock": days,
                    "restock_date": restock_date
                }

            cursor.close()
            return jsonify(list(restock_predictions.values()))

        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    @dss_bp.route('/expiry_alerts', methods=['GET'])
    def expiry_alerts():
        current_date = datetime.now().date()

        high_demand_threshold = 50
        low_demand_threshold = 0

        try:
            conn = mysql.connection
            cursor = conn.cursor()

            cursor.execute("""
                SELECT product_id, product_name, expiry_date, stock_quantity
                FROM products
                WHERE expiry_date > %s
                ORDER BY expiry_date ASC
            """, (current_date,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            products = [dict(zip(columns, row)) for row in rows]

            result = []

            for row in products:
                product_id = row['product_id']
                product_name = row['product_name']
                expiry_date = row['expiry_date']
                stock_quantity = row['stock_quantity']

                if isinstance(expiry_date, datetime):
                    expiry_datetime = expiry_date
                else:
                    expiry_datetime = datetime.combine(expiry_date, datetime.min.time())

                time_to_expiry = (expiry_datetime - datetime.now()).days

                # Fetch sales data in last 30 days
                cursor.execute("""
                    SELECT SUM(oi.quantity) AS total_sales
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE oi.product_id = %s
                    AND o.order_date >= %s
                """, (product_id, current_date - timedelta(days=30)))
                
                sales_data = cursor.fetchone()
                total_sales = sales_data[0] if sales_data[0] else 0

                demand = "High" if total_sales >= high_demand_threshold else "Low"

                total_sales = float(total_sales)
                time_to_expiry = float(time_to_expiry)

                # Priority Score
                priority_score = (total_sales * 1) + (time_to_expiry * 0.5)

                # Expiry Alert Level
                if time_to_expiry <= 7.0:
                    expiry_alert = 'Urgent (Within 1 Week)'
                elif time_to_expiry <= 30.0:
                    expiry_alert = 'Warning (Within 1 Month)'
                else:
                    expiry_alert = 'Normal'

                result.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'expiry_date': expiry_datetime.strftime('%Y-%m-%d'),
                    'time_to_expiry': time_to_expiry,
                    'demand': demand,
                    'priority_score': round(priority_score, 2),
                    'expiry_alert': expiry_alert
                })

            result.sort(key=lambda x: x['priority_score'], reverse=True)

            cursor.close()
            return jsonify(result)

        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    @dss_bp.route('/smart_recommendations', methods=['GET'])
    def smart_recommendations():
        try:
            current_date = datetime.now()

            conn = mysql.connection
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.product_id, p.product_name, p.stock_quantity, 
                       COALESCE(SUM(oi.quantity), 0) AS total_sales
                FROM products p
                LEFT JOIN order_items oi ON p.product_id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.order_id
                WHERE o.order_date >= %s OR o.order_date IS NULL
                GROUP BY p.product_id
            """, (current_date - timedelta(days=30),))

            products = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            products = [dict(zip(columns, row)) for row in products]

            decision_matrix = []
            product_ids = []
            result_data = []

            for product in products:
                product_id = product['product_id']
                product_name = product['product_name']

                # Safe defaults
                stock = product['stock_quantity'] if product['stock_quantity'] is not None else 0
                sales = product['total_sales'] if product['total_sales'] is not None else 0

                if isinstance(stock, (int, float)) is False:
                    stock = 0
                if isinstance(sales, (int, float)) is False:
                    sales = 0

                # KPIs
                ssr = round(stock / sales, 2) if sales > 0 else float('inf')  # Stock to Sales Ratio
                itr = round(sales / stock, 2) if stock > 0 else 0             # Inventory Turnover

                # Trend Analysis (Last 4 weeks)
                cursor.execute("""
                    SELECT WEEK(order_date), SUM(oi.quantity)
                    FROM orders o
                    JOIN order_items oi ON o.order_id = oi.order_id
                    WHERE oi.product_id = %s AND o.order_date >= %s
                    GROUP BY WEEK(order_date)
                    ORDER BY WEEK(order_date)
                """, (product_id, current_date - timedelta(days=30)))

                trends = cursor.fetchall()
                weekly_sales = [row[1] for row in trends]

                if weekly_sales == sorted(weekly_sales):
                    trend_score = 1  # improving
                elif weekly_sales == sorted(weekly_sales, reverse=True):
                    trend_score = 3  # declining
                else:
                    trend_score = 2  # stable

                decision_matrix.append([ssr, 1/itr if itr > 0 else float('inf'), trend_score])
                product_ids.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "stock_quantity": stock,
                    "total_sales": sales
                })

            # Weights and Impacts for SAW
            weights = [0.4, 0.4, 0.2]  # importance of SSR, ITR, Trend
            impacts = ['+', '+', '+']  # higher = worse, so + means promotion needed

            scores, ranks = saw(decision_matrix, weights, impacts)

            # Build final response
            for i, product in enumerate(product_ids):
                rank = ranks[i]
                score = round(scores[i], 4)

                if rank <= 3:
                    recommendation = "High Priority Promotion"
                elif rank <= 6:
                    recommendation = "Moderate Promotion"
                else:
                    recommendation = "No Immediate Promotion"

                result_data.append({
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "stock_quantity": product["stock_quantity"],
                    "total_sales": product["total_sales"],
                    "score": score,
                    "rank": int(rank),
                    "promotion_recommendation": recommendation
                })

            cursor.close()
            return jsonify(result_data)

        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    @dss_bp.route('/seasonal_forecast', methods=['GET'])
    def seasonal_forecast():
        try:
            conn = mysql.connection
            cursor = conn.cursor()

            # Step 1: Fetch historical sales
            query = """
                SELECT p.product_id, p.product_name, o.order_date, oi.quantity
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN products p ON p.product_id = oi.product_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            sales_data = [dict(zip(column_names, row)) for row in rows]

            # Step 2: Organize sales data
            monthly_sales = defaultdict(lambda: defaultdict(int))  
            product_names = {}

            for row in sales_data:
                product_id = row['product_id']
                product_name = row['product_name']
                quantity = row['quantity']
                order_date = row['order_date']

                product_names[product_id] = product_name
                month = order_date.strftime('%Y-%m')
                monthly_sales[product_id][month] += quantity

            # Step 3: Forecast and pattern detection
            forecast_results = []

            for product_id, sales_by_month in monthly_sales.items():
                sorted_months = sorted(sales_by_month.keys())
                sales_values = [sales_by_month[m] for m in sorted_months]
                avg_sales = round(sum(sales_values) / len(sales_values), 2)

                # Predict next month
                last_month = sorted_months[-1]
                year, month = map(int, last_month.split('-'))
                if month == 12:
                    next_month = f"{year + 1}-01"
                else:
                    next_month = f"{year}-{str(month + 1).zfill(2)}"
                next_month_name = f"{calendar.month_name[int(next_month.split('-')[1])]} {next_month.split('-')[0]}"

                # High season detection
                high_season_months = [m for m in sorted_months if sales_by_month[m] > avg_sales * 1.2]
                season_names = [calendar.month_name[int(m.split('-')[1])] for m in high_season_months]
                seasonal_pattern = f"High demand in {', '.join(season_names)}" if season_names else "No strong seasonality"

                # Top selling month
                top_selling_month = max(sales_by_month, key=sales_by_month.get)
                top_selling_month_name = calendar.month_name[int(top_selling_month.split('-')[1])]

                # Month-wise sales with full names
                monthly_trend_named = {
                    calendar.month_name[int(m.split('-')[1])] + ' ' + m.split('-')[0]: sales_by_month[m]
                    for m in sorted_months
                }

                forecast_results.append({
                    "product_id": product_id,
                    "product_name": product_names[product_id],
                    "average_monthly_sales": avg_sales,
                    "next_month": next_month,
                    "next_month_name": next_month_name,
                    "forecast_sales": round(avg_sales),
                    "monthly_sales_trend": monthly_trend_named,
                    "top_selling_month": top_selling_month_name,
                    "seasonal_pattern": seasonal_pattern
                })

            cursor.close()
            return jsonify(forecast_results)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return dss_bp