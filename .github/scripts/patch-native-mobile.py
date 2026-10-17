#!/usr/bin/env python3
"""Apply focused Android branding, photo picker and notification-permission updates."""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
frontend = root / "artifacts/barakat-chemistry"
app_path = frontend / "src/App.tsx"
css_path = frontend / "src/index.css"
pkg_path = frontend / "package.json"
checker_path = root / "scripts/check-project.mjs"
manifest_path = frontend / "public/manifest.webmanifest"
required = [app_path, css_path, pkg_path, checker_path, manifest_path]
missing = [str(p.relative_to(root)) for p in required if not p.is_file()]
if missing:
    raise SystemExit("Native UX patch refused: missing expected files: " + ", ".join(missing))

pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
deps = pkg.setdefault("dependencies", {})
deps["@capacitor/camera"] = "8.2.4"
deps["@capacitor/local-notifications"] = "8.3.1"
pkg.setdefault("devDependencies", {})["@capacitor/assets"] = "3.0.5"
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assets = frontend / "assets"
public = frontend / "public"
assets.mkdir(parents=True, exist_ok=True)

logo_svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<defs>
 <linearGradient id="blue" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#43D7FF"/><stop offset="1" stop-color="#075CC8"/></linearGradient>
 <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFE89B"/><stop offset="1" stop-color="#C88A0B"/></linearGradient>
 <linearGradient id="navy" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#174883"/><stop offset="1" stop-color="#061128"/></linearGradient>
