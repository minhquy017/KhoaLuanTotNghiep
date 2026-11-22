# SỔ TAY HỎI - ĐÁP VÀ KỊCH BẢN PHẢN BIỆN BẢO VỆ KHÓA LUẬN TỐT NGHIỆP
## Chuyên ngành: Khoa học Dữ liệu & Trí tuệ Nhân tạo (DS & AI)
### Đề tài: Hệ thống Trợ lý Du lịch Đa phương thức Spatial GraphRAG phục vụ Di sản Cố đô Huế

---

> **MỤC ĐÍCH TÀI LIỆU:**  
> Tài liệu này tổng hợp toàn bộ các phân tích bản chất kỹ thuật, sự đánh đổi kiến trúc (Architecture Trade-offs), và **kịch bản trả lời mẫu đạt điểm tối đa (10/10)** trước Hội đồng chấm khóa luận tốt nghiệp cho 4 câu hỏi phản biện chuyên sâu thuộc hàng hóc búa nhất về hệ thống AI.

---

## MỤC LỤC
1. [Vấn đề 1: Cặp mô hình CLIP ViT-B/32 + Qwen2.5-VL:7B có bị lãng phí tài nguyên không?](#vấn-đề-1-cặp-mô-hình-clip-vit-b32--qwen25-vl7b-có-bị-lãng-phí-tài-nguyên-không)
2. [Vấn đề 2: Có thể loại bỏ CLIP và để một mình Qwen2.5-VL tự nhận diện ảnh không?](#vấn-đề-2-có-thể-loại-bỏ-clip-và-để-một-mình-qwen25-vl-tự-nhận-diện-ảnh-không)
3. [Vấn đề 3: Bản chất dữ liệu: 3.528 ảnh vs. 77 ảnh (Gallery Vector vs. Testset LOOCV)](#vấn-đề-3-bản-chất-dữ-liệu-3528-ảnh-vs-77-ảnh-gallery-vector-vs-testset-loocv)
4. [Vấn đề 4: LangGraph trong bài là Workflow if-else hay AI Agent thực thụ?](#vấn-đề-4-langgraph-trong-bài-là-workflow-if-else-hay-ai-agent-thực-thụ)

---

## VẤN ĐỀ 1: Cặp mô hình CLIP ViT-B/32 + Qwen2.5-VL:7B có bị lãng phí tài nguyên không?

### 1. Bản chất kỹ thuật & Sự thật kiến trúc
Mô hình Vision-Language Model (VLM) như **Qwen2.5-VL:7B** cấu thành từ 3 thành phần:
$$\text{Qwen2.5-VL:7B} = \underbrace{\text{Vision Transformer (ViT ~1,2B)}}_{\text{Mã hóa thị giác}} + \underbrace{\text{Cross-Attention Projector (~0,2B)}}_{\text{Cầu nối đa phương thức}} + \underbrace{\text{LLM Backbone (~6B)}}_{\text{Bộ não ngôn ngữ}}$$

Trong luồng thực thi 2 giai đoạn (Decoupled Pipeline):
1. **Giai đoạn 1 (Thị giác):** Ảnh đầu vào được đưa qua **CLIP ViT-B/32** $\to$ so khớp véc-tơ với ChromaDB $\to$ trích xuất ra đúng một nhãn văn bản: `place_id = "hue_kdt_01"` (Lăng Khải Định).
2. **Giai đoạn 2 (Ngôn ngữ):** Hệ thống dùng `place_id` duyệt Đồ thị Tri thức (KG) để lấy thông tin món ăn, tọa độ, lịch sử. Sau đó đóng gói toàn bộ thành **chuỗi văn bản thuần túy (Text Prompt)** đưa vào **Qwen2.5-VL:7B**.

👉 **Sự lãng phí thực tế:**
* Vì Prompt đưa vào Qwen2.5-VL **chỉ có chữ (tokens)** mà không truyền ma trận điểm ảnh (pixel tensor), khối **Vision Transformer (~1,2 tỷ tham số)** của Qwen2.5-VL hoàn toàn không được sử dụng nhưng vẫn chiếm dung lượng bộ nhớ.
* Trên phần cứng máy trạm cá nhân **RTX 3050 (4GB VRAM)**, việc nạp bản lượng tử hóa của Qwen2.5-VL buộc Ollama phải đẩy bớt layer sang **RAM CPU**, làm nghẽn băng thông và đẩy độ trễ suy luận lên **7,7 giây**.
* Ngoài ra, một LLM thuần văn bản (Text-only) như `Qwen2.5-7B-Instruct` sẽ có khả năng lập luận, xuất định dạng JSON và xử lý ngữ pháp tiếng Việt sắc bén hơn một mô hình VLM đa nhiệm.

### 2. Hai hướng tối ưu hóa kỹ thuật (Trade-offs)
* **Hướng 1 (Thực dụng cho thiết bị biên):** Giữ nguyên `CLIP ViT-B/32` (siêu nhẹ, chỉ ~300MB VRAM) để nhận diện địa danh, thay `Qwen2.5-VL` bằng mô hình thuần văn bản **`Qwen2.5-7B-Instruct`** (hoặc bản `3B`). Thời gian đáp ứng sẽ giảm ngay từ 7,7s xuống còn **2,5s – 3,5s**.
* **Hướng 2 (Khai thác trọn vẹn sức mạnh VLM):** Sau khi CLIP định danh `place_id`, truyền **cả ảnh gốc lẫn ngữ cảnh KG** vào Qwen2.5-VL để thực hiện Visual Question Answering (VQA) sâu: phân tích thời tiết, góc chụp thực tế của bức ảnh để gợi ý góc chụp ảnh check-in đẹp hơn.

### 3. Kịch bản trả lời Hội đồng 10/10
> *"Dạ thưa Thầy/Cô, nhận xét này hoàn toàn chính xác về mặt tối ưu hóa tài nguyên phần cứng. Trong kiến trúc hiện tại, vì khâu nhận diện thị giác đặc thù địa phương (Fine-grained Landmark Retrieval) đã được giải quyết trọn vẹn và chuẩn xác bởi CLIP và ChromaDB, nên tầng sinh câu trả lời thực chất chỉ nhận ngữ cảnh văn bản thuần túy.*
> 
> *Ban đầu nhóm tích hợp Qwen2.5-VL với định hướng phát triển tính năng VQA sâu — tức là ngoài việc nhận diện địa danh, mô hình có thể đọc được hoa văn bia đá và phân tích bố cục ánh sáng trực tiếp trong ảnh của du khách. Tuy nhiên, để tối ưu hóa triệt để trên môi trường thiết bị biên cá nhân RTX 3050 4GB VRAM, nhóm xác định hướng tinh gọn tối ưu cho môi trường sản xuất (Production) là chuyển tầng sinh văn bản sang mô hình Text-only như `Qwen2.5-7B-Instruct`. Việc này sẽ giải phóng hoàn toàn ~1,2B tham số của Vision Encoder, giảm độ trễ từ 7,7s xuống dưới 3,5s mà vẫn bảo toàn 100% độ chính xác tri thức địa phương."*

---

## VẤN ĐỀ 2: Có thể loại bỏ CLIP và để một mình Qwen2.5-VL tự nhận diện ảnh không?

### 1. Bản chất kỹ thuật & Sự cố sụp đổ hệ thống (Cascading Failure)
Tuyệt đối **KHÔNG NÊN** loại bỏ CLIP vì 4 nguyên nhân khoa học:

1. **Ảo giác nặng với Di tích hẹp (Domain Gap & Fine-grained Recognition):**
   * Các mô hình VLM toàn cầu (Qwen-VL, GPT-4o) chỉ nhận diện tốt các danh thắng nổi tiếng thế giới (Tháp Eiffel, Vịnh Hạ Long, hoặc góc toàn cảnh Ngọ Môn).
   * Đối với các di tích hẹp và chi tiết cổ kính ở Huế (phân biệt giữa *Lăng Thiệu Trị* vs. *Lăng Gia Long*; *Chùa Từ Hiếu* vs. *Chùa Huyền Không Sơn Thượng*; *Cửa Hiển Nhơn* vs. *Cửa Chương Đức*), VLM ở chế độ Zero-shot sẽ **bị ảo giác nghiêm trọng**, đoán mò thành các công trình ở Trung Quốc hoặc miền Bắc.
   * Khi đoán sai tên di tích $\to$ sai tọa độ GPS $\to$ toàn bộ thuật toán Spatial GraphRAG định tuyến sai hoàn toàn.
2. **CLIP + ChromaDB là chốt chặn tất định (Local Grounding):**
   * CLIP không sinh chữ tự do; nó đóng vai trò là hàm trích xuất véc-tơ đặc trưng (Feature Extractor).
   * Khi tính khoảng cách Cosine giữa ảnh truy vấn và kho véc-tơ tham chiếu, hệ thống thực hiện phép tìm kiếm láng giềng gần nhất ($k$-NN) trên tập dữ liệu đã xác thực địa phương, đạt độ chính xác kiểm chuẩn LOOCV Top-1 **98,7%** và Top-3 **100,0%**.
3. **Giới hạn phần cứng (Không thể Few-shot nhiều ảnh vào VLM):**
   * Mỗi bức ảnh đưa vào VLM sẽ chiếm hàng trăm token hình ảnh. Nếu nhồi hàng chục ảnh mẫu vào Context Window của Qwen2.5-VL, GPU 4GB VRAM sẽ bị lỗi **OOM (Out of Memory)** ngay lập tức.
   * Ngược lại, CLIP + ChromaDB chỉ mất **42,5 mili-giây** và tiêu thụ chưa đầy 300MB RAM.
4. **Hàm lượng học thuật của Khóa luận:**
   * Việc loại bỏ CLIP sẽ làm mất đi toàn bộ đóng góp về mảng **Thị giác Máy tính (Computer Vision)**, công thức toán học InfoNCE, ma trận tương đồng $S_{CLIP}$ và bảng thực nghiệm LOOCV tại Chương 2.

### 2. Kịch bản trả lời Hội đồng 10/10
> *"Dạ thưa Thầy/Cô, việc giữ lại CLIP ViT-B/32 là chốt chặn bắt buộc để đảm bảo tính chính xác địa phương (Domain-specific Grounding). Các mô hình VLM tổng quát như Qwen-VL khi nhìn các công trình cổ tại Huế rất dễ bị ảo giác do khoảng cách miền dữ liệu (Domain Gap), không thể phân biệt được các di tích có nét kiến trúc tương đồng như các cổng thành hay lăng tẩm triều Nguyễn.*
> 
> *CLIP kết hợp ChromaDB đóng vai trò như một bộ lọc không gian đóng (Closed-set Identifier), ánh xạ chính xác ảnh chụp của du khách về đúng mã thực thể `place_id` trong Đồ thị Tri thức với độ chính xác Top-1 đạt 98,7% và thời gian truy vấn chỉ 42,5ms. Nếu bỏ CLIP mà để VLM tự phán đoán, sai số nhận diện ban đầu sẽ gây ra lỗi dây chuyền (Cascading Failure), phá vỡ toàn bộ ràng buộc không gian của hệ thống GraphRAG phía sau."*

---

## VẤN ĐỀ 3: Bản chất dữ liệu: 3.528 ảnh vs. 77 ảnh (Gallery Vector vs. Testset LOOCV)

### 1. Phân định rõ hai tập dữ liệu

| Tiêu chí | Kho véc-tơ tham chiếu (**3.528 ảnh**) | Tập kiểm chuẩn thực nghiệm (**77 ảnh / 25 di tích**) |
| :--- | :--- | :--- |
| **Bản chất** | **Gallery Set / Vector Knowledge Base** | **Gold-standard Test Set** |
| **Mục đích** | Cơ sở dữ liệu tri thức thị giác nạp vào ChromaDB collection `hue_landmarks_visual` để hệ thống tra cứu đa phương thức (Visual RAG). | Tập dữ liệu kiểm thử độc lập dùng để đo lường độ chính xác nhận diện của mô hình. |
| **Phạm vi** | Bao phủ 612 địa điểm di tích, ẩm thực, lưu trú, cảnh quan trên toàn Thừa Thiên Huế. | 25 danh lam thắng cảnh & di tích trọng điểm nhất, mỗi nơi gồm 2–4 góc chụp thực tế khác nhau (cận cảnh, góc nghiêng, ánh sáng khác nhau). |
| **Giao thức** | Lưu trữ véc-tơ 512 chiều trích xuất bởi CLIP ViT-B/32. | Thực nghiệm kiểm định chéo loại từng phần tử (Leave-One-Out Cross-Validation -- LOOCV). |

### 2. ⚠️ Lưu ý sống còn về cách dùng từ khi bảo vệ
* ❌ **KHÔNG NÓI:** *"3.000 ảnh là dữ liệu cho mô hình HỌC / TRAIN"* $\to$ Hội đồng sẽ bắt bẻ ngay: *"Em train bao nhiêu epoch? Dùng loss gì? Máy 4GB sao train nổi?"*.
* ✅ **NÓI CHUẨN:** *"3.528 ảnh là **Kho dữ liệu véc-tơ phục vụ nhánh Visual RAG (Multimodal RAG)** để mô hình tra cứu so khớp, còn 77 ảnh là **Tập kiểm thử độc lập (Test Set)** theo giao thức LOOCV."*

### 3. Kịch bản trả lời Hội đồng 10/10
> *"Dạ thưa Thầy/Cô, hệ thống không hề huấn luyện lại (Retrain) mô hình nền CLIP mà áp dụng kiến trúc **Visual RAG (Multimodal RAG)**:*
> * *Kho **3.528 ảnh** chính là **Cơ sở dữ liệu véc-tơ tham chiếu (Gallery Knowledge Base)** bao phủ 612 địa điểm du lịch Huế, được số hóa thành các véc-tơ nhúng 512 chiều lưu trữ trong ChromaDB.*
> * *Tập **77 ảnh** là **Tập kiểm chuẩn có nhãn vàng (Gold-standard Evaluation Set)** đại diện cho 25 di tích trọng điểm. Để chứng minh tính trung thực khoa học và triệt tiêu hoàn toàn hiện tượng rò rỉ dữ liệu (Data Leakage hay Train-on-Test), nhóm áp dụng giao thức LOOCV: mỗi lần kiểm thử, véc-tơ của chính bức ảnh đó bị loại bỏ tạm thời khỏi không gian tìm kiếm, và mô hình phải tìm đúng công trình đó dựa trên các góc chụp còn lại trong cơ sở dữ liệu."*

---

## VẤN ĐỀ 4: LangGraph trong bài là Workflow if-else hay AI Agent thực thụ?

### 1. Bản chất lý thuyết: Workflow vs. Autonomous Agent
* **Autonomous Agent (Tác tử tự do - ReAct Pattern):** LLM tự quyết định hành động trong một vòng lặp kín (*Thought $\to$ Action $\to$ Observation $\to$ Thought*), tự chọn gọi Tool nào, tự quyết định khi nào dừng lại.
* **Structured Agentic Workflow (Quy trình tác tử có cấu trúc - CRAG Pattern):** Các trạng thái và đường đi được lập trình tường minh qua đồ thị trạng thái (`StateGraph`), LLM đảm nhiệm vai trò suy luận/đánh giá tại các nút (Node).

👉 **Thực tế đồ thị LangGraph của đề tài:**
Là một **Directed Acyclic Graph (DAG)** gồm 5 bước: `Extractor` $\to$ `Spatial KG` $\to$ `Grader` $\to$ `(Fallback / Generator)`. Luồng rẽ nhánh dựa trên điểm tin cậy $S_{conf} \ge 0,65$ tại nút `Grader`.

### 2. Tại sao đây vẫn là "Agentic RAG" chứ không phải if-else tầm thường?
1. **Mô hình kinh điển Corrective RAG (CRAG - Yan et al., 2024) [Đã trích dẫn tại mục [8]]:** 
   * Naive RAG là tuyến tính mù quáng: tìm gì đưa nấy.
   * Hệ thống của đề tài có nút **`Grader`** thực hiện cơ chế **Tự suy ngẫm (Self-reflection)**: chấm điểm độ tin cậy của ngữ cảnh. Nếu dữ liệu thiếu hụt ($S_{conf} < 0,65$), hệ thống chủ động kích hoạt hành động sửa sai (Corrective Action) là gọi Web Search bên ngoài theo đúng mô hình bài báo gốc CRAG (Yan et al., 2024). Đây chính là hạt nhân định nghĩa của Agentic RAG.
2. **Đã triệt tiêu hoàn toàn mâu thuẫn câu chữ trong Khóa luận:**
   * Ở **Mục 1.3 (Trang 14)**: Đã xóa chữ *"có chu trình"*, thay bằng *"Đồ thị Trạng thái hữu hạn (StateGraph) với các điểm rẽ nhánh điều kiện và kiểm soát trạng thái tập trung theo mô hình Corrective RAG (CRAG) [8]"*.
   * Ở **Mục 1.4.1 (Trang 42)**: Đã đổi tiêu đề thành *"Máy trạng thái StateGraph và Luồng điều phối Tác tử có Cấu trúc"*, gắn liền với trích dẫn `[8]`, triệt tiêu hoàn toàn từ *"đa tác tử"* gây hiểu nhầm sang Autonomous Multi-Agent tự do.
3. **Sự đánh đổi kỹ thuật có chủ đích (Deliberate Engineering Trade-off):**
   * **Khống chế độ trễ (Bounded Latency):** Trên máy trạm biên RTX 3050, mỗi lượt suy luận LLM 7B mất ~1,5s – 2s. Nếu để vòng lặp ReAct tự do, độ trễ sẽ vọt lên 20–30 giây hoặc rơi vào vòng lặp vô hạn (Infinite Loop).
   * **Tính tất định & An toàn (Determinism & Guardrails):** Ứng dụng du lịch cần sự chính xác tuyệt đối về giá vé, giờ mở cửa và cự ly đi bộ, không thể để agent tự do gọi hàm ngẫu hứng.
   * Khuyến nghị của Anthropic (*Building Effective Agents*): *"Trong thực tế sản xuất, Workflows có kiểm soát mang lại độ tin cậy và hiệu năng vượt trội hơn nhiều so với các tác tử tự do không biên giới"*.

### 3. Kịch bản trả lời Hội đồng 10/10
> *"Dạ em cảm ơn Thầy/Cô, nhận xét này rất chính xác và sắc sảo về mặt phân loại kiến trúc hệ thống AI. Hệ thống của em không phải là một **Autonomous ReAct Agent tự do** (vốn có vòng lặp không giới hạn và tự gọi hàm động), mà chính xác là một **Structured Agentic Workflow** được xây dựng trên nền tảng LangGraph theo mẫu hình **Corrective RAG (CRAG)**.*
> 
> *Tính chất 'Agentic' trong đề tài thể hiện ở việc hệ thống không truy xuất mù quáng như Naive RAG, mà có nút **Grader** thực hiện nhiệm vụ **Tự suy ngẫm (Self-reflection)**: tự động đánh giá độ tin cậy ngữ cảnh và chủ động kích hoạt hành vi sửa sai (Fallback sang Web Search) khi Đồ thị Tri thức bị khuyết thiếu dữ liệu thời gian thực.*
> 
> *Nhóm chủ động không thiết lập vòng lặp chu trình (Cycle) vô tận vì đây là một **sự đánh đổi kỹ thuật có chủ đích**: trên máy trạm biên RTX 3050 4GB VRAM, luồng trạng thái có cấu trúc giúp đảm bảo thời gian phản hồi thực tế dưới 8 giây và triệt tiêu hoàn toàn rủi ro treo hệ thống do vòng lặp vô hạn. Hướng nâng cấp hệ thống sang chuẩn Model Context Protocol (MCP) và Dynamic Tool-Calling khi có hạ tầng GPU mạnh hơn đã được nhóm nêu rõ trong phần Hướng phát triển tương lai ở trang 78 của khóa luận."*

---

## BẢNG TỔNG KẾT TỪ KHÓA ĐẮT GIÁ CẦN DÙNG KHI BẢO VỆ

| Khái niệm thông thường | Cụm từ học thuật "chuẩn điểm 10" nên nói |
| :--- | :--- |
| "3.000 ảnh cho mô hình học" | **"Cơ sở dữ liệu véc-tơ tham chiếu (Gallery Knowledge Base) phục vụ Visual RAG"** |
| "77 ảnh test" | **"Tập kiểm chuẩn có nhãn vàng (Gold-standard Testset) theo giao thức LOOCV"** |
| "If-else rẽ nhánh" | **"Luồng tác tử có cấu trúc (Structured Agentic Workflow) theo mẫu hình Corrective RAG (CRAG)"** |
| "Chấm điểm tin cậy" | **"Cơ chế Tự suy ngẫm và Đánh giá ngữ cảnh (Self-Reflection Grader)"** |
| "Chạy trên laptop yếu" | **"Triển khai tối ưu hóa trên thiết bị biên với tài nguyên phần cứng hạn chế (Edge Deployment on Resource-Constrained Hardware)"** |
| "Không cho vòng lặp lặp lại" | **"Sự đánh đổi kỹ thuật có chủ đích nhằm khống chế chặn trên độ trễ (Bounded Latency Trade-off) và tránh vòng lặp vô hạn"** |

