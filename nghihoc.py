
import json
import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, TemplateError

# Load .env (EMAIL_SENDER và EMAIL_PASSWORD - dùng App Password nếu có 2FA)
load_dotenv()

EMAIL = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("EMAIL_SENDER hoặc EMAIL_PASSWORD chưa được set trong .env!")

SUBJECT = "Thông báo nghỉ học"

# Đường dẫn thư mục chứa nghihoc.html và nghihoc.json
BASE_DIR = r"D:/Module_3/nghihoc"  # dùng raw string để tránh lỗi \

# Load JSON
json_path = os.path.join(BASE_DIR, "nghihoc.json")
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Không tìm thấy file JSON: {json_path}")

with open(json_path, encoding="utf-8") as f:
    student = json.load(f)

print("Dữ liệu học sinh:", student)  # Debug để kiểm tra

# Setup Jinja2
env = Environment(loader=FileSystemLoader(BASE_DIR))
try:
    template = env.get_template("nghihoc.html")
    html_content = template.render(**student)  # **student để unpack dict
except TemplateError as e:
    print("Lỗi render Jinja2:", e)
    raise

# Kết nối SMTP Gmail
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # Bật TLS
    server.login(EMAIL, PASSWORD)
    print("Login Gmail thành công!")

    # Tạo email
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Ban Giám Hiệu <{EMAIL}>"
    msg["To"] = student["email"]
    msg["Subject"] = SUBJECT

    # Text fallback (cho client không hỗ trợ HTML)
    text_part = MIMEText(
        f"Kính gửi phụ huynh học sinh {student['name']} (Lớp {student['class_name']}),\n"
        f"Thời gian nghỉ: {student['date']}\nLý do: {student['reason']}\n"
        "Chi tiết xem trong HTML.",
        "plain", "utf-8"
    )

    html_part = MIMEText(html_content, "html", "utf-8")

    msg.attach(text_part)
    msg.attach(html_part)

    # Gửi
    server.sendmail(EMAIL, student["email"], msg.as_string())
    print(f"✅ Đã gửi thành công đến: {student['email']}")

except smtplib.SMTPAuthenticationError:
    print("Lỗi xác thực: Kiểm tra App Password hoặc bật 2FA + tạo App Password mới!")
except Exception as e:
    print("Lỗi khi gửi email:", str(e))

finally:
    server.quit()