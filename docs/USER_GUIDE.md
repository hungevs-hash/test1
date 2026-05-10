# User Guide

## Khởi động
1. Mở `run_app.bat` hoặc chạy:
   - `pip install -r requirements.txt`
   - `streamlit run app.py`
2. Truy cập URL local do Streamlit cung cấp.

## Đăng nhập
- admin / admin123
- editor / editor123
- viewer / viewer123

## Tác vụ chính
- Cases: xem/tìm/tạo/cập nhật ca bệnh.
- Tests: thêm và xem kết quả xét nghiệm.
- Excel: import/export dữ liệu.
- Dashboard: tổng hợp biểu đồ.
- Audit: xem lịch sử chỉnh sửa.

## Chạy bản EXE (không cần gõ lệnh)
### Build trên máy dev
1. Chạy `build_exe.bat`
2. Lấy file: `dist\\CaseManagerLauncher\\CaseManagerLauncher.exe`

### Chạy trên máy người dùng
- Chạy trực tiếp `CaseManagerLauncher.exe`.
- Trình duyệt sẽ mở giao diện app local.
