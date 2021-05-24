# PBL5-Speech-Recogination-Viet-Nam

- Micro ghi lại dữ liệu âm thanh và gửi về cho raspberry để xử lý.
- Raspberry đọc tín hiệu âm thanh từ micro, xử lý phát hiện tiếng nói và gửi về cho Server (Python) xử lý.
- Server (Python) nhận tín hiệu âm thanh từ raspberry, sử dụng module nhận diện mệnh lệnh từ giọng nói và so khớp với các mệnh lệnh cho sẵn trong cơ sở dữ liệu. (Bộ trích đặc trưng) 
- Sau khi quá trình so khớp dữ liệu từ cơ sở dữ liệu thì gửi thông tin cho xe

## How to Train : 

- open anaconda cmd : 

  - conda activate tf-gpu

  - cd ToYourDirectory

  - python Train.py 

## How to run file : 

 - open anaconda cmd : 

   - conda activate tf-gpu

   - cd ToYourDirectory

   - python Final_GUI.py 

## Run File in Visual Studio :
- run Detect Voice then Press Predict in GUI APP to know what you have say 
