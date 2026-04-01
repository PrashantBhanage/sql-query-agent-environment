import threading
import uvicorn
import gradio as gr

from server import app as fastapi_app
from server.app import env_state, get_schema_info, get_task_description, execute_read_only_query


def run_api_server():
    """Run FastAPI server in a background thread (on 7861)."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=7861, log_level="info")


def reset_task(task_id: str):
    env_state.reset(task_id)
    schema = get_schema_info()
    desc = get_task_description(task_id)

    return {
        "message": "Reset complete",
        "task_description": desc,
        "schema_info": schema,
        "task_id": task_id,
        "step_count": 0,
    }


def execute_task(task_id: str, query: str):
    env_state.increment_step()
    schema_info = get_schema_info()
    task_description = get_task_description(task_id)

    results, error = execute_read_only_query(query)
    reward = 0.0
    feedback = ""
    done = False

    if error:
        reward = -0.1
        feedback = error
    elif results:
        reward = 1.0
        feedback = f"Query executed successfully. {len(results)} row(s) returned."
        done = True
    else:
        reward = 0.5
        feedback = "Query executed successfully. No rows returned."
        done = True

    return {
        "task_id": task_id,
        "task_description": task_description,
        "schema_info": schema_info,
        "query_result": results,
        "error": error,
        "reward": reward,
        "done": done,
        "feedback": feedback,
        "step_count": env_state.step_count,
    }


def create_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## SQL Query Agent Environment (Gradio + FastAPI)")

        with gr.Row():
            task_id = gr.Dropdown(choices=["task_1", "task_2", "task_3", "task_4"], value="task_1", label="Task ID")
            reset_button = gr.Button("Reset")

        reset_output = gr.JSON(label="Reset Output")

        query_input = gr.Textbox(lines=4, placeholder="SELECT ...", label="SQL SELECT Query")
        run_button = gr.Button("Run Query")
        step_output = gr.JSON(label="Step Output")

        reset_button.click(lambda t: reset_task(t), inputs=task_id, outputs=reset_output, api_name="reset_task")
        run_button.click(lambda t, q: execute_task(t, q), inputs=[task_id, query_input], outputs=step_output, api_name="execute_query")

    return demo


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    demo_app = create_ui()
    demo_app.launch(server_name="0.0.0.0", server_port=7860)
