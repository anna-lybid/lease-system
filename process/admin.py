from django.contrib import admin
from .models import Goal, Product, NonFinancedCharge, Contract, ProductNonFinancedCharge, ContractNonFinancedCharge, NonStandardCashflow, ProductNonStandardCashflow, ContractNonStandardCashflow


class ProductNonFinancedChargeInline(admin.TabularInline):
    model = ProductNonFinancedCharge


class ContractNonFinancedChargeInline(admin.TabularInline):
    model = ContractNonFinancedCharge


class ProductNonStandardCashflowInline(admin.TabularInline):
    model = ProductNonStandardCashflow


class ContractNonStandardCashflowInline(admin.TabularInline):
    model = ContractNonStandardCashflow


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductNonFinancedChargeInline, ProductNonStandardCashflowInline]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    inlines = [ContractNonFinancedChargeInline, ContractNonStandardCashflowInline]


admin.site.register(NonFinancedCharge)
admin.site.register(NonStandardCashflow)
admin.site.register(Goal)
