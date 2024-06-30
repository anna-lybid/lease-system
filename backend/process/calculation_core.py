import csv
from datetime import datetime
import io
from decimal import Decimal

from dateutil.relativedelta import relativedelta


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


def calculate_monthly_installment(contract):
    term = contract.term
    capital = contract.amount_financed
    interest_rate = Decimal(-1 + (1 + float(contract.interest_rate)) ** (1 / 12))
    monthly_installment = Decimal("0")


    if contract.non_standard_cashflows.exists():
        rv = contract.non_standard_cashflows.first().amount
        balloon = contract.non_standard_cashflows.first().amount
    else:
        rv = None
        balloon = None

    for month in range(1, term+1):
        add_interest = capital * interest_rate
        capital_before = capital
        capital += add_interest

        if month == term:
            monthly_installment = balloon if balloon else monthly_installment
            monthly_installment = rv if rv else monthly_installment
        capital -= monthly_installment


    end_capital_when_monthly_installment_is_None = capital



    suggested_monthly_installment = Decimal("1041.67") ###
    monthly_installment = suggested_monthly_installment
    capital = contract.amount_financed

    if contract.non_standard_cashflows.exists():
        rv = contract.non_standard_cashflows.first().amount
        balloon = contract.non_standard_cashflows.first().amount
    else:
        rv = None
        balloon = None

    for month in range(1, term + 1):
        add_interest = capital * interest_rate
        capital_before = capital
        capital += add_interest

        if month == term:
            monthly_installment = balloon if balloon else monthly_installment
            monthly_installment = rv if rv else monthly_installment
        capital -= monthly_installment

    end_capital_when_monthly_installment_is_suggested = capital

    monthly_installment = (end_capital_when_monthly_installment_is_None * suggested_monthly_installment) / (end_capital_when_monthly_installment_is_None - end_capital_when_monthly_installment_is_suggested)

    return monthly_installment


def perform_calculation_on_screen(contract):
    interest_rate = Decimal(-1 + (1 + float(contract.interest_rate)) ** (1 / 12))
    start_date = contract.start_date
    contract_id = contract.contract_inner_id
    initial_capital = contract.amount_financed
    term = contract.term
    due_day = contract.due_day
    fee = 0

    if contract.non_standard_cashflows.exists():
        rv = contract.non_standard_cashflows.first().amount
        balloon = contract.non_standard_cashflows.first().amount
    else:
        rv = None
        balloon = None

    if contract.non_financed_charges.exists():
        fee = contract.non_financed_charges.first().amount

    results = []

    monthly_installment = calculate_monthly_installment(contract)
    capital = initial_capital
    current_date = start_date

    for month in range(1, term+1):
        add_interest = capital * interest_rate
        capital_before = capital
        capital += add_interest
        if month == term:
            monthly_installment = balloon if balloon else monthly_installment
            monthly_installment = rv if rv else monthly_installment
        capital -= monthly_installment

        current_date = start_date + relativedelta(months=+month)

        results.append({
            'contract_id': contract_id,
            'start_date': current_date.strftime(f'%d/%m/%y'),
            'due_day': current_date.replace(day=due_day).strftime('%d/%m/%y'),
            'month': month,
            'initial_capital': f"{capital_before:,.2f}",
            'add_interest': f"{add_interest:,.2f}",
            'monthly_installment': f"{(monthly_installment + fee):.2f}" if month == 1 else f"{monthly_installment:.2f}",
            'capital_after': f"{capital:,.2f}"
        })
    return results
