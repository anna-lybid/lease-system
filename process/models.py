from django.db import models
from rest_framework.exceptions import ValidationError


class Goal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class NonFinancedCharge(models.Model):
    name = models.CharField(max_length=100)
    pay_date = models.CharField(max_length=50, default="At time n (end date of contract)")  ## Maybe it will be needed to edit
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class NonStandardCashflow(models.Model):
    name = models.CharField(max_length=100)
    pay_date = models.CharField(max_length=50, default="At time n (end date of contract)")  ## Maybe will be needed to edit
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    product_inner_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    INTEREST_RATE_CHOICES = [
        ("IRR", "IRR"),
        ("Fixed", "Fixed"),
        ("Other", "Other"),
    ]

    interest_rate_type = models.CharField(max_length=10, choices=INTEREST_RATE_CHOICES, default="IRR")
    has_subsidy = models.BooleanField(default=False)

    PAY_TYPE_CHOICES = [
        ("In advance", "In advance"),
        ("In arreas", "In arreas"),
    ]

    pay_type = models.CharField(max_length=50, choices=PAY_TYPE_CHOICES, default="In arreas")   ##in advance or arreas
    term_type = models.CharField(max_length=50, default="Finance for n months")
    include_start_day = models.BooleanField(default=True)
    include_due_day = models.BooleanField(default=True)

    DUE_DAY_MONTH_END_CHOICES = [
        ("No special treatment", "No special treatment"),
        ("Some special treatment", "Some special treatment"),
    ]

    is_due_day_is_month_end = models.CharField(max_length=60, choices=DUE_DAY_MONTH_END_CHOICES, default="No special treatment")
    non_financed_charges = models.ManyToManyField(NonFinancedCharge, through='ProductNonFinancedCharge', null=True, blank=True)
    non_standard_cashflows = models.ManyToManyField(NonStandardCashflow, through='ProductNonStandardCashflow', null=True, blank=True)
    include_accounting_schedules = models.BooleanField(default=False)
    accounting_treatment = models.CharField(max_length=50, null=True, blank=True)

    def clean(self):
        if self.include_accounting_schedules and not self.accounting_treatment:
            raise ValidationError("Accounting treatment is mandatory when including accounting schedules.")

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Contract(models.Model):
    contract_inner_id = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    term = models.IntegerField()
    start_date = models.DateField()
    due_day = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    amount_financed = models.DecimalField(max_digits=10, decimal_places=2)
    subsidy = models.BooleanField(default=False)
    non_financed_charges = models.ManyToManyField(NonFinancedCharge, through='ContractNonFinancedCharge')
    non_standard_cashflows = models.ManyToManyField(NonStandardCashflow, through='ContractNonStandardCashflow')

    def __str__(self):
        return self.contract_inner_id


class ProductNonFinancedCharge(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    non_financed_charge = models.ForeignKey(NonFinancedCharge, on_delete=models.CASCADE)
    PAY_DATE_CHOICES = [
        ("At the end of the contract", "At the end of the contract"),
        ("At the start of the contract", "At the start of the contract"),
        ("On any day during the contract period (manual setting)", "On any day during the contract period")
    ]
    pay_date = models.CharField(max_length=255, choices=PAY_DATE_CHOICES, default="At time n (end date of contract)")
    name = models.CharField(max_length=255)


class ContractNonFinancedCharge(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    non_financed_charge = models.ForeignKey(NonFinancedCharge, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class ProductNonStandardCashflow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    non_standard_cashflow = models.ForeignKey(NonStandardCashflow, on_delete=models.CASCADE)
    PAY_DATE_CHOICES = [
        ("At the end of the contract", "At the end of the contract"),
        ("At the start of the contract", "At the start of the contract"),
        ("On any day during the contract period (manual setting)", "On any day during the contract period")
    ]
    pay_date = models.CharField(max_length=255, choices=PAY_DATE_CHOICES, default="At time n (end date of contract)")
    name = models.CharField(max_length=255)


class ContractNonStandardCashflow(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    non_standard_cashflow = models.ForeignKey(NonStandardCashflow, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
