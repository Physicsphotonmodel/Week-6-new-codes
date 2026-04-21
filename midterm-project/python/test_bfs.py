import logging
import asyncio
from maze import Maze
from node import Direction

# 設定 Log 讓你可以看到 Pacman 規劃的細節
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
log = logging.getLogger(__name__)

async def test_navigation():
    # 1. 載入地圖
    maze_file = "data/appoint_maze.csv" 
    maze = Maze(maze_file)

    # 2. 設定起點 (Node 1) 並將其設為座標原點 (0,0)
    my_start_index = 3
    start_node = maze.node_dict[my_start_index]
    maze.generate_coordinates(start_node)
    log.info(f"Initalizing the coordinate system, start node: {my_start_index}")

    # 3. 測試 BFS：尋找最近的死胡同
    # path_to_deadend = maze.BFS(start_node)
    # log.info(f"BFS 找到最近死胡同路徑: {[n.index for n in path_to_deadend]}")

    # 4. 測試 Pacman 策略 (核心邏輯)
    # 這會內部呼叫 get_all_node_scores()，以 (0,0) 為基準計分
    initial_dir = Direction.NORTH 
    # path_nodes = maze.strategy_pacman_2(start_node, initial_dir, time_limit=65.0)
    path_nodes, final_score, total_time = maze.strategy_pacman_2(
        start_node, 
        initial_dir, 
        time_limit=70.0
    )

    if not path_nodes or len(path_nodes) < 2:
        log.error("路徑規劃失敗")
        return

    # log.info(f"路徑序列: {[n.index for n in path_nodes]}")
    # log.info(f"預期總分: {final_score}")
    # log.info(f"預期總耗時: {total_time:.2f}s")

    # 5. 轉換為車子移動指令
    actions = maze.getActions(path_nodes)
    action_str = maze.actions_to_str(actions)

    print("\n" + "="*30)
    print(f"測試結果：")
    print(f"規劃路徑 (節點): {[n.index for n in path_nodes]}")
    print(f"車子指令字串: {action_str}")
    print("="*30)

if __name__ == "__main__":
    asyncio.run(test_navigation())