from fastapi import FastAPI
import uvicorn

from referal.api import router as referal_router

app = FastAPI()
app.include_router(referal_router, prefix='/referal')

if __name__ == '__main__':
    uvicorn.run('src.main:app', host='127.0.0.1', port=8000, reload=True)
