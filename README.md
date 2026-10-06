## Smart Lost & Found OCR

### About the Project

- Smart Lost & Found OCR is a web-based application that helps users find lost items easily.

- In a normal Lost and Found system, users have to manually check the details of lost and found items. This can take a lot of time when there are many items.

- This project uses Optical Character Recognition (OCR) to read text from an image of a found item. The extracted text is then compared with the details of lost items stored in the database.

- If the system finds a strong match, the item is automatically marked as Found.

### Live Demo

https://lostfoundocr-adcjuhnivotsxkyitkjpmb.streamlit.app/

### Technologies Used

- Python
- Streamlit
- SQLite
- EasyOCR
- OpenCV
- NumPy
- Pillow

### Features

- Report a lost item
- Store lost-item details in a database
- Upload an image of a found item
- Extract text from the image using OCR
- Process images using OpenCV
- Compare found-item details with lost-item details
- Calculate a matching score
- Automatically mark an item as Found when the score is 90% or higher
- Display lost and found items separately
- Maintain item status in the database

### How It Works

<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/d17d2b1d-50bf-48bc-acdc-2f22b224ce39" />

### Main Modules
1. Lost Item Registration

Users can report a lost item by entering information such as:

Owner name
Item name
Description
Contact number
Last seen location
Date lost

The information is stored in the SQLite database.

2. Found Item Image Upload

When an item is found, the user can upload an image containing information about the item.

The uploaded image is processed before the OCR and matching stages.

3. Image Processing

OpenCV is used to process the uploaded image before text extraction.

The image can be processed by:

Resizing the image
Converting the image to grayscale
Improving image quality
Applying image enhancement techniques

This helps EasyOCR extract text more accurately.

4. OCR Text Extraction

EasyOCR is used to extract text from the uploaded image.

For example, the image may contain:

Black Wallet
Chennai Railway Station
Black leather wallet

EasyOCR extracts this information so that it can be used for matching.

5. Item Matching

The extracted information is compared with the lost-item information stored in the database.

The system checks details such as:

Item name
Description
Location
Date
Matching keywords

A matching score is then calculated.

6. Status Update

If the matching score is 90% or higher, the system marks the item as Found.

Before matching:

Status: Lost

After a successful match:

Status: Found

The matched item is then displayed in the Found / Matched Items section.

Matching Logic

The system compares the information extracted from the found-item image with the information stored for lost items.

For example:

Lost Item
Item Name  : Black Wallet
Location   : Chennai Railway Station
Description: Black leather wallet
OCR Result
Black Wallet
Chennai Railway Station
Black leather wallet

The system compares these details and calculates a matching score.

### Example:

Item Name Match    : 100%
Location Match     : 100%
Description Match  : 90%

Overall Match      : 95%

Since:

95% >= 90%

the item is marked as Found.

Status Flow
<img width="1027" height="2297" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/765a4795-9e54-45de-8f65-3b8aaa80a04c" />

The application uses SQLite to store lost-item information.

The database contains fields such as:

### Field	Description

ID	Unique ID of the item
Owner Name	Name of the owner
Item Name	Name of the lost item
Description	Description of the item
Contact	Contact number of the owner
Location	Last known location
Date Lost	Date when the item was lost
Status	Current status of the item

### Example:

ID	Item Name	Location	Status
1	Black Wallet	Chennai Railway Station	Lost
2	Blue Backpack	College Campus	Lost
3	Mobile Phone	Bus Stand	Found

### Project Structure
```
Smart-Lost-and-Found-OCR/
│
├── app.py
├── parser.py
├── executor.py
├── database.py
├── requirements.txt
├── README.md
│
└── .gitignore
```
app.py

Contains the main Streamlit application.

It manages the user interface, page navigation, image upload, OCR processing, matching results, and status updates.

parser.py

Handles image processing and OCR.

It extracts text from uploaded images and converts the extracted information into structured data.

executor.py

Contains the matching logic.

It compares the OCR information with the lost-item records and calculates the similarity score.

database.py

Handles the SQLite database.

It is responsible for creating the database, adding lost items, retrieving records, updating item status, and deleting records.

requirements.txt

Contains the Python packages required to run the application.

### Installation

#### Requirements

Before running the project, install:

Python 3.x
Git
pip

1. Clone the Repository
git clone https://github.com/your-username/smart-lost-and-found-ocr.git
2. Open the Project Folder
cd smart-lost-and-found-ocr
3. Create a Virtual Environment

For Windows:

python -m venv venv

Activate it:

venv\Scripts\activate

For Linux or macOS:

python3 -m venv venv

Activate it:

source venv/bin/activate
4. Install Required Packages
pip install -r requirements.txt
5. Run the Application
streamlit run app.py

The application will open in your browser.

### Requirements

The main packages used in this project are:

streamlit
easyocr
opencv-python-headless
numpy
Pillow

SQLite is included with Python.

All required packages can be installed using:

pip install -r requirements.txt
Deployment

The application can be deployed using Streamlit Community Cloud.

### Example
Step 1: Report a Lost Item

The user enters the lost-item details.

Item Name    : Black Backpack
Description  : Black backpack with laptop compartment
Location     : College Campus
Date Lost    : 05-10-2026
Contact      : **********

The information is saved in the database.

Step 2: Upload Found Item Image

When the item is found, the user uploads an image containing information about the item.

Step 3: Extract Text

OpenCV processes the image and EasyOCR extracts the text.

### Example:

Black Backpack
College Campus
Black backpack
Step 4: Compare Information

The extracted information is compared with the lost-item records.

Example:

Matching Score: 93%
Step 5: Update Status

Since the score is greater than or equal to 90%, the item is marked as Found.

Lost
  |
  v
Found

The item is then displayed in the Found / Matched Items section.

### Project Purpose

The purpose of this project is to make Lost and Found management easier and reduce the time required to identify matching items.

Instead of manually checking every lost and found record, the application uses OCR and automatic matching to identify possible matches.

The project combines:

OCR
Image processing
Database storage
Text matching
Automatic status updates
Limitations

The system may not always extract text correctly from an image.

OCR accuracy can be affected by:

Blurry images
Poor lighting
Low-quality images
Handwritten text
Unclear text
Complex backgrounds

The matching score also does not guarantee that two items are the same. A high-scoring match should still be verified before the item is returned to its owner.

### Future Enhancements

The project can be improved in the future by adding:

Better text matching using NLP
Machine learning-based matching
Email notifications
SMS notifications
User login and registration
Admin login
Cloud database
Mobile application
Object recognition
Location-based matching
Admin dashboard
Improved OCR for low-quality images
Match history

### Benefits

The system provides the following benefits:

Reduces manual searching
Saves time
Extracts information automatically from images
Stores item information in a database
Identifies possible matches automatically
Updates item status automatically
Provides a simple web-based interface

### Author

**Srudhya Sankaranarayanan**

License

This project is developed for educational and demonstration purposes.
