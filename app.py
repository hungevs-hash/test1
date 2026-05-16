import io
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path("data.db")
DATE_FMT = "%d/%m/%Y"

DEFAULT_FIELDS = [
    {"key": "case_code", "label_vi": "Mã số ca", "label_en": "Case code", "type": "text"},
    {"key": "lab_code", "label_vi": "Số Lab", "label_en": "Lab code", "type": "text"},
    {"key": "full_name", "label_vi": "Họ tên", "label_en": "Full name", "type": "text"},
    {"key": "birth_year", "label_vi": "Năm sinh", "label_en": "Birth year", "type": "number"},
    {"key": "age", "label_vi": "Tuổi", "label_en": "Age", "type": "number"},
    {"key": "gender", "label_vi": "Giới tính", "label_en": "Gender", "type": "text"},
    {"key": "address", "label_vi": "Địa chỉ", "label_en": "Address", "type": "text"},
    {"key": "hospital", "label_vi": "Bệnh viện gửi mẫu", "label_en": "Hospital", "type": "text"},
    {"key": "symptoms", "label_vi": "Triệu chứng", "label_en": "Symptoms", "type": "text"},
    {"key": "onset_date", "label_vi": "Ngày khởi phát", "label_en": "Onset date", "type": "date"},
    {"key": "sample_received_date", "label_vi": "Ngày nhận mẫu", "label_en": "Sample received date", "type": "date"},
]

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "editor": {"password": "editor123", "role": "editor"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}


def t(vi: str, en: str) -> str:
    return vi if st.session_state.get("lang", "vi") == "vi" else en


def db_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS field_defs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_key TEXT UNIQUE NOT NULL,
                label_vi TEXT NOT NULL,
                label_en TEXT NOT NULL,
                field_type TEXT NOT NULL CHECK(field_type IN ('text','number','date')),
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_code TEXT UNIQUE NOT NULL,
                data_json TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_by TEXT,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_code TEXT NOT NULL,
                test_type TEXT NOT NULL,
                result_value TEXT,
                result_date TEXT,
                note TEXT,
                updated_by TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_key TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                updated_by TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                reason TEXT
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM field_defs").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO field_defs(field_key,label_vi,label_en,field_type) VALUES(?,?,?,?)",
                [(f["key"], f["label_vi"], f["label_en"], f["type"]) for f in DEFAULT_FIELDS],
            )
        conn.commit()


def fetch_fields(active_only: bool = True) -> pd.DataFrame:
    query = "SELECT * FROM field_defs"
    if active_only:
        query += " WHERE active=1"
    query += " ORDER BY id"
    with db_conn() as conn:
        return pd.read_sql_query(query, conn)


def next_case_code() -> str:
    year = datetime.now().year
    with db_conn() as conn:
        row = conn.execute(
            "SELECT case_code FROM cases WHERE case_code GLOB ? ORDER BY case_code DESC LIMIT 1",
            (f"{year}[0-9][0-9][0-9][0-9]",),
        ).fetchone()
    if not row:
        return f"{year}0001"
    current = int(str(row[0])[-4:])
    return f"{year}{current+1:04d}"


def next_case_code_from(last_code: str | None) -> str:
    year = datetime.now().year
    if not last_code or len(str(last_code)) != 8 or not str(last_code).isdigit():
        return f"{year}0001"
    if str(last_code)[:4] != str(year):
        return f"{year}0001"
    current = int(str(last_code)[-4:])
    return f"{year}{current+1:04d}"


def audit(table: str, key: str, field: str, old: str, new: str, reason: str = ""):
    with db_conn() as conn:
        conn.execute(
            """INSERT INTO audit_logs(table_name,record_key,field_name,old_value,new_value,updated_by,updated_at,reason)
               VALUES(?,?,?,?,?,?,?,?)""",
            (table, key, field, old, new, st.session_state["user"], datetime.now().isoformat(), reason),
        )
        conn.commit()


