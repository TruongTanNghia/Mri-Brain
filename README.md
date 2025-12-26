CÀI MÔI TRƯỞNG ẢO: 
        py -3.8 -m venv venv38
KÍCH HOẠT MÔI TRƯỜNG ẢO:
        ten_env\Scripts\activate
CÀI ĐẶT TOÀN BỘ THƯ VIỆN
        pip install -r requirements.txt
RUN CODE
uvicorn app:app --reload     
