import sqlite3
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

class DairyDB:
    def __init__(self, db_name="dairy.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT,
                shift TEXT,
                mound REAL,
                kg REAL,
                rate REAL
            )
        """)
        self.conn.commit()

    def add_record(self, name, date, shift, mound, kg, rate):
        self.conn.execute("INSERT INTO records (name, date, shift, mound, kg, rate) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, date, shift, mound, kg, rate))
        self.conn.commit()

    def get_all_records(self, name):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM records WHERE name = ? ORDER BY date", (name,))
        return cur.fetchall()

    def delete_record(self, record_id):
        self.conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        self.conn.commit()


def export_pdf(name, records):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    start_y = height - 100

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, start_y, "Owner Name: Obaid Malik")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, start_y - 25, f"Customer Name: {name}")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, start_y - 60, "Dairy Record")

    table_data = [["Date", "Shift", "Mound", "Kg", "Rate", "Total"]]
    total_mound = total_kg = 0

    for rec in records:
        _, _, date, shift, mound, kg, rate = rec
        total = mound * rate if rate else ""
        table_data.append([
            date,
            shift,
            f"{mound}" if mound else "",
            f"{kg}" if kg else "",
            f"{rate}" if rate else "",
            f"{total}" if total else ""
        ])
        total_mound += mound
        total_kg += kg

    table_data.append(["", "", f"Total: {total_mound}", f"Total: {total_kg}", "", ""])

    table = Table(table_data, colWidths=[80, 60, 60, 60, 60, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 40, start_y - 400)

    c.save()
    buffer.seek(0)
    return buffer
