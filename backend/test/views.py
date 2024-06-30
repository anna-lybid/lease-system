
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


def perform_calculation_on_screen(request, contract_id):
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
