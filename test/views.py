import csv
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from process.models import Contract, Product, NonFinancedCharge, ContractNonFinancedCharge, NonStandardCashflow, \
    ContractNonStandardCashflow
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import logging



def upload_csv(request, product_id):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        logging.debug(f"Product id = {product_id}")

        if product_id == 1:
            contract = parse_csv_and_create_contract_hp1(csv_file)
        elif product_id == 2:
            contract = parse_csv_and_create_contract_hp2(csv_file)
        elif product_id == 3:
            contract = parse_csv_and_create_contract_fl1(csv_file)
        else:
            return HttpResponse("Unknown product type")

        return redirect(reverse('process:contract_detail', args=[contract.id]))
    return render(request, 'process/upload_csv.html')

def parse_csv_and_create_contract_hp1(csv_file):
    reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
    for row in reader:
        contract_id = row['Contract id']
        product_id = row['Product id']
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
        product = Product.objects.get(id=1)
        contract = Contract.objects.create(
            contract_id=contract_id,
            product=product,
            term=term,
            start_date=start_date,
            due_day=due_day,
            interest_rate=interest_rate,
            amount_financed=amount_financed
        )
        return contract


def parse_csv_and_create_contract_hp2(csv_file):
    reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
    for row in reader:
        contract_id = row['Contract id']
        product_id = row['Product id']
        term = int(row['Term'])
        start_date_str = row['Start date']
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        due_day = int(row['Due day'])
        interest_rate = float(row['Interest rate'])
        amount_financed = float(row['Amount financed'])
        balloon = float(row['Balloon'])
        non_financed_charge_name = "Balloon"
        non_financed_charge, _ = NonFinancedCharge.objects.get_or_create(name=non_financed_charge_name)
        product = Product.objects.get(id=2)
        contract = Contract.objects.create(
            contract_id=contract_id,
            product=product,
            term=term,
            start_date=start_date,
            due_day=due_day,
            interest_rate=interest_rate,
            amount_financed=amount_financed
        )
        ContractNonFinancedCharge.objects.create(
            contract=contract,
            non_financed_charge=non_financed_charge,
            amount=balloon
        )
        return contract


def parse_csv_and_create_contract_fl1(csv_file):
    reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
    for row in reader:
        contract_id = row['Contract id']
        product_id = row['Product id']
        term = int(row['Term'])
        start_date_str = row['Start date']
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        due_day = int(row['Due day'])
        interest_rate = float(row['Interest rate'])
        amount_financed = float(row['Amount financed'])
        document_fee = float(row['Document fee'])
        rv = float(row['RV'])
        non_financed_charge_name = "Document fee"
        non_standard_cash_flow_name = "RV"
        non_financed_charge, _ = NonFinancedCharge.objects.get_or_create(name=non_financed_charge_name)
        non_standard_cash_flow, _ = NonStandardCashflow.objects.get_or_create(name=non_standard_cash_flow_name)
        product = Product.objects.get(id=3)
        contract = Contract.objects.create(
            contract_id=contract_id,
            product=product,
            term=term,
            start_date=start_date,
            due_day=due_day,
            interest_rate=interest_rate,
            amount_financed=amount_financed
        )

        ContractNonStandardCashflow.objects.create(
            contract=contract,
            non_standard_cashflow=non_standard_cash_flow,
            amount=rv
        )
        ContractNonFinancedCharge.objects.create(
            contract=contract,
            non_financed_charge=non_financed_charge,
            amount=document_fee
        )
        return contract

def calculate_monthly_instalment(initial_capital, interest_rate, term, document_fee=None, rv=None):
    monthly_instalment = Decimal("0")
    result_empty_table = 0
    result_random_monthly_instalment = 0

    capital = initial_capital
    for month in range(1, term + 1):
        add_interest = capital * interest_rate
        capital += add_interest
        if month == term:
            monthly_instalment = rv if rv is not None else monthly_instalment
        capital -= monthly_instalment
        result_empty_table = capital

    monthly_instalment = initial_capital / term

    capital = initial_capital
    for month in range(1, term + 1):
        add_interest = capital * interest_rate
        capital_before = capital
        capital += add_interest
        if month == term:
            monthly_instalment = rv if rv is not None else monthly_instalment
        capital -= monthly_instalment
        result_random_monthly_instalment = capital

    instalment_value = (result_empty_table * (initial_capital / term)) / (
                result_empty_table - result_random_monthly_instalment)

    monthly_instalment = instalment_value
    return monthly_instalment


