import PySimpleGUI as sg
class SalesWindow:
    def __init__(self):
        pass

    @staticmethod
    def create_sales_window():
        sg.theme('NeutralBlue')

        sales_layout = [
            [sg.Text('', size=(15, 0), font=('Helvetica', 15), text_color='blue')],
            [sg.Text('SALES MENU', size=(13, 0), font=('Helvetica', 16), text_color='black')],
            [sg.Text('', size=(15, 0), font=('Helvetica', 15), text_color='blue')],
            [sg.Button('Sales', size=(10, 1)),
             sg.Button('Clients', size=(10, 1)), sg.Button('Invoices', size=(10, 1)),
             sg.Button('Reports', size=(8, 1), key='-REPORTS-'), sg.Button('Back', key='BACK', size=(10, 1))]
        ]
        # Create the main window
        sales_window = sg.Window('Busyman - Sales Menu', sales_layout, element_justification='center',
                                 size=(window_width, window_height), finalize=True, resizable=True, disable_close=False)
        sales_window.maximize()
        return sales_window

    @staticmethod
    def create_sales_reports_menu():
        sg.theme('NeutralBlue')

        sales_reports_layout = [
            [sg.Text('', size=(15, 0), font=('Helvetica', 15), text_color='blue')],
            [sg.Text('REPORTS MENU', size=(15, 0), font=('Helvetica', 16), text_color='black')],
            [sg.Text('', size=(15, 0), font=('Helvetica', 15), text_color='blue')],
            [sg.Button('Top Selling Products', key='-TOP-SELLING', size=(20, 1)),
             sg.Button('Outstanding Balance', key='Oustanding-Balance', size=(20, 1)),
             sg.Button('Summary of Sales', key='SALES-SUMMARY', size=(16, 1)),
             sg.Button('Sales Trends', key='-SALES-TRENDS-', size=(12, 1)),
             sg.Button('Records', key='-RECORDS-', size=(12, 1)),
             sg.Button('Back', key='BACK', size=(5, 1))]
        ]
        # Create the main window
        sales_report_window = sg.Window('Busyman - Sales Reports Menu', sales_reports_layout,
                                        element_justification='center',
                                        size=(window_width, window_height), finalize=True, resizable=True, disable_close=False)
        sales_report_window.maximize()
        return sales_report_window

    @staticmethod
    def read_client_names():
        # clients_sheet = file_input['Clients']
        clients_sheet = None
        for sheet in file_input.sheetnames:
            if sheet == 'Clients':
                clients_sheet = file_input[sheet]
        if not clients_sheet:
            clients_sheet = file_input.create_sheet('Clients')
        client_names = []
        for row in clients_sheet.iter_rows(min_row=2, values_only=True):
            name = row[1]
            company = row[2]
            if name:
                if company:
                    client_names.append(f"{name} - {company}")
                else:
                    client_names.append(name)
            elif company:
                client_names.append(company)
            else:
                client_names.append("")  # Or any default value if both are empty
        return client_names

    @staticmethod
    def create_sales_entry_window():

        product_info = StoresWindow.read_product_names()
        product_names = list(product_info.keys())
        next_invoice_number = HomeWindow.get_next_invoice_number()
        category = ['Book', 'Consultancy', 'Rent']
        account = AccountsWindow.read_acc_owner_names()
        bank_account = AccountsWindow.read_bank_names()

        sales_entry_layout = [
            [sg.Text('', size=(29, 1))],
            [sg.Text('Sell/Take-back', size=(27, 1), font=('Helvetica', 20), text_color='blue')],
            [sg.Text('', size=(29, 1))],
            [sg.Text('Search Customer Name ', key='CUSTOMER', size=(19, 1)), sg.InputText(key='-Name-', size=(28, 1)),
             sg.Button('Next', key='-Next-', size=(4, 1)), sg.Button('Exit', key='EXIT1', size=(6, 1)),
             sg.Text('', key='EMPTY', size=(4, 1), visible=False)],
            [
                sg.Text('', key='-Options-label-', size=(21, 1), visible=False),
                sg.Radio('Sell', 'RADIO1', key='-Sell-', size=(8, 1), visible=False),
                sg.Radio('Take-back', 'RADIO1', key='-Take-back-', visible=False, size=(14, 1))
            ],
            [sg.Text('Invoice Date', size=(19, 1), key='Invoice-date', visible=False),
             sg.InputText(key='-Invoice-date-', default_text=current_date, size=(34, 1), visible=False),
             sg.Button('', image_filename='refresh_resized.png',
                       button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0,
                       key='-REFRESH-DATE-', visible=False)],
            [sg.Text('Customer Name', size=(19, 1), key='-Customer-name', visible=False),
             sg.InputText(key='-Customer-Name-', size=(37, 1), disabled=True, visible=False)],
            [sg.Text('Invoice Number', size=(19, 1), key='Invoice-no', visible=False),
             sg.InputText(key='-Invoice No-', size=(37, 1), default_text=next_invoice_number, visible=False,
                          disabled=True)],
            [sg.Text('Invoice details', key='-Invoice-details-', size=(19, 1), visible=False),
             sg.Listbox(values=[], key='DETAILS', size=(35, 1), visible=False)],
            [sg.Text('Choose Product', key='-Book-label-', size=(19, 1), visible=False),
             sg.InputCombo(product_names, key='-Book-', size=(35, 1), readonly=False, visible=False)],
            [sg.Text('Choose Category', key='-Category-label-', size=(19, 1), visible=False),
             sg.InputCombo(category, key='-CATEGORY-', readonly=True, size=(35, 1), visible=False)],
            [sg.Text('Choose Account', key='-Accounts-label-', size=(19, 1), visible=False),
             sg.InputCombo(account, key='-ACCOUNTS-', readonly=True, size=(35, 1), visible=False)],
            [sg.Text('Choose Bank Account', key='-Bank-Accounts-label-', size=(19, 1), visible=False),
             sg.InputCombo(bank_account, key='-BANK-ACCOUNTS-', readonly=True, size=(35, 1), visible=False)],
            [sg.Text('Quantity', key='-Qty-label-', size=(19, 1), visible=False),
             sg.InputText(key='-Qty-', size=(37, 1), visible=False)],
            [sg.Text('Price', key='-Price-label-', size=(19, 1), visible=False),
             sg.InputText(key='-Price-', size=(37, 1), visible=False)],
            [sg.Text('Notes', key='-Notes-label-', size=(19, 1), visible=False),
             sg.Multiline(key='-Notes-', size=(35, 1), visible=False, enter_submits=False, autoscroll=True)],
            [sg.Text('', key='-empty-', size=(20, 1), visible=False),
             sg.Button('Add Entry', key='-More-', size=(14, 1), visible=False),
             sg.Button('Cancel', key='-Cancel-', visible=False, size=(6, 1)),
             sg.Button('Next', key='GET-NEXT', visible=False, size=(4, 1)),
             sg.Button('Exit', key='EXIT2', size=(6, 1), visible=False)]
        ]

        # Create the sales entry window
        sales_entry_window = sg.Window('Busyman - Sales Entry', sales_entry_layout, finalize=True,
                                       element_justification='center',
                                       size=(window_width, window_height), resizable=True, return_keyboard_events=True, disable_close=False)
        sales_entry_window.maximize()
        return sales_entry_window, product_info

    @staticmethod
    def check_client_exists(client_name: str):
        found_clients = []
        # clients_sheet = file_input['Clients']
        clients_sheet = None
        for sheet in file_input.sheetnames:
            if sheet == 'Clients':
                clients_sheet = file_input[sheet]
        if not clients_sheet:
            clients_sheet = file_input.create_sheet('Clients')
        client_name_parts = client_name.split()

        for row_number, row in enumerate(clients_sheet.iter_rows(values_only=True), start=1):
            full_name = ""
            if row[1] is not None and row[1] != "":
                full_name = row[1].strip()
                if row[2] is not None and row[2] != "":
                    full_name += " - " + row[2].strip()
            elif row[2] is not None and row[2] != "":
                full_name = row[2].strip()

            full_name_original = full_name

            full_name = full_name.strip().casefold()

            if all(part.casefold() in full_name for part in client_name_parts):
                found_clients.append((row_number, full_name_original, row))

        # print(found_clients)

        return found_clients

    @staticmethod
    def select_sales_client_popup(found_clients, sales_entry_window):
        client_options = [client[1] for client in found_clients[1:]]

        layout = [
            [sg.Text('Select a client:', font=('Helvetica', 12))],
            [sg.Listbox(values=client_options, size=(39, 6), key='-CLIENT-LIST-')],
            [sg.Button('Select Client', key='-OK-'), sg.Button('Add New', key='Add-Client'), sg.Button('Cancel')]
        ]
        popup_window = sg.Window('Select Client', layout, finalize=True, modal=True, resizable=True, keep_on_top=True)
        popup_window.maximize()

        while True:
            popup_event, popup_values = popup_window.read()
            if popup_event == sg.WINDOW_CLOSED or popup_event == 'Cancel':
                popup_window.close()
                return None
            elif popup_event == 'Add-Client':
                popup_window.close()
                sales_entry_window.hide()
                client_entry_window = ClientWindow.create_client_entry_window()
                client_entry_window['-Search-Name-'].update(visible=False)
                client_entry_window['-SEARCH-NAME-'].update(visible=False)
                client_entry_window['-NEXT-'].update(visible=False)
                client_entry_window['-Name-Label-'].update(visible=True)
                client_entry_window['-Institution-Label-'].update(visible=True)
                client_entry_window['-Phone-Label-'].update(visible=True)
                client_entry_window['-Email-Label-'].update(visible=True)
                client_entry_window['-Position-Label-'].update(visible=True)
                client_entry_window['-ID-Label-'].update(visible=True)

                client_entry_window['-NAME-'].update(disabled=False, visible=True)
                client_entry_window['-COMPANY-'].update(disabled=False, visible=True)
                client_entry_window['-PHONE-'].update(disabled=False, visible=True)
                client_entry_window['-EMAIL-'].update(disabled=False, visible=True)
                client_entry_window['-POSITION-'].update(disabled=False, visible=True)
                client_entry_window['-ID-'].update(disabled=False, visible=True)
                client_entry_window['Cancel'].update(visible=False)
                client_entry_window['EXIT'].update(visible=False)
                client_entry_window['Add'].update(visible=True)
                client_entry_window['Cancel'].update(visible=True)
                while True:
                    event, values = client_entry_window.read()
                    if event == sg.WINDOW_CLOSED or event == 'Cancel':
                        client_entry_window.close()
                        sales_entry_window.un_hide()
                        break
                    elif event == 'Add':
                        try:
                            phone_number = values['-PHONE-']
                            if phone_number:
                                phone_number = phone_number.lstrip('+0')
                                if phone_number.startswith('254'):
                                    phone_number = '254 ' + phone_number[3:]
                                elif not phone_number.startswith('254'):
                                    # Prepend '254' to the phone number
                                    phone_number = '254 ' + phone_number
                            if not AuthenticationManager.validate_email(values['-EMAIL-']) and values['-EMAIL-']:
                                sg.popup('Please enter a valid email address!', title='Error', keep_on_top=True)
                            else:
                                values['-PHONE-'] = phone_number
                                ClientWindow.save_client_to_excel(values)
                                sg.popup('New client saved successfully!', title='Success', keep_on_top=True)
                                client_entry_window.close()
                                sales_entry_window.un_hide()
                                sales_entry_window['-Name-'].update(value=values['-NAME-'])
                                break

                        except Exception as e:
                            sg.popup(f'An error occurred: {str(e)}', title='Error', keep_on_top=True)

            elif popup_event == '-OK-':
                if popup_values['-CLIENT-LIST-']:
                    selected_client_name = popup_values['-CLIENT-LIST-'][0]
                    selected_client_index = next(
                        (i for i, client in enumerate(found_clients) if client[1] == selected_client_name), None)

                    if selected_client_index is not None:
                        selected_client = found_clients[selected_client_index]
                        popup_window.close()
                        sales_entry_window['-Name-'].update(value=selected_client_name, disabled=True)
                        sales_entry_window['-Options-label-'].update(visible=True)
                        sales_entry_window['-Sell-'].update(visible=True)
                        sales_entry_window['-Take-back-'].update(visible=True)
                        sales_entry_window['EXIT1'].update(visible=False)
                        sales_entry_window['GET-NEXT'].update(visible=True)
                        sales_entry_window['EXIT2'].update(visible=True)
                        sales_entry_window['-Next-'].update(visible=False)
                        sales_entry_window['EMPTY'].update(visible=True)

                        invoice_numbers = 0
                        if invoice_numbers:
                            pass
                            return selected_client

                else:
                    sg.popup('Please select a client.', title='Error', keep_on_top=True)
                    continue
        popup_window.close()
        return None

    @staticmethod
    def show_invoice_numbers(selected_client, sales_entry_window, values):
        client_name = values['-Name-']
        # client_name = selected_client[1]

        invoice_details = {}
        # sales_sheet = file_input['Sales']
        sales_sheet = None
        for sheet in file_input.sheetnames:
            if sheet == 'Sales':
                sales_sheet = file_input[sheet]
        if not sales_sheet:
            sales_sheet = file_input.create_sheet('Sales')

        # Iterate over rows with index
        for row_idx, row in enumerate(sales_sheet.iter_rows(min_row=2, values_only=True), start=2):
            if row[3] == client_name:
                invoice_number = row[2]
                product = row[6]
                quantity = row[7]
                if invoice_number in invoice_details:
                    invoice_details[invoice_number].append((product, quantity))
                else:
                    invoice_details[invoice_number] = [(product, quantity)]

        invoice_list = [f'{invoice_number}: {", ".join([f"{prod} - {qty}" for prod, qty in products])}'
                        for invoice_number, products in invoice_details.items()]

        # Create layout for popup window
        layout = [
            [sg.Text(f'Invoice details for: {client_name}:')],
            [sg.Listbox(values=invoice_list, size=(60, 6), key='-INVOICE-DETAILS-')],
            [sg.Button('Add new', key='ADD-NEW'),
             sg.Button('Cancel', key='CANCEL')]
        ]

        # Display popup window
        popup_window = sg.Window('Invoice Numbers', layout, finalize=True, modal=True, resizable=True, keep_on_top=True)
        while True:
            popup_event, popup_values = popup_window.read()
            if popup_event == sg.WINDOW_CLOSED or popup_event == 'CANCEL':
                popup_window.close()
                break
            elif popup_event == 'SELECT-INVOICE':
                if popup_values['-INVOICE-DETAILS-']:
                    selected_invoice_detail = popup_values['-INVOICE-DETAILS-'][0]
                    selected_invoice_number = selected_invoice_detail.split(':')[0]
                    selected_products = invoice_details[selected_invoice_number]
                    popup_window.close()
                    sales_entry_window['-Options-label-'].update(visible=False)
                    sales_entry_window['-Sell-'].update(visible=False)
                    sales_entry_window['-Take-back-'].update(visible=False)
                    sales_entry_window['CUSTOMER'].update(visible=False)
                    sales_entry_window['-Name-'].update(visible=False)
                    sales_entry_window['-Next-'].update(visible=False)
                    sales_entry_window['GET-NEXT'].update(visible=False)
                    sales_entry_window['-Invoice-details-'].update(visible=True)
                    sales_entry_window['EXIT'].update(visible=False)
                    sales_entry_window['DETAILS'].update(
                        values=[f"{prod} - {qty} Quantity" if qty == 1 else f"{prod} - {qty} Quantities" for prod, qty
                                in selected_products], visible=True)
                    sales_entry_window['Invoice-date'].update(visible=True)
                    sales_entry_window['-Invoice-date-'].update(visible=True)
                    sales_entry_window['-REFRESH-DATE-'].update(visible=True)
                    sales_entry_window['-Customer-name'].update(visible=True)
                    sales_entry_window['-Customer-Name-'].update(value=client_name, visible=True)
                    sales_entry_window['Invoice-no'].update(visible=True)
                    sales_entry_window['-Invoice No-'].update(value=selected_invoice_number, visible=True)
                    sales_entry_window['-Book-label-'].update(visible=True)
                    sales_entry_window['-Book-'].update(visible=True)
                    sales_entry_window['-Qty-label-'].update(visible=True)
                    sales_entry_window['-Qty-'].update(visible=True)
                    sales_entry_window['-Price-label-'].update(visible=True)
                    sales_entry_window['-Price-'].update(visible=True)
                    sales_entry_window['-Category-label-'].update(visible=True)
                    sales_entry_window['-CATEGORY-'].update(visible=True)
                    sales_entry_window['-Accounts-label-'].update(visible=True)
                    sales_entry_window['-ACCOUNTS-'].update(visible=True)
                    sales_entry_window['-empty-'].update(visible=True)
                    sales_entry_window['-More-'].update(visible=True)
                    sales_entry_window['-Cancel-'].update(visible=True)
                else:
                    sg.popup('Please select an invoice.', title='Error', keep_on_top=True)
                    continue

            elif popup_event == 'ADD-NEW':
                sales_entry_window['-Options-label-'].update(visible=False)
                sales_entry_window['-Sell-'].update(visible=False)
                sales_entry_window['-Take-back-'].update(visible=False)
                sales_entry_window['GET-NEXT'].update(visible=False)
                sales_entry_window['CUSTOMER'].update(visible=False)
                sales_entry_window['-Name-'].update(visible=False)
                sales_entry_window['-Next-'].update(visible=False)
                sales_entry_window['EXIT2'].update(visible=False)
                sales_entry_window['Invoice-date'].update(visible=True)
                sales_entry_window['-Invoice-date-'].update(visible=True)
                sales_entry_window['-Customer-name'].update(visible=True)
                sales_entry_window['-Customer-Name-'].update(value=client_name, visible=True)
                sales_entry_window['Invoice-no'].update(visible=True)
                sales_entry_window['-Invoice No-'].update(visible=True, disabled=False)
                sales_entry_window['-Book-label-'].update(visible=True)
                sales_entry_window['-Book-'].update(visible=True)
                sales_entry_window['-Qty-label-'].update(visible=True)
                sales_entry_window['-Qty-'].update(visible=True)
                sales_entry_window['-Price-label-'].update(visible=True)
                sales_entry_window['-Price-'].update(visible=True)
                sales_entry_window['-Notes-label-'].update(visible=True)
                sales_entry_window['-Notes-'].update(visible=True)
                sales_entry_window['-Category-label-'].update(visible=True)
                sales_entry_window['-CATEGORY-'].update(visible=True)
                sales_entry_window['-Accounts-label-'].update(visible=True)
                sales_entry_window['-ACCOUNTS-'].update(visible=True)
                sales_entry_window['-Bank-Accounts-label-'].update(visible=True)
                sales_entry_window['-BANK-ACCOUNTS-'].update(visible=True)
                sales_entry_window['-empty-'].update(visible=True)
                sales_entry_window['-More-'].update(visible=True)
                sales_entry_window['-Cancel-'].update(visible=True)
                sales_entry_window['-REFRESH-DATE-'].update(visible=True)
                break

        # Close the popup window
        popup_window.close()

    @staticmethod
    def handle_selected_sales_client(found_clients, window):
        selected_client = SalesWindow.select_sales_client_popup(found_clients, window)

        if selected_client:
            client_details = selected_client[2]

            # Extract name from the full name
            client_name = client_details[1]
            institution_name = client_details[2]

            if client_name:
                full_name = client_name
            elif institution_name:
                full_name = institution_name.strip()
            else:
                full_name = ""
        # print(selected_client)

    @staticmethod
    def get_invoice_numbers(selected_client, values):
        # Extract client details
        client_name = values['-Name-']
        # client_name = selected_client[1]

        invoice_numbers = []
        # sales_sheet = file_input['Sales']
        sales_sheet = None
        for sheet in file_input.sheetnames:
            if sheet == 'Sales':
                sales_sheet = file_input[sheet]
        if not sales_sheet:
            sales_sheet = file_input.create_sheet('Sales')

        for row in sales_sheet.iter_rows(min_row=2, values_only=True):
            if row[3] == client_name:
                invoice_numbers.append(row[2])

        return invoice_numbers

    @staticmethod
    def add_product_popup():
        product_layout = [
            [sg.Text('Add more products to this invoice?')],
            [sg.Button('Yes'), sg.Button('No')]
        ]
        window = sg.Window('Add products', product_layout, modal=True, resizable=True, keep_on_top=True)
        event, _ = window.read()
        window.close()
        return event

    @staticmethod
    def save_sales_to_excel(values):
        try:
            sales_sheet = None
            for sheet in file_input.sheetnames:
                if sheet == 'Sales':
                    sales_sheet = file_input[sheet]
            if not sales_sheet:
                sales_sheet = file_input.create_sheet('Sales')

            # Find the next empty row
            next_row = sales_sheet.max_row + 1

            last_sales_number = None
            if next_row > 1:
                last_sales_number = sales_sheet.cell(row=next_row - 1, column=1).value

            # Increment the last sales number by one or start from 1 if there's no previous number
            if last_sales_number:
                sales_number = int(last_sales_number) + 1
            else:
                sales_number = 1

            quantity = 0

            if values['-Take-back-']:
                quantity = -1 * int(values['-Qty-'])
            elif values['-Sell-']:
                quantity = int(values['-Qty-'])

            total = round(quantity * float(values['-Price-']), 2)

            invoice_totals = {}
            for row in sales_sheet.iter_rows(min_row=3, values_only=True):
                invoice_nos = row[2]
                amount = row[9]
                if invoice_nos in invoice_totals:
                    invoice_totals[invoice_nos] += float(amount)
                else:
                    invoice_totals[invoice_nos] = float(amount)

            invoice_no = HomeWindow.get_next_invoice_number()
            invoice_number = values['-Invoice No-']
            # Write data to the next empty row
            sanitized_values = {key: sanitize_and_strip(value) for key, value in values.items()}
            sales_sheet.cell(row=next_row, column=1, value=sales_number)
            sales_sheet.cell(row=next_row, column=2, value=values['-Invoice-date-'])
            sales_sheet.cell(row=next_row, column=3, value=values['-Invoice No-'])
            sales_sheet.cell(row=next_row, column=4, value=values['-Customer-Name-'])
            sales_sheet.cell(row=next_row, column=7, value=values['-Book-'])
            sales_sheet.cell(row=next_row, column=8, value=quantity)  #
            sales_sheet.cell(row=next_row, column=9, value=float(sanitized_values['-Price-']))
            sales_sheet.cell(row=next_row, column=10, value=total)
            sales_sheet.cell(row=next_row, column=12, value=total)
            sales_sheet.cell(row=next_row, column=13, value=current_date_time)
            sales_sheet.cell(row=next_row, column=14, value=sanitized_values['-CATEGORY-'])
            sales_sheet.cell(row=next_row, column=15, value=sanitized_values['-ACCOUNTS-'])
            sales_sheet.cell(row=next_row, column=16, value=invoice_no)
            sales_sheet.cell(row=next_row, column=17, value=status)

            # Calculate total amount for the specific invoice number
            total_invoice_amount = sum(
                row[9] for row in sales_sheet.iter_rows(min_row=3, values_only=True) if row[2] == invoice_number)
            sales_sheet.cell(row=next_row, column=18, value=total_invoice_amount)
            sales_sheet.cell(row=next_row, column=19, value=not_paid)
            sales_sheet.cell(row=next_row, column=20, value=values['-Notes-'])
            sales_sheet.cell(row=next_row, column=21, value=values['-BANK-ACCOUNTS-'])

            # Fetch and update the 'Stocks' sheet
            stocks_sheet = None
            for sheet in file_input.sheetnames:
                if sheet == 'Stocks':
                    stocks_sheet = file_input[sheet]
            if not stocks_sheet:
                stocks_sheet = file_input.create_sheet('Stocks')

            product_name = values['-Book-']

            products_sheet = None
            for sheet in file_input.sheetnames:
                if sheet == 'Products':
                    products_sheet = file_input[sheet]
            if not products_sheet:
                products_sheet = file_input.create_sheet('Products')

            # Retrieve the unique_identifier from the 'Products' sheet
            unique_identifier = None
            for row in products_sheet.iter_rows(min_row=2, values_only=True):
                combined_name = f"{row[1]} - {row[2]}"
                if combined_name == product_name:
                    unique_identifier = row[3]
                    break

            stock_found = False
            for idx, row in enumerate(stocks_sheet.iter_rows(min_row=2, values_only=True), start=2):
                if row[2] == unique_identifier:
                    stock_found = True
                    current_total_office = row[4]
                    new_total_office = current_total_office - quantity
                    if new_total_office < 5:
                        sg.popup(f"Product '{product_name}' is almost over. Remaining {new_total_office}", keep_on_top=True)
                    if new_total_office == 0:
                        sg.popup_error(f"Product '{product_name}' not available in the shop", keep_on_top=True)
                        return
                    # Update the stock sheet
                    stocks_sheet.cell(row=idx, column=5, value=new_total_office)
                    break

            stores_sheet = None
            for sheet in file_input.sheetnames:
                if sheet == 'Stores':
                    stores_sheet = file_input[sheet]
            if not stores_sheet:
                stores_sheet = file_input.create_sheet('Stores')
            next_store_row = stores_sheet.max_row + 1

            stores_sheet.cell(row=next_store_row, column=2, value=current_date_time)
            stores_sheet.cell(row=next_store_row, column=3, value=values['-Customer-Name-'])
            stores_sheet.cell(row=next_store_row, column=5, value=values['-Book-'])
            stores_sheet.cell(row=next_store_row, column=7, value=-quantity)
            stores_sheet.cell(row=next_store_row, column=10, value=unique_identifier)
            if unique_identifier is None:
                print("Product not found in 'Stocks' sheet. No update was made.")
            else:
                file_input.save("publishing.xlsx")
                sg.popup('Sales saved successfully!', title='Success', keep_on_top=True)
                print(f"Sales data saved and stock updated for product: {product_name}")

            # Fetch the "Invoices" sheet
            invoices_sheet = file_input['Invoices']

            invoice_numbers = [cell.value for cell in invoices_sheet['B']]
            if invoice_number not in invoice_numbers:
                next_row_invoices = invoices_sheet.max_row + 1

                invoices_sheet.cell(row=next_row_invoices, column=2, value=invoice_number)

            file_input.save("publishing.xlsx")
            customer_name = values['-Customer-Name-']
            notes = values['-Notes-']
            invoice_no = invoice_number
            invoice_date = current_date_time
            items = []
            total_amount = 0

            for row in sales_sheet.iter_rows(min_row=2, values_only=True):
                if row[2] == invoice_no:
                    book = row[6]
                    quantity = row[7]
                    price = row[8]
                    total = round(quantity * price, 2)
                    items.append(
                        {'description': book, 'quantity': quantity, 'unit_price': price, 'total': total})
                    total_amount += total

            invoice_data = {
                'customer_name': customer_name,
                'invoice_number': invoice_no,
                'invoice_date': invoice_date,
                'items': items,
                'total_amount': sum(entry['total'] for entry in items),
                'notes': notes
            }
            sanitized_invoice_no = re.sub(r'\W', '_', invoice_no)  # Replace non-word characters with underscores

            os.makedirs("invoices", exist_ok=True)
            # category = "invoices"
            # filename = os.path.join("invoices", f"invoice_{sanitized_invoice_no}.pdf")
            filename = f"invoice_{sanitized_invoice_no}.pdf"
            SalesWindow.create_invoice(invoice_data, os.path.join("invoices", filename))
            MainWindow.show_download_popup("invoices", filename)

        except Exception as e:
            sg.popup_error(f"An error occurred while saving sales data: {str(e)}", keep_on_top=True)
            print(f"An error occurred while saving sales data: {str(e)}")

    @staticmethod
    def create_invoice(invoice_data, filename):

        # Create a canvas
        c = canvas.Canvas(filename, pagesize=letter)

        # Set up styles
        styles = getSampleStyleSheet()
        style_normal = styles["Normal"]

        # Add company logo as the letterhead
        logo_path = 'teknobyte-tagline.jpg'
        logo_width = 2 * inch
        logo_height = 0.5 * inch
        logo_x = 430
        logo_y = 750
        c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

        # # Add company information
        address = "Brightwoods Apartment, Chania Ave "
        city_state_zip = "PO. Box 74080-00200, Nairobi, KENYA "
        phone = "Phone: +254-705917383"
        email = "Email: info@teknobyte.ltd"
        kra_pin = "PIN: P051155522R"
        c.setFont("Helvetica", 8)
        c.drawString(430, 740, "")
        c.drawString(430, 730, address)
        c.drawString(430, 720, city_state_zip)
        c.drawString(430, 710, phone)
        c.drawString(430, 700, email)
        c.drawString(430, 690, kra_pin)
        c.drawString(430, 660, "")
        # Add invoice details
        c.setFont("Helvetica-Bold", 20)
        c.drawString(280, 640, "Invoice")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 620, "")

        c.drawString(50, 600, f"Date:            {invoice_data['invoice_date']}")
        invoice_label = "Invoice No:"
        invoice_number = invoice_data['invoice_number']
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 580, invoice_label)
        label_width = c.stringWidth(invoice_label, "Helvetica-Bold", 12)

        # Draw the client name in regular font next to the label
        c.setFont("Helvetica", 12)
        c.drawString(50 + label_width + 5, 580, invoice_number)

        # c.drawString(50, 610, f"Invoice Number: {invoice_data['invoice_number']}")
        c.drawString(50, 560, "")
        client_label = "Client:"
        client_name = invoice_data['customer_name']

        # Draw the bold label
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 540, client_label)

        # Calculate the width of the label text to position the client name
        label_width = c.stringWidth(client_label, "Helvetica-Bold", 12)

        # Draw the client name in regular font next to the label
        c.setFont("Helvetica", 12)
        c.drawString(50 + label_width + 5, 540, client_name)
        # c.drawString(50, 540, f"Client Name: {invoice_data['customer_name']}")
        # Add space
        # c.drawString(50, 520, "")

        # Add line items table
        data = [['Description', 'Quantity', 'Unit Price', 'Total']]
        for item in invoice_data['items']:
            data.append([item['description'], item['quantity'], item['unit_price'], item['total']])

        # Set the width of each column
        col_widths = [3 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]  # Adjust widths as needed
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

        table_height = len(data) * 20
        t.wrapOn(c, 0, 0)
        t.drawOn(c, 50, 500 - table_height)

        # Add total amount
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, 480 - table_height, f"Total Amount: {invoice_data['total_amount']}")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 360, "NOTES")
        notes_style = ParagraphStyle(
            'NotesStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT
        )
        notes = Paragraph(invoice_data['notes'].replace('\n', '<br/>'), notes_style)
        w, h = notes.wrap(400, 100)  # Wrap the text within 400 units width
        notes.drawOn(c, 50, 340 - h)
        # c.setFont("Helvetica", 12)
        # c.drawString(50, 340, f"{invoice_data['notes']}")
        c.setFont("Helvetica", 12)
        c.drawString(50, 200, "John Kungu")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 180, "ACCOUNTANT")

        # Save the PDF
        c.save()
        # # Create a backup file with a timestamp
        timestamp = datetime.now().strftime("%d%m%Y")
        backup_filename = f"{filename}_{timestamp}.pdf"
        shutil.copyfile(filename, backup_filename)
        print(f"Backup of {filename} created as {backup_filename}")

    @staticmethod
    def save_sales_acc_to_excel(values):
        try:
            sales_account_sheet = None
            for sheet in file_input.sheetnames:
                if sheet == 'SalesAcc':
                    sales_account_sheet = file_input[sheet]
            if not sales_account_sheet:
                sales_account_sheet = file_input.create_sheet('SalesAcc')

            # Find the next empty row
            next_row = sales_account_sheet.max_row + 1

            last_sales_acc_number = None
            if next_row > 1:
                last_sales_acc_number = sales_account_sheet.cell(row=next_row - 1, column=1).value

            # Increment the last sales number by one or start from 1 if there's no previous number
            if last_sales_acc_number:
                sales_acc_number = int(last_sales_acc_number) + 1
            else:
                sales_acc_number = 1

            quantity = 0

            if values['-Take-back-']:
                quantity = -1 * int(values['-Qty-'])
            elif values['-Sell-']:
                quantity = int(values['-Qty-'])

            total = round(quantity * float(values['-Price-']), 2)

            invoice_number = values['-Invoice No-']

            sanitized_values = {key: sanitize_and_strip(value) for key, value in values.items()}

            # Write data to the next empty row
            sales_account_sheet.cell(row=next_row, column=1, value=sales_acc_number)
            sales_account_sheet.cell(row=next_row, column=2, value=values['-Invoice-date-'])
            sales_account_sheet.cell(row=next_row, column=3, value=invoice_number)
            sales_account_sheet.cell(row=next_row, column=4, value=values['-Customer-Name-'])
            sales_account_sheet.cell(row=next_row, column=7, value=values['-Book-'])
            sales_account_sheet.cell(row=next_row, column=8, value=quantity)
            sales_account_sheet.cell(row=next_row, column=9, value=float(sanitized_values['-Price-']))
            sales_account_sheet.cell(row=next_row, column=10, value=total)
            sales_account_sheet.cell(row=next_row, column=12, value=total)
            sales_account_sheet.cell(row=next_row, column=13, value=current_date_time)
            sales_account_sheet.cell(row=next_row, column=14, value=sanitized_values['-CATEGORY-'])
            sales_account_sheet.cell(row=next_row, column=15, value=sanitized_values['-ACCOUNTS-'])
            sales_account_sheet.cell(row=next_row, column=16, value=sanitized_values['-Frequency-'])
            sales_account_sheet.cell(row=next_row, column=17, value=status)
            sales_account_sheet.cell(row=next_row, column=20, value=values['-Notes-'])
            sales_account_sheet.cell(row=next_row, column=21, value=values['-BANK-ACCOUNTS-'])

            # Fetch the "Invoices" sheet
            invoices_sheet = file_input['Invoices']

            invoice_numbers = [cell.value for cell in invoices_sheet['B']]
            if invoice_number not in invoice_numbers:
                next_row_invoices = invoices_sheet.max_row + 1

                invoices_sheet.cell(row=next_row_invoices, column=2, value=invoice_number)

            file_input.save("publishing.xlsx")
            customer_name = values['-Customer-Name-']
            notes = values['-Notes-']
            invoice_number = values['-Invoice No-']
            invoice_date = current_date_time
            items = []
            total_amount = 0

            for row in sales_account_sheet.iter_rows(min_row=2, values_only=True):
                if row[2] == invoice_number:
                    book = row[6]
                    quantity = row[7]
                    price = row[8]
                    total = round(quantity * price, 2)
                    items.append(
                        {'description': book, 'quantity': quantity, 'unit_price': price,
                         'total': total})
                    total_amount += total

            invoice_data = {
                'customer_name': customer_name,
                'invoice_number': invoice_number,
                'invoice_date': invoice_date,
                'items': items,
                'total_amount': sum(entry['total'] for entry in items),
                'notes': notes
            }
            sanitized_invoice_no = re.sub(r'\W', '_',
                                          invoice_number)  # Replace non-word characters with underscores

            os.makedirs("invoices", exist_ok=True)
            filename = os.path.join("invoices", f"invoice_{sanitized_invoice_no}.pdf")
            SalesWindow.create_invoice(invoice_data, filename)
        except Exception as e:
            sg.popup_error(f"An error occurred while saving sales accounts data: {str(e)}", keep_on_top=True)

    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import PySimpleGUI as sg

    @staticmethod
    def create_next_due_sale(values):
        try:
            product_name = values['-Book-']
            # billing_date_str = values['-Invoice-date-']
            sales_accounts_sheet = file_input['SalesAcc']
            sales_sheet = file_input['Sales']
            sales_list_sheet = file_input['SalesList']
            invoices_sheet = file_input['Invoices']

            # Check if the account exists and retrieve details
            sales_account_found = False
            billing_frequency = None
            sales_account_invoice = None
            qty = None
            price = None
            billing_date_str = None

            for row in sales_accounts_sheet.iter_rows(min_row=2, values_only=True):
                if len(row) <= 20:
                    continue
                if row[6] == product_name and row[16] == "Active":
                    sales_account_found = True
                    billing_frequency = row[15]
                    billing_date_str = row[1]
                    sales_account_invoice = row[2]
                    qty = row[7]
                    price = row[8]
                    break

            if not sales_account_found:
                print("Sales Account not found.")
                return

            # Helper function to check if a bill already exists and its status
            def invoice_exists(invoice_date):
                for row in sales_list_sheet.iter_rows(min_row=2, values_only=True):
                    if len(row) <= 10:
                        continue
                    if row[10] == sales_account_invoice and row[2] == invoice_date.strftime('%d/%m/%Y'):
                        print(f"Sale for {invoice_date.strftime('%d/%m/%Y')} exists with status {row[7]}.")
                        return row[7]
                return None

            def create_sale(invoice_date):
                existing_sale_status = invoice_exists(invoice_date)
                if existing_sale_status is None:
                    next_row = sales_sheet.max_row + 1
                    sales_number = next_row if next_row > 1 else 1
                    invoice_no = HomeWindow.get_next_invoice_number()

                    total = round(int(qty) * float(price), 2)
                    sanitized_values = {key: sanitize_and_strip(value) for key, value in values.items()}

                    # Create the new bill entry
                    sales_sheet.cell(row=next_row, column=1, value=sales_number)
                    sales_sheet.cell(row=next_row, column=2, value=invoice_date.strftime('%d/%m/%Y'))
                    sales_sheet.cell(row=next_row, column=3, value=invoice_no)
                    sales_sheet.cell(row=next_row, column=4, value=values['-Customer-Name-'])
                    sales_sheet.cell(row=next_row, column=7, value=values['-Book-'])
                    sales_sheet.cell(row=next_row, column=8, value=qty)
                    sales_sheet.cell(row=next_row, column=9, value=price)
                    sales_sheet.cell(row=next_row, column=10, value=total)
                    sales_sheet.cell(row=next_row, column=12, value=total)
                    sales_sheet.cell(row=next_row, column=13, value=current_date_time)
                    sales_sheet.cell(row=next_row, column=14, value=sanitized_values.get('-CATEGORY-', ""))
                    sales_sheet.cell(row=next_row, column=15, value=sanitized_values.get('-ACCOUNTS-', ""))
                    sales_sheet.cell(row=next_row, column=16, value=sales_account_invoice)
                    sales_sheet.cell(row=next_row, column=17, value=status)
                    sales_sheet.cell(row=next_row, column=20, value=values.get('-Notes-', ""))
                    sales_sheet.cell(row=next_row, column=21, value=values['-BANK-ACCOUNTS-'])

                    next_row_invoices = invoices_sheet.max_row + 1
                    invoices_sheet.cell(row=next_row_invoices, column=2, value=invoice_no)
                    file_input.save("publishing.xlsx")
                    ReceiptsWindow.generate_sales_list()
                    print(f"Sale created for {invoice_date.strftime('%d/%m/%Y')}")
                else:
                    print(
                        f"Skipping sale creation for {invoice_date.strftime('%d/%m/%Y')} as it already exists with status {existing_sale_status}.")

            # Create the bill for the given billing date
            billing_date = datetime.strptime(billing_date_str, '%d/%m/%Y')
            create_sale(billing_date)

            # Generate all due bills until today
            next_due_date = billing_date
            today_date = datetime.now()
            print(f"Today date: {today_date.strftime('%d/%m/%Y')}")

            while next_due_date <= today_date:
                if billing_frequency == 'Monthly':
                    next_due_date += relativedelta(months=1)
                elif billing_frequency == 'Quarterly':
                    next_due_date += relativedelta(months=3)
                elif billing_frequency == 'Annual':
                    next_due_date += relativedelta(years=1)
                elif billing_frequency == 'Occasional':
                    break  # Handle occasional case as needed

                print(f"Creating sale for next due date: {next_due_date.strftime('%d/%m/%Y')}")
                create_sale(next_due_date)

            for row in sales_list_sheet.iter_rows(min_row=2, values_only=True):
                if row[10] == sales_account_invoice and row[6] == "Paid" and row[7] == "Active":
                    last_billing_date = datetime.strptime(row[2], '%d/%m/%Y')
                    next_due_date = last_billing_date

                    if billing_frequency == 'Monthly':
                        next_due_date += relativedelta(months=1)
                    elif billing_frequency == 'Quarterly':
                        next_due_date += relativedelta(months=3)
                    elif billing_frequency == 'Annual':
                        next_due_date += relativedelta(years=1)
                    elif billing_frequency == 'Occasional':
                        break  # Handle occasional case as needed

                    print(f"Creating next due sale for paid invoice date: {next_due_date.strftime('%d/%m/%Y')}")
                    create_sale(next_due_date)

        except Exception as e:
            sg.popup_error(f"An error occurred while creating the next due sale: {str(e)}", keep_on_top=True)