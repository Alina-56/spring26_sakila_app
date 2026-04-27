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

            cur.execute("""
                SELECT SUM(amount) AS total_revenue,
                       AVG(amount) AS avg_rental_price,
                       COUNT(*) AS total_transactions
                FROM payment
                WHERE payment_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """)
            revenue_stats = cur.fetchone()

            cur.execute("""
                SELECT r.rental_id, f.title, c.first_name, c.last_name, r.rental_date
                FROM rental r
                JOIN inventory i ON r.inventory_id = i.inventory_id
                JOIN film f ON i.film_id = f.film_id
                JOIN customer c ON r.customer_id = c.customer_id
                ORDER BY r.rental_date DESC
                LIMIT 10
                """)
            recent_rentals = cur.fetchall()

            cur.execute("""
                SELECT f.title, COUNT(r.rental_id) AS rental_count
                FROM film f
                JOIN inventory i ON f.film_id = i.film_id
                JOIN rental r ON i.inventory_id = r.inventory_id
                GROUP BY f.film_id, f.title
                ORDER BY rental_count DESC
                LIMIT 10
                """)
            popular_films = cur.fetchall()

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
        )

    except Exception as e:
        flash(str(e), "error")
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
        )


@app.route("/api/actor/<int:actor_id>")
def get_actor(actor_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM actor WHERE actor_id=%s", (actor_id,))
            actor = cur.fetchone()

            if not actor:
                return jsonify({"error": "Actor not found"}), 404

        conn.close()
        return jsonify(actor)

    except Exception:
        return jsonify({"error": "database error"}), 500


@app.route("/api/film/<int:film_id>")
def get_film(film_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM film WHERE film_id=%s", (film_id,))
            film = cur.fetchone()

            if not film:
                return jsonify({"error": "Film not found"}), 404

        conn.close()
        return jsonify(film)

    except Exception:
        return jsonify({"error": "database error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

