tool description mơ hồ  -> Agent không biết nó đang tìm cái gì trong không gian nào 
-> LLM buộc phải đoán query, khi context không đầy đủ, nó tạo ra query rỗng nghĩa 
-> đây không phải lỗi của Agent -> đây là lỗi thiết kế interface

def search(
    query: str,
    source: Literal["web", "internal_kb", "product_catalog"],
    top_k: int = 5,
    date_from: str | None = None,
) -> SearchResult

1. Tool description nên viết như nào?
Nguyên tắc: mô tả phải trả lời được 3 câu hỏi cho LLM trước khi nó gọi 
tool - dùng để làm gì/khi nào dùng/khi nào không dùng

"search: tìm kiếm thông tin từ một nguồn dữ liệu cụ thể. Dùng khi cần tìm sản phẩm,
tài liệu nội bộ, hoặc thông tin wweb theo một câu hỏi/từ khóa cụ thể.

Ví dụ tốt: search(query='laptop RAM 32gb dưới 30 triệu',
                    source='product_catalog', top_k=5)
Ví dụ không nên: search(query='thông tin hữu ích', source='web')

Không dùng tool này để: tra cứu chi tiết 1 sản phẩm đẫ biết ID (dùng get_product_detail),
hoặc lấy đánh giá người (dùng get_review)."

Ba phần bắt buộc trong description: a. chức năng, b. ví dụ input tốt/xấu cụ thể (few shot
ngay trong description - hiệu quả hơn trừu tượng nhiều) c. ranh giới rõ vói tool lân cận dễ gây nhầm

2. Parameter nào bắt buộc?
-query
-source

3. Parameter nào optional?
-top_k
-date_from

4. Agent cần biết điều gì trước khi gọi tool?
-không gian source hợp lệ
-query nên đặt tả theo domain nào
-chi phí/latency tương tối giữa các source (vd: web search chậm&tốn hơn internal_kb)
-để agent ưu tiên nguồn rẻ trước nếu đủ

5. Tool nên trả về raw text hay structured JSON?
Structured JSON, luôn luôn, vì 2 lý do:
-Agent (LLM) cần parse lại kết quả ở bước tiếp theo - JSON có field cố định 
giúp LLM trích xuất chính xác hơn nhiều so với phải tự đọc hiểu một text dài.
-Structured output mới cho phép dedup, ranking, filter bằng code trước khi
đưa vào context - giảm token, giảm khả năng LLM bị ngợp bởi text thừa/

Bài tập nâng cao:

def search_documents(
    query: str,
    doc_type: Literal["policy", "spec", "faq", "report"],
    top_k: int = 5,
) -> list[DocumentResult]:
    """READ-ONLY. Tìm tài liệu nội bộ.
    Không dùng để tìm sản phẩm hay gửi thông tin cho ai.
    An toàn để gọi nhiều lần, không có side effect."""

def send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    requires_confirmation: bool = True,
) -> EmailSendResult:
    """WRITE - SIDE EFFECT không thể hoàn tác. Gửi email thật tới người nhận thật. 
    Chỉ gọi khi Agent có đủ nội dung body hoàn chỉnh, không gọi để thử.
    Nếu không chắc người nhận hoặc nội dung, phải hỏi lại user trước, không tự đoán."""

def query_database(
    table: Literal["users", "orders", "products", "tickets"],
    filters: dict,
    columns: list[str] | None = None,
    limit: int = 50,
) -> list[dict]:
    """READ-ONLY. Truy vấn dữ liệu có cấu trúc từ database nội bộ theo bảng + filter.
    Không dùng để tìm kiếm mờ theo ngôn ngữ tự nhiên (dùng search_documents/search)
    không có quyền UPDATE/DELETE - tool này chỉ đọc."""

def create_ticket(
    title: str,
    description: str,
    priority: Literal["low", "medium", "high", "urgent"],
    assignee: str | None = None,
) -> TicketCreateResult:
    """WRITE - tạo bản ghi mới (có thể hoàn tác bằng cách đóng ticket, nhưng vẫn để lại log).
    Dùng khi cần escalate một vấn đề con người cần xử lý tiếp.
    KHÔNG dùng để gửi thông báo đơn thuần (dùng send_email nếu chỉ cần thông báo, 
    không cần theo dõi trạng thái xử lý)."""

    
