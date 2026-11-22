# k8sfinal · CT665 · 039

เผด็จ แสงบุษราคัม · รหัสนักศึกษา 68130039 · namespace `id-039`

| URL | Deployment | ผลที่แสดง |
| --- | --- | --- |
| `http://www.iam-039.com/` | `portal-039` | รูป ชื่อ และรหัสนักศึกษา |
| `http://www.iam-039.com/research` | `app-research` | ร่างบทสรุปงานวิจัย 365 คำตาม PyThaiNLP |
| `http://www.iam-039.com/api-039/CT665` | `api-039` | ข้อความ CT665 ตัวใหญ่กลางจอ |
| `http://admin.iam-039.com/` | `admin-039` | เมนูแก้ชื่อและรหัสบน Portal หรือแก้บทสรุป Research |

ชุดนี้ใช้ kind **Single-node** และรันทุกบริการบนเครื่องผู้จัดทำ.

## เตรียมเครื่องและติดตั้ง

ต้องมี Docker ที่กำลังทำงาน, kind, kubectl, Bash และ OpenSSL ถ้าใช้ Windows ให้รันด้วย Git Bash หรือรัน `deploy.bat` แทน `bash deploy.sh` ใช้พอร์ต 80 ของเครื่องผ่าน loopback เท่านั้น

```bash
bash deploy.sh cluster
bash deploy.sh build
bash deploy.sh secret
bash deploy.sh deploy
```

1. `cluster` ใช้ `kind create cluster --name k8sfinal --config kind/cluster.yaml` สร้างหนึ่ง control-plane ที่รัน workloads ได้
2. `build` ใช้ `docker build -t localhost/id039-web:4.0 apps` และ `kind load docker-image localhost/id039-web:4.0 --name k8sfinal`
3. `secret` รับ username/password ผ่าน prompt สุ่ม session key ด้วย OpenSSL แล้วใช้ `kubectl create secret generic` ชื่อ `research-editor-secret` เก็บใน namespace `id-039`
4. `deploy` ตรวจจำนวนโหนด เตรียมไดเรกทอรี storage บน kind node จากนั้นใช้ `kubectl apply --dry-run=server -f k8s/` และ `kubectl apply -f k8s/` แล้วรอ Deployment ทั้งหมดพร้อม

เพิ่มบรรทัดจาก `config/hosts.example` ลง `/etc/hosts` บน Linux/macOS หรือ `C:\Windows\System32\drivers\etc\hosts` บน Windows ด้วยสิทธิ์ผู้ดูแล

```text
127.0.0.1 www.iam-039.com admin.iam-039.com
```

ถ้าพอร์ต 80 ถูกใช้ ให้หยุดบริการที่ใช้พอร์ตนั้นก่อนสร้างคลัสเตอร์ HTTP Basic ใช้ได้ในแล็บ loopback นี้ เปิด URL ด้วย `http://` หากเบราว์เซอร์อัปเกรด HTTP เป็น HTTPS อัตโนมัติ ให้ใช้ curl ตรวจสอบหรือปิด HTTPS-only สำหรับสองโฮสต์นี้ในโปรไฟล์ทดสอบ

## โครงสร้างและข้อมูล

- `kind/cluster.yaml` นิยามคลัสเตอร์และ mapping `127.0.0.1:80 → 30080`
- `apps/` Dockerfile, แอป Flask สี่ entry point, templates, CSS, รูป และร่างบทสรุป
- `k8s/` Namespace, PV/PVC, Deployment และ Service ของสี่แอป รวม ConfigMap, Deployment และ NodePort Service ของ NGINX gateway
- `config/hosts.example` รายการชื่อโฮสต์
- `deploy.sh` กับ `deploy.bat` ขั้นตอนติดตั้งและ deploy

NGINX ส่ง Host และ path ไปยัง ClusterIP Services ที่พอร์ต 80 โดยแอปรับที่พอร์ต 5000 Admin ใช้ PVC เขียนไฟล์ Portal และ Research ส่วนหน้า public mount แบบอ่านอย่างเดียว PV แบบ hostPath เก็บข้อมูลใน kind node จึงคงอยู่เมื่อ Pod ถูกสร้างใหม่ การลบคลัสเตอร์จะลบข้อมูลใน node ด้วย รูปอยู่ใน `apps/static/padegh.jpg` และเปลี่ยนด้วยการ build ใหม่ เปรียบเทียบร่าง `apps/seed.txt` กับเนื้อหาที่นำเสนอจริงก่อนส่ง

## ตรวจสอบและเก็บหลักฐาน

```bash
kubectl --context kind-k8sfinal get nodes -o wide
kubectl --context kind-k8sfinal -n id-039 get deploy,pods,svc,pvc -o wide
kubectl --context kind-k8sfinal -n id-039 describe svc gateway-039-svc
kubectl --context kind-k8sfinal -n id-039 describe pvc site-content-pvc
curl --noproxy '*' -fsS http://www.iam-039.com/
curl --noproxy '*' -fsS http://www.iam-039.com/research
curl --noproxy '*' -fsS 'http://www.iam-039.com/api-039/CT665%20039'
curl --noproxy '*' -i http://admin.iam-039.com/
```

เกณฑ์ผ่านบนเครื่องคือ 1 node Ready, Deployment ทั้งห้าพร้อม 1/1, PVC Bound, หน้า public ตอบ 200 และ Admin ตอบ 401 ก่อนเข้าสู่ระบบ เปิดเบราว์เซอร์จับภาพ URL ทั้งสี่ และทดสอบบันทึกจากทั้งสองฟอร์ม ยืนยันว่าหน้าสาธารณะอ่านค่าล่าสุด จากนั้นรัน `bash deploy.sh deploy` อีกครั้งเพื่อสร้าง Pods ใหม่และตรวจข้อมูล

ถ้าพบ ErrImageNeverPull ให้รันขั้น build เพื่อโหลด image เข้า kind node ถ้า gateway ไม่พร้อม ให้ตรวจ `kubectl --context kind-k8sfinal -n id-039 logs deployment/gateway-039`

## GitHub Public

ตรวจไฟล์ที่จะเผยแพร่ รวมถึงชื่อ รูป รหัสนักศึกษา และบทสรุป ผ่าน GitHub CLI ที่ลงชื่อเข้าใช้แล้ว เก็บ kubeconfig, Secret และค่าที่บันทึกใน PV ไว้นอก Git

```bash
git init -b main
git add .
git diff --cached --stat
git commit -m "Add CT665 single-node kind deployment"
gh repo create k8sfinal --public --source=. --remote=origin --push
gh repo view --json url,visibility
```
