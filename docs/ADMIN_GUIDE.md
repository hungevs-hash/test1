# Admin Guide

## Quản lý trường dữ liệu động
- Vào menu `Fields` để thêm trường mới.
- Nên đặt `field_key` không dấu, không khoảng trắng.

## Quản lý tài khoản
- Tài khoản mẫu đang cấu hình cứng trong `app.py` (`USERS`).
- Khi triển khai thực tế, cần đổi mật khẩu mặc định.

## Vận hành
- Backup định kỳ bằng script `python scripts/backup.py`.
- Kiểm tra dữ liệu và audit log hàng tuần.

## Đóng gói EXE
- Cài dependency: `pip install -r requirements.txt`
- Build: `build_exe.bat`
- Artifact: `dist/CaseManagerLauncher/CaseManagerLauncher.exe`
- Khi bàn giao nên gửi kèm thư mục chứa `app.py`, `data.db` (nếu có), `docs/`.
