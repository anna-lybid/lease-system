from django.db import models


class NonFinancedCharge(models.Model):
    name = models.CharField(max_length=100)
    pay_date = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class NonStandardCashflow(models.Model):
    name = models.CharField(max_length=100)
    pay_date = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Goal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, blank=True, null=True)
    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.CharField(max_length=100, blank=True, null=True)
    interest_rate_type = models.CharField(max_length=100)
    has_subsidy = models.BooleanField(default=False)
    in_advance_or_arrears = models.CharField(max_length=100, default="arrears")
    term_type = models.CharField(max_length=100)
    include_start_day = models.BooleanField(default=False)
    include_due_day = models.BooleanField(default=False)
    if_due_date_is_month_end = models.BooleanField(default=False)
    non_financed_charge = models.ManyToManyField(NonFinancedCharge, blank=True)
    non_standard_cashflows = models.ManyToManyField(NonStandardCashflow, blank=True)
    include_accounting_schedules = models.BooleanField(default=False)
    accounting_treatment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.product_id


class HP01(Product):
    term = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    due_day = models.IntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=6)
    amount_financed = models.DecimalField(max_digits=12, decimal_places=2)
    subsidy = models.BooleanField(default=False)


class HP02(Product):
    term = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_day = models.IntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=6,null=True, blank=True)
    amount_financed = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    subsidy = models.BooleanField(default=False)
    non_financed_charge_relation = models.ManyToManyField(NonFinancedCharge, through='HP02NonFinancedCharge', blank=True, related_name='hp02_non_financed_charges')


class FL01(Product):
    term = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    due_day = models.IntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=6)
    amount_financed = models.DecimalField(max_digits=12, decimal_places=2)
    subsidy = models.BooleanField(default=False)
    non_financed_charge_relation = models.ForeignKey(NonFinancedCharge, on_delete=models.CASCADE)
    non_standard_cashflows_relation = models.ForeignKey(NonStandardCashflow, on_delete=models.CASCADE)


class ContractNonFinancedCharge(models.Model):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
    non_financed_charge = models.ForeignKey(NonFinancedCharge, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)


class ContractNonStandardCashflow(models.Model):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
    non_standard_cashflow = models.ForeignKey(NonStandardCashflow, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class Contract(models.Model):
    contract_id = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    term = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    due_day = models.IntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=6)
    amount_financed = models.DecimalField(max_digits=12, decimal_places=2)
    subsidy = models.BooleanField(default=False)
    non_financed_charge_links = models.ManyToManyField(NonFinancedCharge, through='ContractNonFinancedCharge')
    non_standard_cashflow_links = models.ManyToManyField(NonStandardCashflow, through='ContractNonStandardCashflow')

    def __str__(self):
        return str(self.product.product_id)


class HP02NonFinancedCharge(models.Model):
    hp02 = models.ForeignKey(HP02, on_delete=models.CASCADE)
    non_financed_charge_contract_relation = models.ForeignKey(NonFinancedCharge, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.hp02)
