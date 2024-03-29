from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

from Class.Responses import Response
import predict_new as predictor


app = FastAPI()
handler = Mangum(app)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )

@app.get("/")
def read_root():
    return Response.success(message="Connection Sucessfull")

@app.get("/predict_schedule")
async def predict_recent():
    try:
        predictions = predictor.main()
        result = predictions.to_dict(orient='records')
        print(result)
        return Response.success(data=result)
    except Exception as e:
        return Response.error(message=str(e))
