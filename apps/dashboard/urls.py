from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('api/sales-chart/', views.SalesChartDataView.as_view(), name='sales_chart_data'),
    path('api/category-distribution/', views.CategoryDistributionView.as_view(), name='category_distribution'),
    path('api/monthly-sales/', views.MonthlySalesDataView.as_view(), name='monthly_sales_data'),
    path('api/inventory-status/', views.InventoryStatusDataView.as_view(), name='inventory_status_data'),
    path('api/top-products/', views.TopProductsDataView.as_view(), name='top_products_data'),
]