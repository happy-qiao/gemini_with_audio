import vertexai
from vertexai.generative_models import GenerativeModel, Part


def generate_text(project_id: str, location: str) -> str:
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    # Load the model
    model = GenerativeModel("gemini-1.0-pro")
    # Query the model
    response = model.generate_content(
        [
            # Add an example query
            "What color is cheese",
        ]
    )
    print(response)
    return response.text

generate_text('vertexsdk', 'us-west1')



