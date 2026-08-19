Rules:
Nếu các bước xử lý đã biết trước -> Workflow
Nếu cần tìm thông tin tron knowledge base -> RAG
Nếu chỉ cần một lần suy luận/generation -> LLM call
Nếu hệ thống phải tự quyết định bước tiếp theo dựa trên tình huống và tool result -> Agent

1. Tóm tắt một PDF
Sử dụng LLM đơn
- Architecure: PDF -> Extract text -> Chuck/preprocess -> LLM -> Summary

2. Tra cứu chính sách công ty rồi trả lời câu hỏi
RAG
- Architecture: User question -> Retriever -> Company policy documents -> relevant chunks -> LLM -> Answer + citation

3. Nhận yêu cầu khách hàng, kiểm tra database, gửi email và cập nhật CRM.
Workflow cố định
- Receive request -> check customer in database -> update database -> send confirmation email -> update CRM

4. Dịch tiếng Việt sang tiếng Anh.
LLM call
- Vietnamese -> LLM -> English

5. Điều tra nguyên nhân server production bị CPU 100%
Agent
- Agent thực sự cần nếu investigation path không biết trước
- Agent phải đưa ra những hành động: CPU high -> Which process -> Process identified -> Why is process consuming CPU?
-> Check logs OR metrics OR deployment -> Based on result, chooose next tool -> Repeat
- Nếu không dùng agent thì dùng workflow

6. Sinh mô tả sản phẩm từ JSON
LLM call
- JSON -> Prompt -> LLM -> Product Description

7. Research một công ty từ nhiều nguồn rồi tạo báo cáo
Agent
- Agent thực sự cần nếu đây là research mở và không biết cần bao nhiêu bước
- Agent phải đưa ra những hành động nào: Ví dụ nguồn A tăng 30%, nhưng nguồn này cũ rồi. Tôi cần tìm nguồn mới hơn. Hoặc tôi chưa có đủ information -> search thêm. Hai nguồn mâu thuẫn -> tìm nguồn thứ 3. Đây chính là dynamic planning + replanning
- Nếu biết bao nhiêu bước và số người thì Agent không cần -> workflow

8. Đặt lịch họp phù hợp cho 5 người 
Agent + tools 
- Agent không thực sự cần thiết vì yêu cầu rõ (tìm slot mà cả 5 người đều rảnh trong cả 2 tuần tới trong giờ làm việc)
-> có thể làm bằng algorithm + workflow
- Agent phải quyết định những hành động: nếu không có slot nào -> mở rộng thời gian tìm kiếm, nếu 5 người không có slot chung -> tìm slot có 4/5 người,..
- Có thể làm bằng algorithm +_ workflow và có khi tốt hơn Agent vì scheduling là bài toán constraint optimization

Điểm cộng - Khi Agent khiến hệ thống tệ hơn
Đặt lịch họp cho 5 người bằng Agent trong khi bài toán chỉ là constraint matching
Thay vì calenderAPI -> Intersection algo -> best slot 
Bạn xây LLM -> Agent -> calender tool -> LLM -> calender tool -> LLM -> ...
 
Kết quả có thể 
- tốn token hơn
- latency cao hơn
- khó predict
- khó debug
- dễ gọi tool sai
- tạo meeting ngoài ý muốn
...


