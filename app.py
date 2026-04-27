import pymysql
from flask import Flask, flash, jsonify, render_template

from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def get_db_connection():
    return pymysql.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def dashboard():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Total counts
            cur.execute("SELECT COUNT(*) AS total FROM film")
            total_films = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS total FROM actor")
            total_actors = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS total FROM customer")
            total_customers = cur.fetchone()["total"]

            cur.execute(
                "SELECT COUNT(*) AS total FROM rental WHERE return_date IS NULL"
            )
            active_rentals = cur.fetchone()["total"]

            # Revenue statistics
            cur.execute(
                """
                SELECT SUM(amount) AS total_revenue,
                       AVG(amount) AS avg_rental_price,
                       COUNT(*) AS total_transactions
                FROM payment
                WHERE payment_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """
            )
            revenue_stats = cur.fetchone()

            # Recent rentals
            cur.execute(
                """
                SELECT r.rental_id, f.title, c.first_name, c.last_name, r.rental_date
                FROM rental r
                JOIN inventory i ON r.inventory_id = i.inventory_id
                JOIN film f ON i.film_id = f.film_id
                JOIN customer c ON r.customer_id = c.customer_id
                ORDER BY r.rental_date DESC
                LIMIT 10
                """
            )
            recent_rentals = cur.fetchall()

            # Popular films
            cur.execute(
                """
                SELECT f.title, COUNT(r.rental_id) AS rental_count
                FROM film f
                JOIN inventory i ON f.film_id = i.film_id
                JOIN rental r ON i.inventory_id = r.inventory_id
                GROUP BY f.film_id, f.title
                ORDER BY rental_count DESC
                LIMIT 10
                """
            )
            popular_films = cur.fetchall()

            # Store stats
            cur.execute(
                """
                SELECT s.store_id, a.address, a.district, ci.city, co.country,
                       (SELECT COUNT(*) FROM customer c WHERE c.store_id = s.store_id) AS customer_count,
                       (SELECT COUNT(*) FROM inventory i WHERE i.store_id = s.store_id) AS inventory_count
                FROM store s
                JOIN address a ON s.address_id = a.address_id
                JOIN city ci ON a.city_id = ci.city_id
                JOIN country co ON ci.country_id = co.country_id
                """
            )
            store_stats = cur.fetchall()

        conn.close()

        return render_template(
            "dashboard.html",
            total_films=total_films,
            total_actors=total_actors,
            total_customers=total_customers,
            active_rentals=active_rentals,
            revenue_stats=revenue_stats,
            recent_rentals=recent_rentals,
            popular_films=popular_films,
            store_stats=store_stats,
        )

    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "error")
        return render_template(
            "dashboard.html",
            total_films=0,
            total_actors=0,
            total_customers=0,
            active_rentals=0,
            revenue_stats={
                "total_revenue": 0,
                "avg_rental_price": 0,
                "total_transactions": 0,
            },
            recent_rentals=[],
            popular_films=[],
            store_stats=[],
        )


@app.route("/api/actor/<int:actor_id>")
def get_actor_details(actor_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM actor WHERE actor_id = %s", (actor_id,))
            actor = cur.fetchone()

            if not actor:
                return jsonify({"error": "Actor not found"}), 404

            cur.execute(
                """
                SELECT f.film_id, f.title, f.release_year, f.rating, c.name AS category
                FROM film f
                JOIN film_actor fa ON f.film_id = fa.film_id
                LEFT JOIN film_category fc ON f.film_id = fc.film_id
                LEFT JOIN category c ON fc.category_id = c.category_id
                WHERE fa.actor_id = %s
                ORDER BY f.title
                """,
                (actor_id,),
            )
            films = cur.fetchall()

        conn.close()

        return jsonify({"actor": actor, "films": films})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")