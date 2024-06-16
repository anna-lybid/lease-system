from django import forms
from .models import Product, Contract, NonFinancedCharge, NonStandardCashflow


class NonFinancedChargeForm(forms.ModelForm):
    class Meta:
        model = NonFinancedCharge
        fields = ['name', 'pay_date']


class ProductForm(forms.ModelForm):
    non_financed_charge = forms.ModelMultipleChoiceField(queryset=NonFinancedCharge.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Product
        fields = '__all__'

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        non_financed_charge = self.cleaned_data['non_financed_charge']
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ContractForm(forms.ModelForm):
    non_financed_charge = forms.ModelMultipleChoiceField(queryset=NonFinancedCharge.objects.filter(amount__isnull=True), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Contract
        fields = '__all__'

    def save(self, commit=True):
        instance = super(ContractForm, self).save(commit=False)
        non_financed_charge = self.cleaned_data['non_financed_charge']
        for charge in non_financed_charge:
            if charge.amount is None:
                raise forms.ValidationError('Amount must be specified for each NonFinancedCharge')
        if commit:
            instance.save()
            self.save_m2m()
        return instance
