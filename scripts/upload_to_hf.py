import os
import sys
from huggingface_hub import HfApi

def upload_data():
    print("=" * 60)
    print("🚀 TOOL UPLOAD THƯ MỤC DATA LÊN HUGGING FACE DATASETS")
    print("=" * 60)

    # 1. Nhập Token
    token = os.getenv("HF_TOKEN")
    if not token:
        token = input("👉 Dán Access Token (loại WRITE) của bạn vào đây rồi bấm Enter: ").strip()

    if not token.startswith("hf_"):
        print("❌ Token không hợp lệ (thường bắt đầu bằng 'hf_...'). Vui lòng kiểm tra lại.")
        return

    # 2. Nhập thông tin Repo
    default_username = "quy21hn"
    default_repo_name = "vietnam-tourism-dataset"
    
    print(f"\nTên người dùng mặc định: {default_username}")
    username = input(f"Bấm Enter để dùng '{default_username}' hoặc gõ tên khác: ").strip() or default_username
    
    repo_name = input(f"Tên Dataset Repo (mặc định: '{default_repo_name}'): ").strip() or default_repo_name
    repo_id = f"{username}/{repo_name}"

    is_private_input = input("Bạn muốn để Private hay Public? (Gõ 'pub' để Public, Enter để mặc định Private): ").strip().lower()
    is_private = False if is_private_input in ["pub", "public"] else True

    api = HfApi(token=token)

    # 3. Tạo repo nếu chưa tồn tại
    print(f"\n📦 Đang kiểm tra/tạo Dataset repo: https://huggingface.co/datasets/{repo_id} (Private={is_private})...")
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

    # 4. Upload toàn bộ thư mục data/
    local_data_dir = os.path.abspath("data")
    if not os.path.exists(local_data_dir):
        print(f"❌ Không tìm thấy thư mục {local_data_dir}")
        return

    print(f"\n⏳ Bắt đầu upload toàn bộ dữ liệu từ: {local_data_dir}")
    print("   (Hệ thống sẽ giữ nguyên cây thư mục raw/, processed/ và tự xử lý file lớn)")
    print("   Quá trình này có thể mất vài phút tùy vào tốc độ mạng...\n")

    try:
        api.upload_folder(
            folder_path=local_data_dir,
            path_in_repo="data",
            repo_id=repo_id,
            repo_type="dataset",
            ignore_patterns=[
                "*.bak",
                "*.tmp",
                "*progress*",
                "*.db-journal",
                "*.db-wal",
                "*.db-shm"
            ],
            commit_message="Upload complete data folder (raw + processed + sqlite db)"
        )
        print("\n" + "=" * 60)
        print(f"🎉 THÀNH CÔNG! Dữ liệu của bạn đã được đưa lên:")
        print(f"👉 https://huggingface.co/datasets/{repo_id}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình upload: {e}")

if __name__ == "__main__":
    upload_data()