</defs>
<rect width="512" height="512" rx="112" fill="#08142C"/>
<circle cx="256" cy="255" r="204" fill="none" stroke="#D7A42A" stroke-width="5"/>
<circle cx="256" cy="255" r="184" fill="none" stroke="#244E83" stroke-width="12"/>
<path d="M72 329Q164 297 256 387Q348 297 440 329L440 368Q344 342 256 429Q168 342 72 368Z" fill="url(#gold)"/>
<path d="M86 351Q171 330 256 416Q341 330 426 351L426 374Q340 355 256 449Q172 355 86 374Z" fill="#F7FAFF"/>
<path d="M148 84L256 44L364 84L256 132Z" fill="url(#navy)" stroke="#EAF4FF" stroke-width="8" stroke-linejoin="round"/>
<path d="M190 102V132Q256 171 322 132V102L256 132Z" fill="#143C70"/>
<path d="M354 84L385 98V145" fill="none" stroke="url(#gold)" stroke-width="8" stroke-linecap="round"/>
<circle cx="385" cy="156" r="10" fill="url(#gold)"/>
<path d="M375 166H395L400 194Q385 207 370 194Z" fill="url(#gold)"/>
<path d="M229 153H283V210L327 293Q339 317 317 335L256 381L195 335Q173 317 185 293L229 210Z" fill="#F7FBFF" stroke="#174883" stroke-width="9" stroke-linejoin="round"/>
<path d="M240 174H272V216L310 286Q318 300 304 311L256 348L208 311Q194 300 202 286L240 216Z" fill="url(#blue)"/>
<circle cx="249" cy="249" r="8" fill="#EBFAFF"/><circle cx="274" cy="274" r="6" fill="#D0F6FF"/><circle cx="239" cy="289" r="5" fill="#A7EDFF"/>
<path d="M213 153H299" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/>
</svg>'''
brand_logo_svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="700" viewBox="0 0 700 700">
<defs><linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F8D778"/><stop offset="1" stop-color="#C88B10"/></linearGradient></defs>
<rect width="700" height="700" rx="42" fill="#FFFFFF"/>
<image href="logo.svg" x="170" y="20" width="360" height="360" preserveAspectRatio="xMidYMid meet"/>
<text x="350" y="455" font-family="Arial, Tahoma, sans-serif" font-size="47" font-weight="700" text-anchor="middle" direction="rtl" fill="#0A2350">معهد أستاذ بركات</text>
<text x="350" y="508" font-family="Arial, Tahoma, sans-serif" font-size="31" font-weight="700" text-anchor="middle" direction="rtl" fill="#C88B10">للدروس الخصوصية</text>
<path d="M115 575H245M455 575H585" stroke="url(#gold)" stroke-width="5" stroke-linecap="round"/>
<g transform="translate(350 575)" fill="none" stroke="#0A2350" stroke-width="4"><ellipse rx="18" ry="42" transform="rotate(45)"/><ellipse rx="18" ry="42" transform="rotate(-45)"/><ellipse rx="18" ry="42"/><circle r="6" fill="#0A2350"/></g>
</svg>'''
(assets / "logo.svg").write_text(logo_svg + "\n", encoding="utf-8")
(public / "logo.svg").write_text(logo_svg + "\n", encoding="utf-8")
(public / "favicon.svg").write_text(logo_svg + "\n", encoding="utf-8")
(public / "brand-logo.svg").write_text(brand_logo_svg + "\n", encoding="utf-8")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["name"] = "معهد أستاذ بركات — كيمياء السادس الإعدادي"
manifest["short_name"] = "معهد بركات"
manifest["lang"] = "ar"
manifest["dir"] = "rtl"
manifest["icons"] = [{"src": "./logo.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

app = app_path.read_text(encoding="utf-8")
if "BARAKAT_NATIVE_PHOTO_NOTIFICATIONS_V1" not in app:
    app = app.replace(
        "import { App as CapacitorApp } from '@capacitor/app';",
        "import { App as CapacitorApp } from '@capacitor/app';\nimport { Camera as NativeCamera, CameraResultType, CameraSource } from '@capacitor/camera';\nimport { LocalNotifications } from '@capacitor/local-notifications';",
        1
    )
    if "<FlaskConical /><span /></span>;" not in app:
        raise SystemExit("Cannot safely replace the brand mark; App.tsx structure changed.")
    app = app.replace("<FlaskConical /><span /></span>;", "<img src={basePath + '/logo.svg'} alt=\"\" /></span>;", 1)

    upload_start = app.find("function UploadQueue({ files, setFiles, disabled }")
    upload_end = app.find("function FileThumb(", upload_start)
    if upload_start < 0 or upload_end < 0:
        raise SystemExit("Cannot safely locate upload controls.")
    upload_fn = r'''function UploadQueue({ files, setFiles, disabled }: { files: File[]; setFiles: (f: File[]) => void; disabled?: boolean }) {
  const [pickerBusy, setPickerBusy] = useState(false);
  const [pickerError, setPickerError] = useState('');
  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return;
    const received = Array.from(incoming);
    const valid = received.filter(f => /^(image\/(jpeg|png|webp)|application\/pdf)$/.test(f.type) && f.size > 0 && f.size <= 10 * 1024 * 1024);
    const remaining = Math.max(0, 20 - files.length);
    setFiles([...files, ...valid.slice(0, remaining)]);
    if (received.length > 0 && valid.length === 0) setPickerError('الصورة أو الملف غير مدعوم أو أكبر من 10 ميغابايت.');
    else if (valid.length > remaining) setPickerError('الحد الأقصى 20 ملفاً للواجب.');
    else setPickerError('');
  };
  const convertPickedImage = async (webPath: string, format?: string) => {
    const response = await fetch(webPath);
    if (!response.ok) throw new Error('تعذر فتح الصورة المختارة من الهاتف.');
    const blob = await response.blob();
    const fallbackType = format === 'png' ? 'image/png' : format === 'webp' ? 'image/webp' : 'image/jpeg';
    const mime = blob.type || fallbackType;
    if (!/^(image\/jpeg|image\/png|image\/webp)$/.test(mime)) throw new Error('نوع الصورة غير مدعوم. اختر JPG أو PNG أو WEBP.');
    if (blob.size <= 0 || blob.size > 10 * 1024 * 1024) throw new Error('حجم الصورة يجب ألا يتجاوز 10 ميغابايت.');
    const extension = mime === 'image/png' ? 'png' : mime === 'image/webp' ? 'webp' : 'jpg';
    const fileName = 'solution-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7) + '.' + extension;
    return new File([blob], fileName, { type: mime, lastModified: Date.now() });
  };
  const pickFromGallery = async () => {
    if (disabled || pickerBusy || files.length >= 20) return;
    setPickerError('');
    setPickerBusy(true);
    try {
      const result = await NativeCamera.pickImages({ quality: 88, limit: Math.max(1, 20 - files.length) });
      const chosen: File[] = [];
      for (const photo of result.photos) {
        if (!photo.webPath) continue;
        chosen.push(await convertPickedImage(photo.webPath, photo.format));
      }
      const remaining = Math.max(0, 20 - files.length);
      setFiles([...files, ...chosen.slice(0, remaining)]);
      if (chosen.length > remaining) setPickerError('تمت إضافة 20 ملفاً فقط؛ أزل ملفاً لإضافة المزيد.');
    } catch (error) {
      const message = error instanceof Error ? error.message : '';
      if (!/cancel|cancelled|canceled|OS-PLUG-CAMR-0006/i.test(message)) setPickerError(message || 'تعذر فتح معرض الصور. جرّب اختيار صور أو PDF.');
    } finally {
      setPickerBusy(false);
    }
  };
  const takePhoto = async () => {
    if (disabled || pickerBusy || files.length >= 20) return;
    setPickerError('');
    setPickerBusy(true);
    try {
      const photo = await NativeCamera.getPhoto({ quality: 90, allowEditing: false, resultType: CameraResultType.Uri, source: CameraSource.Camera, correctOrientation: true });
      if (!photo.webPath) throw new Error('لم تُرجع الكاميرا صورة صالحة.');
      const file = await convertPickedImage(photo.webPath, photo.format);
      setFiles([...files, file].slice(0, 20));
    } catch (error) {
      const message = error instanceof Error ? error.message : '';
      if (!/cancel|cancelled|canceled|OS-PLUG-CAMR-0006/i.test(message)) setPickerError(message || 'تعذر تشغيل الكاميرا. يمكنك اختيار صورة من المعرض.');
    } finally {
      setPickerBusy(false);
    }
  };
  return <div className="upload-area">
    <div className="upload-controls">
      {Capacitor.isNativePlatform() && <button type="button" className="upload-pick native-upload-button" disabled={disabled || pickerBusy || files.length >= 20} onClick={() => void pickFromGallery()} data-testid="button-native-pick-photos"><ImagePlus size={17} /> {pickerBusy ? 'جارٍ تجهيز الصورة…' : 'اختيار من المعرض'}</button>}
      <label className={"upload-pick " + (disabled ? "disabled" : "")}><input type="file" accept="image/jpeg,image/png,image/webp,application/pdf" multiple disabled={disabled} onChange={e => { addFiles(e.target.files); e.currentTarget.value = ''; }} data-testid="input-solution-files" /><Upload size={17} /> اختيار صور أو PDF</label>
      {Capacitor.isNativePlatform()
        ? <button type="button" className="upload-pick native-upload-button" disabled={disabled || pickerBusy || files.length >= 20} onClick={() => void takePhoto()} data-testid="button-native-take-photo"><Camera size={17} /> التقاط صورة</button>
        : <label className={"upload-pick camera-pick " + (disabled ? "disabled" : "")}><input type="file" accept="image/*" capture="environment" disabled={disabled} onChange={e => { addFiles(e.target.files); e.currentTarget.value = ''; }} data-testid="input-camera-file" /><Camera size={17} /> التقاط صورة</label>}
    </div>
    {pickerError && <p className="inline-error upload-picker-error" role="alert">{pickerError}</p>}
    <small>اختر الصور من المعرض أو التقطها بالكاميرا أو أرفق PDF. الأنواع المسموحة JPG وPNG وWEBP وPDF، حتى 10 ميغابايت للملف، وبحد أقصى 20 ملفاً.</small>
    {files.length > 0 && <div className="file-preview-list">{files.map((file, i) => <div className="file-preview" key={file.name + '-' + file.lastModified + '-' + i} data-testid={'file-preview-' + i}><FileThumb file={file} /><div><b>{file.name}</b><small>{(file.size / 1024 / 1024).toFixed(1)} ميغابايت</small></div><div className="file-order"><button type="button" onClick={() => { if (i > 0) { const next = [...files]; [next[i - 1], next[i]] = [next[i], next[i - 1]]; setFiles(next); } }} disabled={i === 0} aria-label="رفع الملف للأعلى" data-testid={'button-move-up-' + i}><ArrowRight size={15} /></button><button type="button" onClick={() => { if (i < files.length - 1) { const next = [...files]; [next[i + 1], next[i]] = [next[i], next[i + 1]]; setFiles(next); } }} disabled={i === files.length - 1} aria-label="خفض الملف للأسفل" data-testid={'button-move-down-' + i}><ArrowLeft size={15} /></button></div><button type="button" className="icon-button remove-file" onClick={() => setFiles(files.filter((_, index) => index !== i))} aria-label="حذف الملف" data-testid={'button-remove-file-' + i}><X size={16} /></button></div>)}</div>}
  </div>;
}
'''
    app = app[:upload_start] + upload_fn + app[upload_end:]

    permission_component = r'''function NativeNotificationPermissionPrompt() {
  const [permission, setPermission] = useState('checking');
  const [message, setMessage] = useState('');
  const [dismissed, setDismissed] = useState(false);
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) { setPermission('unsupported'); return; }
    let cancelled = false;
    void LocalNotifications.checkPermissions().then(status => {
      if (cancelled) return;
      setPermission(status.display);
      if (status.display === 'granted') void LocalNotifications.createChannel({ id: 'barakat-general', name: 'إشعارات المعهد', description: 'تنبيهات الواجبات وتحديثات المعهد', importance: 5, visibility: 1 }).catch(() => {});
    }).catch(() => { if (!cancelled) setPermission('prompt'); });
    return () => { cancelled = true; };
  }, []);
  const requestPermission = async () => {
    setMessage('');
    try {
      const current = await LocalNotifications.checkPermissions();
      const result = current.display === 'granted' ? current : await LocalNotifications.requestPermissions();
      setPermission(result.display);
      if (result.display === 'granted') {
        await LocalNotifications.createChannel({ id: 'barakat-general', name: 'إشعارات المعهد', description: 'تنبيهات الواجبات وتحديثات المعهد', importance: 5, visibility: 1 });
        setMessage('تم تفعيل إذن إشعارات النظام. وصول التنبيهات والجهاز مغلق يحتاج أيضاً ربط Firebase بخادم المعهد.');
      } else {
        setMessage('الإذن غير مفعّل. افتح إعدادات الهاتف ثم التطبيقات ثم معهد بركات ثم الإشعارات وفعّلها.');
      }
    } catch {
      setMessage('تعذر طلب الإذن الآن. راجع إعدادات إشعارات التطبيق من إعدادات الهاتف.');
    }
  };
  if (!Capacitor.isNativePlatform() || permission === 'checking' || permission === 'unsupported' || permission === 'granted' || dismissed) return null;
  return <aside className="native-notification-permission" dir="rtl" role="region" aria-label="إذن إشعارات المعهد" data-testid="native-notification-permission">
    <span className="native-permission-icon"><Bell size={20} /></span>
    <div className="native-permission-copy"><b>فعّل إشعارات المعهد</b><p>حتى تصلك تنبيهات الواجبات والتحديثات على جهازك.</p>{message && <small role="status">{message}</small>}</div>
    <button type="button" className="native-permission-button" onClick={() => void requestPermission()} data-testid="button-native-notification-permission">السماح بالإشعارات</button>
    <button type="button" className="native-permission-later" onClick={() => setDismissed(true)} aria-label="لاحقاً">لاحقاً</button>
  </aside>;
}

'''
    prompt_marker = "const authConfigAvailable ="
    if prompt_marker not in app:
        raise SystemExit("Cannot locate the App component for notification permission UI.")
    app = app.replace(prompt_marker, permission_component + prompt_marker, 1)

    preview_return = "<WouterRouter base={basePath}><Switch><Route path=\"/\" component={() => <Home authAvailable={false} />} /><Route component={MissingConfigurationPage} /></Switch></WouterRouter><Toaster />"
    if preview_return not in app:
        raise SystemExit("Cannot locate preview render tree for permission UI.")
    app = app.replace(preview_return, preview_return.replace("<Toaster />", "<NativeNotificationPermissionPrompt /><Toaster />"), 1)
    regular_return = "<WouterRouter base={basePath}><Router /></WouterRouter><Toaster />"
    if regular_return not in app:
        raise SystemExit("Cannot locate normal render tree for permission UI.")
    app = app.replace(regular_return, regular_return.replace("<Toaster />", "<NativeNotificationPermissionPrompt /><Toaster />"), 1)

    old_permission_state = """const [permission, setPermission] = useState(
    typeof Notification === 'undefined' ? 'unsupported' : Notification.permission,
  );
  const [permissionMessage, setPermissionMessage] = useState('');"""
    new_permission_state = """const [permission, setPermission] = useState<string>(
    Capacitor.isNativePlatform() ? 'prompt' : (typeof Notification === 'undefined' ? 'unsupported' : Notification.permission),
  );
  const [permissionMessage, setPermissionMessage] = useState('');
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;
    void LocalNotifications.checkPermissions().then(status => setPermission(status.display)).catch(() => setPermission('prompt'));
  }, []);"""
    if old_permission_state not in app:
        raise SystemExit("Cannot safely update notification permission status.")
    app = app.replace(old_permission_state, new_permission_state, 1)

    native_permission_branch = """if (Capacitor.isNativePlatform()) {
      try {
        const current = await LocalNotifications.checkPermissions();
        const result = current.display === 'granted' ? current : await LocalNotifications.requestPermissions();
        setPermission(result.display);
        if (result.display === 'granted') {
          await LocalNotifications.createChannel({ id: 'barakat-general', name: 'إشعارات المعهد', description: 'تنبيهات الواجبات وتحديثات المعهد', importance: 5, visibility: 1 });
          setPermissionMessage('تم تفعيل إذن إشعارات النظام. التنبيهات عند إغلاق التطبيق تحتاج ربط Firebase بخادم المعهد.');
        } else {
          setPermissionMessage('لم يُسمح بالإشعارات. افتح إعدادات الهاتف ثم التطبيقات ثم معهد بركات ثم الإشعارات.');
        }
      } catch {
        setPermissionMessage('تعذر طلب الإذن حالياً. راجع إعدادات إشعارات التطبيق من إعدادات الهاتف.');
      }
      return;
    }
    if (typeof Notification === 'undefined') {"""
    if "const enableNotifications = async () => {" not in app:
        raise SystemExit("Cannot locate notification request handler.")
    app = app.replace("    if (typeof Notification === 'undefined') {", "    " + native_permission_branch, 1)

    old_action = """action={permission === 'granted' ? <span className="inline-info notification-permission">تنبيهات المتصفح مفعلة أثناء استخدام الموقع</span> : <Button variant="outline" onClick={() => void enableNotifications()} testId="button-enable-notifications"><Bell size={15} /> تفعيل تنبيهات المتصفح</Button>}"""
    new_action = """action={permission === 'granted' ? <span className="inline-info notification-permission">{Capacitor.isNativePlatform() ? 'إشعارات الهاتف مفعلة' : 'تنبيهات المتصفح مفعلة أثناء استخدام الموقع'}</span> : <Button variant="outline" onClick={() => void enableNotifications()} testId="button-enable-notifications"><Bell size={15} /> {Capacitor.isNativePlatform() ? 'تفعيل إشعارات الهاتف' : 'تفعيل تنبيهات المتصفح'}</Button>}"""
    if old_action not in app:
        raise SystemExit("Cannot update notification page action label.")
    app = app.replace(old_action, new_action, 1)

    bridge_start = app.find("function BrowserNotificationBridge() {")
    bridge_end = app.find("function TeacherDashboard(", bridge_start)
    if bridge_start < 0 or bridge_end < 0:
        raise SystemExit("Cannot locate notifications bridge.")
    bridge = r'''function notificationNumericId(value: string) {
  let hash = 0;
  for (let i = 0; i < value.length; i++) hash = (Math.imul(hash, 31) + value.charCodeAt(i)) | 0;
  return (hash & 0x7fffffff) || 1;
}

function BrowserNotificationBridge() {
  const q = useListNotifications({
    query: {
      queryKey: getListNotificationsQueryKey(),
      refetchInterval: 60000,
    },
  });
  const seen = useRef(new Set<string>());
  const initialLoad = useRef(true);

  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;
    let disposed = false;
    let listener: { remove: () => Promise<void> } | undefined;
    void LocalNotifications.addListener('localNotificationActionPerformed', action => {
      const target = action.notification.extra?.url;
      if (typeof target === 'string' && target.startsWith('/')) window.location.assign(basePath + target);
    }).then(handle => {
      if (disposed) void handle.remove();
      else listener = handle;
    }).catch(() => {});
    return () => {
      disposed = true;
      if (listener) void listener.remove();
    };
  }, []);

  useEffect(() => {
    if (!q.data) return;
    if (initialLoad.current) {
      q.data.forEach((item) => seen.current.add(item.id));
      initialLoad.current = false;
      return;
    }
    for (const item of q.data) {
      if (seen.current.has(item.id)) continue;
      seen.current.add(item.id);
      if (item.readAt) continue;
      const targetUrl = item.assignmentId ? '/student/assignment/' + item.assignmentId : '/';
      if (Capacitor.isNativePlatform()) {
        void LocalNotifications.checkPermissions().then(status => {
          if (status.display !== 'granted') return;
          return LocalNotifications.schedule({ notifications: [{
            id: notificationNumericId(item.id),
            title: item.title,
            body: item.body,
            schedule: { at: new Date(Date.now() + 1000) },
            channelId: 'barakat-general',
            extra: { url: targetUrl },
          }] });
        }).catch(() => {});
        continue;
      }
      if (typeof Notification === 'undefined' || Notification.permission !== 'granted') continue;
      const options: NotificationOptions = {
        body: item.body,
        tag: item.id,
        icon: basePath + '/logo.svg',
        data: { url: targetUrl },
      };
      void navigator.serviceWorker?.ready
        .then((registration) => registration.showNotification(item.title, options))
        .catch(() => {
          const notification = new Notification(item.title, options);
          notification.onclick = () => { window.location.assign(options.data?.url ?? '/'); };
        });
    }
  }, [q.data]);
  return null;
}

'''
    app = app[:bridge_start] + bridge + app[bridge_end:]
    app = app.replace("BARAKAT_CAPACITOR_INTEGRATION", "BARAKAT_CAPACITOR_INTEGRATION\n// BARAKAT_NATIVE_PHOTO_NOTIFICATIONS_V1", 1)
    app_path.write_text(app, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
if "native-notification-permission" not in css:
    css += r'''

/* Barakat native Android photo picker and notification-permission UI */
.brand-mark { overflow:hidden; }
.brand-mark img { display:block;width:100%;height:100%;object-fit:cover;border-radius:inherit; }
.brand-mark-small img { width:100%;height:100%; }
.native-upload-button { appearance:none;font-family:inherit; }
.native-upload-button:disabled { opacity:.45;cursor:not-allowed; }
.upload-picker-error { margin:10px 2px 0; }
.native-notification-permission { position:fixed;z-index:9998;left:max(14px,env(safe-area-inset-left));right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom));max-width:760px;margin-inline:auto;display:flex;align-items:center;gap:12px;padding:14px 15px;border:1px solid rgba(8,185,245,.35);border-radius:17px;background:rgba(8,20,44,.97);box-shadow:0 16px 50px rgba(0,0,0,.4),inset 0 0 24px rgba(8,185,245,.06);backdrop-filter:blur(18px);color:#F4F7FF; }
.native-permission-icon { flex:0 0 40px;width:40px;height:40px;display:grid;place-items:center;border-radius:12px;background:rgba(8,185,245,.12);color:#59D4FA; }
.native-permission-copy { flex:1;min-width:0; }
.native-permission-copy b { display:block;font-size:13px;color:#F4F7FF; }
.native-permission-copy p { font-size:11px;color:#A7B5D0;line-height:1.7;margin:4px 0 0; }
.native-permission-copy small { display:block;color:#F7D78A;font-size:10px;line-height:1.7;margin-top:5px; }
.native-permission-button { border:1px solid #1D76AB;border-radius:10px;background:linear-gradient(120deg,#174883,#087DB7);padding:10px 13px;color:#FFF;font-size:11px;font-family:inherit;font-weight:700;white-space:nowrap;cursor:pointer; }
.native-permission-later { align-self:flex-start;border:0;background:transparent;color:#95A8C7;font-family:inherit;font-size:10px;padding:2px;cursor:pointer; }
@media (max-width:560px) { .native-notification-permission { align-items:flex-start;flex-wrap:wrap;gap:10px;padding:12px; } .native-permission-icon { width:34px;height:34px;flex-basis:34px; } .native-permission-copy { width:calc(100% - 52px);flex:1; } .native-permission-button { margin-inline-start:44px; } .native-permission-later { margin-inline-start:auto; } }
'''
    css_path.write_text(css, encoding="utf-8")

doc_path = root / "MOBILE_BUILD.md"
if doc_path.is_file():
    doc = doc_path.read_text(encoding="utf-8")
    if "## الصور وإشعارات Android" not in doc:
        doc += r'''

## الصور وإشعارات Android

- يستخدم التطبيق منتقي صور Android الأصلي وزر الكاميرا، مع بديل لاختيار صور أو PDF؛ الحد الأقصى 20 ملفاً و10 ميغابايت لكل ملف.
- مصدر الشعار في مجلد assets ويُستخدم لأيقونة التطبيق وفي واجهة المعهد.
- يظهر طلب إذن إشعارات النظام بعد تثبيت التطبيق، ويختفي إذا كان الإذن ممنوحاً بالفعل.
- إذن الإشعارات المحلي لا يفعّل رسائل Push عند إغلاق التطبيق. يلزم إعداد Firebase Cloud Messaging وربط رموز الجهاز بخادم HTTPS لتسليم الإشعارات عن بعد.
- حفظ الصور في مساحة التخزين الخاصة يحتاج API منشوراً عبر HTTPS وإعداد Clerk وقاعدة البيانات والتخزين؛ اختيار الصورة ومعاينتها لا يعني أنها حُفظت على الخادم.
'''
        doc_path.write_text(doc, encoding="utf-8")

checker = checker_path.read_text(encoding="utf-8")
check_title = "Barakat logo, Android gallery/camera picker and system notification permission are wired"
if check_title not in checker:
    marker = "let failed = 0;"
    additions = r'''await check('Barakat logo, Android gallery/camera picker and system notification permission are wired', async () => {
  const app = await readFile(path.join(root, 'artifacts/barakat-chemistry/src/App.tsx'), 'utf8');
  const icon = await readFile(path.join(root, 'artifacts/barakat-chemistry/assets/logo.svg'), 'utf8');
  const brand = await readFile(path.join(root, 'artifacts/barakat-chemistry/public/brand-logo.svg'), 'utf8');
  const pkg = JSON.parse(await readFile(path.join(root, 'artifacts/barakat-chemistry/package.json'), 'utf8'));
  for (const token of ['NativeCamera.pickImages', 'NativeCamera.getPhoto', 'LocalNotifications.requestPermissions', 'LocalNotifications.createChannel', 'native-notification-permission', 'button-native-pick-photos']) {
    if (!app.includes(token)) throw new Error('ميزة Android غير مربوطة: ' + token);
  }
  if (!icon.includes('#08142C') || !brand.includes('معهد أستاذ بركات') || !app.includes("src={basePath + '/logo.svg'}")) throw new Error('شعار المعهد غير مربوط بالواجهة أو الأيقونة');
  for (const dep of ['@capacitor/camera', '@capacitor/local-notifications']) if (!pkg.dependencies?.[dep]) throw new Error('اعتماد Android مفقود: ' + dep);
  if (!pkg.devDependencies?.['@capacitor/assets']) throw new Error('مولد موارد أيقونة التطبيق مفقود');
  return 'أيقونة الهوية، معرض الصور، الكاميرا وإذن إشعارات Android موجودة';
});

'''
    if marker not in checker:
        raise SystemExit("Cannot extend static checks: insertion marker was not found.")
    checker_path.write_text(checker.replace(marker, additions + marker, 1), encoding="utf-8")

print("Applied native branding, Android gallery/camera picker and notification permission.")
