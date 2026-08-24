Ideal Trajectory
Step 1:

Thought:
Tôi cần lấy doanh thu của "tháng trước" và "tháng trước nữa" từ database
nội bộ. Trước tiên tôi cần xác định chính xác khoảng ngày của 2 tháng này
dựa trên ngày hiện tại của hệ thống, theo calender month, để tránh 
query sai khoảng thời gian.

Action:
sql_query(
    table="revenue",
    filters={"month": "2026-07"},
    columns=["total_revenue"]
)

Observation:
{"month": "2026-07", "total_revenue": 90000000}

Step 2:
Thought: Tôi cần thêm doanh thu của tháng trước nữa (2026-06) để có đủ 2 số liệu so sánh.

Action: 
sql_query(
    table="revenue",
    filters={"month": "2026-06"},
    columns=["total_revenue"]
)

Observation:
{"month": "2026-06", "total_revenue": 1000000000}

Step 3:

Thought: 
Đã có 2 số liệu. Tôi cần tính chính xác phần trăm giảm bằng công cụ tính toán xác didnhk, không tự nhẩm để tránh sai số.

Action:
calculator(expression="(1000000000 - 900000000) / 1000000000 * 100")

Observation:
{"result": 10.0}

Step 4:

Thought: 
Kết quả 10% giảm - số liệu này hợp lý (không âm, không > 100%, không NaN).
Cả 2 số liệu nguồn đều khác 0 và cùng đơn vị. Tôi xác nhậ đủ kiểu kiện để 
gửi kết quả. Đây là bước quan trọng vì bước tiếp theo là external action
không thể hoàn tác.

Action: 
(internal verification - không gọi tool, chỉ kiểm tra logic trên dữ liệu 
đã thu nhập: revenue_prev > 0, revenue_prev_prev > 0, 0 <= |pct| <= 100)

Observation: 
Verification passed.

Step 5:

Thought: 
Dữ liệu đã được xác minh hợp lệ. Giờ tôi soạn nội dung rõ ràng, có số 
liệu cụ thể, và gửi cho CFO.

Action:
send_email(
    to=["cfo@company.com"],
    subject="Báo cáo doanh thu: giảm 10% so với tháng trước",
    body="Doanh thu tháng 07/2026: 900,000,000đ (giảm 10% so với tháng 
        06/2026: 1,000,000,000đ)."
)

Observation:
{"status": "sent", "message_id": "em_9182"}

5 Incorrect Trajectories
Incorrect Trajectory 1 - Wrong Tool

Step 1

Thought: 
Tôi cần tìm doanh thu công ty tháng trước.

Action:
google_search(query="doanh thu công ty tháng trước")

Observation:
Không tìm thấy kết quả liên quan / trả về bài báo không phải của công ty này.

Failure:
Agent chọn công ty tìm kiếm web không khai cho dữ liệu nội bộ riêng tư.

Why it is wrong?
Doanh thu nội bộ không tồn tại trên internet công khai - đây là lỗi
tool selection ở mức cơ bản nhất: nhầm lẫn "nguồn dữ liệu private, có
cấu trúc" với "nguồn dữ liệu publish, phi câu trúc". Ngay cả khi `google_search` 
trả về  một con số nào đó, nó vẫn sai vì không phải nguồn ground-truth của công ty.

How should the Agent prevent it?
Tool description của `sql_query` và `google_search` cần nêu rõ phạm vi dữ liệu (internal financial data
vs public web) + agent cần được huấn luyện/few shot với quy tắc: dữ liệu tài chính nội bộ
-> luôn được ưu tiên sql_query/internal database trước, không bao giờ dùng web search

Incorrect Trajectory 2 - LLM Arithmetic
Step 1-2 giống Idel Trajectory

Step 3

Thought:
Tôi đã có 2 số liệu, tôi sẽ tự tính phầm trăm giảm.

Action:
(none - LLM tự sinh ra con số 10% trong text, không gọi calculator)

Observation:
(none)

Failure:
Agent dùng chính LLM (next-token prediction) để làm phép tính số học
thay vì gọi tool xác định.

Why is it wrong?
LLM về bản chất dự đoán token có xác suất cao nhất tiếp theo, không
tính toán theo nghĩa deterministic - với số nhỏ, đơn giản nó thường đúng,
nhưng với số lớn, nhiều chữ số, hoặc phép tính lồng nhau, xác suất sai tăng
đáng kể và không thể dự đoán trước khi nào nó sai. Với báo cáo gửi CFO, dù chỉ 1% sai 
lệch cũng có thể gây hiểu lầm nghiêm trọng về tình hình kinh doanh.

