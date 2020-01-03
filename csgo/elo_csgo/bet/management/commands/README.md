craw data của 2 trang hltv và vpgame về hết trước đã
sau đó mới xử lý tiếp dữ liệu như là:
+ mapping giữa 2 cái data của hltv và vpgame bằng:
- thời gian: thời gian sẽ nằm trong khoảng +- detail (detail đang để là 2 giờ)
- tên team a và b
- điểm của 2 team

(trước khi mapping 2 cái data của 2 trang này, thì cần đồng bộ lại tên đội ở 2 trang vì 2 trang đang lưu tên 1 số 
đội không giông nhau )

(1 số bản ghi bỏ đi là do: không có tỷ số trong trang bet-vpgame, hoặc tên đội đã lâu và không có dữ liệu để mapping)

thứ tự chạy command sẽ là: số thứ tự command
crawler_1
crawler_2
crawler_3
....

-----------------------------------------------------

(không còn tác dụng nữa a ạ, note ra đây thôi)
tại sao lại chỉ được khoảng 3378 match hợp lệ vì:
+ bên hltv crawl được 8346 match
+ nhưng bên vpgame chỉ crawl được 3781 bet 
=> nếu mapping với nhau thì đc khoảng 3378 match hợp lệ do:
+ có khoảng 200 bản ghi không update tỷ số (tức là  0 - 0) 
+ 1 số đội có bên vpgmae nhưng không có bên hltv
+ hoặc 2 bên đang lưu tên 2 đội không đồng bộ với nhau mà map tay chưa care hết được

-----------------------------------------------------

+ cái map name của 2 trang, thì phải thường xuyên cập nhật,

------------------------- end -----------------------