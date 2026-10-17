#!/usr/bin/env python3
"""Idempotent preparation of the current Barakat Chemistry workspace for Android."""
import json, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
frontend = root / "artifacts/barakat-chemistry"
main_path = frontend / "src/main.tsx"
app_path = frontend / "src/App.tsx"
api_path = root / "artifacts/api-server/src/app.ts"
if not (root / "pnpm-workspace.yaml").is_file() or not main_path.is_file() or not app_path.is_file():
    raise SystemExit("Unrecognized Barakat Chemistry workspace; no patch was applied.")

pkg_path = frontend / "package.json"
pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
deps = pkg.setdefault("dependencies", {})
for name, version in {"@capacitor/core": "8.5.3", "@capacitor/android": "8.5.3", "@capacitor/app": "8.1.2"}.items():
    deps.setdefault(name, version)
pkg.setdefault("devDependencies", {}).setdefault("@capacitor/cli", "8.5.3")
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(frontend / "capacitor.config.ts").write_text('''import type { CapacitorConfig } from "@capacitor/cli";
const config: CapacitorConfig = {
  appId: "iq.barakatchemistry.institute",
  appName: "معهد أستاذ بركات",
  webDir: "dist/public",
  server: { androidScheme: "https", cleartext: false },
};
export default config;
''', encoding="utf-8")

main = main_path.read_text(encoding="utf-8")
if "BARAKAT_API_ORIGIN_CONFIGURATION" not in main:
    marker = "import { createRoot } from 'react-dom/client';"
    patch = """import { createRoot } from 'react-dom/client';
import { setBaseUrl } from '@workspace/api-client-react';

// BARAKAT_API_ORIGIN_CONFIGURATION: web stays same-origin; Android can use a remote API.
const configuredApiOrigin = import.meta.env.VITE_API_BASE_URL?.trim();
if (configuredApiOrigin) {
  const parsedApiOrigin = new URL(configuredApiOrigin);
  const localhost = parsedApiOrigin.hostname === 'localhost' || parsedApiOrigin.hostname === '127.0.0.1';
  if (parsedApiOrigin.protocol !== 'https:' && !localhost) {
    throw new Error('VITE_API_BASE_URL must use HTTPS outside localhost development.');
  }
  if (parsedApiOrigin.pathname !== '/' || parsedApiOrigin.search || parsedApiOrigin.hash || parsedApiOrigin.username || parsedApiOrigin.password) {
    throw new Error('VITE_API_BASE_URL must be an origin only, without a path or credentials.');
  }
  setBaseUrl(parsedApiOrigin.origin);
}
"""
    if marker not in main: raise SystemExit("Unexpected main.tsx; refusing unsafe patch.")
    main_path.write_text(main.replace(marker, patch, 1), encoding="utf-8")