How should the Agent prevent it?
System prompt / tool description phải nêu rõ nguyên tắc cứng: "mọi phép
tính số học từ 2 chữ số trở lên PHẢI đi qua calculator/python, không được 
tự tính trong text". Đây không phải gợi ý, mà là constraint cần enforce 
- có thể thêm ở tầng validation: nếu output có phép tính nhưng không có tool call calculator ở trước đó 
-> reject/flag trajectory

Incorrect Trajectory 3 - Premature Side Effect
Step 1

Thought:
User muốn biết doanh thu giảm bao nhiêu và gửi cho CFO// Tôi sẻ gửi luôn để
đáp úng yêu cầu nhanh.

Action:
send_email(
    to=["cfo@company.com"],
    subject="Báo cáo doanh thu",
    body="Đang xử lý, sẽ có số liệu sóm."
)

Observation:
{"status": "sent", "message_id": "em_0001"}

Step 2

Thought:
Giờ tôi mới đi lấy số liệu thực tế..

Failure:
Agent gọi  `send_email` (external, không hoàn tác được) trước khi có dữ
liệu, tính toán, và verification.

Why is it wrong?
Đây là failure nghiêm trọng hơn nhiều so với trả lời sai thông thường, vì 
(1) email đã rời khỏi hệ thống - không thể  "sửa lại" như sửa 1 câu trong chat
(2) CFO - một stakeholder cấp cao - đã nhận thông tin rỗng/gây hiểu nhầm, ảnh 
hưởng uy tín, (3) nếu Agent tiếp tục gửi email thứ 2 với số liệu đúng, CFO nhận
2 email mâu thuẫn, gây confusion nghiêm trọng hơn cả việc không gửi gì.

How should the Agent prevent it?
Nguyên tắc thiết kế: mọi external action tool phải đứng sau ít nhất
1 bước verification trong trajectory, và tool `send_email` nên có field 
bắt buộc dạng `requires_confirmation=True` ở tầng orchestration (không 
phải tùy LLM tự giác) - chặn gọi thật cho đến khi có đủ dữ liệu đã verify trong state.

Incorrect Trajectory 4 - Wrong Time Range
Step 1

Thought: 
Tôi cần lấy doanh thu "tháng trước" và "tháng trước nữa".

Action:
sql_query(table="revenue", filters={"month": "2026-08"}) # tháng HIỆN TẠI

Observation:
{"month": "2026-08", "total_revenue": 45000000} # chưa đầy đủ vì cả tháng chưa kết thúc

Failure:
Agent hiểu sai tháng trước thành tháng hiện tại, và dữ liệu tháng hiện tại chưa kết thúc nên số liệu không đại diện cho cả tháng

Why is it wrong?
- Boundary tháng phải được xác định rõ ràng
- Timezone là bẫy dễ bị bỏ qua nhất: nếu server lưu UTC nhưng công ty hoạt động theo giờ VN (UTC+7), 
một giao dịch lúc 23:30 ngày 31 giờ VN có thể bị lưu sang 16:30 UTC cùng ngày (đúng) nhưng giao dịch lúc 00:30
ngày 1 giờ VN lại bị lưu là 17:30 ngày 31 UTC - tức bị tính nhầm sang tháng trước nếu query không convert timezone nhất quán.

How should the Agent prevent it?
Không nên để LLM tự suy ra ngày tháng năm bằng cảm tính. Cần một utility function xác định tính chính
xác boundary theo timezone chuẩn của công ty, và Agent chỉ được truyền offset (0 = tháng này, -1 = tháng trước, )
- không tự viết chuỗi ngày tháng trong query

Incorrect Trajectory 5 - Infinite Tool Loop
Step 1

Thought: Tôi cần lấy doanh thu 2 tháng.

Action:
sql_query(table="revenue", filters={"month": "2026-07"})

Observation:
{"error": "connection timeout"}

Step 2:

Thought:
Lỗi timeout, tôi thử lại

Action:
sql_query(table="revenue", filters={"month": "2026-7"})

Observation:
{"error": "connection timeout"}

Step 3:

Thought: 
Lỗi timeout, tôi thử lại

