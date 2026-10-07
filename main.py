event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
except ValueError:
    raise HTTPException(status_code=400, detail="Invalid payload")
except stripe.error.SignatureVerificationError:
    raise HTTPException(status_code=400, detail="Invalid signature")

if event.type == 'checkout.session.completed':
    session = event.data.object
    customer_email = session.get('customer_details', {}).get('email') or session.get('customer_email')
    
    new_key = f"pk_live_{uuid.uuid4().hex}"
    
    db = SessionLocal()
    try:
        db_key = APIKey(key=new_key, email=customer_email)
        db.add(db_key)
        db.commit()
        print(f"Generated API Key: {new_key} for {customer_email}")
    finally:
        db.close()

return {"status": "success"}
@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
        event_dict = event.to_dict()

    if event_dict.get('type') == 'checkout.session.completed':
        session = event_dict.get('data', {}).get('object', {})
        customer_email = session.get('customer_details', {}).get('email') or session.get('customer_email')
        
        new_key = f"pk_live_{uuid.uuid4().hex}"
        
        db = SessionLocal()
        try:
            db_key = APIKey(key=new_key, email=customer_email)
            db.add(db_key)
            db.commit()
            print(f"Generated API Key: {new_key} for {customer_email}")
        finally:
            db.close()
            return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)





    