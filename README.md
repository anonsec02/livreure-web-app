# Livreure - منصة التوصيل الاحترافية

![Livreure Logo](logo.png)

## نظرة عامة

Livreure هي منصة توصيل طعام احترافية مصممة لتنافس التطبيقات العالمية مثل Uber Eats. تقدم المنصة تجربة مستخدم متكاملة للعملاء والمطاعم ووكلاء التوصيل مع لوحة تحكم إدارية شاملة.

## الميزات الرئيسية

### للعملاء
- 🍽️ تصفح المطاعم والقوائم
- 🛒 إضافة الأطباق إلى السلة
- 💳 خيارات دفع متعددة
- 📍 تتبع الطلبات في الوقت الفعلي
- ⭐ تقييم المطاعم والأطباق
- 📱 واجهة متجاوبة لجميع الأجهزة

### للمطاعم
- 🏪 إدارة الملف الشخصي للمطعم
- 📋 إدارة القوائم والأطباق
- 📊 تتبع الطلبات والمبيعات
- 💰 إحصائيات الإيرادات
- ⏰ إدارة أوقات العمل

### لوكلاء التوصيل
- 🏍️ قبول ورفض الطلبات
- 🗺️ تتبع المسارات
- 💵 إدارة الأرباح
- 📈 إحصائيات الأداء

### لوحة تحكم الإدارة
- 👥 إدارة المستخدمين
- 🏪 إدارة المطاعم
- 📦 إدارة الطلبات
- 🚚 إدارة وكلاء التوصيل
- 📊 التحليلات والتقارير
- ⚙️ إعدادات النظام

## التقنيات المستخدمة

### الواجهة الأمامية
- HTML5, CSS3, JavaScript (ES6+)
- تصميم متجاوب (Responsive Design)
- Font Awesome للأيقونات
- Chart.js للرسوم البيانية

### الواجهة الخلفية
- Python Flask
- SQLAlchemy ORM
- SQLite Database
- JWT Authentication
- Flask-CORS

### الأدوات والمكتبات
- Git للتحكم في الإصدارات
- Gunicorn لخادم الإنتاج

## هيكل المشروع

```
livreure-enhanced/
├── index.html              # الواجهة الأمامية الرئيسية
├── styles.css              # ملف التنسيق الرئيسي
├── script.js               # ملف JavaScript الرئيسي
├── translations.js         # ملف الترجمات
├── logo.png                # شعار المنصة
├── admin-dashboard/        # لوحة تحكم الإدارة
│   ├── index.html
│   ├── admin-styles.css
│   ├── admin-script.js
│   └── logo.png
├── backend/                # الواجهة الخلفية
│   ├── src/
│   │   ├── main.py
│   │   ├── models/
│   │   └── routes/
│   ├── requirements.txt
│   └── seed_data.py
└── README.md
```

## التثبيت والتشغيل

### متطلبات النظام
- Python 3.8+
- pip
- Git

### خطوات التثبيت

1. **استنساخ المستودع**
```bash
git clone https://github.com/anonsec02/livreure-web-app.git
cd livreure-web-app
```

2. **تثبيت متطلبات الواجهة الخلفية**
```bash
cd backend
pip install -r requirements.txt
```

3. **إنشاء البيانات التجريبية**
```bash
python seed_data.py
```

4. **تشغيل الخادم**
```bash
python src/main.py
```

5. **فتح المتصفح**
- الواجهة الأمامية: `http://localhost:5000`
- لوحة تحكم الإدارة: `http://localhost:5000/admin-dashboard`

## حسابات الاختبار

### العملاء
- **البريد الإلكتروني:** ahmed@customer.mr
- **كلمة المرور:** customer123

### المطاعم
- **البريد الإلكتروني:** sahara@restaurant.mr
- **كلمة المرور:** restaurant123

### وكلاء التوصيل
- **البريد الإلكتروني:** abdullah@delivery.mr
- **كلمة المرور:** delivery123

### الإدارة
- **البريد الإلكتروني:** admin@livreure.mr
- **كلمة المرور:** admin123

## API Documentation

### نقاط النهاية الرئيسية

#### المصادقة
- `POST /api/auth/login` - تسجيل الدخول
- `POST /api/auth/register` - تسجيل حساب جديد
- `POST /api/auth/logout` - تسجيل الخروج

#### المطاعم
- `GET /api/restaurants` - جلب قائمة المطاعم
- `GET /api/restaurants/{id}` - جلب تفاصيل مطعم
- `GET /api/restaurants/{id}/menu` - جلب قائمة الطعام

#### الطلبات
- `POST /api/orders` - إنشاء طلب جديد
- `GET /api/orders` - جلب طلبات المستخدم
- `PUT /api/orders/{id}/status` - تحديث حالة الطلب

#### الإدارة
- `GET /api/admin/stats` - إحصائيات عامة
- `GET /api/admin/users` - إدارة المستخدمين
- `GET /api/admin/orders` - إدارة الطلبات

## الأمان

- 🔐 تشفير كلمات المرور باستخدام bcrypt
- 🎫 مصادقة JWT للجلسات
- 🛡️ حماية CORS
- 🔒 تحقق من صحة البيانات
- 🚫 حماية من SQL Injection

## الدعم والتواصل

- **المطور:** ra-one02
- **التليجرام:** [@raone_002](https://t.me/raone_002)
- **الإصدار:** 2.0.0
- **الترخيص:** MIT

## المساهمة

نرحب بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المستودع
2. إنشاء فرع جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى الفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## خارطة الطريق

- [ ] تطبيق الهاتف المحمول
- [ ] دعم المدفوعات الإلكترونية
- [ ] نظام الإشعارات المباشرة
- [ ] تحليلات متقدمة
- [ ] دعم متعدد اللغات
- [ ] API للطرف الثالث

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

**تم التطوير بواسطة ra-one02 💻**

*منصة Livreure - حيث يلتقي الطعم بالتكنولوجيا*

