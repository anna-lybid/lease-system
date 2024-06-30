from rest_framework import serializers
from backend.process.models import (
    Goal,
    Product,
    Contract,
    NonStandardCashflow,
    NonFinancedCharge
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
        model = NonFinancedCharge
        fields = ['non_financed_charge', 'amount']


class ContractNonStandardCashflowSerializer(serializers.ModelSerializer):  ##POST
    class Meta:
        model = NonStandardCashflow
        fields = ['non_standard_cashflow', 'amount']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = ['product_inner_id', 'name', 'description']


class ContractSerializer(serializers.ModelSerializer):
    non_standard_cashflows = NonStandardCashflowSerializer(many=True, required=False)
    non_financed_charges = NonFinancedChargeSerializer(many=True, required=False)
    product = ProductListSerializer(required=True)

    class Meta:
        model = Contract
        fields =("id", "contract_inner_id", "product", "term", "start_date", "due_day", "interest_rate", "amount_financed", "subsidy", "non_financed_charges", "non_standard_cashflows")


class ContractListSerializer(ContractSerializer):
    class Meta:
        model = Contract
        fields = ("id", "contract_inner_id", "term", "start_date", "due_day", "interest_rate", "amount_financed")


class UploadCSVSerializer(serializers.Serializer):
    csv_file = serializers.FileField()