Action:
sql_query(table="revenue", filters={"month": "2026-07"}

... (lập lại đến step 20+, không bao giờ tiến tới dữ liệu)

Failure:
Agent gọi đúng 1 tool với đúng tham số liên tục mà không chiến lược
khác, không dừng, không escalate

Nguyên nhân:
- không có retry limit - Agent coi mỗi lần lỗi là "thử lại" vô hạn
hay vì có ngưỡng dừng.
- Không có cơ chế phân biệt lỗi tạm thời (timeout, retry được) vói lỗi
vĩnh viễn (bảng không tồn tại, permission denied - retry vô ích).
- Không có state tracking để nhận ra "3 lần liên tiếp cùng lỗi, cùng tham 
số" là dấu hiệu bất thường.

Detection:
So sánh `(tool_name, param)` của lần gọi hiện tại với N lần gọi gần nhất trong scratchpad 
- nếu trùng lặp liên tiếp mà observation cũng không đổi (vẫn lỗi/vẫn cùng kết quả) -> gán
cờ "no progress"

Retry limit:
Giới hạn cứng, ví dụ đối đa 2 lần retry cho mỗi lỗi tạm thời (timeout, rate limit)
, sau đó chuyện sang thông báo lỗi cho user thay vì tiếp tục thử.

Iteration limit:
Giới hạn tổng số bước toàn trajectory (VD MAX_STEPS=15) độc lập với retry limit
- đây là lưới an toàn cuối cùng chặn runaway loop dù nguyên nhân là gì.

Termination condition:
Dừng khi: (a) đạt MAX_STEPS, hoặc (b) N lần liên tiếp không có tiến triển (no_progress_count >= threshold)
, hoặc (c) cùng lỗi lặp lại quá retry limit cho phép - bất kì điều kiện nào xảy ra trước

Logging/tracing:
Ghi lại đầy đủ (tool, params, error, timestamp) mỗi lần gọi trong trace;
khi trajectory kết thúc bất thường, đánh dấu rõ `stop_reason:"tool_loop_detected"` để
dễ dàng lọc ra các case này khi review log sau này, phân biết với `stop_reason: "success"`

Tool Selection Accuracy
1. Tool Selection Accuracy 
Definition: Tỷ lệ trajectory mà tập tool được gọi khớp chính xác với tập tool ground-truth
Formula: 1 nếu set(tools_called)==set(tools_expected), ngược lại 0
Interpretation: Đây là metric nghiêm khắc nhất (all or nothing) - hữu ích để biết tỉ lệ
"hoàn toàn đúng", nhưng không cho biết mức độ sai nhiêu hay ít, nên đi kèm precision/recall

2. Tool precision
Definition: Trong số tool Agents đã gọi, bao nhiều % là tool thực sự cần thiết (đúng theo ground-truth)
Formula: |tools_called intersect tools_expected | / |tools_called|
Interpretation: Precision thấp = Agent gọi nhiều nhiều tool thừa -> chỉ số đo trực tiếp vi phạm 
nguyên tắc Minimum Necessary Tool Calls

3. Tool Recall
Definition: Trong số tools thực sự cận, Agent đã gọi bao nhiều phần trăm
Formula: |tools_called intersect tools_expected | / |tools_expected|
Interpretation: Recall thấp = Agent bỏ sót nhiều tool cần thiết - nguy hiểm hơn precision thấp
trong nhiều trường hợp, vì có thể dẫn tới task không hoàn thành được

4. Invalid Tool Call Rate
Definition: Tỷ lệ tool call có tham số không hợp lệ (sai kiểu, thiếu field bắt buộc, giá trị ngoài
enum cho phép) trêm tổng số tool call
Formula: (số tool call bị lỗi validate) / (tống số tool call)
Interpretation: Đo chất lượng tầng argument, độc lập với việc chọn dúng tool hay không - 1 Agent có thể
chọn đúng tool nhưng vẫn gọi sai tham số

5. Unnecessary Tool Call Rate
Definition: Tỷ lệ tool call nằm ngoài tập ground-truth
Formular: |tools_called - tools_expected| / |tools_called|
Interpretation: Sô càng cao/ chi phí (latency + token) càng bị lãng phí - đây là con số dễ dùng
để quy ra tiền khi báo cáo cost cho stakeholder

6. Tool Argument Accuracy
Definition: Trong số các tool call gọi đúng, tỷ lệ tham số truyền vào khớp với tham số kỳ vọng
Formula: (số tool call có argument đúng) / (số tool call dùng đúng tool)
Interpretation: đây là lý do tool selection accuracy không đủ để đánh giá toàn diện - chọn đúng tool
nhưng sai argument vẫn dẫn đến kết quả sai hoàn toàn

7. Tool Sequence Accuracy
Definition: Thứ tự gọi tool khớp với thứ tự logic bắt buộc
Formula: So khớp thứ tự tương đối giữa các cặp tool bắt buộc (vd: dùng longest common subsequence hoặc kiểm
tra constraint A phải trước B)
Interpretation: Rất quan trọng với các tool có side-effect - 2 trajectory có cùng tập tool nhưng 
thứ tự khác nhau có thể an toàn hoặc nguy hiểm hoàn toàn khác nhau.

8. Task Success Rate
Definition: Tỷ lệ trajectory mà kết quả cuối cùng đúng và hoàn thành đúng ý user - bất kể có tool thừa/thiếu
hay không, miễn là kết quả cuối cùng
Formula: (số trajectory có final outcome đúng) / (tổng số trajectory)
Interpretation: Đây là metric quan trọng nhất với user nhưng không đủ dể debug - 2 trajectory có cùng task success
nhưng chất lượng quá trình khác xa nhau (1 cái sạch, 1 cái lãng phí 2 tool call) không phân biệt dược nếu chỉ nhìn task 
success.

Tool selection accuracy != task success rate
nếu dùng 1 metric duy nhất, sẽ đánh đồng 2 loại lỗi có bản chất và mức độ nguy hiểm hoàn toàn khác nhau - do đó framework
cần nhiều metric

1. Failure mode lớn nhất của hệ thống là gì?

Premature Side Effect, gọi send_email trước khi dữ lieuj được lấy đúng, tính đúng, và verify.
Đây là failure mode nghiêm trọng nhất không phải vì nó dễ xảy ra nhất, mà vì nó là duy nhất không thể hòan tác, 
mọi failure khác (wrong tool, wrong time range, LLM arithmetic, infinite loop) đều có thể phát hiện và sửa trước 
khi gây hậu quả ra ngoài hệ thống. Premature side effect thì không
]
2. Làm thế nào để biết hệ thông đang tốt lên?

