# TaskOrchestrator
Managing and directing tasks across the ASR and translation services, making it clear that it coordinates multiple processing steps to deliver a final response

## Dependencies

#### Project Requirements
Install project requirements with this command.
```
pip install -r app/requirements.txt
```

### Run project
To run the project run this command.
```
uvicorn app.main:app
```

Then you can access the swagger documentations in
```
http://127.0.0.1:8000/docs
```