from django.contrib import admin
from .models import Goal, Product, NonFinancedCharge, Contract, NonStandardCashflow


# class NonFinancedChargeInline(admin.TabularInline):
#     model = Product.non_financed_charges.through
#     extra = 1
#
#
# class NonStandardCashflowInline(admin.TabularInline):
#     model = Product.non_standard_cashflows.through
#     extra = 1
#
#
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     inlines = [NonStandardCashflowInline, NonFinancedChargeInline]
#     list_display = ('product_inner_id', 'name', 'goal', 'interest_rate_type')
#     search_fields = ('product_inner_id', 'name')
#     list_filter = ('goal', 'interest_rate_type')
#
#
# @admin.register(Contract)
# class ContractAdmin(admin.ModelAdmin):
#     inlines = [NonStandardCashflowInline, NonFinancedChargeInline]
#     list_display = ('contract_inner_id', 'product', 'term', 'start_date', 'due_day', 'interest_rate', 'amount_financed', 'subsidy')
#     search_fields = ('contract_inner_id', 'product__name')
#     list_filter = ('product', 'start_date', 'subsidy')


admin.site.register(NonFinancedCharge)
admin.site.register(NonStandardCashflow)
admin.site.register(Goal)
admin.site.register(Product)
admin.site.register(Contract)