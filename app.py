from incident_commander.ui.app import create_app
from incident_commander.config import GRADIO_PORT, GRADIO_SHARE

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=GRADIO_PORT,
        share=GRADIO_SHARE
    )
else:
    app = create_app()
