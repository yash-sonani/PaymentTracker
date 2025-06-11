from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import mysql.connector
from mysql.connector import Error
import io
from datetime import datetime
import os

from checkprinting import makepdf

app = Flask(__name__)
app.secret_key = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

# Database configuration - Update these with your SiteGround MySQL details
DB_CONFIG = {
    "host": os.getenv("host"),
    "database": os.getenv("database"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "port": 3306,
}


def get_db_connection():
    """Get database connection"""
    try:
        # Ensure port is an integer
        config = DB_CONFIG.copy()
        print(config)
        if "port" in config and not isinstance(config["port"], int):
            config["port"] = int(config["port"])

        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def init_db():
    """Initialize database table"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                payee VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                date DATE NOT NULL,
                memo TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Table created successfully")
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            connection.close()


@app.route("/")
def home():
    """Home page with navigation options"""
    return render_template("home.html")


@app.route("/add_payment", methods=["GET", "POST"])
def add_payment():
    """Add new payment record"""
    if request.method == "POST":
        payee = request.form.get("payee")
        amount = request.form.get("amount")
        date = request.form.get("date")
        memo = request.form.get("memo")
        address = request.form.get("address")

        # Validate required fields
        if not all([payee, amount, date]):
            flash("Please fill in all required fields (Payee, Amount, Date)", "error")
            return redirect(url_for("add_payment"))

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                insert_query = """
                INSERT INTO payments (payee, amount, date, memo, address)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(
                    insert_query, (payee, float(amount), date, memo, address)
                )
                connection.commit()

                flash("Payment record added successfully!", "success")
                return redirect(url_for("view_payments"))
            except Error as e:
                flash(f"Error adding record: {e}", "error")
            finally:
                connection.close()
        else:
            flash("Database connection failed", "error")

    return render_template("add_payment.html")


@app.route("/view_payments")
def view_payments():
    """View all payment records with search functionality"""
    connection = get_db_connection()
    payments = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments ORDER BY date DESC")
            payments = cursor.fetchall()

            # Convert date objects to strings for JSON serialization
            for payment in payments:
                if payment["date"]:
                    payment["date"] = payment["date"].strftime("%Y-%m-%d")
                if payment["created_at"]:
                    payment["created_at"] = payment["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                if payment["updated_at"]:
                    payment["updated_at"] = payment["updated_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

        except Error as e:
            flash(f"Error fetching records: {e}", "error")
        finally:
            connection.close()
    else:
        flash("Database connection failed", "error")

    return render_template("view_payments.html", payments=payments)


@app.route("/edit_payment/<int:payment_id>", methods=["GET", "POST"])
def edit_payment(payment_id):
    """Edit existing payment record"""
    connection = get_db_connection()

    if request.method == "POST":
        payee = request.form.get("payee")
        amount = request.form.get("amount")
        date = request.form.get("date")
        memo = request.form.get("memo")
        address = request.form.get("address")

        if connection:
            try:
                cursor = connection.cursor()
                update_query = """
                UPDATE payments 
                SET payee = %s, amount = %s, date = %s, memo = %s, address = %s
                WHERE id = %s
                """
                cursor.execute(
                    update_query,
                    (payee, float(amount), date, memo, address, payment_id),
                )
                connection.commit()
                flash("Payment record updated successfully!", "success")
                return redirect(url_for("view_payments"))
            except Error as e:
                flash(f"Error updating record: {e}", "error")
            finally:
                connection.close()

    # GET request - fetch payment data for editing
    payment = None
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
            payment = cursor.fetchone()
            if payment and payment["date"]:
                payment["date"] = payment["date"].strftime("%Y-%m-%d")
        except Error as e:
            flash(f"Error fetching record: {e}", "error")
        finally:
            connection.close()

    if not payment:
        flash("Payment record not found", "error")
        return redirect(url_for("view_payments"))

    return render_template("edit_payment.html", payment=payment)


@app.route("/delete_payment/<int:payment_id>", methods=["POST"])
def delete_payment(payment_id):
    """Delete payment record"""
    connection = get_db_connection()

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM payments WHERE id = %s", (payment_id,))
            connection.commit()
            flash("Payment record deleted successfully!", "success")
        except Error as e:
            flash(f"Error deleting record: {e}", "error")
        finally:
            connection.close()
    else:
        flash("Database connection failed", "error")

    return redirect(url_for("view_payments"))


@app.route("/download_payment/<int:payment_id>", methods=["POST"])
def download_payment(payment_id):
    """Download payment record as PDF"""
    connection = get_db_connection()

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
            payment = cursor.fetchone()

            if payment:
                # Create PDF using makepdf method and download generated pdf
                generated_pdf = makepdf(
                    payee=payment["payee"],
                    amount = payment['amount'],                    
                    date = payment["date"].strftime("%m/%d/%Y"),
                    memo=payment["memo"],
                    address=payment["address"],
                )
                try:
                    pdf_buffer = io.BytesIO()
                    pdf_output = generated_pdf.output()
                    pdf_buffer.write(pdf_output)
                    pdf_buffer.seek(0)
                except Exception as e:
                    flash(f"Error generating PDF: {e}", "error")
                flash("Payment record downloaded successfully!", "success")

                file_name = f"payment_{payment_id}.pdf"

                return send_file(
                    pdf_buffer,
                    as_attachment=True,
                    download_name=file_name,
                    mimetype='application/pdf'
                )
                
            else:
                flash("Payment record not found", "error")
        except Error as e:
            flash(f"Error downloading record: {e}", "error")
        finally:
            connection.close()
    else:
        flash("Database connection failed", "error")

    return redirect(url_for("view_payments"))


@app.route("/api/payments")
def api_payments():
    """API endpoint for payment data (for DataTables)"""
    connection = get_db_connection()
    payments = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM payments ORDER BY date DESC")
            payments = cursor.fetchall()

            # Convert date objects to strings
            for payment in payments:
                if payment["date"]:
                    payment["date"] = payment["date"].strftime("%Y-%m-%d")

        except Error as e:
            print(f"Error fetching records: {e}")
        finally:
            connection.close()

    return jsonify({"data": payments})


if __name__ == "__main__":
    # Initialize database
    init_db()
    # Run the app
    app.run(debug=True)
