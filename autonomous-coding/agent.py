"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

from claude_code_sdk import ClaudeSDKClient

from client import create_client
from progress import print_session_header, print_progress_summary
from prompts import get_initializer_prompt, get_coding_prompt, copy_spec_to_project


# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3


def _write_error_log(
    error_log: Path,
    error_time: str,
    iteration: Optional[int],
    error_type: str,
    error_msg: str,
    exception: Exception,
    context: str = "unknown",
) -> None:
    """
    Helper function to write error logs safely.

    Args:
        error_log: Path to error log file
        error_time: ISO format timestamp
        iteration: Iteration number (optional)
        error_type: Exception type name
        error_msg: Exception message
        exception: The exception object
        context: Context where error occurred
    """
    try:
        # 確保目錄存在
        error_log.parent.mkdir(parents=True, exist_ok=True)

        with open(error_log, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"[{error_time}] Agent Error - {context}\n")
            if iteration is not None:
                f.write(f"Iteration: {iteration}\n")
            f.write(f"Error Type: {error_type}\n")
            f.write(f"Error Message: {error_msg}\n")
            f.write(f"\nTraceback:\n")
            traceback.print_exception(
                type(exception), exception, exception.__traceback__, file=f
            )
            f.write(f"\n{'='*70}\n")
        print(f"\nError logged to: {error_log}")
    except Exception as log_error:
        # 即使寫入日誌失敗，也要在終端顯示
        print(f"\n[CRITICAL] Failed to write error log: {log_error}")
        print(f"Original error was: {error_type}: {error_msg}")


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
    iteration: Optional[int] = None,
) -> tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path
        iteration: Current iteration number (for logging)

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
    """
    print("Sending prompt to Claude Agent SDK...\n")

    try:
        # Send the query
        session_start_time = datetime.now()
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        message_count = 0
        tool_use_count = 0
        last_message_time = None

        async for msg in client.receive_response():
            message_count += 1
            last_message_time = datetime.now()
            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        tool_use_count += 1
                        print(f"\n[Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        # Check if command was blocked by security hook
                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            # Show errors (truncated)
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            # Tool succeeded - just show brief confirmation
                            print("   [Done]", flush=True)

        # Session ended - log statistics
        session_end_time = datetime.now()
        session_duration = (session_end_time - session_start_time).total_seconds()
        
        # 檢測可能的異常提前結束
        potential_issue = None
        issue_details = []
        
        if message_count == 0:
            potential_issue = "No messages received"
            issue_details.append("No messages received from agent")
        elif response_text.strip() == "" and tool_use_count == 0:
            potential_issue = "Empty response with no tool usage"
            issue_details.append("No response text and no tools used")
        else:
            # 檢查是否有未完成的工具使用
            # 如果最後一條訊息是工具使用，但沒有後續回應，可能是異常
            response_lower = response_text.lower()
            
            # 檢查是否在工具執行過程中結束
            # 如果最後的訊息時間很近，且沒有明確的完成標記，可能是異常
            time_since_last_msg = (
                (session_end_time - last_message_time).total_seconds()
                if last_message_time
                else 0
            )
            
            # 檢查 response 是否包含完成標記
            completion_markers = [
                "continue", "next session", "will continue", "auto-continue",
                "completed", "finished", "done", "ready for next"
            ]
            has_completion_marker = any(marker in response_lower for marker in completion_markers)
            
            # 如果時間很短（< 2秒）且沒有完成標記，且有很多工具使用，可能是異常
            if (
                time_since_last_msg < 2
                and not has_completion_marker
                and tool_use_count > 0
                and session_duration > 10  # 至少運行了一段時間
            ):
                potential_issue = f"Possible abrupt end: session ended quickly after tool usage"
                issue_details.append(f"Time since last message: {time_since_last_msg:.2f}s")
                issue_details.append(f"Tool uses: {tool_use_count}")
                issue_details.append(f"No completion markers found")
                issue_details.append(f"Response ends with: {response_text[-100:] if len(response_text) > 100 else response_text}")

        # 記錄 session 統計資訊
        session_log = project_dir / "agent_session.log"
        try:
            session_log.parent.mkdir(parents=True, exist_ok=True)
            with open(session_log, "a", encoding="utf-8") as f:
                f.write(f"\n[{session_end_time.isoformat()}] Session {iteration or 'unknown'}\n")
                f.write(f"  Duration: {session_duration:.2f}s\n")
                f.write(f"  Messages: {message_count}\n")
                f.write(f"  Tool uses: {tool_use_count}\n")
                f.write(f"  Response length: {len(response_text)} chars\n")
                if last_message_time:
                    time_since_last = (session_end_time - last_message_time).total_seconds()
                    f.write(f"  Time since last message: {time_since_last:.2f}s\n")
                if potential_issue:
                    f.write(f"  ⚠️  POTENTIAL ISSUE: {potential_issue}\n")
                    for detail in issue_details:
                        f.write(f"    - {detail}\n")
                f.write("-" * 70 + "\n")
        except Exception as log_error:
            print(f"\n[WARNING] Failed to write session log: {log_error}")

        # 如果有潛在問題，在終端顯示警告
        if potential_issue:
            print(f"\n{'='*70}")
            print(f"⚠️  WARNING: {potential_issue}")
            print(f"Session duration: {session_duration:.2f}s")
            print(f"Messages received: {message_count}")
            print(f"Tool uses: {tool_use_count}")
            print(f"Response length: {len(response_text)} chars")
            if issue_details:
                print(f"\nDetails:")
                for detail in issue_details:
                    print(f"  - {detail}")
            print(f"{'='*70}\n")

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except KeyboardInterrupt:
        print("\n[Session interrupted by user]")
        raise  # 重新拋出，讓上層處理

    except Exception as e:
        # 詳細的錯誤日誌
        error_time = datetime.now().isoformat()
        error_type = type(e).__name__
        error_msg = str(e)

        # 檢查是否為 JSON buffer overflow 錯誤
        is_buffer_overflow = (
            "JSON message exceeded maximum buffer size" in error_msg
            or "1048576" in error_msg
        )
        
        # 檢查是否可能與截圖相關（從錯誤前的 log 推斷）
        is_screenshot_related = (
            "take_screenshot" in str(e.__traceback__) if hasattr(e, "__traceback__") else False
        ) or "screenshot" in error_msg.lower()

        print(f"\n{'='*70}")
        print(f"ERROR during agent session [{error_time}]")
        if iteration is not None:
            print(f"Iteration: {iteration}")
        print(f"{'='*70}")
        print(f"Error Type: {error_type}")
        print(f"Error Message: {error_msg}")
        
        # 針對 buffer overflow 提供特殊建議
        if is_buffer_overflow:
            print(f"\n{'='*70}")
            print("⚠️  JSON BUFFER OVERFLOW DETECTED")
            print(f"{'='*70}")
            print("\nThis error occurs when tool results exceed 1MB limit.")
            print("\nCommon causes:")
            print("  1. 📸 Screenshot with fullPage: True")
            print("     - Full-page screenshots generate huge JSON (>1MB)")
            print("     - Solution: Use regular viewport screenshots instead")
            print("     - If needed, scroll and take multiple screenshots")
            print("  2. 📄 Reading entire large files")
            print("     - app_spec.txt, feature_list.json can be very large")
            print("     - Solution: Read in chunks using 'head' or 'tail'")
            print("     - Example: head -100 app_spec.txt")
            print("  3. 🔍 Large grep/glob results")
            print("     - Solution: Limit results with 'head' or line limits")
            print("     - Example: grep 'pattern' file | head -50")
            print("\nQuick fixes:")
            if is_screenshot_related:
                print("  ⚠️  This appears to be screenshot-related!")
                print("  → Remove 'fullPage: True' from screenshot calls")
                print("  → Use regular screenshots or take_snapshot instead")
                print("  → Scroll to different sections if you need to see more")
            else:
                print("  → Read files in chunks (head/tail)")
                print("  → Limit tool result sizes")
                print("  → The prompt has been updated with best practices")
            print(f"\n{'='*70}\n")

        print(f"\nFull Traceback:")
        print("-" * 70)
        traceback.print_exc()
        print("-" * 70)

        # 寫入錯誤日誌檔案
        error_log = project_dir / "agent_errors.log"
        _write_error_log(
            error_log,
            error_time,
            iteration,
            error_type,
            error_msg,
            e,
            context="agent_session",
        )

        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT DEMO")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print(f"Model: {model}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    if is_first_run:
        print("Fresh start - will use initializer agent")
        print()
        print("=" * 70)
        print("  NOTE: First session takes 10-20+ minutes!")
        print("  The agent is generating 200 detailed test cases.")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir)
    else:
        print("Continuing existing project")
        print_progress_summary(project_dir)

    # 確保錯誤日誌目錄存在
    error_log = project_dir / "agent_errors.log"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Print session header
        print_session_header(iteration, is_first_run)

        try:
            # Create client (fresh context)
            client = create_client(project_dir, model)

            # Choose prompt based on session type
            if is_first_run:
                prompt = get_initializer_prompt()
                is_first_run = False  # Only use initializer once
            else:
                prompt = get_coding_prompt()

            # Run session with async context manager
            try:
                async with client:
                    status, response = await run_agent_session(
                        client, prompt, project_dir, iteration=iteration
                    )
            except Exception as context_error:
                # Context manager 或 session 執行時的錯誤
                error_time = datetime.now().isoformat()
                error_type = type(context_error).__name__
                error_msg = str(context_error)

                print(f"\n{'='*70}")
                print(f"ERROR in context manager/session [{error_time}]")
                print(f"Iteration: {iteration}")
                print(f"{'='*70}")
                print(f"Error Type: {error_type}")
                print(f"Error Message: {error_msg}")
                print(f"\nFull Traceback:")
                print("-" * 70)
                traceback.print_exc()
                print("-" * 70)

                # 寫入錯誤日誌
                _write_error_log(
                    error_log,
                    error_time,
                    iteration,
                    error_type,
                    error_msg,
                    context_error,
                    context="context_manager/session",
                )

                status = "error"
                response = str(context_error)

            # Handle status
            if status == "continue":
                print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
                print_progress_summary(project_dir)
                await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

            elif status == "error":
                print("\nSession encountered an error")
                print("Will retry with a fresh session...")
                await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        except Exception as outer_error:
            # 捕捉 create_client 或其他外層錯誤
            error_time = datetime.now().isoformat()
            error_type = type(outer_error).__name__
            error_msg = str(outer_error)

            print(f"\n{'='*70}")
            print(f"FATAL ERROR in main loop [{error_time}]")
            print(f"Iteration: {iteration}")
            print(f"{'='*70}")
            print(f"Error Type: {error_type}")
            print(f"Error Message: {error_msg}")
            print(f"\nFull Traceback:")
            print("-" * 70)
            traceback.print_exc()
            print("-" * 70)

            # 寫入錯誤日誌
            _write_error_log(
                error_log,
                error_time,
                iteration,
                error_type,
                error_msg,
                outer_error,
                context="main_loop",
            )

            print("\n[FATAL] Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")
