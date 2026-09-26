# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** `T052AI`
- **Mã Nhóm / Lớp:** `K4`
- **Tên Repository Nộp Bài:** [younglonelyboiz/K4-L3B-Day10-T052AI-DataPipelineDataObservability](https://github.com/younglonelyboiz/K4-L3B-Day10-T052AI-DataPipelineDataObservability)

---

## # Thành viên

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | Trịnh Xuân Huy | 2A202602995 | trinhhuy2304@gmail.com | Trưởng nhóm / Pipeline Integrator (`core/`, `phase1.py`, `corruption.py`, `corruption_flow.py`) | `report/2A202602995_TrinhXuanHuy.md` |
| 2 | Hoàng Ngọc Đức | 2A202602380 | duchbvts@gmail | Data Foundation & Recovery (`crossref.py`, `cleaning.py`, raw data) | `report/2A202602380_HoangNgocDuc.md` |
| 3 | Lê Việt Hoàng | 2A202602596 | viethoangvuivui@gmail.com | RAG & Vector Index (`retrieval/index.py`, `embeddings.py`, ChromaDB) | `report/2A202602596_LeVietHoang.md` |
| 4 | Mai Tiến Huy | 2A202602914 | huymai40101222@gmail.com | Observability & Evaluation (`quality.py` GX 1.x, `testset.py`, reporting) | `report/2A202602914_MaiTienHuy.md` |

*(Nếu nhóm có 3 hoặc 5-6 thành viên, xem bảng phân công chi tiết theo vai trò trong file `CHECKPOINTS.md`)*.

---

## # Cá nhân

### ## Trịnh Xuân Huy - 2A202602995
- **Vai trò:** Trưởng nhóm & Điều phối Pipeline.
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập cấu hình hệ thống `core/config.py` và đường dẫn artifacts `core/utils.py`.
  - Triển khai kịch bản tiêm lỗi dữ liệu tổng hợp trong `src/ingestion/corruption.py`.
  - Kết nối luồng thực thi trong `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py`.
  - Kiểm tra tính nhất quán của các artifacts và theo dõi Contributor tracking trên GitHub nhánh `main`.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về thiết kế Idempotent Pipeline và quản lý trạng thái luồng dữ liệu đa tầng.

### ## Hoàng Ngọc Đức - 2A202602380
- **Vai trò:** Phụ trách Ingestion, Làm sạch & Phục hồi dữ liệu.
- **Công việc chi tiết đã hoàn thành:**
  - Xây dựng module thu thập Crossref API với cơ chế Fallback offline trong `src/ingestion/crossref.py`.
  - Chuẩn hóa schema, tính toán trường `age_days` và `text_for_embedding` trong `src/ingestion/cleaning.py`.
  - Thực thi cơ chế Idempotent Repair phục hồi dữ liệu từ raw snapshot.
- **Điều học được / Đóng góp chính:**
  - Kỹ thuật truy vết nguồn gốc dữ liệu (Data Lineage) và bảo toàn raw snapshot trước khi biến đổi.

### ## Lê Việt Hoàng - 2A202602596
- **Vai trò:** Phụ trách RAG, Vector Database & Embedding.
- **Công việc chi tiết đã hoàn thành:**
  - Quản lý mô hình embedding `sentence-transformers/all-MiniLM-L6-v2` trong `src/retrieval/embeddings.py` (normalize embedding, cache model).
  - Bổ sung helper tái sử dụng trong `src/retrieval/index.py`: `load_clean_dataframe()` và `build_baseline_index()` (không đổi chữ ký các hàm cũ).
  - Nạp collection `papers-baseline` vào ChromaDB từ `data/clean/papers_clean.json`: 24 tài liệu, 24 vector, persist tại `data/chroma/`, manifest tại `data/embeddings/papers_embeddings.json`.
  - Viết script tái lập `script/build_vector_index.py`: build index + self-check retrieval (mỗi tài liệu tự truy vấn bằng title của nó phải trả về đúng `paper_id`) và in "Tín hiệu hoàn thành".
  - Kiểm chứng QA Agent trích xuất câu trả lời đúng từ metadata (`src/retrieval/qa.py`, `agent.py`).
- **Bằng chứng:**
  - `script/build_vector_index.py` chạy exit code 0, in `Đã index 24 tài liệu vào collection 'papers-baseline'` và `Self-check retrieval 5/5`.
  - Chạy lại script cho kết quả y hệt (tính idempotent: collection cũ bị ghi đè, không nhân bản vector).
- **Điều học được / Đóng góp chính:**
  - Cách cô lập các không gian vector (baseline/corrupted/repaired) để so sánh khách quan giữa dữ liệu sạch và dữ liệu bị lỗi.
- **Còn lại (đang chờ phụ thuộc):**
  - Collection `papers-corrupted` và `papers-repaired` sẽ được nạp sau khi `src/ingestion/corruption.py` hoàn thành (hiện vẫn là stub) — hai collection này tái sử dụng chính `build_baseline_index` với đường dẫn embeddings tương ứng.

### ## Mai Tiến Huy - 2A202602914
- **Vai trò:** Phụ trách Data Observability & Benchmark Evaluation.
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập Quality Gate theo chuẩn mới **Great Expectations 1.x** và giám sát Freshness SLA trong `src/observability/quality.py`.
  - Xây dựng bộ câu hỏi đánh giá chuẩn trong `src/evaluation/testset.py`.
  - Đo lường và xuất bảng đối chiếu 3 trạng thái vào `data/reports/corruption_report.md` và `data/reports/phase1_report.md`.
- **Điều học được / Đóng góp chính:**
  - Cách thiết lập hệ thống cảnh báo sớm chặn đứng hiện tượng Silent Failure trước khi dữ liệu vào serving layer.
