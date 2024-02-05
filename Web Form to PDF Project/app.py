from flask import Flask, render_template, request, make_response, render_template_string
import sqlite3

from pdfkit import pdfkit

app = Flask(__name__)


def read_html_template():
    with open('./index.html', 'r') as file:
        return file.read()


html_template = read_html_template()


def create_table():
    connection = sqlite3.connect('invoice.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            full_name TEXT,
            address TEXT,
            business_number TEXT,
            shipper_exporter TEXT,
            date TEXT,
            invoice_number TEXT,
            consignee TEXT,
            customer_po_number TEXT,
            date_of_export TEXT,
            notify_party TEXT,
            country_of_origin TEXT,
            bl_awb_number TEXT,
            marks TEXT,
            final_destination TEXT,
            export_route_carrier TEXT,
            terms_of_sale TEXT,
            terms_of_payment TEXT,
            freight_prepaid BOOLEAN,
            freight_collect BOOLEAN,
            quantity INTEGER,
            description TEXT,
            hs_number TEXT,
            unit_price TEXT,
            total_price TEXT,
            subtotal TEXT,
            handling TEXT,
            total TEXT,
            certification TEXT,
            exported_to TEXT


        )
    ''')
    connection.commit()
    # print("Table created successful")
    connection.close()


def generate_invoice_pdf(data):
    # Render the HTML template with the provided data
    html_content = render_template_string(html_template, data=data)

    # Set up options for pdfkit
    options = {
        'page-size': 'Letter',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
    }

    # Generate PDF from HTML content
    pdf_filename = f"invoice_{data['invoice_number']}.pdf"
    pdfkit.from_string(html_content, pdf_filename, options=options)

    return pdf_filename


def get_invoice_data_from_db(invoice_number):
    connection = sqlite3.connect('invoice.db')
    cursor = connection.cursor()

    # Fetch the specific invoice data based on the invoice_number
    cursor.execute('''
        SELECT * FROM invoices WHERE invoice_number = ?
    ''', (invoice_number,))

    invoice_data = cursor.fetchone()

    connection.close()

    if invoice_data:
        # Convert the tuple result to a dictionary for easier use
        invoice_dict = {
            'full_name': invoice_data[1],
            'address': invoice_data[2],
            'business_number': invoice_data[3],
            'shipper_exporter': invoice_data[4],
            'date': invoice_data[5],
            'invoice_number': invoice_data[6],
            'consignee': invoice_data[7],
            'customer_po_number': invoice_data[8],
            'date_of_export': invoice_data[9],
            'notify_party': invoice_data[10],
            'country_of_origin': invoice_data[11],
            'bl_awb_number': invoice_data[12],
            'marks': invoice_data[13],
            'final_destination': invoice_data[14],
            'export_route_carrier': invoice_data[15],
            'terms_of_sale': invoice_data[16],
            'terms_of_payment': invoice_data[17],
            'freight_prepaid': bool(invoice_data[18]),
            'freight_collect': bool(invoice_data[19]),
            'quantity': invoice_data[20],
            'description': invoice_data[21],
            'hs_number': invoice_data[22],
            'unit_price': invoice_data[23],
            'total_price': invoice_data[24],
            'subtotal': invoice_data[25],
            'handling': invoice_data[26],
            'total': invoice_data[27],
            'certification': invoice_data[28],
            'exported_to': invoice_data[29]
        }

        return invoice_dict

    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Extract checkbox values
        freight_prepaid = 'prepaid' in request.form.getlist('freight')
        freight_collect = 'collect' in request.form.getlist('freight')

        data = {
            'full_name': request.form['full-name'],
            'address': request.form['address'],
            'business_number': request.form['business-number'],
            'shipper_exporter': request.form['shipper_exporter'],
            'date': request.form['date'],
            'invoice_number': request.form['invoiceNumber'],
            'consignee': request.form['consignee'],
            'customer_po_number': request.form['customerPONumber'],
            'date_of_export': request.form['dateOfExport'],
            'notify_party': request.form['notify_Party'],
            'country_of_origin': request.form['countryOfOrigin'],
            'bl_awb_number': request.form['blAwbNumber'],
            'marks': request.form['marks'],
            'final_destination': request.form['finalDestination'],
            'export_route_carrier': request.form['exportRouteCarrier'],
            'terms_of_sale': request.form['termsOfSale'],
            'terms_of_payment': request.form['termsOfPayment'],
            'freight_prepaid': freight_prepaid,
            'freight_collect': freight_collect,
            'quantity': int(request.form['quantity']),
            'description': request.form['description'],
            'hs_number': request.form['hsNumber'],
            'unit_price': request.form['unitPrice'],
            'total_price': request.form['totalPrice'],
            'subtotal': request.form['subtotal'],
            'handling': request.form['handling'],
            'total': request.form['total'],
            'certification': request.form['certification'],
            'exported_to': request.form['exportedTo']
        }

        connection = sqlite3.connect('invoice.db')
        cursor = connection.cursor()
        # Insert data into the 'invoices' table
        cursor.execute('''
            INSERT INTO invoices (
                full_name, address, business_number, shipper_exporter, date, invoice_number,
                consignee, customer_po_number, date_of_export, notify_party, country_of_origin,
                bl_awb_number, marks, final_destination, export_route_carrier, terms_of_sale,
                terms_of_payment, freight_prepaid, freight_collect, quantity, description, hs_number,
                unit_price, total_price, subtotal, handling, total, certification, exported_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['full_name'], data['address'], data['business_number'], data['shipper_exporter'],
            data['date'], data['invoice_number'], data['consignee'], data['customer_po_number'],
            data['date_of_export'], data['notify_party'], data['country_of_origin'],
            data['bl_awb_number'], data['marks'], data['final_destination'],
            data['export_route_carrier'], data['terms_of_sale'], data['terms_of_payment'],
            data['freight_prepaid'], data['freight_collect'], data['quantity'], data['description'],
            data['hs_number'], data['unit_price'], data['total_price'], data['subtotal'],
            data['handling'], data['total'], data['certification'], data['exported_to']
        ))
        connection.commit()
        # print("inserted the data successfully")
        connection.close()

        # Render the invoice template with the data
        invoice_html = render_template('invoice_template.html', data=data)

        # Generate a PDF invoice
        pdf_filename = generate_invoice_pdf(data)

        # Save the HTML to a file or do something else with it
        with open('invoice.html', 'w') as f:
            f.write(invoice_html)

        # Return a response indicating success
        return f"Invoice submitted successfully! Check your generated invoice.<br>PDF: {pdf_filename}"


@app.route('/view_invoices')
def view_invoices():
    connection = sqlite3.connect('invoice.db')
    cursor = connection.cursor()
    print("Select all records from the 'invoices' table")
    # Select all records from the 'invoices' table
    cursor.execute('SELECT * FROM invoices')
    print("Select all records from the 'invoices' table- fetch done")
    records = cursor.fetchall()
    # print("records are -", records)
    connection.close()

    return render_template('view_invoices_data.html', records=records)


@app.route('/download_invoice/<invoice_number>')
def download_invoice(invoice_number):
    # You need to implement logic to fetch the specific invoice data from the database
    # For simplicity, I'm assuming a function get_invoice_data_from_db to get the data
    invoice_data = get_invoice_data_from_db(invoice_number)

    if invoice_data:
        # Generate and download the PDF
        pdf_filename = generate_invoice_pdf(invoice_data)

        # Prepare the response for the PDF file
        response = make_response(pdf_filename)
        response.headers['Content-Disposition'] = f'attachment; filename={pdf_filename}'

        return response

    return "Invoice not found."


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
