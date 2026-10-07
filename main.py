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



    