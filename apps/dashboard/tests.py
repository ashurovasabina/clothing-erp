from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

class DashboardApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Agar endpointlar login talab qilsa, foydalanuvchi yaratib login qilamiz
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_dashboard_index(self):
        url = reverse('dashboard:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sales_chart_data_api(self):
        url = reverse('dashboard:sales_chart_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_distribution_api(self):
        url = reverse('dashboard:category_distribution')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_monthly_sales_data_api(self):
        url = reverse('dashboard:monthly_sales_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_inventory_status_data_api(self):
        url = reverse('dashboard:inventory_status_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_top_products_data_api(self):
        url = reverse('dashboard:top_products_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_health_check(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'healthy'})