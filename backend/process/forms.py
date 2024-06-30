from django import forms
from .models import Product, NonFinancedCharge, NonStandardCashflow, ProductNonFinancedCharge, \
    ProductNonStandardCashflow, ContractNonStandardCashflow, ContractNonFinancedCharge, Contract


class ProductForm(forms.ModelForm):
    non_financed_charges = forms.ModelMultipleChoiceField(
        queryset=NonFinancedCharge.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )
    non_standard_cashflows = forms.ModelMultipleChoiceField(
        queryset=NonStandardCashflow.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )

    class Meta:
        model = Product
        fields = '__all__'

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        non_financed_charges = self.cleaned_data['non_financed_charges']
        non_standard_cashflows = self.cleaned_data['non_standard_cashflows']
        if commit:
            instance.save()
            instance.productnonfinancedcharge_set.all().delete()
            instance.productnonstandardcashflow_set.all().delete()
            for charge in non_financed_charges:
                ProductNonFinancedCharge.objects.create(
                    product=instance,
                    non_financed_charge=charge,
                    pay_date=charge.pay_date,
                    name=charge.name
                )
            for cashflow in non_standard_cashflows:
                ProductNonStandardCashflow.objects.create(
                    product=instance,
                    non_standard_cashflow=cashflow,
                    pay_date=cashflow.pay_date,
                    name=cashflow.name
                )
        return instance


class ContractForm(forms.ModelForm):
    non_financed_charges = forms.ModelMultipleChoiceField(
        queryset=NonFinancedCharge.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )
    non_standard_cashflows = forms.ModelMultipleChoiceField(
        queryset=NonStandardCashflow.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )

    class Meta:
        model = Contract
        fields = '__all__'

    def save(self, commit=True):
        instance = super(ContractForm, self).save(commit=False)
        non_financed_charges = self.cleaned_data['non_financed_charges']
        non_standard_cashflows = self.cleaned_data['non_standard_cashflows']
        if commit:
            instance.save()
            instance.contractnonfinancedcharge_set.all().delete()
            instance.contractnonstandardcashflow_set.all().delete()
            for charge in non_financed_charges:
                ContractNonFinancedCharge.objects.create(
                    contract=instance,
                    non_financed_charge=charge,
                    amount=0
                )
            for cashflow in non_standard_cashflows:
                ContractNonStandardCashflow.objects.create(
                    contract=instance,
                    non_standard_cashflow=cashflow,
                    amount=0
                )
        return instance
