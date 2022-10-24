# starapp

### Pushing to github (assuming this is set as upstream)
```
git pull
git add .
git commit -m "hello"
git push
```

### Remote to Local
```
git fetch
git checkout main
git pull
```

### Branching
```
git checkout -b <branch>
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

## `example.config.json`
1. Copy `example.config.json` in the same directory
2. Rename to `config.json`
3. Change configs accordingly 

**DO NOT change `example.config.json` directly!**
