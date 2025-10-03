# CaseStudy Project

## 🚀 Setup môi trường

Dự án này sử dụng **Conda** (Python 3.12) và **Poetry** để quản lý thư viện.

### 1. Clone repository
```bash
git clone <repo-url>
cd <repo-folder>

### 2. Tạo Conda Environment
'''bash
conda create -n casestudy python=3.12 -y
conda activate casestudy

### 3. Cài poetry nếu chưa có
#### Cài poetry toàn cục:
'''bash
pip install poetry

####Kiểm tra:
poetry --version

### 4.Liên kết poetry với conda environment
#### Lấy đường dẫn python trong conda:
'''bash
which python # Linux/MacOS
where python # Windowns
#### Ví dụ 
'''swift 
/home/username/anaconda3/envs/casestudy/bin/python
#### Chạy lệnh
poetry env use /home/username/anaconda3/envs/casestudy/bin/python

### 5. Cài dependencies từ pyproject.toml
poetry init
poetry install

#### Lưu ý: khi muốn cài đặt thự viện vào trong project, ta sử dụng poetry add <package_name>
Không được sử dụng pip install hay conda install để tránh lệnh môi trường 


