# OpenAI Playground

This project is about recreating a playground environment for OpenAI assistants using a code interpreter and file retrieval.

## Project Setup

Follow these steps to set up the project:

1. Use `application.py` as your Flask file. This file contains the main application logic.

2. Use `api2.py` for your code to interact with the OpenAI REST API. This file contains the code for making API requests to OpenAI.

3. Apply styles to `index.html` file and `stylesheet.css`. These files contain the HTML structure and CSS styles for the application's frontend.

4. Create a `requirements.txt` file for libraries. This file should list all the Python libraries that your project depends on.

5. Create a `Procfile` for interaction with Gunicorn and Elastic Beanstalk (AWS). This file is used by Gunicorn (a WSGI HTTP server) and AWS Elastic Beanstalk to understand how to run your application.

6. Create an application using AWS Elastic Beanstalk. Follow the instructions in the AWS Elastic Beanstalk documentation to do this.

7. Create a bucket for file using AWS S3. Follow the instructions in the AWS S3 documentation to do this.

8. Zip necessary files. Use a tool like `zip` or a program like WinRAR to do this.

9. Deploy the app. Follow the instructions in the AWS Elastic Beanstalk documentation to do this.

## Usage

Once you've set up the project, you can start using the OpenAI Playground. Enter your code or upload a file, and the playground will interpret the code or retrieve the file using OpenAI's API.
