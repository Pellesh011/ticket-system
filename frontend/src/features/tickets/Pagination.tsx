import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { setPage, selectPagination } from "./ticketsSlice";

function getPageWindow(current: number, total: number): (number | "...")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | "...")[] = [1];

  if (current > 3) {
    pages.push("...");
  }

  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (current < total - 2) {
    pages.push("...");
  }

  if (total > 1) {
    pages.push(total);
  }

  return pages;
}

export function Pagination() {
  const dispatch = useAppDispatch();
  const { page, total_pages, total } = useAppSelector(selectPagination);

  if (total_pages <= 1) return null;

  const pages = getPageWindow(page, total_pages);

  return (
    <div className="pagination">
      <span>Total: {total}</span>
      <div className="pagination-controls">
        <button
          disabled={page <= 1}
          onClick={() => dispatch(setPage(page - 1))}
        >
          Prev
        </button>
        {pages.map((p, i) =>
          p === "..." ? (
            <span key={`ellipsis-${i}`} className="pagination-ellipsis">
              ...
            </span>
          ) : (
            <button
              key={p}
              className={p === page ? "active" : ""}
              onClick={() => dispatch(setPage(p))}
            >
              {p}
            </button>
          ),
        )}
        <button
          disabled={page >= total_pages}
          onClick={() => dispatch(setPage(page + 1))}
        >
          Next
        </button>
      </div>
    </div>
  );
}
