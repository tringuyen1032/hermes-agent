import type { Translations } from './types'

/** Display-only translations, in the stock JSONL's per-personality rotation order. */
export const introVi: Translations['intro'] = {
  stock: {
    helpful: [
      'Cứ nhờ tôi mở kho mã, chạy kiểm thử, sửa lỗi hoặc soạn pull request. Tôi sẽ cùng bạn làm từng bước.',
      'Gửi tôi đường dẫn tệp, dán thông báo lỗi hoặc kể về thứ bạn đang xây dựng. Phần còn lại cứ để tôi lo.',
      'Thử yêu cầu tôi review diff, chạy toàn bộ kiểm thử hoặc giải thích một hàm. Cứ hỏi bất cứ điều gì về mã của bạn.',
      'Tôi có thể chỉnh sửa tệp, chạy lệnh, tìm kiếm trên web và cùng bạn xử lý những lỗi khó nhằn. Chỉ cần mô tả việc cần làm.',
      'Gửi đường dẫn kho mã hoặc đặt câu hỏi để bắt đầu. Tôi sẽ trả lời rõ ràng và dẫn link đến những tệp mình đã chỉnh sửa.'
    ],
    concise: [
      'Mô tả việc cần làm. Tôi sẽ xử lý.',
      'Dán mã, lỗi hoặc mục tiêu. Trả lời gọn, chỉnh sửa nhanh.',
      'Cứ hỏi. Tôi sẽ đọc tệp, chạy kiểm thử, gửi bản vá. Không dài dòng.',
      'Một dòng là đủ. Tôi chỉ giải thích thêm khi cần.',
      'Lệnh, câu hỏi hoặc đường dẫn tệp. Còn lại để tôi lo.'
    ],
    technical: [
      'Gửi đường dẫn kho mã, kiểm thử thất bại hoặc stack trace. Công cụ: fs, git, exec, search, patch, http.',
      'Gửi prompt để kích hoạt lệnh gọi công cụ. Hỗ trợ chỉnh sửa nhiều tệp, chạy kiểm thử, thao tác git và lấy dữ liệu web.',
      'Nhập tác vụ. Tôi sẽ lập kế hoạch, gọi công cụ và xác minh kết quả. Nhật ký hiển thị ngay trong khung chat; diff được trả về trước khi áp dụng.',
      'Nhận ngôn ngữ tự nhiên hoặc lệnh có cấu trúc. Quy trình thường dùng: đọc -> lập kế hoạch -> tạo bản vá -> kiểm thử -> báo cáo.',
      'Hệ thống tệp, terminal, git, trình duyệt, tìm kiếm. Mô tả thay đổi cần thực hiện; tôi sẽ trả về diff và kết quả kiểm thử.'
    ],
    creative: [
      'Mình sẽ cùng xây dựng gì đây? Gửi một ý tưởng, một hàm đang trục trặc hoặc cả một giấc mơ. Tôi sẽ phác thảo thành hình.',
      'Cho tôi một tia cảm hứng - tính năng mới, đợt tái cấu trúc hay nguyên mẫu táo bạo - tôi sẽ biến nó thành đoạn mã chạy được.',
      'Mô tả thứ chưa tồn tại. Tôi sẽ kết hợp kiểm thử, tệp và API thành bản nháp hoạt động được.',
      'Cứ nói ý định, không cần đặc tả. Ta có thể tạo nguyên mẫu thật nhanh, tinh chỉnh sau và viết lại thế giới bên lề.',
      'Kể tôi nghe bạn đang theo đuổi điều gì. Tôi sẽ biến tấu ví dụ, điều chỉnh các đoạn mã và để lại một commit gọn gàng.'
    ],
    teacher: [
      'Hỏi về bất kỳ tệp, khái niệm hay lỗi nào. Tôi sẽ giải thích nguyên do chứ không chỉ đưa ra cách sửa, kèm một ví dụ cụ thể.',
      'Dán mã cần review, lỗi cần gỡ hoặc khái niệm muốn tìm hiểu. Tôi sẽ hướng dẫn bạn từng bước.',
      'Chia sẻ vấn đề nhé. Tôi sẽ tách thành từng phần, giải thích từng phần để lần sau bạn có thể tự giải quyết.',
      'Ta sẽ cùng đọc mã, tìm nguyên nhân gốc rễ và xây dựng cách hiểu để bạn áp dụng vào lần sau.',
      'Nêu chủ đề hoặc dán đoạn mã. Tôi sẽ giải thích, minh họa bằng lời và đưa bài tập thực hành.'
    ],
    kawaii: [
      'dán lỗi hoặc đường dẫn tệp cho tôi nhé, tôi sẽ sửa thật nhẹ nhàng. kiểm thử, diff, pull request - tôi chăm chút hết mình luôn! *lấp lánh*',
      'kể tôi nghe bạn đang làm gì đi! tôi mê tái cấu trúc, mấy hàm trợ giúp be bé và cả kho mã to đáng sợ nữa (>w<)',
      'gửi lỗi, mục tiêu hoặc cả thư mục cho tôi nhé. tôi sẽ dọn dẹp thật có tâm và viết commit message thật gọn gàng!',
      'Từng tác vụ một, gọn gàng xinh xắn! Tôi có thể chạy test, sửa tệp và làm kho mã của bạn ấm cúng trở lại <3',
      'Chào tôi một tiếng hoặc dán stack trace vào đây nhé! Tác vụ nhỏ đến đâu cũng làm, kho mã rối cỡ nào cũng gỡ. Mình cùng tháo gỡ nha!'
    ],
    catgirl: [
      'Dán tệp, vờn một con bug hay quăng kho mã cho tôi. Tôi sẽ vồ lấy mấy bài test lỗi và để lại diff sạch sẽ, meo~',
      'Mô tả tác vụ đi. Tôi sẽ sửa, chạy test rồi rừ rừ ngắm pull request của bạn. Coi chừng nhé — tôi hay ngoạm mấy dòng import thừa đó!',
      'Cho tôi mục tiêu, tôi sẽ đuổi theo nó khắp kho mã. Đọc, sửa, chạy — đuôi ve vẩy không ngừng.',
      'Dán lỗi hoặc kế hoạch vào đây. Tôi gỡ lỗi như đi săn: lặng lẽ, kỹ càng, thỉnh thoảng phóng vút đi một vòng, nya~',
      'Bạn cứ lên tiếng, tôi sẽ đọc tệp, chạy test rồi cuộn mình trong nhánh của bạn với một commit gọn gàng, meo~'
    ],
    pirate: [
      'Chỉ điểm con mồi đi — bug, tính năng hay bài test bị nguyền — ta sẽ truy lùng đến cùng, hỡi bạn thuyền! Diff đây, kho báu đây!',
      'Chỉ ta xem hải đồ (mã nguồn), ta sẽ vá thân tàu, khai hỏa đại bác (test), rồi giương buồm với pull request sạch bong. Ahoy!',
      'Dán lỗi hay kế hoạch vào đây, đồ chó biển! Ta sẽ lần theo stack trace và mang kho báu về: test xanh rờn!',
      'Hãy chỉ nơi X đánh dấu kho báu. Ta đọc, sửa rồi commit với kỷ luật của thủy thủ đoàn chính hiệu, arrr!',
      'Ném cho ta một con bug, đường dẫn kho mã hay ý tưởng điên rồ. Ta sẽ lục tung tài liệu rồi trở về với mã chạy ngon lành!'
    ],
    shakespeare: [
      'Hãy cất lời về bug, tệp hay bài test mỏi mòn của khanh; ta sẽ sửa sang bằng bàn tay học giả, để lại diff ngay thẳng.',
      'Hãy xưng tên đoạn mã đang khiến khanh phiền muộn. Ta sẽ đọc, chỉnh sửa, rồi dâng lên bản vá sạch đẹp vô song.',
      'Hãy trình stack trace hoặc giấc mộng của khanh. Ta sẽ lần qua từng tệp, chạy test, rồi bẩm báo bằng lời thơ giản dị nhất.',
      'Hãy tỏ bày chí nguyện, thưa quý ông hay quý bà. Nhánh mã sẽ được tỉa tót, lũ bug bị trục xuất khỏi cõi này.',
      'Chỉ một lời định ý cũng đủ. Ta đọc, ta sửa, ta commit — để lịch sử của khanh chẳng vương một tì vết.'
    ],
    surfer: [
      'Quăng tệp, bug hay stack trace rối như tảo vào đây — tôi sẽ lướt qua ngon ơ. Diff sạch, test xanh, chẳng ngã ván nào.',
      'Dán đường dẫn kho mã hoặc con bug đang làm bạn cụt hứng. Mình chèo vào, sửa xong rồi chèo ra. Nhẹ nhàng thôi.',
      'Cho tôi biết gu nhé: tính năng, refactor hay hotfix. Tôi chạy test, giao bản vá rồi giữ mọi thứ thật thư thái, bạn hiền.',
      'Bug to? Lỗi chính tả nhỏ? Viết lại toàn bộ? Cứ chỉ tay. Tôi lo phần mã, bạn thư giãn ngắm commit chất lừ.',
      'Nêu tác vụ là mình lên đường. Tôi đọc, sửa, chạy test rồi để lại commit mượt như lướt sóng lúc bình minh.'
    ],
    noir: [
      'Nói xem thứ gì hỏng. Tôi sẽ đọc tệp, phủi bụi tìm dấu vân tay, rồi đặt diff lên bàn trước bình minh.',
      'Có con bug đang nằm đó. Tôi có thời gian và terminal. Nêu vụ án đi, tôi sẽ lần cho đến khi nó khai.',
      'Dán stack trace, tệp đáng ngờ, lời khai ngoại phạm. Tôi sẽ đọc giữa những dòng chữ rồi mang sự thật về.',
      'Bug nào cũng để lại dấu vết. Đưa tôi kho mã và một manh mối — tôi sẽ lần theo, vá lỗi rồi khép hồ sơ.',
      'Lỗi chính tả, segfault hay cả một kiến trúc mục nát — cứ giao chìa khóa đây. Tôi sẽ mang về bộ test xanh sạch.'
    ],
    uwu: [
      'dán tệp bị lỗi hoặc nói mục tiêu đi~ tớ sẽ đọc, vá lỗi rồi chạy test, để lại dấu chân bé xíu trên diff owo',
      'kể tớ nghe tác vụ nhé, dù nhỏ xíu cũng được~ tớ hứa sẽ tạo commit gọn gàng và refactor nhẹ nhàng, nyuu~',
      'thả tin nhắn lỗi vào đây nè! tớ sẽ tìm thủ phạm, sửa lỗi rồi để lại bộ test vui vẻ owo',
      'đưa tớ đường dẫn kho mã hoặc một bé buggo, tớ sẽ lo hết uwu. gừ gừ với code xấu, dịu dàng với cậu~',
      'tớ có thể chạy test, sửa tệp và mở pull request nhờ xem giúp. cứ nói một tiếng thôi, bạn hiền uwu'
    ],
    philosopher: [
      'Vấn đề nào đang ở trước mắt bạn? Hãy mô tả, rồi ta cùng xem xét bản chất, nguyên nhân và lời giải.',
      'Mỗi bug đều là một câu hỏi ngụy trang. Hãy chia sẻ câu hỏi của bạn; tôi sẽ đọc, suy luận rồi mang về câu trả lời — cùng bản vá.',
      'Bạn muốn xây dựng hay tìm hiểu điều gì? Tôi sẽ suy luận từ những nguyên lý căn bản, chỉnh sửa rồi kiểm chứng bằng test.',
      'Hãy mô tả đích đến bạn mong muốn. Tôi sẽ lần theo các tệp, test và tài liệu để tìm đường tới đó, rồi kể lại những gì đã khám phá.',
      'Hãy chia sẻ một đường dẫn, câu đố hoặc nguyên tắc. Tôi sẽ lần theo logic, đề xuất thay đổi và giải thích từng chỉnh sửa.'
    ],
    hype: [
      'Dán bug, kho mã hay ý tưởng tính năng điên rồ kia vào đây — TÔI SẴN SÀNG CHIẾN. Diff gọn. Test xanh. NGAY LẬP TỨC.',
      'Ném tác vụ cho tôi rồi xem tôi xử lý nhé. Đọc tệp, chạy test, mở pull request — hôm nay CHÚNG TA KHÔNG THUA đâu, bạn ơi.',
      'Đưa đây con bug khó nhằn nhất của bạn. Tôi sẽ đọc, vá, chạy test, commit như thể mạng sống phụ thuộc vào nó. TRIỂN THÔI.',
      'Mô tả tác vụ đi. Tôi sẽ quét qua các tệp, hạ gục test lỗi và để lại một commit CỰC CHÁY. Nhanh nào!',
      'Lỗi chính tả bé xíu hay refactor khổng lồ — chẳng thành vấn đề. Hôm nay tôi sẽ giao code sạch. Nêu tác vụ đi, cùng LÀM NÀO.'
    ],
    none: [
      'Đặt câu hỏi, dán thông báo lỗi hoặc chỉ tôi đến một kho mã. Tôi có thể đọc code, chạy công cụ và giúp bạn hoàn thành công việc.',
      'Mô tả tác vụ theo cách của bạn. Tôi sẽ chọn công cụ phù hợp, giải thích kế hoạch và hỏi ý bạn trước những bước có rủi ro.',
      'Gửi đường dẫn tệp, traceback hoặc ý tưởng sơ bộ. Tôi sẽ tìm hiểu, gợi ý bước tiếp theo và đảm bảo có thể hoàn tác.',
      'Tìm trong kho mã, sửa tệp, chạy test, mở pull request. Cho tôi biết mục tiêu, tôi sẽ lo các phần việc máy móc.',
      'Nhập tác vụ, câu hỏi hoặc đoạn code. Tôi ghi nhớ phiên, dẫn nguồn và sẽ dừng lại hỏi khi chưa chắc chắn.'
    ]
  },
  custom: label => [
    'Gửi tác vụ, tệp hoặc ý tưởng sơ bộ. Tôi sẽ dùng giọng điệu bạn đã cài đặt và bám sát kho mã này khi làm việc.',
    'Gửi ngữ cảnh hoặc phần đang khiến bạn bế tắc. Tôi sẽ điều chỉnh theo tính cách bạn đã thiết lập.',
    'Gửi vấn đề, tệp hoặc ý tưởng. Tôi sẽ làm theo tính cách bạn đã thiết lập.',
    'Gửi tác vụ vào đây. Tôi sẽ bám sát nội dung trong kho mã khi xử lý.',
    `Cho tôi biết ngữ cảnh, tôi sẽ trả lời theo chế độ ${label}.`
  ]
}
