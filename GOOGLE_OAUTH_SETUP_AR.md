# إعداد Google Earth Engine OAuth — GeoAnomaly Pro

## ما هو خاص بالمالك؟

هذه القيم تخص **تطبيق GeoAnomaly Pro** مرة واحدة:

- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET
- GOOGLE_OAUTH_REDIRECT_URI

ليست حساب المستخدم ولا كلمة مرور Google.

## ما هو خاص بكل مستخدم؟

كل مستخدم يضغط:

`ربط Google Earth Engine`

ثم يسجل الدخول بحساب Google الخاص به ويمنح التفويض.

## التطوير المحلي

Authorized JavaScript origin:

`http://127.0.0.1:5500`

Authorized redirect URI:

`http://127.0.0.1:8000/auth/earth-engine/callback`

يجب أن تكون القيمة في Google مطابقة تمامًا.

## بعد الحصول على Client ID وSecret

انسخ `.env.example` إلى `.env` ثم ضع القيم في:

`GOOGLE_OAUTH_CLIENT_ID=...`

`GOOGLE_OAUTH_CLIENT_SECRET=...`

لا تضع `.env` في GitHub. الملف موجود في `.gitignore`.

## لا يمكن تشغيل Earth Engine بدون هذا الإعداد

هذا ليس خطأ للمستخدم. إنه إعداد OAuth للتطبيق.

بعد اكتمال إعداد المالك، المستخدمون لا يحتاجون إلى Client ID أو Secret.
