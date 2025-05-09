from fastapi import FastAPI
import datetime

app = FastAPI()

@app.get('/api/datetime')
def get_datetime():
    now = datetime.datetime.now()
    return {
        "Year": now.year,
        "Month": now.month,
        "Day": now.day,
        "Hour": now.hour,
        "Minute": now.minute,
        "Second": now.second
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8088)
