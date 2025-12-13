#ToDoList

##2025/12/12

- suggestion_agent.py : エージェントが tools を使う前に思考した内容があれば response から取得し、message に追加する。
- parent_agent が search query を考えるのか、children が考えるのかを決め、スキーマ整形する。

##2025/12/13

- suggestion_agent.py : 以下の部分、エージェントに tool use の response であることを明示して伝える。（スキーマ用意）

```
if response.stop_reason == "tool_use":
    messages.append({"role": "assistant", "content": response.content})
```
