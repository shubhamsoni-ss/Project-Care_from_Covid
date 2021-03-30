# Project-Care_from_Covid

## Description for project features

This project helps its users to take early preventive measures against COVID by using all the incorporated features. Following are the features available in this project:

1. **signup/login/forgot password/logout/contact us**: These features were added to ensure a good user experience and for the security of data.

2. **Symptoms Checker**: This feature helps the user to select the symptoms which he/she is suffering from and then provide the possible disease along with the cause and preventive
measure on the website as well as on the mail so that the user could take early preventive measures to take relief from the predicted disease. This feature makes use of a machine learning algorithm named "Random Forest Algorithm".

  * Following files are available in the project which will be used exclusively for this feature:
  
    * symptoms_checker.html
    * healthrecord.html
    * check_symptoms.py
    * training.csv
    * testing.csv
    
3. **Social distancing index calculator**: This feature helps the user to analyze the video of any place to determine the index of social distancing which was being followed by the user available in the uploaded video and also get a good visualization with the help of graphs and output video. This feature makes the use of the YOLO v3 algorithm to analyze the video using Yolo weights and Yolo cfg to detect people in the video and mark the frame around them to calculate the social distancing index.

* Following files are available in the project which will be used exclusively for this feature:

    * socialdistancingindex.html
    * uploaded.py
    * coco.names
    * yolov3.cfg
    * yolov3.weights
    * SDIndex.py
    
4. **Contact Tracing**: This feature allows the user to input the details of the places which he/she visited recently and it will be stored in the MySQL database. If the user is
infected with COVID then the status of COVID in the database for the user will change which further triggers the search query into the database to get the details of all other users
who visited the same location, date, and approximately same time to send them an email regarding the risk of COVID infection to them.

## Notes
* _init_.py is the mail file that consists of routing to all the other files and please make sure to change the email address and email password before running this file so that
the alert notifications could be sent to other users by your email id.
* video.3gp is the file input file for the social distancing index calculator and output1.mp4 is the output file generated for it.
* I have used the username and password for my local system's database, it is subjected to be changed if it differs in your system.
* To view and create the database schema for this project, refer to [SRS of the project](https://drive.google.com/file/d/1Aibi4mIQl--io8tY36gLdp_dNzG7D6ig/view?usp=sharing).

## Steps to run this project in your local system
1. Clone or fork the project into your local system.
2. Ensure the availability of python version 2 or above, code editor, MySQL.
3. Change the email address, email password, and MySQL username and password in the _init_.py file.
4. Crete the database and tables in MySQL as given in the attached SRS document.
5. Remember to change the paths of different files and folders in the code as per your local filesystem.
