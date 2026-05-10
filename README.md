# Personal Case Manager (Full MVP)

Phần mềm quản lý ca bệnh cá nhân cho Windows, hỗ trợ Việt/Anh, nhập liệu linh động, quản lý xét nghiệm và theo dõi lịch sử chỉnh sửa.

## Chức năng chính
- Đăng nhập 3 vai trò: admin / editor / viewer.
- Cấu hình trường dữ liệu động (admin).
- Thêm/sửa ca bệnh, tự động sinh mã ca `CASE-YYYY-####`.
- Quản lý xét nghiệm A/B/PCR/NGS.
- Lưu audit log khi cập nhật hồ sơ ca bệnh.
- Import/Export Excel (`.xlsx`).
- Dashboard tổng hợp theo tháng.

## Cài đặt và chạy
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tài khoản test
- admin / admin123
- editor / editor123
- viewer / viewer123

## Quy ước
- Định dạng ngày: `dd/mm/yyyy`.
- Mã số có thể nhập từ Excel hoặc tự sinh tự động.

## Bàn giao kiểu công ty (phiên bản cá nhân)
- Checklist bàn giao: `docs/HANDOVER_CHECKLIST.md`
- Hướng dẫn người dùng: `docs/USER_GUIDE.md`
- Hướng dẫn admin: `docs/ADMIN_GUIDE.md`
- Backup/Restore: `docs/BACKUP_RESTORE.md`
- Data dictionary: `docs/DATA_DICTIONARY.md`
- Chạy nhanh Windows: `run_app.bat`
- Backup script: `scripts/backup.py`

## Build bản EXE (phổ biến cho người dùng Windows)
```bash
build_exe.bat
```

File EXE sau build:
- `dist/CaseManagerLauncher/CaseManagerLauncher.exe`

Chạy nhanh bản đã build:
- `run_portable.bat`

## Bản cuối kiểu phần mềm thường (có icon + installer)
Để tạo bản cài đặt cho người dùng cuối (không cần mở source):

1. Cài Inno Setup (để có lệnh `iscc`).
2. Chạy:
```bash
build_final_installer.bat
```
3. Nhận file cài đặt cuối:
- `dist_installer/CaseManagerSetup.exe`

Sau khi cài xong sẽ có shortcut trên Desktop/Start Menu (tùy chọn desktop icon trong wizard cài).

## Troubleshooting (Windows)
Nếu app bật lên rồi tắt ngay, hãy kiểm tra thư mục `logs/`:
- `logs/install.log`
- `logs/app.log`
- `logs/launcher.log`

Các script `.bat` đã được cập nhật để giữ cửa sổ và báo đường dẫn log lỗi.

## Tạo file cài đặt không cần Python (khuyến nghị)
Bạn **không cần cài Python trên máy người dùng cuối**. Dùng GitHub Actions để build tự động:

1. Vào tab `Actions` của repo.
2. Chọn workflow `Build Windows Installer`.
3. Bấm `Run workflow`.
4. Tải artifact `CaseManagerSetup` (file `CaseManagerSetup.exe`).

Sau đó gửi `CaseManagerSetup.exe` cho người dùng cài đặt như phần mềm bình thường.
