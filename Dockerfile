# 以通用 Python ETL 镜像作为基础
# 这个镜像已经包含了 Python 3.13、所有通用库和 ODBC 驱动
#FROM python_env_common_playwright:2507
#
FROM env_playwrite_simple:202507

# 设置容器内的工作目录
# 假设 project_A 的代码将放在 /app/test_spc 目录下
WORKDIR /app/test/

# 复制 project_A 的所有代码文件到容器中
# 假设 Dockerfile 位于 project_A 目录下，且所有代码都在 . 目录下
COPY . .

# 定义容器启动时要执行的命令
# 这会启动 Python 解释器并运行 main_etl_a.py 脚本
# 确保 main_etl_a.py 位于 WORKDIR (/app/project_A) 下
CMD ["python", "get_BI_pic_python.py"]
