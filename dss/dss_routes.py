from turtle import pd
from flask import Blueprint, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import defaultdict
import calendar
from pygsp import filters
import pygsp as gsp
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pyDecision
import random
from sklearn.cluster import KMeans

from fahp_custom import fahp

dss_bp = Blueprint('dss', __name__)
mysql = None

def init_dss_routes(app, mysql_instance):
    global mysql
    mysql = mysql_instance
    app.register_blueprint(dss_bp)


@dss_bp.route('/dss/test', methods=['GET'])
def test_dss():
    return jsonify({"message": "DSS Blueprint Working!"})


#Decision Support System (DSS) Analysis
@dss_bp.route("/dss", methods=['GET'])
def decision_support_system_advanced():
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        # STEP 1: Query
        query = """
            SELECT 
                oi.product_id,
                p.product_name,
                p.cost_price AS unit_cost_price,
                p.price AS unit_selling_price,
                SUM(oi.quantity) AS total_quantity,
                SUM(oi.quantity * p.cost_price) AS total_cost,
                SUM(oi.quantity * oi.unit_price) AS total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY oi.product_id, p.product_name, p.cost_price, p.price
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        results = [dict(zip(columns, row)) for row in rows]

        if not results:
            return jsonify({"error": "No data found."}), 404

        import numpy as np
        from sklearn.cluster import KMeans

        quantities = [item["total_quantity"] for item in results]
        quantity_array = np.array(quantities).reshape(-1, 1)

        # STEP 2: KMeans
        if len(quantities) >= 3:
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            labels = kmeans.fit_predict(quantity_array)

            centers = kmeans.cluster_centers_.flatten()
            sorted_centers = sorted((center, idx) for idx, center in enumerate(centers))
            demand_mapping = {
                idx: level for level, (_, idx) in zip(["Low", "Medium", "High"], sorted_centers)
            }
        else:
            labels = [0 for _ in quantity_array]
            demand_mapping = {0: "Low"}

        formatted_results = []
        for item, label in zip(results, labels):
            cost_price = float(item["unit_cost_price"])
            selling_price = float(item["unit_selling_price"])
            total_cost = float(item["total_cost"])
            total_revenue = float(item["total_revenue"])
            quantity_sold = item["total_quantity"]

            profit_margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0.0
            demand_level = demand_mapping.get(label, "Low")

            formatted_results.append({
                "product_name": item["product_name"],
                "cost_price": f"Rs. {cost_price:.2f}",
                "selling_price": f"Rs. {selling_price:.2f}",
                "profit_margin": f"{profit_margin:.2f}%",
                "demand_level": demand_level,
                "quantity_sold": f"{quantity_sold} units"
            })

            # STEP 3: INSERT or UPDATE
            cursor.execute("SELECT record_id FROM profit_records WHERE product_id = %s", (item["product_id"],))
            existing_record = cursor.fetchone()

            if existing_record:
                cursor.execute("""
                    UPDATE profit_records
                    SET product_name = %s,
                        cost_price = %s,
                        selling_price = %s,
                        profit_margin = %s,
                        demand_level = %s
                    WHERE product_id = %s
                """, (
                    item["product_name"],
                    cost_price,
                    selling_price,
                    profit_margin,
                    demand_level,
                    item["product_id"]
                ))
            else:
                cursor.execute("""
                    INSERT INTO profit_records 
                    (product_id, product_name, cost_price, selling_price, profit_margin, demand_level) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    item["product_id"],
                    item["product_name"],
                    cost_price,
                    selling_price,
                    profit_margin,
                    demand_level
                ))

        conn.commit()
        return jsonify({"results": formatted_results}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500




# Restock Prediction
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



# Expiry alerts
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



# Smart Recommendations
@dss_bp.route('/smart_recommendations', methods=['GET'])
def smart_recommendations():
    try:
        # Import FAHP fallback if custom not found
        try:
            from fahp_custom import fahp
        except ImportError:
            def fahp(matrix):
                n = len(matrix)
                fuzzy_sums = [np.zeros(3) for _ in range(n)]
                for i in range(n):
                    for j in range(n):
                        fuzzy_sums[i] += np.array(matrix[i][j])
                total_sum = np.sum(fuzzy_sums, axis=0)
                weights = []
                for i in range(n):
                    l = fuzzy_sums[i][0] / total_sum[2]
                    m = fuzzy_sums[i][1] / total_sum[1]
                    u = fuzzy_sums[i][2] / total_sum[0]
                    weights.append((l + m + u) / 3)
                weights = np.array(weights)
                return weights / np.sum(weights)

        from sklearn.preprocessing import MinMaxScaler

        current_date = datetime.now()
        conn = mysql.connection
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.product_id, p.product_name, p.stock_quantity,
                   COALESCE(SUM(oi.quantity), 0) AS total_sales,
                   COALESCE(SUM(oi.unit_price * oi.quantity), 0) AS gross_sales,
                   0 AS discount,
                   0 AS allowance,
                   COALESCE(SUM(p.price * oi.quantity), 0) AS cogs,
                   0 AS backorders,
                   COUNT(DISTINCT o.order_id) AS total_orders,
                   0 AS stock_outs,
                   COALESCE(SUM(oi.quantity), 0) AS received_units
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_date >= %s OR o.order_date IS NULL
            GROUP BY p.product_id
        """, (current_date - timedelta(days=30),))

        products = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        products = [dict(zip(columns, row)) for row in products]

        # --- FAHP fuzzy matrix
        fuzzy_matrix = [
            [[1, 1, 1], [1, 2, 3], [3, 4, 5], [5, 6, 7], [1, 2, 3], [3, 4, 5]],
            [[1/3, 1/2, 1], [1, 1, 1], [2, 3, 4], [3, 4, 5], [1, 2, 3], [2, 3, 4]],
            [[1/5, 1/4, 1/3], [1/4, 1/3, 1/2], [1, 1, 1], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
            [[1/7, 1/6, 1/5], [1/5, 1/4, 1/3], [1/3, 1/2, 1], [1, 1, 1], [1, 1, 2], [2, 3, 4]],
            [[1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/2, 1, 1], [1, 1, 1], [1, 2, 3]],
            [[1/5, 1/4, 1/3], [1/4, 1/3, 1/2], [1/3, 1/2, 1], [1/4, 1/3, 1/2], [1/3, 1/2, 1], [1, 1, 1]]
        ]
        fahp_weights = fahp(fuzzy_matrix)

        decision_matrix = []
        result_data = []

        for p in products:
            # Convert Decimal to float safely
            cogs = float(p['cogs'] or 0.0001)
            stock_qty = float(p['stock_quantity'] or 0)
            total_sales = float(p['total_sales'] or 0)
            total_orders = float(p['total_orders'] or 0.0001)
            received_units = float(p['received_units'] or 0.0001)
            gross_sales = float(p['gross_sales'] or 0)
            discount = float(p['discount'] or 0)
            allowance = float(p['allowance'] or 0)
            backorders = float(p['backorders'] or 0)
            stock_outs = float(p['stock_outs'] or 0)

            avg_inventory = (stock_qty + stock_qty) / 2 or 0.0001
            net_sales = (gross_sales - discount - allowance) or 0.0001

            # KPIs
            itr = round(cogs / avg_inventory, 2)
            product_sales = round(net_sales, 2)
            gross_margin = round(((net_sales - cogs) / net_sales) * 100, 2)
            backorder_rate = round((backorders / total_orders) * 100, 2)
            sell_through = round((total_sales / received_units) * 100, 2)
            stock_out = round((stock_outs / total_orders) * 100, 2)

            decision_matrix.append([
                itr,
                product_sales,
                gross_margin,
                backorder_rate,
                sell_through,
                stock_out
            ])

            result_data.append({
                "product_id": p['product_id'],
                "product_name": p['product_name'],
               
            })

        # Normalize + Score
        X = np.array(decision_matrix, dtype=float)
        scaler = MinMaxScaler()
        X_norm = scaler.fit_transform(X)

        impacts = ['+', '+', '+', '-', '+', '-']
        for i, impact in enumerate(impacts):
            if impact == '-':
                X_norm[:, i] = 1 - X_norm[:, i]

        scores = np.dot(X_norm, fahp_weights)
        ranks = np.argsort(-scores) + 1

        for i, product in enumerate(result_data):
            product["score"] = round(scores[i], 4)
            product["rank"] = int(ranks[i])

            if product["rank"] <= 3:
                product["recommendation"] = "Promote & Restock"
                product["reason"] = "High demand, high profit, and low stock issues."
            elif product["rank"] <= 6:
                product["recommendation"] = "Monitor Closely"
                product["reason"] = "Mixed KPI performance."
            else:
                product["recommendation"] = "Low Priority"
                product["reason"] = "Low demand because of  margin issues."

        cursor.close()
        return jsonify(result_data)

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500



# Seasonal Forecasting

@dss_bp.route('/seasonal_forecast', methods=['GET'])
def seasonal_forecast():
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        # 1️⃣ Fetch historical sales
        query = """
            SELECT p.product_id, p.product_name, o.order_date, oi.quantity, p.stock_quantity
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN products p ON p.product_id = oi.product_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        sales_data = [dict(zip(column_names, row)) for row in rows]

        # 2️⃣ Group sales by product & by month
        monthly_sales = defaultdict(lambda: defaultdict(int))
        product_names = {}
        stock_quantities = {}

        for row in sales_data:
            if row['order_date'] is None:
                continue
            product_id = row['product_id']
            quantity = row['quantity']
            order_date = row['order_date']
            stock_quantities[product_id] = row['stock_quantity']
            product_names[product_id] = row['product_name']

            month = order_date.strftime('%Y-%m')
            monthly_sales[product_id][month] += quantity

        # 3️⃣ Helper for smoothing sales
        def smooth(values, window=3):
            return np.convolve(values, np.ones(window)/window, mode='same')

        forecast_results = []
        average_unit_cost = 100.0  # Example cost per unit

        for product_id, sales_by_month in monthly_sales.items():
            sorted_months = sorted(sales_by_month.keys())
            sales_values = np.array([sales_by_month[m] for m in sorted_months], dtype=float)

            # Smooth sales
            smoothed_values = smooth(sales_values, window=3)
            avg_sales = round(np.mean(smoothed_values), 2)

            # Next Month
            last_month = sorted_months[-1]
            year, month = map(int, last_month.split('-'))
            next_month = f"{year + 1}-01" if month == 12 else f"{year}-{str(month + 1).zfill(2)}"

            prediction = round(avg_sales)

            actual_demand = sales_values[-1]

            # ✅ Forecast Accuracy
            forecast_accuracy_percentage = round((1 - abs(actual_demand - prediction) / actual_demand) * 100, 2) if actual_demand > 0 else 0.0

            # ✅ Inventory Turnover Rate
            cogs = sum(sales_values) * average_unit_cost
            average_inventory = stock_quantities[product_id] / 2.0 if stock_quantities[product_id] else 1
            inventory_turnover_rate = round(cogs / average_inventory, 2)

            # ✅ Seasonal Pattern
            high_season_months = [m for m in sorted_months if sales_by_month[m] > avg_sales * 1.2]
            if high_season_months:
                month_names = [calendar.month_name[int(m.split('-')[1])] for m in high_season_months]
                if len(month_names) == 1:
                    season_type = f"High Season ({month_names[0]})"
                    peak_season_date = datetime.strptime(high_season_months[0], "%Y-%m").date()
                    season_end = peak_season_date
                else:
                    season_type = f"High Season ({month_names[0]}–{month_names[-1]})"
                    peak_season_date = datetime.strptime(high_season_months[0], "%Y-%m").date()
                    season_end = datetime.strptime(high_season_months[-1], "%Y-%m").date()
            else:
                season_type = "No Strong Seasonality"
                peak_season_date = datetime.strptime(last_month, "%Y-%m").date()
                season_end = datetime.strptime(last_month, "%Y-%m").date()

            preparation_start_date = datetime.strptime(sorted_months[0], "%Y-%m").date()

            # ✅ Final Result
            result = {
                "product_id": product_id,
                "year": year,
                "season_type": season_type,
                "predicted_demand": f"{prediction} units",
                "actual_demand": f"{actual_demand} units",
                "forecast_accuracy": f"{forecast_accuracy_percentage}%",
                "inventory_turnover_rate": f"{inventory_turnover_rate} times/year",
                "preparation_start_date": preparation_start_date.strftime("%Y-%m-%d"),
                "peak_season_date": peak_season_date.strftime("%Y-%m-%d"),
                "season_end_date": season_end.strftime("%Y-%m-%d")
            }
            forecast_results.append(result)

            # ✅ Save to database
            insert_query = """
                INSERT INTO seasonal_forecasts 
                (product_id, year, season_type, predicted_demand, actual_demand, forecast_accuracy,
                inventory_turnover_rate, preparation_start_date, peak_season_date, season_end_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                product_id,
                year,
                season_type,
                prediction,
                actual_demand,
                forecast_accuracy_percentage,
                inventory_turnover_rate,
                preparation_start_date.strftime("%Y-%m-%d"),
                peak_season_date.strftime("%Y-%m-%d"),
                season_end.strftime("%Y-%m-%d")
            ))

        conn.commit()
        cursor.close()
        return jsonify(forecast_results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


