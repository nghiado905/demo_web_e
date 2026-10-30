import json
import sqlite3
from app.database import get_connection

TEST_SETS = [
    {
        "id": "toeic_part5_01",
        "title": "TOEIC Part 5: Luyện Đề Thực Chiến Số 01",
        "description": "20 câu ngữ pháp & từ vựng chọn lọc format TOEIC Part 5 sát với đề thi thật ETS.",
        "category": "TOEIC Practice",
        "difficulty": "B1 - B2",
        "time_limit": 15,
        "badge": "TOEIC 650+",
        "created_at": "2026-01-10 10:00:00"
    },
    {
        "id": "toeic_part5_02",
        "title": "TOEIC Part 5: Luyện Đề Thực Chiến Số 02",
        "description": "Bộ đề bẫy từ loại (Word Form), liên từ (Conjunctions) và cấu trúc đảo ngữ thường gặp.",
        "category": "TOEIC Practice",
        "difficulty": "B2 - C1",
        "time_limit": 15,
        "badge": "TOEIC 750+",
        "created_at": "2026-01-12 10:00:00"
    },
    {
        "id": "grammar_core",
        "title": "Chuyên Đề: Ngữ Pháp Cốt Lõi Bứt Phá",
        "description": "Tổng hợp các chủ điểm: Câu điều kiện, Mệnh đề quan hệ rút gọn, Bị động kép và Đảo ngữ.",
        "category": "Grammar Mastery",
        "difficulty": "B1 - B2",
        "time_limit": 18,
        "badge": "Grammar",
        "created_at": "2026-01-15 10:00:00"
    },
    {
        "id": "vocab_phrasal",
        "title": "Chuyên Đề: Cụm Động Từ & Collocations Thông Dụng",
        "description": "Các phrasal verbs và cụm từ cố định trong giao tiếp và công sở mà người học hay nhầm.",
        "category": "Vocabulary & Idioms",
        "difficulty": "B1 - B2",
        "time_limit": 12,
        "badge": "Vocab",
        "created_at": "2026-01-20 10:00:00"
    }
]