app = app_path.read_text(encoding="utf-8")
if "BARAKAT_CAPACITOR_INTEGRATION" not in app:
    marker = "import { type ReactNode, type InputHTMLAttributes, type TextareaHTMLAttributes, useEffect, useRef, useState } from 'react';"
    patch = """import { type ReactNode, type InputHTMLAttributes, type TextareaHTMLAttributes, useEffect, useRef, useState } from 'react';
import { Capacitor } from '@capacitor/core';
import { App as CapacitorApp } from '@capacitor/app';
// BARAKAT_CAPACITOR_INTEGRATION"""
    if marker not in app: raise SystemExit("Unexpected App.tsx imports; refusing unsafe patch.")
    app = app.replace(marker, patch, 1)
    app = app.replace("function Home() {", "function Home({ authAvailable = true }: { authAvailable?: boolean }) {", 1)
    header_old = '''<div className="nav-actions"><Button href="/sign-in" variant="quiet" testId="link-signin">تسجيل الدخول</Button><Button href="/sign-up" testId="link-signup">إنشاء حساب طالب <ArrowLeft size={16} /></Button></div>'''
    header_new = '''{authAvailable ? <div className="nav-actions"><Button href="/sign-in" variant="quiet" testId="link-signin">تسجيل الدخول</Button><Button href="/sign-up" testId="link-signup">إنشاء حساب طالب <ArrowLeft size={16} /></Button></div> : <div className="nav-actions"><span className="inline-error" role="status" data-testid="status-preview-config">نسخة اختبار غير مرتبطة بالخادم</span></div>}'''
    hero_old = '''<div className="hero-actions"><Button href="/sign-up" testId="link-join">ابدأ كطالب <ArrowLeft size={17} /></Button><Button href="/sign-in" variant="outline" testId="link-login-secondary">لدي حساب بالفعل</Button></div>'''
    hero_new = '''<div className="hero-actions">{authAvailable ? <><Button href="/sign-up" testId="link-join">ابدأ كطالب <ArrowLeft size={17} /></Button><Button href="/sign-in" variant="outline" testId="link-login-secondary">لدي حساب بالفعل</Button></> : <p className="inline-error" role="status" data-testid="status-preview-details">هذه نسخة اختبار للواجهة والملزمة فقط. لا تدخل بيانات حسابك؛ يلزم إعداد خادم HTTPS ومصادقة Clerk لتفعيل الواجبات.</p>}</div>'''
    if header_old not in app or hero_old not in app:
        raise SystemExit("Expected public-home controls not found; refusing unsafe patch.")
    app = app.replace(header_old, header_new, 1).replace(hero_old, hero_new, 1)
    old_effect = """function App() {
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;"""
    new_effect = """const authConfigAvailable =
  import.meta.env.VITE_MOBILE_PREVIEW !== 'true' &&
  Boolean(clerkPubKey) &&
  (!Capacitor.isNativePlatform() || Boolean(import.meta.env.VITE_API_BASE_URL?.trim()));

function MissingConfigurationPage() {
  return <main className="app-shell gated" dir="rtl"><div className="glass-panel gated-card"><CircleAlert /><h1>خدمات المعهد غير مهيأة لهذه النسخة</h1><p>تسجيل الدخول والواجبات تحتاج عنوان خادم HTTPS ومفاتيح Clerk وإعدادات قاعدة البيانات والتخزين. لم يتم إنشاء بيانات تجريبية أو تأكيد أي عملية.</p><Button href="/" testId="link-preview-home">العودة إلى الصفحة العامة</Button></div></main>;
}

function App() {
  useEffect(() => {
    if (Capacitor.isNativePlatform()) {
      let listener: { remove: () => Promise<void> } | undefined;
      let cancelled = false;
      void CapacitorApp.addListener('backButton', ({ canGoBack }) => {
        if (canGoBack && window.history.length > 1) window.history.back();
        else void CapacitorApp.exitApp();
      }).then((registered) => {
        if (cancelled) void registered.remove();
        else listener = registered;
      }).catch(() => {
        // Keep the web UI usable if the native back event is unavailable.
      });
      return () => {
        cancelled = true;
        if (listener) void listener.remove();
      };
    }
    if (!('serviceWorker' in navigator)) return;"""
    if old_effect not in app: raise SystemExit("Expected App useEffect not found; refusing unsafe patch.")
    app = app.replace(old_effect, new_effect, 1)
    old_return = '''  return <QueryClientProvider client={queryClient}><ClerkProvider publishableKey={clerkPubKey} proxyUrl={clerkProxyUrl} localization={arSA} appearance={authAppearance}><TooltipProvider><WouterRouter base={basePath}><Router /></WouterRouter><Toaster /></TooltipProvider></ClerkProvider></QueryClientProvider>;
}'''
    new_return = '''  if (!authConfigAvailable) {
    return <QueryClientProvider client={queryClient}><TooltipProvider><WouterRouter base={basePath}><Switch><Route path="/" component={() => <Home authAvailable={false} />} /><Route component={MissingConfigurationPage} /></Switch></WouterRouter><Toaster /></TooltipProvider></QueryClientProvider>;
  }
  return <QueryClientProvider client={queryClient}><ClerkProvider publishableKey={clerkPubKey} proxyUrl={clerkProxyUrl} localization={arSA} appearance={authAppearance}><TooltipProvider><WouterRouter base={basePath}><Router /></WouterRouter><Toaster /></TooltipProvider></ClerkProvider></QueryClientProvider>;
}'''
    if old_return not in app: raise SystemExit("Expected App return not found; refusing unsafe patch.")
    app = app.replace(old_return, new_return, 1)
    old_clerk_key = "const clerkPubKey = publishableKeyFromHost(window.location.hostname, import.meta.env.VITE_CLERK_PUBLISHABLE_KEY);"
    new_clerk_key = """const rawClerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY?.trim();
const clerkPubKey = rawClerkPubKey
  ? publishableKeyFromHost(window.location.hostname, rawClerkPubKey)
  : '';"""
    if old_clerk_key not in app:
        raise SystemExit("Expected Clerk key initialization not found; refusing unsafe patch.")
    app = app.replace(old_clerk_key, new_clerk_key, 1)
    app_path.write_text(app, encoding="utf-8")

