import csv
import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from backend.process.models import Goal, Product, Contract, NonFinancedCharge, NonStandardCashflow
from backend.process.serializers import GoalSerializer, ProductSerializer, ContractSerializer, UploadCSVSerializer, \
    ProductListSerializer
from backend.process.calculation_core import parse_csv, perform_calculation_on_screen


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        goal_pk = self.kwargs['goal_pk']
        goal = get_object_or_404(Goal, pk=goal_pk)
        queryset = Product.objects.filter(goal=goal)

        return queryset


class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer

    def get_queryset(self):
        goal_pk = self.kwargs['goal_pk']
        product_pk = self.kwargs['product_pk']
        product = get_object_or_404(Product, pk=product_pk)

        queryset = Contract.objects.filter(product=product) \
            .select_related('product') \
            .prefetch_related('non_financed_charges', 'non_standard_cashflows')

        return queryset


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
                contract_inner_id=contract_data['contract_id'],
                product=product,
                term=contract_data['term'],
                start_date=contract_data['start_date'],
                due_day=contract_data['due_day'],
                interest_rate=contract_data['interest_rate'],
                amount_financed=contract_data['amount_financed'],
            )

            if contract_data.get("balloon") is not None:
                non_standard_cashflow, created = NonStandardCashflow.objects.get_or_create(
                    name="Balloon charge",
                    defaults={'amount': contract_data["balloon"]}
                )
                if not created:
                    non_standard_cashflow.amount = contract_data["balloon"]
                    non_standard_cashflow.save()
                contract.non_standard_cashflows.add(non_standard_cashflow)


            if contract_data.get("rv") is not None:
                non_standard_cashflow, created = NonStandardCashflow.objects.get_or_create(
                    name="RV charge",
                    defaults={'amount': contract_data["rv"]}
                )
                if not created:
                    non_standard_cashflow.amount = contract_data["rv"]
                    non_standard_cashflow.save()
                contract.non_standard_cashflows.add(non_standard_cashflow)


            if contract_data.get("fee") is not None:
                non_financed_charge, created = NonFinancedCharge.objects.get_or_create(
                    name="Fee charge",
                    defaults={'amount': contract_data["fee"]}
                )
                if not created:
                    non_financed_charge.amount = contract_data["fee"]
                    non_financed_charge.save()
                contract.non_financed_charges.add(non_financed_charge)



            serializer = ContractSerializer(contract)
            return Response({"contract_data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractOnScreenView(APIView):
    def get(self, request, contract_id, *args, **kwargs):
        try:
            contract = Contract.objects.get(pk=contract_id)
            results = perform_calculation_on_screen(contract)
            return Response(results, status=status.HTTP_200_OK)
        except Contract.DoesNotExist:
            return Response({"error": "Contract not found"}, status=status.HTTP_404_NOT_FOUND)


class ContractDownloadView(APIView):
    def get(self, request, contract_id, *args, **kwargs):
        try:
            contract = Contract.objects.get(pk=contract_id)
            current_date = datetime.date.today()
            filename = f"contract_{contract_id}_{current_date.strftime('%Y-%m-%d')}.csv"
            results = perform_calculation_on_screen(contract)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={filename}'

            fieldnames = ['contract_id', 'start_date', 'due_day', 'month', 'initial_capital', 'add_interest',
                          'monthly_installment', 'capital_after']

            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                row = {
                    'contract_id': result['contract_id'],
                    'start_date': result['start_date'],
                    'due_day': result['due_day'],
                    'month': result['month'],
                    'initial_capital': result['initial_capital'],
                    'add_interest': result['add_interest'],
                    'monthly_installment': result['monthly_installment'],
                    'capital_after': result['capital_after'],
                }
                writer.writerow(row)

            return Response("Success", status=status.HTTP_200_OK)

        except Contract.DoesNotExist:
            return Response({"error": "Contract not found"}, status=status.HTTP_404_NOT_FOUND)