def login_screen():
    st.title("🧪 Case Manager / Quản lý ca bệnh")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Đăng nhập / Login"):
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state["user"] = username
                st.session_state["role"] = user["role"]
                st.rerun()
            st.error("Sai tài khoản hoặc mật khẩu")


def field_settings():
    st.subheader(t("Cấu hình trường dữ liệu", "Field settings"))
    df = fetch_fields(active_only=False)
    st.dataframe(df[["id", "field_key", "label_vi", "label_en", "field_type", "active"]], use_container_width=True)
    if st.session_state["role"] != "admin":
        st.info(t("Chỉ admin được sửa cấu hình.", "Only admin can edit field settings."))
        return

    with st.form("add_field"):
        c1, c2, c3, c4 = st.columns(4)
        key = c1.text_input("field_key")
        vi = c2.text_input("label_vi")
        en = c3.text_input("label_en")
        ftype = c4.selectbox("field_type", ["text", "number", "date"])
        if st.form_submit_button(t("Thêm", "Add")) and key and vi and en:
            with db_conn() as conn:
                conn.execute(
                    "INSERT INTO field_defs(field_key,label_vi,label_en,field_type,active) VALUES(?,?,?,?,1)",
                    (key.strip(), vi.strip(), en.strip(), ftype),
                )
                conn.commit()
            st.success(t("Đã thêm trường mới.", "Added new field."))
            st.rerun()


def case_form(existing=None):
    data = {} if existing is None else dict(existing)
    fields = fetch_fields()
    for _, f in fields.iterrows():
        k = f["field_key"]
        label = f["label_vi"] if st.session_state["lang"] == "vi" else f["label_en"]
        val = data.get(k, "")
        if k == "case_code":
            data[k] = st.text_input(label, value=val or next_case_code())
        elif f["field_type"] == "number":
            default_num = int(val) if str(val).isdigit() else 0
            data[k] = int(st.number_input(label, value=default_num, min_value=0))
        elif f["field_type"] == "date":
            try:
                d = datetime.strptime(val, DATE_FMT).date() if val else datetime.now().date()
            except ValueError:
                d = datetime.now().date()
            data[k] = st.date_input(label, value=d).strftime(DATE_FMT)
        else:
            data[k] = st.text_input(label, value=str(val) if val is not None else "")
    return data