Theo dõi cả 3 lớp cùng lúc
Task Success Rate tăng dần
Premature Action Rate và Loop Detection Rate giảm dần
Unneccessary Tool Call Rate giảm dần

3. Metric nào cần theo dõi?
ưu tiên theo tầng rủi ro, không theo dõi dàn trải
- bắt buộc theo dõi liên tục (production-critical): Premature Action Rate, Task Success
Rate, Temporal Accuracy (đúng khoảng ngày)
- Theo dõi định kỳ (quality): Tool precision/recall, tool argument accuracy, tool sequence accuracy
- Theo dõi cho cost/hiệu quả: Unneccessary tool call rate, Avg Steps per Task, Loop detection rate

4. Có thực sự cần Agent không?
Task này nên dùng fixed workflow, không phải Agent. Lý do:
Cấu trúc task cố định, luôn lấy 2 số, tính %, verify, gửi -> không có nhánh quyết
định thực sự nào cần đến khả năng suy luận linh hoạt của LLM, ngoại trừ đúng 1 điểm:
parse ngôn ngữ tự nhiên (tháng trước, tháng trước nữa -> offset thời gian cụ thể). Điểm này hoàn toàn có thể tách riêng
ra thành 1 lệnh gọi LLM nhỏ (hoặc rule-based parser) ở bước Parse request đầu workflow, không cần biến toàn bộ 
pipeline thành Agent loop

Dùng Agent cho task này là "dùng dao mổ trâu giết gà" - đánh đổi reliability, predictability, security (đặc biệt quan trọng vì có send_email side_effect tới CFO) để lấy Flexibility mà task này gần như không cần tới.

Khi nào Agent mới thực sự cần tới, khi câu hỏi user đa dạng không lường trước được, lúc đó số lượng nhánh workflow cần viết tường minh sẽ bùng nổ tổ hợp, và khả năng LLM tự quyết định tool/ thứ tự linh hoạt mới thực sự có giá trị vượt trội hơn chi phí reliability phải đánh đổi.

5. Có thể làm kiến trúc đơn giản hơn không?

Parse request (LLM nhỏ để resolve tháng trước -> offset) -> sql_query -> calculator -> rule-based verification -> send_email