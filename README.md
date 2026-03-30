# Gemini File Search RAG

문서를 폴더에 넣고 실행하면, Google이 자동으로 RAG를 구축해줍니다.

## RAG란?

RAG(Retrieval-Augmented Generation)는 내 문서를 AI가 검색해서 답변하는 기술입니다.

### 일반적인 RAG 구축 과정

| 단계 | 작업 | 필요한 도구 |
|------|------|------------|
| 1. 로드 | PDF에서 텍스트 추출 | PyPDF, LangChain |
| 2. 분할 | 텍스트를 작은 조각(청크)으로 자르기 | TextSplitter |
| 3. 임베딩 | 각 조각을 벡터(숫자)로 변환 | OpenAI Embeddings |
| 4. 저장 | 벡터를 검색 가능한 DB에 저장 | ChromaDB, Supabase |
| 5. 검색 | 질문과 유사한 문서 찾기 | Retriever |
| 6. 답변 | LLM이 검색 결과로 답변 생성 | GPT, Gemini |

### Gemini File Search RAG

**위 과정을 Google이 전부 자동으로 해줍니다.**

| 단계 | 작업 | 누가? |
|------|------|-------|
| 1. 업로드 | docs 폴더에 문서 넣기 | **사용자** |
| 2. 실행 | run.bat 더블클릭 | **사용자** |
| 3~6. 나머지 | 추출, 분할, 임베딩, 저장, 검색, 답변 | **Google 자동** |

## 설치

> [!NOTE]
> uv가 설치되어 있어야 합니다.

### uv 설치 (최초 1회)

**Windows PowerShell:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Gemini RAG 다운로드

1. [GitHub 페이지](https://github.com/daniel8824-del/gemini-rag)에서 **Code → Download ZIP** 클릭
2. 원하는 위치에 압축 풀기

## 사용법

### 1단계: 문서 넣기

`docs` 폴더에 업로드할 문서를 넣으세요.

```
Gemini-RAG/
├── docs/          ← 여기에 문서 넣기
│   ├── 보고서.pdf
│   ├── 데이터.xlsx
│   └── 회의록.docx
├── main.py
└── run.bat
```

### 2단계: 실행

`run.bat`을 더블클릭하세요.

```
==================================================
  Gemini File Search RAG
==================================================
[OK] 저장된 API 키를 불러왔습니다.

전체 문서: 3개 | 업로드 완료: 0개 | 새 문서: 3개

Store 이름 (Enter = 'my-rag-store'):

[...] Store 생성 중: my-rag-store
[OK] Store 생성 완료
[INFO] Store ID: fileSearchStores/abc123

===== 파일 업로드 (3개) =====
  [1/3] 보고서.pdf (2.3MB)... OK
  [2/3] 데이터.xlsx (0.5MB)... OK
  [3/3] 회의록.docx (0.1MB)... OK

[...] 인덱싱 진행 중 (시간이 걸릴 수 있습니다)...
  [OK] 보고서.pdf 완료
  [OK] 데이터.xlsx 완료
  [OK] 회의록.docx 완료

[OK] 모든 파일 인덱싱 완료!

[Store ID] fileSearchStores/abc123

문서에 질문할까요? (y/n): y

===== 질문하기 (종료: q) =====

질문: 이 보고서의 핵심 내용은?

보고서의 핵심 내용은...
```

### 3단계: 문서 추가

`docs` 폴더에 새 파일을 넣고 `run.bat`을 다시 실행하면 됩니다.
이미 업로드한 파일은 건너뛰고 **새 파일만 자동 업로드**합니다.

## Google API 키 발급

최초 실행 시 API 키를 입력해야 합니다. (1회만 입력하면 자동 저장)

1. [Google AI Studio API Keys](https://aistudio.google.com/apikey) 접속
2. Google 계정으로 로그인
3. **Create API Key** 클릭
4. 생성된 키를 복사해서 프로그램에 붙여넣기

> 무료 API 키로 사용 가능합니다. (저장 무료, 인덱싱 100만 토큰당 $0.15)

## 지원 파일 형식

| 분류 | 확장자 |
|------|--------|
| 문서 | `.pdf` `.docx` `.doc` `.pptx` `.ppt` `.xlsx` `.xls` |
| 텍스트 | `.txt` `.md` `.csv` `.tsv` `.html` `.rtf` `.tex` |
| 데이터 | `.json` `.xml` `.yaml` `.yml` |
| 코드 | `.py` `.js` `.ts` `.java` `.sql` `.c` `.cpp` `.go` `.rs` 등 |
| 노트북 | `.ipynb` |

## 설정값

`main.py` 상단에서 수정할 수 있습니다.

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `CHUNK_MAX_TOKENS` | 1000 | 청크당 최대 토큰 수 |
| `CHUNK_OVERLAP_TOKENS` | 100 | 청크 간 중복 토큰 수 |
| `CHAT_TEMPERATURE` | 0.2 | 답변 창의성 (0=정확, 1=창의적) |

## Store ID 활용

업로드 완료 후 표시되는 Store ID를 다른 서비스에서 사용할 수 있습니다.

| 연결 대상 | 방법 |
|-----------|------|
| Google AI Studio | 같은 API 키로 접속하면 Store 공유 |
| n8n | HTTP Request 노드에서 Gemini API + Store ID |
| Streamlit | Python SDK에서 Store ID로 질의 |

## 자주 묻는 질문

> **Q: API 키를 잘못 입력했어요.**
> `.api_key` 파일을 삭제하고 다시 실행하세요.

> **Q: Store를 새로 만들고 싶어요.**
> `.state.json` 파일을 삭제하고 다시 실행하세요.

> **Q: 업로드한 파일을 삭제하고 싶어요.**
> [Google AI Studio](https://aistudio.google.com)에서 Store를 관리할 수 있습니다.

> **Q: 비용이 발생하나요?**
> 저장은 무료입니다. 인덱싱 시 100만 토큰당 $0.15이 발생하지만, PDF 100페이지 기준 약 $0.01~0.02 수준입니다.

> **Q: 업데이트하려면?**
> GitHub에서 최신 ZIP을 다시 다운로드하세요.

## 관련 도구

- [뉴스 수집기](https://github.com/daniel8824-del/google-news-scraper) - Google 뉴스 수집 CLI
- [인스타그램 수집기](https://github.com/daniel8824-del/instagram-collector) - 인스타그램 게시물 수집 CLI
