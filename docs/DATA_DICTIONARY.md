# Data Dictionary

## field_defs
- `field_key`: key kỹ thuật của trường
- `label_vi`, `label_en`: nhãn hiển thị
- `field_type`: text/number/date
- `active`: 1/0

## cases
- `case_code`: mã ca duy nhất
- `data_json`: dữ liệu ca bệnh dạng JSON
- `created_by`, `created_at`, `updated_by`, `updated_at`

## test_results
- `case_code`: liên kết ca bệnh
- `test_type`: A/B/PCR/NGS/Other
- `result_value`, `result_date`, `note`
- `updated_by`, `updated_at`

## audit_logs
- `table_name`, `record_key`, `field_name`
- `old_value`, `new_value`
- `updated_by`, `updated_at`, `reason`
