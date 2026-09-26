"""Build va self-check ChromaDB collection `papers-baseline` (pham vi M3: RAG & Vector Index).

Chay:  python script/build_vector_index.py
Input : data/clean/papers_clean.json (artifact cua buoc cleaning)
Output: data/chroma/ (ChromaDB persist) + data/embeddings/papers_embeddings.json (manifest)
"""
from __future__ import annotations

from core.config import load_settings
from retrieval.index import build_baseline_index, load_clean_dataframe


def main() -> None:
    settings = load_settings()
    dataframe = load_clean_dataframe(settings)
    if dataframe.empty:
        raise SystemExit("Khong co du lieu sach de index. Chay cleaning pipeline truoc.")

    index = build_baseline_index(settings)
    stored = index.collection.count()

    print(f"Tín hiệu hoàn thành: Đã index {len(index.documents)} tài liệu vào collection '{index.collection_name}'")
    print(f"Tín hiệu hoàn thành: ChromaDB persist tại {index.persist_path} (vectors lưu = {stored})")
    print(f"Tín hiệu hoàn thành: Manifest embedding tại {settings.paths.embeddings_json}")

    if stored != len(dataframe):
        raise SystemExit(f"Lech so luong: dataframe={len(dataframe)} nhung ChromaDB={stored}")

    # Self-check retrieval: moi tai lieu truy van bang chinh title cua no phai tra ve chinh no trong top-k.
    sample_size = min(5, len(index.documents))
    hits = 0
    for document in index.documents[:sample_size]:
        results = index.search(document["title"], top_k=settings.top_k)
        if any(item.paper_id == document["paper_id"] for item in results):
            hits += 1

    print(f"Tín hiệu hoàn thành: Self-check retrieval {hits}/{sample_size} tài liệu tự truy vấn đúng paper_id")
    if hits != sample_size:
        raise SystemExit("Self-check retrieval that bai: index tra ve sai tai lieu.")

    probe = "What categories does the paper use for retrieval augmented generation?"
    top = index.search(probe, top_k=1)
    if top:
        print(f"Tín hiệu hoàn thành: Sample query -> '{top[0].title[:70]}' (score={top[0].score:.4f})")


if __name__ == "__main__":
    main()
