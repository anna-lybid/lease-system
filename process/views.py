from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from process.models import Goal, Product, Contract, ContractNonFinancedCharge, ContractNonStandardCashflow
from process.serializers import GoalSerializer, ProductSerializer, ContractSerializer, UploadCSVSerializer, \
    ProductListSerializer, ContractListSerializer
from process.calculation_core import parse_csv


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset
        else:
            return self.queryset.prefetch_related('non_financed_charges', 'non_standard_cashflows')



class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        return ContractSerializer

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset
        else:
            return self.queryset.select_related('product').prefetch_related('non_financed_charges', 'non_standard_cashflows')


class UploadCSVView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = UploadCSVSerializer(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.validated_data['csv_file']
            contract_data = parse_csv(csv_file)
            product_inner_id = contract_data['product_inner_id']
            product = Product.objects.get(product_inner_id=product_inner_id)

            contract = Contract.objects.create(
                contract_inner_id= contract_data['contract_id'],
                product=product,
                term=contract_data['term'],
                start_date=contract_data['start_date'],
                due_day=contract_data['due_day'],
                interest_rate=contract_data['interest_rate'],
                amount_financed=contract_data['amount_financed'],
            )

            if contract_data["balloon"] is not None and product.non_financed_charges.exists():
                non_financed_charge = product.non_financed_charges.first()

                contract_non_financed_charge_instance = ContractNonFinancedCharge.objects.create(
                    contract=contract,
                    non_financed_charge=non_financed_charge,
                    amount=contract_data["balloon"],
                )
                non_financed_charge_instance = contract_non_financed_charge_instance.non_financed_charge
                contract.non_financed_charges.add(non_financed_charge_instance)


            if contract_data["fee"] is not None and product.non_financed_charges.exists():
                non_financed_charge = product.non_financed_charges.first()

                contract_non_financed_charge_instance = ContractNonFinancedCharge.objects.create(
                    contract=contract,
                    non_financed_charge=non_financed_charge,
                    amount=contract_data["fee"],
                )
                non_financed_charge_instance = contract_non_financed_charge_instance.non_financed_charge
                contract.non_financed_charges.add(non_financed_charge_instance)

            serializer = ContractSerializer(contract)

            return Response({"contract_data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
