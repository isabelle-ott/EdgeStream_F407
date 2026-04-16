from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "students.json"

app = Flask(__name__)
app.secret_key = "student-management-secret-key"


@dataclass
class Student:
    student_id: str
    name: str
    gender: str
    grade: str
    class_name: str
    major: str
    birth_date: str
    phone: str
    email: str
    address: str
    guardian_name: str
    guardian_phone: str
    id_card: str
    student_number: str
    enrollment_date: str
    status: str
    dormitory: str
    hobby: str
    emergency_contact: str
    emergency_phone: str
    remark: str
    created_at: str
    updated_at: str


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_students() -> List[dict]:
    ensure_storage()
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_students(students: List[dict]) -> None:
    ensure_storage()
    DATA_FILE.write_text(json.dumps(students, ensure_ascii=False, indent=2), encoding="utf-8")


def get_student(student_id: str) -> Optional[dict]:
    return next((s for s in load_students() if s["student_id"] == student_id), None)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def index():
    students = load_students()
    keyword = request.args.get("q", "").strip().lower()
    if keyword:
        students = [
            s for s in students
            if keyword in " ".join(str(v) for v in s.values()).lower()
        ]
    return render_template("index.html", students=students, keyword=keyword)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        if not student_id or not name:
            flash("学号和姓名不能为空。", "danger")
            return redirect(url_for("add_student"))

        students = load_students()
        if any(s["student_id"] == student_id for s in students):
            flash("该学号已存在，请使用不同的学号。", "warning")
            return redirect(url_for("add_student"))

        student = Student(
            student_id=student_id,
            name=name,
            gender=request.form.get("gender", "未知").strip(),
            grade=request.form.get("grade", "").strip(),
            class_name=request.form.get("class_name", "").strip(),
            major=request.form.get("major", "").strip(),
            birth_date=request.form.get("birth_date", "").strip(),
            phone=request.form.get("phone", "").strip(),
            email=request.form.get("email", "").strip(),
            address=request.form.get("address", "").strip(),
            guardian_name=request.form.get("guardian_name", "").strip(),
            guardian_phone=request.form.get("guardian_phone", "").strip(),
            id_card=request.form.get("id_card", "").strip(),
            student_number=request.form.get("student_number", "").strip(),
            enrollment_date=request.form.get("enrollment_date", "").strip(),
            status=request.form.get("status", "在读").strip(),
            dormitory=request.form.get("dormitory", "").strip(),
            hobby=request.form.get("hobby", "").strip(),
            emergency_contact=request.form.get("emergency_contact", "").strip(),
            emergency_phone=request.form.get("emergency_phone", "").strip(),
            remark=request.form.get("remark", "").strip(),
            created_at=now_str(),
            updated_at=now_str(),
        )
        students.append(asdict(student))
        save_students(students)
        flash("学生信息添加成功。", "success")
        return redirect(url_for("index"))

    return render_template("form.html", student=None, mode="add")


@app.route("/edit/<student_id>", methods=["GET", "POST"])
def edit_student(student_id: str):
    students = load_students()
    student = get_student(student_id)
    if not student:
        flash("未找到该学生。", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        for field in [
            "name", "gender", "grade", "class_name", "major", "birth_date", "phone",
            "email", "address", "guardian_name", "guardian_phone", "id_card",
            "student_number", "enrollment_date", "status", "dormitory", "hobby",
            "emergency_contact", "emergency_phone", "remark",
        ]:
            student[field] = request.form.get(field, "").strip()
        student["updated_at"] = now_str()
        for idx, item in enumerate(students):
            if item["student_id"] == student_id:
                students[idx] = student
                break
        save_students(students)
        flash("学生信息已更新。", "success")
        return redirect(url_for("index"))

    return render_template("form.html", student=student, mode="edit")


@app.route("/delete/<student_id>", methods=["POST"])
def delete_student(student_id: str):
    students = load_students()
    filtered = [s for s in students if s["student_id"] != student_id]
    if len(filtered) == len(students):
        flash("删除失败，未找到该学生。", "danger")
    else:
        save_students(filtered)
        flash("学生已删除。", "success")
    return redirect(url_for("index"))


@app.route("/detail/<student_id>")
def student_detail(student_id: str):
    student = get_student(student_id)
    if not student:
        flash("未找到该学生。", "danger")
        return redirect(url_for("index"))
    return render_template("detail.html", student=student)


if __name__ == "__main__":
    ensure_storage()
    app.run(debug=True)
