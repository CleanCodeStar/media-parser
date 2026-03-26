#!/bin/bash

# ==============================================================================
#  Media Parser - Docker 自动化部署脚本 (Linux)
# ==============================================================================

# 设置颜色变量以便输出更美观
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}>>> 开始执行 Media Parser 部署程序...${NC}"

# 1. 检查必要环境
echo -e "${GREEN}1. 检查 Docker 环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 docker，请先安装 Docker。${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 docker compose，请先安装 Docker Compose。${NC}"
    exit 1
fi

# 2. 检查配置文件
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}[错误] 当前目录下未发现 docker-compose.yml，请在项目根目录运行此脚本。${NC}"
    exit 1
fi

# 3. 停止并移除旧容器
echo -e "${GREEN}2. 停止并清理旧的服务容器...${NC}"
docker compose down --remove-orphans

# 4. 构建并启动服务
echo -e "${GREEN}3. 正在构建并后台启动容器...${NC}"
# 使用 --build 强制重新构建镜像，确保代码更新已包含在内
docker compose up -d --build

# 5. 清理虚悬镜像（节省磁盘空间）
echo -e "${GREEN}4. 清理构建过程中产生的虚悬镜像...${NC}"
if [ "$(docker images -f "dangling=true" -q)" ]; then
    docker rmi $(docker images -f "dangling=true" -q)
    echo -e "${YELLOW}已清理虚悬镜像。${NC}"
else
    echo -e "没有发现需要清理的虚悬镜像。"
fi

# 6. 检查容器运行状态
echo -e "\n${GREEN}====================================================================${NC}"
echo -e "${GREEN}部署完成！当前容器运行状态：${NC}"
docker ps --filter "name=media-parser"
echo -e "${GREEN}====================================================================${NC}"

echo -e "\n${YELLOW}提示: ${NC}"
echo -e "  - 查看实时日志: ${GREEN}docker logs -f media-parser-backend${NC}"
echo -e "  - 查看应用端口: ${GREEN}http://localhost:8051${NC}"
echo -e "  - 停止应用: ${GREEN}docker compose stop${NC}"
