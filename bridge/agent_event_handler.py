"""
Agent Event Handler - Handles agent events and thinking process output
"""

from common.log import logger


class AgentEventHandler:
    """
    Handles agent events and optionally sends intermediate messages to channel
    """
    
    def __init__(self, context=None, original_callback=None):
        """
        Initialize event handler
        
        Args:
            context: COW context (for accessing channel)
            original_callback: Original event callback to chain
        """
        self.context = context
        self.original_callback = original_callback
        
        # Get channel for sending intermediate messages
        self.channel = None
        if context:
            self.channel = context.kwargs.get("channel") if hasattr(context, "kwargs") else None
        
        # Track current thinking for channel output
        self.current_thinking = ""
        self.turn_number = 0
    
    def handle_event(self, event):
        """
        Main event handler
        
        Args:
            event: Event dict with type and data
        """
        event_type = event.get("type")
        data = event.get("data", {})
        
        # Dispatch to specific handlers
        if event_type == "turn_start":
            self._handle_turn_start(data)
        elif event_type == "message_update":
            self._handle_message_update(data)
        elif event_type == "message_end":
            self._handle_message_end(data)
        elif event_type == "tool_execution_start":
            self._handle_tool_execution_start(data)
        elif event_type == "tool_execution_end":
            self._handle_tool_execution_end(data)
        elif event_type == "step_complete":
            self._handle_step_complete(data)
        elif event_type == "tool_results_complete":
            self._handle_tool_results_complete(data)
        
        # Call original callback if provided
        if self.original_callback:
            self.original_callback(event)
    
    def _handle_turn_start(self, data):
        """Handle turn start event"""
        self.turn_number = data.get("turn", 0)
        self.has_tool_calls_in_turn = False
        self.current_thinking = ""
    
    def _handle_message_update(self, data):
        """Handle message update event (streaming text)"""
        delta = data.get("delta", "")
        self.current_thinking += delta
    
    def _handle_message_end(self, data):
        """Handle message end event"""
        tool_calls = data.get("tool_calls", [])
        
        # Only send thinking process if followed by tool calls
        if tool_calls:
            if self.current_thinking.strip():
                logger.info(f"💭 {self.current_thinking.strip()[:200]}{'...' if len(self.current_thinking) > 200 else ''}")
                # Send thinking process to channel
                self._send_to_channel(f"{self.current_thinking.strip()}")
                
                # 修复：将思考消息存储到对话历史中
                self._store_thinking_to_history(self.current_thinking.strip())
        else:
            # No tool calls = final response (logged at agent_stream level)
            if self.current_thinking.strip():
                logger.debug(f"💬 {self.current_thinking.strip()[:200]}{'...' if len(self.current_thinking) > 200 else ''}")
        
        self.current_thinking = ""
    
    def _handle_tool_execution_start(self, data):
        """Handle tool execution start event - logged by agent_stream.py"""
        pass
    
    def _handle_tool_execution_end(self, data):
        """Handle tool execution end event - logged by agent_stream.py"""
        pass
    
    def _handle_step_complete(self, data):
        """
        Handle step complete event - each reasoning step as independent reply
        
        Args:
            data: Event data containing step information
        """
        turn = data.get("turn", 0)
        assistant_msg = data.get("assistant_msg", "")
        tool_calls = data.get("tool_calls", [])
        is_final = data.get("is_final", False)
        
        # Log the step
        if assistant_msg:
            logger.info(f"💭 Step {turn}: {assistant_msg[:150]}{'...' if len(assistant_msg) > 150 else ''}")
        
        if tool_calls:
            tool_names = [tc.get("name", "unknown") for tc in tool_calls]
            logger.info(f"🔧 Step {turn} tools: {', '.join(tool_names)}")
        
        # Send step as independent reply to channel
        self._send_step_to_channel(turn, assistant_msg, tool_calls, is_final)
    
    def _handle_tool_results_complete(self, data):
        """
        Handle tool results complete event - tool execution results as independent reply
        
        Args:
            data: Event data containing tool results
        """
        turn = data.get("turn", 0)
        tool_results = data.get("tool_results", [])
        
        # Log tool results
        if tool_results:
            result_count = len(tool_results)
            logger.info(f"✅ Step {turn} tool results: {result_count} result(s)")
            
            # Send tool results as independent reply to channel
            self._send_tool_results_to_channel(turn, tool_results)
    
    def _send_step_to_channel(self, turn, assistant_msg, tool_calls, is_final):
        """
        Send a reasoning step as independent reply to channel
        
        Args:
            turn: Current turn number
            assistant_msg: Assistant message text
            tool_calls: List of tool calls
            is_final: Whether this is the final step
        """
        # Build step message
        step_message = ""
        if assistant_msg:
            step_message = assistant_msg
        
        # Add tool calls information
        if tool_calls:
            tool_info = "\n\n**工具调用：**\n"
            for i, tc in enumerate(tool_calls, 1):
                tool_name = tc.get("name", "unknown")
                tool_args = tc.get("arguments", {})
                tool_info += f"{i}. **{tool_name}**"
                if tool_args:
                    # Format arguments nicely
                    args_str = ", ".join([f"{k}={v}" for k, v in tool_args.items()])
                    if args_str:
                        tool_info += f" ({args_str})"
                tool_info += "\n"
            step_message += tool_info
        
        # Add step indicator
        if not is_final:
            step_indicator = f"\n\n--- 步骤 {turn} ---"
            step_message += step_indicator
        
        # Send to channel
        self._send_to_channel(step_message)
    
    def _send_tool_results_to_channel(self, turn, tool_results):
        """
        Send tool execution results as independent reply to channel
        
        Args:
            turn: Current turn number
            tool_results: List of tool result blocks
        """
        if not tool_results:
            return
        
        # Build results message
        results_message = f"**工具执行结果（步骤 {turn}）：**\n\n"
        
        for i, result_block in enumerate(tool_results, 1):
            tool_use_id = result_block.get("tool_use_id", f"tool_{i}")
            content = result_block.get("content", "")
            is_error = result_block.get("is_error", False)
            
            # Determine status emoji
            status_emoji = "❌" if is_error else "✅"
            
            # Format content
            if isinstance(content, str):
                # Truncate long content
                if len(content) > 500:
                    content = content[:500] + "... [内容过长已截断]"
                results_message += f"{status_emoji} **工具 {i}**：{content}\n\n"
            else:
                results_message += f"{status_emoji} **工具 {i}**：执行完成\n\n"
        
        # Send to channel
        self._send_to_channel(results_message)
    
    def _send_to_channel(self, message):
        """
        Try to send intermediate message to channel.
        Skipped in SSE mode because thinking text is already streamed via on_event.
        """
        if self.context and self.context.get("on_event"):
            return

        if self.channel:
            try:
                from bridge.reply import Reply, ReplyType
                reply = Reply(ReplyType.TEXT, message)
                self.channel._send(reply, self.context)
            except Exception as e:
                logger.debug(f"[AgentEventHandler] Failed to send to channel: {e}")
    
    def _store_thinking_to_history(self, thinking_text):
        """
        Store assistant thinking messages to conversation history.
        
        Args:
            thinking_text: The thinking text to store
        """
        try:
            # 获取session_id
            if not self.context:
                return
            
            session_id = self.context.get("session_id")
            if not session_id:
                return
            
            # 导入必要的模块
            from agent.memory import get_conversation_store
            
            # 创建助手思考消息
            thinking_message = {
                "role": "assistant",
                "content": [{"type": "text", "text": thinking_text}]
            }
            
            # 存储到对话历史
            store = get_conversation_store()
            store.append_messages(
                session_id=session_id,
                messages=[thinking_message],
                channel_type="web"
            )
            
            logger.debug(f"[AgentEventHandler] Stored thinking message to history: {thinking_text[:100]}...")
            
        except Exception as e:
            logger.debug(f"[AgentEventHandler] Failed to store thinking to history: {e}")
    
    def log_summary(self):
        """Log execution summary - simplified"""
        # Summary removed as per user request
        # Real-time logging during execution is sufficient
        pass
