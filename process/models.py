from django.db import models
from rest_framework.exceptions import ValidationError


class Goal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class NonFinancedCharge(models.Model):
    name = models.CharField(max_length=100)
    pay_date = models.CharField(max_length=50)  ## Maybe it will be needed to edit
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class NonStandardCashflow(models.Model):
    name = models.CharField(max_length=100)
    pay_date = models.CharField(max_length=50)  ## Maybe will be needed to edit
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class Product(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    product_inner_id = models.CharField(max_length=50)
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
    non_financed_charge = models.ManyToManyField(NonFinancedCharge, blank=True, null=True, related_name="non_financed_charge")
    non_standard_cashflows = models.ManyToManyField(NonStandardCashflow, blank=True, null=True, related_name="non_standard_cashflow")
    include_accounting_schedules = models.BooleanField(default=False)
    accounting_treatment = models.CharField(max_length=50)

    def clean(self):
        if self.include_accounting_schedules and not self.accounting_treatment:
            raise ValidationError("Accounting treatment is mandatory when including accounting schedules.")

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Contract(models.Model):
    contract_inner_id = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    term = models.IntegerField()
    start_date = models.DateField()
    due_day = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    amount_financed = models.DecimalField(max_digits=10, decimal_places=2)
    subsidy = models.BooleanField(default=False)
    non_financed_charge = models.ManyToManyField(NonFinancedCharge, blank=True)
    non_standard_cashflows = models.ManyToManyField(NonStandardCashflow, blank=True)