QUESTIONS_DATA = [
    # SET 1: TOEIC Part 5 - Test 1 (20 câu)
    {
        "set_id": "toeic_part5_01",
        "question": "The marketing department needs to analyze the customer survey results ______ before finalizing the annual campaign.",
        "options": ["thorough", "thoroughly", "thoroughness", "more thorough"],
        "correct_answer": 1,
        "translation": "Phòng tiếp thị cần phân tích các kết quả khảo sát khách hàng một cách kỹ lưỡng trước khi hoàn thiện chiến dịch hàng năm.",
        "explanation": "Vị trí cần điền là một TRẠNG TỪ (Adverb) để bổ nghĩa cho động từ 'analyze' (phân tích như thế nào? -> phân tích một cách kỹ lưỡng). Đuôi '-ly' (thoroughly) là trạng từ. 'Thorough' là tính từ, 'thoroughness' là danh từ.",
        "category": "Word Form (Từ loại)",
        "difficulty": "B1",
        "vocab_notes": "analyze (v): phân tích; thoroughly (adv): kỹ lưỡng, cặn kẽ; finalize (v): hoàn tất, chốt lại."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Ms. Johnson requested that all department managers ______ their expense reports by Friday afternoon.",
        "options": ["submit", "submits", "submitted", "submitting"],
        "correct_answer": 0,
        "translation": "Bà Johnson đã yêu cầu tất cả các trưởng bộ phận phải nộp báo cáo chi tiêu trước chiều thứ Sáu.",
        "explanation": "Cấu trúc câu giả định (Subjunctive mood) với động từ yêu cầu: S + request / demand / recommend + that + S + (should) + V-nguyên thể không chia. Do đó động từ phải ở dạng nguyên mẫu 'submit'.",
        "category": "Subjunctive (Thức giả định)",
        "difficulty": "B2",
        "vocab_notes": "request (v): yêu cầu; expense report (n): báo cáo chi tiêu công tác; submit (v): nộp, đệ trình."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "______ the severe snowstorm, the delivery of medical supplies arrived right on schedule.",
        "options": ["Although", "Despite", "Because of", "Even though"],
        "correct_answer": 1,
        "translation": "Bất chấp cơn bão tuyết dữ dội, chuyến giao vật tư y tế vẫn đến đúng theo lịch trình.",
        "explanation": "Phía sau chỗ trống là một cụm danh từ 'the severe snowstorm' và có nghĩa tương phản. 'Despite' (+ Noun phrase) mang nghĩa 'mặc dù/bất chấp'. 'Although' và 'Even though' phải đi kèm một mệnh đề (S + V). 'Because of' chỉ nguyên nhân (do bởi), không hợp nghĩa tương phản.",
        "category": "Prepositions & Conjunctions",
        "difficulty": "B1",
        "vocab_notes": "severe (adj): khốc liệt, dữ dội; medical supplies (n): vật tư y tế; on schedule: đúng lịch trình."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Neither the CEO nor the board members ______ satisfied with the quarterly profit projections.",
        "options": ["was", "were", "is", "has been"],
        "correct_answer": 1,
        "translation": "Cả Giám đốc điều hành lẫn các thành viên hội đồng quản trị đều không hài lòng với các dự phóng lợi nhuận quý.",
        "explanation": "Cấu trúc hòa hợp chủ vị: 'Neither S1 nor S2 + V' -> động từ chia theo chủ ngữ gần nhất (S2). Ở đây S2 là 'the board members' (số nhiều), nên động từ to be phải chia ở số nhiều quá khứ là 'were'.",
        "category": "Subject-Verb Agreement",
        "difficulty": "B2",
        "vocab_notes": "board members: các thành viên HĐQT; projection (n): dự phóng, ước tính; satisfied with: hài lòng với."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The new security policy applies to everyone in the building, ______ senior executives and guest visitors.",
        "options": ["included", "including", "includes", "inclusive"],
        "correct_answer": 1,
        "translation": "Chính sách an ninh mới áp dụng cho tất cả mọi người trong tòa nhà, bao gồm cả các lãnh đạo cấp cao và khách tham quan.",
        "explanation": "'Including' đóng vai trò như một giới từ mang nghĩa 'bao gồm cả ai/cái gì'. Cấu trúc: '..., including + N'.",
        "category": "Prepositions / Participles",
        "difficulty": "B1",
        "vocab_notes": "security policy: chính sách an ninh; senior executive: giám đốc/lãnh đạo cấp cao; apply to: áp dụng cho."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Employees who wish to enroll in the leadership training workshop must sign up ______ the end of business hours today.",
        "options": ["prior", "until", "by", "during"],
        "correct_answer": 2,
        "translation": "Những nhân viên muốn đăng ký tham gia hội thảo đào tạo lãnh đạo phải ghi danh trước cuối giờ làm việc hôm nay.",
        "explanation": "'By' dùng để chỉ một thời hạn chót (deadline) - hành động phải hoàn tất trước hoặc muộn nhất vào thời điểm đó ('by the end of...'). 'Until' diễn tả hành động kéo dài liên tục tới thời điểm đó.",
        "category": "Prepositions of Time",
        "difficulty": "B1",
        "vocab_notes": "enroll in (v): đăng ký tham gia; sign up (v): ghi danh; business hours: giờ hành chính."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The research team has made ______ progress in developing an eco-friendly packaging material.",
        "options": ["consider", "considerably", "considerate", "considerable"],
        "correct_answer": 3,
        "translation": "Nhóm nghiên cứu đã đạt được tiến triển đáng kể trong việc phát triển vật liệu đóng gói thân thiện với môi trường.",
        "explanation": "Vị trí trước danh từ 'progress' cần một TÍNH TỪ để bổ nghĩa. 'Considerable' (adj) nghĩa là 'đáng kể, to lớn'. 'Considerate' (adj) nghĩa là 'chu đáo, biết quan tâm' (không hợp nghĩa). 'Considerably' là trạng từ.",
        "category": "Word Form & Vocabulary",
        "difficulty": "B2",
        "vocab_notes": "considerable (adj): đáng kể, lớn; eco-friendly (adj): thân thiện môi trường; packaging (n): bao bì đóng gói."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "If our overseas supplier ______ the shipment earlier, we wouldn't be facing this warehouse shortage now.",
        "options": ["dispatched", "had dispatched", "would dispatch", "has dispatched"],
        "correct_answer": 1,
        "translation": "Nếu nhà cung cấp nước ngoài gửi hàng sớm hơn, thì bây giờ chúng ta đã không phải đối mặt với tình trạng thiếu hàng trong kho.",
        "explanation": "Đây là câu điều kiện hỗn hợp (Mixed Conditional): Mệnh đề If nói về điều trái ngược quá khứ ('had dispatched' - quá khứ hoàn thành), mệnh đề chính nói về kết quả ở hiện tại ('wouldn't be facing ... now').",
        "category": "Conditionals (Câu điều kiện)",
        "difficulty": "B2",
        "vocab_notes": "overseas supplier: nhà cung cấp nước ngoài; dispatch (v): gửi hàng, điều động; shortage (n): sự thiếu hụt."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Passengers are reminded to keep their personal belongings with them ______ all times while inside the airport terminal.",
        "options": ["in", "at", "on", "for"],
        "correct_answer": 1,
        "translation": "Hành khách được nhắc nhở luôn giữ đồ dùng cá nhân bên mình mọi lúc khi ở trong nhà ga sân bay.",
        "explanation": "Cụm thành ngữ cố định (Idiomatic phrase): 'at all times' = always (mọi lúc, luôn luôn).",
        "category": "Collocations / Prepositions",
        "difficulty": "A2",
        "vocab_notes": "belongings (n): đồ đạc cá nhân; terminal (n): nhà ga; at all times: mọi lúc."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The renovated conference center can easily ______ up to five hundred guests for gala dinners and seminars.",
        "options": ["accommodate", "accumulate", "accomplish", "accelerate"],
        "correct_answer": 0,
        "translation": "Trung tâm hội nghị vừa được nâng cấp có thể dễ dàng chứa tới 500 khách cho các buổi tiệc tối và hội thảo.",
        "explanation": "Dựa vào ngữ cảnh sức chứa của địa điểm: 'accommodate' (v) mang nghĩa cung cấp chỗ ở / đủ không gian sức chứa cho ai. Các từ khác: 'accumulate' (tích lũy), 'accomplish' (hoàn thành), 'accelerate' (tăng tốc).",
        "category": "Vocabulary Context",
        "difficulty": "B2",
        "vocab_notes": "accommodate (v): chứa được, cung cấp chỗ; renovated (adj): được tân trang, sửa chữa; seminar (n): hội thảo."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Having reviewed several competing software platforms, the committee finally opted for the one ______ best met their security specifications.",
        "options": ["that", "whom", "whose", "what"],
        "correct_answer": 0,
        "translation": "Sau khi xem xét một vài nền tảng phần mềm cạnh tranh, ủy ban cuối cùng đã lựa chọn nền tảng đáp ứng tốt nhất các thông số an ninh của họ.",
        "explanation": "Đại từ quan hệ 'that' thay thế cho đại từ chỉ vật/nền tảng 'the one' và làm chủ ngữ cho mệnh đề quan hệ phía sau ('best met...'). 'Whom' chỉ người (tân ngữ), 'whose' chỉ sở hữu, 'what' không dùng làm đại từ quan hệ sau danh từ tiền ngữ.",
        "category": "Relative Pronouns",
        "difficulty": "B1",
        "vocab_notes": "opt for (v): lựa chọn; specification (n): thông số kỹ thuật, quy chuẩn; committee (n): hội đồng, ủy ban."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Please note that tickets purchased during the promotional flash sale are strictly ______.",
        "options": ["refundable", "non-refundable", "refunding", "refund"],
        "correct_answer": 1,
        "translation": "Xin lưu ý rằng vé được mua trong đợt giảm giá chớp nhoáng khuyến mãi tuyệt đối không được hoàn tiền.",
        "explanation": "Cần tính từ miêu tả điều khoản vé khuyến mại: 'non-refundable' (không thể hoàn lại tiền). 'Strictly non-refundable' là cụm từ rất phổ biến trong quy định bán vé và chính sách dịch vụ.",
        "category": "Vocabulary & Word Form",
        "difficulty": "B1",
        "vocab_notes": "promotional (adj): mang tính khuyến mại; strictly (adv): một cách nghiêm ngặt/tuyệt đối; non-refundable (adj): không hoàn tiền."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The newly appointed branch manager has demonstrated an exceptional ability to ______ difficult negotiations.",
        "options": ["handle", "handling", "handled", "be handled"],
        "correct_answer": 0,
        "translation": "Trưởng chi nhánh mới được bổ nhiệm đã thể hiện khả năng xuất sắc trong việc xử lý các cuộc đàm phán khó khăn.",
        "explanation": "Cấu trúc danh từ chỉ năng lực: 'ability + to-infinitive' (khả năng làm điều gì). Do đó ta chọn 'handle' (to handle).",
        "category": "To-Infinitive Structures",
        "difficulty": "B1",
        "vocab_notes": "appointed (adj): được bổ nhiệm; exceptional (adj): xuất sắc, phi thường; negotiation (n): cuộc đàm phán."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Under no circumstances ______ confidential client information be disclosed without written authorization.",
        "options": ["should", "would", "is", "must to"],
        "correct_answer": 0,
        "translation": "Dưới bất kỳ hoàn cảnh nào, thông tin mật của khách hàng cũng không được phép tiết lộ khi chưa có sự ủy quyền bằng văn bản.",
        "explanation": "Cấu trúc ĐẢO NGỮ (Inversion) với cụm từ phủ định đứng đầu câu: 'Under no circumstances + trợ động từ / modal verb + S + V'. Ở đây cần 'should confidential client information be disclosed'.",
        "category": "Inversion (Đảo ngữ)",
        "difficulty": "C1",
        "vocab_notes": "under no circumstances: tuyệt đối không trong bất kỳ trường hợp nào; confidential (adj): bảo mật; disclose (v): tiết lộ; authorization (n): sự cấp phép."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The keynote speaker was delayed by heavy traffic; ______, the presentation began thirty minutes later than anticipated.",
        "options": ["nevertheless", "consequently", "otherwise", "meanwhile"],
        "correct_answer": 1,
        "translation": "Diễn giả chính bị hoãn do tắc đường nghiêm trọng; kết quả là, bài thuyết trình đã bắt đầu muộn hơn 30 phút so với dự kiến.",
        "explanation": "Mối quan hệ nguyên nhân - kết quả giữa hai mệnh đề: Tắc đường -> Kết quả là bị trễ. 'Consequently' (kết quả là, do đó) là trạng từ liên kết chỉ kết quả. 'Nevertheless' (tuy nhiên), 'otherwise' (nếu không thì), 'meanwhile' (trong khi đó).",
        "category": "Conjunctive Adverbs",
        "difficulty": "B2",
        "vocab_notes": "keynote speaker: diễn giả chính; consequently (adv): do đó, kết quả là; anticipate (v): dự tính, lường trước."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "To ensure accurate delivery, please verify that your shipping address is entered ______ on the checkout page.",
        "options": ["correct", "correctly", "correctness", "correction"],
        "correct_answer": 1,
        "translation": "Để đảm bảo giao hàng chính xác, vui lòng xác minh rằng địa chỉ giao hàng của bạn đã được nhập một cách chính xác trên trang thanh toán.",
        "explanation": "Động từ 'entered' (được nhập) cần một TRẠNG TỪ 'correctly' đứng sau để bổ nghĩa (nhập như thế nào? -> nhập chính xác).",
        "category": "Word Form (Adverb)",
        "difficulty": "A2",
        "vocab_notes": "ensure (v): đảm bảo; verify (v): xác minh; shipping address: địa chỉ giao hàng."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The factory's latest automated assembly line is significantly faster and more ______ than the old mechanical system.",
        "options": ["efficient", "efficiency", "efficiently", "efficacious"],
        "correct_answer": 0,
        "translation": "Dây chuyền lắp ráp tự động mới nhất của nhà máy nhanh hơn đáng kể và hiệu quả hơn so với hệ thống cơ khí cũ.",
        "explanation": "Cấu trúc so sánh hơn song hành: 'faster and more + [TÍNH TỪ]'. Cần tính từ 'efficient' (năng suất, hiệu quả). 'Efficiency' là danh từ, 'efficiently' là trạng từ.",
        "category": "Parallel Structure & Comparisons",
        "difficulty": "B1",
        "vocab_notes": "automated (adj): tự động hóa; assembly line: dây chuyền lắp ráp; efficient (adj): hiệu quả, tiết kiệm năng lượng/thời gian."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Mr. Davis was honored at the annual banquet in recognition of his thirty years of dedicated ______ to the corporation.",
        "options": ["serve", "service", "servant", "serving"],
        "correct_answer": 1,
        "translation": "Ông Davis đã được vinh danh tại bữa tiệc thường niên để ghi nhận ba mươi năm cống hiến tận tụy của ông cho tập đoàn.",
        "explanation": "Sau tính từ 'dedicated' cần một DANH TỪ chỉ sự phục vụ/cống hiến: 'service'. Cụm từ hay gặp: 'dedicated service' (sự cống hiến tận tâm). 'Servant' là người hầu, không phù hợp nghĩa.",
        "category": "Collocations & Noun Choice",
        "difficulty": "B1",
        "vocab_notes": "in recognition of: để ghi nhận; banquet (n): yến tiệc; dedicated (adj): tận tụy, cống hiến; service (n): sự phục vụ, công tác."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "Neither of the two candidates who interviewed for the project manager role ______ sufficient experience in agile methodologies.",
        "options": ["have", "has", "are having", "were having"],
        "correct_answer": 1,
        "translation": "Không ai trong số hai ứng viên đã phỏng vấn cho vị trí quản lý dự án có đủ kinh nghiệm về các phương pháp luận Agile.",
        "explanation": "Chủ ngữ là đại từ bất định 'Neither of + Noun số nhiều' -> theo chuẩn ngữ pháp tiếng Anh, động từ chia ở ngôi thứ 3 SỐ ÍT ('has').",
        "category": "Subject-Verb Agreement",
        "difficulty": "B2",
        "vocab_notes": "candidate (n): ứng viên; sufficient (adj): đầy đủ; agile methodology: phương pháp linh hoạt (Agile)."
    },
    {
        "set_id": "toeic_part5_01",
        "question": "The warranty certificate remains valid ______ the product is operated strictly in accordance with the manufacturer's manual.",
        "options": ["provided that", "in case of", "as though", "unless"],
        "correct_answer": 0,
        "translation": "Chứng nhận bảo hành vẫn còn hiệu lực với điều kiện là sản phẩm được vận hành tuân thủ nghiêm ngặt theo hướng dẫn của nhà sản xuất.",
        "explanation": "'Provided that' = 'as long as' / 'if' (với điều kiện là, miễn là) đi với một mệnh đề chỉ điều kiện tích cực. 'Unless' mang nghĩa 'trừ phi' (phủ định, trái nghĩa). 'In case of' đi với cụm danh từ.",
        "category": "Conditionals & Conjunctions",
        "difficulty": "B2",
        "vocab_notes": "warranty certificate: giấy bảo hành; valid (adj): có hiệu lực; in accordance with: tuân theo."
    },

    # SET 2: TOEIC Part 5 - Test 2 (20 câu)
    {
        "set_id": "toeic_part5_02",
        "question": "Dr. Miller suggested that the clinical trial results ______ evaluated by an independent peer-review board.",
        "options": ["are", "be", "were", "to be"],
        "correct_answer": 1,
        "translation": "Tiến sĩ Miller đề xuất rằng các kết quả thử nghiệm lâm sàng cần được đánh giá bởi một hội đồng bình duyệt độc lập.",
        "explanation": "Cấu trúc thức giả định: 'suggest that + S + (should) be + V3/ed'. Thể bị động ở dạng nguyên thể là 'be evaluated'.",
        "category": "Subjunctive / Passive",
        "difficulty": "B2",
        "vocab_notes": "clinical trial: thử nghiệm lâm sàng; independent (adj): độc lập; peer-review: bình duyệt đồng cấp."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The financial forecast indicates that revenue will rise ______ during the upcoming fiscal quarter due to overseas expansion.",
        "options": ["substantial", "substantially", "substance", "substantiate"],
        "correct_answer": 1,
        "translation": "Dự báo tài chính chỉ ra rằng doanh thu sẽ tăng đáng kể trong quý tài chính sắp tới nhờ việc mở rộng ra nước ngoài.",
        "explanation": "Chỗ trống đứng sau nội động từ 'will rise' nên cần một TRẠNG TỪ 'substantially' (đáng kể) để bổ nghĩa cho động từ tăng.",
        "category": "Word Form (Adverbs)",
        "difficulty": "B1",
        "vocab_notes": "revenue (n): doanh thu; fiscal quarter: quý tài chính; substantially (adv): đáng kể; expansion (n): sự mở rộng."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "______ had the plane touched down on the runway when the storm triggered an airport-wide alert.",
        "options": ["Hardly", "No sooner", "As soon as", "Not only"],
        "correct_answer": 0,
        "translation": "Máy bay vừa mới chạm bánh xuống đường băng thì cơn bão đã kích hoạt báo động trên toàn sân bay.",
        "explanation": "Cặp cấu trúc đảo ngữ thời gian: 'Hardly / Scarcely + had + S + V3/ed + WHEN + S + V2/ed' (Vừa mới... thì...). Nếu dùng 'No sooner' thì phải đi với 'THAN'. Do đó chọn 'Hardly'.",
        "category": "Inversion Pairs",
        "difficulty": "C1",
        "vocab_notes": "touch down (v): hạ cánh; runway (n): đường băng; trigger (v): kích hoạt, gây ra."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The architect presented three blueprints, each ______ its own unique ecological advantages.",
        "options": ["has", "having", "have", "had"],
        "correct_answer": 1,
        "translation": "Kiến trúc sư đã trình bày ba bản thiết kế chi tiết, mỗi bản đều sở hữu những lợi thế sinh thái độc đáo riêng.",
        "explanation": "Đây là cấu trúc mệnh đề tuyệt đối (Absolute phrase) hoặc mệnh đề phân từ rút gọn độc lập: 'each having its own...'. Vì mệnh đề chính đã có động từ 'presented', phần sau dấu phẩy là cụm phân từ bổ nghĩa.",
        "category": "Participial Phrases",
        "difficulty": "C1",
        "vocab_notes": "blueprint (n): bản thiết kế kỹ thuật; ecological (adj): thuộc sinh thái; unique (adj): độc nhất."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Customers who sign a two-year service contract are eligible ______ a complimentary high-speed router.",
        "options": ["with", "for", "to", "by"],
        "correct_answer": 1,
        "translation": "Khách hàng ký hợp đồng dịch vụ hai năm có đủ điều kiện để nhận một thiết bị định tuyến tốc độ cao miễn phí.",
        "explanation": "Cấu trúc tính từ đi với giới từ: 'eligible for + Noun' (đủ tư cách/điều kiện nhận cái gì). Nếu đi với động từ sẽ là 'eligible to do something'. Ở đây phía sau là cụm danh từ 'a complimentary router' nên dùng 'for'.",
        "category": "Adjective + Preposition",
        "difficulty": "B1",
        "vocab_notes": "eligible for: đủ điều kiện nhận; complimentary (adj): miễn phí (quà tặng kèm); router: cục phát wifi/định tuyến."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Unless the contract is signed by the client by noon, the project launch will have to be ______.",
        "options": ["postponed", "postponing", "postpones", "postpone"],
        "correct_answer": 0,
        "translation": "Trừ khi hợp đồng được khách hàng ký trước buổi trưa, nếu không việc khởi động dự án sẽ phải bị hoãn lại.",
        "explanation": "Cấu trúc bị động với modal verb: 'will have to be + V3/ed' -> 'postponed' (bị hoãn lại).",
        "category": "Passive Voice",
        "difficulty": "A2",
        "vocab_notes": "postpone (v): hoãn lại; launch (n/v): ra mắt, khởi động; unless = if not."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The supervisor praised the interns for completing the quarterly audit ______ schedule.",
        "options": ["ahead of", "front of", "prior", "forward"],
        "correct_answer": 0,
        "translation": "Người giám sát đã khen ngợi các thực tập sinh vì đã hoàn thành cuộc kiểm toán quý trước thời hạn.",
        "explanation": "Cụm thành ngữ về tiến độ: 'ahead of schedule' = trước thời hạn dự kiến. Trái nghĩa là 'behind schedule' (trễ hạn).",
        "category": "Idiomatic Collocations",
        "difficulty": "B1",
        "vocab_notes": "praise (v): khen ngợi; intern (n): thực tập sinh; quarterly audit: kiểm toán hàng quý; ahead of schedule: trước tiến độ."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "It is imperative that every team member ______ the updated data security protocols immediately.",
        "options": ["acknowledges", "acknowledge", "acknowledged", "acknowledging"],
        "correct_answer": 1,
        "translation": "Điều cấp bách là mọi thành viên trong nhóm phải xác nhận các quy chuẩn bảo mật dữ liệu đã cập nhật ngay lập tức.",
        "explanation": "Cấu trúc tính từ giả định: 'It is imperative / vital / crucial + that + S + (should) V-nguyên thể' -> chọn 'acknowledge'.",
        "category": "Subjunctive Adjectives",
        "difficulty": "B2",
        "vocab_notes": "imperative (adj): khẩn cấp, bắt buộc; acknowledge (v): xác nhận, ghi nhận; protocol (n): giao thức, quy tắc."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The technician noticed that the cooling system was operating ______ than it had during yesterday's stress test.",
        "options": ["more noisy", "much noisier", "more noisily", "noisily"],
        "correct_answer": 2,
        "translation": "Kỹ thuật viên nhận thấy rằng hệ thống làm mát đang hoạt động một cách ồn ào hơn so với buổi kiểm tra tải hôm qua.",
        "explanation": "Bổ nghĩa cho động từ 'operating' cần trạng từ 'noisily'. So sánh hơn của trạng từ có đuôi -ly là 'more noisily'.",
        "category": "Comparatives with Adverbs",
        "difficulty": "B2",
        "vocab_notes": "operate (v): hoạt động, vận hành; cooling system: hệ thống làm mát; stress test: bài kiểm tra áp lực/quá tải."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Because of recent budget constraints, the university had no choice but to ______ several elective arts courses.",
        "options": ["cancel", "canceling", "cancelled", "cancellation"],
        "correct_answer": 0,
        "translation": "Do những hạn chế về ngân sách gần đây, trường đại học không còn lựa chọn nào khác ngoài việc hủy một số khóa học nghệ thuật tự chọn.",
        "explanation": "Cấu trúc cố định: 'have no choice but + to-infinitive' (không còn cách nào khác ngoài việc...). Do đó ta chọn 'cancel'.",
        "category": "Fixed Structures",
        "difficulty": "B2",
        "vocab_notes": "budget constraint (n): thắt chặt ngân sách; elective (adj): tự chọn; no choice but to do: không có lựa chọn nào ngoài."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "A comprehensive list of hotel amenities ______ provided in the welcome packet upon check-in.",
        "options": ["is", "are", "have been", "were"],
        "correct_answer": 0,
        "translation": "Một danh sách toàn diện các tiện ích khách sạn được cung cấp trong gói quà chào mừng khi làm thủ tục nhận phòng.",
        "explanation": "Chủ ngữ chính của câu là 'A comprehensive list' (danh từ số ít), cụm 'of hotel amenities' chỉ là giới từ bổ nghĩa. Do đó động từ to be phải chia số ít ở hiện tại là 'is'.",
        "category": "Subject-Verb Agreement",
        "difficulty": "B1",
        "vocab_notes": "amenities (n): tiện nghi khách sạn; comprehensive (adj): toàn diện, chi tiết; welcome packet: tập tài liệu chào mừng."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Staff members are strictly prohibited from using company-issued laptops for personal endeavors ______ authorized by management.",
        "options": ["without", "unless", "except", "in spite of"],
        "correct_answer": 1,
        "translation": "Các nhân viên bị nghiêm cấm sử dụng máy tính xách tay do công ty cấp cho mục đích cá nhân trừ khi được ban quản lý cho phép.",
        "explanation": "'Unless authorized' là dạng rút gọn của mệnh đề trạng ngữ chỉ điều kiện: 'unless they are authorized' (trừ khi được...). 'Without' cần danh từ hoặc V-ing ('without authorization').",
        "category": "Reduced Adverb Clauses",
        "difficulty": "B2",
        "vocab_notes": "prohibit from (v): cấm làm gì; endeavors (n): việc làm, mục tiêu; company-issued: do công ty cấp."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The keynote speaker expressed profound ______ for the warm welcome she received from the audience.",
        "options": ["appreciate", "appreciated", "appreciation", "appreciative"],
        "correct_answer": 2,
        "translation": "Diễn giả chính đã bày tỏ lòng biết ơn sâu sắc đối với sự chào đón nồng nhiệt mà bà nhận được từ khán giả.",
        "explanation": "Sau tính từ 'profound' (sâu sắc) cần một DANH TỪ làm tân ngữ cho động từ 'expressed'. 'Appreciation' (n) nghĩa là sự cảm kích, trân trọng, biết ơn.",
        "category": "Word Form (Nouns)",
        "difficulty": "B1",
        "vocab_notes": "profound (adj): sâu sắc; appreciation (n): sự cảm kích, trân trọng; audience (n): khán giả."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The newly installed solar panels have proven remarkably efficient, ______ our electricity bills by nearly forty percent.",
        "options": ["reduce", "reduced", "reducing", "reduces"],
        "correct_answer": 2,
        "translation": "Các tấm pin năng lượng mặt trời mới lắp đặt đã chứng minh hiệu quả vượt trội, làm giảm gần 40% hóa đơn tiền điện của chúng tôi.",
        "explanation": "Mệnh đề phân từ chỉ kết quả (Present participle expressing result): ', reducing...'. Hành động giảm tiền điện là hệ quả trực tiếp từ việc pin mặt trời hoạt động hiệu quả.",
        "category": "Participle Clauses",
        "difficulty": "B2",
        "vocab_notes": "solar panels: tấm pin mặt trời; remarkably (adv): một cách đáng kể, rõ rệt; electricity bill: hóa đơn điện."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Mr. Henderson was regarded as one of the most ______ accountants at the firm because of his meticulous attention to detail.",
        "options": ["rely", "reliant", "reliable", "reliably"],
        "correct_answer": 2,
        "translation": "Ông Henderson được coi là một trong những kế toán viên đáng tin cậy nhất tại công ty nhờ sự cẩn trọng tỉ mỉ đến từng chi tiết.",
        "explanation": "Vị trí sau 'the most' và trước danh từ 'accountants' cần một TÍNH TỪ miêu tả phẩm chất người: 'reliable' (đáng tin cậy). 'Reliant' nghĩa là phụ thuộc vào ai/cái gì (reliant on).",
        "category": "Adjective Confusion",
        "difficulty": "B2",
        "vocab_notes": "meticulous (adj): tỉ mỉ, kỹ càng; reliable (adj): đáng tin cậy; regard as (v): coi như là."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Should you require further assistance regarding your hotel reservation, please do not ______ to contact our 24/7 concierge desk.",
        "options": ["hesitate", "hesitation", "hesitant", "hesitated"],
        "correct_answer": 0,
        "translation": "Nếu quý khách cần thêm bất kỳ sự trợ giúp nào liên quan đến việc đặt phòng khách sạn, xin đừng ngần ngại liên hệ bàn trợ giúp 24/7 của chúng tôi.",
        "explanation": "Sau trợ động từ phủ định 'do not' là động từ nguyên mẫu: 'hesitate' (ngần ngại). Cụm quen thuộc trong thư từ lịch sự: 'do not hesitate to contact us'.",
        "category": "Imperatives & Collocations",
        "difficulty": "A2",
        "vocab_notes": "reservation (n): sự đặt chỗ; hesitate (v): do dự, ngần ngại; concierge desk: quầy lễ tân/hướng dẫn."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The human resources manager interviewed five prospective candidates, none of ______ met all the technical prerequisites.",
        "options": ["who", "whom", "them", "which"],
        "correct_answer": 1,
        "translation": "Trưởng phòng nhân sự đã phỏng vấn năm ứng viên tiềm năng, không ai trong số họ đáp ứng được tất cả các điều kiện tiên quyết về kỹ thuật.",
        "explanation": "Cấu trúc đại từ quan hệ sau giới từ chỉ người: 'quantifier + of + WHOM' (none of whom, neither of whom, both of whom). Nếu chỉ vật dùng 'which'. Không dùng 'them' khi nối hai mệnh đề mà không có liên từ 'and'.",
        "category": "Relative Clauses after Prepositions",
        "difficulty": "B2",
        "vocab_notes": "prospective (adj): tiềm năng, triển vọng; prerequisite (n): điều kiện tiên quyết; meet requirements: đáp ứng yêu cầu."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "The company decided to ______ the product launch until several software vulnerabilities had been fully patched.",
        "options": ["hold off", "hold up", "hold out", "hold down"],
        "correct_answer": 0,
        "translation": "Công ty đã quyết định trì hoãn việc ra mắt sản phẩm cho đến khi một số lỗ hổng phần mềm được vá hoàn toàn.",
        "explanation": "'Hold off' (phrasal verb) mang nghĩa là trì hoãn, hoãn lại một việc gì đó chưa thực hiện ngay. 'Hold up' là làm kẹt/chặn lại, 'hold out' là cầm cự.",
        "category": "Phrasal Verbs in Context",
        "difficulty": "B2",
        "vocab_notes": "vulnerability (n): lỗ hổng bảo mật; patch (v): vá lỗi; hold off (phr v): trì hoãn."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "All confidential documents must be shredded immediately ______ their retention period expires.",
        "options": ["once", "meanwhile", "during", "despite"],
        "correct_answer": 0,
        "translation": "Tất cả tài liệu mật phải được tiêu hủy bằng máy cắt ngay một khi thời hạn lưu trữ của chúng hết hạn.",
        "explanation": "'Once' đóng vai trò liên từ chỉ thời gian mang nghĩa 'ngay khi, một khi' (= as soon as), nối hai mệnh đề hoàn chỉnh.",
        "category": "Time Conjunctions",
        "difficulty": "B1",
        "vocab_notes": "shred (v): cắt nhỏ, tiêu hủy tài liệu; retention period: thời gian lưu trữ tài liệu; expire (v): hết hạn."
    },
    {
        "set_id": "toeic_part5_02",
        "question": "Were the board of directors ______ the proposed acquisition, our market share would double within three years.",
        "options": ["to approve", "approving", "approve", "approved"],
        "correct_answer": 0,
        "translation": "Nếu hội đồng quản trị chấp thuận thương vụ mua lại được đề xuất, thị phần của chúng ta sẽ tăng gấp đôi trong vòng ba năm.",
        "explanation": "Đảo ngữ câu điều kiện loại 2: 'Were + S + TO-INFINITIVE, S + would + V'. Do đó chọn 'to approve'.",
        "category": "Inversion in Conditionals",
        "difficulty": "C1",
        "vocab_notes": "acquisition (n): thương vụ mua lại/sáp nhập; market share: thị phần; double (v): tăng gấp đôi."
    },

    # SET 3: Core Grammar Mastery (20 câu)
    {
        "set_id": "grammar_core",
        "question": "If you ______ me about the meeting yesterday, I would not have missed the keynote presentation.",
        "options": ["told", "had told", "would tell", "have told"],
        "correct_answer": 1,
        "translation": "Nếu bạn nói cho tôi biết về cuộc họp ngày hôm qua, thì tôi đã không bỏ lỡ bài thuyết trình chính.",
        "explanation": "Câu điều kiện loại 3 diễn tả một giả định trái ngược với quá khứ. Cấu trúc: 'If + S + had + V3/ed, S + would have + V3/ed'. Vế sau đã có 'would not have missed' nên vế If phải là 'had told'.",
        "category": "Conditionals Type 3",
        "difficulty": "B1",
        "vocab_notes": "miss (v): bỏ lỡ; keynote presentation: bài thuyết trình quan trọng nhất."
    },
    {
        "set_id": "grammar_core",
        "question": "I would rather you ______ anyone about our travel plans until everything is officially confirmed.",
        "options": ["don't tell", "didn't tell", "not to tell", "won't tell"],
        "correct_answer": 1,
        "translation": "Tôi muốn bạn không kể với bất kỳ ai về kế hoạch du lịch của chúng ta cho đến khi mọi thứ được xác nhận chính thức.",
        "explanation": "Cấu trúc 'would rather (that) + S + V-quá khứ đơn' dùng để diễn đạt mong muốn ai đó làm hoặc không làm gì ở hiện tại/tương lai mang tính lịch sự. Thể phủ định là 'didn't tell'.",
        "category": "Subjunctive / Would rather",
        "difficulty": "B2",
        "vocab_notes": "officially (adv): chính thức; confirmed (adj): được xác nhận; would rather someone did: muốn ai đó làm gì."
    },
    {
        "set_id": "grammar_core",
        "question": "The man ______ next to the CEO at the press conference is our chief technology officer.",
        "options": ["who sitting", "sitting", "is sitting", "sits"],
        "correct_answer": 1,
        "translation": "Người đàn ông đang ngồi cạnh Tổng giám đốc điều hành tại buổi họp báo là giám đốc công nghệ của chúng tôi.",
        "explanation": "Rút gọn mệnh đề quan hệ chủ động: 'The man who is sitting...' rút gọn thành 'The man sitting...'. 'Sitting' là hiện tại phân từ mang nghĩa chủ động.",
        "category": "Reduced Relative Clauses",
        "difficulty": "B1",
        "vocab_notes": "press conference: buổi họp báo; chief technology officer (CTO): giám đốc công nghệ."
    },
    {
        "set_id": "grammar_core",
        "question": "Rarely ______ such an incredible performance in an amateur theatrical production.",
        "options": ["we have seen", "have we seen", "we saw", "did we saw"],
        "correct_answer": 1,
        "translation": "Hiếm khi nào chúng tôi lại được chứng kiến một màn biểu diễn xuất sắc đến thế trong một vở kịch nghiệp dư.",
        "explanation": "Đảo ngữ với trạng từ tần suất phủ định/bán phủ định 'Rarely' đứng đầu câu: 'Rarely + trợ động từ (have) + S (we) + V3 (seen)'.",
        "category": "Negative Inversion",
        "difficulty": "B2",
        "vocab_notes": "rarely (adv): hiếm khi; incredible (adj): tuyệt vời, khó tin; amateur theatrical production: vở diễn kịch nghiệp dư."
    },
    {
        "set_id": "grammar_core",
        "question": "By the time the rescue team reached the remote cabin, the blizzard ______ for over twenty-four hours.",
        "options": ["raged", "had been raging", "was raging", "has raged"],
        "correct_answer": 1,
        "translation": "Vào thời điểm đội cứu hộ tiếp cận được căn nhà gỗ hẻo lánh, cơn bão tuyết đã hoành hành liên tục hơn 24 giờ đồng hồ.",
        "explanation": "'By the time + S + V-quá khứ đơn' (reached), mệnh đề còn lại diễn tả một hành động đã và đang xảy ra kéo dài liên tục trước thời điểm đó nên chia Quá khứ hoàn thành tiếp diễn: 'had been raging'.",
        "category": "Past Perfect Continuous",
        "difficulty": "B2",
        "vocab_notes": "remote cabin: căn nhà gỗ hẻo lánh; blizzard (n): bão tuyết; rage (v): hoành hành, gầm rú dữ dội."
    },
    {
        "set_id": "grammar_core",
        "question": "The committee recommended that the draft proposal ______ thoroughly before the vote.",
        "options": ["revised", "be revised", "is revised", "was revised"],
        "correct_answer": 1,
        "translation": "Ủy ban khuyến nghị rằng bản đề xuất phác thảo cần phải được chỉnh sửa kỹ lưỡng trước cuộc bỏ phiếu.",
        "explanation": "Thức giả định bị động: 'recommend that + S + (should) be + V3/ed'. 'The draft proposal' là vật nên cần bị động: 'be revised'.",
        "category": "Subjunctive Mood",
        "difficulty": "B2",
        "vocab_notes": "draft proposal: đề xuất dự thảo; thoroughly: thấu đáo, kỹ càng; revise (v): chỉnh sửa, ôn lại."
    },
    {
        "set_id": "grammar_core",
        "question": "Not only ______ the championship, but they also set a new national scoring record.",
        "options": ["they won", "did they win", "they did win", "won they"],
        "correct_answer": 1,
        "translation": "Không những họ giành chức vô địch, mà họ còn thiết lập một kỷ lục ghi điểm quốc gia mới.",
        "explanation": "Cấu trúc đảo ngữ: 'Not only + trợ động từ + S + V, but S also...'. Vì câu kể về sự kiện quá khứ nên dùng trợ động từ 'did': 'did they win'.",
        "category": "Inversion with Not Only",
        "difficulty": "B1",
        "vocab_notes": "championship (n): chức vô địch; record (n): kỷ lục; set a record: lập kỷ lục."
    },
    {
        "set_id": "grammar_core",
        "question": "I remember ______ the front door before going to bed, but this morning I found it unlocked.",
        "options": ["locking", "to lock", "lock", "locked"],
        "correct_answer": 0,
        "translation": "Tôi nhớ là mình đã khóa cửa trước khi đi ngủ, nhưng sáng nay tôi lại thấy nó mở.",
        "explanation": "'Remember + V-ing': nhớ đã làm một việc gì đó trong quá khứ. 'Remember + to-V': nhớ phải làm việc gì (bổn phận chưa làm). Ở đây người nói nhớ là mình ĐÃ khóa cửa rồi -> dùng 'locking'.",
        "category": "Gerund vs Infinitive",
        "difficulty": "B1",
        "vocab_notes": "remember + V-ing: nhớ đã làm gì; unlocked (adj): không khóa."
    },
    {
        "set_id": "grammar_core",
        "question": "The bridge ______ right now is scheduled to open to traffic in early November.",
        "options": ["building", "is built", "being built", "was built"],
        "correct_answer": 2,
        "translation": "Cây cầu đang được xây dựng hiện nay dự kiến sẽ mở cửa cho xe cộ lưu thông vào đầu tháng 11.",
        "explanation": "Rút gọn mệnh đề quan hệ ở thể BỊ ĐỘNG ĐANG DIỄN RA: 'The bridge which is being built right now...' rút gọn thành 'The bridge being built right now...'.",
        "category": "Reduced Participles (Passive)",
        "difficulty": "B2",
        "vocab_notes": "scheduled to: dự kiến; open to traffic: thông xe; bridge: cây cầu."
    },
    {
        "set_id": "grammar_core",
        "question": "Had I known about the flight cancellation earlier, I ______ my hotel reservation accordingly.",
        "options": ["would adjust", "would have adjusted", "will adjust", "adjusted"],
        "correct_answer": 1,
        "translation": "Nếu tôi biết về việc hủy chuyến bay sớm hơn, tôi đã điều chỉnh việc đặt phòng khách sạn cho phù hợp rồi.",
        "explanation": "Đảo ngữ câu điều kiện loại 3: 'Had + S + V3/ed, S + would have + V3/ed'. Mệnh đề kết quả phải là 'would have adjusted'.",
        "category": "Inversion in Conditionals",
        "difficulty": "B2",
        "vocab_notes": "cancellation (n): sự hủy bỏ; adjust (v): điều chỉnh; accordingly (adv): theo đó, cho phù hợp."
    },
    {
        "set_id": "grammar_core",
        "question": "It is about time you ______ preparing for your final IELTS examination.",
        "options": ["start", "started", "have started", "will start"],
        "correct_answer": 1,
        "translation": "Đã đến lúc bạn nên bắt đầu chuẩn bị cho kỳ thi IELTS cuối kỳ của mình rồi đó.",
        "explanation": "Cấu trúc giả định: 'It is (high/about) time + S + V-quá khứ đơn' diễn tả một việc lẽ ra nên làm từ trước rồi. Do đó dùng động từ chia quá khứ đơn 'started'.",
        "category": "Special Structures",
        "difficulty": "B1",
        "vocab_notes": "it is about time: đã đến lúc cần làm gì; prepare for: chuẩn bị cho."
    },
    {
        "set_id": "grammar_core",
        "question": "The architect whose design ______ the international competition has received numerous lucrative offers.",
        "options": ["won", "was won", "winning", "has won by"],
        "correct_answer": 0,
        "translation": "Kiến trúc sư có bản thiết kế đã chiến thắng cuộc thi quốc tế đã nhận được nhiều lời mời hợp tác béo bở.",
        "explanation": "'Whose design won the international competition': 'design' là chủ ngữ gây ra hành động thắng ('won') cuộc thi. 'Win' mang nghĩa chủ động nên chia 'won'.",
        "category": "Relative Clauses (Whose)",
        "difficulty": "B1",
        "vocab_notes": "lucrative (adj): sinh lợi, béo bở; numerous (adj): đông đảo, nhiều; whose: của người mà."
    },
    {
        "set_id": "grammar_core",
        "question": "You shouldn't have stayed up so late last night; you ______ exhausted today.",
        "options": ["must be", "should be", "can't be", "might have been"],
        "correct_answer": 0,
        "translation": "Đáng lẽ tối qua bạn không nên thức khuya như vậy; chắc hẳn hôm nay bạn đang kiệt sức lắm.",
        "explanation": "'Must be' dùng để đưa ra một suy đoán chắc chắn ở hiện tại dựa trên bằng chứng rõ ràng (vì thức quá khuya nên hôm nay chắc chắn mệt mỏi). 'Exhausted' là kiệt sức.",
        "category": "Modal Verbs of Deduction",
        "difficulty": "B1",
        "vocab_notes": "stay up late: thức khuya; exhausted (adj): kiệt sức; must be: chắc hẳn là."
    },
    {
        "set_id": "grammar_core",
        "question": "No sooner ______ into the classroom than the professor handed out the pop quiz.",
        "options": ["had the students stepped", "the students had stepped", "did the students stepped", "stepped the students"],
        "correct_answer": 0,
        "translation": "Các sinh viên vừa mới bước vào lớp học thì giáo sư đã phát bài kiểm tra đột xuất.",
        "explanation": "Cấu trúc đảo ngữ: 'No sooner + had + S + V3/ed + than + S + V2/ed' (Vừa mới... thì...). Do đó chọn 'had the students stepped'.",
        "category": "Negative Inversion",
        "difficulty": "B2",
        "vocab_notes": "pop quiz: bài kiểm tra nhanh không báo trước; hand out: phát cho; step into: bước vào."
    },
    {
        "set_id": "grammar_core",
        "question": "Despite ______ for over five hours in the pouring rain, the marathon runners showed immense determination.",
        "options": ["having run", "they ran", "they have run", "run"],
        "correct_answer": 0,
        "translation": "Mặc dù đã chạy hơn 5 tiếng đồng hồ dưới cơn mưa như trút nước, các vận động viên marathon vẫn thể hiện lòng quyết tâm to lớn.",
        "explanation": "Sau giới từ 'Despite' cần một V-ing hoặc Having + V3 (Perfect Gerund) để nhấn mạnh hành động chạy đã diễn ra trước đó. Do đó chọn 'having run'.",
        "category": "Gerunds after Prepositions",
        "difficulty": "B2",
        "vocab_notes": "pouring rain: mưa như trút; immense (adj): bao la, to lớn; determination (n): lòng kiên định."
    },

    # SET 4: Vocabulary & Collocations (15 câu)
    {
        "set_id": "vocab_phrasal",
        "question": "Because our flight was delayed by fog, we had to ______ the business lunch until tomorrow afternoon.",
        "options": ["put off", "call off", "give up", "take over"],
        "correct_answer": 0,
        "translation": "Vì chuyến bay của chúng tôi bị hoãn do sương mù, chúng tôi đã phải dời bữa trưa bàn công việc lại đến chiều mai.",
        "explanation": "'Put off' = postpone (trì hoãn, dời lại lịch sau). 'Call off' = cancel (hủy bỏ hoàn toàn). Vì chuyển sang chiều mai nên là dời lịch ('put off').",
        "category": "Phrasal Verbs",
        "difficulty": "B1",
        "vocab_notes": "put off: hoãn lại; call off: hủy bỏ; business lunch: bữa trưa gặp đối tác kinh doanh."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "The company’s CEO decided to step down and ______ control of daily operations to his deputy.",
        "options": ["hand over", "look into", "break down", "get by"],
        "correct_answer": 0,
        "translation": "Tổng giám đốc công ty đã quyết định từ chức và bàn giao quyền kiểm soát các hoạt động hàng ngày cho cấp phó của mình.",
        "explanation": "'Hand over' (phrasal verb) nghĩa là bàn giao quyền lực, nhiệm vụ hoặc tài sản cho ai. 'Look into' là điều tra, 'break down' là hỏng hóc, 'get by' là xoay xở sống qua ngày.",
        "category": "Phrasal Verbs in Business",
        "difficulty": "B2",
        "vocab_notes": "step down (v): từ chức; deputy (n): cấp phó; hand over: bàn giao."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "Young professionals are strongly encouraged to keep ______ with industry developments and digital tools.",
        "options": ["abreast", "apart", "alongside", "afresh"],
        "correct_answer": 0,
        "translation": "Các chuyên viên trẻ được khuyến khích mạnh mẽ nên luôn cập nhật nắm bắt kịp thời các bước phát triển của ngành và công cụ số.",
        "explanation": "Thành ngữ cố định: 'keep abreast of / with something' = luôn cập nhật thông tin mới nhất về cái gì.",
        "category": "Advanced Collocations",
        "difficulty": "C1",
        "vocab_notes": "keep abreast of: bắt kịp, cập nhật; industry development: sự phát triển ngành; encourage: khuyến khích."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "After months of rigorous negotiations, the two tech firms finally reached a ______ agreement.",
        "options": ["mutual", "common", "reciprocal", "shared"],
        "correct_answer": 0,
        "translation": "Sau nhiều tháng đàm phán gắt gao, hai công ty công nghệ cuối cùng đã đạt được một thỏa thuận chung đôi bên cùng có lợi.",
        "explanation": "Cụm danh từ cố định trong kinh doanh: 'a mutual agreement' (thỏa thuận song phương / từ hai phía cùng đồng thuận).",
        "category": "Business Collocations",
        "difficulty": "B1",
        "vocab_notes": "mutual (adj): chung, qua lại lẫn nhau; rigorous (adj): nghiêm ngặt, khắt khe; reach an agreement: đạt thỏa thuận."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "The sudden cancellation of the music festival came as a total shock and threw everyone's weekend plans into ______.",
        "options": ["chaos", "messy", "disordered", "confusionly"],
        "correct_answer": 0,
        "translation": "Việc hủy bỏ đột ngột lễ hội âm nhạc là một cú sốc hoàn toàn và khiến các kế hoạch cuối tuần của mọi người rơi vào cảnh hỗn loạn.",
        "explanation": "Thành ngữ tiếng Anh: 'throw something into chaos' (khiến cho cái gì rơi vào tình trạng hỗn loạn, đảo lộn). 'Chaos' là danh từ không đếm được.",
        "category": "Idiomatic Expressions",
        "difficulty": "B2",
        "vocab_notes": "throw into chaos: làm đảo lộn hoàn toàn; sudden (adj): bất ngờ; cancellation: sự hủy."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "The startup was able to ______ a niche in the competitive electric scooter market.",
        "options": ["carve out", "take in", "make off", "put across"],
        "correct_answer": 0,
        "translation": "Công ty khởi nghiệp đã thành công tạo dựng cho mình một vị thế thích hợp trong thị trường xe trượt điện đầy tính cạnh tranh.",
        "explanation": "Thành ngữ thương mại: 'carve out a niche' = xây dựng hoặc tìm được một phân khúc/chỗ đứng thị trường ngách vững chắc cho mình.",
        "category": "Business Idioms",
        "difficulty": "C1",
        "vocab_notes": "carve out a niche: tạo dựng chỗ đứng thị trường; startup (n): công ty khởi nghiệp; competitive: cạnh tranh."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "The committee decided to ______ the controversial proposal until the next annual general meeting.",
        "options": ["table", "shelf", "situate", "post"],
        "correct_answer": 0,
        "translation": "Ủy ban quyết định gác lại đề xuất gây tranh cãi cho tới cuộc họp đại hội đồng thường niên tiếp theo.",
        "explanation": "Trong tiếng Anh công sở: 'to table a proposal/motion' (theo nghĩa US) nghĩa là hoãn lại, gác lại để xem xét sau.",
        "category": "Workplace Vocabulary",
        "difficulty": "C1",
        "vocab_notes": "table a proposal: hoãn lại đề xuất; controversial (adj): gây tranh cãi; annual meeting: họp thường niên."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "Whenever you encounter a new vocabulary word in reading, try to figure out its meaning from the ______.",
        "options": ["context", "content", "contact", "contrast"],
        "correct_answer": 0,
        "translation": "Bất cứ khi nào bạn bắt gặp một từ vựng mới trong bài đọc, hãy cố gắng suy luận ý nghĩa của nó từ ngữ cảnh.",
        "explanation": "'Context' nghĩa là ngữ cảnh xung quanh. Cụm từ quen thuộc: 'guess / figure out from the context' (đoán nghĩa từ ngữ cảnh). 'Content' là nội dung, 'contact' là liên lạc.",
        "category": "Learning Collocations",
        "difficulty": "A2",
        "vocab_notes": "context (n): ngữ cảnh, bối cảnh; figure out: tìm ra, đoán ra; encounter: bắt gặp."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "His reckless decision to invest all company reserves in speculative crypto assets bordered on ______.",
        "options": ["insanity", "insane", "insanely", "insanities"],
        "correct_answer": 0,
        "translation": "Quyết định liều lĩnh của anh ta khi đầu tư toàn bộ quỹ dự phòng của công ty vào các tài sản tiền ảo đầu cơ gần như chạm ngưỡng điên rồ.",
        "explanation": "Cụm cấu trúc: 'border on + Noun' (gần như chạm tới ngưỡng, suýt trở thành cái gì). Sau giới từ 'on' cần danh từ 'insanity' (sự điên rồ).",
        "category": "Collocations with Prepositions",
        "difficulty": "C1",
        "vocab_notes": "reckless (adj): liều lĩnh, thiếu cẩn trọng; speculative (adj): mang tính đầu cơ; border on: tiệm cận với."
    },
    {
        "set_id": "vocab_phrasal",
        "question": "She has an extraordinary knack ______ remembering names and faces, even of people she met only once.",
        "options": ["for", "at", "with", "in"],
        "correct_answer": 0,
        "translation": "Cô ấy có một tài lẻ phi thường trong việc ghi nhớ tên và khuôn mặt, ngay cả với những người cô ấy chỉ gặp một lần.",
        "explanation": "Cấu trúc danh từ cố định: 'have a knack for (doing) something' = có khiếu, có tài năng thiên bẩm làm việc gì một cách dễ dàng.",
        "category": "Prepositional Collocations",
        "difficulty": "B2",
        "vocab_notes": "knack for: năng khiếu, sở trường; extraordinary (adj): phi thường; remember: ghi nhớ."
    }
]

def seed_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Seed test sets
    for s in TEST_SETS:
        cursor.execute("""
        INSERT OR IGNORE INTO test_sets (id, title, description, category, difficulty, time_limit, badge, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (s["id"], s["title"], s["description"], s["category"], s["difficulty"], s["time_limit"], s["badge"], s["created_at"]))

    # Seed questions
    for q in QUESTIONS_DATA:
        # Check if identical question already exists in this set
        cursor.execute("SELECT id FROM questions WHERE set_id = ? AND question = ?", (q["set_id"], q["question"]))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO questions (set_id, question, options, correct_answer, translation, explanation, category, difficulty, vocab_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["set_id"],
                q["question"],
                json.dumps(q["options"], ensure_ascii=False),
                q["correct_answer"],
                q["translation"],
                q["explanation"],
                q["category"],
                q["difficulty"],
                q["vocab_notes"]
            ))

    conn.commit()
    conn.close()
    print("Database seeded successfully with realistic English questions.")

if __name__ == "__main__":
    from app.database import init_db
    init_db()
    seed_database()
