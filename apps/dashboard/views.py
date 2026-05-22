from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import Order, OrderItem
from apps.inventory.models import Product, ProductVariant, Category
import json
import calendar


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Hozirgi sana
        current_date = timezone.now().date()
        last_month = current_date - timedelta(days=30)

        try:
            # So'nggi buyurtmalar
            recent_orders = Order.objects.filter(
                order_date__gte=last_month
            ).select_related('customer').order_by('-order_date')[:10]

            # Holat bo'yicha buyurtmalar statistikasi
            orders_by_status = Order.objects.values('status').annotate(
                count=Count('id'),
                total_amount=Sum('total')
            ).order_by('status')

            # Kategoriyalar bo'yicha sotuvlar
            category_sales = OrderItem.objects.filter(
                order__order_date__gte=last_month,
                order__status__in=['confirmed', 'processing', 'ready', 'shipped', 'delivered']
            ).values(
                'product_variant__product__category__name'
            ).annotate(
                total=Sum('total_price')
            ).order_by('-total')[:5]

        except Exception as e:
            # Handle any database errors
            recent_orders = []
            orders_by_status = []
            category_sales = []
            print(f"Error fetching dashboard data: {e}")

        context.update({
            'recent_orders': recent_orders,
            'orders_by_status': orders_by_status,
            'category_sales': category_sales,
        })

        return context


class SalesChartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # So'nggi 30 kunlik sotuvlar trendini olish
            days = int(request.GET.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            # Kunlik sotuvlar
            daily_sales = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date,
                status__in=['confirmed', 'processing', 'ready', 'shipped', 'delivered']
            ).values('order_date').annotate(
                total_sales=Sum('total')
            ).order_by('order_date')

            # Prepare dates for chart (all days in range)
            date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                          for i in range((end_date - start_date).days + 1)]

            # Prepare sales data with zeros for days with no sales
            sales_data = [0] * len(date_range)
            date_dict = {d: i for i, d in enumerate(date_range)}

            for sale in daily_sales:
                sale_date = sale['order_date'].strftime('%Y-%m-%d')
                if sale_date in date_dict:
                    sales_data[date_dict[sale_date]] = float(sale['total_sales'])

            # Format data for Chart.js
            return JsonResponse({
                'labels': date_range,
                'datasets': [{
                    'label': 'Sotuvlar (so\'m)',
                    'data': sales_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1,
                    'tension': 0.4
                }]
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class CategoryDistributionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            chart_type = request.GET.get('type', 'products')  # products, sales

            if chart_type == 'products':
                # Kategoriyalardagi mahsulotlar soni
                categories = Category.objects.annotate(
                    product_count=Count('products')
                ).filter(product_count__gt=0).order_by('-product_count')[:10]

                labels = [cat.name for cat in categories]
                data = [cat.product_count for cat in categories]
                title = 'Kategoriyalar bo\'yicha mahsulotlar'

            else:  # sales
                # So'nggi 90 kundagi sotuvlar
                last_90_days = timezone.now().date() - timedelta(days=90)

                categories = OrderItem.objects.filter(
                    order__order_date__gte=last_90_days,
                    order__status__in=['confirmed', 'processing', 'ready', 'shipped', 'delivered']
                ).values(
                    category_name=F('product_variant__product__category__name')
                ).annotate(
                    sales_total=Sum('total_price')
                ).order_by('-sales_total')[:10]

                labels = [item['category_name'] for item in categories if item['category_name']]
                data = [float(item['sales_total']) for item in categories if item['category_name']]
                title = 'Kategoriyalar bo\'yicha sotuvlar'

            # Create colors for chart
            background_colors = [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)'
            ]

            border_colors = [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)'
            ]

            return JsonResponse({
                'title': title,
                'type': 'pie',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': data,
                        'backgroundColor': background_colors[:len(data)],
                        'borderColor': border_colors[:len(data)],
                        'borderWidth': 1
                    }]
                }
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class MonthlySalesDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # Get monthly sales for the past year
            end_date = timezone.now().date()
            start_date = end_date.replace(day=1) - timedelta(days=365)  # Go back a year

            # Query monthly sales
            monthly_sales = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date,
                status__in=['confirmed', 'processing', 'ready', 'shipped', 'delivered']
            ).annotate(
                month=F('order_date__month'),
                year=F('order_date__year')
            ).values('month', 'year').annotate(
                total_sales=Sum('total')
            ).order_by('year', 'month')

            # Prepare month labels and data
            months = []
            sales_data = []

            # Initialize data structure for the last 12 months
            current_month = end_date.month
            current_year = end_date.year

            for i in range(12):
                month_idx = current_month - i
                year = current_year

                if month_idx <= 0:
                    month_idx += 12
                    year -= 1

                # Get month name
                month_name = f"{calendar.month_name[month_idx][:3]} {year}"
                months.insert(0, month_name)
                sales_data.insert(0, 0)  # Default to 0

            # Fill in actual sales data
            for sale in monthly_sales:
                month_idx = sale['month']
                year = sale['year']

                # Calculate how many months ago this was
                months_ago = (current_year - year) * 12 + (current_month - month_idx)

                if 0 <= months_ago < 12:
                    sales_data[11 - months_ago] = float(sale['total_sales'])

            return JsonResponse({
                'labels': months,
                'datasets': [{
                    'label': 'Oylik sotuvlar',
                    'data': sales_data,
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }]
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class InventoryStatusDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # Get inventory status data
            product_variants = ProductVariant.objects.all()

            # Calculate inventory status
            total_products = product_variants.count()
            in_stock = product_variants.filter(stock_quantity__gt=0).count()
            low_stock = product_variants.filter(stock_quantity__gt=0, stock_quantity__lte=10).count()
            out_of_stock = product_variants.filter(stock_quantity=0).count()

            # Pie chart data for inventory status
            pie_data = {
                'labels': ['Mavjud', 'Kam qolgan', 'Tugagan'],
                'datasets': [{
                    'data': [in_stock - low_stock, low_stock, out_of_stock],
                    'backgroundColor': [
                        'rgba(75, 192, 192, 0.6)',  # Teal for in stock
                        'rgba(255, 206, 86, 0.6)',  # Yellow for low stock
                        'rgba(255, 99, 132, 0.6)'  # Red for out of stock
                    ],
                    'borderColor': [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    'borderWidth': 1
                }]
            }

            # Low stock products
            low_stock_products = product_variants.filter(
                stock_quantity__gt=0,
                stock_quantity__lte=10
            ).select_related('product').order_by('stock_quantity')[:10]

            low_stock_data = {
                'labels': [f"{p.product.name} ({p.size.name}, {p.color.name})" for p in low_stock_products],
                'datasets': [{
                    'label': 'Qolgan miqdor',
                    'data': [p.stock_quantity for p in low_stock_products],
                    'backgroundColor': 'rgba(255, 206, 86, 0.6)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 1
                }]
            }

            return JsonResponse({
                'pieData': pie_data,
                'lowStockData': low_stock_data
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class TopProductsDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # Last 90 days
            start_date = timezone.now().date() - timedelta(days=90)

            # Top products by quantity sold
            top_products = OrderItem.objects.filter(
                order__order_date__gte=start_date,
                order__status__in=['confirmed', 'processing', 'ready', 'shipped', 'delivered']
            ).values(
                'product_variant__product__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_sales=Sum('total_price')
            ).order_by('-total_quantity')[:10]

            return JsonResponse({
                'labels': [item['product_variant__product__name'] for item in top_products],
                'datasets': [{
                    'label': 'Sotilgan miqdor',
                    'data': [item['total_quantity'] for item in top_products],
                    'backgroundColor': 'rgba(153, 102, 255, 0.6)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 1
                }, {
                    'label': 'Sotuvlar (so\'m)',
                    'data': [float(item['total_sales']) for item in top_products],
                    'backgroundColor': 'rgba(255, 159, 64, 0.6)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1,
                    'type': 'line',
                    'yAxisID': 'sales'
                }]
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)