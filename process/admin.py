from django.contrib import admin
from .models import Goal, NonFinancedCharge, NonStandardCashflow, Product, Contract
from .forms import ProductForm, ContractForm

admin.site.register(Goal)
admin.site.register(NonFinancedCharge)
admin.site.register(NonStandardCashflow)


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    filter_horizontal = ('non_financed_charge', 'non_standard_cashflows')


admin.site.register(Product, ProductAdmin)


class ContractAdmin(admin.ModelAdmin):
    form = ContractForm
    filter_horizontal = ('non_financed_charge', 'non_standard_cashflows')


admin.site.register(Contract, ContractAdmin)
