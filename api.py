import requests

BASE_URL = (
    "https://AkshatJain20092002-"
    "Email-Classification-Support-System.hf.space/classify"
)

test_email = (
    "Subject: Dringendes Konto-Problem\n\n"
    "Hallo Support-Team,\n\n"
    "mein Name ist Hans Müller und ich schreibe bezüglich meines "
    "Kontos hans.mueller@example.de.\n"
    "meine Kreditkarte 4111-1111-1111-1111\n"
    "mit CVV 456 ist am 05/26 abgelaufen.\n"
    "meine aadhar-Nummer lautet 1234-5678-9123.\n"
    "Bitte kontaktieren Sie mich unter +49-170-1234567\n"
    "so schnell wie möglich.\n\n"
    "Vielen Dank!"
)

response = requests.post(BASE_URL, json={"email_body": test_email})
print(response.status_code)
print(response.json())
