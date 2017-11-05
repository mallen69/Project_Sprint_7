# Guide to Project Documentation

Each sprint in the course will involve documenting your project development and learning processes. This documentation will be published in a central repository on the Devleague github account. This repository is visible only to the coaching team and students in the cohort.

You will fork this repository to your personal github account, and then clone it to your local computer. In the repository you will find a folder for each sprint. You'll create a jupyter notebook in this directory, which you will edit on your local computer, push to your personal github repository and then send to the central repository via a pull request.

## Setting up the connection to the Classfolio

You will only have to do this once.

#### Forking the Classfolio
1. We will begin by creating a fork (personal copy) of the Repository that we want to edit.
2. If you are reading this then you are already on the page that you need to fork. Good job!
3. In the top right hand corner click "Fork".
      - This will create your own copy of the repository. However, right now its only on your github website! you still need to clone it to your local computer.

#### Cloning the Classfolio onto your local computer
4. On the right hand side of the screen click the green "Clone or download" drop down.
5. Click "open in Desktop"
  - You may get a pop up that asks if you want to open Github Desktop. You do.
  - Your Github Desktop app will open
  - It should take you to the URL Tab. Click the URL tab if it doesn't.
6. Go to the section where it says "local path" click "choose" to select a folder on your computer where you would like your repository to be. i.e. Documents or Desktop.
7. You do *not* have to change the name of the folder (unlike when creating a new project) that you are cloning. You'll just be uploading your work back to the group repository.
8. Click "clone"
  - This will clone your personal copy of the repository to your local computer.
9. Ensure that your changes are being made by periodically pushing your personal repo to your online github site.

## Creating, Uploading, and Updating your Documentation

You will follow the same basic process every time you want to create and/or publish your documentation. You should start to get the hang of it after a few sprints.

#### Starting the Jupyter Notebook Server

Jupyter Notebook is a browser-based application that you use to view, edit, and create jupyter notebook files in a browsers. To get it to work, you have to have python and jupyter notebook installed (will come with Anaconda). The first step is starting a server, which will run locally and allow your browser to connect to it.

1. Open a Terminal Screen on a Mac. On a PC open PuTTy or whatever else you use to access a command line environment where you can use python.
2. Navigate to your the folder on your computer with the file that you would like to edit. ie /Users/victorialarson/Desktop/Dev\ League/GitHub/BigDataAnalyst_ProjectDocumentation
3. Type "jupyter notebook"
    - The Jupyter notebook server will now be running on your local computer and causes the application to pop up in a web browser.
4. Click on your personal jupyter notebook (the file extension will be .ipynb)
5. A web browser with your editable jupyter notebook will pop up.

#### Opening a Jupyter Notebook that has been created for you

The default cell you will be editing in is a code cell. We want it to be a markdown cell.

6. In the task bar click "cell > cell type > markdown.
7. This is where you will add in anything and everything about your projects. Likes, dislikes, what you learned, what you want to learn more of.
8. save your work!

You can also change the filename to be a description of a project instead of just your name. If you don't see your name, you can create a new notebook in the browser app.

#### Publishing your documentation to your personal github

9. When you are finished documenting your work Go to your hithub desktop app.
10. Commit your changes.
11. Push your work to your personal github site.

### Publishing your documentation to the central classfolio with a pull request

1. Go back to your forked BigDataAnalystTrack Github website.
2. Click "new pull request"
3. Make sure that the page says "able to merge"
4. Click "create pull request"
5. Add comments
6. CLick "create pull request"
7. __Great job!__ You have completed the forking process! At this step you wait for the Repository administrator to merge your forked repository into the master repository!
