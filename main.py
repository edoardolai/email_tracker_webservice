from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/track_email")
def track_email(request: Request, email: str = ""):
    client_ip = request.client.host

    return {
        "status": "tracked",
        "email_clicked": email,
        "client_ip": client_ip,
    }
