# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                                     |
| --------------- | ------------------------------------------------------------ |
| Họ và tên       | Lê Việt Hoàng                                                |
| MSSV            | 2A202602596                                                  |
| Khóa/Lớp        | K4 - L3B                                                     |
| Tên nhóm        | T052AI                                                       |
| Vai trò chính   | RAG & Vector Index owner (embedding + ChromaDB + QA Agent)   |
| Repository      | https://github.com/younglonelyboiz/K4-L3B-Day10-T052AI-DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26                                                   |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable          | File/hàm phụ trách                                                 | Input nhận vào                          | Output bàn giao          |
| --------------------------- | ------------------------------------------------------------------ | --------------------------------------- | ------------------------ |
| Embedding model             | `src/retrieval/embeddings.py` (`MiniLMEmbeddings`)                 | Text tự do (title/summary/metadata)     | Vector 384 chiều đã normalize |
| Vector store                | `src/retrieval/index.py` (`LocalEmbeddingIndex.build/load/search`) | `data/clean/papers_clean.json` (24 dòng) | Collection `papers-baseline` + `data/embeddings/papers_embeddings.json` |
| Helper build tái sử dụng    | `src/retrieval/index.py` (`load_clean_dataframe`, `build_baseline_index`) | Đường dẫn clean JSON từ `core/config.py` | Index đã nạp cho `evaluate_pipeline` |
| Script tái lập + self-check | `script/build_vector_index.py`                                     | `settings.paths.clean_json`             | Log "Tín hiệu hoàn thành" + exit 0 |
| QA Agent (retrieval path)   | `src/retrieval/qa.py` (`answer_question`), `src/retrieval/agent.py` | Câu hỏi + index                        | `AnswerResult` (answer, doc_ids, contexts) |

**Trạng thái:** 5/5 khối trên đã hoàn thành và có bằng chứng chạy thật.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                            | Thành viên/module được hỗ trợ | Kết quả                                                        |
| ------------------------------------ | ------------------------------ | -------------------------------------------------------------- |
| Xác minh schema clean trước khi index | Module cleaning của M2        | Xác nhận 24 dòng đủ cột `text_for_embedding`/metadata, không phải sửa gì |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện                                 | File/hàm/artifact liên quan              | Kết quả bàn giao                              | Cách xác minh                          |
| ----------------------------------------------------- | ---------------------------------------- | --------------------------------------------- | -------------------------------------- |
| Nạp 24 tài liệu sạch vào ChromaDB collection baseline | `script/build_vector_index.py`           | `data/chroma/` (1 segment + sqlite), 24 vector | `python script/build_vector_index.py`  |
| Sinh manifest embedding để `load()` dùng lại          | `data/embeddings/papers_embeddings.json` (33.782 bytes) | Manifest 24 documents + tên collection | `collection_name` = `papers-baseline`, `len(documents)` = 24 |
| Self-check retrieval                                  | `LocalEmbeddingIndex.search`             | 5/5 tài liệu tự truy vấn bằng title trả về đúng `paper_id` | In trong script               |
| Kiểm chứng QA Agent trích xuất metadata               | `retrieval/qa.py::answer_question`       | Câu hỏi dạng `date` trả về `2026-07-05`, 4 contexts | Chạy 1 dòng Python với index đã `load` |

Output cụ thể mà phần việc của tôi tạo ra: **collection `papers-baseline` sẵn sàng cho `evaluate_pipeline`** — đây là input bắt buộc của cả baseline lẫn corrupted flow; nếu thiếu thì `retrieval_hit_rate` không thể đo được.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Biến 24 bản ghi đã clean thành một không gian vector truy vấn được, sao cho (a) mỗi tài liệu tìm lại được chính nó, (b) chạy lại nhiều lần không sinh vector trùng, (c) mỗi trạng thái dữ liệu (baseline/corrupted/repaired) có không gian riêng để so sánh công bằng.

### Cách triển khai

- Mỗi dòng clean được dựng thành một document: `record_id = "{paper_id}::{index}"`, `content = text_for_embedding`, và metadata phẳng (paper_id, title, published, authors_joined, categories_joined, summary, abs_url, pdf_url). Metadata để phẳng vì ChromaDB đọc lại trực tiếp, không cần join.
- Embedding: `all-MiniLM-L6-v2` với `normalize_embeddings=True`; vì vector đã normalize nên chọn không gian **cosine** (`configuration={"hnsw": {"space": "cosine"}}`) và quy đổi `score = max(0, 1 - distance)`.
- Idempotent: trước khi `create_collection` luôn `delete_collection` cùng tên trong `try/except`, nên chạy lại không nhân bản vector.
- Tên collection suy ra từ đường dẫn manifest embeddings (`_derive_collection_name`) thay vì hardcode, nhờ vậy cùng một hàm phục vụ được cả 3 trạng thái.
- Điểm dễ vỡ nhất là **thứ tự** `record_id` (phải gắn thêm index để không trùng khi hai dòng cùng `paper_id`), nên tên record dùng dạng ghép `paper_id` + vị trí.

### Input, output và contract

