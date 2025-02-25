import boto3
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO

# Function to detect labels using AWS Rekognition
def detect_labels(photo, bucket):
    try:
        client = boto3.client('rekognition')

        # Detect labels in the image
        response = client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            MaxLabels=10
        )

        print(f'Detected labels for {photo}:\n')
        for label in response['Labels']:
            print(f"Label: {label['Name']}")
            print(f"Confidence: {label['Confidence']:.2f}%\n")

        # Load the image from S3
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=photo)
        img_data = obj['Body'].read()
        img = Image.open(BytesIO(img_data))

        # Display the image with bounding boxes
        plt.imshow(img)
        ax = plt.gca()

        # Draw bounding boxes if present
        for label in response['Labels']:
            if 'Instances' in label:  # Ensure Instances key exists
                for instance in label.get('Instances', []):
                    if 'BoundingBox' in instance:  # Check if bounding box exists
                        bbox = instance['BoundingBox']
                        left = bbox['Left'] * img.width
                        top = bbox['Top'] * img.height
                        width = bbox['Width'] * img.width
                        height = bbox['Height'] * img.height

                        # Draw a rectangle
                        rect = patches.Rectangle((left, top), width, height,
                                                 linewidth=2, edgecolor='r', facecolor='none')
                        ax.add_patch(rect)

                        # Display label name
                        label_text = f"{label['Name']} ({label['Confidence']:.2f}%)"
                        plt.text(left, top - 5, label_text, color='red', fontsize=10,
                                 bbox=dict(facecolor='white', alpha=0.5))

        plt.axis('off')
        plt.show()

        return len(response['Labels'])

    except Exception as e:
        print(f"Error: {e}")
        return 0  # Return 0 labels if there's an error

# Main function
def main():
    photo = 'Hackathon.jpg'  
    bucket = 'aws-rekognition-label-pradip'  

    label_count = detect_labels(photo, bucket)
    print(f"Total labels detected: {label_count}")

if __name__ == "__main__":
    main()