def contract_process_on_screen(request, contract_id):
    contract = Contract.objects.get(id=contract_id)

    interest_rate = Decimal(-1 + (1 + float(contract.interest_rate)) ** (1/12))
    start_date = contract.start_date
    contract_id = contract.contract_id
    initial_capital = contract.amount_financed
    term = contract.term
    due_day = contract.due_day

    results = []

    if contract.product.id == 2:
        balloon = contract.contractnonfinancedcharge_set.first().amount
        monthly_instalment = calculate_monthly_instalment(initial_capital, interest_rate, term, rv=balloon)

    elif contract.product.id == 1:
        monthly_instalment = calculate_monthly_instalment(initial_capital, interest_rate, term)

    elif contract.product.id == 3:
        document_fee = contract.contractnonfinancedcharge_set.first().amount
        rv = contract.contractnonstandardcashflow_set.first().amount
        monthly_instalment = calculate_monthly_instalment(initial_capital, interest_rate, term, document_fee=document_fee, rv=rv)
    else:
        return HttpResponse("Can't recognise the product")

    capital = initial_capital
    current_date = start_date

    for month in range(1, term + 1):
        add_interest = capital * interest_rate
        capital_before = capital
        capital += add_interest
        if month == term:
            monthly_instalment = balloon if 'balloon' in locals() else rv if 'rv' in locals() else monthly_instalment
        capital -= monthly_instalment

        current_date = start_date + relativedelta(months=month)

        results.append({
            'contract_id': contract_id,
            'start_date': current_date.strftime(f'%d/%m/%y'),
            'due_day': current_date.replace(day=due_day).strftime('%d/%m/%y'),
            'month': month,
            'initial_capital': f"{capital_before:,.2f}",
            'add_interest': f"{add_interest:,.2f}",
            'monthly_instalment': f"{(monthly_instalment + document_fee) if contract.product.id == 3 and month == 1 else monthly_instalment:.2f}",
            'capital_after': f"{capital:,.2f}"
        })

    context = {
        'contract': contract,
        'results': results
    }

    return render(request, 'process/contract_process.html', context)


def contract_process_download(request, contract_id):
    contract = Contract.objects.get(id=contract_id)

    interest_rate = Decimal(-1 + (1 + float(contract.interest_rate)) ** (1/12))
    start_date = contract.start_date
    contract_id = contract.contract_id
    initial_capital = contract.amount_financed
    term = contract.term
    due_day = contract.due_day

    results = []

    if contract.product.id == 2:
        balloon = contract.contractnonfinancedcharge_set.first().amount
        monthly_instalment = calculate_monthly_instalment(initial_capital, interest_rate, term, rv=balloon)

    elif contract.product.id == 1:
        monthly_instalment = calculate_monthly_instalment(initial_capital, interest_rate, term)

    elif contract.product.id == 3:
        document_fee = contract.contractnonfinancedcharge_set.first().amount
        rv = contract.contractnonstandardcashflow_set.first().amount
        monthly_instalment = calculate_monthly_instalment(initial_capital, interest_rate, term, document_fee=document_fee, rv=rv)
    else:
        return HttpResponse("Can't recognise the product")

    capital = initial_capital
    current_date = start_date

    for month in range(1, term + 1):
        add_interest = capital * interest_rate
        capital_before = capital
        capital += add_interest
        if month == term:
            monthly_instalment = balloon if 'balloon' in locals() else rv if 'rv' in locals() else monthly_instalment
        capital -= monthly_instalment

        current_date = start_date + relativedelta(months=month)

        results.append({
            'Contract ID': contract_id,
            'Start Date': current_date.strftime(f'%d/%m/%y'),
            'Due Day': current_date.replace(day=due_day).strftime('%d/%m/%y'),
            'Month#': month,
            'Initial Capital': f"{capital_before:,.2f}",
            'Add Interest': f"{add_interest:,.2f}",
            'Monthly Instalment': f"{(monthly_instalment + document_fee) if contract.product.id == 3 and month == 1 else monthly_instalment:.2f}",
            'Capital After': f"{capital:,.2f}"
        })
    filename = f"contract_{contract_id}_{current_date.strftime('%Y-%m-%d')}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    fieldnames = ['Contract ID', 'Start Date', 'Due Day', 'Month#', 'Initial Capital', 'Add Interest',
                      'Monthly Instalment', 'Capital After']

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for result in results:
        writer.writerow(result)

    return response