| Thành phần                  | Mô tả                                                                 |
| --------------------------- | --------------------------------------------------------------------- |
| Input                       | `data/clean/papers_clean.json` — 24 dòng, cột bắt buộc: `paper_id`, `title`, `text_for_embedding`, `published`, `authors_joined`, `categories_joined`, `summary`, `abs_url`, `pdf_url` |
| Output                      | `data/chroma/` (ChromaDB persist) + `data/embeddings/papers_embeddings.json` (`backend`, `embedding_model`, `persist_path`, `collection_name`, `documents[24]`) |
| Module phụ thuộc            | `src/ingestion/cleaning.py` (M2), `src/core/config.py`, `src/core/utils.py` |
| Module sử dụng output       | `src/evaluation/metrics.py::evaluate_pipeline`, `src/pipelines/phase1.py` |
| Điều kiện lỗi cần xử lý     | DataFrame rỗng (thiếu artifact clean) và lệch số lượng giữa DataFrame và số vector ChromaDB — script chủ động `SystemExit` khi gặp |

### Cách xác minh

```bash
python script/build_vector_index.py
```

- **Kết quả mong đợi:** 24 tài liệu vào `papers-baseline`, self-check retrieval đạt tối đa.
- **Kết quả thực tế:** `Tín hiệu hoàn thành: Đã index 24 tài liệu vào collection 'papers-baseline'`, `vectors lưu = 24`, `Self-check retrieval 5/5`, sample query trả về `'Advanced Perspectives on Agentic Retrieval-Augmented Generation for Kn...'` với `score=0.5514`; chạy lần hai cho kết quả y hệt.
- **Artifact/log:** `data/chroma/`, `data/embeddings/papers_embeddings.json`, log console của script (không chứa secret).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần chọn cách lưu vector để 3 trạng thái baseline/corrupted/repaired không lẫn vào nhau, đồng thời không làm phình dung lượng nộp bài.
- **Các phương án đã cân nhắc:** (1) lưu embeddings ra JSON rồi tự tính cosine bằng numpy; (2) dùng ChromaDB `PersistentClient` với nhiều collection cùng thư mục persist.
- **Phương án đã chọn:** (2) — ChromaDB persist, mỗi trạng thái một collection.
- **Lý do:** ChromaDB cho truy vấn ANN nhanh và tách collection theo tên nên không phải tự quản lý ma trận vector; cùng một `persist_path` giúp `build` dùng chung cho cả 3 trạng thái. Vẫn ghi kèm JSON manifest vì `LocalEmbeddingIndex.load` cần nó để biết `collection_name`/`persist_path`.
- **Bằng chứng quyết định phù hợp:** Sau khi nạp, `collection.count() = 24` khớp đúng số dòng DataFrame; `LocalEmbeddingIndex.load(settings)` đọc lại được và `answer_question` trả về đúng metadata, chứng tỏ không cần backend riêng.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `ModuleNotFoundError: No module named 'core'`
- **Lệnh hoặc bước tái hiện:** `python -c "import core, retrieval; print(core.__file__)"` (dùng Python base của hệ thống).
- **Nguyên nhân gốc:** Package `day10-data-observability-lab-student` được cài editable với `package-dir = {"": "src"}`, tức `src/` chỉ nằm trên `sys.path` khi interpreter đã cài package này. Python base không cài nên import `core`/`retrieval` thất bại.
- **Cách xử lý:** Dùng đúng interpreter của môi trường ảo dự án `.\.venv\Scripts\python.exe`, không thêm `sys.path.insert` trong code để giữ đúng convention của `script/run_phase1.py`.
- **Cách xác minh sau khi sửa:** `.\.venv\Scripts\python.exe script/build_vector_index.py` chạy exit code 0 và in đủ 5 dòng "Tín hiệu hoàn thành".
- **Điều học được:** Với repo module hóa theo `src/`, lỗi import thường do sai interpreter chứ không phải sai code — phải kiểm tra môi trường trước khi sửa logic.

### Blocker còn lại

- **Phạm vi bị ảnh hưởng:** Collection `papers-corrupted` và `papers-repaired`.
- **Những gì đã loại trừ:** Đã kiểm tra không phải lỗi ở `index.py`/`embeddings.py`; nguyên nhân nằm ở nguồn dữ liệu: `src/ingestion/corruption.py` hiện vẫn `raise NotImplementedError`.
- **Bước tiếp theo:** Khi `corrupt_clean_dataframe` hoàn thành, build 2 collection còn lại bằng chính `LocalEmbeddingIndex.build(df, settings, embeddings_output_path=...)` với `settings.paths.corrupted_embeddings_json` và `settings.paths.repaired_embeddings_json`.

## 7. Hiểu biết về luồng end-to-end