api = api_path.read_text(encoding="utf-8")
if "https://localhost" not in api:
    api = api.replace('''  "http://localhost:5173",
]) {''', '''  "http://localhost:5173",
  // Capacitor Android WebView origins for native requests to the configured HTTPS API.
  "https://localhost",
  "http://localhost",
  "capacitor://localhost",
]) {''', 1)
if 'app.disable("x-powered-by")' not in api:
    api = api.replace("const app: Express = express();", '''const app: Express = express();
app.disable("x-powered-by");
app.use((_req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Permissions-Policy", "camera=(self), microphone=(), geolocation=()");
  if (process.env.NODE_ENV === "production" && process.env.APP_BASE_URL?.startsWith("https://")) {
    res.setHeader("Strict-Transport-Security", "max-age=15552000");
  }
  next();
});''', 1)
api = api.replace("app.use(express.json());\napp.use(express.urlencoded({ extended: true }));",
                  'app.use(express.json({ limit: "256kb", strict: true }));\napp.use(express.urlencoded({ extended: true, limit: "64kb", parameterLimit: 100 }));', 1)
api_path.write_text(api, encoding="utf-8")

env_path = root / ".env.example"
env = env_path.read_text(encoding="utf-8")
if "VITE_API_BASE_URL=" not in env: env += "\n# Optional native API origin; production must use HTTPS.\nVITE_API_BASE_URL=\n"
if "VITE_MOBILE_PREVIEW=" not in env: env += "# Set true only for an unconnected debug APK.\nVITE_MOBILE_PREVIEW=false\n"
env_path.write_text(env, encoding="utf-8")

(root / "MOBILE_BUILD.md").write_text('''# بناء Android (APK)

يستخدم تطبيق Android واجهة React الحالية وAPI الحالي عبر Capacitor، دون استبدال المشروع أو إضافة بيانات وهمية.

## المتطلبات
- Node.js 22+ وpnpm 10 وJDK 21 وAndroid SDK API 36.
- تثبيت ناجح ومتوافق مع ملف القفل.
- خادم API عبر HTTPS مع PostgreSQL وClerk والتخزين الخاص المضبوطين.

## إعداد نسخة متصلة
اضبط VITE_API_BASE_URL على أصل الخادم، مثل https://api.example.com دون /api. اضبط VITE_CLERK_PUBLISHABLE_KEY وVITE_CLERK_PROXY_URL حسب إعداد Clerk. لا تضع CLERK_SECRET_KEY أو DATABASE_URL أو TEACHER_SETUP_TOKEN في التطبيق أو ملفات Vite.

## البناء
من مجلد artifacts/barakat-chemistry:
- pnpm run build
- pnpm exec cap add android (مرة واحدة فقط)
- pnpm exec cap sync android
- cd android && ./gradlew assembleDebug

المخرج android/app/build/outputs/apk/debug/app-debug.apk. نسخة Debug مخصصة للاختبار وليست موقعة للنشر بالمتجر. توقيع الإنتاج يحتاج مفتاحاً خاصاً خارج المستودع.

عند غياب أصل API أو مفتاح Clerk ينتج APK معاينة فقط: الصفحة العامة والملزمة تعملان محلياً، وتبقى المصادقة والواجبات معطلة برسالة واضحة. لا تدخل بيانات حسابك في تلك النسخة.
''', encoding="utf-8")

