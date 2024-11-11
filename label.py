import json
import torch
from transformers import pipeline

# Check for MPS (Apple Silicon) or default to CPU
device = 0 if torch.has_mps else -1

# Initialize sentiment analysis pipeline with a lightweight model and specified device
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="finiteautomata/bertweet-base-sentiment-analysis", 
    device=device
)

def label_data(input_file, output_file):
    """
    This function loads a JSON file with comments, processes each comment with a sentiment analysis model,
    and saves the results into a new JSON file.
    """
    with open(input_file, "r") as f:
        data = json.load(f)
    
    # If `data` is a list, assume it's a list of comments directly
    if isinstance(data, list):
        comments = data
    else:
        # If it's a dictionary, get the comments list from a "comments" key
        comments = data.get("comments", [])

    labeled_comments = []
    
    # Process each comment individually with the pipeline
    for comment in comments:
        try:
            sentiment = sentiment_pipeline(comment, batch_size=1)[0]
            labeled_comments.append({"comment": comment, "sentiment": sentiment})
        except Exception as e:
            print(f"Error processing comment '{comment}': {e}")

    # Write output to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(labeled_comments, f, ensure_ascii=False, indent=4)
    
    print(f"Labeled data saved to {output_file}")

if __name__ == "__main__":
    # Input and output file paths
    input_file = "comments.json"   # Replace with your input JSON file containing comments
    output_file = "labeled_comments.json"   # This will be your output file

    # Run the labeling function
    label_data(input_file, output_file)