1. **Từ Crossref đến vector index:** payload Crossref được parse thành `PaperRecord` → cleaning chuẩn hóa text, tính `age_days`, ghép `text_for_embedding` 5 phần → mỗi dòng thành 1 document → MiniLM encode thành vector 384 chiều đã normalize → nạp vào collection ChromaDB kèm metadata phẳng.
2. **Evaluation set và ground-truth doc IDs:** mỗi câu hỏi có `ground_truth` và `ground_truth_doc_ids`; `retrieval_hit_rate` đo tài liệu đúng có nằm trong top-k retrieval hay không, còn `mean_token_f1`/`judge_accuracy` đo chất lượng câu trả lời trích từ context. Nhờ vậy tách được lỗi do retrieval và lỗi do sinh câu trả lời.
3. **Quality checks khác freshness:** quality checks kiểm tính toàn vẹn cấu trúc tại một thời điểm (row count, `paper_id` not null/unique, title not null, độ dài summary); freshness kiểm theo thời gian — dùng `settings.freshness_threshold_days` (hiện là 180 ngày) để đếm `stale_rows`/`total_rows` và kết luận `is_fresh`, tức cảnh báo dữ liệu lỗi thời dù schema vẫn hợp lệ. Ngưỡng tỷ lệ cụ thể sẽ do `quality.py` quyết định khi được implement (hiện vẫn là stub), nên tôi không khẳng định trước con số.
4. **Vì sao dùng cùng test set cho 3 trạng thái:** nếu đổi câu hỏi giữa các lần đo thì chênh lệch metric có thể do đề bài khác chứ không do dữ liệu, nên không quy được nhân quả; cùng test set thì mọi thay đổi chỉ còn do trạng thái dữ liệu.
5. **Repair thành công dựa trên artifact/metric nào:** repair chạy lại từ raw snapshot (`data/raw/crossref_records.json`) nên phải tái tạo được `papers_clean_repaired.json` khớp schema baseline; thành công khi (a) quality gate trở lại `success = True`, (b) `repaired_metrics.json` quay về mức xấp xỉ `baseline_metrics.json` trên cùng test set.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal        | Baseline       | Corrupted      | Repaired       | Nhận xét của cá nhân                                          |
| -------------------- | -------------- | -------------- | -------------- | ------------------------------------------------------------- |
| `retrieval_hit_rate` | [chờ pipeline] | [chờ pipeline] | [chờ pipeline] | Phụ thuộc `papers_clean_corrupted.json` (đang chặn ở `corruption.py`) |
| `mean_token_f1`      | [chờ pipeline] | [chờ pipeline] | [chờ pipeline] | Chưa có artifact để đối chiếu                                 |
| `judge_accuracy`     | [chờ pipeline] | [chờ pipeline] | [chờ pipeline] | Chưa có artifact để đối chiếu                                 |
| `mean_judge_score`   | [chờ pipeline] | [chờ pipeline] | [chờ pipeline] | Chưa có artifact để đối chiếu                                 |
| Quality checks       | [chờ pipeline] | [chờ pipeline] | [chờ pipeline] | Chưa có artifact để đối chiếu                                 |
| Freshness status     | [chờ pipeline] | [chờ pipeline] | [chờ pipeline] | Chưa có artifact để đối chiếu                                 |

> Ghi chú trung thực: ở thời điểm viết báo cáo, `baseline_metrics.json` / `corrupted_metrics.json` / `repaired_metrics.json` **chưa tồn tại** vì còn phụ thuộc `testset.py`, `quality.py` và `phase1.py`. Tôi không điền số khi chưa có artifact để đối chiếu.

### Kết luận từ số liệu

1. [Data corruption] → [quality/freshness signal thay đổi] → [agent metric thay đổi]: chưa kết luận được, chờ artifact.
2. [Repair action] → [quality/freshness signal phục hồi] → [agent metric phục hồi]: chưa kết luận được, chờ artifact.

**Bằng chứng đã có từ phần việc của tôi:** collection `papers-baseline` với 24 vector, self-check retrieval 5/5 và sample query trả về đúng tài liệu — tức tầng index không phải nguyên nhân gây sụt giảm chỉ số khi chạy corruption flow.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Data pipeline:** metadata phẳng trong vector store quan trọng không kém vector — vì câu trả lời (authors/date/categories) được lấy trực tiếp từ metadata chứ không phải sinh lại từ text đã embed.
2. **Data quality/observability:** idempotency là điều kiện để so sánh công bằng; nếu mỗi lần chạy lại sinh thêm vector trùng thì `retrieval_hit_rate` bị nhiễu và không quy được cho dữ liệu.
3. **Ảnh hưởng của data đến RAG agent:** chỉ cần hỏng `text_for_embedding` hoặc metadata là agent "trả lời sai một cách tự tin" (silent failure) — nên phải đo ở tầng retrieval trước khi đo ở tầng câu trả lời.

### Nếu có thêm thời gian

Thêm bộ test tự động (pytest) khẳng định 3 bất biến của tầng index: số vector = số dòng clean, mỗi tài liệu tự truy vấn trả về đúng `paper_id`, và `load()` sau `build()` cho cùng `collection_name`. Cách đo cải thiện: chạy `pytest` trước mỗi lần push, kỳ vọng toàn bộ test xanh — giúp phát hiện sớm lỗi schema từ tầng cleaning.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Lê Việt Hoàng
**Ngày xác nhận:** 2026-09-26