check_path = root / "scripts/check-project.mjs"
checker = check_path.read_text(encoding="utf-8")
if "Capacitor Android configuration supports HTTPS and a local static bundle" not in checker:
    marker = "let failed = 0;"
    extra = r'''await check('Capacitor Android configuration supports HTTPS and a local static bundle', async () => {
  const cfg = await readFile(path.join(root, 'artifacts/barakat-chemistry/capacitor.config.ts'), 'utf8');
  const pkg = JSON.parse(await readFile(path.join(root, 'artifacts/barakat-chemistry/package.json'), 'utf8'));
  if (!cfg.includes('appId: "iq.barakatchemistry.institute"') || !cfg.includes('webDir: "dist/public"') || !cfg.includes('androidScheme: "https"') || !cfg.includes('cleartext: false')) throw new Error('إعداد Capacitor لا يثبت الحزمة أو HTTPS أو مسار البناء');
  for (const dep of ['@capacitor/core', '@capacitor/android', '@capacitor/app']) if (!pkg.dependencies?.[dep]) throw new Error('اعتماد Capacitor مفقود: ' + dep);
  if (!pkg.devDependencies?.['@capacitor/cli']) throw new Error('أداة Capacitor CLI مفقودة');
  return 'Capacitor يحدد الحزمة وHTTPS ومسار ملفات الواجهة';
});

await check('Android API origin and native back behaviour are configured', async () => {
  const main = await readFile(path.join(root, 'artifacts/barakat-chemistry/src/main.tsx'), 'utf8');
  const app = await readFile(path.join(root, 'artifacts/barakat-chemistry/src/App.tsx'), 'utf8');
  if (!main.includes('VITE_API_BASE_URL') || !main.includes('setBaseUrl(parsedApiOrigin.origin)')) throw new Error('أصل API البعيد غير مدعوم');
  if (!app.includes('Capacitor.isNativePlatform()') || !app.includes("CapacitorApp.addListener('backButton'")) throw new Error('زر الرجوع الأصلي غير معالج');
  return 'أصل API اختياري ومدقق، وزر الرجوع الأصلي معالج';
});

await check('Unconfigured preview APK clearly disables real authentication controls', async () => {
  const app = await readFile(path.join(root, 'artifacts/barakat-chemistry/src/App.tsx'), 'utf8');
  const doc = await readFile(path.join(root, 'MOBILE_BUILD.md'), 'utf8');
  if (!app.includes('VITE_MOBILE_PREVIEW') || !app.includes('نسخة اختبار غير مرتبطة بالخادم') || !app.includes('MissingConfigurationPage')) throw new Error('حالة المعاينة لا توضح أن الخدمات غير مهيأة');
  if (!doc.includes('APK معاينة فقط') && !doc.includes('APK معاينة')) throw new Error('توثيق حالة APK المعيّنة مفقود');
  return 'لا توجد أزرار دخول شكلية عندما تكون الخدمات الخارجية غير مهيأة';
});

await check('API has bounded body parsers and mobile-origin CORS allow-list', async () => {
  const api = await readFile(path.join(root, 'artifacts/api-server/src/app.ts'), 'utf8');
  for (const token of ['https://localhost', 'capacitor://localhost', 'express.json({ limit: "256kb", strict: true })', 'parameterLimit: 100', 'X-Content-Type-Options', 'Referrer-Policy', 'app.disable("x-powered-by")']) if (!api.includes(token)) throw new Error('حماية API مفقودة: ' + token);
  return 'حدود جسم الطلب ورؤوس الأمان وأصول Android مضافة';
});

'''
    if marker not in checker: raise SystemExit("Static checker insertion point missing")
    check_path.write_text(checker.replace(marker, extra + marker, 1), encoding="utf-8")

project_script = root / "scripts/prepare-android-build.py"
if Path(__file__).resolve() != project_script.resolve():
    project_script.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
print("Android source preparation complete.")
