"""
Gemini File Search RAG - 문서 업로드
Google AI Studio에서 사용할 File Search Store를 생성합니다.
실행할 때마다 새로 추가된 문서만 자동 업로드합니다.
"""

import os
import sys
import time
import json
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("\n[!] google-genai 패키지가 설치되어 있지 않습니다.")
    print("    실행 방법: uv run --with google-genai main.py")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
KEY_FILE = BASE_DIR / ".api_key"
STATE_FILE = BASE_DIR / ".state.json"


SUPPORTED_EXTENSIONS = {
    # 문서
    ".pdf", ".docx", ".docm", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    # 텍스트/데이터
    ".txt", ".md", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml",
    ".html", ".htm", ".rtf", ".tex", ".latex",
    # 코드
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".sql",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".rb",
    ".php", ".dart", ".swift", ".kt", ".kts", ".scala",
    ".r", ".m", ".lua", ".pl", ".pm", ".sh", ".bash", ".zsh",
    ".ps1", ".bat", ".cmd",
    # 웹/설정
    ".css", ".scss", ".sass", ".less", ".svg",
    ".toml", ".ini", ".cfg", ".conf", ".env", ".properties",
    # 노트북/기타
    ".ipynb", ".log", ".diff", ".patch",
}


def load_state():
    """저장된 상태 불러오기 (Store 이름, 업로드된 파일 목록)"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"store_name": None, "uploaded_files": []}


def save_state(state):
    """상태 저장"""
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_api_key():
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
        if key:
            print("[OK] 저장된 API 키를 불러왔습니다.")

    if not key:
        print("\n===== Google API 키 설정 =====")
        print("API 키가 없으면 아래 링크에서 무료로 발급받으세요:")
        print("  -> https://aistudio.google.com/apikey\n")
        key = input("Google API 키를 입력하세요: ").strip()
        if not key:
            print("[!] API 키가 필요합니다.")
            sys.exit(1)
        KEY_FILE.write_text(key)
        print("[OK] API 키가 저장되었습니다. (다음부터 자동 로드)")

    return key


def scan_files():
    """docs 폴더에서 지원되는 파일 스캔"""
    DOCS_DIR.mkdir(exist_ok=True)
    files = []
    for f in sorted(DOCS_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            size_mb = f.stat().st_size / (1024 * 1024)
            files.append((f, size_mb))
    return files


def upload_and_wait(client, store_name, files):
    """파일 업로드 + 인덱싱 대기"""
    print(f"\n===== 파일 업로드 ({len(files)}개) =====")
    operations = []
    for i, (file_path, size_mb) in enumerate(files, 1):
        print(f"  [{i}/{len(files)}] {file_path.name} ({size_mb:.1f}MB)...", end=" ", flush=True)
        try:
            op = client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store_name,
                config={"display_name": file_path.name},
            )
            operations.append((file_path.name, op))
            print("OK")
        except Exception as e:
            print(f"실패 - {e}")

    if operations:
        print("\n[...] 인덱싱 진행 중 (시간이 걸릴 수 있습니다)...")
        pending = list(operations)
        while pending:
            still_pending = []
            for name, op in pending:
                try:
                    op = client.operations.get(op)
                    if op.done:
                        print(f"  [OK] {name} 완료")
                    else:
                        still_pending.append((name, op))
                except Exception as e:
                    print(f"  [!] {name} 확인 실패: {e}")
            pending = still_pending
            if pending:
                time.sleep(3)
        print("\n[OK] 모든 파일 인덱싱 완료!")

    return [name for name, _ in operations]


def chat(client, store_name):
    """Store에 질문하기"""
    print("\n===== 질문하기 (종료: q) =====\n")
    while True:
        question = input("질문: ").strip()
        if not question or question.lower() == "q":
            break
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[store_name]
                            )
                        )
                    ]
                ),
            )
            print(f"\n{response.text}\n")
        except Exception as e:
            print(f"\n[!] 오류: {e}\n")


def main():
    print("=" * 50)
    print("  Gemini File Search RAG")
    print("=" * 50)

    # 1. API 키
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    # 2. 상태 불러오기
    state = load_state()

    # 3. docs 폴더 스캔
    all_files = scan_files()
    if not all_files:
        print(f"\n[!] docs 폴더에 문서가 없습니다.")
        print(f"    경로: {DOCS_DIR}")
        print(f"    이 폴더에 문서를 넣고 다시 실행하세요.")
        sys.exit(1)

    # 4. 새 파일만 필터링
    uploaded = set(state["uploaded_files"])
    new_files = [(f, s) for f, s in all_files if f.name not in uploaded]

    print(f"\n전체 문서: {len(all_files)}개 | 업로드 완료: {len(uploaded)}개 | 새 문서: {len(new_files)}개")

    # 5. Store 생성 또는 기존 Store 사용
    if new_files:
        if state["store_name"]:
            store_name = state["store_name"]
        else:
            name = input("\nStore 이름 (Enter = 'my-rag-store'): ").strip()
            store_display = name if name else "my-rag-store"
            print(f"\n[...] Store 생성 중: {store_display}")
            store = client.file_search_stores.create(
                config={"display_name": store_display}
            )
            store_name = store.name
            state["store_name"] = store_name
            print(f"[OK] Store 생성 완료")
            print(f"[INFO] Store ID: {store_name}")
            print(f"       이 ID를 n8n, AI Studio 등에서 사용하세요.")

        # 6. 새 파일 업로드
        uploaded_names = upload_and_wait(client, store_name, new_files)
        state["uploaded_files"].extend(uploaded_names)
        save_state(state)
    else:
        store_name = state["store_name"]

    # Store ID 항상 표시
    if store_name:
        print(f"\n[Store ID] {store_name}")

    # 7. 질문하기
    if store_name:
        chat_yn = input("\n문서에 질문할까요? (y/n): ").strip().lower()
        if chat_yn == "y":
            chat(client, store_name)

    print("\n완료!")


if __name__ == "__main__":
    main()
