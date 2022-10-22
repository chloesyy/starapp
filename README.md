# starapp

### Pushing to github (assuming this is set as upstream)
```
git pull
git add .
git commit -m "hello"
git push
```

### Branching
```
git checkout <branch>
[make changes]
git add .
git commit -m "hello"
git push --set-upstream origin <branch>
```

### Pushing to heroku (for deployment)
```
git push heroku main
```

# BT5110 Starapp Project
## Getting Started
1. Activate virtual environment: ```env\Scripts\activate```
2. Run application: ```python app.py```
3. Local host: ```http://127.0.0.1:1234```
