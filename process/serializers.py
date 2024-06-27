from rest_framework import serializers
from process.models import (
    Goal,
    Product,
    Contract,
    NonStandardCashflow,
    NonFinancedCharge,
    ProductNonFinancedCharge,
    ProductNonStandardCashflow,
    ContractNonFinancedCharge,
    ContractNonStandardCashflow
)


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['id']


class NonStandardCashflowSerializer(serializers.ModelSerializer):  ## For relatons, product and contract
    class Meta:
        model = NonStandardCashflow
        fields = ['name', 'pay_date', 'amount']


class NonFinancedChargeSerializer(serializers.ModelSerializer):  ## For relatons, product and contract
    class Meta:
        model = NonFinancedCharge
        fields = ['name', 'pay_date', 'amount']


class ContractNonFinancedChargeSerializer(serializers.ModelSerializer): ##POST
    class Meta:
        model = ContractNonFinancedCharge
        fields = ['non_financed_charge', 'amount']


class ContractNonStandardCashflowSerializer(serializers.ModelSerializer):  ##POST
    class Meta:
        model = ContractNonStandardCashflow
        fields = ['non_standard_cashflow', 'amount']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description']


class ContractSerializer(serializers.ModelSerializer):
    non_standard_cashflows = NonStandardCashflowSerializer(many=True, required=False)
    non_financed_charges = NonFinancedChargeSerializer(many=True, required=False)
    product = ProductListSerializer(required=True)
    class Meta:
        model = Contract
        fields =("contract_inner_id", "product", "term", "start_date", "due_day", "interest_rate", "amount_financed", "subsidy", "non_financed_charges", "non_standard_cashflows")
        read_only_fields = ['id']


class ContractListSerializer(ContractSerializer):
    class Meta:
        model = Contract
        fields = ("id", "contract_inner_id", "term", "start_date", "due_day", "interest_rate", "amount_financed")

class UploadCSVSerializer(serializers.Serializer):
    csv_file = serializers.FileField()


class ContractNonFinancedChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractNonFinancedCharge
        fields = "__all__"