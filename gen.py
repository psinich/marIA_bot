import uuid

def generate_uuid():
    return str(uuid.uuid4())

for i in range(5):
    print(f"https://challenge.braim.org/certificates/{generate_uuid()}")