def cases_screen():
    st.subheader(t("Quản lý ca bệnh", "Case management"))
    with db_conn() as conn:
        df = pd.read_sql_query("SELECT id, case_code, data_json, created_at, updated_at FROM cases ORDER BY id DESC", conn)

    query = st.text_input(t("Tìm theo mã ca/tên", "Search by case code/name"))
    if not df.empty:
        details = df["data_json"].apply(json.loads).apply(pd.Series)
        show = pd.concat([df[["id", "case_code", "created_at", "updated_at"]], details], axis=1)
        if query:
            q = query.lower()
            show = show[show.apply(lambda r: q in str(r.to_dict()).lower(), axis=1)]
        st.dataframe(show, use_container_width=True)

    if st.session_state["role"] == "viewer":
        return

    mode = st.radio(
        t("Chế độ", "Mode"),
        [t("Thêm mới (Form)", "Create (Form)"), t("Nhập hàng loạt (Bảng)", "Bulk (Table)"), t("Cập nhật", "Update")],
        horizontal=True,
    )
    if mode == t("Thêm mới (Form)", "Create (Form)"):
        with st.form("create_case"):
            payload = case_form()
            if st.form_submit_button(t("Lưu ca", "Save case")):
                with db_conn() as conn:
                    conn.execute(
                        "INSERT INTO cases(case_code,data_json,created_by,created_at) VALUES(?,?,?,?)",
                        (payload["case_code"], json.dumps(payload, ensure_ascii=False), st.session_state["user"], datetime.now().isoformat()),
                    )
                    conn.commit()
                st.success(t("Đã tạo ca bệnh.", "Case created."))
                st.rerun()
    elif mode == t("Nhập hàng loạt (Bảng)", "Bulk (Table)"):
        st.caption(t("Dán trực tiếp từ Excel vào bảng dưới.", "Paste directly from Excel into this table."))
        bulk_cols = ["case_code", "lab_code", "full_name", "age", "gender", "address", "onset_date", "sample_received_date"]
        if "bulk_df" not in st.session_state:
            st.session_state.bulk_df = pd.DataFrame([{c: "" for c in bulk_cols} for _ in range(10)])

        c1, c2, c3 = st.columns([3, 3, 2])
        fill_col = c1.selectbox(t("Cột điền nhanh", "Quick-fill column"), bulk_cols)
        fill_value = c2.text_input(t("Giá trị điền nhanh", "Quick-fill value"))
        if c3.button(t("Áp dụng cho mọi dòng", "Apply to all rows")):
            st.session_state.bulk_df[fill_col] = fill_value

        edited = st.data_editor(st.session_state.bulk_df, num_rows="dynamic", use_container_width=True, key="bulk_editor")
        st.session_state.bulk_df = edited

        if st.button(t("Lưu dữ liệu hàng loạt", "Save bulk data")):
            saved = 0
            next_code = next_case_code()
            with db_conn() as conn:
                for _, row in edited.iterrows():
                    data = {k: ("" if pd.isna(v) else str(v).strip()) for k, v in row.to_dict().items()}
                    if not any(data.values()):
                        continue
                    code = data.get("case_code") or next_code
                    if not data.get("case_code"):
                        next_code = next_case_code_from(code)
                    data["case_code"] = code
                    conn.execute(
                        "INSERT OR REPLACE INTO cases(case_code,data_json,created_by,created_at,updated_by,updated_at) VALUES(?,?,?,?,?,?)",
                        (
                            code,
                            json.dumps(data, ensure_ascii=False),
                            st.session_state["user"],
                            datetime.now().isoformat(),
                            st.session_state["user"],
                            datetime.now().isoformat(),
                        ),
                    )
                    saved += 1
                conn.commit()
            st.success(t(f"Đã lưu {saved} dòng.", f"Saved {saved} rows."))
            st.rerun()
    else:
        case_code = st.text_input("Case code")
        if case_code:
            with db_conn() as conn:
                row = conn.execute("SELECT id,data_json FROM cases WHERE case_code=?", (case_code,)).fetchone()
            if row:
                old_data = json.loads(row[1])
                with st.form("update_case"):
                    payload = case_form(old_data)
                    reason = st.text_input(t("Lý do chỉnh sửa", "Edit reason"), value="update")
                    if st.form_submit_button(t("Cập nhật", "Update")):
                        for k, v in payload.items():
                            if str(old_data.get(k, "")) != str(v):
                                audit("cases", case_code, k, str(old_data.get(k, "")), str(v), reason)
                        with db_conn() as conn:
                            conn.execute(
                                "UPDATE cases SET data_json=?,updated_by=?,updated_at=? WHERE case_code=?",
                                (json.dumps(payload, ensure_ascii=False), st.session_state["user"], datetime.now().isoformat(), case_code),
                            )
                            conn.commit()
                        st.success(t("Đã cập nhật.", "Updated."))
                        st.rerun()


def tests_screen():
    st.subheader(t("Kết quả xét nghiệm", "Test results"))
    if st.session_state["role"] != "viewer":
        with st.form("add_test"):
            c1, c2, c3 = st.columns(3)
            case_code = c1.text_input("Case code")
            test_type = c2.selectbox("Test", ["A", "B", "PCR", "NGS", "Other"])
            result = c3.text_input("Result")
            result_date = st.date_input(t("Ngày kết quả", "Result date")).strftime(DATE_FMT)
            note = st.text_area(t("Ghi chú", "Note"))
            if st.form_submit_button(t("Lưu xét nghiệm", "Save result")) and case_code:
                with db_conn() as conn:
                    conn.execute(
                        """INSERT INTO test_results(case_code,test_type,result_value,result_date,note,updated_by,updated_at)
                           VALUES(?,?,?,?,?,?,?)""",
                        (case_code, test_type, result, result_date, note, st.session_state["user"], datetime.now().isoformat()),
                    )
                    conn.commit()
                st.success(t("Đã lưu kết quả.", "Saved test result."))
                st.rerun()

    with db_conn() as conn:
        results = pd.read_sql_query("SELECT * FROM test_results ORDER BY id DESC", conn)
    st.dataframe(results, use_container_width=True)


