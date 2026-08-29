#!/usr/bin/env bash
# Superpowers 任务管理脚本
# 用于创建、跟踪和管理创作计划中的任务
#
# 使用方法:
#   ./todo.sh add "任务描述"           # 添加任务
#   ./todo.sh list                     # 列出所有任务
#   ./todo.sh done <任务号>            # 标记任务完成
#   ./todo.sh status                   # 查看进度
#   ./todo.sh clear                    # 清除所有任务
#   ./todo.sh export                   # 导出为 Markdown

TODO_FILE="${TODO_FILE:-$HOME/.openclaw/workspace/.superpowers-todo.json}"

# 确保目录存在
mkdir -p "$(dirname "$TODO_FILE")"

# 初始化 TODO 文件
init_todo() {
  if [[ ! -f "$TODO_FILE" ]]; then
    echo '{"tasks": [], "next_id": 1}' > "$TODO_FILE"
  fi
}

# 添加任务
add_task() {
  local description="$1"
  init_todo
  
  local id=$(jq '.next_id' "$TODO_FILE")
  local updated=$(jq --arg desc "$description" --argjson id "$id" \
    '.tasks += [{"id": $id, "description": $desc, "status": "pending", "created_at": now}] | .next_id += 1' \
    "$TODO_FILE")
  echo "$updated" > "$TODO_FILE"
  
  echo "✓ 任务 #$id 已添加：$description"
}

# 列出任务
list_tasks() {
  init_todo
  
  local pending=$(jq '[.tasks[] | select(.status == "pending")]' "$TODO_FILE")
  local done=$(jq '[.tasks[] | select(.status == "done")]' "$TODO_FILE")
  
  echo "📋 待办任务:"
  if [[ $(echo "$pending" | jq 'length') -eq 0 ]]; then
    echo "  (无)"
  else
    echo "$pending" | jq -r '.[] | "  - [ ] #\(.id) \(.description)"'
  fi
  
  echo ""
  echo "✅ 已完成:"
  if [[ $(echo "$done" | jq 'length') -eq 0 ]]; then
    echo "  (无)"
  else
    echo "$done" | jq -r '.[] | "  - [x] #\(.id) \(.description)"'
  fi
}

# 标记任务完成
done_task() {
  local id="$1"
  init_todo
  
  local updated=$(jq --argjson id "$id" \
    '.tasks = [.tasks[] | if .id == $id then .status = "done" else . end]' \
    "$TODO_FILE")
  echo "$updated" > "$TODO_FILE"
  
  echo "✓ 任务 #$id 已标记为完成"
}

# 查看进度
show_status() {
  init_todo
  
  local total=$(jq '.tasks | length' "$TODO_FILE")
  local done=$(jq '[.tasks[] | select(.status == "done")] | length' "$TODO_FILE")
  local pending=$((total - done))
  
  echo "📊 任务进度:"
  echo "  总计：$total"
  echo "  已完成：$done"
  echo "  待办：$pending"
  
  if [[ $total -gt 0 ]]; then
    local percent=$((done * 100 / total))
    echo "  进度：${percent}%"
  fi
}

# 清除所有任务
clear_tasks() {
  init_todo
  echo '{"tasks": [], "next_id": 1}' > "$TODO_FILE"
  echo "✓ 所有任务已清除"
}

# 导出为 Markdown
export_tasks() {
  init_todo
  
  echo "# 任务清单"
  echo ""
  echo "## 待办"
  echo ""
  jq -r '.tasks[] | select(.status == "pending") | "- [ ] #\(.id) \(.description)"' "$TODO_FILE"
  echo ""
  echo "## 已完成"
  echo ""
  jq -r '.tasks[] | select(.status == "done") | "- [x] #\(.id) \(.description)"' "$TODO_FILE"
}

# 主程序
case "${1:-}" in
  add)
    if [[ -z "${2:-}" ]]; then
      echo "用法：$0 add <任务描述>"
      exit 1
    fi
    add_task "$2"
    ;;
  list)
    list_tasks
    ;;
  done)
    if [[ -z "${2:-}" ]]; then
      echo "用法：$0 done <任务号>"
      exit 1
    fi
    done_task "$2"
    ;;
  status)
    show_status
    ;;
  clear)
    clear_tasks
    ;;
  export)
    export_tasks
    ;;
  *)
    echo "Superpowers 任务管理"
    echo ""
    echo "用法:"
    echo "  $0 add <描述>     添加任务"
    echo "  $0 list           列出所有任务"
    echo "  $0 done <任务号>   标记任务完成"
    echo "  $0 status         查看进度"
    echo "  $0 clear          清除所有任务"
    echo "  $0 export         导出为 Markdown"
    ;;
esac
