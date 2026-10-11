# -*- coding: utf-8 -*-
"""
TOOL UPLOAD FILE SQLITE DATABASE LÊN HUGGING FACE DATASETS
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
- Tệp tải lên: data/processed/tourism_vietnam.db (~1.34 GB, 1.69 triệu reviews)
- Sử dụng huggingface_hub API với Git LFS tự động
"""

import os
import sys
import argparse

# Thiết lập UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from huggingface_hub import HfApi, get_token


def upload_sqlite_db(token: str = None, repo_id: str = None, is_private: bool = True):
    print("=" * 75)
    print("🚀 TOOL TẢI FILE CSDL SQLITE (tourism_vietnam.db) LÊN HUGGING FACE")
    print("=" * 75)

    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "tourism_vietnam.db"))
    if not os.path.exists(db_path):
        print(f"❌ Không tìm thấy file CSDL tại: {db_path}")
        return

    file_size_gb = os.path.getsize(db_path) / (1024**3)
    print(f"• Đường dẫn file cục bộ: {db_path}")
    print(f"• Dung lượng: {file_size_gb:.2f} GB ({os.path.getsize(db_path):,} bytes)")

    # 1. Lấy Token
    if not token:
        token = os.getenv("HF_TOKEN") or get_token()

    if not token:
        print("\n🔑 Chưa tìm thấy Hugging Face Token.")
        print("   -> Bạn có thể tạo token tại: https://huggingface.co/settings/tokens (chọn quyền WRITE)")
        token = input("👉 Dán HF Token (bắt đầu bằng 'hf_...') vào đây: ").strip()

    if not token or not token.startswith("hf_"):
        print("❌ Token không hợp lệ. Vui lòng lấy token có quyền WRITE tại https://huggingface.co/settings/tokens.")
        return

    # 2. Xác định Repo ID
    if not repo_id:
        default_repo = "quylhm/vietnam-tourism-dataset"
        print(f"\n📦 Dataset Repo mặc định: '{default_repo}'")
        user_repo = input(f"👉 Bấm Enter để chọn '{default_repo}' hoặc nhập repo khác (username/repo-name): ").strip()
        repo_id = user_repo or default_repo

    api = HfApi(token=token)

    # 3. Tạo repo nếu chưa có
    print(f"\n⏳ Đang kiểm tra / tạo Repo: https://huggingface.co/datasets/{repo_id} (Private={is_private})...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=is_private,
            exist_ok=True
        )
        print("✅ Repo đã sẵn sàng!")
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo repo: {e}")
        return

    # 4. Upload file SQLite lên HF Dataset
    path_in_repo = "data/processed/tourism_vietnam.db"
    print(f"\n📤 Bắt đầu tải {file_size_gb:.2f} GB lên Hugging Face Dataset...")
    print(f"   Vị trí trên repo: {path_in_repo}")
    print("   (Quá trình tải lên sử dụng Git LFS với đường truyền bảo mật, vui lòng đợi vài phút)...\n")

    try:
        res = api.upload_file(
            path_or_fileobj=db_path,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Upload processed SQLite database (1.69M reviews and cleaned places metadata)"
        )
        print("=" * 75)
        print("🎉 TẢI LÊN THÀNH CÔNG RỰC RỠ!")
        print(f"👉 Đường dẫn Dataset: https://huggingface.co/datasets/{repo_id}")
        print(f"👉 File URL: {res}")
        print("=" * 75)
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình upload: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload tourism_vietnam.db to Hugging Face")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face Access Token (WRITE)")
    parser.add_argument("--repo", type=str, default="quylhm/vietnam-tourism-dataset", help="Dataset repo_id (e.g. username/repo-name)")
    parser.add_argument("--public", action="store_true", help="Đặt repo thành Public (mặc định là Private)")
    args = parser.parse_args()

    upload_sqlite_db(
        token=args.token,
        repo_id=args.repo,
        is_private=not args.public
    )