def excel_screen():
    st.subheader("Excel")
    uploaded = st.file_uploader("Import .xlsx", type=["xlsx"])
    if uploaded is not None and st.button("Import"):
        df = pd.read_excel(uploaded)
        with db_conn() as conn:
            for _, row in df.iterrows():
                data = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items()}
                code = str(data.get("case_code") or next_case_code())
                data["case_code"] = code
                conn.execute(
                    "INSERT OR REPLACE INTO cases(case_code,data_json,created_by,created_at,updated_by,updated_at) VALUES(?,?,?,?,?,?)",
                    (code, json.dumps(data, ensure_ascii=False), st.session_state["user"], datetime.now().isoformat(), st.session_state["user"], datetime.now().isoformat()),
                )
            conn.commit()
        st.success(t("Import thành công.", "Import completed."))

    if st.button("Export cases (.xlsx)"):
        with db_conn() as conn:
            cdf = pd.read_sql_query("SELECT case_code,data_json,created_at,updated_at FROM cases", conn)
        if cdf.empty:
            st.warning("No data")
            return
        payload = cdf["data_json"].apply(json.loads).apply(pd.Series)
        out = pd.concat([cdf[["case_code", "created_at", "updated_at"]], payload], axis=1)
        out = out.loc[:, ~out.columns.duplicated()]
        mem = io.BytesIO()
        out.to_excel(mem, index=False)
        st.download_button("Download cases.xlsx", data=mem.getvalue(), file_name="cases.xlsx")


def dashboard_screen():
    st.subheader(t("Tổng hợp", "Dashboard"))
    with db_conn() as conn:
        cases = pd.read_sql_query("SELECT data_json FROM cases", conn)
        tests = pd.read_sql_query("SELECT test_type, result_value, result_date FROM test_results", conn)
    if cases.empty:
        st.info(t("Chưa có dữ liệu.", "No data."))
        return
    parsed = cases["data_json"].apply(json.loads).apply(pd.Series)
    if "onset_date" in parsed.columns:
        months = pd.to_datetime(parsed["onset_date"], format=DATE_FMT, errors="coerce").dt.to_period("M").astype(str)
        st.write(t("Số ca theo tháng", "Cases by month"))
        st.bar_chart(months.value_counts().sort_index())
    if not tests.empty:
        st.write(t("Số xét nghiệm theo loại", "Tests by type"))
        st.bar_chart(tests["test_type"].value_counts())


def audit_screen():
    st.subheader("Audit logs")
    with db_conn() as conn:
        logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 500", conn)
    st.dataframe(logs, use_container_width=True)


def main():
    st.set_page_config(page_title="Case Manager", layout="wide")
    init_db()
    st.session_state.setdefault("lang", "vi")

    if "user" not in st.session_state:
        login_screen()
        return

    st.sidebar.write(f"User: {st.session_state['user']} ({st.session_state['role']})")
    st.sidebar.selectbox("Ngôn ngữ / Language", ["vi", "en"], key="lang")
    menu = st.sidebar.radio("Menu", ["Cases", "Tests", "Fields", "Excel", "Dashboard", "Audit", "Logout"])

    if menu == "Cases":
        cases_screen()
    elif menu == "Tests":
        tests_screen()
    elif menu == "Fields":
        field_settings()
    elif menu == "Excel":
        excel_screen()
    elif menu == "Dashboard":
        dashboard_screen()
    elif menu == "Audit":
        audit_screen()
    elif menu == "Logout":
        st.session_state.clear()
        st.rerun()


if __name__ == "__main__":
    main()
