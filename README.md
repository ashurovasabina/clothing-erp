# Kiyim-Kechak Ulgurji Savdo ERP Tizimi 🚀

O'rta va yirik hajmdagi tayyor kiyim-kechak ulgurji savdo kompaniyalari uchun Django va Jazzmin UI asosida yaratilgan zamonaviy ERP (Enterprise Resource Planning) tizimi.

---

## 🌟 Tizim Xususiyatlari

- **🌐 Ko'p tilli interfeys (Multi-lingual):** To'liq O'zbek (`uz`), Rus (`ru`) va Ingliz (`en`) tillarida ishlovchi interfeys.
- **💼 Integratsiyalashgan Modullar:**
  - **Inventarizatsiya (Ombor):** Mahsulotlar, toifalar (kategoriyalar), o'lchamlar, ranglar, brendlar va mavsumlar boshqaruvi.
  - **Sotuvlar (Sales):** Buyurtmalar, mijozlar va sotuvlar hisoboti.
  - **Sotib olish (Purchases):** Ta'minotchilar, xarid buyurtmalari va omborga kirim.
  - **Moliya (Finance):** Invoyslar (hisob-faktura), to'lovlar va xarajatlar hisobi.
  - **HR va Xodimlar:** Bo'limlar, lavozimlar, xodimlar, davomat va ish haqi (oylik) hisob-kitoblari.
- **📊 Vizual Dashboard:** Chart.js orqali integratsiya qilingan interaktiv tahliliy grafiklar va statistik ma'lumotlar.
- **🛡️ Xavfsizlik va Ruxsatnomalar:** Foydalanuvchilar rollari bo'yicha cheklangan ruxsatlar (Role-based access control).
- **🎨 Premium UI:** Jazzmin kutubxonasi asosida yaratilgan zamonaviy, qulay va responsive boshqaruv paneli.

---

## 🛠️ Texnik Talablar

- **Python:** 3.8 va undan yuqori
- **Django:** 4.2+ / 5.2+
- **Ma'lumotlar ombori:** PostgreSQL 12+ (yoki ishlab chiqish uchun SQLite3)
- **UI Framework:** Django Jazzmin
- **API Engine:** Django Rest Framework (DRF)
- **Grafika kutubxonasi:** Chart.js

---

## 🚀 Mahalliy Tizimni O'rnatish va Ishga Tushirish

Tizimni mahalliy (local) kompyuterda ishga tushirish uchun quyidagi qadamlarni bajaring:

```bash
# 1. Loyihani yuklab oling va unga o'ting
cd clothing_erp-main

# 2. Virtual muhit (virtual environment) yaratish
python -m venv venv

# 3. Virtual muhitni faollashtirish
# Linux / macOS:
source venv/bin/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat

# 4. Zarur kutubxonalarni o'rnatish
pip install -r requirements.txt

# 5. Ma'lumotlar bazasi migratsiyalarini bajarish
python manage.py migrate

# 6. Django static fayllarini to'plash
python manage.py collectstatic --noinput

# 7. Mahalliy serverni ishga tushirish
python manage.py runserver
```

Tizimga kirish uchun brauzeringizda `http://127.0.0.1:8000/admin/` manzilini oching.

---

## 🧪 Sohta Ma'lumotlarni Yaratish (Fake Data Generation)

Loyihani sinash va test qilish uchun tizimda avtomatik ravishda juda realistik ma'lumotlarni generatsiya qilish imkoniyati mavjud. Buning uchun maxsus `generate_fake_data.py` skripti tayyorlangan.

Ushbu skript `Faker` kutubxonasining **Uzbek (`uz_UZ`)** lokali asosida ishlaydi, ya'ni barcha yaratiladigan ismlar, manzillar, kompaniyalar va telefon raqamlari haqiqiy O'zbekiston hududiga mos tarzda yaratiladi.

### Yaratiladigan Ma'lumotlar Ro'yxati:

