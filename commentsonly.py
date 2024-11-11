import json

def extract_comments(input_file, output_file):
    # Load the original data
    with open(input_file, "r") as f:
        data = json.load(f)
    
    # Extract comments
    comments = data.get("comments", [])
    
    # Save only the comments to a new JSON file
    with open(output_file, "w") as f:
        json.dump(comments, f, indent=4)
    
    print(f"Comments saved to {output_file}")

# Usage example
if __name__ == "__main__":
    input_file = "jac53THxO0I_data.json"  # Replace with your actual input file
    output_file = "comments_only.json"  # The file that will contain only the comments
    extract_comments(input_file, output_file)
