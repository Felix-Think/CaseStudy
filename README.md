# CaseStudy Project

Dự án này sử dụng **Conda (Python 3.12)** và **Poetry** để quản lý thư viện.

---

### 1. Clone repository

```bash
git clone https://github.com/Felix-Think/CaseStudy
cd CaseStudy
```

---

### 2. Cài Poetry nếu chưa có

#### Cài poetry toàn cục:

```bash
pip install poetry
```

#### Kiểm tra:

```bash
poetry --version
```

---

### 3. Liên kết Poetry với Conda environment

#### Lấy đường dẫn python trong Conda:

```bash
which python     # Linux / macOS
where python     # Windows
```

#### Ví dụ:

```
/home/username/anaconda3/envs/casestudy/bin/python
```

#### Chạy lệnh liên kết:

```bash
poetry env use /home/username/anaconda3/envs/casestudy/bin/python
```

---

### 4. Cài dependencies từ `pyproject.toml`

Nếu chưa có `pyproject.toml`, khởi tạo:

```bash
poetry init
```

Sau đó cài thư viện:

```bash
poetry install
```

---

### 💡 Lưu ý khi cài thư viện

Khi muốn thêm thư viện vào project, hãy dùng:

```bash
poetry add <package_name>
```

❌ **Không sử dụng** `pip install` hay `conda install` vì sẽ làm lệch môi trường.

---

### 5. Chạy công cụ sinh personas (LLM)

CLI `main_persona.py` đọc case JSON cố định tại `data/drown.json` và gọi LLM để xây dựng danh sách persona chi tiết theo schema chuẩn.

```bash
python main_persona.py
```

- File đầu vào được cố định tại `data/drown.json`.
- Kết quả mặc định lưu tại `<case_id>_personas.json` trong thư mục hiện tại.

Kết quả được in ra console và lưu dưới dạng JSON chứa `case_id` cùng danh sách personas với các trường đã chuẩn hóa.
