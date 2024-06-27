import csv
from datetime import datetime
import io


def parse_csv(csv_file):
    text_file = io.TextIOWrapper(csv_file, encoding='utf-8')
    reader = csv.DictReader(text_file)

    for row in reader:
        contract_id = row['Contract id']
        product_inner_id = row['Product id']
        term = int(row['Term'])
        start_date_str = row['Start date']
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        due_day = int(row['Due day'])
        if '%' in row['Interest rate']:
            percentage_string = row['Interest rate']
            cleaned_string = percentage_string.replace('%', '')
            interest_rate = float(cleaned_string)
        else:
            interest_rate = float(row['Interest rate'])
        if ',' in row['Amount financed']:
            amount_financed_string = row['Amount financed']
            amount_financed = float(amount_financed_string.replace(',', ''))
        else:
            amount_financed = float(row['Amount financed'])

        contract_data = {
            "contract_id": contract_id,
            "product_inner_id": product_inner_id,
            "term": term,
            "start_date": start_date,
            "due_day": due_day,
            "interest_rate": interest_rate,
            "amount_financed": amount_financed,
            "balloon": float(row["Balloon"]) if "Balloon" in row else None,
            "rv": float(row["RV"]) if "RV" in row else None,
            "fee":float(row['Document fee']) if "Document fee" in row else None,
        }
        return contract_data