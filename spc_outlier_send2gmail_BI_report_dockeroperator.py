from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
import pendulum # For timezone awareness
from docker.types import Mount # Import Mount for explicit volume mounting
import os
# Define Beijing timezone
beijing_tz = pendulum.timezone("Asia/Shanghai")

# 获取宿主机上项目根目录的绝对路径
# 假设 AIRFLOW_PROJ_DIR 环境变量在 Airflow Worker 容器中可用，
# 并且指向你的项目根目录（即 docker-compose.yaml 所在的目录）。
# 如果 AIRFLOW_PROJ_DIR 未设置，则默认为当前工作目录（这在Airflow容器内可能不是你期望的宿主机路径）
# 强烈建议在 .env 文件中明确设置 AIRFLOW_PROJ_DIR 为宿主机的绝对路径，例如：
# AIRFLOW_PROJ_DIR=/home/user/my_airflow_project
#AIRFLOW_PROJECT_ROOT = os.environ.get('AIRFLOW_PROJ_DIR', os.getcwd())
#AIRFLOW_PROJECT_ROOT = '/home/carenk/00_enviroment/03_container_airflow'

# 构建 '00_projects' 目录在宿主机上的绝对路径
#HOST_PROJECTS_PATH = os.path.join(AIRFLOW_PROJECT_ROOT, '00_projects')
HOST_PROJECTS_PATH = '/home/carenk/01_projects'

with DAG(
    dag_id='etl_spc_c11_outlier_report_BI_2gmail',
    # Ensure start_date is timezone-aware
    start_date=datetime(2025, 7, 16, 0, 0, tzinfo=beijing_tz),
    schedule_interval='0 7 * * *', # every day 7 am
    catchup=False, # Important: Set to False for new DAGs to avoid backfilling old runs
    tags=['etl', 'spc', 'c11'],
) as dag:
    run_etl_script = DockerOperator(
        task_id='execute_etl_spc_c11_outlier_report_BI_2gmail',
        # Specify the image to use. This should be 'python_env_common_playwright:latest'
        # if you built the new image that includes Playwright.
        # If you are still using the original 'python_env_common:202507' and it now has Playwright,
        # keep that tag.
        image='env_playwrite_simple:202507', # Assuming you built the new image with Playwright
        # Command to run inside the newly spawned container
        command='bash -c "cd /app/projects/01_project_spc/02_auto_sent_report/ && python get_BI_pic_python.py"',
        # Define volume mounts for the task container.
        # We use docker.types.Mount for more explicit control.
        mounts=[
            # Mount the project directory from the host into the container.
            # This is where your 'spc_etl_main.py' script resides.
            # Ensure './00_projects' is the correct host path relative to your DAGs folder.
            Mount(source=HOST_PROJECTS_PATH, target='/app/projects', type='bind'),

            # IMPORTANT: Mount the Docker daemon socket ONLY if 'spc_etl_main.py'
            # or any code it calls internally needs to run 'docker' commands.
            # If your script does NOT interact with the Docker daemon, you can remove this mount.
            # Ensure the Airflow Worker's user has permissions to access this socket on the host
            # (via group_add in your docker-compose.yaml).
            #!!!!!
            #Mount(source='/var/run/docker.sock', target='/var/run/docker.sock', type='bind')
        ],
        # Network to connect to (must be the same as your Airflow services in docker-compose.yaml)
        network_mode='03_container_airflow_airflow_network',
        # Automatically remove the container after the task finishes.
        # This keeps your Docker environment clean.
        auto_remove=True,
        # If you need to specify a user/group inside the Docker container for the task.
        # This should typically match the UID/GID that has permissions on your mounted volumes
        # and on the Docker socket. If you set AIRFLOW_UID in your .env, use that.
        # Example: user='50000:0' or user='${AIRFLOW_UID}:0' if you pass it.
        # For simplicity, if your base image handles the user well, you might not need this.
        # However, if you encounter permission issues within the task container, try setting it.
        # user='${AIRFLOW_UID}:0', # Example, requires AIRFLOW_UID to be set in Airflow env or .env
    )