"""
1. Khi nào Agent cần gọi tool?

Agent gọi tool khi thiếu thông tin cần thiết mà không thể suy luận từ những gì đã biết.
Cụ thể với bài toán này:
- Chưa có danh sách ứng viên laptop nào? -> gọi search_product(query) với query được rút ra từ budget +_ yêu cầu
- Có product_id nhưng chưa chưa biết spec chi tiết (RAM, CPU, giá thực tế) -> gọi get_product_detail(product_id))
- Đã có vài ứng viên tiềm năng nhưng chưa biết độ tin cậy thực tế (pin yếu, tản nhiệt kém,...) -> gọi get_review(product_id)
- Có >= 2 ứng viên gần tương đương, cần phân biệt rạch ròi trước khi chốt top 3 -> gọi compare_products(product_ids)

Không gọi tool khi câu hỏi có thể trả lời bằng suy luận dữ liệu đã có trong scratchpad, hoặc khi đã đủ dữ liệu cho 3 ứng viên tốt nhất

2. Khi nào Agent nên dừng?
- Dừng và trả Final Answer khi tất cả đúng:
Đã có >= 3 ứng viên có đủ: spec chi tiết + review + đã so sánh với nhau
Có thể xếp hạng rõ ràng 3 ứng viên tốt nhất theo tiêu chí (giá, hiệu năng, độ tin cậy)

Dừng sớm khi:
- Hết step budget
- tool liên lục lỗi/ không có dữ liệu

3. Agent có được gọi cùng tool nhiều lần không?
có nhưng có điều kiện. Gọi lại cùng tool là hợp lý khi tham số khác nhau. 
Nhưng cấm gọi lại y hệt tool + y hệt tham số đã gọi trước đó - đây là dấu hiện loop vô nghĩa (redundant call)
, phải chặn bằng cache/dedup

4. Giới hạn tối đa bao nhiêu bước?
không có tuyệt đối, nhưng nguyên tắc thiết kế:
- ước lượng số bước tối thiểu:  search (1) + detail (5) + review (5) + compare(1) =12
- đặt MAX_STEPS = 15-20 

5. Làm sao để tránh infinite loop?
kết hợp nhiều lớp phòng thủ
- Step budget cứng: đếm step_count, vượt MAX_STEPS thì dừng
- Dedup/call cache: lưu tập (tool_name, params_hash) đã gọi, nếu Agent định gọi lại y hệt
-> chặn, ép Reason lại hoặc coi là kết thúc
- Progress check: theo dõi xem scratchpad có tiến triển sau mỗi bước không
- Timeout tổng: độc lập với stepcount, trong trường hợp 1 tool call bị treo lâu
- Tool error backoff: nếu 1 tool lỗi liên tục >= 3 lần cùng với tham số -> đánh dấu unavailable


"""

MAX_STEPS = 18
MAX_NO_PROGRESS_STEPS = 4
MAX_RETRIES_PER_CALL = 2

def run_agent(user_query, budget, requirements):
    state = {
        "goal": {"budget": budget, "requirements": requirements},
        "candidates": {},
        "compared": False,
        "scratchpad": [],
        "call_cache": {},
        "step_count": 0,
        "no_progress_count": 0,
    }

    while True:
        state["step_count"] += 1

        if state["step_count"] > MAX_STEPS: 
            return finalize(state, reason="step_budget_exceeded")

        if state["no_progress_count"] >= MAX_NO_PROGRESS_STEPS:
            return finalize(state, reason="no progress")

        decision = reason(state) # LLM call

        if decision.type == "FINAL_ANSWER" and is_sufficient(state):
            return finalize(state, reason="sufficient_info")
        
        if decision.type == "TOOL_CALL":
            tool_name = decision.tool_name
            params = decision.params
            call_key = (tool_name, hash(params))
        
            if call_key in state["call_cache"]:
                state["scratchpad"].append(
                    f"[Blocked] Duplicate call: {tool_name}({params}) - reuse cached result"
                )
                observation = state["call_cache"][call_key]
            else:
                observation = call_tool_with_retry(
                    tool_name, params, max_retries=MAX_RETRIES_PER_CALL
                )
                state["call_cache"][call_key] = observation
            
            progressed = update_state(state, tool_name, params, observation)
            state["scratchpad"].append(
                {"tool": tool_name, "params": params, "observation": observation}
            )

            if progressed:
                state["no_progress_count"] = 0
            else:
                state["no_progress_count"] += 1
            
            continue
        
        state["no_progress_count"] += 1

def is_sufficient(state):
    ranked = [c for c in state["candidates"].values() if c.get("detail") and c.get("review")]
    return len(ranked) >= 3

def call_tool_with_retry(tool_name, params, max_retries):
    for attempt in range(max_retries + 1):
        result = invoke_tool(tool_name, params)
        if result.ok:
            return result
        
    return {"ok": False, "error": "tool_unavailable_after_retries"}

def finalize(state, reason):
    top3 = rank_candidate(state["candidates"], state["goal"])
    return {
        "answer": top3,
        "stop_reason": reason,
        "steps_used": state["step_count"],
    }

"""
1. Failure mode lớn nhất của thiết kế này?
Agent bị ảo giác đủ dữ liệu - tự cho là đã có đủ info để so sánh trong khi review/detail thực ra lỗi hoặc lỗi âm thầm
is_sufficient() chỉ check sự tồn tại của field, không check chất lượng dữ liệu

2. Làm thế nào để biết hệ thống đang tốt lên?
Theo dõi qua thời gian: tỷ lệ task hoàn thành đúng với số bước dự kiên (ko chạm MAX_STEPS)
tỷ lệ duplicate-call bị chặn giảm dần(agent không hơn, ít lặp vô ích), và độ chính xác của top-3
so với con người

3. Metric nào cần theo dõi?
- số bước trung bình/task (efficiency)
- tỉ lệ tool thành công với lỗi
- tỉ lệ dừng so do step_budget exceed hoặc no progress
- độ chính xác top-3 so với ground truth
- latency tổng end to end

4. Có thực sự cần Agent không?
Không hẳn - nếu catalog laptop có sẵn structured data, một pipeline workflow cố định (filter theop  budget -> 
-> rank theo điểm -> lấy top 3) rẻ hơn, nhanh hơn, dễ debug hơn nhiều so với agent loop
có LLM reasoning ở mỗi bước. Agent chỉ thực sự khi caafnkhi truy vấn người dùng đa dạng, mơ hồ cần tool selectionlinh hoạt

5. Có thể làm kiến trúc đơn giản hơn không?
Có - một workflow tuyến tính cố định: search -> detail (parallel cho top N) ->
review (parallel cho top N) -> compare -> rank, không cần Agent tự reason chọn tool ở
mỗi bước vì trình tự gần như luôn giống nhau. Chỉ nên giữ agent loop thật sự nếu 
bước tiếp theo phụ thuộc vào kết quả bước trước theo cách khó định trước

"""