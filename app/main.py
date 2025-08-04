# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Árvore Pão System")

@app.get("/")
def read_root():
    return {"message": "API funcionando!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "arvore_pao"}