1.  **Superuser (Admin):** `admin` foydalanuvchisi yaratiladi (Parol: `admin12345`).
2.  **Regular Users:** 3 ta qo'shimcha tizim foydalanuvchisi (Parol: `password123`).
3.  **Tizim Sozlamalari va Valyutalar:** UZS, USD va EUR valyutalari.
4.  **Katalog elementlari:** Ranglar (o'zbekcha nomlar va hex kodlar), O'lchamlar, Kategoriyalar (Ko'ylaklar, Shimlar va h.k.), Mahalliy Brendlar (UzTextile, SilkRoad, va h.k.) va Mavsumlar.
5.  **Omborlar va Xodimlar:** 3 ta ombor, 7 ta bo'lim va 30 ta realistik o'zbek xodimlari (barcha shaxsiy ma'lumotlari, lavozimlari va maoshlari bilan).
6.  **Mahsulotlar va Variantlar:** 50 ta mahsulot va ularning o'lcham hamda rang bo'yicha ko'plab variantlari.
7.  **Mijozlar va Ta'minotchilar:** 20 ta mijoz (kompaniyalar va jismoniy shaxslar) va 10 ta ta'minotchi.
8.  **Hujjatlar va Tranzaksiyalar:** 30 ta savdo buyurtmasi, 15 ta xarid buyurtmasi, ombor harakatlari, invoyslar, to'lovlar, xarajatlar, shuningdek xodimlarning davomati va oylik ish haqi vedomostlari.

### Ishga tushirish buyrug'i:

Virtual muhit faollashtirilgan holatda, loyihaning ildiz (root) papkasida turib quyidagi buyruqni ishga tushiring:

```bash
python generate_fake_data.py
```

_Skript muvaffaqiyatli yakunlangach, ekranda `All data has been successfully generated!` yozuvi paydo bo'ladi va siz tayyor login-parol bilan tizimga kirib grafik hisobotlarni tomosha qilishingiz mumkin._

---

## ⚙️ Gunicorn orqali Ishga Tushirish (Production Deployment)

Ishlab chiqarish (Production) muhitida Django'ning ichki `runserver` serveridan foydalanish tavsiya etilmaydi. Buning o'rniga yuqori unumdorlikka ega, xavfsiz va barqaror **Gunicorn (Green Unicorn)** WSGI HTTP serveridan foydalaniladi.

> [!NOTE]
> Gunicorn asosan UNIX-ga asoslangan operatsion tizimlarda (Linux, macOS) ishlaydi. Ishlab chiqarish serverlari deyarli har doim Linux bo'lganligi sababli, ushbu konfiguratsiya serverga joylash (deployment) uchun juda muhimdir.

### 1. Gunicorn-ni o'rnatish

Production virtual muhitida gunicorn kutubxonasini o'rnating:

```bash
pip install gunicorn
```

### 2. Gunicorn orqali serverni qo'lda ishga tushirish

Gunicorn-ni eng oddiy holatda ishga tushirish buyrug'i:

```bash
gunicorn clothing_erp.wsgi:application
```

Ko'proq nazorat va optimallashtirish uchun quyidagi parametrlardan foydalanish tavsiya etiladi:

```bash
gunicorn --bind 0.0.0.0:8000 --workers 3 clothing_erp.wsgi:application
```

**Parametrlar tushuntirishi:**

- `--bind 0.0.0.0:8000` - Serverni barcha tarmoq interfeyslarining `8000` portiga bog'laydi.
- `--workers 3` - So'rovlarni parallel qayta ishlash uchun ishchi jarayonlar soni.
  > 💡 **Formula:** Odatda ishchilar soni `(2 * CPU_yadro_soni) + 1` formulasidan kelib chiqib belgilanadi.
- `clothing_erp.wsgi:application` - Djangoning WSGI kirish nuqtasi.

### 3. Systemd Xizmati sifatida Sozlash (Tavsiya etiladi)

Server o'chib yonganda tizim avtomatik ravishda ishga tushishi uchun Gunicorn-ni tizim xizmati (systemd service) sifatida sozlash tavsiya etiladi.

`/etc/systemd/system/clothing_erp.service` faylini yarating va quyidagi tarkibni joylashtiring:

```ini
[Unit]
Description=Kiyim-Kechak ERP Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/clothing_erp-main
ExecStart=/var/www/clothing_erp-main/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/clothing_erp-main/clothing_erp.sock \
          clothing_erp.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Xizmatni boshqarish buyruqlari:**

```bash
# Xizmatni yoqish va ishga tushirish
sudo systemctl daemon-reload
sudo systemctl start clothing_erp
sudo systemctl enable clothing_erp

# Holatini tekshirish
sudo systemctl status clothing_erp
```

### 4. Nginx orqali Proksilash (Reverse Proxy)

Nginx-ni Gunicorn oldiga teskari proksi (reverse proxy) sifatida qo'yish va statik fayllarni to'g'ridan-to'g'ri Nginx orqali tarqatish eng maqbul yechim hisoblanadi.

Nginx konfiguratsiya fayli namunasi (`/etc/nginx/sites-available/clothing_erp`):

```nginx
server {
    listen 80;
    server_name cloud.sobirjon.codes;

    location = /favicon.ico { access_log off; log_not_found off; }

    # Static fayllarni tarqatish
    location /static/ {
        root /var/www/clothing_erp-main;
    }

    # Media fayllarni tarqatish
    location /media/ {
        root /var/www/clothing_erp-main;
    }

    # Barcha so'rovlarni Gunicorn soketiga yo'naltirish
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/clothing_erp-main/clothing_erp.sock;
    }
}
```
